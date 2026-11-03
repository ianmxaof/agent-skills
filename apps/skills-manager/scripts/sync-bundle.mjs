/**
 * Sync agent-skills library into the Tauri resources bundle.
 * Source: ../../.cursor/skills (canonical Cursor skills)
 * Dest:   ../resources/skills
 * Excludes: vendor, tests, .ship-gate, node_modules, __pycache__
 */
import { cpSync, existsSync, mkdirSync, readdirSync, rmSync, statSync, writeFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const appRoot = join(__dirname, "..");
const repoRoot = join(appRoot, "..", "..");
const srcSkills = join(repoRoot, ".cursor", "skills");
const destSkills = join(appRoot, "resources", "skills");

const SKIP_NAMES = new Set([
  "vendor",
  "tests",
  "test",
  ".ship-gate",
  "node_modules",
  "__pycache__",
  ".pytest_cache",
  ".git",
]);

function shouldSkip(name) {
  if (SKIP_NAMES.has(name)) return true;
  if (name.startsWith(".")) return true;
  return false;
}

if (!existsSync(srcSkills)) {
  console.error(`FAIL: missing source skills at ${srcSkills}`);
  process.exit(1);
}

if (existsSync(destSkills)) {
  rmSync(destSkills, { recursive: true, force: true });
}
mkdirSync(destSkills, { recursive: true });

let count = 0;
for (const name of readdirSync(srcSkills)) {
  if (shouldSkip(name)) continue;
  const src = join(srcSkills, name);
  if (!statSync(src).isDirectory()) continue;
  const skillMd = join(src, "SKILL.md");
  if (!existsSync(skillMd)) {
    console.warn(`skip (no SKILL.md): ${name}`);
    continue;
  }
  cpSync(src, join(destSkills, name), { recursive: true });
  count += 1;
}

const manifest = {
  id: "powercore-agent-skills-starter",
  version: "0.1.0",
  min_manager: "0.1.0",
  synced_at: new Date().toISOString(),
  skill_count: count,
  source: ".cursor/skills",
};
writeFileSync(join(destSkills, "_bundle.json"), JSON.stringify(manifest, null, 2) + "\n");

console.log(`synced ${count} skills → resources/skills`);
console.log(JSON.stringify(manifest));
