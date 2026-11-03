# Compose mapping — capture skills → evidence envelope

`powercore-cleanroom-brief` does **not** scrape. A capture skill (or the operator pasting
its output) supplies material; the brief agent turns each fact into one envelope item
(`id, kind, value, confidence, coverage, limits` — see `scripts/evidence_envelope.py`).

## Ground rules

- **Delta compares only `kind` + `value`** (locked). So `value` must be small, structural and
  reproducible by a second capture at the same widths/state. Put prose, screenshot labels
  and caveats in `coverage` / `limits`, never in `value`.
- `confidence` / `coverage` / `limits` are epistemic metadata: set honestly, never compared.
- **One fact → one item**, stable `id` (`<family>-<slug>`), so baseline and candidate line up.
  A baseline id the candidate lacks is a fail; keep ids deterministic across captures.
- Candidate-only items pass as `extra` (locked): the baseline is the contract.
- Never emit an item for something the source marked *unknown* or that the mode refused.
  A gap goes in the brief's notes, not in the envelope.
- Mode gate: items whose evidence is page source / JS / network / sitemap-or-robots reads
  are **`deep` only** (conservative default; operator may relax). `clean` records carry
  screenshots, visible text and measured/computed values only.

## Confidence mapping

| Source label | Envelope `confidence` |
|--------------|-----------------------|
| observed / measured directly | `high` |
| inferred (fingerprint, single sample, derived) | `medium` (or `low` if weak) |
| unknown / not seen | **no item** |

## powercore-website-clone → envelope

Source files: `BRIEF.md`, `TOKENS.md`, `MOTION.md`, `shots/` (Observe / Harvest outputs).

| Source field | `kind` | `id` pattern | `value` shape | Mode |
|--------------|--------|--------------|---------------|------|
| BRIEF layout measure at a viewport | `layout` | `layout-<width>` (390/768/1440) | `{width, hero_height_px, ...}` | clean |
| BRIEF section order | `structure` | `sections-<width>` | `{order: ["hero","pricing",...]}` | clean |
| TOKENS color / accent | `color` | `palette-<role>` | `{hex, role}` | clean |
| TOKENS font family/weight | `font` | `font-<role>` | `{family, stack, weight}` | clean |
| TOKENS radius / spacing | `spacing` | `spacing-<name>` | `{<name>_px: n}` | clean |
| MOTION driver row | `motion` | `motion-<slug>` | `{driver: "time/scroll/hover/click", effect}` | clean (observed behaviour) |
| `shots/` | — | — | not an item; cite shot labels in `coverage` | — |

## powercore-website-feature-scan → envelope

Source files: `FEATURES.md` (Feature · Surface · Evidence · Confidence),
`STACK.md` (Signal · Kind · Host/path · Confidence · Notes).

| Source row | `kind` | `id` pattern | `value` shape | Mode |
|------------|--------|--------------|---------------|------|
| FEATURES row, evidence = visible UI / screenshot label | `feature` | `feature-<slug>` | `{present: true, surface}` | clean |
| FEATURES row, evidence = DOM id / API path | `feature` | `feature-<slug>` | `{present: true, surface}` | deep |
| STACK row (scripts, hosts, fingerprints) | `stack` | `stack-<slug>` | `{signal, kind, host}` | deep |

FEATURES "absent" rows are not items (absence belongs in brief notes). Source *observed* →
`high`; *inferred* → `medium`/`low`; *unknown* → omit.

## powercore-site-map-tree → envelope

Source: the `# Site map` card (`## Tree`, `## Flow / nav` with `ev:` bullets).

| Source | `kind` | `id` pattern | `value` shape | Mode |
|--------|--------|--------------|---------------|------|
| Primary nav link seen in the rendered page | `nav` | `nav-<path-slug>` | `{path, label}` | clean |
| Tree node from sitemap.xml / robots / BFS | `route` | `route-<path-slug>` | `{path}` | deep |
| Flow/nav bullet | — | — | not an item; its `ev:` goes in `coverage` | — |

Tree caps (depth ≤ 4, ≤ 250 nodes) belong in `limits`.

## From envelope to brief

1. Baseline capture(s) → one record (`make_record` / `dump_record`).
2. `py -3.13 scripts/render_brief.py baseline.json` → brief with a must-match list citing item ids.
3. After build: second capture, same widths/state → candidate record →
   `render_brief.py baseline.json candidate.json` → `## Check delta` via `delta()`.
4. Overall pass only if `all_pass(rows)`.

Example output: `evals/fixtures/example_brief.md` (generated from the two fixtures; a test
regenerates it, so it cannot drift).
