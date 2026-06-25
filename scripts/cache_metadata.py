#!/usr/bin/env python3
"""缓存神策元数据（事件表 + 用户表 + 各事件属性）到本地 JSON 文件。
分析数据前先跑这个，或者直接用缓存文件查属性。
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _auth import api_post, EP_EVENT_LIST, EP_FIELD_LIST

CACHE_DIR = os.path.expanduser("~/.hermes/data/sensors_metadata")
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_events():
    """拉所有事件列表"""
    resp = api_post(EP_EVENT_LIST, {})
    events = resp.get("data", {}).get("schemas", [])
    path = os.path.join(CACHE_DIR, "events.json")
    with open(path, "w") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"✅ 事件列表: {len(events)} 个 → {path}")
    return events

def fetch_fields(schema_name: str, output_name: str):
    """拉某 schema 的属性"""
    resp = api_post(EP_FIELD_LIST, {"schema_name": schema_name})
    fields = resp.get("data", {}).get("fields", [])
    path = os.path.join(CACHE_DIR, f"{output_name}.json")
    with open(path, "w") as f:
        json.dump(fields, f, ensure_ascii=False, indent=2)
    print(f"✅ {schema_name}: {len(fields)} 个属性 → {path}")
    return fields

def main():
    print("📊 缓存神策元数据...")
    
    # 1. 事件列表
    events = fetch_events()
    
    # 2. 用户表
    fetch_fields("users", "users")
    
    # 3. 核心事件属性（只缓存有数据的事件）
    cached = 0
    for e in events:
        if not e.get("has_data"):
            continue
        name = e.get("name", "").replace("events.", "", 1)
        safe_name = name.replace("$", "sys_").replace(".", "_")
        try:
            fetch_fields(f"events.{name}", f"event_{safe_name}")
            cached += 1
        except Exception as e:
            print(f"⚠️ 跳过 {name}: {e}")
    
    print(f"\n✅ 完成: 缓存了 {cached} 个事件的属性 + 用户表")
    print(f"📁 目录: {CACHE_DIR}")

if __name__ == "__main__":
    main()
