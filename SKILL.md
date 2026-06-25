---
name: sensors-analytics
description: 神策分析 OpenAPI 全量接入（77 端点 100% 覆盖）- 极飞农服用户行为埋点分析。封装 user-insight.xa.com
  的 OpenAPI 调用，支持 19 个分析模型（事件/漏斗/留存/分布/间隔/归因/LTV/Session/路径/属性分析）、自定义 SQL、Dashboard
  概览、业务集市、智能预警、事件/属性元数据、渠道追踪 CRUD、Schema 管理、目录服务、标签/分群/导出。
version: 1.2.0
created: 2026-06-02
updated: 2026-06-03
status: production-ready
---


# 神策分析 OpenAPI Skill（sensors-analytics）

> 极飞农服用户行为埋点查询（神策分析）OpenAPI 接入。

## 安装

### 1. 复制 Skill
```bash
cp -r sensors-analytics/ /path/to/your/agent/skills/
```

### 2. 安装依赖
无额外依赖。

### 3. 配置环境变量
无需额外环境变量。

### 4. 验证
查看 SKILL.md 中的使用说明，按文档操作即可。

## 触发场景

当用户要求以下操作时加载此 skill：
- 查极飞农服 App 的用户行为数据（PV/UV/留存/漏斗等）
- 查神策分析平台的事件列表、属性列表
- 用 SQL 查询神策数据
- 导出神策标签/分群数据
- 管理事件/属性的元数据（可见性等）

---

## 一、认证

```python
# 两个 header 缺一不可
headers = {
    "api-key": "<35字符 #K-xxx>",        # ~/.hermes/credentials/sensors.txt
    "sensorsdata-project": "production",  # 项目名，固定值
    "Content-Type": "application/json",
}
```

- **Base URL**: `https://user-insight.xa.com:443`（只有 443 HTTPS 通，其他端口都不行）
- **项目名**: `production`（中文显示"正式项目"，project_id=2）
- **凭据路径**: `~/.hermes/credentials/sensors.txt`（chmod 600）
- **API-Key 权限 = 创建者用户权限**

---

## 二、URL 结构

```
https://user-insight.xa.com:443/api/v3/{产品}/{接口版本}/{端点}
```

| 前缀 | 用途 |
|------|------|
| `/api/v3/portal/v2` | 项目管理、身份、行为审计（5 个端点） |
| `/api/v3/analytics/v1` | 分析模型(19) + 概览(6) + 业务集市(7) + 智能预警(2) + 事件元数据(2) + 属性元数据(6) + 渠道(5) + SQL = 47 个端点 |
| `/api/v3/horizon/v1` | Schema(13) + 目录(3) + 标签(3) + 分群(3) + 实体导出(2) = 21 个端点 |

---

## 三、完整端点索引

### 3.1 Portal V2 — 项目/身份

| 端点常量 | 方法 | 路径 | 用途 |
|----------|------|------|------|
| `EP_PROJECT_LIST` | GET | `.../management/project/list` | 项目列表 |
| `EP_GLOBAL_ACCOUNT` | GET | `.../identity/global-account` | 全局账户信息 |
| `EP_PROJECT_INVITE` | POST | `.../identity/project/invite` | 邀请成员 |
| `EP_BEHAVIOR_LIST` | GET | `.../management/behavior/list` | 行为审计 |
| `EP_ROLE_LIST` | GET | `.../management/role/list` | 角色列表 |

### 3.2 Analytics V1 — 分析模型（19 个）

| 端点常量 | 方法 | 路径 | 用途 | 必填参数 |
|----------|------|------|------|----------|
| `EP_SEG_REPORT` | POST | `.../model/segmentation/report` | 事件分析报告 | measures[].event_name,aggregator + from_date,to_date,unit |
| `EP_SEG_USERS` | POST | `.../model/segmentation/users` | 事件分析用户明细 | 同上 + limit,offset |
| `EP_FUNNEL_REPORT` | POST | `.../model/funnel/report` | 漏斗分析报告 | funnel.steps[].event_name + funnel.max_convert_time |
| `EP_FUNNEL_USERS` | POST | `.../model/funnel/users` | 漏斗用户明细 | 同上 |
| `EP_RETENTION_REPORT` | POST | `.../model/retention/report` | 留存分析报告 | first_event,second_event + retention_xxx_date_period_N |
| `EP_RETENTION_USERS` | POST | `.../model/retention/users` | 留存用户明细 | 同上 |
| `EP_ADDICTION_REPORT` | POST | `.../model/addiction/report` | 分布分析报告 | event_name + filter.conditions |
| `EP_ADDICTION_USERS` | POST | `.../model/addiction/users` | 分布用户明细 | 同上 |
| `EP_INTERVAL_REPORT` | POST | `.../model/interval/report` | 间隔分析 | first_event,second_event |
| `EP_ATTRIBUTION_REPORT` | POST | `.../model/attribution/report` | 归因分析 | attribution_events,target_event |
| `EP_LTV_REPORT` | POST | `.../model/ltv/report` | LTV 分析 | start_sign,measures,unit,duration |
| `EP_LTV_USERS` | POST | `.../model/ltv/users` | LTV 用户明细 | 同上 |
| `EP_USER_ANALYTICS` | POST | `.../model/user-analytics/report` | 属性分析 | measures[].aggregator,by_fields,bucket_params |
| `EP_USER_LIST` | POST | `.../model/user/list` | 用户列表 | filter.conditions |
| `EP_USER_BEHAVIOR` | POST | `.../model/user/behavior` | 用户行为列表 | users[],distinct_id |
| `EP_SESSION_REPORT` | POST | `.../model/session/report` | Session 分析报告 | session 定义 + from_date,to_date |
| `EP_SESSION_USERS` | POST | `.../model/session/users` | Session 用户明细 | 同上 |
| `EP_USER_PATH_USERS` | POST | `.../model/user-path/users` | 用户路径分析 | start_event,path_depth |
| `EP_SQL_QUERY` | POST | `.../model/sql/query` | 自定义 SQL | sql,limit |

### 3.3 Analytics V1 — Dashboard 概览/书签（6 个）

| 端点常量 | 方法 | 路径 | 用途 |
|----------|------|------|------|
| `EP_DASH_NAVIGATION` | GET | `.../dashboard/navigation` | 获取所有概览分组信息 |
| `EP_DASH_NAV_CREATE` | POST | `.../dashboard/navigation/create` | 添加概览分组信息 |
| `EP_DASH_LEGO` | GET | `.../dashboard/lego` | 获取所有基础数据概览数据 |
| `EP_DASH_DETAIL` | GET | `.../dashboard/detail` | 获取单个概览详情 |
| `EP_DASH_SHARE` | POST | `.../dashboard/share` | 概览分享接口 |
| `EP_DASH_BOOKMARKS` | GET | `.../dashboard/bookmarks` | 获取所有书签信息 |

### 3.4 Analytics V1 — Dataset 业务集市（7 个）

| 端点常量 | 方法 | 路径 | 用途 |
|----------|------|------|------|
| `EP_DATASET_DETAIL` | GET | `.../dataset/detail` | 查询业务模型详情信息 |
| `EP_DATASET_LIST` | POST | `.../dataset/detail_list` | 获取业务模型列表 |
| `EP_DATASET_GROUPS` | GET | `.../dataset/group/list` | 获取业务模型分组列表 |
| `EP_DATASET_QUERY` | POST | `.../dataset/model/query` | 通过指标维度规则查询业务模型数据 |
| `EP_DATASET_REFRESH` | POST | `.../dataset/refresh` | 刷新指定业务模型数据 |
| `EP_DATASET_SYNC_TASK` | GET | `.../dataset/sync_task_detail` | 查询业务模型调度任务执行状态 |
| `EP_DATASET_SQL` | POST | `.../dataset/table/sql_query` | 通过 SQL 查询业务模型数据 |

### 3.5 Analytics V1 — SmartAlarm 智能预警（2 个）

| 端点常量 | 方法 | 路径 | 用途 |
|----------|------|------|------|
| `EP_ALARM_ALL` | POST | `.../smart-alarm/all` | 获取所有预警列表 |
| `EP_ALARM_DETAIL` | GET | `.../smart-alarm/detail` | 获取预警配置详细信息 |

### 3.6 Analytics V1 — EventMeta 事件元数据（2 个）

| 端点常量 | 方法 | 路径 | 用途 |
|----------|------|------|------|
| `EP_EVENTMETA_ALL` | GET | `.../event-meta/events/all` | 获取事件列表（轻量） |
| `EP_EVENTMETA_TAGS` | GET | `.../event-meta/events/tags` | 获取事件标签列表 |

### 3.7 Analytics V1 — PropertyMeta 属性元数据（6 个）

| 端点常量 | 方法 | 路径 | 用途 |
|----------|------|------|------|
| `EP_PROP_EVENT_PROPS` | POST | `.../property-meta/event-properties` | 获取指定事件和相关属性 |
| `EP_PROP_EVENT_ALL` | GET | `.../property-meta/event-properties/all` | 获取所有事件属性 |
| `EP_PROP_VALUES` | POST | `.../property-meta/property/values` | 获取属性候选值 |
| `EP_PROP_USER_GROUPS` | GET | `.../property-meta/user-groups/all` | 获取所有用户分群列表 |
| `EP_PROP_USER_ALL` | GET | `.../property-meta/user-properties/all` | 获取所有用户属性列表 |
| `EP_PROP_USER_TAGS` | GET | `.../property-meta/user-tags/dir` | 获取带目录结构的用户标签列表 |

### 3.8 Analytics V1 — Channel 渠道追踪（5 个，完整 CRUD）

| 端点常量 | 方法 | 路径 | 用途 |
|----------|------|------|------|
| `EP_CHANNEL_LINKS_LIST` | POST | `.../channel/links/list` | 获取渠道链接列表 |
| `EP_CHANNEL_LINKS_CREATE` | POST | `.../channel/links/create` | 新建渠道链接 |
| `EP_CHANNEL_LINKS_UPDATE` | POST | `.../channel/links/update` | 更新渠道链接 |
| `EP_CHANNEL_LINKS_DELETE` | POST | `.../channel/links/delete` | 删除渠道链接 |
| `EP_CHANNEL_CAMPAIGNS` | POST | `.../channel/campaigns/list` | 获取活动列表 |

### 3.9 Horizon V1 — Schema 元数据管理（13 个，完整）

| 端点常量 | 方法 | 路径 | 用途 |
|----------|------|------|------|
| `EP_EVENT_LIST` | POST | `.../schema/event/list` | 事件定义列表 |
| `EP_EVENT_GET` | POST | `.../schema/event/get` | 获取单个事件定义 |
| `EP_EVENT_CREATE` | POST | `.../schema/event/create` | 创建事件定义 |
| `EP_EVENT_UPDATE` | POST | `.../schema/event/update` | 更新事件定义 |
| `EP_EVENT_DELETE` | POST | `.../schema/event/delete` | 删除事件定义 |
| `EP_EVENT_FIELD_LIST` | POST | `.../schema/event/field/list` | 获取事件属性 |
| `EP_FIELD_LIST` | POST | `.../schema/field/list` | 获取属性列表 |
| `EP_FIELD_GET` | POST | `.../schema/field/get` | 获取单个属性信息 |
| `EP_FIELD_BATCH_CREATE` | POST | `.../schema/field/batch-create` | 批量创建属性 |
| `EP_FIELD_UPDATE` | POST | `.../schema/field/update` | 更新属性（可见性/字典等） |
| `EP_EXT_TABLE_LIST` | POST | `.../schema/extended-table/list` | 查询维度表关联 |
| `EP_EXT_TABLE_CREATE` | POST | `.../schema/extended-table/batch-create` | 创建维度表关联 |
| `EP_EXT_TABLE_UPDATE` | POST | `.../schema/extended-table/update` | 更新维度表关联 |
| `EP_SCHEMA_GET` | POST | `.../schema/get` | 获取用户表/事件表元信息 |

### 3.10 Horizon V1 — Catalog 目录服务（3 个）

| 端点常量 | 方法 | 路径 | 用途 |
|----------|------|------|------|
| `EP_CATALOG_TREE` | POST | `.../catalog/tree/list` | 查询目录树 |
| `EP_CATALOG_BIND` | POST | `.../catalog/resource/bind` | 挂载资源节点 |
| `EP_CATALOG_UNBIND` | POST | `.../catalog/resource/unbind` | 解绑资源节点 |

### 3.11 Horizon V1 — Tag/Segment/Export（9 个）

| 端点常量 | 方法 | 路径 | 用途 |
|----------|------|------|------|
| `EP_TAG_LIST` | POST | `.../tag/definition/list` | 标签列表 |
| `EP_TAG_DELETE` | POST | `.../tag/definition/delete` | 删除标签 |
| `EP_TAG_TASK_GET` | POST | `.../tag/task/get` | 标签计算任务状态 |
| `EP_SEGMENT_LIST` | POST | `.../segment/definition/list` | 分群列表 |
| `EP_SEGMENT_DELETE` | POST | `.../segment/definition/delete` | 删除分群 |
| `EP_SEGMENT_TASK_GET` | POST | `.../segment/task/get` | 分群计算任务状态 |
| `EP_EXPORT_CREATE` | POST | `.../entity-list/export-task/create` | 创建实体导出任务 |
| `EP_EXPORT_STATUS` | GET | `.../entity-list/export-task/get-status` | 查询导出任务状态 |

---

## 四、脚本使用

### 4.1 list_events.py — 列事件/查属性

```bash
# 列出所有事件
python3 scripts/list_events.py

# 查看 $AppClick 事件的属性列表
python3 scripts/list_events.py --detail '$AppClick'

# JSON 输出
python3 scripts/list_events.py --json
```

### 4.2 query_segmentation.py — 事件分析

```bash
# 查 3 天 PV（按天）
python3 scripts/query_segmentation.py --event '$pageview' --from 2026-06-01 --to 2026-06-03

# UV 统计，按设备型号分组
python3 scripts/query_segmentation.py --event 'user_login' --from 2026-06-01 --to 2026-06-03 \
  --aggregator UV --group-by 'event.user_login.$device_model'

# 带筛选
python3 scripts/query_segmentation.py --event '$AppStartPassively' --from 2026-06-01 --to 2026-06-03 \
  --filter 'event.$AppStartPassively.$os=IOS'

# 查用户明细
python3 scripts/query_segmentation.py --event 'user_login' --from 2026-06-01 --to 2026-06-03 --users --limit 50
```

**aggregator 可选值**: pv（次数）/ uv（人数）/ sum / avg / max / min / count
**unit 可选值**: HOUR / DAY / WEEK / MONTH

### 4.3 query_sql.py — 自定义 SQL

```bash
# 查登录 UV
python3 scripts/query_sql.py --sql "SELECT count(distinct distinct_id) as uv FROM events.user_login WHERE date >= '2026-06-01' AND date <= '2026-06-03'"

# 按天 PV
python3 scripts/query_sql.py --sql "SELECT date, count(*) as pv FROM events.\\\$pageview WHERE date >= '2026-06-01' GROUP BY date ORDER BY date"

# 查用户行为明细
python3 scripts/query_sql.py --sql "SELECT distinct_id, time, \\$app_version FROM events.\\\$AppClick LIMIT 20"
```

**SQL 语法要点**:
- 事件表名: `events.{事件名}`
- 用户表: `users`
- 日期过滤: `WHERE date >= 'yyyy-MM-dd'`
- 特殊字符属性名需转义: `\$` 前缀的属性如 `\$app_version`

### 4.4 export_data.py — 异步导出

```bash
# 导出全量用户（TABLE 模式）
python3 scripts/export_data.py --attrs id,name,city

# 导出某标签用户（FILE 模式）
python3 scripts/export_data.py --tag "user.活跃度.is_not_null()" --attrs id,活跃度 --format FILE

# 只创建任务
python3 scripts/export_data.py --segment "user.\$SegmentMembership.全部用户 == true" --attrs id --create-only

# 查任务状态
python3 scripts/export_data.py --status <task_id>
```

**异步导出三步**:
1. `create` → 拿 task_id
2. `get-status` 轮询直到 FINISH
3. TABLE 模式用 JDBC 拉取 / FILE 模式下载文件

### 4.5 schema.py — Schema 管理

```bash
# 列事件
python3 scripts/schema.py --list-events

# 查事件属性
python3 scripts/schema.py --fields events.\$AppClick

# 设置属性可见
python3 scripts/schema.py --set-visible users.\$identity_anonymous_id true
```

---

## 五、异步导出完整流程

```python
from _auth import api_post, api_get, async_task_wait, EP_EXPORT_CREATE, EP_EXPORT_STATUS

# 1. 创建导出任务
resp = api_post(EP_EXPORT_CREATE, {
    "entity_name": "user",
    "attribute_paths": ["id", "name", "city"],
    "project_id": 2,  # production 项目的数字 ID
    "segment_rule_expression": {
        "type": "EQL_BASED",
        "eql_segment_rule": {"eql": "user.$SegmentMembership.全部用户 == true"}
    },
    "export_format": {"format_type": "TABLE"}  # 或 "FILE"
})
task_id = resp["data"]["task_id"]

# 2. 轮询等待
result = async_task_wait(task_id)  # 默认最多 300s，每 5s 查一次

# 3. 拉取结果
# TABLE 模式 → 用 JDBC 从导出的表中读
# FILE 模式 → 调下载接口拿文件
```

---

## 六、事件分析请求体结构

```json
{
  "measures": [{
    "event_name": "$AppClick",
    "aggregator": "pv",
    "name": "click_pv",
    "filter": {
      "relation": "and",
      "conditions": [{
        "field": "event.$AppClick.$os",
        "function": "equal",
        "params": ["IOS"]
      }]
    }
  }],
  "from_date": "2026-06-01",
  "to_date": "2026-06-03",
  "unit": "DAY",
  "filter": {
    "relation": "and",
    "conditions": [{"field": "...", "function": "equal", "params": ["..."]}]
  },
  "by_fields": [{"field": "event.$AppClick.$device_model"}]
}
```

- `measures`: 指标集合，可多个
- `filter`（顶层）: 全局筛选，对所有指标生效
- `filter`（measure 内）: 事件级筛选，只对该指标生效
- `by_fields`: 分组维度
- `function` 可选: equal / not_equal / contain / not_contain / greater_than / less_than / is_null / is_not_null

---

## 七、已知事件（24 个）

| 事件名 | 显示名 | 有数据 |
|--------|--------|--------|
| `$AppClick` | App 元素点击 | ✅ |
| `$AppStartPassively` | App 被动启动 | ✅ |
| `$AppEnd` | App 退出 | ✅ |
| `$AppPageLeave` | App 页面离开 | ✅ |
| `$AppInstall` | App 安装后首次启动 | ✅ |
| `$AppPushClick` | App 推送点击 | ✅ |
| `$ProfileMergeEvent` | 用户身份融合 | ✅ |
| `user_login` | 用户登录 | ✅ |
| `user_register` | 用户注册 | ✅ |
| `user_sms_send` | 发送短信验证码 | ✅ |
| `device_add_confirm` | 添加设备-确定添加设备 | ✅ |
| `device_add_check` | 添加设备-获取设备信息 | ✅ |
| `device_firmware_update` | 固件更新操作 | ✅ |
| `survey_feild_info` | 测地-成功创建地块 | ✅ |
| `survey_save_feilds` | 测地-测地流程操作 | ✅ |
| `survey_field_info` | survey_field_info | ✅ |
| `survey_use_mapping_device` | 测地/地块管理-选择/切换测绘设备 | ✅ |
| `operation_lift_mode` | 运输作业-执行自动飞行 | ✅ |
| `auto_operation_task_start` | 自主作业任务启动 | ✅ |
| `operation_auto_work_start` | operation_auto_work_start | ✅ |

---

## 十、常用查询配方

> 详见 [references/common-query-recipes.md](references/common-query-recipes.md)：DAU计算、版本分布、功能渗透率、布尔属性 GROUP BY 替代 WHERE、横竖屏设备分布等。
> 详见 [references/device-classification.md](references/device-classification.md)：SRC遥控器型号、平板vs手机分类方法、横屏使用分析。
> 详见 [references/user-login-event.md](references/user-login-event.md)：user_login 事件字段值域、错误码速查、登录分析常用 SQL。
> 详见 [references/official-api-inventory.md](references/official-api-inventory.md)：官方 Swagger 全量端点清单（63个），含覆盖率审计结果和未覆盖端点列表。

**API 覆盖率（2026-06-03 审计）**：已覆盖 21/63 个官方端点（33%）。主要缺失：PropertyMeta（属性候选值/用户属性）、EventMeta（轻量事件列表）、Session/Path 分析、Dashboard/Dataset/Catalog/SmartAlarm。详见 inventory。

---

## 十一、性能与限流

| 项目 | 限制 |
|------|------|
| 调用频率 | ≤ 3 次/秒 |
| 并发控制 | ≤ 10 |
| SQL 查询默认 limit | 10000 |
| 大数据量导出建议 | 用 JDBC 而非 HTTP |

---

## 数据分析工作流（必读）

**做任何查询前，先了解数据长什么样**：

1. **看事件表有什么事件**：`cat ~/.hermes/data/sensors_metadata/events.json | python3 -c "import sys,json; [print(f'{e[\"name\"]:50s} {e.get(\"display_name\",\"\")}') for e in json.load(sys.stdin)]"`
2. **看某事件有什么属性**：`cat ~/.hermes/data/sensors_metadata/event_{事件名}.json | python3 -c "import sys,json; [print(f'{f[\"name\"]:45s} {f.get(\"display_name\",\"\")} ({f[\"type\"]})') for f in json.load(sys.stdin)]"`
3. **看用户表有什么属性**：`cat ~/.hermes/data/sensors_metadata/users.json | python3 -c "import sys,json; [print(f'{f[\"name\"]:45s} {f.get(\"display_name\",\"\")} ({f[\"type\"]})') for f in json.load(sys.stdin)]"`
4. **刷新元数据缓存**：`python3 ~/.hermes/skills/sensors-analytics/scripts/cache_metadata.py`

**元数据缓存位置**：`~/.hermes/data/sensors_metadata/`
- `events.json` — 24 个事件列表
- `users.json` — 31 个用户属性
- `event_{事件名}.json` — 各事件的属性列表（47~136 个不等）

**分析原则**：
- 查询前先查元数据，搞清楚有哪些字段可用，不要猜
- SQL 里用到的属性名必须跟元数据里完全一致
- 有 `has_data=false` 的属性不要查，没数据
- `$` 前缀是系统内置属性（如 `$province`, `$device_model`），无前缀是业务自定义属性

---

## 九、Pitfalls（踩坑必读）

### 1. sensorsdata-project header 必须传
**症状**: 401 "没有访问权限"
**原因**: 没传 `sensorsdata-project` header
**修复**: 固定传 `"sensorsdata-project": "production"`

### 2. 只有 443 HTTPS 通
**症状**: 连接超时
**原因**: 8107/8006/8086/8088 端口都不开放
**修复**: 用 `https://user-insight.xa.com:443`

### 3. Schema event/list 是 POST 不是 GET
**症状**: "Request method 'GET' is not supported"
**修复**: `api_post(EP_EVENT_LIST, {})` 而不是 `api_get`

### 4. Schema field/list 需要传 schema_name
**症状**: "schema name can not be null"
**修复**: 传 `{"schema_name": "events.$AppClick"}` 或 `{"schema_name": "users"}`

### 5. 事件分析必须传 unit
**症状**: "unit should not be null"
**修复**: payload 里加 `"unit": "DAY"`

### 6. SQL 不能直接查 events.{事件名}
**症状**: `SELECT count(*) FROM events.user_login` 返回 "GRPC 服务发生未知异常"
**原因**: 自定义事件表不支持 `events.{event_name}` 语法
**修复**: 用 `SELECT count(*) FROM events WHERE event = 'user_login'`

### 7. SQL 多行结果是流式 JSON
**症状**: JSON 解析失败
**原因**: 多行结果不是一个 JSON 数组，而是每行一个 JSON 对象拼接
**修复**: query_sql.py 已内置 streaming JSON parser，不需要额外处理

### 8. SQL 中特殊属性名要转义
**症状**: SQL 解析错误
**修复**: `$` 前缀的属性用 `\$` 或在 Python 字符串里用 `\\$`

### 9. field/list 的 schema_name 格式
- 事件属性: `events.{事件名}`（如 `events.$AppClick`）
- 用户属性: `users`

### 10. 导出任务 project_id 是数字不是字符串
- production 的 project_id = 2
- 不是 "production"

### 11. filter.function 不是运算符
- 用 `"equal"` 不是 `"="`
- 用 `"not_equal"` 不是 `"!="`
- 完整列表: equal / not_equal / contain / not_contain / greater_than / less_than / is_null / is_not_null

### 12. SQL 中布尔属性过滤会触发 GRPC 错误
**症状**: `WHERE if_use_route_3d = true` → "GRPC 服务发生未知异常"
**原因**: Sensors SQL 对布尔属性直接 WHERE 过滤不稳定
**修复**: 用 `GROUP BY property_name` 然后从结果中取需要的行
```sql
-- ❌ 会报错
SELECT count(distinct distinct_id) FROM events WHERE event='auto_operation_task_start' AND if_use_route_3d = true
-- ✅ 正常
SELECT if_use_route_3d, count(distinct distinct_id) as uv FROM events WHERE event='auto_operation_task_start' AND date='2026-06-03' GROUP BY if_use_route_3d
```

### 13. DAU 计算要用全事件，不要用单个事件
**症状**: 用 `$AppStartPassively` 查 DAU 只有 1 人
**原因**: `$AppStartPassively` 数据不完整，不代表全部活跃
**修复**: 用全事件表的 distinct_id 统计
```sql
-- ❌ 不准（只有 1）
SELECT count(distinct distinct_id) FROM events WHERE event = '$AppStartPassively' AND date = '2026-06-03'
-- ✅ 准确（DAU = 15401）
SELECT count(distinct distinct_id) FROM events WHERE date = '2026-06-03'
```

### 14. SRC 遥控器的 $screen_orientation 字段不可信
**症状**: SRC4/SRC5/SRC6 等遥控器明明只有横屏物理形态，但 SDK 大量报 `portrait`
**原因**: 遥控器 Android 系统的"自然方向(natural orientation)"配置与物理朝向不一致，SDK 按系统 API `getRotation()` 拿到的值跟实际物理横屏相反。还有部分数据根本没报 orientation（NULL）。
**修复**: 查询横屏/竖屏使用分布时，**必须排除 SRC 系列**（`$model NOT LIKE 'SRC%'`），单独分析遥控器。遥控器天然是横屏设备，不存在竖屏使用场景。
```sql
-- ❌ 把 SRC 混入横竖屏对比，遥控器 portrait 数字是错的
WHERE event = '$AppStart' GROUP BY $screen_orientation
-- ✅ 排除 SRC，只看手机和平板
WHERE event = '$AppStart' AND $model NOT LIKE 'SRC%' GROUP BY $screen_orientation
```

### 15. SQL count(*) vs 事件分析模型 (segmentation) 统计口径不同
**症状**: 同一事件同一天的 PV，SQL `count(*)` 和 segmentation report API 返回的数字差几条到几十条
**原因**: segmentation 模型有内部去重/过滤/时间窗口逻辑，和 raw SQL `count(*)` 不完全等价
**示例**: `$AppStart` 2026-06-02，SQL count(*) = 252391，segmentation = 252407（差 16）
**修复**: 对比数据时用**同一口径**——要么都用 SQL，要么都用 segmentation。**不要用 SQL 和 segmentation 交叉对比**。DAU（全表 distinct_id count）两边一致。
**经验**: 百万级 PV 下 SQL 和界面偶尔差 1-2 条（实时查询时序差异），属正常。

### 16. SQL HAVING 子句触发 GRPC 错误
**症状**: `GROUP BY ... HAVING count(*) >= 1000` → "GRPC 服务发生未知异常"
**原因**: Sensors SQL 引擎不支持 HAVING 子句
**修复**: 用子查询或客户端过滤代替
```sql
-- ❌ GRPC 错误
SELECT $device_model, count(*) as pv FROM events WHERE event = '$AppClick' AND date = '2026-06-02' GROUP BY $device_model HAVING count(*) >= 1000
-- ✅ 客户端过滤
SELECT $device_model, count(*) as pv FROM events WHERE event = '$AppClick' AND date = '2026-06-02' GROUP BY $device_model
-- 然后在 Python 里: [row for row in results if row['pv'] >= 1000]
```
**注意**: WHERE + IS NOT NULL 也可能触发 GRPC 错误（如 `$province IS NOT NULL`），视具体属性而定。遇到 GRPC 错误优先检查是否有 HAVING / IS NOT NULL。

### 17. API 数据与界面数据一致性已验证（2026-06-03）
用 liujian1@xa.com 账号登录神策界面（自定义 SQL 页面），与 API 全面对比：

**简单查询**：
- DAU（2026-06-02）: API 25134 = 界面 25134 ✅
- 总 PV: API 1050969 vs 界面 1050970（差 1，正常）
- Top 10 事件 PV/UV: 逐条对比全部一致 ✅
- user_login 按 OS 分组 UV: Android 8422 / HarmonyOS 1407 / iOS 27 ✅

**复杂查询**（多维分组、CASE WHEN、IN 子句、日期范围）：
- `$app_version × $os` 分组 LIMIT 15: 15 行逐条完全一致 ✅
- CASE WHEN 多事件按天趋势（6天）: 6 行完全一致 ✅
- IN 子句 3 事件 × 6 天 = 18 行: 逐条完全一致 ✅

**结论**: API 数据完全可信，复杂查询语法（GROUP BY 多字段、CASE WHEN、IN、ORDER BY、LIMIT、日期范围）均正常工作。可放心用于业务分析。

### 14. App 版本号格式不带 "V" 前缀
**症状**: `WHERE $app_version = 'V7.5.1'` 返回 0 行
**原因**: 版本号存储为 `7.5.1` 而非 `V7.5.1`
**修复**: 去掉 V 前缀
```sql
-- ❌ 返回 0
WHERE $app_version = 'V7.5.1'
-- ✅ 正确
WHERE $app_version = '7.5.1'
```

### 15. position_mode 在不同事件中用完全不同的枚举！
**症状**: 查 `auto_operation_task_start` 的 position_mode 按 survey 事件的经验写 "正常/定位中/未连接"，结果返回 0 行
**原因**: 
- **survey 事件**（survey_save_feilds / survey_use_mapping_device）的 position_mode 存的是 **UI 多语言显示文本**（正常/定位中/未连接 + 英/葡/泰/韩/越/土/俄/罗/保/印尼等翻译）
- **auto_operation_task_start** 的 position_mode 存的是 **技术枚举**: RTK / VRTK / GNSS / PPP / 未知
**修复**: 查不同事件时用不同的归一化 CASE WHEN，详见 references/verified-events.md
```sql
-- auto_operation_task_start 直接可用
SELECT position_mode, count(*) FROM events WHERE event='auto_operation_task_start' ...

-- survey 事件需要多语言归一化
SELECT
  CASE
    WHEN position_mode IN ('正常','Active','Ativo','Activo','Normal','Aktif','Активно','정상','Kích hoạt','普通') THEN '正常'
    WHEN position_mode IN ('定位中','Localizando ','Locating','測位中') THEN '定位中'
    WHEN position_mode IN ('未连接','Desconectado','Disconnected','Отключено','Bağlantısı kesildi','연결되지 않음') THEN '未连接'
    ELSE position_mode
  END as mode_group, count(*) FROM events WHERE event='survey_save_feilds' ...
```

### 16. positioning_reference 存在大小写变体
**症状**: 按 positioning_reference 分组发现 CORS 和 cors 是两行
**修复**: 合并处理 `CASE WHEN positioning_reference = 'cors' THEN 'CORS' ELSE positioning_reference END`

### 17. 国内/海外分析时 $country IS NULL 归国内
**说明**: `$country` 为空的记录大概率是国内老版本 App 未上报国家字段，应归入国内
```sql
CASE WHEN $country = '中国' OR $country = 'China' OR $country IS NULL THEN '国内' ELSE '海外' END
```

### 15. 业务枚举字段多语言、多版本共存，必须归一化
**症状**: `position_mode` / `fail_text` 等字段 GROUP BY 后出现 30+ 行，同一状态被拆成多行
**原因**: App 随系统语言输出枚举值（正常/Active/Ativo/Activo/Активно/정상...），且新旧版本 App 文案不同
**修复**: 用 `CASE WHEN ... IN (...)` 归一化为业务语义分组，见 `references/common-query-recipes.md` 配方 10
**常见多语言枚举字段**:
- `position_mode`: 正常/Active/Ativo/Activo/Normal/Aktif/Активно/정상/普通/نورمال/ปกติ 等
- `fail_text`: 同错误码 1101 有中文新旧格式 + 英文 + 其他语种
- 按 `fail_reason`（错误码数字）聚合更可靠，不要按 `fail_text` 聚合

### 16. 国内/海外拆分用 $country 字段
**修复**: `$country` 存中文国名（'中国'、'土耳其'），NULL 通常为国内
```sql
-- 国内
WHERE $country = '中国' OR $country = 'China' OR $country IS NULL
-- 海外
WHERE $country != '中国' AND $country != 'China' AND $country IS NOT NULL
```

### 18. 官方 Swagger 文件的 URL 和下载方法
**场景**: 需要审计完整 API 端点覆盖时
**URL 模式**: `https://manual.sensorsdata.cn/openapi/api/v1/openapi_file?file_name={filename}`
**发现方法**: 浏览器打开 `https://manual.sensorsdata.cn/openapi?tab=reference&type=sa&suite=sa3.0.4`，点左侧菜单项，用 `performance.getEntriesByType('resource')` 捕获 `openapi_file` 请求的文件名。
**已知文件名**: 详见 `references/official-api-inventory.md` 顶部表格。

### 19. Model v1 swagger JSON 解析报错
**症状**: `json.loads()` 报 `Invalid control character` 或 `Extra data`
**原因**: Model-v1 swagger 文件包含控制字符（\t 等）且有多个 JSON 对象拼接
**修复**: 用 `json.load(f, strict=False)` 并截取第一个完整 JSON 对象
```python
import json
with open('swagger.json') as f:
    data = json.load(f, strict=False)  # 忽略控制字符
# 如果报 Extra data，按大括号深度截取第一个对象
```

### 20. 列事件：EventMeta（轻量 GET）vs Horizon Schema（完整 POST）
**场景**: 需要知道项目有哪些事件时
**推荐**: 用 `EP_EVENTMETA_ALL`（GET，无需 payload，返回精简列表）
**备选**: `EP_EVENT_LIST`（POST `{}`，返回完整 schema 定义，更重）
```python
# ✅ 快速列事件 — 轻量 GET
events = api_get(EP_EVENTMETA_ALL)
# ✅ 需要完整定义（display_name, type, has_data 等）
events = api_post(EP_EVENT_LIST, {})
```
**经验**: 日常查看用 EventMeta，需要元数据详情（如修改可见性）才用 Schema。

### 21. 查属性候选值：PropertyMeta 比 SQL GROUP BY 更高效
**场景**: 想知道某个属性有哪些取值（如 `$device_model` 有哪些型号）
**❌ 低效**: SQL `SELECT $device_model, count(*) GROUP BY $device_model` — 数据量大时慢
**✅ 高效**: `EP_PROP_VALUES` 直接返回属性候选值
```python
# ✅ 快速拿候选值
resp = api_post(EP_PROP_VALUES, {
    "property_name": "$device_model",
    "event_name": "$AppClick"  # 可选，限定某事件下的候选值
})
values = resp.get("data", [])
```
**适用**: 下拉选项填充、筛选条件枚举、数据字典生成。

### 22. 查用户属性/分群列表：PropertyMeta 一套搞定
**场景**: 需要列出所有用户属性、用户分群、用户标签
```python
# 所有用户属性
user_props = api_get(EP_PROP_USER_ALL)
# 所有用户分群
user_groups = api_get(EP_PROP_USER_GROUPS)
# 用户标签（带目录结构）
user_tags = api_get(EP_PROP_USER_TAGS)
```
**注意**: 这些比 Horizon 的 tag/segment 端点更适合"列表浏览"场景。Horizon 端点更适合"创建/删除/计算任务"管理场景。

### 23. Dashboard/Lego：快速获取预置概览数据，不用自己写 SQL
**场景**: 需要项目的基础数据概览（DAU/新增/留存等预置指标）
```python
# 获取所有概览分组（看有哪些看板）
groups = api_get(EP_DASH_NAVIGATION)
# 获取所有基础数据概览（DAU、新增、留存等，平台预计算好的）
lego = api_get(EP_DASH_LEGO)
# 获取单个看板详情
detail = api_get(EP_DASH_DETAIL, params={"dashboard_id": "xxx"})
```
**经验**: 日常看 DAU/新增 等标准指标，先试 Lego，比手写 SQL 快。只有自定义维度分析才用 SQL。

### 24. 分析模型选型速查
| 分析目标 | 用哪个模型 | 端点 |
|----------|-----------|------|
| 某事件发生次数/人数 | 事件分析 | `EP_SEG_REPORT` |
| 用户从 A 到 B 的转化率 | 漏斗分析 | `EP_FUNNEL_REPORT` |
| 做了 A 的人后来做 B 的比例 | 留存分析 | `EP_RETENTION_REPORT` |
| 事件发生的频率分布 | 分布分析 | `EP_ADDICTION_REPORT` |
| 两步操作之间花了多久 | 间隔分析 | `EP_INTERVAL_REPORT` |
| 是什么触发了目标行为 | 归因分析 | `EP_ATTRIBUTION_REPORT` |
| 用户的长期价值 | LTV 分析 | `EP_LTV_REPORT` |
| 一次会话内的行为模式 | Session 分析 | `EP_SESSION_REPORT` |
| 用户的操作路径 | 用户路径 | `EP_USER_PATH_USERS` |
| 灵活自定义查询 | 自定义 SQL | `EP_SQL_QUERY` |

**原则**: 能用专用模型就不用 SQL。专用模型有更好的过滤、分组、时间窗口支持，且结果格式更结构化。SQL 是最后兜底方案。

### 25. 复杂 SQL 的最佳实践
1. **多维分组优先 SQL**: 3+ 维度的 GROUP BY，segmentation API 不支持，SQL 可以
2. **CASE WHEN 做多事件对比**: 一条 SQL 同时查多个事件的指标，比分别调 segmentation 快
3. **日期趋势用 GROUP BY date**: `SELECT date, ... GROUP BY date ORDER BY date`
4. **大数据量加 LIMIT**: 默认 limit 10000，超过就截断，主动加 LIMIT 控制
5. **客户端后处理**: HAVING → 客户端 filter；IS NOT NULL → 客户端过滤
6. **IN 子句批量事件**: `WHERE event IN ('a', 'b', 'c')` 比 UNION 高效

---

## 十、变更日志

### 2026-06-03 v1.2.0（全端点覆盖版）
- ✅ `_auth.py`: 77 个端点常量（官方 63 + Portal 5 + Tag/Segment/Export 9）
- ✅ 新增端点类别：Dashboard(6), Dataset(7), SmartAlarm(2), EventMeta(2), PropertyMeta(6), Channel 完整 CRUD(5), Schema 完整(13), Catalog(3), Session(2), UserPath(1)
- ✅ 新增 Pitfall 20-25：EventMeta vs Schema 选型、PropertyMeta 候选值查询、用户属性/分群列表、Dashboard 概览、分析模型选型速查、复杂 SQL 最佳实践
- ✅ SKILL.md 端点索引表从 3 节扩展到 11 节

### 2026-06-03 v1.1.0（API 覆盖率审计版）
- ✅ 新增 `references/official-api-inventory.md`：官方 63 个端点完整清单 + 覆盖状态
- ✅ 覆盖率审计：21/63（33%），42 个端点缺失已分类记录
- ✅ 新增 Pitfall 18-19：Swagger URL 发现方法 + Model JSON 解析坑

### 2026-06-03 v1.0.0（正式版）
- ✅ Key 确认可用（project=production）
- ✅ _auth.py: 全端点常量 + api_post/api_get/parse_response/async_task_wait helper
- ✅ 5 个脚本: list_events / query_segmentation / query_sql / export_data / schema
- ✅ 24 个事件已确认
- ✅ 端到端验证通过

### 2026-06-02 v0.1.0（脚手架）
- 初始框架搭建，卡在 Key 权限

## 适用场景

- 查询极飞农服 App 的用户行为数据（PV/UV/DAU/留存/漏斗等）
- 用自定义 SQL 做灵活分析（版本分布、功能渗透率、设备型号分布等）
- 管理事件/属性的元数据（可见性、字典、Schema 定义）
- 导出标签/分群用户数据，或创建异步导出任务
- 管理渠道追踪链接（CRUD）、查看 Dashboard 概览和智能预警

## 前提条件

- API Key（35 字符 #K-xxx）已存储在 `~/.hermes/credentials/sensors.txt`（chmod 600）
- 网络可访问 `user-insight.xa.com:443`（仅 443 端口，其他端口不通）
- 请求必须同时传 `api-key` 和 `sensorsdata-project: production` 两个 header
- Python 3 + requests 库

## 能力清单

| 能力 | 说明 | 限制 |
|------|------|------|
| 事件分析（19 个模型） | 事件/漏斗/留存/分布/间隔/归因/LTV/Session/路径/属性分析 | 每个模型有特定必填参数 |
| 自定义 SQL | 灵活查询事件表和用户表 | ≤3次/秒，并发≤10，不支持 HAVING |
| Dashboard 概览 | 获取平台预计算的 DAU/新增/留存等标准指标 | 只读（部分写操作需权限） |
| 业务集市 | 查询/刷新业务模型数据 | 7 个端点 |
| 事件/属性元数据 | 列出事件、属性、候选值、用户分群 | Schema 端点用 POST 不是 GET |
| 渠道追踪 | 完整 CRUD（增删改查渠道链接和活动） | 5 个端点 |
| 标签/分群/导出 | 管理标签和分群定义，创建异步导出任务 | 导出为异步三步流程 |
| 智能预警 | 查看预警列表和配置详情 | 只读 2 个端点 |

## 预期效果

- 事件分析 API 返回结构化的时间序列数据（按天/周/月分组）
- SQL 查询返回 JSON 格式的结果集（多行为流式 JSON，脚本已内置解析器）
- 元数据查询秒级返回事件列表、属性列表及候选值
- 异步导出任务创建后返回 task_id，轮询直到 FINISH 后可拉取数据
- API 数据与神策界面完全一致（已通过全面对比验证）

## Changelog

- **1.2.0** (2026-06-14): 初始版本，可移植性改造
