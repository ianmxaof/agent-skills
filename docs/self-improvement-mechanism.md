# Self-Improvement Mechanism

This document explains how the agent-skills system improves over time without requiring explicit automation.

## Core Insight

The system improves through **natural selection**, not machine learning.

- Weak skills feel annoying → they get refined or retired
- Strong skills feel indispensable → they get used more, promoted
- Lessons accumulate across contexts → compressed experience compounds

This is **Darwinian**, not algorithmic — and that's intentional.

## Three Self-Improvement Loops

### Loop 1: Skills Get Better Through Reuse

```
Skill runs
    │
    v
Artifact produced
    │
    v
Cursor extracts lessons
    │
    v
Lessons influence future runs
    │
    v
Skill feels more/less useful
    │
    v
Skill refined or retired
```

Each time a skill runs:
- It produces structured output
- Cursor processes findings
- Lessons are extracted (if applicable)
- The system learns what works

**Key insight:** Repetition reveals quality. Skills that consistently produce actionable findings earn trust. Skills that produce noise become annoying.

### Loop 2: Lessons Accumulate Across Contexts

`Claude.md` (or equivalent) acts as **cross-project memory**.

```
Project A: adversarial-ui-tester finds accessibility gap
    │
    v
Lesson added: "Always check focus indicators on form buttons"
    │
    v
Project B: Lesson influences implementation decisions
    │
    v
Project C: Lesson prevents the issue from occurring
```

**Important:** Lessons that repeat across multiple integrations gain *weight* without explicit scoring.

You'll notice patterns:
- "We keep hitting this edge case..."
- "This warning is always relevant..."
- "This skill catches something important every time..."

That's signal. That's the system telling you what matters.

### Loop 3: Skill-Gap Detector as Evolution Hook

When the system fails to match intent or a skill proves inadequate:

```
skill-router fails to match
    │
    v
skill-gap-detector proposes new skill
    │
    v
Human reviews proposal
    │
    v
New skill created (or existing skill refined)
```

This prevents entropy while allowing growth:
- New skills must justify themselves
- Existing skills can be refined based on gaps
- The library evolves based on actual needs

## Why Automation is Deferred

You might think: "Why not automate skill scoring?"

**Current answer:** Premature optimization.

If you automated now, you would:
- Encode assumptions that haven't been validated
- Optimize for frequency, not value
- Risk reinforcing bad patterns
- Create complexity before understanding the system

**Right now:** Your judgment is the oracle.

The system is designed so **automation can be added later**, once patterns are obvious.

## What Natural Selection Looks Like

### Over Time, High-Value Skills Emerge

| Indicator | Meaning |
|-----------|---------|
| Skill runs frequently | It's trusted |
| Findings lead to action | It produces signal |
| Skill gets refined | It's worth improving |
| Skill gets promoted | It's universally useful |

### Low-Value Skills Fade

| Indicator | Meaning |
|-----------|---------|
| Skill rarely invoked | Not solving a real problem |
| Findings ignored | Produces noise |
| Skill not refined | Not worth the effort |
| Skill deprecated | Actively unhelpful |

### The Result

After sustained usage:
- **Fewer skills** — only the effective ones remain
- **Stronger skills** — refined through iteration
- **Used more often** — trusted patterns emerge
- **Backed by evidence** — accumulated lessons

## Column Effectiveness Signals

For columns specifically, track informally:

### Positive Signals

- Column consistently produces actionable findings
- Column artifacts influence Cursor plans
- Agent A/Agent B pairing feels efficient
- Compression ratio is healthy (e.g., 2:1 or 3:1)

### Negative Signals

- Column produces noise that Cursor ignores
- Column artifacts sit unprocessed
- Agent B struggles to compress (Agent A is already filtered)
- Same issues found every time (skill not learning)

### What To Do

| Signal | Action |
|--------|--------|
| Column works well | Keep using, consider promotion |
| Column produces noise | Try different Agent B mode |
| Column finds nothing | Check if skill fits target |
| Column always finds same thing | Target may be clean, or skill is too narrow |

## Future Automation Hooks

These can be added **later**, when patterns are obvious:

### Usage Tracking

- Count which skills/columns are invoked
- Track which artifacts lead to implementation
- Identify skills that produce unused findings

### Lesson Repetition

- Note lessons that appear across multiple projects
- Identify patterns that should become skills
- Track when lessons stop appearing (deprecated)

### Skill Merge/Retirement Suggestions

- Detect overlapping skills
- Suggest consolidation
- Propose retirement for unused skills

### Effectiveness Metrics

- Findings → implementation correlation
- Time from artifact to action
- False positive rate (findings that were wrong)

**Important:** All automation should **suggest**, not enforce. Human judgment remains the oracle.

## The Big Picture

You're not building:
- A prompt library
- An agent swarm
- An auto-AI system

You're building:

> **A long-lived cognitive toolchain that compounds judgment over time.**

The real asset isn't:
- The agents
- The skills
- The artifacts

It's the **compressed experience** encoded in skills and lessons.

## Practical Guidance

### For Daily Usage

1. Run skills/columns you trust
2. Process artifacts promptly
3. Extract lessons when you notice patterns
4. Refine skills when they produce noise

### For Weekly/Monthly Review

1. Which skills did you use most?
2. Which skills produced actionable findings?
3. Which skills felt like noise?
4. Any patterns that should become skills?

### For System Evolution

1. Promote project skills that prove universal
2. Retire skills that haven't been used in months
3. Merge overlapping skills
4. Add lessons that keep repeating

## Anti-Patterns

### ❌ Optimizing Too Early

Don't add scoring systems, dashboards, or automation before you understand what "good" looks like.

### ❌ Keeping Everything

Not every skill deserves to live. Retire the ones that don't produce value.

### ❌ Ignoring Friction

If a skill is annoying, that's signal. Either fix it or retire it.

### ❌ Over-Automating

Human judgment is the oracle. Automation should assist, not replace.

## Summary

| Principle | Implementation |
|-----------|----------------|
| Natural selection | Use reveals quality |
| Lessons compound | Claude.md as memory |
| Gaps drive evolution | skill-gap-detector proposes |
| Human remains oracle | Automation suggests only |
| Fewer, stronger skills | Darwinian outcome |

The system improves because you use it, not because it optimizes itself.

