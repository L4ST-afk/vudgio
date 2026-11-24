"""示范页的自证：README 里那段动图不能指向一个坏页。

钉四件（都不联网、不开浏览器）：
1. `demo/index.html` 引的样式表都在盘上——引了不存在的 `tokens.css`，页面在别人机器上是白板；
2. 页面里有 `prefers-reduced-motion` 与自己的开关两处降级——只有开关而没有媒体查询，系统级偏好就失效；
3. 页面里的曲线确实来自本库脚本（出现 `linear(` 且不是手写的一两个数）；
4. README 引的那张图存在且不像占位图（>50KB）。
"""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEMO = os.path.join(ROOT, "demo")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class TestDemoPage(unittest.TestCase):
    def test_stylesheets_exist(self):
        html = read(os.path.join(DEMO, "index.html"))
        hrefs = re.findall(r'<link[^>]+href="([^"]+)"', html)
        self.assertTrue(hrefs, "示范页一个样式表都没引")
        for href in hrefs:
            if href.startswith(("http:", "https:", "//")):
                continue
            self.assertTrue(os.path.exists(os.path.join(DEMO, href)), "缺文件：%s" % href)

    def test_reduced_motion_in_two_places(self):
        html = read(os.path.join(DEMO, "index.html"))
        self.assertIn("prefers-reduced-motion", html, "缺系统级降级：媒体查询")
        self.assertIn('id="rm"', html, "缺页面内开关")

    def test_curves_come_from_script(self):
        html = read(os.path.join(DEMO, "index.html"))
        curves = re.findall(r"linear\(([\d.,\s]+)\)", html)
        self.assertGreaterEqual(len(curves), 3, "示范页应有三条反解曲线")
        for body in curves:
            n = len([v for v in body.split(",") if v.strip()])
            self.assertGreaterEqual(n, 20, "曲线被截断了：%d 个采样点" % n)

    def test_readme_gif_is_real(self):
        gif = os.path.join(DEMO, "motion-demo.gif")
        self.assertTrue(os.path.exists(gif), "README 引的动图不在盘上")
        self.assertGreater(os.path.getsize(gif), 50 * 1024, "动图小于 50KB，多半是占位或截断")
        for name in ("README.md", "README.en.md"):
            self.assertIn("demo/motion-demo.gif", read(os.path.join(ROOT, name)), "%s 没引动图" % name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
