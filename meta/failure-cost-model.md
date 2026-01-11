# Failure-Cost Model

This document defines how to assess the cost of potential failures, enabling the system to match rigor to consequence.

## Core Principle

> **Not all mistakes cost the same. Match analysis depth to failure cost.**

A bug in a toast notification has different consequences than a bug in payment processing. The failure-cost model ensures:
- Low-cost failures get light review (fast)
- High-cost failures get thorough review (safe)
- Resources are allocated proportionally

## Cost Axes

Every change is assessed on four dimensions:

### 1. Blast Radius

**Question:** How much breaks if this fails?

| Level | Description | Examples |
|-------|-------------|----------|
| **Low** (0.0-0.3) | Single component | Toast notification, single form field |
| **Medium** (0.3-0.6) | Feature-level | Checkout flow, user profile page |
| **High** (0.6-1.0) | System-wide | Auth system, data layer, core API |

### 2. Detectability

**Question:** Will failure be obvious?

| Level | Description | Examples |
|-------|-------------|----------|
| **Low** (0.0-0.3) | Immediate error | Crash, visible error message |
| **Medium** (0.3-0.6) | Subtle bug | Wrong calculation, data inconsistency |
| **High** (0.6-1.0) | Silent corruption | Data loss without errors, security bypass |

**Note:** Higher detectability score = HARDER to detect = WORSE.

### 3. Reversibility

**Question:** Can we roll back cleanly?

| Level | Description | Examples |
|-------|-------------|----------|
| **Low** (0.0-0.3) | Feature flag | Instant rollback, no migration |
| **Medium** (0.3-0.6) | Requires migration | Database rollback, config change |
| **High** (0.6-1.0) | Permanent | Data deletion, sent notifications |

### 4. Trust Impact

**Question:** Does this affect user confidence?

| Level | Description | Examples |
|-------|-------------|----------|
| **Low** (0.0-0.3) | Internal only | Admin tools, internal APIs |
| **Medium** (0.3-0.6) | User-facing | UI bugs, minor UX issues |
| **High** (0.6-1.0) | Money/data | Payment errors, data exposure |

## Combined Cost Score

```
cost_score = (blast_radius + detectability + reversibility + trust_impact) / 4
```

**Score Interpretation:**

| Score Range | Cost Level | Meaning |
|-------------|------------|---------|
| 0.0 - 0.25 | Low | Mistakes are cheap, fast iteration OK |
| 0.25 - 0.5 | Medium | Standard review appropriate |
| 0.5 - 0.75 | High | Extra scrutiny needed |
| 0.75 - 1.0 | Critical | Maximum rigor, proofs may be required |

## Cost → Behavior Mapping

### Low Cost (0.0 - 0.25)

**System behavior:**
- Skip heavy analysis
- Accept heuristics
- Favor speed over certainty
- Quick iteration acceptable

**Column router output:**
```yaml
cost_level: low
columns: 0-1
refinement: light | none
proof_required: false
acceptable_confidence: 0.6
```

### Medium Cost (0.25 - 0.5)

**System behavior:**
- Standard column analysis
- Normal refinement
- Balance speed and safety

**Column router output:**
```yaml
cost_level: medium
columns: 2-3
refinement: normal
proof_required: false
acceptable_confidence: 0.7
```

### High Cost (0.5 - 0.75)

**System behavior:**
- More columns
- Strict refinement
- Proofs sometimes required
- Slower is acceptable

**Column router output:**
```yaml
cost_level: high
columns: 3-4
refinement: strict
proof_required: sometimes
acceptable_confidence: 0.8
```

### Critical Cost (0.75 - 1.0)

**System behavior:**
- Maximum columns
- Strict refinement
- Proofs always required
- No shortcuts

**Column router output:**
```yaml
cost_level: critical
columns: 4+
refinement: strict
proof_required: always
mandatory_columns:
  - correctness
  - failure-mode-simulator
acceptable_confidence: 0.9
```

## Assessment Process

### Input

```yaml
change:
  description: "What is being changed"
  
cost_assessment:
  blast_radius:
    score: 0.0-1.0
    reasoning: "Why this score"
  detectability:
    score: 0.0-1.0
    reasoning: "Why this score"
  reversibility:
    score: 0.0-1.0
    reasoning: "Why this score"
  trust_impact:
    score: 0.0-1.0
    reasoning: "Why this score"
```

### Output

```yaml
failure_cost_assessment:
  combined_score: 0.45
  cost_level: medium
  
  axes:
    blast_radius: 0.3
    detectability: 0.5
    reversibility: 0.4
    trust_impact: 0.55
  
  highest_concern: trust_impact
  reasoning:
    - "User-facing checkout change"
    - "Errors may be subtle (wrong totals)"
    - "Feature-flagged for quick rollback"
  
  recommended_behavior:
    columns: 2-3
    refinement: normal
    proof_required: false
```

## Quick Assessment Shortcuts

For speed, use these heuristics:

### Automatic Low Cost

- Config-only changes
- Copy/text updates
- Styling changes
- Test-only changes
- Documentation updates

### Automatic Medium Cost

- New UI components
- Internal refactoring
- Non-critical API changes
- Logging/monitoring changes

### Automatic High Cost

- Database schema changes
- Auth flow changes
- User-facing form changes
- API contract changes

### Automatic Critical Cost

- Payment processing
- Auth token handling
- Data deletion
- Privacy-sensitive data
- Security-critical paths

## Integration with Column Router

The column-router uses failure-cost assessment to:

1. **Calibrate risk tier:**
   ```
   If cost_level == critical AND risk_tier < High:
       risk_tier = High  # Escalate
   ```

2. **Set refinement strictness:**
   ```
   refinement_strictness = cost_level.default_strictness
   ```

3. **Determine proof requirements:**
   ```
   proof_required = (cost_level >= high)
   ```

4. **Set mandatory columns:**
   ```
   If cost_level == critical:
       mandatory_columns.add(correctness)
       mandatory_columns.add(failure-mode-simulator)
   ```

## Integration with Strategic Governor

The governor uses failure-cost to:

1. **Prevent under-analysis:**
   - If cost_level is high but columns < 3 → escalate
   - If cost_level is critical but proofs missing → halt

2. **Prevent over-analysis:**
   - If cost_level is low but columns > 2 → throttle
   - If cost_level is medium but running 4+ columns → suggest reduction

## Examples

### Example 1: Toast Notification

**Change:** Adding success toast to checkout completion

```yaml
failure_cost_assessment:
  combined_score: 0.15
  cost_level: low
  
  axes:
    blast_radius: 0.1     # Single component
    detectability: 0.1    # Obvious if broken
    reversibility: 0.1    # Feature-flagged
    trust_impact: 0.3     # User-facing but minor
  
  recommended_behavior:
    columns: 0-1
    refinement: light
```

### Example 2: Checkout Form Validation

**Change:** Refactoring form validation logic

```yaml
failure_cost_assessment:
  combined_score: 0.50
  cost_level: medium-high
  
  axes:
    blast_radius: 0.4     # Feature-level
    detectability: 0.6    # Validation bugs can be subtle
    reversibility: 0.3    # Feature-flagged
    trust_impact: 0.7     # Checkout is critical path
  
  recommended_behavior:
    columns: 3
    refinement: normal-strict
```

### Example 3: Payment Processing

**Change:** Implementing Stripe integration

```yaml
failure_cost_assessment:
  combined_score: 0.85
  cost_level: critical
  
  axes:
    blast_radius: 0.8     # Affects all purchases
    detectability: 0.9    # Payment bugs can be silent
    reversibility: 0.7    # Partial transactions hard to undo
    trust_impact: 1.0     # Money = maximum trust impact
  
  recommended_behavior:
    columns: 4+
    refinement: strict
    proof_required: true
    mandatory_columns:
      - correctness
      - failure-mode-simulator
```

## Calibration Notes

### Subjectivity

Cost assessment involves judgment. When unsure:
- Err on the side of higher cost
- Document reasoning
- Let human override

### Evolution

Cost thresholds may need calibration:
- Track actual failure rates
- Adjust axis weights if needed
- Update shortcuts based on experience

### Override

Human can always override:
- "Treat this as critical even though it seems low"
- "This is actually low-risk because X"

Cost model informs but doesn't dictate.

## See Also

- `meta/risk-tiers.md` - Risk tier system
- `skills/meta/column-router.md` - Uses cost model
- `skills/meta/strategic-governor.md` - Enforces cost-appropriate analysis
- `templates/failure-cost-assessment.yaml` - Assessment template

