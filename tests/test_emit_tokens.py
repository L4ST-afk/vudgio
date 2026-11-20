#!/usr/bin/env python3
"""emit_tokens.py 的判据回归：色阶阶梯顺序、500 等于基色、四份产物齐全。"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "scripts", "emit_tokens.py")


def run(*args):
    p = subprocess.run([sys.executable, SCRIPT] + list(args),
                       capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout + p.stderr


class TestEmit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_files_and_base_hex(self):
        rc, out = run("--base", "#0f7b6c", "--name", "brand",
                      "--out", self.out, "--extended")
        self.assertEqual(rc, 0, out)
        for f in ("tokens.css", "theme.css", "DESIGN.md", "tokens.json"):
            self.assertTrue(os.path.exists(os.path.join(self.out, f)), f)
        css = open(os.path.join(self.out, "tokens.css"), encoding="utf-8").read()
        self.assertIn("--color-brand-500: #0f7b6c;", css)
        self.assertIn("--ease-out: cubic-bezier(0.23, 1, 0.32, 1);", css)
        theme = open(os.path.join(self.out, "theme.css"), encoding="utf-8").read()
        self.assertIn("@theme", theme)
        data = json.load(open(os.path.join(self.out, "tokens.json"), encoding="utf-8"))
        self.assertIn("brand", data)
        self.assertEqual(data["brand"]["500"], "#0f7b6c")

    def test_ladder_lightness_is_monotonic(self):
        rc, _ = run("--base", "#0f7b6c", "--out", self.out)
        self.assertEqual(rc, 0)
        with open(os.path.join(self.out, "tokens.json"), encoding="utf-8") as fh:
            ramp = json.load(fh)["brand"]
        stops = sorted(int(k) for k in ramp)
        self.assertEqual(stops, [100, 200, 300, 400, 500, 600, 700, 800, 900])

        def lum(h):
            c = h.lstrip("#")
            r, g, b = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        values = [lum(ramp[str(s)]) for s in stops]
        for i in range(len(values) - 1):
            self.assertGreater(values[i], values[i + 1], "色阶应为 100 最亮、900 最暗")

    def test_grey_ramp_runs(self):
        rc, out = run("--grey", "--temperature", "cool", "--name", "neutral",
                      "--out", self.out)
        self.assertEqual(rc, 0, out)
        css = open(os.path.join(self.out, "tokens.css"), encoding="utf-8").read()
        self.assertIn("--color-neutral-500:", css)

    def test_json_only_writes_nothing(self):
        rc, out = run("--base", "#eab308", "--json")
        self.assertEqual(rc, 0)
        self.assertIn('"500"', out)
        self.assertEqual(os.listdir(self.out), [])


if __name__ == "__main__":
    unittest.main()
