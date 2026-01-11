# Migration Guide: Moving to Three-Tier Architecture

This guide helps you migrate existing projects from the old agent-skills structure to the new three-tier architecture (core/domain/project-specific).

## Overview

The new architecture separates:
- **Core skills** (universal) → `agent-skills/skills/core/`
- **Domain skills** (technology-specific) → `agent-skills/skills/domains/{domain}/`
- **Project skills** (project-specific) → `.agent-skills/skills/project/`

## Migration Scenarios

### Scenario 1: agent-skills is a Copy (Not Submodule)

**Current state:**
- `prompt-library/agent-skills/` is a full copy
- Project-specific skills are mixed with universal skills

**Migration steps:**

1. **Create project-specific directory:**
   ```bash
   mkdir -p .agent-skills/skills/project
   mkdir -p .agent-skills/skills/overrides
   ```

2. **Identify project-specific skills:**
   - Review skills in `agent-skills/skills/`
   - Identify which are Prompt Library-specific
   - Examples: `philosophy-compliance-enforcer`, `privacy-tier-auditor`

3. **Move project-specific skills:**
   ```bash
   mv agent-skills/skills/philosophy/philosophy-compliance-enforcer.md \
      .agent-skills/skills/project/philosophy-compliance-enforcer.md
   mv agent-skills/skills/security/privacy-tier-auditor.md \
      .agent-skills/skills/project/privacy-tier-auditor.md
   # ... repeat for all project-specific skills
   ```

4. **Create skill-map.yaml:**
   ```bash
   cp agent-skills/templates/skill-map-template.yaml .agent-skills/skill-map.yaml
   ```

5. **Edit skill-map.yaml:**
   - Set project name and type
   - List universal skills you use
   - List project-specific skills
   - Configure skill chains

6. **Update agent-skills to latest:**
   - Pull latest from universal repo
   - Or re-copy if using copy method

7. **Test skill invocation:**
   ```
   > Assume philosophy-compliance-enforcer and review this PR
   ```

**Rollback plan:**
- Restore old structure from git
- Remove `.agent-skills/` directory
- Fix any broken references

---

### Scenario 2: agent-skills is a Git Submodule

**Current state:**
- `prompt-library/agent-skills/` is a git submodule
- Project-specific skills are in submodule (wrong location)

**Migration steps:**

1. **Create project-specific directory:**
   ```bash
   mkdir -p .agent-skills/skills/project
   mkdir -p .agent-skills/skills/overrides
   ```

2. **Copy project-specific skills OUT of submodule:**
   ```bash
   cp agent-skills/skills/philosophy/philosophy-compliance-enforcer.md \
      .agent-skills/skills/project/philosophy-compliance-enforcer.md
   # ... repeat for all project-specific skills
   ```

3. **Remove project-specific skills from submodule:**
   ```bash
   cd agent-skills
   git rm skills/philosophy/philosophy-compliance-enforcer.md
   git rm skills/security/privacy-tier-auditor.md
   # ... repeat for all project-specific skills
   git commit -m "Remove Prompt Library-specific skills (moved to project)"
   git push
   cd ..
   ```

4. **Update submodule to latest:**
   ```bash
   git submodule update --remote agent-skills
   ```

5. **Create skill-map.yaml:**
   ```bash
   cp agent-skills/templates/skill-map-template.yaml .agent-skills/skill-map.yaml
   ```

6. **Edit skill-map.yaml:**
   - Configure for your project
   - List universal and project skills

7. **Test skill invocation:**
   ```
   > Assume skill-map-validator and validate this project's skill map
   ```

**Rollback plan:**
- Revert submodule to previous commit
- Remove `.agent-skills/` directory
- Restore project-specific skills to submodule (if needed)

---

### Scenario 3: Starting Fresh (Recommended)

**If possible, start with clean setup:**

1. **Remove existing agent-skills:**
   ```bash
   rm -rf agent-skills/
   ```

2. **Clone universal repo as submodule:**
   ```bash
   git submodule add https://github.com/your-org/agent-skills.git agent-skills
   ```

3. **Create project-specific structure:**
   ```bash
   mkdir -p .agent-skills/skills/project
   mkdir -p .agent-skills/skills/overrides
   ```

4. **Copy skill-map template:**
   ```bash
   cp agent-skills/templates/skill-map-template.yaml .agent-skills/skill-map.yaml
   ```

5. **Create project-specific skills:**
   - Use `agent-skills/TEMPLATE.md` as starting point
   - Create skills in `.agent-skills/skills/project/`
   - Set `scope: project` in front matter

6. **Configure skill-map.yaml:**
   - Set project name and type
   - Enable universal skills you need
   - List project-specific skills
   - Configure chains

7. **Validate skill map:**
   ```
   > Assume skill-map-validator and validate this project's skill map
   ```

**This is cleanest approach** but requires recreating project-specific skills.

---

## Common Issues and Solutions

### Issue: Skill Not Found

**Symptom:** Agent can't find skill referenced in skill-map.yaml

**Solution:**
1. Run skill-map-validator to identify broken references
2. Check skill file exists in expected location
3. Verify skill name matches exactly (case-sensitive)
4. Check if skill was moved to core/ directory

### Issue: Override Not Working

**Symptom:** Override file exists but agent uses base skill

**Solution:**
1. Verify override entry in skill-map.yaml
2. Check override file path is correct
3. Validate override front matter has `base-skill` field
4. Ensure override file is in `.agent-skills/skills/overrides/`

### Issue: Circular Dependency in Chain

**Symptom:** Skill chain causes infinite loop

**Solution:**
1. Run skill-map-validator to detect circular dependencies
2. Review chain definition in skill-map.yaml
3. Remove circular reference
4. Test chain execution

### Issue: Missing Front Matter Fields

**Symptom:** Skills missing scope, tier, or other required fields

**Solution:**
1. Update skill front matter with required fields
2. See `TEMPLATE.md` for required fields
3. Use skill-map-validator to identify missing fields

---

## Testing After Migration

### 1. Validate Skill Map

```
> Assume skill-map-validator and validate this project's skill map
```

Should report no errors, minimal warnings.

### 2. Test Skill Invocation

```
> Assume [project-skill-name] and analyze [target]
```

Should successfully load and execute project-specific skill.

### 3. Test Universal Skill

```
> Assume dependency-health-check and analyze dependencies
```

Should successfully load and execute universal skill.

### 4. Test Skill Chain

```
> Run pre-implementation chain
```

Should execute all skills in chain successfully.

---

## Post-Migration Checklist

- [ ] Project-specific skills moved to `.agent-skills/skills/project/`
- [ ] Skill-map.yaml created and configured
- [ ] All skill front matter updated with scope/tier fields
- [ ] Skill map validated (no errors)
- [ ] Skills tested (invocation works)
- [ ] Chains tested (execution works)
- [ ] Documentation updated (if needed)
- [ ] Team notified of new structure

---

## Need Help?

- See `meta/skill-scope-policy.md` for scope classification guidance
- See `TEMPLATE.md` for skill creation template
- See `docs/agent-invocation-guide.md` for usage examples
- Run `skill-map-validator` to identify issues

