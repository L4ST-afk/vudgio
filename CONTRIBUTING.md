# 浮龟 Vudgio · 贡献规范

## 先决定你改的是哪一层

| 层 | 文件 | 判它的人 |
|---|---|---|
| 入口判据 | `SKILL.md`（命令面、主流程、交付门、体量预算） | 人读 ＋ CI（`tests/test_refs_auth.py`、`test_ci_coverage.py`） |
| 细则判据 | `references/*.md`（58 卷，按命令／问题加载） | 人读 ＋ `tests/test_refs_toc.py`（>100 行须有真目录） |
| 执行器 | `scripts/*.py` / `*.mjs` / `*.js` | CI（`tests/test_*.py` 对应件） |
| 判据来源 | `references/sources.md` | 人读 ＋ `tests/test_refs_auth.py` |

**判据只有一处正本**：`SKILL.md` 给命令与门槛，细则卷给判据正文。两处写同一件事，改细则、删重复；`references/index.md` 只给「何时读哪卷」，不承载判据。

## 提交前跑三件

```bash
python3 scripts/selftest.py                    # 冒烟自检须 PASS
cd tests && python3 -m unittest discover        # 全绿（test_take_shots 需本机浏览器，超时可单列）
# 体量闸（若环境里有太玉洞 Tagnodon 的 check_limits.py）
python3 <tagnodon-scripts>/check_limits.py .   # 体量不超限
```

体量闸是库级共享脚本，不一定随包附带；没有它时至少核两条硬线：`SKILL.md` ≤500 行、`references/*.md` >100 行须有 `## 目录` ＋ ≥3 锚点链接。

## 数字与判据的写法

- **判据句写白话**：`⛔` 禁令、`⚠️` 边界、阈值、命令名、字段名、错误原文一律保留原样，不许压成形容词。
- **数字带条件**：视口宽度、字号、时长、对比度写清适用面；没有条件的不写进表格。
- **断言钉不变式，不钉实现参数**：不写「没人改过」型断言。
- **一条判据配一个执行器**：写进 `SKILL.md` 判据账；没有执行器的降为说明，不冒充判据（禅院塔 §2.272）。

## 引用外部来源

- 新增来源先在 `references/sources.md` 登记：来源、用了什么、许可、边界、是否内置正文。
- 只移植判据形态与指针，⛔ 转载他人正文；带许可的来源在 `NOTICE` 与 `THIRD_PARTY_NOTICES.md` 署名。
- 不内置会变的数据（浏览器兼容矩阵、上游版本号）：留查询通道，不抄快照。

## 命名

目录、仓库、包名、分支、文件名一律 `vudgio`；中文名「浮龟」只出现在正文与文档标题，不进路径（与 rassarpa／somnians 的拉丁名目录惯例一致）。脚本名、命令名、CSS 变量名是判据的一部分，⛔ 不改名（自检依赖它们）。

## 提交

- 一个提交只说一件事；改判据与改脚本分开。
- 触及 `SKILL.md` 判据账时，在提交正文写清「改了哪条判据、对应哪个执行器、自检读数」。
- 不提交 `.DS_Store`、`__pycache__`、任何含家目录绝对路径的文件。
