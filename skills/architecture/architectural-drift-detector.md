---
name: architectural-drift-detector
category: architecture
version: 1.0.0
maturity: draft
estimated-cost: medium
typical-runtime: 5-10min
complexity-level: complex
requires-deep-analysis: true
prerequisites:
  - skill: project-structure-analyzer
    reason: "Need codebase structure map to detect drift"
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Architectural Drift Detector

## Purpose

Identifies when new code violates established patterns (e.g., services calling UI, components calling DB directly). Detects boundary violations and proposes refactoring to restore layering.

## When to Invoke

### Explicit Trigger Phrases

- "Run architectural-drift-detector on [codebase/module]"
- "Check for architectural violations"
- "Detect boundary violations"
- "Validate architectural patterns"

### Situational Triggers

- Before major refactoring
- When code quality degrades
- After adding new features
- During architecture review
- When pattern violations are suspected

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Map actual dependency graph
- Compare against intended architecture (service layer → DB, UI → hooks → services)
- Identify boundary violations (e.g., components importing `db` directly)
- Propose refactoring to restore layering
- Document architectural decision records (ADRs)
- Consider context and intent

### What It Must Avoid

- Don't flag legitimate patterns as violations
- Don't ignore context (some violations may be intentional)
- Don't suggest breaking changes without justification
- Don't assume all violations are problems

### What It Must Prioritize

- Direct DB access from components (Critical - breaks layering)
- Services calling UI (High - violates separation)
- Missing abstraction layers (High - tight coupling)
- Pattern inconsistencies (Medium - code quality)
- ADR documentation gaps (Medium - knowledge management)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive architectural audit
- Before major refactoring
- Initial architecture review

**Input:**
- Entire codebase structure
- Dependency graph
- Intended architecture patterns
- Layer definitions

**Process:**
1. Map actual dependency graph
2. Compare with intended architecture
3. Identify boundary violations
4. Find pattern inconsistencies
5. Propose refactoring strategies
6. Generate comprehensive drift report

**Invocation Example:**
> "Run architectural-drift-detector in full-scan mode on entire codebase"

### Incremental Mode

**When to Use:**
- After adding new code
- When modifying architecture
- During feature development

**Input:**
- Changed files
- New dependencies
- Modified patterns

**Process:**
1. Analyze new code for violations
2. Check if boundaries are maintained
3. Verify pattern consistency
4. Report on drift status

**Invocation Example:**
> "Run architectural-drift-detector in incremental mode on files changed in the last commit"

### Targeted Mode

**When to Use:**
- Reviewing specific module
- Validating single component
- Focused drift check

**Input:**
- Specific module or component
- Targeted dependency graph

**Process:**
1. Deep analysis of target architecture
2. Check all boundary violations
3. Verify pattern adherence
4. Provide focused recommendations

**Invocation Example:**
> "Run architectural-drift-detector in targeted mode on src/components/ directory"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Code Quality Issues**
- **Instead:** Use code-quality-audit for code-level problems
- **Why:** This skill focuses on architectural patterns, not code quality.

**Anti-Pattern 2: Performance Issues**
- **Instead:** Use performance-budget-guardian for performance concerns
- **Why:** This skill validates architecture, not performance.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot detect runtime architectural violations
- **Mitigation:** Focus on static code analysis. Recommend runtime architecture validation.
- **Confidence:** ~90% accuracy on static analysis, runtime validation needed for full picture

## Known Limitations

- Cannot test actual runtime behavior (static analysis only)
- May miss context-dependent violations
- Requires intended architecture to be documented
- Cannot verify architecture in production

## Fallback Strategy

If this skill fails, try:

1. **Manual architecture review**: Review architecture diagram and code manually
2. **Dependency analysis tools**: Use tools to visualize dependency graph
3. **Targeted mode**: Focus on specific modules
4. **Architecture documentation**: Review ADRs and architecture docs

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Codebase analyzed
   - Intended architecture referenced
   - Analysis scope

2. **Findings**
   - Boundary violations (Critical/High/Medium/Low)
   - Pattern inconsistencies
   - Missing abstraction layers
   - ADR documentation gaps
   - Each finding includes location, violation type, and fix

3. **Recommendations**
   - Refactoring strategies (prioritized)
   - Boundary restoration
   - Abstraction layer additions
   - ADR documentation
   - Each with effort estimate

4. **Implementation Steps**
   - Ordered refactoring
   - Boundary fixes
   - Abstraction implementations

5. **Files to Modify/Create**
   - Violating files
   - Refactored files
   - ADR documentation

6. **Dependencies**
   - Architecture patterns referenced
   - Refactoring tools recommended

### Filename Convention

Reports must follow: `YYYY-MM-DD_architectural-drift-detector_target-component.md`

## Exit Conditions

### Success

- Architectural drift detected
- Violations identified
- Recommendations provided
- Handoff report generated

### Failure

- No codebase structure found - fail with clear error
- Unreadable code - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Architectural drift detection complete. Found [X] boundary violations, [Y] pattern inconsistencies. See report for refactoring strategies."
4. Indicate readiness for refactoring

