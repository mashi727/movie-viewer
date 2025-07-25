#!/bin/bash

# Movie Viewer クロスプラットフォーム対応実装スクリプト
# このスクリプトは、アプリケーションをmacOS、Windows、Linux対応にします

echo "=== クロスプラットフォーム対応の実装開始 ==="

# 1. utilsディレクトリに新しいモジュールを追加
echo "1. プラットフォーム関連ユーティリティを作成..."

# platform_utils.pyの作成
cat > movie_viewer/utils/platform_utils.py << 'EOF'
"""
プラットフォーム固有の処理を管理するユーティリティ

このモジュールは、Windows、macOS、Linuxの違いを吸収し、
統一的なインターフェースを提供します。
"""

import platform
import sys
import os
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class PlatformUtils:
    """プラットフォーム固有の処理を提供するクラス"""
    
    @staticmethod
    def get_platform() -> str:
        """
        現在のプラットフォームを取得
        
        Returns:
            'windows', 'macos', 'linux', 'unknown' のいずれか
        """
        system = platform.system().lower()
        
        # プラットフォーム名を統一的な形式に変換
        platform_map = {
            'darwin': 'macos',
            'windows': 'windows',
            'linux': 'linux'
        }
        
        return platform_map.get(system, 'unknown')
    
    @staticmethod
    def get_platform_info() -> dict:
        """
        詳細なプラットフォーム情報を取得
        
        Returns:
            プラットフォーム情報の辞書
        """
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'platform': PlatformUtils.get_platform()
        }
    
    @staticmethod
    def get_home_directory() -> Path:
        """
        ユーザーのホームディレクトリを取得
        
        Returns:
            ホームディレクトリのPath
        """
        # Path.home() は全プラットフォームで動作
        return Path.home()
    
    @staticmethod
    def get_app_data_directory(app_name: str = "MovieViewer") -> Path:
        """
        アプリケーションデータディレクトリを取得
        
        各OSの慣習に従った場所を返します：
        - Windows: %APPDATA%/MovieViewer
        - macOS: ~/Library/Application Support/MovieViewer
        - Linux: ~/.config/MovieViewer
        
        Args:
            app_name: アプリケーション名
            
        Returns:
            アプリケーションデータディレクトリのPath
        """
        system = PlatformUtils.get_platform()
        
        if system == 'windows':
            # Windows: 環境変数APPDATAを使用
            base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        elif system == 'macos':
            # macOS: Application Supportディレクトリ
            base = Path.home() / 'Library' / 'Application Support'
        else:
            # Linux: XDG Base Directory仕様に従う
            base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
        
        app_dir = base / app_name
        
        # ディレクトリが存在しない場合は作成
        try:
            app_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created app data directory: {app_dir}")
        except Exception as e:
            logger.error(f"Failed to create app data directory: {e}")
            # フォールバックとしてホームディレクトリ直下を使用
            app_dir = Path.home() / f'.{app_name.lower()}'
            app_dir.mkdir(exist_ok=True)
        
        return app_dir
    
    @staticmethod
    def get_documents_directory() -> Path:
        """
        ドキュメントディレクトリを取得
        
        Returns:
            ドキュメントディレクトリのPath
        """
        system = PlatformUtils.get_platform()
        
        if system == 'windows':
            # Windowsではレジストリから取得を試みる
            try:
                import winreg
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
                ) as key:
                    documents = winreg.QueryValueEx(key, 'Personal')[0]
                    return Path(documents)
            except:
                logger.warning("Failed to get Documents folder from registry")
        
        # デフォルト: ~/Documents
        docs = Path.home() / 'Documents'
        
        # 存在しない場合は各言語版を試す
        if not docs.exists():
            # 日本語版Windows/Linuxの場合
            alternatives = [
                Path.home() / 'ドキュメント',
                Path.home() / 'documents',
                Path.home() / 'Documenti',  # イタリア語
                Path.home() / 'Documentos',  # スペイン語/ポルトガル語
            ]
            
            for alt in alternatives:
                if alt.exists():
                    return alt
        
        # 最終的にDocumentsを返す（存在しなくても）
        return docs
    
    @staticmethod
    def get_video_extensions() -> List[str]:
        """
        サポートする動画ファイル拡張子のリストを取得
        
        プラットフォームによってサポートされる形式が異なる場合があります。
        
        Returns:
            拡張子のリスト（ワイルドカード形式）
        """
        # 基本的な拡張子（全プラットフォーム共通）
        extensions = [
            '*.mp4', '*.m4v', '*.avi', '*.mkv', '*.mov',
            '*.ts', '*.m2ts', '*.mp3', '*.webm', '*.flv',
            '*.ogv', '*.3gp'
        ]
        
        system = PlatformUtils.get_platform()
        
        # プラットフォーム固有の拡張子を追加
        if system == 'windows':
            extensions.extend(['*.wmv', '*.asf'])
        elif system == 'macos':
            extensions.extend(['*.m4v'])  # QuickTime固有
        
        # Windowsは大文字小文字を区別しないが、他のOSでは区別する
        if system != 'windows':
            # 大文字バージョンも追加
            upper_extensions = [ext.upper() for ext in extensions]
            extensions.extend(upper_extensions)
        
        return extensions
    
    @staticmethod
    def fix_high_dpi_scaling():
        """
        高DPIディスプレイでのスケーリング問題を修正
        
        各プラットフォームで適切なDPI設定を行います。
        """
        system = PlatformUtils.get_platform()
        
        if system == 'windows':
            # Windows: プロセスのDPIアウェアネスを設定
            try:
                from ctypes import windll
                # SetProcessDpiAwareness(1) = Process DPI Aware
                windll.shcore.SetProcessDpiAwareness(1)
                logger.info("Set Windows DPI awareness")
            except Exception as e:
                logger.warning(f"Failed to set DPI awareness: {e}")
        
        # Qt固有の高DPI設定（Qt5/Qt6互換）
        try:
            from PySide6.QtCore import Qt
            from PySide6.QtWidgets import QApplication
            
            # Qt6のAttribute
            if hasattr(Qt, 'AA_EnableHighDpiScaling'):
                QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
                QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
                
            logger.info("Qt high DPI scaling enabled")
        except Exception as e:
            logger.warning(f"Failed to set Qt DPI settings: {e}")
    
    @staticmethod
    def get_temp_directory() -> Path:
        """
        一時ファイルディレクトリを取得
        
        Returns:
            一時ディレクトリのPath
        """
        import tempfile
        return Path(tempfile.gettempdir()) / "MovieViewer"
    
    @staticmethod
    def ensure_directory_exists(directory: Path) -> bool:
        """
        ディレクトリが存在することを保証
        
        Args:
            directory: 確認/作成するディレクトリ
            
        Returns:
            成功した場合True
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            return False
EOF

# font_manager.pyの作成
cat > movie_viewer/utils/font_manager.py << 'EOF'
"""
クロスプラットフォーム対応のフォント管理

各OSで最適なフォントを選択し、フォールバック機能を提供します。
"""

import platform
from typing import List, Optional
from PySide6.QtGui import QFont, QFontDatabase
import logging

logger = logging.getLogger(__name__)


class FontManager:
    """フォント管理クラス"""
    
    # プラットフォーム別のフォント設定
    FONT_FAMILIES = {
        'macos': {
            'ui': ['SF Pro Display', 'Helvetica Neue', 'Helvetica'],
            'monospace': ['SF Mono', 'Monaco', 'Menlo', 'Courier New'],
            'japanese': ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic']
        },
        'windows': {
            'ui': ['Segoe UI', 'Arial', 'Tahoma'],
            'monospace': ['Cascadia Mono', 'Consolas', 'Courier New'],
            'japanese': ['Yu Gothic UI', 'Meiryo UI', 'MS UI Gothic']
        },
        'linux': {
            'ui': ['Ubuntu', 'DejaVu Sans', 'Liberation Sans', 'Arial'],
            'monospace': ['Ubuntu Mono', 'DejaVu Sans Mono', 'Liberation Mono'],
            'japanese': ['Noto Sans CJK JP', 'IPAGothic', 'TakaoGothic']
        }
    }
    
    @staticmethod
    def get_platform() -> str:
        """現在のプラットフォームを取得"""
        system = platform.system().lower()
        if system == 'darwin':
            return 'macos'
        elif system == 'windows':
            return 'windows'
        else:
            return 'linux'
    
    @classmethod
    def get_ui_font(cls, size: int = 12) -> QFont:
        """
        UI用の最適なフォントを取得
        
        Args:
            size: フォントサイズ
            
        Returns:
            QFontインスタンス
        """
        platform_name = cls.get_platform()
        font_families = cls.FONT_FAMILIES.get(platform_name, cls.FONT_FAMILIES['linux'])
        
        return cls._get_best_font(font_families['ui'], size)
    
    @classmethod
    def get_monospace_font(cls, size: int = 12) -> QFont:
        """
        等幅フォントを取得
        
        Args:
            size: フォントサイズ
            
        Returns:
            QFontインスタンス
        """
        platform_name = cls.get_platform()
        font_families = cls.FONT_FAMILIES.get(platform_name, cls.FONT_FAMILIES['linux'])
        
        font = cls._get_best_font(font_families['monospace'], size)
        font.setFixedPitch(True)
        return font
    
    @classmethod
    def get_japanese_font(cls, size: int = 12) -> QFont:
        """
        日本語表示用フォントを取得
        
        Args:
            size: フォントサイズ
            
        Returns:
            QFontインスタンス
        """
        platform_name = cls.get_platform()
        font_families = cls.FONT_FAMILIES.get(platform_name, cls.FONT_FAMILIES['linux'])
        
        # 日本語フォントにUIフォントも追加（フォールバック用）
        all_families = font_families['japanese'] + font_families['ui']
        
        return cls._get_best_font(all_families, size)
    
    @staticmethod
    def _get_best_font(families: List[str], size: int) -> QFont:
        """
        利用可能な最適なフォントを取得
        
        Args:
            families: 優先順位付きフォントファミリーリスト
            size: フォントサイズ
            
        Returns:
            QFontインスタンス
        """
        db = QFontDatabase()
        available_families = set(db.families())
        
        # 優先リストから利用可能なフォントを探す
        for family in families:
            if family in available_families:
                logger.debug(f"Selected font: {family}")
                return QFont(family, size)
        
        # フォールバック: システムデフォルト
        logger.warning("No preferred font found, using system default")
        font = QFont()
        font.setPointSize(size)
        return font
    
    @staticmethod
    def list_available_fonts() -> List[str]:
        """
        利用可能なフォントファミリーのリストを取得
        
        Returns:
            フォントファミリー名のリスト
        """
        db = QFontDatabase()
        return sorted(db.families())
EOF

# shortcut_manager.pyの作成
cat > movie_viewer/utils/shortcut_manager.py << 'EOF'
"""
クロスプラットフォーム対応のショートカット管理

各OSの慣習に従ったキーボードショートカットを提供します。
"""

import platform
from typing import Dict, Optional
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)


class ShortcutManager:
    """ショートカットキー管理クラス"""
    
    # カスタムショートカットの定義
    CUSTOM_SHORTCUTS = {
        'jump_to_time': {'win': 'Ctrl+J', 'mac': 'Cmd+J'},
        'rewind_1min': {'win': 'Ctrl+Left', 'mac': 'Cmd+Left'},
        'forward_1min': {'win': 'Ctrl+Right', 'mac': 'Cmd+Right'},
        'frame_forward': {'win': 'Shift+>', 'mac': 'Shift+>'},
        'frame_backward': {'win': 'Shift+<', 'mac': 'Shift+<'},
        'copy_time': {'win': 'Ctrl+Shift+C', 'mac': 'Cmd+Shift+C'},
        'show_help': {'win': 'Shift+?', 'mac': 'Shift+?'},
    }
    
    @staticmethod
    def get_modifier_key() -> int:
        """
        プラットフォームに応じた主修飾キーを取得
        
        Returns:
            Qt.ControlModifier または Qt.MetaModifier
        """
        if platform.system() == 'Darwin':
            # macOSではCmd (Meta) キーを使用
            return Qt.MetaModifier
        else:
            # Windows/LinuxではCtrlキーを使用
            return Qt.ControlModifier
    
    @staticmethod
    def get_modifier_name() -> str:
        """
        プラットフォームに応じた修飾キー名を取得
        
        Returns:
            'Cmd' または 'Ctrl'
        """
        if platform.system() == 'Darwin':
            return 'Cmd'
        else:
            return 'Ctrl'
    
    @classmethod
    def create_shortcut(cls, key: str, use_modifier: bool = True) -> QKeySequence:
        """
        プラットフォームに適したショートカットを作成
        
        Args:
            key: キー文字（例: 'O', 'S', 'Q'）
            use_modifier: 修飾キーを使用するか
            
        Returns:
            QKeySequenceインスタンス
        """
        if not use_modifier:
            return QKeySequence(key)
        
        modifier_name = cls.get_modifier_name()
        shortcut_str = f"{modifier_name}+{key}"
        
        logger.debug(f"Created shortcut: {shortcut_str}")
        return QKeySequence(shortcut_str)
    
    @classmethod
    def get_standard_shortcuts(cls) -> Dict[str, QKeySequence]:
        """
        標準的なショートカットの辞書を取得
        
        Qt標準のショートカットを使用することで、
        各OSの慣習に自動的に従います。
        
        Returns:
            アクション名とQKeySequenceの辞書
        """
        return {
            'new': QKeySequence.New,
            'open': QKeySequence.Open,
            'save': QKeySequence.Save,
            'save_as': QKeySequence.SaveAs,
            'quit': QKeySequence.Quit,
            'copy': QKeySequence.Copy,
            'paste': QKeySequence.Paste,
            'cut': QKeySequence.Cut,
            'undo': QKeySequence.Undo,
            'redo': QKeySequence.Redo,
            'find': QKeySequence.Find,
            'replace': QKeySequence.Replace,
            'select_all': QKeySequence.SelectAll,
            'fullscreen': QKeySequence.FullScreen,
            'help': QKeySequence.HelpContents,
            'preferences': QKeySequence.Preferences,
        }
    
    @classmethod
    def get_custom_shortcut(cls, action: str) -> Optional[QKeySequence]:
        """
        カスタムショートカットを取得
        
        Args:
            action: アクション名
            
        Returns:
            QKeySequenceインスタンス、定義されていない場合None
        """
        if action not in cls.CUSTOM_SHORTCUTS:
            return None
        
        platform_key = 'mac' if platform.system() == 'Darwin' else 'win'
        shortcut_str = cls.CUSTOM_SHORTCUTS[action].get(platform_key)
        
        if shortcut_str:
            return QKeySequence(shortcut_str)
        
        return None
    
    @classmethod
    def get_all_shortcuts(cls) -> Dict[str, QKeySequence]:
        """
        全てのショートカット（標準＋カスタム）を取得
        
        Returns:
            アクション名とQKeySequenceの辞書
        """
        shortcuts = cls.get_standard_shortcuts()
        
        # カスタムショートカットを追加
        for action in cls.CUSTOM_SHORTCUTS:
            custom_shortcut = cls.get_custom_shortcut(action)
            if custom_shortcut:
                shortcuts[action] = custom_shortcut
        
        return shortcuts
    
    @classmethod
    def get_shortcut_description(cls, action: str) -> str:
        """
        ショートカットの説明文字列を取得
        
        Args:
            action: アクション名
            
        Returns:
            人間が読める形式のショートカット説明
        """
        shortcuts = cls.get_all_shortcuts()
        
        if action in shortcuts:
            # QKeySequenceを文字列に変換
            key_str = shortcuts[action].toString()
            
            # プラットフォーム固有の表記に変換
            if platform.system() == 'Darwin':
                # macOS表記
                key_str = key_str.replace('Meta+', '⌘')
                key_str = key_str.replace('Ctrl+', '⌃')
                key_str = key_str.replace('Alt+', '⌥')
                key_str = key_str.replace('Shift+', '⇧')
            
            return key_str
        
        return ""
EOF

# theme_detector.pyの作成（既存のdark_mode.pyを置き換え）
cat > movie_viewer/utils/theme_detector.py << 'EOF'
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
EOF

# __init__.pyの更新
cat > movie_viewer/utils/__init__.py << 'EOF'
"""ユーティリティパッケージ"""

from .dark_mode import DarkModeDetector  # 互換性のため残す
from .theme_detector import ThemeDetector
from .style_manager import StyleManager
from .platform_utils import PlatformUtils
from .font_manager import FontManager
from .shortcut_manager import ShortcutManager

__all__ = [
    'DarkModeDetector',
    'ThemeDetector', 
    'StyleManager',
    'PlatformUtils',
    'FontManager',
    'ShortcutManager'
]
EOF

# 2. app.pyの更新パッチ
echo "2. app.pyをクロスプラットフォーム対応に更新..."

cat > app_crossplatform.patch << 'EOF'
--- a/movie_viewer/app.py
+++ b/movie_viewer/app.py
@@ -6,6 +6,7 @@ import os
 import logging
 import sys
 from pathlib import Path
+import platform
 from typing import Optional
 import importlib.resources
 
@@ -26,7 +27,10 @@ from .core.video_controller import VideoController
 from .core.chapter_manager import ChapterTableManager
 from .core.models import TimePosition
 from .utils.dark_mode import DarkModeDetector
+from .utils.platform_utils import PlatformUtils
+from .utils.font_manager import FontManager
+from .utils.shortcut_manager import ShortcutManager
 from .utils.style_manager import StyleManager
 
 # ロガーの設定
@@ -45,6 +49,9 @@ class VideoPlayerApp(QMainWindow):
         self.file_name: Optional[str] = None
         self.video_controller: Optional[VideoController] = None
         self.chapter_manager: Optional[ChapterTableManager] = None
+        
+        # プラットフォーム情報をログ出力
+        logger.info(f"Platform: {PlatformUtils.get_platform_info()}")
         
         # リソースパスの設定（パッケージ化された環境でも動作）
         try:
@@ -65,13 +72,13 @@ class VideoPlayerApp(QMainWindow):
         self._setup_connections()
         self._apply_styles()
     
         logger.info("VideoPlayerApp の初期化が完了しました")
     
     def _setup_ui(self):
         """UI設定"""
         # UIファイルのロード
         loader = CustomUiLoader()
-        ui_file_path = self.resource_path / "ui" / "video_player.ui"
+        ui_file_path = Path(self.resource_path) / "ui" / "video_player.ui"
         
         # UIファイルの存在確認
         if not ui_file_path.exists():
@@ -170,11 +177,14 @@ class VideoPlayerApp(QMainWindow):
         
         # プレイボタンの設定
         self.play_pause_button.setStyleSheet("background: transparent; border: none;")
-        icon_path = self.resource_path / "icons" / "play.png"
+        icon_path = Path(self.resource_path) / "icons" / "play.png"
         if not icon_path.exists():
-            icon_path = self.resource_path / "play.png"
+            icon_path = Path(self.resource_path) / "play.png"
         if icon_path.exists():
             self.play_pause_button.setIcon(QIcon(str(icon_path)))
             self.play_pause_button.setIconSize(QSize(65, 65))
     
     def _setup_menu_bar(self):
@@ -185,8 +195,9 @@ class VideoPlayerApp(QMainWindow):
         menu_bar.setStyleSheet(StyleManager.get_menu_style())
         
         # フォント設定
-        font = QFont("Noto Sans CJK JP", 16)
+        font = FontManager.get_japanese_font(16)
         menu_bar.setFont(font)
         
-        font2 = QFont("Noto Sans CJK JP", 14)
+        font2 = FontManager.get_japanese_font(14)
         
         # ファイルメニューの設定
@@ -199,9 +210,11 @@ class VideoPlayerApp(QMainWindow):
         file_menu = menu_bar.addMenu("File")
         file_menu.setFont(font)
         
+        shortcuts = ShortcutManager.get_standard_shortcuts()
+        
         actions = [
-            ("Open", "Ctrl+O", lambda: self.open_video()),
-            ("Load", "Ctrl+L", lambda: self.load_chapter_file()),
-            ("Save", "Ctrl+S", lambda: self.save_chapter_file()),
+            ("Open", shortcuts['open'], lambda: self.open_video()),
+            ("Load", ShortcutManager.create_shortcut("L"), lambda: self.load_chapter_file()),
+            ("Save", shortcuts['save'], lambda: self.save_chapter_file()),
             ("Quit", None, lambda: self.quit_application()),
         ]
@@ -218,9 +231,9 @@ class VideoPlayerApp(QMainWindow):
         skip_menu.setFont(font)
         
         skip_actions = [
-            ("1min BW", "Ctrl+Left", lambda: self._rewind_1min()),
-            ("1min FW", "Ctrl+Right", lambda: self._advance_1min()),
-            ("Jump", "Ctrl+J", lambda: self.jump_to_time()),
+            ("1min BW", ShortcutManager.get_custom_shortcut('rewind_1min'), lambda: self._rewind_1min()),
+            ("1min FW", ShortcutManager.get_custom_shortcut('forward_1min'), lambda: self._advance_1min()),
+            ("Jump", ShortcutManager.get_custom_shortcut('jump_to_time'), lambda: self.jump_to_time()),
         ]
         
         for name, shortcut, callback in skip_actions:
@@ -298,8 +311,9 @@ class VideoPlayerApp(QMainWindow):
         self.save_button.clicked.connect(self.save_chapter_file)
         
         # ショートカット
-        self.shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
+        self.shortcut = QShortcut(ShortcutManager.create_shortcut("P"), self)
         self.shortcut.activated.connect(self.print_window_geometry)
 
 
     def _apply_styles(self):
         """スタイルの適用"""
-        QApplication.setStyle("macOS")
+        # プラットフォームに適したスタイルを選択
+        system = PlatformUtils.get_platform()
+        if system == 'windows':
+            QApplication.setStyle("windowsvista")
+        elif system == 'macos':
+            QApplication.setStyle("macOS")
+        else:
+            QApplication.setStyle("Fusion")
         
         layout = self.loaded_ui.centralWidget().layout()
         layout.setSpacing(7)
@@ -488,7 +502,7 @@ class VideoPlayerApp(QMainWindow):
             self, 
             "Open Video File", 
             "", 
-            "Video Files (*.mp4 *.m4v *.avi *.mkv *.mov *.MOV *.ts *.m2ts *.mp3)"
+            f"Video Files ({' '.join(PlatformUtils.get_video_extensions())})"
         )
         
         self._center_dialog(dialog)
@@ -569,9 +583,11 @@ class VideoPlayerApp(QMainWindow):
     def toggle_play_pause(self):
         """再生と一時停止を切り替える"""
+        icon_base = Path(self.resource_path) / "icons"
+        
         if self.media_player.playbackState() == QMediaPlayer.PlayingState:
             self.media_player.pause()
-            icon_path = self.resource_path / "icons" / "play.png"
+            icon_path = icon_base / "play.png"
             if not icon_path.exists():
-                icon_path = self.resource_path / "play.png"
+                icon_path = Path(self.resource_path) / "play.png"
         else:
             self.media_player.play()
-            icon_path = self.resource_path / "icons" / "pause.png"
+            icon_