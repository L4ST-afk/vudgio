#!/usr/bin/env python3
"""动效令牌体检：组件里的缓动/时长是否都走令牌，而不是各自现场挑。

只管一件事——**参数层有没有被绕过**。审美判断不在本脚本范围（那是 motion.md 与评审的活）。

  python3 motion_audit.py                 # 扫当前目录
  python3 motion_audit.py --root project/ # 指定根
  python3 motion_audit.py --json          # 出标记卡草稿（配合 review-animations 的 MARKER-CARD.md）

七条判据（每条对应 tokens.md / motion.md 里已有的一条禁令，判断不新造）：

  R1 transition: all            → 用具体属性            HIGH
  R2 scale(0)                   → 从 0.9–0.97 起        HIGH
  R3 ease-in（单向）             → --ease-out            HIGH
  R4 字面量 cubic-bezier         → var(--ease-*)         MEDIUM
  R5 字面量时长（200ms 等）      → var(--duration-*)     MEDIUM
  R6 动 width/height/top/left    → 动 transform/opacity  HIGH
  R7 有过渡却无 reduced-motion   → 加降级块              MEDIUM（每文件一条）

退出码：0 干净 / 1 有发现 / 2 用法错。
纯标准库，不联网。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

# assets/ 是本库自己的工具页（style-explorer 等），不是待交付件，不进体检
SKIP_DIRS = {"node_modules", "vendor", "dist", "out", "build", ".git", "tests",
             "internal-reviews", "demo", "assets", "_archive", "__pycache__"}
TOKEN_FILES = {"tokens.css", "theme.css", "motion.css"}
EXTS = {".css", ".html", ".htm", ".jsx", ".tsx", ".js", ".vue", ".svelte"}

RULES = {
    "R1": ("HIGH", "transition: all", "只过渡实际在变的属性（transform / opacity / color）"),
    "R2": ("HIGH", "scale(0) 入场", "从 scale(0.9–0.97) + opacity 起，modal 除外"),
    "R3": ("HIGH", "单向 ease-in", "进场用 --ease-out；ease-in 只用于退场"),
    "R4": ("MEDIUM", "字面量 cubic-bezier", "改 var(--ease-out | --ease-in-out | --ease-drawer)"),
    "R5": ("MEDIUM", "字面量时长", "改 var(--duration-press | -tooltip | -popover | -panel | -page)"),
    "R6": ("HIGH", "动布局属性", "动 transform/opacity，不动 width/height/top/left/margin/padding"),
    "R7": ("MEDIUM", "缺 prefers-reduced-motion", "加降级块：位移取消、透明度保留（.reveal 保留类名）"),
}

TXN = re.compile(r"(transition|animation)\s*:\s*([^;{}]+)", re.I)
EASE_IN = re.compile(r"(?<![\w-])ease-in(?!-out)")
CUBIC = re.compile(r"cubic-bezier\s*\(", re.I)
DUR = re.compile(r"(?<![\w.-])\d*\.?\d+\s*m?s\b")
LAYOUT = re.compile(r"\b(width|height|top|left|right|bottom|margin|padding)\b", re.I)
REDUCED = re.compile(r"prefers-reduced-motion", re.I)


def iter_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() not in EXTS:
                continue
            if fn in TOKEN_FILES:
                continue
            yield os.path.join(dirpath, fn)


def audit_file(path: str) -> list[dict]:
    findings = []
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return findings
    # 没有过渡/动画/缩放，这份文件与动效无关，整份跳过
    if "transition" not in text and "animation" not in text and "scale(" not in text:
        return findings

    lines = text.splitlines()
    # reduced-motion 块内是规范自己规定的 `1ms !important` 写法，不算绕过令牌：
    # 逐行跟踪花括号深度，把该块整体屏蔽掉，避免把正确写法报成错误。
    masked: set[int] = set()
    depth, reduced_until = 0, None
    for i, line in enumerate(lines, 1):
        net = line.count("{") - line.count("}")
        if reduced_until is not None:
            depth += net
            masked.add(i)
            if depth <= reduced_until:
                reduced_until = None
            continue
        depth += net
        if REDUCED.search(line):
            reduced_until = depth - net  # @media 所在层的深度
            masked.add(i)

    for i, line in enumerate(lines, 1):
        if i in masked:
            continue
        if not TXN.search(line) and "animation" not in line.lower() and "transition" not in line.lower():
            continue
        m = TXN.search(line)
        if not m:
            continue  # 整行只是含 transition 字样、没有真声明时不要按整行判
        decl = m.group(2)
        codes = []
        if m and m.group(1).lower() == "transition" and re.search(r"\ball\b", decl, re.I):
            codes.append("R1")
        if LAYOUT.search(decl):
            codes.append("R6")
        if EASE_IN.search(decl):
            codes.append("R3")
        if CUBIC.search(decl) and "var(" not in decl:
            codes.append("R4")
        if DUR.search(decl) and "var(" not in decl:
            codes.append("R5")
        # 一行可以有多个问题（既有 ease-in 又有字面量时长），逐条都报，别只留第一条
        for code in codes:
            findings.append({"file": path, "line": i, "rule": code, "snippet": line.strip()[:160]})

    # R2 单独扫全文件：scale(0) 可能写在 transform 里而不是过渡行
    for i, line in enumerate(lines, 1):
        if i not in masked and re.search(r"scale\(\s*0\s*\)", line):
            findings.append({"file": path, "line": i, "rule": "R2", "snippet": line.strip()[:160]})

    # R7 每文件一条：有过渡/动画，却没有任何 reduced-motion 降级
    if path.lower().endswith(".css") and not REDUCED.search(text):
        findings.append({"file": path, "line": 1, "rule": "R7", "snippet": "（整份文件）"})
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true", help="输出标记卡草稿（不做人类可读汇总）")
    a = ap.parse_args()
    if not os.path.isdir(a.root):
        print("✗ --root 不是目录：%s" % a.root, file=sys.stderr)
        return 2

    findings = []
    for p in iter_files(a.root):
        findings += audit_file(p)

    findings.sort(key=lambda f: (RULES[f["rule"]][0] != "HIGH", f["file"], f["line"]))

    if a.json:
        cards = []
        for n, f in enumerate(findings, 1):
            sev, name, want = RULES[f["rule"]]
            cards.append({
                "card": "MK-%02d" % n,
                "rule": f["rule"],
                "severity": sev,
                "file": os.path.relpath(f["file"], a.root),
                "line": f["line"],
                "now": f["snippet"],
                "want": want,
                "evidence": name,
                "verdict": "unverified: 没跑渲染/截图，只做了静态定位",
            })
        print(json.dumps({"findings": len(cards), "cards": cards}, indent=2, ensure_ascii=False))
        return 1 if cards else 0

    if not findings:
        print("✓ 没发现绕过令牌的写法（%s）" % os.path.abspath(a.root))
        return 0

    high = sum(1 for f in findings if RULES[f["rule"]][0] == "HIGH")
    print("发现 %d 处（HIGH %d / MEDIUM %d）\n" % (len(findings), high, len(findings) - high))
    for f in findings:
        sev, name, want = RULES[f["rule"]]
        print("%-6s %-46s %s:%d  %s" % (sev, name, os.path.relpath(f["file"], a.root), f["line"], f["snippet"]))
        print("        → %s" % want)
    print("\n修法：参数只改 tokens.css 一处（缓动 --ease-*、时长 --duration-*），"
          "⛔ 不在组件里现场挑；改完重跑本脚本，再跑 python3 emit_tokens.py 复读令牌。")
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:  # 接 head/less 时提前关管道，不当错误
        raise SystemExit(1)
