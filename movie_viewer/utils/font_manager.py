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
