"""
統合されたテーマ検出システム

各プラットフォームのダークモード設定を検出し、
アプリケーションのテーマを適切に設定します。
"""

import platform
import logging
from typing import Optional, Callable
import subprocess

logger = logging.getLogger(__name__)


class ThemeDetector:
    """クロスプラットフォーム対応のテーマ検出"""
    
    # テーマ変更時のコールバック
    _theme_changed_callbacks: list[Callable[[bool], None]] = []
    
    @classmethod
    def is_dark_mode(cls) -> bool:
        """
        システムのダークモード設定を検出
        
        Returns:
            ダークモードが有効な場合True
        """
        system = platform.system()
        
        try:
            if system == "Darwin":
                return cls._is_dark_mode_macos()
            elif system == "Windows":
                return cls._is_dark_mode_windows()
            elif system == "Linux":
                return cls._is_dark_mode_linux()
        except Exception as e:
            logger.warning(f"Failed to detect theme: {e}")
        
        # デフォルトはライトモード
        return False
    
    @staticmethod
    def _is_dark_mode_macos() -> bool:
        """macOSのダークモード検出"""
        try:
            # subprocessを使用（pyobjc不要）
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True,
                text=True,
                timeout=1
            )
            return 'Dark' in result.stdout
        except subprocess.TimeoutExpired:
            logger.warning("Timeout detecting macOS theme")
        except subprocess.SubprocessError:
            # コマンドが失敗した場合（ライトモードの場合も）
            pass
        except Exception as e:
            logger.debug(f"macOS theme detection failed: {e}")
        
        # pyobjcがある場合は試す
        try:
            from AppKit import NSApplication, NSAppearance
            app = NSApplication.sharedApplication()
            if app:
                appearance = app.effectiveAppearance()
                if appearance:
                    best_match = appearance.bestMatchFromAppearancesWithNames_([
                        "NSAppearanceNameAqua", 
                        "NSAppearanceNameDarkAqua"
                    ])
                    return best_match == "NSAppearanceNameDarkAqua"
        except ImportError:
            logger.debug("pyobjc not available for macOS theme detection")
        except Exception as e:
            logger.debug(f"pyobjc theme detection failed: {e}")
        
        return False
    
    @staticmethod
    def _is_dark_mode_windows() -> bool:
        """Windowsのダークモード検出"""
        try:
            import winreg
            
            # レジストリパス
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            
            # レジストリを開く
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                # AppsUseLightTheme: 0=ダーク, 1=ライト
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0
                
        except FileNotFoundError:
            # Windows 10より前のバージョン
            logger.debug("Theme registry key not found (pre-Windows 10)")
        except Exception as e:
            logger.debug(f"Windows theme detection failed: {e}")
        
        return False
    
    @staticmethod
    def _is_dark_mode_linux() -> bool:
        """Linuxのダークモード検出"""
        
        # GNOME/GTKテーマの確認
        try:
            # gsettingsを使用
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                theme_name = result.stdout.strip().strip("'\"")
                # ダークテーマの一般的なパターン
                dark_patterns = ['dark', 'Dark', 'night', 'Night', 'black', 'Black']
                return any(pattern in theme_name for pattern in dark_patterns)
        except:
            pass
        
        # KDE Plasmaの確認
        try:
            from pathlib import Path
            
            # KDEの設定ファイル
            kde_config = Path.home() / '.config' / 'kdeglobals'
            if kde_config.exists():
                with open(kde_config, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # ColorSchemeでダークテーマを確認
                    if '[General]' in content:
                        for line in content.split('\n'):
                            if line.startswith('ColorScheme='):
                                scheme = line.split('=', 1)[1]
                                return 'dark' in scheme.lower()
        except:
            pass
        
        # 環境変数の確認（一部のディストリビューション）
        gtk_theme = os.environ.get('GTK_THEME', '').lower()
        if gtk_theme and 'dark' in gtk_theme:
            return True
        
        return False
    
    @classmethod
    def register_theme_change_callback(cls, callback: Callable[[bool], None]):
        """
        テーマ変更時のコールバックを登録
        
        Args:
            callback: ダークモードのbool値を受け取る関数
        """
        cls._theme_changed_callbacks.append(callback)
    
    @classmethod
    def check_theme_change(cls) -> bool:
        """
        テーマの変更をチェックし、変更があればコールバックを実行
        
        Returns:
            現在のダークモード状態
        """
        current_dark_mode = cls.is_dark_mode()
        
        # コールバックを実行
        for callback in cls._theme_changed_callbacks:
            try:
                callback(current_dark_mode)
            except Exception as e:
                logger.error(f"Theme change callback failed: {e}")
        
        return current_dark_mode
