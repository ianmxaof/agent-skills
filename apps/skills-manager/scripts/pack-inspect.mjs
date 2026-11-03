/**
 * Zip Windows bundle outputs into dist-inspect for operator review.
 * Does not upload to R2 or touch the store.
 */
import { existsSync, mkdirSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import { spawnSync } from "child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const appRoot = join(__dirname, "..");
const bundleRoot = join(appRoot, "src-tauri", "target", "release", "bundle");
const outDir = join(appRoot, "dist-inspect");
const zipPath = join(outDir, "powercore-skills-manager-0.1.0-win.zip");

if (!existsSync(bundleRoot)) {
  console.error("No release bundle yet. Run: npm run tauri:build");
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });

const ps = `
$ErrorActionPreference = 'Stop'
$src = '${bundleRoot.replace(/'/g, "''")}'
$dest = '${zipPath.replace(/'/g, "''")}'
if (Test-Path $dest) { Remove-Item $dest -Force }
Compress-Archive -Path (Join-Path $src '*') -DestinationPath $dest -Force
Get-Item $dest | Select-Object FullName, Length | Format-List
`;
const r = spawnSync("powershell", ["-NoProfile", "-Command", ps], {
  encoding: "utf8",
});
if (r.status !== 0) {
  console.error(r.stdout || "");
  console.error(r.stderr || "");
  process.exit(r.status || 1);
}
console.log(r.stdout);
console.log("inspect zip ready (not uploaded to store)");
