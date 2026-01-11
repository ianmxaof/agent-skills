# Artifact Structure Template

This directory contains the template for setting up the artifact directory structure in a project.

## Purpose

Artifacts are decision records produced by agent skills. They serve as the handoff boundary between:
- **Agent A** (exploration layer, raw findings production)
- **Agent B** (refinement layer, validated findings production)
- **Cursor** (artifact consumption, integration, implementation)

## Three-Tier Artifact Pipeline

The artifact system follows a three-tier pipeline model:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Three-Tier Artifact Pipeline                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Tier 1: Raw Findings          Tier 2: Refined Signal          │
│   ┌─────────────────┐          ┌─────────────────┐              │
│   │    Agent A      │          │    Agent B      │              │
│   │   (exploration) │ ──────▶  │  (refinement)   │              │
│   └────────┬────────┘          └────────┬────────┘              │
│            │                            │                        │
│            ▼                            ▼                        │
│   ┌─────────────────┐          ┌─────────────────┐              │
│   │   incoming/     │          │    refined/     │              │
│   │ confidence:     │          │ confidence:     │              │
│   │  exploratory    │          │  validated      │              │
│   └─────────────────┘          └────────┬────────┘              │
│                                         │                        │
│                          Tier 3: Implementation                  │
│                                         │                        │
│                                         ▼                        │
│                                ┌─────────────────┐              │
│                                │     Cursor      │              │
│                                │ (consumption)   │              │
│                                └────────┬────────┘              │
│                                         │                        │
│                                         ▼                        │
│                                ┌─────────────────┐              │
│                                │   processed/    │              │
│                                │ confidence:     │              │
│                                │  actionable     │              │
│                                └─────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Setup Instructions

### 1. Create Directory Structure

In your project root, create:

```
.agent-skills/artifacts/
├── incoming/      # Tier 1: Raw findings (Agent A writes)
├── refined/       # Tier 2: Refined findings (Agent B writes)
├── processed/     # Tier 3: Consumed by Cursor
├── archive/       # Historical decision records
└── .gitignore     # Git ignore rules
```

**Commands:**
```bash
mkdir -p .agent-skills/artifacts/incoming
mkdir -p .agent-skills/artifacts/refined
mkdir -p .agent-skills/artifacts/processed
mkdir -p .agent-skills/artifacts/archive
cp agent-skills/templates/artifact-structure/.gitignore .agent-skills/artifacts/
```

### 2. Configure Git Ignore

Copy the `.gitignore` template to ignore transient directories:

```bash
cp agent-skills/templates/artifact-structure/.gitignore .agent-skills/artifacts/
```

The default configuration:
- Ignores `incoming/` and `processed/` (transient)
- Ignores `refined/` (transient)
- Optionally tracks `archive/` (historical records)

### 3. Verify Setup

Your `.agent-skills/` directory should now look like:

```
.agent-skills/
├── artifacts/
│   ├── incoming/
│   ├── refined/
│   ├── processed/
│   ├── archive/
│   └── .gitignore
├── skill-map.yaml
└── README.md
```

## Directory Purposes

| Directory | Tier | Producer | Consumer | Confidence | Retention |
|-----------|------|----------|----------|------------|-----------|
| `incoming/` | 1 | Agent A | Agent B | `exploratory` | Until refined |
| `refined/` | 2 | Agent B | Cursor | `validated` | Until processed |
| `processed/` | 3 | Cursor | Human | `actionable` | 7 days default |
| `archive/` | - | Any | Any | Any | Indefinite |

## Tier Semantics

### Tier 1: Raw Findings (`incoming/`)

- **Producer:** Agent A (exploration layer)
- **Confidence:** `exploratory` — not authoritative
- **Purpose:** Maximum recall, surface everything
- **Content:** Unfiltered, potentially noisy, comprehensive

### Tier 2: Refined Findings (`refined/`)

- **Producer:** Agent B (refinement layer)
- **Confidence:** `validated` — reviewed and compressed
- **Purpose:** Maximum precision, actionable signal
- **Content:** Deduplicated, ranked, clarified

### Tier 3: Implementation (`processed/`)

- **Consumer:** Cursor
- **Confidence:** `actionable` — ready for implementation
- **Purpose:** Decision records and implementation tracking
- **Content:** What was done, what was deferred

## Important: Declarative, Not Enforced

Tier placement is **semantic**, not **policed**:

- Files may accumulate in any tier without forced movement
- No automation moves files between tiers (yet)
- Tier directories describe **intent**, not **policy**
- This defines the *map*, not the *police*

Movement automation is a future consideration after running 10-20 real columns. For now:
- Manual invocation
- Deterministic outputs
- Predictable artifacts

When running columns feels *boring*, then consider automation.

## Artifact Lifecycle

```
Agent A produces raw findings
        │
        ▼
incoming/ (artifact-type: raw-findings, confidence: exploratory)
        │
        ▼
Agent B reads and refines
        │
        ▼
refined/ (artifact-type: refined-findings, confidence: validated)
        │
        ▼
Cursor processes
        │
        ▼
processed/ (status: processed, confidence: actionable)
        │
        ▼
archive/ (status: archived)
```

## Integration with Agent Templates

- **Agent A** writes ONLY to `incoming/` (see `agent-a-instruction-template.md`)
- **Agent B** reads from `incoming/`, writes ONLY to `refined/` (see `agent-b-instruction-template.md`)
- **Cursor** reads from `refined/`, writes to `processed/`

These boundaries are constraints as documentation — they clarify intent and prevent misuse.

## See Also

- `templates/artifact-types.md` - Artifact type definitions and confidence levels
- `templates/agent-a-instruction-template.md` - Agent A invocation template
- `templates/agent-b-instruction-template.md` - Agent B invocation template
- `protocols/handoff-protocol.md` - Artifact content structure
- `skills/meta/skill-router.md` - How skills are resolved and executed

