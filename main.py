"""news-image-20261124 — sum up Tuesday 24 November 2026 in one image.

The picture itself is pre-rendered at build time (see render.py) and stored
in this repository as entry.png. This program is the whole entrypoint: it
copies that exact file into the grader's output directory, using only the
Python standard library, with no network and no rendering at grade time.
That keeps the two grading runs byte-identical.

Run locally with:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, target)
    # Guard: the graded run must deliver the exact bytes we rendered.
    if os.path.getsize(target) != os.path.getsize(source):
        raise RuntimeError("entry.png copy is incomplete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
