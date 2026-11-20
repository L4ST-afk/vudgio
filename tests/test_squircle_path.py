"""Exercise squircle_path.mjs: 几何正确、退出码与输出格式。

纯 Python 标准库调 node；不联网、不启浏览器。
"""
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "squircle_path.mjs")
NODE = shutil.which("node")
POINT = re.compile(r"[ML]\s*(-?[\d.]+)\s+(-?[\d.]+)")


def parse_path(path):
    """从 `M… L… Z` 里取点；⛔ 别用 split(" L") —— 它把 "170.71" 截成 "70.71"。"""
    return [(float(x), float(y)) for x, y in POINT.findall(path)]


@unittest.skipUnless(NODE, "Node is not installed")
class SquirclePathTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([NODE, SCRIPT, *args], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)

    def test_help(self):
        r = self.run_cli("--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--width", r.stdout)

    def test_usage_errors_exit_2(self):
        for argv in (["--width", "300", "--radius", "40"],
                     ["--width", "300", "--height", "200", "--radius", "40", "--format", "png"],
                     ["--width", "300", "--height", "200", "--radius", "40", "--n", "1.5"],
                     ["--width", "abc", "--height", "200", "--radius", "40"]):
            r = self.run_cli(*argv)
            self.assertEqual(r.returncode, 2, (argv, r.stderr))
            self.assertIn("squircle-path", r.stderr)

    def test_css_output(self):
        r = self.run_cli("--width", "300", "--height", "200", "--radius", "40")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('clip-path: path("M', r.stdout)
        self.assertIn('")', r.stdout)
        self.assertIn("-webkit-clip-path", r.stdout)

    def test_json_shape_and_canvas(self):
        r = self.run_cli("--width", "300", "--height", "200", "--radius", "40",
                         "--steps", "16", "--format", "json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["points"], (16 + 1) * 4)
        pts = parse_path(data["path"])
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        self.assertAlmostEqual(min(xs), 0, places=1)
        self.assertAlmostEqual(max(xs), 300, places=1)
        self.assertAlmostEqual(min(ys), 0, places=1)
        self.assertAlmostEqual(max(ys), 200, places=1)

    def test_radius_clamped(self):
        r = self.run_cli("--width", "48", "--height", "48", "--radius", "30", "--format", "json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(data["radius"], 24)
        self.assertIn("夹到 24", r.stderr)

    def test_n_two_is_circle(self):
        # n=2 时超椭圆退化成圆：45° 处的角点应落在圆心 + r/√2
        r = self.run_cli("--width", "200", "--height", "200", "--radius", "100",
                         "--n", "2", "--steps", "8", "--format", "json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        pts = parse_path(data["path"])
        # 第一个角（右上）的第 4 个点约在 45°
        x, y = pts[4]
        self.assertAlmostEqual(x, 200 - 100 + 100 / (2 ** 0.5), delta=1.5)
        self.assertAlmostEqual(y, 100 - 100 / (2 ** 0.5), delta=1.5)

    def test_import_has_no_cli_side_effect(self):
        code = ("const m = await import('./scripts/squircle_path.mjs');"
                "console.log(m.squirclePoints({width: 100, height: 60, radius: 20}).points.length);")
        r = subprocess.run([NODE, "--input-type=module", "-e", code],
                           capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "100")
        self.assertNotIn("--width", r.stderr)


if __name__ == "__main__":
    unittest.main()
