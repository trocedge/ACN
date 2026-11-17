# ACN · 学术会议与竞赛截止日追踪站（中文 README 候选）
> 候选文件，是否设为默认由项目组决定；不覆盖现有英文 README。
## 项目定位
汇总学术会议/竞赛的投稿截止日，帮助同学及时掌握时间节点。
## 快速开始
```bash
python scripts/validate_data.py --source
python scripts/build_compact_data.py
python scripts/build_data.py
```
详见 [本地开发上手](docs/local-development.md)。
## 数据说明
383 份会议档案、2357 个届次；字段见 [字段契约](docs/field-contract.md)，时区见 [时区字典](docs/timezone-dictionary.md)。
## 文档
[文档索引](docs/README.md) ｜ [使用入门](docs/glossary.md) ｜ [质量评估](docs/quality-review-and-improvement-plan.md)
## 贡献
见 [贡献指南](../CONTRIBUTING.md)。
## 许可
沿用仓库既有 LICENSE。
