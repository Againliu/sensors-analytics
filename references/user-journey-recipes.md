# 单用户行为查询配方（user journey）

## 触发场景
运营/客服/产品给出一个 distinct_id（32位大写HEX，神策匿名ID）或 user_id，问：
- 这个用户最近登录/启动/作业了吗？
- 这个用户卡在哪一步？
- 这个用户是不是流失了？
- 这个用户有什么典型操作路径？

## 快速查询（3步，不用自己写SQL）

```bash
cd ~/.hermes/skills/sensors-analytics/scripts

# 1. 中文摘要（默认90天）
python3 user_summary.py D74B8CE70961B4ADDAC9635079442350
python3 user_summary.py D74B8CE70961B4ADDAC9635079442350 30   # 查最近30天

# 2. 拿完整JSON（含 timeline 明细）
python3 user_journey.py D74B8CE70961B4ADDAC9635079442350 90 > /tmp/u.json
```

脚本输出包括：
- 设备矩阵（每个 model/os/app_version 组合的出现时段）
- 事件类型汇总、按天统计
- 关键行为计数（注册/登录/绑机/升级/测地/作业/客服/重登/相机）
- 自动按 30分钟 idle 切分 session，给出阶段摘要
- timeline 明细（time/event/screen/province/city）
- 用户分层判断（故障态/流失风险/真实作业用户等）

## distinct_id 识别
- 神策默认 distinct_id 是设备级匿名ID，**32位大写HEX**（例：`D74B8CE70961B4ADDAC9635079442350`）
- 用户登录后会有 $ProfileMergeEvent 把匿名ID和 login_id 融合
- **一个人可能有多条 distinct_id**：手机、遥控器、第二台手机各自有匿名ID，但
  `$identity_login_id` / `user_id` 相同。要查"这个用户全部行为"需要按 user_id 或 $identity_login_id 查
- 本 skill 目前的 user_journey.py 只按单个 distinct_id 查；跨设备全行为需要自己写 SQL
  用 `WHERE $identity_login_id = 'XXX'` 或 `WHERE user_id IN (...)`

## 关键事件语义表

| 事件 | 含义 | 关键属性 |
|---|---|---|
| `$SignUp` | 注册（也可能是多设备登录触发） | 通常每个设备首次出现1次 |
| `$AppInstall` | 安装后首次启动 | 每个首次启动 |
| `$AppStart` / `$AppEnd` | App 进前台/退后台 | screen_name 是当前 Activity |
| `user_login` | 登录成功 | 触发频次异常高 → 反复掉线重登 |
| `user_sms_send` | 发送短信验证码 | 每次登录前触发 |
| `device_add_check` | 添加设备-获取设备信息 | 点"添加设备"后向无人机发探测；次数多 = 连接不稳 |
| `device_add_confirm` | 添加设备-确定添加 | **真正绑定成功**，这是绑机成功标志 |
| `device_firmware_update` | 固件升级进度上报 | 升级期间约1秒1条；多条 = 在升级中；只有几条但间隔久 = 升级失败重试 |
| `survey_use_mapping_device` | 测地-选择/切换测绘设备 | 进入测地流程 |
| `survey_save_feilds` | 测地-保存地块操作 | 点保存；可能多次（保存多个地块） |
| `survey_feild_info` / `survey_field_info` | 地块信息上报/地块创建成功 | **真正建好了地块** |
| `auto_operation_task_start` | 自主作业任务启动 | **开始飞行作业** |
| `operation_auto_work_start` | operation_auto_work_start | 作业启动相关 |
| `operation_lift_mode` | 运输作业-自动飞行 | 运输作业模式启动 |

## 关键 screen 语义（通过 $screen_name 最后一段识别）

> **重要**：`$screen_name` 是神策 SDK 全埋点预置属性，不只出现在 `$AppStart`/`$AppEnd` 事件里，
> `$AppClick` 事件也有此属性。对于 iOS 用户，`$AppClick` 的 `$screen_name` 是还原页面浏览路径的主要来源
> （iOS 的 `$AppStart`/`$AppEnd` 数据可能不如 Android 全）。
>
> **Android 端**：值为完整 Activity 类名（如 `com.xag.agri.v4.home.core.HomeActivity`），截最后一段。
> **iOS 端**：值为 ViewController 类名，前缀通常为 `SuperX4.`（如 `SuperX4.XAGUpgradeFirmwareController`），截最后一段。

### Android 端 $screen_name 映射

| 关键词 | Activity | 含义 |
|---|---|---|
| `HomeActivity` | 首页 | 正常停留 |
| `UavDetailsActivity` / `SRC4DetailActivity` | 设备详情 | 在看设备状态 |
| `DeviceMeshActivity` | 设备组网 | 设备连接/配网环节，停留久 = 连不上 |
| `AddSRC4DeviceConfirmActivity` | 添加遥控器确认 | 正在加遥控器 |
| `DeviceUpgradeMainActivity` / `AppUpdateActivity` / `SRC4AppUpdateActivity` | 固件/App升级页 | 停留久 / 反复进出 = 升级不顺 |
| `ReLoginActivity` | 重新登录 | **升级后被踢下线**，需要重新登录；次数多 = 登录态异常 |
| `ChatActivity` / `customservice` | 在线客服页 | 进客服咨询；进进出出次数多 = 严重问题求助中 |
| `TCameraActivity` / `albumcamerarecorder` | 相机/相册 | 给客服发截图/拍照反馈 |

### iOS 端 $screen_name 映射（前缀 SuperX4.）

| 关键词 | ViewController | 含义 |
|---|---|---|
| `XAGUserMainController` | 个人中心/首页 | 正常停留 |
| `XAGUpgradeFirmwareController` | 固件升级页 | 停留久 / 反复进出 = 升级不顺 |
| `X4DeviceStatusController` | 设备状态页 | 在看设备状态 |
| `X4AlartController` | 弹窗/提示 | 出现弹窗（可能是错误提示） |
| `X4DeviceListController` | 设备列表 | 浏览/管理设备 |
| `X4FieldMainViewController` | 作业首页 | 进入作业模块 |
| `X4VerificationCodeLoginViewController` | 验证码登录 | 登录环节 |
| `X4FirwareDetailController` | 固件详情 | 查看固件版本信息 |
| `X4MyWorkLogController` | 工作日志 | 查看作业记录 |
| `X4Debug1Controller` / `X4UserDebugViewController` | 调试页 | **进入调试模式**，普通用户不该频繁进 |
| `X4SettingController` | 设置 | 修改配置 |
| `X4DeviceBasicInfoViewController` | 设备基本信息 | 查看设备参数 |
| `XAGSelectTeamController` | 选择团队 | 团队切换 |
| `X4AutoReturnBattreySetController` | 自动返航设置 | 调整返航参数 |
| `X4PasswordLoginViewController` | 密码登录 | 密码方式登录 |

### 用 $AppClick 的 $screen_name 还原 iOS 用户路径（SQL）

```sql
-- 统计 iOS 用户在哪些页面点击操作最多
SELECT "$screen_name", count(*) as clicks
FROM events
WHERE event = '$AppClick'
  AND distinct_id = 'XXX'
  AND date >= '2026-06-01'
GROUP BY "$screen_name"
ORDER BY clicks DESC
LIMIT 30;
```

## 用户分层判断规则（脚本已内置自动判断）

**故障态典型信号**：
- $AppStart ≥ 20 次但 0 次作业事件
- ReLoginActivity 多次出现（≥3）
- device_add_check 远多于 device_add_confirm（反复尝试绑但不成功）
- ChatActivity 进进出出 ≥ 5 次
- 固件升级页反复进出
- 打开相机（通常是给客服发图）

**作业用户信号**：
- 有 `auto_operation_task_start` 或 `operation_lift_mode` 事件
- survey_* 事件之后出现作业启动事件（正常路径）

**流失用户信号**：
- 最后活跃距今 ≥ 14 天
- 最后活跃停留在"绑机"或"客服"环节（说明问题没解决就走了）
- 典型模式：注册 → 绑机 → 升级失败/找客服 → 消失

**新用户路径健康度**：
正常路径应当是：注册 → 登录 → 绑机(device_add_confirm) → 固件升级(1段连续) → 测地 → 作业启动
任何环节反复/长时间停留/反复进出/进客服 = 断点。

## 典型用户画像案例

### 案例1（沉默流失）：只绑机不作业，5/21后消失
```
事件：$AppStart 30, $AppClick 243, device_firmware_update 42, device_add_check 5, device_add_confirm 2
时间：4/27 注册 → 4/28 短暂回访 → 5/21 集中活跃（绑机+升级）→ 之后34天无事件
作业：0 次
结论：绑完机升完级就流失了，没走到测地和作业
```

### 案例2（故障态活跃中）：反复绑机+找客服，卡在上游
```
设备：手机(HarmonyOS) + SRC5遥控器 + 第二台手机，3台设备
时间：6/23 注册 → 6/24 仍活跃（距最后事件4小时）
事件：$AppStart 78, device_add_check 39, device_add_confirm 8, firmware_update 9,
      survey_* 11（测地3块地成功）, customer_service ~25次, camera 打开1次
作业：0 次
结论：地块建了但没能启动作业，SRC5连接/固件问题，深夜密集找客服，仍在活跃但卡在上游
```

## 直接写 SQL 查用户（脚本不满足时）

```sql
-- 某 distinct_id 按天按事件统计
SELECT date, event, count(*) as cnt
FROM events
WHERE distinct_id = 'D74B8CE70961B4ADDAC9635079442350'
  AND date >= '2026-06-01'
GROUP BY date, event
ORDER BY date, event;

-- 按 login_id 查全设备行为
SELECT distinct_id, $model, event, count(*) as cnt
FROM events
WHERE $identity_login_id = '<login_id>'
  AND date >= '2026-06-01'
GROUP BY distinct_id, $model, event;

-- 某用户最近的所有作业事件
SELECT date, time, event, $app_version, $model, $province, $city
FROM events
WHERE distinct_id = 'XXX'
  AND event IN ('auto_operation_task_start','operation_auto_work_start','operation_lift_mode')
ORDER BY time DESC
LIMIT 50;
```

## Pitfalls

1. **$screen_name 是完整类名**，显示时要 `.split('.')[-1]` 截最后一段才是 Activity 名
2. **device_firmware_update 高频是正常的**（升级时1秒1条进度上报），不能当"多次升级"，要按时间聚类看
3. **$SignUp 在同一账号多设备登录时会多次出现**，不等于"注册了多个账号"
4. **user_login 次数 ≠ 用户主动登录次数**，重连、token过期、App重启都可能触发
5. **App版本号不带 V 前缀**（存的是 `7.5.1` 不是 `V7.5.1`）
6. **SRC 遥控器天然横屏**，不要把它的 $screen_orientation 算进横竖屏分析
7. **SQL 多行结果是 NDJSON**（每行一个JSON对象），不能直接 `r.json()`，要用 sql_query() helper 或 NDJSON 解析
8. **count(*) 返回 float**，神策 SQL 接口所有计数都是 float，显示时要 int()
9. **一个自然人 ≠ 一个 distinct_id**，多设备用户会有多个匿名ID，需用 user_id/$identity_login_id 串起来
10. **推断性结论 ≠ 事实**：如"打开了相机"是事实（有 $screen_name=TCameraActivity 记录），但"给客服发图"是推断——不要把推断当事实陈述。次数表述必须与原始数据行数一致，不要四舍五入或泛化（如实际1次进 DeviceMeshActivity 不能说"多次进"）。
11. **$AppClick 的 $screen_name 在 iOS 端尤其重要**：iOS 的 $AppStart/$AppEnd 数据可能不如 Android 全，$AppClick 的 $screen_name 是还原 iOS 用户页面浏览路径的主要来源。
12. **to_time() 函数不可用**（Impala 报 `to_time() unknown for database`），日期过滤用 `date` 字段，时间排序用 `ORDER BY time`，提取小时用 `HOUR(time)`。
