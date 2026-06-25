#!/usr/bin/env python3
"""自定义 SQL 查询 — 最灵活的查询方式

用法:
  # 查登录总量
  python3 query_sql.py --sql "SELECT count(*) FROM events WHERE event = 'user_login'"

  # 查用户总数
  python3 query_sql.py --sql "SELECT count(*) FROM users"

  # 查 top 5 事件
  python3 query_sql.py --sql "SELECT event, count(*) as cnt FROM events GROUP BY event ORDER BY cnt DESC LIMIT 5"

  # 查某用户的登录记录
  python3 query_sql.py --sql "SELECT distinct_id, time FROM events WHERE event = 'user_login' AND date >= '2026-06-01' LIMIT 20"

  # JSON 输出
  python3 query_sql.py --sql "SELECT count(*) FROM users" --json

注意:
  - 不能直接查 events.{事件名}，要用 events WHERE event = '{事件名}'
  - 多行结果是流式 JSON（每行一个 JSON 对象），脚本已自动处理
"""
import argparse, json, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from _auth import BASE_URL, EP_SQL_QUERY, get_headers
import requests

def query_sql_raw(sql: str, project: str = "production", timeout: int = 60):
    """执行自定义 SQL，返回原始响应文本（可能是流式 JSON）"""
    url = BASE_URL + EP_SQL_QUERY
    payload = {"sql": sql, "limit": 10000}
    r = requests.post(url, json=payload, headers=get_headers(project), timeout=timeout)
    return r

def parse_streaming_json(text: str) -> list:
    """解析流式 JSON 响应（每行一个 JSON 对象，或多个 JSON 拼接）"""
    rows = []
    decoder = json.JSONDecoder()
    text = text.strip()
    pos = 0
    while pos < len(text):
        # 跳过空白和换行
        while pos < len(text) and text[pos] in " \t\n\r":
            pos += 1
        if pos >= len(text):
            break
        try:
            obj, end = decoder.raw_decode(text[pos:])
            rows.append(obj)
            pos += end
        except json.JSONDecodeError:
            # 跳过无法解析的部分
            next_brace = text.find("{", pos)
            if next_brace == -1:
                break
            pos = next_brace
    return rows

def main():
    parser = argparse.ArgumentParser(description="神策自定义 SQL 查询")
    parser.add_argument("--sql", required=True, help="SQL 语句")
    parser.add_argument("--limit", type=int, default=100, help="最多显示行数")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    parser.add_argument("--project", default="production")
    args = parser.parse_args()

    try:
        r = query_sql_raw(args.sql, args.project)
        text = r.text

        if r.status_code != 200:
            print(f"❌ HTTP {r.status_code}: {text[:300]}", file=sys.stderr)
            sys.exit(1)

        # 尝试解析（可能是单个 JSON 或流式多 JSON）
        rows = parse_streaming_json(text)
        if not rows:
            print(f"❌ 无法解析响应: {text[:300]}", file=sys.stderr)
            sys.exit(1)

        # 检查错误
        first = rows[0]
        if first.get("error") or first.get("error_type"):
            print(f"❌ API 错误: {first.get('error_type','')} - {first.get('error','')}", file=sys.stderr)
            sys.exit(1)
        if first.get("code") and first["code"] not in ("SUCCESS", ""):
            msg = first.get("message", "")
            print(f"❌ API code={first['code']}: {msg}", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps(rows if len(rows) > 1 else rows[0], ensure_ascii=False, indent=2))
        else:
            # 格式化表格输出
            all_data = []
            columns = None
            for row_resp in rows:
                data = row_resp.get("data", {})
                if isinstance(data, dict):
                    row_data = data.get("data", [])
                    cols = data.get("columns", [])
                    if not columns:
                        columns = cols
                    if isinstance(row_data, list) and row_data:
                        if isinstance(row_data[0], list):
                            all_data.extend(row_data)
                        else:
                            all_data.append(row_data)

            if columns:
                print("\t".join(columns))
                print("-" * (len(columns) * 20))
            for i, row in enumerate(all_data[:args.limit]):
                if isinstance(row, list):
                    print("\t".join(str(v) for v in row))
                else:
                    print(row)
            if len(all_data) > args.limit:
                print(f"\n... 共 {len(all_data)} 行，只显示前 {args.limit} 行")
            elif not columns:
                # 单值结果
                for row_resp in rows:
                    data = row_resp.get("data", {})
                    if isinstance(data, dict):
                        vals = data.get("data", [])
                        print(vals)

    except Exception as e:
        print(f"❌ 查询失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
