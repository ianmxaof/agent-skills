---
name: github-seo-sentry
description: >-
  Scores a GitHub repo's public presentation (README, About description, topics)
  with gh-visibility sentry: organic SEO score, keyword extract, three description
  variants. Use when polishing GitHub About copy, README SEO, repo topics, or when
  the user says /github-seo-sentry, github seo, or presentation sentry. Advisory
  only — never auto-commits or bulk-edits GitHub settings.
---

# GitHub SEO sentry

Same rubric as `github-seo-repo-template` (`gh-visibility`). Read-only: draft copy for a human to paste.

## When to use

- Polish a repo README / GitHub About / topics
- After `github-seo-repo-template` Action comments a score
- Operator says `/github-seo-sentry`, "score this README", "GitHub description + keywords"

## Procedure

1. Find `README.md` (or the public landing doc, not operator changelogs).
2. Run the CLI from the template checkout (no `GITHUB_TOKEN` required):

```bash
pip install -e ".[dev]"   # in github-seo-repo-template
gh-visibility sentry --readme path/to/README.md --name repo-name --output markdown
```

PowerShell:

```powershell
cd C:\Powercore-repo-main\github-seo-repo-template
py -3.13 -m pip install -e ".[dev]"
py -3.13 -m gh_visibility.cli sentry --readme README.md --name github-seo-repo-template --output markdown
```

3. Emit to the operator (paste-ready):
   - **Overall score** /100 and dimension gaps
   - **Keywords** (8–12)
   - **Three About-line variants** (each ≤160 chars) — pick one
   - **Topics** (5–12) — GitHub Settings → Topics
   - Optional: public README outline (What / Who / Quick Start / Usage / License). Do not dump secrets, `.env`, session files, or live money-path UI.

4. **Do not** `gh repo edit`, auto-commit README, or push topics unless the operator explicitly asks.

## GitHub Action

Reusable workflow (advisory job summary, no writes):

```yaml
jobs:
  seo:
    uses: ianmxaof/github-seo-repo-template/.github/workflows/seo-sentry.yml@main
```

Or copy `.github/workflows/seo-sentry.yml` into the target repo.

## Rules

- Human-in-the-loop. Tool is advisory.
- No growth-hack / star-gaming copy.
- TBCC public copy: no island IPs, tokens, or operator dash screenshots with live data.
