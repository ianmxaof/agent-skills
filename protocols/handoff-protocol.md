# Handoff Protocol

## Overview

This protocol defines the standard structure for handoff reports produced by agent skills. Handoff reports are designed to be consumed by implementation agents (e.g., Cursor) to execute recommendations.

## Handoff Report Structure

### Required Sections

1. **Context Summary**
   - Brief overview of what was analyzed
   - Scope of analysis (files, modules, time period)
   - Key assumptions made

2. **Findings**
   - Structured list of issues, opportunities, or observations
   - Each finding should include:
     - Priority level (Critical/High/Medium/Low)
     - Category/type
     - Description
     - Evidence or examples

3. **Recommendations**
   - Actionable recommendations derived from findings
   - Each recommendation should include:
     - Priority
     - Estimated effort
     - Dependencies
     - Expected impact

4. **Implementation Steps**
   - Ordered list of steps to implement recommendations
   - Each step should be:
     - Specific and actionable
     - Include file paths or modules affected
     - Reference specific code locations when possible

5. **Files to Modify/Create**
   - List of files that need changes
   - For each file:
     - Path (relative to project root)
     - Type of change (modify/create/delete)
     - Brief description of changes

6. **Dependencies**
   - External dependencies required
   - Skill prerequisites that were used
   - Tools or frameworks needed

## Filename Convention

Handoff reports must follow this naming pattern:

```
YYYY-MM-DD_skill-name_target-component.md
```

**Examples:**
- `2024-01-05_architecture-review_auth-service.md`
- `2024-01-05_dependency-health-check_full-project.md`
- `2024-01-05_project-structure-analyzer_backend-module.md`

**Components:**
- `YYYY-MM-DD`: Date of analysis (ISO 8601)
- `skill-name`: Kebab-case name of the skill that generated the report
- `target-component`: Brief identifier of what was analyzed (service name, module, "full-project", etc.)

## Context Budget Management

When handoff reports exceed 4000 tokens, use the following strategies:

### Tiered Summarization

1. **Critical Priority Only**
   - Include only Critical and High priority findings in main report
   - Medium and Low priority findings moved to separate file

2. **Separate Detailed Analysis**
   - Create companion file: `YYYY-MM-DD_skill-name_target-component-details.md`
   - Link to detailed analysis from main report
   - Main report preserves only actionable items

3. **Priority Tiers**
   - **Critical**: Security issues, data loss risks, breaking changes
   - **High**: Performance issues, architectural problems, major technical debt
   - **Medium**: Code quality improvements, minor optimizations
   - **Low**: Style improvements, documentation gaps

### Example Structure for Large Reports

```markdown
# Architecture Review - Auth Service

## Executive Summary
[Brief overview - max 500 tokens]

## Critical Findings
[Only Critical and High priority - actionable items]

## Detailed Analysis
See: `2024-01-05_architecture-review_auth-service-details.md` for:
- Medium priority findings
- Low priority findings
- Full code examples
- Extended recommendations

## Implementation Priority
1. [Critical item 1]
2. [Critical item 2]
...
```

## Output Format

Handoff reports should be:
- **Markdown format** for readability
- **Self-contained** for the actionable items
- **Linked** to detailed analysis when needed
- **Version-controlled** alongside code

## Validation

Use `handoff-quality-validator` skill to ensure reports meet this protocol.

---

## Artifact Format (Warp → Cursor Handoff)

When skills are executed through the Warp integration, output is written as artifacts to the filesystem.

### The Decoupling Principle

**Skills produce output. Execution layer handles persistence.**

Skills:
- Produce structured content following this protocol
- Don't "know" where artifacts are stored
- Remain portable across execution environments

Execution layer:
- Receives skill output
- Writes to filesystem with proper naming
- Manages artifact lifecycle

**Why this matters:** Skills can be tested without filesystem side effects, and persistence mechanics can change without updating skill definitions.

### Artifact File Naming

```
{skill-name}-{ISO-timestamp}.md
```

**Examples:**
```
adversarial-ui-tester-2026-01-07T19-42-00Z.md
privacy-tier-auditor-2026-01-07T20-15-30Z.md
architecture-review-2026-01-07T21-30-00Z.md
```

**Rules:**
- Use skill name exactly as in front matter
- ISO 8601 timestamp in UTC
- Replace colons with hyphens for filesystem compatibility
- Always `.md` extension

### Artifact Front Matter (Required)

Every artifact MUST include this front matter block:

```yaml
---
skill: skill-name
scope: core | domain | project
status: new | processed | archived
timestamp: 2026-01-07T19:42:00Z
intended-consumer: cursor | warp | human
priority: critical | high | medium | low
execution-mode: full-scan | incremental | targeted
target: "description of what was analyzed"
---
```

**Required Fields:**

| Field | Description | Values |
|-------|-------------|--------|
| `skill` | Name of skill that produced this | Exact skill name |
| `scope` | Scope of the skill | core, domain, project |
| `status` | Artifact lifecycle status | new, processed, archived |
| `timestamp` | When artifact was created | ISO 8601 UTC |
| `intended-consumer` | Who should process this | cursor, warp, human |
| `priority` | Processing urgency | critical, high, medium, low |

**Optional Fields:**

| Field | Description |
|-------|-------------|
| `execution-mode` | How the skill was invoked |
| `target` | What was analyzed |
| `resolution-trace` | If from skill-router, include trace |
| `chain` | If part of skill chain, chain name |
| `intent` | Intent hash for correlation (optional, v1.5/v2) |

**Note on Intent Hash:** The `intent` field is optional and documented for future use. See `meta/artifact-policy.md` for details on when to use it.

### Artifact Directory Structure

```
.agent-skills/artifacts/
├── incoming/      # New artifacts (Cursor reads when directed)
├── processed/     # Already consumed
├── archive/       # Historical decision records
└── .gitignore
```

### Artifact Lifecycle

```
new → processed → archived
       │
       └→ deleted (not recommended)
```

| Status | Location | Meaning |
|--------|----------|---------|
| `new` | `incoming/` | Awaiting processing |
| `processed` | `processed/` | Recently consumed |
| `archived` | `archive/` | Historical record |

### Example Complete Artifact

```markdown
---
skill: adversarial-ui-tester
scope: core
status: new
timestamp: 2026-01-07T19:42:00Z
intended-consumer: cursor
priority: high
execution-mode: targeted
target: "checkout flow"
intent:
  raw: "adversarial UI testing of checkout flow"
  normalized: "adversarial-ui-test:checkout"
---

# Adversarial UI Tester - Checkout Flow

## Context Summary
Analyzed checkout flow for adversarial UX failure modes.
Scope: /src/components/checkout/
Assumptions: Standard e-commerce flow

## Findings

### Critical Priority

1. **Missing Confirmation on Destructive Action**
   - Category: User Safety
   - Description: "Clear Cart" button has no confirmation
   - Evidence: CheckoutCart.tsx line 42
   - Impact: Accidental data loss

### High Priority

2. **Accessibility: Missing ARIA Labels**
   - Category: Accessibility
   - Description: Form inputs lack aria-labels
   - Evidence: CheckoutForm.tsx lines 15-28
   - Impact: Screen reader users cannot navigate

## Recommendations

1. Add confirmation dialog to "Clear Cart" (Priority: Critical, Effort: 30min)
2. Add aria-labels to all form inputs (Priority: High, Effort: 1hr)

## Implementation Steps

1. Create ConfirmDialog component if not exists
2. Wrap "Clear Cart" handler with confirmation
3. Add aria-label to each input in CheckoutForm
4. Add aria-describedby for validation messages

## Files to Modify

- `/src/components/checkout/CheckoutCart.tsx` - Add confirmation
- `/src/components/checkout/CheckoutForm.tsx` - Add accessibility
- `/src/components/ui/ConfirmDialog.tsx` - Create if needed

## Dependencies

- None (uses existing UI patterns)

## Handoff Notes for Cursor

- Prioritize the confirmation dialog (Critical)
- Use existing ConfirmDialog pattern from settings page
- Do NOT change visual design
- Do NOT refactor unrelated code
```

### See Also

- `meta/artifact-policy.md` - Full artifact lifecycle documentation
- `docs/warp-integration-guide.md` - How Warp writes artifacts
- `docs/agent-invocation-guide.md` - How Cursor processes artifacts

