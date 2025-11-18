# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Movie Viewer is a PySide6-based video player application with chapter management and audio waveform visualization capabilities. The application supports various video formats and provides frame-precise navigation with keyboard shortcuts.

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

3. **ChapterTableManager** (`movie_viewer/core/chapter_manager.py`): Manages chapter/bookmark functionality with QTableView, handles saving/loading chapter files in timestamp format.

4. **AudioAnalyzer** (`movie_viewer/core/audio_analyzer.py`): Extracts and processes audio from video files using ffmpeg/ffprobe for waveform visualization.

5. **WaveformWidget** (`movie_viewer/ui/waveform_widget.py`): PyQtGraph-based widget for displaying audio waveforms and spectrograms with interactive playback position tracking.

### Key Design Patterns

- **MVC Pattern**: Separation between UI (views), business logic (controllers), and data models
- **Qt Signal/Slot**: Communication between components using Qt's signal/slot mechanism
- **Resource Management**: Proper handling of media resources and Qt objects

### Dependencies

- **PySide6**: Qt bindings for Python (main UI framework)
- **OpenCV**: Video processing and frame extraction
- **PyQtGraph**: Scientific graphics and waveform visualization
- **NumPy/SciPy**: Audio signal processing
- **ffmpeg**: Audio extraction (external dependency)

## Current Feature Branch

The `feature/audio-waveform` branch adds audio visualization capabilities:
- Audio extraction using ffmpeg
- Waveform display with PyQtGraph
- Interactive position tracking synchronized with video playback
- Spectrogram visualization support

## Important Considerations

1. **Platform-specific code**: Dark mode detection uses `pyobjc-framework-Cocoa` on macOS
2. **External dependencies**: Requires ffmpeg/ffprobe for audio extraction
3. **Frame accuracy**: Uses OpenCV for precise frame-by-frame navigation
4. **Resource paths**: Uses `importlib.resources` for package-compatible resource loading
5. **Chapter file format**: Simple text format with timestamps (HH:MM:SS.ff) and descriptions