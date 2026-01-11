# Cursor Intake Protocol

This document defines the standard command for Cursor to process incoming artifacts, whether from single skills or columns.

## Purpose

Establish a **standing contract** for artifact processing that:
- Requires no re-explanation of context
- Works on low-energy days
- Is deterministic and predictable
- Treats artifacts as the instruction

## Standard Intake Command

### Primary Command

> **"Run the standard artifact intake and integration pass."**

### Equivalent Variants

All of these mean the same thing:

- "Process incoming artifacts and propose next steps."
- "Ingest warp reviews and produce a consolidated plan."
- "Review inbox artifacts and update the integration plan."
- "Check artifacts/incoming and integrate findings."

### Why One Sentence Works

The artifact **is** the instruction. You don't need to re-explain because:

| Element | Already in Artifact |
|---------|---------------------|
| Scope | Front matter `scope:` field |
| Priority | Front matter `priority:` field |
| Findings | Detailed Findings section |
| Recommendations | Recommendations section |
| What NOT to do | Handoff Notes section |

## What Cursor Does (Intake Pass)

### Step 1: Open Artifacts

```
artifacts/incoming/
├── adversarial-ui-tester-2026-01-07T20-00-00Z.md
├── architecture-review-2026-01-07T20-05-00Z.md
└── performance-budget-guardian-2026-01-07T20-10-00Z.md
```

Read all files where:
- Located in `artifacts/incoming/`
- `status: new`
- `intended-consumer: cursor`

### Step 2: Parse Front Matter

Extract metadata to understand:
- Which skill produced this
- Which column (if any)
- Priority level
- Execution mode and target

### Step 3: Read Findings

For each artifact:
- Parse Summary section
- Parse Detailed Findings section
- Note severity rankings
- Extract recommendations

### Step 4: Synthesize

Look across all artifacts for:

| Pattern | Action |
|---------|--------|
| **Conflicts** | Note for human review |
| **Convergence** | Same issue found by multiple sources → higher confidence |
| **Gaps** | Areas not covered by any artifact |
| **Reinforcing signals** | Multiple artifacts point same direction |

### Step 5: Produce Plan

Generate concrete plan or diff suggestions:
- Prioritize by severity
- Address critical and high first
- Note deferred items
- Include reasoning

### Step 6: Extract Lessons (If Applicable)

Check if findings reveal generalizable lessons:
- Apply lessons-learned-protocol.md criteria
- Propose updates to CLAUDE.md if warranted
- Link back to artifact for provenance

### Step 7: Move Artifacts

After processing:
- Update `status: new` to `status: processed`
- Move artifacts to `artifacts/processed/`

## Standing Contract

This command is a **standing contract**, not a creative request.

### Cursor Should

- Execute deterministically
- Process what's there
- Follow artifact structure
- Report clearly

### Cursor Should NOT

- Invent new analysis
- Ask clarifying questions (unless ambiguous)
- Ignore low-priority findings (just defer them)
- Delete artifacts (move to processed)

## Example Session

```
User: "Run the standard artifact intake and integration pass."

Cursor:
┌──────────────────────────────────────────────────────────────────┐
│ ARTIFACT INTAKE REPORT                                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Found 3 artifacts in incoming/                                   │
│                                                                  │
│ 1. adversarial-ui-tester-2026-01-07T20-00-00Z.md                │
│    Column: ux-adversarial | Priority: high                      │
│    Findings: 6 (2 critical, 2 high, 2 medium)                   │
│                                                                  │
│ 2. architecture-review-2026-01-07T20-05-00Z.md                  │
│    Column: architecture | Priority: medium                      │
│    Findings: 4 (1 high, 3 medium)                               │
│                                                                  │
│ 3. performance-budget-guardian-2026-01-07T20-10-00Z.md          │
│    Column: performance | Priority: medium                       │
│    Findings: 3 (3 medium)                                       │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ SYNTHESIS                                                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Convergence detected:                                            │
│ - Accessibility issue found by BOTH UX and Architecture columns │
│   → HIGH CONFIDENCE: Fix priority elevated                       │
│                                                                  │
│ No conflicts detected.                                           │
│                                                                  │
│ Gap: No security review artifact present                         │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ PROPOSED PLAN                                                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Immediate (Critical):                                            │
│ 1. Fix form validation bypass in checkout (UX-001)              │
│ 2. Add error boundary for payment failures (UX-002)             │
│                                                                  │
│ High Priority:                                                   │
│ 3. Resolve accessibility labeling (UX-003, ARCH-001)            │
│ 4. Add keyboard navigation to modal (UX-004)                    │
│                                                                  │
│ Deferred (Medium):                                               │
│ 5. Optimize bundle size for checkout module (PERF-001)          │
│ 6. Refactor state management pattern (ARCH-002)                 │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ LESSONS EXTRACTED                                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Proposed CLAUDE.md update:                                       │
│ "Always include aria-labels when creating form components"       │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ ARTIFACTS MOVED                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 3 artifacts → processed/                                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Low-Energy Day Usage

The intake protocol is designed for sustainable usage:

```
1. You trigger agents/columns earlier
   └─▶ They run and produce artifacts

2. Later, you say one sentence
   └─▶ "Run the standard artifact intake and integration pass."

3. Cursor does the synthesis
   └─▶ You review the proposed plan

4. You approve or adjust
   └─▶ Cursor implements
```

**No re-explaining. No context reconstruction. No prompt archaeology.**

## Multi-Column Processing

When multiple columns run in parallel:

```
artifacts/incoming/
├── adversarial-ui-tester-2026-01-07T20-00-00Z.md    (column: ux-adversarial)
├── architecture-review-2026-01-07T20-05-00Z.md      (column: architecture)
├── performance-budget-guardian-2026-01-07T20-10-00Z.md (column: performance)
└── failure-mode-simulator-2026-01-07T20-15-00Z.md   (column: correctness)
```

Cursor processes **all** artifacts together in the intake pass.

### Cross-Column Synthesis

| Multiple columns report same issue | Note convergence → higher confidence |
| Columns report conflicting findings | Note conflict → flag for human review |
| Unique findings per column | Process normally |

### Deduplication

Deduplication happens at **Cursor synthesis**, not within columns.

When consolidating:
- Note the merge in the plan
- Don't silently drop findings
- Credit both sources

## Processing Order

### Default: By Priority

1. Critical
2. High
3. Medium
4. Low

### Alternative: By Timestamp

Process oldest first (FIFO).

### Cursor Decides

Based on context and artifact metadata.

## Artifact States

```
incoming/ (status: new)
    │
    │ "Run the standard artifact intake..."
    v
Cursor reads + integrates
    │
    v
processed/ (status: processed)
    │
    │ After retention period
    v
archive/ (status: archived)
```

## Integration Points

- `meta/artifact-policy.md` - Artifact lifecycle rules
- `protocols/handoff-protocol.md` - Artifact content structure
- `protocols/lessons-learned-protocol.md` - Lesson extraction criteria
- `docs/column-pattern-guide.md` - Column pattern details
- `docs/agent-invocation-guide.md` - Full Cursor guide

## Common Mistakes

### ❌ Processing Without Direction

Cursor should NOT auto-scan artifacts. Wait for explicit intake command.

### ❌ Re-Running Analysis

Cursor processes artifacts. It doesn't re-run the skills that generated them.

### ❌ Ignoring Low-Priority Findings

Defer them, don't ignore. They may become important later.

### ❌ Deleting Instead of Moving

Always move to `processed/`. Artifacts are decision records.

### ❌ Over-Explaining Context

Trust the artifact structure. It contains everything needed.

## Summary

| Principle | Implementation |
|-----------|----------------|
| One command | "Run the standard artifact intake..." |
| Deterministic | Same input → same processing |
| Standing contract | Not creative, not exploratory |
| Artifacts carry context | No re-explanation needed |
| Cursor synthesizes | Cross-artifact integration |
| Move, don't delete | Artifacts are records |

