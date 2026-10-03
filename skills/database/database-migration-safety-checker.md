---
name: database-migration-safety-checker
category: database
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 2-5min
complexity-level: moderate
requires-deep-analysis: true
prerequisites:
  - file: src/db/schema.ts
    reason: "Need Dexie schema to analyze migrations"
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Database Migration Safety Checker

## Purpose

Reviews Dexie schema migrations for backwards compatibility and data loss risks. Validates that schema changes won't corrupt user data or break existing functionality.

## When to Invoke

### Explicit Trigger Phrases

- "Run database-migration-safety-checker on [migration/schema]"
- "Check migration safety"
- "Validate schema changes"
- "Review database migration"

### Situational Triggers

- Before deploying schema changes
- When adding new fields to tables
- When modifying indexes
- After Dexie version upgrades
- When data loss risks are suspected

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Review Dexie version upgrades
- Validate that new fields have defaults
- Check for breaking index changes
- Identify potential data loss scenarios
- Verify backwards compatibility
- Check migration logic correctness

### What It Must Avoid

- Don't flag safe migrations as risky
- Don't ignore default value requirements
- Don't miss index migration issues
- Don't assume all migrations are safe

### What It Must Prioritize

- Data loss risks (Critical)
- Missing default values (High)
- Breaking index changes (High)
- Backwards compatibility issues (Medium)
- Migration logic errors (Medium)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive migration audit
- Before major schema changes
- Initial migration review

**Input:**
- All Dexie schema versions
- Migration logic
- Index definitions
- Field definitions

**Process:**
1. Review all schema versions
2. Check for data loss risks
3. Validate default values
4. Check index migrations
5. Verify backwards compatibility
6. Generate comprehensive safety report

**Invocation Example:**
> "Run database-migration-safety-checker in full-scan mode on all migrations"

### Incremental Mode

**When to Use:**
- After adding new migration
- When modifying schema
- During migration development

**Input:**
- New/changed migrations
- Updated schema definitions

**Process:**
1. Analyze new migrations for risks
2. Check if defaults are provided
3. Verify backwards compatibility
4. Report on safety status

**Invocation Example:**
> "Run database-migration-safety-checker in incremental mode on new migration"

### Targeted Mode

**When to Use:**
- Reviewing specific migration
- Validating single schema change
- Focused safety check

**Input:**
- Specific migration version
- Targeted schema change

**Process:**
1. Deep analysis of target migration
2. Check all safety aspects
3. Verify migration logic
4. Provide focused recommendations

**Invocation Example:**
> "Run database-migration-safety-checker in targeted mode on version 2 migration"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General Database Performance**
- **Instead:** Use performance-budget-guardian for performance concerns
- **Why:** This skill focuses on migration safety, not database performance.

**Anti-Pattern 2: Query Optimization**
- **Instead:** Use code-quality-audit for query optimization
- **Why:** This skill validates migration safety, not query efficiency.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot test actual migration execution
- **Mitigation:** Focus on static analysis. Recommend testing migrations on sample data.
- **Confidence:** ~90% accuracy on static analysis, actual testing needed for validation

## Known Limitations

- Cannot test actual migration execution (static analysis only)
- May miss runtime migration issues
- Requires understanding of Dexie migration system
- Cannot verify data in production

## Fallback Strategy

If this skill fails, try:

1. **Manual migration review**: Review Dexie migration docs and patterns
2. **Test migrations**: Run migrations on test data
3. **Targeted mode**: Focus on specific migrations
4. **Migration tools**: Use Dexie migration validation tools

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Migrations analyzed
   - Schema versions reviewed
   - Analysis scope

2. **Findings**
   - Data loss risks (Critical/High/Medium/Low)
   - Missing default values
   - Breaking index changes
   - Backwards compatibility issues
   - Each finding includes location, risk, and fix

3. **Recommendations**
   - Migration fixes (prioritized)
   - Default value additions
   - Index migration strategies
   - Test case additions

4. **Implementation Steps**
   - Ordered fixes
   - Migration updates
   - Test implementations

5. **Files to Modify/Create**
   - Migration files
   - Schema files
   - Test files

6. **Dependencies**
   - Dexie migration system referenced
   - Test framework (if adding tests)

### Filename Convention

Reports must follow: `YYYY-MM-DD_database-migration-safety-checker_target-component.md`

## Exit Conditions

### Success

- Migration safety validated
- Risks identified
- Recommendations provided
- Handoff report generated

### Failure

- No schema found - fail with clear error
- Unreadable code - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Migration safety check complete. Found [X] risks. See report for details."
4. Indicate readiness for fixes

