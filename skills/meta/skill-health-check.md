---
name: skill-health-check
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

# Skill Health Check

## Purpose

Validates that skill definition files are well-formed, complete, and follow the template structure. This meta-skill prevents broken or incomplete skills from being committed to the repository.

## When to Invoke

### Explicit Trigger Phrases

- "Validate skill [skill-name]"
- "Check skill health for [skill]"
- "Run skill-health-check on [skill-file]"
- "Verify skill definition"

### Situational Triggers

- Before committing new skills
- When updating existing skills
- As part of CI/CD validation
- When troubleshooting skill issues
- During repository maintenance

## Required Cursor Settings

- **Mode**: Composer or Chat
- **Model preference**: Claude Sonnet
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Validate YAML front matter structure
- Check all required sections present
- Verify prerequisites are resolvable
- Validate version format
- Check execution modes are valid
- Ensure template compliance

### What It Must Avoid

- Don't validate skill logic (only structure)
- Don't check if skill works correctly (only definition)
- Don't modify the skill (only validate)
- Don't check handoff report quality (that's handoff-quality-validator)

### What It Must Prioritize

- YAML front matter validity
- Required sections presence
- Prerequisite resolvability
- Version format correctness
- Template compliance

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Validating complete skill definition
- Comprehensive health check
- Pre-commit validation

**Input:**
- Complete skill definition file
- TEMPLATE.md for reference

**Process:**
1. Parse and validate YAML front matter
2. Check all required sections present
3. Verify prerequisites are resolvable
4. Validate version format
5. Check execution modes
6. Validate template compliance
7. Generate health report

**Invocation Example:**
> "Run skill-health-check in full-scan mode on skills/architecture/architecture-review.md"

### Incremental Mode

**When to Use:**
- Validating skill updates
- Checking specific changes
- Re-validation after edits

**Input:**
- Skill definition file
- Changed sections (if known)

**Process:**
1. Re-validate changed sections
2. Check if updates maintain compliance
3. Verify no regressions
4. Report validation results

**Invocation Example:**
> "Run skill-health-check in incremental mode on updated skill"

### Targeted Mode

**When to Use:**
- Validating specific aspect
- Checking YAML front matter only
- Focused validation

**Input:**
- Skill definition file
- Specific aspect to validate (YAML, sections, prerequisites, etc.)

**Process:**
1. Deep validation of target aspect
2. Check specific requirements
3. Provide focused feedback

**Invocation Example:**
> "Run skill-health-check in targeted mode on YAML front matter"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Validating Skill Execution**
- **Instead:** Test the skill by running it, use test-runner for execution validation
- **Why:** This skill only validates the definition file structure, not whether the skill actually works.

**Anti-Pattern 2: Validating Handoff Reports**
- **Instead:** Use handoff-quality-validator for report validation
- **Why:** This skill validates skill definitions, not the outputs they produce.

**Anti-Pattern 3: Fixing Skills**
- **Instead:** This skill validates, it doesn't fix. Fix the skill manually.
- **Why:** This is a validation tool, not an editor.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot validate skill logic or correctness
- **Mitigation:** This skill only checks structure. Skill correctness requires testing.
- **Confidence:** 100% on structure validation, 0% on logic validation (by design)

**Limitation:** Cannot verify prerequisites actually exist
- **Mitigation:** Checks if prerequisites are referenced correctly, but cannot verify files/skills exist
- **Confidence:** 100% on format validation, ~90% on existence (if repository is complete)

## Known Limitations

- Only validates structure, not skill logic
- Cannot verify prerequisites actually exist (only format)
- Cannot test if skill works correctly
- Requires skill to follow TEMPLATE.md structure

## Fallback Strategy

If this skill fails, try:

1. **Manual template check**: Review TEMPLATE.md and compare manually
2. **Check YAML syntax**: Use YAML validator
3. **Review sections**: Check all required sections are present
4. **Fix and re-validate**: Make corrections and re-run

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Skill being validated
   - Validation scope
   - Template version used

2. **Findings**
   - YAML front matter issues (Critical/High/Medium/Low)
   - Missing required sections
   - Invalid version format
   - Unresolvable prerequisites
   - Template compliance issues

3. **Recommendations**
   - Fixes needed for compliance
   - Section additions needed
   - YAML corrections
   - Each with specific guidance

4. **Implementation Steps**
   - How to fix each issue
   - Section-by-section fixes
   - YAML front matter corrections

5. **Files to Modify/Create**
   - Skill definition file (if fixes provided)
   - N/A if only validation (no fixes)

6. **Dependencies**
   - TEMPLATE.md referenced
   - Validation rules applied

### Validation Checklist

The validator checks:

**YAML Front Matter:**
- [ ] Valid YAML syntax
- [ ] All required fields present (name, category, version, maturity, etc.)
- [ ] Version format is semantic (X.Y.Z)
- [ ] Maturity level is valid (draft/validated/hardened/deprecated)
- [ ] Complexity level is valid (simple/moderate/complex/expert)
- [ ] Estimated cost is valid (low/medium/high/extreme)
- [ ] Execution modes are valid (full-scan/incremental/targeted)

**Required Sections:**
- [ ] Purpose section present
- [ ] When to Invoke section present
- [ ] Required Cursor Settings section present
- [ ] Behavioral Rules section present
- [ ] Execution Mode Implementation section present
- [ ] Common Misuses / Anti-Patterns section present
- [ ] Known Limitations section present
- [ ] Fallback Strategy section present
- [ ] Output Contract section present
- [ ] Exit Conditions section present

**Prerequisites:**
- [ ] Prerequisites format is valid
- [ ] Prerequisites reference skills or files correctly
- [ ] Reason provided for each prerequisite

### Filename Convention

Validation reports follow: `YYYY-MM-DD_skill-health-check_skill-name.md`

## Exit Conditions

### Success

- Skill validated successfully
- All requirements met
- Issues identified (if any)
- Validation report generated

### Failure

- Skill file not found - fail with clear error
- Invalid YAML - report syntax errors
- Missing required sections - list missing sections
- Critical violations found - report as validation failure

### Handoff to Cursor

After execution:
1. Generate validation report per protocol
2. Save report with proper filename
3. Provide summary: "Skill health check complete. [X] issues found. Skill is [compliant/non-compliant]."
4. If non-compliant, provide specific fixes needed

## Examples

### Example 1: Valid Skill

**Scenario:** Validating a well-formed skill definition

**Expected Output:**
- YAML front matter valid ✓
- All sections present ✓
- Prerequisites valid ✓
- Version format correct ✓
- **Result:** Compliant

### Example 2: Invalid Skill

**Scenario:** Validating skill with missing sections

**Expected Output:**
- Missing: Execution Mode Implementation section ✗
- Invalid version: `1.0` (should be `1.0.0`) ✗
- Missing prerequisite reason ✗
- **Result:** Non-compliant
- **Recommendations:** Add missing section, fix version format, add prerequisite reasons

