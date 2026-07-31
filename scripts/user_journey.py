#!/usr/bin/env python3
"""
sensors-analytics/scripts/user_journey.py

查单个用户（distinct_id）的完整行为旅程：
  1. 事件类型汇总
  2. 按天统计
  3. 作业/测地/客服/绑机等关键行为
  4. 详细时间线

用法:
  python3 user_journey.py <distinct_id> [days]
  python3 user_journey.py D74B8CE70961B4ADDAC9635079442350        # 默认90天
  python3 user_journey.py D74B8CE70961B4ADDAC9635079442350 30     # 30天

输出 JSON 结构:
  {
    "distinct_id": "...",
    "date_range": [first, last],
    "device_summary": [{"model", "os", "app_version", "first_seen", "last_seen"}, ...],
    "events_by_type": [{"event", "cnt", "first_date", "last_date"}, ...],
    "events_by_day":  [{"date", "event", "cnt"}, ...],
    "key_behaviors": {
      "register":      [time, ...],            # $SignUp
      "login":         [time, ...],            # user_login
      "app_start":     count,
      "bind_device":   [time, ...],            # device_add_confirm
      "check_device":  count,                  # device_add_check
      "firmware_update": count,                # device_firmware_update
      "survey":        count,                  # survey_* 合计
      "survey_mapping_device": count,          # survey_use_mapping_device
      "survey_save":   count,                  # survey_save_feilds
      "field_created": count,                  # survey_feild_info
      "operation_start": count,                # auto_operation_task_start + operation_auto_work_start + operation_lift_mode
      "customer_service": count,              # ChatActivity 页面访问（通过 $AppStart 里 $screen_name 判断）
      "re_login":      count,                  # ReLoginActivity
    },
    "journey_stages": [                        # 阶段划分（按时间+事件推断）
      {"stage": "注册/首次使用", "from": t, "to": t, "summary": "..."},
      ...
    ],
    "timeline": [{"time", "event", "app_version", "os", "model", "screen", "province", "city"}, ...]
  }
"""
import sys, os, json
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _auth import sql_query


# 行为分类（业务侧）
EVENT_CATEGORIES = {
    "注册": ["$SignUp", "$AppInstall"],
    "登录": ["user_login", "user_sms_send"],
    "启动/退出": ["$AppStart", "$AppEnd", "$AppStartPassively"],
    "设备绑定": ["device_add_check", "device_add_confirm"],
    "固件升级": ["device_firmware_update"],
    "测地": ["survey_feild_info", "survey_save_feilds", "survey_field_info", "survey_use_mapping_device"],
    "作业": ["auto_operation_task_start", "operation_auto_work_start", "operation_lift_mode"],
}
# 关键 screen 关键词
SCREEN_KEYWORDS = {
    "客服": ["ChatActivity", "customservice"],
    "重登录": ["ReLoginActivity"],
    "设备详情": ["UavDetailsActivity", "SRC4DetailActivity", "DeviceMeshActivity"],
    "设备添加": ["AddSRC4DeviceConfirmActivity", "AddDevice"],
    "固件升级页": ["DeviceUpgradeMainActivity", "AppUpdateActivity", "SRC4AppUpdateActivity"],
    "首页": ["HomeActivity"],
    "相机": ["TCameraActivity", "albumcamerarecorder"],
}


def fmt_time(t):
    if not t:
        return ""
    return str(t)[:19]


def analyze(distinct_id: str, lookback_days: int = 90):
    today = datetime.now().date()
    from_date = (today - timedelta(days=lookback_days)).isoformat()

    # 1) 事件类型汇总
    sql_summary = f"""
SELECT event, count(*) as cnt, min(date) as first_date, max(date) as last_date
FROM events
WHERE distinct_id = '{distinct_id}'
  AND date >= '{from_date}'
GROUP BY event
ORDER BY cnt DESC
LIMIT 200
"""
    cols, rows = sql_query(sql_summary, limit=500)
    events_by_type = [
        {"event": r["event"], "cnt": int(r["cnt"]),
         "first_date": fmt_time(r["first_date"])[:10],
         "last_date": fmt_time(r["last_date"])[:10]}
        for r in rows if r.get("event")
    ]

    if not events_by_type:
        return {"distinct_id": distinct_id, "found": False,
                "message": f"近 {lookback_days} 天无任何事件记录"}

    # 2) 按天×事件
    sql_daily = f"""
SELECT date, event, count(*) as cnt
FROM events
WHERE distinct_id = '{distinct_id}'
  AND date >= '{from_date}'
GROUP BY date, event
ORDER BY date, event
LIMIT 1000
"""
    cols, rows = sql_query(sql_daily, limit=2000)
    events_by_day = [
        {"date": fmt_time(r["date"])[:10], "event": r["event"], "cnt": int(r["cnt"])}
        for r in rows
    ]

    # 3) 全量 timeline（关键列）
    sql_timeline = f"""
SELECT date, time, event, $app_version, $os, $model, $screen_name, $ip, $province, $city, $device_id, user_id
FROM events
WHERE distinct_id = '{distinct_id}'
  AND date >= '{from_date}'
ORDER BY time
LIMIT 1000
"""
    cols, rows = sql_query(sql_timeline, limit=2000)
    timeline = []
    for r in rows:
        screen = (r.get("$screen_name") or "").split(".")[-1] if r.get("$screen_name") else ""
        timeline.append({
            "time": fmt_time(r.get("time")),
            "event": r.get("event"),
            "app_version": r.get("$app_version"),
            "os": r.get("$os"),
            "model": r.get("$model"),
            "screen": screen,
            "province": r.get("$province"),
            "city": r.get("$city"),
        })

    # 4) 设备汇总（model + os + app_version 唯一组合）
    device_map = {}
    for t in timeline:
        key = (t["model"] or "", t["os"] or "", t["app_version"] or "")
        if key not in device_map:
            device_map[key] = {"first": t["time"], "last": t["time"], "events": 0}
        device_map[key]["last"] = t["time"]
        device_map[key]["events"] += 1
    device_summary = [
        {"model": m, "os": o, "app_version": v,
         "first_seen": d["first"], "last_seen": d["last"], "events": d["events"]}
        for (m, o, v), d in device_map.items()
    ]
    device_summary.sort(key=lambda x: x["last_seen"], reverse=True)

    # 5) 关键行为统计
    key_behaviors = {
        "register":       sorted({t["time"] for t in timeline if t["event"] in ("$SignUp",)}),
        "app_install":    sorted({t["time"] for t in timeline if t["event"] == "$AppInstall"}),
        "login_count":    sum(1 for t in timeline if t["event"] == "user_login"),
        "app_start":      sum(1 for t in timeline if t["event"] == "$AppStart"),
        "app_end":        sum(1 for t in timeline if t["event"] == "$AppEnd"),
        "bind_device":    sorted({t["time"] for t in timeline if t["event"] == "device_add_confirm"}),
        "check_device":   sum(1 for t in timeline if t["event"] == "device_add_check"),
        "firmware_update": sum(1 for t in timeline if t["event"] == "device_firmware_update"),
        "survey_total":   sum(1 for t in timeline if (t["event"] or "").startswith("survey_")),
        "survey_mapping_device": sum(1 for t in timeline if t["event"] == "survey_use_mapping_device"),
        "survey_save_field":    sum(1 for t in timeline if t["event"] == "survey_save_feilds"),
        "field_info_created":   sum(1 for t in timeline if t["event"] in ("survey_feild_info","survey_field_info")),
        "operation_start": sum(1 for t in timeline if t["event"] in ("auto_operation_task_start","operation_auto_work_start","operation_lift_mode")),
        "customer_service_visits": sum(1 for t in timeline if any(kw in (t["screen"] or "") for kw in SCREEN_KEYWORDS["客服"])),
        "re_login_count": sum(1 for t in timeline if any(kw in (t["screen"] or "") for kw in SCREEN_KEYWORDS["重登录"])),
        "camera_visits":  sum(1 for t in timeline if any(kw in (t["screen"] or "") for kw in SCREEN_KEYWORDS["相机"])),
        "upgrade_page_visits": sum(1 for t in timeline if any(kw in (t["screen"] or "") for kw in SCREEN_KEYWORDS["固件升级页"])),
    }

    # 6) 阶段划分（按相邻事件间隔 > 30分钟 切分 session）
    sessions = []
    cur = None
    for t in timeline:
        ts = t["time"]
        if not ts:
            continue
        try:
            tdt = datetime.fromisoformat(ts)
        except Exception:
            continue
        if cur is None or (tdt - cur["end"]).total_seconds() > 1800:
            if cur:
                sessions.append(cur)
            cur = {"start": tdt, "end": tdt, "events": []}
        cur["end"] = tdt
        cur["events"].append(t)
    if cur:
        sessions.append(cur)

    def stage_label(evts):
        ev_set = {e["event"] for e in evts}
        screens = " ".join(e.get("screen") or "" for e in evts)
        has_signup = "$SignUp" in ev_set
        has_bind = "device_add_confirm" in ev_set
        has_check = "device_add_check" in ev_set
        has_fw = "device_firmware_update" in ev_set
        has_survey = any((e or "").startswith("survey_") for e in ev_set)
        has_op = bool(key_behaviors["operation_start"]) and any(
            e["event"] in ("auto_operation_task_start","operation_auto_work_start","operation_lift_mode") for e in evts
        )
        has_cs = any(kw in screens for kw in SCREEN_KEYWORDS["客服"])
        has_relogin = any(kw in screens for kw in SCREEN_KEYWORDS["重登录"])
        tags = []
        if has_signup: tags.append("注册/首次启动")
        if has_bind: tags.append("设备绑定成功")
        elif has_check: tags.append("设备绑定尝试")
        if has_fw: tags.append("固件升级")
        if has_survey: tags.append("测地/建地块")
        if has_op: tags.append("执行作业")
        if has_cs: tags.append("咨询客服")
        if has_relogin: tags.append("反复重登")
        if not tags:
            tags.append("浏览App")
        return "、".join(tags)

    journey_stages = []
    for s in sessions:
        journey_stages.append({
            "from": s["start"].isoformat(timespec="seconds"),
            "to":   s["end"].isoformat(timespec="seconds"),
            "duration_min": round((s["end"] - s["start"]).total_seconds() / 60, 1),
            "event_count": len(s["events"]),
            "summary": stage_label(s["events"]),
        })

    # 7) 活跃天数、首次/最后
    dates = sorted({(t["time"] or "")[:10] for t in timeline if t["time"]})
    first_seen = timeline[0]["time"] if timeline else ""
    last_seen = timeline[-1]["time"] if timeline else ""

    return {
        "distinct_id": distinct_id,
        "found": True,
        "lookback_days": lookback_days,
        "first_seen": first_seen,
        "last_seen": last_seen,
        "active_days": len(dates),
        "active_date_list": dates,
        "total_events": len(timeline),
        "device_summary": device_summary,
        "events_by_type": events_by_type,
        "events_by_day": events_by_day,
        "key_behaviors": key_behaviors,
        "journey_stages": journey_stages,
        "timeline": timeline,
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    did = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    result = analyze(did, days)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
