---
type: skill-definition
name: column-router
category: meta
version: 1.0.0
maturity: draft
lifecycle: validated
estimated-cost: low
typical-runtime: 1-2min
complexity-level: moderate
requires-deep-analysis: false
scope: meta
tier: meta
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - meta
  - governance
  - attention
  - risk-assessment
  - column-planning
prerequisites:
  - file: meta/risk-tiers.md
    reason: "Defines risk tier model"
  - file: meta/failure-cost-model.md
    reason: "Provides cost axis analysis"
execution-modes:
  - assessment
---

# Column Router

## Purpose

Decide **how much cognitive scrutiny** a change deserves before running any agents. This meta-skill produces a **column plan**, not execution.

**Core insight:** The column router allocates attention, not execution. It answers "how paranoid should I be?" so you don't have to decide every time.

## When to Invoke

**Before** any column or skill execution when:
- Starting a new integration task
- Unsure how much analysis is warranted
- Want to avoid both over-analysis and under-analysis

**Do NOT invoke when:**
- You already know exactly what analysis is needed
- Running a predefined skill chain
- Trivial changes (config, copy, styling)

## Invocation Pattern

**Standard:**
```
"Assess risk and plan columns for: {change description}"
```

**With context:**
```
"Assess risk for: {description}
Files: {file list}
Surfaces: {ui, api, persistence, auth, etc.}"
```

## Input Requirements

### Required

- **Change description:** What is being changed and why

### Optional (Improves Assessment)

- **Files affected:** List of files that will change
- **Surfaces touched:** ui, api, persistence, auth, payment
- **Pattern match:** Known pattern ID or "novel"
- **Reversibility:** feature-flag, quick-rollback, migration, permanent

## Assessment Process

### Step 1: Identify Surfaces

Determine which system surfaces the change touches:

| Surface | Description | Risk Weight |
|---------|-------------|-------------|
| `ui` | User-facing interface | Medium |
| `api` | Backend endpoints | Medium |
| `persistence` | Database, storage, cache | High |
| `auth` | Authentication/authorization | High |
| `payment` | Money handling | Critical |
| `data` | User data, PII | High |
| `config` | Configuration only | Low |

### Step 2: Assess Base Risk Tier

Using `meta/risk-tiers.md`:

```
Trivial: Config/copy/styling only
Low: Reversible, bounded, known pattern
Medium: Functional, multiple surfaces
High: Irreversible OR sensitive
Critical: Money/auth/data loss potential
```

### Step 2b: Calculate Failure Cost (Optional Enhancement)

If detailed cost assessment is needed, use `meta/failure-cost-model.md`:

Assess four cost axes (each 0.0 - 1.0):
- **Blast Radius**: How much breaks? (single → feature → system-wide)
- **Detectability**: How obvious is failure? (crash → subtle → silent)
- **Reversibility**: How easy to roll back? (flag → migration → permanent)
- **Trust Impact**: Does it affect user confidence? (internal → user-facing → money/data)

```
cost_score = (blast_radius + detectability + reversibility + trust_impact) / 4
```

**Cost → Risk Tier Adjustment:**

| Cost Score | Effect |
|------------|--------|
| 0.0 - 0.25 | May de-escalate risk tier by 1 |
| 0.25 - 0.5 | No change |
| 0.5 - 0.75 | Escalate risk tier by 1 |
| 0.75 - 1.0 | Escalate to Critical minimum |

**When to use:**
- Complex changes where surface-based assessment isn't clear
- High-stakes changes requiring justification
- When governor needs detailed cost reasoning

**When to skip:**
- Trivial changes (use shortcuts)
- Clear surface-based risk tier
- Time-sensitive assessments

### Step 3: Apply Escalation Rules

Check for automatic escalations:

| Signal | Effect |
|--------|--------|
| Touches persistence | +1 tier, min Medium |
| Affects >3 files | +1 tier |
| Novel pattern | +1 tier |
| Prior failures in area | +1 tier |
| Touches auth/* | High minimum |
| Touches payment/* | Critical |

### Step 4: Apply De-escalation Rules

Check for de-escalations:

| Signal | Effect |
|--------|--------|
| Feature-flagged | -1 tier |
| High test coverage (>80%) | -1 tier |
| Known safe pattern | -1 tier |
| Quick rollback (<5min) | -1 tier |

### Step 5: Generate Column Plan

Based on final risk tier:

| Tier | Columns | Refinement | Proofs |
|------|---------|------------|--------|
| Trivial | 0 | None | No |
| Low | 1 | Light | No |
| Medium | 2-3 | Normal | No |
| High | 4 | Strict | Sometimes |
| Critical | 4+ | Strict | Always |

### Step 6: Check Taste Profile

If `meta/taste-profile.yaml` exists, apply preferences:

**6a. Column Preferences by Change Type:**
```yaml
# Example: UI changes
ui_changes:
  always_include: [adversarial-ui]
  rarely_needed: [architecture-review]
```

Add `always_include` columns. Deprioritize `rarely_needed` columns.

**6b. Skill Biases for Target Surfaces:**
```yaml
# Example: Boost adversarial-ui for checkout
adversarial-ui-tester:
  boost_for: [checkout, onboarding, payment]
  boost_amount: 0.15
```

Apply boost/suppress to column recommendations.

**6c. Anti-Pattern Triggers:**

Check `meta/anti-patterns.md` for matching patterns:
- If pattern matches, apply its action (escalate, add column, require proof)
- Include triggered patterns in output

**Example Anti-Pattern Match:**
```yaml
# Pattern AUTH-001 detected
auth_light_review:
  detection: "Change touches auth/* paths AND risk tier < High"
  action: escalate_risk
  escalate_to: high
  mandatory_columns: [correctness, adversarial-ui, failure-mode-simulator]
```

### Step 7: Emit Plan

Output the column plan for approval.

## Output Format

```yaml
column_router_assessment:
  timestamp: 2026-01-08T12:00:00Z
  change_summary: "Brief description of change"
  
risk_assessment:
  tier: medium
  base_tier: low
  failure_cost:  # Optional, included when detailed assessment performed
    score: 0.45
    level: medium
    axes:
      blast_radius: 0.4
      detectability: 0.5
      reversibility: 0.3
      trust_impact: 0.55
    highest_concern: trust_impact
  escalations:
    - reason: "Affects >3 files"
      effect: "+1 tier"
  de_escalations:
    - reason: "Feature-flagged"
      effect: "-1 tier (not applied, already at base)"
  reasoning:
    - "Functional change to checkout flow"
    - "User-facing but reversible"
    - "Similar to known pattern: checkout-form-v1"
  confidence: 0.8

column_plan:
  recommended_columns:
    - name: ux-adversarial
      reason: "User-facing checkout change"
    - name: correctness
      reason: "Functional behavior change"
  optional_columns:
    - name: architecture
      reason: "Only if structural changes detected"
  skip_columns:
    - name: performance
      reason: "No performance-sensitive changes"
  refinement_strictness: normal
  proof_required: false

skip_exploration_if:
  - pattern_id: checkout-form-validation-v1
    reason: "Already validated this exact pattern"

taste_profile_applied:
  column_preferences: "ui_changes"
  skill_biases:
    - skill: adversarial-ui-tester
      effect: "+0.15 (checkout boost)"
  
anti_patterns_triggered:
  - pattern_id: UX-001
    name: "Checkout Changes Without Adversarial Testing"
    action_taken: "Added adversarial-ui to mandatory columns"

governor_note: "Medium risk - 2-3 columns appropriate. Do not over-analyze."
```

## Integration with Other Systems

### Failure-Cost Model

If `meta/failure-cost-model.md` is available, column-router also considers:
- Blast radius
- Detectability
- Reversibility
- Trust impact

This provides more nuanced tier assessment.

### Taste Profile

If `meta/taste-profile.yaml` exists:
- Apply column preferences for change types
- Apply skill biases
- Check anti-patterns for escalation triggers

### Strategic Governor

After column plan is generated, governor may:
- Approve plan as-is
- Suggest throttling (fewer columns)
- Suggest escalation (more columns)

### Skill Router

Column plan feeds into skill-router:
- Recommended columns inform which skills to load
- Refinement strictness affects Agent B behavior

## Behavioral Rules

### DO

- Be explicit about reasoning
- Show escalation/de-escalation logic
- Provide confidence score
- Include governor note

### DO NOT

- Execute columns (only plan them)
- Override human judgment (this is a proposal)
- Assume all changes need maximum analysis
- Ignore taste profile if present

## Example Assessments

### Example 1: Low Risk

**Input:**
```
"Adding a new toast notification component for success messages"
Files: src/components/Toast.tsx
Surfaces: ui
```

**Output:**
```yaml
risk_assessment:
  tier: low
  reasoning:
    - "UI only, no state changes"
    - "Single component, easily reversible"
    - "Known pattern: notification-system-v1"

column_plan:
  recommended_columns:
    - name: ux-adversarial
      reason: "User-facing component"
  refinement_strictness: light

governor_note: "Low risk - 1 column sufficient. Single skill may be enough."
```

### Example 2: High Risk

**Input:**
```
"Refactoring authentication token refresh logic"
Files: src/auth/tokenRefresh.ts, src/auth/session.ts, src/api/client.ts
Surfaces: auth, api
```

**Output:**
```yaml
risk_assessment:
  tier: high
  base_tier: medium
  escalations:
    - reason: "Touches auth/* path"
      effect: "High minimum"
    - reason: "Affects 3+ files"
      effect: "+1 tier (already at High)"
  reasoning:
    - "Authentication is sensitive surface"
    - "Multiple files affected"
    - "Session handling has cascading effects"

column_plan:
  recommended_columns:
    - name: correctness
      reason: "Auth logic must be bulletproof"
    - name: architecture
      reason: "Cross-cutting change"
    - name: adversarial-ui
      reason: "Auth failures affect user experience"
    - name: failure-mode-simulator
      reason: "Must handle edge cases"
  refinement_strictness: strict

governor_note: "High risk - 4 columns mandatory. Do not skip."
```

### Example 3: Critical Risk

**Input:**
```
"Implementing Stripe payment processing for checkout"
Files: src/payment/stripe.ts, src/checkout/payment.tsx
Surfaces: payment, ui, api
```

**Output:**
```yaml
risk_assessment:
  tier: critical
  reasoning:
    - "Payment processing touches money"
    - "User trust surface"
    - "Compliance implications"

column_plan:
  recommended_columns:
    - name: correctness
      reason: "Payment logic must be perfect"
    - name: adversarial-ui
      reason: "User-facing payment flow"
    - name: architecture
      reason: "Integration architecture matters"
    - name: failure-mode-simulator
      reason: "Must handle all failure scenarios"
  refinement_strictness: strict
  proof_required: true
  mandatory_columns:
    - correctness
    - failure-mode-simulator

governor_note: "Critical risk - all columns mandatory. Proofs required. No shortcuts."
```

## Exit Conditions

Column router is complete when:
- Risk tier is determined with reasoning
- Column plan is generated
- Governor note is included
- Human can approve or modify

## Limitations

- Cannot execute columns (only plans them)
- Cannot override human judgment
- Depends on accurate input about change scope
- Taste profile and failure-cost model are optional enhancements

## See Also

- `meta/risk-tiers.md` - Risk tier definitions
- `meta/failure-cost-model.md` - Detailed cost analysis
- `meta/taste-profile.yaml` - Encoded preferences
- `skills/meta/strategic-governor.md` - Plan validation
- `docs/column-pattern-guide.md` - Column execution

