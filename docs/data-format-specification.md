# ACN 数据格式规范与改造说明

> 版本：v1.0 ｜ 日期：2026-11-10
> 适用仓库：`github.com/trocedge/ACN`
> 状态：已实现并验证，待与界面层确认字段契约后收敛

---

## 1. 背景与目标

ACN 是学术会议与竞赛截止日追踪站。原始会议数据分散在 `conference/<学科>/<会议>.yml`，共 383 份档案、10 个学科目录，由 `scripts/build_data.py` 合并为 `public/conference/allconf.json` 供前端消费。

前端改造目标是**行式展示、仅保留重要内容、风格现代化**，并面向全校同学开放使用。原有数据格式（`confs`、空格分隔日期、多套时区写法）不便直接对接新的展示层，因此需要新增一份精简数据视图。

本项目数据均为学术会议，不包含「活动 / 竞赛」等其他类型条目，故**不采用参考站的三表分类方案**，只产出一份表。

---

## 2. 设计原则

| # | 原则 | 说明 |
|---|---|---|
| 1 | 单一事实来源 | 老 `conference/**/*.yml` 仍是唯一数据源，新格式全部由脚本派生，禁止手工双写 |
| 2 | 老链路不侵入 | 原有 `build_data.py` → `allconf.json` → 前端的链路保持原样，贡献方式（改 yml 提 PR）不变 |
| 3 | 字段先全保留 | 界面「仅保留重要内容」属展示层决策，数据层不做不可逆删除，待字段契约确认后再收敛 |
| 4 | 时区语义不失真 | 保留原值，另补可确定的 UTC 偏移；不做静态时区替换 |
| 5 | 可回退 | 改动限于新增文件，删除新增内容即可恢复原状 |

---

## 3. 实现

新增文件：

| 文件 | 作用 |
|---|---|
| `scripts/build_compact_data.py` | 只读扫描散 yml，产出精简大表；提供 `--check` 校验模式 |
| `data/conferences.yml` | 脚本产物，383 条会议，行式展示友好 |
| `docs/data-format-specification.md` | 本文档 |

> 脚本文件名由初版 `build_compact.py` 调整为 `build_compact_data.py`，语义更明确。

### 3.1 字段对照

| 原字段 | 产出字段 | 处理方式 |
|---|---|---|
| 383 个散文件 | 单份 `data/conferences.yml` | 脚本合并 |
| `confs[]` | `events[]` | 字段改名 |
| `timeline[].deadline` `'2020-09-01 23:59:59'` | `'2020-09-01T23:59:59'` | 归一为 ISO 8601 |
| `timezone` | `timezone` + `timezone_utc_offset` | 保留原值，补可确定的偏移 |
| `title` / `description` / `sub` / `rank` / `dblp` | 同名 | 全量保留 |
| — | `source_file` | 新增，便于回溯原档案 |
| — | `schema_version` | 预留，待字段契约确认后启用 |

`rank`（CCF / CORE / THCPL 评级）与 `dblp` 是本项目区别于通用截止日站的核心数据，参考站无对应字段，但不得因对齐参考站而删除。

### 3.2 时区处理

实测 2357 个届次中：`AoE` 1540 条、`UTC-12` 288 条、`UTC+0` 74 条、`UTC` 72 条、`PT` 35 条、`UTC-8` 73 条等。

- `AoE` 定义为 UTC-12，与北京时间（UTC+8）相差 20 小时；若静态替换为 `Asia/Shanghai`，1540 条截止日会整体偏移一天。
- `PT` 为美国太平洋时间，存在夏令时切换，无法用固定偏移表示；此类 35 条 `timezone_utc_offset` 留空，由展示层按具体日期判定。
- 参考站文档中出现的 `24:00:00` 不是合法 ISO 8601 时刻，本仓库实测出现 0 次，未采用；仓库约定使用 `23:59:59`。

### 3.3 输出样例

```yaml
- title: SIGMOD
  description: ACM Conference on Management of Data
  sub: DB
  rank:
    ccf: A
    core: A*
    thcpl: A
  dblp: sigmod
  source_file: conference/DB/sigmod.yml
  events:
    - year: 2022
      id: sigmod22
      link: http://2022.sigmod.org/
      timeline:
        - deadline: '2021-07-02T17:00:00'
          comment: first round
      timezone: AoE
      timezone_utc_offset: -12
      date: June 12-17, 2022
      place: Philadelphia, PA, USA
```

---

## 4. 验证结果

| 项 | 结果 |
|---|---|
| 扫描档案 | 383 |
| 会议条目 / 届次 / 时间节点 | 383 / 2357 / 2939 |
| 日期规范化 | 空格转 T 2841 条；`TBD` 98 条保留；未识别 0 条 |
| 时区 | 2357 条中 35 条无法固定换算，保留原值 |
| `AoE` 原值保留 | 1540 条 |
| 校验（必填字段、`id` 唯一、日期格式、时区白名单、条数一致） | 0 问题 |
| 产出回读 | 776.6 KB，383 条一致 |
| 老链路 `build_data.py` | 正常执行，`allconf.json` / `initial.json` 正常生成 |
| 老文件改动 | 0 |
| 仓库既有 Python 单测 | 82 项中 14 项报错；**未改动的干净副本对照结果相同**，属仓库既有问题（Windows 临时文件占用、依赖缺失），与本次改动无关 |

---

## 5. 复现命令

```bash
python scripts/build_compact_data.py --check   # 仅校验，不落盘
python scripts/build_compact_data.py           # 产出 data/conferences.yml
python -m unittest discover -s scripts -p 'test_*.py'
```

---

## 6. 待确认事项（不阻塞当前交付）

| # | 事项 | 影响 | 当前处理 |
|---|---|---|---|
| 1 | 界面最终展示哪些字段 | 决定是否精简输出 | 全量保留 |
| 2 | 时间显示原始时区还是换算值 | 决定是否补 `deadline_beijing` | 保留原值 + 偏移 |
| 3 | 生成物随仓库提交还是由 CI 生成 | 仓库体积与前端读取方式 | 当前随仓库提交（`data/` 未被 `.gitignore` 忽略） |
| 4 | 中文化字段是否入库 | 全校同学阅读体验 | 英文原值保留，未新增中文副本 |

---

## 7. 变更记录

| 版本 | 日期 | 内容 |
|---|---|---|
| v1.0 | 2026-11-10 | 新增转换脚本与单表产出；确立时区双轨与字段先全保留原则；补齐验证报告 |
