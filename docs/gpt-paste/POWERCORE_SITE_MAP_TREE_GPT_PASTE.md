# PowerCore Site Map Tree — GPT paste twin

Twin of `agent-skills/.cursor/skills/powercore-site-map-tree/SKILL.md` (v1.1 live).

## Job

Map the **shape** of a site (origin-rooted link tree + sitemap) or GitHub repo
(directory tree). Add Mermaid visual and evidence-tagged flow/nav IA read.
Inventory + speculation only — not trust, docs-vs-code, or aesthetics.

## Hub

`/run site-map` or bare `/site-map` on the focused tab. Card: `# Site map` /
`## Root` / `## Origin` / `## Tree` / `## Visual` / `## Flow / nav` /
`## Compose next` / `## Notes`.

## CLI

```text
python site_map.py --json https://example.com
python site_map.py --json --lite https://example.com/deep/page
python site_map.py --json --merge-urls https://example.com/pricing --merge-file urls.json
python site_map.py --json https://github.com/owner/repo
python site_map.py --self-test
```

Default profile is **full** (origin + robots/sitemap + BFS). `--lite` = v1.0 shallow tab BFS.
Thin-map enrich: `--merge-urls` / `--merge-file` (BeatAPI `web_map` is paid-tier; Firecrawl map needs auth).
