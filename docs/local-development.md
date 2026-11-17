# 本地开发上手

> 面向：第一次参与本项目的同学
> 日期：2026-11-10
> 说明：本仓库前端使用 Rust / Trunk / WASM，数据层使用 Python。以下步骤按最小可运行路径编排。

---

## 1. 准备环境

| 工具 | 用途 | 备注 |
|---|---|---|
| Python 3.10+ | 数据合并与校验 | 需 `PyYAML` |
| Git | 版本管理 | 提交信息见 `CONTRIBUTING.md` |
| Rust / Cargo | 前端编译 | 需要 `trunk` 工具 |
| Bun / Node | 部分前端脚本 | 参考站的构建工具，本仓库按需 |

安装 Python 依赖：

```bash
pip install PyYAML
```

> 仓库 `requirements.txt` 目前未覆盖全部测试依赖（如 `icalendar`），
> 若需要跑全量单测，请先阅读 `docs/test-baseline-analysis.md`。

---

## 2. 数据层：最快能看到结果的部分

```bash
# 只校验，不写文件（适合改完 yml 后自检）
python scripts/validate_data.py --source

# 生成精简大表到 data/conferences.yml
python scripts/build_compact_data.py

# 源档案 + 产出文件一起校验，并输出 JSON 报告
python scripts/validate_data.py --json docs/data-validation-report.json
```

预期输出（当前基线）：

```
源档案文件 : 383
会议条目   : 383
ERROR      : 0
WARN       : 1（录取率档案 23 份未直接匹配）
结论       : 通过
```

### 老链路（原有构建流程）

```bash
python scripts/build_data.py     # 生成 public/conference/allconf.json 等
trunk build                      # 或 trunk serve 本地预览
```

> 顺序不能反：按 `scripts/DATA_LOADING.md`，必须先跑 `build_data.py` 再构建前端。

---

## 3. 前端

```bash
trunk serve                      # 本地开发服务器
cargo test                       # Rust 侧测试
```

前端技术栈为 Rust/WASM，改动前建议先与界面负责人确认分工，避免同时修改同一组件。

---

## 4. 常见坑

| 现象 | 原因 | 处理 |
|---|---|---|
| `ModuleNotFoundError: No module named 'yaml'` | 未装 PyYAML | `pip install PyYAML` |
| `ModuleNotFoundError: No module named 'icalendar'` | 测试依赖缺失 | 见 `docs/test-baseline-analysis.md`，属既有问题 |
| Windows 上单测报 `WinError 32` | 临时文件句柄未释放 | 属既有问题，Linux CI 环境不触发 |
| 生成物与仓库里的 `data/conferences.yml` 不一致 | 未重跑生成脚本 | 重跑后再校验；策略见 `docs/generated-artifacts-policy.md` |
| 截止日看起来差一天 | `AoE` 被当成北京时间 | 看 `docs/timezone-dictionary.md` |
| PR 提到上游仓库去了 | README 里有上游链接 | 目标分支选本仓库，见 `CONTRIBUTING.md` |

---

## 5. 目录速查

| 目录 | 装什么 |
|---|---|
| `conference/` | 383 份会议档案（源数据） |
| `accept_rates/` | 历史录取率（321 份） |
| `data/` | 本次改造产出的精简大表 |
| `scripts/` | 数据合并、校验、SEO 生成等脚本 |
| `docs/` | 规范、契约、指南、模板 |
| `public/conference/` | 老链路生成的 JSON（构建产物） |
| `src/`、`worker/` | 前端与边缘服务 |

---

## 6. 提交前清单

- [ ] `python scripts/validate_data.py --source` 的 ERROR 为 0
- [ ] 若改了字段结构，已同步 `docs/field-contract.md` 与 `docs/data-changelog.md`
- [ ] 老链路 `build_data.py` 仍能跑通
- [ ] 没有修改或删除任何源档案之外的既有文件（除非任务明确要求）
- [ ] 分支不是 `main`，PR 描述写清验证结果与待确认事项
