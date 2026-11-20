"""判据级回归：spring_to_linear.py 的曲线必须真落在它声称的时长与过冲上。

⛔ 只测「命令能跑」不算——那和 scripts/selftest.py 的冒烟重复。这里钉四件：
1. `--target` 反解的落定时刻误差 ≤3%；
2. 目标过冲与实测过冲差 ≤2 个百分点；
3. 输出能被 CSS 解析：`linear(...)` 首值 0、末值 1、点数 20–30；
4. 解析式近似确实偏——所以反解必须走数值二分（撤掉它会红）。
"""
import importlib.util
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "scripts", "spring_to_linear.py")


def run(*args):
    p = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, encoding="utf-8", timeout=60)
    return p.returncode, p.stdout


def load_module():
    spec = importlib.util.spec_from_file_location("s2l", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSpringToLinear(unittest.TestCase):
    def test_target_duration_is_hit(self):
        for target, over in ((200, 8), (300, 0), (500, 12)):
            with self.subTest(target=target, overshoot=over):
                rc, out = run("--target", str(target), "--overshoot", str(over), "--json")
                self.assertEqual(rc, 0, out[-300:])
                row = json.loads(out)
                self.assertLessEqual(abs(row["seconds"] * 1000 - target), target * 0.03)
                self.assertLessEqual(abs(row["overshoot_pct"] - over), 2)

    def test_curve_is_css_parsable(self):
        rc, out = run("--target", "200", "--overshoot", "8", "--json")
        self.assertEqual(rc, 0)
        row = json.loads(out)
        curve = row["linear"]
        self.assertTrue(curve.startswith("linear(") and curve.endswith(")"))
        vals = [float(v) for v in curve[len("linear("):-1].split(",")]
        self.assertEqual(vals[0], 0.0)
        self.assertEqual(vals[-1], 1.0)
        self.assertGreaterEqual(len(vals), 20)
        self.assertLessEqual(len(vals), 30)
        self.assertGreater(max(vals), 1.0, "过冲被上钳掉了")
        self.assertIn("cubic-bezier(", row["fallback"])

    def test_bad_arguments_exit_2(self):
        self.assertEqual(run("-k", "0", "-c", "5")[0], 2)
        self.assertEqual(run()[0], 2)
        self.assertEqual(run("--target", "5")[0], 2)

    def test_target_bounds(self):
        """值域 40–1200（改阈值要覆盖边界两侧）。"""
        for ms in (40, 1200):
            rc, out = run("--target", str(ms), "--json")
            self.assertEqual(rc, 0, "%dms 应当接受" % ms)
            got = json.loads(out)["seconds"] * 1000
            self.assertLessEqual(abs(got - ms), ms * 0.03, "%dms 落定实测 %.0fms" % (ms, got))
        for ms in (39, 1201):
            self.assertEqual(run("--target", str(ms))[0], 2, "%dms 应当拒绝" % ms)

    def test_analytic_approximation_is_off(self):
        """负臂：解析式 e^{-ζωt}=0.005 会偏，所以 --target 必须走数值二分。"""
        m = load_module()
        real = m.settle_time(m.simulate(112, 21))
        approx = 5.3 / (m.damping_ratio(112, 21) * (112 ** 0.5))
        self.assertGreater(abs(real - approx), 0.02, "解析式竟然对得上，判据已失去牙齿")



    def test_samples_bounds_have_negative_arm(self):
        """撤掉值域闸要能红：3 与 61 必须 rc=2（本轮实测缺口：撤闸后全绿）。"""
        for n in ("3", "61"):
            rc, _ = run("--preset", "咔嗒", "--samples", n)
            self.assertEqual(rc, 2, "samples=%s 应 rc=2，实得 %d" % (n, rc))
        for n in ("4", "60"):
            rc, _ = run("--preset", "咔嗒", "--samples", n)
            self.assertEqual(rc, 0, "samples=%s 应 rc=0，实得 %d" % (n, rc))

    def test_clamped_settle_is_not_called_stable(self):
        """截断时不许再说「位移稳定」：k=300 c=3 落定触到 3s 上限。"""
        rc, out = run("-k", "300", "-c", "3", "--samples", "24")
        self.assertEqual(rc, 0)
        self.assertIn("未在", out, "触顶仍打印稳定：%s" % out.splitlines()[:2])
        rc2, out2 = run("--target", "200", "--overshoot", "8")
        self.assertNotIn("未在", out2, "正常曲线不该报截断")

if __name__ == "__main__":
    unittest.main(verbosity=2)
