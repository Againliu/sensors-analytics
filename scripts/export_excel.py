#!/usr/bin/env python3
"""
sensors-analytics/export_excel.py

把查询结果导出为 Excel 文件。复用 query_data.py 的查询能力，
把 JSON 结果转成 pandas DataFrame 写 xlsx。

用法：
    python3 export_excel.py --sql "SELECT event, count(*) FROM events GROUP BY event LIMIT 10" --output result.xlsx
    python3 export_excel.py --event app_launch --from 2026-05-01 --to 2026-05-31 --output result.xlsx
"""
import os
import sys
import json
import argparse
from datetime import datetime
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _auth import get_headers
from query_data import query, structured_query


def export_to_excel(query_result: dict, output_path: str):
    """把 query_data 的结果写 xlsx。"""
    try:
        import pandas as pd
    except ImportError:
        print("❌ 需要安装 pandas: pip install pandas openpyxl", file=sys.stderr)
        sys.exit(1)

    # 神策查询返回结构待端到端确认，先尝试几种可能
    rows = []
    if isinstance(query_result, dict):
        rows = (
            query_result.get("data")
            or query_result.get("results")
            or query_result.get("rows")
            or []
        )
    elif isinstance(query_result, list):
        rows = query_result

    if not rows:
        print("⚠️  查询结果为空，写一个空表（只有表头）", file=sys.stderr)
        df = pd.DataFrame()
    else:
        # 如果 rows 是 list of list，自动用列 0,1,2...命名
        if isinstance(rows[0], (list, tuple)):
            df = pd.DataFrame(rows)
        else:
            df = pd.DataFrame(rows)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="data")
        # 顺手加一个 metadata sheet 记录查询参数
        meta = pd.DataFrame([
            {"key": "导出时间", "value": datetime.now().isoformat(timespec="seconds")},
            {"key": "总行数", "value": len(df)},
        ])
        meta.to_excel(writer, index=False, sheet_name="meta")

    print(f"✅ 已导出: {output_path} ({len(df)} 行)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="production")
    ap.add_argument("--sql", help="原始 SQL 字符串")
    ap.add_argument("--event", help="事件名")
    ap.add_argument("--from", dest="date_from")
    ap.add_argument("--to", dest="date_to")
    ap.add_argument("--where", default="")
    ap.add_argument("--group-by", default="")
    ap.add_argument("--metric", default="pv")
    ap.add_argument("--output", "-o", required=True, help="输出 xlsx 路径")
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
        export_to_excel(result, args.output)
    except requests.HTTPError as e:
        print(f"\n❌ HTTP {e.response.status_code}: {e.response.text[:300]}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
