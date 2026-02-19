from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_serializer

from .common import BaseRequest, BaseResponse, WxMPAPIError


class ListExError(WxMPAPIError):
    """获取文章列表失败异常"""

    pass


class ListExRequest(BaseRequest):
    """获取文章列表请求参数"""

    query: str = Field(default="", description="查询字符串")
    action: str = Field(default="list_ex", description="动作")
    fakeid: str = Field(description="公众号ID")
    type: int = Field(default=9, description="类型")


class ArticleListItem(BaseModel):
    """文章列表项"""

    aid: str = Field(description="文章ID（格式：{appmsgid}_{idx}）")
    appmsgid: int = Field(description="文章消息ID")
    cover: str = Field(description="封面图URL")
    create_time: int = Field(description="创建时间戳")
    digest: str = Field(description="文章摘要")
    is_pay_subscribe: int = Field(default=0, description="是否付费订阅")
    item_show_type: int = Field(default=0, description="展示类型")
    itemidx: int = Field(description="文章索引")
    link: str = Field(description="文章链接")
    tagid: List[str] = Field(default_factory=list, description="标签ID列表")
    title: str = Field(description="文章标题")
    update_time: int = Field(description="更新时间戳")

    @field_serializer("create_time", "update_time")
    def serialize_timestamp(self, value: int) -> str:
        """将时间戳转换为格式化的日期时间字符串"""
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")

    @field_serializer("tagid")
    def serialize_tagid(self, value: List[str]) -> str:
        """将标签ID列表转换为逗号分隔的字符串"""
        return ",".join(value) if value else ""


class ListExResponse(BaseResponse):
    """文章列表API响应（list_ex）"""

    app_msg_cnt: int = Field(description="文章总数")
    app_msg_list: List[ArticleListItem] = Field(description="文章列表")
