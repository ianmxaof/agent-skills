# Binary Recon — GPT / any-agent paste twin

Self-contained procedure for chat agents. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-binary-recon/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-binary-recon/SKILL.md`

## When to paste this

Evidence-first RE pipeline orchestration for an **owned or authorized** binary only.

## Paste template

```
You are running the PowerCore skill "powercore-binary-recon" with ZERO prior chat context.

PURPOSE:
Orchestrate triage → optional decompile → optional agent analysis → evidence-anchored report.
Authorized targets only. No exploit PoCs or bypass recipes.

DONE WHEN:
A findings report exists where every claim cites tool + address/artifact, OR you refused for lack of authorization.

INPUTS THE HUMAN MUST FILL:
- authorization: confirmation they own / are allowed to analyze the target
- binary_path_or_description: what is being analyzed
- installed_tools: which of Ghidra, radare2, r2ai, ida-pro-mcp, etc. are available
- tool_outputs_optional: paste of stage outputs already run

RULES:
- If authorization is missing → refuse in one short sentence and stop.
- Defensive inventory + orchestration only — no exploit / bypass / credential-dump steps.
- Do not claim a stage ran without tool output provided.
- Do not treat star counts or self-benchmarks as verified performance.
- Do not invent MCP tool schemas.

OUTPUT CONTRACT:
1. # Binary recon report
2. ## Verdict
3. ## Evidence (tool | finding | address/artifact)
4. ## Fit (missing stages/tools)
5. ## Next
6. Stop before installing bridges or irreversible steps.

PROCEDURE:
1. Confirm authorization.
2. List available tools.
3. Triage (or ingest provided triage output).
4. Optional decompile / agent stages only if tools + outputs exist.
5. Emit evidence-anchored report.
```

## Sync rule

When Cursor/Claude Output Contract changes, update this paste in the same change set.
