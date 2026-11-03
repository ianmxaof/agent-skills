"""Scaffold PowerCore skill surfaces: Cursor + Claude Code twin + GPT paste.

Default after operator ACK on skill-gap (never auto-run without ACK):

  cd agent-skills
  py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-example \\
    --title "Example" --description "When to invoke…"

  py -3.13 -m tools.skill_gap.scaffold_surfaces --check --skill powercore-example
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")

# Default Claude Code project roots that should receive thin twins.
_DEFAULT_CLAUDE_ROOTS = (
    Path(r"C:\Powercore-repo-main\telegram_bot2"),
    Path(r"C:\Powercore-repo-main\powercore-ops"),
    Path(r"C:\Powercore-repo-main\agent-skills"),
)


def _slug_to_title(name: str) -> str:
    parts = name.replace("powercore-", "").replace("tbcc-", "").split("-")
    return " ".join(p[:1].upper() + p[1:] for p in parts if p)


def _gpt_paste_stem(name: str) -> str:
    return name.upper().replace("-", "_") + "_GPT_PASTE.md"


def surface_paths(
    skill_name: str,
    *,
    repo: Path | None = None,
    claude_roots: list[Path] | None = None,
    gpt_paste_dir: Path | None = None,
) -> dict[str, Any]:
    """Return expected paths for the three surfaces (does not create files)."""
    root = (repo or _REPO).resolve()
    paste_dir = (gpt_paste_dir or (root / "docs" / "gpt-paste")).resolve()
    claude = list(claude_roots) if claude_roots is not None else list(_DEFAULT_CLAUDE_ROOTS)
    return {
        "cursor": root / ".cursor" / "skills" / skill_name / "SKILL.md",
        "claude": [r.resolve() / ".claude" / "skills" / skill_name / "SKILL.md" for r in claude],
        "gpt_paste": paste_dir / _gpt_paste_stem(skill_name),
        "evals": root / ".cursor" / "skills" / skill_name / "evals" / "evals.json",
    }


def check_surfaces(
    skill_name: str,
    *,
    repo: Path | None = None,
    claude_roots: list[Path] | None = None,
    gpt_paste_dir: Path | None = None,
    require_all_claude: bool = False,
) -> dict[str, Any]:
    """Report which surfaces exist. Claude: ok if ≥1 twin exists unless require_all_claude."""
    paths = surface_paths(
        skill_name, repo=repo, claude_roots=claude_roots, gpt_paste_dir=gpt_paste_dir
    )
    cursor_ok = paths["cursor"].is_file()
    claude_hits = [p for p in paths["claude"] if p.is_file()]
    claude_ok = (
        len(claude_hits) == len(paths["claude"])
        if require_all_claude
        else len(claude_hits) >= 1
    )
    gpt_ok = paths["gpt_paste"].is_file()
    missing: list[str] = []
    if not cursor_ok:
        missing.append(f"cursor:{paths['cursor']}")
    if not claude_ok:
        missing.append("claude:" + ",".join(str(p) for p in paths["claude"]))
    if not gpt_ok:
        missing.append(f"gpt_paste:{paths['gpt_paste']}")
    return {
        "skill": skill_name,
        "ok": cursor_ok and claude_ok and gpt_ok,
        "cursor": cursor_ok,
        "claude": claude_ok,
        "claude_paths_present": [str(p) for p in claude_hits],
        "gpt_paste": gpt_ok,
        "missing": missing,
        "paths": {
            "cursor": str(paths["cursor"]),
            "claude": [str(p) for p in paths["claude"]],
            "gpt_paste": str(paths["gpt_paste"]),
        },
    }


def _cursor_stub(*, name: str, title: str, description: str, gpt_rel: str) -> str:
    return f"""---
name: {name}
description: >-
  {description}
---

# {title}

Canonical Cursor skill. Triple Surface (locked): Cursor (this file) + Claude Code twin
under consuming repos' `.claude/skills/{name}/` + GPT paste at `{gpt_rel}`.

## Purpose

- TODO: one sentence outcome.

## When to invoke

- Trigger phrases: `/{name}`, TODO
- **Skip:** TODO

## Execution Profile

- Freedom: medium
- Mode: Agent

## Harness attach

| Surface | Value |
|---------|-------|
| **MCP** | none |
| **Hooks** | endgates on stop |
| **Memory** | disk paths TBD |
| **Compose** | → TBD |

## Behavioral rules

- Reason by: TODO
- Avoid: TODO
- Prioritize: TODO

## Output contract

1. TODO

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor (canonical) | `agent-skills/.cursor/skills/{name}/SKILL.md` |
| Claude Code twin | `<project>/.claude/skills/{name}/SKILL.md` |
| GPT / any-agent paste | `{gpt_rel}` |

Bump all three when tightening. Scaffold:

```powershell
cd C:\\Powercore-repo-main\\agent-skills
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill {name} --check
```

## Procedure

1. TODO
2. Stop for operator when judgment is required.
"""


def _claude_stub(*, name: str, title: str, description: str, gpt_rel: str) -> str:
    return f"""---
name: {name}
description: >-
  {description}
---

# {title} — Claude Code twin

Thin mirror of `agent-skills/.cursor/skills/{name}/SKILL.md` (canonical).
Drop Cursor-only Desktop Auto / Cloud lane wording. Keep the same Output Contract.
GPT / chat-only twin: `{gpt_rel}`.

## When to invoke

Same triggers as the Cursor skill. Prefer this twin when the session is Claude Code.

## Rules

- Load the Cursor canonical body when procedure detail is missing here.
- After substantive grind phases that need Cursor review: write reverse report + `PASTE INTO CURSOR`.
- Do not invent doctrine/pricing judgment (MUST NOT unless Cursor skill says MAY).

## Triple Surface

Keep in sync with Cursor skill + GPT paste when version-bumping.
"""


def _gpt_paste_stub(*, name: str, title: str, description: str) -> str:
    return f"""# {title} — GPT / any-agent paste twin

Self-contained procedure for ChatGPT, Gemini, Grok, Claude web, or any agent **without**
repo file access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/{name}/SKILL.md`
- Claude Code: `<project>/.claude/skills/{name}/SKILL.md`

## When to paste this

{description}

## Paste template

```
You are running the PowerCore skill "{name}" ({title}) with ZERO prior chat context.

PURPOSE:
{description}

DONE WHEN:
<one testable outcome>

INPUTS THE HUMAN MUST FILL:
- <field>: <what>
- <field>: <what>

RULES:
- Do not invent file paths or command output you were not given.
- Judgment ceiling: MUST NOT on pricing/doctrine unless the human explicitly unlocks it.
- Prefer short, checkable steps over essays.

OUTPUT CONTRACT:
1. <required section>
2. <required section>
3. Stop and ask the human before any irreversible step.

PROCEDURE:
1. …
2. …
3. …
```

## Sync rule

When the Cursor or Claude twin changes Output Contract / triggers / fence rules,
update this paste in the same change set.
"""


def _write(path: Path, text: str, *, force: bool) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and not force:
        return "skipped_exists"
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
    return "wrote"


def scaffold_surfaces(
    skill_name: str,
    *,
    title: str = "",
    description: str = "",
    repo: Path | None = None,
    claude_roots: list[Path] | None = None,
    gpt_paste_dir: Path | None = None,
    force: bool = False,
    skip_cursor: bool = False,
    skip_claude: bool = False,
    skip_gpt: bool = False,
) -> dict[str, Any]:
    """Create missing Triple Surface stubs. Never overwrites unless force=True."""
    if not _SKILL_NAME_RE.match(skill_name):
        raise ValueError(f"invalid skill name: {skill_name!r}")

    root = (repo or _REPO).resolve()
    paths = surface_paths(
        skill_name, repo=root, claude_roots=claude_roots, gpt_paste_dir=gpt_paste_dir
    )
    title_s = (title or _slug_to_title(skill_name)).strip()
    desc = (description or f"PowerCore skill {skill_name}. Invoke when the operator asks for it.").strip()
    # Relative path for docs inside stubs (portable wording)
    gpt_rel = f"agent-skills/docs/gpt-paste/{paths['gpt_paste'].name}"

    actions: dict[str, Any] = {"skill": skill_name, "actions": {}}

    if not skip_cursor:
        actions["actions"]["cursor"] = _write(
            paths["cursor"],
            _cursor_stub(name=skill_name, title=title_s, description=desc, gpt_rel=gpt_rel),
            force=force,
        )
        evals = paths["evals"]
        if not evals.is_file() or force:
            evals.parent.mkdir(parents=True, exist_ok=True)
            if not evals.is_file() or force:
                seed = {
                    "skill_name": skill_name,
                    "evals": [
                        {
                            "id": "mentions-triple-surface",
                            "prompt": f"Invoke /{skill_name} and confirm surfaces.",
                            "assertions": [
                                {"type": "contains", "value": "Triple Surface"},
                            ],
                        }
                    ],
                }
                evals.write_text(
                    json.dumps(seed, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
                actions["actions"]["evals"] = "wrote"
            else:
                actions["actions"]["evals"] = "skipped_exists"
        else:
            actions["actions"]["evals"] = "skipped_exists"

    if not skip_claude:
        claude_actions = []
        for p in paths["claude"]:
            claude_actions.append(
                {
                    "path": str(p),
                    "status": _write(
                        p,
                        _claude_stub(
                            name=skill_name,
                            title=title_s,
                            description=desc,
                            gpt_rel=gpt_rel,
                        ),
                        force=force,
                    ),
                }
            )
        actions["actions"]["claude"] = claude_actions

    if not skip_gpt:
        actions["actions"]["gpt_paste"] = {
            "path": str(paths["gpt_paste"]),
            "status": _write(
                paths["gpt_paste"],
                _gpt_paste_stub(name=skill_name, title=title_s, description=desc),
                force=force,
            ),
        }

    actions["check"] = check_surfaces(
        skill_name, repo=root, claude_roots=claude_roots, gpt_paste_dir=gpt_paste_dir
    )
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold Cursor + Claude Code + GPT paste skill surfaces"
    )
    parser.add_argument("--skill", required=True, help="Skill folder name (powercore-*)")
    parser.add_argument("--title", default="", help="Human title")
    parser.add_argument("--description", default="", help="Third-person description / when")
    parser.add_argument(
        "--root",
        type=Path,
        default=_REPO,
        help="agent-skills repo root",
    )
    parser.add_argument(
        "--claude-root",
        action="append",
        default=None,
        help="Project root that gets .claude/skills/<name>/ (repeatable). "
        "Default: telegram_bot2, powercore-ops, agent-skills",
    )
    parser.add_argument(
        "--gpt-paste-dir",
        type=Path,
        default=None,
        help="Override GPT paste directory (default: <root>/docs/gpt-paste)",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing stubs")
    parser.add_argument("--check", action="store_true", help="Only report missing surfaces")
    parser.add_argument("--skip-cursor", action="store_true")
    parser.add_argument("--skip-claude", action="store_true")
    parser.add_argument("--skip-gpt", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--require-all-claude",
        action="store_true",
        help="With --check, require every --claude-root twin (default: ≥1)",
    )
    args = parser.parse_args()

    claude_roots = (
        [Path(p) for p in args.claude_root]
        if args.claude_root
        else list(_DEFAULT_CLAUDE_ROOTS)
    )

    if args.check:
        report = check_surfaces(
            args.skill,
            repo=args.root,
            claude_roots=claude_roots,
            gpt_paste_dir=args.gpt_paste_dir,
            require_all_claude=args.require_all_claude,
        )
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            status = "ok" if report["ok"] else "missing"
            print(f"surfaces {args.skill}: {status}")
            for m in report["missing"]:
                print(f"  - {m}")
            if report["claude_paths_present"]:
                print("  claude present:")
                for p in report["claude_paths_present"]:
                    print(f"    {p}")
        return 0 if report["ok"] else 1

    try:
        out = scaffold_surfaces(
            args.skill,
            title=args.title,
            description=args.description,
            repo=args.root,
            claude_roots=claude_roots,
            gpt_paste_dir=args.gpt_paste_dir,
            force=args.force,
            skip_cursor=args.skip_cursor,
            skip_claude=args.skip_claude,
            skip_gpt=args.skip_gpt,
        )
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    else:
        print(f"scaffolded {args.skill}")
        for k, v in out["actions"].items():
            print(f"  {k}: {v}")
        chk = out["check"]
        print(f"check: {'ok' if chk['ok'] else 'incomplete'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
