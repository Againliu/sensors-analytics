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
