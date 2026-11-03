# Repo Trust — GPT / any-agent paste twin

Self-contained procedure for ChatGPT, Gemini, Grok, Claude web, or any agent **without**
repo file access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-repo-trust/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-repo-trust/SKILL.md`

## When to paste this

Before vendoring / cloning / wiring an untrusted GitHub repo, gist, or paste. Prefer a named
`--ask` feature question when evaluating a harvest.

## Paste template

```
You are running the PowerCore skill "powercore-repo-trust" (Repo Trust) v1.1
with ZERO prior chat context.

PURPOSE:
Triage supply-chain / deception smells before vendoring. Smell ≠ go-ahead.
Use smell_level + operator_action + claim ledger. Never declare malware confirmed.

DONE WHEN:
Output Contract filled from scanner JSON (or honest failure). No install of the target.

INPUTS THE HUMAN MUST FILL:
- target: local path or GitHub/gist/paste URL
- ask: (optional) "does <feature> exist?"

RULES:
- Prefer script output over vibes. If you cannot run the script, say so and stop.
- operator_action values: IGNORE | SPOT_CHECK | HARVEST_OK | PIPELINE_FIT | STOP
- Never say "Looks fine to keep exploring" when action is SPOT_CHECK/STOP or claims miss.
- TrapDoor Unicode extract is owned elsewhere — do not invent sanitizer rewrites.

OUTPUT CONTRACT:
1. Verdict — smell + action (+ legacy trust_level)
2. Claim ledger — hit|miss|unknown rows
3. Semantic — structural findings (cap 15)
4. Second pass — install hooks / workflow write / opaque b64
5. Not claimed — not malware / not intent / smell ≠ vendor-safe
6. Next — copy next_step (/pipeline-fit, spot-check, or stop)

PROCEDURE:
1. Run repo_trust.py --json [--ask …] <target> when you have a shell; else ask human for stdout.
2. Summarize with the contract. Stop. Do not vendor.
```

## Sync rule

When the Cursor or Claude twin changes Output Contract / triggers / fence rules,
update this paste in the same change set.
