# Routing Validation Test Cases

This document contains real intents to test the skill-router's ability to correctly resolve user intent to appropriate skills.

## Purpose

These test cases are designed to validate the tag taxonomy through real routing behavior. Each intent should be tested manually using the skill-router, and results should be documented in `routing-observations.md`.

## Test Intents

### Test 1: Adversarial UX Testing
**Intent:** "Stress test onboarding UX for failure modes"

**Expected behavior:** Should route to `adversarial-ui-tester` with high confidence

**Why this test:** Validates that adversarial/UX/failure-mode tags work correctly

---

### Test 2: UI Copy Analysis
**Intent:** "Check if UI copy introduces coercive patterns"

**Expected behavior:** Should route to `ux-copy-neutrality-checker` with high confidence

**Why this test:** Validates UX/copy/language tags and ensures it doesn't match adversarial-ui-tester

---

### Test 3: Architectural Drift Detection
**Intent:** "Review architectural drift in state boundaries"

**Expected behavior:** Should route to `architectural-drift-detector` with high confidence

**Why this test:** Validates architecture/drift/boundaries tags

---

### Test 4: Performance Regression Audit
**Intent:** "Audit performance regressions in capture surface"

**Expected behavior:** Should route to `capture-surface-focus-auditor` or `performance-budget-guardian`

**Why this test:** Tests performance/focus/ux tag overlap and scope precedence

---

### Test 5: Test Coverage Gap Finding
**Intent:** "Find gaps in test coverage for privacy-critical paths"

**Expected behavior:** Should route to `test-coverage-gap-finder` with high confidence

**Why this test:** Validates testing/coverage/quality tags and privacy domain recognition

---

### Test 6: Bundle Size Analysis
**Intent:** "Analyze bundle size impact of new dependencies"

**Expected behavior:** Should route to `bundle-size-analyzer` with high confidence

**Why this test:** Validates performance/bundle/dependencies tags

---

### Test 7: API Boundary Validation
**Intent:** "Validate API boundaries for local-first compliance"

**Expected behavior:** Should route to `api-boundary-validator` with high confidence

**Why this test:** Validates api/boundaries/security/local-first tags

---

## Testing Instructions

1. For each intent, invoke the skill-router (via Warp or manually)
2. Record the resolution trace in `routing-observations.md`
3. Note any surprises, low confidence scores, or unexpected matches
4. After all tests, analyze patterns in the observations

## Success Criteria

- All intents route to expected skills with confidence >= 0.7
- No surprising matches or tag conflicts
- Clear discrimination between similar skills (e.g., adversarial-ui-tester vs ux-copy-neutrality-checker)

