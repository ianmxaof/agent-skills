# LOG — foundation packs from Hub article-to-tool transcript

**Date:** 2026-11-02  
**Source:** Hub session dump (multi `/run powercore-article-to-tool` + fit scans)  
**Action:** Operator ACK — write all foundation packs to disk (Triple Surface).

## Skills scaffolded

| Skill | Primary surface | Notes |
|-------|-----------------|-------|
| `powercore-cleanroom-brief` | Hub `/run` later; chat now | Compose website-clone + feature-scan + site-map |
| `powercore-tool-index-harvest` | Hub `/run` later | Directory → inventory |
| `powercore-tool-catalog` | chat | Catalog page shape; sibling of index-harvest |
| `powercore-secret-forge` | Cursor + CLI stub next | Offline secrets; no CLI yet |
| `powercore-binary-recon` | Hub `/run` later | Authorized targets only; no exploit PoC |

## Not written as skills (HARVEST-only from same transcript)

- Store card chrome rule (no-upload / no-signup / no-watermark) — doc candidate
- `store/launch-channels.md` from 50-directory list — doc candidate

## Check

```powershell
cd C:\Powercore-repo-main\agent-skills
foreach ($s in @(
  'powercore-cleanroom-brief',
  'powercore-tool-index-harvest',
  'powercore-tool-catalog',
  'powercore-secret-forge',
  'powercore-binary-recon'
)) { py -3.13 -m tools.skill_gap.scaffold_surfaces --skill $s --check }
```
