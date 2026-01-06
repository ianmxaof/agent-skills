---
name: architecture-review
category: architecture
version: 1.0.0
maturity: validated
estimated-cost: medium
typical-runtime: 5-10min
complexity-level: moderate
requires-deep-analysis: true
prerequisites:
  - skill: project-structure-analyzer
    reason: "Need codebase map and dependency graph to review architecture effectively"
execution-modes:
  - full-scan
  - incremental
  - targeted
---

# Architecture Review

## Purpose

Reviews codebase architecture, identifies design patterns, detects architectural issues, and provides refactoring recommendations. Builds on project structure analysis to evaluate architectural quality.

## When to Invoke

### Explicit Trigger Phrases

- "Run architecture-review on [component/service]"
- "Review the architecture of [target]"
- "Analyze architectural patterns in [module]"
- "Check for architectural issues"

### Situational Triggers

- Before major refactoring
- When adding new major features
- After project-structure-analyzer (recommended sequence)
- When architectural concerns arise
- During codebase health checks

## Required Cursor Settings

- **Mode**: Composer
- **Model preference**: Claude Sonnet or Opus
- **Multi-Model**: Off
- **Additional settings**: None required

## Behavioral Rules

### How the Model Should Reason

- Evaluate architectural patterns and their appropriateness
- Identify coupling and cohesion issues
- Check for architectural boundaries and their enforcement
- Assess scalability and maintainability concerns
- Look for anti-patterns and design smells
- Consider tradeoffs and context

### What It Must Avoid

- Don't focus on code style (that's code-quality-audit)
- Don't make recommendations without understanding context
- Don't suggest breaking changes without risk assessment
- Don't ignore existing constraints and requirements

### What It Must Prioritize

- Architectural boundaries and module separation
- Dependency direction and layering
- Scalability concerns
- Maintainability and technical debt
- Design pattern appropriateness

## Execution Mode Implementation

### Full Scan Mode

**When to Use:**
- Initial architecture assessment
- Major refactoring planning
- Comprehensive architecture review

**Input:**
- Entire codebase (or major components)
- Output from project-structure-analyzer
- Key architectural files

**Process:**
1. Review overall architecture and patterns
2. Analyze module boundaries and dependencies
3. Identify architectural issues
4. Evaluate scalability and maintainability
5. Generate comprehensive recommendations

**Invocation Example:**
> "Run architecture-review in full-scan mode on the backend service"

### Incremental Mode

**When to Use:**
- After architectural changes
- Reviewing impact of new features
- Continuous architecture monitoring

**Input:**
- Changed files from git diff
- Previous architecture review (if available)
- Context from project-structure-analyzer

**Process:**
1. Analyze impact of changes on architecture
2. Check if boundaries were violated
3. Assess if patterns were maintained
4. Report on architectural drift

**Invocation Example:**
> "Run architecture-review in incremental mode on files changed in the last commit"

### Targeted Mode

**When to Use:**
- Reviewing specific module or service
- Deep dive into architectural concern
- Focused refactoring planning

**Input:**
- Specific module or service
- Its dependencies and dependents
- Related architectural context

**Process:**
1. Deep analysis of target architecture
2. Evaluate module's architectural quality
3. Check integration with rest of system
4. Provide focused recommendations

**Invocation Example:**
> "Run architecture-review in targeted mode on src/auth/ service"

## Common Misuses / Anti-Patterns

### ❌ DON'T Use This Skill For...

**Anti-Pattern 1: Initial Project Setup**
- **Instead:** Use project-structure-analyzer first, then architecture-review
- **Why:** Architecture-review needs existing structure to review. For new projects, focus on structure first.

**Anti-Pattern 2: Running on Every Commit**
- **Instead:** Use incremental mode on PR merge, or scheduled reviews
- **Why:** Medium cost (~$0.30-0.50/run on large codebase). Architecture doesn't change that frequently.

**Anti-Pattern 3: Code Style Issues**
- **Instead:** Use code-quality-audit for code-level issues
- **Why:** Architecture-review focuses on structure and design, not code style or individual function quality.

### ⚠️ WARNING: Known Limitations

**Limitation:** May produce false positives for micro-frontends
- **Mitigation:** Review architectural boundaries section manually. Micro-frontends have intentional duplication.
- **Confidence:** ~70% accuracy on micro-frontend patterns

**Limitation:** May struggle with event-driven architectures
- **Mitigation:** Look for event bus patterns and message queues explicitly
- **Confidence:** ~65% accuracy on event-driven detection

## Known Limitations

- May struggle with codebases > 100k lines - may need to focus on key modules
- Event-driven and message-based architectures are harder to analyze statically
- Micro-frontend boundaries may appear as duplication (false positive)
- Requires TypeScript types or good JSDoc for accurate dependency analysis
- Cannot analyze runtime architecture (only static code structure)

## Fallback Strategy

If this skill fails, try:

1. **Run project-structure-analyzer first**: Ensure you have codebase map
2. **Break into modules**: Use targeted mode on smaller pieces
3. **Check documentation**: ARCHITECTURE.md or design docs may help
4. **Manual review**: For very complex architectures, manual review may be needed

## Output Contract

### Handoff Report Structure

1. **Context Summary**
   - Architecture overview
   - Patterns identified
   - Scope of review

2. **Findings**
   - Architectural strengths
   - Architectural issues (with priority: Critical/High/Medium/Low)
   - Design pattern evaluation
   - Coupling and cohesion assessment
   - Scalability concerns
   - Maintainability issues

3. **Recommendations**
   - Refactoring suggestions (prioritized)
   - Pattern improvements
   - Boundary enforcement
   - Dependency improvements
   - Each with effort estimate and impact

4. **Implementation Steps**
   - Ordered refactoring steps
   - Migration path for breaking changes
   - Risk mitigation strategies

5. **Files to Modify/Create**
   - Files needing architectural changes
   - New files for separation of concerns
   - Configuration changes

6. **Dependencies**
   - Prerequisites used (project-structure-analyzer output)
   - Architectural patterns referenced
   - Design principles applied

### Filename Convention

Reports must follow: `YYYY-MM-DD_architecture-review_target-component.md`

### Context Preservation Strategy

For large codebases:
1. Summary with Critical/High priority findings in main report
2. Detailed analysis in separate file
3. Link to detailed analysis from main report

## Exit Conditions

### Success

- Architecture reviewed comprehensively
- Issues identified and prioritized
- Recommendations provided
- Handoff report generated per protocol

### Failure

- Missing prerequisites (project-structure-analyzer) - fail with clear error
- Unreadable architecture - document what was found
- Timeout - suggest targeted mode

### Handoff to Cursor

After execution:
1. Generate handoff report per protocol
2. Save report with proper filename
3. Provide summary: "Architecture review complete. Found [X] issues, [Y] recommendations. See report for details."
4. Indicate readiness for implementation

## Context Received (for Chained Skills)

If building on project-structure-analyzer:

```markdown
## Context Received

This analysis builds on:
- project-structure-analyzer v1.0.0 (executed 2024-01-05)
- Key findings: Codebase has 5 main modules, client-server separation, React frontend + Node.js backend
- Assumptions carried forward: Structure is accurately mapped, dependencies are correct
```

## Examples

### Example 1: Monolithic Application Review

**Scenario:** Reviewing a monolithic Node.js application

**Expected Findings:**
- Tight coupling between modules
- Lack of clear boundaries
- Shared database access patterns
- Recommendations for service boundaries

### Example 2: Microservices Architecture Review

**Scenario:** Reviewing microservices architecture

**Expected Findings:**
- Service boundaries evaluation
- Inter-service communication patterns
- Data consistency strategies
- Recommendations for service decomposition or consolidation

