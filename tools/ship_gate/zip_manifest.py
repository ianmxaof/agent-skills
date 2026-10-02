"""zip_manifest stop — pack must contain every file the extension manifest references."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any


def _collect_manifest_paths(manifest: dict[str, Any]) -> set[str]:
    needed: set[str] = set()
    icons = manifest.get("icons") or {}
    if isinstance(icons, dict):
        needed.update(str(v) for v in icons.values())
    action = manifest.get("action") or {}
    if isinstance(action, dict):
        di = action.get("default_icon")
        if isinstance(di, dict):
            needed.update(str(v) for v in di.values())
        elif isinstance(di, str):
            needed.add(di)
    bg = manifest.get("background") or {}
    if isinstance(bg, dict) and bg.get("service_worker"):
        needed.add(str(bg["service_worker"]))
    for cs in manifest.get("content_scripts") or []:
        if isinstance(cs, dict):
            for js in cs.get("js") or []:
                needed.add(str(js))
            for css in cs.get("css") or []:
                needed.add(str(css))
    opts = manifest.get("options_ui") or {}
    if isinstance(opts, dict) and opts.get("page"):
        needed.add(str(opts["page"]))
    return {p.replace("\\", "/") for p in needed if p}


def check_zip_manifest(
    zip_path: Path,
    *,
    expected_version: str | None = None,
) -> dict[str, Any]:
    """Return watch-style payload with verdict ok|fail|blocked."""
    if not zip_path.is_file():
        return {
            "verdict": "fail",
            "evidence": f"zip missing: {zip_path}",
            "stop_kind": "zip_manifest",
        }
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = {n.replace("\\", "/") for n in zf.namelist()}
            # Compress-Archive may nest under a folder — also try basename-relative
            manifest_name = None
            for n in names:
                if n.endswith("manifest.json") and not n.endswith("/"):
                    manifest_name = n
                    break
            if not manifest_name:
                return {
                    "verdict": "fail",
                    "evidence": "manifest.json not found in zip",
                    "stop_kind": "zip_manifest",
                }
            raw = zf.read(manifest_name)
            manifest = json.loads(raw.decode("utf-8"))
            base = ""
            if "/" in manifest_name:
                base = manifest_name.rsplit("/", 1)[0] + "/"
            needed = _collect_manifest_paths(manifest)
            missing = []
            for rel in sorted(needed):
                candidates = {rel, base + rel, rel.lstrip("./")}
                if not candidates & names:
                    missing.append(rel)
            ver = str(manifest.get("version") or "")
            if expected_version is not None and ver != str(expected_version):
                return {
                    "verdict": "fail",
                    "evidence": (
                        f"manifest.version={ver!r} != expected {expected_version!r}"
                    ),
                    "stop_kind": "zip_manifest",
                    "manifest_version": ver,
                    "missing": missing,
                }
            if missing:
                return {
                    "verdict": "fail",
                    "evidence": f"missing from zip: {', '.join(missing)}",
                    "stop_kind": "zip_manifest",
                    "manifest_version": ver,
                    "missing": missing,
                }
            return {
                "verdict": "ok",
                "evidence": f"zip_manifest ok version={ver} entries={len(needed)}",
                "stop_kind": "zip_manifest",
                "manifest_version": ver,
            }
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError, UnicodeDecodeError) as e:
        return {
            "verdict": "blocked",
            "evidence": str(e)[:300],
            "stop_kind": "zip_manifest",
        }


def resolve_artifact_zip(root: Path, glob_pat: str, version: str | None = None) -> Path | None:
    pat = glob_pat.replace("{version}", version or "*")
    matches = sorted(root.glob(pat))
    if not matches:
        # also try dist/
        matches = sorted(root.glob(pat.replace("dist/", "")))
    return matches[-1] if matches else None
