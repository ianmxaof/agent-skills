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

