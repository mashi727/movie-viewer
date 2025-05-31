"""
アプリケーションのスタイル管理
"""


class StyleManager:
    """スタイル管理を担当するクラス"""
    
    @staticmethod
    def get_button_style(dark_mode: bool) -> str:
        """ボタンのスタイルシートを取得"""
        if dark_mode:
            return """
                QPushButton {
                    background-color: #44617b;
                    color: white;
                    border: 0px solid #B39CD9;
                    border-radius: 10px;
                    padding: 0px 0px;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #895b8a;
                }
                QPushButton:pressed {
                    background-color: #b44c97;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #e4d2d8;
                    color: black;
                    border: 1px solid #e7e7eb;
                    border-radius: 10px;
                    padding: 0px 0px;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #c4a3bf;
                }
                QPushButton:pressed {
                    background-color: #cc7eb1;
                }
            """
    
    @staticmethod
    def get_menu_style() -> str:
        """メニューバーのスタイルシートを取得"""
        return """
            QMenuBar {
                font-size: 16px;
                padding: 0px;
                margin: 0px;
                alignment: center;
                border-bottom: 1px solid #d3cfd9;
            }
            QMenuBar::item {
                spacing: 10px;
                padding: 4px 8px;
            }
        """
    
    @staticmethod
    def get_status_label_style() -> str:
        """ステータスラベルのスタイルシートを取得"""
        return """
            font-family: 'Inconsolata', 'Menlo', 'Courier', 'Monaco';
            font-size: 18px;
        """
