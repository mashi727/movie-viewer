# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Movie Viewer is a PySide6-based media player application with chapter management and audio waveform visualization capabilities. The application supports various video and audio formats (including M4A) and provides frame-precise navigation with keyboard shortcuts. Audio files are displayed with enhanced waveform visualization.

## Development Commands

### Installation
```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install with macOS dark mode support
pip install -e ".[macos]"
```

### Running the Application
```bash
# Run as module
python -m movie_viewer

# Or using the entry point
movie-viewer
```

### Code Quality
```bash
# Format code with black
black movie_viewer

# Check code style with flake8
flake8 movie_viewer

# Type checking with mypy
mypy movie_viewer

# Run tests (when available)
pytest
```

## Architecture

### Core Components

1. **VideoPlayerApp** (`movie_viewer/app.py`): Main application window that integrates all components including video player, chapter manager, and waveform visualization.

2. **VideoController** (`movie_viewer/core/video_controller.py`): Handles video playback control, frame-accurate seeking, and frame rate detection using OpenCV.

3. **ChapterTableManager** (`movie_viewer/core/chapter_manager.py`): Manages chapter/bookmark functionality with QTableView, handles saving/loading chapter files in timestamp format, and supports YouTube chapter parsing.

4. **AudioAnalyzer** (`movie_viewer/core/audio_analyzer.py`): Extracts and processes audio from video files using ffmpeg/ffprobe for waveform visualization.

5. **WaveformWidget** (`movie_viewer/ui/waveform_widget.py`): PyQtGraph-based widget for displaying audio waveforms and spectrograms with interactive playback position tracking.

6. **AudioDeviceManager** (`movie_viewer/core/audio_device_manager.py`): Manages audio output device selection and switching with Qt signal/slot communication.

### Key Design Patterns

- **MVC Pattern**: Separation between UI (views), business logic (controllers), and data models
- **Qt Signal/Slot**: Communication between components using Qt's signal/slot mechanism
- **Resource Management**: Proper handling of media resources and Qt objects using importlib.resources

### Dependencies

- **PySide6 >= 6.5.0**: Qt bindings for Python (main UI framework)
- **opencv-python >= 4.8.0**: Video processing and frame extraction
- **pyqtgraph >= 0.13.0**: Scientific graphics and waveform visualization
- **numpy >= 1.21.0, scipy >= 1.7.0**: Audio signal processing
- **ffmpeg/ffprobe**: Audio extraction (external dependency)
- **pyobjc-framework-Cocoa >= 9.0.0**: macOS dark mode detection (optional)

## Important Considerations

1. **Platform-specific code**: Dark mode detection uses `pyobjc-framework-Cocoa` on macOS with subprocess fallback
2. **External dependencies**: Requires ffmpeg/ffprobe for audio extraction
3. **Frame accuracy**: Uses OpenCV for precise frame-by-frame navigation (video files only)
4. **Resource paths**: Uses `importlib.resources` for package-compatible resource loading
5. **Chapter file format**: Simple text format with timestamps (HH:MM:SS.mmm) and descriptions
6. **YouTube chapter parsing**: Supports pasting YouTube chapters with Ctrl+V in the chapter table
7. **Audio file support**: M4A and other audio formats are fully supported with optimized waveform display
8. **Media type detection**: Automatically detects audio vs video files and adjusts UI accordingly

## Keyboard Shortcuts

- **Space**: Play/Pause (when video widget has focus)
- **Shift+<**: Backward 1 frame
- **Shift+>**: Forward 1 frame
- **Shift+?**: Show help dialog
- **Ctrl+O**: Open video file
- **Ctrl+L**: Load chapter file
- **Ctrl+S**: Save chapter file
- **Ctrl+J**: Jump to selected chapter
- **Ctrl+V**: Paste YouTube chapters (when table has focus)
- **Ctrl+Left/Right**: Skip ±1 minute

## UI Layout

The application uses a vertical splitter layout:
- Upper 70%: Video player with controls and chapter table
- Lower 30%: Audio waveform visualization with spectrogram