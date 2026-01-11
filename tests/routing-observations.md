# Routing Observations

This document records the results of routing validation tests. Each test captures the resolution trace and observations to identify tag taxonomy issues.

## Purpose

Capture learnings during validation. The "Expected skill" field provides a direct diff between mental model vs router behavior, which is invaluable when tuning tags.

## Test Results Template

For each test, record:

- **Intent tested:** [The exact intent phrase]
- **Expected skill (human intuition):** [Which skill you expected]
- **Selected skill (router decision):** [Which skill the router chose]
- **Confidence score:** [0.0-1.0]
- **Top candidates (with scores):**
  - Skill name: score
  - Skill name: score
- **Match signals observed:**
  - Tags matched: [list]
  - Surface identified: [if applicable]
  - Outcome identified: [if applicable]
- **Surprises or concerns:** [Any unexpected behavior]
- **Tag conflicts identified:** [Any overlapping tags causing confusion]

---

## Test Results

### Test 1: [Intent Name]

- **Intent tested:** 
- **Expected skill (human intuition):** 
- **Selected skill (router decision):** 
- **Confidence score:** 
- **Top candidates (with scores):**
  - 
  - 
- **Match signals observed:**
  - Tags matched: 
  - Surface identified: 
  - Outcome identified: 
- **Surprises or concerns:** 
- **Tag conflicts identified:** 

---

### Test 2: [Intent Name]

- **Intent tested:** 
- **Expected skill (human intuition):** 
- **Selected skill (router decision):** 
- **Confidence score:** 
- **Top candidates (with scores):**
  - 
  - 
- **Match signals observed:**
  - Tags matched: 
  - Surface identified: 
  - Outcome identified: 
- **Surprises or concerns:** 
- **Tag conflicts identified:** 

---

### Test 3: [Intent Name]

- **Intent tested:** 
- **Expected skill (human intuition):** 
- **Selected skill (router decision):** 
- **Confidence score:** 
- **Top candidates (with scores):**
  - 
  - 
- **Match signals observed:**
  - Tags matched: 
  - Surface identified: 
  - Outcome identified: 
- **Surprises or concerns:** 
- **Tag conflicts identified:** 

---

### Test 4: [Intent Name]

- **Intent tested:** 
- **Expected skill (human intuition):** 
- **Selected skill (router decision):** 
- **Confidence score:** 
- **Top candidates (with scores):**
  - 
  - 
- **Match signals observed:**
  - Tags matched: 
  - Surface identified: 
  - Outcome identified: 
- **Surprises or concerns:** 
- **Tag conflicts identified:** 

---

### Test 5: [Intent Name]

- **Intent tested:** 
- **Expected skill (human intuition):** 
- **Selected skill (router decision):** 
- **Confidence score:** 
- **Top candidates (with scores):**
  - 
  - 
- **Match signals observed:**
  - Tags matched: 
  - Surface identified: 
  - Outcome identified: 
- **Surprises or concerns:** 
- **Tag conflicts identified:** 

---

### Test 6: [Intent Name]

- **Intent tested:** 
- **Expected skill (human intuition):** 
- **Selected skill (router decision):** 
- **Confidence score:** 
- **Top candidates (with scores):**
  - 
  - 
- **Match signals observed:**
  - Tags matched: 
  - Surface identified: 
  - Outcome identified: 
- **Surprises or concerns:** 
- **Tag conflicts identified:** 

---

### Test 7: [Intent Name]

- **Intent tested:** 
- **Expected skill (human intuition):** 
- **Selected skill (router decision):** 
- **Confidence score:** 
- **Top candidates (with scores):**
  - 
  - 
- **Match signals observed:**
  - Tags matched: 
  - Surface identified: 
  - Outcome identified: 
- **Surprises or concerns:** 
- **Tag conflicts identified:** 

---

## Summary Analysis

After completing all tests, document patterns here:

### Tag Overlap Issues
- [Skills that always come second]
- [Tags that cause confusion between skills]

### Surprising Matches
- [Tags too broad]
- [Unexpected routing decisions]

### Missing Discriminators
- [Tags too narrow]
- [Skills that should match but don't]

### Confusing Tag Pairs
- [Examples like `ux` vs `ui`, `failure-modes` vs `stress-test`]

---

## Next Steps

1. Review observations to identify tag taxonomy issues
2. Refine tags based on findings (one deliberate pass)
3. Document final taxonomy in `meta/tag-taxonomy.md`
4. Lock taxonomy as stable API

