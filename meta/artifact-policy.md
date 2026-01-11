# Artifact Policy

This document defines the structure, lifecycle, and handling of handoff artifacts in the agent-skills system.

## Key Concept: Artifacts, Not Cache

**Important terminology:** We call these "artifacts", not "cache".

- **Cache** implies: ephemeral, disposable, performance optimization
- **Artifacts** implies: decision records, reviewable, historical value

Artifacts are **decision records** that matter for:
- Debugging routing decisions
- Analyzing skill effectiveness
- Institutional learning
- System evolution

## Decoupling Principle

**Skills produce output. Execution layer handles persistence.**

This is the most important design principle:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Skill       │ --> │  Structured     │ --> │  Execution      │
│   (behavior)    │     │    Output       │     │    Layer        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                        │
                              │                        v
                              │               ┌─────────────────┐
                              │               │  Persist to     │
                              │               │  Filesystem     │
                              └──────────────>└─────────────────┘
```

**Why this matters:**
- Skills remain portable across execution environments
- Skills don't "know" where artifacts go
- Persistence mechanics can change without updating skills
- Testing skills is easier (no filesystem side effects)

**Correct framing in skills:**
> "This skill emits a handoff artifact conforming to handoff-protocol.md. Persistence is handled by the execution environment."

## Artifact Directory Structure

### Universal Template Location

```
agent-skills/templates/artifact-structure/
├── README.md
└── .gitignore
```

### Project Instance Location

```
.agent-skills/artifacts/
├── incoming/      # New artifacts (Cursor reads when pointed here)
├── processed/     # Already consumed
├── archive/       # Historical decision records
└── .gitignore
```

### Directory Purposes

| Directory | Purpose | Retention |
|-----------|---------|-----------|
| `incoming/` | New artifacts awaiting processing | Until processed |
| `processed/` | Recently consumed artifacts | 7 days (configurable) |
| `archive/` | Historical records for analysis | Long-term |

## Artifact Naming Convention

**Format:**
```
{skill-name}-{ISO-timestamp}.md
```

**Examples:**
```
adversarial-ui-tester-2026-01-07T19-42-00Z.md
privacy-tier-auditor-2026-01-07T20-15-30Z.md
skill-router-2026-01-07T20-16-00Z.md
```

**Rules:**
- Use skill name exactly as defined in skill's front matter
- Use ISO 8601 timestamp in UTC
- Replace colons with hyphens for filesystem compatibility
- Always use `.md` extension

## Artifact Front Matter

Every artifact MUST include this front matter:

```yaml
---
skill: skill-name
scope: core | domain | project
status: new | processed | archived
timestamp: 2026-01-07T19:42:00Z
intended-consumer: cursor | warp | human
priority: critical | high | medium | low
execution-mode: full-scan | incremental | targeted
target: "what was analyzed"
---
```

### Required Fields

| Field | Description | Values |
|-------|-------------|--------|
| `skill` | Name of skill that produced this | Skill name |
| `scope` | Scope of the skill | core, domain, project |
| `status` | Current lifecycle status | new, processed, archived |
| `timestamp` | When artifact was created | ISO 8601 UTC |
| `intended-consumer` | Who should process this | cursor, warp, human |
| `priority` | Processing priority | critical, high, medium, low |

### Optional Fields

| Field | Description |
|-------|-------------|
| `execution-mode` | How the skill was run |
| `target` | What was analyzed |
| `resolution-trace` | If from skill-router, include trace |
| `chain` | If part of a skill chain, chain name |
| `intent` | Intent hash for correlation (v1.5/v2 feature) |

**Intent Hash (Optional, v1.5/v2):**

The `intent` field enables correlation of repeated intents and effectiveness analysis per intent class. This is documented but not enforced in v1, as normalization scheme stability is unknown.

```yaml
intent:
  raw: "adversarial UI testing of onboarding flow"
  normalized: "adversarial-ui-test:onboarding"
```

**Note:** This is a future lever, not a current requirement. Wait until normalization patterns stabilize before making it required.

## Status Lifecycle

```
new --> processed --> archived
         |
         └--> deleted (optional)
```

### Status Transitions

| From | To | Trigger |
|------|-----|---------|
| new | processed | Cursor/Warp consumes artifact |
| processed | archived | Retention period expires OR manual archive |
| processed | deleted | Cleanup (not recommended) |
| archived | (permanent) | Long-term storage |

## Processing Workflow

### For Warp (Writing Artifacts)

1. Skill executes and produces structured output
2. Execution layer receives output
3. Execution layer writes to `artifacts/incoming/`:

```bash
mkdir -p .agent-skills/artifacts/incoming
cat << 'EOF' > .agent-skills/artifacts/incoming/adversarial-ui-tester-2026-01-07T19-42-00Z.md
---
skill: adversarial-ui-tester
scope: core
status: new
timestamp: 2026-01-07T19:42:00Z
intended-consumer: cursor
priority: high
---

## Summary
...

## Detailed Findings
...
EOF
```

### For Cursor (Reading Artifacts)

**Important:** Cursor is **pointed at** artifacts, not auto-scanning.

1. User directs Cursor to check `artifacts/incoming/`
2. Cursor reads artifacts where `status: new` AND `intended-consumer: cursor`
3. Cursor processes findings and integrates into project
4. Cursor updates artifact status to `processed`
5. Cursor moves artifact to `artifacts/processed/`

**Suggested Cursor command:**
```
"Process any new artifacts in .agent-skills/artifacts/incoming/"
```

## Git Handling

### Recommended .gitignore

```gitignore
# Artifact directories
incoming/
processed/

# Optionally track archive for historical analysis
# !archive/
```

### Rationale

- `incoming/` and `processed/` are **transient** - they change frequently and contain work-in-progress
- `archive/` is **optional to track** - valuable for historical analysis, skill effectiveness review, and debugging

### If Tracking Archive

When committing archived artifacts:
- Commit periodically (weekly or after significant work)
- Use commit message: "Archive: skill artifacts from [date range]"
- Consider compressing or summarizing very old artifacts

## Retention Policies

### Default Retention

| Directory | Retention | Rationale |
|-----------|-----------|-----------|
| `incoming/` | Until processed | Should be consumed quickly |
| `processed/` | 7 days | Recent history for debugging |
| `archive/` | Indefinite | Long-term institutional memory |

### Cleanup Commands

**Move processed to archive (manual):**
```bash
mv .agent-skills/artifacts/processed/*.md .agent-skills/artifacts/archive/
```

**Delete old processed (automated, 7+ days):**
```bash
find .agent-skills/artifacts/processed/ -name "*.md" -mtime +7 -delete
```

## Multi-Artifact Runs

A single intent can produce multiple artifacts:

```
.agent-skills/artifacts/incoming/
├── skill-router-2026-01-07T19-40-00Z.md          # Resolution trace
├── adversarial-ui-tester-2026-01-07T19-42-00Z.md  # Main analysis
└── skill-gap-detector-2026-01-07T19-45-00Z.md     # If gaps found
```

**Processing order:**
- Process in timestamp order (oldest first)
- Or by priority (critical before high before medium)
- Cursor decides based on context

## Integration with Lessons Learned

When Cursor processes artifacts, it should:

1. Extract generalizable lessons
2. Apply lessons-learned-protocol.md criteria
3. Update CLAUDE.md or propose skill improvements
4. Link back to artifact in archive (for provenance)

See `protocols/lessons-learned-protocol.md` for full protocol.

## Integration with Skill Effectiveness

Resolution trace artifacts feed into skill-effectiveness-analyzer:

1. Track which skills are invoked most often
2. Track confidence scores over time
3. Identify routing patterns and gaps
4. Propose tag improvements

See `skills/meta/skill-effectiveness-analyzer.md` for analysis approach.

## Column-Generated Artifacts

Artifacts generated by 2-agent columns include additional front matter fields.

### Additional Front Matter Fields

| Field | Description | Required |
|-------|-------------|----------|
| `column` | Name of column that generated this artifact | Optional |
| `refinement-layer` | Which Agent B mode was used (generic, domain-aware, effectiveness) | Optional |
| `agent-a-coverage` | Finding count before refinement | Optional |
| `agent-b-output` | Finding count after refinement | Optional |
| `domain-skill` | If refinement-layer is domain-aware, which skill was used as lens | Optional |

### Example Column Artifact Front Matter

```yaml
---
skill: adversarial-ui-tester
scope: core
status: new
timestamp: 2026-01-07T20:00:00Z
intended-consumer: cursor
priority: high
column: ux-adversarial
refinement-layer: generic
agent-a-coverage: 15 findings
agent-b-output: 6 findings
---
```

### Domain-Aware Example

```yaml
---
skill: architecture-review
scope: core
status: new
timestamp: 2026-01-07T20:05:00Z
intended-consumer: cursor
priority: high
column: architecture
refinement-layer: domain-aware
domain-skill: architectural-drift-detector
agent-a-coverage: 9 findings
agent-b-output: 4 findings
---
```

### Enforcement Rule

**Only Agent B writes artifacts.** Agent A output is internal to the column and never persisted to `artifacts/incoming/`.

This is a strict rule. If both agents write artifacts, the compression benefit of the column pattern is lost.

### A→B Handoff Format

Agent A produces raw output with this header (passed to Agent B, not persisted):

```yaml
---
skill: <skill-name>
status: raw
refinement-needed: true
finding-count: <number>
---
```

Agent B receives this, applies refinement, and writes the final artifact.

### Column Artifact Processing

Cursor processes column artifacts **exactly the same** as single-skill artifacts:

1. Read from `incoming/`
2. Parse front matter (including column metadata)
3. Process findings
4. Move to `processed/`

The `column:` field is informational — it helps with debugging and effectiveness tracking but doesn't change processing behavior.

See `docs/column-pattern-guide.md` for full column pattern documentation.

---

## Summary

| Principle | Implementation |
|-----------|----------------|
| Skills don't persist | Execution layer handles writing |
| Cursor doesn't auto-scan | User points Cursor at artifacts |
| Artifacts are decisions | Not logs, not cache |
| Git tracks archive only | Transient directories ignored |
| Lifecycle is explicit | new → processed → archived |
| Columns compress signal | Only Agent B writes artifacts |

