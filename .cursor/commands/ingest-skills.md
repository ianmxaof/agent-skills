# /ingest-skills — Vendor ingest from URL or path

Ingest a GitHub URL, raw file URL, or local folder into the portable **agent-skills** vendor pipeline (dump → sort → promote list). Do **not** `--live` install unless the operator explicitly asks.

## Input

The text after this command (or the latest URL/path in the message) is the source. Accept:

- Full repo: `https://github.com/org/repo`
- Subfolder: `https://github.com/org/repo/tree/main/resources/some-skill`
- Raw `SKILL.md` / `.mdc` URL
- Local path to a skill folder or file

Optional flags in the same message:

- `--name slug` — override batch folder name
- `--boost name=15` — raise importance for a unit (repeatable)
- `--promote` — copy **promote-candidate** tier into `.cursor/skills/` library only (still not live)
- `--live` — only with `--promote`, also install into `~/.cursor/skills/`

## Procedure

1. Resolve `AGENT_SKILLS_ROOT`:
   - Prefer workspace folder ending in `agent-skills`
   - Else `C:\Powercore-repo-main\agent-skills` if it exists
   - Else ask once for the path

2. Run (PowerShell):

```powershell
cd $AGENT_SKILLS_ROOT
$env:PYTHONIOENCODING = 'utf-8'
py -3.13 scripts\pipeline.py "<SOURCE>" 
```

If `--name` was given, append `--name <slug>`.  
If `--boost` was given, append each as `--boost name=points`.  
If `--promote` was given, append `--promote-candidates` (and `--live` only if asked). Prefer `--dry-run` on first promote unless they said to apply.

3. After the script finishes, show a short operator summary:

| Field | Value |
|-------|--------|
| Source | URL/path |
| Incoming batch | `vendor/incoming/...` |
| Units sorted | count |
| Top scores | name · score · tier · kind (top 10) |

4. End with next steps (menu only — do not promote/live unless they asked):

- Promote one: `py -3.13 scripts\promote.py --name <name>`
- Promote candidates: `py -3.13 scripts\promote.py --tier promote-candidate`
- Make live: add `--live` to promote
- Docs: `vendor/README.md`

## Rules

- Never auto `--live` without an explicit ask.
- Never commit unless asked.
- If git clone fails, report the error and stop — do not invent skills.
- If agent-skills is missing scripts, say the pipeline is not installed and point at `vendor/README.md`.
