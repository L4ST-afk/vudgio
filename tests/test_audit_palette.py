#!/usr/bin/env python3
"""audit_palette.py 的判据回归：两个作用域各正反各一支。

钉三条：
1. 正常生成的一条色阶，累计漂移在 --cap-total 内 ⇒ 0 硬失败；
2. 手工造一条两端色相差 40° 的「色阶」⇒ 必红（累计漂移不封顶是真实缺陷）；
3. 角色板里文字压底不足 4.5 ⇒ 退出码 1；干净板 ⇒ 0。
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
AUDIT = os.path.join(SCRIPTS, "audit_palette.py")
EMIT = os.path.join(SCRIPTS, "emit_tokens.py")


def run(script, *args):
    p = subprocess.run([sys.executable, script] + list(args),
                       capture_output=True, text=True, encoding="utf-8", timeout=60)
    return p.returncode, p.stdout + p.stderr


class TestAuditPalette(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def write_tokens(self, ramps: dict) -> str:
        path = os.path.join(self.dir, "tokens.css")
        lines = [":root {"]
        for name, stops in ramps.items():
            for stop, hexv in stops.items():
                lines.append("  --color-%s-%s: %s;" % (name, stop, hexv))
        lines.append("}")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        return path

    def test_generated_ramp_passes(self):
        out = os.path.join(self.dir, "t")
        os.makedirs(out, exist_ok=True)
        rc, log = run(EMIT, "--base", "#eab308", "--out", out)
        self.assertEqual(rc, 0, log[-400:])
        tokens = os.path.join(out, "tokens.css")
        self.assertTrue(os.path.exists(tokens), "emit_tokens 没写出 tokens.css")
        rc, log = run(AUDIT, "--tokens", tokens)
        self.assertEqual(rc, 0, "生成色阶过不了色板审计：%s" % log[-400:])

    def test_hue_drift_over_budget_fails(self):
        # 100 号 345° 与 900 号 284°，相差 61°，且明度单调下降，只该被累计漂移这一条打红
        path = self.write_tokens({"brand": {
            100: "#ffd6e0", 300: "#f09ab0", 500: "#cf6a86",
            700: "#9b3e66", 900: "#55106e"}})
        rc, log = run(AUDIT, "--tokens", path)
        self.assertEqual(rc, 1, "累计色相漂移越界却没红：%s" % log[-400:])
        self.assertIn("累计漂移", log)

    def test_hue_stall_fails(self):
        """同一侧转了却在相邻两级停住 ⇒ 必红。

        这条对应真实事故：硬封顶把蓝 100/200 都压到 -20°，两级看起来是同一档。
        造法：亮端确实在转（228°→205°），但 200 与 300 都停在 220°，明度仍逐级下降。
        """
        path = self.write_tokens({"brand": {
            100: "#e5e9fa", 200: "#b6c8ec", 300: "#90a9da",
            500: "#3f7ba6", 700: "#395d6a", 900: "#273235"}})
        rc, log = run(AUDIT, "--tokens", path)
        self.assertEqual(rc, 1, "色相停级却没红：%s" % log[-400:])
        self.assertIn("色相停级", log)

    def test_text_contrast_fails(self):
        p = os.path.join(self.dir, "p.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"background": "#ffffff", "text": {"primary": "#8a8a8a"},
                       "fills": ["#2563eb"], "accents": ["#2563eb", "#06b6d4"]}, fh)
        rc, log = run(AUDIT, "--palette", p)
        self.assertEqual(rc, 1, "文字没到 4.5:1 却没红：%s" % log[-400:])

    def test_clean_palette_passes(self):
        p = os.path.join(self.dir, "ok.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"background": "#ffffff", "text": {"primary": "#111111"},
                       "fills": ["#1d4ed8"], "accents": ["#1d4ed8", "#f97316"]}, fh)
        rc, log = run(AUDIT, "--palette", p, "--json")
        self.assertEqual(rc, 0, "干净色板却红了：%s" % log[-400:])
        self.assertIn('"ok": true', log.replace(" ", " "))

    def write_palette(self, name, payload) -> str:
        p = os.path.join(self.dir, name)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
        return p

    # 暧昧带降级路径（2026-11-20 第三轮采样）：功能色场景下红橙天生 20–40°，
    # 色相救不了，只能换轴；所以必须有「登记依据就放行」的一档，且这一档本身要能被证伪。
    def test_band_pair_warns_by_default(self):
        p = self.write_palette("band.json", {
            "background": "#ffffff", "text": {"primary": "#111111"},
            "accents": ["#0e8c99", "#2563a8"]})       # 186° ↔ 211.6° = 26°，落暧昧带
        rc, log = run(AUDIT, "--palette", p, "--json")
        self.assertEqual(rc, 0, log[-400:])
        self.assertIn("暧昧带", log)
        self.assertIn('"warn": 1', log)

    def test_waiver_with_two_axes_passes(self):
        p = self.write_palette("waived.json", {
            "background": "#ffffff", "text": {"primary": "#111111"},
            "accents": ["#0e8c99", "#2563a8"],
            "waivers": [{"pair": ["accent1", "accent2"],
                         "basis": "面积 12% vs 2%、形状冗余（✓ 图标）、永不同框"}]})
        rc, log = run(AUDIT, "--palette", p, "--json")
        self.assertEqual(rc, 0, log[-400:])
        self.assertIn('"warn": 0', log)
        self.assertIn('"waived": 1', log)
        self.assertIn("换轴放行", log)

    def test_waiver_with_one_axis_still_warns(self):
        p = self.write_palette("weak.json", {
            "background": "#ffffff", "text": {"primary": "#111111"},
            "accents": ["#0e8c99", "#2563a8"],
            "waivers": [{"pair": ["accent1", "accent2"],
                         "basis": "这一对面积差别很大所以看得清"}]})   # 只claim面积一轴
        rc, log = run(AUDIT, "--palette", p)
        self.assertEqual(rc, 0, log[-400:])
        self.assertIn("豁免不合格", log)

    def test_stale_waiver_is_reported(self):
        p = self.write_palette("stale.json", {
            "background": "#ffffff", "text": {"primary": "#111111"},
            "accents": ["#0e8c99", "#2563a8"],
            "waivers": [{"pair": ["accent1", "accent3"],
                         "basis": "面积 12% vs 2%、形状冗余（✓ 图标）、永不同框"}]})
        rc, log = run(AUDIT, "--palette", p)
        self.assertEqual(rc, 0, log[-400:])
        self.assertIn("失效豁免", log)


if __name__ == "__main__":
    unittest.main()
