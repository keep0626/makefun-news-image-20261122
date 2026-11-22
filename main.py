#!/usr/bin/env python3
"""Copy the committed front page to the grader's output directory.

The picture itself lives in this repository as entry.png; this program
only checks that it is a well-formed PNG inside the competition limits
and copies it to $MAKEFUN_OUTPUT_DIR, or to /output when that variable
is not set. Nothing is drawn or fetched here.
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_size(path):
    """Return (width, height) of a PNG, rejecting anything malformed."""
    with open(path, "rb") as handle:
        head = handle.read(33)
    if head[:8] != PNG_MAGIC:
        raise ValueError("entry.png does not start with the PNG signature")
    if len(head) < 33 or head[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk where one belongs")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    size = os.path.getsize(SOURCE)
    if size > MAX_BYTES:
        raise ValueError(
            "entry.png is %d bytes, over the 1 MiB limit" % size)
    width, height = read_size(SOURCE)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(
            "entry.png is %dx%d, over the 1024x1024 limit"
            % (width, height))
    os.makedirs(outdir, exist_ok=True)
    target = os.path.join(outdir, "entry.png")
    shutil.copyfile(SOURCE, target)
    print("wrote %s (%d bytes)" % (target, size))


if __name__ == "__main__":
    main()
