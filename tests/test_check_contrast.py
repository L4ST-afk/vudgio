#!/usr/bin/env python3
"""check_contrast.py 的判据回归：4.5/3.0 两档、矩阵退出码、感知亮度。"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "scripts", "check_contrast.py")


def run(*args):
    p = subprocess.run([sys.executable, SCRIPT] + list(args),
                       capture_output=True, text=True, encoding="utf-8", timeout=30)
    return p.returncode, p.stdout + p.stderr


class TestPair(unittest.TestCase):
    def test_black_on_white_is_21(self):
        rc, out = run("--pair", "#000000", "#ffffff")
        self.assertEqual(rc, 0)
        self.assertIn("21.00", out)

    def test_mid_grey_fails_normal_text(self):
        rc, out = run("--pair", "#777777", "#ffffff")
        self.assertEqual(rc, 1)
        self.assertIn("FAIL", out)

    def test_same_colour_passes_as_large_only(self):
        rc_normal, _ = run("--pair", "#949494", "#ffffff")
        rc_large, out = run("--pair", "#949494", "#ffffff", "--size", "large")
        self.assertEqual(rc_normal, 1)
        self.assertEqual(rc_large, 0)
        self.assertIn("PASS", out)


class TestMatrix(unittest.TestCase):
    def test_matrix_counts_and_exit_code(self):
        data = {"pairs": [
            {"fg": "#111111", "bg": "#ffffff", "name": "正文"},
            {"fg": "#cccccc", "bg": "#ffffff", "name": "弱提示"},
        ]}
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "pairs.json")
            open(path, "w", encoding="utf-8").write(json.dumps(data))
            rc, out = run("--matrix", path)
        self.assertEqual(rc, 1)
        self.assertIn("1/2", out)

    def test_matrix_without_pairs_is_usage_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "empty.json")
            open(path, "w", encoding="utf-8").write("{}")
            rc, out = run("--matrix", path)
        self.assertEqual(rc, 2)
        self.assertIn("pairs", out)


class TestBrightness(unittest.TestCase):
    def test_yellow_reads_brighter_than_blue(self):
        rc, out = run("--brightness", "#eab308", "#2563eb")
        self.assertEqual(rc, 0)
        rows = [ln for ln in out.splitlines() if "感知亮度" in ln]
        self.assertEqual(len(rows), 2)
        yellow = float(rows[0].split("感知亮度")[1].split()[0])
        blue = float(rows[1].split("感知亮度")[1].split()[0])
        self.assertGreater(yellow, blue)


if __name__ == "__main__":
    unittest.main()
