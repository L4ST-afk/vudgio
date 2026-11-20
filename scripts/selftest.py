#!/usr/bin/env python3
"""离线自检（冒烟级）：语法能过、CLI 能起来。⛔ 不联网、不读凭据、不写业务文件。

⚠️ 边界：这**不是判据级回归**——只证「脚本没坏到起不来」；业务口径仍靠 references/ 的验收项。
"""
import os
import py_compile
import subprocess
import sys

# Windows 控制台默认 cp1252，✓/⚠/中文会在 print 时抛 UnicodeEncodeError；
# 统一按 UTF-8 输出，编不出的字符降级成 ?，别让编码把业务判断顶掉。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


HERE = os.path.dirname(os.path.abspath(__file__))
ENTRIES = ("build_explorer.py", "check_contrast.py", "emit_tokens.py", "spring_to_linear.py")


def main():
    ok = True
    for f in sorted(os.listdir(HERE)):
        if f.endswith(".py") and f != "selftest.py":
            try:
                py_compile.compile(os.path.join(HERE, f), doraise=True)
            except Exception as e:
                print("FAIL 编译 %s: %s" % (f, e))
                ok = False
    for entry in ENTRIES:
        p = subprocess.run([sys.executable, os.path.join(HERE, entry), "--help"],
                           capture_output=True, text=True, encoding="utf-8", timeout=30)
        out = p.stdout + p.stderr
        if p.returncode != 0 or "usage" not in out.lower():
            print("FAIL %s --help 起不来（rc=%d）：%s" % (entry, p.returncode, out[-300:]))
            ok = False
    print("PASS 冒烟自检" if ok else "FAIL 冒烟自检")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
