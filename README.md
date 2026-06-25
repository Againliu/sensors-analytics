# 📊 Sensors Analytics — XAG Agri-Tech User Behavior Analytics (Full API Coverage)

[中文](#中文说明)

Programmatic access to **all 77 endpoints** of the Sensors Analytics (神策分析) OpenAPI — the user behavior analytics platform powering XAG (极飞科技) agricultural technology products. Run event analysis, funnels, retention curves, custom SQL queries, and data exports without touching the web UI.

## What This Skill Provides

### Analytics Models (19)

| Model | What It Answers | Output |
|-------|----------------|--------|
| **Event Analysis** | "How many users triggered the spray start event last week?" | Event counts, user counts, segmented by any property |
| **Funnel Analysis** | "What % of users complete the full spray workflow (create → fly → complete)?" | Conversion rates per step, drop-off analysis |
| **Retention Analysis** | "Do users who use AI route planning come back more often?" | N-day retention matrix, cohort comparison |
| **Distribution Analysis** | "How is session duration distributed across user segments?" | Histogram data, percentile breakdowns |
| **Interval Analysis** | "How long does the average spray operation take from start to end?" | Time intervals between event pairs |
| **Attribution Analysis** | "Which feature drove the most first-time app opens?" | First-touch / last-touch / linear attribution |
| **LTV Analysis** | "What's the lifetime value of users acquired via different channels?" | Revenue per user over time cohorts |
| **Session Analysis** | "How do users navigate through the app in a single session?" | Session counts, duration, page sequences |
| **Path Analysis** | "After opening the map, where do users go next?" | User flow visualization data, node/edge weights |
| **Property Analysis** | "What device models are our users on?" | Property value distributions |

### Platform Operations (58)

| Category | Endpoints | Key Capabilities |
|----------|-----------|-----------------|
| **Dashboard & Overview** | 6 | Real-time KPIs, custom widgets, saved dashboards |
| **Business Marketplace** | 7 | Pre-built analysis templates for common queries |
| **Smart Alerts** | 2 | Automated anomaly detection on key metrics |
| **Event Metadata** | 2 | List tracked events, update visibility/descriptions |
| **Property Metadata** | 6 | Manage event/user properties, type information |
| **Channel Tracking** | 5 | UTM channel CRUD, campaign performance |
| **Custom SQL** | 1 | Full SQL interface over the analytics database |
| **Schema Management** | 13 | Inspect tables, columns, data types |
| **Directory Services** | 3 | Navigate project catalog and saved reports |
| **User Tags** | 3 | Create/query/manage user tags |
| **User Segments** | 3 | Define and query audience segments |
| **Data Export** | 2 | Bulk export query results, tag/segment data |

## Data Available

| Data Type | Examples | Granularity |
|-----------|---------|-------------|
| **User events** | App open, spray start, route plan, device bind, login | Per-event with timestamp + all properties |
| **User properties** | Device model, app version, region, user type | Per-user profile |
| **Session data** | Session duration, page sequence, bounce rate | Per-session |
| **Channel data** | UTM source/medium/campaign, install channel | Per-acquisition |
| **Device data** | OS, device model, screen size, network type | Per-event context |

## Included Scripts

| Script | Purpose | Example |
|--------|---------|---------|
| `query_data.py` | Run any of the 19 analytics models | `python3 scripts/query_data.py --model event --event spray_start` |
| `query_sql.py` | Execute custom SQL | `python3 scripts/query_sql.py --sql "SELECT count(*) FROM events"` |
| `list_events.py` | List all tracked events and properties | `python3 scripts/list_events.py` |
| `cache_metadata.py` | Cache event/property metadata for fast lookups | `python3 scripts/cache_metadata.py` |
| `export_data.py` | Bulk export query results | `python3 scripts/export_data.py --query result.json` |
| `export_excel.py` | Export to formatted Excel | `python3 scripts/export_excel.py --model retention` |
| `query_segmentation.py` | User segmentation queries | `python3 scripts/query_segmentation.py --segment active_users` |
| `schema.py` | Inspect data schema | `python3 scripts/schema.py --table events` |

## Reference Documentation

The `docs/` directory contains official Sensors Analytics OpenAPI documentation:

| Document | Contents |
|----------|----------|
| `open_api_authentication.html/.txt` | Authentication mechanism and API key management |
| `open_api_iface_doc.html/.txt` | Full API interface reference |
| `queries_doc.html/.txt` | Query model parameters and response formats |
| `queries_doc_full.html` | Extended query documentation with examples |
| `channel_doc.html/.txt` | Channel tracking API reference |
| `entity_list_export.html/.txt` | Entity listing and data export |
| `input_output_data.html/.txt` | Data format specifications |
| `tech_export.html/.txt` | Technical export procedures |
| `User_Tag_Management.html/.txt` | User tag creation and management |
| `about_open_api.html/.txt` | Overview and architecture |

## Prerequisites

- Python 3.8+
- `requests` and `openpyxl`
- A Sensors Analytics API key (35-character `#K-xxx` format)

## Setup

1. Copy `sensors-analytics/` into your agent's skills directory
2. Store your API key in a secure file (e.g. `~/.hermes/credentials/sensors.txt`, chmod 600)
3. Verify: `python3 scripts/list_events.py`

## Typical Use Cases

- **"Last month's DAU/MAU?"** → Event analysis on app open events
- **"What's the spray workflow completion rate?"** → Funnel analysis: create → fly → complete
- **"Do AI route planning users retain better?"** → Retention analysis with segmentation
- **"Which device models have the most crashes?"** → Event analysis segmented by device_model
- **"Export all active users for the marketing team"** → Segment query + bulk export
- **"How many users use the new map feature?"** → Event analysis with date filter

## Version

v1.2.0 · Updated 2026-06-03

---

## 中文说明

# 📊 Sensors Analytics — 神策分析 OpenAPI（极飞农服用户行为分析，全量接入）

编程访问神策分析 OpenAPI 的 **全部 77 个端点** — 极飞科技农业技术产品的用户行为分析平台。无需打开 Web UI 即可执行事件分析、漏斗分析、留存曲线、自定义 SQL 查询和数据导出。

## 核心能力

### 分析模型（19 个）

| 模型 | 解决什么问题 | 输出 |
|------|------------|------|
| **事件分析** | "上周有多少人触发了喷洒开始事件？" | 事件次数、用户数，按任意属性分段 |
| **漏斗分析** | "用户完成完整喷洒流程（创建→飞行→完成）的比例是多少？" | 各步骤转化率、流失分析 |
| **留存分析** | "使用 AI 航线规划的用户回访率更高吗？" | N 日留存矩阵、群组对比 |
| **分布分析** | "不同用户群体的会话时长分布如何？" | 直方图数据、百分位分析 |
| **间隔分析** | "平均一次喷洒作业从开始到结束需要多久？" | 事件对之间的时间间隔 |
| **归因分析** | "哪个功能带来了最多的首次打开？" | 首次/末次/线性归因 |
| **LTV 分析** | "不同渠道获取用户的生命周期价值是多少？" | 时间群组内每用户收益 |
| **Session 分析** | "用户在一次会话中如何浏览 App？" | 会话数、时长、页面序列 |
| **路径分析** | "打开地图后用户去了哪里？" | 用户流可视化数据、节点/边权重 |
| **属性分析** | "用户都在用什么设备型号？" | 属性值分布 |

### 平台运维（58 个端点）

| 分类 | 端点数 | 核心能力 |
|------|--------|---------|
| **Dashboard & 概览** | 6 | 实时 KPI、自定义组件、保存仪表盘 |
| **业务集市** | 7 | 预置分析模板 |
| **智能预警** | 2 | 关键指标自动异常检测 |
| **事件元数据** | 2 | 列出埋点事件、更新可见性/描述 |
| **属性元数据** | 6 | 管理事件/用户属性、类型信息 |
| **渠道追踪** | 5 | UTM 渠道增删改查、投放效果 |
| **自定义 SQL** | 1 | 对分析数据库的完整 SQL 接口 |
| **Schema 管理** | 13 | 检查表、列、数据类型 |
| **目录服务** | 3 | 导航项目目录和保存的报告 |
| **用户标签** | 3 | 创建/查询/管理用户标签 |
| **用户分群** | 3 | 定义和查询受众分群 |
| **数据导出** | 2 | 批量导出查询结果、标签/分群数据 |

## 可用数据

| 数据类型 | 示例 | 粒度 |
|---------|------|------|
| **用户事件** | App 打开、喷洒开始、航线规划、设备绑定、登录 | 每条事件含时间戳 + 全部属性 |
| **用户属性** | 设备型号、App 版本、地区、用户类型 | 每用户画像 |
| **会话数据** | 会话时长、页面序列、跳出率 | 每会话 |
| **渠道数据** | UTM source/medium/campaign、安装渠道 | 每次获取 |
| **设备数据** | 操作系统、设备型号、屏幕尺寸、网络类型 | 每事件上下文 |

## 附带脚本

| 脚本 | 用途 | 示例 |
|------|------|------|
| `query_data.py` | 运行 19 种分析模型中的任意一种 | `python3 scripts/query_data.py --model event --event spray_start` |
| `query_sql.py` | 执行自定义 SQL | `python3 scripts/query_sql.py --sql "SELECT count(*) FROM events"` |
| `list_events.py` | 列出所有已埋点的事件和属性 | `python3 scripts/list_events.py` |
| `cache_metadata.py` | 缓存事件/属性元数据加速查询 | `python3 scripts/cache_metadata.py` |
| `export_data.py` | 批量导出查询结果 | `python3 scripts/export_data.py --query result.json` |
| `export_excel.py` | 导出格式化 Excel | `python3 scripts/export_excel.py --model retention` |
| `query_segmentation.py` | 用户分群查询 | `python3 scripts/query_segmentation.py --segment active_users` |
| `schema.py` | 检查数据 Schema | `python3 scripts/schema.py --table events` |

## 参考文档

`docs/` 目录包含神策分析 OpenAPI 官方文档：

| 文档 | 内容 |
|------|------|
| `open_api_authentication.html/.txt` | 认证机制和 API Key 管理 |
| `open_api_iface_doc.html/.txt` | 完整 API 接口参考 |
| `queries_doc.html/.txt` | 查询模型参数和响应格式 |
| `queries_doc_full.html` | 扩展查询文档含示例 |
| `channel_doc.html/.txt` | 渠道追踪 API 参考 |
| `entity_list_export.html/.txt` | 实体列表和数据导出 |
| `input_output_data.html/.txt` | 数据格式规范 |
| `tech_export.html/.txt` | 技术导出流程 |
| `User_Tag_Management.html/.txt` | 用户标签创建和管理 |
| `about_open_api.html/.txt` | 概览和架构 |

## 环境要求

- Python 3.8+
- `requests` 和 `openpyxl`
- 神策分析 API Key（35 字符 `#K-xxx` 格式）

## 安装

1. 将 `sensors-analytics/` 目录复制到你的 Agent skills 目录
2. 将 API Key 存到安全文件（如 `~/.hermes/credentials/sensors.txt`，chmod 600）
3. 验证：`python3 scripts/list_events.py`

## 典型使用场景

- **"上月 DAU/MAU？"** → App 打开事件分析
- **"喷洒流程完成率多少？"** → 漏斗分析：创建→飞行→完成
- **"AI 航线规划用户留存更好吗？"** → 留存分析 + 分群对比
- **"哪些设备型号崩溃最多？"** → 事件分析按 device_model 分段
- **"导出所有活跃用户给市场团队"** → 分群查询 + 批量导出
- **"新地图功能有多少人在用？"** → 事件分析 + 日期过滤

## 版本

v1.2.0 · 更新于 2026-06-03
