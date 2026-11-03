---
name: powercore-secret-forge
description: Generate strong random passwords and Diceware-style passphrases offline
  with a correct entropy figure per secret. Use for /forge, /secret-forge, generate
  a password, passphrase batches, or rotator/dev placeholder seeds.
purpose: Offline secret generation shaped by alphabet flags, with entropy math that
  stays honest in passphrase mode
trigger_phrases:
- /powercore-secret-forge
- /forge
- /secret-forge
- generate a password
- passphrase
inputs:
- count (1-50), length, alphabet flags (lower/upper/number/symbol), no-lookalike, mode
outputs:
- secret per line + bits of entropy per secret
jev_hints:
  lane: chat
  cost: free
  needs_context: false
if_stumped: Ask once for mode (password|passphrase) and count; do not invent a wordlist size.
example_invocation: /forge --mode password --count 5
---
# PowerCore Secret Forge (v0.1)

Canonical Cursor skill. Triple Surface (locked): Cursor (this file) + Claude Code twin
under consuming repos' `.claude/skills/powercore-secret-forge/` + GPT paste at
`agent-skills/docs/gpt-paste/POWERCORE_SECRET_FORGE_GPT_PASTE.md`.

Foundation reverse-specced from a local-first password generator page (wavespeed).

## Purpose

One call returns N passwords or passphrases, alphabet-shaped by flags, look-alike-free
when asked, each with a correct entropy figure — no network, no storage.

## When to invoke

- Credential, throwaway token batch, rotator/dev placeholder seed
- `/forge`, `/secret-forge`, "generate a password", "passphrase"

**Skip when:** Vault write / entitlement secrets; operator wants a stored history.

## Execution Profile

- Freedom: low (exact crypto + output format)
- Mode: Agent

## Harness attach

| Surface | Value |
|---------|-------|
| **MCP** | none |
| **Hooks** | endgates on stop |
| **Memory** | print only — never write secrets to disk or chat history files |
| **Compose** | none required; Hub `/run` only after CLI exists |

## Behavioral rules

- `secrets.choice` / `secrets.randbelow` only. Never `random`.
- Password entropy = `length * log2(alphabet_size)`.
- Passphrase entropy = `words * log2(wordlist_size)`. Same number for both modes is a bug.
- `--no-lookalike` strips `Il1|O0o` from alphabet **and** recomputes alphabet size.
- Print only; never write to disk; never log secrets to chat history files.
- Alphabet &lt; 2 chars or empty → error, not a silent weak secret.
- Output per line: `<secret>\t<bits>`. No prose between secrets.

## Modes

| mode | default | entropy basis |
|------|---------|---------------|
| password | 16 chars, all classes | alphabet size |
| passphrase | 5 words | EFF long list size (declare size used) |

## Checklist (copy and tick)

```
- [ ] 1. Confirm mode, count, flags, lookalike strip
- [ ] 2. Generate with secrets module (or refuse if no runtime)
- [ ] 3. Print secret + bits per line only
- [ ] 4. Do not echo secrets into logs / files
```

## Output contract

```text
<secret>\t<bits>
…
# forge meta (optional footer, no secrets)
mode=… count=… alphabet_size=… wordlist_size=…
```

## Do not

- Network call, Vault write, or stored history
- Claim a secret was saved anywhere
- Guess wordlist size — declare it or ask

## CLI (stub)

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 .cursor/skills/powercore-secret-forge/scripts/secret_forge.py --mode password --count 3 --meta
py -3.13 .cursor/skills/powercore-secret-forge/scripts/secret_forge.py --mode passphrase --count 2 --meta
```

Wordlist default: `data/wordlist_eff_stub.txt` (tiny stub). Swap for full EFF long
list before treating passphrase entropy as production-honest. Hub `/run` not wired yet.

## Triple Surface

| Surface | Path |
|---------|------|
| Cursor (canonical) | `agent-skills/.cursor/skills/powercore-secret-forge/SKILL.md` |
| Claude Code twin | `<project>/.claude/skills/powercore-secret-forge/SKILL.md` |
| GPT / any-agent paste | `agent-skills/docs/gpt-paste/POWERCORE_SECRET_FORGE_GPT_PASTE.md` |

```powershell
cd C:\Powercore-repo-main\agent-skills
py -3.13 -m tools.skill_gap.scaffold_surfaces --skill powercore-secret-forge --check
```

## Status

v0.1 — chat + procedure. CLI not shipped yet.
