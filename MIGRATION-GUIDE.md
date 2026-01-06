# Migration Guide

## Overview

This guide documents procedures for refactoring skills, renaming files, deprecating skills, changing handoff formats, and handling emergencies.

## Refactoring Skills

### When to Refactor

- Skill structure needs improvement
- Adding new required sections
- Changing YAML front matter schema
- Improving clarity or organization

### Refactoring Process

1. **Create Backup**
   ```bash
   git checkout -b refactor/skill-name
   cp skills/category/skill-name.md skills/category/skill-name.md.backup
   ```

2. **Update Skill**
   - Make changes to skill file
   - Ensure all required sections remain
   - Update version in front matter

3. **Update Dependencies**
   - Check `skill-chains/compatibility-matrix.md`
   - Update any skill chains using this skill
   - Update profiles that reference it

4. **Validate**
   - Run `skill-health-check` on updated skill
   - Test skill execution
   - Verify handoff reports still meet protocol

5. **Update Documentation**
   - Update `SKILL-MAP.mmd` if relationships changed
   - Update `SKILL-SELECTOR.md` if use cases changed
   - Update CHANGELOG.md if skill has one

6. **Commit**
   ```bash
   git add skills/category/skill-name.md
   git commit -m "refactor: update skill-name structure and schema"
   ```

## Renaming Skills

### Process

1. **Create New File**
   ```bash
   git mv skills/category/old-name.md skills/category/new-name.md
   ```

2. **Update Skill Content**
   - Update `name:` in YAML front matter
   - Update all internal references to skill name
   - Update purpose/description if needed

3. **Update All References**
   - Search codebase for old name
   - Update skill chains
   - Update compatibility matrix
   - Update profiles
   - Update SKILL-SELECTOR.md
   - Update SKILL-MAP.mmd

4. **Update Prerequisites**
   - Check if other skills reference this one
   - Update their prerequisites sections

5. **Commit**
   ```bash
   git commit -m "rename: old-name -> new-name"
   ```

## Deprecating Skills

See `meta/promotion-criteria.md` for full deprecation process.

### Quick Reference

1. Mark as deprecated in front matter
2. Add deprecation warning to skill file
3. 3-month grace period in original location
4. Move to `skills/deprecated/` after 3 months
5. Remove after 6 months if unused

## Changing Handoff Format

### Major Format Changes

If the handoff protocol structure changes significantly:

1. **Version the Protocol**
   - Update `protocols/handoff-protocol.md` with version
   - Document migration path from old to new format

2. **Update Skills**
   - Update all skills to use new format
   - Or support both formats during transition

3. **Update Validator**
   - Update `handoff-quality-validator` to check new format
   - Support both formats during transition

4. **Communicate**
   - Document breaking changes
   - Provide migration examples
   - Update all documentation

### Minor Format Changes

For small improvements (adding optional fields, clarifying structure):

1. Update protocol document
2. Update template
3. Skills can adopt gradually (backward compatible)

## Emergency Rollback

### When to Rollback

- Skill update breaks production workflows
- Handoff reports become invalid
- Critical bug discovered in skill logic
- Breaking change affects multiple projects

### Rollback Process

1. **Immediate Action**
   ```bash
   # Find last known-good commit
   git log --oneline skills/category/skill-name.md
   
   # Revert to that commit
   git checkout <commit-hash> -- skills/category/skill-name.md
   
   # Commit the rollback
   git commit -m "rollback: revert skill-name to vX.X.X (reason: [brief reason])"
   ```

2. **Document Incident**
   - Add incident report to skill's CHANGELOG.md (if exists)
   - Document:
     - What broke
     - Why it broke
     - How it was fixed
     - Prevention measures

3. **Prevent Regression**
   - Add test case to `tests/` directory
   - Update skill to prevent the issue
   - Run `skill-health-check` to validate

4. **Communicate**
   - Update all skill chains using this skill
   - Notify users if skill is widely used
   - Update compatibility matrix

5. **Fix and Redeploy**
   - Create fix in separate branch
   - Test thoroughly
   - Merge fix after validation

### Rollback Checklist

- [ ] Identify last known-good version
- [ ] Revert skill file
- [ ] Test rollback works
- [ ] Document incident
- [ ] Update skill chains
- [ ] Add prevention test
- [ ] Create fix branch
- [ ] Validate fix
- [ ] Redeploy

## Version Compatibility

### Breaking Changes

When making breaking changes:

1. **Major Version Bump**
   - Update version in front matter (1.0.0 → 2.0.0)
   - Document breaking changes in CHANGELOG

2. **Update Compatibility Matrix**
   - Mark incompatible versions
   - Update skill chains that use this skill

3. **Migration Path**
   - Provide clear migration instructions
   - Support both versions during transition if possible

### Non-Breaking Changes

For additions and improvements:

1. **Minor/Patch Version Bump**
   - 1.0.0 → 1.1.0 (new features)
   - 1.0.0 → 1.0.1 (bug fixes)

2. **Backward Compatible**
   - Old skill chains still work
   - New features are optional

## Moving Skills Between Categories

### Process

1. **Move File**
   ```bash
   git mv skills/old-category/skill-name.md skills/new-category/skill-name.md
   ```

2. **Update Category**
   - Update `category:` in YAML front matter
   - Update any category-specific references

3. **Update References**
   - Update SKILL-MAP.mmd
   - Update SKILL-SELECTOR.md
   - Update profiles

4. **Commit**
   ```bash
   git commit -m "move: skill-name from old-category to new-category"
   ```

## Best Practices

1. **Always Test**
   - Test changes before committing
   - Run skill-health-check
   - Validate handoff reports

2. **Document Changes**
   - Update CHANGELOG.md
   - Document breaking changes
   - Provide migration examples

3. **Update Dependencies**
   - Check skill chains
   - Update compatibility matrix
   - Update all references

4. **Communicate**
   - Document changes clearly
   - Provide migration paths
   - Update all relevant documentation

5. **Version Control**
   - Use git for all changes
   - Create branches for major changes
   - Tag releases if applicable

## Common Scenarios

### Scenario 1: Adding New Required Field

**Change:** Add `complexity-level` to all skills

**Process:**
1. Update TEMPLATE.md
2. Update all existing skills (can be gradual)
3. Update skill-health-check to validate new field
4. Document in migration guide

### Scenario 2: Renaming Execution Mode

**Change:** `full-scan` → `full-analysis`

**Process:**
1. Update TEMPLATE.md
2. Update all skills using old name
3. Update skill chains
4. Update documentation

### Scenario 3: Splitting Skill

**Change:** Split large skill into two focused skills

**Process:**
1. Create new skill files
2. Update original skill to reference new ones
3. Or deprecate original and create new
4. Update all references
5. Update skill chains

