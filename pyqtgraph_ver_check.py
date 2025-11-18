#!/usr/bin/env python3
"""
PyQtGraphの環境チェックスクリプト
"""

import sys

print("=== PyQtGraph環境チェック ===")
print()

# PyQtGraphのバージョン確認
try:
    import pyqtgraph as pg
    print(f"PyQtGraph version: {pg.__version__}")
except ImportError:
    print("ERROR: PyQtGraph is not installed!")
    print("Install with: pip install pyqtgraph")
    sys.exit(1)

# 関連パッケージの確認
packages = ['numpy', 'scipy', 'PySide6']
for package in packages:
    try:
        module = __import__(package)
        version = getattr(module, '__version__', 'unknown')
        print(f"{package} version: {version}")
    except ImportError:
        print(f"WARNING: {package} is not installed!")

print()
print("=== 互換性チェック ===")

# LinearRegionItemのメソッド確認
try:
    region = pg.LinearRegionItem()
    methods = ['setPen', 'setBrush', 'setBounds', 'setRegion', 'getRegion']
    
    print("\nLinearRegionItem available methods:")
    for method in methods:
        if hasattr(region, method):
            print(f"  ✓ {method}")
        else:
            print(f"  ✗ {method} (not available)")
    
    # lines属性の確認
    if hasattr(region, 'lines'):
        print(f"  ✓ lines attribute (contains {len(region.lines)} lines)")
    else:
        print("  ✗ lines attribute (not available)")
    
except Exception as e:
    print(f"Error checking LinearRegionItem: {e}")

# PlotItemのメソッド確認
try:
    app = pg.mkQApp()
    plot = pg.PlotItem()
    methods = ['setBackgroundBrush', 'getViewBox']
    
    print("\nPlotItem available methods:")
    for method in methods:
        if hasattr(plot, method):
            print(f"  ✓ {method}")
        else:
            print(f"  ✗ {method} (not available)")
    
    # ViewBoxのメソッド確認
    if hasattr(plot, 'getViewBox'):
        vb = plot.getViewBox()
        if hasattr(vb, 'setBackgroundColor'):
            print("  ✓ ViewBox.setBackgroundColor")
        else:
            print("  ✗ ViewBox.setBackgroundColor (not available)")
            
except Exception as e:
    print(f"Error checking PlotItem: {e}")

print()
print("=== 推奨事項 ===")
if hasattr(pg, '__version__'):
    ver = pg.__version__
    if ver < '0.13.0':
        print(f"WARNING: PyQtGraph {ver} is old. Recommend upgrading to 0.13.0+")
        print("Upgrade with: pip install pyqtgraph --upgrade")
    else:
        print(f"PyQtGraph {ver} is up to date.")
