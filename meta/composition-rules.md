# Composition Rules

## Overview

This document defines how multiple agent skills can work together, including execution ordering, conflict resolution, and context sharing.

## Execution Modes

### Parallel Execution

Skills can run in parallel when:
- They operate on different parts of the codebase
- They have no data dependencies on each other
- Their outputs are independent

**Example:**
- `dependency-health-check` and `adversarial-ui-tester` can run in parallel
- Both analyze different aspects and don't require each other's output

### Sequential Execution

Skills must run sequentially when:
- One skill's output is required by another
- Skills analyze overlapping code that could conflict
- Order matters for correctness

**Example:**
- `project-structure-analyzer` must run before `architecture-review`
- Architecture review needs the codebase map from structure analyzer

## Conflict Resolution

When skills provide contradictory advice:

1. **Check Rule Precedence**
   - See `meta/rule-precedence.md` for resolution hierarchy
   - Security recommendations override performance recommendations
   - Architecture decisions override code style suggestions

2. **Context Matters**
   - Consider the specific context of each recommendation
   - Some conflicts may be valid (e.g., security vs. performance tradeoffs)

3. **Escalation**
   - If conflicts cannot be resolved automatically, flag for human review
   - Document the conflict in the handoff report

## Shared Context Protocols

### Context Passing Between Skills

When chaining skills, the second skill MUST acknowledge findings from the first:

```markdown
## Context Received

This analysis builds on:
- `project-structure-analyzer` v1.0.0 (executed 2024-01-05)
- Key findings: [summary of relevant findings]
- Assumptions carried forward: [list]
```

### Context Preservation

- Preserve critical context in handoff reports
- Reference previous skill outputs explicitly
- Don't duplicate analysis already performed

### Context Budget

- When chaining skills, be mindful of total context usage
- Summarize previous findings rather than repeating full analysis
- Use references to previous reports when possible

## Skill Chain Patterns

### Pattern 1: Discovery → Analysis → Validation

```
project-structure-analyzer → architecture-review → handoff-quality-validator
```

### Pattern 2: Parallel Analysis → Synthesis

```
dependency-health-check ┐
adversarial-ui-tester  ├→ handoff-quality-validator
code-quality-audit    ┘
```

### Pattern 3: Incremental Updates

```
project-structure-analyzer (incremental mode)
  → architecture-review (targeted mode on changed modules)
```

## Best Practices

1. **Always run prerequisites first**
   - Check skill prerequisites before execution
   - Fail fast if prerequisites aren't met

2. **Document skill chains**
   - Use `skill-chains/` directory for proven combinations
   - Version lock skill chains for reproducibility

3. **Respect execution modes**
   - Use incremental mode when appropriate
   - Use targeted mode for focused analysis

4. **Validate outputs**
   - Run `handoff-quality-validator` on skill chain outputs
   - Ensure handoff reports meet protocol standards

