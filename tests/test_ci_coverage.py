"""测试件与 CI／README 的清单必须对得上。

钉一条：盘上每件 `tests/test_*.py` 都要在 `.github/workflows/tests.yml` 里被真跑一次，
并在 README 的回归命令串里出现。本轮实测缺口：`test_check_contrast` 与 `test_emit_tokens`
从未进 CI，README 只列了 6/11——闸在跑、但两件核心没人跑。

口径：
- CI 的 `modules = [...]` 三处清单合起来算覆盖；同一件出现在两处（重复跑）不算错，但要显名；
- `test_ci_coverage.py` 自己豁免（它不测业务）；
- README 与 README.zh-CN 必须给出同一串命令。
"""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "tests.yml")
SELF = "test_ci_coverage"


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def on_disk():
    return sorted(
        f[:-3] for f in os.listdir(HERE)
        if f.startswith("test_") and f.endswith(".py") and f[:-3] != SELF
    )


def in_ci():
    text = read(WORKFLOW)
    names = []
    for block in re.findall(r"modules = \[(.+?)\]", text, re.S):
        names.extend(re.findall(r'"([^"]+)"', block))
    return names


def in_readme():
    names = {}
    for f in ("README.md", "README.zh-CN.md"):
        line = [l for l in read(os.path.join(ROOT, f)).splitlines() if "python3 -m unittest" in l]
        names[f] = line[0] if line else ""
    return names


class TestCiCoverage(unittest.TestCase):
    def test_every_test_runs_in_ci(self):
        disk = on_disk()
        ci = in_ci()
        missing = [t for t in disk if t not in ci]
        self.assertEqual(missing, [], "CI 没跑的测试件：%s" % ", ".join(missing))

    def test_ci_lists_no_ghost(self):
        disk = set(on_disk())
        ci = in_ci()
        ghosts = sorted(set(ci) - disk - {SELF})
        self.assertEqual(ghosts, [], "CI 列了盘上不存在的测试件：%s" % ", ".join(ghosts))

    def test_readme_lists_all(self):
        disk = on_disk()
        for f, line in in_readme().items():
            self.assertTrue(line, "%s 里没有回归命令串" % f)
            missing = [t for t in disk if t not in line]
            self.assertEqual(missing, [], "%s 漏列：%s" % (f, ", ".join(missing)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
