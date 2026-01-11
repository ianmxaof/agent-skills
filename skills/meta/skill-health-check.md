---
type: skill-definition
name: skill-health-check
category: meta
version: 1.1.0
maturity: validated
lifecycle: validated
estimated-cost: low
typical-runtime: 1-2min
complexity-level: simple
requires-deep-analysis: false
scope: meta
tier: meta
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - meta
  - validation
  - quality
  - format
  - template
  - health
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Skill Health Check

## Purpose

Validates that skill definition files are well-formed, complete, and follow the template structure. This meta-skill prevents broken or incomplete skills from being committed to the repository.

## Scope and Classification

**Scope:** `meta` - Governance skill that operates on other skills

**Tier:** `meta` - Skill management (health checks, validation)

**Type:** `skill-definition` - This is an executable skill

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

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
- Check execution modes are valid (with meta-specific allowances)
- Ensure template compliance
- Validate artifact-type field when present

### What It Must Avoid

- Don't validate skill logic (only structure)
- Don't check if skill works correctly (only definition)
- Don't modify the skill (only validate)
- Don't check handoff report quality (that's handoff-quality-validator)
- Don't reject valid meta scope or custom execution modes for meta skills

### What It Must Prioritize

- YAML front matter validity
- Required sections presence
- Prerequisite resolvability
- Version format correctness
- Template compliance
- Correct handling of meta scope and type field

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
2. Check `type` field (distinguish skills from non-skills)
3. Check all required sections present
4. Verify prerequisites are resolvable
5. Validate version format
6. Check execution modes (standard or meta-extended)
7. Validate artifact-type if present
8. Generate health report

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

**Anti-Pattern 4: Rejecting Valid Meta Skills**
- **Instead:** Accept `scope: meta` and custom execution modes for meta skills
- **Why:** Meta skills have different requirements than domain skills.

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
   - Type and scope validation results

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
- [ ] `type` field present (skill-definition | changelog | readme)
- [ ] All required fields present (name, category, version, maturity, etc.)
- [ ] Version format is semantic (X.Y.Z)
- [ ] Maturity level is valid (draft/validated/hardened/deprecated)
- [ ] Complexity level is valid (simple/moderate/complex/expert)
- [ ] Estimated cost is valid (low/medium/high/extreme)
- [ ] Scope is valid (core/domain/project/meta)
- [ ] Execution modes are valid (see below)
- [ ] `artifact-type` is valid if present (raw-findings/refined-findings/implementation-plan)

**Execution Mode Validation:**
- Standard skills: `full-scan`, `incremental`, `targeted` (required set)
- Meta skills (`scope: meta`): May include custom modes like `change-analysis`, `assessment`, `intentless`

**Type-Aware Validation:**
- If `type: skill-definition` → validate as skill
- If `type: changelog` or `type: readme` → skip skill validation (not a skill)
- If `type` missing → warn and validate as skill (backwards compatibility)

**Required Sections (for skill-definition only):**
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
- Type: skill-definition ✓
- Scope: core ✓
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

### Example 3: Meta Skill with Custom Modes

**Scenario:** Validating a meta skill with custom execution modes

**Expected Output:**
- YAML front matter valid ✓
- Type: skill-definition ✓
- Scope: meta ✓ (custom modes allowed)
- Execution modes: full-scan, assessment, intentless ✓ (valid for meta)
- All sections present ✓
- **Result:** Compliant

### Example 4: Non-Skill Document

**Scenario:** Validating a changelog file

**Expected Output:**
- Type: changelog ✓
- **Result:** Skipped (not a skill definition)
- **Note:** File correctly identified as non-skill document
