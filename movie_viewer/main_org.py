#!/usr/bin/env python

import sys
#from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QSlider, QPushButton, QLabel, QStatusBar,QHeaderView, QTableView, QStyleFactory, QMessageBox
from PySide6.QtGui import QKeySequence, QShortcut, QAction
from PySide6.QtGui import QStandardItemModel, QStandardItem, QKeyEvent, QIcon, QFont
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, Signal
from PySide6.QtCore import QCoreApplication

from PySide6.QtCore import QEvent, QPoint, QSortFilterProxyModel
from PySide6.QtCore import QFile, QIODevice, QUrl, Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QSize, QRect
from PySide6.QtMultimediaWidgets import QVideoWidget
import platform
#from pydub import AudioSegment
#from pydub.playback import play
import subprocess
import threading
from PySide6.QtWidgets import QFileDialog, QLineEdit, QAbstractItemView
import cv2

import re
import os


PATH = './'



# macOSでのダークモード判定関数
def is_dark_mode_macos():
    try:
        from AppKit import NSApplication, NSAppearance
        app = NSApplication.sharedApplication()
        appearance = app.effectiveAppearance()
        best_match = appearance.bestMatchFromAppearancesWithNames_([
            "NSAppearanceNameAqua", "NSAppearanceNameDarkAqua"
        ])
        return best_match == "NSAppearanceNameDarkAqua"
    except Exception as e:
        print(f"Error determining dark mode on macOS: {e}")
        return False

# Windowsでのダークモード判定関数
def is_dark_mode_windows():
    try:
        import ctypes
        registry = ctypes.windll.advapi32
        key = ctypes.create_unicode_buffer("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
        value = ctypes.create_unicode_buffer("AppsUseLightTheme")
        data = ctypes.c_long()
        size = ctypes.c_ulong(ctypes.sizeof(data))

        hkey = ctypes.c_void_p()
        if registry.RegOpenKeyExW(0x80000001, key, 0, 0x20019, ctypes.byref(hkey)) == 0:
            if registry.RegQueryValueExW(hkey, value, 0, None, ctypes.byref(data), ctypes.byref(size)) == 0:
                registry.RegCloseKey(hkey)
                return data.value == 0  # 0 = ダークモード, 1 = ライトモード
    except Exception as e:
        print(f"Error determining dark mode on Windows: {e}")
    return False

# ダークモード判定のOSごとのラッパー関数
def is_dark_mode():
    if platform.system() == "Darwin":  # macOS
        return is_dark_mode_macos()
    elif platform.system() == "Windows":  # Windows
        return is_dark_mode_windows()
    else:
        return False  # 他のOSではライトモードをデフォルト

# ダークモードに応じたボタンスタイルを取得する関数
def get_button_style(dark_mode):
    if dark_mode:
        return """
            QPushButton {
                background-color: #44617b;     /* ボタンの背景色 */
                color: white;                 /* テキストの色 */
                border: 0px solid #B39CD9;    /* 枠線の色と太さ */
                border-radius: 10px;          /* ボタンの角を丸くする */
                padding: 0px 0px;             /* 内側の余白 */
                font-size: 20px;              /* フォントサイズ */
            }
            QPushButton:hover {
                background-color: #895b8a;    /* ホバー時の背景色 */
            }
            QPushButton:pressed {
                background-color: #b44c97;    /* 押下時の背景色 */
            }
        """
    else:
        return """
            QPushButton {
                background-color: #e4d2d8;     /* ボタンの背景色 */
                color: black;                 /* テキストの色 */
                border: 1px solid #e7e7eb;    /* 枠線の色と太さ */
                border-radius: 10px;          /* ボタンの角を丸くする */
                padding: 0px 0px;             /* 内側の余白 */
                font-size: 20px;              /* フォントサイズ */
            }
            QPushButton:hover {
                background-color: #c4a3bf;    /* ホバー時の背景色 */
            }
            QPushButton:pressed {
                background-color: #cc7eb1;    /* 押下時の背景色 */
            }
        """




# ダークモード設定をテストする場合
def buttonstyle():
    dark_mode = is_dark_mode()
    print("Dark Mode" if dark_mode else "Light Mode")
    # ボタンスタイルを出力して確認
    button_style = get_button_style(dark_mode)
    return button_style


# カスタム UI ローダークラス
class CustomUiLoader(QUiLoader):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent


    def createWidget(self, class_name, parent=None, name=""):
        if class_name == "QVideoWidget":
            widget = QVideoWidget(parent)
        else:
            widget = super().createWidget(class_name, parent, name)

        if parent and widget:
            widget.setObjectName(name)
        return widget


from PySide6.QtCore import QThread, QCoreApplication
import threading






class VideoPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # QUiLoaderを使用してUIファイルをロード
        loader = CustomUiLoader()
        ui_file = QFile(PATH+"/ui/video_player.ui")
        if not ui_file.open(QFile.ReadOnly):
            print(f"Error: Cannot open UI file: {ui_file.errorString()}")
            sys.exit(-1)
        self.loaded_ui = loader.load(ui_file)  # UIをロード
        ui_file.close()

        if not self.loaded_ui:
            print("Error: Failed to load UI file.")
            sys.exit(-1)

        print("Debug: UI file loaded successfully.")

        # ロードしたUIを中央ウィジェットとして設定
        self.setCentralWidget(self.loaded_ui)

        # ウィンドウサイズを指定
        self.resize(1025, 597)
        print(f"Debug: Window resized to 1280x708.")


        self.setWindowTitle("Video Player App")
        self.setGeometry(100, 100, 1280, 720)  # ウィンドウサイズを設定

        # デバッグログ
        print("Debug: VideoPlayerApp initialized.")
        self.activateWindow()  # ウィンドウをアクティブに
        self.raise_()          # ウィンドウを最前面に


        # 使用可能なスタイルを表示する
        #print("Available styles:", QStyleFactory.keys())
        QApplication.setStyle("macOS") # 例: "Fusion", "Windows", "Macintosh"
        layout = self.loaded_ui.centralWidget().layout()
        #layout.setContentsMargins(0, 0, 0, 0)  # 左、上、右、下のマージンを0に設定
        layout.setSpacing(7)  # ウィジェット間のスペーシングを0に設定
        #layout = self.loaded_ui.layout()
        #layout.setContentsMargins(0, 0, 0, 0)  # 左、上、右、下のマージンを0に設定
        #layout.setSpacing(7)  # ウィジェット間のスペーシングを0に設定



        # ボタンにスタイルシートを設定
        button_style = buttonstyle()
        self.setStyleSheet(button_style)


        # Quitボタンを取得
        '''
        quit_button = self.loaded_ui.findChild(QPushButton, "quitButtyyon")
        if quit_button:
            print(f"Debug: Quit button geometry: {quit_button.geometry()}")
            print(f"Debug: Quit button text: {quit_button.text()}")
            quit_button.clicked.connect(self.close)  # Quitボタンを押したらアプリを終了
        else:
            print("Error: Quit button not found in the UI.")

        # UIのすべてのボタンをデバッグ出力
        for child in self.loaded_ui.findChildren(QPushButton):
            print(f"Debug: Found button - Name: {child.objectName()}, Text: {child.text()}, Geometry: {child.geometry()}")
        '''

        # ショートカット設定
        self.shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.shortcut.activated.connect(self.print_window_geometry)
        print("Debug: Shortcut Ctrl+P has been set up.")


        self.video_widget = self.loaded_ui.findChild(QVideoWidget, "videoWidget")
        self.slider = self.loaded_ui.findChild(QSlider, "slider")
        self.play_pause_button = self.loaded_ui.findChild(QPushButton, "playButton")
        self.play_pause_button.setStyleSheet("background: transparent; border: none;")
        self.play_pause_button.setIcon(QIcon(PATH+"/icons/play.png"))
        self.play_pause_button.setIconSize(QSize(65, 65))  # アイコンのサイズを指定
        self.copy_time_button = self.loaded_ui.findChild(QPushButton, "copyTimeButton")
        self.minus_10s_button = self.loaded_ui.findChild(QPushButton, "minus10sButton")
        self.minus_button = self.loaded_ui.findChild(QPushButton, "minusButton")
        self.minus_1s_button = self.loaded_ui.findChild(QPushButton, "minus1sButton")
        self.minus_frame_button = self.loaded_ui.findChild(QPushButton, "minus1fButton")
        self.plus_frame_button = self.loaded_ui.findChild(QPushButton, "plus1fButton")
        self.plus_1s_button = self.loaded_ui.findChild(QPushButton, "plus1sButton")
        self.plus_button = self.loaded_ui.findChild(QPushButton, "plusButton")
        self.plus_10s_button = self.loaded_ui.findChild(QPushButton, "plus10sButton")
        self.num_label = self.loaded_ui.findChild(QLabel, "numLabel")


        # Menuの設定
        # マージンを設定
        # QMainWindow 内にメニューバーを作成
        menu_bar = self.loaded_ui.menuBar()
        menu_bar.setNativeMenuBar(False)
        # マージンを設定
        #menu_bar.setContentsMargins(10, 0, 10, 0)  # 左、上、右、下のマージンを設定
        # menu_barの高さを設定、小さくしすぎるとメニューが消えるので、普段は使わない
        menu_bar.setFixedHeight(30)

        # スタイルシートで上下中央揃えとボーダーを指定
        menu_bar.setStyleSheet("""
            QMenuBar {
                font-size: 16px;               /* フォントサイズを指定 */
                padding: 0px;                  /* 内側の余白をリセット */
                margin: 0px;                   /* 外側の余白をリセット */
                alignment: center;             /* 水平と垂直の中央揃え */
                border-bottom: 1px solid #d3cfd9; /* 下部に薄い灰色のボーダー */
            }
            QMenuBar::item {
                spacing: 10px;                 /* メニュー項目間のスペース */
                padding: 4px 8px;              /* メニュー項目内のパディング */
            }
        """)

        # メニューを作成
        # フォントを作成
        font = QFont("Noto Sans CJK JP")
        font.setPointSize(16)  # フォントサイズを設定
        # メニューバーにフォントを設定
        menu_bar.setFont(font)


        font2 = QFont("Noto Sans CJK JP")
        font2.setPointSize(14)  # フォントサイズを設定

        # メニューを追加
        file_menu = menu_bar.addMenu("File")
        file_menu.setFont(font2)

        # メニュー項目を追加
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))  # ショートカットを設定
        open_action.triggered.connect(self.open_video)
        file_menu.addAction(open_action)

        load_action = QAction("Load", self)
        load_action.setShortcut(QKeySequence("Ctrl+L"))  # ショートカットを設定
        load_action.triggered.connect(self.load)
        file_menu.addAction(load_action)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))  # ショートカットを設定
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)


        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        file_menu.addAction(quit_action)

        ope_menu = menu_bar.addMenu("Skip")
        ope_menu.setFont(font2)
        # ショートカットの設定
        bw_shortcut = QAction("1min BW", self) 
        bw_shortcut.setShortcut(QKeySequence('Ctrl+Left'))
        bw_shortcut.triggered.connect(self.rewind_1min)

        fw_shortcut = QAction("1min FW", self) 
        fw_shortcut.setShortcut(QKeySequence('Ctrl+Right'))
        fw_shortcut.triggered.connect(self.advance_1min)

        j_shortcut = QAction("Jump", self) 
        j_shortcut.setShortcut(QKeySequence("Ctrl+J"))
        j_shortcut.triggered.connect(self.jump_to_time)
       

        #get_w_shortcut = QAction("Get_W", self) 
        #get_w_shortcut.setShortcut(QKeySequence("Ctrl+P"))
        #get_w_shortcut.triggered.connect(self.print_window_geometry)

        ope_menu.addAction(bw_shortcut)
        ope_menu.addAction(fw_shortcut)
        ope_menu.addAction(j_shortcut)
        #ope_menu.addAction(get_w_shortcut)



        # tableViewを取得
        self.table_view = self.loaded_ui.findChild(QTableView, "tableView")
        #self.table_view.setDropIndicatorShown(True)
        # モデルを作成
        """QTableViewの設定とカラム追加"""
        # カラムヘッダーを設定
        self.model = QStandardItemModel(0, 2)
        self.model.setHorizontalHeaderLabels(["Time", "Chapter"])


        self.table_view.setModel(self.model)

        self.status_bar = self.loaded_ui.findChild(QStatusBar, 'statusbar')
        # カスタム QLabel を作成
        self.custom_status_label = QLabel()
        self.custom_status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 右寄せ
        self.custom_status_label.setStyleSheet("""
            font-family: 'Inconsolata', 'Menlo', 'Courier', 'Monaco';
            font-size: 18px;
        """)
        # ステータスバーにカスタム QLabel を追加
        self.status_bar.addPermanentWidget(self.custom_status_label, 1)
        # titleLabel を取得
        self.title_label = self.loaded_ui.findChild(QLabel, "titleLabel")


        #self.volume_slider = self.findChild(QSlider, "volumeSlider")
        self.add_button = self.loaded_ui.findChild(QPushButton, "addButton")
        self.add_button.clicked.connect(self.add_row)

        self.del_button = self.loaded_ui.findChild(QPushButton, "delButton")
        self.del_button.clicked.connect(self.del_row)

        self.sort_button = self.loaded_ui.findChild(QPushButton, "sortButton")
        self.sort_button.clicked.connect(self.sort_by_time)

        self.jump_button = self.loaded_ui.findChild(QPushButton, "jumpButton")
        self.jump_button.clicked.connect(self.jump_to_time)

        self.save_button = self.loaded_ui.findChild(QPushButton, "saveButton")
        self.save_button.clicked.connect(self.save)



        # メディアプレイヤーのセットアップ
        self.media_player = QMediaPlayer(self)
        #self.media_player = AdvancedMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)


        # ボタンの接続
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.copy_time_button.clicked.connect(self.copy_time)  # Copy Timeボタンの接続

        # スライダーの接続
        self.slider.sliderMoved.connect(self.set_position)
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)




        # 送りボタンの接続
        self.minus_frame_button.clicked.connect(self.rewind_one_frame)
        self.minus_10s_button.clicked.connect(self.rewind_10_seconds)
        self.minus_1s_button.clicked.connect(self.rewind_1_seconds)
        self.minus_button.clicked.connect(self.rewind_seconds)

        self.plus_frame_button.clicked.connect(self.advance_one_frame)
        self.plus_10s_button.clicked.connect(self.advance_10_seconds)
        self.plus_1s_button.clicked.connect(self.advance_1_seconds)
        self.plus_button.clicked.connect(self.advance_seconds)



        # テーブルモデルの設定
        self.setup_table_view()

        #self.init_ui()

    def showEvent(self, event):
        """ウィンドウが表示されるタイミングでログを出力"""
        super().showEvent(event)
        print("Debug: VideoPlayerApp is now visible.")

    def focusInEvent(self, event):
        """ウィンドウがフォーカスを受け取ったときにログを出力"""
        super().focusInEvent(event)
        print("Debug: VideoPlayerApp received focus.")




    def init_ui(self):
        self.loaded_ui.setGeometry(50, 50, 1376, 723) # WQXGA (Wide-QXGA)
        self.loaded_ui.fontCssLegend = '<style type="text/css"> p {font-family: Arial;font-size: 16pt; color: "#FFF"} </style>'


    def toggle_play_pause(self):
        """再生と一時停止を切り替える"""
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setIcon(QIcon(PATH+"/icons/play.png"))  # 一時停止時にplay.pngを設定
        else:
            self.media_player.play()
            self.play_pause_button.setIcon(QIcon(PATH+"/icons/pause.png"))  # 再生時にpause.pngを設定

    def update_row_column_count(self):
        """行数とカラム数をラベルに表示"""
        row_count = self.model.rowCount()
        column_count = self.model.columnCount()
        self.num_label.setText(f"Rows: {row_count}, Columns: {column_count}")


    def set_position(self, position):
        self.media_player.setPosition(position)

    def update_position(self, position):
        self.slider.setValue(position)
        self.update_time_label()

    def update_duration(self, duration):
        self.slider.setRange(0, duration)
        self.update_time_label()

    def update_time_label(self):
        current_time = self.media_player.position() / 1000  # 現在の再生位置 (秒)
        total_time = self.media_player.duration() / 1000   # 全体の再生時間 (秒)

        # 現在の再生時間のフォーマット
        current_hours, current_remainder = divmod(current_time, 3600)
        current_minutes, current_seconds = divmod(current_remainder, 60)

        # 全体の再生時間のフォーマット
        total_hours, total_remainder = divmod(total_time, 3600)
        total_minutes, total_seconds = divmod(total_remainder, 60)

        self.custom_status_label.setText(
            f"{int(current_hours):01}:{int(current_minutes):02}:{current_seconds:05.2f} / "
            f"{int(total_hours):01}:{int(total_minutes):02}:{total_seconds:05.2f}"
        )


    def copy_time(self):
        """現在の再生位置をクリップボードにコピーする"""
        current_time = self.media_player.position() / 1000  # 現在の再生位置 (秒)

        # 現在の再生時間のフォーマット
        current_hours, current_remainder = divmod(current_time, 3600)
        current_minutes, current_seconds = divmod(current_remainder, 60)

        # フォーマットされた時間を作成
        time_string = f"{int(current_hours):01}:{int(current_minutes):02}:{current_seconds:05.2f}"

        # クリップボードにコピー
        QApplication.clipboard().setText(time_string)
        print(f"Copied to clipboard: {time_string}")

    def setup_table_view(self):
        self.table_view.setDragDropMode(QTableView.DragDrop)  # ドラッグアンドドロップを許可
        self.table_view.setDragEnabled(False)                 # ドラッグを有効化
        self.table_view.setAcceptDrops(False)                 # ドロップを許可
        self.table_view.setDropIndicatorShown(False)          # ドロップインジケータを表示
        # Column 1 の幅を固定に設定
        self.table_view.horizontalHeader().resizeSection(0, 150)  # 0 番目のカラムを 150px に固定
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # Column 2 をストレッチさせる（可変幅）
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def sort_by_time(self):
        # プロキシモデルを使用してソート
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.model)
        
        # Timeカラム(0列目)を昇順にソート
        proxy_model.sort(0, Qt.AscendingOrder)
        
        # ソート結果を新しいモデルに追加
        sorted_data = []
        for row in range(proxy_model.rowCount()):
            row_data = [
                proxy_model.index(row, col).data()
                for col in range(proxy_model.columnCount())
            ]
            sorted_data.append(row_data)

        # 元のモデルをリセットして、ソートされたデータを再挿入
        self.model.setRowCount(0)
        for row_data in sorted_data:
            items = [QStandardItem(field) for field in row_data]
            self.model.appendRow(items)

        # 再設定
        self.table_view.setModel(self.model)


    def rewind_10_seconds(self):
        """再生位置を10秒戻す"""
        current_position = self.media_player.position()  # 現在の再生位置（ミリ秒）
        new_position = max(0, current_position - 10000)  # 10秒（10000ミリ秒）戻す
        self.media_player.setPosition(new_position)
        print(f"Rewound to {new_position / 1000:.2f} seconds")

    def rewind_1_seconds(self):
        """再生位置を.3秒戻す"""
        current_position = self.media_player.position()  # 現在の再生位置（ミリ秒）
        new_position = max(0, current_position - 300)  # 10秒（10000ミリ秒）戻す
        self.media_player.setPosition(new_position)
        print(f"Rewound to {new_position / 1000:.2f} seconds")

    def rewind_seconds(self):
        """再生位置を.3秒戻す"""
        current_position = self.media_player.position()  # 現在の再生位置（ミリ秒）
        new_position = max(0, current_position - 1000)  # 10秒（10000ミリ秒）戻す
        self.media_player.setPosition(new_position)
        print(f"Rewound to {new_position / 1000:.2f} seconds")

    def advance_10_seconds(self):
        """再生位置を10秒進める"""
        current_position = self.media_player.position()  # 現在の再生位置（ミリ秒）
        new_position = max(0, current_position + 10000)  # 10秒（10000ミリ秒）戻す
        self.media_player.setPosition(new_position)
        print(f"Advanced to {new_position / 1000:.2f} seconds")

    def advance_1_seconds(self):
        """再生位置を.3秒進める"""
        current_position = self.media_player.position()  # 現在の再生位置（ミリ秒）
        new_position = max(0, current_position + 300)  # 10秒（10000ミリ秒）戻す
        self.media_player.setPosition(new_position)
        print(f"Advanced to {new_position / 1000:.2f} seconds")

    def advance_seconds(self):
        """再生位置を.3秒進める"""
        current_position = self.media_player.position()  # 現在の再生位置（ミリ秒）
        new_position = max(0, current_position + 1000)  # 10秒（10000ミリ秒）戻す
        self.media_player.setPosition(new_position)
        print(f"Advanced to {new_position / 1000:.2f} seconds")

    def rewind_1min(self):
        """再生位置を1min戻す"""
        current_position = self.media_player.position()  # 現在の再生位置（ミリ秒）
        new_position = max(0, current_position - 60000)  # 60秒（60000ミリ秒）戻す
        self.media_player.setPosition(new_position)
        print(f"Rewound to {new_position / 1000:.2f} seconds")


    def advance_1min(self):
        """再生位置を1min進める"""
        current_position = self.media_player.position()  # 現在の再生位置（ミリ秒）
        new_position = max(0, current_position + 60000)  # 60秒（60000ミリ秒）戻す
        self.media_player.setPosition(new_position)
        print(f"Advanced to {new_position / 1000:.2f} seconds")


    def advance_one_frame(self):
        """再生位置を1フレーム分進める"""
        # フレームごとの再生時間を計算（ミリ秒単位）
        frame_duration_ms = 1000 / self.frame_rate
        # 現在の再生位置を取得
        current_position = self.media_player.position()  # ミリ秒単位
        # 新しい再生位置を計算
        new_position = current_position + frame_duration_ms
        # 再生位置を設定
        self.media_player.setPosition(int(new_position))
        print(f"Advanced 1 frame to {new_position / 1000:.2f} seconds")



    def add_row(self, index=None):
        """行を追加"""
        # 選択されているセルのインデックスを取得
        selected_indexes = self.table_view.selectedIndexes()
        if selected_indexes:
            # 選択されたセルの中で最大の行番号を取得
            max_row = max(index.row() for index in selected_indexes)
            insert_position = max_row + 1  # 選択された最後の行の下に追加
        else:
            # セルが選択されていない場合、末尾に追加
            insert_position = self.model.rowCount()

        # 新しい行を空白セルで作成
        new_row = [QStandardItem("") for _ in range(self.model.columnCount())]
        self.model.insertRow(insert_position, new_row)

        # 行数とカラム数を更新
        self.update_row_column_count()
        print(f"Added row at position {insert_position + 1}")

    def del_row(self, index=None):
        """ハイライトされている行、または編集中の行を削除"""
        # 選択されているセルのインデックスを取得
        selected_indexes = self.table_view.selectedIndexes()
        
        if selected_indexes:
            # 選択されたセルの行番号を取得し、重複を削除
            rows_to_delete = sorted(set(index.row() for index in selected_indexes), reverse=True)

            # 行を削除（逆順で削除してインデックスを崩さない）
            for row in rows_to_delete:
                self.model.removeRow(row)

            # 行数とカラム数を更新
            self.update_row_column_count()
            print(f"Deleted rows: {rows_to_delete}")
        else:
            print("No row selected to delete")

    def get_frame_rate(self, video_path):
        """動画ファイルのフレームレートを取得"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Failed to open video file")
            return 25.0  # デフォルト値
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        print(f"Detected frame rate: {frame_rate} fps")
        return frame_rate



    def set_frame_rate(self, frame_rate):
        """フレームレートを設定"""
        self.frame_rate = frame_rate
        print(f"Frame rate set to {frame_rate} fps")


    def print_window_geometry(self):
        """現在のウィンドウ位置とサイズを出力"""
        print("Debug: print_window_geometry activated.")
        position = self.geometry().topLeft()
        size = self.geometry().size()
        print(f"Window Position: {position}, Size: {size}")

    def open_video(self):
        """動画ファイルを開くダイアログを表示"""
        dialog = QFileDialog(self, "Open Video File","", "Video Files (*.mp4 *.m4v *.avi *.mkv *.mov *.MOV *.ts *.m2ts *.mp3)")

        # ダイアログの位置を調整
        dialog.adjustSize()
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog_geometry = dialog.geometry()
        screen_geometry = QApplication.primaryScreen().geometry()
        self.current_center = self.geometry().center()
        print(self.current_center)
        dialog_geometry.moveCenter(self.current_center)  # 移動後の中心位置を使用
        dialog.setGeometry(dialog_geometry)

        # ダイアログを実行
        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            if file_path:
                self.initialize_video(file_path)


    def load(self):
        """ファイルダイアログを開いて .txt ファイルをロード"""
        # ファイルダイアログを作成
        dialog = QFileDialog(self, "Open .txt File", "", "Text Files (*.txt);;All Files (*)")

        # MainWindow の中心位置を取得
        parent_geometry = self.geometry()
        parent_center = parent_geometry.center()

        # ダイアログの位置を調整
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.adjustSize()
        dialog_geometry = dialog.geometry()
        dialog_geometry.moveCenter(parent_center)
        dialog.setGeometry(dialog_geometry)

        # ダイアログを実行
        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            if file_path:
                try:
                    # ファイルを読み込み
                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = file.readlines()

                    # テーブルモデルをクリア
                    self.model.removeRows(0, self.model.rowCount())

                    # 行ごとにデータを追加
                    for line in lines:
                        line = line.strip()
                        if line:  # 空行をスキップ
                            # 最初のスペースのみで分割
                            items = [QStandardItem(part.strip()) for part in re.split(r'\s+', line, maxsplit=1)]
                            self.model.appendRow(items)

                    print(f"Loaded file: {file_path}")
                    self.update_row_column_count()

                except UnicodeDecodeError:
                    print(f"Error: The file encoding is not UTF-8. Please use a UTF-8 encoded file.")
                except Exception as e:
                    print(f"Error loading file: {e}")



    def save(self):
        """TableViewの内容をスペース区切りで保存"""
        if not hasattr(self, 'file_name') or not self.file_name:
            print("No file name set")
            return

        # 拡張子を .txt に変更
        base_name, _ = os.path.splitext(self.file_name)
        save_file_name = f"{base_name}.txt"

        # ファイルが存在する場合、上書き確認ダイアログを表示
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
            # テーブルの内容を取得
            rows = self.model.rowCount()
            cols = self.model.columnCount()
            with open(save_file_name, "w") as file:
                for row in range(rows):
                    row_data = []
                    for col in range(cols):
                        item = self.model.item(row, col)
                        row_data.append(item.text() if item else "")  # セルが空の場合は空文字列を追加
                    file.write(" ".join(row_data) + "\n")  # 行ごとにスペース区切りで保存

            print(f"Table contents saved to {save_file_name}")
        except Exception as e:
            print(f"Error saving table contents: {e}")


    def quit_application(self):
        """アプリケーションを終了する"""
        QApplication.instance().quit()


    def rewind_one_frame(self):
        """再生位置を1フレーム分戻し、キーフレームかどうかを判定して表示"""
        # フレームごとの再生時間を計算（ミリ秒単位）
        frame_duration_ms = 1000 / self.frame_rate

        # 現在の再生位置を取得
        current_position = self.media_player.position()  # ミリ秒単位
        new_position = max(0, current_position - frame_duration_ms)  # 新しい再生位置を計算

        # 動画ファイルを使用して現在のフレーム情報を取得
        cap = cv2.VideoCapture(self.file_name)  # `self.video_file_path` に動画のパスを設定
        if not cap.isOpened():
            print("Failed to open video file.")
            return

        # 動画フレームレートを取得
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_index = int(new_position / 1000 * fps)  # フレームインデックスを計算

        # フレーム位置を設定
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()

        if not ret:
            print(f"Failed to read frame at index {frame_index}")
            cap.release()
            return

        # キーフレーム判定 (CAP_PROP_POS_AVI_RATIO や CAP_PROP_CODEC_PIXEL_FORMAT を利用する場合もある)
        is_keyframe = cap.get(cv2.CAP_PROP_POS_FRAMES) == frame_index
        frame_type = "Keyframe (I-frame)" if is_keyframe else "Non-keyframe (P/B-frame)"
        print(f"Frame at index {frame_index} is a {frame_type}.")

        # 再生位置を設定
        self.media_player.setPosition(int(new_position))
        print(f"Rewound to {new_position / 1000:.2f} seconds")


    def rewind_1min(self):
        """再生位置を1min戻す"""
        current_position = self.media_player.position()  # 現在の再生位置（ミリ秒）
        new_position = max(0, current_position - 60000)  # 60秒（60000ミリ秒）戻す
        self.media_player.setPosition(new_position)
        print(f"Rewound to {new_position / 1000:.2f} seconds")

    def advance_1min(self):
        """再生位置を1min進める"""
        current_position = self.media_player.position()  # 現在の再生位置（ミリ秒）
        new_position = max(0, current_position + 60000)  # 60秒（60000ミリ秒）戻す
        self.media_player.setPosition(new_position)
        print(f"Advanced to {new_position / 1000:.2f} seconds")

    def jump_to_time(self):
        """ハイライトされた第1カラムの値を取得し再生位置を移動"""
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            print("No cell selected")
            return

        for index in selected_indexes:
            # ハイライトされた行の第1カラムのインデックスを取得
            row = index.row()
            time_index = self.model.index(row, 0)  # 第1カラムのインデックス
            time_str = self.model.data(time_index)

            if time_str:
                try:
                    # 時間形式を正規表現で解析
                    match = re.match(r"^(\d{1,2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?$", time_str)
                    if match:
                        hours, minutes, seconds, milliseconds = match.groups()
                        hours = int(hours)
                        minutes = int(minutes)
                        seconds = int(seconds)
                        milliseconds = int(milliseconds or 0)  # ミリ秒がない場合は0にする

                        # 時間をミリ秒単位に変換
                        total_milliseconds = (
                            hours * 3600000 + minutes * 60000 + seconds * 1000 + milliseconds
                        )

                        # 再生位置を設定
                        self.media_player.setPosition(total_milliseconds)
                        print(f"Jumping to: {total_milliseconds} ms")
                    else:
                        print(f"Invalid time format: {time_str}")
                except Exception as e:
                    print(f"Error parsing time: {e}")
            else:
                print("Empty cell in column 1")
            break  # 最初の選択セルのみ処理



    def initialize_video(self, file_path):
        """動画ファイルをロードして初期化"""
        if not file_path:
            return

        if os.path.exists(file_path):  # ファイルの存在確認
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.play_pause_button.setEnabled(True)

            # フレームレートを設定
            frame_rate = self.get_frame_rate(file_path)
            self.set_frame_rate(frame_rate)

            # ファイル名を抽出
            file_name = os.path.basename(file_path)
            self.title_label.setStyleSheet("QLabel { font-size: 16px ;}")

            # titleLabel にファイル名を表示
            self.title_label.setText(file_name)

            # 動画を再生
            #self.media_player.setPlaybackRate(2.0)
            self.media_player.play()
            self.play_pause_button.setIcon(QIcon(PATH+"/icons/pause.png"))  # 再生時にpause.pngを設定
            self.file_name = file_path  # フルパスで保持
        else:
            print(f"File not found: {file_path}")




if __name__ == "__main__":
    '''
    print("Debug: QApplication instance is about to be created.")
    app = QApplication(sys.argv)
    print("Debug: QApplication instance created.")

    window = VideoPlayerApp()
    print("Debug: VideoPlayerApp instance created.")
    window.show()  # メインウィンドウを表示
    print("Debug: Window is now visible.")

    print(f"Main thread: {threading.current_thread()}")
    print(f"Qt main thread: {QThread.currentThread()}")
    print(f"QCoreApplication instance: {QCoreApplication.instance()}")
    print(f"Active window: {app.activeWindow()}")
    print(f"Focus widget: {app.focusWidget()}")

    sys.exit(app.exec())
    '''

    print("Debug: QApplication instance is about to be created.")
    app = QApplication(sys.argv)
    print("Debug: QApplication instance created.")

    # VideoPlayerApp のインスタンスを作成
    window = VideoPlayerApp()
    print("Debug: VideoPlayerApp instance created.")

    # メインウィンドウを表示
    window.show()
    print("Debug: Window is now visible.")


    # Qt のイベントを処理（ウィンドウの状態更新）
    app.processEvents()

    # フォーカスを明示的に設定
    window.activateWindow()
    window.raise_()
    window.setFocus()


    # デバッグ情報を出力
    print(f"Main thread: {threading.current_thread()}")
    print(f"Qt main thread: {QThread.currentThread()}")
    print(f"QCoreApplication instance: {QCoreApplication.instance()}")
    print(f"Active window: {app.activeWindow()}")
    print(f"Focus widget: {app.focusWidget()}")

    # アプリケーションを実行
    sys.exit(app.exec())

