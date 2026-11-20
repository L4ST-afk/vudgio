# 01 移动端物理约束清单：视口、安全区与触控法则 (Mobile Foundations & Viewport)

> 归属：约束满足闭环 · 第 1 步「采集约束」的移动端物理约束收录卷。
> 本卷只收可机判的移动端物理约束，不出视觉方向，不产出风格建议。

## 目录

- [一、约束收录与可判句](#一约束收录与可判句)
- [二、安全区避让约束](#二安全区避让约束)
- [三、触控热区与费茨法则约束](#三触控热区与费茨法则约束)
- [四、0.5px 精细微边框约束](#四05px-精细微边框约束)
- [五、单手操作与拇指舒适区约束](#五单手操作与拇指舒适区约束)
- [六、达成判据与三态结论](#六达成判据与三态结论)

## 一、约束收录与可判句

移动端与桌面 Web 的根本物理差异在于触控介质（手指而非鼠标指针）、有限视口，以及硬件异形屏幕（刘海、打孔、灵动岛、底部操作指示条）。脱离物理特性写代码，必然导致严重交互灾难。

下表把物理事实写成可判句，作为后续达成判据的来源：

| 约束项 | 可判句（机判来源） | 阈值 / 命令 |
|---|---|---|
| 画布与密度 | 移动端设计必须严格基于逻辑点（pt / dp）进行 | 严禁直接使用物理像素（px）进行固定尺寸开发 |
| 字体单位 | Android 字体必须使用 sp（可随系统字体大小缩放设置自适应）；iOS 使用 pt 并支持 Dynamic Type 动态字阶 | sp / pt + Dynamic Type |
| 布局单位 | iOS 布局间距与容器尺寸使用 pt；Android 使用 dp；移动端 Web / H5 优先使用基于 rem、viewport (vw/vh) 或 Tailwind 标准步进 | pt / dp / rem-vw-vh-Tailwind |
| 1px 物理边框 | 在 @2x、@3x 高清屏上，1px 会渲染为 2 到 3 个物理像素的粗线 | 必须采用移动端专属的 0.5px 微边框配方 |

### 1. 逻辑点画布基线表

下表列出各平台代表机型的逻辑画布尺寸、渲染倍率与物理像素，供约束采集时参考：

| 平台 / 机型代表 | 逻辑画布尺寸 (pt / dp) | 渲染倍率 | 物理像素 (px) | 适用场景 （自研）|
|---|---|---|---|---|
| 通用小程序 / 经典基准 | 375 × 667 / 812 | @2x | 750 × 1334 / 1624 | 微信小程序官方基线、经典开发兼容、轻量 H5 （自研）|
| 主流 iOS (iPhone 13-16) | 390 × 844 / 393 × 852 | @3x | 1170 × 2532 / 1179 × 2556 | 当前现存主流 iPhone 普及机型 （自研）|
| 最新 iOS (iPhone 16/17 Pro) | 402 × 874 / 440 × 956 | @3x | 1206 × 2622 / 1320 × 2868 | 现代新项目、设计系统旗舰级组件库基线 （自研）|
| 标准 Android (Material 3) | 360 × 800 / 412 × 915 | xxhdpi (3x) | 1080 × 2400 / 1236 × 2745 | Android 主流机型开发与界面设计基线 （自研）|

### 2. 单位使用铁律

- 布局间距与容器尺寸：iOS 使用 pt，Android 使用 dp，移动端 Web / H5 优先使用基于 rem、viewport (vw/vh) 或 Tailwind 标准步进。（自研）
- 字体尺寸：Android 必须使用 sp（可随系统字体大小缩放设置自适应），iOS 使用 pt 并支持 Dynamic Type 动态字阶。（自研）
- 1px 物理边框：在 @2x、@3x 高清屏上，1px 会渲染为 2 到 3 个物理像素的粗线。必须采用移动端专属的 0.5px 微边框配方。（自研）

## 二、安全区避让约束

异形屏幕（刘海屏、灵动岛、打孔屏、底部 Home Bar）决定了内容不能撑满物理屏幕边缘。（自研）

### 1. 硬件尺寸基线

顶部状态栏（Status Bar）：
- iOS 经典直面屏：20pt（自研）
- iOS 刘海屏 / 挖孔屏：44pt – 50pt（自研）
- iOS 最新灵动岛旗舰系统：54pt – 62pt（自研）
- Android 标准机型：24dp – 36dp（自研）

顶部导航栏（NavigationBar / TopAppBar）：
- iOS 标准导航栏高：44pt（自研）
- Android Material 3 顶部栏高：56dp 或 64dp（自研）

底部安全操作指示条（Home Indicator）：
- iOS 刘海及全面屏固定高度：34pt（横屏时为 21pt）（自研）
- Android 手势横条区域：16dp – 24dp（传统三键导航栏为 48dp – 56dp）（自研）

底部标签栏（TabBar / BottomNavigation）：
- iOS 官方高度：83pt（由 49pt 按钮操作区 + 34pt 底部安全区组成）（自研）
- Android 官方高度：80dp（含触控热区与文字指示）（自研）

### 2. 工程避让配方（CSS Safe Area）

根视口声明必须包含 `viewport-fit=cover`，完整声明为 `<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">`。

顶部安全区内边距（避免内容被状态栏/灵动岛遮挡），使用 `env(safe-area-inset-top)`：

```css
/* 顶部安全区内边距：避免内容被状态栏/灵动岛遮挡 */
.safe-top {
  /* 必须声明顶部安全区内边距 */
  padding-top: max(20px, env(safe-area-inset-top)); /*自研*/
}
```

底部安全区内边距（避免操作被 Home Bar 遮挡并防止手滑退到桌面），使用 `env(safe-area-inset-bottom)`：

```css
/* 底部安全区内边距：避免操作被 Home Bar 遮挡 */
.safe-bottom { /*自研*/
  /* 必须声明底部安全区内边距 */
  padding-bottom: max(16px, env(safe-area-inset-bottom)); /*自研*/
}
```

底部常驻悬浮按钮（Fixed CTA Button）避让，底部内边距使用 `calc(12px + env(safe-area-inset-bottom))`：

```css
/* 底部常驻悬浮按钮避让 */
.fixed-bottom-cta { /*自研*/
  position: fixed; /*自研*/
  left: 0;
  right: 0;
  bottom: 0;
  padding: 12px 16px; /*自研*/
  /* 底部内边距加上安全区，避免被 Home Bar 截断 */
  padding-bottom: calc(12px + env(safe-area-inset-bottom)); /*自研*/
  background: rgba(255, 255, 255, 0.95); /*自研*/
  backdrop-filter: blur(12px); /*自研*/
  border-top: 1px solid rgba(226, 232, 240, 0.7); /*自研*/
}
```

## 三、触控热区与费茨法则约束

手指的生理接触面是一个面积约为 8mm–10mm 的不规则椭圆。视觉元素小不等于触控热区小。（自研）

### 1. 平台最小触控热区要求

- Apple iOS HIG 规范：最小可交互点击区域必须 ≥ `44×44 pt`。
- Google Android Material 规范：最小可交互点击区域必须 ≥ `48×48 dp`。
- 两触控项安全间距：相邻的可点击对象边缘之间必须保持至少 `8pt / 8dp` 的留白，防止误触。（自研）

### 2. 小图标热区外扩配方

当视觉设计需要一个 16px 或 20px 的微小图标（如返回箭头、关闭叉号、清除搜索框图标）时，严禁将容器尺寸锁死在 16px。采用以下两种手段扩大触控面：（自研）

方案 A：容器保留 `44px` 热区，内部居中对齐小图标，使用 `display: flex` 与 `align-items: center`、`justify-content: center`：

```css
/* 方案 A：容器保留 44px 热区，内部居中对齐小图标 */ /*自研*/
.touch-target { /*自研*/
  width: 44px;
  height: 44px; /*自研*/
  display: flex; /*自研*/
  align-items: center; /*自研*/
  justify-content: center; /*自研*/
}
```

方案 B：伪元素向外扩张热区（保持原有布局紧凑），使用 `::after` 向四周扩展 `10px`：

```css
/* 方案 B：伪元素向外扩张热区，保持原有布局紧凑 */
.expand-touch-area { /*自研*/
  position: relative; /*自研*/
}
.expand-touch-area::after { /*自研*/
  content: "";
  position: absolute; /*自研*/
  top: -10px;
  bottom: -10px; /*自研*/
  left: -10px;
  right: -10px;
}
```

## 四、0.5px 精细微边框约束

移动设备 @2x 和 @3x 屏幕如果直接写 `border: 1px solid #ccc`，边框在手机上看会极其粗笨。（自研）

标准工程实现，使用 `transform: scaleY(0.5)` 与 `transform-origin: 0 100%` 压缩边框：

```css
/* 移动端 0.5px 分割线，使用 scaleY 压缩实现细边框 */
.mobile-hairline-bottom { /*自研*/
  position: relative; /*自研*/
}
.mobile-hairline-bottom::after { /*自研*/
  content: "";
  position: absolute; /*自研*/
  left: 0;
  bottom: 0;
  width: 100%;
  height: 1px;
  background-color: rgba(226, 232, 240, 0.8); /*自研*/
  /* 将 1px 边框压缩为 0.5px 视觉效果 */
  transform: scaleY(0.5); /*自研*/
  transform-origin: 0 100%; /*自研*/
}
```

## 五、单手操作与拇指舒适区约束

用户在单手握持手机（尤其是 6.1 英寸以上的大屏手机）时，拇指可触及区域呈现明显的三层同心圆弧分布：（自研）

```
┌─────────────────────────┐ /*自研*/
│     困难触及区 (Hard)    │  <- 放置：辅助性状态、不可点击标题、纯展示数据 /*自研*/
│   (需要调整握姿或双手)    │ /*自研*/
├─────────────────────────┤ /*自研*/
│     伸展触及区 (Stretch) │  <- 放置：次要操作、搜索框、分类 Tab /*自研*/
├─────────────────────────┤ /*自研*/
│                         │
│     舒适自然区 (Natural) │  <- 放置：核心 CTA 提交按钮、底部 TabBar、 /*自研*/
│    (单手拇指无压力覆盖)   │     列表核心高频点击项、主要输入卡片 /*自研*/
└─────────────────────────┘ /*自研*/
```

### 设计落地要求

1. 核心操作沉底：表单保存、立即购买、确认授权等关键转化按钮一律放置在屏幕下方自然舒适区（距离底部 Safe Area `12px` 处），严禁将单一主按钮孤立放在屏幕右上角。（自研）
2. 长列表下滑触发沉浸：当用户在信息流中向上滚动阅读时，顶部导航栏可平滑上收折叠，为内容让出宝贵的一屏阅读垂直视野。（自研）

## 六、达成判据与三态结论

下列判据可直接用于验收，每条带可执行的检查点：

| 判据 | 检查点 / 命令 | 阈值 |
|---|---|---|
| 画布逻辑点 | 检查是否使用 pt / dp，不使用 px 固定尺寸 | 0 处 px 固定尺寸 |
| 顶部安全区 | 检查是否声明 `env(safe-area-inset-top)` | 已声明 |
| 底部安全区 | 检查是否声明 `env(safe-area-inset-bottom)` | 已声明 |
| 固定底部按钮 | 检查 `padding-bottom: calc(12px + env(safe-area-inset-bottom))` | 已声明 |
| 最小触控热区 iOS | 检查可点击项热区 | ≥ `44×44 pt` |
| 最小触控热区 Android | 检查可点击项热区 | ≥ `48×48 dp` |
| 相邻可点击项间距 | 检查边缘留白 | ≥ `8pt / 8dp` |
| 0.5px 微边框 | 检查是否采用 `0.5px` scale 配方 | 已采用 |
| 拇指舒适区主按钮 | 检查主按钮是否置于屏幕下方，距离底部 Safe Area `12px` 处 | 已置于舒适区 |
| 禁令：主按钮右上角孤立放置 | 检查是否存在单一主按钮孤立在屏幕右上角 | 不得存在 |

三态结论：每条判据分为「过 / 不过 / 证据不足」。缺画面或缺材料一律记为「证据不足」，不得直接判「过」。