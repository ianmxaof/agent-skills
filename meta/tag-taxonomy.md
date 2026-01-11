# Tag Taxonomy

This document defines the stable tag taxonomy for the agent-skills system. Tags enable the skill-router to match user intents to appropriate skills.

## Status

**Current Status:** Pending validation

After validation through real routing tests, this taxonomy will be locked as a stable API. Changes will only be made via skill-gap-detector or effectiveness analysis.

## Tag Categories

Tags are organized into four categories:

| Category | Purpose | Examples |
|----------|---------|----------|
| **Surface** | What is being analyzed | `ui`, `api`, `database`, `architecture`, `state` |
| **Action** | What the skill does | `audit`, `validate`, `detect`, `analyze`, `test` |
| **Domain** | Technology area | `performance`, `security`, `ux`, `testing` |
| **Specific** | Unique identifiers | `adversarial`, `privacy`, `drift`, `coverage` |

## Naming Conventions

1. **Use kebab-case** - All tags use lowercase with hyphens (e.g., `failure-modes`, not `failureModes`)
2. **Be specific** - Prefer specific tags over generic ones
3. **Match user vocabulary** - Use terms users actually say
4. **4-6 tags optimal** - Too few = poor matching, too many = false positives

## Tag Guidelines

### Good Tag Practices

- **Specific over generic**: `adversarial` is better than `testing` for adversarial UI testing
- **Include synonyms**: If users might say "check" or "validate", include both concepts
- **Surface + Action + Domain**: Cover what, how, and where
- **Unique discriminators**: Add specific tags that distinguish this skill from similar ones

### Example: Good Tag Set

```yaml
tags:
  - ui              # Surface
  - ux              # Domain
  - adversarial     # Specific discriminator
  - failure-modes    # Specific discriminator
  - accessibility   # Domain
  - dark-patterns   # Specific discriminator
```

## Anti-Patterns

The following tag patterns should be avoided:

### ❌ Tags That Are Too Generic

**Bad examples:**
- `analysis` - Too broad, doesn't discriminate
- `general` - Meaningless
- `testing` - Too generic, many skills do testing

**Why:** Generic tags cause false positives and poor routing discrimination.

**Instead:** Use specific tags that describe what kind of analysis or testing (e.g., `adversarial`, `coverage`, `stress-test`).

### ❌ Tags That Encode Outcomes Instead of Scope

**Bad examples:**
- `improves-performance` - This is an outcome, not what the skill analyzes
- `fixes-bugs` - Outcome, not scope
- `reduces-bundle-size` - Outcome, not scope

**Why:** Tags should describe what the skill analyzes, not what it achieves. Outcomes change, scope doesn't.

**Instead:** Use scope tags (e.g., `performance`, `bundle`, `dependencies`) and let the skill's purpose section describe outcomes.

### ❌ Tags That Duplicate Skill Names

**Bad examples:**
- Skill: `adversarial-ui-tester`, Tags: `[adversarial, ui, tester]` - Redundant
- Skill: `bundle-size-analyzer`, Tags: `[bundle, size, analyzer]` - Redundant

**Why:** The skill name already conveys this information. Tags should add discriminators, not repeat the name.

**Instead:** Use tags that add context the name doesn't provide (e.g., `adversarial-ui-tester` might have `[ui, ux, adversarial, failure-modes, accessibility]` - the last three add value beyond the name).

## Stability Commitment

**Tags are now stable API.**

After validation and refinement, tags should only be changed via:
- `skill-gap-detector` proposals (when new skills reveal gaps)
- `skill-effectiveness-analyzer` recommendations (when routing patterns show issues)
- Explicit validation cycles (using `tests/VALIDATION_CHECKLIST.md`)

**Do not:**
- Change tags ad-hoc
- Add tags without removing others (keep 4-6 range)
- Rename tags without updating all affected skills
- Add tags "just in case"

## Current Tag Inventory

*This section will be populated after validation and refinement.*

After running routing validation tests and refining tags, document the final tag set here:

### Core Skills Tags
- [To be populated after validation]

### Project Skills Tags
- [To be populated after validation]

### Meta Skills Tags
- [To be populated after validation]

## Validation History

- **Initial tagging:** [Date] - All 22 skills tagged without validation
- **Validation run:** [Date] - [Number] intents tested
- **Refinement pass:** [Date] - Tags refined based on observations
- **Locked as stable:** [Date] - Taxonomy locked, reason: [Reason]

## Related Documents

- `TEMPLATE.md` - Tag guidelines for new skills
- `tests/routing-validation.md` - Test intents for validation
- `tests/routing-observations.md` - Observation template
- `tests/VALIDATION_CHECKLIST.md` - Validation process
- `skills/meta/skill-router.md` - How tags are used in routing

