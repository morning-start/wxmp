# 更新日志

本文档记录 `wxmp` 项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### 计划中
- 支持更多文章格式导出（PDF、EPUB）
- 添加文章内容分析功能
- 支持多账号管理
- 添加 Web 界面

---

## [1.0.2] - 2026-02-21

### 修复
- 优化日志输出，提升调试体验
- 改进时间范围匹配算法的边界条件处理

---

## [1.0.1] - 2026-02-21

### 修复
- 合并 CI/CD 工作流，统一从标签发布
- 优化发布流程，删除独立的 create-release.yml
- 修复 CHANGELOG.md 路径引用（从 wiki 目录移到根目录）

### 变更
- python-publish.yml 现在支持标签推送触发
- 整合 GitHub Release 创建功能到单一工作流
- 简化维护，只需管理一个工作流文件

---

## [1.0.0] - 2026-02-21

### 新增
- **API 层**
  - 完整封装微信公众平台后台 API
  - Token 自动获取和管理
  - 公众号搜索 API
  - 文章列表获取 API
  - 文章内容获取 API
  - 文章链接有效性验证

- **Spider 层**
  - TimeRangeSpider 时间范围爬虫
  - FakeID 缓存管理
  - 时间范围缓存优化
  - 增量更新支持
  - 并发下载文章内容
  - 自动去重和排序

- **Tools 层**
  - 文件名清理工具
  - JSON/HTML/Markdown 文件读写
  - HTML 转 Markdown 转换器
  - YAML front matter 生成
  - 文章内容保存工具

- **数据模型**
  - TimeRange 时间范围模型
  - ArticleDownloadTask 下载任务模型
  - 完整的 API 响应模型

- **文档**
  - 项目概览文档
  - 架构设计文档
  - API 文档
  - 使用指南
  - 数据流动与状态管理文档
  - 贡献指南

- **测试**
  - 时间范围匹配算法测试
  - 11 个测试用例覆盖所有场景

### 特性
- 分层架构设计（API 层、Spider 层、Tools 层）
- Cache Aside 缓存策略
- 时间范围智能匹配算法
- 多线程并发下载
- 自动重试机制
- 文件大小检查
- 进度条显示
- 日志记录

### 技术栈
- Python >= 3.10
- Pydantic >= 2.12.5（数据模型验证）
- Requests >= 2.32.5（HTTP 请求）
- Pandas >= 2.3.3（数据处理）
- Loguru >= 0.7.3（日志记录）
- tqdm >= 4.67.3（进度条显示）
- fake-useragent >= 2.2.0（随机 User-Agent）

---

## 版本说明

### 版本号格式

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向下兼容的功能性新增
- **PATCH**: 向下兼容的问题修正

### 变更类型

- **新增**: 新功能
- **变更**: 现有功能的变更
- **弃用**: 即将移除的功能
- **移除**: 已移除的功能
- **修复**: Bug 修复
- **安全**: 安全相关的修复

---

## 贡献者

感谢所有为项目做出贡献的开发者！

- morning-start - 项目创建者

---

## 链接

- 项目主页: https://github.com/morning-start/wxmp
- 问题反馈: https://github.com/morning-start/wxmp/issues
- 贡献指南: [贡献指南](./贡献指南.md)
