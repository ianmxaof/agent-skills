---
name: test-coverage-gap-finder
category: testing
version: 1.0.0
maturity: draft
estimated-cost: medium
typical-runtime: 5-10min
complexity-level: moderate
requires-deep-analysis: true
scope: core
tier: 3
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - testing
  - coverage
  - quality
  - gaps
  - risk-assessment
  - test-generation
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Test Coverage Gap Finder

## Purpose

Identifies critical code paths without test coverage, especially philosophy-critical paths (privacy, state, recall). Prioritizes gaps by risk and proposes test cases.

## Scope and Classification

**Scope:** `core` - Universal skill that works on any project

**Tier:** `3` - Long-term quality (test coverage analysis)

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## When to Invoke

### Explicit Trigger Phrases

- "Run test-coverage-gap-finder on [codebase/module]"
- "Find test coverage gaps"
- "Identify untested code paths"
- "Check test coverage"

### Situational Triggers

- Before major releases
- After adding new features
- When test coverage is low
- During quality assurance
- When critical bugs occur

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Run coverage analysis
- Identify untested branches in critical services (privacy, state, recall)
- Prioritize gaps by risk (privacy > state > UI)
- Propose test cases for missing coverage
- Validate philosophy compliance tests are comprehensive
- Consider edge cases and error paths

### What It Must Avoid

- Don't suggest testing trivial code
- Don't ignore edge cases
- Don't miss error paths
- Don't assume all gaps are equal (prioritize)

### What It Must Prioritize

- Privacy enforcement paths (Critical - must be 100% covered)
- State transition paths (High - critical logic)
- Recall functionality (High - core feature)
- Philosophy compliance (High - invariants)
- Error handling (Medium - robustness)
- UI components (Low - lower risk)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive coverage audit
- Before major release
- Initial coverage assessment

**Input:**
- All source code
- Test files
- Coverage reports (if available)
- Critical path definitions

**Process:**
1. Analyze code coverage
2. Identify untested branches
3. Prioritize gaps by risk
4. Propose test cases
5. Validate philosophy tests
6. Generate comprehensive gap report

**Invocation Example:**
> "Run test-coverage-gap-finder in full-scan mode on entire codebase"

### Incremental Mode

**When to Use:**
- After adding new code
- When coverage decreases
- During feature development

**Input:**
- Changed files
- New code paths
- Updated tests

**Process:**
1. Analyze new code for coverage
2. Check if gaps were introduced
3. Verify critical paths are tested
4. Report on coverage status

**Invocation Example:**
> "Run test-coverage-gap-finder in incremental mode on new code"

### Targeted Mode

**When to Use:**
- Reviewing specific module
- Validating single service
- Focused coverage check

**Input:**
- Specific module or service
- Targeted code path

**Process:**
1. Deep analysis of target coverage
2. Identify all gaps
3. Prioritize by risk
4. Provide focused recommendations

**Invocation Example:**
> "Run test-coverage-gap-finder in targeted mode on privacy enforcement service"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General Code Quality**
- **Instead:** Use code-quality-audit for code-level problems
- **Why:** This skill focuses on test coverage, not code quality.

**Anti-Pattern 2: Test Quality**
- **Instead:** Use test-runner for test quality validation
- **Why:** This skill finds coverage gaps, not test quality issues.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot run actual coverage analysis without test framework
- **Mitigation:** Analyze code structure and test files. Recommend actual coverage tools for validation.
- **Confidence:** ~85% accuracy on static analysis, actual coverage tools needed for validation

## Known Limitations

- Cannot run actual coverage analysis (static analysis only)
- May miss complex coverage scenarios
- Requires test framework understanding
- Cannot verify coverage in production

## Fallback Strategy

If this skill fails, try:

1. **Coverage tools**: Use Jest, Vitest, or similar coverage tools
2. **Manual review**: Review code and tests manually
3. **Targeted mode**: Focus on specific modules
4. **Test analysis**: Analyze test files for coverage patterns

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Code analyzed
   - Coverage found
   - Analysis scope

2. **Findings**
   - Coverage gaps (Critical/High/Medium/Low)
   - Untested branches
   - Missing test cases
   - Philosophy test gaps
   - Each finding includes location, risk, and test proposal

3. **Recommendations**
   - Test case additions (prioritized)
   - Coverage improvements
   - Philosophy test additions
   - Edge case test additions
   - Each with effort estimate

4. **Implementation Steps**
   - Ordered test additions
   - Test implementations
   - Coverage improvements

5. **Files to Modify/Create**
   - Test files
   - Coverage configuration
   - Test utilities

6. **Dependencies**
   - Test framework referenced
   - Coverage tools recommended

### Filename Convention

Reports must follow: `YYYY-MM-DD_test-coverage-gap-finder_target-component.md`

## Exit Conditions

### Success

- Coverage gaps identified
- Test cases proposed
- Recommendations provided
- Handoff report generated

### Failure

- No code found - fail with clear error
- Unreadable code - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Coverage gap analysis complete. Found [X] critical gaps, [Y] high-priority gaps. See report for test case proposals."
4. Indicate readiness for test implementation

