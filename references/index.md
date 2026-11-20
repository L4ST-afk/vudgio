# 卷册索引（按约束生命周期分组）

> 归属：约束满足闭环 · 卷册导航；按约束生命周期分组（采集→判据→求解→手感→平台→验收→路由）。
> 主入口只列命令与门槛，卷的读取时机全部收在这一卷。按组查，不通读；一次只加载当前任务用到的一到两卷。卷的正文仍是判据正本，本卷只给「什么时候读哪一卷」。

## C 采集（约束采集：把用户/品牌/任务/内容/设备/资产/技术七类事实写成可判句）

- `sources.md` — 判据与约束的来源登记；写达成判据前先查出处，按来源与取用边界使用。

## D 判据（定达成判据：从约束挑出可机判的硬判据，带命令/阈值）

- `craft-floor.md` — 质量地板“九查”，界面可交付前的底线判据（对比度、间距、字体、动效、状态、文案、覆盖等）。
- `type-and-polish.md` — 排版与收尾判据（字号层级、行宽与行高、字重、三个文字色、字距、光学尺寸、收尾九条）。

## S 求解（构建满足解：按约束选组件/字/色/动效，先过结构约束再过视觉约束）

- `card-architectures.md` — 卡片承担与四种空间结构，卡内常驻交互控件不超过 2 个，3D 容器与降级判据。
- `ui-effects.md` — 流光、点阵、流动渐变、着色器的三道闸与各自判据，降级顺序与性能硬线。

## M 手感（动效与手感：可中断、速度交接、1:1、橡皮筋等）

- `motion.md` — 动效约束与手感参数；四问决策、时长表、性能红线。
- `interaction-feel.md` — 可中断、速度交接、1:1、橡皮筋与动量投影的交互手感约束。
- `components-motion.md` — 桌面 Agent 组件与动效满足解：组件契约、反馈与降级。
- `desktop-pitfalls.md` — 桌面端踩坑与防御规约：阴影裁切、多窗口、拖拽死锁。
- `chat-interface.md` — 聊天／会话式界面判据：消息流、输入区、状态与可读性。
- `agent-interaction.md` — 桌面 Agent 交互判据：任务控制权、过程可见、可介入可收回。

## P 平台（平台纵深：B 端、移动端、桌面与聊天界面的专项判据）

- **B 端／后台**：`01-design-tokens-and-foundations.md`（索引卷，含 -1／-2 子卷）、`02-primitive-components.md`、`03-overlays-dialog-drawer.md`、`04-composite-components.md`、`05-page-templates-and-archetypes.md`、`06-component-priority-and-anti-patterns.md`、`07-design-system-audit-checklist.md`。
- **移动端**：`01-mobile-foundations-and-viewport.md`（物理约束）、`02-ios-vs-android-design-paradigms.md`、`03-mobile-navigation-and-gestures.md`、`04-touch-inputs-and-soft-keyboard.md`、`05-mobile-overlays-and-bottom-sheet.md`、`06-mobile-archetypes-and-feed-lists.md`、`07-mobile-pitfalls-and-audit-checklist.md`。
- `acceptance.md` — 桌面 Agent UI 质量验收清单：六态六查与证据格式。

## V 验收（判据验收：派独立评审逐条验证，三态结论过／不过／证据不足）

- `review-rubric.md` — P0/P1/P2 严重度、固定走查顺序、评审表与动效 Before/After/Why，交接三要素与未验证标记。
- `workdir.md` — 交付前的工作区与证据核对（`.vudgio` 过程目录、`git diff` 与未跟踪项核对）。

## R 路由（命令路由与索引：命令触发语、首读卷、交付物）

- `routing.md` — 命令面 13 条的触发语、首读卷、顺带卷与交付；无参数菜单；三条纪律与四型关系。
- `index.md` — 本卷，卷册分组导航。
- `naming.md` — 品牌名来历与概念分层；叙事段可换表达，判据不动。
- `open-claude-manual.md` — 历史归档卷（非判据），保留两代桌面架构机制供参考。
