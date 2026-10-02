"""Mine Cursor agent-transcripts for UX preference candidates.

Default is dry-run → writes a candidates markdown next to the living index.
Use --apply only after review (appends PX rows tagged ``seeded``).

  py -3.13 -m tools.ux_prefs seed --all-projects --plain
  py -3.13 -m tools.ux_prefs seed --all-projects --apply --max-apply 15
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

_REPO_AGENT_SKILLS = Path(__file__).resolve().parents[2]
_DEFAULT_INDEX = Path(r"C:\Powercore-repo-main\powercore-ops\design\powercore-ux.preferences.md")
_DEFAULT_CANDIDATES = Path(
    r"C:\Powercore-repo-main\powercore-ops\design\powercore-ux.preferences.seed-candidates.md"
)

# Prefer PowerCore / UI product slugs; --all-projects scans everything with transcripts.
_DEFAULT_SLUG_PREFIXES = (
    "c-Powercore-repo-main-",
    "c-powercore-repo-main-",
)

_UX_TERMS = re.compile(
    r"\b("
    r"scroll|scrolling|scrollbar|mousewheel|mouse\s*wheel|mouse3|wheel|"
    r"sidebar|history\s*rail|chat\s*rail|chevron|"
    r"hover|padding|spacing|gap|margin|density|"
    r"font|typography|inter|segoe|"
    r"focus|keyboard|hotkey|shortcut|"
    r"enter\s*to\s*send|shift\s*\+\s*enter|"
    r"panel|chrome|tray|tooltip|icon|favicon|"
    r"click|double[- ]?click|drag|resize|overflow|"
    r"dark\s*mode|theme|contrast|"
    r"ui|ux|layout|look\s*like|feel|"
    r"still\s+not|doesn'?t\s+scroll|won'?t\s+scroll|always\s+should|should\s+always"
    r")\b",
    re.I,
)

_IMPERATIVE = re.compile(
    r"\b(should|always|never|still|doesn't|does not|won't|want|make|fix|please|"
    r"instead|rather|prefer|must|need)\b",
    re.I,
)

_USER_QUERY = re.compile(r"<user_query>\s*(.*?)\s*</user_query>", re.I | re.S)
_TIMESTAMP = re.compile(r"<timestamp>\s*</timestamp>", re.I)  # strip empty
_ANY_TIMESTAMP = re.compile(r"<timestamp>.*?</timestamp>", re.I | re.S)


@dataclass
class Hit:
    score: int
    quote: str
    project: str
    transcript_id: str
    path: str
    mtime_iso: str
    terms: list[str]
    bucket: str


def cursor_projects_root() -> Path:
    return Path.home() / ".cursor" / "projects"


def discover_jsonl(
    *,
    all_projects: bool,
    project_slugs: list[str] | None,
    limit_files: int | None,
) -> list[tuple[str, Path]]:
    root = cursor_projects_root()
    if not root.is_dir():
        return []

    if project_slugs:
        slugs = project_slugs
    elif all_projects:
        slugs = sorted(
            p.name for p in root.iterdir() if p.is_dir() and (p / "agent-transcripts").is_dir()
        )
    else:
        slugs = sorted(
            p.name
            for p in root.iterdir()
            if p.is_dir()
            and (p / "agent-transcripts").is_dir()
            and p.name.startswith(_DEFAULT_SLUG_PREFIXES)
        )

    rows: list[tuple[str, Path]] = []
    for slug in slugs:
        base = root / slug / "agent-transcripts"
        if not base.is_dir():
            continue
        for fp in base.rglob("*.jsonl"):
            if "subagents" in {part.lower() for part in fp.parts}:
                continue
            rows.append((slug, fp))

    rows.sort(key=lambda r: r[1].stat().st_mtime, reverse=True)
    if limit_files is not None and limit_files > 0:
        rows = rows[:limit_files]
    return rows


_NOISE = re.compile(
    r"(?is)(?:^\s*<mcp_|<available_subagent|<agent_transcripts|"
    r"<conversation_summary>|\[conversation_summary\]|"
    r"You have access to MCP|PASTE INTO (?:CURSOR|CLAUDE)|"
    r"^\s*##\s*Goal\b|^\s*\*\*Verdict:|"
    r"COMPOSITION LOCK|TL;DR|handoff|silent-fail contract)"
)

# Strong UX-feel corrections (boost + require for long pastes).
_STRONG_UX = re.compile(
    r"(?i)\b("
    r"scroll|scrolling|scrollbar|mouse\s*wheel|mouse3|wheel|"
    r"white\s+border|no\s+border|padding|spacing|hover|"
    r"sidebar|history\s*rail|font|typography|"
    r"still\s+(?:seeing|not)|doesn'?t\s+scroll|won'?t\s+scroll|"
    r"should\s+(?:always|be|look)|always\s+should|"
    r"title\s+header|tooltip|toast\s+notification"
    r")\b"
)


def _extract_user_text(row: dict[str, Any]) -> str:
    if str(row.get("role") or "").lower() != "user":
        return ""
    msg = row.get("message") or {}
    content = msg.get("content")
    chunks: list[str] = []
    if isinstance(content, str):
        chunks.append(content)
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                chunks.append(str(block.get("text") or ""))
            elif isinstance(block, str):
                chunks.append(block)
    raw = "\n".join(chunks).strip()
    if not raw:
        return ""
    # Prefer the literal operator ask; ignore injected system wrappers.
    m = _USER_QUERY.search(raw)
    if m:
        raw = m.group(1).strip()
    else:
        # No <user_query> fence → usually tool/system injection; skip.
        return ""
    raw = _ANY_TIMESTAMP.sub("", raw).strip()
    if _NOISE.search(raw):
        return ""
    # Long pasted specs / multi-topic dumps need a strong UX signal in the head.
    if len(raw) > 400 and not _STRONG_UX.search(raw[:350]):
        return ""
    # Skill-meta / protocol asks are not UX surface prefs.
    if re.search(r"\b(skill|tool|/ux-prefs|/crew|/cc-report)\b", raw, re.I) and not _STRONG_UX.search(
        raw
    ):
        return ""
    return raw


def _bucket_for(terms: Iterable[str]) -> str:
    t = {x.lower() for x in terms}
    if t & {"scroll", "scrolling", "scrollbar", "mousewheel", "wheel", "mouse3"}:
        return "scroll"
    if t & {"sidebar", "history rail", "chat rail", "chevron", "rail"}:
        return "sidebar-rail"
    if t & {"font", "typography", "inter", "segoe"}:
        return "typography"
    if t & {"focus", "keyboard", "hotkey", "shortcut", "enter to send"}:
        return "keyboard-focus"
    if t & {"panel", "chrome", "tray", "theme", "dark mode"}:
        return "chrome"
    if t & {"hover", "padding", "spacing", "gap", "density", "margin"}:
        return "density"
    return "ui-general"


def _score(text: str, terms: list[str]) -> int:
    score = 10 + min(20, 5 * len(terms))
    if _IMPERATIVE.search(text):
        score += 15
    if re.search(r"\bstill\b|\bdoesn't\b|\bwont\b|\bwon't\b", text, re.I):
        score += 10
    if re.search(r"\balways\b|\bshould\b", text, re.I):
        score += 8
    if len(text) < 40:
        score -= 5
    if len(text) > 1200:
        score -= 8
    return max(1, score)


def _one_line(text: str, limit: int = 180) -> str:
    line = re.sub(r"\s+", " ", text).strip()
    if len(line) <= limit:
        return line
    return line[: limit - 1] + "…"


def scan_file(slug: str, path: Path) -> list[Hit]:
    hits: list[Hit] = []
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return hits

    tid = path.stem
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = _extract_user_text(row)
        if not text or len(text) < 12:
            continue
        found = _UX_TERMS.findall(text)
        if not found:
            continue
        terms = sorted({t.lower().replace(" ", "") for t in found})
        # normalize display terms from original matches
        display = sorted({re.sub(r"\s+", " ", t.lower()) for t in found})
        bucket = _bucket_for(display)
        hits.append(
            Hit(
                score=_score(text, terms),
                quote=_one_line(text),
                project=slug,
                transcript_id=tid,
                path=str(path),
                mtime_iso=mtime.date().isoformat(),
                terms=display[:8],
                bucket=bucket,
            )
        )
    return hits


def load_existing_px_blobs(index_path: Path) -> list[str]:
    if not index_path.is_file():
        return []
    text = index_path.read_text(encoding="utf-8", errors="replace").lower()
    return re.findall(r"###\s+(px-\d+[^\n]*)", text) + re.findall(
        r"\*\*rule:\*\*\s*([^\n]+)", text
    )


def overlaps_existing(quote: str, existing: list[str]) -> bool:
    q = set(re.findall(r"[a-z0-9]{4,}", quote.lower()))
    if not q:
        return False
    for blob in existing:
        b = set(re.findall(r"[a-z0-9]{4,}", blob.lower()))
        if not b:
            continue
        inter = len(q & b)
        if inter >= 4 and inter / max(1, len(q)) >= 0.35:
            return True
    return False


def cluster_hits(hits: list[Hit], *, per_bucket: int) -> list[Hit]:
    """Keep highest-scoring unique-ish quotes per bucket."""
    by_bucket: dict[str, list[Hit]] = defaultdict(list)
    for h in sorted(hits, key=lambda x: (-x.score, x.mtime_iso), reverse=False):
        by_bucket[h.bucket].append(h)

    kept: list[Hit] = []
    for bucket, group in sorted(by_bucket.items()):
        group = sorted(group, key=lambda x: -x.score)
        seen_quotes: list[str] = []
        for h in group:
            if any(overlaps_existing(h.quote, [s]) for s in seen_quotes):
                continue
            seen_quotes.append(h.quote)
            kept.append(h)
            if len([k for k in kept if k.bucket == bucket]) >= per_bucket:
                break
    return sorted(kept, key=lambda x: (-x.score, x.bucket))


def next_px_id(index_path: Path) -> int:
    if not index_path.is_file():
        return 8
    ids = [int(x) for x in re.findall(r"###\s+PX-(\d+)", index_path.read_text(encoding="utf-8"))]
    return (max(ids) + 1) if ids else 8


def render_candidates_md(hits: list[Hit], *, scanned_files: int, raw_hits: int) -> str:
    lines = [
        "# PowerCore UX prefs — seed candidates",
        "",
        f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}Z from "
        f"Cursor `agent-transcripts` (files={scanned_files}, raw_hits={raw_hits}, "
        f"clustered={len(hits)})._",
        "",
        "Review, then either edit into `powercore-ux.preferences.md` by hand or run:",
        "",
        "```powershell",
        "cd C:\\Powercore-repo-main\\agent-skills",
        "py -3.13 -m tools.ux_prefs seed --all-projects --apply --max-apply 15",
        "```",
        "",
        "Tag on apply: `seeded` (operator may promote to `locked` / `preferred`).",
        "",
        "| Score | Bucket | Quote | Evidence |",
        "|---:|---|---|---|",
    ]
    for h in hits:
        q = h.quote.replace("|", "/")
        ev = f"{h.mtime_iso} · `{h.project}` · `{h.transcript_id[:8]}`"
        lines.append(f"| {h.score} | {h.bucket} | {q} | {ev} |")
    lines.append("")
    return "\n".join(lines)


def append_applied(index_path: Path, hits: list[Hit]) -> list[str]:
    n = next_px_id(index_path)
    blocks: list[str] = []
    ids: list[str] = []
    for h in hits:
        pid = f"PX-{n:03d}"
        n += 1
        ids.append(pid)
        title = h.bucket.replace("-", " ").title()
        blocks.append(
            "\n".join(
                [
                    f"### {pid} · Seeded: {title} (`seeded`)",
                    "",
                    f"**Rule:** {h.quote}",
                    "",
                    "**Do:** Honor this operator feel on matching PowerCore surfaces.",
                    "**Do not:** Drop without operator review — promote to `preferred`/`locked` when confirmed.",
                    f"**Surfaces:** review (from `{h.project}`)",
                    f"**Evidence:** {h.mtime_iso} transcript `{h.transcript_id}` — {h.path}",
                    "",
                ]
            )
        )
    body = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    if "## Append template" in body:
        body = body.replace(
            "## Append template",
            "## Seeded from transcripts (review)\n\n" + "\n".join(blocks) + "\n## Append template",
            1,
        )
    else:
        body = body.rstrip() + "\n\n## Seeded from transcripts (review)\n\n" + "\n".join(blocks) + "\n"
    # Ensure legend knows seeded
    if "`seeded`" not in body:
        body = body.replace(
            "| `fix-once` | Bitten in prod; treat as regression trap |",
            "| `fix-once` | Bitten in prod; treat as regression trap |\n"
            "| `seeded` | Mined from Cursor transcripts; promote after human skim |",
            1,
        )
    index_path.write_text(body, encoding="utf-8")
    return ids


def cmd_seed(args: argparse.Namespace) -> int:
    files = discover_jsonl(
        all_projects=bool(args.all_projects),
        project_slugs=args.project or None,
        limit_files=args.limit_files,
    )
    raw: list[Hit] = []
    for slug, fp in files:
        raw.extend(scan_file(slug, fp))

    existing = load_existing_px_blobs(Path(args.index))
    filtered = [h for h in raw if not overlaps_existing(h.quote, existing)]
    clustered = cluster_hits(filtered, per_bucket=max(1, int(args.per_bucket)))
    if args.min_score:
        clustered = [h for h in clustered if h.score >= int(args.min_score)]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render_candidates_md(clustered, scanned_files=len(files), raw_hits=len(raw)),
        encoding="utf-8",
    )

    applied_ids: list[str] = []
    if args.apply:
        to_apply = clustered[: max(0, int(args.max_apply))]
        if to_apply:
            applied_ids = append_applied(Path(args.index), to_apply)

    if args.json:
        payload = {
            "scanned_files": len(files),
            "raw_hits": len(raw),
            "candidates": [asdict(h) for h in clustered],
            "candidates_path": str(out),
            "applied": applied_ids,
        }
        print(json.dumps(payload, indent=2))
    elif args.plain:
        print(
            f"ux-prefs seed: files={len(files)} raw={len(raw)} "
            f"candidates={len(clustered)} → {out}"
        )
        if applied_ids:
            print(f"applied: {', '.join(applied_ids)}")
        for h in clustered[:12]:
            print(f"  [{h.score}] {h.bucket}: {h.quote[:100]}")
    else:
        print(f"Wrote {out} ({len(clustered)} candidates from {len(files)} files)")
        if applied_ids:
            print(f"Appended {', '.join(applied_ids)} to {args.index}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tools.ux_prefs")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("seed", help="Mine agent-transcripts for UX preference candidates")
    s.add_argument("--all-projects", action="store_true", help="Scan every Cursor project slug")
    s.add_argument("--project", action="append", help="Limit to project slug(s)")
    s.add_argument("--limit-files", type=int, default=None, help="Cap transcript files (newest first)")
    s.add_argument("--per-bucket", type=int, default=5, help="Max candidates kept per UX bucket")
    s.add_argument("--min-score", type=int, default=20)
    s.add_argument("--index", default=str(_DEFAULT_INDEX))
    s.add_argument("--out", default=str(_DEFAULT_CANDIDATES))
    s.add_argument("--apply", action="store_true", help="Append top candidates as seeded PX rows")
    s.add_argument("--max-apply", type=int, default=10)
    s.add_argument("--json", action="store_true")
    s.add_argument("--plain", action="store_true")
    s.set_defaults(func=cmd_seed)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
