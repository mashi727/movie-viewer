#!/usr/bin/env python3
"""
Test script to verify M4A audio file support in Movie Viewer
"""

import sys
from pathlib import Path

# Add parent directory to path for development testing
sys.path.insert(0, str(Path(__file__).parent))

from movie_viewer.utils.platform_utils import PlatformUtils


def test_file_extensions():
    """Test that M4A is included in supported extensions"""
    print("Testing file extension support...")

    # Get video extensions
    video_extensions = PlatformUtils.get_video_extensions()
    print(f"Video extensions count: {len(video_extensions)}")

    # Check if M4A is included
    m4a_found = any('*.m4a' in ext.lower() for ext in video_extensions)
    print(f"M4A in video extensions: {m4a_found}")

    # Get audio extensions
    audio_extensions = PlatformUtils.get_audio_extensions()
    print(f"Audio extensions count: {len(audio_extensions)}")

    # Check if M4A is in audio extensions
    m4a_in_audio = any('*.m4a' in ext.lower() for ext in audio_extensions)
    print(f"M4A in audio extensions: {m4a_in_audio}")

    print("\nAudio extensions:")
    for ext in sorted(set(e.lower() for e in audio_extensions)):
        print(f"  {ext}")

    return m4a_found and m4a_in_audio


def test_audio_detection():
    """Test audio file detection"""
    print("\nTesting audio file detection...")

    test_files = [
        "test.mp4",
        "test.m4a",
        "test.mp3",
        "test.wav",
        "test.avi",
        "test.flac",
        "test.M4A",  # Test case sensitivity
    ]

    for filename in test_files:
        is_audio = PlatformUtils.is_audio_file(filename)
        print(f"  {filename}: {'Audio' if is_audio else 'Video'}")

    # Specific M4A test
    assert PlatformUtils.is_audio_file("test.m4a"), "M4A should be detected as audio"
    assert PlatformUtils.is_audio_file("TEST.M4A"), "M4A should be case-insensitive"
    assert not PlatformUtils.is_audio_file("test.mp4"), "MP4 should not be audio"

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing M4A Support in Movie Viewer")
    print("=" * 60)

    tests_passed = []

    # Test 1: File extensions
    try:
        result = test_file_extensions()
        tests_passed.append(("File Extensions", result))
    except Exception as e:
        print(f"Error in file extensions test: {e}")
        tests_passed.append(("File Extensions", False))

    # Test 2: Audio detection
    try:
        result = test_audio_detection()
        tests_passed.append(("Audio Detection", result))
    except Exception as e:
        print(f"Error in audio detection test: {e}")
        tests_passed.append(("Audio Detection", False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)

    all_passed = True
    for test_name, passed in tests_passed:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n✓ All tests passed! M4A support is working correctly.")
    else:
        print("\n✗ Some tests failed. Please check the implementation.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())