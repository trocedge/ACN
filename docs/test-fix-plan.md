# 测试基线修复结果（E1，2026-11-10 实测）

## 最终结果
全量 `python -m unittest discover -s scripts -p 'test_*.py'`：**Ran 100 tests — OK (skipped=1)**，错误 **12 → 0**。

## 三类根因与修复（不改任何断言）
| 类别 | 数量 | 根因 | 修复 |
|---|---:|---|---|
| 分享卡片渲染 | 10 | `share_browser.mjs` 只探测 macOS/Linux 浏览器路径，Windows 报 `Share cards require Chrome/Chromium` | 新增 `defaultBrowser()`，按 `PROGRAMFILES(X86)` / `PROGRAMFILES` / `LOCALAPPDATA` 探测 Edge 与 Chrome；本机实测用 Edge 157 真跑通过，非跳过 |
| sqlite 句柄 | 1 | `with sqlite3.connect(...) as db` 只管理事务不关闭连接，Windows 下 `limits.sqlite` 被占用导致临时目录清理失败 | 改用 `contextlib.closing` 显式关闭三处连接，保留原事务语义 |
| symlink 权限 | 1 | Windows 未开开发人员模式，`WinError 1314` 无法创建符号链接 | 捕获 `OSError` 后 `skipTest` 并写明原因；断言与其它用例不变 |

## 红线遵守情况
未删除、未放宽任何断言；未修改业务代码（仅浏览器探测与测试资源管理）；
10 项分享卡片/SEO 测试是真执行通过，唯一 skip 有明确环境理由。

## 干净环境复现
见 `docs/ci-templates/clean-env-check.md`；Windows 需 Chrome 或 Edge，Linux 由 CI 提供。
