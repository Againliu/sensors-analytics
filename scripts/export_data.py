#!/usr/bin/env python3
"""异步导出实体列表（标签/分群数据）

三步流程:
  1. 创建导出任务 → 拿 task_id
  2. 轮询 get-status 直到完成
  3. 下载结果（FILE 模式）或通过 JDBC 拉取（TABLE 模式）

用法:
  # 导出所有用户（TABLE 模式，需 JDBC 拉取）
  python3 export_data.py --segment "user.$SegmentMembership.全部用户 == true" --attrs id,name,city

  # 导出标签数据（FILE 模式）
  python3 export_data.py --tag "user.活跃度.is_not_null()" --attrs id,活跃度 --format FILE

  # 只创建任务不等待
  python3 export_data.py --segment "user.$SegmentMembership.全部用户 == true" --attrs id --create-only
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _auth import api_post, api_get, async_task_wait, EP_EXPORT_CREATE, EP_EXPORT_STATUS

PROJECT_ID = 2  # production 项目的数字 ID

def create_export_task(args):
    """创建导出任务"""
    # 构建分群/标签规则
    if args.tag:
        eql = args.tag
    elif args.segment:
        eql = args.segment
    else:
        eql = "user.$SegmentMembership.全部用户 == true"  # 默认全量

    attrs = [a.strip() for a in args.attrs.split(",")]
    if "id" not in attrs:
        attrs.insert(0, "id")  # 必须包含主键

    payload = {
        "entity_name": "user",
        "attribute_paths": attrs,
        "project_id": PROJECT_ID,
        "segment_rule_expression": {
            "type": "EQL_BASED",
            "eql_segment_rule": {"eql": eql}
        },
        "export_format": {"format_type": args.format.upper()}
    }
    return api_post(EP_EXPORT_CREATE, payload)


def check_status(task_id: str, project: str = "production"):
    """查询任务状态"""
    return api_get(EP_EXPORT_STATUS, params={"task_id": task_id}, project=project)


def main():
    parser = argparse.ArgumentParser(description="神策实体列表异步导出")
    parser.add_argument("--segment", help="分群规则 EQL（如 user.$SegmentMembership.全部用户 == true）")
    parser.add_argument("--tag", help="标签规则 EQL（如 user.活跃度.is_not_null()）")
    parser.add_argument("--attrs", default="id", help="导出属性，逗号分隔（必须含 id）")
    parser.add_argument("--format", default="TABLE", choices=["TABLE", "FILE"], help="导出格式")
    parser.add_argument("--create-only", action="store_true", help="只创建任务，不等待完成")
    parser.add_argument("--status", help="查询已有任务状态（传 task_id）")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    parser.add_argument("--project", default="production")
    args = parser.parse_args()

    try:
        if args.status:
            resp = check_status(args.status, args.project)
            print(json.dumps(resp, ensure_ascii=False, indent=2))
            return

        # 创建任务
        print("📤 创建导出任务...", file=sys.stderr)
        resp = create_export_task(args)
        data = resp.get("data", resp)
        task_id = data.get("task_id", data.get("id", ""))
        if not task_id:
            print(f"❌ 创建失败: {json.dumps(resp, ensure_ascii=False)[:300]}", file=sys.stderr)
            sys.exit(1)
        print(f"✅ 任务已创建: task_id={task_id}", file=sys.stderr)

        if args.create_only:
            print(json.dumps({"task_id": task_id, "status": "CREATED"}, ensure_ascii=False, indent=2))
            return

        # 轮询等待完成
        print(f"⏳ 等待任务完成（最多 5 分钟）...", file=sys.stderr)
        result = async_task_wait(task_id, args.project)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"✅ 导出完成: {json.dumps(result, ensure_ascii=False)[:500]}")

    except Exception as e:
        print(f"❌ 导出失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
