# 微信公众号 API 工具

微信公众平台（微信公众号）API 相关工具，提供公众号搜索、文章列表获取等功能。

## 项目简介

`wxmp` 是一个 Python 库，用于与微信公众平台后台 API 进行交互。通过本项目可以：

- 通过微信登录后的 cookies 获取访问 token
- 搜索公众号（根据关键词查找公众号信息）
- 获取指定公众号的文章列表
- 验证文章链接有效性

## 项目结构

```
wxmp/
├── src/wxmp/                 # 项目源码目录
│   ├── api/                  # API 模块
│   │   ├── __init__.py       # API 导出定义
│   │   ├── common.py         # 公共模型和异常定义
│   │   ├── index.py          # WxMPAPI 主类
│   │   ├── token.py          # Token 获取相关
│   │   ├── search_biz.py     # 公众号搜索 API
│   │   └── list_ex.py        # 文章列表 API
│   └── __init__.py           # 项目入口
├── pyproject.toml            # 项目配置
└── README.md                 # 项目文档
```

## 功能模块

### 1. common.py - 公共模块

定义基础模型和异常类：

- `WxMPAPIError` - 基础异常类
- `BaseRequest` - API 基础请求参数（token、begin、count、lang 等）
- `BaseResp` - 基础响应对象（ret、err_msg）
- `BaseResponse` - 带 base_resp 嵌套的响应模型
- `ErrorDetail` - 错误详情模型
- `ErrorResponse` - 错误响应模型

### 2. index.py - WxMPAPI 主类

核心 API 封装类，提供以下方法：

| 方法 | 说明 |
|------|------|
| `__init__(cookies)` | 初始化，传入微信登录后的 cookies |
| `search_fakeid(query, begin, count)` | 搜索公众号 |
| `search_article_list(fakeid, begin, count)` | 获取公众号文章列表 |
| `is_valid_article_link(link)` | 静态方法，判断文章链接是否有效 |

### 3. token.py - Token 模块

- `TokenError` - Token 获取异常
- `TokenResponse` - Token 响应模型

### 4. search_biz.py - 公众号搜索

- `SearchBizError` - 搜索异常
- `SearchBizRequest` - 搜索请求参数
- `SearchBizResponse` - 搜索响应结果
- `AccountInfo` - 公众号信息模型（fakeid、nickname、alias、头像、签名等）

### 5. list_ex.py - 文章列表

- `ListExError` - 获取文章列表异常
- `ListExRequest` - 文章列表请求参数
- `ListExResponse` - 文章列表响应
- `ArticleListItem` - 文章信息模型（标题、链接、封面、发布时间等）

## 安装

```bash
pip install wxmp
```

或从源码安装：

```bash
git clone <repository-url>
cd wxmp
pip install -e .
```

## 依赖

- Python >= 3.10
- fake-useragent >= 2.2.0
- pydantic >= 2.12.5
- urllib3 >= 2.6.3
- requests

## 快速开始

### 1. 初始化 API

首先需要获取微信公众平台的登录 cookies（在浏览器中登录 mp.weixin.qq.com 后获取）：

```python
from wxmp import WxMPAPI

cookies = {
    "wxuin": "your_wxuin",
    "pass_ticket": "your_pass_ticket",
    # ... 其他 cookies
}

api = WxMPAPI(cookies)
```

### 2. 搜索公众号

```python
from wxmp import WxMPAPI

# 搜索公众号
response = api.search_fakeid("Python")
print(f"找到 {response.total} 个结果")

for account in response.list:
    print(f"名称: {account.nickname}")
    print(f"FakeID: {account.fakeid}")
    print(f"头像: {account.round_head_img}")
    print(f"签名: {account.signature}")
```

### 3. 获取文章列表

```python
# 获取公众号文章列表
response = api.search_article_list(fakeid="公众号的fakeid")

print(f"共有 {response.app_msg_cnt} 篇文章")

for article in response.app_msg_list:
    print(f"标题: {article.title}")
    print(f"链接: {article.link}")
    print(f"创建时间: {article.create_time}")
    print(f"封面: {article.cover}")
```

### 4. 验证文章链接

```python
# 判断文章链接是否有效
is_valid = WxMPAPI.is_valid_article_link("https://mp.weixin.qq.com/s/xxx")
print(f"链接有效: {is_valid}")
```

## 数据模型

### AccountInfo - 公众号信息

| 字段 | 类型 | 说明 |
|------|------|------|
| fakeid | str | 公众号 ID |
| nickname | str | 公众号名称 |
| alias | str | 公众号微信号 |
| round_head_img | str | 公众号头像 URL |
| service_type | int | 服务类型 |
| signature | str | 公众号签名 |
| verify_status | int | 验证状态 |

### ArticleListItem - 文章信息

| 字段 | 类型 | 说明 |
|------|------|------|
| aid | str | 文章 ID（格式：{appmsgid}_{idx}） |
| appmsgid | int | 文章消息 ID |
| cover | str | 封面图 URL |
| create_time | str | 创建时间（格式化字符串） |
| digest | str | 文章摘要 |
| link | str | 文章链接 |
| title | str | 文章标题 |
| update_time | str | 更新时间（格式化字符串） |

## 异常处理

```python
from wxmp import WxMPAPI
from wxmp.api import TokenError, SearchBizError, ListExError

try:
    api = WxMPAPI(cookies)
    response = api.search_fakeid("Python")
except TokenError as e:
    print(f"Token 获取失败: {e}")
except SearchBizError as e:
    print(f"搜索公众号失败: {e}")
except ListExError as e:
    print(f"获取文章列表失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 注意事项

1. **Cookies 获取**：使用本库前需要先在浏览器中登录微信公众平台，然后从浏览器开发者工具中获取 cookies。
2. **频率限制**：请合理控制请求频率，避免被微信限制。
3. **链接有效性**：包含 `tempkey=` 参数的文章链接表示文章已删除或失效。

## License

MIT License
