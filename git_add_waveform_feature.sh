#!/bin/bash

# 波形表示機能をGitで管理するためのスクリプト
# 使用方法: bash git_add_waveform_feature.sh

set -e

echo "================================================"
echo "波形表示機能のGit管理スクリプト"
echo "================================================"
echo ""

# Gitリポジトリの確認
if [ ! -d ".git" ]; then
    echo "エラー: Gitリポジトリではありません。"
    echo "movie_viewerのルートディレクトリで実行してください。"
    exit 1
fi

# 現在のブランチを確認
CURRENT_BRANCH=$(git branch --show-current)
echo "現在のブランチ: $CURRENT_BRANCH"
echo ""

# ステップ1: ブランチの作成
echo "1. フィーチャーブランチの作成"
echo "--------------------------------"
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "警告: 現在mainブランチにいません。"
    read -p "続行しますか？ (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 変更がある場合は保存
if [ -n "$(git status --porcelain)" ]; then
    echo "未コミットの変更があります。"
    echo "stashに保存しますか？"
    read -p "(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git stash save "WIP: before creating waveform feature branch"
        echo "変更をstashに保存しました。"
    fi
fi

# フィーチャーブランチの作成
FEATURE_BRANCH="feature/audio-waveform"
echo ""
echo "フィーチャーブランチを作成: $FEATURE_BRANCH"
git checkout -b $FEATURE_BRANCH 2>/dev/null || {
    echo "ブランチが既に存在します。切り替えます。"
    git checkout $FEATURE_BRANCH
}

echo ""
echo "2. ファイルの作成と更新"
echo "--------------------------------"
echo "以下のコマンドを実行してファイルを作成/更新してください:"
echo ""
echo "  # 自動更新スクリプトを実行"
echo "  bash update_waveform_feature.sh"
echo "  bash update_app_py.sh"
echo ""
read -p "ファイルの作成/更新が完了したら Enter を押してください..."

# ステップ3: 段階的なコミット
echo ""
echo "3. 段階的なコミット"
echo "--------------------------------"

# 関数: コミットを作成
create_commit() {
    local files=$1
    local message=$2
    
    echo ""
    echo "コミット: $message"
    echo "対象ファイル: $files"
    
    # ファイルの存在確認とステージング
    for file in $files; do
        if [ -f "$file" ] || [ -d "$file" ]; then
            git add "$file"
        else
            echo "警告: $file が見つかりません"
        fi
    done
    
    # 変更があればコミット
    if [ -n "$(git diff --cached --name-only)" ]; then
        git commit -m "$message"
        echo "✓ コミット完了"
    else
        echo "- 変更なし（スキップ）"
    fi
}

# 依存関係のコミット
create_commit "requirements.txt setup.py pyproject.toml" \
"feat: Add dependencies for audio waveform visualization

- Add pyqtgraph>=0.13.0 for waveform plotting
- Add numpy>=1.21.0 and scipy>=1.7.0 for audio processing
- Update setup.py with new requirements"

# 音声解析機能のコミット
create_commit "movie_viewer/core/audio_analyzer.py movie_viewer/core/__init__.py" \
"feat: Add AudioAnalyzer class for audio extraction

- Extract audio from video using ffmpeg
- Implement waveform data generation with RMS downsampling
- Add spectrogram calculation functionality
- Support various audio formats through ffmpeg"

# 波形ウィジェットのコミット
create_commit "movie_viewer/ui/waveform_widget.py movie_viewer/ui/__init__.py" \
"feat: Add WaveformWidget for audio visualization

- Implement interactive waveform display with PyQtGraph
- Add real-time spectrogram visualization
- Support region selection for detailed view
- Enable click-to-seek functionality"

# メインアプリケーションのコミット
create_commit "movie_viewer/app.py" \
"feat: Integrate waveform display into main application

- Add waveform widget to main window with QSplitter
- Connect audio analyzer with video playback
- Synchronize playback position with waveform display
- Auto-extract audio when video is loaded"

# ドキュメントのコミット（もし更新していれば）
if [ -f "README_waveform_addition.md" ]; then
    cat README_waveform_addition.md >> README.md
    create_commit "README.md" \
"docs: Update README with waveform feature documentation

- Add feature description and usage instructions
- Document ffmpeg system requirement
- Include troubleshooting section
- Add technical specifications"
fi

echo ""
echo "4. リモートへのプッシュ"
echo "--------------------------------"
echo "以下のコマンドでリモートにプッシュできます:"
echo ""
echo "  git push -u origin $FEATURE_BRANCH"
echo ""
echo "5. Pull Requestの作成"
echo "--------------------------------"
echo "GitHubで以下のURLにアクセスしてPRを作成:"
echo ""
echo "  https://github.com/mashi727/movie_viewer/compare/main...$FEATURE_BRANCH"
echo ""
echo "PRテンプレート:"
echo ""
cat << 'EOF'
## 🎵 音声波形表示機能の追加

### 概要
動画プレイヤーに音声波形とスペクトログラムの表示機能を追加しました。
これにより、音声の視覚的な確認が可能になり、チャプターの頭出しが容易になります。

### 主な変更内容
- ✨ リアルタイム音声波形表示
- 📊 スペクトログラム可視化
- 🖱️ クリックによる再生位置制御
- 🎯 リージョン選択による詳細表示

### 技術仕様
- **音声抽出**: ffmpeg (要インストール)
- **信号処理**: numpy, scipy
- **可視化**: PyQtGraph
- **UI統合**: PySide6 QSplitter

### スクリーンショット
[TODO: 波形表示のスクリーンショットを追加]

### テスト手順
1. `pip install -e .` で依存関係をインストール
2. `movie-viewer` でアプリを起動
3. 動画ファイルを開く（Ctrl+O）
4. 下部に波形が表示されることを確認

### チェックリスト
- [x] コードのテスト完了
- [x] ドキュメント更新
- [x] 新規依存関係の追加
- [ ] コードレビュー
- [ ] 動作確認

### 備考
- ffmpegのインストールが必要です
- 長時間の動画では音声抽出に時間がかかる場合があります
EOF

echo ""
echo "================================================"
echo "完了！"
echo "================================================"
