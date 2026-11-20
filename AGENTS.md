# 本仓规矩（写给所有在这个仓里干活的 agent）

## 提交

- 用仓库已配置的身份（`git config user.name` / `user.email`）。⛔ 不要换成工具身份、机器人邮箱或占位名。
- ⛔ 不要加 `Co-authored-by:` 尾注。
- ⛔ 不要在没人要求时自己提交：改动留在工作区，等人看过。

## 分支与工作树

- ⛔ 不要建分支、worktree、checkpoint ref，除非明确要求。
- 用完清干净：不留 `.git/worktrees`、`refs/copilot/*`、指向旧提交的游离工作树。

## 文件

- `docs/` 是对外文档位。⛔ 往里放评审记录、会议纪要、任务分派记录、过程日志。
- ⛔ 在公开文件里提未发布项目、内部工具、私人来源、个人背景。
- 随包发布的文字要读起来像文档，不像工作流水账。

## 跨平台

- 脚本输出按 UTF-8：Windows 控制台默认 cp1252，直接 `print` 带 ✓/⚠/中文会抛 `UnicodeEncodeError`。
- 调子进程时只要 `text=True`，就显式写 `encoding="utf-8"`；否则 Windows 按本地编码解码，报出来的是莫名其妙的断言失败。
- 缓存目录（`.pytest_cache/`、`__pycache__/`、`*.pyc`）⛔ 进库，`.gitignore` 里已有规则。

两条在 `tests/test_ci_coverage.py` 里有守卫测试，退化会红。

## 推之前

本仓装了 `pre-push`：推的时候自动跑一次对外体检（文件 + 提交身份），不过就不推。⛔ 拿 `--no-verify` 绕过去；绕了请自己补跑一次。
