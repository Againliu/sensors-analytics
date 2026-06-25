# 设备分类与横竖屏分析参考（Verified 2026-06-03）

## 1. 极飞遥控器型号（SRC 系列）

| 型号 | 屏幕尺寸(宽×高) | 物理形态 | 说明 |
|------|----------------|----------|------|
| SRC6 | 1920×1200 | 固定横屏 | 最新款，用户量最大 |
| SRC5 | 1920×1200 | 固定横屏 | 上一代 |
| SRC5_H | 1920×1200 | 固定横屏 | 变体 |
| SRC4_H | 2560×1440 | 固定横屏 | 高分屏 |
| SRC4 | 2560×1440 | 固定横屏 | 早期型号 |

⚠️ **SDK 的 `$screen_orientation` 在 SRC 上不可信**（详见 SKILL.md Pitfall #14）。遥控器是固定横屏硬件，不存在竖屏使用场景。分析横竖屏分布时必须排除 `$model LIKE 'SRC%'`。

---

## 2. 平板 vs 手机分类方法

神策 SDK 没有直接提供"平板/手机"分类字段，需要用屏幕尺寸推断：

```sql
SELECT
  CASE
    WHEN $model LIKE 'SRC%' THEN '遥控器(SRC)'
    WHEN $screen_height < 2000 AND $screen_width < 2000 THEN '平板'
    ELSE '手机'
  END as device_type
```

**判断逻辑**：
- 手机分辨率通常是 1080×2400 / 1200×2670 等，短边 ≥ 1000，长边 ≥ 2000
- 平板分辨率通常是 800×1280 / 1200×1920 等，两边都 < 2000
- 遥控器通过 `$model LIKE 'SRC%'` 识别

**已确认的平板型号**（从数据中识别出）：
- SM-X115（Samsung Galaxy Tab）：800×1340
- TRIPLTEK T93（专业平板）：800×1280
- 荣耀 Pad 系列等

---

## 3. 横屏使用分析标准查询

```sql
-- 手机 vs 平板横屏使用对比（排除遥控器）
SELECT
  CASE
    WHEN $screen_height < 2000 AND $screen_width < 2000 THEN '平板'
    ELSE '手机'
  END as device_type,
  $screen_orientation as orientation,
  count(distinct distinct_id) as uv,
  count(*) as pv
FROM events
WHERE event = '$AppStart'
  AND $model NOT LIKE 'SRC%'
  AND date >= 'YYYY-MM-DD' AND date <= 'YYYY-MM-DD'
GROUP BY device_type, orientation
ORDER BY device_type, orientation
```

推荐用 `$AppStart` 事件（数据最全），事件名用 `\$AppStart`（$ 需转义）。

---

## 4. 实测数据（2026-05-04 ~ 2026-06-03，30天）

| 设备类型 | 横屏UV | 竖屏UV | 横屏占比 |
|---------|--------|--------|---------|
| 手机 | 7,768 | 25,602 | 23% |
| 平板 | 1,686 | 4,728 | 26% |

**结论**: 手机横屏用户是平板的 4.6 倍，但平板用户横屏使用率略高（26% vs 23%）。
