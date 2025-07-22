"""
チャプターテーブル管理機能
"""

import re
#from typing import Optional, List
from typing import List, Tuple, Optional
from PySide6.QtWidgets import QTableView, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QKeySequence
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


    """既存のクラスに以下のメソッドを追加"""
    
    def paste_youtube_chapters(self):
        """
        クリップボードからYouTubeチャプター形式のデータをペースト
        """
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        if not text:
            print("Clipboard is empty")
            return
        
        try:
            # チャプター情報を解析
            chapters = self._parse_youtube_chapters(text)
            
            if not chapters:
                print("No valid chapter data found in clipboard")
                return
            
            # 現在の行数を取得
            current_rows = self.model.rowCount()
            
            # 新しい行を追加してデータを設定
            for time_str, title in chapters:
                # 新しい行を追加
                self.model.insertRow(current_rows)
                
                # 時間を設定
                time_index = self.model.index(current_rows, 0)
                self.model.setData(time_index, time_str, Qt.EditRole)
                
                # タイトルを設定
                title_index = self.model.index(current_rows, 1)
                self.model.setData(title_index, title, Qt.EditRole)
                
                current_rows += 1
            
            print(f"Pasted {len(chapters)} chapters from clipboard")
            
            # テーブルを更新
            self.table_view.resizeColumnsToContents()
            
        except Exception as e:
            print(f"Error pasting chapters: {e}")
    

    def _parse_youtube_chapters(self, text: str) -> List[Tuple[str, str]]:
        """
        YouTubeのチャプター形式のテキストを解析
        
        Args:
            text: チャプター情報を含むテキスト
            
        Returns:
            [(時間, タイトル), ...] のリスト
        """
        chapters = []
        
        # まず改行で分割を試みる
        lines = text.strip().split('\n')
        
        # 改行がない場合（1行のみ）、時間パターンで分割する
        if len(lines) == 1 and lines[0]:
            # 時間形式のパターン (HH:MM:SS.mmm または MM:SS.mmm または HH:MM:SS または MM:SS)
            time_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2}\.\d{3}|\d{1,2}:\d{2}\.\d{3}|\d{1,2}:\d{2}:\d{2}|\d{1,2}:\d{2})')
            
            # 時間パターンを全て見つける
            matches = list(time_pattern.finditer(lines[0]))
            
            if len(matches) > 1:
                # 複数の時間が見つかった場合、時間をセパレータとして使用
                for i, match in enumerate(matches):
                    time_str = match.group(1)
                    
                    # タイトルを抽出
                    if i + 1 < len(matches):
                        # 次の時間の開始位置まで
                        title = lines[0][match.end():matches[i+1].start()].strip()
                    else:
                        # 最後の時間の場合、文字列の最後まで
                        title = lines[0][match.end():].strip()
                    
                    # タイトルから先頭の区切り文字を削除
                    title = re.sub(r'^[-\s]+', '', title)
                    
                    # 時間を正規化
                    normalized_time = self._normalize_time(time_str)
                    
                    if title:  # タイトルがある場合のみ追加
                        chapters.append((normalized_time, title))
                
                return chapters
        
        # 通常の改行区切りの処理
        # 時間形式のパターン (HH:MM:SS.mmm または MM:SS.mmm または HH:MM:SS または MM:SS)
        time_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2}\.\d{3}|\d{1,2}:\d{2}\.\d{3}|\d{1,2}:\d{2}:\d{2}|\d{1,2}:\d{2})')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 時間を探す
            time_matches = list(time_pattern.finditer(line))
            
            if time_matches:
                # 複数の時間がある場合の処理
                for i, match in enumerate(time_matches):
                    time_str = match.group(1)
                    
                    # タイトルを抽出
                    if i == 0:
                        # 最初の時間の場合
                        before = line[:match.start()].strip()
                        if i + 1 < len(time_matches):
                            # 次の時間までの間
                            after = line[match.end():time_matches[i+1].start()].strip()
                        else:
                            # 最後まで
                            after = line[match.end():].strip()
                    else:
                        # 2番目以降の時間
                        before = line[time_matches[i-1].end():match.start()].strip()
                        if i + 1 < len(time_matches):
                            after = line[match.end():time_matches[i+1].start()].strip()
                        else:
                            after = line[match.end():].strip()
                    
                    # タイトルの決定
                    title = after if after else before
                    
                    # タイトルから先頭の区切り文字を削除
                    title = re.sub(r'^[-\s]+', '', title)
                    
                    # 時間を正規化
                    normalized_time = self._normalize_time(time_str)
                    
                    if title:  # タイトルがある場合のみ追加
                        chapters.append((normalized_time, title))
        
        return chapters

    def _normalize_time(self, time_str: str) -> str:
        """
        時間文字列を正規化
        MM:SS -> 0:MM:SS.000
        HH:MM:SS -> HH:MM:SS.000
        MM:SS.mmm -> 0:MM:SS.mmm
        HH:MM:SS.mmm -> HH:MM:SS.mmm
        """
        # ミリ秒部分を分離
        parts = time_str.split('.')
        time_part = parts[0]
        ms_part = parts[1] if len(parts) > 1 else '000'
        
        # 時:分:秒を分離
        time_components = time_part.split(':')
        
        if len(time_components) == 2:  # MM:SS
            hours = 0
            minutes = int(time_components[0])
            seconds = int(time_components[1])
        elif len(time_components) == 3:  # HH:MM:SS
            hours = int(time_components[0])
            minutes = int(time_components[1])
            seconds = int(time_components[2])
        else:
            return time_str
        
        # ミリ秒を3桁に正規化
        ms_part = ms_part.ljust(3, '0')[:3]
        
        return f"{hours}:{minutes:02d}:{seconds:02d}.{ms_part}"

