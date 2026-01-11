# Artifact Types

This document defines the artifact types used in the three-tier artifact pipeline.

## Overview

Artifacts flow through a pipeline with increasing confidence levels:

```
exploratory → validated → actionable
```

Each tier has a specific artifact type, producer, consumer, and confidence level.

## Artifact Type Reference

| Type | Producer | Consumer | Location | Confidence |
|------|----------|----------|----------|------------|
| `raw-findings` | Agent A | Agent B | `incoming/` | `exploratory` |
| `refined-findings` | Agent B | Cursor | `refined/` | `validated` |
| `implementation-plan` | Cursor | Human | `processed/` | `actionable` |

---

## Tier 1: Raw Findings

### Type: `raw-findings`

Raw findings are the unfiltered output of exploration-layer analysis.

**Characteristics:**
- Maximum recall, potentially high noise
- Not authoritative — requires refinement
- Comprehensive, not concise
- May contain duplicates, ambiguities, and low-severity items

**Front Matter Schema:**

```yaml
---
artifact-type: raw-findings
generated-by: agent-a
skill: {skill-name}
status: unrefined
confidence: exploratory
intended-consumer: agent-b
timestamp: {ISO-8601}
finding-count: {number}
target: {target-description}
---
```

**Confidence Level: `exploratory`**

The `exploratory` confidence level signals:
- This output has NOT been reviewed or filtered
- Findings may be false positives
- Do NOT treat as authoritative
- Intended for downstream refinement only

**Location:** `.agent-skills/artifacts/incoming/`

**Naming Convention:** `{skill-name}-raw-findings-{ISO-timestamp}.md`

---

## Tier 2: Refined Findings

### Type: `refined-findings`

Refined findings are the compressed, validated output of refinement-layer analysis.

**Characteristics:**
- Maximum precision, minimal noise
- Deduplicated and ranked by severity
- Actionable recommendations
- Ready for Cursor consumption

**Front Matter Schema:**

```yaml
---
artifact-type: refined-findings
generated-by: agent-b
skill: {skill-name}
scope: core | domain | project | meta
status: new
confidence: validated
timestamp: {ISO-8601}
intended-consumer: cursor
priority: {highest-severity}
column: {column-name}
refinement-layer: generic | domain-aware | effectiveness
agent-a-coverage: {number} findings
agent-b-output: {number} findings
source-artifact: {path-to-raw-findings}
---
```

**Confidence Level: `validated`**

The `validated` confidence level signals:
- This output HAS been reviewed and filtered
- Duplicates have been merged
- Severity has been assigned
- Ready for decision-making

**Location:** `.agent-skills/artifacts/refined/`

**Naming Convention:** `{skill-name}-{ISO-timestamp}.md`

---

## Tier 3: Implementation Artifacts

### Type: `implementation-plan`

Implementation plans are the decision records produced when Cursor acts on refined findings.

**Characteristics:**
- Documents what was implemented
- Records what was deferred and why
- Links to commits or PRs where applicable
- Historical record of decisions

**Front Matter Schema:**

```yaml
---
artifact-type: implementation-plan
generated-by: cursor
skill: {skill-name}
status: processed
confidence: actionable
timestamp: {ISO-8601}
source-artifact: {path-to-refined-findings}
implementation-status: complete | partial | deferred
---
```

**Confidence Level: `actionable`**

The `actionable` confidence level signals:
- Decisions have been made
- Actions have been taken (or explicitly deferred)
- This is the final record of the column's output

**Location:** `.agent-skills/artifacts/processed/`

**Naming Convention:** `{skill-name}-impl-{ISO-timestamp}.md`

---

## Error Artifacts

### Type: `refinement-error`

Produced when Agent B cannot process Agent A's output.

```yaml
---
artifact-type: refinement-error
skill: {skill-name}
status: failed
column: {column-name}
error: artifact-not-found | validation-failed | empty-input
---
```

---

## Confidence Levels

Confidence levels prevent misinterpretation of artifact authority.

| Level | Meaning | Can be trusted for... |
|-------|---------|----------------------|
| `exploratory` | Unreviewed, high recall | Refinement input only |
| `validated` | Reviewed, deduplicated | Decision-making |
| `actionable` | Acted upon | Historical record |

**Rule:** Never treat `exploratory` artifacts as authoritative. Always refine before acting.

---

## Artifact Flow

```
┌──────────────────┐
│   Agent A        │
│   (exploration)  │
└────────┬─────────┘
         │ writes
         ▼
┌──────────────────┐
│ raw-findings     │  ← confidence: exploratory
│ incoming/        │
└────────┬─────────┘
         │ reads
         ▼
┌──────────────────┐
│   Agent B        │
│   (refinement)   │
└────────┬─────────┘
         │ writes
         ▼
┌──────────────────┐
│ refined-findings │  ← confidence: validated
│ refined/         │
└────────┬─────────┘
         │ reads
         ▼
┌──────────────────┐
│   Cursor         │
│ (implementation) │
└────────┬─────────┘
         │ writes
         ▼
┌──────────────────┐
│ implementation-  │  ← confidence: actionable
│ plan             │
│ processed/       │
└──────────────────┘
```

---

## Boundary Rules

Each agent has strict write boundaries:

| Agent | May Write To | Must NOT Write To |
|-------|--------------|-------------------|
| Agent A | `incoming/` | `refined/`, `processed/`, `archive/` |
| Agent B | `refined/` | `incoming/`, `processed/`, `archive/` |
| Cursor | `processed/`, `archive/` | `incoming/`, `refined/` |

These boundaries are documentation, not just rules — they clarify intent and prevent misuse.

---

## See Also

- `templates/artifact-structure/README.md` - Directory structure setup
- `templates/agent-a-instruction-template.md` - Agent A invocation
- `templates/agent-b-instruction-template.md` - Agent B invocation
- `protocols/handoff-protocol.md` - Artifact content structure

