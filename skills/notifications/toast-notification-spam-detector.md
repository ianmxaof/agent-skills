---
name: toast-notification-spam-detector
category: notifications
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 1-3min
complexity-level: simple
requires-deep-analysis: false
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Toast Notification Spam Detector

## Purpose

Ensures toast notifications are sparse and opt-in (prevents notification fatigue). Validates that toasts respect `toastsEnabled` preference and don't violate calm UX principle.

## When to Invoke

### Explicit Trigger Phrases

- "Run toast-notification-spam-detector on [codebase]"
- "Check toast notification frequency"
- "Detect notification spam"
- "Validate toast preferences"

### Situational Triggers

- Before adding new toasts
- When notification fatigue is reported
- After UI changes
- During UX review
- When calm UX principle is violated

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Count toast triggers in codebase
- Identify high-frequency notification sources
- Validate toasts respect `toastsEnabled` preference
- Check for celebration/achievement language
- Propose batching or removal strategies
- Ensure sparse notification principle

### What It Must Avoid

- Don't flag legitimate error notifications
- Don't ignore user preference checks
- Don't miss indirect toast triggers
- Don't assume all toasts are problematic

### What It Must Prioritize

- High-frequency toasts (Critical - violates sparse principle)
- Missing preference checks (High - ignores user choice)
- Celebration language (Medium - violates neutrality)
- Batching opportunities (Medium - reduce spam)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive toast audit
- Before major release
- Initial notification review

**Input:**
- All toast trigger code
- Notification components
- User preference checks
- Toast content

**Process:**
1. Scan all toast triggers
2. Count notification frequency
3. Check preference respect
4. Identify celebration language
5. Find batching opportunities
6. Generate comprehensive spam report

**Invocation Example:**
> "Run toast-notification-spam-detector in full-scan mode on all notifications"

### Incremental Mode

**When to Use:**
- After adding new toasts
- When modifying notification logic
- During feature development

**Input:**
- New/changed toast code
- Updated notification components

**Process:**
1. Analyze new toasts for spam risk
2. Check if preferences are respected
3. Verify sparse principle maintained
4. Report on spam status

**Invocation Example:**
> "Run toast-notification-spam-detector in incremental mode on new toast additions"

### Targeted Mode

**When to Use:**
- Reviewing specific notification
- Validating single toast trigger
- Focused spam check

**Input:**
- Specific toast component
- Targeted notification trigger

**Process:**
1. Deep analysis of target toast
2. Check frequency and preference
3. Verify language neutrality
4. Provide focused recommendations

**Invocation Example:**
> "Run toast-notification-spam-detector in targeted mode on save notification"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General UX Issues**
- **Instead:** Use adversarial-ui-tester for broader UX concerns
- **Why:** This skill focuses specifically on toast notifications, not general UX.

**Anti-Pattern 2: Error Handling**
- **Instead:** Use code-quality-audit for error handling concerns
- **Why:** This skill validates notification spam, not error handling quality.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot test actual user experience
- **Mitigation:** Focus on static code analysis. Recommend user testing for validation.
- **Confidence:** ~85% accuracy on static analysis, user testing needed for full validation

## Known Limitations

- Cannot test actual user experience (static analysis only)
- May miss context-dependent notification needs
- Requires understanding of notification system
- Cannot verify notification frequency in production

## Fallback Strategy

If this skill fails, try:

1. **Manual review**: Review toast triggers manually
2. **User feedback**: Collect user feedback on notification frequency
3. **Targeted mode**: Focus on specific notifications
4. **Notification analytics**: Track actual notification frequency

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Toast triggers analyzed
   - Notification frequency found
   - Analysis scope

2. **Findings**
   - High-frequency toasts (Critical/High/Medium/Low)
   - Missing preference checks
   - Celebration language
   - Batching opportunities
   - Each finding includes location, frequency, and recommendations

3. **Recommendations**
   - Toast removals (prioritized)
   - Preference check additions
   - Batching strategies
   - Language revisions

4. **Implementation Steps**
   - Ordered fixes
   - Preference check additions
   - Toast removals/modifications

5. **Files to Modify/Create**
   - Toast trigger files
   - Notification components
   - Preference check files

6. **Dependencies**
   - Notification system referenced
   - User preference system

### Filename Convention

Reports must follow: `YYYY-MM-DD_toast-notification-spam-detector_target-component.md`

## Exit Conditions

### Success

- Toast spam detected
- Issues identified
- Recommendations provided
- Handoff report generated

### Failure

- No toast code found - fail with clear error
- Unreadable code - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Toast spam detection complete. Found [X] high-frequency toasts, [Y] missing preference checks. See report for details."
4. Indicate readiness for fixes

