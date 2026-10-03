# PowerCore Skills Manager

Tauri desktop app that ships the PowerCore agent-skills library and installs or unloads skills into:

- Cursor — `%USERPROFILE%\.cursor\skills`
- Claude Code — `%USERPROFILE%\.claude\skills`

## Develop

```powershell
cd C:\Powercore-repo-main\agent-skills\apps\skills-manager
npm install
npm run sync:bundle
npm run tauri:dev
```

`sync:bundle` copies `agent-skills/.cursor/skills/*` into `resources/skills` (skips `vendor` and hidden dirs).

## Build (local inspect)

```powershell
npm run tauri:build
npm run pack:inspect
```

Artifacts land under `src-tauri/target/release/bundle/` and `dist-inspect/`. **Do not** upload to the PowerCore store until the operator signs off.

## Pack format (future)

See [`docs/powercore-skill-pack.v1.json`](docs/powercore-skill-pack.v1.json). Extra skill packs and a user-submitted plugin ecosystem will use that manifest; v1 only ships the bundled starter library.

## Branding

PowerCore Chrome tokens (near-black, Inter UI). No Tk.
