#!/usr/bin/env python3
"""事件分析查询 — 最常用的分析接口

用法:
  # PV 统计（按天）
  python3 query_segmentation.py --event '$pageview' --from 2026-06-01 --to 2026-06-03

  # App 点击 PV，按 device_model 分组
  python3 query_segmentation.py --event '$AppClick' --from 2026-06-01 --to 2026-06-03 \\
    --group-by 'event.$AppClick.$device_model' --unit DAY

  # UV 统计
  python3 query_segmentation.py --event 'user_login' --from 2026-06-01 --to 2026-06-03 \\
    --aggregator UV

  # 带筛选: 只看 iOS
  python3 query_segmentation.py --event '$AppStartPassively' --from 2026-06-01 --to 2026-06-03 \\
    --filter 'event.$AppStartPassively.$os=IOS'

  # JSON 输出
  python3 query_segmentation.py --event '$pageview' --from 2026-06-01 --to 2026-06-03 --json
"""
import argparse, json, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from _auth import api_post, EP_SEG_REPORT, EP_SEG_USERS

def build_query(args):
    """构建事件分析请求体"""
    measure = {
        "event_name": args.event,
        "aggregator": args.aggregator.upper(),
        "name": f"{args.event}_{args.aggregator}",
    }
    # 事件级筛选
    if args.event_filter:
        conditions = []
        for f in args.event_filter:
            field, val = f.split("=", 1)
            conditions.append({
                "field": field,
                "function": "equal",
                "params": [val]
            })
        measure["filter"] = {"relation": "and", "conditions": conditions}

    payload = {
        "measures": [measure],
        "from_date": args.from_date,
        "to_date": args.to_date,
        "unit": args.unit.upper(),
    }

    # 全局筛选
    if args.filter:
        conditions = []
        for f in args.filter:
            field, val = f.split("=", 1)
            conditions.append({
                "field": field,
                "function": "equal",
                "params": [val]
            })
        payload["filter"] = {"relation": "and", "conditions": conditions}

    # 分组维度
    if args.group_by:
        payload["by_fields"] = [{"field": g} for g in args.group_by]

    return payload


def query_report(args):
    payload = build_query(args)
    return api_post(EP_SEG_REPORT, payload, timeout=60)


def query_users(args):
    """用户明细（需要额外参数）"""
    payload = build_query(args)
    payload["limit"] = args.limit or 100
    payload["offset"] = args.offset or 0
    return api_post(EP_SEG_USERS, payload, timeout=60)


def format_report(data):
    """格式化输出报告数据"""
    result = data.get("data", {})
    # 响应结构: {data: {series: [{name, data: [...]}]}} 或类似
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False, indent=2)
    return json.dumps(data, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="神策事件分析查询")
    parser.add_argument("--event", required=True, help="事件名（如 $AppClick, user_login）")
    parser.add_argument("--from", dest="from_date", required=True, help="起始日期 yyyy-MM-dd")
    parser.add_argument("--to", dest="to_date", required=True, help="结束日期 yyyy-MM-dd")
    parser.add_argument("--aggregator", default="pv", help="聚合方式: pv/uv/sum/avg/max/min/count (默认 pv)")
    parser.add_argument("--unit", default="DAY", help="时间粒度: HOUR/DAY/WEEK/MONTH (默认 DAY)")
    parser.add_argument("--group-by", nargs="*", help="分组维度（事件/用户属性路径）")
    parser.add_argument("--filter", nargs="*", help="全局筛选 field=value（可多个）")
    parser.add_argument("--event-filter", nargs="*", help="事件级筛选 field=value")
    parser.add_argument("--users", action="store_true", help="查用户明细而非报告")
    parser.add_argument("--limit", type=int, default=100, help="用户明细返回条数")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    parser.add_argument("--project", default="production")
    args = parser.parse_args()

    try:
        if args.users:
            resp = query_users(args)
        else:
            resp = query_report(args)

        if args.json:
            print(json.dumps(resp, ensure_ascii=False, indent=2))
        else:
            print(format_report(resp))
    except Exception as e:
        print(f"❌ 查询失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
