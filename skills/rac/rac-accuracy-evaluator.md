---
name: rac-accuracy-evaluator
category: rac
version: 1.0.0
maturity: draft
estimated-cost: medium
typical-runtime: 5-10min
complexity-level: complex
requires-deep-analysis: true
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# RAC Accuracy Evaluator

## Purpose

Tests RAC (Relevant Action Completion) completion quality by analyzing precision/recall of suggestions. Evaluates semantic matching accuracy and proposes threshold adjustments.

## When to Invoke

### Explicit Trigger Phrases

- "Run rac-accuracy-evaluator on [RAC system]"
- "Evaluate RAC suggestion quality"
- "Test RAC precision/recall"
- "Analyze RAC accuracy"

### Situational Triggers

- After modifying RAC similarity thresholds
- When RAC quality issues are reported
- During RAC feature development
- When tuning embedding models
- Before RAC feature releases

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Analyze phrase extraction quality
- Test semantic matching accuracy
- Evaluate suggestion relevance (precision)
- Measure suggestion coverage (recall)
- Compare different similarity thresholds
- Propose optimal threshold adjustments

### What It Must Avoid

- Don't suggest thresholds without testing
- Don't ignore false positive/negative rates
- Don't miss edge cases in matching
- Don't assume current thresholds are optimal

### What It Must Prioritize

- Precision issues (High - over-suggestion is annoying)
- Recall issues (High - under-suggestion is useless)
- Threshold optimization (Medium - balance precision/recall)
- Edge case handling (Medium - robustness)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive RAC quality audit
- Before major RAC changes
- Initial RAC evaluation

**Input:**
- RAC implementation code
- Phrase extraction logic
- Similarity matching code
- Embedding model configuration
- Test data (if available)

**Process:**
1. Analyze phrase extraction quality
2. Test semantic matching accuracy
3. Evaluate precision and recall
4. Compare threshold options
5. Identify optimization opportunities
6. Generate comprehensive accuracy report

**Invocation Example:**
> "Run rac-accuracy-evaluator in full-scan mode on RAC system"

### Incremental Mode

**When to Use:**
- After threshold changes
- When modifying matching logic
- During RAC development

**Input:**
- Changed RAC code
- Updated thresholds
- Modified matching logic

**Process:**
1. Analyze impact of changes on accuracy
2. Test new thresholds
3. Verify precision/recall balance
4. Report on quality status

**Invocation Example:**
> "Run rac-accuracy-evaluator in incremental mode on threshold changes"

### Targeted Mode

**When to Use:**
- Testing specific threshold
- Evaluating single matching component
- Focused accuracy check

**Input:**
- Specific threshold value
- Targeted matching component

**Process:**
1. Deep analysis of target accuracy
2. Test precision/recall for target
3. Compare with other thresholds
4. Provide focused recommendations

**Invocation Example:**
> "Run rac-accuracy-evaluator in targeted mode on similarity threshold 0.7"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General Code Quality**
- **Instead:** Use code-quality-audit for code-level problems
- **Why:** This skill focuses on RAC accuracy metrics, not code quality.

**Anti-Pattern 2: Performance Issues**
- **Instead:** Use performance-budget-guardian for performance concerns
- **Why:** This skill evaluates suggestion quality, not performance.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot test actual user experience
- **Mitigation:** Focus on precision/recall metrics. Recommend user testing for validation.
- **Confidence:** ~80% accuracy on metrics, user testing needed for full validation

## Known Limitations

- Cannot test actual user experience (metrics only)
- Requires test data for accurate evaluation
- May miss context-dependent accuracy issues
- Cannot verify accuracy in production

## Fallback Strategy

If this skill fails, try:

1. **Manual testing**: Test RAC suggestions manually
2. **User feedback**: Collect user feedback on suggestion quality
3. **Targeted mode**: Focus on specific thresholds
4. **A/B testing**: Test different thresholds with users

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - RAC system analyzed
   - Thresholds tested
   - Analysis scope

2. **Findings**
   - Precision issues (High/Medium/Low)
   - Recall issues (High/Medium/Low)
   - Threshold recommendations
   - Edge case issues
   - Each finding includes metrics and recommendations

3. **Recommendations**
   - Threshold adjustments (prioritized)
   - Matching logic improvements
   - Edge case handling
   - Test case additions

4. **Implementation Steps**
   - Ordered improvements
   - Threshold updates
   - Logic modifications

5. **Files to Modify/Create**
   - RAC implementation files
   - Threshold configuration
   - Test files

6. **Dependencies**
   - Embedding model referenced
   - Similarity calculation method

### Filename Convention

Reports must follow: `YYYY-MM-DD_rac-accuracy-evaluator_target-component.md`

## Exit Conditions

### Success

- RAC accuracy evaluated
- Issues identified
- Recommendations provided
- Handoff report generated

### Failure

- No RAC code found - fail with clear error
- Unreadable code - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "RAC accuracy evaluation complete. Precision: [X]%, Recall: [Y]%. See report for threshold recommendations."
4. Indicate readiness for optimization

