# Warp Integration Guide

This guide explains how Warp agents interact with the agent-skills system to execute skills and produce handoff artifacts.

## Mental Model

**Warp is a bounded execution engine for skills.**

It is:
- An executor, not a thinker
- Deterministic, not creative
- Constrained by skill definitions

It is NOT:
- A planner or designer
- A freestyle problem solver
- A replacement for Cursor's synthesis role

## Two Invocation Modes

### Mode A: Direct Skill Invocation

**When to use:** You know exactly which skill you want.

**Pattern:**
```
"Assume the {skill-name} skill and {action} on {target}"
```

**Examples:**
```
"Assume the adversarial-ui-tester skill and analyze the checkout flow"
"Assume the privacy-tier-auditor skill and audit the recall service"
"Assume the architecture-review skill and review the backend module"
```

**Behavior:**
1. Warp verifies skill exists in `.agent-skills/skill-map.yaml`
2. Loads skill definition directly
3. Executes exactly as specified
4. Emits handoff artifact per protocol

**When to prefer Mode A:**
- Repeated, known workflows
- CI-like automated checks
- When you've run this skill before

### Mode B: Intent-Based Resolution

**When to use:** You describe what you want, let the system find the right skill.

**Pattern:**
```
"Resolve and execute the appropriate skill for: {intent}"
```

**Examples:**
```
"Resolve and execute the appropriate skill for: finding UX weaknesses in the onboarding flow"
"Resolve and execute the appropriate skill for: checking if our error handling is robust"
"Resolve and execute the appropriate skill for: analyzing bundle size impact of new dependencies"
```

**Behavior:**
1. Warp invokes skill-router meta-skill
2. skill-router resolves intent to appropriate skill
3. Emits resolution trace
4. Delegates to selected skill
5. Skill emits handoff artifact

**When to prefer Mode B:**
- Exploring the skill library
- Unsure which skill applies
- Natural language workflows

## Router Mode Flag

When using Mode B, you can specify a mode:

### strict (default)

```
"Resolve and execute the appropriate skill for: {intent}"
```

- If confidence < 0.7: **STOP immediately**
- Reports ambiguity
- Suggests top 2 candidates
- Does NOT execute

### assistive

```
"Resolve and execute (assistive mode) the appropriate skill for: {intent}"
```

- If confidence < 0.7: **Suggests + asks confirmation**
- Shows top candidates with scores
- Executes only after you confirm

**When to use assistive mode:**
- Exploring unfamiliar skills
- Learning the tag taxonomy
- When you're okay with suggestions

## Resolution Trace Format

Every routing decision emits a decision receipt:

```yaml
resolution:
  selected-skill: adversarial-ui-tester
  confidence: 0.82
  mode: strict
  top-candidates:
    - skill: adversarial-ui-tester
      score: 0.82
    - skill: ux-copy-neutrality-checker
      score: 0.61
  match-signals:
    - tags: ["ui", "adversarial", "ux"]
    - surface: "onboarding flow"
    - outcome: "find/analyze"
```

**How to use resolution traces:**
- Debug why a skill was (or wasn't) chosen
- Tune skill tags for better matching
- Feed into skill-effectiveness-analyzer

## The Decoupling Principle

**Critical concept:** Skills produce output. Execution layer handles persistence.

Skills:
- Produce structured content
- Follow handoff-protocol.md
- Don't "know" where artifacts go

Execution layer (Warp):
- Receives skill output
- Writes to filesystem
- Manages artifact lifecycle

**Why this matters:**
- Skills remain portable
- Persistence can change without updating skills
- Testing is easier (no side effects)

## Writing Artifacts to Filesystem

When a skill completes, Warp's execution layer writes the artifact:

```bash
# Create artifact directory if needed
mkdir -p .agent-skills/artifacts/incoming

# Write artifact with proper naming
cat << 'EOF' > .agent-skills/artifacts/incoming/adversarial-ui-tester-2026-01-07T19-42-00Z.md
---
skill: adversarial-ui-tester
scope: core
status: new
timestamp: 2026-01-07T19:42:00Z
intended-consumer: cursor
priority: high
execution-mode: targeted
target: "checkout flow"
---

## Summary
- Found 5 adversarial UX failure modes
- 2 critical, 2 high, 1 medium priority
...

## Detailed Findings
...

## Recommendations
...
EOF

echo "Artifact written: adversarial-ui-tester-2026-01-07T19-42-00Z.md"
```

### Artifact Naming Convention

```
{skill-name}-{ISO-timestamp}.md
```

- Use skill name exactly as in front matter
- ISO 8601 timestamp in UTC
- Replace colons with hyphens
- Always `.md` extension

### Artifact Front Matter (Required)

```yaml
---
skill: skill-name
scope: core | domain | project
status: new
timestamp: 2026-01-07T19:42:00Z
intended-consumer: cursor
priority: critical | high | medium | low
---
```

## Error Handling

### Confidence < 0.7 (Strict Mode)

**What Warp does:**
1. STOP - do not execute any skill
2. Report the ambiguity clearly
3. Show top 2 candidates with scores
4. Suggest clarification or specific skill name

**Example output:**
```
Could not resolve intent with sufficient confidence (0.45).

Top candidates:
- architecture-review (0.45)
- test-coverage-gap-finder (0.42)

Please clarify what aspect you want to analyze, or name a specific skill:
- "Assume architecture-review skill..."
- "Resolve and execute (assistive mode)..."
```

### Skill Not in Skill Map

**What Warp does:**
1. Report skill not available
2. Suggest checking skill-map.yaml
3. List similar available skills if any

### Skill Execution Fails

**What Warp does:**
1. Report the failure
2. Emit partial artifact if possible
3. Suggest skill-gap-detector if skill seems inadequate

## Multi-Artifact Runs

Some intents produce multiple artifacts:

```
.agent-skills/artifacts/incoming/
├── skill-router-2026-01-07T19-40-00Z.md          # Resolution trace
├── adversarial-ui-tester-2026-01-07T19-42-00Z.md  # Main analysis
└── skill-gap-detector-2026-01-07T19-45-00Z.md     # If gaps found
```

Each artifact is independent and follows the same format.

## Standard Workflow

### 1. Issue Intent

```
"Resolve and execute the appropriate skill for: finding adversarial UX 
failure modes in the checkout flow"
```

### 2. Warp Resolves (skill-router)

```yaml
resolution:
  selected-skill: adversarial-ui-tester
  confidence: 0.85
  mode: strict
  ...
```

### 3. Warp Executes (adversarial-ui-tester)

Skill runs analysis per its behavioral rules.

### 4. Warp Writes Artifact

```
Artifact written: adversarial-ui-tester-2026-01-07T19-42-00Z.md
```

### 5. Handoff Complete

Artifact is in `artifacts/incoming/`, ready for Cursor.

## What to Stop Doing

Now that you have this system:

| Old Pattern | New Pattern |
|-------------|-------------|
| Copy-paste raw prompts | Use skill definitions |
| Let agents invent roles | Constrain to skill-map |
| Copy chat logs to Cursor | Use structured artifacts |
| Be the router yourself | Let skill-router decide |
| Explain context repeatedly | Context is in artifacts |

## Integration Points

- **skill-map.yaml**: Authoritative list of available skills
- **skill-router.md**: Default entrypoint for Mode B
- **handoff-protocol.md**: Structure of artifact content
- **artifact-policy.md**: Lifecycle and handling rules
- **skill-gap-detector.md**: When no skill matches

## Troubleshooting

### "Skill not found"
- Check `.agent-skills/skill-map.yaml`
- Verify skill name spelling
- Ensure skill is in correct scope list

### "Low confidence" repeatedly
- Check skill tags in front matter
- Use assistive mode to see candidates
- Consider adding tags or new skill

### "Artifact not written"
- Verify `artifacts/incoming/` exists
- Check filesystem permissions
- Look for execution layer errors

## Column Pattern Usage

Columns provide higher signal quality through a 2-agent pipeline: Agent A (exploration) → Agent B (refinement).

### When to Use Columns

| Use Columns | Use Single Skills |
|-------------|-------------------|
| High-stakes changes | Quick checks |
| Complex domains | Low-stakes review |
| Pre-release audits | Time-constrained |
| When burned by false negatives | When you trust skill output |

**Rule of thumb:** If you'd ask a second person to review, use a column.

### Invoking a Column

**Pattern:**
```
"Run {column-name} column on {target}"
```

**Examples:**
```
"Run UX/Adversarial column on the checkout flow"
"Run Architecture column on the backend module"
"Run all configured columns on the auth service"
```

### Column Execution Flow

```
1. You invoke column
       │
       v
2. Agent A (exploration) runs skill
       │
       │ raw output (internal, NOT persisted)
       v
3. Agent B (refinement) receives output
       │
       │ deduplicates, ranks, clarifies
       v
4. Agent B writes single artifact
       │
       v
5. Artifact in artifacts/incoming/
```

### Agent A vs Agent B in Warp

**Agent A invocation:**
```
"You are Agent A (Exploration Layer). 
Load `adversarial-ui-tester` and analyze the checkout flow. 
Maximize coverage. Allow mess. Do not write artifacts."
```

Agent A should:
- Surface everything
- Allow duplicates
- Not rank by importance
- Pass raw output to Agent B

**Agent B invocation:**
```
"You are Agent B (Refinement Layer). 
Here is the raw output from Agent A: [output]. 
Reduce, rank, clarify, and produce one Cursor-ready artifact."
```

Agent B should:
- Deduplicate
- Rank by severity
- Clarify for actionability
- Write ONE artifact to `incoming/`

### Column Artifact Front Matter

Column artifacts include additional fields:

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
agent-a-coverage: 15 findings    # Before compression
agent-b-output: 6 findings       # After compression
---
```

### Multiple Columns

Run multiple columns for comprehensive review:

```
"Run all configured columns on {target}"
```

This produces multiple artifacts:

```
artifacts/incoming/
├── adversarial-ui-tester-2026-01-07T20-00-00Z.md    (column: ux-adversarial)
├── architecture-review-2026-01-07T20-05-00Z.md      (column: architecture)
├── performance-budget-guardian-2026-01-07T20-10-00Z.md (column: performance)
└── failure-mode-simulator-2026-01-07T20-15-00Z.md   (column: correctness)
```

Cursor synthesizes all artifacts together during intake.

### Starter Column Configurations

| Column | Agent A | Agent B Mode |
|--------|---------|--------------|
| UX/Adversarial | adversarial-ui-tester | generic |
| Architecture | architecture-review | domain-aware (drift-detector) |
| Performance | performance-budget-guardian | domain-aware (bundle-analyzer) |
| Correctness | failure-mode-simulator | generic |

### Column Templates

Use these templates for consistent invocation:
- `templates/agent-a-instruction-template.md`
- `templates/agent-b-instruction-template.md`
- `templates/column-configuration-template.yaml`

### Guardrails

**What NOT to do with columns:**

| ❌ Anti-Pattern | Why |
|-----------------|-----|
| Both agents write artifacts | Defeats compression |
| Agent A invents new skills | Causes drift |
| Agent B re-explores | Not its job |
| Skip Agent B | Defeats the purpose |
| Run 16+ agents without structure | Coordination cost > signal |

See `docs/column-pattern-guide.md` for complete documentation.

---

## Risk Assessment Workflow (Governance)

Before running columns, use the column-router to plan appropriate analysis depth.

### When to Use Risk Assessment

- Starting a new integration task
- Unsure how much analysis is warranted
- Want to avoid both over-analysis and under-analysis

### Invocation Pattern

```
"Assess risk and plan columns for: {change description}"
```

**Examples:**
```
"Assess risk and plan columns for: refactoring checkout validation"
"Assess risk and plan columns for: implementing Stripe payment integration"
"Assess risk and plan columns for: adding toast notifications"
```

### Column Router Output

```yaml
column_router_assessment:
  timestamp: 2026-01-08T12:00:00Z
  change_summary: "Refactoring checkout validation"
  
risk_assessment:
  tier: medium
  failure_cost:
    score: 0.50
    level: medium-high
    highest_concern: trust_impact
  reasoning:
    - "User-facing checkout change"
    - "Feature-flagged for rollback"
    - "Known pattern: checkout-form-v1"

column_plan:
  recommended_columns:
    - name: ux-adversarial
      reason: "User-facing checkout change"
    - name: correctness
      reason: "Functional behavior change"
  refinement_strictness: normal
  proof_required: false

anti_patterns_triggered:
  - pattern_id: UX-001
    action_taken: "Added adversarial-ui to mandatory columns"

governor_note: "Medium risk - 2-3 columns appropriate."
```

### Risk Tiers

| Tier | Columns | Refinement | Use When |
|------|---------|------------|----------|
| Trivial | 0 | None | Config, copy, styling |
| Low | 1 | Light | Reversible, bounded |
| Medium | 2-3 | Normal | Functional changes |
| High | 4 | Strict | Irreversible, sensitive |
| Critical | 4+ | Strict + Proofs | Payment, auth, data |

### Governor Validation

After receiving the column plan, the strategic-governor validates:

**Throttle (reduce):**
- Excessive columns for risk tier
- Repeated refinement with no new signal
- All columns report zero findings

**Escalate (increase):**
- Critical findings in low-risk assessment
- Anti-pattern bypass attempted
- Novel failure mode detected

### Full Governed Workflow

```bash
# 1. Assess risk and get column plan
warp> "Assess risk and plan columns for: refactoring checkout validation"

# 2. Governor validates the plan
# (Happens automatically in column-router output)

# 3. Execute approved columns
warp> "Run UX/Adversarial column on checkout flow"
warp> "Run Correctness column on checkout flow"

# 4. Governor monitors after each column
# (Suggests throttle/escalate based on findings)

# 5. Governor approves final synthesis
# (Validates all requirements met)

# 6. Cursor processes artifacts
cursor> "Run the standard artifact intake and integration pass"
```

### Failure-Cost Assessment (Optional)

For complex changes, include failure-cost assessment:

```
"Assess risk for: implementing Stripe payment integration
Surfaces: payment, ui, api
Reversibility: feature-flag"
```

This provides more detailed cost analysis:
- **Blast Radius:** How much breaks if this fails?
- **Detectability:** Will failure be obvious?
- **Reversibility:** Can we roll back cleanly?
- **Trust Impact:** Does this affect user confidence?

See `meta/failure-cost-model.md` for detailed axis definitions.

---

## See Also

- `skills/meta/skill-router.md` - Full routing algorithm
- `skills/meta/refinement-layer.md` - Agent B meta-skill
- `skills/meta/column-router.md` - Column planning and risk assessment
- `skills/meta/strategic-governor.md` - Governance oversight
- `meta/risk-tiers.md` - Risk tier definitions
- `meta/failure-cost-model.md` - Cost axis assessment
- `meta/governor-rules.md` - Throttle/escalate triggers
- `meta/taste-profile.yaml` - Preferences and biases
- `meta/anti-patterns.md` - Learned regrets and mandatory requirements
- `meta/artifact-policy.md` - Artifact lifecycle
- `protocols/handoff-protocol.md` - Artifact content structure
- `docs/agent-invocation-guide.md` - Cursor processing guide
- `docs/column-pattern-guide.md` - Column pattern details
- `docs/column-examples.md` - Worked examples
- `docs/cursor-intake-protocol.md` - Cursor intake command

