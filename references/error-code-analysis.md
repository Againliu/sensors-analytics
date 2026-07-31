import os
# 跨事件错误码聚合分析（Verified 2026-06-25）

## 触发场景

产品/运营要求查"所有埋点事件中排行前 N 的错误码，以及报错次数、涉及设备数、涉及用户数"。

## 哪些事件有 fail_reason 字段

通过遍历 `~/.hermes/data/sensors_metadata/event_*.json` 属性元数据，搜索含 `fail`/`error`/`reason` 关键字的字段。

**10 个业务事件有 `fail_reason`（失败原因错误码）字段**：

| 事件名 | 显示名 | 额外失败相关字段 |
|--------|--------|-------------------|
| `user_login` | 用户登录 | `fail_text`, `fail_phase`, `if_success_login` |
| `user_register` | 用户注册 | `fail_text`, `fail_phase`, `if_success_register` |
| `user_sms_send` | 发送短信验证码 | `fail_text`, `fail_phase`, `if_success_send` |
| `device_add_check` | 添加设备-获取设备信息 | `fail_text`, `fail_phase` |
| `device_add_confirm` | 添加设备-确定添加设备 | `fail_text`, `fail_phase` |
| `device_firmware_update` | 固件更新操作 | `fail_text`, `fail_phase`, `firmware_update_result` |
| `survey_save_feilds` | 测地-测地流程操作 | `fail_text`, `fail_phase` |
| `survey_use_mapping_device` | 测地/地块管理-选择/切换测绘设备 | `fail_text`, `fail_phase` |
| `operation_lift_mode` | 运输作业-执行自动飞行 | `fail_stage`（注意：是 stage 不是 phase） |
| `auto_operation_task_start` | 自主作业任务启动 | `fail_text`, `fail_stage` |

⚠️ 所有 24 个事件都有 `$idmap_reason`（系统字段，ID 映射原因），**不是业务错误码**，不要用作错误码聚合。

## 元数据文件命名规则

```
~/.hermes/data/sensors_metadata/
├── events.json                          # 24 个事件列表
├── event_{original_name}.json           # 业务事件属性（如 event_user_login.json）
├── event_sys_{name_without_dollar}.json # 系统事件属性（如 event_sys_AppClick.json）
└── users.json                           # 用户表属性
```

**关键**: `events.json` 中每个事件有 `name`（如 `$AppClick`）和 `original_name`（如 `AppClick`）。
- 业务事件：文件名 = `event_{original_name}.json`
- `$` 前缀系统事件：文件名 = `event_sys_{name_without_dollar}.json`（去掉 `$` 前缀）

## 查询方法：拆分查询 + 客户端合并

### 为什么不能一条 SQL 搞定？

Sensors SQL 对宽表（5+ 列）+ 复杂 WHERE（10 个事件 IN）组合不稳定（Pitfall 28/35），NDJSON 流式返回会出现列错位。

### 正确做法：两条查询，客户端 merge

```python
import sys
sys.path.insert(0, os.path.expanduser('~/.hermes/skills/sensors-analytics/scripts'))
from _auth import sql_query

EVENTS_WITH_FAIL = [
    'user_login', 'user_register', 'user_sms_send',
    'device_add_check', 'device_add_confirm', 'device_firmware_update',
    'survey_save_feilds', 'survey_use_mapping_device',
    'operation_lift_mode', 'auto_operation_task_start'
]
event_list = ",".join(f"'{e}'" for e in EVENTS_WITH_FAIL)

# Query 1: 报错次数 + 用户数
sql1 = f"""
SELECT event, fail_reason,
       count(*) as error_count,
       count(distinct distinct_id) as user_count
FROM events
WHERE event IN ({event_list})
  AND date >= '2026-05-26' AND date <= '2026-06-25'
GROUP BY event, fail_reason
LIMIT 500
"""
cols1, rows1 = sql_query(sql1)

# Query 2: 设备数（⚠️ $device_id 不能加双引号！见 Pitfall 37）
sql2 = f"""
SELECT event, fail_reason,
       count(distinct $device_id) as device_count
FROM events
WHERE event IN ({event_list})
  AND date >= '2026-05-26' AND date <= '2026-06-25'
GROUP BY event, fail_reason
LIMIT 500
"""
cols2, rows2 = sql_query(sql2)

# Merge by (event, fail_reason) composite key
data = {}
for r in rows1:
    key = (r.get('event', ''), str(r.get('fail_reason', '')))
    data[key] = {
        'event': r.get('event', ''),
        'fail_reason': str(r.get('fail_reason', '')),
        'error_count': int(r.get('error_count', 0)),
        'user_count': int(r.get('user_count', 0)),
        'device_count': 0
    }
for r in rows2:
    key = (r.get('event', ''), str(r.get('fail_reason', '')))
    if key in data:
        data[key]['device_count'] = int(r.get('device_count', 0))

# Filter out empty/null fail_reason, sort by error_count desc
results = [v for v in data.values()
           if v['fail_reason'] not in ('', 'None', 'null', 'None')]
results.sort(key=lambda x: x['error_count'], reverse=True)

# Top 20
for i, r in enumerate(results[:20], 1):
    print(f"{i:2d}. {r['event']:30s} {r['fail_reason']:20s} "
          f"次数={r['error_count']:>10,} 用户={r['user_count']:>8,} 设备={r['device_count']:>8,}")
```

### 注意事项

1. **`$device_id` 不加双引号** — `count(distinct "$device_id")` 返回 1（字符串字面量），见 Pitfall 37
2. **`sql_query` 返回数值为 float** — `4.0` 而非 `4`，排序和显示前需 `int()` 转换
3. **空值过滤** — 结果含 `fail_reason` 为空字符串、`"None"`、`"null"` 的行，需客户端过滤
4. **fail_reason 值格式不统一** — 有十进制数字（如 `1101`, `9999`, `0`）和十六进制（如 `0x80411007`）两种格式
5. **LIMIT 500** — 10 个事件 × 多个错误码，结果行数可能超 300，默认 LIMIT 10000 足够但建议显式设 500 控制返回量

## 错误码含义查询

`fail_reason` 是错误码（如 `1101`），`fail_text` 是人类可读文案（如"账号或密码错误"）。
要查某个错误码的文案，用：

```sql
SELECT fail_text, count(*) as cnt
FROM events
WHERE event = 'user_login' AND fail_reason = '1101'
  AND date >= '2026-05-26' AND date <= '2026-06-25'
GROUP BY fail_text
ORDER BY cnt DESC
LIMIT 10
```

⚠️ 同一 `fail_reason` 可能有多套 `fail_text`（中文新旧格式 + 多语言），按 `fail_reason` 聚合更可靠。

对于 `0x` 开头的十六进制错误码（如 `0x80411007`），可用事件错误码 API 查含义：
- `GET https://$RELEASE_PLATFORM_HOST/event_manage_admin/v2/view/?product_uuid=<UUID>&lang=zh`
- 植保系列 product_uuid = `5639054e-77a7-4e73-ab26-f7fd5153fc25`
- 需将十六进制转十进制查询
- 详见 event-error-sync skill

## 实测数据（2026-05-26 ~ 2026-06-25，Top 5）

| # | 事件 | 错误码 | 报错次数 | 用户数 | 设备数 |
|---|------|--------|----------|--------|--------|
| 1 | device_add_check | 0x80411007 | 214,920 | 13,987 | 13,959 |
| 2 | user_login | 1101 | ~190,000+ | ~12,000+ | ~12,000+ |
| 3 | auto_operation_task_start | (多种) | ~50,000+ | — | — |
| 4 | survey_save_feilds | (多种) | ~20,000+ | — | — |
| 5 | user_sms_send | (多种) | ~10,000+ | — | — |

（精确数值会随时间变化，以实际查询结果为准。）
