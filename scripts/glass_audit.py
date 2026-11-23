#!/usr/bin/env python3
"""glass_audit.py — 玻璃面板静态审计（浮龟 · 玻璃通道的机械闸）

只做能机判的那几件事：同屏 backdrop 层数、模糊半径、嵌套玻璃、逐帧动 blur、
三层结构（底／描边／光）是否齐、文字是否压在不透明度过低的色上、降级信号在不在。
判据正本见 references/glass.md；本脚本只转述，不替人判「好不好看」。

用法：
    python3 scripts/glass_audit.py page.html            # 人读报告，有 E 级则退出码 1
    python3 scripts/glass_audit.py page.html --json     # 机器读
    python3 scripts/glass_audit.py page.html --tokens   # 附一套标准玻璃变量块
    python3 scripts/glass_audit.py src/                 # 扫目录里的 .html/.css
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BLUR_CAP = 12.0          # px，硬线；超过就不是「演示机上的玻璃」而是糊化
BLUR_WARN = 9.0
BACKDROP_CAP = 3         # 同屏真实 backdrop 层上限
TEXT_ALPHA_FLOOR = 0.85  # 玻璃上的字不能是半透明前景


def _px(value: str) -> float | None:
    m = re.search(r"(-?\d+(?:\.\d+)?)(px|em|rem)?", value or "")
    if not m:
        return None
    return float(m.group(1))


def _alpha(color: str) -> float | None:
    """rgba(...) 取 alpha；hex8 取末两位；其余视为不透明（None 表示判不了）。"""
    if not color:
        return None
    low = color.strip().lower()
    m = re.match(r"rgba?\(\s*([^)]*)\)", low)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        if len(parts) == 4:
            try:
                return float(parts[3])
            except ValueError:
                return None
        return 1.0
    if re.fullmatch(r"#[0-9a-f]{8}", low):
        return int(low[6:8], 16) / 255
    if re.fullmatch(r"#[0-9a-f]{3,6}", low):
        return 1.0
    return None


RULE_RE = re.compile(r"([^{}@]+)\{([^{}]*)\}")
TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:[^<>\"']|\"[^\"]*\"|'[^']*')*)(/?)>", re.S)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def _parse_decls(text: str) -> dict[str, str]:
    out = {}
    for chunk in text.split(";"):
        if ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        out[key.strip().lower()] = value.strip()
    return out


def _strip_at_blocks(css: str) -> str:
    """把 @media / @supports 整块摘掉再当规则读。

    不摘的话，降级块里的 `.card{backdrop-filter:none}` 会被并进 `.card` 的基础规则，
    把「有玻璃」判成「没玻璃」（2026-11-23 补）。
    """
    return re.sub(r"@[^{;]+\{(?:[^{}]|\{[^{}]*\})*\}", "", css)


def _root_vars(css: str) -> dict[str, str]:
    out = {}
    for sel, body in RULE_RE.findall(_strip_at_blocks(css)):
        if sel.strip() not in (":root", "html", "body"):
            continue
        for key, value in _parse_decls(body).items():
            if key.startswith("--"):
                out[key] = value
    return out


def _resolve_vars(value: str, vars_: dict[str, str]) -> str:
    """把 var(--x) 就地展开（只做 :root／html／body 上声明过的，三层封顶）。"""
    for _ in range(3):
        value = re.sub(r"var\((--[-\w]+)\)", lambda m: vars_.get(m.group(1), m.group(0)), value)
    return value


def _class_rules(css: str) -> dict[str, dict[str, str]]:
    """只认单类选择器（`.foo`／`.foo.bar`），够用且不误判后代选择器。"""
    rules: dict[str, dict[str, str]] = {}
    for sel, body in RULE_RE.findall(_strip_at_blocks(css)):
        if ":" in sel or "@" in sel:
            continue
        for part in sel.split(","):
            part = part.strip()
            if not part.startswith(".") or " " in part or ">" in part:
                continue
            classes = [c for c in part.split(".") if c]
            decls = _parse_decls(body)
            for cls in classes:
                rules.setdefault(cls, {}).update(decls)
    return rules


def _attrs(raw: str):
    attrs = {}
    for m in re.finditer(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+))', raw):
        attrs[m.group(1).lower()] = m.group(3) or m.group(4) or m.group(5) or ""
    return attrs


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def audit(html: str, css_files: list[tuple[str, str]] | None = None) -> dict:
    """返回 {issues: [...], stats: {...}}；issues 每条带 level/rule/line/message/fix。"""
    issues: list[dict] = []
    styles = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    for _, extra in (css_files or []):
        styles += "\n" + extra
    rules = _class_rules(styles)
    vars_ = _root_vars(styles)

    has_reduced_motion = "prefers-reduced-motion" in styles
    has_contrast = "prefers-contrast" in styles
    has_supports = "@supports" in styles and "backdrop-filter" in styles
    animations_backdrop = bool(re.search(r"(transition|animation)[^;{}]*backdrop-filter", styles))

    stack: list[dict] = []
    sections: dict[str, list[dict]] = {}
    section_id = "doc"
    glass_layers = 0
    max_blur = 0.0

    def current_section() -> str:
        return section_id

    pos_to_line = lambda p: _line_of(html, p)
    for m in TAG_RE.finditer(html):
        closing, name, raw, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if closing:
            for i in range(len(stack) - 1, -1, -1):
                if stack[i]["tag"] == name:
                    if name == "section" and stack[i].get("was_section"):
                        section_id = stack[i].get("parent_section") or "doc"
                    del stack[i:]
                    break
            continue
        attrs = _attrs(raw)
        decls: dict[str, str] = {}
        for cls in (attrs.get("class") or "").split():
            decls.update(rules.get(cls, {}))
        if "style" in attrs:
            decls.update(_parse_decls(attrs["style"]))
        entry = {"tag": name, "decls": decls, "line": pos_to_line(m.start()), "classes": attrs.get("class") or ""}
        if name == "section":
            parent = section_id
            section_id = attrs.get("id") or attrs.get("data-slide-id") or f"section@{entry['line']}"
            entry["was_section"] = True
            entry["parent_section"] = parent
        if name not in VOID and not selfclose:
            stack.append(entry)
        backdrop = decls.get("backdrop-filter") or decls.get("-webkit-backdrop-filter")
        if backdrop:
            backdrop = _resolve_vars(backdrop, vars_)
        if backdrop and "none" not in backdrop:
            glass_layers += 1
            sec = current_section()
            sections.setdefault(sec, []).append(entry)
            blur = _px(re.search(r"blur\(([^)]*)\)", backdrop).group(1)) if "blur(" in backdrop else None
            if blur:
                max_blur = max(max_blur, blur)
                if blur > BLUR_CAP:
                    issues.append({
                        "level": "E", "rule": "blur-cap", "line": entry["line"],
                        "message": f"模糊半径 {blur:g}px 超过 {BLUR_CAP:g}px 上限（玻璃会糊成一片，老机器也扛不住）",
                        "fix": f"降到 {BLUR_CAP:g}px 以内；要更「厚」用内高光与投影，不要加模糊",
                    })
                elif blur > BLUR_WARN:
                    issues.append({
                        "level": "W", "rule": "blur-high", "line": entry["line"],
                        "message": f"模糊半径 {blur:g}px 偏大（>{BLUR_WARN:g}px），投影／低端屏上会发糊",
                        "fix": "默认档给 8px；只有整屏浮层可到 12px",
                    })
            # 嵌套玻璃：父级也带 backdrop
            if any((p["decls"].get("backdrop-filter") or "") not in ("", "none") for p in stack[:-1]):
                issues.append({
                    "level": "E", "rule": "glass-on-glass", "line": entry["line"],
                    "message": "这层玻璃叠在另一层玻璃上：轻半透明叠轻半透明会把底下糊成灰块",
                    "fix": "里层改实底或直接去 backdrop，只留外层一层玻璃",
                })
            # 三层结构：底／描边／光
            if not (decls.get("background") or decls.get("background-color")):
                issues.append({
                    "level": "W", "rule": "no-tint", "line": entry["line"],
                    "message": "只有 blur 没有底色：这是「模糊」不是「玻璃」，边缘会散开、文字会失读",
                    "fix": "补一层半透明底色（alpha .18–.40），或改用实底卡片",
                })
            if not decls.get("border") and "inset" not in (decls.get("box-shadow") or ""):
                issues.append({
                    "level": "W", "rule": "no-edge", "line": entry["line"],
                    "message": "没有描边也没有内高光：缺了「玻璃的厚度」，读起来像一块蒙版",
                    "fix": "1px 高光描边或一条 inset 顶部高光，二者选一",
                })
            color_alpha = _alpha(decls.get("color") or "")
            if color_alpha is not None and color_alpha < TEXT_ALPHA_FLOOR:
                issues.append({
                    "level": "W", "rule": "text-too-faint", "line": entry["line"],
                    "message": f"玻璃上的字是半透明前景（alpha {color_alpha:.2f}）：底是什么色不归你管，字会随底忽明忽暗",
                    "fix": "文字用实色；至少要半透明的，放到实底层上，不要压在玻璃上",
                })
        if name not in VOID and not selfclose:
            pass

    for sec, layers in sections.items():
        if len(layers) > BACKDROP_CAP:
            issues.append({
                "level": "E", "rule": "backdrop-count", "line": layers[BACKDROP_CAP]["line"],
                "message": f"「{sec}」同屏 {len(layers)} 层 backdrop，超过 {BACKDROP_CAP} 层上限（每层都是一次全屏采样）",
                "fix": f"减到 {BACKDROP_CAP} 层以内：优先留下导航与最重要的一块，其余改实底",
            })
    if animations_backdrop:
        issues.append({
            "level": "E", "rule": "animate-blur", "line": 0,
            "message": "样式里对 backdrop-filter 做了 transition/animation：模糊是最贵绘制属性，逐帧动它必掉帧",
            "fix": "玻璃的到场用 opacity + scale 近似；⛔ 不动 blur",
        })
    if glass_layers and not has_reduced_motion:
        issues.append({
            "level": "W", "rule": "no-degrade", "line": 0,
            "message": "有玻璃但没写 prefers-reduced-motion 降级：动效偏好为「减少」的用户拿到的是满档玻璃",
            "fix": "补 prefers-reduced-motion 与 @supports not (backdrop-filter) 两条降级；prefers-reduced-transparency 不可单独当依据",
        })
    if glass_layers and re.search(r"will-change\s*:\s*backdrop-filter", styles):
        issues.append({
            "level": "W", "rule": "will-change-always", "line": 0,
            "message": "will-change 常驻挂 backdrop-filter：会长期占用合成层，动画结束就该摘",
            "fix": "只在动画前挂、结束即摘；或者干脆不挂",
        })
    if "prefers-reduced-transparency" in styles and not (has_reduced_motion or has_contrast or has_supports):
        issues.append({
            "level": "W", "rule": "single-degrade", "line": 0,
            "message": "只拿 prefers-reduced-transparency 当降级依据：Safari 不支持、Firefox 默认关闭，等于没有",
            "fix": "与 prefers-reduced-motion、prefers-contrast、@supports not 三件套一起用",
        })

    return {
        "issues": issues,
        "stats": {"glass_layers": glass_layers, "max_blur": max_blur, "sections": {k: len(v) for k, v in sections.items()}},
    }


TOKENS = """/* 浮龟 · 玻璃变量（改一处全页生效；数值取自判据的安全区间） */
:root{
  --glass-blur: 8px;                      /* 4–12px，超过 12px 一律 E */
  --glass-tint: rgba(255,255,255,.24);    /* 中性底：换品牌色时只改这里，alpha .18–.40 */
  --glass-edge: rgba(255,255,255,.55);    /* 边缘高光，.35–.70 */
  --glass-thick: 12px;                    /* 内高光偏移基准，8–16px */
  --glass-sat: 1.1;                       /* 1.0–1.35 */
  --glass-radius: 18px;                   /* 16–28px；胶囊控件另算 */
}
.glass{
  background: var(--glass-tint);
  backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat));
  border: 1px solid var(--glass-edge);
  box-shadow: 0 6px 16px rgba(0,0,0,.14),
              inset 2px 2px 1px rgba(255,255,255,.5);
}
@media (prefers-reduced-motion: reduce){ .glass{ transition: none } }
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))){
  .glass{ background: rgba(255,255,255,.92); backdrop-filter: none }
}
"""


def render(result: dict) -> str:
    issues = result["issues"]
    stats = result["stats"]
    lines = [f"玻璃层 {stats['glass_layers']} 处｜最大模糊 {stats['max_blur']:g}px｜分屏账目 "
             + ("、".join(f"{k}:{v}" for k, v in stats["sections"].items()) or "无")]
    if not issues:
        return "\n".join(lines + ["✅ 机械判据全过（⛔ 这只证数值，不证好看）"])
    for it in issues:
        where = f"L{it['line']}" if it["line"] else "样式表"
        lines.append(f"{it['level']} [{it['rule']}] {where}：{it['message']}")
        lines.append(f"    改法：{it['fix']}")
    e = sum(1 for i in issues if i["level"] == "E")
    w = len(issues) - e
    lines.append(f"E {e}／W {w}")
    return "\n".join(lines)


def collect(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_dir():
            out.extend(sorted(x for x in p.rglob("*") if x.suffix in {".html", ".htm", ".css"}))
        elif p.suffix in {".html", ".htm", ".css"}:
            out.append(p)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="玻璃面板静态审计")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--tokens", action="store_true", help="附一套标准玻璃变量块")
    args = ap.parse_args(argv)
    files = collect([Path(p) for p in args.paths])
    if not files:
        print("⛔ 没找到 .html / .css", file=sys.stderr)
        return 2
    reports = []
    hard = 0
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        css_files = []
        for ref in re.findall(r'<link[^>]+href="([^"]+\.css)"', text):
            cand = (path.parent / ref).resolve()
            if cand.is_file():
                css_files.append((ref, cand.read_text(encoding="utf-8", errors="replace")))
        res = audit(text, css_files)
        reports.append({"file": str(path), **res})
        hard += sum(1 for i in res["issues"] if i["level"] == "E")
        if not args.json:
            print(f"\n== {path}")
            print(render(res))
    if args.json:
        print(json.dumps({"files": reports, "E": hard}, ensure_ascii=False, indent=2))
    if args.tokens:
        print("\n" + TOKENS)
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
