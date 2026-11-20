#!/usr/bin/env python3
"""令牌导出：按 Refactoring UI ch.5 的算法生成色阶，落成 tokens.css / @theme / DESIGN.md。

算法（⛔ 不手调 hex，手调必漂）：
  §5.3.3 base(500) -> 两端(900/100) -> 二分(700/300) -> 再二分(800/600/400/200)
  §5.4   饱和度随明度离 50% 变远而抬高，让彩度看起来稳定
  §5.4.2 色相朝亮端（60/180/300）或暗端（0/120/240）旋转：单步偏移 ≤--cap（默认 20°），
         整条色阶两端累计 ≤--cap-total（默认 30°）。两个方向各自封顶会相加，必须另设总预算。
  §5.5.1 灰阶带温度，两端各做补偿
动效令牌取 emil-design-eng（MIT）的四条缓动与时长档。

  python3 emit_tokens.py --base '#0f7b6c' --name brand --out tokens/
  python3 emit_tokens.py --grey --temperature cool --out tokens/
  python3 emit_tokens.py --base '#eab308' --json

纯标准库，不联网。
"""
from __future__ import annotations

import argparse
import colorsys
import json
import os
import re
import sys

BRIGHT_HUES = (60.0, 180.0, 300.0)
DARK_HUES = (0.0, 120.0, 240.0)


def hex_to_hsl(s: str) -> tuple[float, float, float]:
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError("不是合法十六进制色值：%s" % s)
    r, g, b = (int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, sat = colorsys.rgb_to_hls(r, g, b)
    return h * 360, sat * 100, l * 100


def hsl_to_hex(h: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l / 100, s / 100)
    return "#%02x%02x%02x" % tuple(round(c * 255) for c in (r, g, b))


def parse_color(s: str) -> tuple[float, float, float]:
    s = s.strip()
    m = re.match(r"hsl\(\s*([\d.]+)\s*[, ]\s*([\d.]+)%?\s*[, ]\s*([\d.]+)%?\s*\)", s, re.I)
    if m:
        return float(m.group(1)), float(m.group(2)), float(m.group(3))
    return hex_to_hsl(s)


def headroom(l: float) -> float:
    return max(1e-6, 1.0 - abs(2.0 * (l / 100.0) - 1.0))


def compensate(s0: float, l0: float, lt: float, strength: float) -> float:
    if s0 <= 0:
        return 0.0
    return min(100.0, s0 * ((headroom(l0) / headroom(lt)) ** strength))


def signed_delta(frm: float, to: float) -> float:
    return (to - frm + 180.0) % 360.0 - 180.0


def hue_offset(h0: float, l0: float, lt: float, cap: float, prefer: str) -> float:
    """单个 stop 相对 500 的自然色相偏移（有符号，未封顶）。

    封顶不在这里做：逐级夹会把端部几级压成同一偏移（实测蓝 100/200 同为 -20°），
    转出来的色相既不递增也可能反向。交给 build_ramp 按侧整条等比压。
    """
    if lt == l0:
        return 0.0
    lighten = lt > l0
    targets = BRIGHT_HUES if lighten else DARK_HUES
    if prefer in ("warm", "cool"):
        want = 1.0 if prefer == "warm" else -1.0
        nearest = sorted(targets, key=lambda t: (abs(signed_delta(h0, t)),
                                                 -want * signed_delta(h0, t)))[0]
    else:
        nearest = min(targets, key=lambda t: abs(signed_delta(h0, t)))
    span = (100.0 - l0) if lighten else l0
    if span <= 0:
        return 0.0
    progress = min(1.0, abs(lt - l0) / span)
    return signed_delta(h0, nearest) * progress


def rotate_hue(h0: float, l0: float, lt: float, cap: float, prefer: str) -> float:
    return h0 + hue_offset(h0, l0, lt, cap, prefer)


def ramp_offsets(h0, l0, L, cap, prefer, cap_total=30.0):
    """九级各自相对 500 的色相偏移（有符号），含两道闸。

    ① 单步帽 cap：同侧超限时**整侧等比压**，⛔ 不逐级硬夹——硬夹会把端部几级
       压成同一个偏移（实测蓝 100/200 都顶到 -20°），色相既不递增、也可能反向。
    ② 总预算 cap_total:两端跨度超限时整条等比压。两道都用比例，跟级序无关。
    """
    offsets = {s: (0.0 if s == 500 else hue_offset(h0, l0, L[s], cap, prefer)) for s in L}
    for sign in (1, -1):
        side = [abs(o) for o in offsets.values() if o * sign > 0]
        if side and max(side) > cap:
            k_side = cap / max(side)
            offsets = {s: (o * k_side if o * sign > 0 else o) for s, o in offsets.items()}
    spread = max(offsets.values()) - min(offsets.values())
    if cap_total and spread > cap_total:
        k = cap_total / spread
        offsets = {s: o * k for s, o in offsets.items()}
        print("提示：两端累计色相漂移 %.1f° 超过 --cap-total %.0f°，已等比压到 %.1f°"
              % (spread, cap_total, cap_total), file=sys.stderr)
    return offsets


def build_ramp(base, lightest, darkest, strength, cap, extended, prefer, cap_total=30.0):
    h0, s0, l0 = base
    if not (darkest < l0 < lightest):
        raise SystemExit("基色明度 %.0f%% 必须落在最暗 %.0f%% 与最亮 %.0f%% 之间"
                         % (l0, darkest, lightest))
    L = {900: darkest, 500: l0, 100: lightest}
    L[700] = (L[900] + L[500]) / 2
    L[300] = (L[500] + L[100]) / 2
    L[800] = (L[900] + L[700]) / 2
    L[600] = (L[700] + L[500]) / 2
    L[400] = (L[500] + L[300]) / 2
    L[200] = (L[300] + L[100]) / 2
    if extended:
        L[50] = lightest + (100.0 - lightest) * 0.55
        L[950] = darkest * 0.55
    offsets = ramp_offsets(h0, l0, L, cap, prefer, cap_total)
    out = {}
    for stop in sorted(L):
        lt = L[stop]
        h = h0 + offsets[stop]
        s = s0 if stop == 500 else compensate(s0, l0, lt, strength)
        out[stop] = hsl_to_hex(h, s, lt)
    return out


MOTION = {
    "ease-out": "cubic-bezier(0.23, 1, 0.32, 1)",
    "ease-in-out": "cubic-bezier(0.77, 0, 0.175, 1)",
    "ease-drawer": "cubic-bezier(0.32, 0.72, 0, 1)",
}


def write_css(name: str, ramp: dict, out: str) -> str:
    lines = [":root {"]
    for stop, hexv in ramp.items():
        lines.append("  --color-%s-%s: %s;" % (name, stop, hexv))
    for k, v in MOTION.items():
        lines.append("  --%s: %s;" % (k, v))
    for k, v in (("duration-press", "160ms"), ("duration-tooltip", "200ms"),
                 ("duration-popover", "250ms"), ("duration-panel", "400ms"),
                 ("duration-page", "500ms")):
        lines.append("  --%s: %s;" % (k, v))
    lines.append("}")
    p = os.path.join(out, "tokens.css")
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return p


def write_theme(name: str, ramp: dict, out: str) -> str:
    lines = ["/* Tailwind v4：v3 请改成 tailwind.config.js 的 theme.extend */", "@theme {"]
    for stop, hexv in ramp.items():
        lines.append("  --color-%s-%s: %s;" % (name, stop, hexv))
    lines.append("}")
    p = os.path.join(out, "theme.css")
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return p


def write_design_md(name: str, ramp: dict, base_hex: str, out: str) -> str:
    rows = ["| 级 | 色值 | 用途 |", "|---|---|---|"]
    uses = {50: "页面底/浅染", 100: "浅染面、hover 底", 200: "分隔、禁用底",
            300: "边框、弱描边", 400: "占位文字", 500: "基色（品牌原色）",
            600: "主操作填充", 700: "主操作按下", 800: "深色面", 900: "正文/标题",
            950: "最深面"}
    for stop, hexv in ramp.items():
        rows.append("| %s | `%s` | %s |" % (stop, hexv, uses.get(stop, "按需")))
    body = "\n".join([
        "# DESIGN（%s）" % name,
        "",
        "> 由 scripts/emit_tokens.py 生成，基色 `%s`。" % base_hex,
        "> 改色请改基色重跑，⛔ 不手调色值（调过的阶会彼此漂）。",
        "",
        "## 1 配色",
        "",
        "\n".join(rows),
        "",
        "## 2 字体",
        "",
        "- 正文字体：待填（项目实际字体，⛔ 不默认 Inter）",
        "- 展示字体：待填（中英文各自的回退栈）",
        "- 两档字重：400/500 与 600/700；UI 文字不低于 400",
        "",
        "## 3 字号层级",
        "",
        "| 角色 | 字号 | 行高 | 备注 |",
        "|---|---|---|---|",
        "| display | 40-56px | 1.05-1.15 | 每页至多一处 |",
        "| h1 | 28-36px | 1.2-1.3 | 中文按 1.2-1.35 校 |",
        "| h2 | 20-24px | 1.3 | |",
        "| body | 14-16px | 1.6-1.75 | 阅读型 16-18px |",
        "| caption | 12-13px | 1.4 | 不作正文 |",
        "",
        "相邻级差 ≥25%，⛔ 不出现 15/16/17 这种挤在一起的级。",
        "",
        "## 4 圆角与边框",
        "",
        "- 圆角：4 / 8 / 12 / 16（同心：内 = 外 - 内边距）",
        "- 边框：1px 常规、0.5px 分隔；同类线只出现一次",
        "",
        "## 5 间距与阴影",
        "",
        "- 间距刻度：4 / 8 / 12 / 16 / 24 / 32 / 48 / 64",
        "- 阴影：`0 1px 2px rgba(0,0,0,.06)` / `0 8px 24px rgba(0,0,0,.12)`，都带偏移与柔化",
        "- 高度分层最多 5 级，靠明度差 1-3% 分层，不靠加描边",
        "",
        "## 6 三级解析顺序",
        "",
        "1. 项目已有令牌（Step 0 读到的）",
        "2. 本次由本脚本生成并写进项目的令牌",
        "3. 回落书的默认刻度，并**在交付说明里写明降级**",
        "",
        "## 7 动效",
        "",
        "```css",
    ] + ["--%s: %s;" % (k, v) for k, v in MOTION.items()] + [
        "```",
        "",
        "按压 100-160ms、提示 125-200ms、气泡 150-250ms、面板 200-500ms；UI 元素一律 <300ms，整页转场除外。",
        "",
    ])
    p = os.path.join(out, "DESIGN.md")
    open(p, "w", encoding="utf-8").write(body)
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", help="品牌基色，#rrggbb 或 hsl(h,s%%,l%%)；用项目真色")
    ap.add_argument("--grey", action="store_true", help="生成中性色阶")
    ap.add_argument("--temperature", choices=("cool", "warm", "neutral"), default="cool")
    ap.add_argument("--grey-saturation", type=float, default=12.0)
    ap.add_argument("--lightest", type=float, default=96.0)
    ap.add_argument("--darkest", type=float, default=21.0)
    ap.add_argument("--strength", type=float, default=0.55)
    ap.add_argument("--cap", type=float, default=20.0,
                    help="单个 stop 相对 500 的色相偏移上限（度）")
    ap.add_argument("--cap-total", type=float, default=30.0,
                    help="整条色阶 100↔900 两端累计色相漂移上限（度）；0 表示不限制")
    ap.add_argument("--toward", choices=("auto", "warm", "cool"), default="auto")
    ap.add_argument("--extended", action="store_true", help="加 50/950 两级")
    ap.add_argument("--name", default=None, help="色阶名（默认 brand 或 neutral）")
    ap.add_argument("--out", default=".", help="输出目录")
    ap.add_argument("--json", action="store_true", help="只打印 JSON，不写文件")
    a = ap.parse_args()

    if a.cap > 30:
        print("警告：色相旋转 >30 度会读成另一个颜色（§5.4.2）", file=sys.stderr)

    if a.grey:
        hue = {"cool": 220.0, "warm": 35.0, "neutral": 0.0}[a.temperature]
        base = (hue, 0.0 if a.temperature == "neutral" else a.grey_saturation, 50.0)
        name = a.name or "neutral"
        lightest, darkest = (98.0 if a.lightest == 96.0 else a.lightest,
                             17.0 if a.darkest == 21.0 else a.darkest)
    elif a.base:
        base = parse_color(a.base)
        name = a.name or "brand"
        lightest, darkest = a.lightest, a.darkest
    else:
        ap.error("需要 --base 或 --grey")

    ramp = build_ramp(base, lightest, darkest, a.strength, a.cap, a.extended, a.toward, a.cap_total)
    payload = {name: {str(k): v for k, v in ramp.items()}}

    if a.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    os.makedirs(a.out, exist_ok=True)
    base_hex = hsl_to_hex(*base)
    p1 = write_css(name, ramp, a.out)
    p2 = write_theme(name, ramp, a.out)
    p3 = write_design_md(name, ramp, base_hex, a.out)
    p4 = os.path.join(a.out, "tokens.json")
    open(p4, "w", encoding="utf-8").write(json.dumps(payload, indent=2) + "\n")

    # 目标态复读：写成功不等于落对了（禅院塔 §2.35）。四个文件各自回收一次、查出关键行。
    expect = {p1: "--color-%s-500:" % name, p2: "@theme",
              p3: "DESIGN（%s）" % name, p4: "\"500\""}
    for path, token in expect.items():
        try:
            with open(path, encoding="utf-8") as fh:
                got = fh.read()
        except OSError as e:
            print("✗ 回读失败 %s：%s" % (path, e), file=sys.stderr)
            return 2
        if token not in got or len(got.strip()) < 20:
            print("✗ 回读内容不对 %s：缺 %r 或过短" % (path, token), file=sys.stderr)
            return 2

    for stop, hexv in ramp.items():
        print("%-4s %s%s" % (stop, hexv, "  <- 基色" if stop == 500 else ""))
    print("\n写出并回读通过：%s / %s / %s / %s" % (p1, p2, p3, p4))
    print("下一步：python3 scripts/check_contrast.py --pair '<正文色>' '<底色>'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
