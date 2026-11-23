/* clip_audit.js · 阴影裁切审计（acceptance.md §1 的执行体）

用法一（浏览器，文档默认路径）：把本文件整段粘进 DevTools 控制台或
`Runtime.evaluate` / Playwright `browser_evaluate`。末行默认执行一次无参审计；
要传参就把末行改成 `clipAudit({ root: '.screen', viewport: true })`。
透明窗 / 无边框窗口必须带 `viewport: true`，把物理视口一起当裁切边界。

用法二（Node，只测几何内核）：
  const { cutFor } = require('./clip_audit.js');
  cutFor({ left: 0, top: 0, right: 100, bottom: 100 },
         { left: 0, top: 0, right: 100, bottom: 100 });   // → { cut: 0, hidden: false }

判据（和 acceptance.md 同一句）：`cut === 0` 是唯一硬性通过条件；`hidden` 只报出来，
是否必须露出关键阴影由人复核。

口径与盲点：
- 阴影外扩按 `spread + blur` 全量计（保守：宁可多报被裁，不报漏裁）；
- 只认 `box-shadow` 与 `filter: drop-shadow`，不认 SVG 内部阴影与伪元素阴影；
- 默认遍历 `root.querySelectorAll('*')`，**不检查 root 自身**——要查某张卡片的投影，
  就把 root 指到它的父容器（acceptance.md 那条 WARNING 说的就是这件事）；
- 祖先裁切按 `overflow:hidden|clip|auto|scroll` 与 `clip-path` 两类判定；
  祖先的内边距盒用 `getBoundingClientRect` 推，边框宽度不精确到亚像素。
*/
(function (global) {
  "use strict";

  function sidesOf(target, bounds) {
    return {
      left: Math.max(0, bounds.left - target.left),
      top: Math.max(0, bounds.top - target.top),
      right: Math.max(0, target.right - bounds.right),
      bottom: Math.max(0, target.bottom - bounds.bottom),
    };
  }

  function intersect(a, b) {
    if (!a) return b;
    if (!b) return a;
    const left = Math.max(a.left, b.left), top = Math.max(a.top, b.top);
    const right = Math.min(a.right, b.right), bottom = Math.min(a.bottom, b.bottom);
    return right <= left || bottom <= top ? { left, top, right, bottom, empty: true } : { left, top, right, bottom };
  }

  // 纯几何：被裁像素数 + 是否完全看不见。Node 里可直接 require 来测。
  function cutFor(target, bounds) {
    if (!bounds) return { cut: 0, hidden: false, sides: { left: 0, top: 0, right: 0, bottom: 0 } };
    const sides = sidesOf(target, bounds);
    const cut = sides.left + sides.top + sides.right + sides.bottom;
    const outside = target.right <= bounds.left || target.left >= bounds.right
      || target.bottom <= bounds.top || target.top >= bounds.bottom;
    return { cut, hidden: outside, sides };
  }

  function shadowExtent(style) {
    // 阴影的包围盒 = 元素盒按 spread+blur 外扩后再平移 (offsetX, offsetY)。
    // 只取 blur+spread 会漏掉偏移那一侧：`box-shadow: 100px 0 0` 的外扩其实是 100px（2026-11-23 补）
    const sides = { left: 0, top: 0, right: 0, bottom: 0 };
    const grow = (dx, dy, radius) => {
      sides.right = Math.max(sides.right, radius + dx);
      sides.left = Math.max(sides.left, radius - dx);
      sides.bottom = Math.max(sides.bottom, radius + dy);
      sides.top = Math.max(sides.top, radius - dy);
    };
    const box = style.boxShadow && style.boxShadow !== "none" ? style.boxShadow : "";
    for (const part of box.split(/,(?![^(]*\))/)) {
      const nums = part.match(/-?\d+(?:\.\d+)?px/g);
      if (!nums) continue;
      const px = nums.map(parseFloat);
      // 顺序：offsetX offsetY [blur] [spread] [color]
      const blur = Math.abs(px[2] || 0), spread = Math.abs(px[3] || 0);
      grow(px[0] || 0, px[1] || 0, blur + spread);
    }
    const filter = style.filter && style.filter.includes("drop-shadow") ? style.filter : "";
    for (const m of filter.matchAll(/drop-shadow\(([^)]*)\)/g)) {
      const px = (m[1].match(/-?\d+(?:\.\d+)?px/g) || []).map(parseFloat);
      grow(px[0] || 0, px[1] || 0, Math.abs(px[2] || 0));
    }
    return sides;
  }

  function clipBounds(el, clipPath) {
    if (clipPath) {
      // 圆／椭圆／多边形／inset 都有真实包围盒；拿元素矩形顶替会把形状外已被裁掉的阴影算成可见（2026-11-23 补）
      const style = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      const shape = (style.clipPath || "").trim();
      const len = (tok, base) => {
        if (!tok) return null;
        if (tok === "closest-side") return base === "w" ? r.width / 2 : r.height / 2;
        if (tok.endsWith("%")) return (parseFloat(tok) / 100) * base;
        if (tok.endsWith("px")) return parseFloat(tok);
        return null;
      };
      const at = (tok, origin, size) => {
        if (!tok || tok === "center") return origin + size / 2;
        if (tok.endsWith("%")) return origin + (parseFloat(tok) / 100) * size;
        if (tok.endsWith("px")) return origin + parseFloat(tok);
        return null;
      };
      const inner = shape.slice(shape.indexOf("(") + 1, shape.lastIndexOf(")"));
      if (/^circle/i.test(shape) || /^ellipse/i.test(shape)) {
        const split = inner.split(" at ");
        const radii = split[0].trim().split(/\s+/).filter(Boolean);
        const center = (split[1] || "center").trim().split(/\s+/).filter(Boolean);
        const isEllipse = /^ellipse/i.test(shape);
        const rx = len(radii[0], "w");
        const ry = isEllipse ? len(radii[1] || radii[0], "h") : rx;
        const cx = at(center[0], r.left, r.width);
        const cy = at(center[1], r.top, r.height);
        if (rx === null || ry === null || cx === null || cy === null) return null;
        return { left: cx - rx, top: cy - ry, right: cx + rx, bottom: cy + ry };
      }
      if (/^inset/i.test(shape)) {
        const toks = inner.split(/\s+/).filter(Boolean);
        const pick = (i, fallback) => toks[i] ?? fallback;
        const t = len(pick(0, "0px"), "h") ?? 0;
        const rt = len(pick(1, toks[0] || "0px"), "w") ?? 0;
        const b = len(pick(2, toks[0] || "0px"), "h") ?? 0;
        const l = len(pick(3, pick(1, toks[0] || "0px")), "w") ?? 0;
        return { left: r.left + l, top: r.top + t, right: r.right - rt, bottom: r.bottom - b };
      }
      if (/^polygon/i.test(shape)) {
        const pts = shape.slice(shape.indexOf("(") + 1, shape.lastIndexOf(")")).split(",")
          .map((tok) => tok.trim().split(/ +/))
          .filter((pair) => pair.length === 2);
        const coords = pts.map(([x, y]) => [px(x), px(y)]).filter(([x, y]) => x !== null && y !== null);
        if (!coords.length) return null;
        return {
          left: r.left + Math.min(...coords.map((c) => c[0])),
          top: r.top + Math.min(...coords.map((c) => c[1])),
          right: r.left + Math.max(...coords.map((c) => c[0])),
          bottom: r.top + Math.max(...coords.map((c) => c[1])),
        };
      }
      return null;  // path() / url() 等算不出：交给调用方判为「不可判」
    }
    const style = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const bl = parseFloat(style.borderLeftWidth) || 0, bt = parseFloat(style.borderTopWidth) || 0;
    const br = parseFloat(style.borderRightWidth) || 0, bb = parseFloat(style.borderBottomWidth) || 0;
    return { left: r.left + bl, top: r.top + bt, right: r.right - br, bottom: r.bottom - bb };
  }

  function isClipper(style) {
    const o = style.overflow + " " + style.overflowX + " " + style.overflowY;
    if (/(hidden|clip|auto|scroll)/.test(o) && !/(visible)/.test(o)) return "overflow";
    if (style.clipPath && style.clipPath !== "none") return "clip-path";
    if (style.maskImage && style.maskImage !== "none" && !style.maskImage.includes("none")) return "mask";
    return null;
  }

  function clipAudit(opts) {
    if (typeof document === "undefined") throw new Error("clipAudit 只能在浏览器里跑");
    const root = opts && opts.root ? document.querySelector(opts.root) : document.body;
    if (!root) return { cut: 0, checked: 0, items: [], hidden: [], error: "root 不存在：" + opts.root };

    let bounds = opts && opts.viewport ? { left: 0, top: 0, right: innerWidth, bottom: innerHeight } : null;
    const items = [], hidden = [], seen = [], unknown = [];
    let checked = 0;

    for (const el of root.querySelectorAll("*")) {
      const style = getComputedStyle(el);
      const extent = shadowExtent(style);
      if (!extent) continue;
      const r = el.getBoundingClientRect();
      if (!r.width && !r.height) continue;
      checked++;

      let ancestors = null, clippedBy = null;
      for (let p = el.parentElement; p && p !== document.documentElement; p = p.parentElement) {
        // 祖先自己也可能被裁；一并纳入，保证边界是最小交集。
        const kind = isClipper(getComputedStyle(p));
        if (kind) {
          const b = clipBounds(p, kind === "clip-path");
          if (b === null) {
            unknown.push({ element: el.tagName.toLowerCase(), by: (p.className || p.tagName).toString(), why: "clip-path 形状算不出包围盒" });
          } else {
            ancestors = intersect(ancestors, b);
          }
          clippedBy = clippedBy || (p.className || p.tagName).toString();
        }
        if (kind === "overflow" && (style.position === "fixed")) break;
      }
      if (opts && opts.viewport) ancestors = intersect({ left: 0, top: 0, right: innerWidth, bottom: innerHeight }, ancestors);

      const target = { left: r.left - extent.left, top: r.top - extent.top, right: r.right + extent.right, bottom: r.bottom + extent.bottom };
      const res = cutFor(target, ancestors);
      if (res.hidden) {
        hidden.push({ element: el.tagName.toLowerCase() + (el.className ? "." + String(el.className).split(/\s+/).join(".") : ""), by: clippedBy });
      } else if (res.cut > 0) {
        items.push({ element: el.tagName.toLowerCase() + (el.className ? "." + String(el.className).split(/\s+/).join(".") : ""), by: clippedBy, sides: res.sides, pixels: res.cut });
      }
    }

    const cut = items.reduce((n, it) => n + it.pixels, 0);
    // 回执形状对齐 acceptance.md §1 第 5 条：{ ok, cut }；hidden 一律让 ok 为 false，
    // 因为「完全看不见的阴影」要人复核，⛔ 机器替人放行。
    // 算不出包围盒的 clip-path 一律让人复核：⛔ 不许把「没审计」算成「通过」
    return { ok: cut === 0 && hidden.length === 0 && unknown.length === 0, cut, checked, items, hidden, unknown };
  }

  const api = { cutFor, clipAudit, shadowExtent };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else global.clipAudit = clipAudit;

  // 直接粘贴时跑一次默认审计；要传参就改这一行。
  if (typeof document !== "undefined" && typeof module === "undefined") clipAudit({});
})(typeof globalThis !== "undefined" ? globalThis : this);
