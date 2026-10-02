# TBCC Sitrep (v1.0)
Changelog: Initial — mid-operation tactical reconstitution: glossed completions, collision board, CI/CD wire/close, Vectors ($ first). Distinct from Daily Brief (cold-start).

## Purpose
- Reconstruct what parallel agents shipped while the operator multitasked (ADHD / multi-vertex workflow).
- Surface collisions, untested seams, and bake debt before they tax revenue.
- Re-rank next moves for **CI/CD fuses + money** — tactical bearing, not a full sprint rewrite.
- Use **mid-operation** when 2–4 agents/verticals are live; for cold-start priorities use Daily Brief instead.

## When to Invoke
- Trigger phrases: `sitrep`, `situation report`, `mid-op status`, `what just shipped`, `bearing check`, `/sitrep`
- Situational: operator signals multitask overload; ≥2 parallel verticals in flight; after several agent completions without a session-close; agent may **suggest** sitrep (do not auto-run full protocol without a trigger)

## Execution Profile
- Mode: Agent (read-heavy); **no code edits**; may *propose* sprint patches but write nothing unless operator later picks “patch sprint”
- Model lane: A (Auto) by default per model-routing skill; B (frontier Plan/Ask) only if merge/collision judgment is hard
- Parallelism: up to 2 readonly `explore` subagents (cheap) — (1) git/diff + recent commits, (2) sprint/handoffs/agent-transcript titles; inherit Agent mode
- Mode inheritance: explore subagents stay readonly Agent at spawn; do not switch to Plan unless operator asks to implement a Vector

## Delegation & Tooling
- Skills invoked: none required; may consult `model-routing` if spend anxiety is raised
- Commands / hooks: none required; sprint state may already be injected via `.cursor/hooks.json`
- MCP / integrations: optional one-line stack pulse (`tbcc-stack-cli` / island truth) — **never Start bots**, never touch `.env`

## Behavioral Rules
- Reason by evidence sources (ordered):
  1. `git status` + `git log --since='36 hours'` + diffstat (what landed locally)
  2. `tbcc/docs/SPRINT_STATE.md` — In flight / Blocked / DoD gaps (do not paste the full table)
  3. Recent `tbcc/docs/handoffs/*` and agent-transcript titles (glossed completions)
  4. Optional stack pulse (home lean vs island money path)
  5. Field Intel docs only when Vectors/Quests need “intel → money” (`SITE_INTEL_FRONTIER_PROMPTS.md`, browse-intel notes) — **no live scrape**
- Naming: call the four-site overlay system **TBCC Field Suite** (ER/ML/TV/FL Field + `tbcc-suite-rail`); browse/RSS path = **Field Intel**. Avoid “userscript modules” in operator speech.
- Avoid: replaying Daily Brief’s full Untied dump; Cloud Agent bias; inventing blockers; starting payment/loot; re-laddering Deferred without “why now”
- Prioritize ranking order (strict) for Vectors and Wire/close:
  1. **ST money** — live sales, bots answering, FOMO/Telegram reach, loot/payment fulfillment, island tunnel/API truth
  2. **LT money** — revenue island cutover, flywheel (X/Buffer/Erome), scrape→pool, Field Intel → pools, affiliate/loot growth
  3. **Ops risk** — 409/session locks, CHAT_RESTRICTED, dual-DB, GHCR wipe of docker-cp
  4. **Velocity / UX** — Field Suite polish only if it clearly unlocks ST/LT money
- Hard caps: Just shipped ≤8; Wire/close ≤5; Vectors = 5; Quests 0–3 or omit
- **Gloss budget:** prefer last ~36h completions over restating the sprint table
- **Vertical tags** on every Just-shipped and Wire item (`island`, `field-suite`, `loot`, `buffer-x`, `watch-aof`, …)
- **Collision heuristics:** same file touched by >1 recent commit/handoff; “docker-cp / bake”; payment/loot Off vs island; ext version bump without TEST_MAP note
- **CI/CD fuse language:** each Wire item names evidence (`pytest …`, GHCR recreate, `tbcc-stack-cli`, ingest URL)
- Vectors ordered **highest financial impact first** (same ladder shape as Daily Brief Top 5); every row: horizon `ST`|`LT`|`OPS`, effort, Lane (Why+How), Unblocks / Evidence

## Output Contract
- Required sections (exact headings):
  1. **Bearing** — 2–4 sentences: time window, parallel verticals detected, money/runtime one-liner
  2. **Just shipped (you may have glossed)** — ≤8 bullets of *completed* work from git/handoffs/transcripts; vertical-tagged
  3. **Collision board** — overlaps / double-touches / untested seams / bake debt / dual-DB; or `none detected`
  4. **Wire / close** — ≤5 CI/CD or ops fuses ranked by revenue protection
  5. **Vectors** — Top 5 next moves, highest $ impact first
  6. **Quests (stub)** — 0–3 empirical intel/R&D questions only if they clearly unlock ST/LT money; **omit section** if none
  7. **Lane** — one primary lane for “pick a number”
- Format: concise prose + bullets/numbered lists; no full sprint table paste
- Done means: all required sections present (Quests optional omit); Vectors cite evidence; **no edits made**
- Artifacts: none (propose sprint patches in prose only)
- Failure contract: if a probe fails partway, halt and report what completed / missing / inconsistent; no auto recovery, rollback, or retry without operator instruction. If sprint state missing/stale, say so in Bearing and continue from git + notes.

## Exit Conditions
- Next: wait for operator to pick a Vector number (or reject / ask for sprint patch)
- Follows into: implement on Desktop Auto / named Plan / tray ops / handoff-cc as the chosen Vector’s Lane dictates — **none** until they pick
