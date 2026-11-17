# 贡献指南

欢迎参与 ACN（学术会议与竞赛截止日追踪站）的数据维护与功能改进。本文说明如何正确地提交一份修改。

---

## 1. 本仓库与上游的关系

本仓库是 `ccfddl/ccf-deadlines` 的派生项目，用于本项目的界面改造与数据格式演进。

> **提交 PR 时目标分支是本仓库的对应分支，不要直接提到上游仓库。**
> 上游同步由项目组统一处理，个人贡献无需也不应直接推向上游。

---

## 2. 修改数据（最常见）

### 2.1 文件位置

| 内容 | 路径 |
|---|---|
| 会议档案 | `conference/<学科>/<会议>.yml` |
| 学科定义 | `conference/types.yml` |
| 历史录取率 | `accept_rates/<学科>/<会议>.yml` |

学科代码共 10 类：`AI` `CG` `CT` `DB` `DS` `HI` `MX` `NW` `SC` `SE`。

### 2.2 必填字段

顶层条目：`title`、`description`、`sub`、`rank`（含 `ccf`）、`dblp`、`confs`。
每个届次（`confs[]`）：`year`、`id`、`link`、`timeline`、`timezone`、`date`、`place`。

`timeline[].deadline` 格式：`'YYYY-MM-DD HH:mm:ss'` 或 `TBD`。

### 2.3 三条容易踩的约定

1. **只给日期没给时刻**，按 `23:59:59` 补；
2. **未给时区**，按 `AoE` 处理，并在注释中说明这是仓库默认约定，不要写成官方公布值；
3. **未公布的日期**写 `TBD`，不要自行推测或填 0 点。

> `AoE` 是 UTC-12，比北京时间晚 20 小时。修改截止日时请连同 `timezone` 一起核对，
> 详见 `docs/timezone-dictionary.md`。

### 2.4 提交前自检

```bash
python scripts/validate_data.py --source
```

- `ERROR` 必须为 0 才能提交；
- `WARN` 目前有 1 条（录取率档案 23 份未与会议标题直接匹配），属已知问题，不阻断；
- 若新增了档案，请确认 `id` 全局唯一。

---

## 3. 修改代码或文档

| 类型 | 位置 | 注意事项 |
|---|---|---|
| 数据转换脚本 | `scripts/build_compact_data.py` | 老档案只读，不得改写源文件 |
| 数据校验 | `scripts/validate_data.py` | 新增规则需区分 ERROR（阻断）与 WARN（提示） |
| 字段结构变更 | `docs/field-contract.md` + `docs/data-changelog.md` | 必须递增 `schema_version` |
| 文档 | `docs/` | 更新 `docs/README.md` 索引 |
| 前端 | `src/`、`index.html` | 与界面负责人协同，避免冲突 |

---

## 4. 分支与 PR 规范

1. 从 `main` 新建分支，命名建议 `feat/xxx`、`fix/xxx`、`docs/xxx`；
2. 提交信息用一句话说明改了什么，中文或英文均可，但不要写含糊的「update」；
3. **不要直接 push 到 `main`**；
4. PR 描述包含：改动范围、验证结果、待确认事项；
5. 若改动影响字段结构，必须在 PR 中链接字段契约与变更日志。

---

## 5. 红线

- 不编造未公布的日期、地点、评级或录取率；
- 不删除他人的档案或字段；
- 不把 `AoE` 静态替换成北京时间；
- 不把生成物与源数据混为一谈（策略见 `docs/generated-artifacts-policy.md`）；
- 不绕过校验门禁直接合并。

---

## 6. 相关文档

| 想了解 | 看哪里 |
|---|---|
| 站点怎么用、术语是什么 | `docs/glossary.md` |
| 字段含义与展示用途 | `docs/field-contract.md` |
| 时区换算规则 | `docs/timezone-dictionary.md` |
| 数据格式规范与验证 | `docs/data-format-specification.md` |
| 本地怎么跑起来 | `docs/local-development.md` |
| 测试基线现状 | `docs/test-baseline-analysis.md` |
| 文档总索引 | `docs/README.md` |
