# Cleanroom brief

## Source

- url: https://example.com/demo
- mode: clean
- date: 2026-11-02

## Evidence summary

| id | kind | confidence | coverage | limits |
|----|------|------------|----------|--------|
| layout-390 | layout | high | above-fold hero at 390px | no scroll depth beyond fold |
| palette-primary | color | high | computed style on h1 | single node sample |
| font-ui | font | medium | body computed font-family | webfont file not hashed |

## Build brief

Must match (baseline is the contract; `kind` + `value` are checked):

- `layout-390` (layout): {"hero_height_px": 420, "width": 390} — high confidence
- `palette-primary` (color): {"hex": "#1A1A1A", "role": "primary-text"} — high confidence
- `font-ui` (font): {"family": "Inter", "stack": ["Inter", "system-ui"]} — medium confidence

Stack / structure notes: not derivable from evidence; the build agent states its own.

## Check delta (after build)

Candidate: https://example.com/demo-rebuild

| item | baseline | result | pass/fail | note |
|------|----------|--------|-----------|------|
| layout-390 | {"hero_height_px": 420, "width": 390} | {"hero_height_px": 420, "width": 390} | pass | match |
| palette-primary | {"hex": "#1A1A1A", "role": "primary-text"} | {"hex": "#222222", "role": "primary-text"} | fail | value.hex: '#1A1A1A' != '#222222' |
| font-ui | {"family": "Inter", "stack": ["Inter", "system-ui"]} | — | fail | missing in candidate |
| extra-spacing | — | {"section_gap_px": 48} | pass | extra in candidate |

**Overall: FAIL** — 2/4 rows pass.

## Next

1. Fix the failing rows above.
2. Re-capture and re-run the delta.
3. Stop for operator ACK only after all rows pass.
