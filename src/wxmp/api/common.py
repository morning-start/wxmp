from typing import Optional

from pydantic import BaseModel, Field


class WxMPAPIError(Exception):
    """微信MP API基础异常类"""

    pass


class BaseRequest(BaseModel):
    """API基础请求参数"""

    token: str = Field(description="授权token")
    begin: int = Field(default=0, description="列表起始位置")
    count: int = Field(default=5, description="返回消息条数，一个消息可能包含多个文章")
    lang: str = Field(default="zh_CN", description="语言")
    f: str = Field(default="json", description="数据格式")
    ajax: int = Field(default=1, description="是否为ajax请求")


class BaseResp(BaseModel):
    """基础响应对象（微信API标准格式）"""

    ret: int = Field(description="返回码，0表示成功")
    err_msg: str = Field(default="ok", description="返回信息")


class BaseResponse(BaseModel):
    """API基础响应模型（带base_resp嵌套格式）"""

    base_resp: BaseResp = Field(description="基础响应对象")


class ErrorDetail(BaseModel):
    """错误详情模型"""

    code: int = Field(description="错误码")
    message: str = Field(description="错误信息")
    details: Optional[str] = Field(default=None, description="错误详情")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    base_resp: ErrorDetail = Field(description="基础响应")
