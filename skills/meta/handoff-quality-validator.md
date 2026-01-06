---
name: handoff-quality-validator
category: meta
version: 1.0.0
maturity: validated
estimated-cost: low
typical-runtime: 1-2min
complexity-level: simple
requires-deep-analysis: false
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Handoff Quality Validator

## Purpose

Validates that handoff reports produced by other skills meet the protocol standards defined in `protocols/handoff-protocol.md`. This meta-skill ensures consistency and quality across all skill outputs.

## When to Invoke

### Explicit Trigger Phrases

- "Validate handoff report [filename]"
- "Check if [report] meets protocol"
- "Run handoff-quality-validator on [report]"
- "Verify handoff report quality"

### Situational Triggers

- After any skill generates a handoff report
- Before handing off to Cursor for implementation
- As part of skill chain validation
- When troubleshooting handoff issues

## Required Cursor Settings

- **Mode**: Composer or Chat
- **Model preference**: Claude Sonnet
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Check all required sections are present
- Verify section content quality
- Validate filename convention
- Check context budget compliance
- Ensure recommendations are actionable
- Verify priority tiers are used correctly

### What It Must Avoid

- Don't validate the correctness of findings (that's not its job)
- Don't suggest content changes (only structure validation)
- Don't modify the report (only validate)
- Don't check implementation feasibility (only protocol compliance)

### What It Must Prioritize

- Protocol compliance (required sections)
- Filename convention
- Context budget management
- Actionability of recommendations
- Completeness of information

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Validating complete handoff report
- Comprehensive quality check
- Pre-implementation validation

**Input:**
- Complete handoff report file
- Protocol specification

**Process:**
1. Check all required sections present
2. Validate section content quality
3. Verify filename convention
4. Check context budget compliance
5. Validate priority tiers
6. Generate validation report

**Invocation Example:**
> "Run handoff-quality-validator in full-scan mode on 2024-01-05_architecture-review_auth-service.md"

### Incremental Mode

**When to Use:**
- Validating updated report
- Checking specific sections
- Re-validation after edits

**Input:**
- Handoff report file
- Changed sections (if known)

**Process:**
1. Re-validate changed sections
2. Check if updates maintain compliance
3. Verify no regressions
4. Report validation results

**Invocation Example:**
> "Run handoff-quality-validator in incremental mode on updated report"

### Targeted Mode

**When to Use:**
- Validating specific section
- Checking particular aspect
- Focused validation

**Input:**
- Handoff report file
- Specific section or aspect to validate

**Process:**
1. Deep validation of target section
2. Check specific protocol requirements
3. Provide focused feedback

**Invocation Example:**
> "Run handoff-quality-validator in targeted mode on the Recommendations section"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Validating Content Correctness**
- **Instead:** This skill only validates structure and protocol compliance, not content accuracy
- **Why:** Content validation requires domain expertise. This skill ensures format and completeness.

**Anti-Pattern 2: Fixing Reports**
- **Instead:** This skill validates, it doesn't fix. Fix the report manually or re-run the generating skill.
- **Why:** This is a validation tool, not an editor.

**Anti-Pattern 3: Validating Non-Handoff Documents**
- **Instead:** Only use on handoff reports following the protocol
- **Why:** This skill is specifically for handoff report validation, not general document validation.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot validate content accuracy
- **Mitigation:** This skill only checks structure. Content accuracy requires domain review.
- **Confidence:** 100% on structure validation, 0% on content accuracy (by design)

## Known Limitations

- Only validates structure, not content correctness
- Cannot fix reports, only identify issues
- Requires handoff report to be in markdown format
- May not catch all edge cases in complex reports

## Fallback Strategy

If this skill fails, try:

1. **Manual protocol check**: Review `protocols/handoff-protocol.md` manually
2. **Check filename**: Ensure it follows convention
3. **Review sections**: Check all required sections are present
4. **Re-run generating skill**: If report is invalid, regenerate it

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Report being validated
   - Validation scope
   - Protocol version used

2. **Findings**
   - Protocol compliance issues (Critical/High/Medium/Low)
   - Missing sections
   - Filename convention violations
   - Context budget violations
   - Quality issues (unclear recommendations, etc.)

3. **Recommendations**
   - Fixes needed for compliance
   - Section improvements
   - Format corrections
   - Each with specific guidance

4. **Implementation Steps**
   - How to fix each issue
   - Section-by-section fixes
   - Filename correction if needed

5. **Files to Modify/Create**
   - Handoff report file (if fixes provided)
   - N/A if only validation (no fixes)

6. **Dependencies**
   - Protocol specification referenced
   - Validation rules applied

### Validation Checklist

The validator checks:

- [ ] All required sections present (Context Summary, Findings, Recommendations, Implementation Steps, Files to Modify/Create, Dependencies)
- [ ] Filename follows convention: `YYYY-MM-DD_skill-name_target-component.md`
- [ ] Context budget respected (< 4000 tokens for main report, or tiered structure)
- [ ] Priority tiers used correctly (Critical/High/Medium/Low)
- [ ] Recommendations are actionable
- [ ] Implementation steps are specific
- [ ] Files list is accurate
- [ ] No placeholder text (unless intentional)

### Filename Convention

Validation reports follow: `YYYY-MM-DD_handoff-quality-validator_original-report-name.md`

## Exit Conditions

### Success

- Report validated successfully
- All protocol requirements met
- Quality issues identified (if any)
- Validation report generated

### Failure

- Report file not found - fail with clear error
- Unreadable report format - document issues
- Critical protocol violations found - report as validation failure

### Handoff to Cursor

After execution:
1. Generate validation report per protocol
2. Save report with proper filename
3. Provide summary: "Validation complete. [X] issues found. Report is [compliant/non-compliant]."
4. If non-compliant, provide specific fixes needed

## Examples

### Example 1: Valid Report

**Scenario:** Validating a well-formed handoff report

**Expected Output:**
- All sections present ✓
- Filename correct ✓
- Context budget respected ✓
- Recommendations actionable ✓
- **Result:** Compliant

### Example 2: Invalid Report

**Scenario:** Validating report with missing sections

**Expected Output:**
- Missing: Implementation Steps section ✗
- Filename incorrect: `report.md` (should be `YYYY-MM-DD_skill-name_target.md`) ✗
- **Result:** Non-compliant
- **Recommendations:** Add Implementation Steps section, fix filename

