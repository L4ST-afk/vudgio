"""玻璃审计闸（scripts/glass_audit.py）的判据实测。

钉四件事：blur 超限与玻璃叠玻璃必须是 E；同屏 backdrop 超账必须是 E；
把 blur 拿去做 transition 必须是 E；一份参数合规的样例必须通过（不能见玻璃就报红）。
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = Path(HERE).parent
SCRIPT = ROOT / "scripts" / "glass_audit.py"
sys.path.insert(0, str(ROOT / "scripts"))
import glass_audit  # noqa: E402

BAD = """
<html><head><style>
.card{background:rgba(255,255,255,.2);backdrop-filter:blur(20px);color:rgba(255,255,255,.6)}
.inner{backdrop-filter:blur(6px)}
.wrap{backdrop-filter:blur(4px);transition:backdrop-filter .3s}
</style></head><body>
<section id="s1"><div class="card">x</div><div class="wrap"><div class="inner">y</div></div></section>
<section id="s2">
  <div class="card">a</div><div class="card">b</div><div class="card">c</div><div class="card">d</div>
</section>
</body></html>
"""

GOOD = """
<html><head><style>
:root{--glass-blur:8px}
.card{background:rgba(0,0,0,.28);backdrop-filter:blur(var(--glass-blur));border:1px solid rgba(255,255,255,.55);color:#fff}
@media (prefers-reduced-motion: reduce){.card{transition:none}}
@supports not (backdrop-filter: blur(1px)){.card{backdrop-filter:none}}
</style></head><body><section id="s1"><div class="card">好</div></section></body></html>
"""


def rules(result):
    return {i["rule"] for i in result["issues"] if i["level"] == "E"}


class GlassAuditTests(unittest.TestCase):
    def test_bad_fixture_raises_the_four_signals(self):
        result = glass_audit.audit(BAD)
        got = rules(result)
        for need in ("blur-cap", "glass-on-glass", "backdrop-count", "animate-blur"):
            self.assertIn(need, got, f"缺 E 级判据 {need}：{sorted(got)}")

    def test_variable_blur_is_resolved(self):
        result = glass_audit.audit(GOOD)
        self.assertEqual(result["stats"]["glass_layers"], 1)
        self.assertEqual(result["stats"]["max_blur"], 8.0)

    def test_degrade_block_does_not_hide_the_glass(self):
        # 降级块里的 backdrop-filter:none 不能被并进基础规则，否则「有玻璃」会被判成「没玻璃」
        result = glass_audit.audit(GOOD)
        self.assertEqual(result["issues"], [])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.html"
            good = Path(tmp) / "good.html"
            bad.write_text(BAD, encoding="utf-8")
            good.write_text(GOOD, encoding="utf-8")
            for path, want in ((bad, 1), (good, 0)):
                proc = subprocess.run([sys.executable, str(SCRIPT), str(path)],
                                      capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(proc.returncode, want, proc.stdout + proc.stderr)
            proc = subprocess.run([sys.executable, str(SCRIPT), str(bad), "--json"],
                                  capture_output=True, text=True, encoding="utf-8")
            data = json.loads(proc.stdout)
            self.assertGreaterEqual(data["E"], 4)  # blur 超限按元素计，4 类信号至少各命中一次

    def test_tokens_block_is_css(self):
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            glass_audit.main([str(ROOT / "tests" / "fixtures" / "glass-good.html"), "--tokens"])
        self.assertIn("--glass-blur", buf.getvalue())
        self.assertIn("@supports not", buf.getvalue())


class FixtureFilesTests(unittest.TestCase):
    def test_fixtures_on_disk_match(self):
        good = ROOT / "tests" / "fixtures" / "glass-good.html"
        bad = ROOT / "tests" / "fixtures" / "glass-bad.html"
        self.assertTrue(good.is_file() and bad.is_file())
        self.assertEqual(glass_audit.audit(bad.read_text(encoding="utf-8"))["issues"] != [], True)
        self.assertEqual(glass_audit.audit(good.read_text(encoding="utf-8"))["issues"], [])


if __name__ == "__main__":
    unittest.main()
