# Risk Tiers

This document defines the risk tier system used by the column-router to determine how much cognitive scrutiny a change deserves.

## Core Principle

> **Match rigor to risk, not habit.**

Not every change deserves the same analysis. The risk tier system ensures:
- Trivial changes don't waste cognitive resources
- Critical changes get mandatory scrutiny
- The system prevents both under-analysis and over-analysis

## Risk Tier Definitions

| Tier | Meaning | Column Plan | Refinement |
|------|---------|-------------|------------|
| **Trivial** | Config, copy, styling only | 0 columns (single skill or none) | None |
| **Low** | Reversible, bounded, known pattern | 1 column | Light |
| **Medium** | Functional, multiple surfaces | 2-3 columns | Normal |
| **High** | Irreversible OR sensitive areas | 4 columns | Strict |
| **Critical** | Money, auth, data loss potential | 4+ columns | Strict + proofs |

## Tier Criteria

### Trivial

**Characteristics:**
- Configuration changes only
- Copy/text updates
- Styling/cosmetic changes
- No behavioral impact

**Examples:**
- Updating a config value
- Fixing a typo in UI text
- Adjusting CSS spacing
- Updating documentation

**Column Plan:**
```yaml
tier: trivial
columns: 0
refinement: none
action: "Single skill or skip entirely"
```

### Low

**Characteristics:**
- Easily reversible (feature flag, quick rollback)
- Bounded scope (single component)
- Known pattern (done before successfully)
- No persistence changes

**Examples:**
- Adding a new UI component (no state changes)
- Refactoring internal function (no API change)
- Adding logging
- Updating non-critical validation

**Column Plan:**
```yaml
tier: low
columns: 1
refinement: light
recommended_columns:
  - correctness  # OR relevant domain column
```

### Medium

**Characteristics:**
- Functional changes affecting behavior
- Multiple surfaces touched
- Reversible but requires effort
- Some user impact

**Examples:**
- New feature implementation
- Refactoring shared utilities
- API endpoint changes (backward compatible)
- State management updates

**Column Plan:**
```yaml
tier: medium
columns: 2-3
refinement: normal
recommended_columns:
  - Primary domain column (e.g., ux-adversarial)
  - correctness
optional_columns:
  - architecture  # if structural
```

### High

**Characteristics:**
- Irreversible changes OR
- Touches sensitive areas (but not critical) OR
- Affects >3 files/surfaces OR
- Novel pattern (not done before)

**Examples:**
- Database schema migrations
- Authentication flow changes
- Payment UI changes (not payment processing)
- New integration patterns
- Major refactoring

**Column Plan:**
```yaml
tier: high
columns: 4
refinement: strict
recommended_columns:
  - Primary domain column
  - correctness
  - architecture
  - adversarial (if user-facing)
```

### Critical

**Characteristics:**
- Touches money/payments processing
- Touches authentication/authorization
- Risk of data loss or corruption
- Affects user trust directly
- Compliance implications

**Examples:**
- Payment processing logic
- Auth token handling
- Data deletion features
- Privacy-sensitive data handling
- Security-critical code paths

**Column Plan:**
```yaml
tier: critical
columns: 4+
refinement: strict
proof_required: true
mandatory_columns:
  - correctness
  - architecture
  - adversarial-ui (if user-facing)
  - failure-mode-simulator
```

## Escalation Rules

Certain signals automatically escalate the risk tier:

### Automatic Escalation (+1 tier minimum)

| Signal | Detection | Escalation |
|--------|-----------|------------|
| Touches persistence | Changes to DB, storage, cache | +1 tier, min Medium |
| Affects >3 files | File count in change | +1 tier |
| Novel pattern | Not in lessons/known patterns | +1 tier |
| Prior failures | This area had bugs before | +1 tier |

### Mandatory Escalation (to specific tier)

| Signal | Detection | Required Tier |
|--------|-----------|---------------|
| Touches auth/* | Path includes auth | High minimum |
| Touches payment/* | Path includes payment | Critical |
| Touches user data | Handles PII | High minimum |
| Database migration | Schema changes | High minimum |

### De-escalation Rules

Risk can be reduced (but never below Trivial) when:

| Signal | Detection | Effect |
|--------|-----------|--------|
| Feature-flagged | Has feature flag | -1 tier |
| Existing tests | >80% coverage in area | -1 tier |
| Known safe pattern | Matches validated pattern | -1 tier |
| Quick rollback | Documented rollback < 5min | -1 tier |

## Risk Assessment Process

### Input

```yaml
change_description: "Description of what's being changed"
files_affected:
  - path/to/file1.ts
  - path/to/file2.ts
surfaces:
  - ui  # ui, api, persistence, auth, etc.
pattern_match: "known pattern ID or 'novel'"
reversibility: "feature-flag | quick-rollback | migration | permanent"
```

### Output

```yaml
risk_assessment:
  tier: medium
  base_tier: low
  escalations:
    - reason: "Affects >3 files"
      from: low
      to: medium
  de_escalations: []
  reasoning:
    - "Functional change to checkout flow"
    - "User-facing but reversible"
    - "Known pattern (similar to order-summary)"
  confidence: 0.8
```

## Column Plan Generation

Based on risk tier, the column-router generates:

```yaml
column_plan:
  tier: medium
  recommended_columns:
    - ux-adversarial
    - correctness
  optional_columns:
    - architecture
  skip_columns:
    - performance  # not relevant for this change type
  refinement_strictness: normal
  proof_required: false
  skip_exploration_if:
    - pattern_id: checkout-form-v1
      reason: "Already validated this exact pattern"
```

## Integration Points

### Column Router

The column-router consumes risk-tiers.md to:
1. Assess change risk
2. Generate column plan
3. Set refinement strictness

### Strategic Governor

The governor uses risk tier to:
1. Validate column count is appropriate
2. Throttle over-analysis on low-risk
3. Escalate under-analysis on high-risk

### Skill Effectiveness Analyzer

Tracks:
1. Accuracy of risk assessments over time
2. Whether tier-appropriate analysis caught issues
3. Proposes tier adjustments based on data

## Calibration Notes

Risk tiers are **judgments, not algorithms**.

- Tiers encode how paranoid you should be
- They prevent both over-analysis and under-analysis
- They evolve based on experience (lessons learned)
- Human can always override

**Key insight:** The goal is not perfect risk assessment. The goal is preventing obviously wrong allocation of cognitive resources.

## See Also

- `skills/meta/column-router.md` - Consumes risk tiers
- `meta/failure-cost-model.md` - Detailed cost analysis
- `skills/meta/strategic-governor.md` - Enforces tier-appropriate analysis
- `meta/anti-patterns.md` - Learned escalation triggers

