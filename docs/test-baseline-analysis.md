# 既有测试基线分析

> 数字与结论更正见 `docs/corrections.md`；对外汇报以更正记录为准。


> 日期：2026-11-10
> 目的：说明仓库自带测试的历史基线，**区分「既有问题」与「本次改动引入的问题」**。
> 口径：使用未改动的主干副本与本次改动副本分别执行同一命令，对比结果。

---

## 1. 基线数据

执行命令：

```bash
python -m unittest discover -s scripts -p 'test_*.py'
```

| 副本 | 测试总数 | ERROR | FAIL | 结果 |
|---|---:|---:|---:|---|
| 未改动的主干副本 | 82 | 14 | 0 | 未通过 |
| 本次改动后的副本 | 82 | 14 | 0 | 未通过 |

**结论：两次结果完全一致，14 项错误为仓库既有问题，与本次数据格式改造无关。**

> 交付材料中不得把这 14 项描述为「测试全部通过」或「本次改动导致」。

---

## 2. 14 项错误分类

| 类别 | 数量 | 涉及测试 | 已核实的报错 |
|---|---:|---|---|
| 缺 Python 依赖 | 2 | `test_ical_subscription`、`test_rss_dates` | `ModuleNotFoundError: No module named 'icalendar'`（加载阶段即失败） |
| 符号链接权限不足 | 1 | `test_retain_site_assets.RetainedAssetTests.test_symlinks_are_not_copied` | `OSError: [WinError 1314] 客户端没有所需的特权`（创建 symlink） |
| 临时文件句柄未释放 | 1 | `test_worker_database.MessageLimitTests.test_parallel_posts_allow_only_one_message` | `PermissionError: [WinError 32] 另一个程序正在使用此文件 ... limits.sqlite` |
| 临时目录资源清理 | 10 | `test_conference_share_image` 3 项、`test_generate_seo_pages` 6 项、`VenueHubTests` 1 项 | 集中在临时目录创建/清理与文件删除，Windows 下文件句柄释放时序敏感 |

三类根因均与 **Windows 环境特性**（权限、句柄占用）或 **依赖缺失** 有关，Linux CI 环境通常不会触发前两类。

---

## 3. 修复建议（按优先级）

### P0 · 依赖声明（最简单，收益最直接）

`requirements.txt` 当前只有 `jsonschema`、`icalendar`、`xlin` 等少量条目，其中 `icalendar` 在实际执行环境中未安装。建议：

1. 明确列出测试所需依赖及版本下限；
2. CI 中新增 `pip install -r requirements.txt` 步骤；
3. 执行一次干净环境验证，确保 2 个加载失败的测试能被收集。

> 注意：`requirements.txt` 由项目组维护，本次**不擅自修改**，仅给出建议。

### P1 · 临时目录与句柄释放

1. 统一使用 `tempfile.TemporaryDirectory()` 上下文管理器，避免 `setUp` 中手动创建、`tearDown` 中手动删除；
2. sqlite 连接在使用完后显式 `close()`，Windows 上需等待句柄释放再删目录；
3. 对 `tearDown` 的删除操作加重试与短暂等待，避免并发测试互相占用；
4. 涉及 symlink 的测试：Windows 无管理员权限时跳过并给出明确 `skipTest` 理由，而不是报错。

### P2 · CI 环境统一

1. 在 Linux runner 上跑全量 Python 单测，作为合并门禁；
2. Windows 本地测试标注为「尽力而为」，不作为阻断条件；
3. 把 `cargo test` 与前端浏览器测试分开编排，避免互相干扰临时资源。

---

## 4. 验收口径（本次改动采用）

由于基线本身有 14 项错误，本次采用**对照法**而非「全绿法」证明无回归：

| 检查 | 结果 |
|---|---|
| 改动前后测试总数一致 | 82 → 82 ✅ |
| 改动前后错误数未增加 | 14 → 14 ✅ |
| 错误清单一致 | 逐项比对一致 ✅ |
| 新增数据校验脚本自身 | ERROR 0 / WARN 1 ✅ |
| 老链路 `build_data.py` | 正常执行 ✅ |

---

## 5. 风险提示

- 若直接把这 14 项作为「本次 PR 的失败」去修，容易误改他人测试代码，且会把历史问题算到本次改动头上。
- 修复测试属于独立工作项，建议单独建任务、单独提 PR，与数据格式改造解耦。
- 在 CI 接入前，PR 描述应如实写明基线状态，避免评审误解。
