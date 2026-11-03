---
name: tbcc-prompt-chains
description: >-
  Runs named multi-step cognitive YAML chains from tbcc/docs/prompt-chains/ in
  Plan/Ask (no island executor). Invoke with /prompt-chain, /chain, run
  CRITICAL_PATH_ANALYSIS, compress this, classify capture, incident triage bundle.
---

# TBCC Prompt Chains (v1.0)

Changelog: v1.0 — stolen from llm-rag; canonical YAML in repo; agent-executed (not `prompt_chains.py` on island).

## Purpose

- Execute **versioned thinking recipes** (YAML steps with `{context}` passthrough) on a pasted blob — incident notes, sprint dump, vault capture, messy issue list.
- Complement **protocol skills** (`tbcc-entropy-scan`, `directive-generator`): those pick *which workflow*; chains pick *how to compress/reason* on input text.
- **No** Streamlit combo meter, Mem0, or island runtime — agent runs steps inline in this session.

## When to invoke

- Trigger phrases: `/prompt-chain`, `/chain`, `/chain <NAME>`, `run ENTROPY_AUDIT`, `critical path on this`, `compress to one sentence`, `classify this capture`, `incident triage bundle`
- Situational: operator pastes a blob and wants structured multi-step reasoning before a pick; sibling skill says "run chain X" (see registry)
- **Skip:** named file-level bug with "just the bug"; live Beat/Celery changes (use silent-fail + pytest); operator already picked a single protocol and needs no text compression

## Execution profile

- Mode: **Plan / Ask** — no file edits unless operator picks a follow-up slice
- Model lane: Desktop Auto; Frontier if judgment on doctrine/leakage embedded in the blob
- Parallelism: none (steps are sequential; context = previous step output only)
- Do **not** import or call `llm-rag/src/app/utils/prompt_chains.py` from TBCC backend or island

## Delegation & tooling

- **Required read:** `tbcc/docs/prompt-chains-registry.json` (when_hints, bundles, validators)
- **Chain YAML:** `tbcc/docs/prompt-chains/<NAME>.yaml`
- Optional RAG: if vault context helps, read cited paths — chains do not auto-retrieve unless the operator asks
- MCP `ask_llm`: optional for a local runner; stateless — never read rotator index (see `llm_model_index.py` boundary)
- **CLI:** `cd tbcc/backend && py -3.13 scripts/run_prompt_chain.py --list` · `py -3.13 scripts/tbcc_cli.py prompt-chain SYNTHESIS_COMPRESSION --input "..."` — calls `/zeus/v1/ask` on island (default `TBCC_API_PUBLIC_URL`)

## Available chains

| Chain | Steps | Use |
|-------|-------|-----|
| `CRITICAL_PATH_ANALYSIS` | 3 | assumptions → risk table → one action |
| `ENTROPY_AUDIT` | 2 | stale claims → verify/update each |
| `FIRST_PRINCIPLES_STRIP` | 2 | atomic facts → rebuild argument |
| `INBOX_ROUTER` | 1 | PARA label for vault capture |
| `LEVERAGE_MATRIX` | 2 | 2×2 table → one low-effort/high-impact pick |
| `SYNTHESIS_COMPRESSION` | 1 | one dense leverage sentence |

**Bundles** (run in order, pass final output of chain N as `{context}` to chain N+1):

- `incident_triage`: `FIRST_PRINCIPLES_STRIP` → `CRITICAL_PATH_ANALYSIS`
- `directive_pack`: `SYNTHESIS_COMPRESSION` (feeds Goal line in directive-generator)
- `vault_capture`: `INBOX_ROUTER` (after crystallize)

## Behavioral rules

- Load YAML; for each step: format `prompt` with current `{context}`; emit step output; replace context with that output for the next step
- Honor per-step `temperature` intent: extraction low (0.0–0.2), final pick lowest (0.0–0.1)
- Show **Step N / description / output** in the reply — operator must see the pipeline
- `INBOX_ROUTER`: final output must match `task|idea|reference|archive|inbox` only; if not, retry step once at temperature 0.0
- `LEVERAGE_MATRIX` does **not** replace bottom-line next-steps ladder (no reversibility/evidence commands)
- Avoid: running chains unattended on island; inventing steps not in YAML; keeping full original dump in final step when the chain expects compression

## Output contract

1. **Chain** — name (+ bundle if used)
2. **Input** — one-line summary of what was processed (not full dump unless short)
3. **Steps** — numbered; each: description + output (truncate middle steps >400 chars with `…`)
4. **Final** — last step output, clearly labeled
5. **Compose?** — optional next hop: `/directive`, `/entropy-scan`, `/crystallize`, implement — or stop

Done means: all steps completed or failure reported at failing step; Final is actionable or validated (INBOX_ROUTER).

## Exit conditions

- Next: operator pick → load sibling skill per `protocol-chains.json` or registry `compose_before`
- Composes: → `directive-generator` | `tbcc-crystallize` | `tbcc-preflight` | implement (by pick)
- Follows into: Bottom line **Compose:** when obvious

## Agent procedure

1. Resolve chain: explicit name → else match `when_hints` in registry → else ask once
2. Read `tbcc/docs/prompt-chains/<NAME>.yaml`
3. Set `context` = operator paste (or prior skill output if composed)
4. For each step: run prompt mentally; emit step block; update `context`
5. Apply `output_validator` from registry if present
6. Emit Output Contract; stop for pick unless bundled into a sibling skill (e.g. directive-generator runs `SYNTHESIS_COMPRESSION` inline on Goal — see that skill)

## Sibling integrations (do not duplicate — delegate)

| Sibling | Chain hook |
|---------|------------|
| `tbcc-directive-generator` / `directive-generator` | Run `SYNTHESIS_COMPRESSION` on normalized issues **before** writing Goal (step 4 of procedure) |
| `tbcc-crystallize` | After inbox write, suggest `INBOX_ROUTER` on capture body; report label to operator |
| `tbcc-entropy-scan` | Optional: after scan, operator may run `ENTROPY_AUDIT` on `tbcc/docs/` excerpt for doc-hygiene lens |
| `tbcc-silent-fail` | When class-2 diagnosis ambiguous, optional `incident_triage` bundle on probe evidence paste |
| `tbcc-integration-scan` | When candidate is secondhand, optional `FIRST_PRINCIPLES_STRIP` before trust scoring |

Claude Code twin: `.claude/skills/tbcc-prompt-chains/SKILL.md` (same contract).
