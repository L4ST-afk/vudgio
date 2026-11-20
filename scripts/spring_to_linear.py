#!/usr/bin/env python3
"""弹簧参数 → CSS `linear()` 缓动曲线。纯标准库、离线、确定性。

为什么有这个脚本：motion.md 写了「按刚度和阻尼对位移做数值积分，取 20–30 个采样点写进
`linear()`，时长取位移稳定在终点 0.5% 以内的时刻」——那是一句可执行的话，但过去只能手算。
本脚本把那句话兑现成命令，并顺带解决一个它暴露出来的矛盾：

- 「手感」表给的是**材质倾向**（石／金属偏硬，纸／雾偏软），那组 k/c 积分出来的实际时长，
  往往比「时长和幅度」表白纸黑字写的区间长得多（咔嗒档 0.94s vs 按钮该 100–180ms）。
- 所以两种用法分开：`--preset` 复现材质手感；`--target` 按**你要的时长**反解 k/c。

用法：
  python3 spring_to_linear.py --preset 咔嗒
  python3 spring_to_linear.py -k 300 -c 20 --samples 30
  python3 spring_to_linear.py --target 200 --overshoot 8     # 200ms 落定、过冲 8%
  python3 spring_to_linear.py --presets                      # 六个预设一次列全
  python3 spring_to_linear.py --preset 滑入 --json

模型：质量 1、位移 0→1，x'' = -k·x - c·x'（RK4，步长 1ms）。时长取「|位移-1| 连续 ≤0.5%」。
过冲保留（`linear()` 允许 >1），不做上钳——上钳会把回弹抹平成台阶。
"""
import argparse
import json
import math
import sys

# Windows 控制台默认 cp1252，✓/⚠/中文会在 print 时抛 UnicodeEncodeError；
# 统一按 UTF-8 输出，编不出的字符降级成 ?，别让编码把业务判断顶掉。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


# 与 motion.md「手感」表同源：动作 → 刚度 k / 阻尼 c。⛔ 改表请同时改那边，两边不许漂。
PRESETS = {
    "咔嗒": (375, 12),   # 磁铁吸合、卡扣：按钮、开关、下拉展开
    "滑入": (275, 22),   # 抽屉阻尼：底部面板、抽屉、折叠
    "流淌": (175, 35),   # 倒蜂蜜、雾散：页面转场、主视觉出现
    "砸落": (450, 8),    # 锤击、重物落桌：确认选择、完成反馈
    "回弹": (300, 8),    # 橡皮球：庆祝提示、儿童与游戏
    "漂浮": (100, 25),   # 氦气球、飘絮：冥想、梦幻、空闲循环
}

DT = 0.001        # 积分步长（秒）
T_LIMIT = 3.0     # 上限，防未欠阻尼参数积到无穷
TOL = 0.005       # 稳定判据：|位移-1| ≤ 0.5%
HOLD = 0.05       # 需连续保持 50ms，避免恰好穿过终点被误判
FALLBACK_TOL = 2.0  # 过冲低于这个百分比就不必保真，走 cubic-bezier 退路即可


def simulate(k, c, dt=DT, t_limit=T_LIMIT):
    """RK4 积分弹簧，返回 [(t, 位移 0→1)]。"""
    def acc(x, v):
        return -k * x - c * v

    x, v, t = 1.0, 0.0, 0.0   # 位移以 1 为起点，1-x 才是 0→1 的进度
    out = [(0.0, 0.0)]
    for _ in range(int(t_limit / dt)):
        k1x, k1v = v, acc(x, v)
        k2x, k2v = v + 0.5 * dt * k1v, acc(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v)
        k3x, k3v = v + 0.5 * dt * k2v, acc(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v)
        k4x, k4v = v + dt * k3v, acc(x + dt * k3x, v + dt * k3v)
        x += dt / 6.0 * (k1x + 2 * k2x + 2 * k3x + k4x)
        v += dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v)
        t += dt
        out.append((t, 1.0 - x))
    return out


def hold_window(end_guess=T_LIMIT):
    """保持窗按目标时长缩放：40ms 的按钮动作扛不住固定 50ms 的窗。

    固定 HOLD 会把短动作一律抬到 ≥50ms（实测 --target 40 出 74ms），
    所以取 min(50ms, 目标×5%)、下限 2ms —— 既防「恰好穿过终点」误判，又不改短动作的时长。
    """
    return max(0.002, min(HOLD, end_guess * 0.05))


def settle_time(series, hold=None):
    """最后一个偏离终点超过 0.5% 的时刻 + 保持窗。"""
    last_bad = 0.0
    for t, p in series:
        if abs(p - 1.0) > TOL:
            last_bad = t
    if hold is None:
        hold = hold_window(last_bad + HOLD)
    return min(last_bad + hold, T_LIMIT)


def settle_clamped(series, hold=None):
    """落定时刻是否被 T_LIMIT 截断——截断时「已稳定」是假话，调用方必须说明。"""
    last_bad = 0.0
    for t, p in series:
        if abs(p - 1.0) > TOL:
            last_bad = t
    if hold is None:
        hold = hold_window(last_bad + HOLD)
    return (last_bad + hold) > T_LIMIT


def sample(series, n):
    """等距取样；末点钉死为 1。下钳 0，上不钳（过冲要留着）。"""
    end = settle_time(series)
    picks = []
    for i in range(n):
        t = end * i / (n - 1)
        best = min(series, key=lambda s: abs(s[0] - t))
        picks.append(max(0.0, min(1.6, best[1])))
    picks[0], picks[-1] = 0.0, 1.0
    return picks, end


def damping_ratio(k, c):
    return c / (2.0 * math.sqrt(k)) if k > 0 else 0.0


def overshoot(ratio):
    if ratio >= 1.0:
        return 0.0
    return math.exp(-math.pi * ratio / math.sqrt(1 - ratio * ratio))


def ratio_from_overshoot(pct):
    """由目标过冲反解阻尼比（与 overshoot 互逆）；pct=0 → ζ=1（临界阻尼）。"""
    if pct <= 0:
        return 1.0
    o = pct / 100.0
    ln_o = math.log(o)
    # O = exp(-πζ/√(1-ζ²)) ⇒ ζ = |lnO| / √(π² + ln²O)
    return abs(ln_o) / math.sqrt(math.pi ** 2 + ln_o ** 2)


def solve_for_target(ms, overshoot_pct):
    """按目标时长（稳定到 0.5%）与目标过冲反解 k、c。

    ⛔ 不用 e^{-ζωt}=0.005 的解析式——那是包络近似，实测常偏 30%以上（临界阻尼差更多）。
    这里直接二分 ω，让 simulate 量出来的稳定时刻落在目标上，误差 ≤ 2%。
    """
    ratio = ratio_from_overshoot(overshoot_pct)
    target = ms / 1000.0
    hold = hold_window(target)
    lo, hi = 3.0, 300.0
    for _ in range(40):
        mid = (lo + hi) / 2.0
        got = settle_time(simulate(mid ** 2, 2 * ratio * mid), hold)
        if got > target:
            lo = mid
        else:
            hi = mid
    omega = (lo + hi) / 2.0
    return int(round(omega ** 2)), int(round(2 * ratio * omega))


def approx_bezier(k, c):
    """退路：不支持 linear() 的浏览器。按阻尼比推过冲，给一组能用的控制点。"""
    os_pct = overshoot(damping_ratio(k, c))
    y2 = round(1.0 + os_pct * 0.6, 3)
    return "cubic-bezier(0.34, %s, 0.64, 1)" % y2


def auto_samples(k, end, n):
    """过冲明显的弹簧每秒要更多点，否则 linear() 折线会把回弹抹成台阶。

    上限钉 30：与 motion.md「取 20–30 个采样点写进 linear()」同一口径，⛔ 自行加码成 60。
    """
    omega = math.sqrt(k)
    cycles = end / (2 * math.pi / omega) if omega > 0 else 0
    return max(n, min(30, int(cycles * 14) + 6))


def build(k, c, n):
    series = simulate(k, c)
    end = settle_time(series)
    clamped = settle_clamped(series)
    picks, end = sample(series, auto_samples(k, end, n))
    curve = "linear(%s)" % ", ".join("%.3f" % p for p in picks)
    ratio = damping_ratio(k, c)
    return {
        "k": k, "c": c,
        "seconds": round(end, 3),
        "damping_ratio": round(ratio, 3),
        "overshoot_pct": round(overshoot(ratio) * 100, 1),
        "samples": n,
        "clamped": clamped,
        "linear": curve,
        "fallback": approx_bezier(k, c),
    }


def duration_line(row):
    if row.get("clamped"):
        return ("%.2fs（⚠️ 未在 %.1fs 内稳定：曲线被截断，⛔ 当稳定时长用；"
                "换更大的阻尼或更低的刚度再取一次）" % (row["seconds"], T_LIMIT))
    return "%.2fs（位移稳定在终点 0.5%% 以内）" % row["seconds"]


def fmt(row, name=None):
    head = ("%s  k=%d c=%d" % (name, row["k"], row["c"])) if name else ("k=%d c=%d" % (row["k"], row["c"]))
    return (
        "%s\n"
        "  时长      %s\n"
        "  阻尼比    ζ=%.3f，过冲 %.1f%%\n"
        "  曲线      %s;\n"
        "  退路      transition-timing-function: %s;\n"
        % (head, duration_line(row), row["damping_ratio"], row["overshoot_pct"],
           row["linear"], row["fallback"])
    )


def main():
    ap = argparse.ArgumentParser(
        prog="spring_to_linear.py",
        description="弹簧刚度/阻尼 → CSS linear() 缓动曲线（离线、确定性）")
    ap.add_argument("-k", "--stiffness", type=int, help="刚度，如 300")
    ap.add_argument("-c", "--damping", type=int, help="阻尼，如 20")
    ap.add_argument("--preset", choices=sorted(PRESETS), help="手感预设（见 motion.md 手感表）")
    ap.add_argument("--presets", action="store_true", help="列出全部预设")
    ap.add_argument("--target", type=int, help="目标时长（毫秒，按 0.5%% 稳定口径反解 k/c）")
    ap.add_argument("--overshoot", type=float, default=0.0, help="配合 --target：目标过冲百分比，默认 0")
    ap.add_argument("--samples", type=int, default=24, help="采样点数，20–30 为宜（默认 24）")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    args = ap.parse_args()

    if args.presets:
        rows = [{"name": n, **build(k, c, args.samples)} for n, (k, c) in PRESETS.items()]
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print("六个手感预设（k / c → 曲线）：\n")
            for r in rows:
                print(fmt(r, r["name"]))
        return 0

    if args.target is not None:
        if not 40 <= args.target <= 1200:
            print("✗ --target 取 40–1200 毫秒", file=sys.stderr)
            return 2
        k, c = solve_for_target(args.target, args.overshoot)
        label = "反解 %dms / 过冲 %.0f%%" % (args.target, args.overshoot)
    elif args.preset:
        k, c = PRESETS[args.preset]
        label = args.preset
    elif args.stiffness is not None and args.damping is not None:
        k, c = args.stiffness, args.damping
        label = None
    else:
        ap.print_usage(sys.stderr)
        print("✗ 三选一：--preset / -k 与 -c / --target", file=sys.stderr)
        return 2

    if k <= 0 or c <= 0:
        print("✗ 刚度与阻尼都必须是正数", file=sys.stderr)
        return 2
    if not 4 <= args.samples <= 60:
        print("✗ 采样点数取 4–60；界面用 20–30", file=sys.stderr)
        return 2

    row = build(k, c, args.samples)
    if args.json:
        print(json.dumps(row, ensure_ascii=False, indent=2))
        return 0

    print(fmt(row, label))
    if row["overshoot_pct"] > 20:
        print("  ⚠️ 过冲 >20%%：只能用在徽章、勾选这类小物件；整页、面板会晃（motion.md 手感节）")
    if args.target is None and row["seconds"] * 1000 > 400:
        print("  ⚠️ 落定 %.0fms 已超出「界面元素一律 <300ms」——这是材质手感，不是可直接用的时长；"
              "要按时长走就来 --target" % (row["seconds"] * 1000))
    return 0


if __name__ == "__main__":
    sys.exit(main())
