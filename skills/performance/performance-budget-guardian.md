---
name: performance-budget-guardian
category: performance
version: 1.0.0
maturity: draft
estimated-cost: medium
typical-runtime: 5-10min
complexity-level: moderate
requires-deep-analysis: true
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Performance Budget Guardian

## Purpose

Enforces TTI (Time to Interactive) <300ms budget and identifies performance regressions before they ship. Ensures Zero-Click Capture Invariant is maintained by keeping the app instantly ready.

## When to Invoke

### Explicit Trigger Phrases

- "Run performance-budget-guardian on [component/app]"
- "Check TTI budget compliance"
- "Analyze performance regressions"
- "Validate performance budget"

### Situational Triggers

- Before production deployments
- After adding new dependencies
- When bundle size increases
- After major feature additions
- When TTI regressions are suspected
- During performance optimization work

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Measure actual TTI (page load → cursor blinking in textarea)
- Analyze bundle size and composition
- Identify heavy dependencies and their impact
- Check for blocking operations in critical path
- Propose lazy-loading strategies for non-critical features
- Consider tradeoffs between features and performance

### What It Must Avoid

- Don't suggest removing necessary features (suggest optimization instead)
- Don't ignore user experience (performance vs. functionality balance)
- Don't focus only on bundle size (also check runtime performance)
- Don't miss indirect performance impacts (dependencies of dependencies)

### What It Must Prioritize

- TTI violations (Critical - breaks Zero-Click Capture)
- Bundle size violations (High - impacts TTI)
- Critical path blockers (High - delays interactivity)
- Heavy dependencies (Medium - optimization opportunities)
- Lazy-loading opportunities (Medium - easy wins)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive performance audit
- Before major release
- Initial performance assessment

**Input:**
- Entire application
- Bundle analysis
- Build configuration
- Dependencies list
- Runtime performance metrics (if available)

**Process:**
1. Analyze bundle size and composition
2. Identify heavy dependencies
3. Check critical path for blockers
4. Measure TTI (if possible) or estimate
5. Identify optimization opportunities
6. Generate comprehensive performance report

**Invocation Example:**
> "Run performance-budget-guardian in full-scan mode on the entire application"

### Incremental Mode

**When to Use:**
- After adding dependencies
- When bundle size increases
- After feature additions

**Input:**
- Changed files
- New dependencies
- Updated build config
- Bundle diff (if available)

**Process:**
1. Analyze impact of changes on bundle size
2. Check if TTI budget still met
3. Identify new performance issues
4. Report on regression status

**Invocation Example:**
> "Run performance-budget-guardian in incremental mode on dependencies changed in the last commit"

### Targeted Mode

**When to Use:**
- Analyzing specific component
- Reviewing single dependency
- Focused optimization

**Input:**
- Specific component or dependency
- Targeted bundle analysis

**Process:**
1. Deep analysis of target performance impact
2. Calculate TTI contribution
3. Identify optimization strategies
4. Provide focused recommendations

**Invocation Example:**
> "Run performance-budget-guardian in targeted mode on Transformers.js dependency"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Code Quality Issues**
- **Instead:** Use code-quality-audit for code-level problems
- **Why:** This skill focuses on performance metrics, not code quality.

**Anti-Pattern 2: Architecture Review**
- **Instead:** Use architecture-review for structural analysis
- **Why:** This skill validates performance budgets, not architectural patterns.

**Anti-Pattern 3: Running on Every Small Change**
- **Instead:** Use incremental mode on dependency or build config changes
- **Why:** Medium cost. Performance doesn't change with every code edit.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot measure actual TTI without runtime environment
- **Mitigation:** Estimate based on bundle size and critical path analysis. Recommend Lighthouse CI for actual measurements.
- **Confidence:** ~80% accuracy on estimates, actual measurement needed for validation

**Limitation:** May miss runtime performance issues
- **Mitigation:** Focus on bundle size and critical path. Recommend runtime profiling for full analysis.
- **Confidence:** ~85% accuracy on bundle analysis, runtime profiling needed for complete picture

## Known Limitations

- Cannot measure actual TTI without running application
- May miss runtime performance issues (only static analysis)
- Bundle size analysis may not reflect actual load time
- Cannot test actual user experience (only code analysis)

## Fallback Strategy

If this skill fails, try:

1. **Lighthouse CI**: Use automated Lighthouse runs for actual TTI measurement
2. **Bundle analyzer**: Use webpack-bundle-analyzer or similar tools
3. **Targeted mode**: Focus on specific dependencies instead of full scan
4. **Manual profiling**: Use browser DevTools for runtime performance

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Application analyzed
   - Performance budgets (TTI <300ms, Bundle <500KB)
   - Analysis scope

2. **Findings**
   - TTI violations (Critical/High/Medium/Low)
   - Bundle size violations
   - Critical path blockers
   - Heavy dependencies
   - Each finding includes:
     - Current value vs. budget
     - Impact on TTI
     - Optimization opportunity

3. **Recommendations**
   - Performance optimizations (prioritized)
   - Lazy-loading strategies
   - Code-splitting opportunities
   - Dependency optimizations
   - Each with effort estimate and TTI impact

4. **Implementation Steps**
   - Ordered optimizations
   - Build config changes
   - Code-splitting implementation
   - Lazy-loading setup

5. **Files to Modify/Create**
   - Build configuration files
   - Component files for lazy-loading
   - Route files for code-splitting
   - CI configuration for Lighthouse

6. **Dependencies**
   - Build tools referenced
   - Performance monitoring tools recommended

### Filename Convention

Reports must follow: `YYYY-MM-DD_performance-budget-guardian_target-component.md`

### Example Output Structure

```yaml
Performance Analysis:
  Current TTI: 420ms (BUDGET EXCEEDED - Target: <300ms)
  Bundle Size: 680KB (BUDGET EXCEEDED - Target: <500KB)
  
  Critical Path Blockers:
    - Transformers.js model load (150ms)
      Location: src/services/embeddings.ts:23
      Impact: Blocks RAC feature initialization
      Fix: Lazy-load only when RAC feature enabled
    
    - Dexie.open() synchronous call (80ms)
      Location: src/services/database.ts:12
      Impact: Blocks app initialization
      Fix: Show capture surface before DB ready, hydrate async
    
    - Draft restoration blocks render (40ms)
      Location: src/components/capture/DraftRestore.tsx:15
      Impact: Delays first paint
      Fix: Restore draft after first paint

  Bundle Size Contributors:
    - Recharts: 180KB (insights dashboard)
      Location: src/components/insights/Chart.tsx
      Fix: Code-split, load only on Insights tab
    
    - Lucide Icons: 120KB (importing entire library)
      Location: Multiple components
      Fix: Import specific icons only

Recommendations:
  1. Implement lazy loading for RAC embeddings
  2. Code-split Insights dashboard components
  3. Add Lighthouse CI with TTI budget enforcement
  4. Tree-shake unused Lucide icons

Files to Modify:
  - vite.config.ts (code splitting)
  - src/services/embeddings.ts (lazy load)
  - .github/workflows/ci.yml (Lighthouse CI)
```

### Context Preservation Strategy

For large applications:
1. Summary with Critical/High violations in main report
2. Detailed bundle analysis in separate file
3. Link to detailed analysis from main report

## Exit Conditions

### Success

- Performance budget compliance validated
- Violations identified and prioritized
- Optimization recommendations provided
- Handoff report generated per protocol

### Failure

- No build config found - fail with clear error
- Unreadable code - document what was found
- Timeout - suggest targeted mode

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Performance audit complete. TTI: [X]ms (budget: <300ms), Bundle: [Y]KB (budget: <500KB). Found [Z] violations. See report for details."
4. Indicate readiness for optimization

## Context Received (for Chained Skills)

If building on other skills:

```markdown
## Context Received

This analysis builds on:
- project-structure-analyzer v1.0.0 (executed 2024-01-05)
- Key findings: Application structure mapped, dependencies identified
- Assumptions carried forward: Build configuration is accessible
```

## Examples

### Example 1: Bundle Size Violation

**Scenario:** Analyzing bundle size after adding new dependencies

**Expected Findings:**
- Bundle size: 680KB (exceeds 500KB budget)
- Heavy dependency: Recharts (180KB)
- Recommendation: Code-split Insights dashboard

### Example 2: TTI Violation

**Scenario:** Analyzing TTI after adding Transformers.js

**Expected Findings:**
- TTI: 420ms (exceeds 300ms budget)
- Blocker: Transformers.js model load (150ms)
- Recommendation: Lazy-load RAC embeddings

