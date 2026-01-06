# Test Runner

## Overview

This document defines validation criteria and procedures for testing agent skills.

## What "Validated" Maturity Means

A skill reaches "validated" maturity when it:

1. **Meets Protocol Standards**
   - Handoff reports follow `protocols/handoff-protocol.md`
   - All required sections present
   - Filename convention correct
   - Context budget respected

2. **Produces Consistent Results**
   - Same input produces similar output
   - Results are reproducible
   - No random or non-deterministic behavior

3. **Handles Edge Cases**
   - Works with small codebases (< 1000 lines)
   - Works with large codebases (> 50k lines)
   - Handles missing files gracefully
   - Handles malformed input

4. **Validates Prerequisites**
   - Fails clearly when prerequisites missing
   - Provides helpful error messages
   - Doesn't proceed with invalid state

5. **Respects Execution Modes**
   - Full-scan mode works correctly
   - Incremental mode only analyzes changes
   - Targeted mode focuses on scope

## Test Structure

### Test Fixtures

Place sample codebases in `tests/fixtures/`:

```
tests/fixtures/
├── simple-project/          # Minimal codebase
├── medium-project/          # Typical project
├── large-project/           # Complex codebase
└── edge-cases/              # Special scenarios
    ├── no-dependencies/
    ├── circular-deps/
    └── missing-files/
```

### Expected Outputs

Place known-good handoff reports in `tests/expected-outputs/`:

```
tests/expected-outputs/
├── project-structure-analyzer_simple-project.md
├── architecture-review_medium-project.md
└── dependency-health-check_edge-cases.md
```

## Validation Criteria

### 1. Protocol Compliance

**Check:**
- [ ] Handoff report has all required sections
- [ ] Filename follows convention
- [ ] Context budget respected (< 4000 tokens for main report)
- [ ] Priority tiers used correctly

**Command:**
```bash
# Run handoff-quality-validator on output
```

### 2. Content Quality

**Check:**
- [ ] Findings are specific and actionable
- [ ] Recommendations are clear
- [ ] Implementation steps are ordered correctly
- [ ] Files list is accurate

### 3. Execution Mode Validation

**Full-Scan Mode:**
- [ ] Analyzes entire codebase
- [ ] No files missed
- [ ] Complete analysis provided

**Incremental Mode:**
- [ ] Only changed files analyzed
- [ ] Context from previous state included
- [ ] Focuses on impact of changes

**Targeted Mode:**
- [ ] Only specified scope analyzed
- [ ] Other files ignored
- [ ] Deep analysis of target area

### 4. Error Handling

**Check:**
- [ ] Missing prerequisites handled gracefully
- [ ] Invalid input produces clear errors
- [ ] Timeout scenarios handled
- [ ] Context limit scenarios handled

## Test Execution

### Manual Testing

1. **Prepare Test Fixture**
   ```bash
   cd tests/fixtures/simple-project
   ```

2. **Run Skill**
   ```bash
   # In Warp or agent environment
   Run project-structure-analyzer in full-scan mode
   ```

3. **Compare Output**
   ```bash
   # Compare generated report with expected output
   diff generated-report.md tests/expected-outputs/project-structure-analyzer_simple-project.md
   ```

4. **Validate Protocol**
   ```bash
   # Run validator
   Run handoff-quality-validator on generated-report.md
   ```

### Automated Testing (Future)

When automated testing is implemented:

```bash
# Run all tests
npm test

# Run specific skill tests
npm test -- skill-name

# Run with specific fixture
npm test -- skill-name --fixture=simple-project
```

## Test Cases

### Test Case 1: Basic Functionality

**Fixture:** `simple-project`
**Skill:** `project-structure-analyzer`
**Mode:** `full-scan`
**Expected:** Complete codebase map with dependency graph

### Test Case 2: Incremental Analysis

**Fixture:** `medium-project`
**Skill:** `architecture-review`
**Mode:** `incremental`
**Input:** List of changed files
**Expected:** Analysis focused on changed modules only

### Test Case 3: Missing Prerequisites

**Fixture:** `edge-cases/missing-files`
**Skill:** `dependency-health-check`
**Expected:** Clear error message about missing package.json

### Test Case 4: Large Codebase

**Fixture:** `large-project`
**Skill:** `architecture-review`
**Mode:** `full-scan`
**Expected:** Tiered report with summary + detailed analysis file

### Test Case 5: Targeted Analysis

**Fixture:** `medium-project`
**Skill:** `code-quality-audit`
**Mode:** `targeted`
**Input:** `src/auth/` directory
**Expected:** Deep analysis of auth module only

## Success Criteria

A test passes when:

1. **Protocol Compliance**: Handoff report meets all protocol requirements
2. **Content Accuracy**: Findings and recommendations are correct
3. **Completeness**: All expected sections present
4. **Actionability**: Recommendations can be implemented
5. **Reproducibility**: Same input produces similar output

## Continuous Validation

### Pre-Commit Checks

Before promoting a skill to "validated":

- [ ] All test cases pass
- [ ] Protocol compliance verified
- [ ] Edge cases handled
- [ ] Documentation complete

### Periodic Re-validation

Re-test skills periodically:

- After major codebase changes
- When dependencies update
- When protocol changes
- Before promoting to "hardened"

## Reporting Issues

When a test fails:

1. **Document the failure**
   - Which test case failed
   - What was expected
   - What actually happened

2. **Investigate root cause**
   - Check skill logic
   - Verify test fixture
   - Review protocol requirements

3. **Fix and re-test**
   - Update skill if needed
   - Update test if fixture was wrong
   - Re-run test to verify fix

## Test Maintenance

### Updating Expected Outputs

When skill behavior legitimately changes:

1. **Update skill version**
2. **Regenerate expected outputs**
3. **Document what changed**
4. **Update test cases if needed**

### Adding New Test Cases

When new edge cases discovered:

1. **Create test fixture** in `tests/fixtures/`
2. **Run skill** and save expected output
3. **Document test case** in this file
4. **Add to test suite**

