# 飞机/无人机维度查询配方（drone operation analysis）

## 触发场景

运营/客服/产品给出一个飞机序列号（drone_sn，如 `186325P18225512V727T`）问：
- 这台飞机今天作业了吗？作业了几次？成功了吗？
- 这台飞机最近有什么故障？错误码是什么意思？
- 这台飞机已经多久没能正常作业了？

## 核心事件与字段

### auto_operation_task_start（自主作业任务启动）

这是**查飞机作业的核心事件**，含 `drone_sn` 字段可直接按飞机序列号过滤。

| 字段 | 类型 | 说明 |
|------|------|------|
| `drone_sn` | string | 飞机序列号（如 `186325P18225512V727T`） |
| `fail_stage` | string | 失败阶段：`任务加载` / `任务启动` / `自检` / 空（成功） |
| `fail_text` | string | 失败描述（含错误码），空 = 无失败记录 |
| `auto_task_id` | string | 任务唯一ID，用于关联其他作业事件 |
| `work_field_id` | string | 地块ID |
| `drone_electricity` | number | 电量百分比 |
| `estimate_work_area` | number | 预计作业面积（亩） |
| `route_type` | string | 航线类型（如"往返航线"）。⚠️ 注意：存在"往返航线"和"标准往返航线"两个独立枚举值，不是父子关系，分析时需分开统计或产品确认后合并 |
| `position_mode` | string | 定位模式：RTK / VRTK / GNSS / PPP / 未知（技术枚举，非 UI 文案） |
| `communication_link` | string | 通信链路（如"移动通信"） |
| `if_resume_operation` | string/bool | 是否续作业 |
| `if_use_bound` | number/bool | 是否开启扫边：1=开启，0=不扫边 |
| `if_only_bound` | number/bool | 是否只执行扫边航线：1=全部扫边（仅执行扫边航线）；0 需结合 `if_use_bound` 判断为部分扫边或不扫边 |
| `device_model` | string | 设备型号（UAV 编号，如 UAV40/UAV43）。⚠️ 代替 drone_model 做 GROUP BY（drone_model 会触发 GRPC 错误） |

### operation_auto_work_start（实际作业开始）

⚠️ **此事件没有 `drone_sn` 字段**，只有 `auto_task_id`。要判断飞机是否真正起飞作业，需要：
1. 从 `auto_operation_task_start` 拿到 `auto_task_id` 列表
2. 用这些 ID 查 `operation_auto_work_start` 是否有匹配记录

## 查询模式

### 模式0：航线类型与扫边组合分析

```sql
-- 航线类型分布（注意"往返航线"和"标准往返航线"是两个独立枚举）
SELECT route_type, count(*) AS cnt
FROM events
WHERE event = 'auto_operation_task_start'
  AND date >= '<START_DATE>' AND date <= '<END_DATE>'
GROUP BY route_type
ORDER BY cnt DESC;

-- 往返航线中的扫边组合（不扫边/部分扫边/仅扫边）
SELECT if_use_bound, if_only_bound, count(*) AS cnt
FROM events
WHERE event = 'auto_operation_task_start'
  AND date >= '<START_DATE>' AND date <= '<END_DATE>'
  AND route_type = '往返航线'
GROUP BY if_use_bound, if_only_bound
ORDER BY cnt DESC;
-- 组合含义：
--   if_use_bound=0, if_only_bound=0 → 不扫边
--   if_use_bound=1, if_only_bound=0 → 部分扫边（主航线+扫边）
--   if_use_bound=1, if_only_bound=1 → 全部扫边（仅执行扫边航线）
--   if_use_bound=0, if_only_bound=1 → 异常组合，单独保留并核查数据定义
```

### 模式1：飞机今日作业概览

```sql
SELECT count(*) AS total_starts,
       sum(CASE WHEN fail_text = '' OR fail_text IS NULL THEN 1 ELSE 0 END) AS no_fail,
       sum(CASE WHEN fail_text != '' AND fail_text IS NOT NULL THEN 1 ELSE 0 END) AS failed
FROM events
WHERE event = 'auto_operation_task_start'
  AND drone_sn = '186325P18225512V727T'
  AND date = '2026-06-24';
```

### 模式2：失败明细（fail_stage + fail_text 分布）

```sql
SELECT fail_stage, fail_text, count(*) AS cnt
FROM events
WHERE event = 'auto_operation_task_start'
  AND drone_sn = '186325P18225512V727T'
  AND date = '2026-06-24'
  AND fail_text IS NOT NULL
  AND fail_text != ''
GROUP BY fail_stage, fail_text
ORDER BY cnt DESC;
```

### 模式3：近N天失败趋势

```sql
SELECT date,
       count(*) AS total,
       sum(CASE WHEN fail_text = '' OR fail_text IS NULL THEN 1 ELSE 0 END) AS no_fail,
       sum(CASE WHEN fail_text != '' AND fail_text IS NOT NULL THEN 1 ELSE 0 END) AS failed
FROM events
WHERE event = 'auto_operation_task_start'
  AND drone_sn = '186325P18225512V727T'
  AND date >= '2026-06-18'
GROUP BY date
ORDER BY date;
```

### 模式4：判断是否真正起飞作业（关联 auto_task_id）

```sql
-- 第一步：拿飞机今日所有 task_id
SELECT auto_task_id, fail_stage, fail_text
FROM events
WHERE event = 'auto_operation_task_start'
  AND drone_sn = '186325P18225512V727T'
  AND date = '2026-06-24';

-- 第二步：查这些 task_id 是否有 operation_auto_work_start
SELECT count(*) AS work_starts
FROM events
WHERE event = 'operation_auto_work_start'
  AND auto_task_id IN ('id1', 'id2', 'id3')  -- 从第一步拿到
  AND date = '2026-06-24';
-- work_starts = 0 → 全部没起飞
```

### 模式5：从飞机反查用户信息

```sql
SELECT distinct_id, $model, $app_version, $os, $province, $city
FROM events
WHERE event = 'auto_operation_task_start'
  AND drone_sn = '186325P18225512V727T'
  AND date = '2026-06-24'
LIMIT 1;
-- 拿到 distinct_id 后可继续查用户行为（见 user-journey-recipes.md）
```

### 模式6：从飞机反查用户后查完整行为时间线

当需要知道"飞机失败后用户在 App 里做了什么"时，先从飞机事件拿 distinct_id，再查用户行为：

```sql
-- 第一步：从飞机事件拿 distinct_id
SELECT distinct_id FROM events
WHERE event = 'auto_operation_task_start'
  AND drone_sn = '186325P18225512V727T'
  AND date = '2026-06-24'
LIMIT 1;

-- 第二步：用 distinct_id 查该用户指定时间段的所有事件（还原操作路径）
SELECT time, event, fail_stage, fail_text, "$screen_name"
FROM events
WHERE distinct_id = '35C50FCF1B5456ECBC177684157BFFE4'
  AND date = '2026-06-24'
  AND time >= 1719219600000  -- 毫秒时间戳，如 19:00 的起点
ORDER BY time DESC
LIMIT 200;
```

这样可以把飞机侧的失败记录和用户侧的操作行为（升级固件、重试、退出 App 等）拼成完整时间线。
详见 [references/user-journey-recipes.md](references/user-journey-recipes.md) 的 $screen_name 语义表。

### 模式7：飞机历史活跃概览

```sql
SELECT date, count(*) AS task_starts
FROM events
WHERE event = 'auto_operation_task_start'
  AND drone_sn = '186325P18225512V727T'
  AND date >= '2026-04-01'
GROUP BY date
ORDER BY date;
```

## fail_text 常见值与含义

| fail_text | fail_stage | 含义 |
|-----------|-----------|------|
| 空/NULL | 空 | 无失败记录（但未必起飞成功，需查 operation_auto_work_start） |
| `任务加载/加载失败,航线上传失败` | `任务加载` | 航线数据未能上传到飞机，可能是通信/RTK问题 |
| `任务启动/起飞失败,未知错误，请联系客服或售后(0xXXXXXXXX)` | `任务启动` | 起飞阶段失败，括号内为固件错误码 |
| `自检/xxx` | `自检` | 飞机自检未通过 |

## 错误码查询

`fail_text` 中括号内的 `0x` 开头十六进制码是固件级错误码。查询方式：

1. **事件错误码 API**（见 event-error-sync skill）：
   - `GET https://$RELEASE_PLATFORM_HOST/event_manage_admin/v2/view/?product_uuid=<UUID>&lang=zh`
   - 植保系列 product_uuid = `5639054e-77a7-4e73-ab26-f7fd5153fc25`（22模块561条）
   - 航测系列 product_uuid = `14e920af-34e5-4fb3-904f-15425251a9d8`
   - ⚠️ 需将十六进制转十进制查询（如 `0x0F350000` → `255131648`）
   - ⚠️ **并非所有错误码都注册了**，如 `0x0F350000` 在两个产品线中均未匹配，App 端显示"未知错误"

2. **错误码未注册时的处理**：
   - 告诉用户该错误码未在错误码字典中注册，App 端提示为"未知错误"
   - 建议联系售后/研发确认固件级错误码含义
   - 不要编造含义

## 典型分析案例

### 案例：飞机持续一周无法作业

```
飞机：186325P18225512V727T
用户：distinct_id=35C50FCF1B5456ECBC177684157BFFE4，Android V2463A/App 7.5.1，湖南益阳

今日(6/24)：16次任务启动，0次实际作业
  - 6次"任务加载/加载失败,航线上传失败"
  - 1次"任务启动/起飞失败,未知错误(0x0F350000)"
  - 9次无报错但也未进入 operation_auto_work_start

近7天：46次任务启动，0次成功作业
  - 6/24: 7次失败（6航线上传+1起飞失败）
  - 6/22: 2次失败（航线上传）
  - 6/21: 1次失败（航线上传）

两种失败模式：
  ① 任务加载阶段 → 航线数据上传失败（通信/RTK问题）
  ② 任务启动阶段 → 起飞失败，错误码 0x0F350000（未在字典注册）

结论：该飞机已持续一周无法正常作业，问题集中在航线上传和起飞阶段。
```

## Pitfalls

1. **`operation_auto_work_start` 没有 `drone_sn` 字段** — 不能直接按飞机查"是否真正作业了"，必须通过 `auto_task_id` 间接关联。
2. **`fail_text` 为空 ≠ 作业成功** — 无报错记录只说明任务启动阶段没报错，但不代表飞机真正起飞作业了。必须查 `operation_auto_work_start` 确认。
3. **错误码需十六进制转十进制查 API** — `fail_text` 里是 `0x0F350000`，API 需要十进制 `255131648`。
4. **部分错误码未注册** — 查不到不代表不存在，可能是固件级新增码，需联系售后确认。
5. **SELECT 列数过多 + NULL 字段 → 流式 JSON 解析列错位** — 查 `auto_operation_task_start` 时选 8+ 列且部分为 NULL，NDJSON 行解析可能错位。解决：优先查核心字段（fail_stage, fail_text, auto_task_id），分批补充其他字段；或用 GROUP BY 聚合查询代替明细查询。
6. **drone_sn 格式** — 飞机序列号格式为数字+字母组合（如 `186325P18225512V727T`），不是纯数字，SQL 里用字符串引号。
7. **HOUR(time) 可用** — 提取小时用 `HOUR(time)`，不用 `to_time()` 或 `SUBSTR(time, 1, 13)`（后者会 GRPC 报错）。
8. **数据上报有延迟** — 用户刚操作完 App 后立刻查神策，事件可能还没入库（通常 30s~5min 延迟）。用户问"现在呢"时，如果上次查到的最后事件距当前时间 <5 分钟，应告知"数据可能有上报延迟，稍后再查"。
9. **`route_type` 存在"往返航线"和"标准往返航线"两个独立枚举** — 不是父子关系，分析时需分开统计；只有产品口径明确要求时才合并。不要把某次查询的数量写成长期固定值。
10. **`if_use_bound` + `if_only_bound` 组合定义扫边状态** — 见模式0。布尔字段 GROUP BY 比 WHERE 过滤更稳定（见 Pitfall 12），多字段组合 GROUP BY 时列数控制在 4 列以内避免 GRPC。
11. **`drone_model` GROUP BY 触发 GRPC，改用 `device_model`** — 2026-07-28 实测：`SELECT drone_model, count(*) FROM events WHERE event='auto_operation_task_start' GROUP BY drone_model` → "GRPC 服务发生未知异常"。`device_model` 可用于 UAV 机型分组；空值统一标注为"未识别"，空值比例必须按当前查询窗口现场计算，不复用历史比例。
