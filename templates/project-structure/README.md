# Project-Specific Skills Setup

This directory contains a template for setting up project-specific agent skills.

## Quick Start

1. **Copy this structure to your project root:**
   ```bash
   cp -r templates/project-structure/.agent-skills .agent-skills
   ```

2. **Copy the skill map template:**
   ```bash
   cp templates/skill-map-template.yaml .agent-skills/skill-map.yaml
   ```

3. **Edit `.agent-skills/skill-map.yaml`:**
   - Set your project name and type
   - Enable relevant universal skills
   - Add project-specific skills to `project-skills` list
   - Configure skill chains for common workflows

4. **Create your project-specific skills:**
   - Add skills to `.agent-skills/skills/project/`
   - Use `TEMPLATE.md` from the agent-skills repo as a starting point

5. **Validate your skill map:**
   ```
   > Assume skill-map-validator and validate this project's skill map
   ```

## Directory Structure

```
.agent-skills/
├── skills/
│   ├── project/       # Project-specific skills go here
│   └── overrides/     # Project-specific overrides of universal skills
├── skill-map.yaml     # Which skills apply to this project
└── README.md          # How this project uses agent-skills
```

## When to Use Project-Specific Skills

Use project-specific skills when:
- The skill encodes project-specific invariants or patterns
- The skill references project-specific files or configurations
- The skill is not applicable to other projects
- You want to experiment with a skill before promoting it

See `meta/skill-scope-policy.md` for detailed guidance on when skills belong in each layer.

## Promotion Path

When a project-specific skill proves valuable and reusable:
1. Identify the generalizable pattern
2. Promote to domain skill (if technology-specific) or core skill (if universal)
3. Update skill map to use the promoted version
4. Keep project-specific version as override if needed

See `meta/skill-scope-policy.md` for promotion criteria and process.

