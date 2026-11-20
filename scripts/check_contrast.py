#!/usr/bin/env python3
"""对比度门：按 WCAG 2.x 检查前景/背景配对，并报告感知亮度。

判据来源：Refactoring UI §5.6（正文 4.5:1、大字 3:1）与 §5.4.1（感知亮度）。
算法为标准 WCAG 相对亮度；感知亮度只用于解释「同一明度下黄色为什么比蓝色亮」。
纯标准库，不联网。

  python3 check_contrast.py --pair '#ffffff' '#bd4d28'
  python3 check_contrast.py --pair '#6b7280' '#ffffff' --size large
  python3 check_contrast.py --matrix pairs.json
  python3 check_contrast.py --brightness '#eab308' '#bd4d28'

matrix 文件形如 {"pairs":[{"fg":"#111","bg":"#fff","name":"正文","size":"normal"}]}。
任一对不合格时退出码 1，可直接当交付门。
"""
from __future__ import annotations

import argparse
import json
import math
import sys

AA_NORMAL, AA_LARGE = 4.5, 3.0


def hex_to_rgb(s: str) -> tuple[int, int, int]:
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError("不是合法十六进制色值：%s" % s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    def lin(c: int) -> float:
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: str, b: str) -> float:
    la, lb = relative_luminance(hex_to_rgb(a)), relative_luminance(hex_to_rgb(b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def perceived_brightness(c: str) -> float:
    r, g, b = hex_to_rgb(c)
    return math.sqrt(0.299 * r * r + 0.587 * g * g + 0.114 * b * b) / 255


def verdict(ratio: float, size: str) -> tuple[bool, str]:
    need = AA_LARGE if size == "large" else AA_NORMAL
    ok = ratio >= need
    return ok, "%s  %.2f:1  (需 %s:1，%s)" % (
        "PASS" if ok else "FAIL", ratio, need, "大字" if size == "large" else "正文")


def advise(fg: str, bg: str, size: str) -> list[str]:
    tips = []
    if perceived_brightness(bg) < 0.45:
        tips.append("深底上换成同色浅染上的深色字，别在深色块上直接排白字")
        tips.append("把文字色相朝青/品红/黄旋转 20-30 度换对比，不靠提亮到白")
    else:
        tips.append("前景压深一档，或沿色阶再往下走一到两级")
    if size == "normal":
        tips.append("这行字如果 ≥18px/14pt，只需 3:1，可用 --size large 复检")
    return tips


def check_matrix(path: str, size: str) -> int:
    data = json.load(open(path, encoding="utf-8"))
    pairs = data.get("pairs")
    if not pairs:
        print('%s：没有 "pairs" 数组。要把界面上真实出现的组合都声明出来。' % path,
              file=sys.stderr)
        return 2
    failures = 0
    width = max((len(p.get("name", "")) for p in pairs), default=4)
    for p in pairs:
        s = p.get("size", size)
        r = contrast_ratio(p["fg"], p["bg"])
        ok, line = verdict(r, s)
        failures += not ok
        print("%-*s  %s on %s  %s" % (width, p.get("name", ""), p["fg"], p["bg"], line))
        if not ok:
            for t in advise(p["fg"], p["bg"], s):
                print("%-*s    -> %s" % (width, "", t))
    print("\n%d/%d 合格" % (len(pairs) - failures, len(pairs)))
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pair", nargs=2, metavar=("FG", "BG"), help="检查一对颜色")
    ap.add_argument("--matrix", metavar="PAIRS.JSON", help="检查声明的配对表")
    ap.add_argument("--brightness", nargs="+", metavar="COLOR", help="报告感知亮度")
    ap.add_argument("--size", choices=("normal", "large"), default="normal",
                    help="normal = 18px 以下（4.5:1）；large = 3:1")
    a = ap.parse_args()

    if a.brightness:
        for c in a.brightness:
            print("%s  感知亮度 %.3f  WCAG 亮度 %.3f" % (
                c, perceived_brightness(c), relative_luminance(hex_to_rgb(c))))
        return 0

    if a.pair:
        fg, bg = a.pair
        ok, line = verdict(contrast_ratio(fg, bg), a.size)
        print("%s on %s   %s" % (fg, bg, line))
        if not ok:
            for t in advise(fg, bg, a.size):
                print("  -> %s" % t)
        return 0 if ok else 1

    if a.matrix:
        return check_matrix(a.matrix, a.size)

    ap.error("需要 --pair、--matrix 或 --brightness 之一")


if __name__ == "__main__":
    raise SystemExit(main())
