#!/bin/bash

# 波形表示機能を追加するためのアップデートスクリプト
# 使用方法: bash update_waveform_feature.sh

echo "=== Movie Viewer 波形表示機能アップデート ==="
echo ""

# 作業ディレクトリの確認
if [ ! -f "setup.py" ] || [ ! -d "movie_viewer" ]; then
    echo "エラー: movie_viewerプロジェクトのルートディレクトリで実行してください。"
    exit 1
fi

# バックアップディレクトリの作成
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
echo "バックアップディレクトリを作成: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# 既存ファイルのバックアップ
echo "既存ファイルをバックアップ中..."
cp requirements.txt "$BACKUP_DIR/" 2>/dev/null
cp setup.py "$BACKUP_DIR/" 2>/dev/null
cp movie_viewer/app.py "$BACKUP_DIR/" 2>/dev/null

# 1. requirements.txtの更新
echo "1. requirements.txt を更新中..."
cat > requirements.txt << 'EOF'
PySide6>=6.5.0
opencv-python>=4.8.0
pyobjc-framework-Cocoa>=9.0.0  # macOS only for dark mode detection
pyqtgraph>=0.13.0
numpy>=1.21.0
scipy>=1.7.0
librosa>=0.9.0  # 音声処理用（ffmpegが使えない場合のバックアップ）
EOF

# 2. 新しいファイルの作成: audio_analyzer.py
echo "2. movie_viewer/core/audio_analyzer.py を作成中..."
cat > movie_viewer/core/audio_analyzer.py << 'EOF'
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
EOF

# 3. 新しいファイルの作成: waveform_widget.py
echo "3. movie_viewer/ui/waveform_widget.py を作成中..."
cat > movie_viewer/ui/waveform_widget.py << 'EOF'
"""
波形・スペクトログラム表示ウィジェット
"""

import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, QTimer
import numpy as np
from typing import Optional, Tuple


class WaveformWidget(QWidget):
    """波形とスペクトログラムを表示するウィジェット"""
    
    # シグナル定義
    position_changed = Signal(float)  # 再生位置が変更されたときのシグナル（秒）
    region_changed = Signal(float, float)  # リージョンが変更されたときのシグナル（開始、終了）
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.audio_analyzer = None
        self.duration = 0.0
        self.current_position = 0.0
        self.downsample_factor = 100
        
        self._setup_ui()
        self._setup_signals()
    
    def _setup_ui(self):
        """UIのセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # PyQtGraphの設定
        pg.setConfigOptions(antialias=True)
        
        # グラフィックスレイアウトウィジェット
        self.graphics_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graphics_widget)
        
        # 波形プロット
        self.waveform_plot = self.graphics_widget.addPlot(row=0, col=0)
        self.waveform_plot.setLabel('left', 'Amplitude')
        self.waveform_plot.setLabel('bottom', 'Time', units='s')
        self.waveform_plot.showGrid(x=True, y=True, alpha=0.3)
        self.waveform_plot.setMouseEnabled(x=True, y=False)
        
        # 波形データ用のプロットアイテム
        self.waveform_curve = self.waveform_plot.plot(pen='w')
        
        # リージョンアイテム（表示範囲選択用）
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        self.waveform_plot.addItem(self.region)
        
        # 再生位置ライン
        self.position_line = pg.InfiniteLine(
            pos=0, 
            angle=90, 
            pen=pg.mkPen('r', width=2)
        )
        self.waveform_plot.addItem(self.position_line)
        
        # スペクトログラムプロット
        self.spectrogram_plot = self.graphics_widget.addPlot(row=1, col=0)
        self.spectrogram_plot.setLabel('left', 'Frequency', units='Hz')
        self.spectrogram_plot.setLabel('bottom', 'Time', units='s')
        self.spectrogram_plot.showGrid(x=True, y=True, alpha=0.3)
        
        # スペクトログラム画像アイテム
        self.spectrogram_img = pg.ImageItem()
        self.spectrogram_plot.addItem(self.spectrogram_img)
        
        # カラーマップ設定
        self.colormap = pg.colormap.get('viridis')
        self.spectrogram_img.setColorMap(self.colormap)
        
        # カラーバー
        self.colorbar = pg.ColorBarItem(
            values=(-80, 0),
            colorMap=self.colormap,
            label='Power (dB)'
        )
        self.colorbar.setImageItem(self.spectrogram_img, insert_in=self.spectrogram_plot)
        
        # 波形とスペクトログラムのX軸を同期
        self.spectrogram_plot.setXLink(self.waveform_plot)
    
    def _setup_signals(self):
        """シグナルの接続"""
        # リージョン変更時
        self.region.sigRegionChanged.connect(self._on_region_changed)
        
        # 波形クリック時
        self.waveform_plot.scene().sigMouseClicked.connect(self._on_waveform_clicked)
    
    def set_audio_analyzer(self, analyzer):
        """音声解析器を設定"""
        self.audio_analyzer = analyzer
        if analyzer and analyzer.duration:
            self.duration = analyzer.duration
            self._update_waveform()
            self._set_initial_region()
    
    def _update_waveform(self):
        """波形表示を更新"""
        if not self.audio_analyzer:
            return
        
        # 波形データを取得
        waveform_data = self.audio_analyzer.get_waveform_data(self.downsample_factor)
        time_axis = self.audio_analyzer.get_time_axis(self.downsample_factor)
        
        if len(waveform_data) > 0:
            # 波形を描画
            self.waveform_curve.setData(time_axis, waveform_data)
            
            # プロットの範囲を設定
            self.waveform_plot.setXRange(0, self.duration, padding=0)
            self.waveform_plot.setYRange(-0.1, 1.1, padding=0)
    
    def _set_initial_region(self):
        """初期リージョン（冒頭10%）を設定"""
        if self.duration > 0:
            end_time = self.duration * 0.1
            self.region.setRegion((0, end_time))
    
    def _on_region_changed(self):
        """リージョンが変更されたときの処理"""
        region_min, region_max = self.region.getRegion()
        
        # 範囲制限
        region_min = max(0, region_min)
        region_max = min(self.duration, region_max)
        
        # スペクトログラムを更新
        self._update_spectrogram(region_min, region_max)
        
        # シグナルを発行
        self.region_changed.emit(region_min, region_max)
    
    def _update_spectrogram(self, start_time: float, end_time: float):
        """スペクトログラムを更新"""
        if not self.audio_analyzer:
            return
        
        # スペクトログラムを計算
        frequencies, times, spectrogram = self.audio_analyzer.get_spectrogram(
            start_time, end_time
        )
        
        if spectrogram.size > 0:
            # 画像を設定
            self.spectrogram_img.setImage(
                spectrogram.T,
                autoLevels=False,
                levels=(-80, 0)
            )
            
            # 画像の位置とスケールを設定
            self.spectrogram_img.setRect(
                times[0], 
                frequencies[0], 
                times[-1] - times[0], 
                frequencies[-1] - frequencies[0]
            )
            
            # Y軸の範囲を設定（0-8000Hz程度）
            max_freq = min(frequencies[-1], 8000)
            self.spectrogram_plot.setYRange(0, max_freq, padding=0)
    
    def _on_waveform_clicked(self, event):
        """波形がクリックされたときの処理"""
        if event.button() == 1:  # 左クリック
            # クリック位置を取得
            pos = event.scenePos()
            mouse_point = self.waveform_plot.vb.mapSceneToView(pos)
            
            # リージョン内かチェック
            region_min, region_max = self.region.getRegion()
            if region_min <= mouse_point.x() <= region_max:
                # 再生位置を更新
                self.set_position(mouse_point.x())
                # シグナルを発行
                self.position_changed.emit(mouse_point.x())
    
    def set_position(self, position: float):
        """再生位置を設定（秒）"""
        self.current_position = position
        self.position_line.setPos(position)
    
    def set_downsample_factor(self, factor: int):
        """ダウンサンプリング係数を設定"""
        self.downsample_factor = factor
        self._update_waveform()
    
    def get_region(self) -> Tuple[float, float]:
        """現在のリージョンを取得"""
        return self.region.getRegion()
    
    def set_region(self, start: float, end: float):
        """リージョンを設定"""
        self.region.setRegion((start, end))
EOF

# 4. app.pyのバックアップと置き換え
echo "4. movie_viewer/app.py を更新中..."
# 注意: app.pyは非常に長いため、パッチファイルを作成する方が実用的です
# ここでは、主要な変更箇所のみを示します

echo "app.pyの手動更新が必要です。以下の変更を行ってください："
echo ""
echo "1. インポートセクションに追加:"
echo "   from .ui.waveform_widget import WaveformWidget"
echo "   from .core.audio_analyzer import AudioAnalyzer"
echo "   from PySide6.QtWidgets import QSplitter"
echo ""
echo "2. __init__メソッドに追加:"
echo "   self.audio_analyzer: Optional[AudioAnalyzer] = None"
echo "   self.waveform_widget: Optional[WaveformWidget] = None"
echo ""
echo "3. _setup_ui()内でスプリッターを作成して波形ウィジェットを追加"
echo "4. _setup_audio_analyzer()メソッドを追加"
echo "5. initialize_video()に_load_audio_waveform()の呼び出しを追加"
echo ""

# 5. setup.pyの更新
echo "5. setup.py を更新中..."
# setup.pyのinstall_requiresセクションを更新
python3 << 'EOF'
import re

with open('setup.py', 'r') as f:
    content = f.read()

# install_requiresセクションを見つけて更新
pattern = r'install_requires=\[(.*?)\]'
replacement = '''install_requires=[
        "PySide6>=6.5.0",
        "opencv-python>=4.8.0",
        "pyqtgraph>=0.13.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
    ]'''

updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('setup.py', 'w') as f:
    f.write(updated_content)

print("setup.py を更新しました")
EOF

# 6. __init__.pyファイルの更新
echo "6. __init__.py ファイルを更新中..."

# coreパッケージの__init__.pyを更新
echo "Updating movie_viewer/core/__init__.py..."
# 既存のファイルをバックアップ
cp movie_viewer/core/__init__.py movie_viewer/core/__init__.py.backup 2>/dev/null

# 新しい内容を書き込み
cat > movie_viewer/core/__init__.py << 'EOF'
"""コア機能パッケージ"""

from .video_controller import VideoController
from .chapter_manager import ChapterTableManager
from .models import TimePosition
from .audio_analyzer import AudioAnalyzer

__all__ = ['VideoController', 'ChapterTableManager', 'TimePosition', 'AudioAnalyzer']
EOF

# uiパッケージの__init__.pyを更新
echo "Updating movie_viewer/ui/__init__.py..."
# 既存のファイルをバックアップ
cp movie_viewer/ui/__init__.py movie_viewer/ui/__init__.py.backup 2>/dev/null

# 新しい内容を書き込み
cat > movie_viewer/ui/__init__.py << 'EOF'
"""UIコンポーネントパッケージ"""

from .custom_ui_loader import CustomUiLoader
from .waveform_widget import WaveformWidget

__all__ = ['CustomUiLoader', 'WaveformWidget']
EOF

echo ""
echo "=== アップデート完了 ==="
echo ""
echo "重要な注意事項:"
echo "1. app.pyは手動での更新が必要です（上記の指示を参照）"
echo "2. ffmpegがインストールされていることを確認してください"
echo "3. 新しい依存関係をインストールしてください:"
echo "   pip install -e . --upgrade"
echo ""
echo "バックアップは $BACKUP_DIR に保存されています"
echo ""
echo "問題が発生した場合は、バックアップから復元できます:"
echo "  cp $BACKUP_DIR/* ."
echo "  cp $BACKUP_DIR/app.py movie_viewer/"
EOF

chmod +x update_waveform_feature.sh

echo "スクリプトを作成しました: update_waveform_feature.sh"
echo ""
echo "実行方法:"
echo "  bash update_waveform_feature.sh"
echo ""
echo "注意: app.pyの更新は手動で行う必要があります。"
echo "詳細な app.py の内容が必要な場合は、別途提供します。"
