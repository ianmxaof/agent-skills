# Column Pattern Examples

This document provides worked examples of the 2-agent column pattern in action.

## Example 1: Full Column Execution (Single Column)

### Scenario

You want to audit the checkout flow for adversarial UX issues before release.

### Step 1: Invoke the Column

```
User: "Run UX/Adversarial column on the checkout flow"
```

### Step 2: Agent A Executes (Exploration)

Agent A receives instructions from `agent-a-instruction-template.md`:

```markdown
You are Agent A (Exploration Layer) in the UX/Adversarial column.

Skill: adversarial-ui-tester
Target: checkout flow
Posture: exploratory (maximize coverage, allow mess)
```

**Agent A Output (Raw):**

```yaml
---
skill: adversarial-ui-tester
status: raw
refinement-needed: true
finding-count: 15
---

## Raw Findings

1. Form validation bypass: User can submit without filling required fields by tabbing and pressing enter
2. No loading state when payment processing - user might click multiple times
3. Error message for declined card uses technical language ("ERR_CARD_DECLINED_01")
4. Same error message as #3 but slightly different wording found on another path
5. Back button loses cart contents without warning
6. Back button issue also affects saved payment methods
7. Address autocomplete doesn't work with screen readers
8. Price changes silently if item goes out of stock mid-checkout
9. Shipping options loading is slow, no skeleton loader
10. Similar to #9 - payment options also slow to load
11. "Edit" button on order summary is tiny and hard to click on mobile
12. No confirmation before placing order
13. Coupon field accepts invalid codes without error message
14. Coupon field - error appears but disappears after 2 seconds
15. Accessibility: Focus indicator missing on primary CTA button
```

**Note:** Agent A output is messy, has duplicates (3/4, 5/6, 9/10, 13/14), and is unranked. This is intentional.

### Step 3: Agent B Processes (Refinement)

Agent B receives Agent A's output and applies refinement:

```markdown
You are Agent B (Refinement Layer) in the UX/Adversarial column.

Mode: generic
Input: Agent A's 15 findings
Job: Deduplicate, rank, clarify, package
```

**Agent B Processing:**

| Agent A Findings | Agent B Action |
|------------------|----------------|
| 1 (form bypass) | Keep - critical |
| 2 (no loading state) | Keep - high |
| 3, 4 (error messages) | Merge → Finding 3 |
| 5, 6 (back button) | Merge → Finding 4 |
| 7 (accessibility) | Keep - high |
| 8 (silent price change) | Keep - critical |
| 9, 10 (slow loading) | Merge → Finding 6 |
| 11 (tiny button) | Keep - medium |
| 12 (no confirmation) | Keep - high |
| 13, 14 (coupon errors) | Merge → Finding 8 |
| 15 (focus indicator) | Merge with #7 |

### Step 4: Agent B Writes Artifact

**File:** `.agent-skills/artifacts/incoming/adversarial-ui-tester-2026-01-07T20-00-00Z.md`

```yaml
---
skill: adversarial-ui-tester
scope: core
status: new
timestamp: 2026-01-07T20:00:00Z
intended-consumer: cursor
priority: critical
column: ux-adversarial
refinement-layer: generic
agent-a-coverage: 15 findings
agent-b-output: 8 findings
---

## Summary

- 2 critical issues: form validation bypass and silent price changes
- 3 high-priority accessibility and UX gaps
- 3 medium-priority polish issues
- Checkout flow has significant adversarial vulnerabilities

## Detailed Findings

### Finding 1: Form Validation Bypass [CRITICAL]

- **Severity:** critical
- **Issue:** Users can submit checkout form without required fields by using keyboard navigation (tab + enter)
- **Impact:** Invalid orders, failed payments, data integrity issues
- **Reproduction:** Tab through form fields without filling, press Enter on submit button
- **Recommendation:** Implement client-side validation that triggers on submit regardless of input method

### Finding 2: Silent Price Changes [CRITICAL]

- **Severity:** critical
- **Issue:** If an item goes out of stock or price changes during checkout, the cart updates silently without notifying user
- **Impact:** User trust erosion, potential legal issues, support tickets
- **Reproduction:** Start checkout, have admin change item price, proceed to payment
- **Recommendation:** Show explicit notification when cart contents change, require re-confirmation

### Finding 3: No Loading State During Payment [HIGH]

- **Severity:** high
- **Issue:** Payment processing shows no loading indicator, users may click multiple times
- **Impact:** Duplicate charges, failed transactions, user frustration
- **Reproduction:** Submit payment on slow connection
- **Recommendation:** Add loading state, disable button during processing, show progress

### Finding 4: Back Button Loses Data [HIGH]

- **Severity:** high
- **Issue:** Browser back button loses cart contents and saved payment info without warning
- **Impact:** User abandonment, frustration, lost sales
- **Reproduction:** Fill cart, proceed to checkout, press back
- **Recommendation:** Implement navigation guards with confirmation dialog, or persist cart state

### Finding 5: Accessibility Issues [HIGH]

- **Severity:** high
- **Issue:** Multiple accessibility problems: address autocomplete not screen-reader compatible, missing focus indicators on primary CTA
- **Impact:** Excludes users with disabilities, potential ADA compliance issues
- **Reproduction:** Navigate with screen reader, observe missing announcements; tab to submit button, observe missing focus ring
- **Recommendation:** Add ARIA labels to autocomplete, ensure all interactive elements have visible focus states

### Finding 6: Slow Loading Without Feedback [MEDIUM]

- **Severity:** medium
- **Issue:** Shipping and payment options load slowly with no skeleton loader or progress indication
- **Impact:** Users may think checkout is broken, potential abandonment
- **Reproduction:** Load checkout on throttled connection
- **Recommendation:** Add skeleton loaders or spinners for async-loaded sections

### Finding 7: Mobile Usability Issues [MEDIUM]

- **Severity:** medium
- **Issue:** "Edit" button on order summary is very small, difficult to tap on mobile
- **Impact:** Frustration on mobile, lower conversion
- **Reproduction:** View checkout on mobile device, try to tap Edit
- **Recommendation:** Increase tap target size to minimum 44x44px

### Finding 8: Coupon Field Error Handling [MEDIUM]

- **Severity:** medium
- **Issue:** Coupon field accepts invalid codes without error, or shows error that auto-dismisses after 2 seconds
- **Impact:** User confusion, missed discounts, support queries
- **Reproduction:** Enter invalid coupon code
- **Recommendation:** Show persistent error message until user corrects input

## Risks / Edge Cases

- **Duplicate charges:** No idempotency protection visible in payment flow
- **Data loss:** Back navigation can lose significant user input
- **Trust erosion:** Silent price changes may violate user expectations

## Recommendations

- Prioritize findings 1 and 2 before release (critical)
- Address accessibility (finding 5) for compliance
- Do NOT just add a "don't click twice" message for finding 3 — implement proper state management

## Files / Surfaces Involved

- `CheckoutForm.tsx`
- `PaymentProcessor.tsx`
- `CartContext.tsx`
- `OrderSummary.tsx`
- Checkout route navigation handlers

## Handoff Notes for Cursor

- Start with critical findings (1, 2) — these are release blockers
- Finding 5 (accessibility) may require audit of all form components, not just checkout
- Consider implementing a proper form library if validation bypass is systemic
- Defer finding 7 (mobile tap targets) if timeline is tight
```

### Step 5: Cursor Processes

```
User: "Run the standard artifact intake and integration pass."

Cursor:
1. Found 1 artifact in incoming/
   - adversarial-ui-tester-2026-01-07T20-00-00Z.md (column: ux-adversarial)

2. Priority: critical (2 critical findings)

3. Proposed plan:
   - Immediate: Fix form validation bypass, add price change notifications
   - High: Add payment loading states, navigation guards, accessibility fixes
   - Deferred: Mobile tap targets, coupon error handling, skeleton loaders

4. Moving artifact to processed/
```

---

## Example 2: Multiple Parallel Columns

### Scenario

Pre-release audit of the entire checkout module using 4 columns.

### Step 1: Run All Columns

```
User: "Run all configured columns on the checkout module"
```

This triggers 4 columns in parallel (or sequentially):

| Column | Agent A Skill | Agent B Mode |
|--------|--------------|--------------|
| UX/Adversarial | adversarial-ui-tester | generic |
| Architecture | architecture-review | domain-aware (drift-detector) |
| Performance | performance-budget-guardian | domain-aware (bundle-analyzer) |
| Correctness | failure-mode-simulator | generic |

### Step 2: Four Artifacts Produced

```
.agent-skills/artifacts/incoming/
├── adversarial-ui-tester-2026-01-07T20-00-00Z.md    (column: ux-adversarial)
├── architecture-review-2026-01-07T20-05-00Z.md      (column: architecture)
├── performance-budget-guardian-2026-01-07T20-10-00Z.md (column: performance)
└── failure-mode-simulator-2026-01-07T20-15-00Z.md   (column: correctness)
```

### Step 3: Cursor Synthesizes

```
User: "Run the standard artifact intake and integration pass."

Cursor:
┌──────────────────────────────────────────────────────────────────┐
│ ARTIFACT INTAKE REPORT                                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Found 4 artifacts in incoming/                                   │
│                                                                  │
│ 1. adversarial-ui-tester (column: ux-adversarial)               │
│    Findings: 8 (2 critical, 3 high, 3 medium)                   │
│                                                                  │
│ 2. architecture-review (column: architecture)                   │
│    Findings: 4 (1 high, 3 medium)                               │
│                                                                  │
│ 3. performance-budget-guardian (column: performance)            │
│    Findings: 3 (3 medium)                                       │
│                                                                  │
│ 4. failure-mode-simulator (column: correctness)                 │
│    Findings: 5 (1 critical, 2 high, 2 medium)                   │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ CROSS-COLUMN SYNTHESIS                                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ CONVERGENCE DETECTED (high confidence):                          │
│ - Form validation issue found by BOTH UX and Correctness columns│
│   → Elevated to release blocker                                  │
│                                                                  │
│ - Payment error handling found by UX, Architecture, Correctness │
│   → Systemic issue, needs architectural fix                      │
│                                                                  │
│ CONFLICTS DETECTED (needs human review):                         │
│ - Architecture suggests extracting CheckoutContext               │
│ - Performance suggests inlining to reduce bundle size            │
│   → Trade-off decision required                                  │
│                                                                  │
│ UNIQUE FINDINGS (single column):                                 │
│ - UX: Mobile tap targets (medium)                                │
│ - Performance: Lazy-load payment SDK (medium)                    │
│ - Correctness: Race condition in cart sync (high)                │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ CONSOLIDATED PLAN                                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ RELEASE BLOCKERS (3):                                            │
│ 1. Form validation bypass (UX + Correctness)                     │
│ 2. Silent price changes (UX)                                     │
│ 3. Payment retry logic missing (Correctness)                     │
│                                                                  │
│ HIGH PRIORITY (4):                                               │
│ 4. Unified error handling pattern (Architecture + UX)            │
│ 5. Cart sync race condition (Correctness)                        │
│ 6. Accessibility fixes (UX)                                      │
│ 7. Navigation state management (UX)                              │
│                                                                  │
│ DEFERRED (6):                                                    │
│ 8. CheckoutContext extraction (Architecture)                     │
│ 9. Bundle size optimization (Performance)                        │
│ 10. Lazy-load payment SDK (Performance)                          │
│ 11. Mobile tap targets (UX)                                      │
│ 12. Coupon error handling (UX)                                   │
│ 13. Skeleton loaders (UX)                                        │
│                                                                  │
│ NEEDS DISCUSSION:                                                │
│ - Architecture vs Performance trade-off on context extraction    │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ LESSONS EXTRACTED                                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Pattern: Multiple columns finding same issue = systemic problem  │
│ Proposed CLAUDE.md update:                                       │
│ "When 2+ columns report similar findings, treat as architectural"│
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Example 3: Column Artifact with Domain-Aware Refinement

### Scenario

Architecture column using `architectural-drift-detector` as refinement lens.

### Agent A Output (architecture-review)

```yaml
---
skill: architecture-review
status: raw
refinement-needed: true
finding-count: 9
---

## Raw Findings

1. CheckoutContext doing too much - 500+ lines
2. PaymentProcessor tightly coupled to Stripe
3. CartContext and CheckoutContext have overlapping state
4. Direct DOM manipulation in OrderSummary
5. State management inconsistent - mix of context and local state
6. API calls scattered across components
7. No clear data flow pattern
8. Similar to #5 - some components use Redux, others use Context
9. Error boundaries missing in payment section
```

### Agent B Processing (Domain-Aware Mode)

Agent B uses `architectural-drift-detector` as lens:

```markdown
Mode: domain-aware
Domain skill: architectural-drift-detector

Apply drift detection criteria:
- What was the intended pattern?
- Where has it drifted?
- What is the impact of drift?
```

### Agent B Output

```yaml
---
skill: architecture-review
scope: core
status: new
timestamp: 2026-01-07T20:05:00Z
intended-consumer: cursor
priority: high
column: architecture
refinement-layer: domain-aware
domain-skill: architectural-drift-detector
agent-a-coverage: 9 findings
agent-b-output: 4 findings
---

## Summary

- Primary drift: State management pattern inconsistency
- Secondary drift: API call patterns diverged from established approach
- 2 high, 2 medium findings
- Checkout module has accumulated technical debt

## Detailed Findings

### Finding 1: State Management Drift [HIGH]

- **Severity:** high
- **Issue:** Checkout module mixes Context, Redux, and local state without clear pattern
- **Intended Pattern:** Redux for global state, Context for feature-scoped state
- **Observed Drift:** CheckoutContext duplicates CartContext state; some components use Redux checkout slice
- **Impact:** Bugs from state sync, difficult debugging, onboarding friction
- **Recommendation:** Consolidate to single state approach per domain

### Finding 2: API Layer Drift [HIGH]

- **Severity:** high
- **Issue:** API calls made directly in components instead of through service layer
- **Intended Pattern:** All API calls through `services/` directory
- **Observed Drift:** PaymentProcessor and ShippingSelector make direct fetch calls
- **Impact:** Inconsistent error handling, no retry logic, harder to mock for tests
- **Recommendation:** Extract API calls to checkout.service.ts

### Finding 3: Component Coupling [MEDIUM]

- **Severity:** medium
- **Issue:** PaymentProcessor tightly coupled to Stripe SDK
- **Intended Pattern:** Payment providers abstracted behind interface
- **Observed Drift:** Stripe-specific code in component, not payment service
- **Impact:** Switching providers requires component changes, test complexity
- **Recommendation:** Extract to PaymentProvider interface

### Finding 4: Error Boundary Gap [MEDIUM]

- **Severity:** medium
- **Issue:** Payment section lacks error boundary
- **Intended Pattern:** Each major feature section wrapped in error boundary
- **Observed Drift:** Only page-level boundary exists
- **Impact:** Payment errors crash entire checkout instead of graceful degradation
- **Recommendation:** Add error boundary around PaymentSection component

## Drift Analysis Summary

| Area | Intended | Actual | Severity |
|------|----------|--------|----------|
| State | Redux + Context (scoped) | Mixed (3 patterns) | High |
| API | Service layer | Direct fetch | High |
| Payments | Provider interface | Stripe hardcoded | Medium |
| Errors | Feature boundaries | Page-level only | Medium |

## Recommendations

- Consolidate state management before adding features
- Extract API layer to enable proper error handling
- Do NOT refactor PaymentProcessor until state is stabilized

## Files / Surfaces Involved

- `CheckoutContext.tsx` - needs major refactor
- `PaymentProcessor.tsx` - coupling issue
- `ShippingSelector.tsx` - direct API calls
- `services/checkout.service.ts` - needs creation

## Handoff Notes for Cursor

- State management is the root cause — fix first
- API extraction can be incremental (one component at a time)
- Error boundaries are quick wins
- Defer payment provider abstraction until state is clean
```

---

## Example 4: No Findings Artifact

### Scenario

Performance column finds no issues.

### Agent B Output

```yaml
---
skill: performance-budget-guardian
scope: core
status: new
timestamp: 2026-01-07T20:10:00Z
intended-consumer: cursor
priority: low
column: performance
refinement-layer: generic
agent-a-coverage: 0 findings
agent-b-output: 0 findings
---

## Summary

- Agent A (exploration) produced no findings for the checkout module
- Bundle size within budget
- No performance regressions detected

## Analysis

- Main bundle: 145KB (budget: 200KB) ✓
- Checkout chunk: 45KB (budget: 75KB) ✓
- No obvious lazy-load candidates
- Core Web Vitals within acceptable range

## Recommendations

- No action required
- Consider this module "green" for performance

## Handoff Notes for Cursor

- Absence of findings is signal — checkout module is performant
- May want to re-run after adding new dependencies
```

---

## Key Takeaways

1. **Agent A is messy by design** — Duplicates and unranked findings are expected
2. **Agent B compresses significantly** — 15 findings → 8 findings is normal
3. **Cursor synthesizes across columns** — Convergence = high confidence
4. **No findings is valid** — Column can report clean status
5. **Domain-aware refinement adds value** — Drift detection enhances architecture review

