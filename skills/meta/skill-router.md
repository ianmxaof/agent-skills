---
name: skill-router
category: meta
version: 1.0.0
maturity: draft
estimated-cost: low
typical-runtime: 1-2min
complexity-level: moderate
requires-deep-analysis: false
scope: meta
tier: meta
writes-code: false
modifies-files: false
handoff-protocol: standard-v1
tags:
  - meta
  - routing
  - intent
  - resolution
prerequisites:
  - file: .agent-skills/skill-map.yaml
    reason: "Authoritative source of available skills for this project"
execution-modes:
  - full-scan
---

# Skill Router

## Purpose

Translate a high-level user intent into the correct executable agent skill defined in the agent-skills system, without inventing roles or duplicating work. This is the **default Warp entrypoint** for intent-based skill resolution.

## Scope and Classification

**Scope:** `meta` - Meta-skill for skill management

**Tier:** `meta` - Skill management (intent resolution and routing)

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.

## Two Invocation Modes

### Mode A — Direct Skill Invocation (Deterministic)

User explicitly names a skill:

```
"Assume the adversarial-ui-tester skill and analyze the checkout flow"
```

**Behavior:**
1. Verify skill exists in skill-map.yaml
2. Load and execute exactly as specified
3. No intent resolution needed

### Mode B — Intent-Based Resolution (This Skill)

User describes what they want:

```
"Find UX weaknesses and adversarial failure modes in this UI"
```

**Behavior:**
1. Invoke this skill-router
2. Resolve intent to appropriate skill
3. Delegate to skill executor

## Normalized Command

**Standard invocation:**
```
"Resolve and execute the appropriate skill for: <intent>"
```

**With mode modifier:**
```
"Resolve and execute (assistive mode) the appropriate skill for: <intent>"
```

## Router Mode Flag

```yaml
mode: strict | assistive
```

### strict (default)
- Confidence < 0.7 → STOP immediately
- Report ambiguity to user
- Suggest top 2 candidate skills with scores
- Do NOT execute
- Optionally invoke skill-gap-detector

### assistive
- Confidence < 0.7 → Suggest top candidates + ask confirmation
- Execute only after user confirms
- Useful for exploration and discovery

**Why modes exist:** Lets you intentionally loosen guardrails for exploration without changing code or skill definitions.

## Resolution Algorithm (Strict Order)

Execute these steps in order. Do not skip or reorder.

### Step 1: Load Skill Map

```
Read .agent-skills/skill-map.yaml
```

This file is **authoritative**. Only skills listed here are eligible for resolution.

### Step 2: Check for Exact Name Match

If the user's intent contains an exact skill name:
- Verify skill is in skill-map.yaml
- If found: confidence = 1.0, proceed to Step 5
- If not found: report "Skill not available in this project"

### Step 3: Extract Intent Signals

Parse the user's intent to extract:
- **Keywords**: nouns and verbs (e.g., "UI", "adversarial", "testing", "coverage")
- **Target surface**: what is being analyzed (ui, api, database, architecture, etc.)
- **Desired outcome**: what the user wants (audit, validate, detect, analyze, test)

### Step 4: Match and Score Candidates

For each skill in skill-map.yaml:

1. **Tag overlap score** (0.0 - 0.5)
   - Count matching tags between intent keywords and skill tags
   - Normalize by total possible matches

2. **Purpose alignment score** (0.0 - 0.3)
   - Compare intent with skill's purpose section
   - Higher score for semantic alignment

3. **Scope precedence bonus** (0.0 - 0.2)
   - Project-specific skills: +0.2
   - Domain skills: +0.1
   - Core skills: +0.0

**Base confidence = tag_score + purpose_score + scope_bonus**

### Step 4b: Apply Lifecycle Weighting

If `meta/skill-trust-scores.yaml` exists, apply lifecycle modifiers:

| Lifecycle Stage | Weight Modifier |
|-----------------|-----------------|
| `default` | 1.2x |
| `preferred` | 1.1x |
| `validated` | 1.0x |
| `experimental` | 0.7x |
| `legacy` | 0.5x |
| `deprecated` | 0.1x (emit warning) |

Additionally, apply trust score modifier:

```
lifecycle_weight = stage_weight * (0.5 + 0.5 * trust_score)
```

**Final confidence = base_confidence * lifecycle_weight**

**Example:**
- Base confidence: 0.75
- Lifecycle: `preferred` (1.1x)
- Trust score: 0.85
- Lifecycle weight: 1.1 * (0.5 + 0.425) = 1.0175
- Final confidence: 0.75 * 1.0175 = 0.763

**Warnings:**
- If selected skill is `legacy`: Include deprecation notice in trace
- If selected skill is `deprecated`: Emit warning and suggest replacement
- If selected skill is `experimental`: Note that skill is untested

Rank all candidates by final confidence score.

### Step 5: Apply Confidence Threshold

**If highest confidence >= 0.7:**
- Select the top-scoring skill
- Emit resolution trace
- Proceed to execution

**If highest confidence < 0.7:**

In **strict mode** (default):
- STOP immediately
- Report: "Could not resolve intent with sufficient confidence"
- Show top 2 candidates with scores
- Suggest: "Please clarify or name a specific skill"
- Optionally invoke skill-gap-detector

In **assistive mode**:
- Show top 2 candidates with scores
- Ask: "Did you mean one of these? Please confirm or clarify."
- Wait for user confirmation before executing

**Note on Confidence Scores:**

Confidence scores are comparative, not probabilistic. They represent relative match quality among available skills, not absolute probability of correctness. Thresholds may be tuned after observing real routing behavior. A score of 0.7 means "better match than 70% of alternatives," not "70% chance of being correct."

### Step 6: Emit Resolution Trace

Every successful routing decision MUST emit this decision receipt:

```yaml
resolution:
  selected-skill: <skill-name>
  confidence: <0.0-1.0>
  mode: strict | assistive
  lifecycle:
    stage: <experimental|validated|preferred|default|legacy|deprecated>
    trust_score: <0.0-1.0>
    warning: <null|"experimental"|"legacy"|"deprecated">
  top-candidates:
    - skill: <skill-name>
      score: <0.0-1.0>
      lifecycle: <stage>
    - skill: <skill-name>
      score: <0.0-1.0>
      lifecycle: <stage>
  match-signals:
    - tags: [<matched-tags>]
    - surface: "<identified-target>"
    - outcome: "<identified-action>"
```

**Why resolution trace matters:**
- Lets you tune tags later based on actual routing behavior
- Helps debug why a skill was chosen (or not)
- Feeds directly into skill-effectiveness-analyzer
- This is a **decision receipt**, not verbose logging

### Step 7: Delegate Execution

After resolution:
1. Explicitly declare: "Resolved intent to `{skill}` (scope: {scope}, confidence: {score})"
2. Load the selected skill definition
3. Execute skill exactly as specified in its behavioral rules
4. Skill emits structured artifact per handoff-protocol.md

## Failure Conditions

### Never Invent Roles

If no skill matches with >= 0.7 confidence:
- **NEVER** invent a new role or behavior
- **NEVER** combine multiple skills without explicit instruction
- **NEVER** guess at what the user meant

Failure must be **cheap and visible**, not clever.

### When to Invoke skill-gap-detector

Invoke skill-gap-detector when:
- Router confidence < 0.7 in strict mode
- User explicitly says "there should be a skill for this"
- Skill execution reveals the skill is inadequate

## Inputs

1. **User intent** (natural language)
2. **`.agent-skills/skill-map.yaml`** (authoritative skill list)
3. **Skill definitions** (for tag and purpose matching)
4. **Mode flag** (strict or assistive, default: strict)

## Output

This skill does NOT produce analysis output of its own.

**Output is:**
- Resolution trace (always)
- Delegation to selected skill (on success)
- Ambiguity report (on failure)

## Examples

### Example 1: High-Confidence Match

**Intent:** "Find adversarial UX failure modes in the checkout flow"

**Resolution:**
```yaml
resolution:
  selected-skill: adversarial-ui-tester
  confidence: 0.85
  mode: strict
  top-candidates:
    - skill: adversarial-ui-tester
      score: 0.85
    - skill: ux-copy-neutrality-checker
      score: 0.52
  match-signals:
    - tags: ["ui", "adversarial", "ux", "failure-modes"]
    - surface: "checkout flow"
    - outcome: "find/detect"
```

**Action:** Execute adversarial-ui-tester

### Example 2: Low-Confidence (Strict Mode)

**Intent:** "Check if the code is good"

**Resolution:**
```yaml
resolution:
  selected-skill: null
  confidence: 0.45
  mode: strict
  top-candidates:
    - skill: architecture-review
      score: 0.45
    - skill: test-coverage-gap-finder
      score: 0.42
  match-signals:
    - tags: ["quality"]
    - surface: "code"
    - outcome: "check"
```

**Action:** STOP. Report ambiguity:
> "Could not resolve intent with sufficient confidence (0.45).
> Top candidates:
> - architecture-review (0.45)
> - test-coverage-gap-finder (0.42)
> Please clarify what aspect of 'good' you want to check, or name a specific skill."

### Example 3: Exact Name Match

**Intent:** "Run privacy-tier-auditor on the recall service"

**Resolution:**
```yaml
resolution:
  selected-skill: privacy-tier-auditor
  confidence: 1.0
  mode: strict
  top-candidates:
    - skill: privacy-tier-auditor
      score: 1.0
  match-signals:
    - tags: ["exact-match"]
    - surface: "recall service"
    - outcome: "audit"
```

**Action:** Execute privacy-tier-auditor (exact name detected)

## Anti-Patterns

### ❌ DON'T: Silent Best-Guess Routing

**Bad:** Picking the highest-scoring skill even at 0.4 confidence

**Good:** Stopping and asking for clarification

### ❌ DON'T: Inventing Composite Skills

**Bad:** "I'll combine adversarial-ui-tester and ux-copy-neutrality-checker for a comprehensive review"

**Good:** "Intent matches multiple skills. Please specify which aspect to focus on, or run them separately."

### ❌ DON'T: Verbose Explanations in Resolution

**Bad:** Multi-paragraph explanation of why a skill was chosen

**Good:** Structured resolution trace + one-line declaration

## Integration Points

- **skill-map.yaml**: Authoritative source of available skills
- **skill-gap-detector**: Invoked when router fails to find a match
- **skill-effectiveness-analyzer**: Consumes resolution traces for improvement
- **handoff-protocol.md**: Executed skills emit artifacts per this protocol
- **meta/skill-trust-scores.yaml**: Lifecycle stage and trust scores for weighting
- **meta/skill-lifecycle.md**: Lifecycle stage definitions and transitions
- **meta/taste-profile.yaml**: (Optional) Skill biases for routing preferences

## Exit Conditions

### Success
- Skill resolved with >= 0.7 confidence
- Resolution trace emitted
- Skill execution delegated

### Failure (Recoverable)
- Confidence < 0.7
- User asked to clarify
- skill-gap-detector optionally invoked

### Failure (Unrecoverable)
- skill-map.yaml not found
- No skills defined in project

