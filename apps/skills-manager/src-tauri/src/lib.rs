mod skills;

use skills::{
    bundle_info, detect_targets, install_skill, list_catalog, list_installed, unload_skill,
    BundleInfo, InstalledMap, SkillInfo, TargetPaths,
};
use tauri::AppHandle;

#[tauri::command]
fn list_catalog_cmd(app: AppHandle) -> Result<Vec<SkillInfo>, String> {
    list_catalog(&app)
}

#[tauri::command]
fn list_installed_cmd() -> Result<InstalledMap, String> {
    list_installed()
}

#[tauri::command]
fn detect_targets_cmd() -> Result<TargetPaths, String> {
    detect_targets()
}

#[tauri::command]
fn install_skill_cmd(app: AppHandle, skill_id: String, target: String) -> Result<(), String> {
    install_skill(&app, &skill_id, &target)
}

#[tauri::command]
fn unload_skill_cmd(skill_id: String, target: String) -> Result<(), String> {
    unload_skill(&skill_id, &target)
}

#[tauri::command]
fn bundle_info_cmd(app: AppHandle) -> Result<BundleInfo, String> {
    bundle_info(&app)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            list_catalog_cmd,
            list_installed_cmd,
            detect_targets_cmd,
            install_skill_cmd,
            unload_skill_cmd,
            bundle_info_cmd,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
