---
name: api-boundary-validator
category: api
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 2-5min
complexity-level: moderate
requires-deep-analysis: true
scope: core
tier: 3
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - api
  - boundaries
  - security
  - local-first
  - external-calls
  - validation
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# API Boundary Validator

## Purpose

Ensures no unintended external API calls (preserves local-first principle). Validates that all API calls are documented, justified, and gated behind user opt-in where required.

## Scope and Classification

**Scope:** `core` - Universal skill that works on any project

**Tier:** `3` - Long-term quality (API boundary validation)

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## When to Invoke

### Explicit Trigger Phrases

- "Run api-boundary-validator on [codebase/service]"
- "Check for external API calls"
- "Validate API boundaries"
- "Audit external dependencies"

### Situational Triggers

- Before production deployments
- After adding new features
- When local-first principle is violated
- During security audits
- When telemetry concerns arise

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Scan codebase for `fetch()`, `axios`, `XMLHttpRequest`
- Validate all API calls are documented and justified
- Check for telemetry/analytics that leak user data
- Ensure RAC LLM calls are gated behind user opt-in
- Propose removal or gating strategies
- Consider local-first alternatives

### What It Must Avoid

- Don't flag legitimate documented API calls
- Don't ignore opt-in gating requirements
- Don't miss indirect API calls (through libraries)
- Don't assume all API calls are violations

### What It Must Prioritize

- Unauthorized API calls (Critical - breaks local-first)
- Missing opt-in gates (High - violates privacy)
- Data leaks in telemetry (High - privacy violation)
- Undocumented API calls (Medium - code quality)
- Local-first alternatives (Medium - improvements)

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Comprehensive API audit
- Before major release
- Initial local-first validation

**Input:**
- All source code
- API call patterns
- Telemetry code
- Opt-in gating logic

**Process:**
1. Scan for all API calls
2. Validate documentation
3. Check opt-in gating
4. Identify data leaks
5. Find local-first alternatives
6. Generate comprehensive API report

**Invocation Example:**
> "Run api-boundary-validator in full-scan mode on entire codebase"

### Incremental Mode

**When to Use:**
- After adding new features
- When modifying API calls
- During feature development

**Input:**
- Changed files
- New API calls
- Modified telemetry

**Process:**
1. Analyze new API calls
2. Verify documentation and gating
3. Check for data leaks
4. Report on boundary status

**Invocation Example:**
> "Run api-boundary-validator in incremental mode on files changed in the last commit"

### Targeted Mode

**When to Use:**
- Reviewing specific service
- Validating single API call
- Focused boundary check

**Input:**
- Specific service file
- Targeted API call

**Process:**
1. Deep analysis of target API call
2. Verify documentation and gating
3. Check for data leaks
4. Provide focused recommendations

**Invocation Example:**
> "Run api-boundary-validator in targeted mode on RAC LLM service"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: General Security Issues**
- **Instead:** Use dependency-health-check for dependency security
- **Why:** This skill focuses specifically on API boundaries, not general security.

**Anti-Pattern 2: Performance Issues**
- **Instead:** Use performance-budget-guardian for performance concerns
- **Why:** This skill validates API boundaries, not performance.

### ⚠️ WARNING: Known Limitations

**Limitation:** May miss API calls through third-party libraries
- **Mitigation:** Review library documentation and source. Recommend runtime monitoring.
- **Confidence:** ~90% accuracy on direct calls, ~70% on library calls

## Known Limitations

- May miss API calls through libraries
- Cannot test actual runtime behavior
- Requires understanding of local-first principle
- Cannot verify API calls in production

## Fallback Strategy

If this skill fails, try:

1. **Manual code review**: Search for API call patterns manually
2. **Runtime monitoring**: Monitor network requests at runtime
3. **Targeted mode**: Focus on specific services
4. **Network tools**: Use browser DevTools to monitor API calls

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - API calls found
   - Local-first principle referenced
   - Analysis scope

2. **Findings**
   - Unauthorized API calls (Critical/High/Medium/Low)
   - Missing opt-in gates
   - Data leaks in telemetry
   - Undocumented API calls
   - Each finding includes location, risk, and fix

3. **Recommendations**
   - API call removals (prioritized)
   - Opt-in gate additions
   - Local-first alternatives
   - Documentation additions
   - Each with effort estimate

4. **Implementation Steps**
   - Ordered fixes
   - Opt-in gate implementations
   - API call removals/modifications

5. **Files to Modify/Create**
   - API call files
   - Opt-in gate files
   - Documentation files

6. **Dependencies**
   - Local-first principle referenced
   - API documentation standards

### Filename Convention

Reports must follow: `YYYY-MM-DD_api-boundary-validator_target-component.md`

## Exit Conditions

### Success

- API boundaries validated
- Violations identified
- Recommendations provided
- Handoff report generated

### Failure

- No code found - fail with clear error
- Unreadable code - document what was found

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "API boundary validation complete. Found [X] unauthorized calls, [Y] missing opt-in gates. See report for details."
4. Indicate readiness for fixes

