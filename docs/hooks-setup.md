# 本地钩子启用说明（第 22 条）
```bash
git config core.hooksPath docs/ci-templates
chmod +x docs/ci-templates/pre-commit
```
- 只设置本仓库局部配置，不改全局 git 配置。
- 提交前自动执行 `validate_data.py --source`，ERROR 非 0 时阻止提交并给出修复提示。
