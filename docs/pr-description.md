# PR 描述（可直接粘贴，第 31 条）
## 改动范围
新增数据格式转换与校验体系，覆盖 `scripts/`、`data/`、`docs/`、`.github/workflows/data-check.yml`；
**不修改、不删除任何 `conference/**/*.yml` 源档案**。
- `scripts/build_compact_data.py`：合并 383 份散档为单表（schema 1.1），补状态、双时区换算、中文辅助字段、TBD 跟踪、排序键。
- `scripts/validate_data.py`：ERROR/WARN 分级校验，支持 `--source` 门禁与 JSON 报告。
- `docs/`：字段契约、时区字典、变更日志、术语表、10 份界面规格、CI/探活模板、改进与差距清单。
## 验证结果
- `validate_data.py --source`：ERROR 0；观察项 WARN 见 `docs/timeline-order-observations.md`
- `build_compact_data.py --check`：校验问题 0，产出 383 条一致
- `build_data.py`：老链路退出码 0
- 新增单测（schema 兼容 / 校验规则）：全通过
- 测试基线对照：干净副本 82 项 / 14 错；改动后 100 项 / **12 错**（补齐 `icalendar` 后下降 2），新增 11 项单测全过，**未新增失败**
- 老档案改动：0
## 诚实边界
前端 `src/`、`index.html` 未改（界面层负责）；既有 4 个 workflow 未改；
剩余 12 项既有测试错误如实保留，补丁方案见 `docs/test-fix-plan.md`，不写「测试全绿」。
## 待确认 5 项
字段清单 / 时间展示口径 / 生成物策略 / status 重算方式 / 录取率 id 关联。
