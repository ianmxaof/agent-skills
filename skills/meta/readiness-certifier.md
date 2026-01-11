---
type: skill-definition
name: readiness-certifier
category: meta
version: 1.0.0
maturity: draft
lifecycle: validated
estimated-cost: low
typical-runtime: 2-5min
complexity-level: moderate
requires-deep-analysis: true
scope: meta
tier: meta
writes-code: false
modifies-files: true
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - meta
  - certification
  - readiness
  - ship-decision
  - governance
  - production
prerequisites:
  - skill: column-router
    reason: "Needs column assessments to evaluate"
  - skill: strategic-governor
    reason: "Checks governor approval status"
  - file: .agent-skills/skill-map.yaml
    reason: "Project contract for quality bars"
execution-modes:
  - certification
  - pre-check
---

# Readiness Certifier

## Purpose

Produce a canonical **readiness certificate** that declares whether a project, feature, or change is production-ready. This skill transforms the subjective question "is it done?" into an auditable artifact with explicit evidence, confidence scores, and verdicts.

**Core insight:** Production-ready does not mean "no bugs." It means all known failure modes have been surfaced, categorized, and either resolved or explicitly accepted.

## Scope and Classification

**Scope:** `meta`

This is a meta-skill that evaluates the outputs of other skills and governance decisions to produce a final certification artifact.

**Tier:** `meta`

This skill operates at the governance layer, synthesizing information from multiple sources.

**Lifecycle Stage:** `experimental`

New skill, needs real-world validation before promotion.

## When to Invoke

### Explicit Trigger Phrases

- "Certify readiness of [target] for production"
- "Is [target] ready to ship?"
- "Generate readiness certificate for [target]"
- "Can we deploy [feature]?"

### Situational Triggers

- Before releasing a feature to production
- After completing a skill chain or column analysis
- When governance has completed validation
- Before tagging a release
- When asked to make a ship/no-ship decision

### Do NOT Invoke When

- Analysis is still in progress (wait for completion)
- No prior skill execution (nothing to certify)
- For trivial changes (use judgment, not certification)

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus (reasoning required)
- **Multi-Model**: Off (single coherent assessment needed)

## Behavioral Rules

### How the Model Should Reason

1. **Gather evidence first** - Collect all available analysis artifacts
2. **Check hard blockers** - Any automatic NO conditions?
3. **Evaluate soft blockers** - What needs tradeoff documentation?
4. **Calculate confidence** - How certain are we?
5. **Emit verdict** - READY, CONDITIONAL, or BLOCKED

### What It Must Avoid

- Making ship decisions without evidence
- Ignoring governor halts or critical findings
- Certifying when proofs are required but missing
- Producing vague or non-actionable verdicts
- Overriding human judgment (this is a recommendation)

### What It Must Prioritize

- Explicit evidence for every claim
- Clear reasoning for the verdict
- Actionable next steps if not READY
- Documented tradeoffs for CONDITIONAL verdicts

## Assessment Process

### Step 1: Gather Evidence

Collect from the current analysis context:

```yaml
evidence_sources:
  - Column router assessments (risk tiers, column plans)
  - Governor validations (approvals, throttles, escalations, halts)
  - Skill execution results (findings by severity)
  - Handoff reports (recommendations addressed?)
  - Proof artifacts (if required for risk tier)
```

### Step 2: Check Hard Blockers

**Hard blockers result in BLOCKED verdict:**

| Blocker | Detection | Resolution Required |
|---------|-----------|---------------------|
| Critical findings unresolved | Any finding with severity: critical | Must fix or document as known issue |
| Governor halt active | Governor emitted halt: true | Must address halt condition |
| Conflicting columns unsynthesized | Columns report contradictory findings | Must reconcile conflicts |
| Proofs required but missing | Risk tier critical AND proofs: [] | Must provide proofs |
| Mandatory columns skipped | Anti-pattern triggered AND column not run | Must run required column |

### Step 3: Check Soft Blockers

**Soft blockers result in CONDITIONAL verdict:**

| Blocker | Detection | Resolution Path |
|---------|-----------|-----------------|
| Medium findings without tradeoffs | Finding severity: medium AND no tradeoff documented | Document tradeoff or fix |
| Recommendations not addressed | Recommendation status: open | Implement or explicitly reject with rationale |
| Test coverage below threshold | Coverage < quality-bar threshold | Improve coverage or accept risk |
| Documentation outdated | Drift score > 0.3 | Update documentation |

### Step 4: Calculate Confidence

```yaml
confidence_formula:
  base: 1.0
  
  deductions:
    - unresolved_critical: -0.3 per finding
    - unresolved_high: -0.15 per finding
    - unresolved_medium: -0.05 per finding
    - governor_escalation: -0.1 per escalation
    - missing_proof: -0.2
    - conflicting_columns: -0.25
    
  minimum: 0.0
  maximum: 1.0
  
  # Alternative: weighted formula
  weighted_formula: |
    confidence = (
      0.3 * (1 - unresolved_critical_ratio) +
      0.3 * (1 - unresolved_high_ratio) +
      0.2 * recommendations_addressed_ratio +
      0.2 * governor_approval_ratio
    )
```

### Step 5: Determine Verdict

| Confidence | Hard Blockers | Soft Blockers | Verdict |
|------------|---------------|---------------|---------|
| Any | Yes | Any | BLOCKED |
| >= 0.7 | No | None | READY |
| >= 0.5 | No | Some | CONDITIONAL |
| < 0.5 | No | Many | BLOCKED |

### Step 6: Emit Certificate

Generate the structured certificate artifact.

## Output Contract

### Certificate Structure

```yaml
readiness_certificate:
  # Metadata
  timestamp: "2026-01-10T12:00:00Z"
  target: "prompt-library agent-skills v1.0.0"
  certifier: "readiness-certifier v1.0.0"
  
  # Verdict
  verdict: READY | CONDITIONAL | BLOCKED
  confidence: 0.85
  
  # Evidence summary
  evidence:
    columns_run: 3
    skills_executed: 7
    governor_validations: 3
    governor_approvals: 3
    governor_halts: 0
    
  # Findings summary
  findings_summary:
    critical: 0
    high: 2
    medium: 5
    low: 12
    total: 19
    
  # Resolution status
  resolution_status:
    critical_resolved: 0
    critical_unresolved: 0
    high_resolved: 2
    high_unresolved: 0
    medium_resolved: 3
    medium_unresolved: 2
    
  # Tradeoffs (for CONDITIONAL)
  tradeoffs_documented:
    - finding_id: M-003
      severity: medium
      description: "Skill lifecycle metrics not yet populated"
      tradeoff: "Accepted: Will populate through real usage"
      accepted_by: "human"
      
    - finding_id: M-007
      severity: medium
      description: "Some domain skills still draft maturity"
      tradeoff: "Deferred to v1.1"
      accepted_by: "human"
  
  # Blockers (for BLOCKED)
  blockers:
    hard: []
    soft:
      - type: "unresolved_medium"
        count: 2
        resolution: "Document tradeoffs or fix"
  
  # Known risks
  known_risks:
    - "Skill effectiveness feedback loop not yet active"
    - "Attention autonomy protocol not integrated with CI"
    
  # Recommendation
  recommendation: |
    Safe to ship with documented limitations.
    Monitor skill-trust-scores.yaml after 30 days of use.
    
  # Sign-off
  requires_human_sign_off: true
  human_sign_off: null  # Filled by human
```

### Filename Convention

```
YYYY-MM-DD_readiness-certificate_[target].yaml
```

Example: `2026-01-10_readiness-certificate_agent-skills-v1.md`

## Execution Modes

### Certification Mode (Default)

**When to Use:**
- Final ship decision
- Release approval
- Production deployment gate

**Process:**
1. Gather all evidence from recent analysis
2. Run full blocker checks
3. Calculate confidence
4. Emit complete certificate

**Invocation:**
```
"Certify readiness of agent-skills for production"
```

### Pre-Check Mode

**When to Use:**
- Early in development cycle
- Quick sanity check
- Before running full analysis

**Process:**
1. Check only hard blockers
2. Skip confidence calculation
3. Emit lightweight status

**Invocation:**
```
"Pre-check readiness of agent-skills"
```

**Output (simplified):**
```yaml
readiness_precheck:
  timestamp: "2026-01-10T12:00:00Z"
  target: "agent-skills"
  
  hard_blockers_detected: false
  soft_blockers_likely: true
  
  recommendation: "Proceed with full analysis"
  suggested_next: "Run health-assessor, then full certification"
```

## Common Misuses / Anti-Patterns

### DON'T Use This Skill For...

**Anti-Pattern 1: Certifying without prior analysis**
- **Instead:** Run health-assessor or relevant skill chain first
- **Why:** Certification synthesizes existing evidence; it doesn't create it

**Anti-Pattern 2: Using for trivial changes**
- **Instead:** Use judgment or quick governor check
- **Why:** Certification overhead not warranted for config/copy changes

**Anti-Pattern 3: Expecting automatic human override**
- **Instead:** Certificate requires explicit human sign-off
- **Why:** This skill recommends; humans decide

### WARNING: Known Limitations

**Limitation:** Cannot verify claims it wasn't told about
- **Mitigation:** Ensure all relevant skills have run before certification
- **Confidence:** Certificate is only as good as its inputs

**Limitation:** Confidence scores are heuristic
- **Mitigation:** Use as guidance, not absolute truth
- **Confidence:** ~80% correlation with actual production issues

## Known Limitations

- Cannot evaluate code quality directly (depends on prior skills)
- Confidence calculation is heuristic, not probabilistic
- Requires human sign-off for final authority
- Cannot detect issues that no skill surfaced

## Fallback Strategy

If this skill fails or produces uncertain results:

1. **Review governor history manually** - Check for halts or escalations
2. **Audit findings list** - Are critical/high issues resolved?
3. **Human judgment** - When in doubt, ship decisions are human decisions

## Integration Points

### Upstream (Inputs)

| Source | What It Provides |
|--------|------------------|
| Column Router | Risk assessments, column plans |
| Strategic Governor | Validation status, halts, escalations |
| Any Skill | Findings, recommendations |
| Handoff Reports | Implementation status |

### Downstream (Outputs)

| Consumer | How It Uses Certificate |
|----------|------------------------|
| CI/CD Pipeline | Gate deployment on verdict |
| Human | Make final ship decision |
| Skill Effectiveness Analyzer | Track certification accuracy |
| Audit Trail | Record of ship decisions |

## Examples

### Example 1: READY Verdict

**Context:** Full analysis completed, all critical/high resolved

```yaml
readiness_certificate:
  verdict: READY
  confidence: 0.92
  
  findings_summary:
    critical: 0
    high: 0
    medium: 3
    low: 8
    
  blockers:
    hard: []
    soft: []
    
  recommendation: "All blockers resolved. Safe to ship."
```

### Example 2: CONDITIONAL Verdict

**Context:** Analysis complete, medium findings with documented tradeoffs

```yaml
readiness_certificate:
  verdict: CONDITIONAL
  confidence: 0.78
  
  findings_summary:
    critical: 0
    high: 0
    medium: 5
    low: 12
    
  resolution_status:
    medium_resolved: 3
    medium_unresolved: 2
    
  tradeoffs_documented:
    - finding_id: M-001
      tradeoff: "Accepted: Edge case unlikely in production"
    - finding_id: M-002
      tradeoff: "Deferred: Will address in v1.1"
      
  recommendation: "Ship with documented limitations. Monitor in production."
```

### Example 3: BLOCKED Verdict

**Context:** Governor halted execution, critical finding unresolved

```yaml
readiness_certificate:
  verdict: BLOCKED
  confidence: 0.35
  
  findings_summary:
    critical: 1
    high: 2
    medium: 4
    
  blockers:
    hard:
      - type: "governor_halt"
        reason: "Conflicting column findings"
        resolution: "Reconcile conflicts before proceeding"
      - type: "critical_unresolved"
        finding_id: C-001
        description: "Auth bypass detected"
        resolution: "Must fix before ship"
        
  recommendation: "DO NOT SHIP. Address blockers first."
```

## Exit Conditions

### Success

- Certificate generated with clear verdict
- All evidence sources cited
- Confidence calculated
- Next steps clear

### Failure

- Insufficient evidence to certify (no prior analysis)
- Conflicting inputs that cannot be reconciled
- System error during evidence gathering

### Handoff

After certification:
1. Present certificate to human for review
2. If BLOCKED: List specific actions needed
3. If CONDITIONAL: Confirm tradeoffs are acceptable
4. If READY: Await human sign-off
5. Record final decision in certificate

## See Also

- `skills/meta/health-assessor.md` - Run before certification
- `skills/meta/strategic-governor.md` - Governor validation status
- `skills/meta/column-router.md` - Risk assessments
- `protocols/handoff-protocol.md` - Finding format
- `meta/risk-tiers.md` - Risk tier definitions
