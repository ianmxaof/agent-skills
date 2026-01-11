---
name: documentation-drift-detector
category: analysis
version: 1.0.0
maturity: draft
lifecycle: experimental
estimated-cost: medium
typical-runtime: 3-7min
complexity-level: moderate
requires-deep-analysis: true
scope: core
tier: 3
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
tags:
  - documentation
  - drift
  - consistency
  - semantic
  - cross-surface
  - analysis
  - validation
prerequisites: []
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Documentation Drift Detector

## Purpose

Identify when documentation has diverged from the reality it describes. This skill detects the insidious failure mode where the README says one thing but the actual code, prompts, or schemas do another.

**Core insight:** In a prompt library or developer tooling project, the most dangerous bugs aren't crashes—they're semantic drift where documentation promises behaviors that no longer exist.

## Scope and Classification

**Scope:** `core`

This is a universal skill that works on any project with documentation.

**Tier:** `3` (Long-term Quality)

Documentation drift doesn't cause immediate failures but erodes trust and causes confusion over time.

**Lifecycle Stage:** `experimental`

New skill that needs real-world validation.

## When to Invoke

### Explicit Trigger Phrases

- "Check for documentation drift"
- "Are the docs up to date?"
- "Validate documentation against code"
- "Find outdated documentation"
- "Check README accuracy"

### Situational Triggers

- After significant code changes
- Before releases (ensure docs match release)
- During documentation audits
- When users report confusion
- Periodically (weekly/monthly) as hygiene

### Do NOT Invoke When

- Documentation doesn't exist yet (use documentation-generator)
- Code is intentionally undocumented
- During active development (wait for stabilization)

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet (good at comparison)
- **Multi-Model**: Off

## Behavioral Rules

### How the Model Should Reason

1. **Identify documentation files** - README, docs/, inline comments
2. **Extract claims** - What does documentation say exists/works?
3. **Verify against reality** - Does the claimed thing actually exist?
4. **Classify drift** - Structural, behavioral, or temporal?
5. **Assess severity** - How misleading is the drift?
6. **Generate fixes** - Specific corrections needed

### What It Must Avoid

- Flagging intentional differences (e.g., planned features)
- Treating examples as claims
- Ignoring context (some drift is acceptable)
- Generating vague findings ("docs are outdated")

### What It Must Prioritize

- High-impact drift (user-facing claims that are wrong)
- Structural drift (files/paths that don't exist)
- API contract drift (documented behavior ≠ actual behavior)
- Specific, actionable findings

## Drift Types

### Structural Drift

**Definition:** Documentation references files, directories, or structures that don't exist (or exist elsewhere).

**Detection:**
- Path references in docs → verify path exists
- Directory structure claims → verify against actual
- File mentions → verify file exists at claimed location

**Examples:**
```yaml
structural_drift:
  - claim: "See skills/core/dependency-health-check.md"
    reality: "File exists at skills/security/dependency-health-check.md"
    severity: medium
    fix: "Update path in documentation"
    
  - claim: "The templates/ directory contains..."
    reality: "templates/ has different contents than documented"
    severity: medium
    fix: "Update directory listing in docs"
```

### Behavioral Drift

**Definition:** Documentation describes behavior that doesn't match actual implementation.

**Detection:**
- Output format claims → verify against actual output
- "When to use" claims → verify triggers still apply
- API contracts → verify inputs/outputs match

**Examples:**
```yaml
behavioral_drift:
  - claim: "Outputs column_router_assessment"
    reality: "Actually outputs column_plan"
    severity: high
    fix: "Update output contract documentation"
    
  - claim: "Requires package.json"
    reality: "Also works with requirements.txt"
    severity: low
    fix: "Update prerequisites section"
```

### Temporal Drift

**Definition:** Documentation is stale relative to recent code changes.

**Detection:**
- Doc modification time >> code modification time
- Version numbers in docs ≠ actual versions
- Changelog not updated

**Examples:**
```yaml
temporal_drift:
  - claim: "Version 1.0.0"
    reality: "Package.json shows 1.2.0"
    severity: medium
    fix: "Update version references"
    
  - indicator: "README last modified 90 days ago"
    reality: "Code modified 15 times since"
    severity: medium
    fix: "Review README for accuracy"
```

### Semantic Drift

**Definition:** Documentation uses terminology or concepts that no longer apply.

**Detection:**
- Deprecated terms still in docs
- Renamed concepts not updated
- Removed features still documented

**Examples:**
```yaml
semantic_drift:
  - claim: "Uses the validation-layer skill"
    reality: "Skill renamed to refinement-layer"
    severity: high
    fix: "Update all references to new name"
```

## Assessment Process

### Step 1: Identify Documentation Surfaces

```yaml
documentation_surfaces:
  primary:
    - README.md
    - docs/**/*.md
    
  secondary:
    - "**/README.md"  # Nested READMEs
    - CHANGELOG.md
    - CONTRIBUTING.md
    
  inline:
    - Code comments (if configured)
    - Docstrings (if configured)
```

### Step 2: Extract Claims

For each documentation file, extract verifiable claims:

```yaml
claim_types:
  - file_references:
      pattern: "See `path/to/file`" or "[link](path/to/file)"
      verify: "File exists at path"
      
  - directory_structures:
      pattern: "```\ndir/\n  file1\n  file2\n```"
      verify: "Directory matches structure"
      
  - output_contracts:
      pattern: "Output: { field: type }"
      verify: "Actual output matches contract"
      
  - prerequisites:
      pattern: "Requires: file.json"
      verify: "Prerequisite exists and is used"
      
  - version_numbers:
      pattern: "version: X.Y.Z"
      verify: "Matches actual version"
```

### Step 3: Verify Claims Against Reality

For each claim:
1. Attempt to verify against actual codebase
2. If verification fails, record drift
3. Classify drift type
4. Assess severity

### Step 4: Calculate Drift Score

```yaml
drift_score_formula:
  base: 0.0  # Perfect sync
  
  additions:
    - structural_drift: +0.15 per instance
    - behavioral_drift: +0.20 per instance
    - temporal_drift: +0.10 per instance
    - semantic_drift: +0.15 per instance
    
  severity_multipliers:
    - critical: 2.0x
    - high: 1.5x
    - medium: 1.0x
    - low: 0.5x
    
  maximum: 1.0  # Complete drift
```

**Score Interpretation:**
| Score | Meaning |
|-------|---------|
| 0.0 - 0.1 | Excellent sync |
| 0.1 - 0.3 | Minor drift (acceptable) |
| 0.3 - 0.5 | Moderate drift (should address) |
| 0.5 - 0.7 | Significant drift (needs attention) |
| 0.7 - 1.0 | Severe drift (urgent fix needed) |

### Step 5: Generate Fix Recommendations

For each drift finding:
- Specific file and line
- What to change
- Suggested correct text
- Priority

## Output Contract

### Drift Report Structure

```yaml
drift_report:
  # Metadata
  timestamp: "2026-01-10T12:00:00Z"
  target: "prompt-library"
  skill: "documentation-drift-detector v1.0.0"
  
  # Summary
  drift_score: 0.35
  drift_level: moderate
  
  surfaces_analyzed:
    - path: README.md
      claims_found: 24
      claims_verified: 21
      drift_detected: 3
      
    - path: docs/agent-invocation-guide.md
      claims_found: 15
      claims_verified: 13
      drift_detected: 2
      
  # Findings by type
  findings:
    structural:
      - id: S-001
        severity: medium
        location:
          file: README.md
          line: 45
        claim: "See skills/core/dependency-health-check.md"
        reality: "File exists at skills/security/dependency-health-check.md"
        fix: "Update path to skills/security/dependency-health-check.md"
        
    behavioral:
      - id: B-001
        severity: high
        location:
          file: docs/column-pattern-guide.md
          line: 127
        claim: "Output includes 'column_router_assessment' key"
        reality: "Actual output key is 'column_plan'"
        fix: "Change 'column_router_assessment' to 'column_plan'"
        
    temporal:
      - id: T-001
        severity: low
        location:
          file: README.md
          line: 1
        indicator: "README last modified 45 days ago"
        reality: "Skills modified 12 times since"
        fix: "Review and update README"
        
    semantic: []
    
  # Priority fixes
  priority_fixes:
    critical: []
    high:
      - id: B-001
        summary: "Column router output contract mismatch"
        effort: "5 minutes"
    medium:
      - id: S-001
        summary: "Incorrect skill path reference"
        effort: "2 minutes"
    low:
      - id: T-001
        summary: "README may be stale"
        effort: "30 minutes review"
        
  # Recommendations
  recommendations:
    - "Update path references in README.md"
    - "Verify output contracts match actual skill behavior"
    - "Consider adding automated drift checks to CI"
    
  # Files to modify
  files_to_modify:
    - path: README.md
      changes: 2
      effort: "10 minutes"
    - path: docs/column-pattern-guide.md
      changes: 1
      effort: "5 minutes"
```

### Filename Convention

```
YYYY-MM-DD_documentation-drift_[target].md
```

Example: `2026-01-10_documentation-drift_prompt-library.md`

## Execution Modes

### Full Scan Mode

**When to Use:**
- Initial audit
- Pre-release check
- Periodic hygiene

**Process:**
1. Scan all documentation files
2. Extract all claims
3. Verify all claims
4. Generate complete report

**Invocation:**
```
"Run documentation-drift-detector on prompt-library"
```

### Incremental Mode

**When to Use:**
- After code changes
- PR review
- CI integration

**Process:**
1. Accept changed files list
2. Find documentation that references changed areas
3. Verify only affected claims
4. Generate delta report

**Invocation:**
```
"Check documentation drift for changes in skills/"
```

### Targeted Mode

**When to Use:**
- Checking specific documentation
- After editing docs
- Verifying single file

**Process:**
1. Analyze specified documentation file(s)
2. Extract and verify all claims
3. Generate focused report

**Invocation:**
```
"Check drift in README.md"
```

## Common Misuses / Anti-Patterns

### DON'T Use This Skill For...

**Anti-Pattern 1: Checking non-existent documentation**
- **Instead:** Use documentation-generator first
- **Why:** Can't detect drift in what doesn't exist

**Anti-Pattern 2: Running during active development**
- **Instead:** Wait for feature stabilization
- **Why:** Drift is expected during development

**Anti-Pattern 3: Treating all drift as critical**
- **Instead:** Use severity levels appropriately
- **Why:** Some drift is acceptable; prioritize high-impact fixes

### WARNING: Known Limitations

**Limitation:** Cannot verify semantic correctness
- **Mitigation:** Manual review still needed for meaning
- **Confidence:** ~85% accuracy on structural claims

**Limitation:** May miss implicit claims
- **Mitigation:** Focus on explicit, verifiable claims
- **Confidence:** Explicit claims are reliable

## Known Limitations

- Cannot verify code behavior (only structure)
- May not catch all path variations
- Depends on consistent documentation format
- Cannot verify claims in images or diagrams

## Fallback Strategy

If drift detection fails:

1. **Report partial results** - What was successfully checked
2. **List unchecked claims** - For manual review
3. **Suggest manual audit** - When automation is insufficient

## Integration Points

### Upstream (Inputs)

| Source | What It Provides |
|--------|------------------|
| File system | Documentation files, code files |
| Git | Change history for temporal drift |
| skill-map.yaml | Surface definitions |

### Downstream (Outputs)

| Consumer | How It Uses Report |
|----------|-------------------|
| Human | Fix prioritization |
| Health Assessor | Documentation surface health |
| Readiness Certifier | Documentation quality evidence |
| CI/CD | Automated drift gates |

## Examples

### Example 1: Clean Documentation

```yaml
drift_report:
  drift_score: 0.05
  drift_level: excellent
  
  summary: "Documentation is well-synchronized with code"
  
  findings:
    structural: []
    behavioral: []
    temporal:
      - severity: low
        note: "Minor staleness in CHANGELOG"
```

### Example 2: Moderate Drift

```yaml
drift_report:
  drift_score: 0.35
  drift_level: moderate
  
  findings:
    structural:
      - severity: medium
        count: 2
        summary: "Path references outdated"
    behavioral:
      - severity: high
        count: 1
        summary: "Output contract mismatch"
        
  priority_fixes:
    high:
      - "Update column-router output documentation"
    medium:
      - "Fix path references in README"
```

### Example 3: Severe Drift

```yaml
drift_report:
  drift_score: 0.72
  drift_level: severe
  
  alert: "Documentation significantly out of sync"
  
  findings:
    structural:
      count: 8
      summary: "Multiple file references broken"
    behavioral:
      count: 5
      summary: "Several API contracts outdated"
    semantic:
      count: 3
      summary: "Deprecated terminology still in use"
      
  recommendation: |
    URGENT: Documentation needs comprehensive review.
    Consider documentation sprint before release.
```

## Exit Conditions

### Success

- All targeted documentation analyzed
- Claims extracted and verified
- Drift score calculated
- Actionable findings generated

### Failure

- Documentation files inaccessible
- No verifiable claims found
- Critical error during analysis

### Handoff

After detection:
1. Present drift report with severity
2. Provide specific fix recommendations
3. Estimate effort for fixes
4. Optionally generate fix suggestions for Cursor

## See Also

- `skills/meta/health-assessor.md` - Uses drift detection for health
- `skills/meta/readiness-certifier.md` - Documentation quality in certification
- `meta/skill-scope-policy.md` - Scope classification
- `protocols/handoff-protocol.md` - Finding format
