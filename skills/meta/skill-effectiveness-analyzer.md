---
name: skill-effectiveness-analyzer
category: meta
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 2-5min
complexity-level: simple
requires-deep-analysis: false
prerequisites: []
execution-modes:
  - full-scan
  - targeted
---

# Skill Effectiveness Analyzer

## Purpose

Validates that skills are actually useful (not just theoretical). Tracks usage, measures issue detection rate, analyzes false positive rate, and proposes skill improvements or retirement.

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

3. **Recommendations**
   - Skill improvements (prioritized)
   - Retirement candidates
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

