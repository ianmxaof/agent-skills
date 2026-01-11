---
name: failure-mode-simulator
category: failure-modes
version: 1.0.0
maturity: draft
estimated-cost: high
typical-runtime: 10-20min
complexity-level: expert
requires-deep-analysis: true
scope: core
tier: 3
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - testing
  - failure-modes
  - stress-test
  - resilience
  - simulation
  - edge-cases
prerequisites: []
execution-modes:
  - full-scan
  - targeted
---

# Failure Mode Simulator

## Purpose

Simulates the 6 stress-test failure modes and validates that countermeasures work. Seeds test database with pathological data and validates compression affordances, privacy enforcement, and performance under load.

## Scope and Classification

**Scope:** `core` - Universal skill that works on any project

**Tier:** `3` - Long-term quality (stress testing and failure mode validation)

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## When to Invoke

### Explicit Trigger Phrases

- "Run failure-mode-simulator on [failure-mode]"
- "Simulate [failure-mode]"
- "Test failure mode countermeasures"
- "Validate stress test scenarios"

### Situational Triggers

- Before major releases
- When countermeasures are added
- During stress testing
- When failure modes are suspected
- During quality assurance

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Seed test database with pathological data (1000 prompts, 400 variants, etc.)
- Simulate user workflows that trigger failure modes
- Validate compression affordances surface correctly
- Check privacy tier enforcement under stress
- Measure performance under load
- Verify countermeasures are effective

### What It Must Avoid

- Don't corrupt production data (use test database only)
- Don't ignore edge cases in failure modes
- Don't miss subtle failure mode triggers
- Don't assume countermeasures work (verify)

### What It Must Prioritize

- Hoarding Singularity (Critical - variant explosion)
- Trust Violation (Critical - privacy leaks)
- Performance Degradation (High - TTI violations)
- Countermeasure effectiveness (High - must work)
- Edge case handling (Medium - robustness)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive failure mode testing
- Before major release
- Initial stress test validation

**Input:**
- All failure mode definitions
- Countermeasure implementations
- Test database setup
- Stress test scenarios

**Process:**
1. Seed test database with pathological data
2. Simulate each failure mode
3. Validate countermeasures work
4. Check privacy enforcement
5. Measure performance impact
6. Generate comprehensive simulation report

**Invocation Example:**
> "Run failure-mode-simulator in full-scan mode on all failure modes"

### Targeted Mode

**When to Use:**
- Testing specific failure mode
- Validating single countermeasure
- Focused stress test

**Input:**
- Specific failure mode
- Targeted countermeasure

**Process:**
1. Deep simulation of target failure mode
2. Validate specific countermeasure
3. Test edge cases
4. Provide focused recommendations

**Invocation Example:**
> "Run failure-mode-simulator in targeted mode on Hoarding Singularity"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General Testing**
- **Instead:** Use test-coverage-gap-finder for general test coverage
- **Why:** This skill focuses specifically on failure mode simulation, not general testing.

**Anti-Pattern 2: Performance Testing**
- **Instead:** Use performance-budget-guardian for performance concerns
- **Why:** This skill simulates failure modes, not general performance testing.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot run actual simulations without test environment
- **Mitigation:** Focus on test scenario design. Recommend actual test execution for validation.
- **Confidence:** ~85% accuracy on scenario design, actual testing needed for validation

## Known Limitations

- Cannot run actual simulations (test design only)
- Requires test database setup
- May miss complex failure mode interactions
- Cannot verify countermeasures in production

## Fallback Strategy

If this skill fails, try:

1. **Manual testing**: Run failure mode scenarios manually
2. **Test database**: Set up test database and run scenarios
3. **Targeted mode**: Focus on specific failure modes
4. **Stress testing tools**: Use automated stress testing tools

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Failure modes simulated
   - Countermeasures tested
   - Analysis scope

2. **Findings**
   - Countermeasure effectiveness (Critical/High/Medium/Low)
   - Failure mode triggers found
   - Privacy enforcement issues
   - Performance degradation
   - Each finding includes scenario, result, and recommendations

3. **Recommendations**
   - Countermeasure improvements (prioritized)
   - Test scenario additions
   - Performance optimizations
   - Privacy enforcement fixes

4. **Implementation Steps**
   - Ordered improvements
   - Countermeasure updates
   - Test additions

5. **Files to Modify/Create**
   - Countermeasure files
   - Test scenario files
   - Performance optimization files

6. **Dependencies**
   - Failure mode definitions referenced
   - Test framework

### Filename Convention

Reports must follow: `YYYY-MM-DD_failure-mode-simulator_target-component.md`

## Exit Conditions

### Success

- Failure modes simulated
- Countermeasures validated
- Issues identified
- Handoff report generated

### Failure

- No failure mode definitions found - fail with clear error
- Cannot set up test database - document limitations

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Failure mode simulation complete. Tested [X] failure modes, [Y] countermeasures validated. See report for details."
4. Indicate readiness for improvements

