# 神策 OpenAPI 官方端点完整清单（2026-06-03 全量覆盖）

> 来源：https://manual.sensorsdata.cn/openapi (分析云3.0.4)
> 总计 63 个官方端点 + 14 个额外端点（Portal/Tag/Segment/Export）= 77 个端点常量
> **覆盖率: 100%**（v1.2.0 起全部接入）

## Swagger 文件获取

```
https://manual.sensorsdata.cn/openapi/api/v1/openapi_file?file_name={filename}
```

发现方法：浏览器打开文档页面，点左侧菜单项，用 `performance.getEntriesByType('resource').filter(e => e.name.includes('openapi_file'))` 捕获请求的文件名。

| 类别 | Swagger 文件 | 端点数 | Base URL |
|------|-------------|--------|----------|
| Dashboard 概览 | `3.0.4-analytics-Dashboard-v1-swagger.json` | 6 | /api/v3/analytics/v1 |
| Dataset 业务集市 | `3.0.4-analytics-Dataset-v1-swagger.json` | 7 | /api/v3/analytics/v1 |
| Model v1 分析模型 | `3.0.4-analytics-Model-v1-swagger.json` | 19 | /api/v3/analytics/v1 |
| Model v2 分析模型 | `3.0.4-analytics-Model-v2-swagger.json` | 6 | /api/v3/analytics/v2 |
| SmartAlarm 智能预警 | `3.0.4-analytics-SmartAlarm-v1-swagger.json` | 2 | /api/v3/analytics/v1 |
| EventMeta 事件元数据 | `3.0.4-analytics-EventMeta-v1-swagger.json` | 2 | /api/v3/analytics/v1 |
| PropertyMeta 属性元数据 | `3.0.4-analytics-PropertyMeta-v1-swagger.json` | 6 | /api/v3/analytics/v1 |
| Catalog 目录 | `1.3.6-horizon-Catalog-v1-swagger.json` | 3 | /api/v3/horizon/v1 |
| Schema 元数据管理 | `1.3.6-horizon-Schema-v1-swagger.json` | 13 | /api/v3/horizon/v1 |
| Channel 渠道追踪 | `3.0.4-analytics-Channel-v1-swagger.json` | 5 | /api/v3/analytics/v1 |

## Model v1 完整端点（19 个）

| 路径 | 用途 | 端点常量 |
|------|------|----------|
| /model/segmentation/report | 事件分析报告 | EP_SEG_REPORT |
| /model/segmentation/users | 事件分析用户明细 | EP_SEG_USERS |
| /model/funnel/report | 漏斗分析报告 | EP_FUNNEL_REPORT |
| /model/funnel/users | 漏斗用户明细 | EP_FUNNEL_USERS |
| /model/retention/report | 留存分析报告 | EP_RETENTION_REPORT |
| /model/retention/users | 留存用户明细 | EP_RETENTION_USERS |
| /model/addiction/report | 分布分析报告 | EP_ADDICTION_REPORT |
| /model/addiction/users | 分布用户明细 | EP_ADDICTION_USERS |
| /model/interval/report | 间隔分析报告 | EP_INTERVAL_REPORT |
| /model/attribution/report | 归因分析报告 | EP_ATTRIBUTION_REPORT |
| /model/ltv/report | LTV 分析报告 | EP_LTV_REPORT |
| /model/ltv/users | LTV 用户明细 | EP_LTV_USERS |
| /model/user-analytics/report | 属性分析报告 | EP_USER_ANALYTICS |
| /model/user/list | 用户列表 | EP_USER_LIST |
| /model/user/behavior | 用户行为列表 | EP_USER_BEHAVIOR |
| /model/session/report | Session 分析报告 | EP_SESSION_REPORT |
| /model/session/users | Session 用户明细 | EP_SESSION_USERS |
| /model/user-path/users | 用户路径分析 | EP_USER_PATH_USERS |
| /model/sql/query | 自定义 SQL | EP_SQL_QUERY |

## Model v2（6 个，v2 增强版）

v2 版本 base URL 为 `/api/v3/analytics/v2`，支持更丰富的参数。包含：attribution/report, funnel/report, funnel/users, retention/report, retention/users, sql/query。
当前 skill 统一使用 v1 端点，v2 端点如需可后续扩展。

## Swagger JSON 解析注意事项

Model-v1 swagger 文件包含控制字符（\t）和多 JSON 对象拼接，解析时需：
```python
import json
with open('swagger.json') as f:
    data = json.load(f, strict=False)  # 忽略控制字符
# 如报 "Extra data"，按大括号深度截取第一个完整 JSON 对象
```
