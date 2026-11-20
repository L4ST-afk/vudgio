"""本库自己的「超百行必有真目录」闸（补 太玉洞 在这里的盲区）。

背景：`太玉洞Tagnodon/scripts/check_limits.py` 见到 skill 根有 LICENSE 就把所有 references
当「外部件」，>100 行只报 info、⛔ 不判红（2026-11-17 那版为防拆外部件加的口子）。
浮龟根有 LICENSE，于是这条闸在本库**整片失效**——连自己写的卷也不再被查。

这里按同一条判据重新钉一遍，只认一件事：>100 行的卷，顶部要有 `## 目录`，且目录里有真链接。
"""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REFS = os.path.join(os.path.dirname(HERE), "references")
LIMIT = 100


def scan():
    rows = []
    for name in sorted(os.listdir(REFS)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(REFS, name)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        lines = text.count("\n")   # 与 wc -l 同口径
        if lines <= LIMIT:
            continue
        head = text[: text.find("## 目录")] if "## 目录" in text else ""
        links = re.findall(r"\]\(#[^)]+\)", text)
        rows.append((name, lines, bool(head != text and "## 目录" in text), len(links)))
    return rows


class TestReferenceToc(unittest.TestCase):
    def test_long_refs_have_real_toc(self):
        rows = scan()
        self.assertTrue(rows, "扫描为空：references 里一个超百行的卷都没有，闸可能没接上")
        bad = [(n, ln, t, k) for n, ln, t, k in rows if not (t and k >= 3)]
        self.assertEqual(bad, [], "超百行缺真目录（要 ## 目录＋至少 3 条链接）：%r" % (bad,))

    def test_scan_counts_match_wc(self):
        """口径自证：扫描给的行数要和 wc -l 对得上，否则闸量的是另一个对象。"""
        for name, lines, _, _ in scan():
            with open(os.path.join(REFS, name), "rb") as fh:
                real = fh.read().count(b"\n")   # wc -l 口径：数换行，不看末行有没有换行
            self.assertEqual(lines, real, "%s 行数口径不一致" % name)



    def test_claimed_volume_count_matches_disk(self):
        """宣称卷数要与盘上一致（本轮 54 对 55 的红灯就是缺这条）。"""
        root = os.path.dirname(HERE)
        actual = len([n for n in os.listdir(REFS) if n.endswith(".md")])
        for f in ("README.md", "README.zh-CN.md"):
            with open(os.path.join(root, f), encoding="utf-8") as fh:
                text = fh.read()
            m = re.search(r"(\d+)\s*(?:卷索引|volumes)", text)
            self.assertIsNotNone(m, "%s 里没有卷数宣称" % f)
            self.assertEqual(int(m.group(1)), actual, "%s 宣称 %s 卷，盘上 %d 卷" % (f, m.group(1), actual))

    def test_layer_count_matches_table(self):
        """「能力分成 N 层」要与紧随其后的表行数一致。"""
        root = os.path.dirname(HERE)
        with open(os.path.join(root, "SKILL.md"), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        for i, line in enumerate(lines):
            m = re.search(r"能力分成(\S+?)层", line)
            if not m:
                continue
            block = []
            for nxt in lines[i + 1:]:
                if nxt.startswith("|"):
                    block.append(nxt.strip())
                elif block:
                    break
            # 表头 1 行 + 分隔线若干，都算进 block；只数内容行
            content = [b for b in block if not re.fullmatch(r"\|[-:\s|]+\|", b)]
            rows = max(0, len(content) - 1)
            self.assertGreaterEqual(rows, 2, "没找到分层表")
            self.assertEqual(m.group(1), "六" if rows == 6 else self._cn(rows),
                             "宣称「%s 层」，表实 %d 行" % (m.group(1), rows))

    @staticmethod
    def _cn(n):
        return {4: "四", 5: "五", 6: "六", 7: "七", 8: "八"}.get(n, str(n))

if __name__ == "__main__":
    unittest.main(verbosity=2)
