# Skill Scope Policy

This document defines when skills belong in the universal repo vs project-specific directories, and governs the promotion path from project-specific to universal skills.

## Three Layers of Skills

### Layer 1: Core (Universal)

**Location:** `agent-skills/skills/core/`

**Characteristics:**
- Works on **any** project (language-agnostic where possible)
- No project-specific assumptions
- General-purpose analysis
- Reusable across different technology stacks

**Criteria for Core Skills:**
- Used successfully on 3+ different projects
- No project-specific assumptions remain
- Documentation is general-purpose
- Works with multiple languages/frameworks

**Examples:**
- `dependency-health-check` (scans package.json, requirements.txt, etc.)
- `test-coverage-gap-finder` (works with any test framework)
- `bundle-size-analyzer` (works with any bundler)
- `architecture-review` (reviews design patterns generally)

**Promotion Path:** Project → Domain → Core

---

### Layer 2: Domain (Technology-Specific)

**Location:** `agent-skills/skills/domains/{domain}/`

**Characteristics:**
- Specific to a **technology domain** (React apps, CLI tools, ML projects, etc.)
- Assumes certain stack/patterns
- Reusable across projects in that domain
- Not applicable to projects outside the domain

**Criteria for Domain Skills:**
- Used successfully on 2+ projects in the same domain
- Domain-specific assumptions are documented
- Skill is valuable to others in that domain
- Cannot be generalized further without losing value

**Examples:**
```
domains/
├── react-apps/
│   ├── react-state-management-review.md
│   ├── react-component-boundaries-audit.md
│   └── react-hooks-misuse-detector.md
├── cli-tools/
│   ├── cli-ux-consistency-checker.md
│   └── cli-help-text-validator.md
└── electron-apps/
    ├── ipc-security-auditor.md
    └── electron-bundle-optimizer.md
```

**Promotion Path:** Project → Domain

---

### Layer 3: Project-Specific

**Location:** `{project-root}/.agent-skills/skills/project/`

**Characteristics:**
- Only relevant to **this specific project**
- Encodes project-specific invariants/patterns
- NOT intended for reuse elsewhere
- May eventually be generalized and promoted

**Criteria for Project-Specific Skills:**
- Encodes project-specific concepts (e.g., "Prompt Library philosophy", "Privacy tiers")
- Not applicable to other projects
- May contain project-specific file paths or configurations
- May eventually be generalized if pattern is identified

**Examples (Prompt Library):**
- `philosophy-compliance-enforcer` (Prompt Library philosophy)
- `privacy-tier-auditor` (Prompt Library privacy tiers)
- `state-invariant-validator` (Prompt Library state machine)
- `variant-tree-explosion-detector` (Prompt Library variant trees)

**Promotion Path:** When pattern is identified as reusable

---

## Promotion Criteria

### Project → Domain Promotion

**Required:**
1. Skill has been used on current project for 2+ months
2. You identify the generalizable **pattern** (not implementation)
3. You can name at least 2 other projects in the same domain that would benefit
4. You remove all project-specific references

**Process:**
1. Copy skill to `agent-skills/skills/domains/{domain}/`
2. Generalize: Replace project-specific details with configuration
3. Document assumptions (e.g., "Assumes React project")
4. Add `derived-from` field in front matter
5. Add example projects that could use this skill
6. Submit PR to universal repo

**Example:**
- **Project skill:** `prompt-library/philosophy-compliance-enforcer.md`
- **Generalized domain skill:** `domains/opinionated-apps/philosophy-enforcer.md`
- **Changes:** Replace "Prompt Library philosophy" with "documented project philosophy (configurable path)"

---

### Domain → Core Promotion

**Required:**
1. Skill has been used in 3+ projects across 2+ domains
2. Skill is fully configurable (no domain assumptions)
3. Skill provides value to ANY project (not just specific tech stack)

**Process:**
1. Move skill to `agent-skills/skills/core/`
2. Remove domain-specific assumptions
3. Add comprehensive configuration options
4. Document which project types benefit most
5. Submit PR to universal repo

**Example:**
- **Domain skill:** `domains/opinionated-apps/philosophy-enforcer.md`
- **Core skill:** `core/principle-enforcer.md`
- **Changes:** Remove "React" assumptions, add support for any project with documented principles

---

## Conflict Resolution Rules

### Skill Precedence Hierarchy

When a skill exists in multiple locations, agents use this precedence order:

1. **Project override** (`.agent-skills/skills/overrides/{skill}.md`) - **Highest priority**
2. **Project-specific** (`.agent-skills/skills/project/{skill}.md`)
3. **Domain skill** (`agent-skills/skills/domains/{domain}/{skill}.md`)
4. **Core skill** (`agent-skills/skills/core/{skill}.md`) - **Lowest priority**

**Example:**

If all four exist:
- `.agent-skills/skills/overrides/architecture-review.md` (used)
- `.agent-skills/skills/project/architecture-review.md` (ignored)
- `agent-skills/skills/domains/react-apps/architecture-review.md` (ignored)
- `agent-skills/skills/core/architecture-review.md` (ignored)

**Rationale:** Project-specific customization should always win.

### Override Best Practices

**Use overrides when:**
- You need project-specific customization of a universal skill
- You want to add project context to a domain skill
- You need stricter/looser rules than the universal version
- The base skill is 90% correct but needs minor adjustments

**Don't use overrides when:**
- The skill is fundamentally different (create new project skill instead)
- The override would break the handoff protocol (create new skill instead)
- You're duplicating more than 30% of the base skill (create new skill instead)

**Override Structure:**
```yaml
---
name: architecture-review
scope: override
base-skill: core/architecture-review
customizations:
  - "Add Prompt Library philosophy enforcement"
  - "Check for privacy tier violations"
---

# Architecture Review (Prompt Library Override)

This skill extends the core architecture-review with Prompt Library-specific checks.

## Base Skill Behavior
[Inherits from core/architecture-review.md]

## Project-Specific Additions
- Philosophy compliance (Zero-Click Capture, Neutrality)
- Privacy tier enforcement in all database queries
- State transition validation
```

---

## Performance Considerations

### Skill Map Size Limits

**Recommended limits:**
- Universal skills: 10-15 (only enable skills you actually use)
- Domain skills: 5-10
- Project skills: 5-15
- Total: <30 skills per project

**Why limits matter:**
- Agents load all skills in skill map (even if not invoked)
- More skills = more tokens = slower + more expensive
- Unused skills waste context
- Large skill maps make it harder to find the right skill

### Optimization Strategies

**1. Use skill chains instead of individual skills:**

Bad:
```yaml
universal-skills:
  - architecture-review
  - dependency-health-check
  - test-coverage-gap-finder
  - bundle-size-analyzer
  - api-boundary-validator
  - architectural-drift-detector
```

Good:
```yaml
universal-skills:
  - architecture-review  # Use this when needed
  
chains:
  full-audit:  # Use chain for comprehensive reviews
    - architecture-review
    - dependency-health-check
    - test-coverage-gap-finder
```

**Rationale:** Agent only loads skills in the invoked chain, not all skills in map.

---

**2. Create focused skill maps:**

Bad (one skill map for everything):
```yaml
universal-skills: [50 skills]
project-skills: [20 skills]
```

Good (multiple skill maps for different contexts):

`.agent-skills/skill-maps/development.yaml`:
```yaml
universal-skills:
  - dependency-health-check
  - test-coverage-gap-finder
```

`.agent-skills/skill-maps/pre-deployment.yaml`:
```yaml
universal-skills:
  - performance-budget-guardian
  - bundle-size-analyzer
```

**Usage:**
```
> Use skill map .agent-skills/skill-maps/development.yaml
> Assume dependency-health-check and analyze
```

**Rationale:** Context-specific skill maps reduce loaded skills.

---

**3. Lazy-load skills:**

If agent tooling supports it:
- Don't load skill definitions until skill is invoked
- Load on-demand from file system
- Cache loaded skills for session

**Current limitation:** Most agents don't support lazy loading yet.

---

## Anti-Patterns (What NOT to Do)

### ❌ Don't: Add project-specific skills to universal repo

**Bad:**
```
agent-skills/skills/core/prompt-library-philosophy-enforcer.md
```

**Why:** Other projects don't use Prompt Library's philosophy

**Good:**
```
prompt-library/.agent-skills/skills/project/philosophy-compliance-enforcer.md
```

---

### ❌ Don't: Generalize too early

**Bad:** After using a skill once, immediately promote to core

**Why:** You don't know if the pattern is actually reusable yet

**Good:** Use skill on current project for 2+ months, then evaluate

---

### ❌ Don't: Over-abstract

**Bad:** Make skill so general it's useless

**Example:**
```yaml
name: generic-validator
description: Validates anything against any rules
```

**Why:** Too abstract to be useful

**Good:** Keep domain-specific versions, promote only when clear pattern emerges

---

### ❌ Don't: Create bloated skill maps

**Bad:**
```yaml
universal-skills: [50 skills]
domain-skills: [30 skills]
project-skills: [20 skills]
```

**Why:** Agents load all skills, wasting tokens and context

**Good:** Keep total <30 skills, use chains for comprehensive workflows

---

## Maintenance Policy

### Review Cycle: Quarterly

**Questions to ask:**
1. Are any project-specific skills ready for promotion?
2. Are any domain skills used by 3+ projects (promote to core)?
3. Are any core skills unused (consider deprecation)?
4. Are any domain definitions outdated (e.g., "react-apps" now includes Next.js)?

### Deprecation Path

**If a skill is unused for 6+ months:**
1. Mark as `maturity: deprecated` in front matter
2. Add deprecation notice in skill description
3. Suggest alternative skills
4. After 3 more months, move to `agent-skills/archive/`

See `meta/promotion-criteria.md` for detailed deprecation process.

---

## Examples

### Promotion Example

**Project Skill:**
- `prompt-library/.agent-skills/skills/project/philosophy-compliance-enforcer.md`
- Enforces Prompt Library's specific philosophy rules

**After 2+ months of use, identify pattern:**
- Other opinionated apps (Obsidian plugins, VSCode extensions) also need philosophy enforcement

**Create Domain Skill:**
- `agent-skills/skills/domains/opinionated-apps/philosophy-enforcer.md`
- Generalizes to work with any project that has a philosophy document
- Configurable path to philosophy file

**After 3+ projects use it, promote to Core:**
- `agent-skills/skills/core/principle-enforcer.md`
- Works for any project with documented principles (not just "philosophy")
- Fully configurable

---

## Tracking

Use observability logs to track:
- Skill usage frequency
- Success/failure rates
- User feedback
- Promotion candidates

This data informs both promotion and retirement decisions.

See `meta/observability.md` for details.

