# TBCC Daily Brief (v1.0)
Changelog: Initial — anytime warm-start: untied loose ends + Top 5 ranked by short/long-term financial impact.

## Purpose
- Bring the operator up to speed on **untied loose ends** without replaying the whole sprint.
- Emit a **Top 5** direction ladder (same shape as Bottom line next-steps) ranked by **money impact first** — short-term cashflow, then long-term revenue architecture.
- Use when cold-starting a chat, after time away, or when asking “what should we do next?”

## When to Invoke
- Trigger phrases: `daily brief`, `TBCC daily brief`, `bring me up to speed`, `loose ends`, `what’s untied`, `/daily-brief`
- Situational: user returns after ≥1 day gap and asks for priorities; optional at session start if they say “brief me”

## Execution Profile
- Mode: Agent (read-heavy); **no code edits** unless user picks a ladder item after the brief
- Model lane: A (Auto) by default; B (frontier Plan/Ask) only if ranking trade-offs are ambiguous
- Parallelism: optional readonly `explore` subagent (cheap) to skim handoffs / improvement notes; inherit Agent mode
- Mode inheritance: explore subagents stay readonly Agent; do not switch to Plan unless user asks to implement

## Delegation & Tooling
- Skills invoked: none required; may consult `model-routing` if spend anxiety is raised
- Commands / hooks: none; sprint state already injected via `.cursor/hooks.json`
- MCP / integrations: optional Buffer/stack probes only if needed for a one-line money/ops pulse — never Start bots

## Behavioral Rules
- Reason by: read `tbcc/docs/SPRINT_STATE.md` (In flight, Blocked, DoD gaps, Deferred) + skim `TBCC_IMPROVEMENT_NOTES.md` / recent handoffs for open threads
- Avoid: re-laddering Deferred without a “why now”; Cloud Agent bias; inventing blockers not in sources; starting payment/loot bots
- Prioritize ranking order (strict):
  1. **ST money** — live sales, bots answering, FOMO/Telegram reach, loot/payment fulfillment, island tunnel/API truth
  2. **LT money** — revenue island cutover, flywheel (X/Buffer/Erome), scrape→pool pipeline, affiliate/loot growth
  3. **Ops risk** — 409/session locks, CHAT_RESTRICTED, dual-DB confusion
  4. **Velocity / UX** — extension polish, filters, docs — only if they clearly unlock ST/LT money
- Cap loose ends to the **most material** items (≤8 bullets); dump is not a brief
- Top 5 ordered **highest financial impact first** (opposite of Bottom line’s low→high convenience ladder)
- Every Top 5 row: horizon `ST`|`LT`|`OPS`, effort, Lane (Why+How), Unblocks / Evidence tags like Bottom line

## Output Contract
- Required sections (exact headings):
  1. **Pulse** — 1–3 sentences: money/runtime truth + date context. **Must include** OpenRouter vision spend from `GET /analytics/ops-picture` field `vision_llm.pulse_line` (or island snapshot). Do not omit because CLIP is off.
  2. **Untied** — bullets of open loops (owner if known)
  3. **Top 5** — numbered 1→5, highest $ impact first
  4. **Lane** — one primary lane for “pick a number”
- Format: concise prose + numbered list; no paste of full sprint table
- Done means: all four sections present; Top 5 cite evidence from sprint/notes/stack; no edits made
- Artifacts: none required (optional: patch `Last updated` on sprint only if facts changed during probes)
- Failure contract: if sprint state missing/stale, say so in Pulse, run minimal inference from git/notes, ask one confirm; do not invent a full sprint rewrite unless user invokes sprint-start

## Exit Conditions
- Next: wait for user to pick a Top 5 number (or reject)
- Follows into: implement on Desktop Auto / named Plan / tray ops / handoff-cc as the chosen row’s Lane dictates — **none** until they pick
