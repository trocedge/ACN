# 评审一页纸摘要（第 40 条）
**改动范围**：新增数据转换/校验脚本、结构化数据、字段契约与规范、界面规格、CI 与探活模板；源档案零改动。
**验证结果**：源档案 ERROR 0；转换校验 0 问题；产出 383 条一致；老链路退出码 0；新增单测全通过。
**诚实边界**：前端源码与既有 4 个 workflow 未改；82 项测试中 14 项既有错误与本次改动无关，不写「测试全绿」；中文辅助字段未覆盖部分留空不编造。
**待确认**：字段清单 / 时间展示口径 / 生成物策略 / status 重算 / 录取率关联（见 `docs/decisions.md`）。
**复现命令**：
```bash
python scripts/validate_data.py --source
python scripts/build_compact_data.py --check
python scripts/build_data.py
```
