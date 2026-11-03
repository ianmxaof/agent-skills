#!/usr/bin/env python3
"""Render a cleanroom brief (Output Contract markdown) from evidence records.

Pure and deterministic: same records + same date -> same text. No capture, no network.

    py -3.13 scripts/render_brief.py baseline.json [candidate.json] [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from evidence_envelope import (  # noqa: E402
    EvidenceRecord,
    all_pass,
    delta,
    load_record,
)


def _cell(x: object) -> str:
    text = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False, sort_keys=True)
    return text.replace("|", "\\|").replace("\n", " ")


def render_brief(
    baseline: EvidenceRecord,
    candidate: EvidenceRecord | None = None,
    *,
    date: str = "unspecified",
    tolerance: float = 0.0,
) -> str:
    by_id = {i["id"]: i for i in baseline["items"]}
    out: list[str] = ["# Cleanroom brief", ""]

    out += [
        "## Source",
        "",
        f"- url: {baseline['source']}",
        f"- mode: {baseline['mode']}",
        f"- date: {date}",
        "",
    ]

    out += [
        "## Evidence summary",
        "",
        "| id | kind | confidence | coverage | limits |",
        "|----|------|------------|----------|--------|",
    ]
    for sid in baseline["summary"]:
        i = by_id[sid]
        out.append(
            f"| {_cell(sid)} | {_cell(i['kind'])} | {i['confidence']} | "
            f"{_cell(i['coverage'])} | {_cell(i['limits'])} |"
        )
    hidden = len(baseline["items"]) - len(baseline["summary"])
    if hidden:
        out += ["", f"_{hidden} more item(s) not in summary — page with `page_items`._"]
    out.append("")

    out += [
        "## Build brief",
        "",
        "Must match (baseline is the contract; `kind` + `value` are checked):",
        "",
    ]
    for i in baseline["items"]:
        out.append(
            f"- `{i['id']}` ({i['kind']}): {_cell(i['value'])} — {i['confidence']} confidence"
        )
    out += [
        "",
        "Stack / structure notes: not derivable from evidence; the build agent states its own.",
        "",
    ]

    out += ["## Check delta (after build)", ""]
    rows = None
    if candidate is None:
        out += ["_Awaiting build — no candidate capture yet. Not scoring._", ""]
    else:
        rows = delta(baseline, candidate, tolerance=tolerance)
        cand_by_id = {i["id"]: i for i in candidate["items"]}
        out += [
            f"Candidate: {candidate['source']}",
            "",
            "| item | baseline | result | pass/fail | note |",
            "|------|----------|--------|-----------|------|",
        ]
        for r in rows:
            b = by_id.get(r["id"])
            c = cand_by_id.get(r["id"])
            out.append(
                f"| {_cell(r['id'])} | {_cell(b['value']) if b else '—'} | "
                f"{_cell(c['value']) if c else '—'} | {'pass' if r['pass'] else 'fail'} | "
                f"{_cell(r['note'])} |"
            )
        passed = sum(1 for r in rows if r["pass"])
        verdict = "PASS" if all_pass(rows) else "FAIL"
        out += ["", f"**Overall: {verdict}** — {passed}/{len(rows)} rows pass.", ""]

    out += ["## Next", ""]
    if rows is None:
        out += [
            "1. Build against the must-match list.",
            "2. Re-capture at the same widths/state and re-run with the candidate record.",
        ]
    elif all_pass(rows):
        out += ["1. Stop for operator ACK on pass."]
    else:
        out += [
            "1. Fix the failing rows above.",
            "2. Re-capture and re-run the delta.",
            "3. Stop for operator ACK only after all rows pass.",
        ]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("baseline")
    ap.add_argument("candidate", nargs="?")
    ap.add_argument("--date", default="unspecified")
    ap.add_argument("--tolerance", type=float, default=0.0)
    a = ap.parse_args()
    cand = load_record(a.candidate) if a.candidate else None
    text = render_brief(load_record(a.baseline), cand, date=a.date, tolerance=a.tolerance)
    sys.stdout.buffer.write(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
