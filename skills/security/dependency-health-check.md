---
name: dependency-health-check
category: security
version: 1.0.0
maturity: validated
lifecycle: validated
estimated-cost: low
typical-runtime: 2-5min
complexity-level: simple
requires-deep-analysis: false
scope: core
tier: 1
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - security
  - dependencies
  - vulnerabilities
  - npm
  - audit
  - packages
prerequisites:
  - file: package.json
    reason: "Need dependency list to analyze"
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Dependency Health Check

## Purpose

Analyzes project dependencies for security vulnerabilities, outdated packages, license issues, and maintenance status. Provides actionable recommendations for dependency updates and security fixes.

## Scope and Classification

**Scope:** `core` - Universal skill that works on any project with dependencies

**Tier:** `1` - Existential risk (security vulnerabilities)

**Lifecycle Stage:** `validated` - Proven to work in production

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## Tags (for Intent Resolution)

Tags enable the skill-router to match user intents to skills:

- **security** - Core domain
- **dependencies** - What is being analyzed
- **vulnerabilities** - Primary concern
- **npm** - Common package manager
- **audit** - Action type
- **packages** - Alternate term for dependencies

## When to Invoke

### Explicit Trigger Phrases

- "Run dependency-health-check on this project"
- "Check for security vulnerabilities"
- "Analyze dependency health"
- "Find outdated packages"
- "Audit npm packages"
- "Check for CVEs in dependencies"

### Situational Triggers

- Before production deployments
- After adding new dependencies
- During security audits
- Regularly (weekly/monthly) for maintenance
- When security advisories are published

## Required Cursor Settings

- **Mode**: Composer or Chat
- **Model preference**: Claude Sonnet
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Check for known security vulnerabilities
- Identify outdated packages (major/minor/patch versions behind)
- Assess maintenance status (active/abandoned)
- Check license compatibility
- Prioritize critical security issues
- Consider update impact and breaking changes

### What It Must Avoid

- Don't suggest updates without considering breaking changes
- Don't ignore transitive dependencies
- Don't recommend updates that would break the build
- Don't focus on dev dependencies unless security-critical

### What It Must Prioritize

- Critical and high severity security vulnerabilities
- Outdated packages with security fixes available
- Abandoned or unmaintained packages
- License compatibility issues
- Update paths and migration guides

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Initial dependency audit
- Comprehensive security check
- Regular maintenance review

**Input:**
- package.json (or equivalent: requirements.txt, Gemfile, etc.)
- package-lock.json / yarn.lock (if available)
- All dependencies (direct and transitive)

**Process:**
1. Parse dependency files
2. Check for known vulnerabilities
3. Identify outdated packages
4. Assess maintenance status
5. Check license compatibility
6. Generate comprehensive report

**Invocation Example:**
> "Run dependency-health-check in full-scan mode on this project"

### Incremental Mode

**When to Use:**
- After adding new dependencies
- When specific packages updated
- Continuous monitoring

**Input:**
- Changed dependency files
- New packages added
- Updated package versions

**Process:**
1. Analyze new/changed dependencies
2. Check for vulnerabilities in new packages
3. Verify update safety
4. Report on changes

**Invocation Example:**
> "Run dependency-health-check in incremental mode on dependencies changed in the last commit"

### Targeted Mode

**When to Use:**
- Checking specific package
- Analyzing security advisory
- Focused update planning

**Input:**
- Specific package name(s)
- Package version range

**Process:**
1. Deep analysis of target package(s)
2. Check vulnerability database
3. Assess update options
4. Provide focused recommendations

**Invocation Example:**
> "Run dependency-health-check in targeted mode on express package"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Code Quality of Dependencies**
- **Instead:** Use code-quality-audit if you need to review dependency source code
- **Why:** This skill focuses on security, maintenance, and version health, not code quality.

**Anti-Pattern 2: Architecture Decisions**
- **Instead:** Use architecture-review for dependency architecture
- **Why:** This skill checks health, not whether dependencies are architecturally appropriate.

**Anti-Pattern 3: Running on Every Commit**
- **Instead:** Run weekly/monthly or on dependency changes
- **Why:** Dependencies don't change that frequently. Low cost but unnecessary for every commit.

### ⚠️ WARNING: Known Limitations

**Limitation:** May not have access to latest vulnerability databases
- **Mitigation:** Recommend using npm audit, Snyk, or Dependabot for real-time data
- **Confidence:** ~80% accuracy on known vulnerabilities, real-time tools are more accurate

**Limitation:** Cannot test if updates break the build
- **Mitigation:** Recommend testing updates in separate branch
- **Confidence:** Update recommendations are based on semantic versioning, actual testing needed

## Known Limitations

- May not have real-time vulnerability data (use npm audit/Snyk for latest)
- Cannot test if updates actually work (recommend testing)
- May miss transitive dependency issues without lock files
- License checking may not cover all edge cases
- Maintenance status assessment is based on recent activity, not guaranteed

## Fallback Strategy

If this skill fails, try:

1. **Use npm audit / yarn audit**: Built-in vulnerability checking
2. **Use Snyk or Dependabot**: Real-time security monitoring
3. **Check package.json manually**: Review dependencies manually
4. **Check package repositories**: Visit npm/pypi/etc. for package status

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Total dependencies analyzed
   - Package manager used
   - Analysis scope (direct/transitive)

2. **Findings**
   - Security vulnerabilities (Critical/High/Medium/Low)
   - Outdated packages (major/minor/patch)
   - Unmaintained packages
   - License issues
   - Each with package name, current version, recommended version

3. **Recommendations**
   - Security updates (prioritized by severity)
   - Version updates (with breaking change assessment)
   - Package replacements (for unmaintained packages)
   - Each with effort estimate and risk level

4. **Implementation Steps**
   - Ordered update steps
   - Testing requirements
   - Rollback plan
   - Migration notes for breaking changes

5. **Files to Modify/Create**
   - package.json updates
   - package-lock.json updates
   - .nvmrc or version files (if applicable)

6. **Dependencies**
   - Vulnerability databases referenced
   - Tools recommended (npm audit, Snyk, etc.)

### Filename Convention

Reports must follow: `YYYY-MM-DD_dependency-health-check_target-component.md`

Examples:
- `2024-01-05_dependency-health-check_full-project.md`
- `2024-01-05_dependency-health-check_backend-dependencies.md`

### Context Preservation Strategy

For projects with many dependencies:
1. Summary with Critical/High vulnerabilities in main report
2. Detailed list in separate file
3. Link to detailed analysis

## Exit Conditions

### Success

- Dependencies analyzed
- Vulnerabilities identified
- Recommendations provided
- Handoff report generated

### Failure

- Missing package.json (or equivalent) - fail with clear error
- Unreadable dependency files - document what was found
- No dependencies found - report as such

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Dependency check complete. Found [X] vulnerabilities, [Y] outdated packages. See report for details."
4. Indicate readiness for updates

## Context Received (for Chained Skills)

If this skill builds on others:

```markdown
## Context Received

This analysis builds on:
- project-structure-analyzer v1.0.0 (executed [date])
- Key findings: Project structure mapped, dependency locations identified
- Assumptions carried forward: Package manager is npm/yarn
```

## Examples

### Example 1: Security Vulnerability Check

**Scenario:** Checking for known vulnerabilities

**Expected Findings:**
- Critical: express@4.16.0 has CVE-2023-XXXXX
- High: lodash@4.17.15 has prototype pollution vulnerability
- Recommendations: Update to express@4.18.2, lodash@4.17.21

### Example 2: Outdated Packages Check

**Scenario:** Checking for outdated dependencies

**Expected Findings:**
- react@16.8.0 is 5 major versions behind (current: 18.x)
- axios@0.19.0 is outdated (current: 1.x)
- Recommendations: Update plan with breaking change notes

