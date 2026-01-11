# Skill Selector

## Decision Tree

Use this guide to choose the right skill(s) for your needs.

```
I want to improve my codebase
│
├─ What aspect needs work?
│  │
│  ├─ Structure & Organization
│  │  └─→ project-structure-analyzer
│  │      (Maps codebase, creates dependency graph)
│  │
│  ├─ Architecture & Design
│  │  └─→ architecture-review
│  │      (Reviews patterns, identifies issues, recommends refactoring)
│  │      ⚠️ Run project-structure-analyzer first
│  │
│  ├─ Code Quality
│  │  └─→ code-quality-audit
│  │      (Analyzes code quality, identifies technical debt)
│  │
│  ├─ User Interface / UX
│  │  └─→ adversarial-ui-tester
│  │      (Tests UI from user perspective, finds UX issues)
│  │
│  ├─ Security & Dependencies
│  │  └─→ dependency-health-check
│  │      (Checks vulnerabilities, outdated packages)
│  │
│  └─ Documentation
│     └─→ documentation-generator
│         (Generates documentation, finds gaps)
│
├─ I want to validate something
│  │
│  ├─ Validate handoff report quality
│  │  └─→ handoff-quality-validator
│  │      (Checks if report meets protocol)
│  │
│  └─ Validate skill definition
│     └─→ skill-health-check
│         (Checks if skill file is well-formed)
│
└─ I want a comprehensive analysis
   └─→ Use skill chain: full-codebase-audit-v1
       (Runs multiple skills in sequence)
```

## Quick Reference

### By Goal

| Goal | Recommended Skill(s) |
|------|---------------------|
| Understand codebase structure | project-structure-analyzer |
| Review architecture | project-structure-analyzer → architecture-review |
| Improve code quality | code-quality-audit |
| Fix UX issues | adversarial-ui-tester |
| Check security | dependency-health-check |
| Generate docs | documentation-generator |
| Full audit | full-codebase-audit-v1 (skill chain) |

### By Project Type

| Project Type | Recommended Skills |
|-------------|-------------------|
| React SPA | See `profiles/react-spa.md` |
| Node.js API | project-structure-analyzer → architecture-review → dependency-health-check |
| Monolith | project-structure-analyzer → architecture-review |
| Microservices | project-structure-analyzer → architecture-review (per service) |

### By Situation

| Situation | Recommended Skill(s) |
|-----------|-------------------|
| First time on project | project-structure-analyzer |
| Before major refactor | project-structure-analyzer → architecture-review |
| PR review | Use incremental mode on changed files |
| Security audit | dependency-health-check |
| Accessibility check | adversarial-ui-tester |
| Performance issues | architecture-review (with performance focus) |

## Skill Combinations

### Recommended Sequences

**Discovery → Analysis**
```
project-structure-analyzer → architecture-review
```
Understand structure, then review architecture.

**Parallel Analysis**
```
dependency-health-check || adversarial-ui-tester
```
Check dependencies and UI simultaneously (no dependency between them).

**Validation Chain**
```
[Any skill] → handoff-quality-validator
```
Validate any skill's output.

### Skill Chains

See `skill-chains/` directory for version-locked combinations:
- `full-codebase-audit-v1.yaml`: Comprehensive analysis

## Execution Modes

### When to Use Full-Scan

- First time analyzing codebase
- Major refactoring planning
- Comprehensive audit needed
- Before major release

### When to Use Incremental

- PR review
- After making changes
- Continuous monitoring
- Regular maintenance

### When to Use Targeted

- Debugging specific issue
- Analyzing one module
- Focused refactoring
- Large codebase (break into pieces)

## Cost Considerations

| Skill | Cost | Runtime | When to Use |
|-------|-----|---------|-------------|
| project-structure-analyzer | Low | 1-3min | Often (foundational) |
| architecture-review | Medium | 5-10min | Before refactoring, major changes |
| adversarial-ui-tester | Medium | 5-15min | Before releases, UX concerns |
| dependency-health-check | Low | 2-5min | Regularly (weekly/monthly) |
| handoff-quality-validator | Low | 1-2min | After any skill |
| skill-health-check | Low | 1-2min | Before committing skills |

## Complexity Levels

Choose skills appropriate for your expertise:

- **Simple**: Can be used by anyone
  - project-structure-analyzer
  - dependency-health-check
  - handoff-quality-validator
  - skill-health-check

- **Moderate**: Requires some domain knowledge
  - architecture-review
  - adversarial-ui-tester

- **Complex**: Requires architectural knowledge
  - (Future skills)

- **Expert**: Requires deep system knowledge
  - (Future skills)

## Still Not Sure?

1. **Start with project-structure-analyzer**: It's foundational and low cost
2. **Check skills-index.md**: Comprehensive index organized by scope and tier
3. **Check profiles/**: See if your project type has a profile
4. **Use skill chains**: Try `full-codebase-audit-v1` for comprehensive analysis
5. **Review skill-scope-policy.md**: Understand when to use project-specific vs universal skills
6. **Ask**: Review skill descriptions in `skills/` directory

## Project-Specific vs Universal Skills

**Universal Skills (Core):**
- Work on any project
- Located in `agent-skills/skills/core/`
- Examples: dependency-health-check, architecture-review

**Project-Specific Skills:**
- Only relevant to your project
- Located in `.agent-skills/skills/project/`
- Examples: philosophy-compliance-enforcer (Prompt Library)

**When to use each:**
- Use universal skills for general analysis (architecture, dependencies, testing)
- Use project-specific skills for project-specific invariants (philosophy, privacy tiers, state machines)

See `meta/skill-scope-policy.md` for detailed guidance.

## Examples

### Example 1: New to Project

**Goal**: Understand the codebase

**Skills**:
1. project-structure-analyzer (full-scan)
2. architecture-review (full-scan) - after #1

**Result**: Complete understanding of structure and architecture

### Example 2: PR Review

**Goal**: Review changes in pull request

**Skills**:
1. project-structure-analyzer (incremental on changed files)
2. architecture-review (incremental) - if structural changes
3. adversarial-ui-tester (incremental) - if UI changes

**Result**: Focused review of changes

### Example 3: Security Audit

**Goal**: Check for security issues

**Skills**:
1. dependency-health-check (full-scan)

**Result**: Security vulnerabilities and update recommendations

