use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillInfo {
    pub id: String,
    pub name: String,
    pub description: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TargetPaths {
    pub cursor_skills: String,
    pub claude_skills: String,
    pub cursor_exists: bool,
    pub claude_exists: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InstalledMap {
    pub cursor: Vec<String>,
    pub claude: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BundleInfo {
    pub version: String,
    pub skill_count: u32,
    pub path: String,
}

fn home_dir() -> Result<PathBuf, String> {
    std::env::var_os("USERPROFILE")
        .or_else(|| std::env::var_os("HOME"))
        .map(PathBuf::from)
        .ok_or_else(|| "HOME/USERPROFILE not set".to_string())
}

fn validate_skill_id(id: &str) -> Result<(), String> {
    if id.is_empty() || id.contains("..") || id.contains('/') || id.contains('\\') {
        return Err("invalid skill id".into());
    }
    if !id
        .chars()
        .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
    {
        return Err("skill id must be alphanumeric/dash/underscore".into());
    }
    Ok(())
}

/// Resolve bundled skills directory (dev: resources/skills next to app; prod: resource dir).
pub fn bundle_skills_dir(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    use tauri::Manager;
    // Prefer Tauri resource dir when packaged
    if let Ok(res) = app.path().resource_dir() {
        let candidate = res.join("skills");
        if candidate.is_dir() {
            return Ok(candidate);
        }
        let nested = res.join("resources").join("skills");
        if nested.is_dir() {
            return Ok(nested);
        }
    }
    // Dev / sync-bundle output relative to CARGO_MANIFEST_DIR
    let dev = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../resources/skills");
    if let Ok(canon) = fs::canonicalize(&dev) {
        if canon.is_dir() {
            return Ok(canon);
        }
    }
    Err(format!(
        "bundled skills not found (run npm run sync:bundle). tried {:?}",
        dev
    ))
}

fn parse_frontmatter(skill_md: &str) -> (String, String) {
    let mut name = String::new();
    let mut description = String::new();
    if !skill_md.starts_with("---") {
        return (name, description);
    }
    if let Some(end) = skill_md[3..].find("---") {
        let block = &skill_md[3..3 + end];
        for line in block.lines() {
            let line = line.trim();
            if let Some(rest) = line.strip_prefix("name:") {
                name = rest.trim().trim_matches('"').to_string();
            } else if let Some(rest) = line.strip_prefix("description:") {
                description = rest.trim().trim_matches('"').to_string();
                // Collapse long descriptions for list UI
                if description.len() > 160 {
                    description.truncate(157);
                    description.push_str("...");
                }
            }
        }
    }
    (name, description)
}

pub fn list_catalog(app: &tauri::AppHandle) -> Result<Vec<SkillInfo>, String> {
    let root = bundle_skills_dir(app)?;
    let mut out = Vec::new();
    let entries = fs::read_dir(&root).map_err(|e| e.to_string())?;
    for entry in entries {
        let entry = entry.map_err(|e| e.to_string())?;
        let path = entry.path();
        if !path.is_dir() {
            continue;
        }
        let id = entry.file_name().to_string_lossy().to_string();
        if id.starts_with('_') || id.starts_with('.') {
            continue;
        }
        let skill_md = path.join("SKILL.md");
        if !skill_md.is_file() {
            continue;
        }
        let text = fs::read_to_string(&skill_md).unwrap_or_default();
        let (name, description) = parse_frontmatter(&text);
        out.push(SkillInfo {
            id: id.clone(),
            name: if name.is_empty() { id } else { name },
            description,
        });
    }
    out.sort_by(|a, b| a.name.to_lowercase().cmp(&b.name.to_lowercase()));
    Ok(out)
}

pub fn detect_targets() -> Result<TargetPaths, String> {
    let home = home_dir()?;
    let cursor = home.join(".cursor").join("skills");
    let claude = home.join(".claude").join("skills");
    Ok(TargetPaths {
        cursor_exists: cursor.is_dir(),
        claude_exists: claude.is_dir(),
        cursor_skills: cursor.to_string_lossy().to_string(),
        claude_skills: claude.to_string_lossy().to_string(),
    })
}

fn list_skill_ids(dir: &Path) -> Vec<String> {
    let mut ids = Vec::new();
    if !dir.is_dir() {
        return ids;
    }
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let name = entry.file_name().to_string_lossy().to_string();
                if path.join("SKILL.md").is_file() || path.join("skill.md").is_file() {
                    ids.push(name);
                } else if path.join("SKILL.md").exists() {
                    ids.push(name);
                } else {
                    // still count folders (Cursor skills are dirs)
                    ids.push(name);
                }
            }
        }
    }
    ids.sort();
    ids
}

pub fn list_installed() -> Result<InstalledMap, String> {
    let t = detect_targets()?;
    Ok(InstalledMap {
        cursor: list_skill_ids(Path::new(&t.cursor_skills)),
        claude: list_skill_ids(Path::new(&t.claude_skills)),
    })
}

fn copy_dir_recursive(src: &Path, dst: &Path) -> Result<(), String> {
    fs::create_dir_all(dst).map_err(|e| e.to_string())?;
    for entry in fs::read_dir(src).map_err(|e| e.to_string())? {
        let entry = entry.map_err(|e| e.to_string())?;
        let path = entry.path();
        let name = entry.file_name();
        let dest_path = dst.join(&name);
        if path.is_dir() {
            copy_dir_recursive(&path, &dest_path)?;
        } else {
            fs::copy(&path, &dest_path).map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}

pub fn install_skill(app: &tauri::AppHandle, skill_id: &str, target: &str) -> Result<(), String> {
    validate_skill_id(skill_id)?;
    let bundle = bundle_skills_dir(app)?;
    let src = bundle.join(skill_id);
    if !src.is_dir() {
        return Err(format!("skill not in bundle: {skill_id}"));
    }
    let t = detect_targets()?;
    let dest_root = match target {
        "cursor" => PathBuf::from(&t.cursor_skills),
        "claude" => PathBuf::from(&t.claude_skills),
        _ => return Err("target must be cursor or claude".into()),
    };
    fs::create_dir_all(&dest_root).map_err(|e| e.to_string())?;
    let dest = dest_root.join(skill_id);
    if dest.exists() {
        fs::remove_dir_all(&dest).map_err(|e| e.to_string())?;
    }
    copy_dir_recursive(&src, &dest)?;
    let card = dest.join("CARD.json");
    if card.is_file() {
        let _ = fs::remove_file(card);
    }
    Ok(())
}

pub fn unload_skill(skill_id: &str, target: &str) -> Result<(), String> {
    validate_skill_id(skill_id)?;
    let t = detect_targets()?;
    let dest_root = match target {
        "cursor" => PathBuf::from(&t.cursor_skills),
        "claude" => PathBuf::from(&t.claude_skills),
        _ => return Err("target must be cursor or claude".into()),
    };
    let dest = dest_root.join(skill_id);
    // Safety: dest must be exactly one child of dest_root
    let canon_root = fs::canonicalize(&dest_root).unwrap_or(dest_root.clone());
    if !dest.exists() {
        return Ok(());
    }
    let canon_dest = fs::canonicalize(&dest).map_err(|e| e.to_string())?;
    if !canon_dest.starts_with(&canon_root) {
        return Err("refusing to delete outside skills root".into());
    }
    if canon_dest == canon_root {
        return Err("refusing to delete skills root".into());
    }
    fs::remove_dir_all(&canon_dest).map_err(|e| e.to_string())?;
    Ok(())
}

pub fn bundle_info(app: &tauri::AppHandle) -> Result<BundleInfo, String> {
    let root = bundle_skills_dir(app)?;
    let meta_path = root.join("_bundle.json");
    let (version, skill_count) = if meta_path.is_file() {
        let v: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(&meta_path).map_err(|e| e.to_string())?)
                .unwrap_or(serde_json::json!({}));
        (
            v.get("version")
                .and_then(|x| x.as_str())
                .unwrap_or("0.1.0")
                .to_string(),
            v.get("skill_count")
                .and_then(|x| x.as_u64())
                .unwrap_or(0) as u32,
        )
    } else {
        let n = list_catalog(app)?.len() as u32;
        ("0.1.0".into(), n)
    };
    Ok(BundleInfo {
        version,
        skill_count,
        path: root.to_string_lossy().to_string(),
    })
}
