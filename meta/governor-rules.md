# Governor Rules

This document defines the throttle and escalate triggers used by the strategic-governor to prevent over-analysis and under-analysis.

## Rule Categories

| Prefix | Category | Effect |
|--------|----------|--------|
| T-### | Throttle | Reduce analysis |
| E-### | Escalate | Increase analysis |
| H-### | Halt | Stop and require intervention |

---

## Throttle Rules (T-###)

Throttle rules reduce unnecessary analysis.

### T-001: Excessive Columns for Risk Tier

**Purpose:** Prevent over-analysis relative to actual risk.

**Detection Logic:**
```
IF proposed_columns > max_columns_for_tier[risk_tier]
THEN trigger T-001
```

**Thresholds:**

| Risk Tier | Max Columns | Warning Threshold |
|-----------|-------------|-------------------|
| Trivial | 1 | 0 |
| Low | 2 | 1 |
| Medium | 3 | 2 |
| High | 5 | 3 |
| Critical | No limit | N/A |

**Action:** Suggest reducing column count

**Severity:** Advisory (can be overridden)

---

### T-002: Repeated Refinement With No New Signal

**Purpose:** Stop when columns are reporting the same findings.

**Detection Logic:**
```
IF column_N.findings ⊆ previous_columns.findings
   AND column_N adds no unique findings
THEN trigger T-002
```

**Action:** Suggest stopping - same findings already captured

**Severity:** Advisory

---

### T-003: All Columns Report Zero Findings

**Purpose:** Stop when multiple columns find nothing.

**Detection Logic:**
```
IF columns_completed >= 2
   AND total_findings == 0
   AND risk_tier != critical
THEN trigger T-003
```

**Action:** Change likely clean. Stop analysis.

**Severity:** Advisory (mandatory stop suggestion for Trivial/Low)

---

### T-004: Diminishing Returns Pattern

**Purpose:** Detect when additional columns add less value.

**Detection Logic:**
```
IF findings_per_column is strictly decreasing
   AND latest_column.findings <= 2
   AND at least 2 columns completed
THEN trigger T-004
```

**Example Pattern:**
- Column 1: 8 findings
- Column 2: 3 findings
- Column 3: 1 finding → T-004 triggered

**Action:** Suggest stopping - diminishing returns detected

**Severity:** Advisory

---

### T-005: Low-Risk With Strong Signals

**Purpose:** Allow early termination when low-risk with clean results.

**Detection Logic:**
```
IF risk_tier IN [trivial, low]
   AND first_column.findings <= 1
   AND all findings are low severity
THEN trigger T-005
```

**Action:** Suggest proceeding without additional columns

**Severity:** Advisory

---

## Escalate Rules (E-###)

Escalate rules increase scrutiny when signals indicate higher risk.

### E-001: Critical Findings in Low-Risk Assessment

**Purpose:** Catch when risk assessment underestimated severity.

**Detection Logic:**
```
IF risk_tier IN [trivial, low, medium]
   AND any finding.severity == critical
THEN trigger E-001
```

**Action:**
- Escalate risk_tier by 2 (minimum High)
- Add correctness column if not present
- Re-validate column plan

**Severity:** Mandatory

---

### E-002: Conflicting Artifacts Between Columns

**Purpose:** Prevent synthesis when columns disagree.

**Detection Logic:**
```
IF column_A.finding CONTRADICTS column_B.finding
THEN trigger E-002
```

**Examples of Conflicts:**
- Column A: "Form validation is correct"
- Column B: "Form allows invalid input"

**Action:**
- HALT synthesis
- Require human review
- Flag conflicting findings

**Severity:** Mandatory (halt)

---

### E-003: Novel Failure Mode Detected

**Purpose:** Flag failure patterns not in known anti-patterns.

**Detection Logic:**
```
IF finding describes failure mode
   AND failure mode NOT IN anti_patterns
   AND finding.severity >= medium
THEN trigger E-003
```

**Action:**
- Add failure-mode-simulator column
- Suggest creating new anti-pattern
- Flag for post-analysis review

**Severity:** Mandatory

---

### E-004: Proof Required But Missing

**Purpose:** Enforce proof requirements for critical tiers.

**Detection Logic:**
```
IF risk_tier == critical
   AND proof_required == true
   AND proofs_provided == false
THEN trigger E-004
```

**Action:**
- HALT synthesis
- Require proofs before proceeding

**Severity:** Mandatory (halt)

---

### E-005: Anti-Pattern Bypass Attempted

**Purpose:** Prevent skipping mandatory analysis.

**Detection Logic:**
```
IF anti_pattern.action == "add_column"
   AND anti_pattern.mandatory_columns NOT IN executed_columns
THEN trigger E-005
```

**Action:**
- HALT execution
- Report missing mandatory columns
- Require column execution before proceeding

**Severity:** Mandatory (halt)

---

### E-006: High-Severity Finding Density

**Purpose:** Escalate when many serious issues found.

**Detection Logic:**
```
IF high_severity_findings >= 3
   AND columns_completed <= 2
THEN trigger E-006
```

**Action:**
- Suggest adding failure-mode-simulator
- Consider escalating risk tier
- Flag for thorough review

**Severity:** Advisory (mandatory for auth/payment surfaces)

---

### E-007: Coverage Gaps Detected

**Purpose:** Escalate when analysis missed obvious areas.

**Detection Logic:**
```
IF surfaces_touched contains X
   AND no column analyzed X
THEN trigger E-007
```

**Example:**
- Change touches auth/* 
- No column specifically analyzed auth surface

**Action:**
- Flag coverage gap
- Suggest appropriate column
- Consider anti-pattern if repeated

**Severity:** Advisory

---

## Halt Rules (H-###)

Halt rules completely stop processing until resolved.

### H-001: Mandatory Column Missing

**Trigger:** E-005 (anti-pattern bypass)

**Resolution:** Execute mandatory column

---

### H-002: Proofs Missing for Critical

**Trigger:** E-004 (proof required)

**Resolution:** Provide required proofs

---

### H-003: Unresolved Conflicts

**Trigger:** E-002 (conflicting artifacts)

**Resolution:** Human reviews and resolves conflict

---

### H-004: Security Finding in Payment Flow

**Purpose:** Never auto-proceed past payment security issues.

**Detection Logic:**
```
IF surface == payment
   AND any finding.category == security
THEN trigger H-004
```

**Resolution:** Security review required

---

## Rule Evaluation Order

Rules are evaluated in this order:

1. **Halt rules (H-###)** - Check first, stop if triggered
2. **Escalate rules (E-###)** - Apply all triggered escalations
3. **Throttle rules (T-###)** - Apply only if no escalations active

**Note:** Escalation always overrides throttling. If both E-001 and T-001 trigger, escalation takes precedence.

## Rule Customization

Rules can be customized per-project via `meta/taste-profile.yaml`:

```yaml
governor_overrides:
  T-001:
    max_columns:
      low: 3          # Override: allow 3 columns for Low tier
  E-001:
    auto_escalate: false  # Require confirmation before escalating
```

## Adding New Rules

### Template

```yaml
rule_id: X-NNN
name: "Descriptive Name"
purpose: "What this rule prevents or ensures"
detection: "How to detect this condition"
action: "What to do when triggered"
severity: advisory | mandatory | halt
added: YYYY-MM-DD
triggers: 0               # Track how often rule fires
last_triggered: null
```

### Review Process

Before adding a rule:
1. Verify it addresses a real problem
2. Check for conflicts with existing rules
3. Determine appropriate severity
4. Add to relevant category (T/E/H)

## Rule Performance Tracking

Track rule effectiveness:

```yaml
rule_metrics:
  T-001:
    triggers_total: 47
    accepted: 38          # User followed suggestion
    overridden: 9         # User proceeded anyway
    override_outcomes:
      good: 6             # Override was correct
      bad: 3              # Should have throttled
  E-001:
    triggers_total: 12
    prevented_issues: 8   # Escalation caught real problem
    false_positives: 4    # Escalation was unnecessary
```

Review metrics quarterly to:
- Tune thresholds
- Adjust severity levels
- Retire ineffective rules
- Add missing rules

## See Also

- `skills/meta/strategic-governor.md` - Uses these rules
- `meta/risk-tiers.md` - Risk tier definitions
- `meta/anti-patterns.md` - Anti-pattern triggers
- `meta/taste-profile.yaml` - Rule customization

