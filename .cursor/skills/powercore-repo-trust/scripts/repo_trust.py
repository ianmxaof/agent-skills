#!/usr/bin/env python3
"""Repo trust triage: semantic-deception scan + thin supply-chain heuristics.

Does not execute target code. Not a malware verdict.
v1.1 — smell ≠ go-ahead; claim ledger + operator_action + mandatory Next.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SEM_SCRIPTS = SCRIPTS.parent.parent / "semantic-deception-detector" / "scripts"
sys.path.insert(0, str(SEM_SCRIPTS))

from fetch_target import resolve_scan_root  # noqa: E402
from scan import (  # noqa: E402
    VERSION as SEM_VERSION,
    compose_next_step,
    compose_operator_action,
    scan_root,
)

TRUST_VERSION = "1.2.0"
INSTALL_HOOK_KEYS = (
    "preinstall",
    "install",
    "postinstall",
    "preuninstall",
    "postuninstall",
    "prepare",
    "prepublishOnly",
)
OPAQUE_B64_RE = re.compile(r"(?:[A-Za-z0-9+/]{80,}={0,2})")
WORKFLOW_WRITE_RE = re.compile(
    r"permissions\s*:\s*[\s\S]{0,400}?\bcontents\s*:\s*write\b",
    re.IGNORECASE,
)
# Opt-in --deps: known npm/PyPI typosquat / lookalike names (defensive denylist only).
_TYPOSQUAT_NAMES = {
    "requets",
    "requestes",
    "urlib3",
    "urllib3-https",
    "beautifu1soup4",
    "beautifulsoup",
    "python-dateuitl",
    "dateutil-python",
    "djanga",
    "dajngo",
    "colourama",
    "jinj2",
    "npmpackage",
    "crossenv",
    "crypt",
    "openssl.js",
    "node-openssl",
}
_REQ_LINE_RE = re.compile(
    r"^\s*([A-Za-z0-9_.-]+)\s*(?:[=<>!~]|\[|$)",
    re.MULTILINE,
)


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _second_pass(root: Path, *, max_files: int = 400) -> list[dict]:
    findings: list[dict] = []
    n = 0
    for path in root.rglob("*"):
        if n >= max_files:
            break
        if not path.is_file():
            continue
        name = path.name.lower()
        rel = _rel(root, path)
        if any(part.startswith(".") and part not in (".github",) for part in path.parts):
            # still allow .github
            if ".github" not in path.parts:
                continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if len(raw) > 512_000:
            continue
        n += 1
        text = ""
        try:
            text = raw.decode("utf-8", errors="replace")
        except Exception:
            continue

        if name == "package.json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                data = None
            scripts = (data or {}).get("scripts") if isinstance(data, dict) else None
            if isinstance(scripts, dict):
                for key in INSTALL_HOOK_KEYS:
                    if key in scripts and str(scripts[key]).strip():
                        findings.append(
                            {
                                "category": "install_hook",
                                "confidence": "high",
                                "path": rel,
                                "line": 0,
                                "evidence": f"package.json scripts.{key}={scripts[key]!r}"[:240],
                                "detail": "npm lifecycle hook can run arbitrary code on install",
                            }
                        )

        if name in ("setup.py", "setup.cfg", "pyproject.toml"):
            lowered = text.lower()
            if any(tok in lowered for tok in ("os.system", "subprocess", "urllib.request", "requests.get", "eval(")):
                # only flag if it looks like install-time side effect in setup.py / build backend
                if name == "setup.py" or "[build-system]" in lowered or "tool.setuptools" in lowered:
                    findings.append(
                        {
                            "category": "install_hook",
                            "confidence": "heuristic",
                            "path": rel,
                            "line": 0,
                            "evidence": "setup/build file references network or subprocess/eval",
                            "detail": "review install-time side effects before pip install",
                        }
                    )

        if ".github" in path.parts and path.suffix in (".yml", ".yaml"):
            if WORKFLOW_WRITE_RE.search(text):
                findings.append(
                    {
                        "category": "workflow_write",
                        "confidence": "heuristic",
                        "path": rel,
                        "line": 0,
                        "evidence": "workflow grants contents: write",
                        "detail": "review whether write is required; supply-chain risk if compromised",
                    }
                )

        if path.suffix in (".py", ".js", ".ts", ".mjs", ".cjs", ".sh", ".ps1"):
            for m in OPAQUE_B64_RE.finditer(text):
                blob = m.group(0)
                try:
                    decoded = base64.b64decode(blob, validate=False)
                except Exception:
                    continue
                if len(decoded) < 40:
                    continue
                # skip obvious PEM / certificates
                if b"BEGIN " in decoded[:80]:
                    continue
                findings.append(
                    {
                        "category": "opaque_base64",
                        "confidence": "heuristic",
                        "path": rel,
                        "line": text[: m.start()].count("\n") + 1,
                        "evidence": f"opaque base64 blob (~{len(blob)} chars)",
                        "detail": "may be benign asset; spot-check if unexpected in source",
                    }
                )
                break  # one per file is enough

    return findings


def _iter_declared_deps(root: Path) -> list[tuple[str, str]]:
    """Return (name, path) dependency declarations from common manifests."""
    out: list[tuple[str, str]] = []
    candidates = [
        root / "package.json",
        root / "requirements.txt",
        root / "requirements-dev.txt",
        root / "pyproject.toml",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = _rel(root, path)
        name = path.name.lower()
        if name == "package.json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict):
                continue
            for key in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
                block = data.get(key)
                if isinstance(block, dict):
                    for dep in block:
                        out.append((str(dep).lower(), rel))
        elif name.startswith("requirements"):
            for m in _REQ_LINE_RE.finditer(text):
                dep = m.group(1).lower()
                if dep and not dep.startswith("#"):
                    out.append((dep, rel))
        elif name == "pyproject.toml":
            # Light parse — no tomllib required for name tokens after =
            for m in re.finditer(
                r'(?m)^\s*["\']?([A-Za-z0-9_.-]+)["\']?\s*=\s*["\']',
                text,
            ):
                dep = m.group(1).lower()
                if dep in {"name", "version", "description", "readme", "requires-python", "license"}:
                    continue
                out.append((dep, rel))
    return out


def _deps_pass(root: Path) -> list[dict]:
    """Opt-in typosquat / lookalike dependency names."""
    findings: list[dict] = []
    seen: set[str] = set()
    for dep, rel in _iter_declared_deps(root):
        key = f"{dep}@{rel}"
        if key in seen:
            continue
        seen.add(key)
        if dep in _TYPOSQUAT_NAMES or dep.replace("_", "-") in _TYPOSQUAT_NAMES:
            findings.append(
                {
                    "category": "deps_typosquat",
                    "confidence": "high",
                    "path": rel,
                    "line": 0,
                    "evidence": f"dependency name {dep!r} matches known lookalike denylist",
                    "detail": "review before install; may be typosquat",
                }
            )
    return findings


def _meta_pass(root: Path) -> list[dict]:
    """Opt-in local meta heuristics (no network): license gap, docs-vs-code skew."""
    findings: list[dict] = []
    license_hits = list(root.glob("LICENSE*")) + list(root.glob("LICENCE*")) + list(root.glob("COPYING*"))
    if not license_hits:
        findings.append(
            {
                "category": "meta_no_license",
                "confidence": "heuristic",
                "path": ".",
                "line": 0,
                "evidence": "no LICENSE/LICENCE/COPYING file at repo root",
                "detail": "spot-check licensing before vendor; not proof of malice",
            }
        )

    readme = None
    for name in ("README.md", "README.rst", "README"):
        if (root / name).is_file():
            readme = root / name
            break
    code_files = 0
    for pat in ("*.py", "*.js", "*.ts", "*.go", "*.rs"):
        code_files += sum(1 for _ in root.rglob(pat) if _.is_file())
        if code_files > 50:
            break
    if readme is not None:
        try:
            rsize = readme.stat().st_size
        except OSError:
            rsize = 0
        if rsize >= 40_000 and code_files <= 5:
            findings.append(
                {
                    "category": "meta_docs_heavy",
                    "confidence": "heuristic",
                    "path": _rel(root, readme),
                    "line": 0,
                    "evidence": f"README ~{rsize} bytes but only ~{code_files} code files sampled",
                    "detail": "docs-heavy trees warrant claim ledger / --ask before harvest",
                }
            )
    return findings


def _legacy_trust_level(score: int) -> str:
    if score >= 40:
        return "HIGH"
    if score >= 15:
        return "REVIEW"
    return "LOW"


def _compose_trust_contract(
    *,
    sem_smell: str,
    sem_action: str,
    claim_ledger: list[dict],
    second: list[dict],
    ask: str | None,
) -> tuple[str, str, str]:
    """Merge semantic contract with second-pass hooks. Never upgrade to IGNORE on hooks."""
    smell = sem_smell
    if any(
        f.get("confidence") == "high" and f.get("category") in {"install_hook", "deps_typosquat"}
        for f in second
    ):
        if smell in ("CLEAN", "LOW"):
            smell = "REVIEW"
    action = compose_operator_action(smell, claim_ledger, ask)
    # Preserve STOP from semantic if stronger
    rank = {"IGNORE": 0, "HARVEST_OK": 1, "SPOT_CHECK": 2, "PIPELINE_FIT": 3, "STOP": 4}
    if rank.get(sem_action, 0) > rank.get(action, 0):
        action = sem_action
    if any(f.get("confidence") == "high" for f in second) and action in ("IGNORE", "HARVEST_OK"):
        action = "SPOT_CHECK"
    return smell, action, compose_next_step(action)


def build_report(
    root: Path,
    *,
    max_files: int,
    max_bytes: int,
    ask: str | None = None,
    claims_from_readme: bool = True,
    deps: bool = False,
    meta: bool = False,
) -> dict:
    sem = scan_root(
        root,
        max_files=max_files,
        max_bytes=max_bytes,
        ask=ask,
        claims_from_readme=claims_from_readme,
    )
    second = _second_pass(root, max_files=max_files)
    if deps:
        second.extend(_deps_pass(root))
    if meta:
        second.extend(_meta_pass(root))
    sem_payload = asdict(sem)
    # Drop the raw capability inventory — Hub/CLI summary only need findings.
    sem_payload.pop("capabilities", None)
    high_second = sum(8 for f in second if f.get("confidence") == "high")
    heur_second = sum(2 for f in second if f.get("confidence") != "high")
    trust_score = int(sem.structural_score) + high_second + heur_second
    trust_level = _legacy_trust_level(trust_score)
    if sem.structural_level in ("REVIEW", "HIGH") and trust_level == "LOW":
        trust_level = "REVIEW"
    if any(f.get("confidence") == "high" for f in second) and trust_level == "LOW":
        trust_level = "REVIEW"

    smell, action, next_step = _compose_trust_contract(
        sem_smell=sem.smell_level,
        sem_action=sem.operator_action,
        claim_ledger=sem.claim_ledger,
        second=second,
        ask=ask,
    )
    # Align legacy trust_level floor with smell
    if smell in ("HIGH", "BLOCK") and trust_level != "HIGH":
        trust_level = "HIGH"
    elif smell == "REVIEW" and trust_level == "LOW":
        trust_level = "REVIEW"

    return {
        "trust_version": TRUST_VERSION,
        "semantic_version": SEM_VERSION,
        "trust_score": trust_score,
        "trust_level": trust_level,
        "smell_level": smell,
        "operator_action": action,
        "ask": (ask.strip() if ask and ask.strip() else None),
        "claim_ledger": sem.claim_ledger,
        "next_step": next_step,
        "semantic": sem_payload,
        "second_pass": second,
        "summary": {
            "semantic_structural": sem.structural_level,
            "smell_level": smell,
            "operator_action": action,
            "second_pass_count": len(second),
            "second_pass_high": sum(1 for f in second if f.get("confidence") == "high"),
            "claim_ledger_hits": sum(1 for c in sem.claim_ledger if c.get("status") == "hit"),
            "claim_ledger_misses": sum(1 for c in sem.claim_ledger if c.get("status") == "miss"),
        },
    }


def exit_code_for_trust(report: dict) -> int:
    if report.get("operator_action") in {"STOP", "PIPELINE_FIT", "SPOT_CHECK"}:
        return 1
    if report.get("trust_level") != "LOW":
        return 1
    return 0


def _print_hub_card(report: dict, *, source_kind: str, source_url: str) -> None:
    """Plain Hub/Vincent card — action + claim misses first; no 'Looks fine' on LOW."""
    print(f"powercore-repo-trust {TRUST_VERSION}")
    print()
    print("# Repo trust check")
    print()
    print("## Verdict")
    print()
    print(
        f"smell={report['smell_level']}  action={report['operator_action']}  "
        f"(legacy trust_level={report['trust_level']} score={report['trust_score']})"
    )
    print()
    print(report["next_step"])
    print()
    if report.get("ask"):
        print(f"ask: {report['ask']}")
        print()
    print("## Claim ledger")
    print()
    ledger = report.get("claim_ledger") or []
    if not ledger:
        print("(empty — pass --ask for question-aware verify)")
    else:
        for c in ledger:
            loc = (
                f"{c['evidence_path']}:{c['evidence_line']}"
                if c.get("evidence_path")
                else "(no hit)"
            )
            print(f"- [{c['status']}] {c['claim'][:120]}")
            print(f"  {loc}")
    print()
    print("## Semantic")
    print()
    sem = report.get("semantic") or {}
    print(
        f"structural={sem.get('structural_level')} / {sem.get('structural_score')}  "
        f"total={sem.get('risk_level')} / {sem.get('risk_score')}"
    )
    findings = (sem.get("findings") or [])[:12]
    if not findings:
        print("(no structural findings)")
    for f in findings:
        loc = f"{f['path']}:{f['line']}" if f.get("line") else f["path"]
        print(f"- [{f['category']} conf={f.get('confidence')}] {loc}: {f.get('evidence', '')[:120]}")
    print()
    print("## Second pass")
    print()
    second = report.get("second_pass") or []
    if not second:
        print("(none)")
    for f in second[:15]:
        print(f"- [{f['category']} conf={f['confidence']}] {f['path']}: {f['evidence']}")
    print()
    print("## Not claimed")
    print()
    print("Not malware confirmation. Not intent. Not a legal opinion. Smell ≠ safe to vendor.")
    print()
    print("## Next")
    print()
    print(report["next_step"])
    print()
    print(f"source: {source_kind} {source_url}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Repo trust triage (semantic-scan + install/workflow heuristics)")
    p.add_argument("target", nargs="?", default=".", help="Local path or URL")
    p.add_argument("--json", action="store_true")
    p.add_argument("--max-files", type=int, default=400)
    p.add_argument("--max-bytes", type=int, default=512_000)
    p.add_argument(
        "--ask",
        default=None,
        help="Operator question to verify against the tree (claim ledger)",
    )
    p.add_argument(
        "--no-readme-claims",
        action="store_true",
        help="Skip auto README feature-bullet ledger when --ask is absent",
    )
    p.add_argument(
        "--deps",
        action="store_true",
        help="Opt-in: flag known typosquat/lookalike dependency names",
    )
    p.add_argument(
        "--meta",
        action="store_true",
        help="Opt-in: local meta heuristics (no LICENSE, docs-heavy skew)",
    )
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args(argv)

    if args.self_test:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "# Demo\n\n## Features\n\n- Ships plan_edit_before_execute gate\n",
                encoding="utf-8",
            )
            (root / "gate.py").write_text(
                "def plan_edit_before_execute():\n    return True\n",
                encoding="utf-8",
            )
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "x",
                        "scripts": {"postinstall": "node evil.js"},
                        "dependencies": {"requets": "1.0.0"},
                    }
                ),
                encoding="utf-8",
            )
            hit = build_report(
                root,
                max_files=50,
                max_bytes=100_000,
                ask="does plan_edit_before_execute exist?",
                claims_from_readme=False,
            )
            assert hit["claim_ledger"] and hit["claim_ledger"][0]["status"] == "hit", hit["claim_ledger"]
            # install_hook high → at least SPOT_CHECK / REVIEW smell
            assert hit["operator_action"] in {"SPOT_CHECK", "PIPELINE_FIT", "STOP"}, hit
            assert hit["smell_level"] in {"REVIEW", "HIGH", "BLOCK", "LOW"}, hit["smell_level"]

            miss = build_report(
                root,
                max_files=50,
                max_bytes=100_000,
                ask="does totally_missing_feature_xyz exist?",
                claims_from_readme=False,
            )
            assert miss["claim_ledger"][0]["status"] == "miss", miss["claim_ledger"]
            # Install-hook elevates smell→REVIEW so action may be PIPELINE_FIT (stronger than SPOT_CHECK).
            assert miss["operator_action"] in {"SPOT_CHECK", "PIPELINE_FIT", "STOP"}, miss["operator_action"]
            assert "Looks fine" not in miss["next_step"]

            clean = root / "clean_tree"
            clean.mkdir()
            (clean / "only.py").write_text("def noop():\n    return 1\n", encoding="utf-8")
            clean_miss = build_report(
                clean,
                max_files=20,
                max_bytes=50_000,
                ask="does totally_missing_feature_xyz exist?",
                claims_from_readme=False,
            )
            assert clean_miss["operator_action"] == "SPOT_CHECK", clean_miss

            deps_rep = build_report(
                root,
                max_files=50,
                max_bytes=100_000,
                claims_from_readme=False,
                deps=True,
                meta=True,
            )
            cats = {f["category"] for f in deps_rep["second_pass"]}
            assert "deps_typosquat" in cats, cats
            assert "meta_no_license" in cats, cats
            assert deps_rep["operator_action"] in {"SPOT_CHECK", "PIPELINE_FIT", "STOP"}, deps_rep
        print("self-test: PASS")
        return 0

    with resolve_scan_root(args.target) as mat:
        report = build_report(
            mat.root,
            max_files=args.max_files,
            max_bytes=args.max_bytes,
            ask=args.ask,
            claims_from_readme=not args.no_readme_claims,
            deps=bool(args.deps),
            meta=bool(args.meta),
        )
        report["fetch"] = {
            "source_url": mat.source_url,
            "source_kind": mat.source_kind,
            "scan_root": str(mat.root),
        }
        if args.json:
            # Compact — Hub/Vault stdout caps break on indented dumps of large trees.
            print(json.dumps(report, separators=(",", ":")))
        else:
            _print_hub_card(report, source_kind=mat.source_kind, source_url=mat.source_url)
        return exit_code_for_trust(report)


if __name__ == "__main__":
    raise SystemExit(main())
