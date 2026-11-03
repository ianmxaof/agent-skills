---
name: powercore-skill-gap
description: >-
  Suggest missing PowerCore skills after crystallize; Triple Surface scaffold
  (Cursor + Claude twin + GPT paste) on operator ACK. Invoke on skill gap,
  create skill, Claude twin, GPT paste twin, from-now-on checklist.
---

# PowerCore skill-gap — Claude Code twin

Thin mirror of `agent-skills/.cursor/skills/powercore-skill-gap/SKILL.md` (canonical).
GPT paste: `agent-skills/docs/gpt-paste/POWERCORE_SKILL_GAP_GPT_PASTE.md`.

## When to invoke

Same as Cursor: skill gap / create skill / missing checklist / Triple Surface.

## Locked create rule

After operator ACK, **do not** ship Cursor-only. Scaffold all three surfaces:

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-<slug> `
  --title "…" --description "…"
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-<slug> --check
```

Backfill: `--skip-cursor` writes Claude + GPT only.

## Pending proposals → ACK → scaffold

Endgates rows now log `proposed_slug` + `score` on every suggest. Review the backlog (read-only):

```powershell
py -3.13 -m tools.skill_gap.pending            # structured rows only
py -3.13 -m tools.skill_gap.pending --legacy   # also recover pre-logging rows from the free-text `lines`
```

Only after operator ACK, one line writes all three surfaces (never auto-write):

```powershell
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-<slug> --title "…" --description "…"
```

Compose edge (manual, not wrapped): to tune an *existing* skill rather than mint one, use
`tools.skill_gap.improve_once` / `overnight_loop`. No `powercore-skill-improve` skill yet —
revisit once goldens ≥ 12. Slugs `untitled`, bare `gap`/`vault`/`report`/`fail` are rejected.

## Rules

- Suggest-only until ACK — never auto-write SKILL.md.
- Prefer `powercore-*` names; do not mint new `tbcc-*`.
- Load Cursor canonical for full Anthropic shape checks + scoring dimensions.
- End multiphase grinds with `PASTE INTO CURSOR` when a reverse report is required.

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor | `agent-skills/.cursor/skills/<name>/SKILL.md` |
| Claude | `<project>/.claude/skills/<name>/SKILL.md` |
| GPT paste | `agent-skills/docs/gpt-paste/<NAME>_GPT_PASTE.md` |
