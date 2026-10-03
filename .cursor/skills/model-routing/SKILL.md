---
name: model-routing
description: Decide which AI model lane (Cursor Auto, named frontier model in Cursor, or Claude Code) is best for the current development task, given the user's Cursor Pro and Claude Pro subscriptions and their rate limits. Use when selecting models for subagents, when starting a large or complex task, when the user asks which model to use, or whenever usage limits, rate limits, quotas, or model cost come up.
---

# Model Routing

Changelog: v1.1 — asymmetric spend + judgment escalation gate; forbid Auto-stub on revenue/architecture doctrine.

Route work across three lanes to maximize quality per dollar under the user's two subscriptions: **Cursor Pro ($20/mo)** and **Claude Pro ($20/mo, includes Claude Code)**. Current quota numbers live in [limits.md](limits.md) — read it before giving quota-sensitive advice, and re-verify against official docs if it looks stale.

TBCC project rules (`bottom-line-next-steps.mdc`, `tbcc-agent-platform-routing.mdc`) apply the same calculus in-repo; **judgment escalation and Cloud hard gates there win** when they conflict with a casual Auto default.

## The Three Lanes

| Lane | What | Cost behavior | Use for |
|------|------|---------------|---------|
| **A — Cursor Auto** | Auto router in the model picker | Generous included usage on Pro; does not meaningfully drain the $20 pool | Default for ~80% of *implementation*: edits, tests, routine refactors, docs, scripting, ops smoke |
| **B — Named frontier model in Cursor** | Manually picked model (Opus-class, GPT-class, Gemini Pro-class) | Draws down the $20/mo included API pool at provider rates | Architecture, product/monetization critique, gnarly debugging, high-risk doctrine, final review — **Plan/Ask, short output** |
| **C — Claude Code (terminal)** | Separate Anthropic quota, Sonnet-class on Pro plan | Independent of Cursor entirely; 5-hour rolling window + weekly cap | Long agentic grinds, large mechanical batch work, a second parallel workstream while Cursor handles another task |

## Asymmetric spend

- **Execution** → Lane A (or C if mechanical grind).
- **Judgment** → Lane B once, then A implements.
- Wrong product/architecture decisions cost more than frontier tokens. Under-using Lane B on monetization/doctrine is **not** thrift.

## Judgment escalation gate (≥2 triggers → Lane B)

Escalate when **at least two** apply:

1. Revenue model (pricing, SKUs, gates, loot economy, funnels).
2. Multi-system architecture (ext + backend + bots + host/gates, lasting shape).
3. Irreversible doctrine (brand, watermark/leak policy, recovery ledger, ship-vs-wait).
4. Leakage / trust / ToS risk.
5. Operator asked for critique / strategy (not “just implement”).
6. Ambiguous high-cost trade-offs (hybrid hosts, primary revenue path, etc.).

Then: **Lane B Plan/Ask → Lane A implement.** Do not invent doctrine mid-PR on Auto.

Optional specialist: name a model family in the one-line call when it matches the question (e.g. Thinking-High for scarcity psychology) — still short Plan/Ask.

## Routing Procedure

1. **Classify the task**:
   - *Routine* (clear spec, low blast radius) → Lane A.
   - *Judgment gate* or *hard thinking, small output* → Lane B (Plan/Ask). Then implement on Lane A.
   - *Long grind, low judgment* → Lane C, freeing Cursor for interactive work.
2. **Check budget phase**: Early in the Cursor billing month, Lane B is cheap insurance — use it for planning when the gate fires. Late in the month with the pool depleted, fall back to Lane A + Lane C and reserve Lane B for true emergencies (or rely on Auto for execution only).
3. **Check Claude window risk**: Claude Code has a rolling 5-hour window and a shared weekly cap. Don't start a multi-hour Lane C grind if the weekly cap is nearly exhausted; run `/usage` inside Claude Code to check.
4. **Recommend, don't lecture**: when this skill fires, output a one-line routing call (e.g. "Lane B for the schema design, then Lane A to implement") — not a full explanation, unless asked.
5. **Anti Auto-stub**: never recommend Lane A as the *thinking* lane for gate-triggered work just to sound economical.

## Subagent Model Routing (applies inside Cursor agent runs)

When spawning subagents via the Task tool:

- **explore / search / summarize** → cheap fast model (mini/flash/haiku class). Never spend frontier tokens on file discovery.
- **plan / review / security audit** → top-tier thinking model; these are small-output, high-judgment tasks where model quality dominates.
- **implementation / best-of-N runners** → default (inherit parent model); for best-of-N, consider mixing one frontier attempt with cheaper attempts.
- If the user is on Auto for the top-level agent, leave subagent model unset unless one of the above rules clearly applies — **except** when spawning an explicit plan/review subagent for judgment-gate work (then set a thinking/frontier model).

## Honest Constraints (do not overpromise)

- The agent **cannot switch its own top-level model mid-conversation**; only the user can, via the model picker. Routing happens at: session start (recommendation), subagent spawning (agent-controlled), and Cursor↔Claude Code handoff (recommendation).
- The agent **cannot read live usage meters**. Authoritative sources: [cursor.com/dashboard](https://cursor.com/dashboard) → Usage, and `/usage` inside Claude Code. If a routing call depends on remaining quota, ask the user or tell them where to check.
- Claude Pro does **not** include Opus in Claude Code — Sonnet-class only. Opus-class work belongs in Lane B.

## Worked Examples

- "Design the sync engine for offline mode" → Lane B (Plan mode, frontier model), then implement on Lane A.
- "Critique this Telegram loot monetization loop" → Lane B Ask (judgment gate: revenue + critique); then Lane A for scaffold code.
- "Zip flywheel: hybrid host + gate + SKU + extension toolbar" → Lane B short Plan (architecture + revenue), then Lane A/C implement.
- "Rename this API across the backend and fix call sites" → Lane A; if it's 50+ files of mechanical churn, Lane C while Cursor stays free.
- "Why does this race condition only happen in prod?" → Lane B (Debug-style investigation justifies frontier reasoning).
- "Write tests for these five new services" → Lane C overnight or in parallel; review the output on Lane A.
- "Add a button to the settings page" → Lane A, no discussion needed.
- "Move the progress bar to the top of the gallery" → Lane A.
