"""PowerCore Ship Gate CLI.

Usage:
  py -3.13 -m tools.ship_gate.run --auto --root text-expander --json
  py -3.13 -m tools.ship_gate.run --lane live --root tbcc --json
  py -3.13 -m tools.ship_gate.run --lane live --root tbcc --deployed --json
  py -3.13 -m tools.ship_gate.run --check-evidence --root text-expander
  py -3.13 -m tools.ship_gate.run --lane pre_activate --product text-expander --json
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
import time
from pathlib import Path
from typing import Any

from .evidence import (
    check_evidence_fresh,
    utc_now,
    write_pre_activate,
    write_root_evidence,
    write_run_log,
)
from .registry import find_root, load_registry, roots
from .runners import run_watch, watch_in_range
from .tree_hash import short_hash, tree_hash
from .verdicts import is_green, normalize_verdict, worst_verdict


def _agent_skills_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _new_run_id() -> str:
    return "r" + secrets.token_hex(2)


def format_summary_line(payload: dict[str, Any]) -> str:
    run_id = payload.get("run_id") or "?"
    tree = short_hash(str(payload.get("tree_hash") or ""), 8)
    lane = payload.get("lane") or "lean"
    watches = payload.get("watches") or []
    n_ok = sum(1 for w in watches if normalize_verdict(w.get("verdict")) == "ok")
    n_idle = sum(1 for w in watches if normalize_verdict(w.get("verdict")) == "idle")
    n_bad = sum(1 for w in watches if not is_green(w.get("verdict")))
    worst = normalize_verdict(payload.get("worst"))
    reason = ""
    if not is_green(worst):
        for w in watches:
            if normalize_verdict(w.get("verdict")) == worst:
                evidence = str(w.get("evidence") or "")[:80]
                reason = f" [{w.get('id')}: {evidence}]"
                break
    ev = payload.get("evidence_path") or ""
    return (
        f"PSG {run_id} tree={tree} {lane}: {n_ok} ok / {n_idle} idle / {n_bad} not-green"
        f" - {worst}{reason} - evidence: {ev}"
    )


def _store_root(registry: dict[str, Any]) -> Path | None:
    for r in roots(registry):
        if str(r.get("id")) == "store":
            return Path(str(r.get("root")))
    return None


def run_root(
    root_cfg: dict[str, Any],
    *,
    lane: str,
    defaults: dict[str, Any],
    store_root: Path | None,
    deployed: bool = False,
    product_filter: str | None = None,
) -> dict[str, Any]:
    root = Path(str(root_cfg.get("root")))
    path_globs = list(root_cfg.get("paths") or [])
    ignore = list(root_cfg.get("ignore") or [])
    th = tree_hash(root, path_globs, ignore)
    run_id = _new_run_id()
    watches_out: list[dict[str, Any]] = []
    unmapped: list[str] = []

    lean_budget = float(defaults.get("lean_budget_s") or 180)
    t_start = time.perf_counter()

    for watch in root_cfg.get("watches") or []:
        wlane = str(watch.get("lane") or "lean")
        if lane == "lean" and wlane != "lean":
            continue
        if lane == "live" and wlane != "live":
            continue
        if lane == "stress" and wlane != "stress":
            continue
        if lane == "pre_activate" and wlane not in ("lean", "pre_activate"):
            # pre_activate also runs lean watches for the product root
            if wlane != "lean":
                continue
        if wlane == "live" and not deployed and lane != "live":
            continue
        if watch.get("runs_where") == "island" and lane == "lean":
            continue
        if product_filter and root_cfg.get("store_id") and str(root_cfg.get("store_id")) != product_filter:
            if str(root_cfg.get("id")) != product_filter:
                continue

        # when_paths: for Phase 1 auto, run all lean watches on the root
        if not watch_in_range(watch, ["*"]):
            continue

        if time.perf_counter() - t_start > lean_budget and lane == "lean":
            watches_out.append(
                {
                    "id": str(watch.get("id")),
                    "verdict": "blocked",
                    "evidence": f"lean budget {lean_budget}s exceeded",
                    "stop_kind": watch.get("stop_kind"),
                }
            )
            break

        result = run_watch(
            watch,
            root=root,
            root_cfg=root_cfg,
            defaults=defaults,
            store_root=store_root,
        )
        watches_out.append(result)

    worst = worst_verdict(w.get("verdict") for w in watches_out) if watches_out else "ok"
    payload: dict[str, Any] = {
        "run_id": run_id,
        "ts": utc_now(),
        "agent": os_agent(),
        "lane": lane,
        "root": root_cfg.get("id"),
        "tree_hash": th,
        "worst": worst,
        "watches": watches_out,
        "unmapped": unmapped,
    }
    ev_path = write_root_evidence(root, payload)
    payload["evidence_path"] = str(ev_path)
    write_run_log(_agent_skills_root(), run_id, payload)

    if lane == "stress":
        from .stress import write_stress_evidence

        stress_path = write_stress_evidence(
            _agent_skills_root(),
            root_id=str(root_cfg.get("id")),
            product_id=(
                str(root_cfg.get("store_id")) if root_cfg.get("store_id") else None
            ),
            payload=payload,
        )
        payload["stress_evidence_path"] = str(stress_path)

    payload["summary"] = format_summary_line(payload)
    return payload


def os_agent() -> str:
    import os

    return os.environ.get("PSG_AGENT", "cursor")


def cmd_auto(args: argparse.Namespace) -> int:
    registry = load_registry()
    defaults = registry.get("defaults") or {}
    store = _store_root(registry)
    results: list[dict[str, Any]] = []
    unmapped_msgs: list[str] = []

    selected = []
    if args.root:
        cfg = find_root(registry, args.root)
        if not cfg:
            print(f"PSG: unknown root {args.root}", file=sys.stderr)
            return 2
        selected = [cfg]
    else:
        selected = roots(registry)
        if args.lane == "live":
            # Only roots that declare at least one live watch
            selected = [
                r
                for r in selected
                if any(str(w.get("lane")) == "live" for w in (r.get("watches") or []))
            ]
        elif args.lane == "stress":
            selected = [
                r
                for r in selected
                if any(str(w.get("lane")) == "stress" for w in (r.get("watches") or []))
            ]

    for root_cfg in selected:
        root = Path(str(root_cfg.get("root")))
        if not root.is_dir():
            unmapped_msgs.append(f"PSG: unmapped missing-root {root_cfg.get('id')}")
            continue
        # Phase 1: run lean for every existing registered root when --auto
        # (caller can pass --root to narrow). Skip if only check-evidence.
        payload = run_root(
            root_cfg,
            lane=args.lane,
            defaults=defaults,
            store_root=store,
            deployed=args.deployed,
            product_filter=args.product,
        )
        results.append(payload)
        print(payload["summary"])
        if not is_green(payload.get("worst")) and not args.json:
            for w in payload.get("watches") or []:
                if not is_green(w.get("verdict")):
                    print(
                        f"Not ready: {w.get('id')}: {w.get('evidence')}",
                        file=sys.stderr,
                    )
                    break

    for m in unmapped_msgs:
        print(m)

    if args.json:
        print(json.dumps({"results": results, "unmapped": unmapped_msgs}, indent=2))

    if not results:
        return 1
    worst = worst_verdict(r.get("worst") for r in results)
    return 0 if is_green(worst) else 1


def cmd_check_evidence(args: argparse.Namespace) -> int:
    registry = load_registry()
    cfg = find_root(registry, args.root)
    if not cfg:
        print(f"PSG: unknown root {args.root}", file=sys.stderr)
        return 2
    root = Path(str(cfg.get("root")))
    th = tree_hash(root, list(cfg.get("paths") or []), list(cfg.get("ignore") or []))
    result = check_evidence_fresh(root, th)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("ok"):
            print(f"PSG evidence ok — {result.get('path')}")
        else:
            print(f"PSG evidence fail — {result.get('reason')} — {result.get('path')}")
    return 0 if result.get("ok") else 1


def cmd_pre_activate(args: argparse.Namespace) -> int:
    """Run lean on product root + write pre_activate evidence stub (R2 HEAD when configured)."""
    registry = load_registry()
    defaults = registry.get("defaults") or {}
    store = _store_root(registry)
    product = args.product
    if not product:
        print("PSG: --product required for pre_activate", file=sys.stderr)
        return 2

    product_root = None
    for r in roots(registry):
        if str(r.get("store_id")) == product or str(r.get("id")) == product:
            product_root = r
            break
    if not product_root:
        print(f"PSG: no registry root for product {product}", file=sys.stderr)
        return 2

    lean = run_root(
        product_root,
        lane="lean",
        defaults=defaults,
        store_root=store,
        product_filter=product,
    )
    print(lean["summary"])

    version = None
    for w in lean.get("watches") or []:
        if w.get("manifest_version"):
            version = w["manifest_version"]
    if not version and store:
        from .runners import store_expected_version

        version = store_expected_version(store, product) or "0.0.0"

    # Phase 3: stress evidence ≤7d required for the product key
    from .stress import STRESS_MAX_AGE_S, check_stress_fresh

    stress_keys = []
    if product_root.get("store_id"):
        stress_keys.append(str(product_root["store_id"]))
    stress_keys.append(str(product_root.get("id")))
    stress_check = None
    for key in stress_keys:
        stress_check = check_stress_fresh(
            _agent_skills_root(), key, max_age_s=STRESS_MAX_AGE_S
        )
        if stress_check.get("ok"):
            break
    if stress_check is None or not stress_check.get("ok"):
        reason = (stress_check or {}).get("reason") or "stress evidence missing"
        print(f"PSG pre_activate blocked: {reason}", file=sys.stderr)
        if store:
            write_pre_activate(
                store,
                product,
                str(version),
                {
                    "product": product,
                    "version": version,
                    "ts": utc_now(),
                    "worst": "fail",
                    "lean_run_id": lean.get("run_id"),
                    "tree_hash": lean.get("tree_hash"),
                    "stress": stress_check,
                    "r2": {"ok": False, "configured": False, "evidence": "skipped"},
                    "watches": lean.get("watches"),
                },
            )
        if args.json:
            print(json.dumps({"lean": lean, "stress": stress_check}, indent=2))
        return 1
    print(
        f"PSG stress evidence ok: {stress_check.get('path')} "
        f"(age_s={stress_check.get('age_s'):.0f})"
    )

    # Run store pre_activate watches if present
    store_cfg = find_root(registry, "store")
    r2_ok = True
    r2_evidence = "skipped (no pre_activate http watch or no store root)"
    if store_cfg and store:
        for watch in store_cfg.get("watches") or []:
            if str(watch.get("lane")) != "pre_activate":
                continue
            # Expand URL placeholders lightly — without live R2 host, mark blocked not ok
            url = str(watch.get("url") or "")
            if "<r2" in url or "{artifact" in url:
                r2_ok = False
                r2_evidence = "R2 URL not configured in registry"
                result = {
                    "id": watch.get("id"),
                    "verdict": "blocked",
                    "evidence": r2_evidence,
                    "stop_kind": "http",
                }
            else:
                result = run_watch(
                    watch,
                    root=store,
                    root_cfg=store_cfg,
                    defaults=defaults,
                    store_root=store,
                )
                r2_ok = is_green(result.get("verdict"))
                r2_evidence = str(result.get("evidence"))
            lean.setdefault("watches", []).append(result)

    # Phase 1: lean green is required; unconfigured R2 does not block evidence write,
    # but a configured R2 that fails does block.
    r2_configured = "not configured" not in r2_evidence.lower()
    lean_worst = normalize_verdict(lean.get("worst"))
    overall = lean_worst
    if r2_configured and not r2_ok:
        overall = worst_verdict([lean_worst, "fail"])

    if store:
        ev = write_pre_activate(
            store,
            product,
            str(version),
            {
                "product": product,
                "version": version,
                "ts": utc_now(),
                "worst": overall if is_green(lean_worst) else lean_worst,
                "lean_run_id": lean.get("run_id"),
                "tree_hash": lean.get("tree_hash"),
                "stress": stress_check,
                "r2": {
                    "ok": r2_ok,
                    "configured": r2_configured,
                    "evidence": r2_evidence,
                },
                "watches": lean.get("watches"),
            },
        )
        print(f"PSG pre_activate evidence: {ev}")

    if args.json:
        print(json.dumps(lean, indent=2))
    return 0 if is_green(lean_worst) and (not r2_configured or r2_ok) else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ship_gate", description="PowerCore Ship Gate (PSG)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--root", default=None, help="Registry root id")
    p.add_argument(
        "--lane",
        default="lean",
        choices=["lean", "live", "stress", "pre_activate"],
    )
    p.add_argument("--product", default=None)
    p.add_argument(
        "--deployed",
        action="store_true",
        help="This pass included a deploy — allow live watches",
    )
    p.add_argument("--auto", action="store_true", help="Run in-range lean for roots")
    p.add_argument(
        "--check-evidence",
        action="store_true",
        help="Validate last.json vs current tree_hash (no re-run)",
    )

    args = p.parse_args(argv)

    if args.check_evidence:
        if not args.root:
            print("PSG: --root required with --check-evidence", file=sys.stderr)
            return 2
        return cmd_check_evidence(args)

    if args.lane == "pre_activate" or (args.product and args.lane == "pre_activate"):
        return cmd_pre_activate(args)

    if args.product and args.lane == "lean" and not args.auto and not args.root:
        # treat as product lean via store_id match
        args.auto = True

    return cmd_auto(args)


if __name__ == "__main__":
    raise SystemExit(main())
