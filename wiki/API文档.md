# API 文档

## API 层概述

API 层提供微信公众平台后台 API 的基础封装，所有 API 调用都通过 `WxMPAPI` 类进行。

## WxMPAPI 类

### 初始化

```python
class WxMPAPI:
    def __init__(self, cookies: dict[str, str]) -> None
```

**参数**:
- `cookies`: 微信公众平台登录后的 cookies 字典

**示例**:
```python
from wxmp import WxMPAPI

cookies = {
    "wxuin": "your_wxuin",
    "pass_ticket": "your_pass_ticket",
    # ... 其他 cookies
}

api = WxMPAPI(cookies)
```

### 方法列表

#### 1. _fetch_token

获取访问 token（内部方法）。

```python
def _fetch_token(self) -> str
```

**返回值**:
- `str`: 访问 token

**异常**:
- `TokenError`: Token 获取失败

**说明**:
- 自动从微信公众平台主页获取 token
- 在初始化时自动调用

---

#### 2. fetch_fakeid

搜索公众号。

```python
def fetch_fakeid(
    self,
    query: str,
    begin: int = 0,
    count: int = 5
) -> SearchBizResponse
```

**参数**:
- `query`: 搜索关键词
- `begin`: 起始位置（默认 0）
- `count`: 返回数量（默认 5）

**返回值**:
- `SearchBizResponse`: 搜索响应对象

**异常**:
- `SearchBizError`: 搜索失败

**示例**:
```python
response = api.fetch_fakeid("Python")
print(f"找到 {response.total} 个结果")

for account in response.list:
    print(f"名称: {account.nickname}")
    print(f"FakeID: {account.fakeid}")
```

---

#### 3. fetch_article_list

获取公众号文章列表。

```python
def fetch_article_list(
    self,
    fakeid: str,
    begin: int = 0,
    count: int = 5
) -> ListExResponse
```

**参数**:
- `fakeid`: 公众号 fakeid
- `begin`: 起始位置（默认 0）
- `count`: 返回数量（默认 5）

**返回值**:
- `ListExResponse`: 文章列表响应对象

**异常**:
- `ListExError`: 获取文章列表失败

**示例**:
```python
response = api.fetch_article_list(fakeid="MzI...")
print(f"共有 {response.app_msg_cnt} 篇文章")

for article in response.app_msg_list:
    print(f"标题: {article.title}")
    print(f"链接: {article.link}")
```

---

#### 4. is_valid_article_link

判断文章链接是否有效（静态方法）。

```python
@staticmethod
def is_valid_article_link(link: str) -> bool
```

**参数**:
- `link`: 文章链接

**返回值**:
- `bool`: 链接是否有效

**说明**:
- 包含 `tempkey=` 参数的链接表示文章已删除或失效

**示例**:
```python
is_valid = WxMPAPI.is_valid_article_link("https://mp.weixin.qq.com/s/xxx")
print(f"链接有效: {is_valid}")
```

---

#### 5. fetch_article_content

获取文章内容（静态方法）。

```python
@staticmethod
def fetch_article_content(link: str, timeout: int = 10) -> str
```

**参数**:
- `link`: 文章链接
- `timeout`: 超时时间（秒，默认 10）

**返回值**:
- `str`: 文章 HTML 内容

**异常**:
- `requests.HTTPError`: HTTP 请求失败

**示例**:
```python
html = WxMPAPI.fetch_article_content("https://mp.weixin.qq.com/s/xxx")
print(html)
```

---

#### 6. fetch_multi_article_content

批量获取文章内容（异步静态方法）。

```python
@staticmethod
async def fetch_multi_article_content(
    links: list[str],
    timeout: int = 10
) -> list[str]
```

**参数**:
- `links`: 文章链接列表
- `timeout`: 超时时间（秒，默认 10）

**返回值**:
- `list[str]`: 文章 HTML 内容列表（顺序与输入一致）

**示例**:
```python
import asyncio

links = [
    "https://mp.weixin.qq.com/s/xxx1",
    "https://mp.weixin.qq.com/s/xxx2",
]

htmls = asyncio.run(WxMPAPI.fetch_multi_article_content(links))
```

---

## 数据模型

### TokenResponse

Token 响应模型。

```python
class TokenResponse(BaseModel):
    pass
```

---

### SearchBizRequest

公众号搜索请求模型。

```python
class SearchBizRequest(BaseModel):
    action: str = "search_biz"
    begin: int = 0
    count: int = 5
    query: str = ""
    token: str = ""
```

---

### SearchBizResponse

公众号搜索响应模型。

```python
class SearchBizResponse(BaseModel):
    base_resp: BaseResp
    list: list[AccountInfo]
    total: int
```

---

### AccountInfo

公众号信息模型。

```python
class AccountInfo(BaseModel):
    fakeid: str
    nickname: str
    alias: str
    round_head_img: str
    service_type: int
    verify_flag: int
    signature: str
```

**字段说明**:
- `fakeid`: 公众号 ID
- `nickname`: 公众号名称
- `alias`: 公众号微信号
- `round_head_img`: 公众号头像 URL
- `service_type`: 服务类型
- `verify_flag`: 验证标志
- `signature`: 公众号签名

---

### ListExRequest

文章列表请求模型。

```python
class ListExRequest(BaseModel):
    begin: int = 0
    count: int = 5
    fakeid: str = ""
    token: str = ""
    type: int = 0
    query: str = ""
```

---

### ListExResponse

文章列表响应模型。

```python
class ListExResponse(BaseModel):
    base_resp: BaseResp
    app_msg_cnt: int
    app_msg_list: list[ArticleListItem]
```

**字段说明**:
- `app_msg_cnt`: 文章总数
- `app_msg_list`: 文章列表

---

### ArticleListItem

文章信息模型。

```python
class ArticleListItem(BaseModel):
    aid: str
    appmsgid: int
    cover: str
    create_time: int
    digest: str
    link: str
    title: str
    update_time: int
```

**字段说明**:
- `aid`: 文章 ID（格式：`{appmsgid}_{idx}`）
- `appmsgid`: 文章消息 ID
- `cover`: 封面图 URL
- `create_time`: 创建时间（时间戳）
- `digest`: 文章摘要
- `link`: 文章链接
- `title`: 文章标题
- `update_time`: 更新时间（时间戳）

---

### BaseResp

基础响应模型。

```python
class BaseResp(BaseModel):
    ret: int
    err_msg: str
```

**字段说明**:
- `ret`: 返回码（0 表示成功）
- `err_msg`: 错误信息

---

## 异常类

### WxMPAPIError

基础异常类。

```python
class WxMPAPIError(Exception):
    pass
```

---

### TokenError

Token 获取异常。

```python
class TokenError(WxMPAPIError):
    pass
```

**触发场景**:
- Cookie 无效
- 网络请求失败
- Token 提取失败

---

### SearchBizError

搜索公众号异常。

```python
class SearchBizError(WxMPAPIError):
    pass
```

**触发场景**:
- 搜索关键词无效
- 网络请求失败
- 响应解析失败

---

### ListExError

获取文章列表异常。

```python
class ListExError(WxMPAPIError):
    pass
```

**触发场景**:
- FakeID 无效
- 网络请求失败
- 响应解析失败

---

## 使用示例

### 完整示例

```python
from wxmp import WxMPAPI, TokenError, SearchBizError, ListExError

# 1. 初始化 API
cookies = {
    "wxuin": "your_wxuin",
    "pass_ticket": "your_pass_ticket",
}

try:
    api = WxMPAPI(cookies)
    print("API 初始化成功")

    # 2. 搜索公众号
    response = api.fetch_fakeid("Python")
    print(f"找到 {response.total} 个结果")

    if response.list:
        fakeid = response.list[0].fakeid
        nickname = response.list[0].nickname
        print(f"选择公众号: {nickname}")

        # 3. 获取文章列表
        article_response = api.fetch_article_list(fakeid)
        print(f"共有 {article_response.app_msg_cnt} 篇文章")

        # 4. 获取文章内容
        if article_response.app_msg_list:
            article = article_response.app_msg_list[0]
            if api.is_valid_article_link(article.link):
                html = api.fetch_article_content(article.link)
                print(f"获取文章成功: {article.title}")
            else:
                print("文章已失效")

except TokenError as e:
    print(f"Token 获取失败: {e}")
except SearchBizError as e:
    print(f"搜索公众号失败: {e}")
except ListExError as e:
    print(f"获取文章列表失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 注意事项

1. **Cookie 获取**: 需要先在浏览器中登录微信公众平台，然后从开发者工具中获取 cookies
2. **频率限制**: 请合理控制请求频率，避免被微信限制
3. **Token 有效期**: Token 可能会过期，建议定期重新获取
4. **链接有效性**: 包含 `tempkey=` 参数的文章链接表示文章已删除或失效
5. **网络超时**: 建议设置合理的超时时间，避免长时间等待
