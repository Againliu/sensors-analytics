# 神策 OpenAPI 速查（OpenAPI Quick Reference）

> 浓缩参考：从 `manual.sensorsdata.cn/sa/` 官方文档 + `manual.sensorsdata.cn/openapi` 完整端点手册抓出的核心信息。
> 完整端点列表需登录 `https://manual.sensorsdata.cn/openapi` 在线查（神策未提供离线 PDF/JSON）。

---

## 1. URL 速查表

| 用途 | URL |
|---|---|
| 神策 UI（生产）| `https://user-insight.xa.com/` |
| 神策 API（生产）| `https://user-insight.xa.com:443/api/v3/...` |
| 神策 API（文档示例）| `http://{host}:8107/api/v3/...`（**本地部署**，极飞内网用域名）|
| OpenAPI 概述 | `https://manual.sensorsdata.cn/sa/docs/about_open_api/v0300` |
| OpenAPI 认证 | `https://manual.sensorsdata.cn/sa/docs/open_api_authentication/v0300` |
| OpenAPI 手册（外站）| `https://manual.sensorsdata.cn/openapi` ← 完整端点列表在这 |
| 导数 | `https://manual.sensorsdata.cn/sa/docs/input_output_data/v0300` |
| 数据导出 | `https://manual.sensorsdata.cn/sa/docs/export_data/v0300` |
| 常见问题 | `https://manual.sensorsdata.cn/sa/docs/question/v0300` |

---

## 2. 认证 header（必须两个同时传）

```bash
-H "api-key: #K-XXXXX...35字符" \
-H "sensorsdata-project: production"
```

- `api-key`：从 `~/.hermes/credentials/sensors.txt` 读，35 字符，`#K-` 前缀
- `sensorsdata-project`：项目名，极飞常见是 `production` 或 `default`
- 权限 = 创建 key 的用户权限（**不是** key 自己的 ACL）

---

## 3. URL 结构

```
http(s)://{domain}{Base URL}{API URL}
```

- `domain` = `user-insight.xa.com`（极飞部署）
- `Base URL` 选项：
  - `/api/v3/portal/v2` — 主门户（事件/属性/查询/管理）
  - `/api/v3/analytics/v1` — 分析模块（project/list 等）
  - `/api/v3/export/v1` — 异步导出
- `v3` = API 大版本（不变），`v2/v1` = 接口版本（产品升级会变）
- **无路径参数**，所有参数在 query 或 body；复杂结构体放 body

---

## 4. 已知端点（部分，需补全）

| 类别 | 端点（Path）| 说明 |
|---|---|---|
| 元数据 | `/api/v3/portal/v2/management/event/list` | 列事件 |
| 元数据 | `/api/v3/portal/v2/management/event/detail` | 事件详情（带属性）|
| 元数据 | `/api/v3/portal/v2/management/property/list` | 属性列表 |
| 元数据 | `/api/v3/portal/v2/management/behavior/list` | 行为列表（占位测试）|
| 查询 | `/api/v3/portal/v2/query/data` | SQL-like 查询 |
| 异步导数 | `/api/v3/export/v1/data/export/task` | 创建导出任务 |
| 异步导数 | `/api/v3/export/v1/data/export/task/status` | 查任务状态 |
| 测试 | `/api/v3/analytics/v1/project/list` | 项目列表（文档示例）|

> 完整端点需到 `https://manual.sensorsdata.cn/openapi` 在线查。

---

## 5. curl 模板

### 5.1 列事件（GET）
```bash
curl -sX GET "https://user-insight.xa.com:443/api/v3/portal/v2/management/event/list" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "api-key: $(cat ~/.hermes/credentials/sensors.txt)" \
  -H "sensorsdata-project: production"
```

### 5.2 查 SQL 数据（POST）
```bash
curl -sX POST "https://user-insight.xa.com:443/api/v3/portal/v2/query/data" \
  -H "Content-Type: application/json" \
  -H "api-key: $(cat ~/.hermes/credentials/sensors.txt)" \
  -H "sensorsdata-project: production" \
  -d '{"project":"production","sql":"SELECT event, count(*) FROM events GROUP BY event LIMIT 10"}'
```

### 5.3 管理员 key 切换身份
```bash
curl ... \
  -H "api-key: #K-XXX" \
  -H "account-id: target-user-id"  # 必须是管理员 key
```

---

## 6. 错误码对照

| HTTP | error_type | 含义 | 处置 |
|---|---|---|---|
| 200 | — | 成功 | — |
| 401 | `UNAUTHORIZED` | key 无权限 / 项目看不到 | 看 `__PRESET_DATA.authConfig.license` 是否 `project_num >= max_project_num` |
| 4xx | `BAD_REQUEST` | 项目不存在 / 参数错 | 换 project 名 / 检查 body |
| 302 | — | 网关跳登录（访问根）| 正常 — 端点返回 JSON |
| 401 | — | 网关层未鉴权 | 检查 HTTPS + api-key header |

---

## 7. License 状态探测（根因排查）

```bash
# 从 user-insight.xa.com 根 HTML 挖 license
curl -sk https://user-insight.xa.com:443/ | grep -oP 'license\{[^}]+\}' | head -1
```

**关键字段**：
- `customer_id`：客户名（极飞=`jifeikeji`）
- `max_project_num` / `project_num`：项目配额/已用
- `expire_time`：到期时间
- `max_message_num` / `message_num`：事件数配额

**若 `project_num >= max_project_num` → 这是 UNAUTHORIZED 的最常见根因**，不是 key 错。

---

## 8. 神策 SAMQL 语法速记（SQL-like）

- 表：`events`（事件表）、`users`（用户表）、`items`（item 表）
- 函数：`count(*)`、`count(distinct user_id)`（UV）、`sum(x)`、`avg(x)`
- 字段：`event`（事件名）、`time`（时间）、`user_id`、`distinct_id`、`properties.x`
- 时间过滤：`WHERE time BETWEEN '2026-05-01' AND '2026-05-31'`
- 分组：`GROUP BY properties.device_model`
- 限制：`LIMIT 10000`（默认上限）

> 完整 SAMQL 语法在 `https://manual.sensorsdata.cn/sa/docs/samql`（待抓取确认 URL）。

---

## 9. Python 快速调用样板

```python
import requests

API_KEY = open(os.path.expanduser("~/.hermes/credentials/sensors.txt")).read().strip()
HEADERS = {
    "api-key": API_KEY,
    "sensorsdata-project": "production",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
BASE = "https://user-insight.xa.com:443"

# 列事件
r = requests.get(f"{BASE}/api/v3/portal/v2/management/event/list", headers=HEADERS, timeout=30)
print(r.json())

# 查数据
r = requests.post(
    f"{BASE}/api/v3/portal/v2/query/data",
    headers=HEADERS,
    json={"project": "production", "sql": "SELECT event, count(*) FROM events GROUP BY event LIMIT 10"},
    timeout=60,
)
print(r.json())
```
