// ==WindhawkMod==
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
# === System volume (tray / empty taskbar / scroll-anywhere) ===
- volumeIndicator: win11
  $name: Volume control indicator
  $options:
  - win11: Windows 11
  - modern: Windows 10
  - classic: Windows 7
  - none: None
- scrollArea: notification_area
  $name: Scroll area
  $options:
  - taskbar: The taskbar
  - notification_area: The tray area
  - taskbarWithoutNotificationArea: The taskbar without the tray area
  - none: None (only additional scroll regions)
- additionalScrollRegions: ""
  $name: Additional scroll regions
  $description: >-
    A comma-separated list of additional regions along the taskbar where
    scrolling will control the system volume. Each region is a range like
    "100-200" (pixels) or "20%-50%" (percentage of taskbar length).
- middleClickToMute: true
  $name: Middle click to mute
  $description: >-
    With this option enabled, middle clicking the volume tray icon will
    mute/unmute the system volume (Windows 11 version 22H2 or newer).
- systemCtrlScrollVolumeChange: false
  $name: Ctrl + Scroll to change volume
  $description: >-
    When enabled, scrolling the mouse wheel will only change the volume when
    the Ctrl key is held down.
- scrollAnywhereKeys:
  - shift: false
  - ctrl: false
  - alt: false
  - win: false
  $name: Scroll anywhere modifier keys
  $description: >-
    A combination of modifier keys that, when held, allow controlling the system
    volume by scrolling the mouse wheel anywhere on the screen. Note that
    scrolling won't work when the foreground window is of an elevated process
    (such as Windhawk or Task Manager).
- fullScreenScrolling: disabled
  $name: Full screen scrolling
  $description: >-
    Scroll at the taskbar position to control the system volume, even when the
    taskbar is covered by a full screen window.
  $options:
  - disabled: Disabled
  - withIndicator: Enabled with indicator
  - withoutIndicator: Enabled without indicator
- systemNoAutomaticMuteToggle: false
  $name: No automatic mute toggle
  $description: >-
    For the Windows 11 indicator, this option causes volume scrolling to be
    disabled when the volume is muted. For the other control indicators: By
    default, the output device is muted once the volume reaches zero, and is
    unmuted on any change to a non-zero volume. Enabling this option turns off
    this functionality, such that the device mute status is not changed.
- systemVolumeChangeStep: 2
  $name: Volume change step
  $description: >-
    Allows to configure the volume change that will occur with each notch of
    mouse wheel movement. For the Windows 11 indicator, must be a multiple of
    2.
- oldTaskbarOnWin11: false
  $name: Customize the old taskbar on Windows 11
  $description: >-
    Enable this option to customize the old taskbar on Windows 11 (if using
    ExplorerPatcher or a similar tool).
# === Per-app volume (taskbar buttons) ===
- perAppVolumeChangeStep: 10
  $name: Volume change step
  $description: >-
    Allows to configure the volume change that will occur with each notch of
    mouse wheel movement.
- ctrlClickToMute: true
  $name: Ctrl + Click to mute
  $description: >-
    When enabled, Ctrl+clicking on a taskbar button will toggle the mute state
    of the application.
- perAppCtrlScrollVolumeChange: false
  $name: Ctrl + Scroll to change volume
  $description: >-
    When enabled, scrolling the mouse wheel will only change the volume when
    the Ctrl key is held down.
- terseFormat: false
  $name: Terse format
  $description: >-
    When enabled, the tooltip shows a compact format with emojis instead of
    text (e.g., "🔊 64%" instead of "Volume: 64%").
- perAppNoAutomaticMuteToggle: false
  $name: No automatic mute toggle
  $description: >-
    By default, the app is muted once the volume reaches zero, and is unmuted
    on any change to a non-zero volume. Enabling this option turns off this
    functionality, such that the app mute status is not changed.
*/
// ==/WindhawkModSettings==

#include <windhawk_utils.h>
#include <commctrl.h>
#include <dwmapi.h>
#include <endpointvolume.h>
#include <mmdeviceapi.h>
#include <objbase.h>
#include <psapi.h>
#include <windowsx.h>
#include <algorithm>
#include <atomic>
#include <optional>
#include <string_view>
#include <unordered_set>
#include <vector>
#include <cmath>
#include <functional>
#include <string>
#include <unordered_map>
#include <audiopolicy.h>
#include <tlhelp32.h>
#include <winternl.h>
#undef GetCurrentTime
#include <winrt/Windows.Foundation.Collections.h>
#include <winrt/Windows.UI.Input.h>
#include <winrt/Windows.UI.ViewManagement.h>
#include <winrt/Windows.UI.Xaml.Controls.Primitives.h>
#include <winrt/Windows.UI.Xaml.Controls.h>
#include <winrt/Windows.UI.Xaml.Input.h>
#include <winrt/Windows.UI.Xaml.Media.h>
using namespace winrt::Windows::UI::Xaml;

namespace volume_system {
// pack-includes: #include <windhawk_utils.h>
// pack-includes: #include <commctrl.h>
// pack-includes: #include <dwmapi.h>
    enum class VolumeIndicator {
        None,
        Classic,
        Modern,
        Win11,
    };

    enum class ScrollArea {
        taskbar,
        notificationArea,
        taskbarWithoutNotificationArea,
        none,
    };

    struct Region {
        bool isPercentage;
        int start;
        int end;
    };

    enum class FullScreenScrolling {
        disabled,
        withIndicator,
        withoutIndicator,
    };

    struct {
        VolumeIndicator volumeIndicator;
        ScrollArea scrollArea;
        std::vector<Region> additionalScrollRegions;
        bool middleClickToMute;
        bool ctrlScrollVolumeChange;
        struct {
            bool shift;
            bool ctrl;
            bool alt;
            bool win;
        } scrollAnywhereKeys;
        FullScreenScrolling fullScreenScrolling;
        bool noAutomaticMuteToggle;
        int volumeChangeStep;
        bool oldTaskbarOnWin11;
    } g_settings;

    enum class Target {
        Explorer,
        ShellExperienceHost,
        SndVol,
    };

    Target g_target;

    std::atomic<bool> g_systemTrayModuleHooked;
    std::atomic<bool> g_initialized;
    bool g_inputSiteProcHooked;
    std::unordered_set<HWND> g_secondaryTaskbarWindows;

    UINT g_scrollAnywhereMsg =
        RegisterWindowMessage(L"Windhawk_ScrollAnywhere_" WH_MOD_ID);
    HANDLE g_scrollAnywhereThread;

    enum {
        WIN_VERSION_UNSUPPORTED = 0,
        WIN_VERSION_7,
        WIN_VERSION_8,
        WIN_VERSION_81,
        WIN_VERSION_811,
        WIN_VERSION_10_T1,        // 1507
        WIN_VERSION_10_T2,        // 1511
        WIN_VERSION_10_R1,        // 1607
        WIN_VERSION_10_R2,        // 1703
        WIN_VERSION_10_R3,        // 1709
        WIN_VERSION_10_R4,        // 1803
        WIN_VERSION_10_R5,        // 1809
        WIN_VERSION_10_19H1,      // 1903, 1909
        WIN_VERSION_10_20H1,      // 2004, 20H2, 21H1, 21H2
        WIN_VERSION_SERVER_2022,  // Server 2022
        WIN_VERSION_11_21H2,
        WIN_VERSION_11_22H2,
    };

    #if defined(__GNUC__) && __GNUC__ > 8
    #define WINAPI_LAMBDA_RETURN(return_t) ->return_t WINAPI
    #elif defined(__GNUC__)
    #define WINAPI_LAMBDA_RETURN(return_t) WINAPI->return_t
    #else
    #define WINAPI_LAMBDA_RETURN(return_t) ->return_t
    #endif

    #ifndef WM_POINTERWHEEL
    #define WM_POINTERWHEEL 0x024E
    #endif

    int g_nWinVersion;
    int g_nExplorerVersion;
    HWND g_hTaskbarWnd;
    DWORD g_dwTaskbarThreadId;

    #pragma region functions

    UINT GetDpiForWindowWithFallback(HWND hWnd) {
        using GetDpiForWindow_t = UINT(WINAPI*)(HWND hwnd);
        static GetDpiForWindow_t pGetDpiForWindow = []() {
            HMODULE hUser32 = GetModuleHandle(L"user32.dll");
            if (hUser32) {
                return (GetDpiForWindow_t)GetProcAddress(hUser32,
                                                         "GetDpiForWindow");
            }

            return (GetDpiForWindow_t) nullptr;
        }();

        int iDpi = 96;
        if (pGetDpiForWindow) {
            iDpi = pGetDpiForWindow(hWnd);
        } else {
            HDC hdc = GetDC(NULL);
            if (hdc) {
                iDpi = GetDeviceCaps(hdc, LOGPIXELSX);
                ReleaseDC(NULL, hdc);
            }
        }

        return iDpi;
    }

    bool IsTaskbarWindow(HWND hWnd) {
        WCHAR szClassName[32];
        if (!GetClassName(hWnd, szClassName, ARRAYSIZE(szClassName))) {
            return false;
        }

        return _wcsicmp(szClassName, L"Shell_TrayWnd") == 0 ||
               _wcsicmp(szClassName, L"Shell_SecondaryTrayWnd") == 0;
    }

    bool GetNotificationAreaRect(HWND hMMTaskbarWnd, RECT* rcResult) {
        if (hMMTaskbarWnd == g_hTaskbarWnd) {
            HWND hTrayNotifyWnd =
                FindWindowEx(hMMTaskbarWnd, NULL, L"TrayNotifyWnd", NULL);
            if (hTrayNotifyWnd && GetWindowRect(hTrayNotifyWnd, rcResult) &&
                !IsRectEmpty(rcResult)) {
                return true;
            }

            // When attaching an external monitor, it was observed that the rect can
            // be empty. Use fallback in this case.
        } else if (g_nExplorerVersion >= WIN_VERSION_11_21H2) {
            RECT rcTaskbar;
            if (GetWindowRect(hMMTaskbarWnd, &rcTaskbar)) {
                HWND hBridgeWnd = FindWindowEx(
                    hMMTaskbarWnd, NULL,
                    L"Windows.UI.Composition.DesktopWindowContentBridge", NULL);
                while (hBridgeWnd) {
                    RECT rcBridge;
                    if (!GetWindowRect(hBridgeWnd, &rcBridge)) {
                        break;
                    }

                    if (!EqualRect(&rcBridge, &rcTaskbar)) {
                        if (IsRectEmpty(&rcBridge)) {
                            break;
                        }

                        CopyRect(rcResult, &rcBridge);
                        return true;
                    }

                    hBridgeWnd = FindWindowEx(
                        hMMTaskbarWnd, hBridgeWnd,
                        L"Windows.UI.Composition.DesktopWindowContentBridge", NULL);
                }
            }

            // On newer Win11 versions, the clock on secondary taskbars is difficult
            // to detect without either UI Automation or UWP UI APIs. Use fallback.
        } else if (g_nExplorerVersion >= WIN_VERSION_10_R1) {
            HWND hClockButtonWnd =
                FindWindowEx(hMMTaskbarWnd, NULL, L"ClockButton", NULL);
            if (hClockButtonWnd && GetWindowRect(hClockButtonWnd, rcResult) &&
                !IsRectEmpty(rcResult)) {
                return true;
            }
        } else {
            // In older Windows versions, there's no clock on the secondary taskbar.
            SetRectEmpty(rcResult);
            return true;
        }

        RECT rcTaskbar;
        if (!GetWindowRect(hMMTaskbarWnd, &rcTaskbar)) {
            return false;
        }

        // Just consider the last pixels as a fallback, not accurate, but better
        // than nothing.
        int lastPixels = MulDiv(50, GetDpiForWindowWithFallback(hMMTaskbarWnd), 96);
        CopyRect(rcResult, &rcTaskbar);
        if (rcResult->right - rcResult->left > lastPixels) {
            if (GetWindowLong(hMMTaskbarWnd, GWL_EXSTYLE) & WS_EX_LAYOUTRTL) {
                rcResult->right = rcResult->left + lastPixels;
            } else {
                rcResult->left = rcResult->right - lastPixels;
            }
        }

        return true;
    }

    bool IsPointInsideTaskbarScrollArea(HWND hMMTaskbarWnd, POINT pt) {
        switch (g_settings.scrollArea) {
            case ScrollArea::taskbar: {
                RECT rc;
                return GetWindowRect(hMMTaskbarWnd, &rc) && PtInRect(&rc, pt);
            }

            case ScrollArea::notificationArea: {
                RECT rc;
                return GetNotificationAreaRect(hMMTaskbarWnd, &rc) &&
                       PtInRect(&rc, pt);
            }

            case ScrollArea::taskbarWithoutNotificationArea: {
                RECT rc;
                return GetWindowRect(hMMTaskbarWnd, &rc) && PtInRect(&rc, pt) &&
                       (!GetNotificationAreaRect(hMMTaskbarWnd, &rc) ||
                        !PtInRect(&rc, pt));
            }

            case ScrollArea::none:
                return false;
        }

        return false;
    }

    VS_FIXEDFILEINFO* GetModuleVersionInfo(HMODULE hModule, UINT* puPtrLen) {
        HRSRC hResource;
        HGLOBAL hGlobal;
        void* pData;
        void* pFixedFileInfo;
        UINT uPtrLen;

        pFixedFileInfo = NULL;
        uPtrLen = 0;

        hResource =
            FindResource(hModule, MAKEINTRESOURCE(VS_VERSION_INFO), RT_VERSION);
        if (hResource != NULL) {
            hGlobal = LoadResource(hModule, hResource);
            if (hGlobal != NULL) {
                pData = LockResource(hGlobal);
                if (pData != NULL) {
                    if (!VerQueryValue(pData, L"\\", &pFixedFileInfo, &uPtrLen) ||
                        uPtrLen == 0) {
                        pFixedFileInfo = NULL;
                        uPtrLen = 0;
                    }
                }
            }
        }

        if (puPtrLen)
            *puPtrLen = uPtrLen;

        return (VS_FIXEDFILEINFO*)pFixedFileInfo;
    }

    BOOL WindowsVersionInit() {
        g_nWinVersion = WIN_VERSION_UNSUPPORTED;

        VS_FIXEDFILEINFO* pFixedFileInfo = GetModuleVersionInfo(NULL, NULL);
        if (!pFixedFileInfo)
            return FALSE;

        WORD nMajor = HIWORD(pFixedFileInfo->dwFileVersionMS);
        WORD nMinor = LOWORD(pFixedFileInfo->dwFileVersionMS);
        WORD nBuild = HIWORD(pFixedFileInfo->dwFileVersionLS);
        WORD nQFE = LOWORD(pFixedFileInfo->dwFileVersionLS);

        switch (nMajor) {
            case 6:
                switch (nMinor) {
                    case 1:
                        g_nWinVersion = WIN_VERSION_7;
                        break;

                    case 2:
                        g_nWinVersion = WIN_VERSION_8;
                        break;

                    case 3:
                        if (nQFE < 17000)
                            g_nWinVersion = WIN_VERSION_81;
                        else
                            g_nWinVersion = WIN_VERSION_811;
                        break;

                    case 4:
                        g_nWinVersion = WIN_VERSION_10_T1;
                        break;
                }
                break;

            case 10:
                if (nBuild <= 10240)
                    g_nWinVersion = WIN_VERSION_10_T1;
                else if (nBuild <= 10586)
                    g_nWinVersion = WIN_VERSION_10_T2;
                else if (nBuild <= 14393)
                    g_nWinVersion = WIN_VERSION_10_R1;
                else if (nBuild <= 15063)
                    g_nWinVersion = WIN_VERSION_10_R2;
                else if (nBuild <= 16299)
                    g_nWinVersion = WIN_VERSION_10_R3;
                else if (nBuild <= 17134)
                    g_nWinVersion = WIN_VERSION_10_R4;
                else if (nBuild <= 17763)
                    g_nWinVersion = WIN_VERSION_10_R5;
                else if (nBuild <= 18362)
                    g_nWinVersion = WIN_VERSION_10_19H1;
                else if (nBuild <= 19041)
                    g_nWinVersion = WIN_VERSION_10_20H1;
                else if (nBuild <= 20348)
                    g_nWinVersion = WIN_VERSION_SERVER_2022;
                else if (nBuild <= 22000)
                    g_nWinVersion = WIN_VERSION_11_21H2;
                else
                    g_nWinVersion = WIN_VERSION_11_22H2;
                break;
        }

        if (g_nWinVersion == WIN_VERSION_UNSUPPORTED)
            return FALSE;

        return TRUE;
    }

    #pragma endregion  // functions

    #pragma region regions

    // https://stackoverflow.com/a/54364173
    std::wstring_view TrimStringView(std::wstring_view s) {
        s.remove_prefix(std::min(s.find_first_not_of(L" \t\r\v\n"), s.size()));
        s.remove_suffix(
            std::min(s.size() - s.find_last_not_of(L" \t\r\v\n") - 1, s.size()));
        return s;
    }

    // https://stackoverflow.com/a/46931770
    std::vector<std::wstring_view> SplitStringView(std::wstring_view s,
                                                   std::wstring_view delimiter) {
        size_t pos_start = 0, pos_end, delim_len = delimiter.length();
        std::wstring_view token;
        std::vector<std::wstring_view> res;

        while ((pos_end = s.find(delimiter, pos_start)) !=
               std::wstring_view::npos) {
            token = s.substr(pos_start, pos_end - pos_start);
            pos_start = pos_end + delim_len;
            res.push_back(token);
        }

        res.push_back(s.substr(pos_start));
        return res;
    }

    bool SvToInt(std::wstring_view s, int* result) {
        if (s.empty()) {
            return false;
        }

        int value = 0;
        for (WCHAR c : s) {
            if (c < L'0' || c > L'9') {
                return false;
            }
            int digit = c - L'0';
            if (value > (INT_MAX - digit) / 10) {
                return false;
            }
            value = value * 10 + digit;
        }

        *result = value;
        return true;
    }

    std::optional<Region> ParseRegion(std::wstring_view regionStr) {
        auto parts = SplitStringView(regionStr, L"-");
        if (parts.size() != 2) {
            Wh_Log(L"Invalid region (expected start-end): %.*s",
                   (int)regionStr.size(), regionStr.data());
            return std::nullopt;
        }

        auto startStr = TrimStringView(parts[0]);
        auto endStr = TrimStringView(parts[1]);

        bool startIsPercentage = !startStr.empty() && startStr.back() == L'%';
        bool endIsPercentage = !endStr.empty() && endStr.back() == L'%';
        if (startIsPercentage != endIsPercentage) {
            Wh_Log(L"Invalid region (mixed percent and pixel): %.*s",
                   (int)regionStr.size(), regionStr.data());
            return std::nullopt;
        }

        bool isPercentage = startIsPercentage;
        if (isPercentage) {
            startStr.remove_suffix(1);
            endStr.remove_suffix(1);
        }

        int start;
        int end;
        if (!SvToInt(startStr, &start) || !SvToInt(endStr, &end)) {
            Wh_Log(L"Invalid region (non-numeric values): %.*s",
                   (int)regionStr.size(), regionStr.data());
            return std::nullopt;
        }

        if (start >= end) {
            Wh_Log(L"Invalid region (start must be less than end): %.*s",
                   (int)regionStr.size(), regionStr.data());
            return std::nullopt;
        }

        return Region{isPercentage, start, end};
    }

    bool IsPointInsideAdditionalRegion(HWND hMMTaskbarWnd, POINT pt) {
        if (g_settings.additionalScrollRegions.empty()) {
            return false;
        }

        RECT rc;
        if (!GetWindowRect(hMMTaskbarWnd, &rc) || !PtInRect(&rc, pt)) {
            return false;
        }

        bool isHorizontal = (rc.right - rc.left) >= (rc.bottom - rc.top);
        int taskbarLength;
        int cursorOffset;
        if (isHorizontal) {
            taskbarLength = rc.right - rc.left;
            if (GetWindowLong(hMMTaskbarWnd, GWL_EXSTYLE) & WS_EX_LAYOUTRTL) {
                cursorOffset = rc.right - 1 - pt.x;
            } else {
                cursorOffset = pt.x - rc.left;
            }
        } else {
            taskbarLength = rc.bottom - rc.top;
            cursorOffset = pt.y - rc.top;
        }

        UINT dpi = GetDpiForWindowWithFallback(hMMTaskbarWnd);

        for (const auto& region : g_settings.additionalScrollRegions) {
            int start, end;
            if (region.isPercentage) {
                start = MulDiv(taskbarLength, region.start, 100);
                end = MulDiv(taskbarLength, region.end, 100);
            } else {
                start = MulDiv(region.start, dpi, 96);
                end = MulDiv(region.end, dpi, 96);
            }

            if (cursorOffset >= start && cursorOffset <= end) {
                return true;
            }
        }

        return false;
    }

    bool IsPointInsideScrollArea(HWND hMMTaskbarWnd, POINT pt) {
        return IsPointInsideTaskbarScrollArea(hMMTaskbarWnd, pt) ||
               IsPointInsideAdditionalRegion(hMMTaskbarWnd, pt);
    }

    #pragma endregion  // regions

    #pragma region volume_functions

    const static GUID XIID_IMMDeviceEnumerator = {
        0xA95664D2,
        0x9614,
        0x4F35,
        {0xA7, 0x46, 0xDE, 0x8D, 0xB6, 0x36, 0x17, 0xE6}};
    const static GUID XIID_MMDeviceEnumerator = {
        0xBCDE0395,
        0xE52F,
        0x467C,
        {0x8E, 0x3D, 0xC4, 0x57, 0x92, 0x91, 0x69, 0x2E}};
    const static GUID XIID_IAudioEndpointVolume = {
        0x5CDF2C82,
        0x841E,
        0x4546,
        {0x97, 0x22, 0x0C, 0xF7, 0x40, 0x78, 0x22, 0x9A}};

    static IMMDeviceEnumerator* g_pDeviceEnumerator;

    BOOL IsDefaultAudioEndpointAvailable() {
        IMMDevice* defaultDevice = NULL;
        HRESULT hr;
        BOOL bSuccess = FALSE;

        if (g_pDeviceEnumerator) {
            hr = g_pDeviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole,
                                                              &defaultDevice);
            if (SUCCEEDED(hr)) {
                bSuccess = TRUE;

                defaultDevice->Release();
            }
        }

        return bSuccess;
    }

    BOOL IsVolMuted(BOOL* pbMuted) {
        IMMDevice* defaultDevice = NULL;
        IAudioEndpointVolume* endpointVolume = NULL;
        HRESULT hr;
        BOOL bSuccess = FALSE;

        if (g_pDeviceEnumerator) {
            hr = g_pDeviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole,
                                                              &defaultDevice);
            if (SUCCEEDED(hr)) {
                hr = defaultDevice->Activate(XIID_IAudioEndpointVolume,
                                             CLSCTX_INPROC_SERVER, NULL,
                                             (LPVOID*)&endpointVolume);
                if (SUCCEEDED(hr)) {
                    if (SUCCEEDED(endpointVolume->GetMute(pbMuted)))
                        bSuccess = TRUE;

                    endpointVolume->Release();
                }

                defaultDevice->Release();
            }
        }

        return bSuccess;
    }

    BOOL ToggleVolMuted() {
        IMMDevice* defaultDevice = NULL;
        IAudioEndpointVolume* endpointVolume = NULL;
        HRESULT hr;
        BOOL bMuted;
        BOOL bSuccess = FALSE;

        if (g_pDeviceEnumerator) {
            hr = g_pDeviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole,
                                                              &defaultDevice);
            if (SUCCEEDED(hr)) {
                hr = defaultDevice->Activate(XIID_IAudioEndpointVolume,
                                             CLSCTX_INPROC_SERVER, NULL,
                                             (LPVOID*)&endpointVolume);
                if (SUCCEEDED(hr)) {
                    if (SUCCEEDED(endpointVolume->GetMute(&bMuted))) {
                        if (SUCCEEDED(endpointVolume->SetMute(!bMuted, NULL)))
                            bSuccess = TRUE;
                    }

                    endpointVolume->Release();
                }

                defaultDevice->Release();
            }
        }

        return bSuccess;
    }

    BOOL AddMasterVolumeLevelScalar(float fMasterVolumeAdd) {
        IMMDevice* defaultDevice = NULL;
        IAudioEndpointVolume* endpointVolume = NULL;
        HRESULT hr;
        float fMasterVolume;
        BOOL bSuccess = FALSE;

        if (g_pDeviceEnumerator) {
            hr = g_pDeviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole,
                                                              &defaultDevice);
            if (SUCCEEDED(hr)) {
                hr = defaultDevice->Activate(XIID_IAudioEndpointVolume,
                                             CLSCTX_INPROC_SERVER, NULL,
                                             (LPVOID*)&endpointVolume);
                if (SUCCEEDED(hr)) {
                    if (SUCCEEDED(endpointVolume->GetMasterVolumeLevelScalar(
                            &fMasterVolume))) {
                        fMasterVolume += fMasterVolumeAdd;

                        if (fMasterVolume < 0.0)
                            fMasterVolume = 0.0;
                        else if (fMasterVolume > 1.0)
                            fMasterVolume = 1.0;

                        if (SUCCEEDED(endpointVolume->SetMasterVolumeLevelScalar(
                                fMasterVolume, NULL))) {
                            bSuccess = TRUE;

                            if (!g_settings.noAutomaticMuteToggle) {
                                // Windows displays the volume rounded to the
                                // nearest percentage. The range [0, 0.005) is
                                // displayed as 0%, [0.005, 0.015) as 1%, etc. It
                                // also mutes the volume when it becomes zero, we do
                                // the same.

                                if (fMasterVolume < 0.005)
                                    endpointVolume->SetMute(TRUE, NULL);
                                else
                                    endpointVolume->SetMute(FALSE, NULL);
                            }
                        }
                    }

                    endpointVolume->Release();
                }

                defaultDevice->Release();
            }
        }

        return bSuccess;
    }

    void SndVolInit() {
        HRESULT hr = CoCreateInstance(
            XIID_MMDeviceEnumerator, NULL, CLSCTX_INPROC_SERVER,
            XIID_IMMDeviceEnumerator, (LPVOID*)&g_pDeviceEnumerator);
        if (FAILED(hr))
            g_pDeviceEnumerator = NULL;
    }

    void SndVolUninit() {
        if (g_pDeviceEnumerator) {
            g_pDeviceEnumerator->Release();
            g_pDeviceEnumerator = NULL;
        }
    }

    #pragma endregion  // volume_functions

    #pragma region sndvol_win11

    UINT g_uShellHookMsg = RegisterWindowMessage(L"SHELLHOOK");
    DWORD g_lastScrollTime;
    short g_lastScrollDeltaRemainder;

    bool PostAppCommand(SHORT appCommand, int count) {
        if (!g_hTaskbarWnd) {
            return false;
        }

        HWND hReBarWindow32 =
            FindWindowEx(g_hTaskbarWnd, nullptr, L"ReBarWindow32", nullptr);
        if (!hReBarWindow32) {
            return false;
        }

        HWND hMSTaskSwWClass =
            FindWindowEx(hReBarWindow32, nullptr, L"MSTaskSwWClass", nullptr);
        if (!hMSTaskSwWClass) {
            return false;
        }

        for (int i = 0; i < count; i++) {
            PostMessage(hMSTaskSwWClass, g_uShellHookMsg, HSHELL_APPCOMMAND,
                        MAKELPARAM(0, appCommand));
        }

        return true;
    }

    bool Win11IndicatorAdjustVolumeLevelWithMouseWheel(short delta) {
        BOOL muted;
        if (g_settings.noAutomaticMuteToggle && IsVolMuted(&muted) && muted) {
            return true;
        }

        if (GetTickCount() - g_lastScrollTime < 1000 * 5) {
            delta += g_lastScrollDeltaRemainder;
        }

        int clicks = delta / WHEEL_DELTA;
        Wh_Log(L"%d clicks (delta=%d)", clicks, delta);

        if (clicks) {
            SHORT appCommand = APPCOMMAND_VOLUME_UP;
            if (clicks < 0) {
                clicks = -clicks;
                appCommand = APPCOMMAND_VOLUME_DOWN;
            }

            if (g_settings.volumeChangeStep) {
                clicks *= g_settings.volumeChangeStep / 2;
            }

            if (clicks > 1) {
                AddMasterVolumeLevelScalar(
                    (appCommand == APPCOMMAND_VOLUME_UP ? 0.02f : -0.02f) *
                    (float)(clicks - 1));
            }

            if (!PostAppCommand(appCommand, 1)) {
                return false;
            }
        }

        g_lastScrollTime = GetTickCount();
        g_lastScrollDeltaRemainder = delta % WHEEL_DELTA;

        return true;
    }

    #pragma endregion  // sndvol_win11

    #pragma region sndvol

    BOOL OpenScrollSndVol(WPARAM wParam, LPARAM lMousePosParam);
    void SetSndVolTimer();
    void KillSndVolTimer();
    void CleanupSndVol();

    static BOOL AdjustVolumeLevelWithMouseWheel(int nWheelDelta, int nStep);
    static BOOL OpenScrollSndVolInternal(WPARAM wParam,
                                         LPARAM lMousePosParam,
                                         HWND hVolumeAppWnd,
                                         BOOL* pbOpened);
    static BOOL ValidateSndVolProcess();
    static BOOL ValidateSndVolWnd();
    static void CALLBACK CloseSndVolTimerProc(HWND hWnd,
                                              UINT uMsg,
                                              UINT_PTR idEvent,
                                              DWORD dwTime);
    static HWND GetSndVolDlg(HWND hVolumeAppWnd);
    static BOOL CALLBACK EnumThreadFindSndVolWnd(HWND hWnd, LPARAM lParam);
    static BOOL IsSndVolWndInitialized(HWND hWnd);
    static BOOL MoveSndVolCenterMouse(HWND hWnd);

    // Modern indicator functions
    static BOOL CanUseModernIndicator();
    static BOOL ShowSndVolModernIndicator();
    static BOOL HideSndVolModernIndicator();
    static void EndSndVolModernIndicatorSession();
    static HWND GetOpenSndVolModernIndicatorWnd();
    static HWND GetSndVolTrayControlWnd();
    static BOOL CALLBACK EnumThreadFindSndVolTrayControlWnd(HWND hWnd,
                                                            LPARAM lParam);

    static HANDLE hSndVolProcess;
    static HWND hSndVolWnd;
    static UINT_PTR nCloseSndVolTimer;
    static int nCloseSndVolTimerCount;
    static HWND hSndVolModernPreviousForegroundWnd;
    static BOOL bSndVolModernLaunched;
    static BOOL bSndVolModernAppeared;

    BOOL OpenScrollSndVol(WPARAM wParam, LPARAM lMousePosParam) {
        HANDLE hMutex;
        HWND hVolumeAppWnd;
        DWORD dwProcessId;
        WCHAR szCommandLine[sizeof("SndVol.exe -f 4294967295")];
        STARTUPINFO si;
        PROCESS_INFORMATION pi;

        if (g_settings.volumeIndicator == VolumeIndicator::Win11 &&
            g_nWinVersion >= WIN_VERSION_11_22H2) {
            return Win11IndicatorAdjustVolumeLevelWithMouseWheel(
                GET_WHEEL_DELTA_WPARAM(wParam));
        }

        if (g_settings.volumeIndicator == VolumeIndicator::None) {
            return AdjustVolumeLevelWithMouseWheel(GET_WHEEL_DELTA_WPARAM(wParam),
                                                   0);
        }

        if (CanUseModernIndicator()) {
            if (!AdjustVolumeLevelWithMouseWheel(GET_WHEEL_DELTA_WPARAM(wParam), 0))
                return FALSE;

            ShowSndVolModernIndicator();
            SetSndVolTimer();
            return TRUE;
        }

        if (!IsDefaultAudioEndpointAvailable())
            return FALSE;

        if (!AdjustVolumeLevelWithMouseWheel(GET_WHEEL_DELTA_WPARAM(wParam), 0))
            return FALSE;

        if (ValidateSndVolProcess()) {
            // If not initializing
            if (WaitForInputIdle(hSndVolProcess, 0) == 0) {
                if (ValidateSndVolWnd()) {
                    // False because we didn't open it, it was open
                    return FALSE;
                }

                hVolumeAppWnd = FindWindow(L"Windows Volume App Window",
                                           L"Windows Volume App Window");
                if (hVolumeAppWnd) {
                    GetWindowThreadProcessId(hVolumeAppWnd, &dwProcessId);

                    if (GetProcessId(hSndVolProcess) == dwProcessId) {
                        BOOL bOpened;
                        if (OpenScrollSndVolInternal(wParam, lMousePosParam,
                                                     hVolumeAppWnd, &bOpened)) {
                            if (bOpened)
                                SetSndVolTimer();

                            return bOpened;
                        }
                    }
                }
            }

            return FALSE;
        }

        hMutex = OpenMutex(SYNCHRONIZE, FALSE, L"Windows Volume App Window");
        if (hMutex) {
            CloseHandle(hMutex);

            hVolumeAppWnd = FindWindow(L"Windows Volume App Window",
                                       L"Windows Volume App Window");
            if (hVolumeAppWnd) {
                GetWindowThreadProcessId(hVolumeAppWnd, &dwProcessId);

                hSndVolProcess =
                    OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE,
                                FALSE, dwProcessId);
                if (hSndVolProcess) {
                    // if not initializing
                    if (WaitForInputIdle(hSndVolProcess, 0) == 0) {
                        if (ValidateSndVolWnd()) {
                            // False because we didn't open it, it was open
                            return FALSE;
                        }

                        BOOL bOpened;
                        if (OpenScrollSndVolInternal(wParam, lMousePosParam,
                                                     hVolumeAppWnd, &bOpened)) {
                            if (bOpened)
                                SetSndVolTimer();

                            return bOpened;
                        }
                    }
                }
            }

            return FALSE;
        }

        wsprintf(szCommandLine, L"SndVol.exe -f %u", (DWORD)lMousePosParam);

        ZeroMemory(&si, sizeof(STARTUPINFO));
        si.cb = sizeof(STARTUPINFO);

        if (!CreateProcess(NULL, szCommandLine, NULL, NULL, FALSE,
                           ABOVE_NORMAL_PRIORITY_CLASS | CREATE_SUSPENDED, NULL,
                           NULL, &si, &pi))
            return FALSE;

        if (g_nExplorerVersion <= WIN_VERSION_7)
            SendMessage(g_hTaskbarWnd, WM_USER + 12, 0, 0);  // Close start menu

        AllowSetForegroundWindow(pi.dwProcessId);
        ResumeThread(pi.hThread);

        CloseHandle(pi.hThread);
        hSndVolProcess = pi.hProcess;

        SetSndVolTimer();

        return TRUE;
    }

    void SetSndVolTimer() {
        nCloseSndVolTimer =
            SetTimer(NULL, nCloseSndVolTimer, 100, CloseSndVolTimerProc);
        nCloseSndVolTimerCount = 0;
    }

    void KillSndVolTimer() {
        if (nCloseSndVolTimer != 0) {
            KillTimer(NULL, nCloseSndVolTimer);
            nCloseSndVolTimer = 0;
        }
    }

    void CleanupSndVol() {
        KillSndVolTimer();

        if (hSndVolProcess) {
            CloseHandle(hSndVolProcess);
            hSndVolProcess = NULL;
            hSndVolWnd = NULL;
        }
    }

    static BOOL AdjustVolumeLevelWithMouseWheel(int nWheelDelta, int nStep) {
        if (!nStep) {
            nStep = g_settings.volumeChangeStep;
            if (!nStep)
                nStep = 2;
        }

        return AddMasterVolumeLevelScalar((float)nWheelDelta * nStep *
                                          ((float)0.01 / 120));
    }

    static BOOL OpenScrollSndVolInternal(WPARAM wParam,
                                         LPARAM lMousePosParam,
                                         HWND hVolumeAppWnd,
                                         BOOL* pbOpened) {
        HWND hSndVolDlg = GetSndVolDlg(hVolumeAppWnd);
        if (hSndVolDlg) {
            if (GetWindowTextLength(hSndVolDlg) == 0)  // Volume control
            {
                if (IsSndVolWndInitialized(hSndVolDlg) &&
                    MoveSndVolCenterMouse(hSndVolDlg)) {
                    if (g_nExplorerVersion <= WIN_VERSION_7)
                        SendMessage(g_hTaskbarWnd, WM_USER + 12, 0,
                                    0);  // Close start menu

                    SetForegroundWindow(hVolumeAppWnd);
                    PostMessage(hVolumeAppWnd, WM_USER + 35, 0, 0);

                    *pbOpened = TRUE;
                    return TRUE;
                }
            } else if (IsWindowVisible(
                           hSndVolDlg))  // Another dialog, e.g. volume mixer
            {
                if (g_nExplorerVersion <= WIN_VERSION_7)
                    SendMessage(g_hTaskbarWnd, WM_USER + 12, 0,
                                0);  // Close start menu

                SetForegroundWindow(hVolumeAppWnd);
                PostMessage(hVolumeAppWnd, WM_USER + 35, 0, 0);

                *pbOpened = FALSE;
                return TRUE;
            }
        }

        return FALSE;
    }

    static BOOL ValidateSndVolProcess() {
        if (!hSndVolProcess)
            return FALSE;

        if (WaitForSingleObject(hSndVolProcess, 0) != WAIT_TIMEOUT) {
            CloseHandle(hSndVolProcess);
            hSndVolProcess = NULL;
            hSndVolWnd = NULL;

            return FALSE;
        }

        return TRUE;
    }

    static BOOL ValidateSndVolWnd() {
        HWND hForegroundWnd;
        DWORD dwProcessId;
        WCHAR szClass[sizeof("#32770") + 1];

        hForegroundWnd = GetForegroundWindow();

        if (hSndVolWnd == hForegroundWnd)
            return TRUE;

        GetWindowThreadProcessId(hForegroundWnd, &dwProcessId);

        if (GetProcessId(hSndVolProcess) == dwProcessId) {
            GetClassName(hForegroundWnd, szClass, sizeof("#32770") + 1);

            if (lstrcmp(szClass, L"#32770") == 0) {
                hSndVolWnd = hForegroundWnd;

                return TRUE;
            }
        }

        hSndVolWnd = NULL;

        return FALSE;
    }

    static void CALLBACK CloseSndVolTimerProc(HWND hWnd,
                                              UINT uMsg,
                                              UINT_PTR idEvent,
                                              DWORD dwTime) {
        if (CanUseModernIndicator()) {
            HWND hSndVolModernIndicatorWnd = GetOpenSndVolModernIndicatorWnd();
            if (!bSndVolModernAppeared) {
                if (hSndVolModernIndicatorWnd) {
                    bSndVolModernAppeared = TRUE;
                    nCloseSndVolTimerCount = 1;

                    // Windows 11 shows an ugly focus border. Make it go away by
                    // making the window think it becomes inactive.
                    if (g_nWinVersion >= WIN_VERSION_11_21H2) {
                        PostMessage(hSndVolModernIndicatorWnd, WM_ACTIVATE,
                                    MAKEWPARAM(WA_INACTIVE, FALSE), 0);
                    }

                    return;
                } else {
                    nCloseSndVolTimerCount++;
                    if (nCloseSndVolTimerCount < 10)
                        return;
                }
            } else {
                if (hSndVolModernIndicatorWnd) {
                    POINT pt;
                    GetCursorPos(&pt);
                    HWND hPointWnd = GetAncestor(WindowFromPoint(pt), GA_ROOT);

                    if (!hPointWnd)
                        nCloseSndVolTimerCount++;
                    else if (hPointWnd == hSndVolModernIndicatorWnd)
                        nCloseSndVolTimerCount = 0;
                    else if (IsTaskbarWindow(hPointWnd) &&
                             IsPointInsideScrollArea(hPointWnd, pt))
                        nCloseSndVolTimerCount = 0;
                    else
                        nCloseSndVolTimerCount++;

                    if (nCloseSndVolTimerCount < 10)
                        return;

                    HideSndVolModernIndicator();
                }
            }

            EndSndVolModernIndicatorSession();
        } else {
            if (ValidateSndVolProcess()) {
                if (WaitForInputIdle(hSndVolProcess, 0) != 0)
                    return;

                if (ValidateSndVolWnd()) {
                    POINT pt;
                    GetCursorPos(&pt);
                    HWND hPointWnd = GetAncestor(WindowFromPoint(pt), GA_ROOT);

                    if (!hPointWnd)
                        nCloseSndVolTimerCount++;
                    else if (hPointWnd == hSndVolWnd)
                        nCloseSndVolTimerCount = 0;
                    else if (IsTaskbarWindow(hPointWnd) &&
                             IsPointInsideScrollArea(hPointWnd, pt))
                        nCloseSndVolTimerCount = 0;
                    else
                        nCloseSndVolTimerCount++;

                    if (nCloseSndVolTimerCount < 10)
                        return;

                    if (hPointWnd != hSndVolWnd)
                        PostMessage(hSndVolWnd, WM_ACTIVATE,
                                    MAKEWPARAM(WA_INACTIVE, FALSE), (LPARAM)NULL);
                }
            }
        }

        KillTimer(NULL, nCloseSndVolTimer);
        nCloseSndVolTimer = 0;
    }

    static HWND GetSndVolDlg(HWND hVolumeAppWnd) {
        HWND hWnd = NULL;
        EnumThreadWindows(GetWindowThreadProcessId(hVolumeAppWnd, NULL),
                          EnumThreadFindSndVolWnd, (LPARAM)&hWnd);
        return hWnd;
    }

    static BOOL CALLBACK EnumThreadFindSndVolWnd(HWND hWnd, LPARAM lParam) {
        WCHAR szClass[16];

        GetClassName(hWnd, szClass, _countof(szClass));
        if (lstrcmp(szClass, L"#32770") == 0) {
            *(HWND*)lParam = hWnd;
            return FALSE;
        }

        return TRUE;
    }

    static BOOL IsSndVolWndInitialized(HWND hWnd) {
        HWND hChildDlg;

        hChildDlg = FindWindowEx(hWnd, NULL, L"#32770", NULL);
        if (!hChildDlg)
            return FALSE;

        if (!(GetWindowLong(hChildDlg, GWL_STYLE) & WS_VISIBLE))
            return FALSE;

        return TRUE;
    }

    static BOOL MoveSndVolCenterMouse(HWND hWnd) {
        NOTIFYICONIDENTIFIER notifyiconidentifier;
        BOOL bCompositionEnabled;
        POINT pt;
        SIZE size;
        RECT rc, rcExclude, rcInflate;
        int nInflate;

        ZeroMemory(&notifyiconidentifier, sizeof(NOTIFYICONIDENTIFIER));
        notifyiconidentifier.cbSize = sizeof(NOTIFYICONIDENTIFIER);
        memcpy(&notifyiconidentifier.guidItem,
               "\x73\xAE\x20\x78\xE3\x23\x29\x42\x82\xC1\xE4\x1C\xB6\x7D\x5B\x9C",
               sizeof(GUID));

        if (Shell_NotifyIconGetRect(&notifyiconidentifier, &rcExclude) != S_OK)
            SetRectEmpty(&rcExclude);

        GetCursorPos(&pt);
        GetWindowRect(hWnd, &rc);

        nInflate = 0;

        if (DwmIsCompositionEnabled(&bCompositionEnabled) == S_OK &&
            bCompositionEnabled) {
            memcpy(
                &notifyiconidentifier.guidItem,
                "\x43\x65\x4B\x96\xAD\xBB\xEE\x44\x84\x8A\x3A\x95\xD8\x59\x51\xEA",
                sizeof(GUID));

            if (Shell_NotifyIconGetRect(&notifyiconidentifier, &rcInflate) ==
                S_OK) {
                nInflate = rcInflate.bottom - rcInflate.top;
                InflateRect(&rc, nInflate, nInflate);
            }
        }

        size.cx = rc.right - rc.left;
        size.cy = rc.bottom - rc.top;

        if (!CalculatePopupWindowPosition(
                &pt, &size,
                TPM_CENTERALIGN | TPM_VCENTERALIGN | TPM_VERTICAL | TPM_WORKAREA,
                &rcExclude, &rc))
            return FALSE;

        SetWindowPos(
            hWnd, NULL, rc.left + nInflate, rc.top + nInflate, 0, 0,
            SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_ASYNCWINDOWPOS);

        return TRUE;
    }

    // Modern indicator functions

    static BOOL CanUseModernIndicator() {
        if (g_nWinVersion < WIN_VERSION_10_T1 ||
            g_settings.volumeIndicator == VolumeIndicator::Classic)
            return FALSE;

        DWORD dwEnabled = 1;
        DWORD dwValueSize = sizeof(dwEnabled);
        DWORD dwError = RegGetValue(
            HKEY_LOCAL_MACHINE,
            L"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\MTCUVC",
            L"EnableMTCUVC", RRF_RT_REG_DWORD, NULL, &dwEnabled, &dwValueSize);

        // We don't check dwError just like Microsoft doesn't at SndVolSSO.dll.
        if (!dwError)
            Wh_Log(L"%u", dwError);

        return dwEnabled != 0;
    }

    static BOOL ShowSndVolModernIndicator() {
        if (bSndVolModernLaunched)
            return TRUE;  // already launched

        HWND hSndVolModernIndicatorWnd = GetOpenSndVolModernIndicatorWnd();
        if (hSndVolModernIndicatorWnd)
            return TRUE;  // already shown

        HWND hForegroundWnd = GetForegroundWindow();
        if (hForegroundWnd && hForegroundWnd != g_hTaskbarWnd)
            hSndVolModernPreviousForegroundWnd = hForegroundWnd;

        HWND hSndVolTrayControlWnd = GetSndVolTrayControlWnd();
        if (!hSndVolTrayControlWnd)
            return FALSE;

        if (!PostMessage(hSndVolTrayControlWnd, 0x460, 0,
                         MAKELPARAM(NIN_SELECT, 100)))
            return FALSE;

        bSndVolModernLaunched = TRUE;
        return TRUE;
    }

    static BOOL HideSndVolModernIndicator() {
        HWND hSndVolModernIndicatorWnd = GetOpenSndVolModernIndicatorWnd();
        if (hSndVolModernIndicatorWnd) {
            if (!hSndVolModernPreviousForegroundWnd ||
                !SetForegroundWindow(hSndVolModernPreviousForegroundWnd))
                SetForegroundWindow(g_hTaskbarWnd);
        }

        return TRUE;
    }

    static void EndSndVolModernIndicatorSession() {
        hSndVolModernPreviousForegroundWnd = NULL;
        bSndVolModernLaunched = FALSE;
        bSndVolModernAppeared = FALSE;
    }

    static HWND GetOpenSndVolModernIndicatorWnd() {
        HWND hForegroundWnd = GetForegroundWindow();
        if (!hForegroundWnd)
            return NULL;

        // Check class name
        WCHAR szBuffer[32];
        if (!GetClassName(hForegroundWnd, szBuffer, 32) ||
            wcscmp(szBuffer, L"Windows.UI.Core.CoreWindow") != 0)
            return NULL;

        // Check that the MtcUvc prop exists
        WCHAR szVerifyPropName[sizeof(
            "ApplicationView_CustomWindowTitle#1234567890#MtcUvc")];
        wsprintf(szVerifyPropName, L"ApplicationView_CustomWindowTitle#%u#MtcUvc",
                 (DWORD)(DWORD_PTR)hForegroundWnd);

        SetLastError(0);
        GetProp(hForegroundWnd, szVerifyPropName);
        if (GetLastError() != 0)
            return NULL;

        return hForegroundWnd;
    }

    static HWND GetSndVolTrayControlWnd() {
        // The window we're looking for has a class name similar to
        // "ATL:00007FFAECBBD280". It shares a thread with the bluetooth window,
        // which is easier to find by class, so we use that.

        HWND hBluetoothNotificationWnd =
            FindWindow(L"BluetoothNotificationAreaIconWindowClass", NULL);
        if (!hBluetoothNotificationWnd)
            return NULL;

        HWND hWnd = NULL;
        EnumThreadWindows(GetWindowThreadProcessId(hBluetoothNotificationWnd, NULL),
                          EnumThreadFindSndVolTrayControlWnd, (LPARAM)&hWnd);
        return hWnd;
    }

    static BOOL CALLBACK EnumThreadFindSndVolTrayControlWnd(HWND hWnd,
                                                            LPARAM lParam) {
        HMODULE hInstance = (HMODULE)GetWindowLongPtr(hWnd, GWLP_HINSTANCE);
        if (hInstance && hInstance == GetModuleHandle(L"sndvolsso.dll")) {
            *(HWND*)lParam = hWnd;
            return FALSE;
        }

        return TRUE;
    }

    #pragma endregion  // sndvol

    ////////////////////////////////////////////////////////////

    bool OnMouseWheel(HWND hWnd, WPARAM wParam, LPARAM lParam) {
        if (GetCapture()) {
            return false;
        }

        if (g_settings.ctrlScrollVolumeChange && GetKeyState(VK_CONTROL) >= 0) {
            return false;
        }

        POINT pt;
        pt.x = GET_X_LPARAM(lParam);
        pt.y = GET_Y_LPARAM(lParam);

        if (!IsPointInsideScrollArea(hWnd, pt)) {
            return false;
        }

        // Allows to steal focus.
        INPUT input;
        ZeroMemory(&input, sizeof(INPUT));
        SendInput(1, &input, sizeof(INPUT));

        OpenScrollSndVol(wParam, lParam);

        return true;
    }

    LRESULT CALLBACK TaskbarWindowSubclassProc(_In_ HWND hWnd,
                                               _In_ UINT uMsg,
                                               _In_ WPARAM wParam,
                                               _In_ LPARAM lParam,
                                               _In_ DWORD_PTR dwRefData) {
        LRESULT result = 0;

        switch (uMsg) {
            case WM_COPYDATA: {
                result = DefSubclassProc(hWnd, uMsg, wParam, lParam);

                typedef struct _notifyiconidentifier_internal {
                    DWORD dwMagic;    // 0x34753423
                    DWORD dwRequest;  // 1 for (x,y) | 2 for (w,h)
                    DWORD cbSize;     // 0x20
                    DWORD hWndHigh;
                    DWORD hWndLow;
                    UINT uID;
                    GUID guidItem;
                } NOTIFYICONIDENTIFIER_INTERNAL;

                COPYDATASTRUCT* p_copydata = (COPYDATASTRUCT*)lParam;

                // Change Shell_NotifyIconGetRect handling result for the volume
                // icon. In case it's not visible, or in Windows 11, it returns 0,
                // which causes sndvol.exe to ignore the command line position.
                if (result == 0 && p_copydata->dwData == 0x03 &&
                    p_copydata->cbData == sizeof(NOTIFYICONIDENTIFIER_INTERNAL)) {
                    NOTIFYICONIDENTIFIER_INTERNAL* p_icon_ident =
                        (NOTIFYICONIDENTIFIER_INTERNAL*)p_copydata->lpData;
                    if (p_icon_ident->dwMagic == 0x34753423 &&
                        (p_icon_ident->dwRequest == 0x01 ||
                         p_icon_ident->dwRequest == 0x02) &&
                        p_icon_ident->cbSize == 0x20 &&
                        memcmp(&p_icon_ident->guidItem,
                               "\x73\xAE\x20\x78\xE3\x23\x29\x42\x82\xC1\xE4"
                               "\x1C\xB6\x7D\x5B\x9C",
                               sizeof(GUID)) == 0) {
                        RECT rc;
                        GetWindowRect(hWnd, &rc);

                        if (p_icon_ident->dwRequest == 0x01)
                            result = MAKEWORD(rc.left, rc.top);
                        else
                            result =
                                MAKEWORD(rc.right - rc.left, rc.bottom - rc.top);
                    }
                }
                break;
            }

            case WM_MOUSEWHEEL:
                if (g_nExplorerVersion < WIN_VERSION_11_21H2 &&
                    OnMouseWheel(hWnd, wParam, lParam)) {
                    result = 0;
                } else {
                    result = DefSubclassProc(hWnd, uMsg, wParam, lParam);
                }
                break;

            case WM_NCDESTROY:
                result = DefSubclassProc(hWnd, uMsg, wParam, lParam);

                if (hWnd != g_hTaskbarWnd) {
                    g_secondaryTaskbarWindows.erase(hWnd);
                }
                break;

            default:
                if (uMsg == g_scrollAnywhereMsg) {
                    if (LOWORD(wParam) == 1) {
                        AdjustVolumeLevelWithMouseWheel(
                            GET_WHEEL_DELTA_WPARAM(wParam), 0);
                    } else {
                        OpenScrollSndVol(wParam, lParam);
                    }
                    result = 0;
                } else {
                    result = DefSubclassProc(hWnd, uMsg, wParam, lParam);
                }
                break;
        }

        return result;
    }

    WNDPROC InputSiteWindowProc_Original;
    LRESULT CALLBACK InputSiteWindowProc_Hook(HWND hWnd,
                                              UINT uMsg,
                                              WPARAM wParam,
                                              LPARAM lParam) {
        switch (uMsg) {
            case WM_POINTERWHEEL:
                if (HWND hRootWnd = GetAncestor(hWnd, GA_ROOT);
                    IsTaskbarWindow(hRootWnd) &&
                    OnMouseWheel(hRootWnd, wParam, lParam)) {
                    return 0;
                }
                break;
        }

        return InputSiteWindowProc_Original(hWnd, uMsg, wParam, lParam);
    }

    void SubclassTaskbarWindow(HWND hWnd) {
        WindhawkUtils::SetWindowSubclassFromAnyThread(hWnd,
                                                      TaskbarWindowSubclassProc, 0);
    }

    void UnsubclassTaskbarWindow(HWND hWnd) {
        WindhawkUtils::RemoveWindowSubclassFromAnyThread(hWnd,
                                                         TaskbarWindowSubclassProc);
    }

    void HandleIdentifiedInputSiteWindow(HWND hWnd) {
        if (!g_dwTaskbarThreadId ||
            GetWindowThreadProcessId(hWnd, nullptr) != g_dwTaskbarThreadId) {
            return;
        }

        HWND hParentWnd = GetParent(hWnd);
        WCHAR szClassName[64];
        if (!hParentWnd ||
            !GetClassName(hParentWnd, szClassName, ARRAYSIZE(szClassName)) ||
            _wcsicmp(szClassName,
                     L"Windows.UI.Composition.DesktopWindowContentBridge") != 0) {
            return;
        }

        hParentWnd = GetParent(hParentWnd);
        if (!hParentWnd || !IsTaskbarWindow(hParentWnd)) {
            return;
        }

        // At first, I tried to subclass the window instead of hooking its wndproc,
        // but the inputsite.dll code checks that the value wasn't changed, and
        // crashes otherwise.
        auto wndProc = (WNDPROC)GetWindowLongPtr(hWnd, GWLP_WNDPROC);
        WindhawkUtils::SetFunctionHook(wndProc, InputSiteWindowProc_Hook,
                                       &InputSiteWindowProc_Original);

        if (g_initialized) {
            Wh_ApplyHookOperations();
        }

        Wh_Log(L"Hooked InputSite wndproc %p", wndProc);
        g_inputSiteProcHooked = true;
    }

    void HandleIdentifiedTaskbarWindow(HWND hWnd) {
        g_hTaskbarWnd = hWnd;
        g_dwTaskbarThreadId = GetWindowThreadProcessId(hWnd, nullptr);
        SndVolInit();
        SubclassTaskbarWindow(hWnd);
        for (HWND hSecondaryWnd : g_secondaryTaskbarWindows) {
            SubclassTaskbarWindow(hSecondaryWnd);
        }

        if (g_nExplorerVersion >= WIN_VERSION_11_21H2 && !g_inputSiteProcHooked) {
            HWND hXamlIslandWnd = FindWindowEx(
                hWnd, nullptr, L"Windows.UI.Composition.DesktopWindowContentBridge",
                nullptr);
            if (hXamlIslandWnd) {
                HWND hInputSiteWnd = FindWindowEx(
                    hXamlIslandWnd, nullptr,
                    L"Windows.UI.Input.InputSite.WindowClass", nullptr);
                if (hInputSiteWnd) {
                    HandleIdentifiedInputSiteWindow(hInputSiteWnd);
                }
            }
        }
    }

    void HandleIdentifiedSecondaryTaskbarWindow(HWND hWnd) {
        if (!g_dwTaskbarThreadId ||
            GetWindowThreadProcessId(hWnd, nullptr) != g_dwTaskbarThreadId) {
            return;
        }

        g_secondaryTaskbarWindows.insert(hWnd);
        SubclassTaskbarWindow(hWnd);

        if (g_nExplorerVersion >= WIN_VERSION_11_21H2 && !g_inputSiteProcHooked) {
            HWND hXamlIslandWnd = FindWindowEx(
                hWnd, nullptr, L"Windows.UI.Composition.DesktopWindowContentBridge",
                nullptr);
            if (hXamlIslandWnd) {
                HWND hInputSiteWnd = FindWindowEx(
                    hXamlIslandWnd, nullptr,
                    L"Windows.UI.Input.InputSite.WindowClass", nullptr);
                if (hInputSiteWnd) {
                    HandleIdentifiedInputSiteWindow(hInputSiteWnd);
                }
            }
        }
    }

    HWND FindCurrentProcessTaskbarWindows(
        std::unordered_set<HWND>* secondaryTaskbarWindows) {
        struct ENUM_WINDOWS_PARAM {
            HWND* hWnd;
            std::unordered_set<HWND>* secondaryTaskbarWindows;
        };

        HWND hWnd = nullptr;
        ENUM_WINDOWS_PARAM param = {&hWnd, secondaryTaskbarWindows};
        EnumWindows(
            [](HWND hWnd, LPARAM lParam) WINAPI_LAMBDA_RETURN(BOOL) {
                ENUM_WINDOWS_PARAM& param = *(ENUM_WINDOWS_PARAM*)lParam;

                DWORD dwProcessId = 0;
                if (!GetWindowThreadProcessId(hWnd, &dwProcessId) ||
                    dwProcessId != GetCurrentProcessId())
                    return TRUE;

                WCHAR szClassName[32];
                if (GetClassName(hWnd, szClassName, ARRAYSIZE(szClassName)) == 0)
                    return TRUE;

                if (_wcsicmp(szClassName, L"Shell_TrayWnd") == 0) {
                    *param.hWnd = hWnd;
                } else if (_wcsicmp(szClassName, L"Shell_SecondaryTrayWnd") == 0) {
                    param.secondaryTaskbarWindows->insert(hWnd);
                }

                return TRUE;
            },
            (LPARAM)&param);

        return hWnd;
    }

    using CreateWindowExW_t = decltype(&CreateWindowExW);
    CreateWindowExW_t CreateWindowExW_Original;
    HWND WINAPI CreateWindowExW_Hook(DWORD dwExStyle,
                                     LPCWSTR lpClassName,
                                     LPCWSTR lpWindowName,
                                     DWORD dwStyle,
                                     int X,
                                     int Y,
                                     int nWidth,
                                     int nHeight,
                                     HWND hWndParent,
                                     HMENU hMenu,
                                     HINSTANCE hInstance,
                                     LPVOID lpParam) {
        HWND hWnd = CreateWindowExW_Original(dwExStyle, lpClassName, lpWindowName,
                                             dwStyle, X, Y, nWidth, nHeight,
                                             hWndParent, hMenu, hInstance, lpParam);
        if (!hWnd)
            return hWnd;

        BOOL bTextualClassName = ((ULONG_PTR)lpClassName & ~(ULONG_PTR)0xffff) != 0;

        if (bTextualClassName && _wcsicmp(lpClassName, L"Shell_TrayWnd") == 0) {
            Wh_Log(L"Taskbar window created: %08X", (DWORD)(ULONG_PTR)hWnd);
            HandleIdentifiedTaskbarWindow(hWnd);
        } else if (bTextualClassName &&
                   _wcsicmp(lpClassName, L"Shell_SecondaryTrayWnd") == 0) {
            Wh_Log(L"Secondary taskbar window created: %08X",
                   (DWORD)(ULONG_PTR)hWnd);
            HandleIdentifiedSecondaryTaskbarWindow(hWnd);
        }

        return hWnd;
    }

    using CreateWindowInBand_t = HWND(WINAPI*)(DWORD dwExStyle,
                                               LPCWSTR lpClassName,
                                               LPCWSTR lpWindowName,
                                               DWORD dwStyle,
                                               int X,
                                               int Y,
                                               int nWidth,
                                               int nHeight,
                                               HWND hWndParent,
                                               HMENU hMenu,
                                               HINSTANCE hInstance,
                                               LPVOID lpParam,
                                               DWORD dwBand);
    CreateWindowInBand_t CreateWindowInBand_Original;
    HWND WINAPI CreateWindowInBand_Hook(DWORD dwExStyle,
                                        LPCWSTR lpClassName,
                                        LPCWSTR lpWindowName,
                                        DWORD dwStyle,
                                        int X,
                                        int Y,
                                        int nWidth,
                                        int nHeight,
                                        HWND hWndParent,
                                        HMENU hMenu,
                                        HINSTANCE hInstance,
                                        LPVOID lpParam,
                                        DWORD dwBand) {
        HWND hWnd = CreateWindowInBand_Original(
            dwExStyle, lpClassName, lpWindowName, dwStyle, X, Y, nWidth, nHeight,
            hWndParent, hMenu, hInstance, lpParam, dwBand);
        if (!hWnd)
            return hWnd;

        BOOL bTextualClassName = ((ULONG_PTR)lpClassName & ~(ULONG_PTR)0xffff) != 0;

        if (bTextualClassName &&
            _wcsicmp(lpClassName, L"Windows.UI.Input.InputSite.WindowClass") == 0) {
            Wh_Log(L"InputSite window created: %08X", (DWORD)(ULONG_PTR)hWnd);
            if (g_nExplorerVersion >= WIN_VERSION_11_21H2 &&
                !g_inputSiteProcHooked) {
                HandleIdentifiedInputSiteWindow(hWnd);
            }
        }

        return hWnd;
    }

    using ForceFocusBasedMouseWheelRouting_t = DWORD_PTR(WINAPI*)(BOOL enabled);
    ForceFocusBasedMouseWheelRouting_t ForceFocusBasedMouseWheelRouting_Original;
    DWORD_PTR WINAPI ForceFocusBasedMouseWheelRouting_Hook(BOOL enabled) {
        Wh_Log(L">");

        // Always disable to prevent the volume control from stealing mouse wheel
        // messages.
        return ForceFocusBasedMouseWheelRouting_Original(FALSE);
    }

    void LoadSettings() {
        PCWSTR volumeIndicator = Wh_GetStringSetting(L"volumeIndicator");
        g_settings.volumeIndicator = VolumeIndicator::Win11;
        if (wcscmp(volumeIndicator, L"modern") == 0) {
            g_settings.volumeIndicator = VolumeIndicator::Modern;
        } else if (wcscmp(volumeIndicator, L"classic") == 0) {
            g_settings.volumeIndicator = VolumeIndicator::Classic;
        } else if (wcscmp(volumeIndicator, L"none") == 0) {
            g_settings.volumeIndicator = VolumeIndicator::None;
        } else {
            // Old option for compatibility.
            if (wcscmp(volumeIndicator, L"tooltip") == 0) {
                g_settings.volumeIndicator = VolumeIndicator::None;
            }
        }
        Wh_FreeStringSetting(volumeIndicator);

        PCWSTR scrollArea = Wh_GetStringSetting(L"scrollArea");
        g_settings.scrollArea = ScrollArea::taskbar;
        if (wcscmp(scrollArea, L"notification_area") == 0) {
            g_settings.scrollArea = ScrollArea::notificationArea;
        } else if (wcscmp(scrollArea, L"taskbarWithoutNotificationArea") == 0) {
            g_settings.scrollArea = ScrollArea::taskbarWithoutNotificationArea;
        } else if (wcscmp(scrollArea, L"none") == 0) {
            g_settings.scrollArea = ScrollArea::none;
        }
        Wh_FreeStringSetting(scrollArea);

        g_settings.middleClickToMute = Wh_GetIntSetting(L"middleClickToMute");
        g_settings.ctrlScrollVolumeChange =
            Wh_GetIntSetting(L"systemCtrlScrollVolumeChange");
        g_settings.scrollAnywhereKeys.shift =
            Wh_GetIntSetting(L"scrollAnywhereKeys.shift");
        g_settings.scrollAnywhereKeys.ctrl =
            Wh_GetIntSetting(L"scrollAnywhereKeys.ctrl");
        g_settings.scrollAnywhereKeys.alt =
            Wh_GetIntSetting(L"scrollAnywhereKeys.alt");
        g_settings.scrollAnywhereKeys.win =
            Wh_GetIntSetting(L"scrollAnywhereKeys.win");

        PCWSTR fullScreenScrolling = Wh_GetStringSetting(L"fullScreenScrolling");
        g_settings.fullScreenScrolling = FullScreenScrolling::disabled;
        if (wcscmp(fullScreenScrolling, L"withIndicator") == 0) {
            g_settings.fullScreenScrolling = FullScreenScrolling::withIndicator;
        } else if (wcscmp(fullScreenScrolling, L"withoutIndicator") == 0) {
            g_settings.fullScreenScrolling = FullScreenScrolling::withoutIndicator;
        }
        Wh_FreeStringSetting(fullScreenScrolling);

        g_settings.noAutomaticMuteToggle =
            Wh_GetIntSetting(L"systemNoAutomaticMuteToggle");
        g_settings.volumeChangeStep = Wh_GetIntSetting(L"systemVolumeChangeStep");
        g_settings.oldTaskbarOnWin11 = Wh_GetIntSetting(L"oldTaskbarOnWin11");

        g_settings.additionalScrollRegions.clear();
        PCWSTR additionalScrollRegions =
            Wh_GetStringSetting(L"additionalScrollRegions");
        for (auto regionStr : SplitStringView(additionalScrollRegions, L",")) {
            regionStr = TrimStringView(regionStr);
            if (regionStr.empty()) {
                continue;
            }
            if (auto region = ParseRegion(regionStr)) {
                g_settings.additionalScrollRegions.push_back(*region);
            }
        }
        Wh_FreeStringSetting(additionalScrollRegions);
    }

    // The return type is int to match the produce<> COM thunk variant below, which
    // returns an HRESULT. For the standalone implementation variant (which returns
    // void), its caller is a thin thunk that overwrites the return value, so the
    // returned value is harmlessly discarded.
    using VolumeSystemTrayIconDataModel_OnIconClicked_t =
        int(WINAPI*)(void* pThis, void* param1);
    VolumeSystemTrayIconDataModel_OnIconClicked_t
        VolumeSystemTrayIconDataModel_OnIconClicked_Original;
    int WINAPI VolumeSystemTrayIconDataModel_OnIconClicked_Hook(void* pThis,
                                                                void* param1) {
        Wh_Log(L">");

        if (g_settings.middleClickToMute && GetKeyState(VK_MBUTTON) < 0) {
            ToggleVolMuted();
            return 0;  // S_OK
        }

        return VolumeSystemTrayIconDataModel_OnIconClicked_Original(pThis, param1);
    }

    bool HookSystemTraySymbols(HMODULE module) {
        // In SystemTray.dll, the implementation function was inlined into the
        // produce<> COM thunk, so hook that.
        bool isSystemTrayDll = module == GetModuleHandle(L"SystemTray.dll");

        // SystemTray.dll, Taskbar.View.dll
        WindhawkUtils::SYMBOL_HOOK symbolHooks[] = {
            {
                {isSystemTrayDll
                     ? LR"(public: virtual int __cdecl winrt::impl::produce<struct winrt::SystemTray::implementation::VolumeSystemTrayIconDataModel,struct winrt::SystemTray::IIconDataModel>::OnIconClicked(void *))"
                     : LR"(public: void __cdecl winrt::SystemTray::implementation::VolumeSystemTrayIconDataModel::OnIconClicked(struct winrt::SystemTray::IconClickedEventArgs const &))"},
                &VolumeSystemTrayIconDataModel_OnIconClicked_Original,
                VolumeSystemTrayIconDataModel_OnIconClicked_Hook,
                true,
            },
        };

        if (!HookSymbols(module, symbolHooks, ARRAYSIZE(symbolHooks))) {
            Wh_Log(L"HookSymbols failed");
            return false;
        }

        return true;
    }

    HMODULE GetSystemTrayModuleHandle() {
        HMODULE module = GetModuleHandle(L"SystemTray.dll");
        if (!module) {
            module = GetModuleHandle(L"Taskbar.View.dll");
            if (module) {
                // Starting with Taskbar.View.dll 2604.8002.200.6000, the SystemTray
                // types moved out of Taskbar.View.dll into SystemTray.dll, so don't
                // hook Taskbar.View.dll at this version and above.
                VS_FIXEDFILEINFO* fixedFileInfo =
                    GetModuleVersionInfo(module, nullptr);
                WORD moduleMajor =
                    fixedFileInfo ? HIWORD(fixedFileInfo->dwFileVersionMS) : 0;
                if (!moduleMajor || moduleMajor >= 2604) {
                    Wh_Log(L"Skipping Taskbar.View.dll version %d", moduleMajor);
                    module = nullptr;
                }
            }
        }
        if (!module) {
            module = GetModuleHandle(L"ExplorerExtensions.dll");
        }

        return module;
    }

    bool ShouldHookSystemTraySymbols() {
        return g_nWinVersion >= WIN_VERSION_11_22H2 && g_settings.middleClickToMute;
    }

    void HandleLoadedModuleIfSystemTray(HMODULE module, LPCWSTR lpLibFileName) {
        if (ShouldHookSystemTraySymbols() && !g_systemTrayModuleHooked &&
            GetSystemTrayModuleHandle() == module &&
            !g_systemTrayModuleHooked.exchange(true)) {
            Wh_Log(L"Loaded %s", lpLibFileName);

            if (HookSystemTraySymbols(module)) {
                Wh_ApplyHookOperations();
            }
        }
    }

    bool IsExplorerPatcherModule(HMODULE module) {
        WCHAR moduleFilePath[MAX_PATH];
        switch (
            GetModuleFileName(module, moduleFilePath, ARRAYSIZE(moduleFilePath))) {
            case 0:
            case ARRAYSIZE(moduleFilePath):
                return false;
        }

        PCWSTR moduleFileName = wcsrchr(moduleFilePath, L'\\');
        if (!moduleFileName) {
            return false;
        }

        moduleFileName++;

        if (_wcsnicmp(L"ep_taskbar.", moduleFileName, sizeof("ep_taskbar.") - 1) ==
            0) {
            Wh_Log(L"ExplorerPatcher taskbar module: %s", moduleFileName);
            return true;
        }

        return false;
    }

    void HandleLoadedExplorerPatcher() {
        HMODULE hMods[1024];
        DWORD cbNeeded;
        if (EnumProcessModules(GetCurrentProcess(), hMods, sizeof(hMods),
                               &cbNeeded)) {
            for (size_t i = 0; i < cbNeeded / sizeof(HMODULE); i++) {
                if (IsExplorerPatcherModule(hMods[i])) {
                    if (g_nExplorerVersion >= WIN_VERSION_11_21H2) {
                        g_nExplorerVersion = WIN_VERSION_10_20H1;
                    }
                    break;
                }
            }
        }
    }

    void HandleLoadedModuleIfExplorerPatcher(HMODULE module) {
        if (module && !((ULONG_PTR)module & 3)) {
            if (IsExplorerPatcherModule(module)) {
                if (g_nExplorerVersion >= WIN_VERSION_11_21H2) {
                    g_nExplorerVersion = WIN_VERSION_10_20H1;
                }
            }
        }
    }

    void OnLoadLibraryExW(HMODULE module, LPCWSTR lpLibFileName) {
        if (module) {
            HandleLoadedModuleIfExplorerPatcher(module);
            HandleLoadedModuleIfSystemTray(module, lpLibFileName);
        }
    }

    bool IsScrollAnywhereEnabled() {
        return g_settings.scrollAnywhereKeys.shift ||
               g_settings.scrollAnywhereKeys.ctrl ||
               g_settings.scrollAnywhereKeys.alt ||
               g_settings.scrollAnywhereKeys.win;
    }

    bool IsMouseHookNeeded() {
        return IsScrollAnywhereEnabled() ||
               g_settings.fullScreenScrolling != FullScreenScrolling::disabled;
    }

    bool AreScrollAnywhereModifiersHeld() {
        bool shiftKeyState = GetAsyncKeyState(VK_SHIFT) < 0;
        bool ctrlKeyState = GetAsyncKeyState(VK_CONTROL) < 0;
        bool altKeyState = GetAsyncKeyState(VK_MENU) < 0;
        bool winKeyState =
            (GetAsyncKeyState(VK_LWIN) < 0) || (GetAsyncKeyState(VK_RWIN) < 0);

        return g_settings.scrollAnywhereKeys.shift == shiftKeyState &&
               g_settings.scrollAnywhereKeys.ctrl == ctrlKeyState &&
               g_settings.scrollAnywhereKeys.alt == altKeyState &&
               g_settings.scrollAnywhereKeys.win == winKeyState;
    }

    // Using the Win or Alt key as a scroll-anywhere modifier would trigger a menu
    // on release: a lone Win tap opens the Start menu, and a lone Alt tap activates
    // the window's menu bar. To prevent this, the mouse hook flags the key as used
    // for scrolling, and the keyboard hook below masks its release: it suppresses
    // the real key-up and re-injects a dummy key (0xE8, unassigned) before it, so
    // Windows sees a non-modifier key and skips the menu. 0xE8 is the masking key
    // recommended by AutoHotkey for exactly this, both for Win and Alt:
    // https://www.autohotkey.com/docs/v2/lib/A_MenuMaskKey.htm
    //
    // Masking must happen at release time, not during the scroll, since holding the
    // key auto-repeats key-down events that would re-arm the lone-tap detection.
    struct ModifierMaskState {
        bool down;
        bool usedForScroll;
    };

    ModifierMaskState g_winMaskState;
    ModifierMaskState g_altMaskState;

    // Returns true if the original key-up was suppressed and re-sent masked, in
    // which case the caller should swallow it.
    bool MaskModifierKeyEvent(ModifierMaskState* state,
                              WPARAM wParam,
                              KBDLLHOOKSTRUCT* pKbdStruct) {
        if (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN) {
            // Reset the flag on the initial press, but not on auto-repeat events
            // (which keep firing while the key is held).
            if (!state->down) {
                state->down = true;
                state->usedForScroll = false;
            }
        } else if (wParam == WM_KEYUP || wParam == WM_SYSKEYUP) {
            state->down = false;

            // Ignore injected key-ups (such as the one we re-send below) to avoid
            // masking them again.
            if (state->usedForScroll && !(pKbdStruct->flags & LLKHF_INJECTED)) {
                state->usedForScroll = false;

                INPUT input[3] = {};
                input[0].type = INPUT_KEYBOARD;
                input[0].ki.wVk = 0xE8;
                input[1].type = INPUT_KEYBOARD;
                input[1].ki.wVk = 0xE8;
                input[1].ki.dwFlags = KEYEVENTF_KEYUP;
                // Faithfully replay the original key-up. The extended-key flag must
                // be preserved, otherwise extended modifiers (right Alt/AltGr and
                // the Win keys) may not be released correctly and could get stuck
                // down.
                input[2].type = INPUT_KEYBOARD;
                input[2].ki.wVk = (WORD)pKbdStruct->vkCode;
                input[2].ki.wScan = (WORD)pKbdStruct->scanCode;
                input[2].ki.dwFlags = KEYEVENTF_KEYUP;
                if (pKbdStruct->flags & LLKHF_EXTENDED) {
                    input[2].ki.dwFlags |= KEYEVENTF_EXTENDEDKEY;
                }

                // Only suppress the original key-up if we managed to re-send the
                // whole sequence, otherwise the key would get stuck down (e.g. when
                // SendInput is blocked by an elevated foreground window).
                if (SendInput(ARRAYSIZE(input), input, sizeof(INPUT)) ==
                    ARRAYSIZE(input)) {
                    return true;
                }
            }
        }

        return false;
    }

    LRESULT CALLBACK LowLevelKeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
        if (nCode != HC_ACTION) {
            return CallNextHookEx(nullptr, nCode, wParam, lParam);
        }

        KBDLLHOOKSTRUCT* pKbdStruct = (KBDLLHOOKSTRUCT*)lParam;

        ModifierMaskState* state = nullptr;
        switch (pKbdStruct->vkCode) {
            case VK_LWIN:
            case VK_RWIN:
                state = &g_winMaskState;
                break;
            case VK_LMENU:
            case VK_RMENU:
                state = &g_altMaskState;
                break;
        }

        if (state && MaskModifierKeyEvent(state, wParam, pKbdStruct)) {
            return 1;
        }

        return CallNextHookEx(nullptr, nCode, wParam, lParam);
    }

    LRESULT CALLBACK LowLevelMouseProc(int nCode, WPARAM wParam, LPARAM lParam) {
        if (nCode != HC_ACTION || wParam != WM_MOUSEWHEEL) {
            return CallNextHookEx(nullptr, nCode, wParam, lParam);
        }

        HWND hTaskbarWnd = g_hTaskbarWnd;
        if (!hTaskbarWnd) {
            return CallNextHookEx(nullptr, nCode, wParam, lParam);
        }

        MSLLHOOKSTRUCT* pMouseStruct = (MSLLHOOKSTRUCT*)lParam;

        // Scroll anywhere: modifier keys held.
        if (IsScrollAnywhereEnabled() && AreScrollAnywhereModifiersHeld()) {
            // Mark the Win/Alt keys as used so that the keyboard hook masks their
            // release and no menu (Start menu / menu bar) opens.
            if (g_settings.scrollAnywhereKeys.win) {
                g_winMaskState.usedForScroll = true;
            }
            if (g_settings.scrollAnywhereKeys.alt) {
                g_altMaskState.usedForScroll = true;
            }
            PostMessage(hTaskbarWnd, g_scrollAnywhereMsg,
                        MAKEWPARAM(0, HIWORD(pMouseStruct->mouseData)),
                        MAKELPARAM(pMouseStruct->pt.x, pMouseStruct->pt.y));
            return 1;
        }

        // Full screen scrolling: cursor in taskbar region but taskbar not visible.
        if (g_settings.fullScreenScrolling != FullScreenScrolling::disabled) {
            POINT pt = pMouseStruct->pt;

            HWND hPointWnd = WindowFromPoint(pt);
            if (hPointWnd) {
                HWND hRootWnd = GetAncestor(hPointWnd, GA_ROOT);
                if (hRootWnd && IsTaskbarWindow(hRootWnd)) {
                    return CallNextHookEx(nullptr, nCode, wParam, lParam);
                }
            }

            bool isInScrollArea = false;

            if (IsPointInsideScrollArea(hTaskbarWnd, pt)) {
                isInScrollArea = true;
            }

            if (!isInScrollArea) {
                DWORD dwTaskbarThreadId = g_dwTaskbarThreadId;
                if (dwTaskbarThreadId) {
                    // EnumThreadWindows returns FALSE if the callback returned
                    // FALSE, i.e. a match was found.
                    if (!EnumThreadWindows(
                            dwTaskbarThreadId,
                            [](HWND hWnd, LPARAM lParam)
                                WINAPI_LAMBDA_RETURN(BOOL) {
                                    WCHAR szClassName[32];
                                    if (GetClassName(hWnd, szClassName,
                                                     ARRAYSIZE(szClassName)) &&
                                        _wcsicmp(szClassName,
                                                 L"Shell_SecondaryTrayWnd") == 0) {
                                        if (IsPointInsideScrollArea(
                                                hWnd, *(POINT*)lParam)) {
                                            return FALSE;
                                        }
                                    }
                                    return TRUE;
                                },
                            (LPARAM)&pt)) {
                        isInScrollArea = true;
                    }
                }
            }

            if (isInScrollArea) {
                WORD mode = (g_settings.fullScreenScrolling ==
                             FullScreenScrolling::withoutIndicator)
                                ? 1
                                : 0;
                PostMessage(hTaskbarWnd, g_scrollAnywhereMsg,
                            MAKEWPARAM(mode, HIWORD(pMouseStruct->mouseData)),
                            MAKELPARAM(pt.x, pt.y));
                return 1;
            }
        }

        return CallNextHookEx(nullptr, nCode, wParam, lParam);
    }

    DWORD WINAPI ScrollAnywhereThread(LPVOID lpParameter) {
        HANDLE hReadyEvent = (HANDLE)lpParameter;

        g_winMaskState = {};
        g_altMaskState = {};

        HHOOK mouseHook =
            SetWindowsHookEx(WH_MOUSE_LL, LowLevelMouseProc, nullptr, 0);

        // Only needed to mask the Win/Alt key release, see LowLevelKeyboardProc.
        HHOOK keyboardHook = nullptr;
        if (g_settings.scrollAnywhereKeys.win || g_settings.scrollAnywhereKeys.alt) {
            keyboardHook =
                SetWindowsHookEx(WH_KEYBOARD_LL, LowLevelKeyboardProc, nullptr, 0);
        }

        SetEvent(hReadyEvent);

        if (!mouseHook) {
            Wh_Log(L"SetWindowsHookEx failed: %u", GetLastError());
            if (keyboardHook) {
                UnhookWindowsHookEx(keyboardHook);
            }
            return 1;
        }

        BOOL bRet;
        MSG msg;
        while ((bRet = GetMessage(&msg, nullptr, 0, 0)) != 0) {
            if (bRet == -1) {
                break;
            }

            if (msg.hwnd == nullptr && msg.message == WM_APP) {
                PostQuitMessage(0);
                continue;
            }

            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }

        if (keyboardHook) {
            UnhookWindowsHookEx(keyboardHook);
        }
        UnhookWindowsHookEx(mouseHook);
        return 0;
    }

    void ScrollAnywhereThreadInit() {
        if (g_scrollAnywhereThread) {
            return;
        }

        HANDLE hReadyEvent = CreateEvent(nullptr, TRUE, FALSE, nullptr);
        if (!hReadyEvent) {
            return;
        }

        g_scrollAnywhereThread =
            CreateThread(nullptr, 0, ScrollAnywhereThread, hReadyEvent, 0, nullptr);
        if (g_scrollAnywhereThread) {
            WaitForSingleObject(hReadyEvent, INFINITE);
        }

        CloseHandle(hReadyEvent);
    }

    void ScrollAnywhereThreadUninit() {
        if (g_scrollAnywhereThread) {
            PostThreadMessage(GetThreadId(g_scrollAnywhereThread), WM_APP, 0, 0);
            WaitForSingleObject(g_scrollAnywhereThread, INFINITE);
            CloseHandle(g_scrollAnywhereThread);
            g_scrollAnywhereThread = nullptr;
        }
    }

    BOOL FeatureInit() {
        Wh_Log(L">");

        LoadSettings();

        if (!WindowsVersionInit()) {
            Wh_Log(L"Unsupported Windows version");
            return FALSE;
        }

        g_target = Target::Explorer;

        WCHAR moduleFilePath[MAX_PATH];
        switch (
            GetModuleFileName(nullptr, moduleFilePath, ARRAYSIZE(moduleFilePath))) {
            case 0:
            case ARRAYSIZE(moduleFilePath):
                Wh_Log(L"GetModuleFileName failed");
                return FALSE;

            default:
                if (PCWSTR moduleFileName = wcsrchr(moduleFilePath, L'\\')) {
                    moduleFileName++;
                    if (_wcsicmp(moduleFileName, L"ShellExperienceHost.exe") == 0) {
                        g_target = Target::ShellExperienceHost;
                    } else if (_wcsicmp(moduleFileName, L"SndVol.exe") == 0) {
                        g_target = Target::SndVol;
                    }
                } else {
                    Wh_Log(L"GetModuleFileName returned an unsupported path");
                    return FALSE;
                }
                break;
        }

        if (g_target == Target::ShellExperienceHost || g_target == Target::SndVol) {
            if (g_settings.volumeChangeStep == 2 &&
                !g_settings.noAutomaticMuteToggle) {
                return FALSE;
            }

            if (g_target == Target::ShellExperienceHost) {
                bool useModernIndicator =
                    g_settings.volumeIndicator == VolumeIndicator::Modern &&
                    CanUseModernIndicator();
                if (!useModernIndicator) {
                    return FALSE;
                }
            } else if (g_target == Target::SndVol) {
                bool useClassicIndicator =
                    g_settings.volumeIndicator == VolumeIndicator::Classic ||
                    (g_settings.volumeIndicator == VolumeIndicator::Modern &&
                     !CanUseModernIndicator());
                if (!useClassicIndicator) {
                    return FALSE;
                }
            }

            HMODULE user32Module = GetModuleHandle(L"user32.dll");
            if (user32Module) {
                auto pFunc = (ForceFocusBasedMouseWheelRouting_t)GetProcAddress(
                    user32Module, MAKEINTRESOURCEA(2575));
                if (pFunc) {
                    WindhawkUtils::SetFunctionHook(
                        pFunc, ForceFocusBasedMouseWheelRouting_Hook,
                        &ForceFocusBasedMouseWheelRouting_Original);
                }
            }

            return TRUE;
        }

        g_nExplorerVersion = g_nWinVersion;
        if (g_nExplorerVersion >= WIN_VERSION_11_21H2 &&
            g_settings.oldTaskbarOnWin11) {
            g_nExplorerVersion = WIN_VERSION_10_20H1;
        }

        if (ShouldHookSystemTraySymbols()) {
            if (HMODULE systemTrayModule = GetSystemTrayModuleHandle()) {
                g_systemTrayModuleHooked = true;
                if (!HookSystemTraySymbols(systemTrayModule)) {
                    return FALSE;
                }
            } else {
                Wh_Log(L"System tray module not loaded yet");
            }
        }

        WindhawkUtils::SetFunctionHook(CreateWindowExW, CreateWindowExW_Hook,
                                       &CreateWindowExW_Original);

        HMODULE user32Module =
            LoadLibraryEx(L"user32.dll", nullptr, LOAD_LIBRARY_SEARCH_SYSTEM32);
        if (user32Module) {
            auto pCreateWindowInBand = (CreateWindowInBand_t)GetProcAddress(
                user32Module, "CreateWindowInBand");
            if (pCreateWindowInBand) {
                WindhawkUtils::SetFunctionHook(pCreateWindowInBand,
                                               CreateWindowInBand_Hook,
                                               &CreateWindowInBand_Original);
            }
        }

        HandleLoadedExplorerPatcher();
    g_initialized = true;

        return TRUE;
    }

    void FeatureAfterInit() {
        Wh_Log(L">");

        if (g_target != Target::Explorer) {
            return;
        }

        if (ShouldHookSystemTraySymbols() && !g_systemTrayModuleHooked) {
            if (HMODULE systemTrayModule = GetSystemTrayModuleHandle()) {
                if (!g_systemTrayModuleHooked.exchange(true)) {
                    Wh_Log(L"Got system tray module");

                    if (HookSystemTraySymbols(systemTrayModule)) {
                        Wh_ApplyHookOperations();
                    }
                }
            }
        }

        // Try again in case there's a race between the previous attempt and the
        // LoadLibraryExW hook.
        HandleLoadedExplorerPatcher();

        WNDCLASS wndclass;
        if (GetClassInfo(GetModuleHandle(NULL), L"Shell_TrayWnd", &wndclass)) {
            HWND hWnd =
                FindCurrentProcessTaskbarWindows(&g_secondaryTaskbarWindows);
            if (hWnd) {
                HandleIdentifiedTaskbarWindow(hWnd);
            }
        }

        if (IsMouseHookNeeded()) {
            ScrollAnywhereThreadInit();
        }
    }

    void FeatureUninit() {
        Wh_Log(L">");

        if (g_target != Target::Explorer) {
            return;
        }

        ScrollAnywhereThreadUninit();

        if (g_hTaskbarWnd) {
            UnsubclassTaskbarWindow(g_hTaskbarWnd);

            for (HWND hSecondaryWnd : g_secondaryTaskbarWindows) {
                UnsubclassTaskbarWindow(hSecondaryWnd);
            }
        }

        CleanupSndVol();
        SndVolUninit();
    }

    BOOL FeatureSettingsChanged(BOOL* bReload) {
        Wh_Log(L">");

        bool prevOldTaskbarOnWin11 = g_settings.oldTaskbarOnWin11;
        bool prevMiddleClickToMute = g_settings.middleClickToMute;

        LoadSettings();

        if (g_target == Target::ShellExperienceHost || g_target == Target::SndVol) {
            if (g_settings.volumeChangeStep == 2 &&
                !g_settings.noAutomaticMuteToggle) {
                return FALSE;
            }

            if (g_target == Target::ShellExperienceHost) {
                bool useModernIndicator =
                    g_settings.volumeIndicator == VolumeIndicator::Modern &&
                    CanUseModernIndicator();
                if (!useModernIndicator) {
                    return FALSE;
                }
            } else if (g_target == Target::SndVol) {
                bool useClassicIndicator =
                    g_settings.volumeIndicator == VolumeIndicator::Classic ||
                    (g_settings.volumeIndicator == VolumeIndicator::Modern &&
                     !CanUseModernIndicator());
                if (!useClassicIndicator) {
                    return FALSE;
                }
            }

            return TRUE;
        }

        *bReload = g_settings.oldTaskbarOnWin11 != prevOldTaskbarOnWin11 ||
                   g_settings.middleClickToMute != prevMiddleClickToMute;
        if (!*bReload) {
            ScrollAnywhereThreadUninit();
            if (IsMouseHookNeeded()) {
                ScrollAnywhereThreadInit();
            }
        }

        return TRUE;
    }
}  // namespace volume_system

namespace volume_perapp {
// pack-includes: #include <windhawk_utils.h>
// pack-includes: #include <atomic>
// pack-includes: #include <cmath>
    struct {
        int volumeChangeStep;
        bool ctrlClickToMute;
        bool ctrlScrollVolumeChange;
        bool terseFormat;
        bool noAutomaticMuteToggle;
    } g_settings;

    std::atomic<bool> g_taskbarViewDllLoaded;

    IMMDeviceEnumerator* g_pDeviceEnumerator;

    // Per-app volume: taskbar button integration.
    thread_local bool g_captureTaskGroup;
    thread_local void* g_capturedTaskGroup;

    // Click sentinel pattern for getting native task item/group from WindowsUdk.
    WCHAR g_clickSentinel[] = L"click-sentinel";
    void* g_clickSentinel_TaskGroup = nullptr;
    void* g_clickSentinel_TaskItem = nullptr;

    void* QueryViaVtable(void* object, void* vtable) {
        void* ptr = object;
        while (*(void**)ptr != vtable) {
            ptr = (void**)ptr + 1;
        }
        return ptr;
    }

    const GUID XIID_IMMDeviceEnumerator = {
        0xA95664D2,
        0x9614,
        0x4F35,
        {0xA7, 0x46, 0xDE, 0x8D, 0xB6, 0x36, 0x17, 0xE6}};
    const GUID XIID_MMDeviceEnumerator = {
        0xBCDE0395,
        0xE52F,
        0x467C,
        {0x8E, 0x3D, 0xC4, 0x57, 0x92, 0x91, 0x69, 0x2E}};
    const GUID XIID_IAudioSessionManager2 = {
        0x77AA99A0,
        0x1BD6,
        0x484F,
        {0x8B, 0xC7, 0x2C, 0x65, 0x4C, 0x9A, 0x9B, 0x6F}};

    void SndVolInit() {
        HRESULT hr = CoCreateInstance(
            XIID_MMDeviceEnumerator, NULL, CLSCTX_INPROC_SERVER,
            XIID_IMMDeviceEnumerator, (LPVOID*)&g_pDeviceEnumerator);
        if (FAILED(hr)) {
            g_pDeviceEnumerator = NULL;
        }
    }

    void SndVolUninit() {
        if (g_pDeviceEnumerator) {
            g_pDeviceEnumerator->Release();
            g_pDeviceEnumerator = NULL;
        }
    }

    // Callback type for processing audio sessions.
    // Receives the session's process ID and session control interface.
    // Returns true to continue iterating, false to stop.
    using AudioSessionCallback =
        std::function<bool(DWORD pid, IAudioSessionControl2* sessionControl)>;

    // Iterates over all audio sessions.
    // Calls the callback for each session with its PID and IAudioSessionControl2.
    // Returns true if at least one session was processed.
    bool ForEachAudioSession(const AudioSessionCallback& callback) {
        if (!g_pDeviceEnumerator) {
            SndVolInit();
            if (!g_pDeviceEnumerator) {
                return false;
            }
        }

        winrt::com_ptr<IMMDevice> defaultDevice;
        HRESULT hr = g_pDeviceEnumerator->GetDefaultAudioEndpoint(
            eRender, eConsole, defaultDevice.put());
        if (FAILED(hr)) {
            return false;
        }

        winrt::com_ptr<IAudioSessionManager2> sessionManager;
        hr = defaultDevice->Activate(XIID_IAudioSessionManager2, CLSCTX_ALL, NULL,
                                     sessionManager.put_void());
        if (FAILED(hr)) {
            return false;
        }

        winrt::com_ptr<IAudioSessionEnumerator> sessionEnumerator;
        hr = sessionManager->GetSessionEnumerator(sessionEnumerator.put());
        if (FAILED(hr)) {
            return false;
        }

        int sessionCount = 0;
        hr = sessionEnumerator->GetCount(&sessionCount);
        if (FAILED(hr)) {
            return false;
        }

        bool foundSession = false;

        for (int i = 0; i < sessionCount; i++) {
            winrt::com_ptr<IAudioSessionControl> sessionControl;
            hr = sessionEnumerator->GetSession(i, sessionControl.put());
            if (FAILED(hr)) {
                continue;
            }

            winrt::com_ptr<IAudioSessionControl2> sessionControl2;
            hr = sessionControl->QueryInterface(__uuidof(IAudioSessionControl2),
                                                sessionControl2.put_void());
            if (FAILED(hr)) {
                continue;
            }

            // Skip system sounds session.
            if (sessionControl2->IsSystemSoundsSession() == S_OK) {
                continue;
            }

            DWORD sessionPID = 0;
            hr = sessionControl2->GetProcessId(&sessionPID);
            if (FAILED(hr)) {
                continue;
            }

            foundSession = true;
            if (!callback(sessionPID, sessionControl2.get())) {
                break;
            }
        }

        return foundSession;
    }

    // Get the command line of a process from its handle.
    // Returns empty string on failure.
    std::wstring GetProcessCommandLine(HANDLE hProcess) {
        PROCESS_BASIC_INFORMATION pbi;
        ULONG returnLength;
        NTSTATUS status = NtQueryInformationProcess(
            hProcess, ProcessBasicInformation, &pbi, sizeof(pbi), &returnLength);

        if (!NT_SUCCESS(status) || !pbi.PebBaseAddress) {
            return {};
        }

        PEB peb;
        if (!ReadProcessMemory(hProcess, pbi.PebBaseAddress, &peb, sizeof(peb),
                               nullptr)) {
            return {};
        }

        RTL_USER_PROCESS_PARAMETERS params;
        if (!ReadProcessMemory(hProcess, peb.ProcessParameters, &params,
                               sizeof(params), nullptr)) {
            return {};
        }

        std::wstring cmdLine(params.CommandLine.Length / sizeof(WCHAR), L'\0');
        if (!ReadProcessMemory(hProcess, params.CommandLine.Buffer, cmdLine.data(),
                               params.CommandLine.Length, nullptr)) {
            return {};
        }

        return cmdLine;
    }

    // Find Chromium's audio subprocess for a given parent process.
    // Chromium-based browsers run audio in a separate utility process with
    // specific command line flags. Returns the audio subprocess PID or 0 if not
    // found.
    DWORD FindChromiumAudioSubprocessUncached(DWORD parentPID) {
        HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (snapshot == INVALID_HANDLE_VALUE) {
            return 0;
        }

        DWORD audioSubprocessPID = 0;
        std::vector<DWORD> rendererPIDs;

        PROCESSENTRY32 pe32;
        pe32.dwSize = sizeof(pe32);

        if (Process32First(snapshot, &pe32)) {
            do {
                if (pe32.th32ParentProcessID != parentPID) {
                    continue;
                }

                HANDLE hProcess =
                    OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ,
                                FALSE, pe32.th32ProcessID);
                if (!hProcess) {
                    continue;
                }

                std::wstring cmdLine = GetProcessCommandLine(hProcess);
                CloseHandle(hProcess);

                if (cmdLine.empty()) {
                    continue;
                }

                // Parse command line and check for Chromium audio service flags.
                int argc = 0;
                LPWSTR* argv = CommandLineToArgvW(cmdLine.c_str(), &argc);
                if (!argv) {
                    continue;
                }

                bool isUtility = false;
                bool isAudioService = false;
                bool isRenderer = false;
                for (int i = 0; i < argc; i++) {
                    if (wcscmp(argv[i], L"--type=utility") == 0) {
                        isUtility = true;
                    } else if (wcscmp(argv[i],
                                      L"--utility-sub-type=audio.mojom."
                                      L"AudioService") == 0) {
                        isAudioService = true;
                    } else if (wcscmp(argv[i], L"--type=renderer") == 0) {
                        isRenderer = true;
                    }
                }

                LocalFree(argv);

                if (isUtility && isAudioService) {
                    audioSubprocessPID = pe32.th32ProcessID;
                    break;
                } else if (isRenderer) {
                    rendererPIDs.push_back(pe32.th32ProcessID);
                }
            } while (Process32Next(snapshot, &pe32));
        }

        CloseHandle(snapshot);

        if (audioSubprocessPID) {
            return audioSubprocessPID;
        }

        // Fallback: return first renderer process with audio session.
        if (rendererPIDs.empty()) {
            return 0;
        }

        DWORD rendererAudioPID = 0;
        ForEachAudioSession([&](DWORD sessionPID, IAudioSessionControl2*) {
            for (DWORD pid : rendererPIDs) {
                if (sessionPID == pid) {
                    rendererAudioPID = pid;
                    return false;  // Stop iterating.
                }
            }
            return true;  // Continue iterating.
        });
        return rendererAudioPID;
    }

    // Cache for Chromium audio subprocess lookups to avoid expensive repeated
    // process enumeration.
    struct ChromiumAudioSubprocessCache {
        DWORD audioSubprocessPID;
        ULONGLONG timestamp;
    };
    std::unordered_map<DWORD, ChromiumAudioSubprocessCache>
        g_chromiumAudioSubprocessCache;
    constexpr ULONGLONG kChromiumCacheTTL = 5000;  // 5 seconds.

    DWORD FindChromiumAudioSubprocess(DWORD parentPID) {
        ULONGLONG now = GetTickCount64();

        // Check cache first.
        auto it = g_chromiumAudioSubprocessCache.find(parentPID);
        if (it != g_chromiumAudioSubprocessCache.end()) {
            if (now - it->second.timestamp < kChromiumCacheTTL) {
                return it->second.audioSubprocessPID;
            }
        }

        // Cache miss or expired, do the lookup.
        DWORD audioSubprocessPID = FindChromiumAudioSubprocessUncached(parentPID);

        // Clean up expired entries.
        for (auto cacheIt = g_chromiumAudioSubprocessCache.begin();
             cacheIt != g_chromiumAudioSubprocessCache.end();) {
            if (now - cacheIt->second.timestamp >= kChromiumCacheTTL) {
                cacheIt = g_chromiumAudioSubprocessCache.erase(cacheIt);
            } else {
                ++cacheIt;
            }
        }

        // Update cache.
        g_chromiumAudioSubprocessCache[parentPID] = {audioSubprocessPID, now};

        return audioSubprocessPID;
    }

    struct AppVolumeResult {
        int volume;  // 0-100.
        bool muted;
    };

    // Adjust volume for all audio sessions matching the given process ID.
    std::optional<AppVolumeResult> AdjustAppVolumeForPID(DWORD targetPID,
                                                         float fVolumeAdd) {
        std::optional<AppVolumeResult> result;

        ForEachAudioSession([&](DWORD pid, IAudioSessionControl2* sessionControl) {
            if (pid != targetPID) {
                return true;  // Continue to next session.
            }

            winrt::com_ptr<ISimpleAudioVolume> vol;
            if (FAILED(sessionControl->QueryInterface(__uuidof(ISimpleAudioVolume),
                                                      vol.put_void()))) {
                return true;  // Continue to next session.
            }

            float currentVolume = 0.0f;
            HRESULT hr = vol->GetMasterVolume(&currentVolume);
            if (FAILED(hr)) {
                return true;  // Continue to next session.
            }

            float newVolume = currentVolume + fVolumeAdd;
            if (newVolume < 0.0f) {
                newVolume = 0.0f;
            } else if (newVolume > 1.0f) {
                newVolume = 1.0f;
            }

            hr = vol->SetMasterVolume(newVolume, NULL);
            if (SUCCEEDED(hr)) {
                AppVolumeResult r;
                r.volume = (int)(newVolume * 100.0f + 0.5f);

                // Handle mute state based on volume.
                if (!g_settings.noAutomaticMuteToggle) {
                    if (newVolume < 0.005f) {
                        vol->SetMute(TRUE, NULL);
                        r.muted = true;
                    } else {
                        vol->SetMute(FALSE, NULL);
                        r.muted = false;
                    }
                } else {
                    // Read actual mute state.
                    BOOL isMuted = FALSE;
                    r.muted = SUCCEEDED(vol->GetMute(&isMuted)) && isMuted;
                }

                result = r;
            }

            return true;  // Continue to process all sessions.
        });

        return result;
    }

    std::optional<AppVolumeResult> AdjustAppVolume(DWORD targetPID,
                                                   float fVolumeAdd) {
        auto result = AdjustAppVolumeForPID(targetPID, fVolumeAdd);
        if (result) {
            return result;
        }

        // Try Chromium audio subprocess if no session found.
        DWORD audioSubprocessPID = FindChromiumAudioSubprocess(targetPID);
        if (audioSubprocessPID) {
            result = AdjustAppVolumeForPID(audioSubprocessPID, fVolumeAdd);
        }

        return result;
    }

    // Toggle mute state for a process. Returns new state with volume, or nullopt
    // if no session.
    std::optional<AppVolumeResult> ToggleAppMuteForPID(DWORD targetPID) {
        std::optional<AppVolumeResult> result;

        ForEachAudioSession([&](DWORD pid, IAudioSessionControl2* sessionControl) {
            if (pid != targetPID) {
                return true;  // Continue to next session.
            }

            winrt::com_ptr<ISimpleAudioVolume> vol;
            if (FAILED(sessionControl->QueryInterface(__uuidof(ISimpleAudioVolume),
                                                      vol.put_void()))) {
                return true;  // Continue to next session.
            }

            BOOL isMuted = FALSE;
            HRESULT hr = vol->GetMute(&isMuted);
            if (FAILED(hr)) {
                return true;  // Continue to next session.
            }

            hr = vol->SetMute(!isMuted, NULL);
            if (SUCCEEDED(hr)) {
                AppVolumeResult r;
                r.muted = !isMuted;

                float currentVolume = 0.0f;
                if (SUCCEEDED(vol->GetMasterVolume(&currentVolume))) {
                    r.volume = (int)(currentVolume * 100.0f + 0.5f);
                } else {
                    r.volume = 0;
                }

                result = r;
            }

            return true;  // Continue to process all sessions.
        });

        return result;
    }

    std::optional<AppVolumeResult> ToggleAppMute(DWORD targetPID) {
        auto result = ToggleAppMuteForPID(targetPID);
        if (result) {
            return result;
        }

        // Try Chromium audio subprocess if no session found.
        DWORD audioSubprocessPID = FindChromiumAudioSubprocess(targetPID);
        if (audioSubprocessPID) {
            result = ToggleAppMuteForPID(audioSubprocessPID);
        }

        return result;
    }

    HWND FindCurrentProcessTaskbarWnd() {
        HWND hTaskbarWnd = nullptr;

        EnumWindows(
            [](HWND hWnd, LPARAM lParam) -> BOOL {
                DWORD dwProcessId;
                WCHAR className[32];
                if (GetWindowThreadProcessId(hWnd, &dwProcessId) &&
                    dwProcessId == GetCurrentProcessId() &&
                    GetClassName(hWnd, className, ARRAYSIZE(className)) &&
                    _wcsicmp(className, L"Shell_TrayWnd") == 0) {
                    *reinterpret_cast<HWND*>(lParam) = hWnd;
                    return FALSE;
                }
                return TRUE;
            },
            reinterpret_cast<LPARAM>(&hTaskbarWnd));

        return hTaskbarWnd;
    }

    using RunFromWindowThreadProc_t = void(WINAPI*)(void* parameter);

    bool RunFromWindowThread(HWND hWnd,
                             RunFromWindowThreadProc_t proc,
                             void* procParam) {
        static const UINT runFromWindowThreadRegisteredMsg =
            RegisterWindowMessage(L"Windhawk_RunFromWindowThread_" WH_MOD_ID);

        struct RUN_FROM_WINDOW_THREAD_PARAM {
            RunFromWindowThreadProc_t proc;
            void* procParam;
        };

        DWORD dwThreadId = GetWindowThreadProcessId(hWnd, nullptr);
        if (dwThreadId == 0) {
            return false;
        }

        if (dwThreadId == GetCurrentThreadId()) {
            proc(procParam);
            return true;
        }

        HHOOK hook = SetWindowsHookEx(
            WH_CALLWNDPROC,
            [](int nCode, WPARAM wParam, LPARAM lParam) -> LRESULT {
                if (nCode == HC_ACTION) {
                    const CWPSTRUCT* cwp = (const CWPSTRUCT*)lParam;
                    if (cwp->message == runFromWindowThreadRegisteredMsg) {
                        RUN_FROM_WINDOW_THREAD_PARAM* param =
                            (RUN_FROM_WINDOW_THREAD_PARAM*)cwp->lParam;
                        param->proc(param->procParam);
                    }
                }

                return CallNextHookEx(nullptr, nCode, wParam, lParam);
            },
            nullptr, dwThreadId);
        if (!hook) {
            return false;
        }

        RUN_FROM_WINDOW_THREAD_PARAM param{
            .proc = proc,
            .procParam = procParam,
        };
        SendMessage(hWnd, runFromWindowThreadRegisteredMsg, 0, (LPARAM)&param);

        UnhookWindowsHookEx(hook);

        return true;
    }

    using CWindowTaskItem_GetWindow_t = HWND(WINAPI*)(void* pThis);
    CWindowTaskItem_GetWindow_t CWindowTaskItem_GetWindow;

    using CImmersiveTaskItem_GetAppWindow_t = HWND(WINAPI*)(void* pThis);
    CImmersiveTaskItem_GetAppWindow_t CImmersiveTaskItem_GetAppWindow;

    void* CImmersiveTaskItem_vftable;
    void* CImmersiveTaskItem_vftable_ITaskItem;

    using TryGetItemFromContainer_TaskListWindowViewModel_t =
        void*(WINAPI*)(void** output, UIElement* container);
    TryGetItemFromContainer_TaskListWindowViewModel_t
        TryGetItemFromContainer_TaskListWindowViewModel_Original;

    using TaskListWindowViewModel_get_TaskItem_t = int(WINAPI*)(void* pThis,
                                                                void** taskItem);
    TaskListWindowViewModel_get_TaskItem_t
        TaskListWindowViewModel_get_TaskItem_Original;

    using TryGetItemFromContainer_TaskListGroupViewModel_t =
        void*(WINAPI*)(void** output, UIElement* container);
    TryGetItemFromContainer_TaskListGroupViewModel_t
        TryGetItemFromContainer_TaskListGroupViewModel_Original;

    using TaskListGroupViewModel_IsMultiWindow_t = bool(WINAPI*)(void* pThis);
    TaskListGroupViewModel_IsMultiWindow_t
        TaskListGroupViewModel_IsMultiWindow_Original;

    using ITaskGroup_IsRunning_t = bool(WINAPI*)(void* pThis);
    ITaskGroup_IsRunning_t ITaskGroup_IsRunning_Original;
    bool WINAPI ITaskGroup_IsRunning_Hook(void* pThis) {
        if (g_captureTaskGroup) {
            Wh_Log(L">");
            g_capturedTaskGroup = *(void**)pThis;
            return false;
        }

        return ITaskGroup_IsRunning_Original(pThis);
    }

    using CTaskGroup_GetNumItems_t = int(WINAPI*)(void* pThis);
    CTaskGroup_GetNumItems_t CTaskGroup_GetNumItems;

    HDPA GetTaskItemsArray(void* taskGroup) {
        // This is a horrible hack, but it's the best way I found to get the array
        // of task items from a task group. It relies on the implementation of
        // CTaskGroup::GetNumItems being just this:
        //
        // return DPA_GetPtrCount(this->taskItemsArray);
        //
        // Or in other words:
        //
        // return *(int*)this[taskItemsArrayOffset];
        //
        // Instead of calling it with a real taskGroup object, we call it with an
        // array of pointers to ints. The returned int value is actually the offset
        // to the array member.

        static size_t offset = []() {
            constexpr int kIntArraySize = 256;
            int arrayOfInts[kIntArraySize];
            int* arrayOfIntPtrs[kIntArraySize];
            for (int i = 0; i < kIntArraySize; i++) {
                arrayOfInts[i] = i;
                arrayOfIntPtrs[i] = &arrayOfInts[i];
            }

            return CTaskGroup_GetNumItems(arrayOfIntPtrs);
        }();

        return (HDPA)((void**)taskGroup)[offset];
    }

    using CTaskListWnd_HandleClick_t = HRESULT(WINAPI*)(void* pThis,
                                                        void* taskGroup,
                                                        void* taskItem,
                                                        void** launcherOptions);
    CTaskListWnd_HandleClick_t CTaskListWnd_HandleClick_Original;
    HRESULT WINAPI CTaskListWnd_HandleClick_Hook(void* pThis,
                                                 void* taskGroup,
                                                 void* taskItem,
                                                 void** launcherOptions) {
        if (*launcherOptions == &g_clickSentinel) {
            Wh_Log(L"Click triggered by sentinel, taskGroup=%p, taskItem=%p",
                   taskGroup, taskItem);
            g_clickSentinel_TaskGroup = taskGroup;
            g_clickSentinel_TaskItem = taskItem;
            return S_OK;
        }

        return CTaskListWnd_HandleClick_Original(pThis, taskGroup, taskItem,
                                                 launcherOptions);
    }

    using TaskItem_ReportClicked_t = int(WINAPI*)(void* pThis, void* param);
    TaskItem_ReportClicked_t TaskItem_ReportClicked_Original;

    using TaskGroup_ReportClicked_t = int(WINAPI*)(void* pThis, void* param);
    TaskGroup_ReportClicked_t TaskGroup_ReportClicked_Original;

    // Triggers the sentinel to capture real native task item from WindowsUdk task
    // item.
    void* GetNativeTaskItemFromWindowsUdkTaskItem(void* windowsUdkTaskItem) {
        g_clickSentinel_TaskItem = nullptr;
        TaskItem_ReportClicked_Original(windowsUdkTaskItem, &g_clickSentinel);
        return g_clickSentinel_TaskItem;
    }

    // Triggers the sentinel to capture real native task group from WindowsUdk task
    // group.
    void* GetNativeTaskGroupFromWindowsUdkTaskGroup(void* windowsUdkTaskGroup) {
        g_clickSentinel_TaskGroup = nullptr;
        TaskGroup_ReportClicked_Original(windowsUdkTaskGroup, &g_clickSentinel);
        return g_clickSentinel_TaskGroup;
    }

    winrt::com_ptr<IUnknown> GetWindowsUdkTaskItemFromTaskListButton(
        UIElement element) {
        winrt::com_ptr<IUnknown> windowViewModel;
        TryGetItemFromContainer_TaskListWindowViewModel_Original(
            windowViewModel.put_void(), &element);
        if (!windowViewModel) {
            return nullptr;
        }

        winrt::com_ptr<IUnknown> windowsUdkTaskItem;
        TaskListWindowViewModel_get_TaskItem_Original(
            windowViewModel.get(), windowsUdkTaskItem.put_void());
        return windowsUdkTaskItem;
    }

    void* GetWindowsUdkTaskGroupFromTaskListButton(UIElement element) {
        winrt::com_ptr<IUnknown> groupViewModel = nullptr;
        TryGetItemFromContainer_TaskListGroupViewModel_Original(
            groupViewModel.put_void(), &element);
        if (!groupViewModel) {
            return nullptr;
        }

        g_capturedTaskGroup = nullptr;
        g_captureTaskGroup = true;
        TaskListGroupViewModel_IsMultiWindow_Original((void**)groupViewModel.get() -
                                                      1);
        g_captureTaskGroup = false;
        return g_capturedTaskGroup;
    }

    HWND GetWindowFromTaskItem(void* taskItem) {
        if (!taskItem) {
            return nullptr;
        }

        if (*(void**)taskItem == CImmersiveTaskItem_vftable_ITaskItem) {
            void* immersiveTaskItem =
                QueryViaVtable(taskItem, CImmersiveTaskItem_vftable);
            return CImmersiveTaskItem_GetAppWindow(immersiveTaskItem);
        }

        return CWindowTaskItem_GetWindow(taskItem);
    }

    // Get process ID from a taskbar button element.
    // Tries to get from individual task item first, then from task group.
    DWORD GetProcessIdFromTaskListButton(UIElement element) {
        // First try to get from individual task item using sentinel pattern.
        auto windowsUdkTaskItem = GetWindowsUdkTaskItemFromTaskListButton(element);
        if (windowsUdkTaskItem) {
            void* nativeTaskItem =
                GetNativeTaskItemFromWindowsUdkTaskItem(windowsUdkTaskItem.get());
            if (nativeTaskItem) {
                HWND hWnd = GetWindowFromTaskItem(nativeTaskItem);
                if (hWnd) {
                    DWORD processId = 0;
                    GetWindowThreadProcessId(hWnd, &processId);
                    return processId;
                }
            }
        }

        // Try to get from task group (for grouped items).
        void* windowsUdkTaskGroup =
            GetWindowsUdkTaskGroupFromTaskListButton(element);
        if (windowsUdkTaskGroup) {
            void* nativeTaskGroup =
                GetNativeTaskGroupFromWindowsUdkTaskGroup(windowsUdkTaskGroup);
            if (nativeTaskGroup) {
                HDPA taskItemsArray = GetTaskItemsArray(nativeTaskGroup);
                if (taskItemsArray && DPA_GetPtrCount(taskItemsArray) > 0) {
                    void* taskItem = DPA_GetPtr(taskItemsArray, 0);
                    HWND hWnd = GetWindowFromTaskItem(taskItem);
                    if (hWnd) {
                        DWORD processId = 0;
                        GetWindowThreadProcessId(hWnd, &processId);
                        return processId;
                    }
                }
            }
        }

        return 0;
    }

    struct {
        Controls::Primitives::Popup popup = nullptr;
        winrt::weak_ref<FrameworkElement> taskbarFrame;
        double rotationAngle = 0.0;
        double cursorX = 0.0;
        double cursorY = 0.0;
        UINT_PTR hideTimer = 0;
    } g_volumeTooltipState;

    struct TaskbarFrameAncestorResult {
        FrameworkElement element = nullptr;
        bool isOverflowPopup = false;
    };

    TaskbarFrameAncestorResult FindTaskbarFrameAncestor(UIElement element) {
        auto parent = Media::VisualTreeHelper::GetParent(element);
        while (parent) {
            auto className = winrt::get_class_name(parent);
            if (className == L"Taskbar.TaskbarFrame") {
                return {parent.try_as<FrameworkElement>(), false};
            }
            if (className == L"Taskbar.FlyoutFrame") {
                return {parent.try_as<FrameworkElement>(), true};
            }
            parent = Media::VisualTreeHelper::GetParent(parent);
        }
        return {};
    }

    void CALLBACK HideVolumeTooltipTimerProc(HWND hwnd,
                                             UINT message,
                                             UINT_PTR idTimer,
                                             DWORD dwTime) {
        KillTimer(nullptr, g_volumeTooltipState.hideTimer);
        g_volumeTooltipState.hideTimer = 0;

        if (g_volumeTooltipState.popup) {
            g_volumeTooltipState.popup.IsOpen(false);
        }
    }

    // Tooltip positioning offset from cursor in pixels.
    constexpr int kTooltipOffset = 12;
    constexpr int kTooltipOffsetTaskbarEdge = 4;

    // Get rotation angle from element's parent RenderTransform.
    // Used to detect vertical taskbar orientation.
    double GetParentRotationAngle(FrameworkElement element) {
        auto parent =
            Media::VisualTreeHelper::GetParent(element).try_as<UIElement>();
        if (!parent) {
            return 0.0;
        }

        auto transform = parent.RenderTransform();
        if (!transform) {
            return 0.0;
        }

        if (auto rotateTransform = transform.try_as<Media::RotateTransform>()) {
            return rotateTransform.Angle();
        }

        if (auto transformGroup = transform.try_as<Media::TransformGroup>()) {
            for (auto child : transformGroup.Children()) {
                if (auto rotateTransform = child.try_as<Media::RotateTransform>()) {
                    return rotateTransform.Angle();
                }
            }
        }

        return 0.0;
    }

    void UpdateTooltipPosition() {
        if (!g_volumeTooltipState.popup) {
            return;
        }

        auto popup = g_volumeTooltipState.popup;
        auto border = popup.Child().try_as<FrameworkElement>();
        double tooltipHeight = border ? border.ActualHeight() : 0;

        auto taskbarFrame = g_volumeTooltipState.taskbarFrame.get();
        if (!taskbarFrame) {
            // Overflow popup: use stored cursor coordinates.
            popup.HorizontalOffset(g_volumeTooltipState.cursorX + kTooltipOffset);
            popup.VerticalOffset(g_volumeTooltipState.cursorY - tooltipHeight / 2);
        } else {
            // Main taskbar: use element-relative coordinates.
            double cursorX = g_volumeTooltipState.cursorX;
            double cursorY = g_volumeTooltipState.cursorY;

            // Get TaskbarFrame's position in root coordinates. In some cases,
            // taskbarFrame may be contained in an element with a larger height,
            // with a region above that's invisible.
            auto transform = taskbarFrame.TransformToVisual(nullptr);
            auto frameOrigin = transform.TransformPoint({0, 0});

            if (g_volumeTooltipState.rotationAngle == 0.0) {
                // Horizontal taskbar.
                double taskbarHeight = taskbarFrame.ActualHeight();
                popup.HorizontalOffset(cursorX + kTooltipOffset);
                popup.VerticalOffset(
                    frameOrigin.Y +
                    std::fmax((taskbarHeight - tooltipHeight) / 2,
                              static_cast<double>(kTooltipOffsetTaskbarEdge)));
            } else {
                // Vertical taskbar.
                popup.HorizontalOffset(kTooltipOffsetTaskbarEdge);
                popup.VerticalOffset(cursorY + kTooltipOffset);
            }
        }
    }

    void ShowVolumeTooltip(FrameworkElement taskbarFrame,
                           double cursorX,
                           double cursorY,
                           bool isOverflowPopup,
                           PCWSTR text) {
        if (!taskbarFrame) {
            return;
        }

        // Create the popup if it doesn't exist.
        if (!g_volumeTooltipState.popup) {
            Controls::Border border;
            border.IsHitTestVisible(false);
            border.Padding(ThicknessHelper::FromLengths(12, 6, 12, 6));
            border.CornerRadius(CornerRadiusHelper::FromUniformRadius(4));

            Controls::TextBlock textBlock;
            textBlock.FontSize(12);
            border.Child(textBlock);

            Controls::Primitives::Popup popup;
            popup.IsHitTestVisible(false);
            if (isOverflowPopup) {
                popup.ShouldConstrainToRootBounds(false);
            }
            popup.Child(border);

            // Update position when the border size changes.
            border.SizeChanged([](auto&&, auto&&) { UpdateTooltipPosition(); });

            g_volumeTooltipState.popup = popup;
        }

        // Store taskbarFrame only for main taskbar (element-relative coords).
        // null taskbarFrame indicates screen coordinates mode.
        g_volumeTooltipState.taskbarFrame =
            isOverflowPopup ? nullptr : taskbarFrame;
        g_volumeTooltipState.cursorX = cursorX;
        g_volumeTooltipState.cursorY = cursorY;

        auto popup = g_volumeTooltipState.popup;
        auto border = popup.Child().try_as<Controls::Border>();

        // Update the text.
        if (auto textBlock = border.Child().try_as<Controls::TextBlock>()) {
            textBlock.Text(text);
        }

        // Use system accent color for styling.
        winrt::Windows::UI::ViewManagement::UISettings uiSettings;
        auto accentColor = uiSettings.GetColorValue(
            winrt::Windows::UI::ViewManagement::UIColorType::Accent);
        border.Background(Media::SolidColorBrush(accentColor));

        // Set text color to white for contrast.
        if (auto textBlock = border.Child().try_as<Controls::TextBlock>()) {
            textBlock.Foreground(
                Media::SolidColorBrush(winrt::Windows::UI::Colors::White()));
        }

        // Set XamlRoot and position near cursor.
        popup.XamlRoot(taskbarFrame.XamlRoot());

        // Check if taskbar frame's parent is rotated (vertical taskbar).
        g_volumeTooltipState.rotationAngle = GetParentRotationAngle(taskbarFrame);

        UpdateTooltipPosition();

        popup.IsOpen(true);

        // Reset the hide timer.
        if (g_volumeTooltipState.hideTimer) {
            KillTimer(nullptr, g_volumeTooltipState.hideTimer);
        }
        g_volumeTooltipState.hideTimer =
            SetTimer(nullptr, 0, 1000, HideVolumeTooltipTimerProc);
    }

    void HideVolumeTooltip() {
        if (g_volumeTooltipState.hideTimer) {
            KillTimer(nullptr, g_volumeTooltipState.hideTimer);
            g_volumeTooltipState.hideTimer = 0;
        }

        if (g_volumeTooltipState.popup) {
            g_volumeTooltipState.popup.IsOpen(false);
        }

        // Destroy popup to disassociate from XamlRoot. A new one will be
        // created next time.
        g_volumeTooltipState.popup = nullptr;
        g_volumeTooltipState.taskbarFrame = nullptr;
        g_volumeTooltipState.rotationAngle = 0.0;
        g_volumeTooltipState.cursorX = 0.0;
    }

    void ShowVolumeResultTooltip(UIElement element,
                                 Input::PointerRoutedEventArgs args,
                                 std::optional<AppVolumeResult> volumeResult) {
        auto [taskbarFrame, isOverflowPopup] = FindTaskbarFrameAncestor(element);
        if (!taskbarFrame) {
            return;
        }

        auto point = args.GetCurrentPoint(taskbarFrame);
        // Transform from taskbarFrame-relative to root-relative coordinates.
        auto transform = taskbarFrame.TransformToVisual(nullptr);
        auto rootPoint =
            transform.TransformPoint({static_cast<float>(point.Position().X),
                                      static_cast<float>(point.Position().Y)});
        double cursorX = rootPoint.X;
        double cursorY = rootPoint.Y;

        WCHAR tooltipText[64];
        if (!volumeResult) {
            wcscpy_s(tooltipText,
                     g_settings.terseFormat ? L"🔕" : L"No audio session");
        } else if (volumeResult->muted) {
            wcscpy_s(tooltipText, g_settings.terseFormat ? L"🔇" : L"Muted");
        } else {
            swprintf_s(tooltipText,
                       g_settings.terseFormat ? L"🔊 %d%%" : L"Volume: %d%%",
                       volumeResult->volume);
        }
        ShowVolumeTooltip(taskbarFrame, cursorX, cursorY, isOverflowPopup,
                          tooltipText);
    }

    // Per-app volume wheel scroll handling.
    using TaskListButton_OnPointerWheelChanged_t = int(WINAPI*)(void* pThis,
                                                                void* pArgs);
    TaskListButton_OnPointerWheelChanged_t
        TaskListButton_OnPointerWheelChanged_Original;
    int WINAPI TaskListButton_OnPointerWheelChanged_Hook(void* pThis, void* pArgs) {
        Wh_Log(L">");

        auto original = [=]() {
            return TaskListButton_OnPointerWheelChanged_Original(pThis, pArgs);
        };

        UIElement element = nullptr;
        ((IUnknown*)pThis)
            ->QueryInterface(winrt::guid_of<UIElement>(), winrt::put_abi(element));
        if (!element) {
            return original();
        }

        auto className = winrt::get_class_name(element);
        if (className != L"Taskbar.TaskListButton") {
            return original();
        }

        Input::PointerRoutedEventArgs args = nullptr;
        ((IUnknown*)pArgs)
            ->QueryInterface(winrt::guid_of<Input::PointerRoutedEventArgs>(),
                             winrt::put_abi(args));
        if (!args) {
            return original();
        }

        // If Ctrl + Scroll is required, skip if Ctrl is not pressed.
        if (g_settings.ctrlScrollVolumeChange && GetKeyState(VK_CONTROL) >= 0) {
            return original();
        }

        double delta = args.GetCurrentPoint(element).Properties().MouseWheelDelta();
        if (!delta) {
            return original();
        }

        // Get process ID from the taskbar button.
        DWORD processId = GetProcessIdFromTaskListButton(element);
        if (!processId) {
            Wh_Log(L"Could not get process ID from taskbar button");
            return original();
        }

        Wh_Log(L"Per-app volume: PID=%u, delta=%f", processId, delta);

        // Calculate volume change.
        int step = g_settings.volumeChangeStep;
        if (!step) {
            step = 2;
        }
        float volumeChange = (float)delta * step * (0.01f / WHEEL_DELTA);

        // Adjust the app's volume.
        auto volumeResult = AdjustAppVolume(processId, volumeChange);

        ShowVolumeResultTooltip(element, args, volumeResult);

        // Mark event as handled.
        args.Handled(true);
        return 0;
    }

    using TaskListButton_OnPointerExited_t = int(WINAPI*)(void* pThis, void* pArgs);
    TaskListButton_OnPointerExited_t TaskListButton_OnPointerExited_Original;
    int WINAPI TaskListButton_OnPointerExited_Hook(void* pThis, void* pArgs) {
        Wh_Log(L">");

        auto original = [=]() {
            return TaskListButton_OnPointerExited_Original(pThis, pArgs);
        };

        UIElement element = nullptr;
        ((IUnknown*)pThis)
            ->QueryInterface(winrt::guid_of<UIElement>(), winrt::put_abi(element));
        if (!element) {
            return original();
        }

        auto className = winrt::get_class_name(element);
        if (className != L"Taskbar.TaskListButton") {
            return original();
        }

        HideVolumeTooltip();

        return original();
    }

    using TaskListButton_OnPointerMoved_t = int(WINAPI*)(void* pThis, void* pArgs);
    TaskListButton_OnPointerMoved_t TaskListButton_OnPointerMoved_Original;
    int WINAPI TaskListButton_OnPointerMoved_Hook(void* pThis, void* pArgs) {
        auto original = [=]() {
            return TaskListButton_OnPointerMoved_Original(pThis, pArgs);
        };

        // Only update if tooltip is currently shown.
        if (!g_volumeTooltipState.popup || !g_volumeTooltipState.popup.IsOpen()) {
            return original();
        }

        UIElement element = nullptr;
        ((IUnknown*)pThis)
            ->QueryInterface(winrt::guid_of<UIElement>(), winrt::put_abi(element));
        if (!element) {
            return original();
        }

        auto className = winrt::get_class_name(element);
        if (className != L"Taskbar.TaskListButton") {
            return original();
        }

        Input::PointerRoutedEventArgs args = nullptr;
        ((IUnknown*)pArgs)
            ->QueryInterface(winrt::guid_of<Input::PointerRoutedEventArgs>(),
                             winrt::put_abi(args));
        if (!args) {
            return original();
        }

        auto ancestorFrame = FindTaskbarFrameAncestor(element).element;
        if (ancestorFrame) {
            auto point = args.GetCurrentPoint(ancestorFrame);
            // Transform from ancestorFrame-relative to root-relative coordinates.
            auto transform = ancestorFrame.TransformToVisual(nullptr);
            auto rootPoint =
                transform.TransformPoint({static_cast<float>(point.Position().X),
                                          static_cast<float>(point.Position().Y)});
            g_volumeTooltipState.cursorX = rootPoint.X;
            g_volumeTooltipState.cursorY = rootPoint.Y;
        }

        UpdateTooltipPosition();

        return original();
    }

    using TaskListButton_OnPointerPressed_t = int(WINAPI*)(void* pThis,
                                                           void* pArgs);
    TaskListButton_OnPointerPressed_t TaskListButton_OnPointerPressed_Original;
    int WINAPI TaskListButton_OnPointerPressed_Hook(void* pThis, void* pArgs) {
        Wh_Log(L">");

        auto original = [=]() {
            return TaskListButton_OnPointerPressed_Original(pThis, pArgs);
        };

        if (!g_settings.ctrlClickToMute) {
            return original();
        }

        // Check if Ctrl is pressed.
        if (GetKeyState(VK_CONTROL) >= 0) {
            return original();
        }

        UIElement element = nullptr;
        ((IUnknown*)pThis)
            ->QueryInterface(winrt::guid_of<UIElement>(), winrt::put_abi(element));
        if (!element) {
            return original();
        }

        auto className = winrt::get_class_name(element);
        if (className != L"Taskbar.TaskListButton") {
            return original();
        }

        Input::PointerRoutedEventArgs args = nullptr;
        ((IUnknown*)pArgs)
            ->QueryInterface(winrt::guid_of<Input::PointerRoutedEventArgs>(),
                             winrt::put_abi(args));
        if (!args) {
            return original();
        }

        // Get process ID from the taskbar button.
        DWORD processId = GetProcessIdFromTaskListButton(element);
        if (!processId) {
            Wh_Log(L"Could not get process ID from taskbar button");
            return original();
        }

        Wh_Log(L"Ctrl+click to toggle mute: PID=%u", processId);

        // Toggle mute state.
        auto muteResult = ToggleAppMute(processId);

        ShowVolumeResultTooltip(element, args, muteResult);

        // Mark event as handled to prevent normal click behavior.
        args.Handled(true);
        return 0;
    }

    void LoadSettings() {
        g_settings.volumeChangeStep = Wh_GetIntSetting(L"perAppVolumeChangeStep");
        g_settings.ctrlClickToMute = Wh_GetIntSetting(L"ctrlClickToMute");
        g_settings.ctrlScrollVolumeChange =
            Wh_GetIntSetting(L"perAppCtrlScrollVolumeChange");
        g_settings.terseFormat = Wh_GetIntSetting(L"terseFormat");
        g_settings.noAutomaticMuteToggle =
            Wh_GetIntSetting(L"perAppNoAutomaticMuteToggle");
    }

    bool HookTaskbarViewDllSymbols(HMODULE module) {
        // Taskbar.View.dll
        WindhawkUtils::SYMBOL_HOOK symbolHooks[] = {
            {
                {LR"(public: virtual int __cdecl winrt::impl::produce<struct winrt::Taskbar::implementation::TaskListButton,struct winrt::Windows::UI::Xaml::Controls::IControlOverrides>::OnPointerWheelChanged(void *))"},
                &TaskListButton_OnPointerWheelChanged_Original,
                TaskListButton_OnPointerWheelChanged_Hook,
            },
            {
                {LR"(public: virtual int __cdecl winrt::impl::produce<struct winrt::Taskbar::implementation::TaskListButton,struct winrt::Windows::UI::Xaml::Controls::IControlOverrides>::OnPointerExited(void *))"},
                &TaskListButton_OnPointerExited_Original,
                TaskListButton_OnPointerExited_Hook,
            },
            {
                {LR"(public: virtual int __cdecl winrt::impl::produce<struct winrt::Taskbar::implementation::TaskListButton,struct winrt::Windows::UI::Xaml::Controls::IControlOverrides>::OnPointerMoved(void *))"},
                &TaskListButton_OnPointerMoved_Original,
                TaskListButton_OnPointerMoved_Hook,
            },
            {
                {LR"(public: virtual int __cdecl winrt::impl::produce<struct winrt::Taskbar::implementation::TaskListButton,struct winrt::Windows::UI::Xaml::Controls::IControlOverrides>::OnPointerPressed(void *))"},
                &TaskListButton_OnPointerPressed_Original,
                TaskListButton_OnPointerPressed_Hook,
            },
            {
                {LR"(struct winrt::Taskbar::TaskListWindowViewModel __cdecl TryGetItemFromContainer<struct winrt::Taskbar::TaskListWindowViewModel>(struct winrt::Windows::UI::Xaml::UIElement const &))"},
                &TryGetItemFromContainer_TaskListWindowViewModel_Original,
            },
            {
                {LR"(public: virtual int __cdecl winrt::impl::produce<struct winrt::Taskbar::implementation::TaskListWindowViewModel,struct winrt::Taskbar::ITaskListWindowViewModel>::get_TaskItem(void * *))"},
                &TaskListWindowViewModel_get_TaskItem_Original,
            },
            {
                {LR"(struct winrt::Taskbar::TaskListGroupViewModel __cdecl TryGetItemFromContainer<struct winrt::Taskbar::TaskListGroupViewModel>(struct winrt::Windows::UI::Xaml::UIElement const &))"},
                &TryGetItemFromContainer_TaskListGroupViewModel_Original,
            },
            {
                {LR"(public: bool __cdecl winrt::Taskbar::implementation::TaskListGroupViewModel::IsMultiWindow(void)const )"},
                &TaskListGroupViewModel_IsMultiWindow_Original,
            },
            {
                {LR"(public: __cdecl winrt::impl::consume_WindowsUdk_UI_Shell_ITaskGroup<struct winrt::WindowsUdk::UI::Shell::ITaskGroup>::IsRunning(void)const )"},
                &ITaskGroup_IsRunning_Original,
                ITaskGroup_IsRunning_Hook,
            },
        };

        return HookSymbols(module, symbolHooks, ARRAYSIZE(symbolHooks));
    }

    bool HookTaskbarDllSymbols() {
        HMODULE module =
            LoadLibraryEx(L"taskbar.dll", nullptr, LOAD_LIBRARY_SEARCH_SYSTEM32);
        if (!module) {
            Wh_Log(L"Couldn't load taskbar.dll for per-app volume");
            return false;
        }

        WindhawkUtils::SYMBOL_HOOK taskbarDllHooks[] = {
            {
                {LR"(public: virtual int __cdecl CTaskGroup::GetNumItems(void))"},
                &CTaskGroup_GetNumItems,
            },
            {
                {LR"(public: virtual struct HWND__ * __cdecl CWindowTaskItem::GetWindow(void))"},
                &CWindowTaskItem_GetWindow,
            },
            {
                {LR"(public: virtual struct HWND__ * __cdecl CImmersiveTaskItem::GetAppWindow(void))"},
                &CImmersiveTaskItem_GetAppWindow,
            },
            {
                {LR"(const CImmersiveTaskItem::`vftable')"},
                &CImmersiveTaskItem_vftable,
            },
            {
                {LR"(const CImmersiveTaskItem::`vftable'{for `ITaskItem'})"},
                &CImmersiveTaskItem_vftable_ITaskItem,
            },
            {
                {LR"(public: virtual long __cdecl CTaskListWnd::HandleClick(struct ITaskGroup *,struct ITaskItem *,struct winrt::Windows::System::LauncherOptions const &))"},
                &CTaskListWnd_HandleClick_Original,
                CTaskListWnd_HandleClick_Hook,
            },
            {
                {LR"(public: virtual int __cdecl winrt::impl::produce<struct winrt::WindowsUdk::UI::Shell::implementation::TaskItem,struct winrt::WindowsUdk::UI::Shell::ITaskItem>::ReportClicked(void *))"},
                &TaskItem_ReportClicked_Original,
            },
            {
                {LR"(public: virtual int __cdecl winrt::impl::produce<struct winrt::WindowsUdk::UI::Shell::implementation::TaskGroup,struct winrt::WindowsUdk::UI::Shell::ITaskGroup>::ReportClicked(void *))"},
                &TaskGroup_ReportClicked_Original,
            },
        };

        return HookSymbols(module, taskbarDllHooks, ARRAYSIZE(taskbarDllHooks));
    }

    HMODULE GetTaskbarViewModuleHandle() {
        HMODULE module = GetModuleHandle(L"Taskbar.View.dll");
        if (!module) {
            module = GetModuleHandle(L"ExplorerExtensions.dll");
        }

        return module;
    }

    void HandleLoadedModuleIfTaskbarView(HMODULE module, LPCWSTR lpLibFileName) {
        if (!g_taskbarViewDllLoaded && GetTaskbarViewModuleHandle() == module &&
            !g_taskbarViewDllLoaded.exchange(true)) {
            Wh_Log(L"Loaded %s", lpLibFileName);

            if (HookTaskbarViewDllSymbols(module)) {
                Wh_ApplyHookOperations();
            }
        }
    }

    void OnLoadLibraryExW(HMODULE module, LPCWSTR lpLibFileName) {
        if (module) {
            HandleLoadedModuleIfTaskbarView(module, lpLibFileName);
        }
    }

    BOOL FeatureInit() {
        Wh_Log(L">");

        LoadSettings();

        if (!HookTaskbarDllSymbols()) {
            return FALSE;
        }

        if (HMODULE taskbarViewModule = GetTaskbarViewModuleHandle()) {
            g_taskbarViewDllLoaded = true;
            if (!HookTaskbarViewDllSymbols(taskbarViewModule)) {
                return FALSE;
            }
        } else {
            Wh_Log(L"Taskbar view module not loaded yet");
        }
    return TRUE;
    }

    void FeatureAfterInit() {
        Wh_Log(L">");

        if (!g_taskbarViewDllLoaded) {
            if (HMODULE taskbarViewModule = GetTaskbarViewModuleHandle()) {
                if (!g_taskbarViewDllLoaded.exchange(true)) {
                    Wh_Log(L"Got Taskbar.View.dll");

                    if (HookTaskbarViewDllSymbols(taskbarViewModule)) {
                        Wh_ApplyHookOperations();
                    }
                }
            }
        }
    }

    void FeatureUninit() {
        Wh_Log(L">");

        HWND hTaskbarWnd = FindCurrentProcessTaskbarWnd();
        if (hTaskbarWnd) {
            RunFromWindowThread(
                hTaskbarWnd,
                [](void*) {
                    HideVolumeTooltip();
                    SndVolUninit();
                },
                nullptr);
        }
    }

    void FeatureSettingsChanged() {
        Wh_Log(L">");

        LoadSettings();
    }
}  // namespace volume_perapp


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
