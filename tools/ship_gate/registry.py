"""Load ship_gate registry.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


def registry_path() -> Path:
    return Path(__file__).resolve().parent / "registry.yaml"


def load_registry(path: Path | None = None) -> dict[str, Any]:
    p = path or registry_path()
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("registry.yaml must be a mapping")
    return data


def roots(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return list(registry.get("roots") or [])


def find_root(registry: dict[str, Any], root_id: str) -> dict[str, Any] | None:
    for r in roots(registry):
        if str(r.get("id")) == root_id:
            return r
    return None
