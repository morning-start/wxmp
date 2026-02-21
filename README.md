# 微信公众号 API 工具

微信公众平台（微信公众号）API 相关工具，提供公众号搜索、文章列表获取、文章内容下载等功能。

**项目地址**: https://github.com/morning-start/wxmp

## 项目简介

`wxmp` 是一个 Python 库，用于与微信公众平台后台 API 进行交互。通过本项目可以：

- 通过微信登录后的 cookies 获取访问 token
- 搜索公众号（根据关键词查找公众号信息）
- 获取指定公众号的文章列表
- 验证文章链接有效性
- 下载文章内容并转换为 Markdown 格式
- 支持时间范围缓存和增量更新
- 支持并发下载

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
response = api.search_fakeid("Python")
for account in response.list:
    print(f"名称: {account.nickname}")
```

### 3. 使用时间范围爬虫（推荐）

```python
from wxmp.spider import TimeRangeSpider
from datetime import datetime

spider = TimeRangeSpider.from_cookies_file("cookies.json")
bizs = spider.load_or_search_bizs(["Python编程"])

time_range = TimeRange(
    begin=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31)
)

df = spider.search_articles_content(bizs, time_range)
spider.save_all_article_content(df, save_dir="temp/article_content/")
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
- [更新日志](./wiki/CHANGELOG.md) - 版本历史、变更记录

## License

MIT License
