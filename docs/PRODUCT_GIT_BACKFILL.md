# Product git backfill (H7)

Every PowerCore product root must be its own git repo with an `origin` remote (PPQ P0, Q-010; ship-gate `pre_activate` refuses without it). Remote ACK 2026-10-03: browser-hub and powerplayer origins created (private, no push). Init a repo or create a remote only after the operator ACKs that specific product. Replace `<owner>` with the GitHub account/org.

Regenerate: `py -3.13 -m tools.product_qualify git-scan` (strict: `git rev-parse --show-toplevel` must equal the root).

Scan (2026-10-02):

| products | root | git? | origin? | manual command(s) |
|----------|------|------|---------|-------------------|
| vault, ops-feeds, rotator | `C:/Powercore-repo-main/powercore-ops` | yes | https://github.com/ianmxaof/powercore-ops.git | none |
| pc-notes | `C:/Powercore-repo-main/notes-app` | yes | https://github.com/ianmxaof/pc-notes.git | none |
| text-expander | `C:/Powercore-repo-main/text-expander` | NO | - | `git -C "C:\Powercore-repo-main\text-expander" init -b main`<br>`# ensure .gitignore exists, review `git status`, then first commit`<br>`gh repo create <owner>/text-expander --private --source "C:\Powercore-repo-main\text-expander" --remote origin`<br>`# or: git -C "C:\Powercore-repo-main\text-expander" remote add origin <url>` |
| github-presentation | `C:/Powercore-repo-main/powercore-store/test-installs/github-presentation/extracted` | NO | - | `# staged buyer copy (test-installs): find the real dev source repo first; do NOT init here` |
| local-rag | `C:/Powercore-repo-main/llm-rag` | yes | https://github.com/ianmxaof/llm-rag-os.git | none |
| prompt-library | `C:/Powercore-repo-main/prompt-library` | yes | https://github.com/ianmxaof/prompt-library.git | none |
| browser-hub | `C:/Powercore-repo-main/powercore-browser-hub` | yes | NO | `gh repo create <owner>/powercore-browser-hub --private --source "C:\Powercore-repo-main\powercore-browser-hub" --remote origin`<br>`# or: git -C "C:\Powercore-repo-main\powercore-browser-hub" remote add origin <url>` |
| powerplayer | `C:/Powercore-repo-main/vlc-skin` | yes | NO | `gh repo create <owner>/vlc-skin --private --source "C:\Powercore-repo-main\vlc-skin" --remote origin`<br>`# or: git -C "C:\Powercore-repo-main\vlc-skin" remote add origin <url>` |
| powercore-store | `C:\Powercore-repo-main\powercore-store` | NO | - | `git -C "C:\Powercore-repo-main\powercore-store" init -b main`<br>`# ensure .gitignore exists, review `git status`, then first commit`<br>`gh repo create <owner>/powercore-store --private --source "C:\Powercore-repo-main\powercore-store" --remote origin`<br>`# or: git -C "C:\Powercore-repo-main\powercore-store" remote add origin <url>` |

## Notes

- **github-presentation** is a staged buyer copy under `powercore-store/test-installs/`. Find the real dev source first; do **not** init a repo there.
- **powercore-store** is a plain dir today (no `.git`), and several registry roots sit inside it.
- **browser-hub** and **powerplayer (vlc-skin)** already have git but no `origin`: add the remote only.
- **powercore-ops** is shared by vault, ops-feeds and rotator (one repo, one row).
- Home-dir caveat: if a parent directory (e.g. the user home) is itself a git repo, a plain product dir is reported as "inside another work tree"; the gate treats that as not-its-own-repo.
