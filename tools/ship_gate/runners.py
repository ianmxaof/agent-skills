"""Execute individual PSG watches."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

from .verdicts import normalize_verdict
from .zip_manifest import check_zip_manifest, resolve_artifact_zip
from .live import http_check, resolve_idle


def _run_cmd(
    cmd: str,
    *,
    cwd: Path,
    budget_s: float,
    shell: bool = True,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            shell=shell,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=budget_s,
        )
        dur = time.perf_counter() - t0
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        snippet = out[-500:] if out else ""
        if proc.returncode == 0:
            return {
                "verdict": "ok",
                "evidence": snippet or f"exit 0 ({dur:.1f}s)",
                "duration_s": round(dur, 3),
                "exit_code": 0,
            }
        return {
            "verdict": "fail",
            "evidence": snippet or f"exit {proc.returncode}",
            "duration_s": round(dur, 3),
            "exit_code": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "verdict": "blocked",
            "evidence": f"timeout after {budget_s}s",
            "duration_s": budget_s,
        }
    except OSError as e:
        return {
            "verdict": "blocked",
            "evidence": str(e)[:300],
            "duration_s": round(time.perf_counter() - t0, 3),
        }


def run_probe_json(cmd: str, *, cwd: Path, budget_s: float) -> dict[str, Any]:
    """Run silent_fail_probe-style command; parse --json verdict (ignore exit code)."""
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=budget_s,
        )
        dur = time.perf_counter() - t0
        raw = (proc.stdout or "").strip()
        if not raw:
            return {
                "verdict": "blocked",
                "evidence": "empty probe stdout",
                "duration_s": round(dur, 3),
            }
        # Prefer last JSON object line
        payload = None
        for line in reversed(raw.splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    payload = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
        if payload is None:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                # first-token fallback
                token = raw.split()[0].strip().lower()
                return {
                    "verdict": normalize_verdict(token),
                    "evidence": raw[:300],
                    "duration_s": round(dur, 3),
                }
        verdict = normalize_verdict(payload.get("verdict"))
        evidence = str(
            payload.get("stop_evidence")
            or payload.get("error")
            or payload.get("id")
            or raw[:200]
        )
        return {
            "verdict": verdict,
            "evidence": evidence[:400],
            "duration_s": round(dur, 3),
            "payload": payload,
        }
    except subprocess.TimeoutExpired:
        return {"verdict": "blocked", "evidence": f"timeout after {budget_s}s"}
    except OSError as e:
        return {"verdict": "blocked", "evidence": str(e)[:300]}


def store_expected_version(store_root: Path, store_id: str) -> str | None:
    products_path = store_root / "data" / "products.json"
    if not products_path.is_file():
        return None
    try:
        products = json.loads(products_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    for p in products:
        if str(p.get("id")) == store_id or str(p.get("slug")) == store_id:
            art = p.get("artifact") or {}
            return str(art.get("version") or "") or None
    return None


def run_watch(
    watch: dict[str, Any],
    *,
    root: Path,
    root_cfg: dict[str, Any],
    defaults: dict[str, Any],
    store_root: Path | None = None,
) -> dict[str, Any]:
    wid = str(watch.get("id") or "watch")
    stop_kind = str(watch.get("stop_kind") or "cli_exit")
    budget = float(watch.get("budget_s") or defaults.get("budget_s") or 90)
    lane = str(watch.get("lane") or "lean")
    runs_where = str(watch.get("runs_where") or "local")
    work_cwd = root
    if watch.get("cwd"):
        work_cwd = (root / str(watch["cwd"])).resolve()

    base: dict[str, Any] = {
        "id": wid,
        "stop_kind": stop_kind,
        "lane": lane,
        "runs_where": runs_where,
    }

    idle = resolve_idle(
        watch.get("idle_flag"),
        search_roots=[root, root.parent, Path(r"C:\Powercore-repo-main\telegram_bot2")],
    )
    if idle is not None and idle.get("verdict") == "idle":
        base.update(idle)
        return base
    if idle is not None and idle.get("verdict") == "blocked" and watch.get("idle_flag"):
        # Flag declared but unreadable — only block LIVE watches; lean continues
        if lane == "live":
            base.update(idle)
            return base

    if runs_where == "island" and lane == "live":
        pass

    if stop_kind == "zip_manifest":
        store_id = root_cfg.get("store_id")
        expected = None
        if store_id and store_root:
            expected = store_expected_version(store_root, str(store_id))
        glob_pat = str(
            watch.get("path")
            or root_cfg.get("artifact_zip_glob")
            or "dist/*-{version}.zip"
        )
        # Prefer version from local extension manifest if present
        local_ver = None
        man = root / "extension" / "manifest.json"
        if man.is_file():
            try:
                local_ver = str(json.loads(man.read_text(encoding="utf-8")).get("version") or "")
            except (OSError, json.JSONDecodeError):
                local_ver = None
        zip_path = resolve_artifact_zip(root, glob_pat, local_ver or expected)
        if zip_path is None:
            result = {
                "verdict": "fail",
                "evidence": f"no zip matched {glob_pat}",
                "stop_kind": "zip_manifest",
            }
        else:
            result = check_zip_manifest(zip_path, expected_version=expected or local_ver)
        base.update(result)
        return base

    if stop_kind == "probe":
        cmd = str(watch.get("cmd") or "")
        if "--json" not in cmd:
            # Parent argparse flags must precede the subcommand (silent_fail_probe).
            if ".py " in cmd:
                cmd = cmd.replace(".py ", ".py --json ", 1)
            else:
                cmd = cmd + " --json"
        result = run_probe_json(cmd, cwd=work_cwd, budget_s=budget)
        thr = watch.get("threshold") if isinstance(watch.get("threshold"), dict) else None
        if thr and lane == "stress":
            from .stress import apply_probe_threshold

            gated = apply_probe_threshold(result.get("payload"), thr, result.get("verdict") or "blocked")
            result = {
                **result,
                "verdict": gated["verdict"],
                "evidence": gated.get("evidence") or result.get("evidence"),
                "metrics": gated.get("metrics"),
            }
        base.update(result)
        return base

    if stop_kind in ("pytest", "node_test", "cli_exit"):
        cmd = str(watch.get("cmd") or "")
        if not cmd:
            base.update({"verdict": "blocked", "evidence": "missing cmd"})
            return base
        # Expand env-ish placeholders
        cmd = cmd.replace("{root}", str(root))
        result = _run_cmd(cmd, cwd=work_cwd, budget_s=budget)
        thr = watch.get("threshold") if isinstance(watch.get("threshold"), dict) else None
        if thr and lane == "stress" and result.get("exit_code") == 0:
            # Prefer JSON metrics line from stdout for latency gates
            from .stress import apply_latency_threshold

            metrics_payload = None
            evidence = str(result.get("evidence") or "")
            for line in reversed(evidence.splitlines()):
                line = line.strip()
                if line.startswith("{") and "p95_ms" in line:
                    try:
                        metrics_payload = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue
            if metrics_payload and "p95_ms" in metrics_payload:
                # Reconstruct samples approx from p95 only — use reported p95/max
                p95 = float(metrics_payload["p95_ms"])
                mx = float(metrics_payload.get("max_ms") or p95)
                n = int(metrics_payload.get("n") or thr.get("min_iterations") or 1)
                fake_samples = [p95] * max(1, n)
                fake_samples[-1] = mx
                gated = apply_latency_threshold(fake_samples, thr)
                result = {
                    **result,
                    "verdict": gated["verdict"],
                    "evidence": gated.get("evidence") or result.get("evidence"),
                    "metrics": gated.get("metrics") or metrics_payload,
                }
            elif thr.get("p95_ms_max") is not None:
                result = {
                    **result,
                    "verdict": "blocked",
                    "evidence": "stress latency JSON metrics missing from command output",
                }
        base.update(result)
        return base

    if stop_kind == "http":
        url = str(watch.get("url") or "")
        if not url:
            base.update({"verdict": "blocked", "evidence": "missing url"})
            return base
        parse = watch.get("parse") if isinstance(watch.get("parse"), dict) else {}
        method = str(watch.get("method") or "GET")
        result = http_check(url, method=method, parse=parse, timeout_s=min(budget, 30))
        base.update(result)
        return base

    if stop_kind == "file":
        path = root / str(watch.get("path") or "")
        if path.is_file():
            base.update({"verdict": "ok", "evidence": f"file exists {path.name}"})
        else:
            base.update({"verdict": "fail", "evidence": f"file missing {path}"})
        return base

    base.update({"verdict": "blocked", "evidence": f"unknown stop_kind={stop_kind}"})
    return base


def path_matches(changed_rel: str, patterns: list[str] | None) -> bool:
    if not patterns:
        return True
    from fnmatch import fnmatch

    rel = changed_rel.replace("\\", "/")
    for pat in patterns:
        p = pat.replace("\\", "/")
        if fnmatch(rel, p) or fnmatch(rel, p.lstrip("./")):
            return True
        # prefix directory match for foo/**
        if p.endswith("/**") and (rel.startswith(p[:-3]) or rel == p[:-3]):
            return True
    return False


def detect_changed_rels(root: Path, paths: list[str], ignore: list[str], previous_hash: str | None) -> list[str]:
    """If no previous hash / evidence, treat all path patterns as in range (full lean for root)."""
    # For --auto without prior evidence: if tree exists, root is "in range" when caller asks.
    # Caller decides which roots to scan; this returns sentinel ["*"] meaning all watches.
    _ = (previous_hash, ignore)
    return ["*"]


def watch_in_range(watch: dict[str, Any], changed_rels: list[str]) -> bool:
    when = watch.get("when_paths")
    if not when:
        return True
    if "*" in changed_rels:
        return True
    return any(path_matches(rel, list(when)) for rel in changed_rels)
