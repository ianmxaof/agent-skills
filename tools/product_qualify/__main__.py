"""PowerCore Product Qualify (PPQ) CLI.

  py -3.13 -m tools.product_qualify board --plain
  py -3.13 -m tools.product_qualify status --id vault --plain
  py -3.13 -m tools.product_qualify scaffold --id github-presentation --plain
  py -3.13 -m tools.product_qualify media-prompt --id text-expander --plain
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

OPS = Path(r"C:\Powercore-repo-main\powercore-ops")
REGISTRY = OPS / "products" / "REGISTRY.yaml"
DOCTRINE = OPS / "design" / "powercore-product-qualification.md"
PRODUCTS = OPS / "products"

_STAGE_RE = re.compile(r"^\*\*Stage:\*\*\s*(P[0-6])", re.M)
_BLOCKER_RE = re.compile(
    r"^\|\s*(Q-\d+)\s*\|[^|]*\|\s*(missed|covered|blocked|n/a)\s*\|[^|]*\|\s*(yes)\s*\|",
    re.M | re.I,
)


def _parse_registry_products(text: str) -> list[dict[str, str]]:
    """Minimal YAML list parser for our REGISTRY shape (no PyYAML required)."""
    products: list[dict[str, str]] = []
    cur: dict[str, str] | None = None
    in_products = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("products:"):
            in_products = True
            continue
        if not in_products:
            continue
        if line.startswith("defaults:"):
            break
        if re.match(r"^\s*-\s+id:\s*", line):
            if cur:
                products.append(cur)
            cur = {"id": re.sub(r"^\s*-\s+id:\s*", "", line).strip()}
            continue
        if cur is None:
            continue
        m = re.match(r"^\s+([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith("#"):
            val = ""
        if " #" in val:
            val = val.split(" #", 1)[0].strip()
        val = val.strip('"').strip("'")
        if key != "id":
            cur[key] = val
    if cur:
        products.append(cur)
    return products


def load_registry() -> list[dict[str, str]]:
    if not REGISTRY.is_file():
        raise SystemExit(f"missing registry: {REGISTRY}")
    return _parse_registry_products(REGISTRY.read_text(encoding="utf-8"))


def checklist_path(product_id: str) -> Path:
    return PRODUCTS / product_id / "QUALIFICATION.md"


def read_stage(md: str, fallback: str = "P0") -> str:
    m = _STAGE_RE.search(md)
    return m.group(1) if m else fallback


def missed_blockers(md: str) -> list[str]:
    out: list[str] = []
    for m in _BLOCKER_RE.finditer(md):
        qid, status, _ = m.group(1), m.group(2).lower(), m.group(3)
        if status == "missed":
            out.append(qid)
    return out


def cmd_board(_: argparse.Namespace) -> int:
    rows = load_registry()
    print(f"PPQ board | {len(rows)} products | doctrine={DOCTRINE.name}")
    for p in rows:
        pid = p["id"]
        path = checklist_path(pid)
        if path.is_file():
            md = path.read_text(encoding="utf-8")
            stage = read_stage(md, p.get("stage", "P0"))
            blockers = missed_blockers(md)
            top = blockers[0] if blockers else "none"
            print(f"  {pid:20} stage={stage}  blockers={len(blockers)}  top={top}  pkg={p.get('packaging', '?')}")
        else:
            print(f"  {pid:20} stage={p.get('stage', '?')}  MISSING checklist  pkg={p.get('packaging', '?')}")
    return 0


def cmd_status(ns: argparse.Namespace) -> int:
    pid = ns.id
    path = checklist_path(pid)
    if not path.is_file():
        print(f"PPQ {pid}: no checklist at {path}", file=sys.stderr)
        return 1
    md = path.read_text(encoding="utf-8")
    stage = read_stage(md)
    blockers = missed_blockers(md)
    print(f"PPQ {pid} stage={stage} | blockers={len(blockers)} | next=see loose ends in {path}")
    if blockers:
        print("missed blockers: " + ", ".join(blockers))
    # print Next line if present
    for line in md.splitlines():
        if line.startswith("**Next:**"):
            print(line)
            break
    return 0


_SCAFFOLD = """# PPQ — {id}

**Stage:** P0  
**Updated:** (set on write)  
**Root:** `{root}`  
**Store id:** {store_id}  
**Packaging:** {packaging}  
**One-liner:** (fill)

## Scorecard

| Stage | Verdict | Notes |
|------:|---------|-------|
| P0 | missed | |
| P1 | missed | |
| P2 | missed | |
| P3 | missed | |
| P4 | missed | |
| P5 | missed | |
| P6 | missed | |

**Next:** complete P0 scaffold rows with evidence.

## Checklist

| id | stage | status | kind | blocker | evidence |
|----|------:|--------|------|---------|----------|
| Q-001 | P0 | missed | auto | yes | registry row |
| Q-002 | P0 | missed | manual | no | root + entrypoint |
| Q-003 | P1 | missed | manual | yes | smoke path |
| Q-004 | P2 | missed | manual | yes | chrome / ux-prefs audit |
| Q-005 | P3 | missed | manual | yes | vault/tray or n/a |
| Q-006 | P4 | missed | auto | yes | install artifact |
| Q-007 | P5 | missed | manual | yes | first-run ≤3 steps |
| Q-008 | P6 | missed | auto | yes | store + PSG pre_activate |
| Q-009 | P6 | missed | manual | no | cardLoopVideo via make-card-loop (or n/a) |

## Loose ends (≤10)

1. **blocker** — finish P0 registration evidence

## Smoke

```powershell
cd C:\\Powercore-repo-main\\agent-skills
py -3.13 -m tools.product_qualify status --id {id} --plain
```
"""


def cmd_scaffold(ns: argparse.Namespace) -> int:
    pid = ns.id
    path = checklist_path(pid)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and not ns.force:
        print(f"exists: {path} (pass --force to overwrite)", file=sys.stderr)
        return 1

    reg = {p["id"]: p for p in load_registry()}
    meta = reg.get(pid, {})
    root = meta.get("root", "C:/Powercore-repo-main/(unknown)")
    store_id = meta.get("store_id") or "none"
    packaging = meta.get("packaging", "unknown")

    # Ensure registry mention
    if pid not in reg:
        stub = (
            f"\n  - id: {pid}\n"
            f"    name: {pid}\n"
            f"    root: C:/Powercore-repo-main/{pid}\n"
            f"    store_id: null\n"
            f"    packaging: unknown\n"
            f"    ship_gate_root: null\n"
            f"    stage: P0\n"
            f"    notes: scaffolded by product_qualify\n"
        )
        text = REGISTRY.read_text(encoding="utf-8")
        # insert before defaults:
        if "\ndefaults:" in text:
            text = text.replace("\ndefaults:", stub + "\ndefaults:", 1)
        else:
            text = text.rstrip() + stub + "\n"
        REGISTRY.write_text(text, encoding="utf-8")
        print(f"registry: appended {pid}")
        root = f"C:/Powercore-repo-main/{pid}"
        store_id = "null"
        packaging = "unknown"

    body = _SCAFFOLD.format(
        id=pid,
        root=root,
        store_id=store_id,
        packaging=packaging,
    )
    path.write_text(body, encoding="utf-8")
    print(f"wrote {path}")
    print(f"PPQ {pid} stage=P0 | blockers=see checklist | next=fill evidence")
    return 0


STORE = Path(r"C:\Powercore-repo-main\powercore-store")
PROMPTS = STORE / "public" / "videos" / "GEMINI_CARD_LOOP_PROMPTS.md"
CARD_ART = STORE / "public" / "images" / "product-cards"
INBOX = STORE / "public" / "videos" / "product-loops" / "_inbox"
LOOP_SCRIPT = STORE / "scripts" / "make-card-loop.ps1"


def cmd_media_prompt(ns: argparse.Namespace) -> int:
    """Emit Gemini paste + ffmpeg finish steps for a store slug."""
    slug = (ns.id or "").strip()
    if not slug:
        print("need --id <store_slug>", file=sys.stderr)
        return 1

    def _out(s: str) -> None:
        # Windows cp1252 consoles choke on arrows in prompt docs.
        try:
            print(s)
        except UnicodeEncodeError:
            print(s.encode("ascii", "replace").decode("ascii"))

    art = CARD_ART / f"{slug}.png"
    if not art.is_file():
        print(f"warn: card art missing: {art}", file=sys.stderr)
    else:
        _out(f"Card art: {art}")

    master = ""
    motion = ""
    if PROMPTS.is_file():
        text = PROMPTS.read_text(encoding="utf-8")
        # Extract Master fenced block (first ```text after 'Master prompt')
        m = re.search(
            r"## Master prompt.*?```text\n(.*?)```",
            text,
            re.S,
        )
        if m:
            master = m.group(1).strip()
        mm = re.search(
            rf"### {re.escape(slug)}\s*\n```text\n(.*?)```",
            text,
            re.S,
        )
        if mm:
            motion = mm.group(1).strip()
        else:
            motion = (
                f"Motion: slow push-in for half the clip, then reverse to the exact "
                f"opening frame (seamless bounce for {slug})."
            )
    else:
        print(f"warn: prompts file missing: {PROMPTS}", file=sys.stderr)
        master = "(open GEMINI_CARD_LOOP_PROMPTS.md — master block missing)"
        motion = f"Motion: bounce A->B->A for {slug}."

    _out("")
    _out("========== PASTE INTO GEMINI (attach card PNG) ==========")
    _out(master)
    _out("")
    _out(motion)
    _out("========== END PASTE ==========")
    _out("")
    _out("After download:")
    _out(f"  1. Save raw to: {INBOX}\\{slug}.mp4")
    _out(
        "  2. Encode loop:\n"
        f"     cd {STORE}\\scripts\n"
        f'     .\\make-card-loop.ps1 -Video "{INBOX}\\{slug}.mp4" -Slug {slug}'
    )
    _out(f'  3. Catalog: "cardLoopVideo": "/videos/product-loops/{slug}.webm"')
    _out(f"  Script: {LOOP_SCRIPT}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="product_qualify", description="PowerCore PPQ CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def _add_plain(p: argparse.ArgumentParser) -> None:
        p.add_argument("--plain", action="store_true", help="compat flag (always plain)")

    p_board = sub.add_parser("board", help="list registry products + stages")
    _add_plain(p_board)
    p_board.set_defaults(func=cmd_board)

    p_status = sub.add_parser("status", help="one product scorecard line")
    p_status.add_argument("--id", required=True)
    _add_plain(p_status)
    p_status.set_defaults(func=cmd_status)

    p_sc = sub.add_parser("scaffold", help="create QUALIFICATION.md (+ registry stub)")
    p_sc.add_argument("--id", required=True)
    p_sc.add_argument("--force", action="store_true")
    _add_plain(p_sc)
    p_sc.set_defaults(func=cmd_scaffold)

    p_media = sub.add_parser(
        "media-prompt",
        help="emit Gemini card-loop prompt + ffmpeg finish steps for a store slug",
    )
    p_media.add_argument("--id", required=True, help="store slug (e.g. text-expander)")
    _add_plain(p_media)
    p_media.set_defaults(func=cmd_media_prompt)

    ns = ap.parse_args(argv)
    return int(ns.func(ns))


if __name__ == "__main__":
    raise SystemExit(main())
