---
name: strategic-governor
category: meta
version: 1.0.0
maturity: experimental
lifecycle: experimental
estimated-cost: low
typical-runtime: 1min
complexity-level: simple
requires-deep-analysis: false
scope: meta
tier: meta
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
tags:
  - meta
  - governance
  - throttle
  - escalate
  - attention
  - oversight
prerequisites:
  - file: meta/risk-tiers.md
    reason: "Defines risk tier model"
  - file: meta/governor-rules.md
    reason: "Defines throttle/escalate triggers"
execution-modes:
  - validate
  - monitor
---

# Strategic Governor

## Purpose

Prevent over-analysis and under-analysis. The governor is the system that says "no" or "more" based on the relationship between risk tier, column count, and actual findings.

**Core insight:** More columns != better analysis. The governor ensures analysis is proportional to risk and responsive to actual findings.

## When to Invoke

The strategic governor runs at three points:

1. **After column-router produces a plan** (validate mode)
   - Validate column count is appropriate for risk tier
   - Check for anti-pattern violations
   - Approve, throttle, or escalate

2. **After each column completes** (monitor mode)
   - Check if findings warrant continuing
   - Detect diminishing returns
   - Recommend stopping or adding columns

3. **Before final artifact synthesis** (final mode)
   - Validate proof requirements met
   - Check for conflicting signals
   - Approve synthesis or recommend additional analysis

## Invocation Pattern

**Validate mode (after column-router):**
```
"Validate column plan for: {risk tier} with {N} columns"
```

**Monitor mode (after column completes):**
```
"Check findings after column {N} of {total}: {finding count} findings"
```

**Final mode (before synthesis):**
```
"Final validation: {risk tier}, {column count} columns, {total findings}"
```

## Throttle Triggers (Reduce Analysis)

The governor recommends **throttling** (reducing analysis) when:

### T-001: Excessive Columns for Risk Tier

| Risk Tier | Max Columns Before Warning |
|-----------|---------------------------|
| Trivial | 1 |
| Low | 2 |
| Medium | 3 |
| High | 5 |
| Critical | No limit |

**Response:**
```yaml
governor_assessment:
  recommendation: throttle
  trigger: T-001
  reasoning: "Running 3 columns on Low risk tier is excessive"
  action: "Stop after current column unless findings warrant more"
```

### T-002: Repeated Refinement With No New Signal

**Detection:** Same findings appear across multiple columns without new information.

**Response:**
```yaml
governor_assessment:
  recommendation: throttle
  trigger: T-002
  reasoning: "Columns 2 and 3 reported same findings as column 1"
  action: "Stop - additional columns unlikely to add value"
```

### T-003: All Columns Report Zero Findings

**Detection:** Multiple columns complete with no findings.

**Response:**
```yaml
governor_assessment:
  recommendation: throttle
  trigger: T-003
  reasoning: "3 columns completed with 0 findings"
  action: "Change likely clean. Stop analysis."
  caveat: "Unless risk tier is Critical, then continue"
```

### T-004: Diminishing Returns Pattern

**Detection:** Finding count decreasing across columns.
- Column 1: 8 findings
- Column 2: 3 findings  
- Column 3: 1 finding

**Response:**
```yaml
governor_assessment:
  recommendation: throttle
  trigger: T-004
  reasoning: "Finding rate declining (8 → 3 → 1)"
  action: "Suggest stopping - diminishing returns detected"
```

## Escalate Triggers (Increase Analysis)

The governor recommends **escalation** (more analysis) when:

### E-001: Critical Findings in Low-Risk Assessment

**Detection:** High-severity finding in Trivial/Low risk tier.

**Response:**
```yaml
governor_assessment:
  recommendation: escalate
  trigger: E-001
  reasoning: "Critical finding detected in Low risk assessment"
  action: "Escalate to Medium minimum. Add correctness column."
  new_risk_tier: medium
```

### E-002: Conflicting Artifacts Between Columns

**Detection:** Two columns report contradictory findings.

**Response:**
```yaml
governor_assessment:
  recommendation: escalate
  trigger: E-002
  reasoning: "ux-adversarial and correctness report conflicting findings"
  action: "Do not synthesize. Human review required."
  halt: true
```

### E-003: Novel Failure Mode Detected

**Detection:** Finding describes failure pattern not in known patterns.

**Response:**
```yaml
governor_assessment:
  recommendation: escalate
  trigger: E-003
  reasoning: "Novel failure mode detected - not in anti-patterns"
  action: "Add failure-mode-simulator column. Consider new anti-pattern."
```

### E-004: Proof Required But Missing

**Detection:** Critical risk tier but no proofs provided.

**Response:**
```yaml
governor_assessment:
  recommendation: escalate
  trigger: E-004
  reasoning: "Critical risk tier requires proofs. None provided."
  action: "Halt synthesis until proofs available."
  halt: true
```

### E-005: Anti-Pattern Bypass Attempted

**Detection:** Anti-pattern triggered but mandatory columns skipped.

**Response:**
```yaml
governor_assessment:
  recommendation: escalate
  trigger: E-005
  reasoning: "AUTH-001 triggered but adversarial-ui column skipped"
  action: "Cannot proceed. Mandatory column required."
  halt: true
```

## Output Format

### Validate Mode Output

```yaml
governor_validation:
  mode: validate
  timestamp: 2026-01-08T12:00:00Z
  
  input:
    risk_tier: medium
    proposed_columns: 3
    failure_cost: 0.45
    anti_patterns_active: [UX-001]
  
  assessment:
    recommendation: approve | throttle | escalate
    triggers_activated: []
    reasoning:
      - "Column count appropriate for risk tier"
      - "Anti-pattern UX-001 mandatory columns included"
    
  action:
    proceed: true
    modifications: []
    
  note: "Plan approved. Proceed with 3 columns."
```

### Monitor Mode Output

```yaml
governor_monitor:
  mode: monitor
  timestamp: 2026-01-08T12:15:00Z
  
  input:
    column_completed: 2
    total_columns: 3
    findings_this_column: 2
    cumulative_findings: 7
    finding_trend: [5, 2]  # Column 1: 5, Column 2: 2
  
  assessment:
    recommendation: continue | throttle | escalate
    triggers_activated: [T-004]
    reasoning:
      - "Finding rate declining"
      - "But 2 findings still discovered"
    
  action:
    continue_to_next: true
    suggestion: "Final column may have diminishing returns"
    
  note: "Continue but monitor for zero-finding column"
```

### Final Mode Output

```yaml
governor_final:
  mode: final
  timestamp: 2026-01-08T12:30:00Z
  
  input:
    risk_tier: medium
    columns_completed: 3
    total_findings: 9
    conflicting_findings: 0
    proof_required: false
    proofs_provided: false
  
  assessment:
    recommendation: approve | reject | escalate
    triggers_activated: []
    reasoning:
      - "All columns completed"
      - "No conflicting findings"
      - "Proofs not required for medium tier"
    
  action:
    synthesis_approved: true
    human_review_required: false
    
  note: "Ready for artifact synthesis."
```

## Integration Points

### Column Router

Governor validates column-router output:
- Checks column count vs risk tier
- Verifies anti-pattern mandatory columns
- May modify plan before execution

### Artifact Synthesis

Governor approves final synthesis:
- Validates proof requirements
- Checks for conflicts
- Approves or halts

### Taste Profile

Governor uses taste profile for:
- `max_columns_before_warn` threshold
- `require_approval_for` list
- `auto_approve_for` list

### Governor Rules

Governor loads trigger definitions from `meta/governor-rules.md`.

## Behavioral Rules

### DO

- Validate proportionality (risk vs effort)
- Halt on conflicts or missing proofs
- Suggest (don't demand) throttling for low-risk
- Enforce mandatory requirements for high-risk

### DO NOT

- Override human decisions
- Automatically skip required analysis
- Ignore anti-pattern triggers
- Synthesize with unresolved conflicts

## Examples

### Example 1: Appropriate Analysis

**Input:**
- Risk: Medium
- Columns: 2
- Findings: 5 total, no conflicts

**Output:**
```yaml
governor_validation:
  recommendation: approve
  note: "Column count appropriate for Medium risk. Proceed."
```

### Example 2: Over-Analysis Detected

**Input:**
- Risk: Low
- Columns: 4 (proposed)
- No anti-patterns triggered

**Output:**
```yaml
governor_validation:
  recommendation: throttle
  trigger: T-001
  reasoning: "4 columns excessive for Low risk tier"
  action: "Reduce to 1-2 columns"
  suggestion: "Consider single correctness column instead"
```

### Example 3: Under-Analysis Detected

**Input:**
- Risk: Low (assessed)
- Columns: 1 (completed)
- Finding: Critical security issue

**Output:**
```yaml
governor_monitor:
  recommendation: escalate
  trigger: E-001
  reasoning: "Critical finding in Low risk assessment"
  action: "Escalate to High. Add adversarial-ui and failure-mode columns."
  new_risk_tier: high
```

### Example 4: Synthesis Blocked

**Input:**
- Risk: Critical
- Columns: 4 (completed)
- Proofs: None provided

**Output:**
```yaml
governor_final:
  recommendation: reject
  trigger: E-004
  reasoning: "Critical tier requires proofs. None provided."
  action: "Halt synthesis. Proofs required before proceeding."
  synthesis_approved: false
```

## Limitations

- Cannot force humans to follow recommendations
- Throttle suggestions are advisory for non-critical tiers
- Escalation enforcement only applies to documented anti-patterns
- Human can override with explicit acknowledgment

## Exit Conditions

### Success (Approve)
- Analysis proportional to risk
- Required columns executed
- Proofs provided (if required)
- No unresolved conflicts

### Success (Throttle)
- Suggested reduction accepted
- Analysis completes with fewer columns
- No critical findings emerge

### Failure (Halt)
- Conflicts detected
- Proofs missing for critical tier
- Mandatory columns skipped
- Requires human intervention

## See Also

- `meta/governor-rules.md` - Trigger definitions
- `meta/risk-tiers.md` - Risk tier model
- `skills/meta/column-router.md` - Produces plans to validate
- `meta/taste-profile.yaml` - Thresholds and preferences
- `meta/anti-patterns.md` - Mandatory requirements

