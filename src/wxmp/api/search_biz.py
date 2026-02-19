from typing import List

from pydantic import BaseModel, Field

from .common import BaseRequest, BaseResponse, WxMPAPIError


class SearchBizError(WxMPAPIError):
    """搜索公众号失败异常"""

    pass


class SearchBizRequest(BaseRequest):
    """搜索公众号请求参数"""

    query: str = Field(description="查询字符串")
    action: str = Field(default="search_biz", description="动作")


class AccountInfo(BaseModel):
    """公众号信息"""

    fakeid: str = Field(description="公众号fakeid（用于获取文章列表）")
    nickname: str = Field(description="公众号名称")
    alias: str = Field(default="", description="公众号微信号")
    round_head_img: str = Field(description="公众号头像URL")
    service_type: int = Field(description="服务类型")
    signature: str = Field(description="公众号签名")
    verify_status: int = Field(description="验证状态")


class SearchBizResponse(BaseResponse):
    """搜索公众号API响应"""

    list: List[AccountInfo] = Field(description="公众号列表")
    total: int = Field(description="搜索结果总数")
