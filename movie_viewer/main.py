#!/usr/bin/env python
"""
Movie Viewer - メインエントリーポイント
"""

import sys
import threading
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, QCoreApplication

# パッケージとして実行される場合と直接実行される場合の両方に対応
if __name__ == "__main__":
    from app import VideoPlayerApp
else:
    from .app import VideoPlayerApp


def main():
    """メインエントリーポイント"""
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


if __name__ == "__main__":
    main()