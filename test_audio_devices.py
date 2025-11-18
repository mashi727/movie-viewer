#!/usr/bin/env python3
"""
音声デバイス切り替え機能のテストスクリプト
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtMultimedia import QMediaDevices

def test_audio_devices():
    """利用可能な音声デバイスをリストアップ"""
    app = QApplication(sys.argv)
    
    print("=== Audio Output Devices ===")
    print()
    
    # 利用可能な音声出力デバイスを取得
    audio_outputs = QMediaDevices.audioOutputs()
    
    if not audio_outputs:
        print("No audio output devices found!")
        return
    
    # デフォルトデバイスを取得
    default_device = QMediaDevices.defaultAudioOutput()
    default_id = default_device.id().data().decode('utf-8') if default_device.id() else None
    
    print(f"Found {len(audio_outputs)} audio output device(s):\n")
    
    for i, device in enumerate(audio_outputs):
        device_id = device.id().data().decode('utf-8') if device.id() else 'unknown'
        device_name = device.description()
        is_default = device_id == default_id
        
        print(f"{i + 1}. {device_name}")
        print(f"   ID: {device_id}")
        if is_default:
            print("   [DEFAULT DEVICE]")
        print()
    
    # デバイス変更の監視をテスト
    def on_devices_changed():
        print("Audio devices have been changed!")
    
    QMediaDevices.audioOutputsChanged.connect(on_devices_changed)
    
    print("Monitor is active. Connect/disconnect audio devices to test detection.")
    print("Press Ctrl+C to exit.")
    
    try:
        app.exec()
    except KeyboardInterrupt:
        print("\nTest completed.")

if __name__ == "__main__":
    test_audio_devices()