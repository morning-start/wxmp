import re
import warnings

import requests
from fake_useragent import UserAgent
from urllib3.exceptions import InsecureRequestWarning

from .list_ex import ListExError, ListExRequest, ListExResponse
from .search_biz import SearchBizError, SearchBizRequest, SearchBizResponse
from .token import TokenError

warnings.filterwarnings("ignore", category=InsecureRequestWarning)


class WxMPAPI:
    def __init__(self, cookies: dict) -> None:
        self.cookies = cookies
        self.domain = "https://mp.weixin.qq.com"
        self.headers = {
            "User-Agent": UserAgent().random,
            "Host": "mp.weixin.qq.com",
            "Referer": "https://mp.weixin.qq.com/",
        }
        self.session = requests.Session()
        self.token = None

    def _get_token(self) -> str:
        url = self.domain
        try:
            res = self.session.get(
                url=url, headers=self.headers, cookies=self.cookies, verify=False
            )
            res.raise_for_status()

            token = re.findall(r".*?token=(\d+)", res.url)
            if token:
                return token[0]
            raise TokenError("从重定向URL中提取token失败")
        except requests.HTTPError as e:
            raise TokenError(f"HTTP请求失败: {e.response.status_code}")
        except Exception as e:
            raise TokenError(f"获取token时发生错误: {str(e)}")

    def search_fakeid(
        self, query: str, begin: int = 0, count: int = 5
    ) -> SearchBizResponse:
        url = self.domain + "/cgi-bin/searchbiz"
        params = SearchBizRequest(
            action="search_biz",
            begin=begin,
            count=count,
            query=query,
            token=self.token,
        )
        try:
            res = self.session.get(
                url=url,
                params=params.model_dump(),
                headers=self.headers,
                cookies=self.cookies,
                verify=False,
            )
            res.raise_for_status()
            return SearchBizResponse(**res.json())
        except requests.HTTPError as e:
            raise SearchBizError(f"HTTP请求失败: {e.response.status_code}")
        except Exception as e:
            raise SearchBizError(f"搜索公众号时发生错误: {str(e)}")

    def search_article_list(
        self, fakeid: str, begin: int = 0, count: int = 5
    ) -> ListExResponse:
        url = self.domain + "/cgi-bin/appmsg"
        params = ListExRequest(
            begin=begin,
            count=count,
            fakeid=fakeid,
            token=self.token,
        )
        try:
            res = self.session.get(
                url=url,
                params=params.model_dump(),
                headers=self.headers,
                cookies=self.cookies,
                verify=False,
            )
            res.raise_for_status()
            return ListExResponse(**res.json())
        except requests.HTTPError as e:
            raise ListExError(f"HTTP请求失败: {e.response.status_code}")
        except Exception as e:
            raise ListExError(f"获取文章列表时发生错误: {str(e)}")

    @staticmethod
    def is_valid_article_link(link: str) -> bool:
        """
        判断文章链接是否有效
        包含 tempkey= 的链接说明文章已删除或失效
        """
        if not link:
            return False
        # 检查是否包含 tempkey= 参数（说明文章已失效）
        if "tempkey=" in link:
            return False
        return True
