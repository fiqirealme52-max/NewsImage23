#!/usr/bin/env python3
"""News 23 entrypoint: copy entry.png to /output/entry.png after checks.

Validates the PNG signature and that the image is exactly 1024x1024
before writing. No network access. Deterministic: entry.png is a
pre-rendered artifact (see draw.py); this script only validates + copies.
Running it twice produces the same /output/entry.png byte for byte.
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST_DIR = "/output"
DST = os.path.join(DST_DIR, "entry.png")

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    with open(SRC, "rb") as f:
        data = f.read()
    if not data.startswith(PNG_MAGIC):
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        print(f"entry.png is {width}x{height}, expected 1024x1024",
              file=sys.stderr)
        return 1
    os.makedirs(DST_DIR, exist_ok=True)
    shutil.copyfile(SRC, DST)
    print(f"wrote {DST} ({len(data)} bytes, 1024x1024)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
