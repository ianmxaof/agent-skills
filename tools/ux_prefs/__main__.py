"""PowerCore UX prefs tooling.

  py -3.13 -m tools.ux_prefs seed --all-projects --plain
"""

from __future__ import annotations

from tools.ux_prefs.seed_from_transcripts import main

if __name__ == "__main__":
    raise SystemExit(main())
