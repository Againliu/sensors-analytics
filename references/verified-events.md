# 神策已验证事件与字段（2026-06-03 实测更新）

> 来源：`POST /api/v3/horizon/v1/schema/event/list` body `{}`
> Project: `production` (id=2)
> 总计: 24 个事件

## 全量事件列表

| # | event_name | display_name |
|---|---|---|
| 1 | `$AppClick` | App 元素点击 |
| 2 | `$AppStartPassively` | App 被动启动 |
| 3 | `$AppEnd` | App 退出 |
| 4 | `$AppPageLeave` | App 页面离开 |
| 5 | `$AppInstall` | App 安装后首次启动 |
| 6 | `$AppPushClick` | App 推送点击 |
| 7 | `$ProfileMergeEvent` | 用户身份融合 |
| 8 | `user_login` | 用户登录 |
| 9 | `user_register` | 用户注册 |
| 10 | `user_sms_send` | 发送短信验证码 |
| 11 | `device_add_confirm` | 添加设备-确定添加设备 |
| 12 | `device_add_check` | 添加设备-获取设备信息 |
| 13 | `device_firmware_update` | 固件更新操作 |
| 14 | `survey_feild_info` | 测地-成功创建地块 |
| 15 | `survey_save_feilds` | 测地-测地流程操作 |
| 16 | `survey_field_info` | survey_field_info |
| 17 | `survey_use_mapping_device` | 测地/地块管理-选择/切换测绘设备 |
| 18 | `operation_lift_mode` | 运输作业-执行自动飞行 |
| 19 | `auto_operation_task_start` | 自主作业任务启动 |
| 20 | `operation_auto_work_start` | operation_auto_work_start |

---

## user_login 关键字段

| 字段名 | 显示名 | 类型 | 已知值 |
|--------|--------|------|--------|
| `auth_method` | 验证方式 | STRING | 密码 / 短信 / 未知（第三方/自动登录） |
| `if_success_login` | 是否登录成功 | NUMBER | 1.0=成功, 0.0=失败 |
| `fail_reason` | 失败原因错误码 | STRING | 1101/9999/1302/1107/1003/1132/404 |
| `fail_text` | 失败原因文案 | STRING | ⚠️ 多语言+新旧格式共存，按 fail_reason 数值分组 |
| `fail_phase` | 失败环节 | STRING | 账号密码校验 / 验证码校验 / 发送验证码 |
| `login_entry` | 登录界面类型 | STRING | 登录失效界面 / 默认登录界面 |
| `sms_code_request_count` | 发送短信验证码次数 | NUMBER | |
| `login_total_duration` | login_total_duration | NUMBER | |
| `phone_country_code` | 手机区号 | STRING | |

### 登录错误码 Top 排名（近30天, 2026-05-04~06-03）

| 错误码 | 含义 | 总次数 | 占比 |
|-------|------|-------|------|
| 1101 | 账号/密码错误 | ~49,500 | 61.9% |
| 9999 | 网络/未知错误 | ~24,200 | 30.3% |
| 1302 | 验证码错误 | ~6,700 | 8.4% |
| 1107 | 密码错误过多锁定 | 820 | 1.0% |
| 1003 | 请求方式错误 | 485 | 0.6% |
| 1132 | 密码错误（另一种） | 306 | 0.4% |
| 404 | HTTP 404（接口异常） | 352 | 0.4% |

---

## auto_operation_task_start 关键字段

| 字段名 | 显示名 | 类型 | 已知值 |
|--------|--------|------|--------|
| `actuator_model` | 执行类型 | STRING | 喷洒 / 播撒 / 空飞 / 无挂载 |
| `route_type` | 航线类型 | STRING | 往返航线 / 标准往返航线 / 自由航线 / 定点航线 |
| `position_mode` | 定位模式 | STRING | ⚠️ **用技术枚举**: RTK / VRTK / GNSS / PPP / 未知 |
| `positioning_reference` | 定位基准源 | STRING | 网络RTK / 云基站 / 移动基站 / CORS / cors（小写变体） |
| `operation_position` | 开始作业位置 | STRING | 地面 / 空中 |
| `out_in_route_type` | 进出航线模式 | STRING | 安全点模式 / 安全区模式 |
| `if_empty_operation` | 是否开启空飞作业 | NUMBER | 0.0 / 1.0 |
| `if_resume_operation` | 是否恢复作业 | NUMBER | 0.0 / 1.0 |
| `bound_type_spray` | 扫边喷洒方式 | STRING | 外侧喷洒 / 双边喷洒 / 关闭喷洒 / 空 |
| `bound_type_spread` | 扫边播撒方式 | STRING | 双边播撒 / 外侧播撒 / 关闭播撒 / 空 |
| `feed_spray` | 换行段喷洒 | STRING | |
| `device_model` | 设备型号 | STRING | UAV40/UAV43/UAV35/UAV47/UAV46/UAV39/UAV23/UAV34/UAV27/UAV38/UAV17 |
| `drone_model` | drone_model | STRING | |
| `controller_model` | 遥控器型号 | STRING | |
| `xrtk_model` | XRTK型号 | STRING | |
| `if_use_xrtk` | 是否使用 XRTK | | |
| `xrtk_sn` | XRTK SN | STRING | |
| `screw_feeder_model` | 绞龙型号 | STRING | |
| `work_speed` | 作业飞行速度 | NUMBER | |
| `work_height` | 作业飞行高度 | NUMBER | |
| `spray_volume` | 喷洒量 | NUMBER | |
| `estimate_spray_volume` | 预估喷洒用量 | NUMBER | |
| `estimate_work_area` | 预估作业面积 | NUMBER | |
| `route_3d_type` | 三维航线版本 | STRING | |
| `last_operation_time` | 上次作业时间 | STRING | |
| `work_field_id` | 作业地块 ID | STRING | |
| `work_field_guid` | 作业地块 GUID | STRING | |
| `auto_task_id` | 任务 ID | STRING | |

---

## survey_save_feilds / survey_use_mapping_device 关键字段

| 字段名 | 显示名 | 类型 | 已知值 |
|--------|--------|------|--------|
| `position_mode` | 定位模式 | STRING | ⚠️ **多语言 UI 文本**: 正常/定位中/未连接/RTK/GNSS + 各语言翻译 |
| `positioning_reference` | 定位基准源 | STRING | 网络RTK / 云基站 / CORS / 移动基站 / 空 |
| `survey_mode` | 测地模式 | STRING | |
| `survey_mark_point_mode` | 测地打点模式 | STRING | |
| `device_sn` | 设备序列号 | STRING | |
| `device_model` | 设备型号 | STRING | |
| `all_device_information` | 所有设备序列号 | STRING | |
| `survey_feilds_area` | 每个地块边界面积 | STRING | |
| `survey_feilds_number` | 地块边界数量 | NUMBER | |
| `survey_feilds_point_number` | 每个地块的地块边界点数量 | STRING | |
| `survey_point_marker_number` | 测地标记点数量 | NUMBER | |
| `survey_line_marker_number` | 测地标记线数量 | NUMBER | |
| `survey_non_spray_number` | 测地禁喷区数量 | NUMBER | |
| `survey_polygonal_obstacle_number` | 测地多边形障碍物数量 | NUMBER | |
| `survey_circular_obstacle_number` | 测地圆形障碍物数量 | NUMBER | |
| `survey_operation_point_number` | 测地作业点数量 | NUMBER | |

---

## operation_lift_mode 关键字段

| 字段名 | 显示名 | 类型 | 已知值 |
|--------|--------|------|--------|
| `lift_mode` | 运输模式 | STRING | 录制往返模式 / 目标点运输模式 / 直线往返模式 |
| `position_mode` | 定位模式 | STRING | 同 survey 事件，多语言枚举 |
| `actuator_model` | 执行类型 | STRING | |
| `work_speed` | 作业飞行速度 | NUMBER | |
| `device_model` | 设备型号 | STRING | |
| `controller_model` | 遥控器型号 | STRING | |
| `xrtk_model` | XRTK型号 | STRING | |

---

## 通用定位字段（所有事件可用）

| 字段名 | 显示名 | 说明 |
|--------|--------|------|
| `$country` | 国家 | 中文存储：'中国'、'土耳其'、'美国' 等 |
| `$province` | 省份 | |
| `$city` | 城市 | |
| `system_language` | 系统语言 | survey 事件有此字段 |
| `$model` | 手机型号 | |
| `$device_id` | 设备 ID | |
| `$app_version` | App 版本 | 格式不带 V 前缀: '7.5.1' 不是 'V7.5.1' |

---

## 国内/海外分析 SQL 模式

```sql
CASE
  WHEN $country = '中国' OR $country = 'China' OR $country IS NULL THEN '国内'
  ELSE '海外'
END as region
```

- `$country IS NULL` 归入国内 — 国内老用户/早期版本可能未上报国家字段
- `$country` 存中文（'中国' 不是 'CN'）
- 海外 Top 国家：土耳其、美国、泰国、巴西、印尼、越南、保加利亚、韩国

---

## ⚠️ position_mode 字段在不同事件中使用不同枚举！

| 事件类型 | position_mode 值 | 说明 |
|---------|-----------------|------|
| **survey 事件**（测地/测绘） | 正常/定位中/未连接/RTK/GNSS + 多语言翻译 | UI 显示文本，需 CASE WHEN 归一化 |
| **auto_operation_task_start**（自主作业） | RTK/VRTK/GNSS/PPP/未知 | 技术枚举，直接可用 |
