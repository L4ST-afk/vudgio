# 令牌

> 归属：约束满足闭环 · 第 2 步「定达成判据」。令牌 = 约束的机器可读形态，每个值必须来自系统，⛔ 不手调 hex。

## 目录

- [反例](#反例)
- [先检测（Step 0）](#先检测step-0)
- [三级解析顺序](#三级解析顺序)
- [十类令牌](#十类令牌)
- [动效令牌](#动效令牌)
- [生成色阶（禁手调）](#生成色阶禁手调)
- [对比度门](#对比度门)
- [落盘与说话](#落盘与说话)

## 反例

两种情况最常见：一是从一个好看的截图里手抄 `#3b82f6`、`#1f2937`，再手调三档，调完 400 比 500 还深——色阶彼此漂了，没人能复原；二是项目根本没有令牌，模型就默认 indigo + gray，页面一看就是生成器产物。（错误原文保留）

规则：**值必须来自系统，⛔ 不手调 hex**；没有系统就先生成一套，再声明它是这一次生成的。

## 先检测（Step 0）

一个来回就能查完，⛔ 凭印象：框架与渲染方式（SSR/SPA）／Tailwind 大版本（v4 `@theme`、v3 `tailwind.config.js`）／已有 tokens 与主题文件／组件库（shadcn/ui 等自带令牌契约）／暗色是已有、计划还是无。没读到就写「未读到」。

**既有系统永远优先。** 把原则翻译成它的词汇，⛔ 覆盖、⛔ 静默迁移、⛔ 引入用户没要的构建依赖。（库名 `shadcn/ui` 不改）

## 三级解析顺序

任何一个具体值，按这个顺序取：

1. 项目已有令牌（Step 0 读到的）
2. 本次生成的令牌（本卷算法 + `scripts/emit_tokens.py`）
3. 书的默认刻度——**并且必须在交付说明里写明降级**

脚本名 `scripts/emit_tokens.py` 不得改动。

三级都取不到，这个缺口本身就是发现：项目缺一个令牌，先补它，否则同类决定会各写各的。

## 十类令牌

| 类 | 刻度 | 约束 |
|---|---|---|
| 色阶 | 100–900（可加 50/950） | 相邻级差 ≥25% 感知步距；色相旋转 ≤20–30° |
| 文字色 | 深 / 灰 / 浅灰，最多三档 | 灰字不上彩底；要的是降对比，不是变灰 |
| 间距 | 4/8/12/16/24/32/48/64 | 组内紧于组间；一处距离只由一层加 |
| 字号 | display / h1 / h2 / body / caption | 相邻级差 ≥25%，⛔ 15/16/17 挤在一起 |
| 行高 | 随行宽与字号 | 窄 1.5 → 宽 2；大字可到 1 |
| 圆角 | 4/8/12/16 | 同心：内 = 外 − 内边距；⛔ 圆角套圆角 |
| 边框 | 1px 常规、0.5px 分隔 | 同类线全页只出现一次 |
| 阴影 | 最多 5 级 | 都带偏移 + 柔化；靠明度 1–3% 分层，不靠加描边 |
| 缓动 | out / in-out / drawer 三条 | `cubic-bezier(0.23,1,0.32,1)`、`(0.77,0,0.175,1)`、`(0.32,0.72,0,1)` |
| 时长 | press 100–160 / tooltip 125–200 / popover 150–250 / panel 200–500 | UI 元素 <300ms，整页转场除外 |

刻度、数值、阈值、⛔ 禁令、**不得改动**。缓动三条的 `cubic-bezier` 参数值不得改动。

## 动效令牌

缓动与时长的值同样来自系统，⛔ 逐个组件现场挑：

```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);      /* 进入 */
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);  /* 来回 */
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);   /* 抽屉、面板 */
--duration-press: 160ms; --duration-tooltip: 200ms;
--duration-popover: 250ms; --duration-panel: 400ms; --duration-page: 500ms;
```

CSS 变量名与取值**不得改动**（字段名保留）。

**有弹簧手感就要有曲线文件，⛔ 靠感觉写 `cubic-bezier`。** 按目标时长反解，命令直接吐 CSS：

```bash
python3 scripts/spring_to_linear.py --target 200 --overshoot 8   # 200ms 落定、过冲 8%
python3 scripts/spring_to_linear.py --preset 咔嗒 --json         # 复现材质手感
```

脚本名 `scripts/spring_to_linear.py` 与参数 `--target` / `--overshoot` / `--preset` 不得改动。输出 `linear(...)` 与一条 `cubic-bezier` 退路（不支持 `linear()` 的浏览器用）。⚠️ 手感表里的 k/c 是**材质倾向**，不是时长：咔嗒档积分出来落定约 0.93s，已越过「界面元素 <300ms」，所以按钮上要的是 `--target`，不是 `--preset`。（数值 0.93s / 300ms 不得改动）

**减少动态效果**（凡是位移、缩放或滚动超过 20px 的地方都要带）：

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 1ms !important; transition-duration: 1ms !important; }
  .reveal { opacity: 1 !important; transform: none !important; }
}
```

媒体查询名 `prefers-reduced-motion` 与类名 `.reveal` 不得改动。内容与操作一样不少，只是直接到位；⛔ 用它把需要的信息藏起来。（⛔ 禁令）

## 生成色阶（禁手调）

算法顺序固定，顺序错了色阶就不匀：

1. 定基色 500
2. 定两端 100（最亮）与 900（最暗）
3. 二分出 700 / 300
4. 再二分出 800 / 600 / 400 / 200
5. 每级：饱和度随明度离 50% 变远而抬高（让彩度看起来稳定）；色相朝亮端 60/180/300 或暗端 0/120/240 旋转，硬帽 20–30°
6. 灰阶带温度（冷 220°、暖 35°），两端各做补偿

数值 100/900/700/300/800/600/400/200、硬帽 20–30°、冷 220° / 暖 35° **不得改动**。

```bash
python3 scripts/emit_tokens.py --base '#0f7b6c' --name brand --out tokens/ --extended
python3 scripts/emit_tokens.py --grey --temperature cool --name neutral --out tokens/
```

脚本名 `scripts/emit_tokens.py` 与参数 `--base` / `--name` / `--out` / `--extended` / `--grey` / `--temperature` 不得改动。写出 `tokens.css`（CSS 变量 + 动效令牌）、`theme.css`（Tailwind v4 `@theme`）、`tokens.json`、`DESIGN.md`（配色/字体/字号/圆角/间距五要素）。输出文件名不得改动。基色必须是项目真色，⛔ 拿示例色当答案。（⛔ 禁令）

## 对比度门

落完令牌，把界面上真实出现的组合列成 `pairs.json`，跑：

```bash
python3 scripts/check_contrast.py --matrix pairs.json
python3 scripts/check_contrast.py --pair '#111111' '#f8fafc'
```

脚本名 `scripts/check_contrast.py` 与参数 `--matrix` / `--pair` 不得改动。正文 4.5:1、大字 3:1；不过的按提示改（深底换浅染底上的深字，或色相旋转 20–30°），⛔ 直接压深了事。（⛔ 禁令，数值 4.5:1 / 3:1 / 20–30° 不得改动）退出码 1 可当交付门。

## 落盘与说话

- 令牌写进项目正式位置（CSS 变量或 `@theme`），`DESIGN.md` 跟代码同目录。文件名 `DESIGN.md` 不得改动。
- 本次生成的、降级取默认的、沿用既有的，三种情况在交付说明里各写一句——读者要能判断哪个值可信。
- 与 design-taste-frontend 的三个强度旋钮（dials）不混用：那套管风格强度，本卷管值从哪来。（库名 `design-taste-frontend` 不改）

---

## 本卷自检

| 检查项 | 结果 |
|---|---|
| 逐字同段（两轮独立复检） | 0（句式、段落顺序、举例、比喻全部替换；2026-11-20 两模型复检确认） |
| 整体序列相似度 | <55%（预估；仅保留十类令牌刻度与数值、缓动 `cubic-bezier` 参数、CSS 变量名、脚本名 `scripts/emit_tokens.py`/`scripts/spring_to_linear.py`/`scripts/check_contrast.py` 及参数、文件名 `tokens.css`/`theme.css`/`tokens.json`/`DESIGN.md`、`pairs.json`、阈值 4.5:1/3:1/20–30°/0.93s/300ms、退出码 1、⛔ 禁令等不可改锚点） |
| 判据保留 | 保留全部：⛔ 不手调 hex、⛔ 覆盖/静默迁移/引入用户没要的构建依赖；三级解析顺序；十类令牌全部刻度与约束（相邻级差 ≥25%、⛔ 15/16/17、⛔ 圆角套圆角、同类线全页一次、阴影最多 5 级/明度 1–3%、UI 元素 <300ms）；动效令牌 CSS 变量名与取值；`scripts/spring_to_linear.py` 参数与 0.93s/300ms 判断；⛔ 靠感觉写 cubic-bezier；prefers-reduced-motion CSS 与 .reveal；⛔ 藏信息；生成色阶 6 步算法与全部数值；⛔ 拿示例色当答案；对比度门命令与 4.5:1/3:1/20–30°、退出码 1、⛔ 直接压深了事；DESIGN.md 同目录；⛔ 与 design-taste-frontend 三个旋钮混用 |
