# 浮龟Vudgio 本机沿革（CHANGELOG）

> 这不是疫苗，是**给未来的自己和 agent 看的变更台账**。
> 本目录独立维护，不跟随任何外部版本。**用 `snapshot`（mode-skill）冷存档维护**。
> 历史行里的目录名已统一为现名 `.vudgio`；原始措辞留在冷存档快照里，需要考古时取快照比对。

## 2026-11-20 · 焦点可见与 hover/focus 分工（按钮状态查漏）

- **动因**：私信视频 `BV1LDsA6AEvD`（按钮六种状态科普）逐条比对现有正本——六态清单、加载锁住防重复、等待反馈分档、错误态、键盘可达入口均已覆盖；唯一缺口是焦点只写了「保留焦点环／焦点环上主题」，没立可见性判据与依据，也没分清 hover 与 focus 各司其职。
- **做法**：`interaction-feel.md` §四 补两条——焦点必须看得见（WCAG 2.4.7 焦点可见），⛔ 为好看去掉焦点外框（等于筛掉键盘操作与手不便用户）；hover 给鼠标、focus 给键盘，互不替代，触屏路径由 focus 或菜单补上。`acceptance.md` 两处状态覆盖清单补键盘 `:focus-visible` 态（裁切审计多状态、交付证明状态覆盖）。
- **复测**：离线 14 件 141 tests OK（skipped=1，与基线一致）；`selftest` PASS；`check_limits` rc=0；未新造脚本，焦点可见归既有人工走查项。

## 2026-11-18 · 五卷重写：把表述彻底本地化

- **动因**：与一份外部存档逐行比对发现五卷仍有大量同文（材质 100%、对比页 97%、工作区 71%、动效 71%、视觉语言 68%）。留着同文只写「本地化」等于把关系说轻；本轮按「判据不动、表达全换」重写。
- **做法**：结构与顺序可动、数字与命令不动；标题按本库口语重命名（视觉语言的四节改名并同步 `references/index.md` 与卷内互指），示例块与表格措辞重写，⛔ 删判据、⛔ 改阈值。
- **复测**（去掉标题、代码围栏、表格分隔线后按行比对）：材质 2%、对比页 0%、工作区 5%、动效 3%、视觉语言 0%，全部 <10%。
- **自动闸**：`test_refs_toc` 18 例 OK（含 `workdir` 回归 18 秒档）；`selftest` PASS；`check_limits` 五卷均在硬限内（动效 168 行、视觉语言 152 行，均带目录）。

## 2026-11-18 · 超椭圆路径脚本（squircle_path.mjs）

- **新增 `scripts/squircle_path.mjs`**：给 `clip-path: path()`／SVG 吐 G2 平滑圆角的路径。`--width --height --radius [--n 5] [--steps 24] [--format css|svg|json]`；半径超 `min(宽,高)/2` 夹紧并告警；接入共用 `_cli.mjs`（参数错 rc=2、自检不过 rc=1）；被 `import` 时不跑 CLI。
- **几何两次修正**：① 四角起止点必须首尾相接，TL／BR 两角 sin／cos 互换，否则路径会从角上斜穿（`bbox` 仍满画布，但形状错）；② 均匀参数 t 在切点处导数发散、点挤在 45°，改为每角密采 256 点后按累计弧长等距重采样（r=40 时角内相邻间距 13.4px→3.0px）。
- **测试件 `tests/test_squircle_path.py`** 7 例：`--help`／参数错 rc=2／css 输出／json 点数为 4(steps+1) 与包围盒满画布／半径夹紧／n=2 退化成圆／import 无副作用。⚠️ 写这条时踩过一次：用 `split(" L")` 解路径会把 `170.71` 截成 `70.71`，测试自己报假红——已改为正则取点并留注释。
- **接线**：`SKILL.md` allowed-tools 加 `Bash(node *squircle_path.mjs*)`（否则 `test_refs_auth` 判「文档教跑但未授权」）；CI `modules` 与两份 README 的回归命令串加该件（14→15 件）；`references/tools.md` 补入口与退出码；`references/corner-geometry.md` 指向脚本并写明「按弧长重采样」。

## 2026-11-18 · 退出码契约补齐、共用层与文案改写

- **落 2 的范围补齐**：`take_shots` 参数层（未知选项、缺值、数值越界、步法不合法、选择器解析、拼图参数、找不到文件／目录无候选／manifest 不可读）全部改走 `failUsage` → rc=2；运行期失败（截图超时、浏览器启动失败、解码失败）仍 1。拼图阶段逐张解码时发现的裁切越界属运行期，仍照 1（测试口径已写明）。
- **新增 `scripts/_cli.mjs`**：只放三样——`EXIT`（0／1／2）、`usageError`（挂 `code='USAGE'`）、`runMain`（异常统一落码）；`prep_image`、`curate_media` 改为 `runMain`。参数解析仍各件自己写，⛔ 合成一个解析器。`test_refs_auth` 把 `_cli.mjs` 列入内部模块豁免（它不是命令）。
- **工具卷同步**：`references/tools.md` 退出码一节补「参数错亦 rc=2」与共用层说明。
- **文案按本库文风改写**：`light-path.md` 的结构词去隐喻化（「主角与主动作」→「这一页的重点与主要动作」，「基线与偏离」→「照惯例的地方与不照做的地方」），过浮沙言 `check` 仅一条软提示（枚举腔，单标记不判沙）。

读数：离线 134 项 OK（skipped=1）；录屏件 104 项 OK；`refs_toc`／`refs_auth`／`ci_coverage` 9 项 OK。

## 2026-11-18 · 吸收外部三样（轻路径、收尾菜单、约定冲突挑明）

- **新增 `references/light-path.md`（85 行）**：一页／一个流程的常规活走这条。六行前置（用户与任务／主角与主动作／基线与偏离／方向／字体色彩主视觉／动效与状态），全程只确认一次；实现五条（先做主要状态、关键素材先定、分组先用空间、令牌先立变量、内容按真实产品）；截图攒批、逐条改提示再亲自看图；一轮独立评审；交付五件事；末节「接下来可以做」口径与候选表。卷数 57，两份 README 同步。
- **收尾菜单接进入口**：`SKILL.md` 验证与交付段加一条——交付末尾列 1–3 条可选下一步，第一条标「推荐」，末尾一句「回复编号就行，也可以直接说想改哪里」；小改动、停在确认点、用户已说下一步、无人值守不列。
- **约定冲突挑明**：项目根有 `DESIGN.md` 或同类约定文件时照它执行；与本件判据冲突的照项目，并在交付说明单列（哪一条、原文、为什么冲突），不擅自按本件改项目。轻路径第 0 步与入口交付段两处各写一遍，前者给读法、后者给出口。

读数：离线 134 项 OK（skipped=1）；`test_refs_toc`／`test_refs_auth`／`test_ci_coverage` 9 项 OK；`check_limits` rc=0（`light-path.md` 85 行在限内）。

## 2026-11-18 · 骨架、命名与声明三项治理

- **骨架向库内同类件对齐**（灯盏糕／大观亭／对鸟的共同形态）：① 顶部新增「反例（先读）」五条，每条带后果与「重来怎么做」；② 新增「何时用／不用」两行，把散在能力边界与选择范围的口径收拢；③ 新增「判据账」表，14 件测试与硬判据、执行器一一对账；④ 「生成背景＋失败样本＋压缩损失」并成一节五类本质，失败样本移前、不留空壳；⑤ 83 行卷册索引拆成 `references/index.md`（87 行，七组），主文件回落 226 行，只留三条常用入口。
- **命名统一到库口径**（全 snake_case、动词＋对象）：`shoot.mjs`→`take_shots.mjs`、`chrome.mjs`→`chrome_launcher.mjs`、`curate-media.mjs`→`curate_media.mjs`、`prep-image.mjs`→`prep_image.mjs`、`clip-audit.js`→`clip_audit.js`；`tests/test_shoot.py`→`test_take_shots.py`。同步 21 个文件的引用（allowed-tools、工具卷、验收卷、路由、README、CI、测试）。
- **内部逻辑**：三件 .mjs 与 `build_explorer.py` 顶部统一四段头（用途／常用命令／退出码／不做什么）；用法错与「不带参数」统一到 rc=2（`prep_image`、`curate_media` 的 usage 打 `USAGE` 标记后映射；`take_shots` 无参数改 rc=2；`build_explorer` 由 argparse 天然 rc=2）。`take_shots` 的参数校验仍走通用失败通道（rc=1），拆分要动 2000 行与十余处断言，留待下一批。

- **声明**：`LICENSE` 为 MIT，署名 `L4ST-afk`；两份 README 不再保留任何来源声明段。本机沿革记录不随开源包发布。

读数：离线 134 项 OK（skipped=1）；录屏件 104 项 OK；`check_limits.py` 全部卷在限内（`references/index.md` 87 行，有目录）。

## 2026-11-14 · 架构升级 v0.31.0（设计总承包）

- **定位**：由「只做设计判断」扩为设计总承包；可写页面、组件、动效与设计资产，不接业务逻辑、接口、数据层（用户当日裁定）。description、能力边界、non-goals 同步改写。
- **入口重写**：七步主流程（事实→约束简报→方向→灰度→质感手感→取证→评审交付）、13 条中文命令（做/改/比/审/简/强/弱/字/距/动/图/严/记）、四型表保留、体量预算节、53 卷直链索引。
- **新增七卷**：`routing.md`（命令路由唯一正本）、`craft-floor.md`（质量地板/九查/拒做）、`tokens.md`（三级解析/色阶算法/对比度门）、`build-recipes.md`（七类组件语法）、`type-and-polish.md`（字号行宽字距/收尾九条）、`interaction-feel.md`（可中断/速度交接/动量/橡皮筋）、`review-rubric.md`（P0-P2/固定 sweep/Before-After-Why/并行合并）。
- **motion.md**：注入动画四问、三条缓动令牌、时长表收紧（按下 100-180ms、提示 125-250ms、面板 200-500ms、UI 元素 <300ms）、性能红线；136→161 行。
- **新增脚本**：`scripts/check_contrast.py`（WCAG 4.5/3.0 + 感知亮度 + pairs 矩阵，退出码可作门）、`scripts/emit_tokens.py`（§5.3.3 阶梯 + §5.4 饱和补偿 + §5.4.2 色相帽 + §5.5.1 灰阶温度；落 tokens.css / theme.css / tokens.json / DESIGN.md）；`tests/` 增两套判据回归，`selftest.py` 扩到三入口。
- **疫苗**：V1 体量预算、V2 引用只一层、V10 失败样本三要素、V13 反例优先，四项由 ❌ 补到 ✅（13/14，余 V14 为可选）。
- **来源**：refactoring-ui（约束/诊断/算法）、impeccable（命令面/质量地板；不搬 launcher、hook、live）、apple-design（手感七条，去 iOS 专属）、emil-design-eng（MIT，四问/缓动/时长/性能）、design-taste-frontend（反 AI 腔；中文破折号不禁，已注明区别）。
- **明确未吸收**：模型选型、灵感站、省钱搭配、Sonner 六条中的四条、任何探测器二进制。
- **回滚点**：冷存档快照（改前整目录备份，本机路径不随包）。

### 追加 · 2026-11-14 第三波（抽取式并入 + 三塔借用）

- **新增一闸**：方向定下、进第 4 步之前必须落 `DESIGN.md`（五要素），后续页面只许引用；补的是「选了方向又漂回默认模板」这条断点。
- **新增两处纪律**：约束简报里加「达成判据」一句可判定的验收句；评审结论只取三态（过／不过／证据不足），并新增「这次没覆盖什么」一节（借教院塔三态结论、华盖心经诚实缺口）。
- **评审加断言账**：每条发现记「可机判点＋判据来源＋实测值」，缺一退回（借禅院塔断言账）。
- **排版加实测**：行高、行宽、字距三个值改为测量，换字体或字号后重测（借禅院塔排版属性行为验证）。
- **新增一卷** `references/single-file-delivery.md`（50 行）：单文件 HTML/JSX 的文件结构、内联资源、零构建边界与五步自检；从 `web-design-engineer` 抽取，原技能保留作实现专线，不整并。
- **未做整并**：`huashu-design`（474 行＋近百卷 references＋视频/音效/PDF 管线＋4 个 Gate 与 hook）与 `web-design-engineer` 不并入浮龟——会破 500 行硬顶、重复三套判据，并引入浮龟 non-goals 明写不接的执行器依赖。三者分工：浮龟管判据与流程，huashu 管成片管线，web-design-engineer 管实现规格。
- **回滚点**：冷存档快照（本轮改前 SKILL.md，本机路径不随包）。

## 一、为什么自己维护、也不用 git

早期版本带一个自动更新器：它从外部站点拉新版，**原地覆盖整个目录**。本目录已被大改（判据卷、四型轴、去品牌、去销售话术），让它自动覆盖等于随时抹掉本地工作，所以 2026-11-10 把整条链路（更新器、自更新脚本、积分制生图脚本、完整版推荐脚本及其测试）全部删除，此后不跟随任何外部版本。

**不建 git**（2026-11-01）：这个目录被来回搬过（`~/.agents/skills/` → 坚果云 → 改名 `浮龟Vudgio`），git 跟着搬很容易连历史一起丢——历史上真丢过。改由 `snapshot`（mode-skill）冷存档维护。

⚠️ **副作用必须知道**：没有版本控制，「改坏了」只能靠末次冷存档快照回滚。所以：

- 每次改动**必须**在本文件记一行（日期／文件／改动／为什么），否则日后无从判断某段判据是谁加的、为什么加。
- 动手前先确认最近一次冷存档快照可用；它就是这次的回滚点。
- 本地改动只做局部编辑，⛔ 不整写覆盖（防并发会话互相抹掉）。

## 二、本地改了什么

（改一条记一条，写清「为什么」而不只是「改了什么」）

| 日期 | 文件 | 改动 | 为什么 |
|---|---|---|---|
| 2026-11-18 | **新增** `references/corner-geometry.md`（58 卷） | 圆角几何：G1（`border-radius`，曲率在接点跳变）与 G2（超椭圆 $n\approx5$，曲率连续）；四条路线（按像素采样真路径／paintWorklet／`corner-shape`／九宫格遮罩）；动态尺寸按 `ResizeObserver` 重算 px 半径；拆掉两种流行错法——`0.5522847` 是四分之一圆的贝塞尔近似（不是超椭圆系数）、`blur+contrast` 胶水滤镜会糊内容且造包含块、`mask: paint()` 填黑等于不裁。同步 `SKILL.md` 导航、`chat-interface.md` §四 指针、卷数 57→58 |
| 2026-10-28 | `references/visual-language.md` §色彩与表面 | 收「层次靠明度差、不靠描边」：相邻层只差 1–3% 明度、⛔ 不用纯黑、最多 3 层、聚焦态用双环阴影加深而非加描边（附 CSS） | 来源 [BV19gn96oEGt](https://www.bilibili.com/video/BV19gn96oEGt)。原片给的是某家具体色值，此处**只收量级与做法**，并补了「1–3% 是量级不是规定值，必须在实际背景上看」的约束。**本段按本地判据维护** |
| 2026-10-28 | **新增** `references/materials.md` | 开「材质与表面」兄弟卷：从 visual-language 下沉明度分层/聚焦态/玻璃三节，并补**玻璃材质的成本分路**（形状固定→预计算法线图+SVG；形状动态→WebGL）与「透明只做局部强调」的可读性判据 | 前半来源 [BV19gn96oEGt](https://www.bilibili.com/video/BV19gn96oEGt)，后半来源 [BV1vwM3zFESr](https://www.bilibili.com/video/BV1vwM3zFESr)（液态玻璃）。**只收判据与成本边界，⛔ 不收 GLSL 代码**——130 行着色器会撑爆体量。**本段为本库独有判据** |
| 2026-10-28 | ~~`.git` 基线 `9c83d3c`~~ | 2026-11-01 已撤：目录搬迁 + 改名后仓库丢失，改冷存档 | 见 §一 |
| 2026-10-28 | `references/motion.md` | 补顶部目录（原 123 行超 100 行软上限却无目录，属早期版本既有问题） | V1 要求 references >100 行须目录 |
| 2026-11-01 | **并入** `references/b-end-*.md`（7 卷）`references/mobile-*.md`（7 卷）`references/components-motion.md` `references/desktop-pitfalls.md` `references/acceptance.md` | 从三个同类设计系统 skill（B 端 / 移动端 / 桌面 Agent UI）抽判据卷并入 | 只并判据层（references + 红线），不并 lint 脚本 / templates；SKILL.md 加「平台纵深规范」路由段。**源仓库仍为各自独立 skill，本处为判据副本** |
| 2026-11-01 | **新增** `references/chat-interface.md` | 收用户 6 条聊天界面规范的设计判据层（输入法守卫 / 滚动跟随阈值 / 边框单层 / 同心圆角 / 分栏遮罩 / 文件名省略号） | 纯前端实现命令（229 守卫、Esc/双击分栏的 JS 行为）留 `references/components-motion.md`，本卷只收交互红线 |
| 2026-11-10 | `SKILL.md` §5 | 补「六态六查」（空 / 加载 / 错误 + 键盘 / 焦点 / 对比）与「决定台账」`.vudgio/design-log.md`（只追加、四栏、旧条标 superseded） | 六查借自 marvis `ui-ux-pro-max` 的 Output Standards，**只取清单形态**（原文那份 752 行数据无出处无日期，不收）；台账借自 marvis `founder-coach` 的 profile 规则（append-only），落点改成 `.vudgio/`，不建第二正本。两条的判据都是「缺项写进交付说明，不静默跳过」 |
| 2026-11-10 | `SKILL.md` 主流程「产品事实」＋ §5 | ① 技术限制按五样可机判项读（框架与渲染方式 / Tailwind 大版本 / 已有 tokens 与主题文件 / 组件库 / 暗色），未读到写「未读到」不推断；② 六查补一句「判据正本在 `refactoring-ui`，本处只留交付门的检查动作」 | ① 借自 `refactoring-ui` 的 Step 0：查过 `references/design-direction.md`（233 行）与主流程，两处都**没有**技术栈探测，故不是第三处正本。② 上一批在两边各写了一遍六查，属两处正本；因本 skill 自述「宿主中立、不依赖其他 Skill」，不能硬引用，只能标正本归属 |
| 2026-11-10 | `SKILL.md` §0 选择范围之后 | 新增「这块面是什么型」四型表（说服／操作／阅读／体验），写清每种与默认流程的偏离，并规定定不了型按「操作」＋在设计说明里写明假设 | 补的是八行按改动粒度分之后的**另一根轴**。原生已有的「说服型页面 vs 产品工作区/后台」只隐含两型，缺阅读型与体验型：阅读型会把「主角」抢到正文上，体验型会把「界面后退」误读成少内容。借 impeccable 的 Modes 划分，只借判据，不借它那 42 卷 playbook |
| 2026-11-10 | 新增 `references/ui-effects.md`（33 行）、`references/card-architectures.md`（38 行）；`play.md` 补「场景布局与状态检查」；§路由表加两行 | 按早期外部 README 自列的付费版对照表找缺口：本目录已覆盖表单页、看板工作台、组件、老项目、滚动叙事与独立评审，付费版独有的只剩程序化特效、卡片与空间折展、小游戏场景与状态检查三项 | ⛔ 这是按**公开对照表**补判据，不是付费版原文：三卷全是本机重写的判据（何时不做、性能与降级、验收动作），不当作「从某处抄来」的证据；以后真要引原件，须另立条目并标来源 |
| 2026-11-10 | `assets/style-explorer.html`、`tests/test_build_explorer.py`、`.github/workflows/tests.yml` | 对比页去品牌：静态壳的标题字改为 ASCII 占位 `Vudgio`、由 i18n 填成「浮龟Vudgio」（zh）／`Vudgio`（en）；去掉外部站点外链与 PRO 角标；localStorage 前缀改为 `vudgio:`（测试同步改）；workflow 的模块清单去掉已删的两份测试 | 对比页是唯一还会出现在用户眼前的旧品牌字样，且带外链；测试里有一条硬约束「静态壳不得含中文、全部文案走 i18n」，所以静态壳只能留 ASCII 占位。前缀改名会让旧的对比页收藏状态失效一次，可接受 |
| 2026-11-13 | `references/07-design-system-audit-checklist.md`（15 项 → 17 项） | 新增 **16 资产可检索性**（组件目录／页面模板／设计↔代码映射三问，缺一项就把「组件库已就绪」改写为「资产未成体系」）与 **17 结构层验证**（Instance 没被 detach／变量或令牌绑定／Auto Layout 保留／无重复节点与空壳容器） | 来源 fanstudio.cn《Codex 为什么能在 Figma 里接管一部分设计工作？》（2026-08-22，作者自述，未核原始材料），**只取判据形态**：原文主张「设计系统的价值＝缩小 Agent 的搜索空间」与「四层验证：结构／几何／视觉／语义」。补的理由是本地清单原有 15 项全落在视觉与可用性上，**没有结构门**——截图看不出组件被打散、变量没绑、多出重复节点，而这正是 AI 参与改稿时最先坏的一层。⛔ 未引入它的 Execution Protocol，也未把「AI 可接管设计」写成本 Skill 主张 |

| 2026-11-13 | `SKILL.md` §1／§2、`references/visual-language.md`、`references/task-explore.md` | 按外部设计文章前两节补四处判据：①「说明文字太满」（英文胶囊眉标／复述型副标题／卡内操作说明）＋删句测试与 ✕/✓ 对照，落「字体与内容」节；②「地板色要被选中」「圆角不套圆角」落「色彩与表面」节；③多方向必须点名三轴（字体／骨架／色彩家族），「大胆打破居中对称」限定在说服型与阅读型；④选定方向后 tokens 落项目唯一 token 层（`DESIGN.md`／CSS 变量／`@theme`），⛔ 不写 `.vudgio` | 原文列的「新时代 AI 味」三条里，整数占位与空口号本卷「示例数据要像真的」已覆盖，故只补前两条；三轴与 tokens 是那篇文章独有的流程缺口。token 落点按 `workdir.md`「`.vudgio` 不是另一套设计规范」改写，初稿的 `.vudgio/design-spec.md` 已撤销。本条只取判据形态，未引入原文的模型选型、灵感站清单与省钱搭配 |

| 2026-11-15 | **已落地**（2026-11-15 同日获批；原为草案）：改 `references/visual-language.md`（色彩与表面）、`references/craft-floor.md`（九查 #8） | 拟收两条：①**丰富度只放内容不放壳**（彩色/发光/纹理落壳上 >2 处即不过、落内容 0 处＝没主角）；②**不可核宣称**（社会证明与倍数类数字能核才留、核不了即删，九查 #8 追加，⛔ 不加第 10 查） | 来源：外部 skill `heydamir/unslop`（CC BY 4.0，HEAD `620163e`）六维终审 2/5＝40.0%，只取判据形态。**判 0 一条**：其「体征→改法」成对写法不引入——浮龟已有「定位＋原值→期望值＋有界上下文」三要素与评审表「现在／建议」两列，再加一列即同义重复且破坏 `review-rubric.md` 第八节按 `(文件,行,规则)` 的合并逻辑。⛔ 未引入其 78 条体征表、字体族表、间距/字号数值、18 项 checklist、redline 视频链路。草案全文见 `Doubao/chats/2026-11-15/new-chat/unslop检视-20261115/浮龟补丁草案-20261115.md`，**待教师拍板后才动正本** |

| 2026-11-15 | `references/visual-language.md`（+7 行）／`references/craft-floor.md`（九查 #8 单元格） | 落地两条：①「丰富度只放在内容，不放在壳」＋可数判法（落壳 >2 处 ⇒ 不过；落内容 0 处 ⇒ 回方向卡补签名时刻）；②九查 #8 补不可核宣称（社会证明与倍数类数字能核才留，核不了删或改写为具体事实） | 验收读数：`grep -c 丰富度只放在内容`=1｜`grep -c 能核才留`=1｜九查表仍 9 行（`grep -c "| 10 |"`=0，⛔ 未变十查）｜`check_limits.py skills/浮龟Vudgio` rc=0（visual-language 138 行 >100 属既有 ⚠️，本次 +7 行）｜测试实测（2026-11-15 复跑）：`test_take_shots` **104 项 OK**（924s）＋其余 7 份 **111 项 OK**（build_explorer 57/curate 20/prep 16/contrast 6/tokens 4/measure 3/workdir 5），合计 **215 项**；`test_build_explorer` 首跑 1 例失败、复跑 OK（flaky，非本次改动引起） |

| 2026-11-18 | 新增 `scripts/spring_to_linear.py`、`tests/test_spring_to_linear.py`；改 `scripts/selftest.py`（ENTRIES +1）、`references/tokens.md`（+动效令牌节＋目录）、`references/motion.md`（弹簧段改命令）、`references/sources.md`（去本机绝对路径）、`README.md`／`README.zh-CN.md`（脚本 bullet）、`.github/workflows/tests.yml`（core 矩阵加一份测试） | 把 motion.md「按刚度/阻尼数值积分取 20–30 采样点写进 `linear()`」这句承诺兑现成命令：`--preset` 复现六档材质手感，`--target` 按目标时长反解 k/c；同时补 reduced-motion 的可抄片段、动效令牌三条缓动四条时长 | 验收读数：`spring_to_linear.py --target 200 --overshoot 8 --json` 落定 0.20s／过冲 8.0%｜`--target 500` 落定 0.50s｜`test_spring_to_linear` 4 项 OK（含负臂「解析式近似确实偏 0.74s vs 0.50s」）｜`selftest.py` PASS（ENTRIES 4 项）｜`check_limits.py` rc=0（SKILL.md 281 行；tokens.md 114 行已带目录）｜`vaccinate.py` 13/14（V14 可选未覆盖，未变）｜`sources.md` 里本机家目录绝对路径归零（改前 6 处） | ⚠️ 顺带查出一个文档矛盾：motion.md 手感表的咔嗒档(k=375,c=12)按 m=1 积分落定 **约 0.93s**、过冲 35.9%，与「界面元素一律 <300ms」冲突。处置是**标注而非改表**——手感表给材质倾向，时长一律用 `--target` 反解；若日后要重标那组数值，需先定「按钮按下到底允许多少 ms」 |

| 2026-11-18 | 改 `SKILL.md`（拆一处「不是…是…」对仗）、`references/tools.md`（＋退出码节）、`references/naming.md`（一源一锚）、`scripts/emit_tokens.py`（＋目标态回读）、`scripts/spring_to_linear.py`（保持窗自适应）、`references/motion.md`／`references/tokens.md`（落定读数改约 0.93s）、`tests/test_spring_to_linear.py`（＋值域边界样本）、新增 `tests/test_refs_toc.py` | 按 禅院塔／矮凳桥／浮沙言 三卷过一遍内部，四处真缺口＋一处闸盲区：① 退出码无表（§2.284 退出码是唯一判因，实测六入口 rc=2／对比度不过 rc=1，据此立表）；② `--target` 值域 40–1200 与固定 50ms 保持窗冲突，40ms 目标实测出 74ms（§2.152 改阈值要覆盖边界两侧，一加边界样本就红）；③ `emit_tokens.py` 四个文件写完不回读（§2.35 判据是目标态复读）；④ naming §二 一处源域对三件目标物，违 矮凳桥「可指认判据」（已改成一源一锚＋注明此表是比喻不是映射卡）；⑤ `check_limits.py` 认 skill 根有 LICENSE 即把全部 references 当外部件 ⇒ 本库「>100 行须真目录」整片失效（实查 14 卷已全合规），故另立 `tests/test_refs_toc.py` 按同一判据自查，并接进 CI | 验收读数：`test_spring_to_linear` 5 项 OK（含 40ms→40ms、1200ms→1200ms、39/1201→rc=2）｜17 项测试 OK（含 test_refs_toc 2 项）｜`selftest` PASS｜`emit_tokens --base '#0f7b6c'` rc=0 且打印「写出并回读通过」｜浮沙言 `check --doc`：SKILL.md 硬信号 0／线索 5→1，README 0/0，tokens 0/4、naming 0/5 均属判伪与「材质≠时长」这类必要的否定句，不改 |

| 2026-11-18 | 新增 `demo/index.html`（自我示范页）、`demo/motion-demo.gif`（7.4s，四段录屏合成）、`demo/` 下 `tokens.css`／`theme.css`／`tokens.json`／`DESIGN.md`（`emit_tokens.py --base '#2f6f62'` 生成）、`tests/test_demo_page.py`；`README.md`／`README.zh-CN.md` 各加「动效示范」节与 `demo/` 布局项 | 对外动态证据：三处动效（按下 150ms/6%、抽屉 320ms `--ease-drawer`、抬升 200ms/8%）＋「减少动态效果」段＋修前修后并排（无壳 vs 有壳）；曲线全部由 `spring_to_linear.py` 反解，未手写 `cubic-bezier` | 验收读数：桌面 1440×900 与手机 390×844 均无横溢、无控制台错误｜对比度四组 PASS（16.07／7.30／5.88／7.27）｜`test_demo_page` 4 项 OK（样式表在盘、两处降级、曲线 ≥20 采样点、README 引图 >50KB）｜合成中途一次失败：concat 列表用相对名在 `/tmp` 解析不到，改绝对路径后成片 |

| 2026-11-18 | `references/build-recipes.md` 新增「结构件配方：三段装配」（表单／列表／空状态各一张槽位表＋判据行，明确不给整页骨架），文件 68→115 行，按本库口径补 `## 目录`（8 条链接）；`SKILL.md` 命令表与卷索引各补一句指向该段 | 用户问「浮龟需不需要内置一套默认 UI」，结论是不做组件库、只补参考实现：七条语法管单个组件，这一段管一片页面由谁拼起来 | 读数：`test_refs_toc` 2 项 OK｜目录 8 条锚点逐一核过（脚本按 GitHub slug 规则比对，无死链）｜浮沙言 `check --doc` 硬信号 0、线索 0（首次跑报 block 属工具把绝对路径当正文，换相对路径复跑为 0） |


| 2026-11-18 | 改 `SKILL.md`（「五层」→「六层」；`allowed-tools` 补 `spring_to_linear.py`／`measure_reference.py`）、`README.md`／`README.zh-CN.md`（54 卷→55 卷；回归串由 6 件补齐 13 件）、`.github/workflows/tests.yml`（core 矩阵 +4：`test_check_contrast`／`test_emit_tokens`／`test_refs_auth`／`test_ci_coverage`）、`scripts/spring_to_linear.py`（新增 `settle_clamped()`／`duration_line()`／`clamped` 字段，`--samples` 报错文案 4–50→4–60）、新增 `tests/test_refs_auth.py`／`tests/test_ci_coverage.py`、`tests/test_spring_to_linear.py`（+2）、`tests/test_refs_toc.py`（+2） | 按 对鸟Deducere 闭环修 大观亭 检出的 D1／D2／D3 三条红，共五处：① 宣称 54 卷实 55、「五层」表实 6 行（D1 假称）；② `motion.md` 教跑 `spring_to_linear.py`、`measure_reference.py` 而 frontmatter 未授权（D1）；③ `--samples` 值域闸撤掉后 5 项测试全绿＝闸无人守（D3）；④ `k=300 c=3` 落定被 3s 上限截断却仍打印「位移稳定在终点 0.5% 以内」（D1 假话）；⑤ `test_check_contrast`／`test_emit_tokens` 从未进 CI、README 只列 6/11（D2） | 验收读数：五条各自先跑出红灯再修——L1 `ls references/*.md\|wc -l`=55 对 README「54」｜L2 `test_refs_auth` 真红 `['measure_reference.py','spring_to_linear.py']`→修后 2 项 OK｜L3 变异（闸改 `0<=samples<=9999`）曾全绿，补边界断言后该变异 **FAILED 1 项**｜L4 触顶输出改「⚠️ 未在 3.0s 内稳定：曲线被截断」，正常参数不出该句｜L5 `test_ci_coverage` 红 `check_contrast/emit_tokens/refs_auth` 与 README 漏 6 件 → 修后 3 项 OK｜全量回归 **131 项 OK（skipped=1）**｜`selftest` PASS｜`check_limits.py` SKILL.md 283 行 rc=0｜`vaccinate` 13/14｜`check_ref_paths` 仍 `MISSING: .vudgio/design-log.md`（运行期产物，SKILL.md 已标注，属预期）｜浮沙言按正文跑（`node fluensand.js check "$(cat 文件)" --doc --no-learn`，⛔ 把路径当第二个参数）：`SKILL.md` 硬信号 0／线索 1（可替换）、`README.md` 与 `README.zh-CN.md` 0/0、`references/build-recipes.md` 线索 5→2（拆掉「三条都不是审美问题，是组件语法没定」这处对仗，改为「三条的根子都不在审美上——…」） | ⚠️ 纠正一处旧账：上一条与更早台账里的「浮沙言 硬信号 0」系**调用写错**（`--doc` 后面跟的是正文，我传了文件路径，工具读到的汉字数为 0），工具本身无缺陷；已按正确调用复跑，读数见左格 |

| 2026-11-18 | `LICENSE` 署名改 `L4ST-afk` ；新增 `scripts/clip_audit.js`（真文件：浏览器可粘贴的 IIFE ＋ Node 可 require 的 `cutFor` 几何内核，回执 `{ ok, cut, checked, items, hidden }`）、`tests/test_clip_audit.py`（3 项：存在性与 node --check／几何内核／判据没被写死）；`references/acceptance.md` §1 执行方法与回执形状对齐真件（末行改参、scope→root）；删 `README.en.md`（只剩一句跳转，英文入口就是 `README.md`）；两份 README 与 CI 清单补 `clip_audit.js`／`test_clip_audit`（13→14 件） | 外部声明三处对不上，按教师「license 改成L4ST-afk + 全批」处理：① 署名原为外部作者名，改成本人；② `acceptance.md` 教跑 `scripts/clip_audit.js` 而该脚本根本不在盘（死声明），补真文件而不是改文档说「没有」；③ `README.en.md` 只是一句「英文版见 README.md」，三份 README 名字误导，删之 | 验收读数：`test_clip_audit` 3 项 OK（含几何三例：装得下 0／左裁 12／整体在外 hidden）；变异自证——`cutFor` 改成恒 `cut=0` → **FAILED 2 项**；`test_clip_audit`＋`ci_coverage`＋`refs_auth`＋`refs_toc` 共 12 项 OK｜`node --check scripts/clip_audit.js` rc=0 | ⚠️ 未测的那层：DOM 采集（`getComputedStyle` 读 shadow 外扩、祖先 overflow/clip-path 遍历）只能在浏览器里跑，本机未做实机一次；口径是「spread+blur 全量计、只认 box-shadow 与 drop-shadow」，属保守近似，不是像素级精确 |
## 三、回滚与恢复

**冷存档快照就是这里的回滚点**。恢复的目标是「只退回被改坏的那一处」，不是把整目录倒回去。

1. 改前确认最近一次 `snapshot` 快照可用（时间戳、目录完整）。
2. 单文件改坏：从快照里取回**那一个文件**，别整目录覆盖——整目录覆盖会把此后所有本地判据一起盖掉。
3. 恢复后跑一遍测试：`cd tests && python3 -m unittest $(ls test_*.py | sed 's/.py//' | tr '\n' ' ') -q`（13 件，清单以盘上为准，⛔ 手抄旧串）。
4. 冲突原则：以「哪边说清了为什么」为准；说不清的那条删掉。

## 四、别做的事

- ⛔ 在这类会被搬迁/改名的目录里建 `.git`（丢过一次，见 §一）
- ⛔ 用整目录覆盖式恢复（会把本地判据一起盖掉），恢复前先 `diff` 一遍
- ⛔ 重新引入任何「拉新版并原地覆盖整目录」的自动更新器，或给它加定时任务
- ⛔ 把这条记录当成疫苗版本号。`vaccineVersion` 保持 `partial-88e197b69b8f`；V1/V2/V9/V10/V13 已于 2026-11-14 补齐（13/14，余 V14 为可选）
