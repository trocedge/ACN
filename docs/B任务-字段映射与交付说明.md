# B 任务交付说明 · 精简数据格式

> 分支：`feat/compact-data-format` ｜ 2026-11-09
> 对应群内要求：前端仅保留行式展示；数据格式需调整，但 oseddl 不完全符合、不需要「活动」等格式；先完成改造再分后续任务。

## 做了什么

新增两个文件，**不改任何老文件**：

| 文件 | 作用 |
|---|---|
| `scripts/build_compact.py` | 只读扫描 `conference/**/*.yml`，产出一份精简大表 |
| `data/conferences.yml` | 脚本产物，383 条会议、行式展示友好 |

老链路（`scripts/build_data.py` → `public/conference/allconf.json`）保持原样，别人继续按老格式提 PR，不受影响。

## 为什么不分三类

参考站 oseddl 把数据拆成 conferences / competitions / activities 三张表，但本项目是学术会议截止日追踪，没有「活动」类数据。按学长要求**只产出一份表**，不造 `category`、不造假条目。

## 字段映射

| 老（ACN） | 新 | 说明 |
|---|---|---|
| 383 个散文件 | 一份 `data/conferences.yml` | 脚本合并 |
| `confs[]` | `events[]` | 改字段名 |
| `timeline[].deadline` `'2020-09-01 23:59:59'` | `'2020-09-01T23:59:59'` | ISO 8601，2841 条 |
| `timezone` | 原值 + `timezone_utc_offset` | **保留原值**，见下 |
| `title` / `description` / `sub` / `rank` / `dblp` | 同名 | 全保留，不删字段 |
| — | `source_file` | 新增，方便回溯到原 yml |

`rank`（CCF 评级）与 `dblp` 是本项目内核，参考站没有但不能删。等 A 同学确认界面显示哪些字段后，再决定是否精简。

## 时区处理（最容易出错的地方）

- 2357 个届次里 **`AoE` 1540 条**、`UTC-12` 288、`PT` 35、`UTC-8` 73 等。
- `AoE` = UTC-12，与 `Asia/Shanghai`（UTC+8）差 20 小时。**绝不能硬替换**，否则 1540 条截止日集体错一天。
- 做法：保留 `timezone` 原值，另补 `timezone_utc_offset`（能确定的填数字；`PT` 等 35 条因夏令时留 `null`，不让前端瞎算）。
- 参考站示例里的 `24:00:00` 不是合法 ISO 8601，本仓库实测出现 0 次，未采用。

## 验证结果

| 项 | 结果 |
|---|---|
| 扫描文件 | 383 个会议档案 |
| 会议条目 / 届次 / 时间节点 | 383 / 2357 / 2939 |
| 日期规范化 | 空格转 T 2841 条、TBD 98 条、未识别 **0** 条 |
| 校验（必填字段、id 唯一、日期、时区） | **0 问题** |
| `AoE` 原值保留 | 1540 条 ✅ |
| 产出回读 | 776.6 KB，383 条一致 ✅ |
| 老链路 `build_data.py` | 正常跑通，产物 `allconf.json` / `initial.json` 生成 ✅ |
| 老文件改动 | **0** ✅ |
| 仓库自带 Python 单测 | 82 tests / 14 errors，**干净副本同样 14 errors**，与本次改动无关（Windows 临时 sqlite 占用 + 缺依赖） |

## 给 A 同学的接口

`data/conferences.yml` 是列表，每行一个会议：

```yaml
- title: SIGMOD
  description: ACM Conference on Management of Data
  sub: DB
  rank: {ccf: A, core: A*, thcpl: A}
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

行式展示建议直接用 `events[*].timeline[*].deadline`；时间显示口径（原值 / 换算北京时间）请 A 定，定了我这边再补字段，不改老数据。

## 复现命令

```bash
python scripts/build_compact.py --check   # 只校验不落盘
python scripts/build_compact.py           # 产出 data/conferences.yml
python -m unittest discover -s scripts -p 'test_*.py'
```

## 待确认（不阻塞）

1. 界面最终显示哪几个字段 → 决定是否精简输出。
2. 时间显示原始时区还是北京时间 → 决定是否加 `deadline_beijing`。
3. 新数据文件是随仓库提交，还是改由 CI 生成并加入 `.gitignore` → 当前按「随仓库提交」处理，便于 A 直接对接。
