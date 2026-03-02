<!--
版本: 2.3.0
更新日期: 2026-03-03
状态: Published
-->

# 微信公众号 API 工具

微信公众平台（微信公众号）API 相关工具，提供公众号搜索、文章列表获取、文章内容下载等功能。

**项目地址**: https://github.com/morning-start/wxmp

---

## 项目简介

`wxmp` 是一个 Python 库，用于与微信公众平台后台 API 进行交互。通过本项目可以：

- 通过微信登录后的 cookies 获取访问 token
- 搜索公众号（根据关键词查找公众号信息）
- 获取指定公众号的文章列表
- 验证文章链接有效性
- 下载文章内容并转换为 Markdown 格式
- 支持时间范围缓存和增量更新
- 支持并发下载

## 核心特性

- **API 封装**: 完整封装微信公众平台后台 API
- **缓存优化**: 支持 FakeID 缓存和时间范围缓存，避免重复获取
- **并发下载**: 支持多线程并发下载文章内容
- **格式转换**: 自动将 HTML 文章转换为 Markdown 格式
- **灵活扩展**: 用户可直接使用已有爬虫或基于 API 构建自定义爬虫
- **增量更新**: 支持时间范围缓存，只获取新增文章

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | >= 3.10 | 开发语言 |
| Pydantic | >= 2.12.5 | 数据模型验证 |
| Requests | >= 2.32.5 | HTTP 请求 |
| Pandas | >= 2.3.3 | 数据处理 |
| Loguru | >= 0.7.3 | 日志记录 |
| tqdm | >= 4.67.3 | 进度条显示 |
| fake-useragent | >= 2.2.0 | 随机 User-Agent |

## 安装

```bash
pip install wxmp
```

或从源码安装：

```bash
git clone https://github.com/morning-start/wxmp.git
cd wxmp
pip install -e .
```

## 快速开始

### 1. 初始化 API

```python
from wxmp import WxMPAPI

cookies = {
    "wxuin": "your_wxuin",
    "pass_ticket": "your_pass_ticket",
}

api = WxMPAPI(cookies)
```

### 2. 搜索公众号

```python
response = api.fetch_fakeid("Python")
for account in response.arr:
    print(f"名称: {account.nickname}")
    print(f"FakeID: {account.fakeid}")
```

### 3. 使用时间范围爬虫（推荐）

```python
from wxmp.spider import TimeRangeSpider
from wxmp.tools.time_manager import TimeRange
from datetime import datetime
from pathlib import Path

spider = TimeRangeSpider.from_cookies_file("cookies.json")
bizs = spider.load_or_search_bizs(["Python编程"])

time_range = TimeRange(
    begin=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31)
)

df = spider.search_articles_content(bizs, time_range)
spider.save_all_article_content(
    df=df,
    save_dir=Path("temp/article_content/"),
    time_range=time_range
)
```

## 项目结构

```
wxmp/
├── src/wxmp/                    # 源码目录
│   ├── api/                     # API 层 - 基础 API 封装
│   │   ├── __init__.py
│   │   ├── common.py           # 公共模型和异常
│   │   ├── index.py            # WxMPAPI 主类
│   │   ├── token.py            # Token 获取
│   │   ├── search_biz.py       # 公众号搜索 API
│   │   └── list_ex.py          # 文章列表 API
│   ├── spider/                  # Spider 层 - 业务逻辑层
│   │   ├── __init__.py
│   │   └── time_range_spider.py # 时间范围爬虫
│   └── tools/                   # Tools 层 - 工具层
│       ├── __init__.py
│       ├── article.py          # 文章内容处理
│       ├── file.py             # 文件操作工具
│       └── time_manager.py     # 时间范围缓存管理
├── wiki/                        # 项目文档
├── pyproject.toml              # 项目配置
└── README.md                   # 项目说明
```

## 文档

详细文档请查看 [Wiki](./wiki/README.md)：

- [项目概览](./wiki/项目概览.md) - 项目简介、技术栈、架构概览
- [架构设计](./wiki/架构设计.md) - 设计原则、模块设计、缓存策略
- [API 文档](./wiki/API文档.md) - API 层完整文档、数据模型、异常类
- [使用指南](./wiki/使用指南.md) - 快速开始、使用场景、最佳实践
- [数据流动与状态管理](./wiki/数据流动与状态管理.md) - 数据流转、状态机、缓存策略
- [贡献指南](./wiki/贡献指南.md) - 如何贡献代码、开发环境设置
- [常见问题](./wiki/常见问题.md) - 常见问题和解决方案
- [CHANGELOG](./CHANGELOG.md) - 版本历史、变更记录

## License

MIT License
