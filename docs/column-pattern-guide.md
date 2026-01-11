# Column Pattern Guide

This guide explains the 2-agent column pattern for structured analysis with higher signal quality.

## What Are Columns?

A **column** is a 2-agent pipeline that produces one artifact:

```
┌─────────────────────────────────────────────────────────────────┐
│                        COLUMN PATTERN                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐   raw output    ┌─────────┐   artifact   ┌──────┐ │
│  │ Agent A │ ───────────────▶│ Agent B │ ────────────▶│Cursor│ │
│  │(explore)│   (internal)    │(refine) │  (incoming/) │      │ │
│  └─────────┘                 └─────────┘              └──────┘ │
│                                                                 │
│  Coverage        ──────▶        Signal        ──────▶ Synthesis │
│  Mess allowed                   Compression           Decisions │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key insight:** Columns create **vertical depth** (A→B) and **horizontal parallelism** (multiple columns).

## Why Columns Exist

Single-skill execution produces output of variable quality. Columns add a compression layer that:

1. **Deduplicates** overlapping findings
2. **Ranks** by severity and impact
3. **Clarifies** vague observations into actionable items
4. **Validates** against handoff protocol

**Result:** Higher signal quality at the cost of slightly more compute.

## Agent Roles

### Agent A (Exploration Layer)

**Purpose:** Maximize coverage, surface everything.

**Posture:**
- Comprehensive over concise
- Allow mess
- Don't self-censor
- Don't rank (light severity labels only)

**Output:** Raw, ephemeral (passed to Agent B, not persisted)

### Agent B (Refinement Layer)

**Purpose:** Filter and compress into one clean artifact.

**Posture:**
- Filter, not thinker
- Reduce, rank, clarify
- Enforce protocol
- Package for Cursor

**Output:** Single artifact to `artifacts/incoming/`

### Critical Rule: Agent B is a Filter

Agent B is NOT a "second opinion" or "additional analysis." Agent B is a **filter**.

| Agent B Should | Agent B Should NOT |
|----------------|---------------------|
| Deduplicate | Add new findings |
| Rank by severity | Explore new areas |
| Clarify language | Speculate beyond evidence |
| Enforce structure | Argue with Agent A |

If Agent B acts as a second thinker, you get:
- Conflicting signals
- Argument instead of compression
- Two artifacts instead of one

## Column Patterns

### Pattern 1: Same Skill, Two Passes

Agent A runs a skill in exploratory mode. Agent B uses generic refinement.

**Example:**
```
Agent A: adversarial-ui-tester (exploratory)
Agent B: refinement-layer (generic mode)
```

**Best for:** Most cases. When skill output is good but messy.

### Pattern 2: Skill → Meta-Skill Pairing

Agent A runs a domain skill. Agent B uses a related meta-skill as refinement lens.

**Example:**
```
Agent A: architecture-review
Agent B: architectural-drift-detector (as lens)
```

**Best for:** When domain-specific filtering adds value.

### Pattern 3: Router → Skill → Validator

Agent A routes intent and executes. Agent B validates contract.

**Example:**
```
Agent A: skill-router → adversarial-ui-tester
Agent B: handoff-quality-validator
```

**Best for:** When quality assurance on the artifact itself is needed.

## Starter Column Configurations

### Example 4-Column Setup

| Column | Agent A Skill | Agent B Mode | Purpose |
|--------|--------------|--------------|---------|
| UX/Adversarial | adversarial-ui-tester | generic refinement | Surface UX failure modes |
| Architecture | architecture-review | architectural-drift-detector | Find structural issues |
| Performance | performance-budget-guardian | bundle-size-analyzer | Catch perf regressions |
| Correctness/Safety | failure-mode-simulator | handoff-quality-validator | Validate resilience |

This produces **4 artifacts** for Cursor to synthesize.

### Recommended Starting Point

Start with 2-4 columns. Add more only if:
- You're consistently missing issues
- Coverage gaps are documented
- You have bandwidth to process more artifacts

## Column Invocation

### Pattern

```
"Run {column-name} column on {target}"
```

### Examples

```
"Run UX/Adversarial column on the checkout flow"
"Run Architecture column on the backend module"
"Run all configured columns on the auth service"
```

### Invocation Behavior

1. Agent A executes skill in exploratory posture
2. Agent A output passed to Agent B (internal handoff)
3. Agent B refines and writes artifact
4. Artifact appears in `incoming/` with `column: <column-name>` in front matter

## When to Use Columns vs Single Skills

### Use Single Skill When

- Quick check on known area
- Low-stakes review
- Time-constrained
- You trust the skill's default output

### Use Columns When

- High-stakes changes (production, privacy, security)
- Complex domain with many edge cases
- You want higher signal quality
- Pre-release audit
- You've been burned by false negatives before

### Rule of Thumb

> If you'd ask a second person to review, use a column.

## Column Orchestration

### Parallel Execution

Columns run **in parallel** (conceptually). They don't depend on each other.

**Execution options:**

1. **Manual parallel:** Open multiple Warp windows, run one column each
2. **Sequential:** Run columns one at a time in same window
3. **Batch command (future):** "Run all columns on {target}"

### Cursor Processing

Cursor processes **all artifacts together**, regardless of execution order.

### Exception: Dependent Analysis

If you need column B to see column A's output, that's a **skill chain**, not columns.

Use `skill-chains/` for sequential dependencies.

## Column Artifacts

### Front Matter

Column artifacts include additional metadata:

```yaml
---
skill: adversarial-ui-tester
scope: core
status: new
timestamp: 2026-01-07T20:00:00Z
intended-consumer: cursor
priority: high
column: ux-adversarial           # Column identifier
refinement-layer: generic        # Agent B mode
agent-a-coverage: 15 findings    # Pre-refinement count
agent-b-output: 6 findings       # Post-refinement count
---
```

### Naming

Same as single-skill artifacts:

```
{skill-name}-{ISO-timestamp}.md
```

The `column:` field in front matter distinguishes column artifacts.

## Guardrails (What NOT to Do)

### ❌ Let Both A and B Write Artifacts

Only Agent B writes artifacts. Agent A output is ephemeral.

**Why:** Defeats compression. You'd get two artifacts instead of one high-quality artifact.

### ❌ Let A Invent New Skills

Agent A executes the loaded skill only.

**Why:** Skill definitions are the source of truth. Ad-hoc behavior causes drift.

### ❌ Let B "Re-Explore" Instead of Pruning

Agent B filters Agent A's output. It does not do its own exploration.

**Why:** That's what Agent A is for. Re-exploration defeats the pipeline purpose.

### ❌ Run 16 Agents With No Column Structure

More agents ≠ better output.

**Why:** Coordination cost beats signal after ~8 columns (16 agents).

### ❌ Make Agent B a "Second Thinker"

Agent B is a filter. It does not generate new analysis.

**Why:** Two thinkers cause argument. One explorer + one filter causes compression.

### ❌ Run Columns Without Processing Previous Artifacts

Clear the inbox before running new columns.

**Why:** Creates backlog. Findings get stale. Synthesis becomes overwhelming.

### ❌ Skip Agent B to "Save Time"

Agent B is the value-add of the column pattern.

**Why:** Without compression, you're just running a single skill with extra steps.

### ❌ Have Agent B Add Findings Agent A Didn't Surface

If Agent B is finding new issues, it's exploring, not refining.

**Why:** Violates role separation. Run a different skill if coverage is incomplete.

## Scaling Limits

### Why ~16 Agents (8 Columns) Is the Practical Limit

| Factor | Impact at Scale |
|--------|-----------------|
| Human attention | You can only read so many artifacts |
| Synthesis bottleneck | Cursor integrates everything |
| Diminishing returns | Redundancy increases fast |
| Coordination cost | Overhead beats signal |

### Recommendation

- **Start with:** 2-4 columns
- **Maximum practical:** 8 columns
- **Beyond 8:** Reconsider scope or target decomposition

## Failure Modes

### Agent A Produces Nothing

**What happens:** Agent B reports "no findings" artifact with explanation.

**Not a failure:** Absence of signal is signal. Target may be clean.

### Agent A Produces Low-Quality Output

**What happens:** Agent B still refines (that's its job).

**If unusable:** Agent B emits "refinement-failed" artifact. Cursor decides re-run.

### Confidence Threshold Not Met

**What happens:** Agent A still produces raw output. Agent B notes low confidence.

**Cursor decides:** Whether to act on low-confidence findings.

### Column Timeout

**What happens:** Partial artifacts are acceptable.

**Mark artifact:** `status: partial`

**Document:** What was completed before timeout.

## Cross-Column Deduplication

### Rule

Deduplication happens at **Cursor synthesis**, not within columns.

### Why

Each column has limited context. Only Cursor sees all artifacts.

### Cursor Behavior

| Scenario | Cursor Action |
|----------|---------------|
| Multiple columns find same issue | Note convergence (higher confidence) |
| Columns conflict | Note disagreement (flag for human) |
| Unique findings | Process normally |

### Never Silently Drop

Cursor should never silently drop findings. If deduplicated, note the merge.

## Governance Integration

### Column Router

Before running columns, the **column-router** determines:
- How many columns are appropriate for the risk tier
- Which columns are mandatory (based on anti-patterns)
- What refinement strictness to use

**Invocation:**
```
"Assess risk and plan columns for: {change description}"
```

**Output:** Column plan with recommended and mandatory columns.

See `skills/meta/column-router.md` for details.

### Strategic Governor

During and after column execution, the **strategic-governor** validates:
- Column count is appropriate for risk tier (throttle if excessive)
- Mandatory columns are executed (escalate if missing)
- Proofs are provided for critical tiers
- Conflicts are resolved before synthesis

**Invocation Points:**
1. After column-router produces plan (validate)
2. After each column completes (monitor)
3. Before artifact synthesis (final approval)

**Governor Actions:**
- **Approve:** Proceed as planned
- **Throttle:** Suggest fewer columns (advisory)
- **Escalate:** Add columns or increase strictness (mandatory for high-risk)
- **Halt:** Stop and require human intervention (conflicts, missing proofs)

See `skills/meta/strategic-governor.md` and `meta/governor-rules.md` for details.

### Taste Profile Integration

Column behavior is influenced by `meta/taste-profile.yaml`:
- Column preferences by change type (always include, rarely needed)
- Skill biases for specific surfaces
- Refinement strictness defaults
- Maximum columns before warning

### Anti-Pattern Enforcement

`meta/anti-patterns.md` defines mandatory columns:
- AUTH-001: Auth changes require 4 columns minimum
- PAY-001: Payment changes require proofs
- UX-001: Checkout changes require adversarial-ui

The governor enforces these requirements.

### Governed Column Flow

```
┌───────────────┐
│ Intent        │
└───────┬───────┘
        ▼
┌───────────────┐
│ Column Router │  ──── Risk assessment
└───────┬───────┘  ──── Column plan
        ▼
┌───────────────┐
│ Governor      │  ──── Validate plan
│ (validate)    │
└───────┬───────┘
        ▼
┌───────────────┐
│ Column 1      │
│ (A→B)         │
└───────┬───────┘
        ▼
┌───────────────┐
│ Governor      │  ──── Check findings
│ (monitor)     │  ──── Throttle or escalate
└───────┬───────┘
        ▼
       ...        (repeat for each column)
        ▼
┌───────────────┐
│ Governor      │  ──── Final validation
│ (final)       │  ──── Approve synthesis
└───────┬───────┘
        ▼
┌───────────────┐
│ Cursor        │  ──── Synthesize artifacts
│ Synthesis     │
└───────────────┘
```

## Integration Points

- `skills/meta/refinement-layer.md` - Agent B meta-skill
- `skills/meta/column-router.md` - Column planning
- `skills/meta/strategic-governor.md` - Governance oversight
- `meta/governor-rules.md` - Throttle/escalate rules
- `meta/taste-profile.yaml` - Column preferences
- `meta/anti-patterns.md` - Mandatory requirements
- `templates/agent-a-instruction-template.md` - Agent A instructions
- `templates/agent-b-instruction-template.md` - Agent B instructions
- `templates/column-configuration-template.yaml` - Column config
- `docs/cursor-intake-protocol.md` - How Cursor processes artifacts
- `meta/artifact-policy.md` - Artifact lifecycle

## See Also

- `docs/column-examples.md` - Full worked examples
- `docs/warp-integration-guide.md` - Warp execution details
- `docs/agent-invocation-guide.md` - Cursor processing
- `docs/self-improvement-mechanism.md` - How columns improve over time

