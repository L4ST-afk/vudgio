# 取证工具执行器

> 归属：约束满足闭环 · 第 4 步「取证」。
> 只说三件事：什么时候用哪个工具、怎么读退出码、命令怎么拼。本目录自带程序⛔ 需读源码；`<skill>` 换成本 Skill 安装目录。全部选项与输出结构看各自 `--help`，写错时报错会给可照抄的写法。

要生成文件先按 [工作区](workdir.md) 定过程输出与命令目录，无项目约定用 `.vudgio/<任务名>`；显式输出路径始终优先，截图与图片处理各有自己的 cwd 要求。

宿主自带浏览器工具时，看页面、走流程照常用。要交证据优先用这里的截图工具——它开独立临时浏览器，不碰用户自己浏览器的数据。本机缺 Node 22 或 Chrome／Chromium／Edge 时退回宿主工具，交同样证据。任务或项目已指定截图工具时照用它。

## 退出码＝判据读数

判「这步过没过」只看退出码，⛔ 看日志里有没有报错字样。六个入口同一约定：

| 码 | 含义 | 例 |
| --- | --- | --- |
| 0 | 跑通且判据过 | `check_contrast --pair '#111' '#f8fafc'` |
| 1 | 判据不过：对比度不达标、目标时长越出 40–1200ms | `check_contrast --pair '#777' '#888'` |
| 2 | 用法或输入错：缺参数、值域外、文件不存在 | 任何脚本无参直跑 |

实测（2026-11-18）：六入口无参一律 rc=2；参数错、缺值、步法不合法亦 rc=2（`take_shots` 同日补齐，此前混在 1）；`check_contrast` 不过 rc=1。

三件 mjs 共用 `scripts/_cli.mjs`（`EXIT`／`usageError`／`runMain`）：用法错挂 `code='USAGE'` 统一落 2，运行期异常落 1；参数解析各件自己写，⛔ 合成一个解析器。

拿 rc 当交付门（如 CI 拦对比度）时只认 0；rc=1 是要改稿，⛔ 当「跑完了」。

## 截图与录屏

### 截多少、何时截

两种用途⛔ 混：

- **看一眼**：改完一批想看效果。只截当前屏、一条命令；把改动攒齐再截，⛔ 每改一处截一次；页面没变就⛔ 重复截。
- **取证**：只在送评审前、交付前保留足以判断的标准视口图。常规单页一次截桌面＋手机标准视口（`--size desktop,mobile`），用 `--steps` 验 1–2 个代表交互状态即可收尾。交互状态直接用 `--steps "click ..."` 触发，⛔ 在页面代码里为截图专门开发 `?state=<名>` 路由；带 `sticky` 顶栏或 `100vh`／`resize` 监听的工作台⛔ 加 `--full`（`fullPage: true`），避免空白拼接伪影，也⛔ 对每个局部卡片逐一单拍。要比状态加 `--sheet`，要遮字加 `--mask`。方向首屏那一轮每方向只截一张，不取整套证据。

动效默认用 `--frames` 出带时间的序列图，或让评审者打开页面直接操作。只有确要判正常速度手感、且评审能播视频时才 `--record`，⛔ 为交付而录屏。确需整套证据用 `--evidence --frames <帧数>`；满足录屏条件才加 `--record`。

每轮评审只重取本轮改动影响的证据；没动过的状态与动效沿用上轮文件，交接时注明沿用。改了共享样式这种拿不准是否被影响的重取那项。评审者只要求扩大覆盖却说不清缺哪条判断依据时，⛔ 补图也不加轮。

### 常用命令

```text
node <skill>/scripts/take_shots.mjs index.html --size desktop,mobile --out shots
```

| 要什么 | 加什么 |
| --- | --- |
| 桌面＋手机标准视口 | `index.html --size desktop,mobile --out shots`（单端看一眼 `--size desktop`；不写默认手机 390x844；只看整体版式加 `--thumb`） |
| 多个候选一次截完出并排图 | 传候选目录（如 `explore`）或多个 HTML，同一浏览器会话截完自动出 `sheet.png` |
| 只看改过的局部 | `--selector ".card"`，自动滚入视口只截该元素 |
| 操作几步再截 | `--steps "click .open; wait 300"` |
| 核长页滚动动效 | `--frames 8 --steps "scroll 600; scroll 600; scroll 600"`，按页长多写几步；录屏条件见上 |
| 给评审指问题：画框标编号 | `--mark "1=.page-head .btn; 2=.toggle-row"` |
| 看清一段过渡 | `--frames 8 --steps "click .open"`，只出带时间序列图 |
| 拼对比图、不需要页面 | `--stitch a.png --label 修改前 --stitch b.png --label 修改后` |
| 按共有元素统一比例裁同区 | `--stitch a.png --match-width 240 --stitch b.png --match-width 300 --crop "0,0,800,600"`；以首图元素宽为准、裁切在统一比例后；已知倍数改用 `--scale`，完整写法看 `--help` |

交互、保存、提交、失败恢复从页面真实入口起，用 `--steps "click .open; fill #name \"内容\"; drag .card 120 0"` 或宿主浏览器真实点击，必要时连续填写、点击、等到结果。保存后刷新或重进读回，失败后恢复到可重试状态；留能对应实际结果的截图或操作记录，执行不了就写明未验证。其余选项、选择器与动作写法、输出文件与 `report.json` 结构看 `node <skill>/scripts/take_shots.mjs --help`。拿不准写法先 `--dry-run`，不启动浏览器。超时自动放宽重跑一次，仍失败照报错里的命令重跑。

### 检索与下载真实素材

在项目工作目录运行，后续命令同目录，搜索编号才接得上：

```text
node <skill>/scripts/curate_media.mjs search "<关键词>" --kind texture --limit 6 --sheet --dir candidates   # 搜材质候选，出联系表
node <skill>/scripts/curate_media.mjs search "<一组词> | <另一组词>" --sheet --dir candidates   # 多词组一次搜完
node <skill>/scripts/curate_media.mjs preview V1,T2 --sheet --dir candidates   # 预览已搜到的候选
node <skill>/scripts/curate_media.mjs fetch C1,T2 --dir assets --sheet   # 下载选中的候选
node <skill>/scripts/curate_media.mjs fetch V3 --dir <不上线的参考图目录>   # 只做参考的素材不下进页面
node <skill>/scripts/curate_media.mjs fetch T2 --maps all --resolution 1k --dir assets   # 拉整套贴图与法线
```

`--kind` 取 `all|texture|design|photo|blueprint|map|plate|science|video`。信源含材质库、欧美与日本博物馆及图书馆馆藏、NASA；各类别对应信源看 `--help`。`all` 交错取各源、`|` 一次搜几组词。关键词多用英文，东亚题材可直接用中日文，简体搜不到换繁体或日文。

结果存 `.curate-cache.json`，编号跨次保留。每项 `use` 说明用途：`page` 可进页面（CC BY／BY-SA 要署名）、`check` 先看来源页、`reference` ⛔ 进页面、`--use page` 只留第一种。

`search --sheet` 与 `preview` 出带编号、用途、原图尺寸的联系表 PNG，直接读图挑，⛔ 只看标题；同时给每项算 `look`（四边色、是否浅色纸底、哪些区域干净可压字），出 HTML 联系表。`fetch --sheet` 出本地联系表并查真实宽高，完整解码、视频自动截首帧 poster。

贴图默认下 1k Diffuse；`--maps all` 拉 Diffuse、Roughness、OpenGL Normal JPG 并校大小与 MD5。使用与许可见 [素材](media.md#真实贴图与科学工程素材)。下载及 poster 自动写同目录 `SOURCES.md`，兼容 `fetch "<URL>" --out assets/<文件名> --note "来源说明"`。全部选项看 `node <skill>/scripts/curate_media.mjs --help`。

### 看结果

交评审前自己先看一眼：默认状态是否已加载完、遮字版有没有把图形一起盖掉。证据有错先重截再交。汇总提示录屏或序列图与截图不一致时，静止终态以截图为准，单独查看那段操作或补序列图核过渡。序列图只判状态与变化，⛔ 据此宣称正常速度手感已验证。空的 WebGL 截图⛔ 当证据。

每张截图还跑一遍可读性与渲染检查，发现的问题写进 `report.json` 的 `lint`，以「默认做法提示」列出：文字对比度不达标（正文 <3:1、大字 <2.5:1）、正文小于 11px、多行行高过紧、首屏停在透明状态的内容、手机上输入框字号小于 16px（聚焦时 iOS 会放大页面）、首屏 4 块以上各自加框或框里套框、弹窗主动作按钮落在视口外，另外还有控制台错误、横向溢出、加载失败的图片这几项硬问题。提示清零后仍要自己看截图。检查报 401／404 这类与画面无关的错误，交付说明记一行，⛔ 为过检查去改登录、接口等业务代码。

## 可操作小样

方向阶段的首屏不做交互，用不到本节；选定方向做完整页面时再用。存量项目优先沿用已装组件库、图标库、样式体系与技术栈。新项目按用户约束、技术栈与主要交互选组件基础——原生控件、轻量基础组件、完整组件库都行，⛔ 强制引入完整库；已有工程或交付约定优先于下面的独立 HTML 做法。

无工程约束、交独立小样时，默认单入口 `index.html`，优先把 HTML、`<style>`、`<script>` 内聚单文件，服从项目与交付约定。颜色、字号、间距、圆角先定成少量 CSS 变量，后面一律引用；独立小样⛔ 另引构建链。可用原生脚本或轻量库做真实筛选、切换与详情交互。正式入口 HTML 的本地依赖放同目录 `vendor/` 再引用，过程小样及其依赖才放任务目录。
