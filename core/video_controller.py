"""
ビデオ再生制御機能
"""

import cv2
from PySide6.QtMultimedia import QMediaPlayer


class VideoController:
    """ビデオ制御を担当するクラス"""
    
    def __init__(self, media_player: QMediaPlayer):
        self.media_player = media_player
        self.frame_rate = 25.0  # デフォルトフレームレート
    
    def seek_by_milliseconds(self, milliseconds: int) -> int:
        """指定されたミリ秒分シーク"""
        current_position = self.media_player.position()
        new_position = max(0, current_position + milliseconds)
        self.media_player.setPosition(new_position)
        print(f"Seeked to {new_position / 1000:.2f} seconds")
        return new_position
    
    def seek_by_frame(self, frame_count: int = 1) -> int:
        """フレーム単位でシーク"""
        frame_duration_ms = 1000 / self.frame_rate
        milliseconds = int(frame_duration_ms * frame_count)
        new_position = self.seek_by_milliseconds(milliseconds)
        print(f"{'Advanced' if frame_count > 0 else 'Rewound'} {abs(frame_count)} frame(s)")
        return new_position
    
    def set_frame_rate(self, frame_rate: float):
        """フレームレートを設定"""
        self.frame_rate = frame_rate
        print(f"Frame rate set to {frame_rate} fps")
    
    @staticmethod
    def get_frame_rate(video_path: str) -> float:
        """動画ファイルのフレームレートを取得"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Failed to open video file")
            return 25.0
        
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        print(f"Detected frame rate: {frame_rate} fps")
        return frame_rate
    
    def get_frame_info(self, file_path: str, position_ms: int) -> tuple[bool, str]:
        """指定位置のフレーム情報を取得"""
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return False, "Failed to open video file"
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_index = int(position_ms / 1000 * fps)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        
        if not ret:
            cap.release()
            return False, f"Failed to read frame at index {frame_index}"
        
        # キーフレーム判定
        is_keyframe = cap.get(cv2.CAP_PROP_POS_FRAMES) == frame_index
        frame_type = "Keyframe (I-frame)" if is_keyframe else "Non-keyframe (P/B-frame)"
        
        cap.release()
        return True, f"Frame at index {frame_index} is a {frame_type}."
