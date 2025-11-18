#!/bin/bash

# 波形表示をライトモード用に更新するスクリプト
# 使用方法: bash update_to_lightmode.sh

echo "=== 波形表示をライトモード用に更新 ==="
echo ""

# waveform_widget.pyの存在確認
if [ ! -f "movie_viewer/ui/waveform_widget.py" ]; then
    echo "エラー: movie_viewer/ui/waveform_widget.py が見つかりません。"
    echo "movie_viewerプロジェクトのルートディレクトリで実行してください。"
    exit 1
fi

# バックアップ作成
echo "バックアップを作成中..."
cp movie_viewer/ui/waveform_widget.py movie_viewer/ui/waveform_widget.py.backup_darkmode

# ライトモード版のwaveform_widget.pyを作成
echo "ライトモード版のwaveform_widget.pyを作成中..."
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
        
        # PyQtGraphの設定（ライトモード用）
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'w')  # 白背景
        pg.setConfigOption('foreground', 'k')  # 黒文字
        
        # グラフィックスレイアウトウィジェット
        self.graphics_widget = pg.GraphicsLayoutWidget()
        self.graphics_widget.setBackground('w')  # 白背景
        layout.addWidget(self.graphics_widget)
        
        # 波形プロット
        self.waveform_plot = self.graphics_widget.addPlot(row=0, col=0)
        self.waveform_plot.setLabel('left', 'Amplitude', color='#333333')
        self.waveform_plot.setLabel('bottom', 'Time', units='s', color='#333333')
        self.waveform_plot.showGrid(x=True, y=True, alpha=0.2)
        self.waveform_plot.setMouseEnabled(x=True, y=False)
        self.waveform_plot.getAxis('left').setPen('#333333')
        self.waveform_plot.getAxis('bottom').setPen('#333333')
        
        # 波形データ用のプロットアイテム（濃い青色）
        self.waveform_curve = self.waveform_plot.plot(pen=pg.mkPen('#0066CC', width=1.5))
        
        # リージョンアイテム（表示範囲選択用、薄い青色）
        self.region = pg.LinearRegionItem(brush=pg.mkBrush(100, 150, 200, 50))
        self.region.setZValue(10)
        self.region.setPen(pg.mkPen('#4488CC', width=2))
        self.waveform_plot.addItem(self.region)
        
        # 再生位置ライン（赤色）
        self.position_line = pg.InfiniteLine(
            pos=0, 
            angle=90, 
            pen=pg.mkPen('#CC0000', width=2)
        )
        self.waveform_plot.addItem(self.position_line)
        
        # スペクトログラムプロット
        self.spectrogram_plot = self.graphics_widget.addPlot(row=1, col=0)
        self.spectrogram_plot.setLabel('left', 'Frequency', units='Hz', color='#333333')
        self.spectrogram_plot.setLabel('bottom', 'Time', units='s', color='#333333')
        self.spectrogram_plot.showGrid(x=True, y=True, alpha=0.2)
        self.spectrogram_plot.getAxis('left').setPen('#333333')
        self.spectrogram_plot.getAxis('bottom').setPen('#333333')
        
        # スペクトログラム画像アイテム
        self.spectrogram_img = pg.ImageItem()
        self.spectrogram_plot.addItem(self.spectrogram_img)
        
        # カラーマップ設定（ライトモード用に調整）
        # カスタムカラーマップ（白→青→紫→赤）
        colors = [
            (0.0, (255, 255, 255)),    # 白（低エネルギー）
            (0.25, (200, 220, 255)),   # 薄い青
            (0.5, (100, 150, 255)),    # 青
            (0.75, (150, 100, 200)),   # 紫
            (1.0, (200, 50, 50))       # 赤（高エネルギー）
        ]
        self.colormap = pg.ColorMap(pos=[c[0] for c in colors], 
                                   color=[c[1] for c in colors])
        self.spectrogram_img.setColorMap(self.colormap)
        
        # カラーバー
        self.colorbar = pg.ColorBarItem(
            values=(-80, 0),
            colorMap=self.colormap,
            label='Power (dB)',
            width=20
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
            
            # プロットの範囲を設定（ライトモード用に余白を調整）
            self.waveform_plot.setXRange(0, self.duration, padding=0)
            self.waveform_plot.setYRange(-0.05, 1.05, padding=0)
            
            # 背景をより明確に白に設定
            self.waveform_plot.setBackgroundBrush('w')
    
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
            
            # 背景を白に設定
            self.spectrogram_plot.setBackgroundBrush('w')
    
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

echo ""
echo "=== 更新完了 ==="
echo ""
echo "ライトモード用の変更内容:"
echo "- 背景色を白に設定"
echo "- 波形を濃い青色（#0066CC）に変更"
echo "- グリッドラインの透明度を下げて見やすく"
echo "- 軸ラベルとテキストを濃いグレー（#333333）に"
echo "- リージョンを薄い青色の半透明に"
echo "- 再生位置ラインを赤色（#CC0000）に"
echo "- スペクトログラムのカラーマップを白→青→紫→赤に調整"
echo ""
echo "バックアップファイル:"
echo "  movie_viewer/ui/waveform_widget.py.backup_darkmode"
echo ""
echo "元に戻す場合:"
echo "  cp movie_viewer/ui/waveform_widget.py.backup_darkmode movie_viewer/ui/waveform_widget.py"
