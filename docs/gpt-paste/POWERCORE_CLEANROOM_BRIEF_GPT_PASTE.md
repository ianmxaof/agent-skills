# Cleanroom Brief — GPT / any-agent paste twin

Self-contained procedure for ChatGPT, Gemini, Grok, Claude web, or any agent **without**
repo file access. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-cleanroom-brief/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-cleanroom-brief/SKILL.md`

## When to paste this

Evidence-gated clone/rebuild: study a surface, emit a build brief, then check the result
against recorded evidence (confidence + coverage + limits).

## Paste template

```
You are running the PowerCore skill "powercore-cleanroom-brief" (Cleanroom Brief) with ZERO prior chat context.

PURPOSE:
Turn "clone this surface" into a deterministic evidence pass that a build agent must clear before acceptance.

DONE WHEN:
Evidence record + build brief exist; if a build was provided, a per-item pass/fail delta exists.

INPUTS THE HUMAN MUST FILL:
- target_url: surface to study
- mode: clean (default) | deep
- build_result_url_or_path: optional, for the check step

RULES:
- clean mode: screenshots + visible text + measured layout/colour/font only — no source/JS reads.
- deep mode: may use source/JS the human provides.
- Never invent confidence when evidence was not provided.
- Never score similarity without both baseline and post-build captures.
- Do not invent file paths or command output you were not given.

OUTPUT CONTRACT:
1. # Cleanroom brief
2. ## Source
3. ## Evidence summary (id · kind · confidence · coverage · limits)
4. ## Build brief (must-match list)
5. ## Check delta (after build) — or "awaiting build"
6. ## Next
7. Stop and ask before irreversible steps.

PROCEDURE:
1. Confirm mode + URL.
2. From the page excerpt / human captures, build evidence items.
3. Emit build brief citing evidence ids.
4. If build result provided: compare and list pass/fail per item.
5. Stop for human ACK.
```

## Sync rule

When the Cursor or Claude twin changes Output Contract / triggers / fence rules,
update this paste in the same change set.
