# Promotion Criteria

## Overview

This document defines when lessons learned, ad-hoc prompts, or experimental approaches become formal agent skills in this repository.

## Promotion to Skill

### Criteria

A lesson or pattern should become a formal skill when it meets **all** of the following:

1. **Reusability**
   - Used successfully 3+ times across different projects
   - Applies to multiple codebases or contexts
   - Not project-specific

2. **Clear Success Metrics**
   - Has measurable outcomes
   - Can be validated objectively
   - Success/failure is unambiguous

3. **Structured Process**
   - Has defined steps or methodology
   - Can be executed consistently
   - Not dependent on specific context or knowledge

4. **Documentation**
   - Can be documented clearly
   - Has clear purpose and scope
   - Includes examples and anti-patterns

5. **Value Proposition**
   - Provides clear value
   - Saves time or improves outcomes
   - Worth the token cost

### Promotion Process

1. **Draft Skill**
   - Create skill file using `TEMPLATE.md`
   - Mark as `maturity: draft`
   - Document in skill's purpose section: "Promoted from lesson learned on [date]"

2. **Validation**
   - Use skill in 3+ real scenarios
   - Collect feedback and refine
   - Update based on learnings

3. **Promote to Validated**
   - After successful validation, update `maturity: validated`
   - Add to appropriate skill category
   - Update `SKILL-MAP.mmd` and `SKILL-SELECTOR.md`

4. **Harden**
   - After extended use (6+ months), consider `maturity: hardened`
   - Hardened skills are stable and well-tested
   - Rarely need updates

## Skill Retirement Criteria

Skills should be deprecated when they meet **any** of the following:

1. **Low Usage**
   - Used < 3 times in 6 months (tracked via observability)
   - No active users or interest
   - Superseded by better alternatives

2. **Superseded**
   - Better skill exists that covers the same need
   - New approach is clearly superior
   - Old skill is redundant

3. **Obsolete Technology**
   - Underlying tools/frameworks no longer relevant
   - Technology stack deprecated
   - No longer applicable to modern codebases

4. **Maintenance Burden**
   - Maintenance cost exceeds value
   - Requires constant updates
   - Better to start fresh

5. **Poor Outcomes**
   - Consistently produces poor results
   - High failure rate
   - Users report negative experiences

### Deprecation Process

1. **Mark as Deprecated**
   - Update skill front matter: `maturity: deprecated`
   - Add deprecation warning at top of skill file
   - Include migration path to replacement (if exists)

2. **Grace Period (3 months)**
   - Skill remains in original location
   - Warning visible to users
   - Usage tracked for final decision

3. **Move to Deprecated (after 3 months)**
   - Move to `skills/deprecated/` directory
   - Update all skill chains that reference it
   - Update compatibility matrix

4. **Remove (after 6 months)**
   - If no usage in 6 months, remove entirely
   - Archive in git history
   - Update documentation to remove references

### Deprecation Warning Template

```markdown
> **⚠️ DEPRECATED**: This skill is deprecated as of [date].
> 
> **Reason**: [Low usage / Superseded by X / Obsolete technology]
> 
> **Migration**: Use [replacement skill] instead.
> 
> **Removal Date**: [6 months from deprecation]
```

## Examples

### Promotion Example

**Lesson Learned:**
"I always check for circular dependencies when reviewing architecture"

**Becomes Skill:**
- `architecture-review` includes circular dependency detection
- Or separate `circular-dependency-detector` if it's a distinct, reusable process

### Retirement Example

**Skill:** `legacy-framework-migrator` (for deprecated framework X)

**Retirement Reason:** Framework X no longer used, all projects migrated

**Process:**
1. Mark deprecated: 2024-01-01
2. Move to deprecated/: 2024-04-01
3. Remove: 2024-07-01

## Tracking

Use observability logs to track:
- Skill usage frequency
- Success/failure rates
- User feedback

This data informs both promotion and retirement decisions.

