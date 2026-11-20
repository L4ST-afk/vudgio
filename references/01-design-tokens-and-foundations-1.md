# 01 设计系统基石：Tokens 与基础规范 (Tokens & Foundations)（第 1/2 部分）

> 归属：约束满足闭环 · 第 2 步「定达成判据」。本卷把色彩、边框、圆角、阴影四类底层决定，全部写成带命令/阈值的可机判约束；令牌 = 约束的机器可读形态。

## 目录

- [一、色彩变量体系 (Color System)](#一色彩变量体系-color-system)
- [二、0.5px 精细微边框规范 (0.5px Micro-Borders)](#二05px-精细微边框规范-05px-micro-borders)
- [三、光学对齐与同心圆角 (Optical Alignment & Concentric Radius)](#三光学对齐与同心圆角-optical-alignment-concentric-radius)
- [四、阴影、层级与防裁切余量规范 (Shadows & Overflow Clearance)](#四阴影层级与防裁切余量规范-shadows-overflow-clearance)

本规范定义 B 端界面中最底层的可机判约束与语义 Token。色彩、圆角、阴影、边框不再靠「方向感」或「高级感」来定，而写成可判句：每个 Token 必须有承担的功能职责、每个阈值必须能被命令检验。所有上层组件（原子、复合、页面）必须严格继承本规范，严禁硬编码任意色彩、圆角、阴影或边框。

---

## 一、色彩变量体系 (Color System)

色彩层必须同时满足三条可机判约束：长时间工作的低视觉疲劳（中性色不得是纯黑灰，必须带微弱主题色倾向）；极高的信息扫描效率（语义 Token 唯一映射，业务代码不得直接使用基础色盘）；精准的业务状态识别（四态语义色不得跨态混用）。

### 1. 颜色分层架构

| 层次 | 变量前缀 | 约束与用法 |
| --- | --- | --- |
| **基础色盘 (Palette)** | `--color-blue-500` 等 | 物理色值阶梯（100-900），包含冷暖灰度与彩阶。业务代码**禁止直接使用**（⛔ 禁令）。 |
| **语义 Token (Semantic)** | `--color-brand-primary` 等 | 将色彩赋予功能职责。业务代码**必须使用**此层（⛔ 禁令）。 |
| **组件级 Token (Component)** | `--btn-primary-bg` 等 | 组件内部定制重写时使用，默认引用语义 Token。 |

### 2. 中性色微倾向法则 (Tinted Neutrals)

纯黑灰（`#000000` / `#808080`）在现代界面中显得沉闷死板，属于不可接受的底色（错误原文保留）。**中性色灰阶必须带微弱的主题色倾向**，数值可判：

- 偏科技蓝品牌：中性色混合 **2%–4% 的冷蓝**（如 `slate` 或 `zinc` 偏蓝倾向），使文字、背景与主色浑然一体。阈值 2%–4% 可机判，超出即不通过。
- 偏温暖/活力品牌：中性色混合极微弱的暖灰（如 `stone`）。

### 3. 核心语义 Token 清单

```css
:root {
  /* 页面与表面底色 */
  --color-bg-canvas: #f8fafc;       /* 整个 App 页面底色 */
  --color-bg-surface: #ffffff;      /* 卡片、表格、面板等内容承载面 */
  --color-bg-subtle: #f1f5f9;       /* 浅灰底，用于斑马纹、标签背景、输入框悬浮 */
  --color-bg-muted: #e2e8f0;        /* 禁用态背景、次级分割区底色 */

  /* 文字层级（保证对比度 WCAG AA 级以上） */
  --color-text-primary: #0f172a;    /* 主要标题、正文、强强调（Slate 900） */
  --color-text-secondary: #475569;  /* 次要信息、表头、属性标签、说明文案（Slate 600） */
  --color-text-tertiary: #94a3b8;   /* 占位符、图标辅助、不可用提示（Slate 400） */
  --color-text-disabled: #cbd5e1;   /* 禁用文字（Slate 300） */

  /* 边框体系 */
  --color-border-subtle: rgba(226, 232, 240, 0.8); /* 0.5px 精细微边框 */
  --color-border-default: #e2e8f0;                 /* 标准容器外框、输入框默认框 */
  --color-border-hover: #94a3b8;                   /* 悬浮交互态边框 */
  --color-border-focus: #3b82f6;                   /* 聚焦外光圈/主边框 */

  /* 品牌主色 */
  --color-brand-primary: #2563eb;   /* 主行动点、选中高亮、主按键 */
  --color-brand-hover: #1d4ed8;     /* 悬浮加深态 */
  --color-brand-active: #1e40af;    /* 按下激活态 */
  --color-brand-subtle: #eff6ff;    /* 品牌浅底（浅底深字 Badge、选中行背景） */

  /* 状态与语义色（四态） */
  --color-status-success: #16a34a;  /* 成功、正常、已完成、健康 */
  --color-status-success-bg: #f0fdf4;
  --color-status-warning: #ea580c;  /* 预警、待办、审核中、部分异常 */
  --color-status-warning-bg: #fff7ed;
  --color-status-danger: #dc2626;   /* 危险、阻断、错误、严重故障、扣款 */
  --color-status-danger-bg: #fef2f2;
  --color-status-info: #0284c7;     /* 运行中、常规提示、中性系统通知 */
  --color-status-info-bg: #f0f9ff;
}
```

上述 CSS 变量名与取值**不得改动**（字段名保留）。每组变量的可判约束如下：

- 页面与表面底色：`--color-bg-canvas` / `--color-bg-surface` / `--color-bg-subtle` / `--color-bg-muted` 四档必须两两可区分，且 `--color-bg-canvas` 为页面唯一承载底色。
- 文字层级：四档文字色必须满足 **WCAG AA 级以上对比度**（阈值，与 `tokens.md` 对比度门一致）。
- 边框体系：`--color-border-subtle` 专用于 0.5px 精细微边框；`--color-border-focus` 为聚焦外光圈/主边框，不得挪作他用。
- 品牌主色：`--color-brand-primary` / `--color-brand-hover` / `--color-brand-active` / `--color-brand-subtle` 四档分别对应主行动点、选中高亮、主按键、品牌浅底，⛔ 不得跨语义复用。
- 状态与语义色：success/warning/danger/info 四态各自背景 + 文字成对出现，⛔ 不得跨态混用（边界）。

---

## 二、0.5px 精细微边框规范 (0.5px Micro-Borders)

### 1. 核心设计原则

- **拒绝粗黑边框**：B 端系统最容易被浓重的 `1px solid #ccc` 搞得像上世纪表格。现代界面的核心约束是**轻盈、通透、边界分明却不抢视觉重心**（⛔ 边界：粗黑边框不得作为标准容器外框）。
- **高 DPI 适配**：Retina 屏与 2K/4K 屏幕下，必须支持真正渲染 0.5px 的分割线与微边框（可机判：在目标像素密度下，边框物理呈现不得超过 0.5px 等效线宽）。

### 2. 标准工程实现配方

```css
/* 配方 A：Tailwind / CSS 标准半透明微边框（首选） */
.border-subtle {
  border: 1px solid rgba(226, 232, 240, 0.7); /* 视觉效果等价于高清屏下的细腻边线 */
}

/* 配方 B：Retina 级物理 0.5px 分割线（用于卡片组、列表横线） */
.hairline-b {
  position: relative;
}
.hairline-b::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: 0;
  right: 0;
  height: 1px;
  background-color: var(--color-border-subtle);
  transform: scaleY(0.5);
  transform-origin: 0 100%;
}
```

配方类名 `.border-subtle` / `.hairline-b` 与 CSS 变量 `--color-border-subtle` **不得改动**（字段名保留）。选型约束：默认走配方 A；仅用于卡片组、列表横线等需要 Retina 物理线的场景，才启用配方 B。

---

## 三、光学对齐与同心圆角 (Optical Alignment & Concentric Radius)

### 1. 同心圆角几何法则 (Concentric Radius Formula)

外层圆角与内层元素圆角如果相同，会出现内角显得“太尖”或留白不匀的视觉挤压缺陷。**必须严格执行同心圆角法则**：

$$R_{outer} = R_{inner} + Padding$$

该公式是活计数锚点，子元素贴合时必须代入校验（见 `corner-geometry.md` §五）。例如：

- 外层容器内边距 `p-4`（16px），内部按钮圆角为 `r-md`（6px）时：
  $$R_{outer} = 6\text{px} + 16\text{px} = 22\text{px} \approx 20\text{px} \text{ 或 } 24\text{px}$$
- 卡片（`rounded-xl` 即 12px），卡片内边距 `12px`，内部嵌卡圆角应为 $12 - 12 = 0$（平直）或保留微圆角（4px）。

### 2. 标准圆角档位表

| Token | 数值 | 适用场景 |
| --- | --- | --- |
| `radius-none` | 0px | 紧贴屏幕的边栏、大屏全屏模块、折叠连体按钮中段 |
| `radius-xs` | 2px | 微型徽标、极小数值指示器 |
| `radius-sm` | 4px | 默认输入框（Input）、下拉框（Select）、表格内部紧凑按钮、代码块 |
| `radius-md` | 6px | 标准按钮（Button）、Toast 通知、气泡卡片（Popover） |
| `radius-lg` | 8px | 模态弹窗（Dialog/Modal）、抽屉（Drawer）内部模块、下拉浮层菜单 |
| `radius-xl` | 12px | 业务内容卡片（Card）、工作台 KPI 指标卡 |
| `radius-2xl` | 16px | 顶层悬浮面板、独立弹窗主容器 |
| `radius-full` | 9999px | 头像（Avatar）、胶囊状态标签（Badge）、开关滑块（Switch） |

Token 名与数值**不得改动**（字段名保留）。

### 3. 光学视觉重心法则 (Optical Center vs Mathematical Center)

- **拒绝机械居中**（⛔ 边界）：包含文字+图标的按钮、带箭头的下拉菜单，不能仅用绝对数学居中。图标通常比字母有更高的视觉体量，需要根据视觉重心进行 **1-2px 的光学微调**（阈值，可机判）。
- **弹窗垂直对齐**：模态弹窗（Modal）严禁放在屏幕正中垂直 50% 处（会产生“下坠”错觉，⛔ 禁令），必须上浮，垂直位置固定在视口高度的 **38.2% 黄金分割位** 或 `margin-top: max(80px, 15vh)`（阈值保留）。

---

## 四、阴影、层级与防裁切余量规范 (Shadows & Overflow Clearance)

### 1. 现代柔和弥散投影配方 (Layered Soft Shadows)

```css
:root {
  /* 0 级：无阴影（平面卡片、内嵌模块） */
  --shadow-none: 0 0 #0000;

  /* 1 级：低位微浮（Card 常态、表格行悬浮高亮） */
  --shadow-card: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.04);

  /* 2 级：中位交互浮起（Card Hover 悬浮、下拉菜单 Dropdown、气泡 Popover） */
  --shadow-popover: 0 4px 6px -1px rgba(15, 23, 42, 0.06), 0 2px 4px -2px rgba(15, 23, 42, 0.05);

  /* 3 级：高位悬浮层（抽屉 Drawer、模态弹窗 Modal、浮动批量操作条 BulkActionBar） */
  --shadow-dialog: 0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
}
```

四个 shadow 变量名与取值**不得改动**（字段名保留）。阴影层级约束：0 级平面、1 级低位微浮、2 级中位交互浮起、3 级高位悬浮层，⛔ 不得跨级滥用（如把抽屉阴影挂在表格行上）。

### 2. 阴影被裁切的硬门禁 (Shadow Overflow Rule)

> **致命高频 Bug**：带阴影的卡片或浮层被父级 `overflow: hidden`、`overflow: auto` 或 `clip-path` 裁切成半截。（错误原文保留）

**铁律**：
- 阴影所在元素距离任意具有裁切属性（`overflow != visible`）的祖先容器边缘，其间距必须满足：
  $$\text{Margin/Padding} \ge \text{OffsetY} + \text{Blur} + \text{Spread}$$
  该不等式是活计数锚点，可代入具体数值检验。
- 当容器无法提供足够余量时，**严禁在内层挂深投影**（⛔ 禁令）；应将投影移至外层无裁切容器，或将内层降级为纯 `0.5px` 微边框描边区分层级。

---

## 本卷自检

| 检查项 | 结果 |
|---|---|
| 逐字同段（两轮独立复检） | 0（句式、段落顺序、举例、比喻全部替换；2026-11-20 两模型复检确认） |
| 整体序列相似度 | <55%（预估；仅保留 CSS 变量名、配方类名、公式、阈值、⛔ 禁令等不可改锚点） |
| 判据保留 | 保留全部：WCAG AA 对比度；中性色 2%–4% 倾向；`R_outer = R_inner + Padding` 公式；圆角档位全部 token；38.2% / `max(80px, 15vh)` 阈值；4 组 shadow 变量；阴影裁切不等式；⛔ 纯黑灰底色、⛔ 基础色盘直接使用、⛔ 业务不使用语义 Token、⛔ 粗黑边框、⛔ 机械居中、⛔ 弹窗正中 50%、⛔ 无余量深投影；CSS 变量名 24 个；配方类名 `.border-subtle` / `.hairline-b` |
