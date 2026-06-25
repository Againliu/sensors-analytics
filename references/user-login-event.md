# user_login 事件字段与值域速查

> 用于 App 登录分析。查询前先读此文件，不要猜字段值。

## 核心业务字段

| 字段名 | 显示名 | 值域（已知） | 说明 |
|--------|--------|-------------|------|
| `auth_method` | 验证方式 | `密码` / `短信` / `未知` | "未知"多为第三方登录或自动登录未标记场景 |
| `login_entry` | 登录界面类型 | `登录失效界面` / `默认登录界面` | 失效界面 = token 过期等被动触发 |
| `if_success_login` | 是否登录成功 | `0`（失败）/ `1`（成功） | NUMBER 类型，SQL 用 `= 0` 过滤 |
| `fail_reason` | 失败原因错误码 | 见下方错误码表 | 字符串，同码可能有多套文案 |
| `fail_text` | 失败原因文案 | 多语言文案（中/英/葡/泰/韩/越） | 同错误码新旧文案并存 |
| `fail_phase` | 失败环节 | `账号密码校验` / `验证码校验` / `发送验证码` | |
| `sms_code_request_count` | 发送短信验证码次数 | NUMBER | |
| `login_total_duration` | 登录总耗时 | NUMBER | |
| `phone_country_code` | 手机区号 | STRING | 海外用户分析可用 |

## 错误码速查表（2026-06 实测数据）

| 错误码 | 含义 | 占比(失败PV) | 备注 |
|--------|------|-------------|------|
| **1101** | 账号或密码错误 | ~62% | 最高频，多套文案并存 |
| **9999** | 网络/未知错误 | ~30% | 含多语言文案 |
| **1302** | 验证码错误 | ~8% | |
| **1107** | 密码错误过多已锁定 | ~1% | 潜在流失点 |
| **1132** | 密码错误（另一种） | <1% | 与 1101 类似但码不同 |
| **1003** | 请求方式错误 | <1% | |
| **404** | HTTP 404 接口异常 | <1% | passport.xag.cn 接口 |

## 常用分析查询

### 登录方式占比
```sql
SELECT auth_method, count(*) as pv, count(distinct distinct_id) as uv
FROM events WHERE event='user_login' AND date >= '{from}' AND date <= '{to}'
GROUP BY auth_method ORDER BY uv DESC
```

### 登录成功率
```sql
SELECT auth_method, if_success_login, count(*) as pv
FROM events WHERE event='user_login' AND date >= '{from}' AND date <= '{to}'
GROUP BY auth_method, if_success_login ORDER BY auth_method, if_success_login
```

### 失败错误码排名
```sql
SELECT fail_reason, fail_text, count(*) as pv, count(distinct distinct_id) as uv
FROM events WHERE event='user_login' AND date >= '{from}' AND date <= '{to}'
AND if_success_login = 0
GROUP BY fail_reason, fail_text ORDER BY pv DESC LIMIT 20
```

### 失败环节分布
```sql
SELECT fail_phase, count(*) as pv
FROM events WHERE event='user_login' AND date >= '{from}' AND date <= '{to}'
AND if_success_login = 0
GROUP BY fail_phase ORDER BY pv DESC
```

## 注意事项

- `auth_method` 的 "未知" 值占比约 20%，不代表数据缺失，是业务未标记场景
- 同错误码（如 1101）在不同版本/语言下有不同 fail_text，做 GROUP BY 时要合并同码
- `if_success_login` 是 NUMBER 类型，SQL 中用 `= 0` 而非 `= 'false'`
- 登录失效界面的登录次数远多于默认界面（约 2:1），说明续登是主要场景
