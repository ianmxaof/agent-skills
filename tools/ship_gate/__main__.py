"""Nightly stress entrypoint (same as nightly.ps1)."""

from __future__ import annotations

import sys

from .run import main


def nightly() -> int:
    rc = 0
    for root in ("text-expander", "tbcc"):
        code = main(["--lane", "stress", "--root", root])
        if code != 0:
            rc = code
    return rc


if __name__ == "__main__":
    raise SystemExit(nightly() if "--nightly" in sys.argv else main())
