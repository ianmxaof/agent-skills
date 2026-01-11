---
name: capture-surface-focus-auditor
category: performance
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 2-5min
complexity-level: simple
requires-deep-analysis: false
scope: project
tier: 1
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
domain: prompt-library
tags:
  - performance
  - focus
  - ux
  - zero-click
  - capture
  - textarea
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Capture Surface Focus Auditor

## Purpose

Validates that capture surface auto-focuses and stays focused (Zero-Click Capture enforcement). Ensures focus flow from page load → textarea is maintained and not interrupted by other components.

## Scope and Classification

**Scope:** `project` - Prompt Library-specific skill

**Tier:** `1` - Existential risk (Zero-Click Capture enforcement)

**Domain:** `prompt-library` - Encodes Prompt Library-specific capture surface behavior

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## When to Invoke

### Explicit Trigger Phrases

- "Run capture-surface-focus-auditor on [component/app]"
- "Check capture surface focus"
- "Validate auto-focus behavior"
- "Audit focus flow"

### Situational Triggers

- Before production deployments
- After adding modals or dialogs
- When focus issues are reported
- After navigation changes
- When TTI measurements are off

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Trace focus flow from page load → textarea
- Identify components that steal focus
- Check for modals/dialogs that interrupt capture
- Validate focus restoration after navigation
- Measure time-to-focus (should be <100ms)
- Look for focus traps and restoration logic

### What It Must Avoid

- Don't flag legitimate focus changes (user-initiated)
- Don't ignore focus restoration (check if it happens)
- Don't miss async focus issues (check timing)
- Don't assume focus works (verify implementation)

### What It Must Prioritize

- Time-to-focus violations (Critical - breaks Zero-Click Capture)
- Focus blockers (High - delays interactivity)
- Missing focus restoration (High - breaks UX after modals)
- Focus stealing components (Medium - interrupts capture)
- Navigation focus issues (Medium - breaks flow)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive focus audit
- Before major release
- Initial focus validation

**Input:**
- All UI components
- Capture surface component
- Modal/dialog components
- Navigation components
- Focus management code

**Process:**
1. Trace focus flow from page load
2. Identify focus blockers
3. Check for focus stealing components
4. Validate focus restoration
5. Measure time-to-focus
6. Generate comprehensive focus report

**Invocation Example:**
> "Run capture-surface-focus-auditor in full-scan mode on the entire application"

### Incremental Mode

**When to Use:**
- After adding modals/dialogs
- When modifying navigation
- After focus-related changes

**Input:**
- Changed components
- New modals/dialogs
- Modified navigation

**Process:**
1. Analyze impact of changes on focus
2. Check if new components steal focus
3. Verify focus restoration still works
4. Report on focus status

**Invocation Example:**
> "Run capture-surface-focus-auditor in incremental mode on files changed in the last commit"

### Targeted Mode

**When to Use:**
- Reviewing specific component
- Validating single modal
- Focused focus check

**Input:**
- Specific component
- Targeted modal/dialog
- Single focus operation

**Process:**
1. Deep analysis of target focus behavior
2. Check focus flow for target
3. Verify restoration logic
4. Provide focused recommendations

**Invocation Example:**
> "Run capture-surface-focus-auditor in targeted mode on DraftRestore modal"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General Performance Issues**
- **Instead:** Use performance-budget-guardian for broader performance concerns
- **Why:** This skill focuses specifically on focus behavior, not general performance.

**Anti-Pattern 2: Accessibility Issues**
- **Instead:** Use adversarial-ui-tester for accessibility concerns
- **Why:** This skill validates focus flow, not full accessibility compliance.

**Anti-Pattern 3: Running on Backend Code**
- **Instead:** Focus on UI components and capture surface
- **Why:** This skill is specifically for frontend focus behavior.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot test actual runtime focus behavior
- **Mitigation:** Focus on static code analysis. Recommend manual testing for validation.
- **Confidence:** ~85% accuracy on static analysis, manual testing needed for full validation

**Limitation:** May miss timing-related focus issues
- **Mitigation:** Review async operations and timing carefully
- **Confidence:** ~80% accuracy on timing issues

## Known Limitations

- Cannot test actual runtime focus behavior (static analysis only)
- May miss timing-related focus issues
- Requires understanding of React focus management
- Cannot verify focus in production (only code analysis)

## Fallback Strategy

If this skill fails, try:

1. **Manual testing**: Actually use the app and check focus behavior
2. **Browser DevTools**: Use focus debugging tools
3. **Targeted mode**: Focus on specific components instead of full scan
4. **Focus testing tools**: Use automated focus testing tools

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Components analyzed
   - Focus flow traced
   - Analysis scope

2. **Findings**
   - Time-to-focus violations (Critical/High/Medium/Low)
   - Focus blockers identified
   - Missing focus restoration
   - Focus stealing components
   - Each finding includes:
     - Component/location
     - Impact on focus
     - Time delay (if measurable)
     - Fix recommendation

3. **Recommendations**
   - Focus fixes (prioritized)
   - Focus restoration implementations
   - Modal focus trap setups
   - Navigation focus preservation
   - Each with effort estimate

4. **Implementation Steps**
   - Ordered fixes
   - Focus restoration code
   - Modal focus trap code
   - Navigation focus preservation

5. **Files to Modify/Create**
   - Component files needing focus fixes
   - Modal/dialog components
   - Navigation components
   - Focus test files

6. **Dependencies**
   - React focus management referenced
   - Testing framework (if adding tests)

### Filename Convention

Reports must follow: `YYYY-MM-DD_capture-surface-focus-auditor_target-component.md`

### Example Output Structure

```yaml
Focus Flow Analysis:
  
  Time-to-Focus: 180ms (Target: <100ms)
  
  Focus Blockers:
    - DraftRestore modal steals focus on mount
      Location: src/components/capture/DraftRestore.tsx:23
      Impact: Adds 80ms delay
      Fix: Remove modal, restore draft silently
    
    - NavigationTabs onClick() triggers re-render
      Location: src/components/layout/NavigationTabs.tsx:15
      Impact: Textarea loses focus on tab switch
      Fix: Preserve focus with useEffect hook

  Focus Recovery Issues:
    - Opening VariantTree modal breaks focus
      Location: src/components/variants/VariantTree.tsx
      Impact: User must manually refocus after closing modal
      Fix: Add focus restoration on modal close

Recommendations:
  1. Remove DraftRestore modal (silent restoration)
  2. Add focus preservation across navigation
  3. Implement modal focus trap with restoration
  4. Add focus timing metrics to performance tests

Files to Modify:
  - src/components/capture/DraftRestore.tsx (remove)
  - src/components/layout/PersistentCaptureLayer.tsx
  - src/components/layout/NavigationTabs.tsx
  - tests/capture-focus.test.ts (new)
```

### Context Preservation Strategy

For large applications:
1. Summary with Critical/High violations in main report
2. Detailed focus flow analysis in separate file
3. Link to detailed analysis from main report

## Exit Conditions

### Success

- Focus flow validated
- Blockers identified
- Recommendations provided
- Handoff report generated per protocol

### Failure

- No capture surface found - fail with clear error
- Unreadable code - document what was found
- Timeout - suggest targeted mode

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Focus audit complete. Time-to-focus: [X]ms (target: <100ms). Found [Y] blockers. See report for details."
4. Indicate readiness for implementation

## Context Received (for Chained Skills)

If building on other skills:

```markdown
## Context Received

This analysis builds on:
- project-structure-analyzer v1.0.0 (executed 2024-01-05)
- Key findings: UI component structure mapped, capture surface identified
- Assumptions carried forward: Capture surface component is correctly identified
```

## Examples

### Example 1: Modal Stealing Focus

**Scenario:** Checking DraftRestore modal

**Expected Findings:**
- Modal steals focus on mount
- Adds 80ms delay to time-to-focus
- Fix: Remove modal, restore draft silently

### Example 2: Navigation Breaking Focus

**Scenario:** Checking navigation components

**Expected Findings:**
- Tab switch causes textarea to lose focus
- Fix: Preserve focus with useEffect hook

