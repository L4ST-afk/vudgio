# 04 触控输入与软键盘约束：键盘唤起映射与收起模式红线 (Touch Inputs & Soft Keyboard)

> 归属：约束满足闭环 · 第 1 步「采集约束」+ 第 2 步「定达成判据」的触控输入与软键盘约束卷。
> 本卷把软键盘遮挡、输入类型映射、键盘收起与表单单屏法则写成可机判约束，不出方向，不比较输入优劣。

## 一、起点说明

移动端输入体验是整个 App 流失率最高的环节。软键盘弹出时将占据屏幕 `40%` 到 `55%` 的绝对空间，处理不当会造成输入框被键盘遮挡、页面布局被粗暴顶碎、吸底按钮遮挡视线、键盘无法收起等一系列严重问题。（自研）

## 二、软键盘遮挡与视口自适应约束

### 1. 核心高频 Bug 场景约束

- 输入框盲打：点击靠下方的输入框，软键盘弹起直接盖住输入框，用户完全看不见自己打的字。（自研）
- Fixed 吸底按钮撞车：使用 `position: fixed; bottom: 0` 的主按钮在 iOS/Android 键盘弹起时，被系统粗暴顶到键盘正上方，直接盖住正在编辑的内容区域。（自研）

### 2. 标准工程解决方案约束

方案 A：输入框聚焦自动居中滚动（Scroll Into Center View）。在输入框聚焦时，延迟 `300ms` 等待键盘弹起动效完成，再调用 `scrollIntoView({ behavior: 'smooth', block: 'center' })` 将输入项滚动到可见视口的正中央，而非顶部或底部：

```typescript
/* 方案 A：聚焦后延迟 300ms，将输入框滚动到视口正中央 */
const handleInputFocus = (event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => { /*自研*/
  const target = event.currentTarget; /*自研*/
  setTimeout(() => { /*自研*/
    target.scrollIntoView({ behavior: "smooth", block: "center" });
  }, 300);
};
```

方案 B：表单容器底部增加弹性内边距垫高，为滚动容器预留 `350px` 的底部缓冲空间：

```css
/* 方案 B：表单容器底部预留 350px 缓冲，避免软键盘遮挡 */
.form-scroll-container { /*自研*/
  padding-bottom: 350px; /* 预留给软键盘与吸底按钮的富余滚动空间 */ /*自研*/
  overflow-y: auto; /*自研*/
  -webkit-overflow-scrolling: touch; /*自研*/
}
```

## 三、字段类型与键盘外观的精准映射约束

> 铁律：严禁在所有输入项上无脑使用通用的 `<input type="text">`！根据字段业务类型唤起最契合的原生键盘，能消灭 `80%` 的多余切换操作。（自研）

下表把业务场景与 HTML5 属性配置、键盘唤起效果写成可判句：

| 业务输入场景 | HTML5 标准属性配置 | 键盘唤起效果 | 关键增益与体验细节 （自研）|
|---|---|---|---|
| 手机号码 | `type="tel"`；`inputmode="tel"` | 纯数字九宫格大按键（带 `+`、`*`、`#` 符号） | 按钮面积最大，单手按键极速输入，支持粘贴剪贴板号码 |
| 短信验证码 | `type="text"`；`inputmode="numeric"`；`autoComplete="one-time-code"` | 纯数字键盘 | 支持 iOS/Android 系统短信验证码一键填充 |
| 金额与纯数值 | `type="text"`；`inputmode="decimal"` | 带小数点的紧凑数字小键盘 | 杜绝用户误触打入字母或特殊字符 |
| 电子邮箱 | `type="email"`；`inputmode="email"` | 包含 `@` 和 `.` 独立按键的全键盘 | 消除用户在第二层标点符号面板找 `@` 的繁琐路径 |
| 搜索框 | `type="search"` | 键盘右下角主按键变为蓝底“搜索（Search）” | 监听键盘 Enter 事件直接触发搜索，免点页面搜索按钮 |
| 安全密码 | `type="password"` | 密码安全键盘，遮蔽内容，防录屏 | 必须在右侧配备“眼睛”图标，允许用户切换显隐核对 （自研）|

## 四、键盘收起交互行为的三种标准模式约束

键盘不能只管弹出不管收回。必须在页面中提供自然的键盘关闭出口：（自研）

1. 轻触空白处立即收起（Tap to Dismiss）：用户点击表单外的任意空白区域或遮罩层，立即调用 `document.activeElement.blur()` 收起软键盘。
2. 列表滑动即收起（On Drag Dismiss）：在聊天界面、商品评论区、搜索结果长列表中，一旦用户手指开始向上或向下拖动滚动列表，键盘必须自动平滑退下（对齐 iOS 原生 `UIScrollView.KeyboardDismissMode.onDrag`）。
3. 完成动作自动收起：验证码输满 `4` 位/`6` 位、点击了键盘右下角“搜索”或“完成”，系统在触发请求的同时必须自动收起键盘，露出完整的操作反馈结果。

## 五、移动端表单轻量化与单屏法则约束

在移动设备上填写长表单极易让人产生心理窒息感。（自研）

### 核心约束

- 单屏字段 `≤ 5` 项：单页面表单核心字段尽量控制在 `5` 项以内，超出部分采用分步向导（Stepper）或分组卡片折叠承载。
- 占位符严禁废话：占位提示仅用于展示示例格式（如 `例如: 13800000000`），不要在 placeholder 里写大段说明规则。（自研）
- 校验即时化：在输入框失去焦点（`onBlur`）时立即触发局部校验，红字提示直接紧贴在输入框下方，严禁用模态弹窗打断输入心流。（自研）

## 六、达成判据与三态结论

下列判据可直接用于验收，每条带可执行的检查点：

| 判据 | 检查点 / 命令 | 阈值 |
|---|---|---|
| 输入类型禁令 | 检查是否无脑使用 `type="text"` | 不得存在 |
| 手机号码属性 | 检查 `type="tel"` 与 `inputmode="tel"` | 已声明 |
| 短信验证码属性 | 检查 `type="text"`、`inputmode="numeric"`、`autoComplete="one-time-code"` | 已声明 |
| 金额属性 | 检查 `type="text"`、`inputmode="decimal"` | 已声明 |
| 邮箱属性 | 检查 `type="email"`、`inputmode="email"` | 已声明 |
| 搜索框属性 | 检查 `type="search"` 与 Enter 监听 | 已声明 |
| 密码显隐图标 | 检查 `type="password"` 右侧“眼睛”图标 | 必须配备 |
| 聚焦滚动延迟 | 检查 `handleInputFocus` `setTimeout` | `300ms` |
| 聚焀滚动对齐 | 检查 `scrollIntoView` `block` | center |
| 表单容器缓冲 | 检查 `.form-scroll-container` `padding-bottom` | `350px` |
| 轻触空白收起 | 检查 `document.activeElement.blur()` | 已调用 |
| 列表滑动收起 | 检查 `UIScrollView.KeyboardDismissMode.onDrag` | 已对齐 |
| 完成动作自动收起 | 检查验证码输满 `4` 位/`6` 位或点击搜索/完成 | 必须自动收起键盘 |
| 单屏字段数量 | 检查单页面表单核心字段 | `≤ 5` 项 |
| 占位符禁令 | 检查 `placeholder` 是否写大段说明规则 | 不得存在 |
| 校验即时化 | 检查 `onBlur` 局部校验与红字提示位置 | 红字提示紧贴输入框下方 |
| 模态弹窗校验禁令 | 检查是否用模态弹窗打断输入心流 | 不得使用 |

三态结论：每条判据分为「过 / 不过 / 证据不足」。缺画面或缺材料一律记为「证据不足」，不得直接判「过」。