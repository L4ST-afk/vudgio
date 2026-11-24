"""motion_audit.py 的行为测试：判据要能红，也要不乱红。

每条判据都配一条负臂（故意踩线必须报），另配两条防误报臂：
reduced-motion 降级块里的 `1ms !important` 是规范自己规定的写法，
tokens.css 本身就是令牌源，两处都不该被当成「绕过令牌」。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "scripts", "motion_audit.py")


def run(root, *extra):
    p = subprocess.run([sys.executable, SCRIPT, "--root", root, *extra],
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


class TestMotionAudit(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="motion-audit-")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def write(self, rel, text):
        path = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_clean_project_exits_0(self):
        self.write("ok.css", """
.card { transition: transform var(--duration-popover) var(--ease-out); }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition-duration: 1ms !important; }
}
""")
        rc, out = run(self.dir)
        self.assertEqual(rc, 0, out)

    def test_transition_all_is_flagged(self):
        self.write("bad.css", ".card{transition:all 300ms ease}\n@media (prefers-reduced-motion:reduce){}")
        rc, out = run(self.dir)
        self.assertEqual(rc, 1, out)
        self.assertIn("transition: all", out)

    def test_reduced_motion_1ms_is_not_flagged(self):
        # 唯一的时间值在降级块里，且是规范给的写法 → 不许报
        self.write("ok.css", """
.x { transition: opacity var(--duration-tooltip) var(--ease-out); }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 1ms !important; transition-duration: 1ms !important; }
}
""")
        rc, out = run(self.dir)
        self.assertEqual(rc, 0, out)

    def test_layout_property_is_flagged(self):
        self.write("bad.css", ".m{transition:width 300ms ease}\n@media (prefers-reduced-motion:reduce){}")
        rc, out = run(self.dir)
        self.assertEqual(rc, 1, out)
        self.assertIn("动布局属性", out)

    def test_scale_zero_is_flagged(self):
        self.write("bad.css", ".hero{transform:scale(0)}\n")
        rc, out = run(self.dir)
        self.assertEqual(rc, 1, out)
        self.assertIn("scale(0)", out)

    def test_literal_curve_and_duration_are_flagged(self):
        self.write("bad.css", ".b{transition:transform 200ms cubic-bezier(0.4,0,0.2,1)}\n"
                               "@media (prefers-reduced-motion:reduce){}\n")
        rc, out = run(self.dir)
        self.assertEqual(rc, 1, out)
        self.assertIn("字面量 cubic-bezier", out)
        self.assertIn("字面量时长", out)

    def test_one_way_ease_in_is_flagged(self):
        self.write("bad.css", ".b{transition:opacity var(--duration-press) ease-in}\n"
                               "@media (prefers-reduced-motion:reduce){}\n")
        rc, out = run(self.dir)
        self.assertEqual(rc, 1, out)
        self.assertIn("单向 ease-in", out)

    def test_tokens_css_is_source_not_finding(self):
        # 令牌源里出现字面量曲线是正常的，跳过它
        self.write("tokens.css", ":root{--ease-out:cubic-bezier(0.23,1,0.32,1);--duration-press:160ms}\n")
        self.write("ok.css", ".x{transition:transform var(--duration-press) var(--ease-out)}\n"
                             "@media (prefers-reduced-motion:reduce){}\n")
        rc, out = run(self.dir)
        self.assertEqual(rc, 0, out)

    def test_assets_dir_is_skipped(self):
        self.write("assets/tool.html", "<style>.x{transition:all .3s}</style>")
        rc, out = run(self.dir)
        self.assertEqual(rc, 0, out)

    def test_json_matches_marker_card_fields(self):
        self.write("bad.css", ".card{transition:all 300ms ease-in}\n")
        rc, out = run(self.dir, "--json")
        self.assertEqual(rc, 1, out)
        data = json.loads(out)
        self.assertGreater(data["findings"], 0)
        card = data["cards"][0]
        for key in ("card", "rule", "severity", "file", "line", "now", "want", "evidence", "verdict"):
            self.assertIn(key, card)
        self.assertTrue(card["card"].startswith("MK-"))
        self.assertIn("unverified", card["verdict"])


if __name__ == "__main__":
    unittest.main()
