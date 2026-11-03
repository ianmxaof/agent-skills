---
name: powercore-binary-recon
description: Orchestrates an evidence-first reverse-engineering pipeline over an
  owned or authorized binary — static triage, optional LLM decompile pass, agent
  analysis via installed MCP bridges, evidence-anchored findings report. Use for
  /recon, triage this binary, decompile and report, or RE workstream setup on
  authorized targets only.
purpose: Wire existing RE tools into one reviewable pipeline with per-finding evidence
trigger_phrases:
- /powercore-binary-recon
- /recon
- triage this binary
- binary RE pipeline
- decompile and report
inputs:
- path to owned/authorized binary, firmware, or APK
- which MCP bridges are installed (if any)
outputs:
- evidence-anchored findings report (markdown card, per-finding tool + address refs)
jev_hints:
  lane: run
  cost: heavy
  needs_context: true
if_stumped: Ask once for the target binary path and which MCP bridges are installed.
example_invocation: /recon ./target.exe
---
# PowerCore Binary Recon (v0.1)

Canonical Cursor skill. Triple Surface (locked): Cursor (this file) + Claude Code twin
under consuming repos' `.claude/skills/powercore-binary-recon/` + GPT paste at
`agent-skills/docs/gpt-paste/POWERCORE_BINARY_RECON_GPT_PASTE.md`.

Foundation from public RE-tool roundups (Ghidra / radare2 / LLM4Decompile / r2ai /
ida-pro-mcp / reverse-engineering-assistant / REA). **Orchestration skill only** —
does not ship exploit PoCs or unauthorized access steps.

## Purpose

Run an evidence-first pipeline over a binary the operator **owns or is authorized**
to analyze, and emit a findings report where every claim cites tool + address/artifact.

## When to invoke

- `/recon`, "triage this binary", "decompile and report", RE workstream setup
- Operator has a local target and optional MCP bridges installed

**Skip when:** no authorization; they want malware weaponization; Hub tab is marketing-only
(`/capture` + Desk instead).

## Stage order

1. **Triage** — Ghidra GUI or radare2 CLI: format, symbols, entry points
2. **Decompile** — optional LLM-assisted decompile; note re-executability caveats on self-benchmarks
3. **Agent loop** — only if MCP bridges installed (r2ai / ida-pro-mcp / REA-class); operator reviews
4. **Report** — every finding anchored to evidence (tool, address, artifact)

## Execution Profile

- Freedom: medium (stage order locked; tool choice depends on install)
- Mode: Agent

## Harness attach

| Surface | Value |
|---------|-------|
| **MCP** | optional: ida-pro-mcp, reverse-engineering-assistant, r2ai — never invent schemas |
| **Hooks** | endgates on stop; ship-gate before any vendored bridge |
| **Memory** | findings markdown; no secret extraction into chat logs |
| **Compose** | → `powercore-repo-trust` before vendoring bridges · ← `/capture` for study lists |

## Behavioral rules

- Authorized targets only. Refuse otherwise in one short sentence.
- Stay at **defensive inventory + skill shape** — no exploit PoC, no bypass recipes.
- Do not present self-benchmark scores as verified performance.
- Do not claim a stage ran without its tool output in the transcript.
- Prefer `/run repo-trust` before installing any third-party RE bridge.

## Checklist (copy and tick)

```
- [ ] 1. Confirm ownership/authorization + binary path
- [ ] 2. List installed tools / MCP bridges (or stop — triage-only)
- [ ] 3. Triage → optional decompile → optional agent loop
- [ ] 4. Emit Output Contract with evidence rows
- [ ] 5. Stop; no silent install of bridges
```

## Output contract

```markdown
# Binary recon report

## Verdict
one line

## Evidence
| tool | finding | address/artifact |

## Fit
what stage runner still missing

## Next
1. …
```

## Do not

- Analyze binaries without ownership/authorization
- Emit exploit / bypass / credential-dump procedures
- Claim MCP tools exist without schema evidence
- Treat star-count / trending claims as proof

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor (canonical) | `agent-skills/.cursor/skills/powercore-binary-recon/SKILL.md` |
| Claude Code twin | `<project>/.claude/skills/powercore-binary-recon/SKILL.md` |
| GPT / any-agent paste | `agent-skills/docs/gpt-paste/POWERCORE_BINARY_RECON_GPT_PASTE.md` |

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-binary-recon --check
```

## Status

v0.1 — chat orchestration contract. Stage-runner CLI not shipped.
