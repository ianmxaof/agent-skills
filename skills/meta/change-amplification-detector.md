---
name: change-amplification-detector
category: meta
version: 1.0.0
maturity: draft
lifecycle: experimental
estimated-cost: low
typical-runtime: 1-3min
complexity-level: moderate
requires-deep-analysis: false
scope: meta
tier: 2
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
tags:
  - meta
  - change-impact
  - amplification
  - risk-detection
  - governance
  - cascade
prerequisites: []
execution-modes:
  - change-analysis
  - pre-change
---

# Change Amplification Detector

## Purpose

Identify when a numerically small change has disproportionate downstream impact. A 2-line change to a schema might affect 30 skills—this skill surfaces that amplification before it becomes a problem.

**Core insight:** Not all changes are equal. A single line in `TEMPLATE.md` propagates to every future skill. A one-field addition to `risk-tiers.md` affects every column-router decision. The amplification detector ensures these high-leverage changes get proportionate scrutiny.

## Scope and Classification

**Scope:** `meta`

This is a governance skill that informs risk assessment.

**Tier:** `2` (System Health)

Amplification detection prevents cascading failures and ensures appropriate review depth.

**Lifecycle Stage:** `experimental`

New skill that needs real-world validation.

## When to Invoke

### Explicit Trigger Phrases

- "Check amplification for this change"
- "What's the impact of changing [file]?"
- "Is this a high-leverage change?"
- "Analyze change cascade"

### Situational Triggers

- Before modifying files in `meta/`
- Before modifying `TEMPLATE.md`
- Before modifying protocols
- When column-router plans seem insufficient for change
- When change touches shared infrastructure

### Do NOT Invoke When

- Change is isolated (single component, no dependencies)
- Change is documentation-only (no behavioral impact)
- Already know the change is high-risk (use appropriate depth)

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet
- **Multi-Model**: Off

## Behavioral Rules

### How the Model Should Reason

1. **Analyze change location** - Where in the system is the change?
2. **Map dependencies** - What depends on the changed file?
3. **Calculate amplification** - Impact scope ÷ change size
4. **Assess risk escalation** - Should risk tier increase?
5. **Recommend scrutiny level** - What analysis is appropriate?

### What It Must Avoid

- Treating all changes as high-amplification
- Missing transitive dependencies
- Ignoring cascade effects
- Over-estimating isolated changes

### What It Must Prioritize

- Governance file changes (meta/, protocols/)
- Template changes (affect future creations)
- Schema changes (affect parsers and validators)
- Shared utility changes (affect many consumers)

## Amplification Model

### Amplification Score

```yaml
amplification_formula:
  amplification_score = downstream_impact / change_size
  
  where:
    change_size: 
      - lines_changed
      - files_modified
      - normalized to 0.0-1.0 scale
      
    downstream_impact:
      - direct_dependents: Files that import/reference changed file
      - transitive_dependents: Files that depend on direct dependents
      - behavioral_impact: Does change affect runtime behavior?
      - normalized to 0.0-1.0 scale
```

### Score Interpretation

| Amplification Score | Meaning | Risk Escalation |
|---------------------|---------|-----------------|
| 0.0 - 1.0 | Low amplification | None |
| 1.0 - 2.0 | Moderate amplification | +1 risk tier |
| 2.0 - 5.0 | High amplification | +2 risk tiers |
| 5.0+ | Critical amplification | Minimum High tier |

## High-Amplification Patterns

### Known High-Amplification Locations

| File/Pattern | Amplification Risk | Reason |
|--------------|-------------------|---------|
| `meta/*.yaml` | Critical | Governance rules affect all decisions |
| `meta/*.md` | High | Policies affect all skills |
| `protocols/*.md` | High | Contracts affect all handoffs |
| `TEMPLATE.md` | Critical | All future skills inherit changes |
| `skills/meta/*.md` | High | Meta-skills affect routing |
| `skill-map.yaml` | Critical | Project contract |
| `templates/*.yaml` | High | Configuration templates |

### Amplification by Change Type

| Change Type | Base Amplification |
|-------------|-------------------|
| Add field to schema | High (parsers must handle) |
| Remove field from schema | Critical (breaking change) |
| Rename concept | High (all references must update) |
| Change default value | Medium (behavior shifts) |
| Add new file | Low (additive) |
| Modify existing behavior | Medium-High (depends on usage) |

## Assessment Process

### Step 1: Identify Change Scope

```yaml
change_scope:
  files_modified:
    - path: meta/risk-tiers.md
      lines_changed: 5
      change_type: behavioral
      
  change_size:
    total_lines: 5
    total_files: 1
    normalized_size: 0.05  # Small change
```

### Step 2: Map Dependencies

```yaml
dependency_map:
  direct_dependents:
    - skills/meta/column-router.md
      imports: "References risk-tiers.md for tier definitions"
    - skills/meta/strategic-governor.md
      imports: "Uses risk tiers for validation"
    - skills/meta/health-assessor.md
      imports: "Calculates concern by risk weight"
      
  transitive_dependents:
    - skills/meta/readiness-certifier.md
      via: column-router.md
    - protocols/attention-autonomy-protocol.md
      via: health-assessor.md
      
  total_impact:
    direct: 3
    transitive: 12
    behavioral_scope: governance
```

### Step 3: Calculate Amplification

```yaml
amplification_calculation:
  change_size: 0.05  # 5 lines, normalized
  downstream_impact: 0.60  # 12 files affected, governance scope
  
  amplification_score: 12.0  # (0.60 / 0.05)
  
  interpretation: "Critical amplification - small change, large impact"
```

### Step 4: Recommend Risk Escalation

```yaml
risk_escalation:
  original_assessment:
    risk_tier: low
    reason: "Only 5 lines changed"
    
  amplified_assessment:
    risk_tier: high
    reason: "Critical amplification detected"
    escalation: "+2 tiers due to amplification > 5.0"
    
  recommendation: |
    This change to risk-tiers.md affects column-router, 
    strategic-governor, and 12 downstream files.
    
    Recommend: Full governance validation before merge.
```

## Output Contract

### Amplification Report Structure

```yaml
amplification_report:
  # Metadata
  timestamp: "2026-01-10T12:00:00Z"
  skill: "change-amplification-detector v1.0.0"
  
  # Change analyzed
  change:
    files:
      - path: meta/risk-tiers.md
        lines_changed: 5
        change_type: behavioral
    total_lines: 5
    total_files: 1
    
  # Impact analysis
  impact_analysis:
    direct_dependents:
      count: 3
      files:
        - skills/meta/column-router.md
        - skills/meta/strategic-governor.md
        - skills/meta/health-assessor.md
        
    transitive_dependents:
      count: 12
      sample:
        - skills/meta/readiness-certifier.md
        - protocols/attention-autonomy-protocol.md
        
    behavioral_scope: governance
    
  # Amplification score
  amplification:
    score: 12.0
    level: critical
    interpretation: "Small change with governance-wide impact"
    
  # Risk assessment
  risk_assessment:
    base_tier: low
    amplified_tier: high
    escalation_reason: "Amplification score > 5.0"
    
  # Recommendations
  recommendations:
    - "Escalate to High risk tier minimum"
    - "Run column-router, strategic-governor validation"
    - "Verify all dependent skills handle change"
    - "Consider staged rollout if possible"
    
  # Suggested validation
  suggested_validation:
    mandatory_skills:
      - architecture-review
      - skill-health-check
    optional_skills:
      - documentation-drift-detector
    columns: 4
    refinement: strict
```

### Filename Convention

```
YYYY-MM-DD_amplification-report_[target].yaml
```

Example: `2026-01-10_amplification-report_risk-tiers-change.yaml`

## Execution Modes

### Change-Analysis Mode (Default)

**When to Use:**
- After making changes (pre-commit, PR review)
- Analyzing specific modification
- Understanding impact of proposed change

**Process:**
1. Accept changed files/diff
2. Map all dependencies
3. Calculate amplification
4. Generate report with recommendations

**Invocation:**
```
"Analyze amplification for changes to meta/risk-tiers.md"
```

### Pre-Change Mode

**When to Use:**
- Before making changes
- Planning high-risk modifications
- Understanding potential impact

**Process:**
1. Accept file path(s) to be modified
2. Map dependencies (without actual change)
3. Estimate potential amplification
4. Generate advisory report

**Invocation:**
```
"What's the amplification risk if I modify TEMPLATE.md?"
```

**Output (Pre-Change):**
```yaml
amplification_advisory:
  target: TEMPLATE.md
  
  warning: |
    TEMPLATE.md is a critical amplification point.
    Changes here affect ALL future skills created from this template.
    
  potential_impact:
    all_future_skills: true
    existing_skills: false  # Unless backfill
    
  recommendation: |
    Consider impact carefully before modifying.
    If change is necessary:
    - Document the change in CHANGELOG
    - Consider backward compatibility
    - Plan skill-health-check on existing skills
```

## Common Misuses / Anti-Patterns

### DON'T Use This Skill For...

**Anti-Pattern 1: Every small change**
- **Instead:** Use for suspected high-leverage changes only
- **Why:** Most changes are low-amplification; checking everything is wasteful

**Anti-Pattern 2: Replacing risk assessment**
- **Instead:** Use alongside column-router, not instead of
- **Why:** Amplification is one factor in risk, not the whole picture

**Anti-Pattern 3: Blocking all high-amplification changes**
- **Instead:** Use for appropriate scrutiny, not avoidance
- **Why:** High-amplification changes are sometimes necessary

### WARNING: Known Limitations

**Limitation:** Cannot detect semantic amplification
- **Mitigation:** Manual review for meaning changes
- **Confidence:** ~90% accuracy on structural dependencies

**Limitation:** May miss dynamic dependencies
- **Mitigation:** Document runtime dependencies explicitly

## Known Limitations

- Cannot detect runtime/dynamic dependencies
- May not catch all transitive impacts
- Semantic changes harder to assess than structural
- Requires accurate dependency information

## Fallback Strategy

If dependency mapping fails:

1. **Use known patterns** - Check against high-amplification locations
2. **Assume high impact** - For governance files, default to high amplification
3. **Manual review** - When automated analysis is uncertain

## Integration Points

### Upstream (Inputs)

| Source | What It Provides |
|--------|------------------|
| Git diff | Changed files and lines |
| File system | Dependency scanning |
| skill-map.yaml | Surface definitions |

### Downstream (Outputs)

| Consumer | How It Uses Report |
|----------|-------------------|
| Column Router | Risk tier escalation |
| Health Assessor | Change velocity weighting |
| Strategic Governor | Validation requirements |
| Human | Change planning |

### Integration with Column Router

When amplification is detected, column-router should:

```yaml
column_router_integration:
  on_high_amplification:
    - escalate_risk_tier: true
    - increase_columns: true
    - require_strict_refinement: true
    
  on_critical_amplification:
    - minimum_tier: high
    - mandatory_columns:
        - architecture-review
        - relevant domain skill
    - require_proofs: true
```

## Examples

### Example 1: Low Amplification

```yaml
amplification_report:
  change:
    files: [skills/testing/adversarial-ui-tester.md]
    lines_changed: 10
    
  impact_analysis:
    direct_dependents: 0
    transitive_dependents: 0
    
  amplification:
    score: 0.0
    level: low
    
  risk_assessment:
    base_tier: low
    amplified_tier: low  # No escalation
    
  recommendation: "Proceed with normal review"
```

### Example 2: High Amplification

```yaml
amplification_report:
  change:
    files: [meta/taste-profile.yaml]
    lines_changed: 3
    
  impact_analysis:
    direct_dependents: 3
    transitive_dependents: 8
    
  amplification:
    score: 3.7
    level: high
    
  risk_assessment:
    base_tier: low
    amplified_tier: medium
    escalation: "+2 tiers"
    
  recommendation: "Run governance validation"
```

### Example 3: Critical Amplification

```yaml
amplification_report:
  change:
    files: [TEMPLATE.md]
    lines_changed: 2
    
  impact_analysis:
    direct_dependents: 0  # No direct imports
    future_impact: all_new_skills
    behavioral_scope: skill_creation
    
  amplification:
    score: "∞"  # Affects unlimited future skills
    level: critical
    
  risk_assessment:
    base_tier: trivial
    amplified_tier: high
    escalation: "Critical infrastructure change"
    
  recommendation: |
    CRITICAL: Template changes affect all future skills.
    - Document change rationale
    - Consider backward compatibility
    - Run skill-health-check on sample existing skills
    - Require explicit approval
```

## Exit Conditions

### Success

- Dependencies mapped
- Amplification calculated
- Risk escalation determined
- Recommendations generated

### Failure

- File not found
- Dependency mapping failed
- Critical error in analysis

### Handoff

After analysis:
1. Present amplification report
2. Recommend risk tier adjustment
3. Suggest validation skills
4. Hand off to column-router for planning

## See Also

- `skills/meta/column-router.md` - Uses amplification for risk
- `skills/meta/health-assessor.md` - Change velocity assessment
- `meta/risk-tiers.md` - Risk tier definitions
- `protocols/attention-autonomy-protocol.md` - Trigger integration
