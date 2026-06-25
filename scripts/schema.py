#!/usr/bin/env python3
"""Schema 管理 — 事件/属性的元数据操作

用法:
  # 列出所有事件
  python3 schema.py --list-events

  # 查看某事件的属性
  python3 schema.py --fields events.$AppClick

  # 设置属性可见性
  python3 schema.py --set-visible events.user_login.$identity_login_id true
  python3 schema.py --set-visible users.$identity_anonymous_id true
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _auth import api_post, EP_EVENT_LIST, EP_FIELD_LIST, EP_FIELD_UPDATE

def list_events():
    resp = api_post(EP_EVENT_LIST, {})
    return resp.get("data", {}).get("schemas", [])

def list_fields(schema_name: str):
    resp = api_post(EP_FIELD_LIST, {"schema_name": schema_name})
    return resp.get("data", {}).get("fields", [])

def set_field_visible(schema_name: str, field_name: str, visible: bool):
    payload = {
        "schema_name": schema_name,
        "field": {"name": field_name, "visible": visible},
        "update_mask": "visible"
    }
    return api_post(EP_FIELD_UPDATE, payload)

def main():
    parser = argparse.ArgumentParser(description="神策 Schema 管理")
    parser.add_argument("--list-events", action="store_true", help="列出所有事件")
    parser.add_argument("--fields", help="查看某 schema 的属性（如 events.$AppClick 或 users）")
    parser.add_argument("--set-visible", nargs=2, metavar=("FIELD_PATH", "VISIBLE"),
                        help="设置属性可见性: schema.field true/false")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    parser.add_argument("--project", default="production")
    args = parser.parse_args()

    try:
        if args.list_events:
            events = list_events()
            if args.json:
                print(json.dumps(events, ensure_ascii=False, indent=2))
            else:
                print(f"事件列表（{len(events)} 个）：")
                for e in events:
                    name = e.get("name", "").replace("events.", "", 1)
                    display = e.get("display_name", "")
                    has_data = "✅" if e.get("has_data") else "❌"
                    print(f"  {has_data} {name:<50s} {display}")

        elif args.fields:
            fields = list_fields(args.fields)
            if args.json:
                print(json.dumps(fields, ensure_ascii=False, indent=2))
            else:
                print(f"{args.fields} 的属性（{len(fields)} 个）：")
                for f in fields:
                    name = f.get("name", "")
                    display = f.get("display_name", "")
                    ftype = f.get("type", "")
                    vis = "👁" if f.get("visible", True) else "🚫"
                    has_data = "✅" if f.get("has_data") else "❌"
                    print(f"  {vis} {name:<45s} {display:<25s} {ftype:<10s} {has_data}")

        elif args.set_visible:
            field_path, visible_str = args.set_visible
            visible = visible_str.lower() in ("true", "1", "yes")
            # field_path 格式: schema_name.field_name
            parts = field_path.rsplit(".", 1)
            if len(parts) != 2:
                print(f"❌ 格式错误: 应为 schema_name.field_name", file=sys.stderr)
                sys.exit(1)
            schema_name, field_name = parts
            resp = set_field_visible(schema_name, field_name, visible)
            print(f"✅ {field_path} → visible={visible}")
            if args.json:
                print(json.dumps(resp, ensure_ascii=False, indent=2))

        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ 操作失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
