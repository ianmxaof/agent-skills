---
name: powercore-secret-forge
description: Generate strong random passwords and Diceware-style passphrases offline
  with a correct entropy figure per secret. Use for /forge, /secret-forge, generate
  a password, or passphrase batches.
---
# Secret Forge — Claude Code twin

Thin mirror of `agent-skills/.cursor/skills/powercore-secret-forge/SKILL.md`.
GPT paste: `agent-skills/docs/gpt-paste/POWERCORE_SECRET_FORGE_GPT_PASTE.md`.

## Rules

- `secrets` module only — never `random`
- Password entropy = `length * log2(alphabet)`; passphrase = `words * log2(wordlist)`
- `--no-lookalike` strips `Il1|O0o` and recomputes alphabet size
- Print `<secret>\t<bits>` only; never write secrets to disk or logs

## Output contract

One secret + bits per line; optional meta footer with no secrets.

## Do not

- Network / Vault write / stored history; guess wordlist size
