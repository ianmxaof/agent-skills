# Column Runner Template (Reference Scaffolding)

This is a **reference pattern**, not a hard protocol. Think of it like a Makefile example, not a build system.

Use this template as guidance when running 2-agent columns manually.

---

## What This Is

A column is a two-agent workflow:
1. **Agent A** (exploration) → writes raw findings to `artifacts/incoming/`
2. **Agent B** (refinement) → reads raw findings, writes refined output to `artifacts/refined/`

This template provides example prompts for both stages.

## What This Is NOT

- Not an enforced protocol
- Not automated orchestration
- Not a rigid system

Refinement will come after running 10-20 real columns. For now: manual invocation, deterministic outputs, predictable artifacts.

When running columns feels *boring*, then consider automation.

---

## Column Configuration

Before running a column, define:

| Parameter | Value |
|-----------|-------|
| **Column Name** | `{column-name}` (e.g., `ux-adversarial`, `security-audit`) |
| **Skill** | `{skill-name}` (e.g., `adversarial-ui-tester`) |
| **Target** | `{target-description}` (e.g., "the checkout flow") |
| **Refinement Mode** | `generic` | `domain-aware` | `effectiveness` |

---

## Stage 1: Agent A (Exploration)

### Prompt Template

Copy and invoke in a new agent session:

```markdown
# Agent A Instructions (Exploration Layer)

You are **Agent A (Exploration Layer)** in the {column-name} column.

## Your Role

You are the **exploration** layer. Your job is to maximize coverage and surface everything potentially relevant.

## Skill to Load

**Skill:** `{skill-name}`

Load and execute this skill in **exploratory posture**.

## Operating Posture

- **Maximize coverage** — Surface edge cases, risks, ambiguities, and failure modes
- **Allow mess** — Comprehensiveness > polish
- **Do NOT self-censor findings** — If you see something, report it
- **Do NOT optimize for brevity** — More detail is better at this stage
- **Do NOT decide priority** — Light severity labels only (critical/high/medium/low)
- **Do NOT deduplicate** — Report everything, even if it seems redundant

## Artifact Emission Rules

Write your findings to:

```
.agent-skills/artifacts/incoming/{skill-name}-raw-findings-{ISO-timestamp}.md
```

### Front Matter (Required)

```yaml
---
artifact-type: raw-findings
generated-by: agent-a
skill: {skill-name}
status: unrefined
confidence: exploratory
intended-consumer: agent-b
timestamp: {ISO-8601}
finding-count: {number}
target: {target-description}
---
```

## Artifact Boundary Rules (STRICT)

- You MUST write findings to `.agent-skills/artifacts/incoming/`
- You MUST NOT write to `refined/`, `processed/`, or `archive/`
- You MUST use artifact-type: raw-findings
- You MUST set confidence: exploratory

## Target

Analyze: **{target-description}**

## Exit Condition

Done when:
1. Comprehensive raw findings produced
2. Artifact written to `artifacts/incoming/`
3. Path and finding count printed
```

### Expected Output

After Agent A completes:
- Artifact created at `.agent-skills/artifacts/incoming/{skill-name}-raw-findings-{timestamp}.md`
- Terminal shows artifact path and finding count
- Status: success

### Verification

Confirm the artifact exists:
```bash
ls .agent-skills/artifacts/incoming/
```

---

## Stage 2: Agent B (Refinement)

### Prerequisite

Agent A must have completed and written an artifact to `incoming/`.

Note the artifact filename from Agent A's output.

### Prompt Template

Copy and invoke in a new agent session:

```markdown
# Agent B Instructions (Refinement Layer)

You are **Agent B (Refinement Layer)** in the {column-name} column.

## Your Role

You are a **filter**, not a second thinker. Compress Agent A's raw output into one Cursor-ready artifact.

## Input

Load raw findings from:

```
@.agent-skills/artifacts/incoming/{agent-a-artifact-filename}.md
```

### Input Validation

Before processing, verify:
- artifact-type: raw-findings ✓
- confidence: exploratory ✓
- generated-by: agent-a ✓

If validation fails, stop and report the mismatch.

## Refinement Mode

**Mode:** `{generic | domain-aware | effectiveness}`

## Your Job (Required Actions)

1. **Deduplicate** — Merge findings that describe the same underlying issue
2. **Rank** — Assign severity: critical, high, medium, low (in that order)
3. **Clarify** — Rewrite vague findings for actionability
4. **Validate** — Check against handoff-protocol.md structure
5. **Package** — Produce one structured artifact

## Rules (STRICT)

- Do NOT add new findings unless strictly implied by Agent A's output
- Do NOT explore new areas
- Do NOT speculate
- You are a filter, not a thinker

## Output

Write to `.agent-skills/artifacts/refined/{skill-name}-{ISO-timestamp}.md`:

```yaml
---
artifact-type: refined-findings
generated-by: agent-b
skill: {skill-name}
scope: {core | domain | project | meta}
status: new
confidence: validated
timestamp: {ISO-8601}
intended-consumer: cursor
priority: {highest-severity}
column: {column-name}
refinement-layer: {generic | domain-aware | effectiveness}
agent-a-coverage: {original-finding-count} findings
agent-b-output: {refined-finding-count} findings
source-artifact: .agent-skills/artifacts/incoming/{agent-a-artifact-filename}.md
---

## Summary
- (≤5 bullets)

## Detailed Findings
...

## Recommendations
...

## Handoff Notes for Cursor
...
```

## Exit Condition

Done when:
- Single artifact written to `artifacts/refined/`
- All required sections present
- Finding count reflects compression
- Source artifact path recorded
```

### Expected Output

After Agent B completes:
- Artifact created at `.agent-skills/artifacts/refined/{skill-name}-{timestamp}.md`
- Compression achieved (fewer findings than Agent A)
- Ready for Cursor consumption

### Verification

Confirm the artifact exists:
```bash
ls .agent-skills/artifacts/refined/
```

---

## Complete Example: UX/Adversarial Column

### Configuration

| Parameter | Value |
|-----------|-------|
| Column Name | `ux-adversarial` |
| Skill | `adversarial-ui-tester` |
| Target | "the checkout flow" |
| Refinement Mode | `generic` |

### Stage 1: Agent A

Invoke with:
```
Skill: adversarial-ui-tester
Target: the checkout flow
Output: .agent-skills/artifacts/incoming/adversarial-ui-tester-raw-findings-2026-01-10T20-00-00Z.md
```

Wait for completion. Confirm artifact exists.

### Stage 2: Agent B

Invoke with:
```
Input: @.agent-skills/artifacts/incoming/adversarial-ui-tester-raw-findings-2026-01-10T20-00-00Z.md
Mode: generic
Output: .agent-skills/artifacts/refined/adversarial-ui-tester-2026-01-10T20-30-00Z.md
```

Wait for completion. Column done.

---

## Troubleshooting

### Agent A didn't write an artifact

Check:
- Did you include the Artifact Emission Rules section?
- Did you specify the correct output path?
- Did Agent A encounter an error?

Resolution: Re-run Agent A with the full template.

### Agent B can't find the artifact

Check:
- Is the filename correct?
- Did you use the `@` reference syntax?
- Does the file exist in `incoming/`?

Resolution: List the directory contents and verify the filename.

### Agent B didn't compress findings

Check:
- Is Agent B adding new findings? (Should not)
- Is Agent B just copying? (Should dedupe/rank)

Resolution: Remind Agent B of its role: "You are a filter, not a thinker."

---

## Notes

- This is **scaffolding** — a reference for manual operation
- Run 10-20 columns before considering automation
- When execution feels **boring and predictable**, you're ready to automate
- The system should "disappear" into workflow before you add complexity

## See Also

- `templates/agent-a-instruction-template.md` - Full Agent A template
- `templates/agent-b-instruction-template.md` - Full Agent B template
- `templates/artifact-types.md` - Artifact type definitions
- `templates/artifact-structure/README.md` - Directory structure

