#!/usr/bin/env python3
"""
sensors-analytics/scripts/user_summary.py

用户旅程快速读版（人读友好的中文摘要）。
用法:
  python3 user_summary.py <distinct_id> [days]
输出: 直接打印中文摘要到 stdout（设备、关键行为、阶段），适合在对话里引用。
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from user_journey import analyze


def fmt_ts(t):
    if not t: return "—"
    s = str(t)
    if len(s) >= 16:
        return s[5:16]  # MM-DD HH:MM
    return s[:16]


def summarize(result):
    if not result.get("found"):
        return f"❌ {result['distinct_id']}: {result['message']}"

    lines = []
    did = result["distinct_id"]
    lines.append(f"## 用户 {did}")
    lines.append(f"- 首次活跃: {result['first_seen']}")
    lines.append(f"- 最后活跃: {result['last_seen']}")
    lines.append(f"- 活跃天数: {result['active_days']} 天 ({', '.join(result['active_date_list'])})")
    lines.append(f"- 总事件数: {result['total_events']}")
    lines.append("")

    # 设备
    lines.append("### 设备矩阵")
    for d in result["device_summary"]:
        lines.append(f"- {d['model'] or '未知型号'} / {d['os'] or '?'} / App {d['app_version'] or '?'}  "
                     f"({d['first_seen'][5:16]} ~ {d['last_seen'][5:16]}, {d['events']} 事件)")
    lines.append("")

    # 关键行为
    kb = result["key_behaviors"]
    lines.append("### 关键行为")
    lines.append(f"- 注册: {len(kb['register'])} 次 ({', '.join(fmt_ts(t) for t in kb['register']) or '—'})")
    lines.append(f"- 登录/发短信: {kb['login_count']} 次")
    lines.append(f"- 启动/退出 App: {kb['app_start']} / {kb['app_end']}")
    lines.append(f"- 绑定设备: {len(kb['bind_device'])} 次成功 ({', '.join(fmt_ts(t) for t in kb['bind_device']) or '—'})")
    lines.append(f"- 设备连接检查: {kb['check_device']} 次")
    lines.append(f"- 固件升级进度上报: {kb['firmware_update']} 次")
    lines.append(f"- 测地/地块操作: {kb['survey_total']} 次 (选测绘设备 {kb['survey_mapping_device']}, "
                 f"保存地块 {kb['survey_save_field']}, 地块创建 {kb['field_info_created']})")
    lines.append(f"- 启动作业: {kb['operation_start']} 次 {'⚠️ 无作业记录' if kb['operation_start']==0 else '✅'}")
    lines.append(f"- 进在线客服: {kb['customer_service_visits']} 次")
    lines.append(f"- 触发重新登录: {kb['re_login_count']} 次")
    lines.append(f"- 打开相机（可能在给客服发图）: {kb['camera_visits']} 次")
    lines.append(f"- 在固件升级页停留次数: {kb['upgrade_page_visits']} 次")
    lines.append("")

    # 阶段
    lines.append("### 行为阶段（按 session 切分，相邻事件 >30 分钟为新 session）")
    for i, s in enumerate(result["journey_stages"], 1):
        lines.append(f"{i}. **{fmt_ts(s['from'])} → {fmt_ts(s['to'])}** "
                     f"({s['duration_min']} 分钟, {s['event_count']} 事件)  "
                     f"→ {s['summary']}")

    # 用户分层判断
    lines.append("")
    lines.append("### 判断")
    signals = []
    if kb["operation_start"] == 0 and kb["survey_total"] == 0:
        signals.append("未进入测地/作业阶段，纯设备准备")
    if kb["operation_start"] == 0 and kb["survey_total"] > 0:
        signals.append("做完测地但没开始作业，卡在上游环节")
    if kb["operation_start"] > 0:
        signals.append("已开始实际作业，是真实作业用户")
    if kb["customer_service_visits"] >= 5:
        signals.append(f"密集使用客服({kb['customer_service_visits']}次)，大概率遇到严重问题")
    if kb["re_login_count"] >= 3:
        signals.append(f"反复重登({kb['re_login_count']}次)，存在登录态/升级后掉线问题")
    if kb["app_start"] >= 20 and kb["operation_start"] == 0:
        signals.append(f"高频进出App({kb['app_start']}次启动)但没作业，典型故障态行为")
    days_since_last = 0
    try:
        from datetime import datetime
        last = datetime.fromisoformat(result["last_seen"])
        days_since_last = (datetime.now() - last).days
    except Exception:
        pass
    if days_since_last >= 14:
        signals.append(f"已沉默 {days_since_last} 天，流失风险高")
    elif days_since_last <= 1:
        signals.append("最近 24 小时内仍活跃")
    for s in signals:
        lines.append(f"- {s}")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    did = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    result = analyze(did, days)
    print(summarize(result))


if __name__ == "__main__":
    main()
