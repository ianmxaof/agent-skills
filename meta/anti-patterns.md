# Anti-Patterns (Learned Regrets)

This document captures patterns that have caused problems and should trigger automatic escalation or specific behaviors. These are "things we learned the hard way."

## Purpose

Anti-patterns serve as:
- **Automatic escalation triggers** for the column-router
- **Warning signals** for the strategic-governor
- **Historical memory** to prevent repeating mistakes

## How Anti-Patterns Work

When the column-router or governor detects an anti-pattern:

1. **Alert is raised** with the pattern ID
2. **Risk tier is escalated** (if not already at level)
3. **Specific action is enforced** (e.g., mandatory columns)
4. **Human is notified** of the pattern match

## Anti-Pattern Structure

```yaml
pattern_id:
  name: "Human-readable name"
  incident: "Brief description of what went wrong"
  detection: "How to identify this pattern"
  rule: "What this triggers"
  action: escalate_risk | add_column | require_proof | halt_and_ask
  severity: critical | high | medium
  added: "YYYY-MM-DD"
  last_triggered: "YYYY-MM-DD or null"
```

---

## Critical Anti-Patterns

These trigger immediate escalation to Critical tier.

### AUTH-001: Auth Changes Without Full Analysis

```yaml
auth_light_review:
  name: "Auth Changes Without Full Analysis"
  incident: "Silent auth bypass shipped due to insufficient review"
  detection: "Change touches auth/* paths AND risk tier < High"
  rule: "Auth changes → High risk minimum, 4 columns mandatory"
  action: escalate_risk
  escalate_to: high
  mandatory_columns:
    - correctness
    - adversarial-ui
    - failure-mode-simulator
  severity: critical
  added: 2026-01-08
  last_triggered: null
```

### PAY-001: Payment Logic Without Proofs

```yaml
payment_no_proofs:
  name: "Payment Logic Without Proofs"
  incident: "Payment calculation error caught only in production"
  detection: "Change touches payment/* AND proof_required = false"
  rule: "Payment changes → proofs always required"
  action: require_proof
  severity: critical
  added: 2026-01-08
  last_triggered: null
```

### DATA-001: Deletion Without Confirmation

```yaml
deletion_no_confirm:
  name: "Deletion Without Confirmation"
  incident: "User data deleted without proper confirmation UX"
  detection: "Change adds delete functionality without confirmation UI"
  rule: "Deletion actions → adversarial-ui mandatory"
  action: add_column
  mandatory_columns:
    - adversarial-ui
  severity: critical
  added: 2026-01-08
  last_triggered: null
```

---

## High Anti-Patterns

These trigger escalation to High tier or add mandatory columns.

### UX-001: Checkout Changes Without Adversarial Testing

```yaml
checkout_no_adversarial:
  name: "Checkout Changes Without Adversarial Testing"
  incident: "Edge case in checkout flow caused cart abandonment spike"
  detection: "Change touches checkout/* AND adversarial-ui not in columns"
  rule: "Checkout changes → adversarial-ui mandatory"
  action: add_column
  mandatory_columns:
    - adversarial-ui
  severity: high
  added: 2026-01-08
  last_triggered: null
```

### DB-001: Schema Changes Without Migration Test

```yaml
schema_no_migration_test:
  name: "Schema Changes Without Migration Test"
  incident: "Migration failed in production due to untested edge case"
  detection: "Change includes database schema AND failure-mode not in columns"
  rule: "Schema changes → failure-mode-simulator mandatory"
  action: add_column
  mandatory_columns:
    - failure-mode-simulator
  severity: high
  added: 2026-01-08
  last_triggered: null
```

### API-001: Breaking API Change Without Version Bump

```yaml
breaking_api_no_version:
  name: "Breaking API Change Without Version Bump"
  incident: "Client apps broke after unversioned API change"
  detection: "API endpoint modified in non-additive way"
  rule: "Breaking API changes → architecture-review mandatory"
  action: add_column
  mandatory_columns:
    - architecture-review
  severity: high
  added: 2026-01-08
  last_triggered: null
```

### FORM-001: Form Validation Changes Without Edge Case Testing

```yaml
form_validation_light:
  name: "Form Validation Changes Without Edge Case Testing"
  incident: "Validation bypass allowed invalid data submission"
  detection: "Change modifies form validation logic"
  rule: "Form validation → correctness column mandatory"
  action: add_column
  mandatory_columns:
    - correctness
  severity: high
  added: 2026-01-08
  last_triggered: null
```

---

## Medium Anti-Patterns

These add warnings or suggest additional analysis.

### PERF-001: Heavy Dependency Addition

```yaml
heavy_dependency:
  name: "Heavy Dependency Addition"
  incident: "Bundle size increased 40% from unreviewed dependency"
  detection: "New dependency added to package.json"
  rule: "New dependency → bundle-size-analyzer suggested"
  action: suggest_column
  suggested_columns:
    - bundle-size-analyzer
  severity: medium
  added: 2026-01-08
  last_triggered: null
```

### STATE-001: Global State Modification

```yaml
global_state_mod:
  name: "Global State Modification"
  incident: "Subtle state bug caused intermittent UI issues"
  detection: "Change modifies global/shared state"
  rule: "Global state changes → architecture-review suggested"
  action: suggest_column
  suggested_columns:
    - architecture-review
  severity: medium
  added: 2026-01-08
  last_triggered: null
```

### TEST-001: Removing Tests

```yaml
test_removal:
  name: "Removing Tests"
  incident: "Removed test was only validation for edge case"
  detection: "Test file or test case deleted"
  rule: "Test removal → correctness column suggested"
  action: suggest_column
  suggested_columns:
    - correctness
  severity: medium
  added: 2026-01-08
  last_triggered: null
```

---

## Adding New Anti-Patterns

### When to Add

Add a new anti-pattern when:
1. A bug reaches production that could have been caught
2. A pattern of similar issues emerges
3. A category of change repeatedly causes problems
4. Post-incident review identifies a gap

### Template

```yaml
CATEGORY-NNN:
  name: "Descriptive Name"
  incident: "What went wrong that caused this pattern to be added"
  detection: "How the column-router detects this pattern"
  rule: "What behavior this triggers"
  action: escalate_risk | add_column | require_proof | suggest_column | halt_and_ask
  severity: critical | high | medium
  added: YYYY-MM-DD
  last_triggered: null
```

### Categories

| Prefix | Area |
|--------|------|
| AUTH | Authentication/authorization |
| PAY | Payment/money |
| DATA | Data handling/storage |
| UX | User experience |
| DB | Database/persistence |
| API | API contracts |
| FORM | Form handling |
| PERF | Performance |
| STATE | State management |
| TEST | Testing |
| SEC | Security |

---

## Integration Points

### Column Router

The column-router checks anti-patterns during:
- Step 3: Apply Escalation Rules
- Step 6: Check Taste Profile

When a pattern matches:
1. Log the pattern match
2. Apply the specified action
3. Include pattern ID in assessment output

### Strategic Governor

The governor uses anti-patterns to:
- Validate that mandatory columns are included
- Prevent de-escalation when pattern is active
- Flag attempts to bypass required analysis

### Output Format

When an anti-pattern is triggered:

```yaml
anti_patterns_triggered:
  - pattern_id: AUTH-001
    name: "Auth Changes Without Full Analysis"
    action_taken: "Escalated to High, added mandatory columns"
  - pattern_id: UX-001
    name: "Checkout Changes Without Adversarial Testing"
    action_taken: "Added adversarial-ui to columns"
```

---

## Maintenance

### Monthly Review

- Check `last_triggered` dates
- Consider removing patterns that never trigger (may be too specific)
- Consider refining patterns that trigger too often (may be too broad)

### Post-Incident

After any production incident:
1. Identify if existing pattern should have caught it
2. If no pattern exists, create one
3. Update severity if pattern didn't escalate enough

### Retirement

Retire patterns when:
- Underlying code is fundamentally changed
- Detection no longer applies
- Pattern has never triggered in 6+ months

Retired patterns move to `anti-patterns-archive.md` for history.

---

## See Also

- `meta/taste-profile.yaml` - Positive preferences
- `meta/risk-tiers.md` - Risk tier definitions
- `skills/meta/column-router.md` - Uses anti-patterns
- `skills/meta/strategic-governor.md` - Enforces anti-patterns

