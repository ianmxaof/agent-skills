---
name: protocol-author
description: Scaffold, revise, and validate AI protocols that conform to the user's Global Protocol Standard v2.4. Use when the user asks to create a new protocol, update or version-bump an existing protocol, or audit a protocol for compliance with the standard.
---

# Protocol Author

Protocols are named operating procedures the user invokes by trigger phrase or /command. Every protocol must conform to the Global Protocol Standard v2.4 (in User Rules and `.cursor/rules/global-protocol-standard.mdc`).

## Workflow

1. **Locate or place it.** Default home for a new protocol is a personal skill: `~/.cursor/skills/<protocol-name>/SKILL.md`. Use a project rule (`.cursor/rules/`) only when the protocol is repo-specific. Ask if unclear.
2. **Fill the template below completely.** Never leave a required section empty or write "TBD" — ask the user instead.
3. **Register compose edges** in `tbcc/docs/protocol-chains.json` when this playbook should hand off to another (keep skills light — graph in JSON, not duplicated prose).
4. **Validate** against the checklist before presenting.
5. **On every revision**: bump the version and replace the changelog line. Substantive edits to Behavioral Rules, Output Contract, or Execution Profile require a version bump.

## Template

```markdown
# <Protocol Name> (v1.0)
Changelog: <one line describing this version's change>

## Purpose
- What this protocol is for
- When it should be used

## When to Invoke
- Trigger phrases: "<phrase>", /<command-alias>
- Situational triggers: <conditions>

## Execution Profile
- Mode: <Agent | Plan | Ask | Debug>; mode switching <allowed/not allowed>
- Model lane: <A (Auto) | B (frontier) | C (Claude Code)> per the model-routing skill
- Parallelism: <subagents allowed, readonly?, model class per subagent>
- Mode inheritance: subagents inherit parent's declared protocol mode at spawn; state explicitly if a subagent needs a different mode

## Delegation & Tooling
- Skills invoked: <names or "none">
- Commands / hooks / Automations involved: <names or "none">
- MCP / integrations required: <names or "none">

## Behavioral Rules
- Reason by: <approach>
- Avoid: <list>
- Prioritize: <list>

## Output Contract
- Required sections: <list>
- Format: <format>
- Done means: <testable completion condition>
- Artifacts: <files / PRs / reports that must exist>
- Failure contract: if a step fails partway, halt and report what completed, what didn't, what's inconsistent; no auto recovery/retry without user instruction

## Exit Conditions
- Next: <what happens after done>
- Follows into: <protocol name | mode | "none">
- Composes: <named handoff(s); also add/update edge in tbcc/docs/protocol-chains.json>
```

## Validation Checklist

- [ ] Version number and one-line changelog at the top
- [ ] All required GSP sections present and non-empty (incl. Composes when another protocol should follow)
- [ ] Model lane references the model-routing skill; no hardcoded model names unless the protocol justifies one
- [ ] Each allowed subagent has a model class (cheap for explore/search, frontier for plan/review)
- [ ] Mode inheritance stated in Execution Profile when subagents are used
- [ ] Failure contract present in Output Contract
- [ ] "Done" is testable, not vibes
- [ ] Exit conditions name a concrete next step or "none"
- [ ] Compose edge registered in `tbcc/docs/protocol-chains.json` when handoff is expected
- [ ] Trigger phrases don't collide with an existing protocol or command
- [ ] Operator-facing tone matches GSP v2.4 (jargon kept; first-use gloss; slightly slower pace)
