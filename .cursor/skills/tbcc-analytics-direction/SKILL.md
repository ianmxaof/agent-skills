# TBCC Analytics Direction (v1.0)
Changelog: Initial — on-demand data-driven Top 5 investment ranking; hybrid deterministic rank + optional LLM narrative.

## Purpose
- Answer **where to invest the next hour** using live TBCC analytics (not sprint/git alone).
- Compose ops picture, growth signals, proposals, funnel spikes, pool pressure, and demand gaps into ranked **directions**.
- Distinct from **Ops Picture** (what's broken), **Daily Brief** (sprint menu), **Sitrep** (what shipped), and **Revenue Brief** (scheduled inbox).

## When to Invoke
- Trigger phrases: `/analytics-direction`, `analytics direction`, `where to invest`, `growth direction`, `data-driven priorities`
- Situational: after `/ops-picture` blockers are understood; before picking a sprint task; weekly money strategy check
- Telegram: Secretary `/direction` or `/direction llm` (phone-first)

## Execution Profile
- Mode: Agent (read-heavy); **no code edits** unless operator picks a direction to implement
- Model lane: Auto by default; frontier Plan/Ask only if direction choice requires doctrine (pricing, irreversible leak policy)
- Parallelism: optional readonly probes — island API, MCP `analytics_direction`, local CLI; inherit Agent mode
- Mode inheritance: subagents stay readonly Agent

## Delegation & Tooling
- Commands / scripts (preferred order):
  1. **Island:** `ssh root@5.161.53.91 "cd /opt/tbcc/infra && docker compose -f docker-compose.revenue-island.yml --env-file .env.revenue-island exec -T api python scripts/analytics_direction_snapshot.py --days 30"`
  2. **HTTP:** `GET https://api.powercore.app/analytics/direction?days=30` (add `&use_llm=true` for narrative)
  3. **Local CLI:** `cd tbcc/backend && python scripts/analytics_direction_snapshot.py --days 30 --markdown`
  4. **MCP `user-tbcc`:** `analytics_direction(days=30, use_llm=False)`
  5. **Telegram:** `/direction` on @aof_secretary_bot (admin); `/direction llm` for narrative
- Cross-read `tbcc/docs/SPRINT_STATE.md` **In flight** labels only for sprint cross-check section
- Never: auto-execute growth proposals, Start bots, edit `.env`

## Behavioral Rules
- **Source priority:** island DB/API → local API → MCP → sprint labels for cross-check only
- **Window:** default **30 days** unless user specifies
- **Ranking law:** ST revenue > LT compounding > OPS risk (same as Daily Brief Top 5 / Sitrep Vectors)
- **Observe-only:** directions cite `mcp_followup` tools — operator or agent acts only after pick
- **Contradictions:** surface thin-pool vs post-more conflicts; do not hide downgraded proposals
- **LLM:** include narrative section only when user asks or `use_llm=true`; never reorder deterministic Top 5
- Avoid: inventing revenue; full sprint table paste; Cloud Agent bias; fixing without user pick

## Output Contract
- Required sections (exact headings):
  1. **Evidence** — source (island/local/MCP/Telegram), window, 3–5 headline metrics from `evidence_summary`
  2. **Trends** — income/companion/post deltas if material; else `flat`
  3. **Directions** — numbered 1→5 ($ impact first): horizon · category · confidence · title · MCP follow-up
  4. **Contradictions** — bullets or `none`
  5. **Sprint cross-check** — aligned vs gap (In flight labels only)
  6. **Narrative** — optional; only if LLM requested
  7. **Lane** — one primary lane for “pick a number”
- Done means: all required sections (Narrative optional omit); directions cite evidence; no edits made
- Failure contract: if island unreachable, fall back to local/MCP, label confidence **low** on money figures; list probe gaps

## Exit Conditions
- Next: wait for operator to pick a direction number
- Chain: `/preflight` if implementation ≥3 files; tray ops for runtime fixes; **none** until they pick
