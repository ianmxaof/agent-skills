# Lessons Learned Protocol

This protocol defines how lessons learned are ingested into the system, preventing CLAUDE.md from becoming a junk drawer while preserving valuable insights.

## What Qualifies as a Lesson

A lesson learned should be added when it meets **all** of the following criteria:

1. **Generalizable Pattern**
   - Not a one-time workaround or project-specific hack
   - Applies to similar situations in the future
   - Can be expressed as a conditional pattern: "When X, avoid Y because Z"

2. **Actionable Insight**
   - Provides clear guidance for future decisions
   - Helps prevent mistakes or improve outcomes
   - Not just a description of what happened

3. **Narrowest Applicable Scope**
   - Generalize to the narrowest scope that still applies
   - Avoid absolute language ("never", "always") unless truly universal
   - Phrase as conditional patterns, not universal rules

4. **Validated Through Experience**
   - Based on actual experience, not speculation
   - Has been observed or tested in practice
   - Not a theoretical concern

## Required Structure

### Format

Lessons should follow this pattern:

```markdown
### [Category Name]
- **Pattern:** When [condition X], avoid [action Y] because [reason Z]
- **Scope:** [narrowest applicable scope - e.g., "React textarea components", "Dexie migrations"]
- **Example:** [Brief example if helpful]
```

### Conditional Patterns

**Good (conditional):**
```markdown
- When using `visibility: hidden` on parent containers for ghost-text suggestions, avoid it because it hides children as well. Use `color: transparent` for prefix text instead.
```

**Bad (absolute):**
```markdown
- Never use `visibility: hidden` on parent containers.
```

**Why:** The lesson applies specifically to ghost-text suggestions, not all cases.

### Scope Specification

**Good (narrow scope):**
```markdown
- **Scope:** React textarea components with ghost text overlays
- **Pattern:** When implementing ghost text overlays, account for textarea `scrollTop` and `scrollLeft` using `transform: translate(-scrollLeft, -scrollTop)` to keep overlay aligned with scrolled text.
```

**Bad (too broad):**
```markdown
- Always account for scroll position in overlays.
```

**Why:** This is too general and may not apply to all overlay scenarios.

## Where to Write

### Location

Lessons learned are written in the **Lessons Learned** section of `CLAUDE.md` in the project root.

### Organization

Organize lessons by category:

```markdown
## Lessons Learned

### Completion System
- [Lesson 1]
- [Lesson 2]

### State Management
- [Lesson 3]

### Performance
- [Lesson 4]
```

## When NOT to Add

**Do NOT add lessons for:**

1. **Temporary Workarounds**
   - One-time fixes that will be replaced
   - Hacks that are documented elsewhere
   - Workarounds that are project-specific

2. **Project-Specific Details**
   - File paths specific to this project
   - Configuration values
   - Project-specific business logic

3. **Theoretical Concerns**
   - "Might be a problem" without evidence
   - Speculation about future issues
   - Unvalidated assumptions

4. **Obvious or Trivial**
   - Things that are already well-documented
   - Common knowledge in the domain
   - Self-evident patterns

5. **Too Specific**
   - Lessons that only apply to one exact scenario
   - Edge cases that are unlikely to recur
   - Bugs that are already fixed

## Quality Gates

### Maximum Lessons Per Cycle

**Limit: 5 lessons per agent cycle**

**Rationale:**
- Prevents documentation bloat
- Forces prioritization of most valuable insights
- Keeps lessons focused and actionable

**If you have more than 5 lessons:**
- Prioritize by impact and reusability
- Combine related lessons into patterns
- Defer less critical lessons to next cycle

### Review Process

**Before adding a lesson:**

1. **Check if lesson already exists**
   - Search CLAUDE.md for similar patterns
   - Avoid duplicates or near-duplicates

2. **Validate generalizability**
   - Can this be expressed as a conditional pattern?
   - Does it apply beyond this specific case?
   - Is the scope appropriately narrow?

3. **Check promotion criteria**
   - Should this become a skill instead? (see `meta/promotion-criteria.md`)
   - Is it reusable enough to be a skill?
   - Does it have clear success metrics?

## Promotion Path: Lesson → Skill

### When a Lesson Should Become a Skill

A lesson should be promoted to a skill when it meets **all** of the following:

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

1. **Create skill file** using `TEMPLATE.md`
2. **Mark as `maturity: draft`**
3. **Document in skill's purpose section:** "Promoted from lesson learned on [date]"
4. **Use skill in 3+ real scenarios**
5. **Promote to `maturity: validated`** after successful validation
6. **Remove lesson from CLAUDE.md** (or mark as "now a skill")

See `meta/promotion-criteria.md` for detailed promotion process.

## Examples

### Good Lesson

```markdown
### Completion System
- **Pattern:** When implementing semantic completion matches, return **suffixes** (not full phrases) when the phrase starts with the user's recent input.
- **Scope:** Semantic completion systems with phrase matching
- **Example:** If user typed "hello" and match is "hello world", return " world" not "hello world"
```

**Why this is good:**
- Conditional pattern (when X, do Y)
- Narrow scope (semantic completion systems)
- Actionable (clear guidance)
- Generalizable (applies to similar systems)

### Bad Lesson

```markdown
### Completion System
- Always return suffixes for completions.
```

**Why this is bad:**
- Too absolute ("always")
- Too broad (all completion systems)
- Not conditional
- Missing context

### Lesson That Should Become a Skill

```markdown
### State Management
- **Pattern:** When reviewing state transitions, validate against state machine diagram to ensure no invalid transitions (e.g., no `shipped → exploring` reversals).
```

**Why this should become a skill:**
- Has clear process (validate against diagram)
- Reusable across projects with state machines
- Has measurable outcome (invalid transitions found)
- Can be structured as a skill (`state-invariant-validator`)

## Maintenance

### Periodic Review

**Quarterly review of lessons:**

1. **Check for duplicates**
   - Merge similar lessons
   - Remove redundant entries

2. **Evaluate promotion candidates**
   - Identify lessons that should become skills
   - Promote if criteria are met

3. **Remove obsolete lessons**
   - Lessons that are no longer relevant
   - Lessons that have been superseded
   - Lessons that are now common knowledge

4. **Update scope if needed**
   - Narrow scope if too broad
   - Expand scope if too narrow (rare)

### Archiving

**Archive lessons that:**
- Have been promoted to skills
- Are no longer relevant
- Have been superseded by better patterns

**Archive format:**
```markdown
### [Archived] Category Name
- [Original lesson]
- **Archived:** [Date] - [Reason: promoted to skill / superseded / obsolete]
```

## Integration with Other Systems

### Cursor Rules

Reference existing `.cursor/rules/lessons-learned.mdc` for:
- Formatting guidelines
- Scope generalization rules
- Conditional pattern requirements

### Skill Promotion

Link to `meta/promotion-criteria.md` for:
- When lessons become skills
- Promotion process
- Skill creation guidelines

### Skill Scope Policy

Reference `meta/skill-scope-policy.md` for:
- When skills belong in core vs domain vs project
- Promotion paths between layers
- Governance rules

