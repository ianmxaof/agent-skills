---
name: skill-name
category: category-name
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 2-5min
complexity-level: simple
requires-deep-analysis: false
prerequisites:
  - skill: prerequisite-skill-name
    reason: "Why this is needed"
  - file: required-file.json
    reason: "What this file provides"
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Skill Name

## Purpose

[What this skill does and when it should be used]

## When to Invoke

### Explicit Trigger Phrases

- "Run [skill-name] on [target]"
- "Analyze [aspect] using [skill-name]"
- "Check [component] with [skill-name]"

### Situational Triggers

- When [specific situation occurs]
- Before [specific action]
- After [specific event]

## Required Cursor Settings

- **Mode**: [Composer / Chat / etc.]
- **Model preference**: [Claude Sonnet / Opus / etc.]
- **Multi-Model**: On / Off
- **Additional settings**: [Any other required settings]

## Behavioral Rules

### How the Model Should Reason

- [Guidance on reasoning approach]
- [What to prioritize]
- [What to avoid]

### What It Must Avoid

- [Specific anti-patterns in execution]
- [Common mistakes to prevent]

### What It Must Prioritize

- [Key priorities during execution]
- [Critical aspects to focus on]

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Initial assessment of codebase
- Major refactoring planning
- Comprehensive analysis needed

**Input:**
- Entire codebase
- All relevant files

**Process:**
- Agent reads all relevant files
- Performs comprehensive analysis
- Generates complete report

**Invocation Example:**
> "Run [skill-name] in full-scan mode on the entire project"

### Incremental Mode

**When to Use:**
- PR review
- Continuous monitoring
- Analyzing recent changes

**Input:**
- Git diff or changed files list
- Only files modified since last analysis

**Process:**
- Agent reads only changed files + necessary context
- Compares against previous state
- Focuses on impact of changes

**Invocation Example:**
> "Run [skill-name] in incremental mode on files changed in the last commit"

### Targeted Mode

**When to Use:**
- Debugging specific issues
- Focused refactoring
- Analyzing specific modules

**Input:**
- Specific file paths or modules
- Defined scope only

**Process:**
- Agent reads only specified scope
- Deep analysis of targeted area
- Ignores rest of codebase

**Invocation Example:**
> "Run [skill-name] in targeted mode on src/auth/ directory"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: [Description]**
- **Instead:** Use [alternative skill or approach]
- **Why:** [Reason this is wrong - e.g., "This skill requires existing architecture to review"]

**Anti-Pattern 2: [Description]**
- **Instead:** [Alternative approach]
- **Why:** [Reason - e.g., "High token cost ($0.50/run on large codebase), better for PR merge than every commit"]

### ⚠️ WARNING: Known Limitations

**Limitation:** [Description - e.g., "May produce false positives for micro-frontends"]
- **Mitigation:** [How to handle - e.g., "Review architectural boundaries section manually"]
- **Confidence:** [Accuracy estimate - e.g., "~70% accuracy on micro-frontend patterns"]

## Known Limitations

- [Limitation 1 - e.g., "May struggle with codebases > 50k lines"]
- [Limitation 2 - e.g., "Requires TypeScript types to be accurate"]
- [Limitation 3 - e.g., "Cannot analyze binary files"]

## Fallback Strategy

If this skill fails, try:

1. [Fallback option 1 - e.g., "Run simpler-code-review instead"]
2. [Fallback option 2 - e.g., "Break codebase into modules"]
3. [Fallback option 3 - e.g., "Manual review required"]

## Output Contract

### Handoff Report Structure

The handoff report MUST include these sections (see `protocols/handoff-protocol.md`):

1. **Context Summary**
   - [What should be included]

2. **Findings**
   - [Structure and format]
   - Priority levels: Critical/High/Medium/Low

3. **Recommendations**
   - [Structure and format]
   - Actionable items with effort estimates

4. **Implementation Steps**
   - [Ordered list format]

5. **Files to Modify/Create**
   - [Format: path, change type, description]

6. **Dependencies**
   - [External dependencies, prerequisites used]

### Filename Convention

Reports must follow: `YYYY-MM-DD_skill-name_target-component.md`

### Context Preservation Strategy

When handoff report exceeds 4000 tokens:

1. Summarize findings into tiers (Critical/High/Medium/Low)
2. Link to detailed analysis in separate file
3. Preserve only actionable items in handoff

## Exit Conditions

### Success

- [What constitutes successful execution]
- [What should be in the handoff report]
- [Next steps after success]

### Failure

- [When skill should fail]
- [Error conditions]
- [What to report on failure]

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary to user
4. Indicate readiness for Cursor implementation

## Context Received (for Chained Skills)

If this skill builds on others, acknowledge:

```markdown
## Context Received

This analysis builds on:
- [Previous skill name] v[version] (executed [date])
- Key findings: [summary]
- Assumptions carried forward: [list]
```

## Examples

### Example 1: [Use Case]

[Description of example scenario and expected output]

### Example 2: [Use Case]

[Description of example scenario and expected output]

