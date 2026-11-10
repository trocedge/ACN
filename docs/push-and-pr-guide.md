# 推送分支与提交 PR 指引

> 版本：v1.0 ｜ 日期：2026-11-10
> 本文件是通用操作说明，**不含任何账号、令牌或本机绝对路径**；凭据一律由操作者本人在浏览器授权。

## 背景

GitHub 已停用「用户名 + 密码」的 Git 推送认证，必须走浏览器 OAuth 授权或 Personal Access Token。
自动化执行环境无法弹出交互式授权窗口，因此首次推送需要由有写权限的成员在本机终端完成一次授权。

## 前置条件

| 项 | 要求 |
|---|---|
| 账号 | 已加入本仓库 Collaborator，具备分支推送权限 |
| 浏览器 | 已登录该 GitHub 账号 |
| 分支 | `feat/compact-data-format`（相对 `main` 领先若干提交） |
| 身份 | 仓库局部 `git config user.name/email` 已设置，不依赖全局配置 |

## 步骤

### 1. 确认权限并接受邀请

在浏览器登录被授权的账号（点右上角头像确认用户名），打开仓库主页。

若出现「已邀请您参与此代码库的协作 / 查看邀请」横幅，说明邀请**尚未接受**，
点击「查看邀请」→「接受邀请」；接受后横幅消失，账号才具备分支推送权限。

两点容易误判：

- 公开仓库任何人都能浏览代码，**「能看见仓库」不等于「有写权限」**；真正的验证是第 2 步推送成功。
- 合作者名单位于仓库 `Settings → Collaborators`，该菜单仅管理员可见。普通成员看不到属正常现象，不代表权限未生效。

**顺序要求：先接受邀请，再推送分支。** 邀请未接受时即使完成浏览器授权，推送仍会返回 `403`。

### 2. 推送分支

在本机终端进入仓库目录，执行：

```bash
git push -u origin feat/compact-data-format
```

弹出凭据管理器窗口后选择「Sign in with your browser / 用浏览器登录」，在浏览器中确认账号并点击授权。
**不要输入 GitHub 密码**（已停用）。成功时终端会打印 `* [new branch] feat/... -> feat/...`。

若本机终端无法弹出授权窗口，可改用设备码流程（由 GCM 提供 `github login --device`），
或由管理员生成仅含 `repo` 权限的 Personal Access Token 作为一次性凭据。
Token 不得写入仓库文件、文档或聊天记录。

### 3. 验证

打开 `https://github.com/trocedge/ACN/tree/feat/compact-data-format`，能看到 `docs/`、`scripts/`、`data/` 即推送成功。

### 4. 提交 PR

打开 `https://github.com/trocedge/ACN/compare/main...feat/compact-data-format`：

- `base` 选 `main`，`compare` 选 `feat/compact-data-format`
- 标题与正文直接复用 `docs/pr-description.md`（该文件随分支同步，数字与验收结果已更新）
- 点击 **Create pull request**
- **不要自行点击 Merge pull request**，是否合并由项目组决定

### 5. 推送后检查

- 新增的 `data-check.yml` 与 `healthcheck.yml` 是否出现在 Actions 列表
- PR 上的数据门禁是否通过（`validate_data.py --source` 退出码 0）
- 若 CI 报依赖缺失，按 `docs/ci-templates/clean-env-check.md` 补齐测试依赖

## 常见错误

| 现象 | 原因 | 处理 |
|---|---|---|
| `Invalid username or token` | 使用了密码或未完成授权 | 重新执行浏览器授权，勿输密码 |
| `CONNECT tunnel failed 502` / 超时 | 本地代理抖动 | 重试一次；仍失败则记录报错排查网络 |
| 授权窗口不出现 | 终端非交互 | 换用本机可见终端窗口或设备码流程 |
| `403` / `repository not found` | 账号无写权限 | 联系管理员确认 Collaborator |
| commit 不显示头像 | 提交邮箱未在该账号绑定 | 不影响 PR 合并，但贡献者统计与个人贡献图无法归属；在账号 `Settings → Emails` 补绑后会自动重建历史归属 |

## 常见误解：贡献者 ≠ 合作者

| 名单 | 统计依据 | 在哪看 |
|---|---|---|
| 贡献者 Contributors | 按**默认分支的提交记录**自动统计，与权限无关 | `Insights → Contributors` 或仓库右侧栏 |
| 合作者 Collaborators | 权限名单，被邀请且有写权限的成员 | `Settings → Collaborators`（仅管理员可见） |

因此接受邀请后、甚至推送分支后，贡献者列表里仍不会出现新成员名字，属正常现象：

- 非默认分支上的提交不计入贡献者图表；需要 PR 合并到默认分支后才可能统计。
- 提交邮箱若未关联账号，提交不会链接到该账号，也不会出现在贡献者图表。
- 统计刷新最长约 24 小时。

**判断权限是否生效的正确方式**是：邀请横幅消失，且分支推送成功；不要用贡献者列表判断。

## 安全约定

- 不输入、不保存、不传播 GitHub 密码与个人访问令牌
- 不修改仓库全局 git 配置，仅使用仓库局部身份
- 不合并 `main`；合并由项目组评审后决定
