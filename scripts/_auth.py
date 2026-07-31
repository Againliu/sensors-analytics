#!/usr/bin/env python3
"""
sensors-analytics/_auth.py

神策分析 OpenAPI 认证 + 端点常量 + 通用 helper。
所有脚本 from _auth import ...

端点按四大前缀分类:
  PORTAL_V2  = /api/v3/portal/v2     — 项目管理/身份/行为审计
  ANALYTICS  = /api/v3/analytics/v1  — 分析模型(19)+概览+业务集市+智能预警+属性元数据+渠道+SQL
  HORIZON    = /api/v3/horizon/v1    — Schema/标签/分群/目录/实体导出
  
  覆盖神策 OpenAPI 官方 63 个端点 + Portal V2 额外 5 个 + Tag/Segment/Export 9 个
"""
import os, sys, json, time
import requests

# ═══════════════════════════════════════════════════
# 基础配置
# ═══════════════════════════════════════════════════
BASE_URL = "https://user-insight.xa.com:443"
DEFAULT_PROJECT = "production"

# ═══════════════════════════════════════════════════
# URL 前缀（v3 大版本不变，v1/v2 接口版本随产品升级变）
# ═══════════════════════════════════════════════════
PORTAL_V2   = "/api/v3/portal/v2"
ANALYTICS   = "/api/v3/analytics/v1"
HORIZON     = "/api/v3/horizon/v1"

# ═══════════════════════════════════════════════════
# 端点常量 — Portal V2（项目管理/身份/行为审计）
# ═══════════════════════════════════════════════════
EP_PROJECT_LIST       = PORTAL_V2 + "/management/project/list"
EP_GLOBAL_ACCOUNT     = PORTAL_V2 + "/identity/global-account"
EP_PROJECT_INVITE     = PORTAL_V2 + "/identity/project/invite"
EP_BEHAVIOR_LIST      = PORTAL_V2 + "/management/behavior/list"
EP_ROLE_LIST          = PORTAL_V2 + "/management/role/list"

# ═══════════════════════════════════════════════════
# 端点常量 — Analytics V1（16 个分析模型 + SQL）
# ═══════════════════════════════════════════════════
# 事件分析
EP_SEG_REPORT         = ANALYTICS + "/model/segmentation/report"
EP_SEG_USERS          = ANALYTICS + "/model/segmentation/users"
# 漏斗
EP_FUNNEL_REPORT      = ANALYTICS + "/model/funnel/report"
EP_FUNNEL_USERS       = ANALYTICS + "/model/funnel/users"
# 留存
EP_RETENTION_REPORT   = ANALYTICS + "/model/retention/report"
EP_RETENTION_USERS    = ANALYTICS + "/model/retention/users"
# 分布（addiction = 分布，神策内部命名）
EP_ADDICTION_REPORT   = ANALYTICS + "/model/addiction/report"
EP_ADDICTION_USERS    = ANALYTICS + "/model/addiction/users"
# 间隔
EP_INTERVAL_REPORT    = ANALYTICS + "/model/interval/report"
# 归因
EP_ATTRIBUTION_REPORT = ANALYTICS + "/model/attribution/report"
# LTV
EP_LTV_REPORT         = ANALYTICS + "/model/ltv/report"
EP_LTV_USERS          = ANALYTICS + "/model/ltv/users"
# 属性分析
EP_USER_ANALYTICS     = ANALYTICS + "/model/user-analytics/report"
# 用户
EP_USER_LIST          = ANALYTICS + "/model/user/list"
EP_USER_BEHAVIOR      = ANALYTICS + "/model/user/behavior"
# Session 分析
EP_SESSION_REPORT     = ANALYTICS + "/model/session/report"
EP_SESSION_USERS      = ANALYTICS + "/model/session/users"
# 用户路径分析
EP_USER_PATH_USERS    = ANALYTICS + "/model/user-path/users"
# 自定义 SQL
EP_SQL_QUERY          = ANALYTICS + "/model/sql/query"

# ═══════════════════════════════════════════════════
# 端点常量 — Analytics V1: Dashboard 概览/书签
# ═══════════════════════════════════════════════════
EP_DASH_NAVIGATION    = ANALYTICS + "/dashboard/navigation"
EP_DASH_NAV_CREATE    = ANALYTICS + "/dashboard/navigation/create"
EP_DASH_LEGO          = ANALYTICS + "/dashboard/lego"
EP_DASH_DETAIL        = ANALYTICS + "/dashboard/detail"
EP_DASH_SHARE         = ANALYTICS + "/dashboard/share"
EP_DASH_BOOKMARKS     = ANALYTICS + "/dashboard/bookmarks"

# ═══════════════════════════════════════════════════
# 端点常量 — Analytics V1: Dataset 业务集市
# ═══════════════════════════════════════════════════
EP_DATASET_DETAIL     = ANALYTICS + "/dataset/detail"
EP_DATASET_LIST       = ANALYTICS + "/dataset/detail_list"
EP_DATASET_GROUPS     = ANALYTICS + "/dataset/group/list"
EP_DATASET_QUERY      = ANALYTICS + "/dataset/model/query"
EP_DATASET_REFRESH    = ANALYTICS + "/dataset/refresh"
EP_DATASET_SYNC_TASK  = ANALYTICS + "/dataset/sync_task_detail"
EP_DATASET_SQL        = ANALYTICS + "/dataset/table/sql_query"

# ═══════════════════════════════════════════════════
# 端点常量 — Analytics V1: SmartAlarm 智能预警
# ═══════════════════════════════════════════════════
EP_ALARM_ALL          = ANALYTICS + "/smart-alarm/all"
EP_ALARM_DETAIL       = ANALYTICS + "/smart-alarm/detail"

# ═══════════════════════════════════════════════════
# 端点常量 — Analytics V1: EventMeta 事件元数据（轻量）
# ═══════════════════════════════════════════════════
EP_EVENTMETA_ALL      = ANALYTICS + "/event-meta/events/all"
EP_EVENTMETA_TAGS     = ANALYTICS + "/event-meta/events/tags"

# ═══════════════════════════════════════════════════
# 端点常量 — Analytics V1: PropertyMeta 属性元数据
# ═══════════════════════════════════════════════════
EP_PROP_EVENT_PROPS   = ANALYTICS + "/property-meta/event-properties"
EP_PROP_EVENT_ALL     = ANALYTICS + "/property-meta/event-properties/all"
EP_PROP_VALUES        = ANALYTICS + "/property-meta/property/values"
EP_PROP_USER_GROUPS   = ANALYTICS + "/property-meta/user-groups/all"
EP_PROP_USER_ALL      = ANALYTICS + "/property-meta/user-properties/all"
EP_PROP_USER_TAGS     = ANALYTICS + "/property-meta/user-tags/dir"

# ═══════════════════════════════════════════════════
# 端点常量 — Analytics V1: Channel 渠道追踪（完整 CRUD）
# ═══════════════════════════════════════════════════
EP_CHANNEL_LINKS_LIST    = ANALYTICS + "/channel/links/list"
EP_CHANNEL_LINKS_CREATE  = ANALYTICS + "/channel/links/create"
EP_CHANNEL_LINKS_UPDATE  = ANALYTICS + "/channel/links/update"
EP_CHANNEL_LINKS_DELETE  = ANALYTICS + "/channel/links/delete"
EP_CHANNEL_CAMPAIGNS     = ANALYTICS + "/channel/campaigns/list"

# ═══════════════════════════════════════════════════
# 端点常量 — Horizon V1: Schema 元数据管理（完整 13 个）
# ═══════════════════════════════════════════════════
EP_EVENT_LIST         = HORIZON + "/schema/event/list"
EP_EVENT_GET          = HORIZON + "/schema/event/get"
EP_EVENT_CREATE       = HORIZON + "/schema/event/create"
EP_EVENT_UPDATE       = HORIZON + "/schema/event/update"
EP_EVENT_DELETE       = HORIZON + "/schema/event/delete"
EP_EVENT_FIELD_LIST   = HORIZON + "/schema/event/field/list"
EP_FIELD_LIST         = HORIZON + "/schema/field/list"
EP_FIELD_GET          = HORIZON + "/schema/field/get"
EP_FIELD_BATCH_CREATE = HORIZON + "/schema/field/batch-create"
EP_FIELD_UPDATE       = HORIZON + "/schema/field/update"
EP_EXT_TABLE_LIST     = HORIZON + "/schema/extended-table/list"
EP_EXT_TABLE_CREATE   = HORIZON + "/schema/extended-table/batch-create"
EP_EXT_TABLE_UPDATE   = HORIZON + "/schema/extended-table/update"
EP_SCHEMA_GET         = HORIZON + "/schema/get"

# ═══════════════════════════════════════════════════
# 端点常量 — Horizon V1: Catalog 目录服务
# ═══════════════════════════════════════════════════
EP_CATALOG_TREE       = HORIZON + "/catalog/tree/list"
EP_CATALOG_BIND       = HORIZON + "/catalog/resource/bind"
EP_CATALOG_UNBIND     = HORIZON + "/catalog/resource/unbind"

# ═══════════════════════════════════════════════════
# 端点常量 — Horizon V1: Tag/Segment/Export
# ═══════════════════════════════════════════════════
EP_TAG_LIST           = HORIZON + "/tag/definition/list"
EP_TAG_DELETE         = HORIZON + "/tag/definition/delete"
EP_TAG_TASK_GET       = HORIZON + "/tag/task/get"
EP_SEGMENT_LIST       = HORIZON + "/segment/definition/list"
EP_SEGMENT_DELETE     = HORIZON + "/segment/definition/delete"
EP_SEGMENT_TASK_GET   = HORIZON + "/segment/task/get"
EP_EXPORT_CREATE      = HORIZON + "/entity-list/export-task/create"
EP_EXPORT_STATUS      = HORIZON + "/entity-list/export-task/get-status"

# ═══════════════════════════════════════════════════
# 认证
# ═══════════════════════════════════════════════════
def get_api_key() -> str:
    """从 ~/.hermes/credentials/sensors.txt 读 API-Key（35 字符，#K-XXXXX...）"""
    cred_path = os.path.expanduser("~/.hermes/credentials/sensors.txt")
    if not os.path.exists(cred_path):
        print(f"❌ 凭据文件不存在: {cred_path}", file=sys.stderr)
        sys.exit(1)
    api_key = open(cred_path).read().strip()
    if not api_key or len(api_key) != 35 or not api_key.startswith("#K-"):
        print(f"⚠️ 凭据格式异常: 长度={len(api_key)}, 前缀={api_key[:4]}", file=sys.stderr)
    return api_key


def get_headers(project: str = DEFAULT_PROJECT) -> dict:
    """生成鉴权 header"""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "api-key": get_api_key(),
        "sensorsdata-project": project,
    }


# ═══════════════════════════════════════════════════
# Helper
# ═══════════════════════════════════════════════════
def join_url(*parts) -> str:
    """拼 URL: join_url(BASE_URL, EP_SEG_REPORT) → 完整 URL"""
    parts = [p.strip("/") for p in parts if p]
    if not parts:
        return ""
    return "/".join(parts)


def api_post(endpoint: str, payload: dict, project: str = DEFAULT_PROJECT,
             timeout: int = 30) -> dict:
    """POST 请求 + 自动解析响应。返回 {"code", "data", ...} 或抛异常"""
    url = join_url(BASE_URL, endpoint)
    r = requests.post(url, json=payload, headers=get_headers(project), timeout=timeout)
    return parse_response(r)


def api_get(endpoint: str, params: dict = None, project: str = DEFAULT_PROJECT,
            timeout: int = 30) -> dict:
    """GET 请求 + 自动解析"""
    url = join_url(BASE_URL, endpoint)
    r = requests.get(url, params=params, headers=get_headers(project), timeout=timeout)
    return parse_response(r)


def parse_response(r: requests.Response, expect_stream: bool = False) -> dict | list:
    """解析响应。
    
    普通模式(expect_stream=False): 返回单个 dict（首个 JSON 对象）。
    流式模式(expect_stream=True): 返回 list[dict]，合并所有行的 data 行。
    
    神策 SQL 端点当结果有多行时，会返回 NDJSON（每行一个 JSON 对象，content-type 仍
    是 application/json），此时 r.json() 会抛 JSONDecodeError('Extra data')，
    必须用 raw_decode 逐个解析。
    """
    if r.status_code != 200:
        raise Exception(f"HTTP {r.status_code}: {r.text[:300]}")
    text = r.text
    # 先尝试单对象
    try:
        body = json.loads(text)
        if expect_stream:
            # 单对象也包成 list
            return [body]
        return body
    except json.JSONDecodeError:
        pass
    # NDJSON 流式解析
    objs = []
    decoder = json.JSONDecoder()
    i = 0
    while i < len(text):
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text):
            break
        try:
            obj, idx = decoder.raw_decode(text, i)
            objs.append(obj)
            i = idx
        except json.JSONDecodeError:
            i += 1
    if not objs:
        raise Exception(f"JSON 解析失败（0 个对象）: {text[:300]}")
    if not expect_stream:
        # 单对象模式返回第一个 + 校验
        body = objs[0]
    else:
        body = objs
    if isinstance(body, dict):
        if body.get("error") or body.get("error_type"):
            raise Exception(f"API 错误: {body.get('error_type','')} - {body.get('error','')}")
        if body.get("code") and body["code"] not in ("SUCCESS", ""):
            msg = body.get("message", body.get("error_info", {}).get("error_causes", []))
            raise Exception(f"API code={body['code']}: {msg}")
    return body


def sql_query(sql: str, limit: int = 1000, project: str = DEFAULT_PROJECT,
              timeout: int = 60) -> tuple[list, list[dict]]:
    """执行 SQL 查询并返回 (columns, rows)，自动处理 NDJSON 流式响应。
    
    返回:
      columns: 列名列表，如 ['date', 'event', 'cnt']
      rows:    dict 列表，每个 dict 的 key 是 column 名。
               注意: 神策返回的数值是 float（count(*) → float），需自行转 int。
    
    用法:
      cols, rows = sql_query(\"SELECT event, count(*) as cnt FROM events ...\")
      for r in rows:
          print(r['event'], int(r['cnt']))
    """
    url = join_url(BASE_URL, EP_SQL_QUERY)
    r = requests.post(url, json={"sql": sql, "limit": limit},
                      headers=get_headers(project), timeout=timeout)
    objs = parse_response(r, expect_stream=True)
    if not isinstance(objs, list):
        objs = [objs]
    all_rows = []
    columns = None
    for obj in objs:
        if not isinstance(obj, dict):
            continue
        if obj.get("code") and obj["code"] != "SUCCESS":
            msg = obj.get("message", "")
            raise Exception(f"SQL API code={obj['code']}: {msg}")
        d = obj.get("data", {})
        obj_columns = d.get("columns", [])
        if columns is None:
            columns = obj_columns
        data = d.get("data", [])
        if isinstance(data, list) and obj_columns:
            n = len(obj_columns)
            # 处理两种 data 格式:
            # 1. data = [v1, v2, v3, v1, v2, v3, ...] (扁平值列表)
            # 2. data = [[v1, v2, v3], [v1, v2, v3], ...] (嵌套行列表)
            if len(data) > 0 and isinstance(data[0], list):
                # 嵌套行列表
                for row in data:
                    if isinstance(row, list) and len(row) == n:
                        all_rows.append(dict(zip(obj_columns, row)))
            else:
                # 扁平值列表
                for j in range(0, len(data), n):
                    chunk = data[j:j+n]
                    if len(chunk) == n:
                        all_rows.append(dict(zip(obj_columns, chunk)))
        # 如果后续对象的 columns 不同，更新（第一行可能是 header 对象）
        if obj_columns and columns != obj_columns:
            columns = obj_columns
    return columns or [], all_rows


def async_task_wait(task_id: str, project: str = DEFAULT_PROJECT,
                    max_wait: int = 300, interval: int = 5) -> dict:
    """轮询异步导出任务直到完成。返回最终状态 dict"""
    start = time.time()
    while time.time() - start < max_wait:
        resp = api_get(EP_EXPORT_STATUS, params={"task_id": task_id}, project=project)
        data = resp.get("data", {})
        status = data.get("status", "")
        if status in ("FINISH", "SUCCESS", "DONE"):
            return data
        if status in ("FAIL", "FAILED", "ERROR"):
            raise Exception(f"导出任务失败: {data}")
        print(f"  ⏳ 任务状态: {status}, 已等 {int(time.time()-start)}s...", file=sys.stderr)
        time.sleep(interval)
    raise Exception(f"导出任务超时 ({max_wait}s): task_id={task_id}")


# ═══════════════════════════════════════════════════
# 自测
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    key = get_api_key()
    print(f"✅ API-Key: {key[:5]}... (长度 {len(key)})")
    print(f"✅ Base URL: {BASE_URL}")
    print(f"✅ Project: {DEFAULT_PROJECT}")
    # 探活: 项目列表
    try:
        resp = api_get(EP_PROJECT_LIST)
        projects = resp.get("data", {}).get("projects", [])
        print(f"✅ 项目列表: {len(projects)} 个")
        for p in projects:
            proj = p.get("project", {})
            print(f"   - {proj.get('name')} ({proj.get('cname', '')})")
    except Exception as e:
        print(f"❌ 鉴权失败: {e}")
