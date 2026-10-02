#!/usr/bin/env python3
"""Overnight self-improve loop for a PowerCore skill (Karpathy-style, guarded).

  cd agent-skills
  py -3.13 -m tools.skill_gap.overnight_loop --skill cc-report --until-perfect
  py -3.13 -m tools.skill_gap.overnight_loop --skill cc-report --max-iters 50 --sleep 30 --live

Never pushes, never starts bots, never touches .env. One SKILL.md edit per
iteration; rollback if total score drops.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _score_bundle(skill_dir: Path, *, live: bool, live_max: int) -> dict:
    from tools.skill_gap.body_assertions import run_body_assertions
    from tools.skill_gap.evals_runner import find_evals, run_evals_file
    from tools.skill_gap.run_triggers import run_triggers

    evals_path = find_evals(skill_dir)
    fixtures = run_evals_file(evals_path) if evals_path else {"ok": False, "score": "0/0", "passed": 0, "total": 0}
    triggers = run_triggers(skill_dir)
    body = run_body_assertions(skill_dir)
    live_res = None
    if live:
        from tools.skill_gap.live_runner import run_live_evals

        live_res = run_live_evals(skill_dir, max_cases=live_max)

    # Composite: fixtures + triggers + body (+ live if enabled)
    parts = [fixtures, triggers, body]
    if live_res is not None and not live_res.get("skipped"):
        parts.append(live_res)
    passed = sum(int(p.get("passed") or 0) for p in parts)
    total = sum(int(p.get("total") or 0) for p in parts)
    ok = all(bool(p.get("ok")) for p in parts if p.get("total", 0) > 0)
    return {
        "ok": ok,
        "passed": passed,
        "total": total,
        "score": f"{passed}/{total}",
        "fixtures": {"score": fixtures.get("score"), "ok": fixtures.get("ok")},
        "triggers": {"score": triggers.get("score"), "ok": triggers.get("ok")},
        "body": {"score": body.get("score"), "ok": body.get("ok")},
        "live": (
            {"score": live_res.get("score"), "ok": live_res.get("ok"), "skipped": live_res.get("skipped")}
            if live_res
            else None
        ),
        "_raw": {"fixtures": fixtures, "triggers": triggers, "body": body, "live": live_res},
    }


def _log(skill_dir: Path, row: dict) -> None:
    path = skill_dir / "evals" / "results.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _print(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Overnight skill self-improve loop")
    parser.add_argument("--skill", required=True)
    parser.add_argument("--max-iters", type=int, default=100, help="Safety cap (default 100)")
    parser.add_argument("--sleep", type=float, default=5.0, help="Seconds between iterations when perfect/watching")
    parser.add_argument("--until-perfect", action="store_true", help="Exit when composite score is perfect")
    parser.add_argument("--live", action="store_true", help="Also score live Vault Rotator ask outputs")
    parser.add_argument("--live-max", type=int, default=3, help="Max live positive cases per iter")
    parser.add_argument("--json-each", action="store_true", help="Print JSON each iteration")
    parser.add_argument(
        "--demo-break",
        action="store_true",
        help="Once at start: strip a required needle so the mutator has work (smoke only)",
    )
    args = parser.parse_args()

    skill_dir = _REPO / ".cursor" / "skills" / args.skill
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        _print(f"missing skill: {skill_md}")
        return 2

    from tools.skill_gap.mutator import backup_skill, propose_and_apply, restore_skill
    from tools.skill_gap import versions as V

    # Seed version history if empty so rollback always has a base.
    seed = V.ensure_seed(skill_dir, score="", note="auto-seed before overnight")
    if seed:
        _print(f"seeded version {seed.id}")

    if args.demo_break:
        text = skill_md.read_text(encoding="utf-8")
        # Remove all required phrases so body assertions fail (substring-safe).
        broken = text.replace("PASTE INTO CURSOR", "PASTE_INTO_CURSOR_REMOVED")
        if broken != text:
            skill_md.write_text(broken, encoding="utf-8")
            _print("demo-break: removed PASTE INTO CURSOR occurrences")

    _print(
        f"overnight start skill={args.skill} max_iters={args.max_iters} "
        f"until_perfect={args.until_perfect} live={args.live}"
    )

    best = -1
    for i in range(1, args.max_iters + 1):
        bundle = _score_bundle(skill_dir, live=args.live, live_max=args.live_max)
        row = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "skill": args.skill,
            "iter": i,
            "mode": "overnight",
            "score": bundle["score"],
            "ok": bundle["ok"],
            "fixtures": bundle["fixtures"],
            "triggers": bundle["triggers"],
            "body": bundle["body"],
            "live": bundle["live"],
            "mutation": None,
            "kept": None,
        }
        _print(f"iter {i}: {bundle['score']} ({'PASS' if bundle['ok'] else 'FAIL'})")
        if args.json_each:
            _print(json.dumps({k: v for k, v in row.items() if k != "mutation"}, ensure_ascii=False))

        if bundle["ok"]:
            best = max(best, bundle["passed"])
            _log(skill_dir, row)
            if args.until_perfect:
                _print("perfect — stopping")
                return 0
            time.sleep(max(0.0, args.sleep))
            continue

        # Mutate once
        bak = backup_skill(skill_md)
        raw = bundle["_raw"]
        mutation = propose_and_apply(
            skill_dir,
            body_result=raw["body"],
            trigger_result=raw["triggers"],
            live_result=raw.get("live"),
        )
        if mutation is None:
            row["mutation"] = {"kind": "none", "detail": "no mutator action"}
            _log(skill_dir, row)
            _print("no mutator action — sleeping")
            time.sleep(max(0.0, args.sleep))
            continue

        after = _score_bundle(skill_dir, live=args.live, live_max=args.live_max)
        if after["passed"] < bundle["passed"]:
            restore_skill(skill_md, bak)
            row["mutation"] = {"kind": mutation.kind, "detail": mutation.detail}
            row["kept"] = False
            row["after_score"] = after["score"]
            _log(skill_dir, row)
            _print(f"rollback {mutation.kind}: {bundle['score']} -> {after['score']}")
        else:
            row["mutation"] = {"kind": mutation.kind, "detail": mutation.detail}
            row["kept"] = True
            row["after_score"] = after["score"]
            row["score"] = after["score"]
            row["ok"] = after["ok"]
            try:
                snap = V.snapshot(
                    skill_dir,
                    score=after["score"],
                    note=f"overnight keep:{mutation.kind}",
                    source="overnight",
                )
                row["version"] = snap.id
                _print(f"versioned {snap.id}")
            except Exception as e:  # noqa: BLE001
                row["version_error"] = str(e)[:200]
                _print(f"version snapshot failed: {e}")
            _log(skill_dir, row)
            _print(f"kept {mutation.kind}: {bundle['score']} -> {after['score']}")
            best = max(best, after["passed"])
            if args.until_perfect and after["ok"]:
                _print("perfect after mutation — stopping")
                return 0

        # Drop backup if kept; keep bak file for forensics either way
        time.sleep(max(0.0, min(args.sleep, 2.0)))

    _print(f"hit max-iters={args.max_iters} best_passed={best}")
    return 0 if best >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
