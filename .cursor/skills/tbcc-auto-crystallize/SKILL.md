---
name: tbcc-auto-crystallize
description: >-
  Need-to-Know (NTK) auto-crystallize gate for vault inbox. MUST run at end of
  substantive assistant turns (not thanks/lint/Ask trivia): score via
  run_crystallize_gate.py --auto and write when tier is suggest/auto/must.
  Use when operator says crystallize, /crystallize, auto-crystallize, NTK,
  vault capture, or when tip auto-crystallize-gate fires. Covers project
  registry, tiers, env knobs, never-list. Manual /crystallize always wins.
---

# TBCC auto-crystallize (NTK gate)

Always-on tip (procedure lives here): `.cursor/rules/powercore-endgates.mdc`

Prefer one CLI for end-of-turn:

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.endgates --prompt "..." --response "..." --auto --plain
```

## Agent procedure (end of turn)

1. **Skip fast** if turn is clearly trivial — no CLI needed.
2. Otherwise:

```powershell
cd C:\Powercore-repo-main\telegram_bot2\tbcc\backend
py -3.13 scripts\run_crystallize_gate.py --source cursor --model "cursor-agent" `
  --prompt "USER_PROMPT_HERE" --response "ASSISTANT_RESPONSE_HERE" --auto --json
```

Use `--file` or pipe stdin if response is long. For gate-only (no write): omit `--auto`.

3. **Report one line** to operator:
   - Wrote: `💎 Auto-crystallized (NTK 52, tbcc) → knowledge/inbox/…`
   - Skip: *(silent — do not mention)*
   - Only if write is off (`INCLUDE_SUGGEST=0`) and tier is suggest: `💎 Crystallize suggested (NTK 52, tbcc) — say /crystallize to capture`

4. Manual `/crystallize` always wins — see `tbcc-crystallize` skill.

## NTK scale (0–100)

| Dimension | Max | Signals |
|---|---:|---|
| project_relevance | 30 | Matches `tbcc/data/crystallize_project_registry.yaml` slugs |
| subject_weight | 30 | Code, paths, env vars, wiring, architecture, tables |
| durability | 20 | Long-form, defaults/canonical rules, procedures |
| actionability | 10 | Runnable commands, checklists |
| novelty | 10 | New implementation, caveats, root-cause fixes |

**Tiers** (env defaults): `skip` <40 · `suggest` 40–59 · `auto` 60–79 · `must` ≥80

**Confidence** (0–1): certainty that matched **projects** and **subjects** are correct.

## When to auto-write

All must be true:

- `TBCC_AUTO_CRYSTALLIZE_ENABLED=1` (default on)
- Tier is `suggest`, `auto`, or `must` (`TBCC_AUTO_CRYSTALLIZE_INCLUDE_SUGGEST=1` default — do **not** wait for `/crystallize`)
- Confidence ≥ `TBCC_AUTO_CRYSTALLIZE_MIN_CONFIDENCE` (default 0.45)
- Completion is **need-to-know** for future work — not social, not trivial Q&A, not duplicate of obvious docs

## Never crystallize

Secrets without redaction; operator said skip; pure formatting/lint; "thanks/ok" acks; Ask-mode read-only with no new durable facts.

## Extend projects

Edit `tbcc/data/crystallize_project_registry.yaml` — add `slug` + `aliases`. No code change required.

## Env knobs (`tbcc/.env`)

- `TBCC_AUTO_CRYSTALLIZE_ENABLED=1`
- `TBCC_AUTO_CRYSTALLIZE_THRESHOLD=60`
- `TBCC_AUTO_CRYSTALLIZE_MUST_AT=80`
- `TBCC_AUTO_CRYSTALLIZE_SUGGEST_AT=40`
- `TBCC_AUTO_CRYSTALLIZE_INCLUDE_SUGGEST=1`
- `TBCC_AUTO_CRYSTALLIZE_MIN_CONFIDENCE=0.45`
- `TBCC_AUTO_CRYSTALLIZE_LLM_GATE=0` — set `1` to refine borderline scores via chat LLM (future: Jev decisions)

Capture only — no island deploy, no money path. Redaction stays on.
