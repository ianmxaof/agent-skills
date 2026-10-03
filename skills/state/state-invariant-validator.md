---
name: state-invariant-validator
category: state
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 2-5min
complexity-level: moderate
requires-deep-analysis: true
prerequisites:
  - file: src/services/state-transitions.ts
    reason: "Need state transition logic to validate"
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# State Invariant Validator

## Purpose

Ensures state transitions follow the defined rules (e.g., no `shipped → exploring` reversals). Validates that state machine invariants are maintained and momentum principles are preserved.

## When to Invoke

### Explicit Trigger Phrases

- "Run state-invariant-validator on [service/component]"
- "Check state transition validity"
- "Validate state machine rules"
- "Review state transitions"

### Situational Triggers

- Before adding new state transitions
- When modifying state transition logic
- After refactoring state management
- During state machine design
- When state-related bugs occur

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Review all `db.tools.update()` calls that change `state` field
- Validate transitions against state machine diagram/rules
- Identify missing transition guards
- Check for UI that enables invalid transitions
- Verify momentum principles are maintained
- Consider edge cases and error states

### What It Must Avoid

- Don't flag legitimate transitions as violations
- Don't ignore error state transitions
- Don't miss indirect state changes (through other fields)
- Don't assume all transitions are explicit (check implicit ones)

### What It Must Prioritize

- Invalid transitions (Critical - breaks state machine)
- Missing guards (High - allows invalid transitions)
- UI enabling invalid transitions (High - user can break invariants)
- Momentum violations (Medium - philosophical concern)
- Edge case handling (Medium - robustness)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive state machine validation
- Before major refactoring
- Initial state machine audit

**Input:**
- All state transition code
- State machine definition/rules
- UI components that trigger state changes
- Database update operations

**Process:**
1. Map all state transitions in code
2. Validate against state machine rules
3. Check for missing guards
4. Verify UI doesn't enable invalid transitions
5. Identify edge cases
6. Generate comprehensive validation report

**Invocation Example:**
> "Run state-invariant-validator in full-scan mode on all state transitions"

### Incremental Mode

**When to Use:**
- After adding new state transitions
- When modifying transition logic
- During feature development

**Input:**
- Changed state transition code
- New UI components
- Modified state logic

**Process:**
1. Analyze changed transitions
2. Verify new transitions are valid
3. Check for new invalid transition paths
4. Report on compliance status

**Invocation Example:**
> "Run state-invariant-validator in incremental mode on files changed in the last commit"

### Targeted Mode

**When to Use:**
- Reviewing specific transition
- Validating single state change
- Focused validation

**Input:**
- Specific state transition function
- Targeted UI component
- Single state change operation

**Process:**
1. Deep analysis of target transition
2. Verify validity against rules
3. Check guards and edge cases
4. Provide focused recommendations

**Invocation Example:**
> "Run state-invariant-validator in targeted mode on restoreFromArchive function"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General Code Quality**
- **Instead:** Use code-quality-audit for code-level problems
- **Why:** This skill focuses specifically on state transition validity, not general code quality.

**Anti-Pattern 2: Performance Issues**
- **Instead:** Use performance-budget-guardian for performance concerns
- **Why:** This skill validates state machine rules, not performance.

**Anti-Pattern 3: Running on Non-State Code**
- **Instead:** Focus on state management and transition code
- **Why:** This skill is specifically for state machine validation.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot detect runtime state violations
- **Mitigation:** Focus on static code analysis. Recommend runtime tests for validation.
- **Confidence:** ~90% accuracy on static analysis, runtime testing needed for full validation

**Limitation:** May miss implicit state changes
- **Mitigation:** Review all database update operations, not just explicit state transitions
- **Confidence:** ~85% accuracy on implicit transitions

## Known Limitations

- Cannot test actual runtime behavior (static analysis only)
- May miss complex state change patterns
- Requires state machine rules to be documented
- Cannot verify state consistency in production

## Fallback Strategy

If this skill fails, try:

1. **Manual state machine review**: Review state diagram and transition rules manually
2. **Runtime tests**: Write tests that verify state transitions
3. **Targeted mode**: Focus on specific transitions instead of full scan
4. **State machine tools**: Use formal state machine validation tools

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - State transitions analyzed
   - State machine rules referenced
   - Analysis scope

2. **Findings**
   - Invalid transitions found (Critical/High/Medium/Low)
   - Missing guards identified
   - UI enabling invalid transitions
   - Momentum violations
   - Each finding includes:
     - Transition (from → to)
     - Location
     - Risk description
     - Fix recommendation

3. **Recommendations**
   - Guard additions (prioritized)
   - Transition fixes
   - UI updates
   - Test case additions
   - Each with effort estimate

4. **Implementation Steps**
   - Ordered fixes
   - Guard implementations
   - UI updates
   - Test additions

5. **Files to Modify/Create**
   - State transition files
   - UI component files
   - Test files

6. **Dependencies**
   - State machine rules referenced
   - Test framework (if adding tests)

### Filename Convention

Reports must follow: `YYYY-MM-DD_state-invariant-validator_target-component.md`

### Example Output Structure

```yaml
State Transition Analysis:
  
  Valid Transitions Found:
    ✓ exploring → shipped (markAsShipped)
    ✓ exploring → archived (archiveTool)
    ✓ shipped → archived (archiveTool)
    ✓ archived → exploring (restoreFromArchive)
  
  Invalid Transitions Found:
    ✗ shipped → exploring (NO IMPLEMENTATION - CORRECT)
  
  Missing Guards:
    - restoreFromArchive() allows shipped → exploring
      Location: src/services/state-transitions.ts:42
      Risk: Violates momentum principle
      Fix: Add guard: if (tool.state === 'shipped') return;
  
  UI Enabling Invalid Transitions:
    - "Restore" button shown for shipped prompts
      Location: src/components/prompts/PromptCard.tsx:67
      Risk: Users expect to restore shipped prompts
      Fix: Hide "Restore" for shipped state

Test Cases to Add:
  - restoreFromArchive() rejects shipped → exploring
  - UI hides restore button for shipped prompts
  - State machine diagram in docs matches code

Files to Modify:
  - src/services/state-transitions.ts
  - src/components/prompts/PromptCard.tsx
  - tests/state-transitions.test.ts
```

### Context Preservation Strategy

For large codebases:
1. Summary with Critical/High violations in main report
2. Detailed transition analysis in separate file
3. Link to detailed analysis from main report

## Exit Conditions

### Success

- State transitions validated
- Invalid transitions identified
- Recommendations provided
- Handoff report generated per protocol

### Failure

- No state transition code found - fail with clear error
- Unreadable code - document what was found
- Timeout - suggest targeted mode

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "State transition validation complete. Found [X] invalid transitions, [Y] missing guards. See report for details."
4. Indicate readiness for implementation

## Context Received (for Chained Skills)

If building on other skills:

```markdown
## Context Received

This analysis builds on:
- project-structure-analyzer v1.0.0 (executed 2024-01-05)
- Key findings: State management structure mapped, transition functions identified
- Assumptions carried forward: State machine rules are documented
```

## Examples

### Example 1: Invalid Transition

**Scenario:** Checking restoreFromArchive function

**Expected Findings:**
- Missing guard: allows shipped → exploring
- Risk: Violates momentum principle
- Fix: Add guard to prevent shipped → exploring

### Example 2: UI Enabling Invalid Transition

**Scenario:** Reviewing UI components

**Expected Findings:**
- "Restore" button shown for shipped prompts
- Risk: Users can trigger invalid transition
- Fix: Hide restore button for shipped state

