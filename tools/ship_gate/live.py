"""LIVE-lane helpers: island HTTP assertions + idle_flag from env."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .verdicts import normalize_verdict


def _load_dotenv_value(key: str, search_roots: list[Path]) -> str | None:
    env_val = os.environ.get(key)
    if env_val is not None:
        return env_val
    for root in search_roots:
        for candidate in (root / ".env", root / "tbcc" / ".env"):
            if not candidate.is_file():
                continue
            try:
                for line in candidate.read_text(encoding="utf-8", errors="replace").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, _, v = line.partition("=")
                    if k.strip() == key:
                        return v.strip().strip('"').strip("'")
            except OSError:
                continue
    return None


def flag_is_off(raw: str | None) -> bool:
    if raw is None:
        return False
    return raw.strip().lower() in ("0", "false", "off", "no", "")


def resolve_idle(
    idle_flag: str | None,
    *,
    search_roots: list[Path] | None = None,
) -> dict[str, Any] | None:
    """If idle_flag is set and off, return idle verdict payload; else None."""
    if not idle_flag:
        return None
    roots = search_roots or []
    val = _load_dotenv_value(idle_flag, roots)
    if val is None:
        return {
            "verdict": "blocked",
            "evidence": f"idle_flag {idle_flag} not readable",
            "idle_flag": idle_flag,
        }
    if flag_is_off(val):
        return {
            "verdict": "idle",
            "evidence": f"idle({idle_flag}={val})",
            "idle_flag": idle_flag,
            "idle_value": val,
        }
    return None


def json_path_get(data: Any, path: str) -> Any:
    """Minimal JSONPath: $.a.b.c only."""
    if not path or path == "$":
        return data
    cur = data
    for part in path.lstrip("$").lstrip(".").split("."):
        if part == "":
            continue
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def http_check(
    url: str,
    *,
    method: str = "GET",
    parse: dict[str, Any] | None = None,
    timeout_s: float = 15.0,
) -> dict[str, Any]:
    parse = parse or {}
    try:
        req = Request(
            url,
            method=method.upper(),
            headers={"User-Agent": "PowerCore-ShipGate/1"},
        )
        with urlopen(req, timeout=timeout_s) as resp:  # noqa: S310
            status = getattr(resp, "status", 200)
            body = resp.read(8192)
    except HTTPError as e:
        return {
            "verdict": "fail",
            "evidence": f"HTTP {e.code} {url}",
            "stop_kind": "http",
        }
    except (URLError, TimeoutError, OSError) as e:
        return {
            "verdict": "blocked",
            "evidence": f"{type(e).__name__}: {e}"[:300],
            "stop_kind": "http",
        }

    want_status = int(parse.get("status") or 200)
    if status != want_status:
        return {
            "verdict": "fail",
            "evidence": f"HTTP {status} (want {want_status}) {url}",
            "stop_kind": "http",
        }

    json_path = parse.get("json_path")
    expect = parse.get("equals")
    if json_path:
        try:
            data = json.loads(body.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            return {
                "verdict": "blocked",
                "evidence": "non-json body",
                "stop_kind": "http",
            }
        got = json_path_get(data, str(json_path))
        if "verdict" in str(json_path) or (
            isinstance(got, str) and normalize_verdict(got) in (
                "ok", "fail", "stale", "never_seen", "idle", "blocked"
            ) and expect is None and "status" not in str(json_path)
        ):
            # path points at a PSG/silent-fail verdict field
            if got is None:
                return {
                    "verdict": "fail",
                    "evidence": f"{json_path} missing",
                    "stop_kind": "http",
                }
            return {
                "verdict": normalize_verdict(got),
                "evidence": f"{json_path}={got!r}",
                "stop_kind": "http",
            }
        want = expect if expect is not None else "ok"
        if str(got).lower() != str(want).lower():
            return {
                "verdict": "fail",
                "evidence": f"{json_path}={got!r} want {want!r}",
                "stop_kind": "http",
            }
        return {
            "verdict": "ok",
            "evidence": f"HTTP {status} {json_path}={got!r}",
            "stop_kind": "http",
        }

    return {
        "verdict": "ok",
        "evidence": f"HTTP {status} {url}",
        "stop_kind": "http",
    }
