import json
from datetime import datetime
from typing import Any, List, Optional

from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from .common import BaseRequest, BaseResponse, WxMPAPIError


class ListExError(WxMPAPIError):
    """获取文章列表失败异常"""

    pass


class ListExRequest(BaseRequest):
    """获取文章列表请求参数"""

    query: str = Field(default="", description="查询字符串")
    action: str = Field(default="list_ex", description="动作")
    fakeid: str = Field(description="公众号ID")
    type: str = Field(default="9", description="类型")


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
    """文章列表 API 响应（list_ex）"""

    app_msg_cnt: Optional[int] = Field(default=0, description="文章总数")
    app_msg_list: List[ArticleListItem] = Field(
        default_factory=list, description="文章列表"
    )


class SentInfo(BaseModel):
    """发送信息"""

    time: int = Field(description="发送时间戳")
    func_flag: int = Field(description="功能标志")
    is_send_all: bool = Field(description="是否群发")
    is_published: int = Field(description="是否已发布")

    @field_serializer("time")
    def serialize_time(self, value: int) -> str:
        """将时间戳转换为格式化的日期时间字符串"""
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")


class AppMsgInfoItem(BaseModel):
    """appmsg_info 列表项"""

    share_type: int = Field(default=0, description="分享类型")
    appmsgid: int = Field(description="文章消息 ID")
    vote_id: List[Any] = Field(default_factory=list, description="投票 ID 列表")
    super_vote_id: List[Any] = Field(
        default_factory=list, description="超级投票 ID 列表"
    )
    smart_product: int = Field(default=0, description="智能产品标志")
    appmsg_like_type: int = Field(default=0, description="文章喜欢类型")
    itemidx: int = Field(description="文章索引")
    is_pay_subscribe: int = Field(default=0, description="是否付费订阅")
    is_from_transfer: int = Field(default=0, description="是否来自转载")
    open_fansmsg: int = Field(default=0, description="是否开启粉丝消息")
    share_imageinfo: List[Any] = Field(default_factory=list, description="分享图片信息")
    item_show_type: int = Field(default=0, description="展示类型")
    audio_in_appmsg: List[Any] = Field(default_factory=list, description="文章内音频")
    modify_detail_wording: List[Any] = Field(
        default_factory=list, description="修改详情措辞"
    )


class AppMsgExItem(BaseModel):
    """appmsgex 列表项"""

    aid: str = Field(description="文章 ID（格式：{appmsgid}_{idx}）")
    title: str = Field(description="文章标题")
    cover: str = Field(description="封面图 URL")
    link: str = Field(description="文章链接")
    digest: str = Field(description="文章摘要")
    update_time: int = Field(description="更新时间戳")
    appmsgid: int = Field(description="文章消息 ID")
    itemidx: int = Field(description="文章索引")
    item_show_type: int = Field(default=0, description="展示类型")
    author_name: str = Field(default="", description="作者名称")
    tagid: List[str] = Field(default_factory=list, description="标签 ID 列表")
    create_time: int = Field(description="创建时间戳")
    is_pay_subscribe: int = Field(default=0, description="是否付费订阅")
    has_red_packet_cover: int = Field(default=0, description="是否有红包封面")
    album_id: str = Field(default="0", description="专辑 ID")
    checking: int = Field(default=0, description="审核状态")
    media_duration: str = Field(default="0:00", description="媒体时长")
    mediaapi_publish_status: int = Field(default=0, description="媒体 API 发布状态")
    copyright_type: int = Field(default=0, description="版权类型")
    appmsg_album_infos: List[Any] = Field(
        default_factory=list, description="文章专辑信息"
    )
    pay_album_info: dict = Field(default_factory=dict, description="付费专辑信息")
    is_deleted: bool = Field(default=False, description="是否已删除")
    ban_flag: int = Field(default=0, description="禁止标志")
    pic_cdn_url_235_1: str = Field(default="", description="235:1 比例图片 CDN URL")
    pic_cdn_url_16_9: str = Field(default="", description="16:9 比例图片 CDN URL")
    pic_cdn_url_3_4: str = Field(default="", description="3:4 比例图片 CDN URL")
    pic_cdn_url_1_1: str = Field(default="", description="1:1 比例图片 CDN URL")
    line_info: dict = Field(default_factory=dict, description="行信息")
    copyright_stat: int = Field(default=0, description="版权统计")
    is_rumor_refutation: int = Field(default=0, description="是否辟谣")
    multi_picture_cover: int = Field(default=0, description="多图封面标志")
    share_imageinfo: List[Any] = Field(default_factory=list, description="分享图片信息")

    @field_serializer("create_time", "update_time")
    def serialize_timestamp(self, value: int) -> str:
        """将时间戳转换为格式化的日期时间字符串"""
        return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")

    @field_serializer("tagid")
    def serialize_tagid(self, value: List[str]) -> str:
        """将标签 ID 列表转换为逗号分隔的字符串"""
        return ",".join(value) if value else ""


class PublishInfo(BaseModel):
    """发布信息"""

    type: int = Field(description="类型")
    msgid: int = Field(description="消息 ID")
    sent_info: SentInfo = Field(description="发送信息")
    appmsg_info: List[AppMsgInfoItem] = Field(
        default_factory=list, description="文章消息信息列表"
    )
    appmsgex: List[AppMsgExItem] = Field(
        default_factory=list, description="文章扩展信息列表"
    )


class PublishListItem(BaseModel):
    """发布列表项"""

    publish_type: int = Field(description="发布类型")
    publish_info: str = Field(description="发布信息（JSON 字符串）")
    publish_info_parsed: Optional[PublishInfo] = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def parse_publish_info_validator(self) -> "PublishListItem":
        """解析 publish_info JSON 字符串"""
        try:
            self.publish_info_parsed = PublishInfo.model_validate(
                json.loads(self.publish_info)
            )
        except (json.JSONDecodeError, Exception):
            pass
        return self


class PublishPage(BaseModel):
    """发布页面信息"""

    total_count: int = Field(description="总数量")
    publish_count: int = Field(description="发布数量")
    masssend_count: int = Field(description="群发数量")
    publish_list: List[PublishListItem] = Field(
        default_factory=list, description="发布列表"
    )


class ListExPublishRequest(BaseRequest):
    """获取文章列表请求参数"""

    query: str = Field(default="", description="查询字符串")
    sub_action: str = Field(default="list_ex", description="子动作")
    fakeid: str = Field(description="公众号ID")
    type: str = Field(default="101_1", description="类型")


class ListExPublishResponse(BaseResponse):
    """已发布文章列表 API 响应（list_ex）"""

    is_admin: bool = Field(default=True, description="是否管理员")
    publish_page: Optional[str] = Field(
        default=None, description="发布页面信息（JSON 字符串）"
    )
    publish_page_parsed: Optional[PublishPage] = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def parse_publish_page_validator(self) -> "ListExPublishResponse":
        """解析 publish_page JSON 字符串"""
        if self.publish_page:
            try:
                self.publish_page_parsed = PublishPage.model_validate(
                    json.loads(self.publish_page)
                )
            except (json.JSONDecodeError, Exception):
                pass
        return self

    @property
    def app_msg_cnt(self) -> int:
        """获取文章总数"""
        return len(self.app_msg_list)

    @property
    def app_msg_list(self) -> List[ArticleListItem]:
        """获取所有文章列表（转换为 ArticleListItem 格式）"""
        if not self.publish_page_parsed:
            return []

        articles = []
        for publish_item in self.publish_page_parsed.publish_list:
            if publish_item.publish_info_parsed:
                for appmsgex in publish_item.publish_info_parsed.appmsgex:
                    # 将 AppMsgExItem 转换为 ArticleListItem
                    article = ArticleListItem(
                        aid=appmsgex.aid,
                        appmsgid=appmsgex.appmsgid,
                        cover=appmsgex.cover,
                        create_time=appmsgex.create_time,
                        digest=appmsgex.digest,
                        is_pay_subscribe=appmsgex.is_pay_subscribe,
                        item_show_type=appmsgex.item_show_type,
                        itemidx=appmsgex.itemidx,
                        link=appmsgex.link,
                        tagid=appmsgex.tagid,
                        title=appmsgex.title,
                        update_time=appmsgex.update_time,
                    )
                    articles.append(article)
        return articles

    @property
    def total_count(self) -> int:
        """获取总数量"""
        return self.publish_page_parsed.total_count if self.publish_page_parsed else 0

    @property
    def publish_count(self) -> int:
        """获取发布数量"""
        return self.publish_page_parsed.publish_count if self.publish_page_parsed else 0

    @property
    def masssend_count(self) -> int:
        """获取群发数量"""
        return (
            self.publish_page_parsed.masssend_count if self.publish_page_parsed else 0
        )

    @property
    def publish_list(self) -> List[PublishListItem]:
        """获取发布列表"""
        return self.publish_page_parsed.publish_list if self.publish_page_parsed else []

    def get_publish_list_by_type(self, publish_type: int) -> List[PublishListItem]:
        """根据发布类型过滤发布列表"""
        return [item for item in self.publish_list if item.publish_type == publish_type]

    def get_all_articles(self) -> List[tuple[PublishListItem, AppMsgExItem]]:
        """获取所有文章（展平为 (发布项，文章) 元组列表）"""
        articles = []
        for publish_item in self.publish_list:
            if publish_item.publish_info_parsed:
                for appmsgex in publish_item.publish_info_parsed.appmsgex:
                    articles.append((publish_item, appmsgex))
        return articles

    def get_article_links(self) -> List[str]:
        """获取所有文章链接"""
        links = []
        for publish_item in self.publish_list:
            if publish_item.publish_info_parsed:
                for appmsgex in publish_item.publish_info_parsed.appmsgex:
                    if appmsgex.link:
                        links.append(appmsgex.link)
        return links
