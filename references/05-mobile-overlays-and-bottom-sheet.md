# 05 移动端浮层与底部抽屉约束：浮层选型、三分屏高度与滚动穿透红线 (Mobile Overlays & Bottom Sheet)

> 归属：约束满足闭环 · 第 2 步「定达成判据」的移动端浮层与底部抽屉判据卷。
> 本卷把浮层组件选型、展开高度档位、滚动锁死与点击穿透写成可机判判据，不出方向，不比较浮层优劣。

## 一、起点说明

移动端屏幕面积极其狭小，弹窗与浮层必须极度克制。居中弹窗是打断心流最强烈的武器，在移动端应优先使用从底部升起的半屏抽屉（Bottom Sheet / ActionSheet）。

## 二、移动端浮层组件选型矩阵约束

下表把浮层组件的唤起位置、适用场景与关键约束写成可判句：

| 组件名称 | 唤起位置 | 核心适用场景 | 关键约束与设计禁令 （自研）|
|---|---|---|---|
| 底部动作列表（ActionSheet） | 屏幕底部升起 | 单维度操作分流（如“拍照 / 从相册选择 / 取消”、“分享至微信 / 朋友圈”） | 选项单列垂直居中排布；“取消”按钮必须物理独立分组，用 `8pt` 灰色间距与上方动作区完全切断 |
| 半屏抽屉（Modal Bottom Sheet） | 屏幕底部升起（`30%`/`60%`/`80%`） | 商品多规格 SKU 选择、多维度高级筛选、复杂地址选择、快捷评论面板 | 顶部必须包含拖拽指示条（Drag Handle，`36×4pt`）；支持手指下滑手势平滑关闭；底部必须留足 `34pt` 安全区 |
| 模态确认框（Alert / Dialog） | 屏幕中央垂直偏上（`38.2%` 处） | 涉及账号注销、彻底删除、权限关闭等破坏性二次确认 | 严禁承载超过 `2` 个以上的输入框；严禁用于常规图文长详情展示；必须提供明确取消出口 |
| 轻量轻提示（Toast / Snackbar） | 屏幕下方或中央 | “复制成功”、“已加入书签”等弱状态反馈 | 严禁包含可点击的操作按钮；展示时长严格控制在 `1.5秒–2.5秒` 之间自动平滑淡出，不阻断底层任何操作 |

## 三、底部半屏抽屉的三分屏高度法则约束

为了保证全应用浮层视觉节奏的一致性，Bottom Sheet 的展开高度严禁随意指定固定像素，统一按照屏幕高度的百分比划分三大标准档位：（自研）

- `80%` 高度档位：用于多步骤填写、SKU 选择、复杂树形分类选择；顶部保留 `20%` 原生背景露底，支持点击快速关闭。
- `60%` 高度档位（最通用）：用于中等复杂度筛选、商品图文摘要参数、评论区。
- `30%` 高度档位：用于单选选择器、支付方式二选一、短提示面板。

## 四、滚动穿透与手势死锁的终极治理约束

### 1. 底层页面滚动锁死配方（Body Scroll Lock）

当浮层（Modal/Drawer）展开时锁死 body，记录原有 `scrollY`，将 `document.body.style.position` 设为 `fixed`、`top` 设为 `-scrollY`、`left`/`right` 设为 `0`、`overflow` 设为 `hidden`；浮层关闭时恢复滚动位置：

```typescript
/* 当浮层展开时锁死 body 滚动，记录 scrollY 并固定位置 */
export const lockBodyScroll = () => { /*自研*/
  const scrollY = window.scrollY; /*自研*/
  document.body.style.position = "fixed"; /*自研*/
  document.body.style.top = `-${scrollY}px`; /*自研*/
  document.body.style.left = "0"; /*自研*/
  document.body.style.right = "0"; /*自研*/
  document.body.style.overflow = "hidden"; /*自研*/
};

/* 当浮层关闭时恢复滚动位置 */
export const unlockBodyScroll = () => { /*自研*/
  const scrollY = document.body.style.top; /*自研*/
  document.body.style.position = ""; /*自研*/
  document.body.style.top = ""; /*自研*/
  document.body.style.left = ""; /*自研*/
  document.body.style.right = ""; /*自研*/
  document.body.style.overflow = ""; /*自研*/
  window.scrollTo(0, parseInt(scrollY || "0", 10) * -1); /*自研*/
};
```

### 2. 内部滚动与下拉收起的手势死锁解决约束

- 当抽屉内部有长列表（如评论列表）且当前滚动条位于最顶部（`scrollTop === 0`）时，用户继续向下拉动手指，此时判定为“关闭抽屉意图”，跟随手指位移将抽屉整体向下滑出视口。（自研）
- 当滚动条不在顶部（`scrollTop > 0`）时，向下拉动优先响应内部列表向上回滚，绝不能误触发浮层关闭。（自研）

## 五、点击穿透防范约束

移动端早期因模拟双击缩放存在 `300ms` 点击延迟，直接使用 `touchend` 隐藏遮罩会导致手指点击事件穿透到遮罩底部的真实链接或按钮上：

- 硬规则：统一采用现代标准的 `pointerdown` / `pointerup` 或框架成熟的点击事件处理。（自研）
- 浮层退出过渡动画保护：浮层在执行关闭淡出动画的 `200ms–300ms` 期间，遮罩层必须通过 `pointer-events: none` 阻断一切穿透事件。（自研）

## 六、达成判据与三态结论

下列判据可直接用于验收，每条带可执行的检查点：

| 判据 | 检查点 / 命令 | 阈值 |
|---|---|---|
| ActionSheet 选项排布 | 检查选项单列垂直居中 | 已单列垂直居中 |
| ActionSheet 取消按钮分组 | 检查“取消”按钮是否物理独立分组 | 物理独立分组，`8pt` 灰色间距 |
| Modal Bottom Sheet 拖拽指示条 | 检查顶部是否包含 Drag Handle | `36×4pt` |
| Modal Bottom Sheet 下滑关闭 | 检查是否支持手指下滑手势平滑关闭 | 已支持 |
| Modal Bottom Sheet 底部安全区 | 检查底部是否留足安全区 | `34pt` |
| Alert/Dialog 位置 | 检查屏幕中央垂直偏上位置 | `38.2%` 处 |
| Alert/Dialog 输入框上限 | 检查是否承载超过 `2` 个输入框 | 严禁超过 `2` 个 |
| Alert/Dialog 长详情禁令 | 检查是否用于常规图文长详情展示 | 严禁使用 |
| Alert/Dialog 取消出口 | 检查是否提供明确取消出口 | 必须提供 |
| Toast/Snackbar 按钮禁令 | 检查是否包含可点击的操作按钮 | 严禁包含 |
| Toast/Snackbar 展示时长 | 检查自动淡出时长 | `1.5秒–2.5秒` |
| Toast/Snackbar 阻断禁令 | 检查是否阻断底层操作 | 不阻断底层任何操作 |
| Bottom Sheet `80%` 档位 | 检查多步骤填写/SKU 选择/复杂树形分类选择高度 | `80%`，顶部保留 `20%` 原生背景露底，支持点击关闭 |
| Bottom Sheet `60%` 档位 | 检查中等复杂度筛选等高度 | `60%` |
| Bottom Sheet `30%` 档位 | 检查单选选择器/支付方式二选一/短提示面板高度 | `30%` |
| body 滚动锁死 | 检查 `lockBodyScroll` 实现 | `position: fixed`，`top: -scrollY`，`overflow hidden` |
| body 滚动恢复 | 检查 `unlockBodyScroll` 实现 | `window.scrollTo` 还原位置 |
| `scrollTop === 0` 关闭判定 | 检查抽屉内部列表在顶部继续向下拉动 | 判定为关闭抽屉意图 |
| `scrollTop > 0` 回滚优先 | 检查滚动条不在顶部向下拉动 | 优先响应内部列表向上回滚，绝不能误触发浮层关闭 |
| 点击事件处理 | 检查是否使用 `pointerdown` / `pointerup` 或框架成熟点击处理 | 已统一采用 |
| 遮罩穿透阻断 | 检查关闭淡出动画 `200ms–300ms` 期间遮罩层 `pointer-events` | `pointer-events: none` |

三态结论：每条判据分为「过 / 不过 / 证据不足」。缺画面或缺材料一律记为「证据不足」，不得直接判「过」。