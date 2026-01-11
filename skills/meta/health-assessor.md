---
type: skill-definition
name: health-assessor
category: meta
version: 1.0.0
maturity: draft
lifecycle: validated
estimated-cost: low
typical-runtime: 2-5min
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
  - health
  - autonomous
  - intentless
  - triage
  - assessment
  - attention
prerequisites:
  - file: .agent-skills/skill-map.yaml
    reason: "Defines project surfaces and risk weights"
execution-modes:
  - intentless
  - surface-focused
  - change-triggered
---

# Health Assessor

## Purpose

Autonomously assess project health and identify areas needing attention **without being told what to look for**. This is the "intentless analysis" entry point—the skill that answers "what needs my attention?" so you don't have to decide.

**Core insight:** The health assessor is the first step in autonomous attention. Instead of "run X skill on Y," you say "assess the project" and the system decides where scrutiny is valuable.

## Scope and Classification

**Scope:** `meta`

This is a meta-skill that orchestrates other skills based on detected needs.

**Tier:** `meta`

Operates at the governance layer, directing attention rather than performing analysis.

**Lifecycle Stage:** `experimental`

New skill that enables autonomous attention routing.

## When to Invoke

### Explicit Trigger Phrases

- "Assess the health of [project]"
- "What needs attention in [project]?"
- "Identify areas of concern"
- "Where should I focus?"
- "Run a health check"

### Situational Triggers

- Starting a new work session
- After being away from the project
- When unsure where to begin
- Before planning a sprint
- When cognitive load is high and you need triage

### Do NOT Invoke When

- You know exactly what to analyze (use specific skill)
- Running a predefined skill chain
- In the middle of implementing a specific feature (use targeted skills)

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet (reasoning for triage)
- **Multi-Model**: Off

## Behavioral Rules

### How the Model Should Reason

1. **Load project contract** - Understand what surfaces exist
2. **Detect changes** - What has changed since last assessment?
3. **Calculate concern** - Risk × change velocity × staleness
4. **Prioritize surfaces** - Rank by concern score
5. **Plan columns** - Invoke column-router for high-concern surfaces
6. **Emit report** - Prioritized attention list with reasoning

### What It Must Avoid

- Running all skills on everything (wasteful)
- Ignoring the skill-map contract
- Making assumptions about unmapped surfaces
- Skipping low-risk surfaces entirely (they may have drifted)
- Proposing analysis without justification

### What It Must Prioritize

- Risk-weighted attention allocation
- Explicit "no action needed" for clean surfaces
- Specific skill recommendations (not just "check this")
- Reasoning transparency (why this surface needs attention)

## Assessment Process

### Step 1: Load Project Contract

Read `.agent-skills/skill-map.yaml` to understand:

```yaml
project_context:
  name: From skill-map.yaml
  surfaces: List of defined surfaces
  risk_weights: Per-surface risk classification
  enabled_skills: Which skills are available
  attention_triggers: Auto-assess patterns
  quality_bars: Thresholds to check
```

If skill-map.yaml doesn't exist:
- Emit warning
- Fall back to heuristic assessment based on directory structure
- Recommend creating skill-map.yaml

### Step 2: Detect Changes

**If git is available:**
```yaml
change_detection:
  method: git
  scope: "Changes since last assessment or last N days"
  
  metrics_per_surface:
    files_changed: Count of modified files
    lines_changed: Total LOC delta
    change_velocity: Changes per day
    last_change: Most recent modification timestamp
```

**If git is not available:**
```yaml
change_detection:
  method: timestamps
  scope: "File modification times"
  
  metrics_per_surface:
    files_modified_recently: Count within 7 days
    oldest_unchanged: Longest time since modification
```

**Output:**
```yaml
change_summary:
  total_files_changed: 15
  surfaces_affected:
    - surface: agent-skills
      files_changed: 8
      change_velocity: high
    - surface: documentation
      files_changed: 2
      change_velocity: low
```

### Step 3: Calculate Concern Scores

For each surface:

```yaml
concern_formula:
  concern_score = risk_weight * change_velocity * (1 - recent_validation)
  
  where:
    risk_weight: From skill-map.yaml (0.0 - 1.0)
    change_velocity: Normalized change rate (0.0 - 1.0)
    recent_validation: 1.0 if validated within threshold, decays over time
```

**Risk weight mapping:**
| Risk Level | Weight |
|------------|--------|
| critical | 1.0 |
| high | 0.8 |
| medium | 0.5 |
| low | 0.3 |

**Change velocity mapping:**
| Velocity | Score |
|----------|-------|
| No changes | 0.0 |
| 1-2 files | 0.3 |
| 3-5 files | 0.5 |
| 6-10 files | 0.7 |
| 10+ files | 1.0 |

**Validation decay:**
| Time Since Validation | Factor |
|-----------------------|--------|
| < 1 day | 0.1 |
| 1-3 days | 0.3 |
| 3-7 days | 0.5 |
| 7-14 days | 0.7 |
| 14+ days | 1.0 |

### Step 4: Rank Surfaces by Concern

Sort surfaces by concern_score descending.

```yaml
surface_ranking:
  - surface: agent-skills
    concern_score: 0.72
    risk_weight: high
    change_velocity: high
    last_validated: 5 days ago
    
  - surface: documentation
    concern_score: 0.45
    risk_weight: low
    change_velocity: low
    last_validated: 14 days ago
    
  - surface: meta-system
    concern_score: 0.10
    risk_weight: critical
    change_velocity: none
    last_validated: 2 days ago
```

### Step 5: Plan Columns for High-Concern Surfaces

For surfaces with concern_score > 0.5:
- Invoke column-router logic (internally)
- Generate column plans
- Include in output

For surfaces with concern_score 0.3 - 0.5:
- Flag as "monitor"
- Suggest lightweight check

For surfaces with concern_score < 0.3:
- Mark as "no action needed"
- Include in output explicitly

### Step 6: Emit Health Report

Generate structured output with prioritized recommendations.

## Output Contract

### Health Assessment Structure

```yaml
health_assessment:
  # Metadata
  timestamp: "2026-01-10T12:00:00Z"
  project: prompt-library
  assessment_type: intentless
  skill_map_loaded: true
  
  # Overall verdict
  overall_health: HEALTHY | ATTENTION_NEEDED | DEGRADED
  confidence: 0.78
  
  # Surface analysis
  surfaces_assessed:
    - surface: agent-skills
      concern_score: 0.72
      concern_level: high
      
      metrics:
        risk_weight: high
        files_changed: 8
        change_velocity: high
        days_since_validation: 5
        
      reasoning:
        - "High change velocity (8 files in 5 days)"
        - "Not validated since last changes"
        - "High risk weight per skill-map"
        
      recommended_action: "Run architecture-review and skill-health-check"
      recommended_skills:
        - architecture-review
        - skill-health-check
      priority: 1
      
    - surface: documentation
      concern_score: 0.45
      concern_level: medium
      
      metrics:
        risk_weight: low
        files_changed: 2
        change_velocity: low
        days_since_validation: 14
        
      reasoning:
        - "Potential drift from recent skill changes"
        - "Low risk but stale validation"
        
      recommended_action: "Run documentation-drift-detector"
      recommended_skills:
        - documentation-drift-detector
      priority: 2
      
    - surface: meta-system
      concern_score: 0.10
      concern_level: low
      
      metrics:
        risk_weight: critical
        files_changed: 0
        change_velocity: none
        days_since_validation: 2
        
      reasoning:
        - "No changes detected"
        - "Recently validated"
        
      recommended_action: "No action needed"
      recommended_skills: []
      priority: null
  
  # Surfaces explicitly not needing attention
  no_action_surfaces:
    - surface: meta-system
      reason: "No changes, recently validated"
    - surface: templates
      reason: "No changes detected"
  
  # Column plans for high-concern surfaces
  column_plans:
    - surface: agent-skills
      risk_tier: medium
      recommended_columns:
        - name: architecture
          skill: architecture-review
          reason: "Structural changes detected"
        - name: correctness
          skill: skill-health-check
          reason: "Skill definitions modified"
      refinement_strictness: normal
      
  # Attention priority (ordered)
  attention_priority:
    1: agent-skills
    2: documentation
    
  # Suggested invocation for Cursor
  suggested_invocation: |
    Run architecture-review on skills/ directory.
    Then run documentation-drift-detector on docs/.
    
  # Next assessment recommendation
  next_assessment:
    recommended_in: "3 days"
    reason: "High change velocity in agent-skills"
```

### Filename Convention

```
YYYY-MM-DD_health-assessment_[project].yaml
```

Example: `2026-01-10_health-assessment_prompt-library.yaml`

### Overall Health Verdicts

| Verdict | Criteria |
|---------|----------|
| HEALTHY | No surface with concern > 0.5, no critical surfaces flagged |
| ATTENTION_NEEDED | At least one surface with concern > 0.5 |
| DEGRADED | Multiple high-concern surfaces OR critical surface flagged |

## Execution Modes

### Intentless Mode (Default)

**When to Use:**
- General health check
- Starting a new session
- "What needs attention?"

**Process:**
1. Load skill-map
2. Detect all changes
3. Score all surfaces
4. Generate full report

**Invocation:**
```
"Assess the health of prompt-library"
```

### Surface-Focused Mode

**When to Use:**
- Checking specific area
- After working on one surface
- Quick targeted check

**Process:**
1. Load skill-map
2. Analyze only specified surface(s)
3. Generate focused report

**Invocation:**
```
"Assess the health of the skills surface"
```

### Change-Triggered Mode

**When to Use:**
- Automated/CI integration
- Post-commit hooks
- Scheduled assessments

**Process:**
1. Accept change list as input
2. Map changes to surfaces
3. Assess only affected surfaces
4. Generate delta report

**Invocation:**
```
"Assess health impact of these changes: [file list]"
```

**Output (delta):**
```yaml
health_delta:
  trigger: change_event
  changes_analyzed: 5
  
  surfaces_impacted:
    - surface: agent-skills
      impact: significant
      recommendation: "Validate with architecture-review"
      
  surfaces_not_impacted:
    - surface: documentation
    - surface: meta-system
```

## Common Misuses / Anti-Patterns

### DON'T Use This Skill For...

**Anti-Pattern 1: Replacing specific analysis**
- **Instead:** If you know what to check, use the specific skill
- **Why:** Health assessor is for triage, not deep analysis

**Anti-Pattern 2: Running after every commit**
- **Instead:** Use change-triggered mode or batch assessments
- **Why:** Over-assessment wastes cognitive resources

**Anti-Pattern 3: Ignoring "no action needed" surfaces**
- **Instead:** Trust the assessment; review periodically
- **Why:** Explicit no-ops prevent analysis paralysis

### WARNING: Known Limitations

**Limitation:** Depends on accurate skill-map.yaml
- **Mitigation:** Validate skill-map before relying on health assessor
- **Confidence:** Quality of assessment matches quality of skill-map

**Limitation:** Cannot detect issues in unmapped surfaces
- **Mitigation:** Keep skill-map updated when adding new surface types

## Known Limitations

- Requires skill-map.yaml for accurate assessment
- Change detection depends on git or file timestamps
- Cannot detect semantic issues (only change patterns)
- Concern scores are heuristic, not precise

## Fallback Strategy

If skill-map.yaml is missing:

1. **Heuristic mode** - Analyze directory structure
2. **Emit warning** - Recommend creating skill-map.yaml
3. **Best-effort assessment** - Based on file types and paths

If git is unavailable:

1. **Timestamp mode** - Use file modification times
2. **Reduced accuracy** - Note in output
3. **Proceed with assessment** - Better than nothing

## Integration Points

### Upstream (Inputs)

| Source | What It Provides |
|--------|------------------|
| skill-map.yaml | Surface definitions, risk weights |
| Git history | Change detection |
| File system | Timestamps if no git |
| Previous assessments | Validation timestamps |

### Downstream (Outputs)

| Consumer | How It Uses Assessment |
|----------|------------------------|
| Column Router | Risk tier inputs |
| Human | Attention prioritization |
| CI/CD | Automated health gates |
| Readiness Certifier | Pre-certification evidence |

## Examples

### Example 1: Healthy Project

```yaml
health_assessment:
  overall_health: HEALTHY
  confidence: 0.85
  
  surfaces_assessed:
    - surface: agent-skills
      concern_score: 0.25
      recommended_action: "No action needed"
      
    - surface: documentation
      concern_score: 0.15
      recommended_action: "No action needed"
      
  attention_priority: []
  
  suggested_invocation: |
    No immediate action required.
    Continue with planned work.
```

### Example 2: Attention Needed

```yaml
health_assessment:
  overall_health: ATTENTION_NEEDED
  confidence: 0.72
  
  surfaces_assessed:
    - surface: agent-skills
      concern_score: 0.68
      concern_level: high
      recommended_action: "Run architecture-review"
      
    - surface: documentation
      concern_score: 0.35
      concern_level: medium
      recommended_action: "Monitor for drift"
      
  attention_priority:
    1: agent-skills
    
  suggested_invocation: |
    Run architecture-review on skills/ directory.
    Monitor documentation for drift after skills update.
```

### Example 3: Degraded State

```yaml
health_assessment:
  overall_health: DEGRADED
  confidence: 0.60
  
  surfaces_assessed:
    - surface: meta-system
      concern_score: 0.85
      concern_level: critical
      reasoning:
        - "Critical surface modified without validation"
        - "Governance files changed"
      recommended_action: "URGENT: Validate meta-system changes"
      
    - surface: agent-skills
      concern_score: 0.72
      concern_level: high
      recommended_action: "Run full skill audit"
      
  attention_priority:
    1: meta-system
    2: agent-skills
    
  suggested_invocation: |
    PRIORITY: Validate meta-system changes immediately.
    Then run full skill audit on agent-skills.
```

## Exit Conditions

### Success

- All mapped surfaces assessed
- Concern scores calculated
- Recommendations generated
- Output structured correctly

### Failure

- skill-map.yaml missing AND no fallback possible
- File system inaccessible
- Critical error in change detection

### Handoff

After assessment:
1. Present prioritized attention list
2. Suggest specific skills to run
3. Indicate timeline for next assessment
4. Hand off to column-router for high-concern surfaces

## See Also

- `.agent-skills/skill-map.yaml` - Project contract
- `skills/meta/column-router.md` - Plans columns for assessment
- `skills/meta/readiness-certifier.md` - Uses assessment for certification
- `protocols/attention-autonomy-protocol.md` - Automated triggering
- `meta/risk-tiers.md` - Risk tier definitions
