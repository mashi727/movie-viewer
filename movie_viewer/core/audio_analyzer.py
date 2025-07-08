"""
音声解析機能
"""

import cv2
import numpy as np
from scipy import signal
from typing import Tuple, Optional
import subprocess
import json


class AudioAnalyzer:
    """音声解析を担当するクラス"""
    
    def __init__(self):
        self.audio_data = None
        self.sample_rate = None
        self.duration = None
    
    def extract_audio(self, video_path: str) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """
        動画ファイルから音声データを抽出
        
        Args:
            video_path: 動画ファイルのパス
            
        Returns:
            audio_data: 音声データ（numpy array）
            sample_rate: サンプリングレート
        """
        try:
            # ffprobeで動画情報を取得
            probe_cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'stream=codec_type,sample_rate,duration',
                '-of', 'json', video_path
            ]
            
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            probe_data = json.loads(probe_result.stdout)
            
            # 音声ストリームを探す
            audio_stream = None
            for stream in probe_data['streams']:
                if stream['codec_type'] == 'audio':
                    audio_stream = stream
                    break
            
            if not audio_stream:
                print("No audio stream found in video")
                return None, None
            
            sample_rate = int(audio_stream.get('sample_rate', 44100))
            
            # ffmpegで音声を抽出（モノラル、16bit PCM）
            extract_cmd = [
                'ffmpeg', '-i', video_path,
                '-vn',  # ビデオなし
                '-ac', '1',  # モノラル
                '-ar', str(sample_rate),  # サンプリングレート
                '-f', 's16le',  # 16bit PCM
                '-'
            ]
            
            result = subprocess.run(extract_cmd, capture_output=True)
            
            if result.returncode != 0:
                print(f"Failed to extract audio: {result.stderr.decode()}")
                return None, None
            
            # バイナリデータをnumpy配列に変換
            audio_data = np.frombuffer(result.stdout, dtype=np.int16)
            
            # 正規化（-1.0 to 1.0）
            audio_data = audio_data.astype(np.float32) / 32768.0
            
            self.audio_data = audio_data
            self.sample_rate = sample_rate
            self.duration = len(audio_data) / sample_rate
            
            return audio_data, sample_rate
            
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return None, None
    
    def get_waveform_data(self, downsample_factor: int = 100) -> np.ndarray:
        """
        表示用の波形データを取得（ダウンサンプリング済み）
        
        Args:
            downsample_factor: ダウンサンプリング係数
            
        Returns:
            ダウンサンプリングされた波形データ
        """
        if self.audio_data is None:
            return np.array([])
        
        # ダウンサンプリング
        if downsample_factor > 1:
            # RMSでダウンサンプリング（より視覚的に適切）
            samples_per_pixel = downsample_factor
            n_pixels = len(self.audio_data) // samples_per_pixel
            
            waveform = np.zeros(n_pixels)
            for i in range(n_pixels):
                start = i * samples_per_pixel
                end = start + samples_per_pixel
                segment = self.audio_data[start:end]
                waveform[i] = np.sqrt(np.mean(segment**2))  # RMS
        else:
            waveform = np.abs(self.audio_data)
        
        # 正規化
        if np.max(waveform) > 0:
            waveform = waveform / np.max(waveform)
        
        return waveform
    
    def get_spectrogram(self, start_time: float, end_time: float, 
                       nperseg: int = 1024, noverlap: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        指定範囲のスペクトログラムを計算
        
        Args:
            start_time: 開始時間（秒）
            end_time: 終了時間（秒）
            nperseg: FFTウィンドウサイズ
            noverlap: オーバーラップサンプル数
            
        Returns:
            frequencies: 周波数軸
            times: 時間軸
            spectrogram: スペクトログラムデータ
        """
        if self.audio_data is None or self.sample_rate is None:
            return np.array([]), np.array([]), np.array([[]])
        
        # サンプルインデックスに変換
        start_idx = int(start_time * self.sample_rate)
        end_idx = int(end_time * self.sample_rate)
        
        # 範囲チェック
        start_idx = max(0, start_idx)
        end_idx = min(len(self.audio_data), end_idx)
        
        # 音声データの切り出し
        audio_segment = self.audio_data[start_idx:end_idx]
        
        if len(audio_segment) < nperseg:
            return np.array([]), np.array([]), np.array([[]])
        
        # スペクトログラムの計算
        if noverlap is None:
            noverlap = nperseg // 2
            
        frequencies, times, spectrogram = signal.spectrogram(
            audio_segment, 
            fs=self.sample_rate,
            window='hann',
            nperseg=nperseg,
            noverlap=noverlap,
            scaling='density'
        )
        
        # 時間軸を調整（開始時間を加算）
        times = times + start_time
        
        # dBスケールに変換
        spectrogram_db = 10 * np.log10(spectrogram + 1e-10)
        
        return frequencies, times, spectrogram_db
    
    def get_time_axis(self, downsample_factor: int = 100) -> np.ndarray:
        """
        波形表示用の時間軸を取得
        
        Args:
            downsample_factor: ダウンサンプリング係数
            
        Returns:
            時間軸データ（秒）
        """
        if self.audio_data is None or self.sample_rate is None:
            return np.array([])
        
        n_samples = len(self.audio_data)
        if downsample_factor > 1:
            n_pixels = n_samples // downsample_factor
            time_axis = np.linspace(0, self.duration, n_pixels)
        else:
            time_axis = np.arange(n_samples) / self.sample_rate
        
        return time_axis
