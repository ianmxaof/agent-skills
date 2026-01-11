---
name: privacy-tier-auditor
category: security
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 3-7min
complexity-level: moderate
requires-deep-analysis: true
scope: project
tier: 1
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
domain: prompt-library
tags:
  - privacy
  - security
  - vault
  - data-access
  - audit
  - compliance
prerequisites:
  - file: src/services/*.ts
    reason: "Need to scan service files for privacy checks"
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Privacy Tier Auditor

## Purpose

Ensures Privacy Absolutism is enforced at every data access point. Validates that vault-tier prompts are excluded from recall, analytics, RAC phrase extraction, insights, completions, and all other data access operations.

## Scope and Classification

**Scope:** `project` - Prompt Library-specific skill

**Tier:** `1` - Existential risk (privacy enforcement)

**Domain:** `prompt-library` - Encodes Prompt Library-specific privacy tier system

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## When to Invoke

### Explicit Trigger Phrases

- "Run privacy-tier-auditor on [service/component]"
- "Check privacy tier enforcement"
- "Audit vault-tier exclusions"
- "Validate privacy compliance"

### Situational Triggers

- Before adding new data access features
- After modifying database queries
- During security audits
- When adding analytics or insights
- Before production deployments

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Scan all database queries for privacy tier filtering
- Identify missing `tool.privacyTier !== 'vault'` checks
- Validate vault-tier exclusion in all systems (recall, analytics, RAC, insights, completions, exports)
- Check for metadata leaks in logs and exports
- Look for indirect access patterns (filtering, aggregation, etc.)
- Consider edge cases (empty results, null checks, etc.)

### What It Must Avoid

- Don't flag legitimate vault-tier access (if explicitly allowed)
- Don't ignore indirect access patterns (aggregations, counts, etc.)
- Don't miss metadata leaks (even metadata can be sensitive)
- Don't assume all queries are safe (verify each one)

### What It Must Prioritize

- Critical: Missing privacy checks in data access
- High: Vault-tier included in analytics/insights
- High: Vault-tier metadata in exports/logs
- Medium: Indirect access patterns
- Low: Development-only code (still should be flagged)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive privacy audit
- Before major release
- Initial security assessment

**Input:**
- All service files
- Database query patterns
- Analytics and insights code
- Export functionality
- Logging code

**Process:**
1. Scan all database queries
2. Check for privacy tier filtering
3. Validate vault-tier exclusion in all systems
4. Check for metadata leaks
5. Identify missing privacy checks
6. Generate comprehensive audit report

**Invocation Example:**
> "Run privacy-tier-auditor in full-scan mode on all services"

### Incremental Mode

**When to Use:**
- After adding new data access code
- When modifying database queries
- During feature development

**Input:**
- Changed service files
- New database queries
- Modified analytics code

**Process:**
1. Analyze changed code for privacy checks
2. Verify new queries filter vault-tier
3. Check for privacy violations in changes
4. Report on compliance status

**Invocation Example:**
> "Run privacy-tier-auditor in incremental mode on files changed in the last commit"

### Targeted Mode

**When to Use:**
- Reviewing specific service
- Validating single data access point
- Focused security check

**Input:**
- Specific service file
- Targeted database query
- Single feature

**Process:**
1. Deep analysis of target for privacy checks
2. Verify all access points filter vault-tier
3. Check for edge cases
4. Provide focused recommendations

**Invocation Example:**
> "Run privacy-tier-auditor in targeted mode on src/services/rac-extraction.ts"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General Security Issues**
- **Instead:** Use dependency-health-check or other security tools for non-privacy issues
- **Why:** This skill focuses specifically on privacy tier enforcement, not general security.

**Anti-Pattern 2: Code Quality Issues**
- **Instead:** Use code-quality-audit for code-level problems
- **Why:** This skill validates privacy compliance, not code quality.

**Anti-Pattern 3: Running on UI Components Only**
- **Instead:** Focus on service layer and data access code
- **Why:** Privacy tier enforcement happens at the data access layer, not UI.

### ⚠️ WARNING: Known Limitations

**Limitation:** Cannot detect runtime privacy violations
- **Mitigation:** Focus on static code analysis. Recommend runtime tests for validation.
- **Confidence:** ~90% accuracy on static analysis, runtime testing needed for full validation

**Limitation:** May miss complex indirect access patterns
- **Mitigation:** Review aggregation and filtering logic carefully
- **Confidence:** ~85% accuracy on indirect patterns

## Known Limitations

- Cannot test actual runtime behavior (static analysis only)
- May miss complex query patterns
- Requires understanding of privacy tier system
- Cannot verify data in production (only code analysis)

## Fallback Strategy

If this skill fails, try:

1. **Manual code review**: Search for `privacyTier` and `vault` in codebase
2. **Runtime tests**: Write tests that verify vault-tier exclusion
3. **Targeted mode**: Focus on specific services instead of full scan
4. **Security audit**: Use general security tools for broader analysis

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Services/files analyzed
   - Privacy tier system overview
   - Analysis scope

2. **Findings**
   - Missing privacy checks (Critical/High/Medium/Low)
   - Each finding includes:
     - Location (file:line)
     - Risk description
     - Data access type (recall, analytics, RAC, etc.)
     - Fix recommendation
   - Vault-tier inclusion in analytics
   - Metadata leaks in exports/logs
   - Indirect access patterns

3. **Recommendations**
   - Privacy check additions (prioritized)
   - Query modifications
   - Filter implementations
   - Test case additions
   - Each with effort estimate and risk level

4. **Implementation Steps**
   - Ordered fixes
   - Privacy check additions
   - Query modifications
   - Test implementations

5. **Files to Modify/Create**
   - Service files needing privacy checks
   - Test files for privacy enforcement
   - Query modification locations

6. **Dependencies**
   - Privacy tier system referenced
   - Test framework (if adding tests)

### Filename Convention

Reports must follow: `YYYY-MM-DD_privacy-tier-auditor_target-component.md`

### Example Output Structure

```yaml
Critical Findings:
  - Missing Privacy Check: src/services/rac-extraction.ts:45
    Risk: Vault-tier prompts extracted into RAC phrase memory
    Data Access: RAC phrase extraction
    Fix: Add vault-tier filter before extraction loop
  
  - Missing Privacy Check: src/services/insights.ts:120
    Risk: Vault-tier prompts counted in usage timeline
    Data Access: Analytics/insights
    Fix: Filter by privacyTier before aggregation

Low-Priority Findings:
  - Console.log in development exposes prompt text
    Risk: Vault-tier text visible in dev tools
    Location: src/services/recall.ts:67
    Fix: Redact or disable logs for vault-tier

Test Cases to Add:
  - RAC phrase extraction excludes vault-tier prompts
  - Analytics exclude vault-tier from all metrics
  - Exports never include vault-tier metadata

Files to Modify:
  - src/services/rac-extraction.ts
  - src/services/insights.ts
  - tests/privacy-tier-enforcement.test.ts
```

### Context Preservation Strategy

For large codebases:
1. Summary with Critical/High violations in main report
2. Detailed analysis in separate file
3. Link to detailed analysis from main report

## Exit Conditions

### Success

- Privacy tier enforcement validated
- Missing checks identified
- Recommendations provided
- Handoff report generated per protocol

### Failure

- No service files found - fail with clear error
- Unreadable code - document what was found
- Timeout - suggest targeted mode

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Privacy tier audit complete. Found [X] missing checks, [Y] violations. See report for details."
4. Indicate readiness for implementation

## Context Received (for Chained Skills)

If building on other skills:

```markdown
## Context Received

This analysis builds on:
- project-structure-analyzer v1.0.0 (executed 2024-01-05)
- Key findings: Service layer structure mapped, database access patterns identified
- Assumptions carried forward: Privacy tier system is correctly implemented
```

## Examples

### Example 1: Missing Privacy Check in RAC

**Scenario:** Auditing RAC phrase extraction service

**Expected Findings:**
- Missing privacy check before phrase extraction
- Risk: Vault-tier prompts could be extracted
- Fix: Add `tool.privacyTier !== 'vault'` filter

### Example 2: Analytics Privacy Violation

**Scenario:** Auditing insights/analytics service

**Expected Findings:**
- Vault-tier prompts included in usage metrics
- Risk: Privacy violation in analytics
- Fix: Filter by privacy tier before aggregation

