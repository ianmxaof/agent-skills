# Agent Invocation Guide

This guide explains how agents use the skill map system to load and execute skills.

## How Agents Use Skill Maps

When you invoke a Warp agent with a skill:

```
> Assume architecture-review skill and analyze this codebase
```

**Agent execution flow:**

1. **Check for skill map:**
   - Look for `.agent-skills/skill-map.yaml` in project root
   - If found, load and parse skill map
   - If not found, fall back to scanning `agent-skills/skills/` directory

2. **Resolve skill location:**
   - Check if skill is in `universal-skills` list
   - If yes, load from `agent-skills/skills/core/{skill}.md`
   - Check if skill is in `domain-skills` list
   - If yes, load from `agent-skills/skills/domains/{domain}/{skill}.md`
   - Check if skill is in `project-skills` list
   - If yes, load from `.agent-skills/skills/project/{skill}.md`

3. **Check for override:**
   - If override exists in `skill-map.yaml` for this skill
   - Load override file from `.agent-skills/skills/overrides/{skill}.md`
   - Apply override customization to base skill

4. **Execute skill:**
   - Load skill definition
   - Execute per skill's behavioral rules
   - Produce handoff report per protocol

5. **Save handoff report:**
   - Save report with filename: `YYYY-MM-DD_{skill-name}_{target}.md`
   - Indicate readiness for Cursor implementation

## Fallback Behavior

**If no skill map exists:**

- Agent scans `agent-skills/skills/` directory
- Loads all skills found (slower, more token usage)
- Less precise skill selection
- No project-specific customization

**Recommendation:** Always create a skill map for better performance and project-specific customization.

## Invocation Examples

### Example 1: Invoking Universal Skill

```
> Assume dependency-health-check and analyze dependencies
```

**Agent reads:**
- `.agent-skills/skill-map.yaml` → finds `dependency-health-check` in `universal-skills` list
- Loads `agent-skills/skills/core/dependency-health-check.md`
- Executes skill with universal context

### Example 2: Invoking Project-Specific Skill

```
> Assume philosophy-compliance-enforcer and review this PR
```

**Agent reads:**
- `.agent-skills/skill-map.yaml` → finds `philosophy-compliance-enforcer` in `project-skills` list
- Loads `.agent-skills/skills/project/philosophy-compliance-enforcer.md`
- Executes skill with Prompt Library-specific context

### Example 3: Invoking Domain Skill

```
> Assume react-state-management-review and analyze state management
```

**Agent reads:**
- `.agent-skills/skill-map.yaml` → finds `react-apps/react-state-management-review` in `domain-skills` list
- Loads `agent-skills/skills/domains/react-apps/react-state-management-review.md`
- Executes skill with React-specific context

### Example 4: Invoking Skill Chain

```
> Run pre-implementation chain
```

**Agent reads:**
- `.agent-skills/skill-map.yaml` → finds `chains.pre-implementation`
- Executes skills in sequence:
  1. philosophy-compliance-enforcer
  2. privacy-tier-auditor
  3. state-invariant-validator
- Produces combined handoff report

### Example 5: Using Override

If skill map has:
```yaml
overrides:
  - skill: architecture-review
    override-file: .agent-skills/skills/overrides/architecture-review-custom.md
```

```
> Assume architecture-review and review architecture
```

**Agent reads:**
- Finds `architecture-review` in `universal-skills`
- Loads base skill: `agent-skills/skills/core/architecture-review.md`
- Finds override in skill map
- Loads override: `.agent-skills/skills/overrides/architecture-review-custom.md`
- Applies override customization
- Executes customized skill

## Skill Precedence

When a skill exists in multiple locations, agents use this precedence:

1. **Project override** (`.agent-skills/skills/overrides/{skill}.md`) - **Highest priority**
2. **Project-specific** (`.agent-skills/skills/project/{skill}.md`)
3. **Domain skill** (`agent-skills/skills/domains/{domain}/{skill}.md`)
4. **Core skill** (`agent-skills/skills/core/{skill}.md`) - **Lowest priority**

**Example:**

If all four exist for `architecture-review`:
- Override is used (even if project-specific version exists)
- Project-specific is ignored
- Domain and core versions are ignored

## Performance Considerations

### Skill Map Size

**Recommended limits:**
- Universal skills: 10-15
- Domain skills: 5-10
- Project skills: 5-15
- Total: <30 skills per project

**Why limits matter:**
- Agents load all skills in skill map (even if not invoked)
- More skills = more tokens = slower + more expensive
- Unused skills waste context

### Optimization Strategies

**1. Use skill chains:**

Instead of listing all skills individually:
```yaml
universal-skills:
  - architecture-review  # Use this when needed
  
chains:
  full-audit:  # Use chain for comprehensive reviews
    - architecture-review
    - dependency-health-check
    - test-coverage-gap-finder
```

Agent only loads skills in the invoked chain, not all skills in map.

**2. Create focused skill maps:**

Instead of one large skill map:
```yaml
# .agent-skills/skill-maps/development.yaml
universal-skills:
  - dependency-health-check
  - test-coverage-gap-finder

# .agent-skills/skill-maps/pre-deployment.yaml
universal-skills:
  - performance-budget-guardian
  - bundle-size-analyzer
```

Use context-specific skill maps to reduce loaded skills.

## Troubleshooting

### Skill Not Found

**Symptom:** Agent can't find skill

**Check:**
1. Skill name matches exactly (case-sensitive)
2. Skill is listed in skill-map.yaml
3. Skill file exists in expected location
4. Run skill-map-validator to identify issues

### Wrong Skill Version Used

**Symptom:** Agent uses wrong version of skill

**Check:**
1. Skill precedence (override > project > domain > core)
2. Override configuration in skill-map.yaml
3. Skill file locations

### Chain Execution Fails

**Symptom:** Skill chain doesn't execute

**Check:**
1. All skills in chain exist
2. No circular dependencies
3. Chain definition in skill-map.yaml is correct
4. Run skill-map-validator to detect issues

## Best Practices

1. **Always create a skill map** - Better performance and customization
2. **Keep skill maps focused** - Only enable skills you actually use
3. **Use chains for workflows** - Reduces loaded skills
4. **Validate skill maps** - Run skill-map-validator regularly
5. **Document overrides** - Explain why override is needed

## Artifact Processing (Cursor)

Cursor processes handoff artifacts produced by Warp agents. This section explains how.

### Important: Cursor is Pointed At, Not Auto-Scanning

**Cursor does NOT automatically scan for artifacts.** You must explicitly direct Cursor to process them.

**Why:** No brittle filesystem watching. This is a logical contract, not a filesystem watch.

### Standard Cursor Command

```
"Process any new artifacts in .agent-skills/artifacts/incoming/"
```

### Processing Workflow

1. **Direct Cursor to artifacts:**
   ```
   "Check .agent-skills/artifacts/incoming/ for new artifacts and process them"
   ```

2. **Cursor reads artifacts:**
   - Opens each file where `status: new` AND `intended-consumer: cursor`
   - Parses front matter and content

3. **Cursor integrates findings:**
   - Converts findings into implementation plan
   - Updates code/docs as specified
   - Follows recommendations in artifact

4. **Cursor updates artifact status:**
   - Changes `status: new` to `status: processed`
   - Moves artifact to `artifacts/processed/`

5. **Cursor extracts lessons (optional):**
   - Identifies generalizable patterns
   - Updates `CLAUDE.md` or lessons-learned
   - Links back to artifact for provenance

### Example Processing Session

```
User: "Process the latest adversarial-ui-tester artifact"

Cursor:
1. Reads .agent-skills/artifacts/incoming/adversarial-ui-tester-2026-01-07T19-42-00Z.md
2. Parses: 5 findings (2 critical, 2 high, 1 medium)
3. Plans: Add guardrails to checkout flow, fix accessibility issues
4. Implements: Updates CheckoutForm.tsx, adds aria labels
5. Moves artifact to processed/
6. Reports: "Processed artifact. 4/5 recommendations implemented. 1 deferred for discussion."
```

### What Cursor Should Do With Artifacts

| Artifact Type | Cursor Action |
|---------------|---------------|
| Analysis findings | Plan + implement fixes |
| Recommendations | Evaluate and integrate |
| Lessons learned | Update CLAUDE.md or rules |
| Skill gap proposals | Evaluate for skill creation |

### What Cursor Should NOT Do

- ❌ Automatically scan artifacts directory
- ❌ Process artifacts without being directed
- ❌ Assume all artifacts need immediate action
- ❌ Delete artifacts (move to processed instead)

### Artifact Lifecycle in Cursor

```
incoming/ (status: new)
    │
    │ "Process artifacts"
    v
Cursor reads + integrates
    │
    v
processed/ (status: processed)
    │
    │ After retention period
    v
archive/ (status: archived)
```

### Integration with Lessons Learned

When processing artifacts, Cursor should:

1. Check if findings reveal generalizable lessons
2. Apply lessons-learned-protocol.md criteria
3. Propose updates to CLAUDE.md or project rules
4. Link back to artifact in archive (for provenance)

See `protocols/lessons-learned-protocol.md` for full protocol.

### Integration with Skill Effectiveness

Resolution trace artifacts should be noted for skill-effectiveness-analyzer:

- Which skills are invoked most often
- Confidence scores over time
- Routing patterns and gaps

This feeds into continuous improvement of skill tags and definitions.

## Processing Column Artifacts

Cursor processes column artifacts **exactly the same** as single-skill artifacts. No special handling needed.

### Why This Works

By design:
- Column artifacts follow the same handoff protocol
- Column artifacts have the same front matter structure
- Column artifacts are just higher-quality single artifacts
- The `column:` field is informational, not behavioral

### Column Artifact Recognition

Column artifacts include additional front matter:

```yaml
---
skill: adversarial-ui-tester
status: new
column: ux-adversarial           # Indicates this came from a column
refinement-layer: generic        # How Agent B processed it
agent-a-coverage: 15 findings    # Raw count from exploration
agent-b-output: 6 findings       # Refined count
---
```

### Multi-Column Processing

When multiple columns run in parallel, their artifacts appear in `incoming/` with different `column:` values.

**Cursor behavior for multi-column intake:**

1. **Read all artifacts** in `incoming/`
2. **Parse front matter** to understand sources
3. **Synthesize across columns:**

| Pattern | Cursor Action |
|---------|---------------|
| Same issue found by multiple columns | Note convergence → higher confidence |
| Columns report conflicting findings | Note disagreement → flag for human |
| Unique findings per column | Process normally |

### Cross-Column Deduplication

**Rule:** Deduplication happens at Cursor synthesis, not within columns.

Each column has limited context. Only Cursor sees all artifacts.

When consolidating similar findings:
- Note the merge in the plan
- Don't silently drop findings
- Credit both source columns

### Example Multi-Column Intake

```
User: "Run the standard artifact intake and integration pass."

Cursor:
Found 4 artifacts in incoming/:
- adversarial-ui-tester (column: ux-adversarial) - 6 findings
- architecture-review (column: architecture) - 4 findings
- performance-budget-guardian (column: performance) - 3 findings
- failure-mode-simulator (column: correctness) - 5 findings

Synthesis:
- Convergence: Form validation issue found by UX + Correctness (high confidence)
- Conflict: Architecture vs Performance on context extraction (needs discussion)
- Unique: 8 findings found by single columns

Consolidated plan:
[prioritized action items]
```

### Standard Intake Command

The same command works for single-skill and column artifacts:

> "Run the standard artifact intake and integration pass."

See `docs/cursor-intake-protocol.md` for full intake protocol.

---

## See Also

- `templates/skill-map-template.yaml` - Skill map template
- `meta/skill-scope-policy.md` - Scope classification and precedence rules
- `skills/meta/skill-map-validator.md` - Validation skill
- `skills/meta/refinement-layer.md` - Column Agent B meta-skill
- `docs/migration-guide.md` - Migration instructions
- `docs/warp-integration-guide.md` - Warp agent guide
- `docs/column-pattern-guide.md` - Full column pattern documentation
- `docs/column-examples.md` - Worked column examples
- `docs/cursor-intake-protocol.md` - Cursor intake command
- `docs/self-improvement-mechanism.md` - How the system evolves
- `meta/artifact-policy.md` - Artifact lifecycle and handling
- `protocols/handoff-protocol.md` - Artifact content structure

