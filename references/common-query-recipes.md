# 神策常用查询配方（Verified 2026-06-03）

## 1. DAU（日活跃用户）

```sql
-- ✅ 全量 DAU（当天任意事件触发）
SELECT count(distinct distinct_id) as dau FROM events WHERE date = 'YYYY-MM-DD'

-- ✅ 登录 UV（当天登录人数，通常 < DAU）
SELECT count(distinct distinct_id) as uv FROM events WHERE event = 'user_login' AND date = 'YYYY-MM-DD'
```

⚠️ **不要用 `$AppStartPassively` 查 DAU**，该事件数据不完整，实际 UV 可能只有 1。

---

## 2. App 版本分布

```sql
-- Top N 版本分布（当天）
SELECT \$app_version as version, count(distinct distinct_id) as uv
FROM events
WHERE date = 'YYYY-MM-DD'
GROUP BY \$app_version
ORDER BY uv DESC
LIMIT 10
```

⚠️ 版本号格式：**不带 V 前缀**，如 `7.5.1` 而非 `V7.5.1`。

---

## 3. 特定功能使用率（按事件属性）

```sql
-- ❌ 直接 WHERE 过滤布尔属性 → GRPC 报错
SELECT count(distinct distinct_id) FROM events
WHERE event = 'auto_operation_task_start' AND if_use_route_3d = true

-- ✅ 用 GROUP BY 代替
SELECT if_use_route_3d, count(distinct distinct_id) as uv
FROM events
WHERE event = 'auto_operation_task_start' AND date = 'YYYY-MM-DD'
GROUP BY if_use_route_3d
ORDER BY uv DESC
```

计算占比：功能UV / 事件总UV 或 功能UV / 当日DAU，取决于要回答的问题。

---

## 4. 某事件的用户总数（作业类）

```sql
-- 当天有自主作业行为的用户数
SELECT count(distinct distinct_id) as uv
FROM events
WHERE event = 'auto_operation_task_start' AND date = 'YYYY-MM-DD'
```

---

## 5. 版本 × 功能交叉分析

```sql
-- 某功能的用户使用版本分布
SELECT \$app_version, count(distinct distinct_id) as uv
FROM events
WHERE event = 'auto_operation_task_start'
  AND date = 'YYYY-MM-DD'
GROUP BY \$app_version
ORDER BY uv DESC
```

---

## 6. 渗透率计算模板

```
功能渗透率 = 功能UV / DAU × 100%
功能作业渗透率 = 功能UV / 作业总UV × 100%  （更聚焦）
```

---

## 关键数据（2026-06-03 实测）

| 指标 | 数值 |
|------|------|
| DAU | 15,401 |
| 登录UV | 7,869 |
| 自主作业UV | 6,936 |
| 三维航线作业UV | 126（占作业1.80%，占DAU 0.82%） |
| V7.5.1用户 | 7,886（占51.2%） |
| V7.4.2用户 | 5,703（占37.0%） |

---

## 7. 横屏使用：手机 vs 平板

```sql
-- 必须排除 SRC 遥控器（SDK 横竖屏报告不准，详见 device-classification.md）
SELECT
  CASE
    WHEN \$screen_height < 2000 AND \$screen_width < 2000 THEN '平板'
    ELSE '手机'
  END as device_type,
  \$screen_orientation as orientation,
  count(distinct distinct_id) as uv
FROM events
WHERE event = '\$AppStart'
  AND \$model NOT LIKE 'SRC%'
  AND date >= 'YYYY-MM-DD' AND date <= 'YYYY-MM-DD'
GROUP BY device_type, orientation
ORDER BY device_type, orientation
```

⚠️ **不要信任 SRC 遥控器的 `$screen_orientation`**，它固定横屏但 SDK 大量误报 `portrait`，必须单独排除。

---

## 8. 登录方式占比 + 成功率分析

```sql
-- 按验证方式统计 PV/UV
SELECT auth_method, count(*) as pv, count(distinct distinct_id) as uv
FROM events
WHERE event='user_login' AND date >= 'FROM' AND date <= 'TO'
GROUP BY auth_method ORDER BY uv DESC

-- 登录成功率（按验证方式）
SELECT auth_method, if_success_login, count(*) as pv
FROM events
WHERE event='user_login' AND date >= 'FROM' AND date <= 'TO'
GROUP BY auth_method, if_success_login ORDER BY auth_method

-- 登录失败错误码排名
SELECT fail_reason, fail_text, count(*) as pv, count(distinct distinct_id) as uv
FROM events
WHERE event='user_login' AND date >= 'FROM' AND date <= 'TO' AND if_success_login = 0
GROUP BY fail_reason, fail_text ORDER BY pv DESC LIMIT 20

-- 失败环节分布
SELECT fail_phase, count(*) as pv
FROM events
WHERE event='user_login' AND date >= 'FROM' AND date <= 'TO' AND if_success_login = 0
GROUP BY fail_phase ORDER BY pv DESC
```

**已知错误码**（2026-06 实测）：
| 错误码 | 含义 | 备注 |
|--------|------|------|
| 1101 | 账号或密码错误 | 占失败总量 ~62%，新旧文案多语言共存 |
| 9999 | 网络/未知错误 | ~30%，多语言文案（中/英/葡/泰/韩/越南语） |
| 1302 | 验证码错误 | ~8% |
| 1107 | 密码错误过多已锁定 | ~1%，高风险流失点 |
| 1132 | 密码错误（另一种） | 可能是新接口返回码 |
| 1003 | 请求方式错误 | 建议重启 App |
| 404 | HTTP 404 接口异常 | 极少但严重 |

⚠️ **同一错误码有多套 fail_text**（中文新格式/旧格式/英文），分析时按 `fail_reason` 聚合，不要按 `fail_text`。

---

## 9. 国内/海外拆分（定位模式、基准源等）

```sql
-- 通用模板：任意属性 × 国内/海外
SELECT some_field,
       sum(case when $country = '中国' or $country = 'China' or $country is null then 1 else 0 end) as domestic,
       sum(case when $country != '中国' and $country != 'China' and $country is not null then 1 else 0 end) as overseas,
       count(*) as total
FROM events
WHERE event='EVENT_NAME' AND date >= 'FROM' AND date <= 'TO'
GROUP BY some_field ORDER BY total DESC
```

⚠️ `$country` 存储为**中文**（'中国'、'土耳其'、'美国'），NULL 通常是国内用户。

---

## 10. 定位模式/基准源分析（测地事件）

```sql
-- 定位模式（position_mode）— 必须归一化！详见 pitfall #15
SELECT position_mode, count(*) as pv, count(distinct distinct_id) as uv
FROM events
WHERE event='survey_use_mapping_device' AND date >= 'FROM' AND date <= 'TO'
GROUP BY position_mode ORDER BY pv DESC

-- 定位基准源
SELECT positioning_reference, count(*) as pv, count(distinct distinct_id) as uv
FROM events
WHERE event='survey_use_mapping_device' AND date >= 'FROM' AND date <= 'TO'
GROUP BY positioning_reference ORDER BY pv DESC
```

**position_mode 多语言归一化 SQL**（CASE WHEN 聚合）：
```sql
SELECT
  CASE
    WHEN position_mode IN ('RTK','GNSS') THEN 'RTK/GNSS高精度'
    WHEN position_mode IN ('正常','Active','Ativo','Activo','Normal','Aktif',
         'Активно','Активен','정상','Kích hoạt','普通','نورمال','ปกติ','Neconectat') THEN '正常(已定位)'
    WHEN position_mode IN ('定位中','Localizando ','Locating','Localización','測位中','Konumlandırma') THEN '定位中'
    WHEN position_mode IN ('未连接','Desconectado','Disconnected','Отключено',
         'Bağlantısı kesildi','연결되지 않음','Đã ngắt kết nối','Не е свързан') THEN '未连接'
    ELSE '其他/空'
  END as mode_group, ...
```

---

## 11. 查单个用户最近有没有登录/启动 App（给定 32 位 HEX ID）

**典型场景**: 业务/客服/产品丢一个 32 位大写 HEX（如 `D74B8CE70961B4ADDAC9635079442350`）问"这个用户最近几天有没有登录或启动 App？"

```sql
-- Step 1：宽窗口（180天）查活跃情况，同时匹配 distinct_id 和 $identity_login_id
SELECT max(date) AS last_date,
       min(date) AS first_date,
       count(*)   AS total_events,
       count(distinct date) AS active_days
FROM events
WHERE (distinct_id = '{ID}' OR "$identity_login_id" = '{ID}')
  AND date >= date_sub(current_date(), 180);

-- Step 2：拉最后活跃附近的明细（启动/登录事件）
SELECT date, time, event, $app_version, $os, $model, $province, $city
FROM events
WHERE (distinct_id = '{ID}' OR "$identity_login_id" = '{ID}')
  AND date >= '{last_date}'
ORDER BY time DESC
LIMIT 100;
```

**回复口径**:
- 近 N 天有活跃 → 列出最后启动/登录时间、版本、设备、地区；
- **近 7 天 0 结果 ≠ 用户不存在**，先用 180 天宽窗口确认历史上是否存在；
- 历史有数据但最近 30+ 天无活跃 → 明确说"最后活跃 YYYY-MM-DD，距今 N 天，最近几天无登录/启动记录"，不要误判为"没有这个用户"。

**ID 字段识别**（本项目 production）：
| 字段 | 格式 | 用途 |
|---|---|---|
| `distinct_id` | 32 位大写 HEX（如 `32D7D85CC3C1D65E9C6602724FF9997E`） | 神策主标识，匿名阶段=设备ID，登录后切到 login_id |
| `$identity_login_id` | 32 位大写 HEX | 登录后 ID，登录用户与 distinct_id 相同 |
| `$device_id` / `$identity_anonymous_id` | 短小写（如 `fa44c7f251568a8b`，14-16 位） | 匿名设备短 ID，不是 32 位大写 |
| `user_id` | 业务长整型（负数如 `-7.3e+18`） | 业务后端 user_id，不适合直接给用户查 |

⚠️ **不要在 users 表用多个 OR 条件**（`id='X' OR user_id='X' OR $device_id='X'`），会触发 `COMMON-R-131-1 GRPC 服务发生未知异常`。查"是否存在 + 最近行为"一律走 events 表。

---

## 12. 跨事件错误码排行（报错次数 / 设备数 / 用户数 / 提示文案）

**典型场景**: 产品/运营要"各埋点事件里排行前 N 的错误码，以及报错次数、涉及设备数、涉及用户数"。

**含 `fail_reason` 字段的 10 个事件**（2026-06 实测）：
| 事件 | 说明 |
|------|------|
| `device_add_check` | 添加设备-获取设备信息 |
| `device_add_confirm` | 添加设备-确定添加设备 |
| `device_firmware_update` | 固件更新操作 |
| `user_login` | 用户登录 |
| `user_register` | 用户注册 |
| `user_sms_send` | 发送短信验证码 |
| `survey_save_feilds` | 测地-测地流程操作 |
| `survey_use_mapping_device` | 测地/地块管理-选择/切换测绘设备（fail_reason 通常为空） |
| `operation_lift_mode` | 运输作业-执行自动飞行（错误码为十进制数字，非 hex 格式） |
| `auto_operation_task_start` | 自主作业任务启动 |

### 全局 Top 20（跨所有事件）

```sql
SELECT event, COALESCE(fail_reason, '(空)') as fr, count(*) as ec, count(distinct distinct_id) as uc
FROM events
WHERE event IN ('device_add_check','device_add_confirm','device_firmware_update',
  'user_login','user_register','user_sms_send','survey_save_feilds',
  'survey_use_mapping_device','operation_lift_mode','auto_operation_task_start')
  AND date >= 'FROM' AND date <= 'TO'
GROUP BY event, fr
ORDER BY ec DESC
LIMIT 1000
```

然后 Python 里取全局 Top 20。device_count 需单独查（`$device_id` 不加引号，见 Pitfall 37）。

### 按事件分组 Top 20（三查询合并模式）

每个事件执行三条 SQL，Python 合并取 Top 20（详见 Pitfall 38）：

```python
# 查询1：报错次数 + 用户数
q1 = f"""SELECT COALESCE(fail_reason, '(空)') as fr,
         count(*) as ec, count(distinct distinct_id) as uc
         FROM events WHERE event = '{ev}' AND date >= '{from}' AND date <= '{to}'
         GROUP BY fr LIMIT 2000"""

# 查询2：设备数
q2 = f"""SELECT COALESCE(fail_reason, '(空)') as fr,
         count(distinct $device_id) as dc
         FROM events WHERE event = '{ev}' AND date >= '{from}' AND date <= '{to}'
         GROUP BY fr"""

# 查询3：提示文案（取每个 fr 下 count 最大的 fail_text）
q3 = f"""SELECT COALESCE(fail_reason, '(空)') as fr,
         COALESCE(fail_text, '(空)') as ft, count(*) as tc
         FROM events WHERE event = '{ev}' AND date >= '{from}' AND date <= '{to}'
         GROUP BY fr, ft"""
```

**合并逻辑**：
1. q1 结果按 `ec` 降序取前 20 行 → 主表
2. q2 按 `fr` join 到主表 → 补 `dc`（设备数）
3. q3 按 `fr` 分组，取 `tc` 最大的 `ft` → 补文案列

**注意事项**：
- `(空)` 表示 `fail_reason` 为 NULL 的记录（可能是成功操作未上报错误码，也可能是上报缺失），占比可能很高（如 `auto_operation_task_start` 的 `(空)` 占 95%+）
- `fail_text` 是多语言文案（中/英/土/韩/越南/葡萄牙语等），取频次最高的一条即可代表
- `operation_lift_mode` 的错误码是十进制数字（如 `1326198`），不是 hex 格式，需单独 `hex()` 转换后查 API
- `0` 和 `1` 在多个事件中出现量很大，含义可能是成功/占位码，需业务确认
