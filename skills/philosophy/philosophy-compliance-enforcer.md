---
name: philosophy-compliance-enforcer
category: philosophy
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 2-5min
complexity-level: moderate
requires-deep-analysis: true
prerequisites:
  - file: .cursor/rules/project-philosophy.mdc
    reason: "Need philosophy rules to validate against"
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Philosophy Compliance Enforcer

## Purpose

Validates that new features and changes don't violate the app's core philosophical invariants (Zero-Click Capture, Semantic Gravity, Neutrality, Privacy Absolutism, etc.). Ensures philosophical consistency is maintained during development.

## When to Invoke

### Explicit Trigger Phrases

- "Run philosophy-compliance-enforcer on [feature/component]"
- "Check if [change] violates philosophy"
- "Validate philosophy compliance for [target]"
- "Review [feature] against project philosophy"

### Situational Triggers

- Before implementing new features
- When adding UI components
- After major refactoring
- During code review
- When philosophical concerns arise

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Review proposed features against `.cursor/rules/project-philosophy.mdc`
- Identify violations of core invariants (Zero-Click Capture, Neutrality, Privacy Absolutism, etc.)
- Check for gamification patterns (achievements, counters, celebrations)
- Validate UI copy for prescriptive or judgmental language
- Suggest alternatives that preserve philosophical invariants
- Consider context and intent, not just surface-level patterns

### What It Must Avoid

- Don't flag legitimate state transitions as violations
- Don't suggest removing necessary features (suggest neutral alternatives)
- Don't ignore context (some patterns may be acceptable in specific contexts)
- Don't be overly strict (balance philosophy with usability)

### What It Must Prioritize

- Zero-Click Capture Invariant violations
- Neutrality Invariant violations (judgmental language, quality assessments)
- Privacy Absolutism violations
- Gamification patterns (achievements, counters, celebrations)
- Prescriptive language in UI copy

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive philosophy audit
- Before major release
- Initial project setup validation

**Input:**
- Entire codebase or major components
- Philosophy rules file (`.cursor/rules/project-philosophy.mdc`)
- UI components and copy

**Process:**
1. Load philosophy rules
2. Scan all UI components for violations
3. Check feature implementations against invariants
4. Identify gamification patterns
5. Validate language for neutrality
6. Generate comprehensive compliance report

**Invocation Example:**
> "Run philosophy-compliance-enforcer in full-scan mode on the entire application"

### Incremental Mode

**When to Use:**
- After adding new features
- When making UI changes
- During feature development

**Input:**
- Changed files from git diff
- New components or features
- Updated UI copy

**Process:**
1. Analyze changed code against philosophy rules
2. Check new features for violations
3. Validate updated UI copy
4. Report on compliance status

**Invocation Example:**
> "Run philosophy-compliance-enforcer in incremental mode on files changed in the last commit"

### Targeted Mode

**When to Use:**
- Reviewing specific feature
- Validating single component
- Focused compliance check

**Input:**
- Specific component or feature
- Targeted UI copy

**Process:**
1. Deep analysis of target against philosophy
2. Check all invariants for target
3. Validate language and patterns
4. Provide focused recommendations

**Invocation Example:**
> "Run philosophy-compliance-enforcer in targeted mode on src/components/completions/CompletionWorkshop.tsx"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Code Quality Issues**
- **Instead:** Use code-quality-audit for code-level problems
- **Why:** This skill focuses on philosophical compliance, not code quality or architecture.

**Anti-Pattern 2: Performance Issues**
- **Instead:** Use performance-budget-guardian for performance concerns
- **Why:** This skill validates philosophy, not performance characteristics.

**Anti-Pattern 3: Running on Every Small Change**
- **Instead:** Use incremental mode on feature additions or UI changes
- **Why:** Low cost but unnecessary for pure refactoring or bug fixes that don't affect philosophy.

### ⚠️ WARNING: Known Limitations

**Limitation:** May flag false positives for legitimate state management
- **Mitigation:** Review context carefully. State transitions are not violations if they're neutral.
- **Confidence:** ~85% accuracy on pattern detection, context review needed

**Limitation:** Cannot detect subtle philosophical drift
- **Mitigation:** Manual review of feature intent and user experience
- **Confidence:** ~75% accuracy on subtle violations

## Known Limitations

- Requires philosophy rules file to be up-to-date
- May miss context-dependent violations
- Cannot validate runtime behavior (only static code analysis)
- Subtle philosophical drift may require human judgment

## Fallback Strategy

If this skill fails, try:

1. **Manual philosophy review**: Read `.cursor/rules/project-philosophy.mdc` and review manually
2. **Check philosophy tests**: Review `tests/philosophy-compliance.test.ts` for examples
3. **Targeted mode**: Focus on specific components instead of full scan
4. **Human review**: Some philosophical judgments require human perspective

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Features/components analyzed
   - Philosophy rules referenced
   - Analysis scope

2. **Findings**
   - Philosophy violations (Critical/High/Medium/Low)
   - Each violation includes:
     - Description
     - Severity
     - Invariant violated
     - Location
     - Alternative suggestion
   - Gamification patterns found
   - Prescriptive language identified
   - Neutrality violations

3. **Recommendations**
   - Fixes for each violation (prioritized)
   - Alternative implementations that preserve invariants
   - Language revisions for neutrality
   - UI copy improvements
   - Each with effort estimate

4. **Implementation Steps**
   - Ordered fixes
   - Component updates
   - Copy revisions
   - Test case additions

5. **Files to Modify/Create**
   - Components with violations
   - UI copy files
   - Philosophy test files

6. **Dependencies**
   - Philosophy rules file referenced
   - Test framework (if adding tests)

### Filename Convention

Reports must follow: `YYYY-MM-DD_philosophy-compliance-enforcer_target-component.md`

### Example Output Structure

```yaml
Findings:
  - Violation: "Proposed 'Mark as Best' button implies quality judgment"
    Severity: High
    Invariant: Neutrality Invariant
    Location: src/components/completions/CompletionWorkshop.tsx:45
    Alternative: "Mark as Active" (neutral state transition)
  
  - Violation: "Completion acceptance counter" 
    Severity: Critical
    Invariant: No Gamification
    Location: src/components/dashboard/StatsPanel.tsx:23
    Alternative: Remove counter entirely

Recommendations:
  - Revise UI copy to use observational language
  - Replace judgment-based features with state-based features
  - Add philosophy test cases for new features

Files to Review:
  - src/components/completions/CompletionWorkshop.tsx
  - tests/philosophy-compliance.test.ts
```

### Context Preservation Strategy

For large codebases:
1. Summary with Critical/High violations in main report
2. Detailed analysis in separate file
3. Link to detailed analysis from main report

## Exit Conditions

### Success

- Philosophy compliance validated
- Violations identified and prioritized
- Alternatives suggested
- Handoff report generated per protocol

### Failure

- Missing philosophy rules file - fail with clear error
- Unreadable code - document what was found
- Timeout - suggest targeted mode

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Philosophy compliance check complete. Found [X] violations. See report for details and alternatives."
4. Indicate readiness for implementation

## Context Received (for Chained Skills)

If building on other skills:

```markdown
## Context Received

This analysis builds on:
- project-structure-analyzer v1.0.0 (executed 2024-01-05)
- Key findings: Codebase structure mapped, UI components identified
- Assumptions carried forward: Philosophy rules file is accurate and complete
```

## Examples

### Example 1: Gamification Detection

**Scenario:** Checking for achievement/counter patterns

**Expected Findings:**
- Violation: "Completion counter in dashboard"
- Severity: Critical
- Invariant: No Gamification
- Alternative: Remove counter, use neutral state display

### Example 2: Neutrality Language Check

**Scenario:** Reviewing UI copy for prescriptive language

**Expected Findings:**
- Violation: "You should try this prompt" (prescriptive)
- Severity: Medium
- Invariant: Neutrality
- Alternative: "This prompt is available" (observational)

