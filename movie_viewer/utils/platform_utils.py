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
