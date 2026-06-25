#!/usr/bin/env python3
"""
sensors-analytics/query_data.py

SQL-like 数据查询。封装 /api/v3/portal/v2/query 系列端点。

用法：
    # 简版：直接传 SQL 字符串
    python3 query_data.py --sql "SELECT event, count(*) FROM events GROUP BY event LIMIT 10"

    # 高阶：传 --from/--to/--event/--where/--group-by/--metric
    python3 query_data.py \\
        --event app_launch \\
        --from 2026-05-01 \\
        --to 2026-05-31 \\
        --where "city=广州" \\
        --group-by "device_model" \\
        --metric "pv,uv"
"""
import os
import sys
import json
import argparse
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _auth import BASE_URL, PORTAL_V2, get_headers, join_url


def query(sql: str, project: str = "production", timeout: int = 60) -> dict:
    """直接传 SQL 字符串查。"""
    url = join_url(BASE_URL, PORTAL_V2, "query/data")
    print(f"🔍 执行查询: POST {url}", file=sys.stderr)
    print(f"   SQL: {sql[:200]}{'...' if len(sql) > 200 else ''}", file=sys.stderr)
    body = {"project": project, "sql": sql}
    r = requests.post(url, headers=get_headers(project), json=body, timeout=timeout)
    r.raise_for_status()
    return r.json()


def structured_query(
    event: str,
    date_from: str,
    date_to: str,
    where: str = "",
    group_by: str = "",
    metric: str = "pv",
    project: str = "production",
    timeout: int = 60,
) -> dict:
    """高阶结构化查询。"""
    # 用神策 SAMQL 语法（类 SQL）
    select_part = f"Func({metric})" if "," not in metric else ",".join(f"Func({m.strip()})" for m in metric.split(","))
    where_part = f" WHERE {where}" if where else ""
    group_part = f" GROUP BY {group_by}" if group_by else ""
    sql = f"SELECT {select_part} FROM {event}{where_part}{group_part} LIMIT 10000"
    return query(sql, project, timeout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="production")
    ap.add_argument("--sql", help="原始 SQL 字符串")
    ap.add_argument("--event", help="事件名（结构化查询用）")
    ap.add_argument("--from", dest="date_from", help="起始日期 YYYY-MM-DD")
    ap.add_argument("--to", dest="date_to", help="截止日期 YYYY-MM-DD")
    ap.add_argument("--where", default="", help="过滤条件，如 city=广州")
    ap.add_argument("--group-by", default="", help="分组字段")
    ap.add_argument("--metric", default="pv", help="指标，逗号分隔（pv/uv/count）")
    args = ap.parse_args()

    if not args.sql and not args.event:
        ap.error("必须传 --sql 或 --event")

    try:
        if args.sql:
            result = query(args.sql, args.project)
        else:
            result = structured_query(
                event=args.event,
                date_from=args.date_from,
                date_to=args.date_to,
                where=args.where,
                group_by=args.group_by,
                metric=args.metric,
                project=args.project,
            )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except requests.HTTPError as e:
        print(f"\n❌ HTTP {e.response.status_code}: {e.response.text[:300]}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
