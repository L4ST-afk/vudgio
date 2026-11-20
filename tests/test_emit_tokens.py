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


    def test_total_hue_drift_within_budget(self):
        """两端累计漂移必须 ≤ --cap-total：只封单步时，亮端与暗端会相加破 30°。"""
        import colorsys

        def hue(h):
            c = h.lstrip("#")
            r, g, b = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
            return colorsys.rgb_to_hsv(r, g, b)[0] * 360.0

        for base in ("#eab308", "#2563eb", "#0f7b6c", "#dc2626"):
            with self.subTest(base=base):
                rc, out = run("--base", base, "--json")
                self.assertEqual(rc, 0, out)
                ramp = json.JSONDecoder().raw_decode(out[out.index("{"):])[0]["brand"]
                gaps = [abs(hue(ramp["100"]) - hue(ramp["900"])) % 360]
                span = min(gaps[0], 360 - gaps[0])
                self.assertLessEqual(span, 30.0 + 0.6,
                                     "%s 两端累计漂移 %.1f° 越界" % (base, span))

    def test_cap_total_zero_disables_clamp(self):
        rc, out = run("--base", "#eab308", "--json", "--cap-total", "0")
        self.assertEqual(rc, 0, out)
        self.assertIn("500", out)

    def test_no_hue_stall_at_either_end(self):
        """封顶不许逐级硬夹：硬夹会让端部几级偏移相同（蓝 100/200 都是 -20°）。

        这条就是那次事故的回归——旧实现里蓝亮端 100 与 200 偏移相等，
        转出来的色相 204.0 与 207.9 甚至反向。判据：同一侧偏移大小随离 500 的距离
        单调递增、且两两不等；同时单步帽与总预算都必须真的顶得住。
        """
        sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
        import emit_tokens as et

        for base in ("#eab308", "#2563eb", "#0f7b6c", "#dc2626"):
            with self.subTest(base=base):
                h0, s0, l0 = et.hex_to_hsl(base)
                lightest, darkest, cap = 97.0, 17.0, 20.0
                L = {900: darkest, 500: l0, 100: lightest}
                L[700] = (L[900] + L[500]) / 2
                L[300] = (L[500] + L[100]) / 2
                L[800] = (L[900] + L[700]) / 2
                L[600] = (L[700] + L[500]) / 2
                L[400] = (L[500] + L[300]) / 2
                L[200] = (L[300] + L[100]) / 2
                off = et.ramp_offsets(h0, l0, L, cap, "auto", 30.0)

                self.assertLessEqual(max(abs(v) for v in off.values()), cap + 0.01,
                                     "%s 单步偏移超帽" % base)
                self.assertLessEqual(max(off.values()) - min(off.values()), 30.0 + 0.01,
                                     "%s 总预算超限" % base)

                for sign, name in ((1, "亮端"), (-1, "暗端")):
                    side = sorted(((abs(L[s] - l0), abs(off[s])) for s in L
                                   if off[s] * sign > 0), reverse=True)
                    mags = [m for _, m in side]
                    if len(mags) < 2:
                        continue
                    self.assertEqual(len(set(round(m, 3) for m in mags)), len(mags),
                                     "%s %s 有两级偏移相同：%s" % (base, name, mags))
                    for i in range(len(mags) - 1):
                        self.assertGreater(mags[i], mags[i + 1],
                                           "%s %s 偏移没有随离 500 变远而变大：%s"
                                           % (base, name, mags))


    def test_endpoint_fold_at_cap(self):
        """单侧帽的语义＝端点预算：输出端点必须恰好等于 min(自然端点, cap)。

        这条把「20° 是什么」钉死（2026-11-20 外部评审两轮互斥之后补）：20° 是**单侧端点**预算，
        不是步进帽。500→端点共 4 级线性分配，端点 20° ≡ 5°/步；按步进解读才会“永不触发”。
        判据：扫一串自然端点 E，输出端点 = min(E, 20)，曲线只在 20 处折一次；
        且封顶后每一级都等于自然值乘同一个系数（比例压，⛔ 不是把端部硬切）。
        """
        sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
        import emit_tokens as et

        cap = 20.0
        h0, s0, l0 = et.hex_to_hsl("#dc2626")
        seen_below = seen_above = 0
        for lightest in (58.0, 66.0, 74.0, 82.0, 90.0, 100.0):
            with self.subTest(lightest=lightest):
                L = {500: l0, 100: lightest}
                for stop, frac in ((400, 0.2), (300, 0.5), (200, 0.8)):
                    L[stop] = l0 + (lightest - l0) * frac
                nat = et.ramp_offsets(h0, l0, L, 999.0, "auto", 0)
                cut = et.ramp_offsets(h0, l0, L, cap, "auto", 0)
                e_nat = max(abs(v) for v in nat.values())
                e_cut = max(abs(v) for v in cut.values())

                if e_nat <= cap:
                    seen_below += 1
                    for s in L:
                        self.assertAlmostEqual(cut[s], nat[s], places=3,
                                               msg="自然端点 %.1f° 未超帽却被改了" % e_nat)
                else:
                    seen_above += 1
                    self.assertAlmostEqual(e_cut, cap, places=2,
                                           msg="自然端点 %.1f° 封顶后没落在 %.1f°" % (e_nat, cap))
                    k = cap / e_nat
                    for s in L:
                        self.assertAlmostEqual(cut[s], nat[s] * k, places=2,
                                               msg="第 %s 级不是等比压（应乘 %.3f）" % (s, k))
                # 端点是最大偏移那一级：封顶后最大只能出现在最远离 500 的级上
                self.assertEqual(max(cut, key=lambda s: abs(cut[s])),
                                 max(L, key=lambda s: abs(L[s] - l0)))

        self.assertGreaterEqual(seen_below, 1, "扫到的自然端点全都超帽，测不出折点")
        self.assertGreaterEqual(seen_above, 1, "扫到的自然端点全都未超帽，测不出折点")

    def test_total_budget_scales_uniformly(self):
        """总预算闸也是比例压：跨度 = min(自然跨度, cap_total)，全级同一系数。"""
        sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
        import emit_tokens as et

        for base in ("#2563eb", "#eab308"):
            with self.subTest(base=base):
                h0, s0, l0 = et.hex_to_hsl(base)
                L = {900: 17.0, 500: l0, 100: 97.0}
                for stop, frac in ((800, 0.875), (700, 0.75), (600, 0.875)):
                    L[stop] = 17.0 + (l0 - 17.0) * frac
                for stop, frac in ((400, 0.2), (300, 0.5), (200, 0.8)):
                    L[stop] = l0 + (97.0 - l0) * frac
                nat = et.ramp_offsets(h0, l0, L, 999.0, "auto", 0)
                cut = et.ramp_offsets(h0, l0, L, 999.0, "auto", 30.0)
                spread_nat = max(nat.values()) - min(nat.values())
                spread_cut = max(cut.values()) - min(cut.values())
                self.assertAlmostEqual(spread_cut, min(spread_nat, 30.0), places=2)
                if spread_nat > 30.0:
                    k = 30.0 / spread_nat
                    for s in L:
                        self.assertAlmostEqual(cut[s], nat[s] * k, places=2)


if __name__ == "__main__":
    unittest.main()
