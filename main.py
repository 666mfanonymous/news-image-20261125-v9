#!/usr/bin/env python3
# main.py deterministically copies entry.png to the requested output directory.
# entry.png is the graded artifact; this entrypoint preserves its exact bytes.
"""Deterministic make.fun entrypoint for news-image-20261125: copies entry.png to output dir."""

from __future__ import annotations

import os
from pathlib import Path


def main() -> None:
    src = Path(__file__).resolve().parent / "entry.png"
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if output_dir:
        dest = Path(output_dir) / "entry.png"
    else:
        dest = Path("/output/entry.png")

    dest.parent.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    dest.write_bytes(data)


if __name__ == "__main__":
    main()
