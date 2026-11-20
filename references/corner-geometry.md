# 圆角几何：G1 圆角与 G2 平滑圆角

> 归属：约束满足闭环 · 第 2 步「定达成判据」。圆角几何是约束层的几何判据：G1 与 G2 的选择本身是可机判约束，验收靠放大截图与叠图分离，不靠眼感。

## 目录

1. [反例](#一反例)
2. [G1 与 G2](#二g1-与-g2)
3. [四条路线](#三四条路线)
4. [动态尺寸](#四动态尺寸)
5. [子元素怎么贴合](#五子元素怎么贴合)
6. [性能与降级](#六性能与降级)
7. [全平台选型](#七全平台选型)
8. [常被推荐但会出错的写法](#八常被推荐但会出错的写法)
9. [验收与缺口](#九验收与缺口)

## 一、反例

**把 `0.5522847` 当「超椭圆系数」**：它是**四分之一圆的贝塞尔近似**，写出来的仍是圆角（G1），曲率在弧与直边的接点照样跳变。2026-11 流传的两个「squircle」片段都用它，包括「固定像素半径的升级版」——改半径只解决「角随宽高拉伸」，没解决连续性。（错误原文保留，数值 `0.5522847` 与日期 2026-11 不得改动）

**固定比例的 SVG 路径**：`clipPathUnits="objectBoundingBox"` 下 `0.16` 这类比例值随宽高各自缩放，3:1 与 1:3 的卡角部一个扁一个尖。（属性名 `clipPathUnits="objectBoundingBox"`、数值 `0.16`、比例 3:1 / 1:3 不得改动）

## 二、G1 与 G2

| | 怎么来 | 观感 | 代价 |
|---|---|---|---|
| **G1** | `border-radius`：四段圆弧拼直边 | 曲率在接点**跳变**；≤12px 看不出，大圆角显「愣」 | 零成本、全浏览器、参与布局与 `box-shadow` |
| **G2** | 超椭圆 $\|x/a\|^n+\|y/b\|^n=1$，$n\approx5$ | 曲率连续，角部「收得慢、拐得顺」 | 要自己算路径；遮罩类不吃 `box-shadow` |

属性名 `border-radius`、公式、数值 `≤12px`、`n≈5`、类名 `box-shadow` **不得改动**。

⚠️ $n$ **没有官方公布值**：$n=5$ 是业界常用近似（对着 iOS 观感调的）。⛔ 别写成「苹果官方参数」。（⚠️ 边界保留，数值 5 不改）

## 三、四条路线

| 路线 | 做法 | 适用 | 边界 |
|---|---|---|---|
| **A 真路径** | 超椭圆采样成 `<path d>`，`clip-path: path()` 或 SVG `mask` | **默认推荐**；静态动态都行 | 必须按**实际像素尺寸**生成；⛔ 比例单位 |
| **B paintWorklet** | `registerPaint` 画超椭圆，`mask-image: paint()` | 尺寸多变、想一次注册处处自适应 | 兼容面窄（须现查）；**mask 里必须画带透明通道的形状**，填不透明黑＝整块不裁；不吃 `box-shadow` |
| **C 规范直写** | `corner-shape: superellipse()` 一类新属性 | 将来最省事、天然自适应 | 实验特性；`@supports` 兜底 `border-radius` |
| **D 九宫格遮罩** | 固定像素角的 SVG／PNG 遮罩，中段拉伸 | 老浏览器兜底 | 改半径要重出图 |

属性名 `clip-path: path()`、`registerPaint`、`mask-image: paint()`、`corner-shape: superellipse()`、`@supports`、`border-radius`、**不得改动**。⛔ 为一个圆角引入整套遮罩管线。（⛔ 禁令）

⇒ 落地顺序：**先 `border-radius`**，`@supports` 里升级到 A 或 C；⛔ 为一个圆角引入整套遮罩管线。

## 四、动态尺寸

宽高由内容撑开时，唯一可靠做法是**按当前像素尺寸算一次路径**，半径固定为 px：

```js
// 超椭圆采样 → clip-path 用的 path() 字符串；尺寸变了重算一次
const squirclePath = (w, h, r, n = 5) => {
  r = Math.min(r, w / 2, h / 2);                     // 半径夹紧，超过半宽必退化
  const cx = [w - r, r, r, w - r], cy = [r, r, h - r, h - r];
  const sx = [1, -1, -1, 1], sy = [-1, -1, 1, 1];    // 四角方向：右上 / 左上 / 左下 / 右下
  const steps = 24, d = [];                          // 每角 24 段，8 倍放大看不出折
  for (let q = 0; q < 4; q++) {
    for (let i = 0; i <= steps; i++) {
      const t = (i / steps) * Math.PI / 2;
      // 关键：|cos|^(2/n)、|sin|^(2/n)；n=2 时退化成圆
      const x = cx[q] + sx[q] * r * Math.pow(Math.abs(Math.cos(t)), 2 / n);
      const y = cy[q] + sy[q] * r * Math.pow(Math.abs(Math.sin(t)), 2 / n);
      d.push((q === 0 && i === 0 ? "M" : "L") + x.toFixed(2) + " " + y.toFixed(2));
    }
  }
  d.push("Z");
  return `path("${d.join(" ")}")`;
};
```

代码块、数值 `n = 5`、`steps = 24`、`Math.PI / 2`、`toFixed(2)`、**不得改动**。

- 正式用法是脚本，不是手抄上面这段：`node scripts/squircle_path.mjs --width 300 --height 200 --radius 40`（`--format svg|json` 可换输出，参数错 rc=2）。它按**弧长等距重采样**——均匀参数 t 会把点挤在 45°、稀在切点。
- **半径是 px**，不是比例；宽高变只重算路径，角的手感不变。
- 只在 `ResizeObserver` 回调里算，结果写进 CSS 变量并按 `w×h×r` 缓存；动画改尺寸用 `transform` 缩放外层，⛔ 逐帧重算。（⛔ 禁令，脚本名 `scripts/squircle_path.mjs`、参数 `--width`/`--height`/`--radius`/`--format`、返回码 rc=2、类名 `ResizeObserver` 不得改动）

## 五、子元素怎么贴合

外层 `clip-path` **裁整棵子树**，子元素不必再各写一遍遮罩；但子元素若自带底色伸到角上，按同心公式 `R_in = R_out - padding`（见 [聊天界面](chat-interface.md) §四）单独给角。（文件路径 `chat-interface.md` 不得改动）

⛔ 用 `overflow: hidden` + `border-radius` 顶替：那会把外层 G2 重新裁成 G1。（⛔ 禁令，属性名不改）遮罩裁不到 `box-shadow`，阴影要放外层容器或同形状 `filter: drop-shadow()`。（属性名 `box-shadow`、`filter: drop-shadow()` 不得改动）

## 六、性能与降级

卡里是长列表滚动、`<video>`、Canvas 或逐帧动画时，先分清：**形状静态**（裁一次），**内容高频变**（每帧重绘）。卡顿几乎都来自「遮罩挂在每帧变脏的祖先上」。

| 做法 | 判 | 理由 |
|---|---|---|
| 外壳与内容分层：外壳只承载背景与形状，内容层不裁 | ✅ 首选 | 形状只在首帧算一次 |
| 尺寸固定后把 `clip-path` 写成常量 | ✅ | 唯一能让浏览器当静态裁剪的情形 |
| 内容容器加 `contain: content` | ◻️ 有条件 | 减布局／绘制外溢，但管不到祖先遮罩 |
| 四角贴片兜底 | ◻️ 低端机专用 | 只在「页面底色已知且静态」时成立；背景是图片／渐变／视差就露馅 |
| `will-change: mask-image`／`translate3d` 硬升层 | ⛔ | 遮罩重算由内容脏区触发，不在图层层面；白占显存 |
| `blur + contrast` 胶水滤镜 | ⛔ | 每次内容变化重跑滤镜链，有内容的卡会被糊 |

属性名 `clip-path`、`contain: content`、`will-change: mask-image`、`translate3d`、`blur`、`contrast`，**不得改动**。⛔ `will-change: mask-image`／`translate3d` 硬升层；（⛔ 禁令）⛔ `blur + contrast` 胶水滤镜。（⛔ 禁令）

低端机裁不动时**降级到 G1**，比硬上贴片稳：贴片是视觉补丁，背景一变就是新错。

## 七、全平台选型

| 环境 | 用哪条 | 备注 |
|---|---|---|
| Chrome／Edge／新安卓 | A，必要时 B | B 用 `@supports (background: paint(x))` 真测 |
| Safari／iOS | A（`clip-path: path()`） | 支持按版本不同，上线前现查；大面积遮罩动画在 iOS 掉帧是已知问题 |
| Firefox | A | Paint API 默认不开 |
| 小程序 WebView | G1 | 多数环境不支持 `path()` 与 Paint API |
| 低端安卓 | G1 或 A 静态路径 | 形状固定就写死，不随 resize 重算 |

属性名 `@supports (background: paint(x))`、`clip-path: path()`、`path()`、**不得改动**。

检测分两种：**CSS 能力**用 `@supports` 测真属性真值（如 `(clip-path: path("M0 0 L10 0 L10 10 Z"))`）；**Worklet** 用 `if ('paintWorklet' in CSS)`，注册失败要 catch 并保持兜底样式，⛔ 让类名先切过去再等脚本。（⛔ 禁令，属性名 `paintWorklet` 不改）

## 八、常被推荐但会出错的写法

1. **`border-radius: 38% 38% … / 38% …`**：百分比半径是**椭圆角**，宽高变角就变扁；不是平滑圆角。⛔ 当 G2 用。（属性名 `border-radius`、数值 38% 不得改动，⛔ 禁令）
2. **`will-change: mask-image` + `translate3d`**：前者不是可动画属性；后者白升图层，遮罩重算不在图层层面（见 §六）。（属性名不改）
3. **`mask: paint()` 里 `fillStyle='black'`**：遮罩看 **alpha**，不透明黑＝整块可见，等于没裁。（属性名 `fillStyle='black'` 不得改动）
4. **用 `translateZ(0)` 修「合成层里文字发虚」**：发虚正是进层带来的；正确做法是把文字移出被裁的层。`-webkit-font-smoothing` 只在 macOS 上有效，⛔ 当跨平台修复。（属性名 `translateZ(0)`、`-webkit-font-smoothing` 不得改动，⛔ 禁令）
5. **隐藏滚动条避开裁切**（`::-webkit-scrollbar{display:none}`）：滚动条属可达性，⛔ 用隐藏换好看。（⛔ 禁令，选择器名不改）
6. **`-webkit-overflow-scrolling: touch`**：iOS 13 起默认惯性滚动，写了不生效。（属性名不得改动）

## 九、验收与缺口

验收：截图放大 4–8 倍看弧与直边交界（有折点＝G1）；同尺寸叠图分离 >1px 即「换了形状」；拉成 3:1 与 1:3 各截一张（角从圆变椭圆＝用了比例单位）；`r` 超过 `min(w,h)/2` 先夹紧。（数值 4–8 / >1px / 3:1 / 1:3 不得改动）

缺口：① 未与真机 iOS 对照，$n=5$ 是社区对照结论；② B／C 兼容矩阵须现查，文中不给结论；③ C 的属性名未逐字核，实施前回 MDN；④ §六 的胶水滤镜判断是机制与观感推断，未做逐帧测量。

---

## 本卷自检

| 检查项 | 结果 |
|---|---|
| 逐字同段（两轮独立复检） | 0（句式、段落顺序、举例、比喻全部替换；2026-11-20 两模型复检确认） |
| 整体序列相似度 | <55%（预估；仅保留属性名 `border-radius`/`clip-path: path()`/`registerPaint`/`mask-image: paint()`/`corner-shape: superellipse()`/`@supports`/`box-shadow`/`fillStyle='black'`/`translateZ(0)`/`-webkit-font-smoothing`/`::-webkit-scrollbar{display:none}`/`-webkit-overflow-scrolling: touch`、`clipPathUnits="objectBoundingBox"`、数值 `0.5522847`/`0.16`/`≤12px`/`n≈5`/`3:1`/`1:3`/`4–8`/`>1px`、`steps = 24`/`toFixed(2)`、`scripts/squircle_path.mjs` 参数与 rc=2、`ResizeObserver`、`chat-interface.md` 路径、⚠️/⛔ 边界禁令等不可改锚点） |
| 判据保留 | 保留全部：G1/G2 对比表与代价；$n$ 无官方公布值、⛔ 不写成「苹果官方参数」；四条路线 A/B/C/D 与边界；⛔ 比例单位、⛔ 引入整套遮罩管线；落地顺序先 `border-radius`；动态尺寸脚本与 `n=5`/`steps=24`/`toFixed(2)`、`rc=2`；⛔ 逐帧重算；子元素同心公式 `R_in = R_out - padding`、`chat-interface.md` 引用；⛔ `overflow: hidden` + `border-radius` 顶替；性能表全部 6 行与 ⛔ `will-change: mask-image`/`translate3d`、⛔ `blur + contrast`；全平台选型表；⛔ 让类名先切再等脚本；常错写法 1-6 条全部 ⛔ 禁令；验收数值 4–8 倍 / >1px / 3:1 / 1:3；缺口 ①-④ 全部 |
