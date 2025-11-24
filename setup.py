"""
Movie Viewer パッケージのセットアップ設定
"""

from setuptools import setup, find_packages
from pathlib import Path

# READMEを読み込む
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="movie-viewer",
    version="1.0.1",
    author="mashi727",
    author_email="your.email@example.com",
    description="A media player application with chapter management and audio support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mashi727/movie_viewer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video :: Display",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.5.0",
        "opencv-python>=4.8.0",
        "pyqtgraph>=0.13.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "macos": ["pyobjc-framework-Cocoa>=9.0.0"],
    },
    entry_points={
        "console_scripts": [
            "movie-viewer=movie_viewer.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "movie_viewer": [
            "ui/*.ui",
            "icons/*.png",
        ],
    },
)