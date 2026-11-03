---
name: powercore-binary-recon
description: Orchestrates an evidence-first reverse-engineering pipeline over an
  owned or authorized binary — static triage, optional LLM decompile, agent analysis
  via installed MCP bridges, evidence-anchored findings report. Authorized targets only.
---
# Binary Recon — Claude Code twin

Thin mirror of `agent-skills/.cursor/skills/powercore-binary-recon/SKILL.md`.
GPT paste: `agent-skills/docs/gpt-paste/POWERCORE_BINARY_RECON_GPT_PASTE.md`.

## Stages

1. Triage (Ghidra / radare2) → 2. Optional decompile → 3. Optional MCP agent loop → 4. Report

## Rules

- Owned/authorized targets only — refuse otherwise
- Defensive inventory + orchestration — no exploit PoC / bypass recipes
- Every finding cites tool + address/artifact
- Do not claim a stage ran without tool output in the transcript

## Output contract

`# Binary recon report` → Verdict · Evidence table · Fit · Next

## Relay

After grind needing Cursor review: reverse report + `PASTE INTO CURSOR`.
