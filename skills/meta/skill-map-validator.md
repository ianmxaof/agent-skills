---
name: skill-map-validator
category: meta
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 1-3min
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
  - skill-map
  - references
  - configuration
  - integrity
prerequisites: []
execution-modes:
  - full-scan
  - targeted
---

# Skill Map Validator

## Purpose

Validates that skill maps reference existing skills and catches broken references before runtime. Ensures skill maps are correctly configured and all referenced skills exist in their expected locations.

## Scope and Classification

**Scope:** `meta` - Meta-skill for skill management

**Tier:** `meta` - Skill management and validation

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## When to Invoke

### Explicit Trigger Phrases

- "Run skill-map-validator on this project's skill map"
- "Validate skill map configuration"
- "Check for broken skill references"
- "Validate .agent-skills/skill-map.yaml"

### Situational Triggers

- After creating or modifying skill-map.yaml
- Before deploying agent workflows
- When skill references fail at runtime
- During project setup
- After moving or renaming skills

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Read `.agent-skills/skill-map.yaml` (or specified skill map file)
- For each skill in `universal-skills`, `domain-skills`, `project-skills`:
  - Check if skill file exists in expected location
  - Validate front matter is complete
  - Check for required fields (scope, tier, etc.)
- For each override:
  - Check if base skill exists
  - Validate override file exists
  - Verify override structure
- For each chain:
  - Check if all referenced skills exist
  - Detect circular dependencies
  - Validate chain structure
- Produce validation report with errors, warnings, and recommendations

### What It Must Avoid

- Don't modify skill maps (only validate)
- Don't create missing skills (only report)
- Don't assume skill locations without checking
- Don't ignore warnings (report all issues)

### What It Must Prioritize

- Missing skill files (Critical - will cause runtime failures)
- Broken override references (High - overrides won't work)
- Circular dependencies in chains (High - infinite loops)
- Missing front matter fields (Medium - incomplete metadata)
- Chain validation issues (Medium - chains may fail)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive skill map validation
- Initial project setup validation
- Before deploying workflows

**Input:**
- `.agent-skills/skill-map.yaml` (or specified path)
- Skill definitions in expected locations
- Override files (if any)

**Process:**
1. Read and parse skill-map.yaml
2. Validate YAML structure
3. Check all universal-skills references
4. Check all domain-skills references
5. Check all project-skills references
6. Validate all overrides
7. Validate all chains
8. Generate comprehensive validation report

**Invocation Example:**
> "Run skill-map-validator in full-scan mode on this project's skill map"

### Targeted Mode

**When to Use:**
- Validating specific skill map file
- Checking specific skill references
- Focused validation

**Input:**
- Specific skill map file path
- Targeted skill references

**Process:**
1. Read specified skill map
2. Validate targeted references
3. Check specific skills or chains
4. Provide focused validation report

**Invocation Example:**
> "Run skill-map-validator in targeted mode on .agent-skills/skill-maps/development.yaml"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Skill Definition Validation**
- **Instead:** Use skill-health-check for skill definition validation
- **Why:** This skill validates skill map references, not skill definition quality.

**Anti-Pattern 2: Skill Effectiveness Analysis**
- **Instead:** Use skill-effectiveness-analyzer for effectiveness analysis
- **Why:** This skill validates references, not skill usage or effectiveness.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot validate skill behavior, only references
- **Mitigation:** Use skill-health-check for skill definition validation
- **Confidence:** ~100% accuracy on reference validation, 0% on behavior validation

## Known Limitations

- Only validates references, not skill behavior
- Cannot detect semantic issues (wrong skill for task)
- Requires skill map to be valid YAML
- Cannot validate skills in external repositories

## Fallback Strategy

If this skill fails, try:

1. **Manual validation**: Check skill map YAML syntax manually
2. **YAML validator**: Use YAML linter to check syntax
3. **File system check**: Manually verify skill files exist
4. **Targeted mode**: Validate specific sections

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Skill map file analyzed
   - Total skills referenced
   - Analysis scope

2. **Findings**
   - **Errors (must fix):**
     - Missing skill files
     - Broken references
     - Invalid YAML structure
     - Circular dependencies
   - **Warnings (should fix):**
     - Missing front matter fields
     - Chain validation issues
     - Override structure issues
   - Each finding includes:
     - Severity (Error/Warning)
     - Location (skill map path, line number if available)
     - Description
     - Expected location
     - Fix recommendation

3. **Recommendations**
   - How to fix errors (prioritized)
   - How to address warnings
   - Best practices for skill map configuration
   - Each with effort estimate

4. **Implementation Steps**
   - Ordered fixes
   - Skill map updates needed
   - File creation/movement needed

5. **Files to Modify/Create**
   - Skill map file (if fixes needed)
   - Missing skill files (create or move)
   - Override files (if missing)

6. **Dependencies**
   - Skill map file referenced
   - Skill definitions referenced

### Filename Convention

Reports must follow: `YYYY-MM-DD_skill-map-validator_target-component.md`

### Example Output Structure

```yaml
Validation Results:

Errors (must fix):
  - Skill not found: react-hooks-misuse-detector
    Referenced in: domain-skills
    Expected location: agent-skills/skills/domains/react-apps/react-hooks-misuse-detector.md
    Fix: Remove from skill map or create skill file
    
  - Override base skill not found: test-coverage-gap-finder
    Referenced in: overrides[0]
    Expected location: agent-skills/skills/core/test-coverage-gap-finder.md
    Fix: Create base skill or remove override

Warnings (should fix):
  - Skill missing tier field: architectural-drift-detector
    Location: agent-skills/skills/core/architectural-drift-detector.md
    Fix: Add tier field to front matter
    
  - Chain references non-existent skill: pre-deployment → focus-auditor
    Location: chains.pre-deployment
    Fix: Remove focus-auditor from chain or create skill

Recommendations:
  - Remove react-hooks-misuse-detector from skill map (skill doesn't exist yet)
  - Create test-coverage-gap-finder in core/ or remove override
  - Add tier field to architectural-drift-detector front matter
  - Fix pre-deployment chain (remove or create focus-auditor skill)
```

## Exit Conditions

### Success

- Skill map validated
- All references checked
- Errors and warnings identified
- Handoff report generated

### Failure

- Invalid YAML - fail with clear error
- Skill map file not found - fail with clear error
- Unreadable skill map - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Skill map validation complete. Found [X] errors, [Y] warnings. See report for details and fixes."
4. Indicate readiness for fixes

## Examples

### Example 1: Valid Skill Map

**Scenario:** Validating a correctly configured skill map

**Expected Output:**
- No errors
- Minimal warnings (if any)
- All skills found in expected locations
- All chains valid

### Example 2: Broken References

**Scenario:** Skill map references non-existent skills

**Expected Output:**
- Errors for missing skills
- Recommendations to remove or create skills
- Clear fix instructions

