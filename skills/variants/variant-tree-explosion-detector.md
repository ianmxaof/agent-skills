---
name: variant-tree-explosion-detector
category: variants
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 3-7min
complexity-level: moderate
requires-deep-analysis: true
prerequisites:
  - file: src/db/schema.ts
    reason: "Need database schema to query variant counts"
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Variant Tree Explosion Detector

## Purpose

Identifies prompts with pathological variant counts (>100) and suggests compression. Detects micro-variants (semantic distance <0.1) and proposes bulk hide operations.

## When to Invoke

### Explicit Trigger Phrases

- "Run variant-tree-explosion-detector on [database/prompts]"
- "Check for variant explosion"
- "Detect micro-variants"
- "Find compression opportunities"

### Situational Triggers

- When variant counts seem high
- Before database cleanup
- When hoarding patterns suspected
- During variant management work
- When performance issues related to variants

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Scan database for high variant counts
- Identify micro-variants (semantic distance <0.1)
- Calculate compression opportunities
- Propose bulk hide operations
- Generate UI prompts for user action
- Consider user workflow impact

### What It Must Avoid

- Don't suggest removing legitimate variants
- Don't ignore user intent (some variants may be intentional)
- Don't miss semantic similarity patterns
- Don't assume all high counts are problems

### What It Must Prioritize

- Pathological variant counts (Critical - >100 variants)
- Micro-variants (High - semantic distance <0.1)
- Compression opportunities (Medium - easy wins)
- User action prompts (Medium - surface affordances)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive variant audit
- Database cleanup planning
- Initial variant analysis

**Input:**
- Database variant data
- Semantic similarity calculations
- Variant relationships

**Process:**
1. Scan all prompts for variant counts
2. Identify high-count prompts
3. Calculate semantic distances
4. Find micro-variants
5. Calculate compression opportunities
6. Generate comprehensive explosion report

**Invocation Example:**
> "Run variant-tree-explosion-detector in full-scan mode on all prompts"

### Incremental Mode

**When to Use:**
- After adding variants
- When variant counts increase
- During variant management

**Input:**
- New/changed variants
- Updated variant counts

**Process:**
1. Analyze new variants for explosion risk
2. Check if counts exceed thresholds
3. Identify new micro-variants
4. Report on explosion status

**Invocation Example:**
> "Run variant-tree-explosion-detector in incremental mode on new variants"

### Targeted Mode

**When to Use:**
- Analyzing specific prompt
- Reviewing single variant tree
- Focused explosion check

**Input:**
- Specific prompt ID
- Targeted variant tree

**Process:**
1. Deep analysis of target variant tree
2. Calculate compression opportunities
3. Identify micro-variants
4. Provide focused recommendations

**Invocation Example:**
> "Run variant-tree-explosion-detector in targeted mode on prompt ID 123"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General Database Issues**
- **Instead:** Use database-migration-safety-checker for migration concerns
- **Why:** This skill focuses specifically on variant explosion, not general database issues.

**Anti-Pattern 2: Performance Issues**
- **Instead:** Use performance-budget-guardian for performance concerns
- **Why:** This skill detects variant patterns, not performance problems.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot access actual database at runtime
- **Mitigation:** Focus on code analysis and patterns. Recommend database queries for actual counts.
- **Confidence:** ~85% accuracy on pattern detection, database queries needed for validation

## Known Limitations

- Cannot access actual database (static analysis only)
- Requires semantic similarity calculations
- May miss context-dependent variant relationships
- Cannot verify compression impact

## Fallback Strategy

If this skill fails, try:

1. **Database queries**: Query database directly for variant counts
2. **Manual review**: Review variant trees manually
3. **Targeted mode**: Focus on specific prompts
4. **Compression tools**: Use variant compression utilities

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Prompts analyzed
   - Variant counts found
   - Analysis scope

2. **Findings**
   - Pathological variant counts (Critical/High/Medium/Low)
   - Micro-variants identified
   - Compression opportunities
   - Each finding includes prompt ID, count, and recommendations

3. **Recommendations**
   - Compression strategies (prioritized)
   - Bulk hide operations
   - UI prompts for user action
   - Variant management improvements

4. **Implementation Steps**
   - Ordered compression operations
   - Bulk hide implementations
   - UI prompt additions

5. **Files to Modify/Create**
   - Variant management files
   - UI components for compression
   - Compression utility files

6. **Dependencies**
   - Database schema referenced
   - Semantic similarity system

### Filename Convention

Reports must follow: `YYYY-MM-DD_variant-tree-explosion-detector_target-component.md`

## Exit Conditions

### Success

- Variant explosion detected
- Compression opportunities identified
- Recommendations provided
- Handoff report generated

### Failure

- No database schema found - fail with clear error
- Unreadable code - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Variant explosion detection complete. Found [X] prompts with >100 variants, [Y] micro-variants. See report for compression opportunities."
4. Indicate readiness for compression

