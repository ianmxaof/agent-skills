# Secret Forge — GPT / any-agent paste twin

Self-contained procedure for chat agents. Keep in sync with:

- Cursor: `agent-skills/.cursor/skills/powercore-secret-forge/SKILL.md`
- Claude Code: `<project>/.claude/skills/powercore-secret-forge/SKILL.md`

## When to paste this

Offline password / passphrase generation with honest entropy figures.

## Paste template

```
You are running the PowerCore skill "powercore-secret-forge" with ZERO prior chat context.

PURPOSE:
Generate N passwords or passphrases offline with correct entropy per secret. No storage.

DONE WHEN:
Each line is <secret>\t<bits> and entropy math matches the mode.

INPUTS THE HUMAN MUST FILL:
- mode: password | passphrase
- count: 1–50
- length_or_words: chars or word count
- flags: lower/upper/number/symbol; no_lookalike yes/no
- wordlist_size: REQUIRED for passphrase mode (do not guess)

RULES:
- Use a CSPRNG conceptually (describe / use secure random). Never weak PRNG.
- Password bits = length * log2(alphabet_size).
- Passphrase bits = words * log2(wordlist_size).
- no_lookalike strips Il1|O0o and recomputes alphabet size.
- Print secrets only as requested lines — do not add prose between them.
- Do not claim secrets were saved anywhere.
- Alphabet size < 2 → error.

OUTPUT CONTRACT:
1. One line per secret: <secret>\t<bits>
2. Optional footer meta (mode, count, alphabet_size, wordlist_size) with NO secrets
3. Stop.

PROCEDURE:
1. Confirm inputs.
2. Compute alphabet or require wordlist_size.
3. Generate and print.
```

## Sync rule

When Cursor/Claude Output Contract changes, update this paste in the same change set.
