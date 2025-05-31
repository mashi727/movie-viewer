"""
カスタムUIローダー
"""

from PySide6.QtUiTools import QUiLoader
from PySide6.QtMultimediaWidgets import QVideoWidget


class CustomUiLoader(QUiLoader):
    """カスタムUIローダークラス"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
    
    def createWidget(self, class_name, parent=None, name=""):
        """ウィジェットを作成"""
        if class_name == "QVideoWidget":
            widget = QVideoWidget(parent)
        else:
            widget = super().createWidget(class_name, parent, name)
        
        if parent and widget:
            widget.setObjectName(name)
        return widget
