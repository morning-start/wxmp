import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Literal, NamedTuple

import pandas as pd
from loguru import logger
from tqdm import tqdm

from wxmp.api import ArticleListItem, SearchBizError, TokenError, WxMPAPI
from wxmp.tools import load_json, sanitize_filename, save_article_content, save_json
from wxmp.tools.time_manager import TimeManager, TimeRange


class ArticleDownloadTask(NamedTuple):
    url: str
    title: str
    save_dir: Path
    save_file: Literal["md", "html"] = "md"
    max_retries: int = 3
    timeout: int = 30
    date_str: str = ""
    account_name: str = ""
    digest: str = ""
    min_file_size_kb: int = 3


class TimeRangeSpider(WxMPAPI):
    def __init__(self, cookies: dict[str, str]) -> None:
        super().__init__(cookies)
        try:
            self.token = self._fetch_token()
            logger.info(f"获取token成功: {self.token}")
        except TokenError as e:
            logger.error(f"❌ 获取token失败: {str(e)}")
            raise

    @classmethod
    def from_cookies_file(cls, file_path: str) -> "TimeRangeSpider":
        data = load_json(file_path)
        cookies = data["请求 Cookie"]
        return cls(cookies)

    def load_or_search_bizs(
        self, gzh_names: list[str] = None, cache_file: Path = Path("temp/fakeids.json")
    ) -> dict[str, str]:
        """
        加载或获取公众号fakeid映射（带缓存优化）

        Args:
            gzh_names: 公众号名称列表，如果为空则使用缓存文件中的所有公众号
            cache_file: 缓存文件路径

        Returns:
            公众号名称到fakeid的映射
        """
        bizs = {}

        if cache_file.exists():
            logger.info(f"从缓存加载fakeids: {cache_file}")
            cached_bizs = load_json(cache_file)

            # 如果公众号名称列表为空，则使用缓存文件中的所有公众号
            if not gzh_names:
                bizs = cached_bizs
                logger.info(f"使用缓存文件中的所有公众号，共 {len(bizs)} 个")
            else:
                required_names = set(gzh_names)
                required_cached_bizs = {
                    name: cached_bizs[name]
                    for name in required_names & set(cached_bizs.keys())
                }
                bizs.update(required_cached_bizs)
        else:
            if not gzh_names:
                logger.warning("缓存文件不存在且未指定公众号名称，返回空字典")
                return {}

        need_names = set(gzh_names) - set(bizs.keys()) if gzh_names else set()
        if need_names:
            logger.info(f"从网络获取fakeids: {need_names}")
            for name in need_names:
                try:
                    result = self.fetch_fakeid(name)
                    if result.arr:
                        nickname = result.arr[0].nickname
                        fakeid = result.arr[0].fakeid
                        bizs[nickname] = fakeid
                        logger.info(f"成功获取公众号: {nickname} -> {fakeid}")
                    else:
                        logger.warning(f"公众号搜索结果为空: {name}")
                except SearchBizError as e:
                    logger.error(f"搜索公众号失败: {name}, 错误: {str(e)}")
            save_json(bizs, cache_file)

        return bizs

    def search_article_list(
        self, fakeid: str, begin: int, count: int
    ) -> list[ArticleListItem]:
        """
        获取文章列表

        Args:
            fakeid: 公众号fakeid
            begin: 列表起始位置
            count: 返回数量

        Returns:
            过滤后的文章列表
        """
        articles = self.fetch_article_list(fakeid, begin, count)
        valid_articles = [
            article
            for article in articles.app_msg_list
            if self.is_valid_article_link(article.link)
        ]
        return valid_articles

    def search_articles(
        self,
        fakeid: str,
        max_count: int | None = None,
        time_range: TimeRange | None = None,
    ) -> list[ArticleListItem]:
        """
        加载或获取文章链接列表（带缓存优化）

        Args:
            nickname: 公众号名称
            fakeid: 公众号fakeid
            max_count: 最大获取数量限制
            time_range: 时间范围限制

        Returns:
            文章链接列表
        """
        EACH_COUNT = 5
        # article 中有时间属性，获取所有在时间范围的文章信息，
        all_articles: list[ArticleListItem] = []
        begin = 0
        while True:
            # 获取到的文章都是倒序排列，就是由近到远的顺序，越在后面的越早
            articles = self.search_article_list(fakeid, begin, EACH_COUNT)
            all_articles += articles
            begin += EACH_COUNT
            # 如果articles为空list，说明超出范围，停止获取
            if not articles:
                logger.warning(f"公众号「{nickname}」获取到的文章为空，停止获取")
                break
            # 如果时间范围限制存在，超过start_date，停止获取
            if time_range and articles[-1].create_time < time_range.begin.timestamp():
                break
            # 如果最大数量限制存在，超过最大数量，停止获取
            if max_count and len(all_articles) >= max_count:
                logger.warning(
                    f"公众号「{nickname}」获取到的文章数量 {len(all_articles)} 已超过最大数量 {max_count}，停止获取"
                )
                break

        return all_articles

    # 剩余的时间范围 meta_file,start_time,end_time
    @staticmethod
    def get_remaining_time_range(
        meta_file: Path, need_time: TimeRange
    ) -> tuple[TimeRange, TimeRange]:
        """
        获取剩余的时间范围

        Args:
            meta_file: 元数据文件路径
            time_range: 时间范围

        Returns:
            剩余的时间范围（开始日期，结束日期）
        """
        if not meta_file.exists():
            return need_time, need_time
        meta_time = TimeRange(**load_json(meta_file))

        remaining_range, new_meta_info = match_remaining_time_range(
            meta_time, need_time
        )
        return remaining_range, new_meta_info

    def search_articles_content(
        self,
        bizs: dict[str, str],
        time_range: TimeRange,
        save_dir: Path = Path("temp/articles_info/"),
    ) -> pd.DataFrame:
        """
        获取文章内容（不带缓存优化）

        Args:
            bizs: 公众号名称到fakeid的映射
            time_range: 时间范围

        Returns:
            文章内容DataFrame
        """
        # 创建保存目录
        save_dir.mkdir(parents=True, exist_ok=True)

        for nickname, fakeid in bizs.items():
            safe_nickname = sanitize_filename(nickname)
            if TimeManager.check_file_exist(safe_nickname, save_dir):
                tm = TimeManager.load_file(safe_nickname, save_dir)
            else:
                tm = TimeManager.new()

            remaining_range = tm.match_remaining_time_range(time_range)
            if remaining_range is None:
                logger.info(f"公众号 {nickname} 已经获取到所有文章，跳过")
                continue
            articles = self.search_articles(fakeid, time_range=remaining_range)
            if not articles:
                logger.warning(f"公众号 {nickname} 没有获取到有效文章")
                continue

            df_articles = pd.DataFrame([article.model_dump() for article in articles])

            tm.append_data(df_articles)
            tm.save_file(safe_nickname, save_dir)

        # 合并bizs中对应的csv文件，并且 nickname 列为对应公众号名称
        csv_files: list[Path] = []
        for nickname in bizs.keys():
            safe_nickname = sanitize_filename(nickname)
            csv_path = save_dir / f"{safe_nickname}.csv"
            if csv_path.exists():
                csv_files.append(csv_path)
        if csv_files:
            df = pd.concat(
                [pd.read_csv(f).assign(nickname=f.stem) for f in csv_files],
                ignore_index=True,
            )
        else:
            df = pd.DataFrame()
        return df

    @staticmethod
    def download_article_content(task: ArticleDownloadTask) -> bool:
        """
        保存文章内容到Markdown文件

        Args:
            task: ArticleDownloadTask 文章下载任务

        Returns:
            是否成功保存
        """
        max_retries = task.max_retries

        task.save_dir.mkdir(parents=True, exist_ok=True)

        safe_title = sanitize_filename(task.title)
        save_path = task.save_dir / f"{safe_title}.{task.save_file}"

        if save_path.exists():
            return True

        for attempt in range(max_retries):
            try:
                content = WxMPAPI.fetch_article_content(task.url, timeout=task.timeout)
                result = save_article_content(
                    content,
                    save_path,
                    task.save_file,
                    title=task.title,
                    date_str=task.date_str,
                    link=task.url,
                    account_name=task.account_name,
                    digest=task.digest,
                    min_file_size_kb=task.min_file_size_kb,
                )
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(
                        f"获取文章内容失败（重试{max_retries}次后）: {task.title}, 错误: {e}"
                    )
                    return False
                time.sleep(1)
        return False

    @staticmethod
    def save_all_article_content(
        df: pd.DataFrame,
        save_dir: Path = Path("temp/article_content/"),
        max_workers: int = 5,
        time_range: TimeRange = None,
        save_file: Literal["md", "html"] = "md",
        min_file_size_kb: int = 3,
    ):
        """
        保存所有文章内容到Markdown文件（并发下载）

        Args:
            df: 包含文章信息的DataFrame
            save_dir: 保存目录
            max_workers: 最大并发数
            time_range: 时间范围
            save_file: 保存格式（md 或 html）
            min_file_size_kb: 最小文件大小（KB）
        """
        save_dir.mkdir(parents=True, exist_ok=True)
        # 筛选出在时间范围内的文章
        df["create_time"] = pd.to_datetime(df["create_time"])
        if time_range:
            df = df[
                (df["create_time"] >= time_range.begin)
                & (df["create_time"] <= time_range.end)
            ]

        tasks = []
        for _, row in df.iterrows():
            safe_nickname = sanitize_filename(row["nickname"])
            task = ArticleDownloadTask(
                url=row["link"],
                title=row["title"],
                save_dir=save_dir / safe_nickname,
                save_file=save_file,
                max_retries=3,
                timeout=30,
                date_str=row.get("create_time", ""),
                account_name=row.get("nickname", ""),
                digest=row.get("digest", ""),
                min_file_size_kb=min_file_size_kb,
            )
            tasks.append((task, row["link"], row["title"]))

        success_count = 0
        fail_count = 0
        skip_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(TimeRangeSpider.download_article_content, task): (
                    url,
                    title,
                )
                for task, url, title in tasks
            }

            with tqdm(total=len(futures), desc="下载文章", unit="篇") as pbar:
                for future in as_completed(futures):
                    url, title = futures[future]
                    try:
                        result = future.result()
                        if result:
                            success_count += 1
                        else:
                            fail_count += 1
                    except Exception as e:
                        fail_count += 1
                        logger.error(f"处理文章时发生异常: {title}, 错误: {e}")
                    pbar.update(1)

        logger.info(
            f"文章下载完成: 成功 {success_count} 篇, 失败 {fail_count} 篇, "
            f"跳过 {skip_count} 篇, 总计 {len(tasks)} 篇"
        )
