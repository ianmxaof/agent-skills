---
name: powercore-repo-trust
description: >
  Triages untrusted checkouts/URLs before vendoring. v1.1: smell_level +
  operator_action + claim ledger + --ask. Smell ≠ go-ahead.
---

# Repo Trust — Claude Code twin

Thin mirror of `agent-skills/.cursor/skills/powercore-repo-trust/SKILL.md` (canonical).
GPT paste: `agent-skills/docs/gpt-paste/POWERCORE_REPO_TRUST_GPT_PASTE.md`.

## Contract (v1.1)

Lead with `smell_level` + `operator_action` + claim ledger + script `next_step`.
Never “Looks fine to vendor” on LOW smell when action is SPOT_CHECK/STOP or claims miss.
Compose → `powercore-pipeline-fit` on HARVEST_OK / PIPELINE_FIT. Gate scary runs with
`powercore-skill-fire-gate`. Do not fork TrapDoor Unicode paths (Threat Monitor B1).

## When to invoke

`/repo-trust`, safe-to-vendor, gist/paste triage — prefer `--ask "does <feature> exist?"`.
