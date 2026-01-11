---
name: skill-effectiveness-analyzer
category: meta
version: 1.1.0
maturity: draft
lifecycle: experimental
estimated-cost: low
typical-runtime: 2-5min
complexity-level: simple
requires-deep-analysis: false
scope: meta
tier: meta
writes-code: false
modifies-files: true
handoff-protocol: standard-v1
meta-skill: true
tags:
  - meta
  - effectiveness
  - tracking
  - improvement
  - analytics
  - usage
  - feedback-loop
  - trust-scores
prerequisites: []
execution-modes:
  - full-scan
  - targeted
  - feedback-ingestion
constraints:
  - Never edits code
  - Never edits skills directly
  - Only proposes decisions for lifecycle changes
  - May update skill-trust-scores.yaml in feedback-ingestion mode
---

# Skill Effectiveness Analyzer

## Purpose

Validates that skills are actually useful (not just theoretical). Tracks usage, measures issue detection rate, analyzes false positive rate, and proposes skill improvements or retirement.

## Explicit Boundaries (CRITICAL)

This is a **meta-skill** with strict boundaries to prevent recursive chaos:

### ❌ NEVER Does This

1. **Never edits code**
   - Only analyzes and proposes
   - Does not modify any source code files
   - Does not implement recommendations

2. **Never edits skills directly**
   - Does not modify skill definition files
   - Does not update skill front matter
   - Does not change skill content

3. **Only proposes decisions**
   - Proposes retire/refine/merge decisions
   - Proposes improvements
   - Never executes changes

4. **Never executes changes**
   - All recommendations are proposals only
   - Human review required before any changes
   - Output is structured recommendations, not implementations

### ✅ ONLY Does This

1. **Analyzes skill usage data**
   - Reads observability logs
   - Calculates metrics
   - Identifies patterns

2. **Produces structured recommendations**
   - Handoff report with findings
   - Prioritized recommendations
   - Effort estimates

3. **Documents analysis**
   - Usage statistics
   - Effectiveness metrics
   - Improvement opportunities

### Output Format

All output must be:
- **Structured recommendations only**
- **No implementation code**
- **No file modifications**
- **Proposals that require human review**

See "Output Contract" section for detailed handoff report structure.

## When to Invoke

### Explicit Trigger Phrases

- "Run skill-effectiveness-analyzer on [skill/skills]"
- "Analyze skill effectiveness"
- "Check skill usage statistics"
- "Evaluate skill performance"

### Situational Triggers

- Periodically (monthly/quarterly)
- When skill usage is low
- When false positive rate is high
- Before retiring skills
- During skill maintenance

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Track how often each skill is invoked (from observability logs)
- Measure issue detection rate (findings per invocation)
- Analyze false positive rate
- Propose skill improvements or retirement
- Document lessons learned
- Compare skill effectiveness

### What It Must Avoid

- Don't suggest retiring skills without sufficient data
- Don't ignore context (some skills may be rarely used but critical)
- Don't miss improvement opportunities
- Don't assume low usage means useless

### What It Must Prioritize

- Low usage skills (High - candidates for retirement)
- High false positive rate (High - needs improvement)
- Low detection rate (Medium - may need improvement)
- Improvement opportunities (Medium - enhance skills)
- Retirement candidates (Low - after sufficient data)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive skill effectiveness audit
- Periodic review
- Initial effectiveness assessment

**Input:**
- Observability logs (`.skill-usage/`)
- Skill definitions
- Usage statistics
- Detection rates

**Process:**
1. Analyze usage statistics
2. Calculate detection rates
3. Measure false positive rates
4. Identify improvement opportunities
5. Propose retirements
6. Generate comprehensive effectiveness report

**Invocation Example:**
> "Run skill-effectiveness-analyzer in full-scan mode on all skills"

### Targeted Mode

**When to Use:**
- Analyzing specific skill
- Validating single skill effectiveness
- Focused effectiveness check

**Input:**
- Specific skill
- Targeted usage data

**Process:**
1. Deep analysis of target skill
2. Calculate effectiveness metrics
3. Identify improvements
4. Provide focused recommendations

**Invocation Example:**
> "Run skill-effectiveness-analyzer in targeted mode on philosophy-compliance-enforcer"

### Feedback Ingestion Mode (NEW)

**When to Use:**
- Automatic trust score updates
- After skill chain completion
- On weekly schedule
- Closing the effectiveness feedback loop

**Purpose:**
This mode enables the system to automatically learn from execution results. Instead of waiting for human-triggered analysis, feedback-ingestion mode processes execution logs and updates trust scores automatically, closing the feedback loop.

**Input:**
- `.skill-usage/*.jsonl` - Execution logs
- `meta/skill-trust-scores.yaml` - Current trust data
- Recent handoff reports (optional) - For actionable rate calculation

**Process:**
1. Read new execution logs since last ingestion
2. Calculate metrics per skill:
   - Success rate (executions without errors)
   - Average runtime vs estimated
   - Error patterns
3. Cross-reference with handoff outcomes (if available):
   - Did findings lead to changes? (actionable_rate)
   - Were findings overridden? (override_rate)
4. Update `skill-trust-scores.yaml`:
   - Recalculate trust_score
   - Update usage_count, last_used
   - Flag lifecycle transitions
5. Generate ingestion report

**Invocation Examples:**
```
"Ingest skill effectiveness feedback"
"Update skill trust scores from recent executions"
"Run skill-effectiveness-analyzer in feedback-ingestion mode"
```

**Automatic Trigger:**
This mode can be triggered automatically:
- After any skill chain completes
- Weekly via scheduled task
- When `.skill-usage/` has new entries

**Output: Feedback Ingestion Report**

```yaml
feedback_ingestion_report:
  timestamp: "2026-01-10T12:00:00Z"
  ingestion_window:
    from: "2026-01-03T00:00:00Z"
    to: "2026-01-10T12:00:00Z"
  
  executions_processed: 47
  skills_updated: 12
  
  # Per-skill updates
  skill_updates:
    - skill: adversarial-ui-tester
      executions: 8
      success_rate: 0.875
      avg_runtime_seconds: 245
      estimated_runtime_seconds: 300
      
      metrics_updated:
        actionable_rate:
          previous: 0.72
          current: 0.78
          delta: +0.06
        false_positive_rate:
          previous: 0.15
          current: 0.12
          delta: -0.03
          
      trust_score:
        previous: 0.82
        current: 0.85
        delta: +0.03
        
    - skill: bundle-size-analyzer
      executions: 3
      success_rate: 0.67
      
      metrics_updated:
        actionable_rate:
          previous: 0.70
          current: 0.65
          delta: -0.05
          
      trust_score:
        previous: 0.70
        current: 0.65
        delta: -0.05
        
      alert: "Trust score declining - review skill performance"
  
  # Lifecycle transitions proposed
  lifecycle_transitions_proposed:
    - skill: architecture-review
      from: validated
      to: preferred
      reason: "10+ uses, 72% actionable rate, meets promotion criteria"
      requires_approval: true
      
  # Alerts
  alerts:
    - skill: failure-mode-simulator
      type: stale
      message: "No executions in 30 days"
      suggestion: "Consider in next audit or verify still needed"
      
    - skill: bundle-size-analyzer
      type: declining_trust
      message: "Trust score dropped 0.05 in one week"
      suggestion: "Review recent false positives"
  
  # Files modified
  files_modified:
    - path: meta/skill-trust-scores.yaml
      changes: 12  # skill entries updated
      
  # Next scheduled ingestion
  next_ingestion: "2026-01-17T12:00:00Z"
```

**Behavioral Rules for Feedback Ingestion:**

1. **DO automatically update** `skill-trust-scores.yaml`:
   - usage_count
   - last_used
   - trust_score
   - metrics (actionable_rate, false_positive_rate, override_rate)

2. **DO NOT automatically change** lifecycle stage:
   - Lifecycle transitions are PROPOSED only
   - Requires human approval
   - Exception: automatic legacy flagging after 90 days no use (configurable)

3. **DO alert on anomalies:**
   - Trust score drops > 0.1 in one week
   - No executions in 30+ days
   - Error rate > 30%

4. **DO track ingestion history:**
   - Log ingestion timestamps
   - Prevent duplicate processing
   - Enable delta calculations

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Skill Quality Validation**
- **Instead:** Use skill-health-check for skill definition validation
- **Why:** This skill analyzes effectiveness, not skill definition quality.

**Anti-Pattern 2: Handoff Report Validation**
- **Instead:** Use handoff-quality-validator for report validation
- **Why:** This skill evaluates skill usage, not report quality.

### ⚠️ WARNING: Known Limitations

**Limitation:** Requires observability logs to be enabled
- **Mitigation:** Recommend enabling observability logging. Without logs, analysis is limited.
- **Confidence:** ~95% accuracy with logs, ~50% without logs

## Known Limitations

- Requires observability logs (may not be available)
- Cannot measure actual user value (only usage metrics)
- May miss context-dependent effectiveness
- Cannot verify effectiveness in production

## Fallback Strategy

If this skill fails, try:

1. **Manual review**: Review skill usage manually
2. **User feedback**: Collect user feedback on skill effectiveness
3. **Targeted mode**: Focus on specific skills
4. **Usage analytics**: Analyze skill usage patterns manually

## Lifecycle Management

This skill is responsible for updating skill lifecycle data in `meta/skill-trust-scores.yaml`.

### Trust Score Calculation

For each skill analyzed, calculate trust score:

```
trust_score = (
    0.4 * actionable_rate +
    0.3 * (1 - false_positive_rate) +
    0.2 * (1 - override_rate) +
    0.1 * recency_factor
)
```

### Lifecycle Recommendations

Based on analysis, propose lifecycle transitions:

**Promotion Recommendations:**
- `experimental → validated`: 3+ uses, >50% actionable rate
- `validated → preferred`: 10+ uses, >70% actionable rate, <15% override rate
- `preferred → default`: 25+ uses, consistent performance

**Demotion Recommendations:**
- Any → `legacy`: Not used in 90 days, or superseded
- `legacy → deprecated`: Not used after legacy status
- Performance demotion: actionable rate <60%, override rate >25%

### Output: Lifecycle Updates

Include in handoff report:

```yaml
lifecycle_recommendations:
  promotions:
    - skill: adversarial-ui-tester
      from: validated
      to: preferred
      reason: "47 uses, 78% actionable rate, 8% override rate"
  demotions:
    - skill: legacy-code-scanner
      from: validated
      to: legacy
      reason: "No use in 95 days"
  trust_score_updates:
    adversarial-ui-tester:
      previous: 0.72
      current: 0.85
      change: +0.13
```

### Integration with skill-trust-scores.yaml

After human approval, updates should be applied to `meta/skill-trust-scores.yaml`:
- Update `lifecycle` field
- Update `trust_score` field
- Update `metrics` fields
- Add entry to `lifecycle_history`

**Important:** This skill only PROPOSES changes. Human must apply them.

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Skills analyzed
   - Usage data source
   - Analysis scope

2. **Findings**
   - Low usage skills (High/Medium/Low)
   - High false positive rates
   - Low detection rates
   - Improvement opportunities
   - Each finding includes metrics and recommendations

3. **Lifecycle Analysis**
   - Current lifecycle stage per skill
   - Proposed promotions
   - Proposed demotions
   - Trust score changes

4. **Recommendations**
   - Skill improvements (prioritized)
   - Retirement candidates
   - Lifecycle transitions
   - Usage improvements
   - Documentation updates
   - Each with effort estimate

4. **Implementation Steps**
   - Ordered improvements
   - Skill updates
   - Retirement processes

5. **Files to Modify/Create**
   - Skill definition files
   - Documentation files
   - Retirement documentation

6. **Dependencies**
   - Observability logs referenced
   - Skill definitions

### Filename Convention

Reports must follow: `YYYY-MM-DD_skill-effectiveness-analyzer_target-component.md`

## Exit Conditions

### Success

- Skill effectiveness analyzed
- Improvements identified
- Retirement candidates found
- Handoff report generated

### Failure

- No observability logs found - fail with clear error (recommend enabling)
- Unreadable data - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Skill effectiveness analysis complete. Found [X] low-usage skills, [Y] improvement opportunities. See report for details."
4. Indicate readiness for improvements

