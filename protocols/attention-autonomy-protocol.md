# Attention Autonomy Protocol

## Purpose

Define how the agent-skills system autonomously decides where attention is valuable, without requiring human invocation for every decision. This protocol enables the shift from "you invoke skills" to "the system notices what needs attention."

## Core Principle

> **The system should know where to look before you ask.**

Autonomous attention routing means:
- Changes trigger appropriate analysis automatically
- Staleness is detected and flagged
- Anomalies surface without being queried
- "Do nothing" is an explicit, logged decision

## Protocol Components

This protocol coordinates three layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIGGER LAYER                             │
│  (Change Events, Scheduled Checks, Anomaly Detection)       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ASSESSMENT LAYER                           │
│  (Health Assessor, Drift Detector, Amplification Detector)  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   GOVERNANCE LAYER                           │
│  (Column Router, Strategic Governor, Readiness Certifier)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     OUTPUT LAYER                             │
│  (Findings, Certificates, No-Op Decisions, Feedback)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Trigger Layer

### 1.1 Change Events (Git-Based)

When integrated with git hooks or CI pipelines:

```yaml
change_event_triggers:
  # On every commit
  on_commit:
    - pattern: "skills/**/*.md"
      action: queue_health_assessment
      surface: agent-skills
      priority: high
      
    - pattern: "meta/**/*"
      action: queue_health_assessment
      surface: meta-system
      priority: critical
      escalate: true
      
    - pattern: "protocols/**/*.md"
      action: queue_drift_check
      surface: protocols
      priority: high
      
    - pattern: "TEMPLATE.md"
      action: queue_amplification_check
      priority: high
      reason: "Template changes affect all future skills"
      
    - pattern: "*.yaml"
      action: queue_validation
      priority: medium
      
  # On pull request
  on_pr:
    - condition: files_changed > 5
      action: require_column_router
      approval_required: true
      
    - condition: touches_critical_surface
      action: require_full_audit
      block_merge: true
      
  # On merge to main
  on_merge:
    - branch: main
      action: queue_readiness_check
      
    - branch: release/*
      action: require_certification
      block_deploy: true
```

### 1.2 Scheduled Triggers (Temporal)

Regular checks regardless of changes:

```yaml
scheduled_triggers:
  # Daily
  daily:
    - skill: health-assessor
      scope: high_velocity_surfaces
      at: "06:00 UTC"
      
    - skill: skill-effectiveness-analyzer
      mode: feedback-ingestion
      at: "07:00 UTC"
      
  # Weekly  
  weekly:
    - skill: documentation-drift-detector
      scope: all_surfaces
      day: monday
      at: "08:00 UTC"
      
    - skill: skill-effectiveness-analyzer
      mode: full-scan
      day: friday
      at: "16:00 UTC"
      
  # Monthly
  monthly:
    - skill: readiness-certifier
      scope: full_project
      day: 1
      at: "09:00 UTC"
      
    - action: lifecycle_review
      description: "Review skill promotions/demotions"
      requires: human_approval
```

### 1.3 Anomaly Triggers (Reactive)

Event-driven triggers based on system state:

```yaml
anomaly_triggers:
  # Skill failure patterns
  - condition: "Same skill fails 3x in 24h"
    action:
      - flag_skill_for_review
      - suggest_demotion
      - notify_human
    severity: high
    
  # Governor interventions
  - condition: "Governor halts 2x on same surface in 7 days"
    action:
      - escalate_surface_risk_tier
      - notify_human
      - require_human_triage
    severity: critical
    
  # Trust score decline
  - condition: "Trust score drops > 0.1 in 7 days"
    action:
      - queue_effectiveness_analysis
      - alert_declining_skill
    severity: medium
    
  # Stale skills
  - condition: "Skill not used in 30 days"
    action:
      - flag_as_potentially_stale
      - include_in_next_audit
    severity: low
    
  # Coverage gaps
  - condition: "Routing fails to match for 3 different intents"
    action:
      - invoke_skill_gap_detector
      - propose_new_skill
    severity: medium
```

---

## 2. Attention Budget

Prevent infinite analysis loops and resource exhaustion:

```yaml
attention_budget:
  # Daily limits
  daily:
    max_autonomous_runs: 10
    max_columns_total: 20
    max_skills_invoked: 30
    
  # Per-surface limits
  per_surface:
    cooldown_after_assessment: 4h
    max_assessments_per_day: 3
    max_assessments_per_week: 10
    
  # Cost thresholds
  cost_limits:
    max_daily_token_budget: 100000
    warn_at_percentage: 80
    
  # Override conditions
  escalation_override:
    # These ignore budget constraints:
    - critical_findings_detected
    - governor_halt_active
    - security_vulnerability_found
    - human_explicit_request
    
  # Budget exhaustion behavior
  on_budget_exhausted:
    action: defer_to_next_period
    notify: true
    log: true
    priority_queue: enabled  # Critical items still processed
```

---

## 3. Explicit No-Op Artifact

When the system decides **no action is needed**, it must say so explicitly. This prevents the "did it check or did it forget?" ambiguity.

### No-Op Decision Structure

```yaml
no_action_decision:
  # Metadata
  timestamp: "2026-01-10T12:00:00Z"
  target: prompt-library
  trigger: scheduled_daily_check
  
  # Decision
  decision: NO_ACTION_NEEDED
  
  # Evidence
  assessment_performed:
    skill: health-assessor
    mode: intentless
    duration_ms: 1250
    
  # Reasoning
  reasoning:
    - "No changes to high-risk surfaces since last assessment"
    - "All trust scores stable (variance < 0.02)"
    - "No drift detected in documentation"
    - "Governor has no pending escalations"
    
  # Surface status
  surface_status:
    agent-skills:
      status: clean
      last_change: "2026-01-08T14:30:00Z"
      last_validated: "2026-01-09T06:00:00Z"
      
    meta-system:
      status: clean
      last_change: "2026-01-05T09:15:00Z"
      last_validated: "2026-01-09T06:00:00Z"
      
    documentation:
      status: clean
      drift_score: 0.05
      last_validated: "2026-01-06T08:00:00Z"
      
  # Next scheduled check
  next_scheduled_check: "2026-01-11T06:00:00Z"
  
  # Override instruction
  override_with: |
    To force assessment despite this decision:
    "Force health assessment on prompt-library"
    or
    "Override no-op and run full audit"
```

### Why No-Op Artifacts Matter

1. **Auditability**: Know that the system checked, even when nothing was found
2. **Confidence**: Explicit "nothing needed" is different from "didn't check"
3. **Debugging**: If issues arise, no-op logs help reconstruct what was evaluated
4. **Learning**: Pattern of no-ops can inform trigger refinement

---

## 4. Attention Routing Flow

### Standard Flow

```
1. TRIGGER DETECTED
   │
   ├─ Change event?  ──────────────────────┐
   ├─ Scheduled check? ────────────────────┤
   └─ Anomaly detected? ───────────────────┤
                                           │
2. CHECK BUDGET ◄──────────────────────────┘
   │
   ├─ Budget available? ───► Continue
   └─ Budget exhausted? ───► Queue for next period (unless override)
   │
3. RUN ASSESSMENT
   │
   ├─ Health Assessor (for general triggers)
   ├─ Drift Detector (for doc-related triggers)
   └─ Amplification Detector (for high-impact triggers)
   │
4. EVALUATE RESULTS
   │
   ├─ No concerns? ────────► Emit NO_ACTION_DECISION
   │
   └─ Concerns found? ─────► Continue to governance
   │
5. GOVERNANCE
   │
   ├─ Column Router (plan analysis depth)
   ├─ Strategic Governor (validate proportionality)
   └─ Skill Router (select appropriate skills)
   │
6. EXECUTE ANALYSIS
   │
   └─ Run planned columns/skills
   │
7. SYNTHESIZE & OUTPUT
   │
   ├─ Generate findings
   ├─ Update trust scores (if feedback-ingestion)
   └─ Propose lifecycle transitions
   │
8. CLOSE LOOP
   │
   ├─ Log execution
   ├─ Update last_assessed timestamps
   └─ Schedule next check
```

### Escalation Flow

```
1. CRITICAL TRIGGER DETECTED
   │
   ├─ Governor halt
   ├─ Critical finding
   └─ Security issue
   │
2. BYPASS BUDGET ──────► Override attention limits
   │
3. ESCALATE RISK TIER ─► Force higher scrutiny
   │
4. REQUIRE HUMAN ──────► Block until human review
   │
5. EXECUTE WITH OVERSIGHT
   │
   └─ Human must approve before proceeding
```

---

## 5. Integration Points

### Git Hook Integration

Example pre-commit hook:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Extract changed files
CHANGED_FILES=$(git diff --cached --name-only)

# Check for high-risk patterns
if echo "$CHANGED_FILES" | grep -q "^meta/\|^protocols/"; then
    echo "⚠️  High-risk files modified. Queuing assessment..."
    # Queue attention check (implementation depends on your setup)
    curl -X POST http://localhost:8080/attention/queue \
         -d "trigger=pre-commit&files=$CHANGED_FILES"
fi
```

### CI Pipeline Integration

Example GitHub Actions:

```yaml
# .github/workflows/attention-check.yml
name: Attention Check

on:
  push:
    branches: [main]
  pull_request:

jobs:
  attention-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Health Assessment
        run: |
          # Invoke health-assessor
          warp --skill health-assessor --mode change-triggered \
               --changed-files "${{ github.event.changed_files }}"
               
      - name: Check for Blockers
        run: |
          # Parse health assessment output
          if grep -q "overall_health: DEGRADED" assessment.yaml; then
            echo "::error::Health assessment detected degraded state"
            exit 1
          fi
```

### Warp Agent Integration

```yaml
# warp-config.yaml
attention_autonomy:
  enabled: true
  
  triggers:
    on_session_start:
      - skill: health-assessor
        mode: quick
        
    on_idle:
      interval: 30m
      action: check_scheduled_tasks
      
  notifications:
    slack_webhook: ${SLACK_WEBHOOK_URL}
    notify_on:
      - critical_findings
      - governor_halts
      - readiness_blocked
```

---

## 6. Configuration

### Attention Autonomy Config File

```yaml
# .agent-skills/attention-config.yaml

# Enable/disable autonomous attention
enabled: true

# Trigger configuration
triggers:
  change_events: true
  scheduled: true
  anomaly_detection: true
  
# Budget configuration  
budget:
  daily_runs: 10
  daily_columns: 20
  cooldown_hours: 4
  
# Notification preferences
notifications:
  on_critical: always
  on_no_op: daily_summary
  channel: slack  # or email, webhook, etc.
  
# Override permissions
overrides:
  allow_budget_override: [critical, governor_halt]
  require_human_for: [lifecycle_transitions, skill_retirement]
  
# Logging
logging:
  log_no_ops: true
  log_decisions: true
  retention_days: 90
```

---

## 7. Observability

### Attention Metrics to Track

```yaml
attention_metrics:
  # Volume metrics
  - triggers_per_day
  - assessments_per_day
  - no_ops_per_day
  - escalations_per_day
  
  # Efficiency metrics
  - budget_utilization_percentage
  - average_assessment_duration
  - findings_per_assessment
  
  # Quality metrics
  - false_positive_rate_on_triggers
  - missed_issues_rate  # Issues found manually that should have been caught
  - human_override_rate
  
  # Health metrics
  - surfaces_with_stale_validation
  - skills_with_declining_trust
  - outstanding_escalations
```

### Dashboard Queries

```yaml
# Example queries for attention dashboard

daily_summary:
  query: |
    SELECT 
      DATE(timestamp) as date,
      COUNT(*) as total_assessments,
      SUM(CASE WHEN decision = 'NO_ACTION_NEEDED' THEN 1 ELSE 0 END) as no_ops,
      SUM(CASE WHEN findings_count > 0 THEN 1 ELSE 0 END) as actionable
    FROM attention_log
    WHERE timestamp > NOW() - INTERVAL '7 days'
    GROUP BY DATE(timestamp)

escalation_trend:
  query: |
    SELECT 
      DATE(timestamp) as date,
      trigger_type,
      COUNT(*) as count
    FROM escalations
    WHERE timestamp > NOW() - INTERVAL '30 days'
    GROUP BY DATE(timestamp), trigger_type
```

---

## 8. Evolution and Tuning

### Self-Improvement Mechanisms

The attention autonomy system should improve over time:

1. **Trigger Refinement**
   - Track false positive rate per trigger pattern
   - Adjust trigger sensitivity based on outcomes
   - Retire triggers that never fire or always fire

2. **Budget Optimization**
   - Analyze budget utilization patterns
   - Adjust limits based on actual needs
   - Identify waste (runs that produce no findings)

3. **Priority Tuning**
   - Learn which surfaces actually produce issues
   - Adjust risk weights based on historical data
   - Deprioritize surfaces that are always clean

### Review Cadence

```yaml
attention_system_review:
  weekly:
    - Review escalation patterns
    - Check budget utilization
    
  monthly:
    - Analyze trigger effectiveness
    - Review no-op patterns
    - Adjust risk weights if needed
    
  quarterly:
    - Full attention system audit
    - Retire ineffective triggers
    - Propose new trigger patterns
```

---

## See Also

- `skills/meta/health-assessor.md` - Primary assessment skill
- `skills/meta/readiness-certifier.md` - Certification output
- `skills/meta/column-router.md` - Analysis planning
- `skills/meta/strategic-governor.md` - Governance layer
- `meta/risk-tiers.md` - Risk classification
- `.agent-skills/skill-map.yaml` - Project contract
