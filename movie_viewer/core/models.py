"""
データモデルの定義
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class TimePosition:
    """時間情報を管理するデータクラス"""
    hours: int = 0
    minutes: int = 0
    seconds: float = 0.0
    
    @classmethod
    def from_milliseconds(cls, ms: int) -> 'TimePosition':
        """ミリ秒から時間情報を生成"""
        total_seconds = ms / 1000
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return cls(int(hours), int(minutes), seconds)
    
    @classmethod
    def from_string(cls, time_str: str) -> Optional['TimePosition']:
        """時間文字列から時間情報を生成"""
        match = re.match(r"^(\d{1,2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?$", time_str)
        if not match:
            return None
        
        hours, minutes, seconds, milliseconds = match.groups()
        ms = int(milliseconds or 0)
        return cls(
            int(hours),
            int(minutes),
            int(seconds) + ms / 1000
        )
    
    def to_milliseconds(self) -> int:
        """ミリ秒に変換"""
        return int(
            self.hours * 3600000 + 
            self.minutes * 60000 + 
            self.seconds * 1000
        )
    
    def to_string(self, include_ms: bool = True) -> str:
        """文字列形式に変換"""
        if include_ms:
            return f"{self.hours:01}:{self.minutes:02}:{self.seconds:05.2f}"
        return f"{self.hours:01}:{self.minutes:02}:{int(self.seconds):02}"
