# 竞赛数据目录

本目录存放**教育部白名单竞赛**的截止日数据，是项目主线数据源。

## 目录结构

```
competition/
├── types.yml          # 竞赛分类定义（ACADEMIC/TECH/ART/PRACTICE）
├── <类别>/<竞赛>.yml   # 归类后的竞赛数据，如 competition/TECH/xxx.yml
```

## 一条竞赛数据的最小结构

```yaml
- title: 全国青少年科技创新大赛
  description: 面向青少年的科技创新类竞赛
  sub: TECH
  confs:
    - year: 2027
      id: xxx27
      link: https://example.com
      timeline:
        - deadline: '2027-03-01 23:59:59'
          comment: 报名截止
      timezone: UTC+8
```

## 收录规则

1. 只收教育部白名单竞赛，判定依据见 `docs/whitelist-competitions.md`
2. 每条数据须在 `docs/whitelist-competitions.md` 清单中有对应行
3. `sub` 取 `types.yml` 中定义的分类值

## 当前状态

**未做**：本目录目前只有分类定义，尚无真实竞赛数据。白名单官方名单待项目组提供后填入。
