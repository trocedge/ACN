# 竞赛数据目录

本目录存放**大学生竞赛白名单**数据，是项目收窄后的主线数据源。会议数据已整体迁到 `archive/conference/`。

## 目录结构

```
competition/
├── types.yml           # 竞赛分类定义（12 类，短码见下）
├── whitelist.yml       # 白名单竞赛目录，84 项基础 + 可扩展，按官方序号排列
├── import-template.csv # 批量录入模板（表头 + 示例行）
└── README.md
```

## 当前数据

| 内容 | 数量 | 说明 |
|---|---|---|
| 竞赛条目 | 84 | 中国高等教育学会《2024 全国普通高校大学生竞赛分析报告》竞赛目录 |
| 已核实官网 | 14 | 其余 `site` 留空，不填猜测地址 |
| 报名截止时间 | 0 | 未采集，一律不填（填错比空着更糟） |

## 单条数据结构

```yaml
- seq: 1                          # 官方目录序号，不要改动
  title: '中国国际 “互联网+”大学生创新创业大赛'   # 官方原文，不改写
  sub: COMP                       # 分类短码
  category: 综合类                 # 官方分类原文
  site: https://cy.ncss.cn/       # 官网，未核实则整行不写
```

采集到报名截止时间后（**核实官方公告后**），在条目下追加：

```yaml
  deadline: '2027-03-15T18:00:00'   # ISO 8601，北京时间
  timezone: Asia/Shanghai
  source_url: https://xxx           # 该截止时间的官方公告地址，必填
```

`deadline` 只接受 `YYYY-MM-DDTHH:mm:ss` 格式，且必须同时填 `source_url`，否则 CI 校验不过。

## 批量录入（推荐）

一条一条手敲 YAML 费劲，批量补几十上百个建议走「填表格 → 一键转」：

1. 复制 `import-template.csv`，用 Excel / WPS 打开填数据（一列一个字段）
2. 跑转换脚本，自动合并进 `whitelist.yml` 并校验
3. 跑「本地验证」三条，全绿再提交

```bash
python scripts/csv_to_whitelist.py 你的名单.csv
```

### 各列含义

| 列 | 必填 | 说明 |
|---|---|---|
| seq | 是 | 序号。1—84 补全现有项，85 起新增扩展项（须连续） |
| title | 新增时必填 | 官方名称原文；补全现有项时可留空（= 不改动） |
| sub | 新增时必填 | 分类短码，12 选 1 |
| category | 新增时必填 | 分类名称 |
| site | 否 | 官网，核实过才填 |
| deadline | 否 | 报名截止时间，`YYYY-MM-DDTHH:mm:ss` 北京时间 |
| timezone | 否 | 固定 `Asia/Shanghai`，填了 deadline 才需要 |
| source_url | 否 | 截止时间对应的官方公告地址，填了 deadline 必填 |

### 规则

- **空单元格 = 不改动**：补全现有项时，只填要更新的列，其余留空
- **seq 命中现有项** → 只更新你填了的字段
- **seq 是全新序号** → 追加到末尾，必须把 title / sub / category 填全
- **deadline 留空** → 整组省略 deadline / timezone / source_url
- 转换时自动校验，报错定位到 CSV 行号；写回前自动备份 `whitelist.yml.bak`

## 本地验证

```bash
python scripts/validate_competition.py      # 校验数据（含产物一致性）
python scripts/build_data.py                # 重新生成 public/competition/*.json
python scripts/test_validate_competition.py # 校验器单测
```

改完数据后跑上面三条，全部通过再提交。校验规则详见 `docs/page-inventory.md`。

## 分类短码

`COMP` 综合 / `CS` 计算机 / `SCI` 理学 / `EE` 电子信息 / `MED` 医学 / `ENG` 其他工学 / `ART` 艺术 / `BIZ` 经管 / `LANG` 语言 / `VOC` 职业技能 / `ROBOT` 机器人 / `AGRI` 农学

## 收录规则

1. 必须在 `docs/whitelist-competitions.md` 的 84 项清单里，序号能对上
2. 名称与官方目录原文一致，不改写、不简称
3. `site` 只填核实过的，核实不了就留空
4. `sub` 必须是 `types.yml` 里的 12 个短码之一

## 注意事项

`seq` 字段不要写成 `no`。YAML 1.1 把裸写的 `no` 当布尔值 `false` 解析，字段名会直接解析错误，之前踩过一次。
