---
name: tbcc-agent-crew
description: >-
  GSP v2.4 — spin a small maker/checker agent crew with role isolation, shared
  handoff artifacts, and mandatory /silent-fail external stops. Invoke with
  /crew, /crew investigate, /crew codebase-audit, agent crew, maker checker swarm.
---

# TBCC Agent Crew (v1.2)

Changelog: v1.2 — Graph Spec template (Lunar graph-engineering doctrine); EDGE DATA contract on checker; optional metrics stub. v1.1 — `codebase-audit` preset. v1.0 — maker/checker presets; blast-radius fence; Compose → /silent-fail.

## Purpose

- Run **multiple specialized makers** plus a **coordinator checker** instead of one solo agent grinding everything.
- Force **role isolation in prompts and tools**, not fake isolation via “five bots / one login” (Grok failure mode).
- End every crew with **checkable stops** via `/silent-fail` — never agent self-attestation alone.
- **codebase-audit:** monorepo “nervous system” — surface bloat *and* forgotten half-built connections (reconnect > delete).

## When to Invoke

- Trigger phrases: `/crew`, `/crew <preset>`, `/crew investigate`, `/crew codebase-audit`, `/crew niche-find`, `/crew repo-graph`, `agent crew`, `maker checker`, `spin up a crew`
- Situational: multi-surface bug; investigate-then-patch; ops brief; **repo bloat / orphan-script / reconnect pass**
- **Skip:** one-line bug fix; docs-only; Start bots / `.env`; “just implement”; money/Telegram mutate without operator unlock; auto-delete without operator pick

## Presets

| Preset | Makers (≤3) | Coordinator job |
|--------|-------------|-----------------|
| `investigate` (default) | explore codebase · form repro hypotheses · draft patch proposal (no apply) | Synthesize contradictions; refuse “looks fixed”; emit silent-fail stop list |
| `preflight-review` | map blast radius · list tests/migrations · list Do-not-touch hits | Produce `/preflight`-shaped plan; no code |
| `ops-brief` | sitrep/git skim · sprint/handoff skim · health probe | One brief + silent-fail watches for touched surfaces |
| `codebase-audit` (`repo-graph` alias) | **bloat scout** · **connection scout** · **entropy on findings** | Merge two ledgers; refuse mass-delete; rank reconnect first; emit evidence stops |
| `niche-find` | **catalog scout** · **demand scout (web search)** · **fence checker** | Merge ≤5 buyer-niche ideas; drop age/personal-ad/RSS; inbox export |

Custom: operator names roles; still ≤3 makers + 1 checker; still end with `/silent-fail`.

### `codebase-audit` detail (readonly unless operator unlocks deletes)

**Phases (in one crew run):**

1. **Dispatch** — scope roots (default): `tbcc/backend/scripts/`, `tbcc/docs/handoffs/`, optionally `tbcc/services/`, extension dead paths. Respect SPRINT Do-not-touch.
2. **Fan-out**
   - **Bloat scout:** empty dirs; zero-importer scripts; duplicate `_probe_*`; handoffs with no `_report`; TEST_MAP orphans
   - **Connection scout:** exists but never called (imports, Beat keys, CLI entrypoints, docs claiming a script that has no callers)
   - **Entropy maker:** ≤5 vertices on findings (`missed`/`covered`/`blocked`) — reconnect yield only
3. **Merge** — dedupe; prefer reconnect over delete; empty folders are low priority unless they confuse agents
4. **Verify** — every row needs an external stop (see below). **No deletes / no wire-ups in this phase.**

**Report artifact:** `tbcc/docs/handoffs/YYYY-MM-DD_codebase-audit_report.md` with:

| Ledger | Cap | Required per row |
|--------|-----|------------------|
| **A — Bloat** | ≤20 | path · why candidate · evidence command+snippet · proposed action `archive`/`delete`/`keep` · risk |
| **B — Reconnect** | ≤10 | path A · path B · missing link · evidence · proposed wire (one clause) · unblocks |

Rank ledger B above A. Operator picks 1–3 items → `/preflight` or `/directive`.

**Task-specific silent-fail (codebase-audit):**

| Claim | Stop evidence |
|-------|----------------|
| “unused script” | `rg`/import graph shows zero callers **and** not in Beat schedule / TEST_MAP / CLI help — paste command |
| “empty folder” | `Get-ChildItem` / `dir` empty (or only noise) |
| “connect A↔B” | both paths exist; cite the gap (missing call / missing import) |
| intentional archive / paused / Do-not-touch | verdict `idle` — not bloat |

Forbidden: auto-delete; treating governor-idle / `*_ENABLED=0` as unused without reading enablement; Grok-scale fan-out (>3 makers).

### `niche-find` detail (readonly; no money mutate)

Buyer/demand niches against **existing** loot pools. Web search, not RSS. Age fence on.

1. **Catalog scout** — `analytics-direction-latest.md` + money-path health + pool slugs (`src_lv_*`).
2. **Demand scout** — free-first web search (`TBCC_EXA_API` → `TBCC_SERP_API` → `TBCC_PARALLELAI_API` → Brave → DuckDuckGo). Cursor Exa MCP / `WebSearch` may supplement.
3. **Fence checker** — drop under-21 sexual hits only (legal floor). No source/host denylist. Keep RSS, ABG, and other adult sources as corpus evidence.
4. **Coordinator** — ≤5 suggested ideas → `llm-rag/knowledge/inbox/thinktank-niche-*.md` (corpus thinktank reads these on the next pass)

CLI (preferred mechanical run):

```
cd C:\Powercore-repo-main\telegram_bot2\tbcc\backend
py -3.13 scripts/run_niche_find.py --json
```

`--offline` skips LLM; `--no-search` is catalog-only (use when the parent will search). Graph spec skip — Python scouts are the makers. Still end with `/silent-fail`. Silent-fail stops: inbox file exists; pytest `tests/test_niche_find_service.py`; first digest bullet contains a thesis not just a title.

## Execution Profile

- Mode: **Agent** for orchestration; makers default **readonly** unless operator said implement
- Model lane: Desktop Auto parent; cheap model for explore makers; Frontier only for judgment-gate coordinator verdicts
- Parallelism: up to 3 Task/explore makers in parallel; coordinator = parent only
- Mode inheritance: makers inherit readonly unless preset or operator unlocks write; never Start bots

## Delegation & Tooling

- **Required read first:** `tbcc/docs/AGENT_BLAST_RADIUS.md`
- Also: `tbcc/docs/SPRINT_STATE.md`; `/silent-fail` skill; optional `SILENT_FAIL_REGISTRY.example.json`; for `codebase-audit` also `tbcc/docs/entropy-lenses.json` (innovation axes)
- **Graph Spec (v1.2):** before spawning makers on `investigate` or `preflight-review`, coordinator fills the paste block in `tbcc/docs/CREW_GRAPH_SPEC.md` (GOAL → EDGE DATA → FAILURE POLICY → BUDGET). Prompts optimize nodes; the spec optimizes topology. Skip for `ops-brief`, `niche-find` (CLI scouts are the makers), or when the task is genuinely single-agent (Lunar §14).
- Shared artifacts: `tbcc/docs/handoffs/` or operator-named scratch path under `tbcc/docs/handoffs/`
- MCP: none required; do not Start bots
- Skills: `tbcc-silent-fail` (mandatory exit); `tbcc-entropy-scan` (inline vertex pass inside codebase-audit — do not spawn a separate unbounded entropy chat); `tbcc-preflight` if ≥3-file implement follows; `directive-generator` for Lane C

## Behavioral Rules

- Reason by: load blast-radius → **fill Graph Spec when preset warrants it** → pick preset → spawn makers with **narrow jobs** → write maker briefs to shared path → coordinator synthesizes → `/silent-fail`
- **Dependency test (every maker→checker edge):** coordinator must state *what exact data crosses* — not "maker finished." If nothing crosses, delete the edge or merge makers.
- **Checker is asymmetric verifier:** objective = falsify/contradict maker claims, not defend them.
- **Role ≠ identity.** Assume shared `.env` / MCP / Telethon graph. Do not claim credential isolation.
- Avoid: Grok-style “five specialists on one browser login”; coordinator holding write tools it doesn’t need; skipping silent-fail; inventing restart/page policy; mass-delete PRs
- Prioritize: reconnect half-built scripts; external stops; reversible proposals; sprint Do-not-touch

## Output Contract

1. **Preset** — name + one-line why
2. **Graph spec** — GOAL + PARALLEL WORK + EDGE DATA (+ BUDGET/HUMAN GATE); or `skipped — single-agent`
3. **Blast fence** — which shared surfaces this crew could touch (from AGENT_BLAST_RADIUS)
4. **Maker briefs** — ≤3; each job + artifact path written; each lists **outputs crossing to checker**
5. **Coordinator verdict** — synthesize / contradict / refuse (for codebase-audit: include Ledger A+B summary counts)
6. **Silent-fail stops** — hand off to `/silent-fail` with watch ids or exact commands (per-row evidence for audit)
7. **Metrics stub (optional)** — makers_completed, verifier_rejections, fan_out_unique_findings, human_intervention
8. **Next** — none | implement | `/preflight` | `/directive` | operator pick from Ledger B then A

Done means: maker artifacts exist; coordinator verdict written; silent-fail stop list present (run or queued for operator). For codebase-audit: report file with both ledgers.

Failure contract: if a maker fails, report partial briefs; do not pretend full coverage; do not auto-retry unbounded.

## Exit Conditions

- Next: run `/silent-fail` (required) → operator picks fix / ignore / implement / reconnect
- Composes: → `tbcc-silent-fail` → optional `tbcc-preflight` | `directive-generator`
- Follows into: Bottom line **Compose: /silent-fail** after every crew

## Agent procedure

1. Read `AGENT_BLAST_RADIUS.md` + sprint state.
2. Resolve preset (default `investigate`).
3. Coordinator fills Graph Spec (`tbcc/docs/CREW_GRAPH_SPEC.md`) unless skipped per §Delegation.
4. Spawn ≤3 makers (cheap explore for map/search).
5. Collect briefs into handoff/scratch files — structured outputs, not prose blobs when feasible.
6. Coordinator emits Output Contract §1–5 (+ optional §7).
7. Invoke or emit exact `/silent-fail` watch list (§6). Stop for operator.
