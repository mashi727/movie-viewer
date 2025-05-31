"""
OS別のダークモード検出機能
"""

import platform


class DarkModeDetector:
    """ダークモード検出を担当するクラス"""
    
    @staticmethod
    def is_dark_mode() -> bool:
        """OSのダークモード設定を検出"""
        system = platform.system()
        
        if system == "Darwin":
            return DarkModeDetector._is_dark_mode_macos()
        elif system == "Windows":
            return DarkModeDetector._is_dark_mode_windows()
        return False
    
    @staticmethod
    def _is_dark_mode_macos() -> bool:
        """macOSでのダークモード判定"""
        try:
            from AppKit import NSApplication, NSAppearance
            app = NSApplication.sharedApplication()
            appearance = app.effectiveAppearance()
            best_match = appearance.bestMatchFromAppearancesWithNames_([
                "NSAppearanceNameAqua", "NSAppearanceNameDarkAqua"
            ])
            return best_match == "NSAppearanceNameDarkAqua"
        except Exception as e:
            print(f"Error determining dark mode on macOS: {e}")
            return False
    
    @staticmethod
    def _is_dark_mode_windows() -> bool:
        """Windowsでのダークモード判定"""
        try:
            import ctypes
            registry = ctypes.windll.advapi32
            key = ctypes.create_unicode_buffer(
                "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
            )
            value = ctypes.create_unicode_buffer("AppsUseLightTheme")
            data = ctypes.c_long()
            size = ctypes.c_ulong(ctypes.sizeof(data))
            
            hkey = ctypes.c_void_p()
            if registry.RegOpenKeyExW(0x80000001, key, 0, 0x20019, ctypes.byref(hkey)) == 0:
                if registry.RegQueryValueExW(hkey, value, 0, None, ctypes.byref(data), ctypes.byref(size)) == 0:
                    registry.RegCloseKey(hkey)
                    return data.value == 0
        except Exception as e:
            print(f"Error determining dark mode on Windows: {e}")
        return False
