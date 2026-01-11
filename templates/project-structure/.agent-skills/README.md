# Project-Specific Agent Skills

This directory contains agent skills specific to this project.

## Structure

- **`skills/project/`** - Project-specific skills that are not intended for reuse
- **`skills/overrides/`** - Project-specific customizations of universal or domain skills
- **`skill-map.yaml`** - Declares which skills are available for this project

## Usage

When invoking agent skills, agents will:
1. Read `skill-map.yaml` to determine available skills
2. Load skills from appropriate locations (core, domain, or project)
3. Apply overrides if specified
4. Execute skills and produce handoff reports

## Adding New Project-Specific Skills

1. Create skill file in `skills/project/` using `TEMPLATE.md` from agent-skills repo
2. Add skill name to `project-skills` list in `skill-map.yaml`
3. Set `scope: project` in skill front matter
4. Document the skill's purpose and when to use it

## Customizing Universal Skills

If you need to customize a universal skill for this project:

1. Create override file in `skills/overrides/`
2. Reference base skill in front matter: `base-skill: core/skill-name`
3. Add override entry to `skill-map.yaml`:
   ```yaml
   overrides:
     - skill: skill-name
       override-file: .agent-skills/skills/overrides/skill-name-custom.md
       reason: "Brief explanation of customization"
   ```

See `meta/skill-scope-policy.md` for override best practices.

## Skill Chains

Define common workflows in `skill-map.yaml`:

```yaml
chains:
  pre-implementation:
    - skill-1
    - skill-2
    - skill-3
```

Invoke chains:
```
> Run pre-implementation chain
```

## Validation

Validate your skill map:
```
> Assume skill-map-validator and validate this project's skill map
```

This checks for:
- Missing skill files
- Broken references
- Circular dependencies in chains
- Incomplete front matter

