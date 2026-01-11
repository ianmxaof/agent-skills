# Front Matter Update Summary

This document summarizes the front matter updates needed for all skills to support the three-tier architecture.

## Required Front Matter Fields

All skills need these new fields added to their YAML front matter:

```yaml
scope: core | domain | project
tier: 1 | 2 | 3 | meta
writes-code: false  # All current skills are analysis-only
modifies-files: false  # All current skills are analysis-only
handoff-protocol: standard-v1
promotion-candidate: false  # Set to true if ready for promotion
derived-from: project-name/skill-name  # Optional, tracks promotion path
domain: react-apps | cli-tools | etc  # Required if scope=domain
```

## Skills to Update

### Core Skills (Universal)

These skills should be moved to `skills/core/` and updated:

1. **dependency-health-check** (Tier 2)
   - Current: `skills/security/dependency-health-check.md`
   - New: `skills/core/dependency-health-check.md`
   - Scope: core, Tier: 2

2. **test-coverage-gap-finder** (Tier 3)
   - Current: `skills/testing/test-coverage-gap-finder.md`
   - New: `skills/core/test-coverage-gap-finder.md`
   - Scope: core, Tier: 3

3. **bundle-size-analyzer** (Tier 3)
   - Current: `skills/performance/bundle-size-analyzer.md`
   - New: `skills/core/bundle-size-analyzer.md`
   - Scope: core, Tier: 3

4. **api-boundary-validator** (Tier 3)
   - Current: `skills/api/api-boundary-validator.md`
   - New: `skills/core/api-boundary-validator.md`
   - Scope: core, Tier: 3

5. **architectural-drift-detector** (Tier 2)
   - Current: `skills/architecture/architectural-drift-detector.md`
   - New: `skills/core/architectural-drift-detector.md`
   - Scope: core, Tier: 2

6. **project-structure-analyzer** (Tier 3)
   - Current: `skills/analysis/project-structure-analyzer.md`
   - New: `skills/core/project-structure-analyzer.md`
   - Scope: core, Tier: 3

7. **architecture-review** (Tier 3)
   - Current: `skills/architecture/architecture-review.md`
   - New: `skills/core/architecture-review.md`
   - Scope: core, Tier: 3

8. **adversarial-ui-tester** (Tier 2)
   - Current: `skills/testing/adversarial-ui-tester.md`
   - New: `skills/core/adversarial-ui-tester.md`
   - Scope: core, Tier: 2

9. **failure-mode-simulator** (Tier 3)
   - Current: `skills/failure-modes/failure-mode-simulator.md`
   - New: `skills/core/failure-mode-simulator.md`
   - Scope: core, Tier: 3

10. **ux-copy-neutrality-checker** (Tier 3)
    - Current: `skills/ux/ux-copy-neutrality-checker.md`
    - New: `skills/core/ux-copy-neutrality-checker.md`
    - Scope: core, Tier: 3

### Project-Specific Skills (Prompt Library)

These skills should be moved to `.agent-skills/skills/project/` and updated:

1. **philosophy-compliance-enforcer** (Tier 1)
   - Current: `skills/philosophy/philosophy-compliance-enforcer.md`
   - New: `.agent-skills/skills/project/philosophy-compliance-enforcer.md`
   - Scope: project, Tier: 1, domain: prompt-library

2. **privacy-tier-auditor** (Tier 1)
   - Current: `skills/security/privacy-tier-auditor.md`
   - New: `.agent-skills/skills/project/privacy-tier-auditor.md`
   - Scope: project, Tier: 1, domain: prompt-library

3. **state-invariant-validator** (Tier 1)
   - Current: `skills/state/state-invariant-validator.md`
   - New: `.agent-skills/skills/project/state-invariant-validator.md`
   - Scope: project, Tier: 1, domain: prompt-library

4. **capture-surface-focus-auditor** (Tier 1)
   - Current: `skills/performance/capture-surface-focus-auditor.md`
   - New: `.agent-skills/skills/project/capture-surface-focus-auditor.md`
   - Scope: project, Tier: 1, domain: prompt-library

5. **performance-budget-guardian** (Tier 1)
   - Current: `skills/performance/performance-budget-guardian.md`
   - New: `.agent-skills/skills/project/performance-budget-guardian.md`
   - Scope: project, Tier: 1, domain: prompt-library

6. **database-migration-safety-checker** (Tier 2)
   - Current: `skills/database/database-migration-safety-checker.md`
   - New: `.agent-skills/skills/project/database-migration-safety-checker.md`
   - Scope: project, Tier: 2, domain: prompt-library

7. **rac-accuracy-evaluator** (Tier 2)
   - Current: `skills/rac/rac-accuracy-evaluator.md`
   - New: `.agent-skills/skills/project/rac-accuracy-evaluator.md`
   - Scope: project, Tier: 2, domain: prompt-library

8. **variant-tree-explosion-detector** (Tier 2)
   - Current: `skills/variants/variant-tree-explosion-detector.md`
   - New: `.agent-skills/skills/project/variant-tree-explosion-detector.md`
   - Scope: project, Tier: 2, domain: prompt-library

9. **toast-notification-spam-detector** (Tier 2)
   - Current: `skills/notifications/toast-notification-spam-detector.md`
   - New: `.agent-skills/skills/project/toast-notification-spam-detector.md`
   - Scope: project, Tier: 2, domain: prompt-library

### Meta Skills

These skills stay in `skills/meta/` and need front matter updates:

1. **skill-effectiveness-analyzer** (Meta)
   - Current: `skills/meta/skill-effectiveness-analyzer.md`
   - Already updated with boundaries
   - Scope: meta, Tier: meta

2. **skill-health-check** (Meta)
   - Current: `skills/meta/skill-health-check.md`
   - Scope: meta, Tier: meta

3. **handoff-quality-validator** (Meta)
   - Current: `skills/meta/handoff-quality-validator.md`
   - Scope: meta, Tier: meta

4. **skill-map-validator** (Meta)
   - New: `skills/meta/skill-map-validator.md`
   - Already created with complete front matter
   - Scope: meta, Tier: meta

## Update Template

For each skill, add this section after the front matter:

```markdown
## Scope and Classification

**Scope:** `core` | `domain` | `project`

**Tier:** `1` | `2` | `3` | `meta`

See `meta/skill-scope-policy.md` for detailed guidance on scope classification and promotion paths.
```

## Tier Classifications

- **Tier 1 (Existential Risk):** philosophy-compliance-enforcer, privacy-tier-auditor, performance-budget-guardian, state-invariant-validator, capture-surface-focus-auditor
- **Tier 2 (System Health):** database-migration-safety-checker, rac-accuracy-evaluator, variant-tree-explosion-detector, toast-notification-spam-detector, architectural-drift-detector, dependency-health-check, adversarial-ui-tester
- **Tier 3 (Long-term Quality):** failure-mode-simulator, ux-copy-neutrality-checker, bundle-size-analyzer, api-boundary-validator, test-coverage-gap-finder, project-structure-analyzer, architecture-review
- **Meta:** skill-effectiveness-analyzer, skill-health-check, handoff-quality-validator, skill-map-validator

## Default Values

For all skills:
- `writes-code: false` (all current skills are analysis-only)
- `modifies-files: false` (all current skills are analysis-only)
- `handoff-protocol: standard-v1`
- `promotion-candidate: false` (set to true if ready for promotion)

## Status

- ✅ TEMPLATE.md - Updated with new fields
- ✅ skill-effectiveness-analyzer.md - Updated with boundaries
- ✅ skill-map-validator.md - Created with complete front matter
- ✅ api-boundary-validator.md - Updated in original location
- ⏳ Remaining skills - Need front matter updates and moves

## Next Steps

1. Update front matter for all remaining skills
2. Move core skills to `skills/core/`
3. Move project-specific skills to `.agent-skills/skills/project/`
4. Create `.agent-skills/skill-map.yaml` for Prompt Library
5. Validate skill map with skill-map-validator

