---
name: powercore-site-map-tree
description: >-
  Builds a hierarchical site or repo map (link tree / directory tree) for the
  open Hub tab or a pasted URL — full origin map by default (robots/sitemap +
  BFS), with Mermaid visual, evidence-tagged flow/nav read, and compose hops.
  Inventory + IA speculation only, not a security verdict. Use for /site-map,
  /sitemap-tree, "map this site", or "show the repo tree".
---

# PowerCore Site Map Tree (v1.1)

Separate from `semantic-deception-detector` and `powercore-repo-trust`. Answers
**what’s the shape — and what does the IA suggest?** — not docs↔code or install safety.

## Purpose

- Emit a **readable tree** of a website’s linked pages (origin-rooted) or a
  GitHub repo’s directory layout (Trees API).
- Prefer **whole-site** inventory: `robots.txt` Sitemap: lines + `sitemap.xml`
  (+ index children) unioned with same-origin BFS — not only the focused tab URL.
- Add **Mermaid** visual, **Flow / nav** bullets (every claim carries `ev:`), and
  **Compose next** hops to sibling Hub skills.
- Cap depth/nodes so Hub chat stays usable; `--lite` restores the shallow v1.0 path.
- Never execute remote code. Never claim malware / trust / fit.

## When to Invoke

- `/site-map`, `/sitemap`, `/run site-map`, `map this site`, `show the repo tree`
- After Desk / feature-scan when the operator wants orientation + IA read

**Do not use for:** security scoring, docs-vs-code, install-hook triage.

## CLI / Hub

```powershell
python "C:\Powercore-repo-main\agent-skills\.cursor\skills\powercore-site-map-tree\scripts\site_map.py" --json "https://example.com"
python …\site_map.py --json --lite "https://example.com/deep/page"
python …\site_map.py --json --merge-urls "https://example.com/pricing" --merge-urls "https://example.com/docs"
# or: --merge-file urls.json   # BeatAPI {urls:[…]} / Firecrawl map dump
python …\site_map.py --json "https://github.com/owner/repo"
python …\site_map.py --self-test
```

**Thin-map enrich:** BeatAPI `web_map` is paid-tier on free accounts; Firecrawl `firecrawl_map` needs auth. Agents dump provider URLs into `--merge-file` / `--merge-urls` — CLI stays stdlib-only.

Hub: **Map this tab · site / repo tree** → `/run site-map` (or bare `/site-map`).
Injects this tab’s URL; script **re-roots at origin** in full profile.
Card sections: Root · Origin · Tree · Visual · Flow/nav · Compose next · Notes.

Registry id: `site-map` → `powercore-site-map-tree/scripts/site_map.py`.

## Output Contract

Card headings (in order): `# Site map` → `## Root` → `## Origin` (when distinct) →
`## Tree` → `## Visual` (fenced `mermaid`) → `## Flow / nav` → `## Compose next` →
`## Notes`.

Tree meta line example: `_Site link tree_ · N nodes · profile=full · sources=robots,sitemap,bfs`

Every Flow/nav bullet must carry `· ev: …`. Compose next lists sibling `/run …` hops only.

## Limits

| Profile | Caps |
|---------|------|
| **full** (default) | origin-rooted; robots + sitemap + BFS; depth ≤ 4, ≤ 250 nodes, ≤ 36 HTML fetches |
| **lite** (`--lite`) | tab-URL BFS only; depth ≤ 3, ≤ 80 nodes, smaller HTML budget |
| Repo | ≤ 80 paths (or `--max-nodes`); skips `node_modules` / `vendor` / etc. |

Mermaid capped at 60 nodes for readability.

## Data spine (real evidence)

| Source | Role |
|--------|------|
| `GET /robots.txt` | Sitemap: URLs |
| `sitemap.xml` / index | Authoritative URL inventory |
| HTML BFS + navish `<a>` attrs | Link graph + chrome placement |
| BeatAPI `web_map` / Firecrawl `firecrawl_map` | Optional agent enrichment when thin/SPA (not required for CLI) |

## Sibling skills (Compose next)

- **feature-scan** — features + stack · **website-clone** — aesthetics
- **semantic-scan** — docs↔code · **repo-trust** — supply-chain
- **hub-clear** — `/clear` Ask transcript (unrelated)
