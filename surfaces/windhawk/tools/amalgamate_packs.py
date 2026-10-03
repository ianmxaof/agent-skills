#!/usr/bin/env python3
"""Amalgamate Windhawk mod pairs into local@ packs (namespaced + shared LoadLibraryExW)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "ModsSource"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_headers(text: str) -> tuple[str, str, str]:
    """Return (settings_yaml_inner, includes_and_body_start_index material).

    Splits after ==/WindhawkModSettings==.
    """
    m = re.search(
        r"// ==WindhawkModSettings==\s*/\*(.*?)\*/\s*// ==/WindhawkModSettings==\s*",
        text,
        re.S,
    )
    if not m:
        raise SystemExit(f"no settings block in input")
    settings = m.group(1).strip("\n")
    body = text[m.end() :]
    return settings, body


def collect_includes(body: str) -> tuple[list[str], str]:
    includes: list[str] = []
    lines = body.splitlines(keepends=True)
    i = 0
    # skip blank / comments before includes
    while i < len(lines):
        s = lines[i].strip()
        if (
            s.startswith("#include")
            or s.startswith("#undef")
            or s.startswith("#ifndef")
            or s.startswith("#define M_PI")
            or s.startswith("#endif")
            or s == ""
            or s.startswith("//")
            and "Source code" in s
            or s.startswith("//")
            and "bug reports" in s
            or s.startswith("//")
            and "pull requests" in s
            or s.startswith("//")
            and "GNU" in s
            or s.startswith("//")
            and "https://" in s
            or s.startswith("//")
            and s == "//"
        ):
            if s.startswith("#include") or s.startswith("#undef"):
                includes.append(lines[i].rstrip("\n"))
            elif s.startswith("#ifndef") or s.startswith("#define M_PI") or s.startswith("#endif"):
                includes.append(lines[i].rstrip("\n"))
            i += 1
            continue
        # keep using namespace at top with includes for per-app
        if s.startswith("using namespace"):
            includes.append(lines[i].rstrip("\n"))
            i += 1
            continue
        break
    rest = "".join(lines[i:])
    return includes, rest


def rename_settings_keys(text: str, mapping: dict[str, str]) -> str:
    out = text
    # Longer keys first so prefixes don't double-hit
    for old, new in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
        out = out.replace(f'L"{old}"', f'L"{new}"')
        out = out.replace(f'L"{old}[', f'L"{new}[')
    return out


def prefix_settings_yaml(settings: str, mapping: dict[str, str]) -> str:
    out = settings
    for old, new in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
        # top-level yaml keys: "- oldKey:" or "- oldKey "
        out = re.sub(
            rf"(?m)^(-\s+){re.escape(old)}(\s*:)",
            rf"\1{new}\2",
            out,
        )
    return out


def prepare_feature(
    ns: str,
    body: str,
    setting_map: dict[str, str],
    *,
    strip_ll_hook: bool = True,
) -> str:
    includes, rest = collect_includes(body)
    # includes handled by pack; drop from feature
    rest = rename_settings_keys(rest, setting_map)

    # Rename entry points
    rest = rest.replace("BOOL Wh_ModInit()", f"BOOL FeatureInit()")
    rest = rest.replace("void Wh_ModAfterInit()", f"void FeatureAfterInit()")
    rest = rest.replace("void Wh_ModUninit()", f"void FeatureUninit()")
    rest = rest.replace(
        "BOOL Wh_ModSettingsChanged(BOOL* bReload)",
        "BOOL FeatureSettingsChanged(BOOL* bReload)",
    )
    rest = rest.replace("void Wh_ModSettingsChanged()", "void FeatureSettingsChanged()")

    if strip_ll_hook:
        # Convert LoadLibraryExW_Hook -> OnLoadLibraryExW (no Original call)
        rest = re.sub(
            r"using LoadLibraryExW_t = decltype\(&LoadLibraryExW\);\s*"
            r"LoadLibraryExW_t LoadLibraryExW_Original;\s*"
            r"HMODULE WINAPI LoadLibraryExW_Hook\(LPCWSTR lpLibFileName,\s*"
            r"HANDLE hFile,\s*"
            r"DWORD dwFlags\) \{\s*"
            r"HMODULE module = LoadLibraryExW_Original\(lpLibFileName, hFile, dwFlags\);\s*"
            r"if \(module(.*?)\) \{(.*?)\}\s*"
            r"return module;\s*"
            r"\}",
            r"void OnLoadLibraryExW(HMODULE module, LPCWSTR lpLibFileName) {\n"
            r"    if (module\1) {\2}\n"
            r"}",
            rest,
            count=1,
            flags=re.S,
        )
        # Remove only the LoadLibraryExW hook install; keep kernelBaseModule if
        # later hooks (GetTickCount/Sleep) still need it.
        def _strip_ll_install(m: re.Match[str]) -> str:
            after = rest[m.end() : m.end() + 200]
            keep_kb = "kernelBaseModule" in after or "pKernelBaseGetTickCount" in after
            return (
                "\n    HMODULE kernelBaseModule = GetModuleHandle(L\"kernelbase.dll\");\n"
                if keep_kb
                else "\n"
            )

        rest2, nsub = re.subn(
            r"\n\s*HMODULE kernelBaseModule = GetModuleHandle\(L\"kernelbase\.dll\"\);\s*"
            r"(?:auto pKernelBaseLoadLibraryExW = \(decltype\(&LoadLibraryExW\)\)GetProcAddress\(\s*"
            r"kernelBaseModule, \"LoadLibraryExW\"\);\s*"
            r"WindhawkUtils::(?:SetFunctionHook|Wh_SetFunctionHookT)\(\s*"
            r"pKernelBaseLoadLibraryExW,\s*"
            r"LoadLibraryExW_Hook,\s*"
            r"&LoadLibraryExW_Original\);)\s*",
            _strip_ll_install,
            rest,
            count=1,
        )
        if nsub:
            rest = rest2
        else:
            rest = re.sub(
                r"\n\s*HMODULE kernelBaseModule = GetModuleHandle\(L\"kernelbase\.dll\"\);\s*"
                r"auto pKernelBaseLoadLibraryExW = \(decltype\(&LoadLibraryExW\)\)GetProcAddress\(\s*"
                r"kernelBaseModule, \"LoadLibraryExW\"\);\s*"
                r"WindhawkUtils::SetFunctionHook\(pKernelBaseLoadLibraryExW,\s*"
                r"LoadLibraryExW_Hook,\s*"
                r"&LoadLibraryExW_Original\);\s*",
                "\n",
                rest,
                count=1,
            )

    # Indent body into namespace
    indented = "\n".join(
        ("    " + line if line.strip() else line) for line in rest.splitlines()
    )
    include_note = "\n".join(f"// pack-includes: {inc}" for inc in includes[:3])
    return (
        f"namespace {ns} {{\n"
        f"{include_note}\n"
        f"{indented}\n"
        f"}}  // namespace {ns}\n"
    ), includes


def build_volume_pack() -> None:
    sys_text = read(SRC / "taskbar-volume-control.wh.cpp")
    app_text = read(SRC / "taskbar-volume-control-per-app.wh.cpp")
    sys_settings, sys_body = strip_headers(sys_text)
    app_settings, app_body = strip_headers(app_text)

    sys_map = {
        "volumeChangeStep": "systemVolumeChangeStep",
        "ctrlScrollVolumeChange": "systemCtrlScrollVolumeChange",
        "noAutomaticMuteToggle": "systemNoAutomaticMuteToggle",
    }
    app_map = {
        "volumeChangeStep": "perAppVolumeChangeStep",
        "ctrlScrollVolumeChange": "perAppCtrlScrollVolumeChange",
        "noAutomaticMuteToggle": "perAppNoAutomaticMuteToggle",
    }

    # Prefer tray for system volume so buttons stay free for per-app
    sys_settings = sys_settings.replace(
        "- scrollArea: taskbar", "- scrollArea: notification_area"
    )
    sys_settings = prefix_settings_yaml(sys_settings, sys_map)
    app_settings = prefix_settings_yaml(app_settings, app_map)
    # Label sections in settings
    merged_settings = (
        "# === System volume (tray / empty taskbar / scroll-anywhere) ===\n"
        + sys_settings
        + "\n# === Per-app volume (taskbar buttons) ===\n"
        + app_settings
    )

    sys_feat, sys_inc = prepare_feature("volume_system", sys_body, sys_map)
    app_feat, app_inc = prepare_feature("volume_perapp", app_body, app_map)

    includes = []
    seen = set()
    for inc in (
        ['#include <windhawk_utils.h>']
        + sys_inc
        + app_inc
    ):
        if inc not in seen:
            seen.add(inc)
            includes.append(inc)

    glue = r'''
static bool IsExplorerProcess() {
    WCHAR moduleFilePath[MAX_PATH];
    DWORD n = GetModuleFileName(nullptr, moduleFilePath, ARRAYSIZE(moduleFilePath));
    if (!n || n >= ARRAYSIZE(moduleFilePath)) {
        return false;
    }
    PCWSTR name = wcsrchr(moduleFilePath, L'\\');
    name = name ? name + 1 : moduleFilePath;
    return _wcsicmp(name, L"explorer.exe") == 0;
}

using LoadLibraryExW_t = decltype(&LoadLibraryExW);
LoadLibraryExW_t LoadLibraryExW_Original;

HMODULE WINAPI LoadLibraryExW_Hook(LPCWSTR lpLibFileName,
                                   HANDLE hFile,
                                   DWORD dwFlags) {
    HMODULE module = LoadLibraryExW_Original(lpLibFileName, hFile, dwFlags);
    if (module) {
        volume_system::OnLoadLibraryExW(module, lpLibFileName);
        if (IsExplorerProcess()) {
            volume_perapp::OnLoadLibraryExW(module, lpLibFileName);
        }
    }
    return module;
}

static void InstallSharedLoadLibraryHook() {
    HMODULE kernelBaseModule = GetModuleHandle(L"kernelbase.dll");
    auto pKernelBaseLoadLibraryExW = (decltype(&LoadLibraryExW))GetProcAddress(
        kernelBaseModule, "LoadLibraryExW");
    WindhawkUtils::Wh_SetFunctionHookT(pKernelBaseLoadLibraryExW,
                                       LoadLibraryExW_Hook,
                                       &LoadLibraryExW_Original);
}

BOOL Wh_ModInit() {
    Wh_Log(L"> volume-pack");
    if (!volume_system::FeatureInit()) {
        return FALSE;
    }
    if (IsExplorerProcess()) {
        if (!volume_perapp::FeatureInit()) {
            Wh_Log(L"per-app FeatureInit failed");
            return FALSE;
        }
        InstallSharedLoadLibraryHook();
    }
    return TRUE;
}

void Wh_ModAfterInit() {
    volume_system::FeatureAfterInit();
    if (IsExplorerProcess()) {
        volume_perapp::FeatureAfterInit();
    }
}

void Wh_ModUninit() {
    if (IsExplorerProcess()) {
        volume_perapp::FeatureUninit();
    }
    volume_system::FeatureUninit();
}

BOOL Wh_ModSettingsChanged(BOOL* bReload) {
    BOOL ok = volume_system::FeatureSettingsChanged(bReload);
    if (IsExplorerProcess()) {
        volume_perapp::FeatureSettingsChanged();
    }
    return ok;
}
'''

    header = '''// ==WindhawkMod==
// @id              taskbar-volume-pack
// @name            Taskbar Volume Pack (system + per-app)
// @description     System volume (tray/scroll) + per-app volume on taskbar buttons — amalgamated for fewer explorer injects
// @version         1.0.0
// @author          Ian (pack) / m417z (upstream features)
// @include         explorer.exe
// @include         ShellExperienceHost.exe
// @include         SndVol.exe
// @architecture    x86-64
// @compilerOptions -lcomctl32 -ldwmapi -lgdi32 -lole32 -loleaut32 -lruntimeobject -lntdll -lversion
// @license         GPL-3.0
// ==/WindhawkMod==

// Amalgamated from taskbar-volume-control + taskbar-volume-control-per-app.
// Upstream GPL-3.0 — keep attributions. Do not enable the two upstream mods
// alongside this pack.

// ==WindhawkModReadme==
/*
# Taskbar Volume Pack

Combines:

* **System volume** — scroll tray / regions / scroll-anywhere (m417z)
* **Per-app volume** — scroll taskbar buttons (m417z)

Default: system scroll area is the **tray** so buttons stay free for per-app.
Disable `taskbar-volume-control` and `taskbar-volume-control-per-app` when using this.
*/
// ==/WindhawkModReadme==

// ==WindhawkModSettings==
/*
'''
    footer_settings = '''
*/
// ==/WindhawkModSettings==

'''
    out = (
        header
        + merged_settings
        + footer_settings
        + "\n".join(includes)
        + "\n\n"
        + sys_feat
        + "\n"
        + app_feat
        + "\n"
        + glue
    )
    dest = SRC / "local@taskbar-volume-pack.wh.cpp"
    dest.write_text(out, encoding="utf-8")
    print(f"wrote {dest} ({dest.stat().st_size} bytes)")
    if "OnLoadLibraryExW" not in sys_feat or "OnLoadLibraryExW" not in app_feat:
        print("WARNING: OnLoadLibraryExW transform may have failed", file=sys.stderr)
    if "LoadLibraryExW_Hook" in sys_feat or "LoadLibraryExW_Hook" in app_feat:
        print("WARNING: leftover LoadLibraryExW_Hook in feature namespaces", file=sys.stderr)


def build_autohide_pack() -> None:
    a_text = read(SRC / "taskbar-auto-hide-when-maximized.wh.cpp")
    b_text = read(SRC / "taskbar-autohide-instant-show.wh.cpp")
    a_settings, a_body = strip_headers(a_text)
    b_settings, b_body = strip_headers(b_text)

    # oldTaskbarOnWin11 shared — keep one key; both LoadSettings read it
    merged_settings = (
        "# === Auto-hide policy (when maximized / intersect) ===\n"
        + a_settings
        + "\n# === Instant show / animation (Bo0ii) ===\n"
        # drop duplicate oldTaskbarOnWin11 from animation block
        + re.sub(
            r"(?ms)^- oldTaskbarOnWin11:.*?^(?=- |\Z)",
            "",
            b_settings,
        )
    )

    a_feat, a_inc = prepare_feature("autohide_policy", a_body, {})
    b_feat, b_inc = prepare_feature("autohide_anim", b_body, {})

    includes = []
    seen = set()
    for inc in ['#include <windhawk_utils.h>'] + a_inc + b_inc:
        if inc not in seen:
            seen.add(inc)
            includes.append(inc)

    glue = r'''
using LoadLibraryExW_t = decltype(&LoadLibraryExW);
LoadLibraryExW_t LoadLibraryExW_Original;

HMODULE WINAPI LoadLibraryExW_Hook(LPCWSTR lpLibFileName,
                                   HANDLE hFile,
                                   DWORD dwFlags) {
    HMODULE module = LoadLibraryExW_Original(lpLibFileName, hFile, dwFlags);
    if (module) {
        autohide_policy::OnLoadLibraryExW(module, lpLibFileName);
        autohide_anim::OnLoadLibraryExW(module, lpLibFileName);
    }
    return module;
}

static void InstallSharedLoadLibraryHook() {
    HMODULE kernelBaseModule = GetModuleHandle(L"kernelbase.dll");
    auto pKernelBaseLoadLibraryExW = (decltype(&LoadLibraryExW))GetProcAddress(
        kernelBaseModule, "LoadLibraryExW");
    WindhawkUtils::Wh_SetFunctionHookT(pKernelBaseLoadLibraryExW,
                                       LoadLibraryExW_Hook,
                                       &LoadLibraryExW_Original);
}

BOOL Wh_ModInit() {
    Wh_Log(L"> autohide-pack");
    if (!autohide_policy::FeatureInit()) {
        return FALSE;
    }
    if (!autohide_anim::FeatureInit()) {
        return FALSE;
    }
    InstallSharedLoadLibraryHook();
    return TRUE;
}

void Wh_ModAfterInit() {
    autohide_policy::FeatureAfterInit();
    autohide_anim::FeatureAfterInit();
}

void Wh_ModUninit() {
    autohide_anim::FeatureUninit();
    autohide_policy::FeatureUninit();
}

BOOL Wh_ModSettingsChanged(BOOL* bReload) {
    BOOL ok = autohide_policy::FeatureSettingsChanged(bReload);
    BOOL ok2 = autohide_anim::FeatureSettingsChanged(bReload);
    return ok && ok2;
}
'''

    header = '''// ==WindhawkMod==
// @id              taskbar-autohide-pack
// @name            Taskbar Autohide Pack (policy + instant show)
// @description     Auto-hide when maximized/intersect + instant show animations — amalgamated
// @version         1.0.0
// @author          Ian (pack) / m417z + Bo0ii (upstream)
// @include         explorer.exe
// @architecture    x86-64
// @compilerOptions -ldwmapi -lole32 -loleaut32 -lversion
// @license         MIT / upstream terms
// ==/WindhawkMod==

// Amalgamated from taskbar-auto-hide-when-maximized + taskbar-autohide-instant-show.
// Disable those two upstream mods when using this pack.

// ==WindhawkModReadme==
/*
# Taskbar Autohide Pack

Combines:

* **Policy** — auto-hide only when maximized / intersecting (m417z)
* **Instant show** — remove edge delay + animation types (Bo0ii)

Disable `taskbar-auto-hide-when-maximized` and `taskbar-autohide-instant-show` when using this.
*/
// ==/WindhawkModReadme==

// ==WindhawkModSettings==
/*
'''
    out = (
        header
        + merged_settings
        + """
*/
// ==/WindhawkModSettings==

"""
        + "\n".join(includes)
        + "\n\n"
        + a_feat
        + "\n"
        + b_feat
        + "\n"
        + glue
    )
    dest = SRC / "local@taskbar-autohide-pack.wh.cpp"
    dest.write_text(out, encoding="utf-8")
    print(f"wrote {dest} ({dest.stat().st_size} bytes)")
    for label, feat in (("policy", a_feat), ("anim", b_feat)):
        if "OnLoadLibraryExW" not in feat:
            print(f"WARNING: {label} OnLoadLibraryExW missing", file=sys.stderr)
        if "LoadLibraryExW_Hook" in feat:
            print(f"WARNING: {label} leftover LoadLibraryExW_Hook", file=sys.stderr)


def main() -> int:
    build_volume_pack()
    build_autohide_pack()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
