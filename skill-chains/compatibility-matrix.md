# Skill Compatibility Matrix

## Overview

This matrix documents which skill versions work together, which can run in parallel, and data dependencies between skills.

## Compatibility Legend

- ✅ **Compatible**: Skills work well together
- ❌ **Incompatible**: Skills conflict or are redundant
- ⚠️ **Parallel OK**: Can run in parallel (no data dependency)
- 🔗 **Sequential Required**: Must run in sequence (data dependency)
- 📋 **Recommended**: Recommended combination

## Skill Compatibility Table

| Skill A | Skill B | Compatible? | Execution | Notes |
|---------|---------|-------------|------------|-------|
| project-structure-analyzer v1.x | architecture-review v1.x | ✅ Sequential Required | Sequential | Architecture review needs codebase map |
| project-structure-analyzer v1.x | dependency-health-check v1.x | ⚠️ Parallel OK | Parallel | No data dependency |
| project-structure-analyzer v1.x | adversarial-ui-tester v1.x | ⚠️ Parallel OK | Parallel | Different analysis domains |
| architecture-review v1.x | architecture-review v1.x | ❌ Incompatible | N/A | Redundant - same skill twice |
| architecture-review v1.x | code-quality-audit v1.x | ✅ Compatible | Parallel or Sequential | Different focus areas |
| dependency-health-check v1.x | adversarial-ui-tester v1.x | ⚠️ Parallel OK | Parallel | No data dependency |
| dependency-health-check v1.x | code-quality-audit v1.x | ⚠️ Parallel OK | Parallel | Different analysis domains |
| handoff-quality-validator v1.x | Any skill v1.x | ✅ Sequential Required | Sequential | Validates after skill execution |
| skill-health-check v1.x | Any skill v1.x | ✅ Compatible | Independent | Validates skill definition, not execution |

## Recommended Skill Chains

### Full Codebase Audit

**Chain:** `full-codebase-audit-v1`

1. project-structure-analyzer (full-scan)
2. architecture-review (full-scan) - depends on #1
3. dependency-health-check (full-scan) - can run in parallel with #2
4. handoff-quality-validator - validates all reports

**Execution:** Sequential for #1→#2, parallel for #2 and #3, sequential for #4

### Security & Quality Check

**Chain:** `security-quality-v1`

1. dependency-health-check (full-scan)
2. code-quality-audit (full-scan) - can run in parallel with #1
3. handoff-quality-validator - validates reports

**Execution:** Parallel for #1 and #2, sequential for #3

### UI & UX Review

**Chain:** `ui-ux-review-v1`

1. adversarial-ui-tester (full-scan)
2. handoff-quality-validator - validates report

**Execution:** Sequential

## Version Compatibility

### Breaking Changes

When a skill has a breaking change (major version bump):

- **v1.x → v2.x**: May break compatibility with skill chains
- Check this matrix for updated compatibility
- Update skill chains that use the skill

### Non-Breaking Changes

- **v1.0.0 → v1.1.0**: Backward compatible
- **v1.0.0 → v1.0.1**: Backward compatible
- Existing skill chains continue to work

## Data Dependencies

### Prerequisite Skills

Some skills require output from others:

- **architecture-review** requires: project-structure-analyzer
- **handoff-quality-validator** requires: Any skill that produces handoff report

### File Dependencies

Some skills require specific files:

- **dependency-health-check** requires: package.json (or equivalent)
- **project-structure-analyzer** requires: Project files (any)

## Parallel Execution Rules

Skills can run in parallel when:

1. **No data dependency**: Neither skill needs the other's output
2. **Different domains**: Skills analyze different aspects
3. **Independent analysis**: Results don't conflict

Examples of parallel-safe combinations:
- dependency-health-check + adversarial-ui-tester
- code-quality-audit + dependency-health-check
- project-structure-analyzer + dependency-health-check (if structure analyzer doesn't need dependency info)

## Sequential Execution Rules

Skills must run sequentially when:

1. **Data dependency**: One skill needs the other's output
2. **Prerequisite**: Skill explicitly lists another as prerequisite
3. **Validation**: Validator skills must run after the skill being validated

Examples of sequential requirements:
- project-structure-analyzer → architecture-review
- Any skill → handoff-quality-validator

## Conflict Resolution

When skills provide contradictory advice:

1. **Check rule-precedence.md**: Security > Architecture > Performance > Code Quality > Documentation
2. **Context matters**: Some conflicts may be valid tradeoffs
3. **Document conflicts**: Flag for human review if cannot resolve automatically

## Updating This Matrix

When adding new skills or updating versions:

1. **Test compatibility**: Run skills together to verify
2. **Document results**: Add to this matrix
3. **Update skill chains**: Update affected chains
4. **Version lock**: Update skill chain YAML files with new versions

## Examples

### Example 1: Compatible Sequential

```
project-structure-analyzer → architecture-review
```
✅ Compatible, Sequential Required

### Example 2: Compatible Parallel

```
dependency-health-check || adversarial-ui-tester
```
⚠️ Parallel OK (no data dependency)

### Example 3: Incompatible

```
architecture-review → architecture-review
```
❌ Incompatible (redundant)

