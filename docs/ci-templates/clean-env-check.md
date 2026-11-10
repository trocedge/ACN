# 干净环境验证（第 24 条）
```bash
python -m venv .venv-test
.venv-test/Scripts/activate        # Windows
pip install -r docs/ci-templates/requirements-test.txt
python -m unittest discover -s scripts -p 'test_*.py'
```
验收：收集到 82 项测试，无 `ModuleNotFoundError`。
