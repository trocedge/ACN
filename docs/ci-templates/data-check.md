# CI 数据校验工作流模板

> 用途：供负责工程化与发布的项目成员参考，复制到 `.github/workflows/` 后启用。
> 本文件仅为模板，**不直接修改仓库现有的 workflow**。
> 配套脚本：`scripts/validate_data.py`、`scripts/build_compact_data.py`

```yaml
name: data-validation

on:
  pull_request:
    paths:
      - 'conference/**/*.yml'
      - 'scripts/build_compact_data.py'
      - 'scripts/validate_data.py'
      - 'data/conferences.yml'
  push:
    branches: [main]
    paths:
      - 'conference/**/*.yml'
  workflow_dispatch:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: 安装依赖
        run: pip install PyYAML

      # 门禁：只校验源档案，不依赖任何生成物，PR 阶段即可阻断
      - name: 源档案校验（阻断项不为零则失败）
        run: python scripts/validate_data.py --source --json validation.json

      - name: 上传校验报告
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: data-validation-report
          path: validation.json

  # 可选：切换为「CI 生成产物」方案后再启用此任务
  # regenerate:
  #   needs: validate
  #   runs-on: ubuntu-latest
  #   steps:
  #     - uses: actions/checkout@v4
  #     - uses: actions/setup-python@v5
  #       with: { python-version: '3.11' }
  #     - run: pip install PyYAML
  #     - name: 重新生成并完整校验
  #       run: |
  #         python scripts/build_compact_data.py
  #         python scripts/validate_data.py
  #     - name: 校验老链路
  #       run: python scripts/build_data.py
```

## 接入说明

| 项 | 说明 |
|---|---|
| 触发范围 | 只监听 `conference/**/*.yml` 与数据脚本，避免无关 PR 触发 |
| 阻断逻辑 | `validate_data.py` 遇 ERROR 返回退出码 1，PR 自动变红；WARN 不阻断 |
| 依赖 | 仅 `PyYAML`；Linux 环境可避开 Windows 临时文件占用问题 |
| 报告 | 输出 `validation.json`，含 ERROR/WARN 数与样例，便于评审查看 |
| 边界 | 本模板不改动现有 workflow、不配置 Pages 部署、不代他人决定生成物策略 |

## 验收

1. 故意把某份 `conference/*.yml` 的 `deadline` 改成非法格式 → PR 应被阻断。
2. 恢复后 → 校验通过，报告 `errors: 0`。
3. 正常数据下 WARN 应为 1（录取率档案 23 份未直接匹配），不阻断合并。
