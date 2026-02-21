# CI/CD 文档

本文档介绍 `wxmp` 项目的持续集成和持续部署（CI/CD）流程。

---

## 概述

项目使用 GitHub Actions 实现自动化发布流程，包含两个主要工作流：

1. **GitHub Release 自动发布** - 推送标签时自动创建 GitHub Release
2. **PyPI 自动发布** - GitHub Release 发布后自动上传到 PyPI

---

## 工作流架构

```
┌─────────────────┐
│  推送 Git 标签   │
│  (v1.0.0)       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  create-release.yml         │
│  - 检出代码                 │
│  - 解析标签信息             │
│  - 提取 CHANGELOG           │
│  - 创建 GitHub Release      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  GitHub Release Published   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  python-publish.yml         │
│  - 构建分发包               │
│  - 上传到 PyPI              │
└─────────────────────────────┘
```

---

## 工作流详解

### 1. GitHub Release 自动发布

**文件**: `.github/workflows/create-release.yml`

#### 触发条件

```yaml
on:
  push:
    tags:
      - 'v*.*.*'
```

当推送符合 `v*.*.*` 格式的标签时触发（如 `v1.0.0`、`v1.1.0`、`v2.0.0` 等）。

#### 工作流程

1. **检出代码**
   - 使用 `actions/checkout@v4` 检出完整仓库历史
   - 设置 `fetch-depth: 0` 获取完整历史记录

2. **解析标签信息**
   - 提取标签名（如 `v1.0.0`）
   - 提取版本号（如 `1.0.0`）

3. **提取变更日志**
   - 从 `wiki/CHANGELOG.md` 中提取对应版本的变更内容
   - 使用 AWK 脚本解析 Markdown 文件
   - 如果找不到对应版本，显示默认提示信息

4. **创建 GitHub Release**
   - 使用 `softprops/action-gh-release@v2` 创建 Release
   - 自动填充 Release 说明
   - 设置为正式发布（非草稿、非预发布）

#### 权限要求

```yaml
permissions:
  contents: write
```

需要 `contents: write` 权限才能创建 GitHub Release。

---

### 2. PyPI 自动发布

**文件**: `.github/workflows/python-publish.yml`

#### 触发条件

```yaml
on:
  release:
    types: [published]
```

当 GitHub Release 被发布（从草稿状态转为已发布）时触发。

#### 工作流程

##### Job 1: release-build

1. **检出代码**
   - 使用 `actions/checkout@v4` 检出代码

2. **设置 Python 环境**
   - 使用 `actions/setup-python@v5` 安装 Python
   - 使用最新稳定版本

3. **构建分发包**
   - 安装 `build` 工具
   - 运行 `python -m build` 构建分发包
   - 生成 `dist/` 目录，包含 `.tar.gz` 和 `.whl` 文件

4. **上传构建产物**
   - 使用 `actions/upload-artifact@v4` 上传构建产物
   - 保存为 `release-dists` 供后续 Job 使用

##### Job 2: pypi-publish

1. **下载构建产物**
   - 使用 `actions/download-artifact@v4` 下载构建产物
   - 从 `release-dists` 恢复到 `dist/` 目录

2. **发布到 PyPI**
   - 使用 `pypa/gh-action-pypi-publish@release/v1`
   - 使用 OIDC (OpenID Connect) 认证
   - 自动上传所有分发包到 PyPI

#### 权限要求

```yaml
permissions:
  contents: read
  id-token: write
```

- `contents: read` - 读取仓库内容
- `id-token: write` - OIDC 认证必需

#### 环境配置

```yaml
environment:
  name: pypi
```

使用 `pypi` 环境，可以配置部署保护规则。

---

## 使用指南

### 发布新版本

#### 步骤 1: 更新版本号

编辑 `pyproject.toml` 文件，更新版本号：

```toml
[project]
name = "wxmp"
version = "1.1.0"
```

#### 步骤 2: 更新 CHANGELOG

编辑 `wiki/CHANGELOG.md` 文件，添加新版本的变更记录：

```markdown
## [1.1.0] - 2026-02-22

### 新增
- 新功能 1
- 新功能 2

### 修复
- 修复问题 1
```

#### 步骤 3: 提交更改

```bash
git add pyproject.toml wiki/CHANGELOG.md
git commit -m "chore: 准备发布 v1.1.0"
```

#### 步骤 4: 创建标签

```bash
git tag -a v1.1.0 -m "Release v1.1.0"
```

#### 步骤 5: 推送标签

```bash
git push origin v1.1.0
```

推送标签后，GitHub Actions 会自动：
1. 创建 GitHub Release
2. 从 CHANGELOG 提取变更说明
3. 发布到 PyPI

---

### 手动发布到 PyPI

如果需要手动控制发布时机：

1. 推送标签后，GitHub Release 会自动创建
2. 在 GitHub Releases 页面查看 Release
3. 点击 "Edit release" 编辑 Release 说明
4. 确认无误后，Release 会自动触发 PyPI 发布流程

---

### 查看发布状态

#### GitHub Actions

访问仓库的 Actions 页面：
```
https://github.com/morning-start/wxmp/actions
```

查看工作流运行状态和日志。

#### GitHub Releases

访问仓库的 Releases 页面：
```
https://github.com/morning-start/wxmp/releases
```

查看已发布的版本。

#### PyPI

访问 PyPI 项目页面：
```
https://pypi.org/project/wxmp/
```

查看已发布的包版本。

---

## 配置说明

### PyPI 信任发布

项目使用 PyPI 的信任发布（Trusted Publishing）功能，无需在 GitHub 中存储 API Token。

#### 配置步骤

1. 在 PyPI 上创建项目
2. 在 PyPI 项目设置中添加发布者
3. 配置 OIDC 发布者：
   - GitHub 仓库: `morning-start/wxmp`
   - 工作流: `python-publish.yml`
   - 环境: `pypi`

详细配置步骤请参考：
- [PyPI 信任发布文档](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions OIDC 文档](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-pypi)

---

### 环境保护

建议在 GitHub 仓库设置中配置环境保护：

1. 进入仓库 Settings → Environments
2. 创建 `pypi` 环境
3. 配置部署保护规则：
   - 需要审批
   - 限制可部署的分支
   - 添加等待时间

---

## 故障排查

### GitHub Release 未创建

**可能原因**:
- 标签格式不正确（必须是 `v*.*.*` 格式）
- 标签未推送到远程仓库
- 工作流权限配置错误

**解决方法**:
```bash
# 检查标签格式
git tag -l

# 确认标签已推送
git ls-remote --tags origin

# 查看工作流日志
# 访问 Actions 页面查看详细错误信息
```

---

### CHANGELOG 未提取

**可能原因**:
- `wiki/CHANGELOG.md` 文件不存在
- 版本号格式不匹配
- AWK 脚本解析失败

**解决方法**:
1. 确保 `wiki/CHANGELOG.md` 文件存在
2. 检查版本号格式（如 `[1.0.0]`）
3. 查看工作流日志中的提取步骤

---

### PyPI 发布失败

**可能原因**:
- 信任发布未配置
- 分发包构建失败
- 版本号已存在

**解决方法**:
1. 检查 PyPI 信任发布配置
2. 查看构建步骤日志
3. 确认版本号未在 PyPI 上存在
4. 检查包名是否冲突

---

### 构建失败

**可能原因**:
- 依赖项安装失败
- Python 版本不兼容
- 构建配置错误

**解决方法**:
1. 检查 `pyproject.toml` 配置
2. 确认依赖项版本正确
3. 本地测试构建：
   ```bash
   python -m pip install build
   python -m build
   ```

---

## 最佳实践

### 版本号管理

遵循语义化版本（Semantic Versioning）：

```
MAJOR.MINOR.PATCH
```

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向下兼容的功能性新增
- **PATCH**: 向下兼容的问题修正

示例：
- `1.0.0` - 初始稳定版本
- `1.1.0` - 新增功能
- `1.1.1` - Bug 修复
- `2.0.0` - 重大更新

---

### CHANGELOG 维护

每次发布前更新 CHANGELOG：

```markdown
## [1.1.0] - 2026-02-22

### 新增
- 新功能描述

### 变更
- 功能变更说明

### 弃用
- 即将移除的功能

### 移除
- 已移除的功能

### 修复
- Bug 修复说明

### 安全
- 安全相关修复
```

---

### 发布前检查清单

在发布新版本前，确保：

- [ ] 版本号已更新（`pyproject.toml`）
- [ ] CHANGELOG 已更新（`wiki/CHANGELOG.md`）
- [ ] 所有更改已提交
- [ ] 标签已创建并推送
- [ ] 本地构建测试通过
- [ ] 文档已更新
- [ ] 测试用例通过

---

### 本地测试构建

在推送标签前，本地测试构建：

```bash
# 安装构建工具
pip install build

# 构建分发包
python -m build

# 检查构建产物
ls -la dist/

# 测试安装
pip install dist/wxmp-*.whl
```

---

## 相关资源

### 官方文档

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [GitHub Release 文档](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [PyPI 发布文档](https://packaging.python.org/tutorials/packaging-projects/)
- [PyPI 信任发布](https://docs.pypi.org/trusted-publishers/)

### 项目文档

- [项目概览](./wiki/项目概览.md)
- [贡献指南](./wiki/贡献指南.md)
- [更新日志](./wiki/CHANGELOG.md)

---

## 常见问题

### Q: 如何回滚已发布的版本？

A: GitHub Release 和 PyPI 版本一旦发布无法删除，但可以：

1. 在 GitHub 上标记为 "Pre-release"
2. 在 PyPI 上 yank（标记为已弃用）版本
3. 发布新版本修复问题

### Q: 如何发布预发布版本？

A: 在标签名中使用预发布标识符：

```bash
git tag -a v1.1.0-alpha.1 -m "Release v1.1.0-alpha.1"
git push origin v1.1.0-alpha.1
```

然后手动编辑 GitHub Release，勾选 "Set as a pre-release"。

### Q: 如何跳过 PyPI 发布？

A: 推送标签后，在 GitHub Release 页面保持草稿状态，不点击 "Publish release"。

### Q: 如何添加发布附件？

A: 在 GitHub Release 页面手动编辑，上传附件文件。

---

## 更新历史

### 2026-02-21

- 初始版本
- 添加 GitHub Release 自动发布工作流
- 添加 PyPI 自动发布工作流
- 完善文档和使用指南

---

## 贡献

如有问题或建议，请：

1. 提交 Issue: [GitHub Issues](https://github.com/morning-start/wxmp/issues)
2. 提交 Pull Request: [GitHub Pull Requests](https://github.com/morning-start/wxmp/pulls)

---

## 许可证

本项目遵循 MIT 许可证。详见 [LICENSE](./LICENSE) 文件。
