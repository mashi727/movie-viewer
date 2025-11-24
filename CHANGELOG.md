# Changelog

All notable changes to Movie Viewer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-25

### Added
- Full support for M4A audio files and other audio formats (AAC, WAV, FLAC, OGG, Opus, WMA, AIFF)
- Automatic audio file detection with `is_audio_file()` method
- Dedicated audio playback mode with optimized UI layout
- Enhanced waveform visualization for audio-only files
- `show_full_waveform()` method for better audio visualization
- `get_audio_extensions()` method to retrieve supported audio formats
- Test script for M4A support verification

### Changed
- Application description updated from "video player" to "media player"
- File dialog now shows all supported media formats
- Video widget automatically hides when playing audio files
- Waveform display expands to 70% of window height for audio files
- File title shows [Audio] or [Video] prefix for clarity

### Fixed
- Improved file format detection for case-insensitive matching

## [1.0.0] - 2025-07-09

### Initial Release
- Video playback support for multiple formats (MP4, AVI, MKV, MOV, TS, M2TS)
- Frame-by-frame navigation for precise video editing
- Chapter/bookmark management with timestamps
- Audio waveform and spectrogram visualization
- Dark/Light mode support with OS detection
- Keyboard shortcuts for efficient navigation
- YouTube chapter parsing and import
- Audio device selection and switching
- Save and load chapter lists in text format