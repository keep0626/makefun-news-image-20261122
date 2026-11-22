#!/usr/bin/env python3
"""make.fun bounty: Sum up 22 November's world news in one image.

The entry image is drawn by render.py (Pillow, DejaVu) from the 32
verified 22 Nov 2026 stories in stories.json, and committed here as
entry.png. This program only copies it to the output directory: the
grader runs with the standard library alone and no network, so the
copy keeps the entry deterministic and offline. Two runs write the
same bytes.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out = os.path.join(out_dir, "entry.png")
    if not os.path.isfile(SRC):
        print("entry.png not found next to main.py", file=sys.stderr)
        return 1
    with open(SRC, "rb") as fh:
        head = fh.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    if os.path.getsize(SRC) > MAX_BYTES:
        print("entry.png exceeds the 1 MiB limit", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, out)
    digest = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"wrote {out} ({os.path.getsize(out)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
