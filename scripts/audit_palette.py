#!/usr/bin/env python3
"""色板级审计：判「一整套色板在一起好不好用」，不是判一对前后景。

与 check_contrast.py 的分工（⛔ 别混着用）：
  check_contrast.py  一对前景/背景够不够（文字门，4.5 / 3.0）
  audit_palette.py   多个角色色之间的相 distance 与填充边界（成套门）

两类作用域，两套阈值，互不引用：
  · 色阶内部（同一族 100↔900）：两端累计色相漂移 ≤30°（--cap-total 同值）；这是旋转补偿预算。
  · 角色之间（两个独立强调色/填充色）：ΔL* ≥10（⛔ 别低于，转灰会并级）、
    色相夹角不落 15–40°（落进去既不像同族也不像对比）。

用法：
  python3 audit_palette.py --tokens tokens/tokens.css
  python3 audit_palette.py --palette p.json
  python3 audit_palette.py --palette p.json --json

palette json 形如：
{"background":"#ffffff","text":{"primary":"#111111","secondary":"#555555"},
 "fills":["#2563eb","#f59e0b"],"accents":["#2563eb","#06b6d4"],
 "waivers":[{"pair":["accent1","fill1"],"basis":"面积 12% vs 2%、形状冗余（✓ 图标）、永不同框"}]}

waivers 是暧昧带的降级路径，不是免死金牌：一对落在 15–40° 且登记了依据，才降级放行；
依据须 ≥20 字且至少盖住「面积／形状／位置」三轴中的两轴，只写「面积大」不算；
登记了却没对上任何暧昧对，反过来报「失效豁免」。

纯标准库，不联网；有硬失败时退出码 1，可直接当交付门。
"""
from __future__ import annotations

import argparse
import colorsys
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_contrast import contrast_ratio, hex_to_rgb  # 复用同一套色彩数学

# Windows 控制台默认 cp1252，✓/⚠/中文会在 print 时抛 UnicodeEncodeError；
# 统一按 UTF-8 输出，编不出的字符降级成 ?，别让编码把业务判断顶掉。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


AA_NORMAL = 4.5
NON_TEXT = 3.0
LSTAR_MIN = 10.0        # 两个角色色之间最小的 CIE L* 差
HUE_BAND = (15.0, 40.0)  # 暧昧带下界/上界（只判角色对，⛔ 不用于色阶内部）
CAP_TOTAL = 30.0        # 色阶两端累计色相漂移上限，与 emit_tokens --cap-total 同值

# 降级路径：暧昧带在「功能色」场景下不可满足（红橙天生 20–40°），凭色相救不了，
# 只能换轴。认哪几条轴、要几轴同时成立，是这条判据可证伪的部分：
#   面积（大小悬殊才不至于并读）、形状（图标/纹样/形状冗余）、位置（不同框/不同屏）。
AXIS_WORDS = {"area": ("面积", "占比", "大小"),
              "shape": ("形状", "图标", "纹样", "图形"),
              "position": ("位置", "不同框", "同框", "不同屏", "不相邻")}
AXES_MIN = 2            # 至少两轴同时成立，单轴（只写「面积大」）不算
BASIS_MIN = 20          # 依据太短等于没写


def lstar(hexv: str) -> float:
    r, g, b = hex_to_rgb(hexv)
    c = [x / 255.0 for x in (r, g, b)]
    y = 0.2126 * (c[0] / 12.92 if c[0] <= 0.03928 else ((c[0] + 0.055) / 1.055) ** 2.4) \
        + 0.7152 * (c[1] / 12.92 if c[1] <= 0.03928 else ((c[1] + 0.055) / 1.055) ** 2.4) \
        + 0.0722 * (c[2] / 12.92 if c[2] <= 0.03928 else ((c[2] + 0.055) / 1.055) ** 2.4)
    f = y ** (1 / 3) if y > 0.008856 else 7.787 * y + 16 / 116
    return 116 * f - 16


def hue(hexv: str) -> float:
    r, g, b = (x / 255.0 for x in hex_to_rgb(hexv))
    h, _, _ = colorsys.rgb_to_hsv(r, g, b)
    return h * 360.0


def hue_gap(a: str, b: str) -> float:
    d = abs(hue(a) - hue(b)) % 360.0
    return min(d, 360.0 - d)


def signed_hue_gap(a: str, b: str) -> float:
    d = (hue(a) - hue(b)) % 360.0
    return d if d <= 180 else d - 360


def load_tokens(path: str) -> dict:
    src = open(path, encoding="utf-8").read()
    out = {}
    for name, stop, hexv in re.findall(
            r"--color-([a-z0-9-]+?)-(\d{2,3})\s*:\s*(#[0-9a-fA-F]{6})", src):
        out.setdefault(name, {})[int(stop)] = hexv
    return out


def audit_family(name: str, stops: dict, against: list[str]) -> list[dict]:
    issues = []
    ks = sorted(stops)
    if len(ks) < 2:
        return issues
    lo, hi = stops[ks[0]], stops[ks[-1]]
    drift = abs(hue_gap(lo, hi))
    if drift > CAP_TOTAL:
        issues.append(dict(item="%s 色阶累计漂移" % name, value=round(drift, 1),
                           level="FAIL",
                           msg="%s: %s→%s 色相累计漂移 %.1f° > %.0f°，两端会读成两个色族"
                               % (name, lo, hi, drift, CAP_TOTAL)))
    # 明度必须随 stop 单调下降（100 最亮 → 900 最暗）
    ls = [lstar(stops[k]) for k in ks]
    if any(ls[i] <= ls[i + 1] for i in range(len(ls) - 1)):
        bad = ["%s(% .0f)" % (ks[i], ls[i]) for i in range(len(ls) - 1) if ls[i] <= ls[i + 1]]
        issues.append(dict(item="%s 明度单调" % name, value=0, level="FAIL",
                           msg="%s: 明度没有随级号单调下降（%s），中间级会跳" % (name, "、".join(bad))))
    # 色相不许「停在原地」：同一侧既然转了，就必须逐级递进，⛔ 两级同色相
    # （旧实现逐级硬夹，蓝 100/200 都顶到 -20°，转出来两级看起来是同一档）
    mid = min(ks, key=lambda k: abs(k - 500))
    for half in ([k for k in ks if k < mid], [k for k in ks if k > mid]):
        if len(half) < 2:
            continue
        order = sorted(half, key=lambda k: abs(k - mid))
        if not any(hue_gap(stops[k], stops[mid]) >= 1.0 for k in order):
            continue                                          # 这一侧本来就不转，放过
        dup = [order[i] for i in range(1, len(order))
               if hue_gap(stops[order[i]], stops[order[i - 1]]) < 1.0]
        if dup:
            issues.append(dict(item="%s 色相停级" % name, value=0, level="FAIL",
                               msg="%s: 相邻级色相差 <1°（%s），色阶在某处停住，"
                                   "两级看起来是同一个色" % (name, "、".join(str(k) for k in dup))))
    # 填充/描边用法下，每级对给定底的最低对比
    for bg in against:
        worst = min(((contrast_ratio(stops[k], bg), k) for k in ks), key=lambda x: x[0])
        if worst[0] < NON_TEXT:
            issues.append(dict(item="%s-%s 对底" % (name, worst[1]), value=round(worst[0], 2),
                               level="WARN",
                               msg="%s-%s %s 对底 %s 仅 %.2f:1（做填充/描边需 %.1f）"
                                   % (name, worst[1], stops[worst[1]], bg, worst[0], NON_TEXT)))
    return issues


def waiver_axes(basis: str) -> int:
    """数这条依据实际claim了哪几轴。写全三轴的才算数，只写「面积大」不算。"""
    hits = set()
    for axis, words in AXIS_WORDS.items():
        if any(w in basis for w in words):
            hits.add(axis)
    return len(hits)


def pair_key(na: str, nb: str) -> frozenset:
    return frozenset((na.lower(), nb.lower()))


def audit_roles(p: dict) -> list[dict]:
    issues = []
    bg = p.get("background", "#ffffff")
    raw_waivers = p.get("waivers") or []
    waivers = {}
    for w in raw_waivers:
        pair = w.get("pair") or []
        if len(pair) != 2:
            continue
        waivers[pair_key(pair[0], pair[1])] = w.get("basis") or ""
    seen_pairs = set()
    waived = []
    for role, hexv in (p.get("text") or {}).items():
        r = contrast_ratio(hexv, bg)
        if r < AA_NORMAL:
            issues.append(dict(item="text.%s" % role, value=round(r, 2), level="FAIL",
                               msg="文字 %s %s 压底 %s 仅 %.2f:1 < %.1f" % (role, hexv, bg, r, AA_NORMAL)))
    for i, hexv in enumerate(p.get("fills") or []):
        r = contrast_ratio(hexv, bg)
        if r < NON_TEXT:
            issues.append(dict(item="fills[%d]" % i, value=round(r, 2), level="WARN",
                               msg="填充 %s 对底 %s 仅 %.2f:1（边界会糊，需 %.1f）" % (hexv, bg, r, NON_TEXT)))
    accents = [("accent%d" % (i + 1), h) for i, h in enumerate(p.get("accents") or [])]
    accents += [("fill%d" % (i + 1), h) for i, h in enumerate(p.get("fills") or [])]
    seen, uniq = set(), []
    for label, h in accents:                      # 同一个色值在两类里都点名时只留一次
        key = h.lower()
        if key not in seen:
            seen.add(key)
            uniq.append((label, h))
    accents = uniq
    for i in range(len(accents)):
        for j in range(i + 1, len(accents)):
            (na, a), (nb, b) = accents[i], accents[j]
            dl = abs(lstar(a) - lstar(b))
            if dl < LSTAR_MIN:
                issues.append(dict(item="%s↔%s ΔL*" % (na, nb), value=round(dl, 1), level="WARN",
                                   msg="%s %s ↔ %s %s 明度只差 %.1f（< %.0f）：转灰/黑白打印会并级"
                                       % (na, a, nb, b, dl, LSTAR_MIN)))
            dh = hue_gap(a, b)
            if HUE_BAND[0] <= dh <= HUE_BAND[1]:
                k = pair_key(na, nb)
                seen_pairs.add(k)
                basis = waivers.get(k)
                if basis is None:
                    issues.append(dict(item="%s↔%s ΔH" % (na, nb), value=round(dh, 1), level="WARN",
                                       msg="%s %s ↔ %s %s 色相夹角 %.1f° 落在 %.0f–%.0f° 暧昧带："
                                           "既不像同族也不像对比，推到 ≥60° 或 ≤10°；"
                                           "功能色（状态色）救不了时登记 waivers 换轴"
                                           % (na, a, nb, b, dh, HUE_BAND[0], HUE_BAND[1])))
                elif len(basis) < BASIS_MIN or waiver_axes(basis) < AXES_MIN:
                    issues.append(dict(item="%s↔%s ΔH 豁免不合格" % (na, nb), value=round(dh, 1),
                                       level="WARN",
                                       msg="%s↔%s 登记了豁免，但依据%s（须 ≥%d 字、且至少 %d 轴：面积／形状／位置）"
                                           % (na, nb,
                                              "太短" if len(basis) < BASIS_MIN else "只盖住 %d 轴" % waiver_axes(basis),
                                              BASIS_MIN, AXES_MIN)))
                else:
                    waived.append((na, nb, round(dh, 1), basis))
    for na, nb, dh, basis in waived:
        issues.append(dict(item="%s↔%s ΔH 豁免" % (na, nb), value=dh, level="OK",
                           msg="%s↔%s 色相夹角 %.1f° 仍在暧昧带，按登记换轴放行：%s"
                               % (na, nb, dh, basis)))
    for (na, nb), basis in waivers.items():
        if pair_key(na, nb) not in seen_pairs:
            issues.append(dict(item="失效豁免", value=0, level="WARN",
                               msg="waivers 里登记的一对被判角色不在暧昧带（或已改名）：%s"
                                   % "/".join(sorted((na, nb)))))
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", help="emit_tokens.py 产出的 tokens.css")
    ap.add_argument("--palette", help="角色色板 json")
    ap.add_argument("--against", default="",
                    help="可选：逐级比较的底色，逗号分隔。只填真实会相邻的底（如 '#ffffff'）；"
                         "100/900 本来就是浅染/深压面，别拿它去比纯白纯黑")
    ap.add_argument("--json", action="store_true", help="末行输出机器可读 JSON")
    a = ap.parse_args()
    if not a.tokens and not a.palette:
        ap.error("需要 --tokens 或 --palette")

    issues = []
    if a.tokens:
        fams = load_tokens(a.tokens)
        if not fams:
            print("FAIL 没从 %s 里读到 --color-<name>-<stop> 令牌" % a.tokens)
            return 1
        against = [s.strip() for s in a.against.split(",") if s.strip()]
        for name, stops in fams.items():
            issues += audit_family(name, stops, against)
    if a.palette:
        issues += audit_roles(json.load(open(a.palette, encoding="utf-8")))

    fails = [i for i in issues if i["level"] == "FAIL"]
    warns = [i for i in issues if i["level"] == "WARN"]
    oks = [i for i in issues if i["level"] == "OK"]
    for i in issues:
        print("%s %s：%s" % ({"FAIL": "✗", "WARN": "⚠", "OK": "✓"}[i["level"]], i["item"], i["msg"]))
    tail = "（另有 %d 条换轴豁免放行）" % len(oks) if oks else ""
    print("%s 色板审计：%d 硬失败 / %d 提醒%s" % ("✗" if fails else "✓", len(fails), len(warns), tail))
    if a.json:
        print(json.dumps({"ok": not fails, "fail": len(fails), "warn": len(warns),
                          "waived": len(oks), "issues": issues}, ensure_ascii=False))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
