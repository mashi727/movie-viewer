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
