---
type: skill-definition
name: skill-gap-detector
category: meta
version: 1.0.0
maturity: draft
lifecycle: validated
estimated-cost: low
typical-runtime: 2-5min
complexity-level: simple
requires-deep-analysis: false
scope: meta
tier: meta
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
promotion-candidate: false
tags:
  - meta
  - gaps
  - proposals
  - evolution
prerequisites: []
execution-modes:
  - targeted
---

# Skill Gap Detector

## Purpose

Close the learning loop when the skill-router fails to find a match or when existing skills prove inadequate. This skill proposes new skills or refinements to existing skills, enabling the agent-skills system to evolve based on real usage.

## Scope and Classification

**Scope:** `meta` - Meta-skill for skill management

**Tier:** `meta` - Skill management (system evolution)

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## When to Invoke

### Automatic Invocation

- **Router confidence < 0.7** in strict mode
- skill-router explicitly delegates to this skill

### Manual Invocation

- "There should be a skill for this"
- "This skill doesn't cover what I need"
- "Propose a new skill for: <description>"
- After skill execution reveals inadequacy

### Post-Execution Invocation

- Skill output was insufficient for the task
- User identifies missing capabilities
- Recurring pattern not yet captured as a skill

## Behavioral Rules

### How the Model Should Reason

1. **Analyze the gap**
   - What intent was the user trying to fulfill?
   - Why didn't existing skills match?
   - What capability is missing?

2. **Check for near-matches**
   - Could an existing skill be enhanced?
   - Is this a scope/tag issue (skill exists but wasn't matched)?
   - Would a skill override solve this?

3. **Determine the right response**
   - New skill proposal
   - Enhancement to existing skill
   - Tag refinement suggestion
   - Skill override creation

### What It Must Avoid

- **Don't propose trivial skills** (one-time tasks don't need skills)
- **Don't duplicate existing capabilities** (check carefully first)
- **Don't propose overly broad skills** (scope should be focused)
- **Don't implement the skill** (only propose)

### What It Must Prioritize

- Reusability across future tasks
- Clear scope boundaries
- Integration with existing skill ecosystem
- Actionable proposals

## Analysis Process

### Step 1: Understand the Unfulfilled Intent

Extract from the failed routing or user feedback:
- What was the user trying to accomplish?
- What surface/target was involved?
- What outcome was expected?

### Step 2: Analyze Existing Skills

Check if the gap is actually:
- A **tagging issue**: Skill exists but tags don't match intent keywords
- A **scope issue**: Skill exists but in wrong scope (project vs core)
- A **coverage issue**: Skill exists but doesn't cover this use case
- A **true gap**: No skill addresses this need

### Step 3: Determine Response Type

| Situation | Response |
|-----------|----------|
| Skill exists, tags don't match | Propose tag additions |
| Skill exists, scope too narrow | Propose skill enhancement |
| Skill exists in core, needs project customization | Propose skill override |
| No skill covers this need | Propose new skill |
| Need is too specific/one-time | Decline to propose |

### Step 4: Generate Proposal

For new skills, include:
- **Name**: Following naming conventions
- **Purpose**: One-line description
- **Scope**: core, domain, or project
- **Suggested tags**: For intent matching
- **Key behaviors**: What the skill should do
- **Anti-patterns**: What it should avoid

## Output Contract

### For New Skill Proposals

```yaml
proposal:
  type: new-skill
  name: suggested-skill-name
  purpose: "One-line description of what it does"
  scope: core | domain | project
  domain: null | domain-name  # if scope is domain
  suggested-tags:
    - tag1
    - tag2
    - tag3
  key-behaviors:
    - "What it should do"
    - "Another behavior"
  anti-patterns:
    - "What it should NOT do"
  estimated-complexity: simple | moderate | complex
  template-link: agent-skills/TEMPLATE.md
```

### For Skill Enhancement Proposals

```yaml
proposal:
  type: enhancement
  target-skill: existing-skill-name
  enhancement-type: tags | scope | behaviors | coverage
  current-state: "What the skill does now"
  proposed-change: "What should be added/modified"
  rationale: "Why this enhancement is needed"
```

### For Tag Refinement Proposals

```yaml
proposal:
  type: tag-refinement
  target-skill: existing-skill-name
  current-tags: [existing, tags]
  proposed-tags: [existing, tags, new-tag1, new-tag2]
  rationale: "Why these tags should be added"
```

### For Decline (No Proposal)

```yaml
proposal:
  type: decline
  reason: "Why no skill is proposed"
  alternatives:
    - "Alternative approach 1"
    - "Alternative approach 2"
```

## Examples

### Example 1: True Gap - New Skill Needed

**Context:** Router failed with 0.35 confidence for "analyze GraphQL schema for breaking changes"

**Analysis:**
- No skill handles GraphQL specifically
- api-boundary-validator focuses on REST/external calls
- architectural-drift-detector doesn't cover schema evolution

**Proposal:**
```yaml
proposal:
  type: new-skill
  name: graphql-schema-validator
  purpose: "Detect breaking changes in GraphQL schema evolution"
  scope: domain
  domain: graphql-apis
  suggested-tags:
    - graphql
    - schema
    - breaking-changes
    - api
    - validation
  key-behaviors:
    - "Compare schema versions for breaking changes"
    - "Identify deprecated fields usage"
    - "Validate resolver compatibility"
  anti-patterns:
    - "Don't validate business logic"
    - "Don't generate schema documentation"
  estimated-complexity: moderate
  template-link: agent-skills/TEMPLATE.md
```

### Example 2: Tagging Issue

**Context:** Router failed for "check if our error messages are user-friendly" but ux-copy-neutrality-checker exists

**Analysis:**
- ux-copy-neutrality-checker handles UI copy
- But its tags are: ux, copy, language, neutrality
- Missing: errors, messages, user-friendly

**Proposal:**
```yaml
proposal:
  type: tag-refinement
  target-skill: ux-copy-neutrality-checker
  current-tags: [ux, copy, language, neutrality]
  proposed-tags: [ux, copy, language, neutrality, errors, messages, user-friendly]
  rationale: "Skill already analyzes UI text including error messages, but tags don't reflect this. Adding these tags will improve routing for error message analysis intents."
```

### Example 3: Decline - Too Specific

**Context:** User asks "make a skill for fixing the bug in handleSubmit on line 42"

**Analysis:**
- This is a one-time, highly specific task
- Not reusable
- Already covered by normal development workflow

**Proposal:**
```yaml
proposal:
  type: decline
  reason: "This is a specific bug fix, not a reusable pattern. Skills are for repeatable analysis and validation tasks."
  alternatives:
    - "Use Cursor directly for this bug fix"
    - "If submit handling bugs are recurring, consider a form-validation-auditor skill"
```

## Integration Points

- **skill-router**: Primary invoker when confidence < 0.7
- **TEMPLATE.md**: Reference for new skill creation
- **skill-map.yaml**: Check existing skills before proposing
- **meta/skill-scope-policy.md**: Guidance on scope decisions

## Exit Conditions

### Success

- Proposal generated (new skill, enhancement, tag refinement, or decline)
- Proposal follows output contract format
- Next steps are clear

### Failure

- Cannot determine user intent
- Insufficient context to make proposal
- Ask for clarification

## Handoff Notes

After generating a proposal:

1. **For new skills**: User should create skill using TEMPLATE.md
2. **For enhancements**: User should update the target skill
3. **For tag refinements**: User should add tags to skill front matter
4. **For declines**: User should follow suggested alternatives

This skill does NOT implement changes. It only proposes.

