---
name: bundle-size-analyzer
category: performance
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 3-7min
complexity-level: moderate
requires-deep-analysis: true
scope: core
tier: 3
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - performance
  - bundle
  - dependencies
  - optimization
  - tree-shaking
  - code-splitting
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Bundle Size Analyzer

## Purpose

Identifies heavy dependencies and proposes tree-shaking/code-splitting opportunities. Analyzes bundle composition and calculates TTI impact per dependency.

## Scope and Classification

**Scope:** `core` - Universal skill that works on any project

**Tier:** `3` - Long-term quality (bundle size optimization)

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## When to Invoke

### Explicit Trigger Phrases

- "Run bundle-size-analyzer on [bundle/app]"
- "Analyze bundle size"
- "Find heavy dependencies"
- "Check bundle composition"

### Situational Triggers

- Before production deployments
- After adding new dependencies
- When bundle size increases
- During performance optimization
- When TTI regressions occur

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Analyze bundle composition
- Identify largest dependencies
- Check for unused imports
- Propose lazy-loading strategies
- Calculate TTI impact per dependency
- Consider tree-shaking opportunities

### What It Must Avoid

- Don't suggest removing necessary dependencies
- Don't ignore indirect dependencies
- Don't miss code-splitting opportunities
- Don't assume all large dependencies are problems

### What It Must Prioritize

- Bundle size violations (Critical - >500KB)
- Heavy dependencies (High - >100KB)
- Unused imports (Medium - easy wins)
- Lazy-loading opportunities (Medium - optimization)
- Tree-shaking gaps (Medium - optimization)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive bundle audit
- Before major release
- Initial bundle analysis

**Input:**
- Bundle analysis output
- Dependencies list
- Build configuration
- Import statements

**Process:**
1. Analyze bundle composition
2. Identify largest dependencies
3. Check for unused imports
4. Find lazy-loading opportunities
5. Calculate TTI impact
6. Generate comprehensive bundle report

**Invocation Example:**
> "Run bundle-size-analyzer in full-scan mode on entire bundle"

### Incremental Mode

**When to Use:**
- After adding dependencies
- When bundle size increases
- During optimization work

**Input:**
- New dependencies
- Bundle diff
- Changed imports

**Process:**
1. Analyze impact of changes
2. Check if bundle size budget met
3. Identify new heavy dependencies
4. Report on bundle status

**Invocation Example:**
> "Run bundle-size-analyzer in incremental mode on new dependencies"

### Targeted Mode

**When to Use:**
- Analyzing specific dependency
- Reviewing single import
- Focused bundle check

**Input:**
- Specific dependency
- Targeted import

**Process:**
1. Deep analysis of target dependency
2. Calculate size contribution
3. Identify optimization opportunities
4. Provide focused recommendations

**Invocation Example:**
> "Run bundle-size-analyzer in targeted mode on Transformers.js dependency"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General Performance Issues**
- **Instead:** Use performance-budget-guardian for broader performance concerns
- **Why:** This skill focuses specifically on bundle size, not general performance.

**Anti-Pattern 2: Runtime Performance**
- **Instead:** Use performance-budget-guardian for runtime performance
- **Why:** This skill analyzes bundle composition, not runtime behavior.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot measure actual bundle size without build
- **Mitigation:** Estimate based on dependency sizes. Recommend actual build analysis for validation.
- **Confidence:** ~85% accuracy on estimates, actual build needed for validation

## Known Limitations

- Cannot measure actual bundle size (static analysis only)
- May miss dynamic imports
- Requires build output or analysis tools
- Cannot verify actual load time

## Fallback Strategy

If this skill fails, try:

1. **Bundle analyzer tools**: Use webpack-bundle-analyzer or similar
2. **Build analysis**: Run build and analyze output
3. **Targeted mode**: Focus on specific dependencies
4. **Performance tools**: Use Lighthouse for actual load time

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Bundle analyzed
   - Dependencies found
   - Analysis scope

2. **Findings**
   - Bundle size violations (Critical/High/Medium/Low)
   - Heavy dependencies
   - Unused imports
   - Lazy-loading opportunities
   - Each finding includes size, impact, and recommendations

3. **Recommendations**
   - Dependency optimizations (prioritized)
   - Lazy-loading strategies
   - Tree-shaking improvements
   - Code-splitting opportunities
   - Each with effort estimate and TTI impact

4. **Implementation Steps**
   - Ordered optimizations
   - Import modifications
   - Lazy-loading implementations

5. **Files to Modify/Create**
   - Import files
   - Build configuration
   - Lazy-loading components

6. **Dependencies**
   - Build tools referenced
   - Bundle analysis tools recommended

### Filename Convention

Reports must follow: `YYYY-MM-DD_bundle-size-analyzer_target-component.md`

## Exit Conditions

### Success

- Bundle size analyzed
- Heavy dependencies identified
- Optimization opportunities found
- Handoff report generated

### Failure

- No build output found - fail with clear error
- Unreadable code - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Bundle analysis complete. Bundle size: [X]KB (budget: <500KB). Found [Y] heavy dependencies. See report for optimization opportunities."
4. Indicate readiness for optimization

