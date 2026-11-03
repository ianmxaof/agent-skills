# TBCC Ops Picture (v1.0)
Changelog: Initial — live analytics snapshot + error-hub synopsis + plain-language blockers for correctness and financial ops.

## Purpose
- Produce a **current picture** of TBCC money metrics, funnel health, scheduling/posting reliability, and operational conflicts.
- Summarize the **error hub** (home tray log or island container logs) in operator-readable form.
- Explain in **plain language** the most important outstanding issues that prevent TBCC from working correctly or improving financial operations.
- Distinct from **Daily Brief** (untied + Top 5 menu) and **Sitrep** (what parallel agents just shipped).

## When to Invoke
- Trigger phrases: `/ops-picture`, `ops picture`, `TBCC ops picture`, `health and analytics`, `financial ops report`, `what's broken in tbcc`, `analytics and errors`
- Situational: before a revenue debug session; after deploy; when income/loot/companion “feels off”; weekly money check

## Execution Profile
- Mode: Agent (read-heavy); **no code edits** unless user picks a fix afterward
- Model lane: A (Auto) by default; B (frontier Plan/Ask) only if blocker diagnosis is ambiguous across ≥3 systems
- Parallelism: optional readonly probes in parallel — island SSH `docker ps`, MCP `user-tbcc` analytics, local API; inherit Agent mode
- Mode inheritance: subagents stay readonly Agent; do not Start bots or edit `.env`

## Delegation & Tooling
- Skills invoked: none required
- Commands / scripts (preferred order):
  1. **Island (canonical money DB):** `ssh root@5.161.53.91 "cd /opt/tbcc/infra && docker compose -f docker-compose.revenue-island.yml --env-file .env.revenue-island exec -T api python scripts/ops_picture_snapshot.py"` (after script is deployed)
  2. **Local API container / home backend:** `cd tbcc/backend && python scripts/ops_picture_snapshot.py`
  3. **HTTP fallbacks** (island `https://api.powercore.app` or `TBCC_PUBLIC_API_BASE_URL`): `GET /analytics/ops-picture?days=30` (preferred — full snapshot + blockers), `/analytics/income/summary`, `/gate-funnel`, `/companion-margin`, `/health/scheduling/fast`
  4. **MCP `user-tbcc`:** `tbcc_health`, `analytics_income_summary`, `analytics_weekly_summary`, `analytics_subscriptions`, `analytics_post_events_summary` when API/script unavailable
  5. **Home error hub:** tail `tbcc/.tbcc-run/error-hub.log` (last ~80 lines) when snapshot `error_hub.available=false` and operator is on Windows tray stack
  6. **Island error tail:** `docker compose ... logs --tail 60 worker api beat payment_bot loot_bot companion_bot secretary_bot` — pattern-match 409, `database is locked`, tracebacks
- Never: `POST /bots/runtime/*/start`, tray Start, spawn duplicate bots

## Behavioral Rules
- **Source priority:** island DB/API (money truth) → home API → MCP → sprint/handoffs for context only
- **Analytics window:** default **30 days** for money/funnel; **7 days** for posts/import failures unless user specifies
- **Plain language blockers:** rank by financial impact first:
  1. **ST money** — bots down, checkout broken, loot can't deliver, companion zero conversion, gate/beacon dead
  2. **LT money** — attribution blind, thin pools, flywheel stalled, affiliate mis-routed
  3. **Ops risk** — 409 conflicts, session locks, scheduler stalls, import backlog, worker crashes
  4. **Noise** — deprecations, benign hub lines, preview crawlers — mention briefly or skip
- Translate metrics: e.g. `photos_sold=0` → “Spicy bot isn't converting paid photos”; `stall.count>0` → “Scheduled posts are overdue”
- Cap error-hub synopsis to **≤8 distinct themes** (group repeated lines); cite severity
- Cross-check `tbcc/docs/SPRINT_STATE.md` **In flight** only for labels — live probes win over stale notes
- Avoid: inventing revenue; full sprint table paste; Cloud Agent bias; fixing anything without user picking a row

## Output Contract
- Required sections (exact headings):
  1. **Snapshot** — date/time, data source (island/local/MCP), one-line runtime truth (containers up / API reachable)
  2. **Analytics** — bullets: income rollup (gross vs payouts vs net), **Stars cashflow** (ledger vs Fragment 21-day hold), **external cashflow** (Linkvertise/AdMaven sync + payouts), **OpenRouter vision spend** (`vision_llm.pulse_line` from the same snapshot — daily/weekly/monthly key usage + local vision call counters + 429s), gate-funnel, companion, loot, posts/imports failure %
  3. **Error hub** — grouped synopsis (theme · severity · count/recency); `none material` if clean
  4. **Blockers** — numbered **1→N** (highest $ impact first), each: **what's wrong** · **why it hurts money/ops** · **evidence** (metric, log line, endpoint)
  5. **Lane** — one primary lane for “pick a number to fix”
- Format: concise prose + bullets; numbers rounded sensibly; no secret values
- Done means: all five sections present; blockers cite probe evidence; no edits made
- Artifacts: none (optional: user may save output to handoff)
- Failure contract: if island unreachable, say so in Snapshot, fall back to MCP/local, label confidence **low** on money figures; do not invent blockers — list probe gaps

## Exit Conditions
- Next: wait for operator to pick a blocker number or ask for deeper drill-down on one metric
- Follows into: tray ops / island deploy / Desktop Auto fix / Frontier Plan if doctrine — **none** until they pick
