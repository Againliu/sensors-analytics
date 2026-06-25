#!/usr/bin/env python3
"""列出神策项目的事件列表 + 可选查看某个事件的属性详情

用法:
  python3 list_events.py                    # 列出所有事件
  python3 list_events.py --detail $AppClick # 查看某事件的属性列表
  python3 list_events.py --json             # 输出原始 JSON
"""
import argparse, json, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from _auth import api_post, api_get, EP_EVENT_LIST, EP_FIELD_LIST

def list_events():
    resp = api_post(EP_EVENT_LIST, {})
    schemas = resp.get("data", {}).get("schemas", [])
    return schemas

def get_fields(event_name: str):
    """获取某事件的属性列表"""
    resp = api_post(EP_FIELD_LIST, {"schema_name": f"events.{event_name}"})
    return resp.get("data", {}).get("fields", [])

def main():
    parser = argparse.ArgumentParser(description="神策事件列表/详情")
    parser.add_argument("--detail", help="查看某事件的属性列表（传事件名如 $AppClick）")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    parser.add_argument("--project", default="production")
    args = parser.parse_args()

    if args.detail:
        fields = get_fields(args.detail)
        if args.json:
            print(json.dumps(fields, ensure_ascii=False, indent=2))
        else:
            print(f"事件 {args.detail} 的属性列表（{len(fields)} 个）：")
            print(f"{'属性名':<45s} {'显示名':<25s} {'类型':<10s} {'有数据'}")
            print("-" * 100)
            for f in fields:
                name = f.get("name", "")
                display = f.get("display_name", "")
                ftype = f.get("type", "")
                has_data = f.get("has_data", False)
                visible = f.get("visible", True)
                vis_mark = "" if visible else " [隐藏]"
                print(f"{name:<45s} {display:<25s} {ftype:<10s} {'✅' if has_data else '❌'}{vis_mark}")
    else:
        events = list_events()
        if args.json:
            print(json.dumps(events, ensure_ascii=False, indent=2))
        else:
            print(f"项目事件列表（{len(events)} 个）：")
            print(f"{'事件名':<50s} {'显示名':<30s} {'有数据':<6s} {'类型'}")
            print("-" * 110)
            for e in events:
                name = e.get("name", "").replace("events.", "", 1)
                display = e.get("display_name", "")
                has_data = "✅" if e.get("has_data") else "❌"
                etype = e.get("type", "")
                print(f"{name:<50s} {display:<30s} {has_data:<6s} {etype}")

if __name__ == "__main__":
    main()
