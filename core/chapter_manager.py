"""
チャプターテーブル管理機能
"""

import re
from typing import Optional, List
from PySide6.QtWidgets import QTableView, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QSortFilterProxyModel

from .models import TimePosition


class ChapterTableManager:
    """チャプターテーブルの管理を担当するクラス"""
    
    def __init__(self, table_view: QTableView):
        self.table_view = table_view
        self.model = QStandardItemModel(0, 2)
        self.model.setHorizontalHeaderLabels(["Time", "Chapter"])
        self.table_view.setModel(self.model)
        self._setup_table_view()
    
    def _setup_table_view(self):
        """テーブルビューの設定"""
        self.table_view.setDragDropMode(QTableView.DragDrop)
        self.table_view.setDragEnabled(False)
        self.table_view.setAcceptDrops(False)
        self.table_view.setDropIndicatorShown(False)
        
        # カラム幅の設定
        header = self.table_view.horizontalHeader()
        header.resizeSection(0, 150)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
    
    def add_row(self, at_position: Optional[int] = None) -> int:
        """行を追加"""
        if at_position is None:
            selected_indexes = self.table_view.selectedIndexes()
            if selected_indexes:
                at_position = max(index.row() for index in selected_indexes) + 1
            else:
                at_position = self.model.rowCount()
        
        new_row = [QStandardItem("") for _ in range(self.model.columnCount())]
        self.model.insertRow(at_position, new_row)
        return at_position
    
    def delete_selected_rows(self) -> List[int]:
        """選択された行を削除"""
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            return []
        
        rows_to_delete = sorted(
            set(index.row() for index in selected_indexes), 
            reverse=True
        )
        
        for row in rows_to_delete:
            self.model.removeRow(row)
        
        return rows_to_delete
    
    def sort_by_time(self):
        """時間順でソート"""
        proxy_model = QSortFilterProxyModel(self.table_view)
        proxy_model.setSourceModel(self.model)
        proxy_model.sort(0, Qt.AscendingOrder)
        
        # ソート結果を取得
        sorted_data = []
        for row in range(proxy_model.rowCount()):
            row_data = [
                proxy_model.index(row, col).data()
                for col in range(proxy_model.columnCount())
            ]
            sorted_data.append(row_data)
        
        # モデルを再構築
        self.model.setRowCount(0)
        for row_data in sorted_data:
            items = [QStandardItem(field) for field in row_data]
            self.model.appendRow(items)
    
    def get_selected_time(self) -> Optional[TimePosition]:
        """選択された行の時間を取得"""
        selected_indexes = self.table_view.selectedIndexes()
        if not selected_indexes:
            return None
        
        row = selected_indexes[0].row()
        time_str = self.model.data(self.model.index(row, 0))
        
        if time_str:
            return TimePosition.from_string(time_str)
        return None
    
    def get_row_column_count(self) -> tuple[int, int]:
        """行数とカラム数を取得"""
        return self.model.rowCount(), self.model.columnCount()
    
    def save_to_file(self, file_path: str):
        """テーブル内容をファイルに保存"""
        rows = self.model.rowCount()
        cols = self.model.columnCount()
        
        with open(file_path, "w", encoding="utf-8") as file:
            for row in range(rows):
                row_data = []
                for col in range(cols):
                    item = self.model.item(row, col)
                    row_data.append(item.text() if item else "")
                file.write(" ".join(row_data) + "\n")
    
    def load_from_file(self, file_path: str):
        """ファイルからテーブル内容を読み込み"""
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        self.model.removeRows(0, self.model.rowCount())
        
        for line in lines:
            line = line.strip()
            if line:
                items = [
                    QStandardItem(part.strip()) 
                    for part in re.split(r'\s+', line, maxsplit=1)
                ]
                # 不足している列を空文字で埋める
                while len(items) < self.model.columnCount():
                    items.append(QStandardItem(""))
                self.model.appendRow(items)
