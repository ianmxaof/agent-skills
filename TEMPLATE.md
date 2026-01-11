---
type: skill-definition
name: skill-name
category: category-name
version: 1.0.0
maturity: draft
lifecycle: experimental | validated | preferred | default | legacy | deprecated
estimated-cost: low
typical-runtime: 2-5min
complexity-level: simple
requires-deep-analysis: false
scope: core | domain | project | meta
domain: react-apps | cli-tools | etc
derived-from: project-name/skill-name
promotion-candidate: true | false
tier: 1 | 2 | 3 | meta
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
artifact-type: raw-findings | refined-findings | implementation-plan
tags:
  - category-tag      # e.g., testing, performance, security
  - surface-tag       # e.g., ui, api, database, architecture
  - action-tag        # e.g., audit, validate, detect, analyze
  - domain-tag        # e.g., react, node, typescript (if applicable)
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

## Scope and Classification

**Scope:** `core` | `domain` | `project` | `meta`

- **`core`**: Universal skill that works on any project (language-agnostic where possible)
- **`domain`**: Technology-specific skill (e.g., React apps, CLI tools)
- **`project`**: Project-specific skill (only relevant to this project)
- **`meta`**: Governance skill that operates on other skills or the skill system itself

**Tier:** `1` | `2` | `3` | `meta`

- **Tier 1**: Existential risk (philosophy, privacy, performance, state invariants)
- **Tier 2**: System health (migrations, accuracy, drift detection)
- **Tier 3**: Long-term quality (testing, documentation, architecture)
- **Meta**: Skill management (effectiveness analysis, health checks, routing)

**Type:** `skill-definition` | `changelog` | `readme`

- **`skill-definition`**: A skill file that can be executed
- **`changelog`**: Change log document (not a skill)
- **`readme`**: Documentation file (not a skill)

Use the `type` field to distinguish skill definitions from other documents in the skills directory.

**Promotion Status:**

- `promotion-candidate: true` - Skill is ready to be promoted to next layer
- `promotion-candidate: false` - Skill should remain in current layer
- `derived-from` - Tracks promotion path (e.g., "prompt-library/philosophy-compliance-enforcer")

**Lifecycle Stage:**

Skills progress through lifecycle stages based on real-world performance:

| Stage | Meaning | Router Weight |
|-------|---------|---------------|
| `experimental` | New, untested | 0.7x (deprioritized) |
| `validated` | Proven to work | 1.0x (baseline) |
| `preferred` | Strong track record | 1.1x (boosted) |
| `default` | First choice for domain | 1.2x (highest) |
| `legacy` | Superseded but functional | 0.5x (deprioritized) |
| `deprecated` | Scheduled for removal | 0.1x (warn) |

New skills should start as `experimental`. See `meta/skill-lifecycle.md` for promotion/demotion criteria.

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## Tags (for Intent Resolution)

Tags enable the skill-router to match user intents to skills. Choose tags carefully:

**Tag Categories:**

| Category | Purpose | Examples |
|----------|---------|----------|
| **Surface** | What is being analyzed | ui, api, database, architecture, state |
| **Action** | What the skill does | audit, validate, detect, analyze, test |
| **Domain** | Technology area | performance, security, ux, testing |
| **Specific** | Unique identifiers | adversarial, privacy, drift, coverage |

**Tag Guidelines:**

1. **Be specific** - "adversarial" is better than "testing" for UI adversarial testing
2. **Include synonyms** - If users might say "check" or "validate", include both concepts
3. **4-6 tags optimal** - Too few = poor matching, too many = false positives
4. **Match user vocabulary** - Use terms users actually say, not internal jargon

**Example Tag Sets:**

```yaml
# Good: Specific and varied
tags:
  - ui
  - ux
  - adversarial
  - failure-modes
  - accessibility
  - dark-patterns

# Bad: Too generic
tags:
  - testing
  - analysis
```

See `skills/meta/skill-router.md` for how tags are used in intent resolution.

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

Skills support execution modes to control analysis scope. The standard set is:

- **full-scan**: Comprehensive analysis of entire target
- **incremental**: Analysis of changes only
- **targeted**: Focused analysis of specific area

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

### Meta Skill Execution Modes (scope: meta only)

Skills with `scope: meta` may define additional execution modes beyond the standard set:

| Mode | Purpose | Example Use |
|------|---------|-------------|
| `change-analysis` | Analyze impact of changes to skills | Detecting amplification |
| `assessment` | Evaluate health/readiness | Health assessment |
| `intentless` | Route without explicit user intent | Skill routing |

Meta skills should document their custom modes in the Execution Mode Implementation section. Validators should accept custom modes for `scope: meta` skills.

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

### Artifact Type (Pipeline Integration)

When skills produce artifacts for the pipeline, specify the artifact type:

- **`raw-findings`**: Unrefined exploration output (Agent A → `incoming/`)
- **`refined-findings`**: Validated, compressed output (Agent B → `refined/`)
- **`implementation-plan`**: Action records (Cursor → `processed/`)

See `templates/artifact-types.md` for full artifact type documentation.

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

