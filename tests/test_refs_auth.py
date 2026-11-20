"""正文教人跑的脚本，必须在本件 allowed-tools 里放行。

钉一条：`references/` 与 `SKILL.md` 里出现的 `scripts/<名>`，若宿主按 allowed-tools
授权，没列进去就等于「文档教你跑、运行时却拦你」。实跑过的坑：`motion.md` 让人跑
`spring_to_linear.py --target`，而 frontmatter 只授权了六个入口。

口径：
- 只认 `scripts/<名>` 且文件真在 `scripts/` 下（正文举例的别家路径不算）；
- `selftest.py` 这类只读冒烟入口按白名单豁免（不走本件授权）；`_cli.mjs` 是内部模块（退出码与用法错），⛔ 不能当命令跑，同样豁免；
- 授权写法按前缀通配（`Bash(python3 *emit_tokens.py*)`），按文件名尾匹配即可。
"""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPTS = os.path.join(ROOT, "scripts")

# 不参与授权的自检入口（谁都能跑的只读冒烟与外部执行器）＋ 内部模块（不单独跑，只被 entry import）
EXEMPT = {"selftest.py", "_cli.mjs"}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def mentioned():
    names = set()
    for base, _, files in os.walk(ROOT):
        if os.sep + "tests" in base:
            continue
        for f in files:
            if not f.endswith(".md"):
                continue
            if f in ("README.md", "README.zh-CN.md", "CHANGELOG.md"):
                continue
            text = read(os.path.join(base, f))
            names.update(re.findall(r"scripts/([A-Za-z0-9_.-]+\.(?:py|mjs))", text))
    return names


def allowed():
    head = read(os.path.join(ROOT, "SKILL.md")).split("---")[1]
    return head


class TestRefsAuth(unittest.TestCase):
    def test_every_taught_script_is_authorized(self):
        names = mentioned()
        self.assertTrue(names, "没扫到任何 scripts/ 引用，正则坏了")
        head = allowed()
        missing = []
        for n in sorted(names):
            if n in EXEMPT:
                continue
            if not os.path.exists(os.path.join(SCRIPTS, n)):
                continue
            if n not in head:
                missing.append(n)
        self.assertEqual(missing, [], "正文教跑但未授权：%s" % ", ".join(missing))

    def test_exempt_files_exist(self):
        for n in EXEMPT:
            self.assertTrue(os.path.exists(os.path.join(SCRIPTS, n)), "白名单里写了不存在的脚本：%s" % n)


if __name__ == "__main__":
    unittest.main(verbosity=2)
