"""
メインアプリケーションクラス
"""

import os
import sys
from pathlib import Path
from typing import Optional
import importlib.resources

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QSlider, QPushButton,
    QLabel, QStatusBar, QTableView, QStyleFactory, QMessageBox
)
from PySide6.QtGui import (
    QKeySequence, QShortcut, QAction, QIcon, QFont
)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QFile, Qt, QUrl, QSize

from .ui.custom_ui_loader import CustomUiLoader
from .core.video_controller import VideoController
from .core.chapter_manager import ChapterTableManager
from .core.models import TimePosition
from .utils.dark_mode import DarkModeDetector
from .utils.style_manager import StyleManager


class VideoPlayerApp(QMainWindow):
    """メインアプリケーションクラス"""
    
    def __init__(self):
        super().__init__()
        self.file_name: Optional[str] = None
        self.video_controller: Optional[VideoController] = None
        self.chapter_manager: Optional[ChapterTableManager] = None
        
        # リソースパスの設定（パッケージ化された環境でも動作）
        try:
            # Python 3.9+
            import importlib.resources as pkg_resources
            self.resource_path = Path(pkg_resources.files('movie_viewer'))
        except (ImportError, AttributeError):
            # Python 3.8
            try:
                import pkg_resources
                self.resource_path = Path(pkg_resources.resource_filename('movie_viewer', ''))
            except ImportError:
                # 開発環境（パッケージ化されていない場合）
                self.resource_path = Path(__file__).parent
        
        self._setup_ui()
        self._setup_media_player()
        self._setup_connections()
        self._apply_styles()
    
    def _setup_ui(self):
        """UI設定"""
        # UIファイルのロード
        loader = CustomUiLoader()
        ui_file_path = self.resource_path / "ui" / "video_player.ui"
        
        # UIファイルの存在確認
        if not ui_file_path.exists():
            # 別の可能性のあるパスを試す
            ui_file_path = self.resource_path / "video_player.ui"
            if not ui_file_path.exists():
                print(f"Error: UI file not found at {ui_file_path}")
                print(f"Current directory: {Path.cwd()}")
                print(f"Resource path: {self.resource_path}")
                sys.exit(-1)
        
        ui_file = QFile(str(ui_file_path))
        if not ui_file.open(QFile.ReadOnly):
            print(f"Error: Cannot open UI file: {ui_file.errorString()}")
            sys.exit(-1)
        
        self.loaded_ui = loader.load(ui_file)
        ui_file.close()
        
        if not self.loaded_ui:
            print("Error: Failed to load UI file.")
            sys.exit(-1)
        
        self.setCentralWidget(self.loaded_ui)
        self.resize(1025, 597)
        self.setWindowTitle("Video Player App")
        self.setGeometry(100, 100, 1280, 720)
        
        # UIコンポーネントの取得
        self._get_ui_components()
        
        # メニューバーの設定
        self._setup_menu_bar()
        
        # ステータスバーの設定
        self._setup_status_bar()
        
        # チャプターマネージャーの初期化
        self.chapter_manager = ChapterTableManager(self.table_view)

        # ビデオウィジェットをクリック可能にする（追加）
        self.video_widget.setFocusPolicy(Qt.ClickFocus)
        self.video_widget.mousePressEvent = lambda event: self.setFocus()

    
    def _get_ui_components(self):
        """UIコンポーネントの取得"""
        # ビデオ関連
        self.video_widget = self.loaded_ui.findChild(QVideoWidget, "videoWidget")
        self.slider = self.loaded_ui.findChild(QSlider, "slider")
        self.play_pause_button = self.loaded_ui.findChild(QPushButton, "playButton")
        
        # コントロールボタン
        self.copy_time_button = self.loaded_ui.findChild(QPushButton, "copyTimeButton")
        self.minus_10s_button = self.loaded_ui.findChild(QPushButton, "minus10sButton")
        self.minus_button = self.loaded_ui.findChild(QPushButton, "minusButton")
        self.minus_1s_button = self.loaded_ui.findChild(QPushButton, "minus1sButton")
        self.minus_frame_button = self.loaded_ui.findChild(QPushButton, "minus1fButton")
        self.plus_frame_button = self.loaded_ui.findChild(QPushButton, "plus1fButton")
        self.plus_1s_button = self.loaded_ui.findChild(QPushButton, "plus1sButton")
        self.plus_button = self.loaded_ui.findChild(QPushButton, "plusButton")
        self.plus_10s_button = self.loaded_ui.findChild(QPushButton, "plus10sButton")
        
        # テーブル関連
        self.table_view = self.loaded_ui.findChild(QTableView, "tableView")
        self.add_button = self.loaded_ui.findChild(QPushButton, "addButton")
        self.del_button = self.loaded_ui.findChild(QPushButton, "delButton")
        self.sort_button = self.loaded_ui.findChild(QPushButton, "sortButton")
        self.jump_button = self.loaded_ui.findChild(QPushButton, "jumpButton")
        self.save_button = self.loaded_ui.findChild(QPushButton, "saveButton")
        
        # ラベル
        self.num_label = self.loaded_ui.findChild(QLabel, "numLabel")
        self.title_label = self.loaded_ui.findChild(QLabel, "titleLabel")
        self.status_bar = self.loaded_ui.findChild(QStatusBar, 'statusbar')
        
        # プレイボタンの設定
        self.play_pause_button.setStyleSheet("background: transparent; border: none;")
        icon_path = self.resource_path / "icons" / "play.png"
        if not icon_path.exists():
            icon_path = self.resource_path / "play.png"
        if icon_path.exists():
            self.play_pause_button.setIcon(QIcon(str(icon_path)))
            self.play_pause_button.setIconSize(QSize(65, 65))
    
    def _setup_menu_bar(self):
        """メニューバーの設定"""
        menu_bar = self.loaded_ui.menuBar()
        menu_bar.setNativeMenuBar(False)
        menu_bar.setFixedHeight(30)
        menu_bar.setStyleSheet(StyleManager.get_menu_style())
        
        # フォント設定
        font = QFont("Noto Sans CJK JP", 16)
        menu_bar.setFont(font)
        
        font2 = QFont("Noto Sans CJK JP", 14)
        
        # ファイルメニューの設定
        self._setup_file_menu(menu_bar, font2)
        
        # スキップメニューの設定
        self._setup_skip_menu(menu_bar, font2)
    
    def _setup_file_menu(self, menu_bar, font):
        """ファイルメニューの設定"""
        file_menu = menu_bar.addMenu("File")
        file_menu.setFont(font)
        
        actions = [
            ("Open", "Ctrl+O", self.open_video),
            ("Load", "Ctrl+L", self.load_chapter_file),
            ("Save", "Ctrl+S", self.save_chapter_file),
            ("Quit", None, self.quit_application),
        ]
        
        for name, shortcut, callback in actions:
            action = QAction(name, self)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(callback)
            file_menu.addAction(action)
    
    def _setup_skip_menu(self, menu_bar, font):
        """スキップメニューの設定"""
        skip_menu = menu_bar.addMenu("Skip")
        skip_menu.setFont(font)
        
        skip_actions = [
            ("1min BW", "Ctrl+Left", self._rewind_1min),
            ("1min FW", "Ctrl+Right", self._advance_1min),
            ("Jump", "Ctrl+J", self.jump_to_time),
        ]
        
        for name, shortcut, callback in skip_actions:
            action = QAction(name, self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(callback)
            skip_menu.addAction(action)
    
    def _setup_status_bar(self):
        """ステータスバーの設定"""
        self.custom_status_label = QLabel()
        self.custom_status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.custom_status_label.setStyleSheet(StyleManager.get_status_label_style())
        self.status_bar.addPermanentWidget(self.custom_status_label, 1)
    
    def _setup_media_player(self):
        """メディアプレイヤーの設定"""
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)
        
        self.video_controller = VideoController(self.media_player)
    
    def _setup_connections(self):
        """シグナル・スロットの接続"""
        # メディアプレイヤー
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.slider.sliderMoved.connect(self.set_position)
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        
        # コントロールボタン
        self.copy_time_button.clicked.connect(self.copy_time)
        
        # シークボタン
        seek_buttons = [
            (self.minus_10s_button, -10000),
            (self.minus_button, -1000),
            (self.minus_1s_button, -300),
            (self.minus_frame_button, -1),  # フレーム単位
            (self.plus_frame_button, 1),    # フレーム単位
            (self.plus_1s_button, 300),
            (self.plus_button, 1000),
            (self.plus_10s_button, 10000),
        ]
        
        for button, value in seek_buttons:
            if abs(value) == 1:  # フレーム単位
                button.clicked.connect(
                    lambda checked, v=value: self.video_controller.seek_by_frame(v)
                )
            else:
                button.clicked.connect(
                    lambda checked, v=value: self.video_controller.seek_by_milliseconds(v)
                )
        
        # テーブル操作
        self.add_button.clicked.connect(self.add_chapter_row)
        self.del_button.clicked.connect(self.delete_chapter_rows)
        self.sort_button.clicked.connect(self.chapter_manager.sort_by_time)
        self.jump_button.clicked.connect(self.jump_to_time)
        self.save_button.clicked.connect(self.save_chapter_file)
        
        # ショートカット
        self.shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.shortcut.activated.connect(self.print_window_geometry)


    def _apply_styles(self):
        """スタイルの適用"""
        QApplication.setStyle("macOS")
        
        layout = self.loaded_ui.centralWidget().layout()
        layout.setSpacing(7)
        
        dark_mode = DarkModeDetector.is_dark_mode()
        button_style = StyleManager.get_button_style(dark_mode)
        self.setStyleSheet(button_style)


    def keyPressEvent(self, event):
        """キーボードイベントの処理"""
        # スペースキーが押されたときに再生・一時停止を切り替え
        if event.key() == Qt.Key_Space:
            self.toggle_play_pause()
            event.accept()
        else:
            # その他のキーはデフォルトの処理に委ねる
            super().keyPressEvent(event)


    def toggle_play_pause(self):
        """再生と一時停止を切り替える"""
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            icon_path = self.resource_path / "icons" / "play.png"
            if not icon_path.exists():
                icon_path = self.resource_path / "play.png"
        else:
            self.media_player.play()
            icon_path = self.resource_path / "icons" / "pause.png"
            if not icon_path.exists():
                icon_path = self.resource_path / "pause.png"
        
        if icon_path.exists():
            self.play_pause_button.setIcon(QIcon(str(icon_path)))
    
    def set_position(self, position: int):
        """再生位置を設定"""
        self.media_player.setPosition(position)
    
    def update_position(self, position: int):
        """再生位置の更新"""
        self.slider.setValue(position)
        self.update_time_label()
    
    def update_duration(self, duration: int):
        """再生時間の更新"""
        self.slider.setRange(0, duration)
        self.update_time_label()

    def update_time_label(self):
        """時間ラベルを更新する（修正版）"""
        # エラーチェックを追加
        if not hasattr(self, 'media_player') or not self.media_player:
            return
            
        current_time = self.media_player.position() / 1000  # 現在の再生位置 (秒)
        total_time = self.media_player.duration() / 1000   # 全体の再生時間 (秒)

        # 現在の再生時間のフォーマット
        current_hours, current_remainder = divmod(current_time, 3600)
        current_minutes, current_seconds = divmod(current_remainder, 60)

        # 全体の再生時間のフォーマット
        total_hours, total_remainder = divmod(total_time, 3600)
        total_minutes, total_seconds = divmod(total_remainder, 60)

        # 小数点2桁の従来フォーマット（エラーが出ていた部分）
        # self.custom_status_label.setText(
        #     f"{int(current_hours):01}:{int(current_minutes):02}:{current_seconds:05.2f} / "
        #     f"{int(total_hours):01}:{int(total_minutes):02}:{total_seconds:05.2f}"
        # )
        
        # 小数点3桁の新フォーマット（copy_timeと統一）
        self.custom_status_label.setText(
            f"{int(current_hours):01}:{int(current_minutes):02}:{current_seconds:06.3f} / "
            f"{int(total_hours):01}:{int(total_minutes):02}:{total_seconds:06.3f}"
        )


    def copy_time(self):
        """現在の再生位置をクリップボードにコピーする"""
        current_time = self.media_player.position() / 1000  # 現在の再生位置 (秒)

        # 現在の再生時間のフォーマット
        current_hours, current_remainder = divmod(current_time, 3600)
        current_minutes, current_seconds = divmod(current_remainder, 60)

        # フォーマットされた時間を作成
        # 変更前: time_string = f"{int(current_hours):01}:{int(current_minutes):02}:{current_seconds:05.2f}"
        time_string = f"{int(current_hours):01}:{int(current_minutes):02}:{current_seconds:06.3f}"  # ← この行を変更

        # クリップボードにコピー
        QApplication.clipboard().setText(time_string)
        print(f"Copied to clipboard: {time_string}")

    def update_time_label(self):
        """時間ラベルを更新する（修正版）"""
        # エラーチェックを追加
        if not hasattr(self, 'media_player') or not self.media_player:
            return
            
        current_time = self.media_player.position() / 1000  # 現在の再生位置 (秒)
        total_time = self.media_player.duration() / 1000   # 全体の再生時間 (秒)

        # 現在の再生時間のフォーマット
        current_hours, current_remainder = divmod(current_time, 3600)
        current_minutes, current_seconds = divmod(current_remainder, 60)

        # 全体の再生時間のフォーマット
        total_hours, total_remainder = divmod(total_time, 3600)
        total_minutes, total_seconds = divmod(total_remainder, 60)

        # 小数点2桁の従来フォーマット（エラーが出ていた部分）
        # self.custom_status_label.setText(
        #     f"{int(current_hours):01}:{int(current_minutes):02}:{current_seconds:05.2f} / "
        #     f"{int(total_hours):01}:{int(total_minutes):02}:{total_seconds:05.2f}"
        # )
        
        # 小数点3桁の新フォーマット（copy_timeと統一）
        self.custom_status_label.setText(
            f"{int(current_hours):01}:{int(current_minutes):02}:{current_seconds:06.3f} / "
            f"{int(total_hours):01}:{int(total_minutes):02}:{total_seconds:06.3f}"
        )
        
    
    def add_chapter_row(self):
        """チャプター行を追加"""
        position = self.chapter_manager.add_row()
        self.update_row_column_count()
        print(f"Added row at position {position + 1}")
    
    def delete_chapter_rows(self):
        """チャプター行を削除"""
        deleted_rows = self.chapter_manager.delete_selected_rows()
        if deleted_rows:
            self.update_row_column_count()
            print(f"Deleted rows: {deleted_rows}")
        else:
            print("No row selected to delete")
    
    def update_row_column_count(self):
        """行数とカラム数をラベルに表示"""
        row_count, column_count = self.chapter_manager.get_row_column_count()
        self.num_label.setText(f"Rows: {row_count}, Columns: {column_count}")
    
    def jump_to_time(self):
        """選択された時間にジャンプ"""
        time_position = self.chapter_manager.get_selected_time()
        if time_position:
            milliseconds = time_position.to_milliseconds()
            self.media_player.setPosition(milliseconds)
            print(f"Jumping to: {milliseconds} ms")
        else:
            print("No valid time selected")
    
    def open_video(self):
        """動画ファイルを開く"""
        dialog = QFileDialog(
            self, 
            "Open Video File", 
            "", 
            "Video Files (*.mp4 *.m4v *.avi *.mkv *.mov *.MOV *.ts *.m2ts *.mp3)"
        )
        
        self._center_dialog(dialog)
        
        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            if file_path:
                self.initialize_video(file_path)
    
    def load_chapter_file(self):
        """チャプターファイルを読み込む"""
        dialog = QFileDialog(
            self, 
            "Open .txt File", 
            "", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        self._center_dialog(dialog)
        
        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            if file_path:
                try:
                    self.chapter_manager.load_from_file(file_path)
                    self.update_row_column_count()
                    print(f"Loaded file: {file_path}")
                except UnicodeDecodeError:
                    print("Error: The file encoding is not UTF-8.")
                except Exception as e:
                    print(f"Error loading file: {e}")
    
    def save_chapter_file(self):
        """チャプターファイルを保存"""
        if not self.file_name:
            print("No file name set")
            return
        
        base_name = os.path.splitext(self.file_name)[0]
        save_file_name = f"{base_name}.txt"
        
        if os.path.exists(save_file_name):
            reply = QMessageBox.question(
                self,
                "Overwrite Confirmation",
                f"The file '{save_file_name}' already exists.\nDo you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                print("Save canceled by user")
                return
        
        try:
            self.chapter_manager.save_to_file(save_file_name)
            print(f"Table contents saved to {save_file_name}")
        except Exception as e:
            print(f"Error saving table contents: {e}")
    
    def quit_application(self):
        """アプリケーションを終了"""
        QApplication.instance().quit()
    
    def print_window_geometry(self):
        """ウィンドウ情報を出力"""
        position = self.geometry().topLeft()
        size = self.geometry().size()
        print(f"Window Position: {position}, Size: {size}")
    
    def initialize_video(self, file_path: str):
        """動画ファイルを初期化"""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.play_pause_button.setEnabled(True)
        
        # フレームレートを設定
        frame_rate = VideoController.get_frame_rate(file_path)
        self.video_controller.set_frame_rate(frame_rate)
        
        # ファイル情報を表示
        file_name = os.path.basename(file_path)
        self.title_label.setStyleSheet("QLabel { font-size: 16px ;}")
        self.title_label.setText(file_name)
        
        # 動画を再生
        self.media_player.play()
        icon_path = self.resource_path / "icons" / "pause.png"
        if not icon_path.exists():
            icon_path = self.resource_path / "pause.png"
        if icon_path.exists():
            self.play_pause_button.setIcon(QIcon(str(icon_path)))
        self.file_name = file_path
    
    def _center_dialog(self, dialog: QFileDialog):
        """ダイアログを中央に配置"""
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.adjustSize()
        dialog_geometry = dialog.geometry()
        parent_center = self.geometry().center()
        dialog_geometry.moveCenter(parent_center)
        dialog.setGeometry(dialog_geometry)
    
    def _rewind_1min(self):
        """1分巻き戻し"""
        self.video_controller.seek_by_milliseconds(-60000)
    
    def _advance_1min(self):
        """1分早送り"""
        self.video_controller.seek_by_milliseconds(60000)
    
    def showEvent(self, event):
        """ウィンドウが表示されるタイミングでの処理"""
        super().showEvent(event)
        print("Debug: VideoPlayerApp is now visible.")
    
    def focusInEvent(self, event):
        """フォーカスを受け取ったときの処理"""
        super().focusInEvent(event)
        print("Debug: VideoPlayerApp received focus.")
