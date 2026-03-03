import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

from .converters import HTMLConverter, HTMLToMarkdownConverter
from .file import save_html, save_markdown
from .size_parser import parse_file_size


@dataclass
class ArticleMetadata:
    """文章元数据"""

    title: str = ""
    date_str: str = ""
    link: str = ""
    account_name: str = ""
    digest: str = ""

    def generate_yaml(self) -> str:
        """
        生成 YAML front matter 格式的元数据

        Args:
            metadata: 文章元数据

        Returns:
            YAML front matter 字符串
        """
        yaml_front_matter = "---\n"
        if self.title:
            yaml_front_matter += f"title: {self.title}\n"
        if self.date_str:
            yaml_front_matter += f"date: {self.date_str}\n"
        if self.link:
            yaml_front_matter += f"link: {self.link}\n"
        if self.account_name:
            yaml_front_matter += f"account: {self.account_name}\n"
        if self.digest:
            yaml_front_matter += f"summary: {self.digest}\n"
        yaml_front_matter += "---\n"
        return yaml_front_matter


class ArticleDownloader:
    """
    文章下载器

    封装文章下载、转换、保存的完整流程，支持重试机制和文件大小检查。

    Example:
        >>> downloader = ArticleDownloader(
        ...     max_retries=3,
        ...     retry_delay=1.0,
        ...     min_file_size="3KB",
        ... )
        >>> metadata = ArticleMetadata(
        ...     title="示例文章",
        ...     date_str="2024-01-01",
        ...     link="https://example.com/article",
        ...     account_name="示例公众号",
        ... )
        >>> success = downloader.download(
        ...     url="https://example.com/article",
        ...     save_path=Path("articles/example.md"),
        ...     metadata=metadata,
        ...     fetch_func=lambda url, timeout: requests.get(url, timeout=timeout).text,
        ... )
    """

    def __init__(
        self,
        *,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: int = 30,
        save_format: Literal["md", "html"] = "md",
        min_file_size: str = "200B",
        converter: HTMLConverter | None = None,
    ):
        """
        初始化文章下载器

        Args:
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
            timeout: 请求超时时间（秒）
            save_format: 保存格式（"md" 或 "html"）
            min_file_size: 最小文件大小（支持单位：B, KB, MB, GB），小于此值的文件会被删除
            converter: HTML 转换器，默认使用 HTMLToMarkdownConverter
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.save_format = save_format
        self.min_file_size_bytes = parse_file_size(min_file_size)
        self.converter = converter or HTMLToMarkdownConverter()

    def download(
        self,
        url: str,
        save_path: Path,
        metadata: ArticleMetadata,
        fetch_func: Callable[[str, int], str],
    ) -> bool:
        """
        下载文章并保存

        Args:
            url: 文章 URL
            save_path: 保存路径
            metadata: 文章元数据
            fetch_func: 获取文章内容的函数，接收 (url, timeout) 返回 HTML 内容

        Returns:
            是否成功保存
        """
        save_path.parent.mkdir(parents=True, exist_ok=True)

        if save_path.exists():
            return True

        for attempt in range(self.max_retries):
            try:
                content = fetch_func(url, self.timeout)
                return self._save_content(content, save_path, metadata)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return False
                time.sleep(self.retry_delay)

        return False

    def _save_content(
        self, html: str, save_path: Path, metadata: ArticleMetadata
    ) -> bool:
        """
        保存文章内容

        Args:
            html: HTML 内容
            save_path: 保存路径
            metadata: 文章元数据

        Returns:
            是否成功保存
        """
        try:
            if self.save_format == "md":
                yaml_front_matter = metadata.generate_yaml()
                main_content = self._extract_main_content(html)
                markdown_content = yaml_front_matter + self.converter.convert(
                    main_content
                )
                save_markdown(markdown_content, save_path)
            elif self.save_format == "html":
                save_html(html, save_path)

            return self._check_file_size(save_path)

        except Exception:
            self._cleanup_on_error(save_path)
            return False

    def _extract_main_content(self, html: str) -> str:
        """
        提取文章主体内容

        Args:
            html: HTML 内容

        Returns:
            主体内容 HTML
        """
        import re

        content_match = re.search(
            r'<div[^>]*id="js_content"[^>]*>(.*?)</div>', html, re.DOTALL
        )

        if content_match:
            return content_match.group(1)

        body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL)
        return body_match.group(1) if body_match else html

    def _check_file_size(self, save_path: Path) -> bool:
        """
        检查文件大小是否满足要求

        Args:
            save_path: 文件路径

        Returns:
            文件大小是否满足要求
        """
        file_size = save_path.stat().st_size

        if file_size < self.min_file_size_bytes:
            save_path.unlink()
            return False

        return True

    def _cleanup_on_error(self, save_path: Path) -> None:
        """
        出错时清理文件

        Args:
            save_path: 文件路径
        """
        if save_path.exists():
            try:
                save_path.unlink()
            except Exception:
                pass
