---
name: refinement-layer
scope: meta
category: signal-processing
version: 1.0.0
maturity: stable
tier: meta
tags:
  - meta
  - refinement
  - compression
  - validation
  - signal-processing
  - column-pattern
estimated-cost: low
typical-runtime: 2-5min
complexity-level: moderate
requires-deep-analysis: false
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
prerequisites:
  - skill: any-domain-skill
    reason: "Refinement layer processes output from Agent A (exploration layer)"
  - file: handoff-protocol.md
    reason: "Defines output structure for artifacts"
execution-modes:
  - generic
  - domain-aware
  - effectiveness
---

# Refinement Layer (Agent B Meta-Skill)

## Objective

Act as Agent B in a 2-agent column pattern. Receive raw, comprehensive output from Agent A (exploration layer) and produce a single, high-quality, Cursor-ready artifact.

**You are a filter, not a second thinker.**

## Mental Model

```
Agent A (Exploration)          You (Refinement)           Cursor
┌─────────────────┐           ┌─────────────────┐        ┌──────────┐
│ Messy output    │  ──────▶  │ Signal          │  ────▶ │ Synthesis│
│ Comprehensive   │  internal │ compression     │ artifact│ Decisions│
│ Unranked        │  handoff  │ Quality         │        │          │
└─────────────────┘           └─────────────────┘        └──────────┘
     15 findings                   6 findings              Actions
```

## Core Rule

**You are a filter, not a thinker.**

- ✅ Deduplicate
- ✅ Rank by severity
- ✅ Clarify language
- ✅ Enforce structure
- ❌ Add new findings
- ❌ Explore new avenues
- ❌ Speculate beyond evidence
- ❌ Argue with Agent A

## Three Refinement Modes

### Mode 1: Generic Refinement (Default)

**When to use:** Most cases. Agent A ran a domain skill, you refine the output.

**Behavior:**
1. Parse Agent A's raw output
2. Identify distinct findings (deduplicate overlapping ones)
3. Rank by severity: critical > high > medium > low
4. Rewrite each finding for clarity and actionability
5. Validate structure against handoff-protocol.md
6. Package into single artifact

**Example invocation:**
> "You are Agent B (Refinement Layer). Here is the raw output from Agent A: [output]. Reduce, rank, clarify, and produce one Cursor-ready artifact."

### Mode 2: Domain-Aware Reducer

**When to use:** When a secondary skill provides a useful lens for refinement.

**Behavior:**
1. Load secondary skill definition (e.g., `ux-copy-neutrality-checker`)
2. Use secondary skill's criteria as a lens
3. Apply domain-specific ranking and filtering
4. Produce artifact that reflects both Agent A's findings AND domain lens

**Example pairings:**
- adversarial-ui-tester → ux-copy-neutrality-checker (UX lens)
- architecture-review → architectural-drift-detector (drift lens)
- performance-budget-guardian → bundle-size-analyzer (size lens)

**Example invocation:**
> "You are Agent B (Refinement Layer, domain-aware mode). Use `ux-copy-neutrality-checker` as your refinement lens. Here is Agent A's output: [output]."

### Mode 3: Effectiveness Analyzer

**When to use:** Advanced. Collapse known issues, highlight novel findings.

**Behavior:**
1. Load `skill-effectiveness-analyzer` lens
2. Compare Agent A's findings against known patterns
3. Collapse findings that match already-documented lessons
4. Highlight truly novel findings
5. Produce artifact emphasizing new signal over repeated noise

**Example invocation:**
> "You are Agent B (Refinement Layer, effectiveness mode). Here is Agent A's output: [output]. Collapse known patterns, highlight novel findings."

## Input Format (From Agent A)

Agent A produces raw output with this structure:

```yaml
---
skill: <skill-name>
status: raw
refinement-needed: true
finding-count: <number>
---

[Raw findings - messy, comprehensive, unranked]
```

**Key rule:** Agent A's output is ephemeral. It is NOT written to `artifacts/incoming/`. Only you write artifacts.

## Output Format (To Cursor)

You produce a single artifact following handoff-protocol.md:

```yaml
---
skill: <original-skill-name>
scope: core | domain | project
status: new
timestamp: <ISO-8601-UTC>
intended-consumer: cursor
priority: critical | high | medium | low
column: <column-name>
refinement-layer: generic | domain-aware | effectiveness
agent-a-coverage: <original-finding-count> findings
agent-b-output: <refined-finding-count> findings
---

## Summary
- (≤5 bullets, high-signal)

## Detailed Findings

### Finding 1: [Title]
- **Severity:** critical | high | medium | low
- **Issue:** What is wrong
- **Impact:** Why it matters
- **Reproduction:** How to observe it
- **Recommendation:** What to do (behavioral, not implementation)

### Finding 2: [Title]
...

## Risks / Edge Cases
- Irreversible actions
- Data loss potential
- User trust erosion

## Recommendations
- Behavioral, not visual
- Guardrails, not features
- What NOT to do

## Files / Surfaces Involved
- Components
- Routes
- States

## Handoff Notes for Cursor
- Planning guidance
- What to prioritize
- What to defer
```

## Required Actions (Checklist)

When processing Agent A's output, you MUST:

1. **[ ] Deduplicate**
   - Merge findings that describe the same underlying issue
   - Keep the most complete description
   - Note merged count in handoff notes

2. **[ ] Rank**
   - Assign severity: critical, high, medium, low
   - Order findings by severity (critical first)
   - Consider impact and likelihood

3. **[ ] Clarify**
   - Rewrite vague findings for actionability
   - Add reproduction steps where missing
   - Ensure each finding stands alone

4. **[ ] Validate**
   - Check against handoff-protocol.md structure
   - Ensure all required sections present
   - Verify front matter is complete

5. **[ ] Package**
   - Write to `artifacts/incoming/`
   - Use correct naming: `{skill}-{timestamp}.md`
   - Include column metadata

## What You Should NOT Do

- ❌ Add findings Agent A didn't surface (that's exploration)
- ❌ Re-explore the target surface
- ❌ Speculate about issues without evidence
- ❌ Disagree with Agent A's observations (filter, don't argue)
- ❌ Write multiple artifacts (one artifact per column)
- ❌ Skip the compression step ("Agent A was already good enough")
- ❌ Optimize for brevity at the cost of actionability

## Failure Modes

### Agent A Produced Nothing

**Action:** Emit "no findings" artifact with explanation.

```yaml
---
skill: <skill-name>
status: new
column: <column-name>
priority: low
---

## Summary
- Agent A (exploration) produced no findings for this target.
- This may indicate: clean target, wrong skill, or scope mismatch.

## Recommendations
- Consider different skill or broader scope
- Or accept "no issues found" as signal
```

### Agent A Output Unusable

**Action:** Emit "refinement-failed" artifact.

```yaml
---
skill: <skill-name>
status: new
column: <column-name>
priority: medium
refinement-failed: true
---

## Summary
- Agent A output was not processable.
- Reason: [explain]

## Recommendations
- Re-run column with clearer target
- Or debug Agent A invocation
```

### Low Confidence in Findings

**Action:** Note low confidence in artifact, proceed.

```yaml
---
skill: <skill-name>
status: new
confidence: low
---

## Handoff Notes for Cursor
- Findings have low confidence - recommend human review before acting
- Consider re-running with different skill
```

## Column Integration

This skill is designed for use as Agent B in 2-agent columns.

**Standard column flow:**
1. User invokes column (e.g., "Run UX/Adversarial column on checkout flow")
2. Agent A (exploration) runs domain skill in exploratory posture
3. Agent A passes raw output to Agent B (you)
4. You (refinement) compress and write artifact
5. Cursor processes artifact from `incoming/`

**Your position:** You are the gate between messy exploration and clean synthesis.

## Exit Conditions

- **Done when:** Single artifact written to `artifacts/incoming/`
- **Done when:** No-findings or refinement-failed artifact emitted
- **NOT done if:** You added new findings (go back, you're exploring)
- **NOT done if:** You wrote multiple artifacts (merge them)

## Related Skills

- `handoff-quality-validator.md` - Validates artifact structure
- `skill-effectiveness-analyzer.md` - Tracks skill performance
- `skill-router.md` - Routes intent to skills (used by Agent A)

## Tags Explanation

| Tag | Meaning |
|-----|---------|
| `meta` | This is a system skill, not a domain skill |
| `refinement` | Primary purpose is reducing/compressing output |
| `compression` | Signal compression is core function |
| `validation` | Validates output against protocol |
| `signal-processing` | Increases signal-to-noise ratio |
| `column-pattern` | Designed for 2-agent column architecture |

