# Movie Viewer

A feature-rich video player application with chapter management capabilities built with PySide6.

## Features

- Play various video formats (MP4, AVI, MKV, MOV, TS, M2TS, MP3)
- Frame-by-frame navigation
- Chapter/bookmark management with time stamps
- Dark/Light mode support (automatic OS detection)
- Keyboard shortcuts for efficient navigation
- Save and load chapter lists

## Installation

### From GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/mashi727/movie_viewer.git
cd movie_viewer

# Install in development mode
pip install -e .

# Or install directly from GitHub
pip install git+https://github.com/mashi727/movie_viewer.git
```

### From PyPI (if published)

```bash
pip install movie-viewer
```

### macOS Users

For dark mode detection on macOS, install with:

```bash
pip install movie-viewer[macos]
```

## Usage

After installation, you can run the application from anywhere:

```bash
movie-viewer
```

Or run as a Python module:

```bash
python -m movie_viewer
```

## Keyboard Shortcuts

- `Ctrl+O` - Open video file
- `Ctrl+L` - Load chapter file
- `Ctrl+S` - Save chapter file
- `Ctrl+P` - Print window geometry (debug)
- `Ctrl+J` - Jump to selected time
- `Ctrl+←` - Rewind 1 minute
- `Ctrl+→` - Forward 1 minute
- `Space` - Play/Pause (when video widget has focus)

## Controls

- **-10s / +10s** - Skip backward/forward 10 seconds
- **-1s / +1s** - Skip backward/forward 1 second
- **-.3s / +.3s** - Skip backward/forward 0.3 seconds
- **-1f / +1f** - Skip backward/forward 1 frame
- **COPY** - Copy current timestamp to clipboard
- **Row add/del** - Add or delete chapter entries
- **SORT** - Sort chapters by time
- **Jump** - Jump to selected chapter time
- **Save** - Save chapter list

## Chapter File Format

Chapter files are saved as `.txt` files with the same name as the video file. Format:

```
0:00:00.00 Opening
0:05:23.50 Chapter 1 - Introduction
0:12:45.00 Chapter 2 - Main Content
```

## Requirements

- Python 3.8+
- PySide6 6.5.0+
- OpenCV-Python 4.8.0+
- pyobjc-framework-Cocoa 9.0.0+ (macOS only, for dark mode detection)

## Development

```bash
# Clone repository
git clone https://github.com/mashi727/movie_viewer.git
cd movie_viewer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black movie_viewer

# Check code style
flake8 movie_viewer
```

## Project Structure

```
movie_viewer/
├── __init__.py
├── main.py              # Entry point
├── app.py               # Main application
├── ui/
│   ├── custom_ui_loader.py
│   └── video_player.ui
├── core/
│   ├── video_controller.py
│   ├── chapter_manager.py
│   └── models.py
├── utils/
│   ├── dark_mode.py
│   └── style_manager.py
└── icons/
    ├── play.png
    └── pause.png
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

mashi727

## Acknowledgments

- Built with PySide6 (Qt for Python)
- Video processing with OpenCV
- Icons from [your icon source]