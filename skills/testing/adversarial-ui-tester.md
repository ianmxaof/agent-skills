---
name: adversarial-ui-tester
category: testing
version: 1.0.0
maturity: validated
estimated-cost: medium
typical-runtime: 5-15min
complexity-level: moderate
requires-deep-analysis: true
scope: core
tier: 2
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - ui
  - ux
  - adversarial
  - failure-modes
  - accessibility
  - dark-patterns
  - user-testing
  - edge-cases
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Adversarial UI Tester

## Purpose

Tests user interfaces from an adversarial user perspective, identifying UX issues, edge cases, accessibility problems, and potential user frustration points. This skill demonstrates the value of non-code analysis in the agent-skills toolbox.

## Scope and Classification

**Scope:** `core` - Universal skill that works on any project

**Tier:** `2` - System health (UX and accessibility validation)

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## When to Invoke

### Explicit Trigger Phrases

- "Run adversarial-ui-tester on [component/page]"
- "Test the UI for UX issues"
- "Find edge cases in [UI component]"
- "Check for accessibility issues"

### Situational Triggers

- Before user-facing releases
- When UX concerns are raised
- After major UI changes
- During accessibility audits
- When onboarding new users to the interface

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Think like a frustrated or confused user
- Look for edge cases and error states
- Identify accessibility barriers
- Find usability friction points
- Consider different user personas (novice, expert, disabled users)
- Test mental models and expectations

### What It Must Avoid

- Don't focus on code quality (that's code-review)
- Don't suggest backend changes (focus on UI/UX)
- Don't ignore user context and personas
- Don't assume all users are technical

### What It Must Prioritize

- User experience and usability
- Accessibility (WCAG compliance)
- Error handling and edge cases
- User flow and navigation
- Feedback and affordances

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive UI audit
- Before major release
- Initial UX assessment

**Input:**
- All UI components and pages
- User flows and navigation
- Error states and edge cases
- Accessibility features

**Process:**
1. Map all user interfaces and flows
2. Test from adversarial user perspective
3. Identify UX issues and friction points
4. Check accessibility compliance
5. Find edge cases and error states
6. Generate comprehensive UX report

**Invocation Example:**
> "Run adversarial-ui-tester in full-scan mode on the entire application"

### Incremental Mode

**When to Use:**
- After UI changes in PR
- Continuous UX monitoring
- Focused review of updates

**Input:**
- Changed UI components
- Modified user flows
- Updated pages

**Process:**
1. Analyze impact of UI changes
2. Test changed components adversarially
3. Check if new issues introduced
4. Verify accessibility maintained

**Invocation Example:**
> "Run adversarial-ui-tester in incremental mode on UI components changed in the last commit"

### Targeted Mode

**When to Use:**
- Testing specific component or flow
- Deep dive into UX concern
- Focused accessibility audit

**Input:**
- Specific UI component or page
- User flow to test
- Component code and props

**Process:**
1. Deep adversarial testing of target
2. Identify all edge cases
3. Test accessibility thoroughly
4. Find usability issues

**Invocation Example:**
> "Run adversarial-ui-tester in targeted mode on the checkout flow"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Code Quality Issues**
- **Instead:** Use code-quality-audit for code-level problems
- **Why:** This skill focuses on user experience, not code implementation quality.

**Anti-Pattern 2: Backend API Testing**
- **Instead:** Use API testing skills or integration testing
- **Why:** This skill tests UI/UX, not backend functionality.

**Anti-Pattern 3: Running on Non-UI Code**
- **Instead:** Only use on UI components, pages, and user-facing code
- **Why:** This skill is specifically for user interface testing, not backend services.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot test actual runtime behavior
- **Mitigation:** Focus on code patterns, accessibility attributes, error handling code. Recommend manual testing for runtime.
- **Confidence:** ~75% accuracy on static analysis, runtime testing needed for full validation

**Limitation:** May miss context-dependent UX issues
- **Mitigation:** Consider user personas and use cases explicitly
- **Confidence:** ~70% accuracy on context-dependent issues

## Known Limitations

- Cannot test actual user interactions (static code analysis only)
- May miss runtime-specific UX issues
- Requires good component structure to analyze effectively
- May not catch all accessibility issues without runtime testing
- Context-dependent UX problems may be missed

## Fallback Strategy

If this skill fails, try:

1. **Manual testing**: Actually use the UI and note issues
2. **Accessibility tools**: Use automated accessibility checkers
3. **User testing**: Get real users to test the interface
4. **Targeted mode**: Focus on specific components instead of full scan

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - UI components analyzed
   - User flows tested
   - Testing approach and personas used

2. **Findings**
   - UX issues (prioritized: Critical/High/Medium/Low)
   - Accessibility violations (WCAG level)
   - Edge cases and error states
   - Usability friction points
   - Navigation and flow issues

3. **Recommendations**
   - UX improvements (prioritized)
   - Accessibility fixes
   - Error handling improvements
   - User flow optimizations
   - Each with effort estimate and user impact

4. **Implementation Steps**
   - Ordered fixes
   - Component updates needed
   - Accessibility attribute additions
   - Error state handling

5. **Files to Modify/Create**
   - UI component files
   - Error handling components
   - Accessibility improvements
   - User flow updates

6. **Dependencies**
   - UI framework and libraries
   - Accessibility tools needed
   - Testing libraries (if recommended)

### Filename Convention

Reports must follow: `YYYY-MM-DD_adversarial-ui-tester_target-component.md`

### Context Preservation Strategy

For large UIs:
1. Summary with Critical/High priority issues in main report
2. Detailed findings in separate file
3. Link to detailed analysis

## Exit Conditions

### Success

- UI tested from adversarial perspective
- UX issues identified
- Accessibility problems found
- Recommendations provided
- Handoff report generated

### Failure

- No UI components found - fail with clear error
- Unreadable UI code - document what was found
- Timeout - suggest targeted mode

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "UI testing complete. Found [X] UX issues, [Y] accessibility problems. See report for details."
4. Indicate readiness for implementation

## Examples

### Example 1: Form Component Testing

**Scenario:** Testing a complex form component

**Expected Findings:**
- Missing error messages for validation
- Inaccessible form labels
- Poor error state handling
- Confusing user flow
- Recommendations for improvements

### Example 2: Navigation Flow Testing

**Scenario:** Testing application navigation

**Expected Findings:**
- Broken navigation paths
- Missing breadcrumbs or back buttons
- Confusing menu structure
- Accessibility issues with keyboard navigation
- Recommendations for navigation improvements

