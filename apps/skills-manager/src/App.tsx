import { useCallback, useEffect, useMemo, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { openPath } from "@tauri-apps/plugin-opener";
import "./App.css";

type SkillInfo = {
  id: string;
  name: string;
  description: string;
};

type TargetPaths = {
  cursor_skills: string;
  claude_skills: string;
  cursor_exists: boolean;
  claude_exists: boolean;
};

type InstalledMap = {
  cursor: string[];
  claude: string[];
};

type BundleInfo = {
  version: string;
  skill_count: number;
  path: string;
};

export default function App() {
  const [catalog, setCatalog] = useState<SkillInfo[]>([]);
  const [installed, setInstalled] = useState<InstalledMap>({ cursor: [], claude: [] });
  const [targets, setTargets] = useState<TargetPaths | null>(null);
  const [bundle, setBundle] = useState<BundleInfo | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const [cat, inst, tgt, bun] = await Promise.all([
        invoke<SkillInfo[]>("list_catalog_cmd"),
        invoke<InstalledMap>("list_installed_cmd"),
        invoke<TargetPaths>("detect_targets_cmd"),
        invoke<BundleInfo>("bundle_info_cmd"),
      ]);
      setCatalog(cat);
      setInstalled(inst);
      setTargets(tgt);
      setBundle(bun);
      setSelectedId((prev) => prev ?? cat[0]?.id ?? null);
    } catch (e) {
      setError(String(e));
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return catalog;
    return catalog.filter(
      (s) =>
        s.id.toLowerCase().includes(q) ||
        s.name.toLowerCase().includes(q) ||
        s.description.toLowerCase().includes(q)
    );
  }, [catalog, query]);

  const selected = catalog.find((s) => s.id === selectedId) ?? null;
  const onCursor = selected ? installed.cursor.includes(selected.id) : false;
  const onClaude = selected ? installed.claude.includes(selected.id) : false;

  async function toggle(target: "cursor" | "claude", install: boolean) {
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      if (install) {
        await invoke("install_skill_cmd", { skillId: selected.id, target });
      } else {
        await invoke("unload_skill_cmd", { skillId: selected.id, target });
      }
      await refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="mark" aria-hidden />
        <div>
          <h1>PowerCore Skills Manager</h1>
          <div className="sub">Install bundled skills into Cursor or Claude Code</div>
        </div>
      </header>

      <div className="main">
        <aside className="list">
          <input
            className="search"
            placeholder="Filter skills…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {filtered.map((s) => (
            <button
              key={s.id}
              type="button"
              className={`skill-row${s.id === selectedId ? " active" : ""}`}
              onClick={() => setSelectedId(s.id)}
            >
              <div>{s.name}</div>
              <div className="id">{s.id}</div>
            </button>
          ))}
          {!filtered.length && <div className="empty">No skills match.</div>}
        </aside>

        <section className="detail">
          {!selected && <div className="empty">Select a skill from the list.</div>}
          {selected && (
            <>
              <h2>{selected.name}</h2>
              <div className="mono">{selected.id}</div>
              <p>{selected.description || "No description in SKILL.md frontmatter."}</p>

              <div className="targets">
                <div className="target-card">
                  <div>
                    <h3>Cursor</h3>
                    <div className={`status${onCursor ? " on" : ""}`}>
                      {onCursor ? "Installed" : "Not installed"}
                    </div>
                  </div>
                  {onCursor ? (
                    <button
                      type="button"
                      className="btn danger"
                      disabled={busy}
                      onClick={() => void toggle("cursor", false)}
                    >
                      Unload
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="btn primary"
                      disabled={busy}
                      onClick={() => void toggle("cursor", true)}
                    >
                      Install
                    </button>
                  )}
                </div>

                <div className="target-card">
                  <div>
                    <h3>Claude Code</h3>
                    <div className={`status${onClaude ? " on" : ""}`}>
                      {onClaude ? "Installed" : "Not installed"}
                    </div>
                  </div>
                  {onClaude ? (
                    <button
                      type="button"
                      className="btn danger"
                      disabled={busy}
                      onClick={() => void toggle("claude", false)}
                    >
                      Unload
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="btn primary"
                      disabled={busy}
                      onClick={() => void toggle("claude", true)}
                    >
                      Install
                    </button>
                  )}
                </div>
              </div>

              {error && <div className="error">{error}</div>}
            </>
          )}
        </section>
      </div>

      <footer className="footer">
        <span>
          Bundle v{bundle?.version ?? "—"} · {bundle?.skill_count ?? catalog.length} skills
        </span>
        {targets && (
          <>
            <span title={targets.cursor_skills}>
              Cursor: {targets.cursor_exists ? "ready" : "will create"} ·{" "}
              <button
                type="button"
                className="link"
                onClick={() => void openPath(targets.cursor_skills)}
              >
                open
              </button>
            </span>
            <span title={targets.claude_skills}>
              Claude: {targets.claude_exists ? "ready" : "will create"} ·{" "}
              <button
                type="button"
                className="link"
                onClick={() => void openPath(targets.claude_skills)}
              >
                open
              </button>
            </span>
          </>
        )}
      </footer>
    </div>
  );
}
