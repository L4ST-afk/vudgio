"""clip_audit.js 的存在性与几何内核。

两件事分开测：
- 存在性：`acceptance.md §1` 让人跑 `scripts/clip_audit.js`，该文件必须在盘、语法过；
- 内核：`cutFor` 是纯几何，Node 里直接 require 就能验——尽力钉住「cut === 0」这个唯一判据
  别被改成恒 0。DOM 采集那一层（getComputedStyle / 祖先遍历）要在浏览器里跑，
  本文件不假装测过它。
"""
import json
import os
import shutil
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "scripts", "clip_audit.js")


class TestClipAudit(unittest.TestCase):
    def test_script_exists_and_parses(self):
        self.assertTrue(os.path.exists(SCRIPT), "acceptance.md 教跑的 clip_audit.js 不在盘上")
        node = shutil.which("node")
        if not node:
            self.skipTest("没有 node，跳过语法检查")
        r = subprocess.run([node, "--check", SCRIPT], capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(r.returncode, 0, "语法不过：%s" % r.stderr.strip())

    def test_geometry_kernel(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("没有 node")
        probe = r"""
const { cutFor } = require(process.env.CLIP_AUDIT);
const t = { left: 0, top: 0, right: 100, bottom: 100 };
const out = {
  inside:  cutFor(t, { left: -20, top: -20, right: 120, bottom: 120 }),
  leftCut: cutFor(t, { left: 12, top: 0, right: 200, bottom: 100 }),
  outside: cutFor(t, { left: 300, top: 0, right: 400, bottom: 100 }),
  unbounded: cutFor(t, null),
};
console.log(JSON.stringify(out));
"""
        r = subprocess.run([node, "-e", probe], capture_output=True, text=True, encoding="utf-8", timeout=60,
                           env={**os.environ, "CLIP_AUDIT": SCRIPT})
        self.assertEqual(r.returncode, 0, r.stderr.strip())
        d = json.loads(r.stdout)
        self.assertEqual(d["inside"]["cut"], 0, "装得下的阴影不该报被裁")
        self.assertEqual(d["leftCut"]["cut"], 12, "左裁 12px 应报 12：%r" % d["leftCut"])
        self.assertEqual(d["outside"]["hidden"], True, "整体在边界外必须报隐藏")
        self.assertEqual(d["unbounded"]["cut"], 0, "没有裁切祖先时应为 0")

    def test_judge_is_not_hardcoded_zero(self):
        """变异闸：把 cutFor 改成恒返回 cut:0，上面那条就该红——这里先确认源码里没有恒 0。"""
        src = open(SCRIPT, encoding="utf-8").read()
        self.assertIn("sides.left + sides.top", src, "几何求和没了，判据可能被写死")
        self.assertIn("cut === 0", open(os.path.join(ROOT, "references", "acceptance.md"), encoding="utf-8").read(),
                      "acceptance.md 的硬判据（cut === 0）被删了")


if __name__ == "__main__":
    unittest.main(verbosity=2)
