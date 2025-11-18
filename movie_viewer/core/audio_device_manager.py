"""
音声デバイス管理機能
"""

from typing import List, Optional, Dict
from PySide6.QtMultimedia import QMediaDevices, QAudioDevice, QAudioOutput
from PySide6.QtCore import QObject, Signal


class AudioDeviceManager(QObject):
    """音声出力デバイスの管理を担当するクラス"""
    
    device_changed = Signal(str)  # デバイスが変更されたときのシグナル
    devices_updated = Signal(list)  # デバイスリストが更新されたときのシグナル
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_device: Optional[QAudioDevice] = None
        self._audio_output: Optional[QAudioOutput] = None
        self._devices_cache: List[QAudioDevice] = []
        
        # QMediaDevicesのインスタンスを作成してシグナルを接続
        self._media_devices = QMediaDevices(parent)
        self._media_devices.audioOutputsChanged.connect(self._on_devices_changed)
        
        # 初期デバイスリストを取得
        self._update_devices_cache()
    
    def _update_devices_cache(self):
        """デバイスリストのキャッシュを更新"""
        self._devices_cache = QMediaDevices.audioOutputs()
        device_info = self.get_devices_info()
        self.devices_updated.emit(device_info)
    
    def _on_devices_changed(self):
        """音声デバイスが変更されたときの処理"""
        print("Audio devices changed")
        self._update_devices_cache()
    
    def get_devices_info(self) -> List[Dict[str, str]]:
        """
        利用可能な音声出力デバイスの情報を取得
        
        Returns:
            デバイス情報のリスト（ID、名前、説明）
        """
        devices_info = []
        for device in self._devices_cache:
            info = {
                'id': device.id().data().decode('utf-8') if device.id() else 'unknown',
                'name': device.description(),
                'is_default': device.isDefault()
            }
            devices_info.append(info)
        return devices_info
    
    def get_current_device(self) -> Optional[Dict[str, str]]:
        """
        現在選択されているデバイス情報を取得
        
        Returns:
            現在のデバイス情報、または None
        """
        if not self._current_device:
            return None
        
        return {
            'id': self._current_device.id().data().decode('utf-8') if self._current_device.id() else 'unknown',
            'name': self._current_device.description(),
            'is_default': self._current_device.isDefault()
        }
    
    def set_audio_output(self, audio_output: QAudioOutput):
        """
        管理するQAudioOutputオブジェクトを設定
        
        Args:
            audio_output: QAudioOutputインスタンス
        """
        self._audio_output = audio_output
        if audio_output:
            self._current_device = audio_output.device()
    
    def switch_device_by_index(self, index: int) -> bool:
        """
        インデックスで指定されたデバイスに切り替え
        
        Args:
            index: デバイスリストのインデックス
            
        Returns:
            切り替えが成功したかどうか
        """
        if not self._audio_output:
            print("No audio output object set")
            return False
        
        if index < 0 or index >= len(self._devices_cache):
            print(f"Invalid device index: {index}")
            return False
        
        device = self._devices_cache[index]
        return self._switch_to_device(device)
    
    def switch_device_by_id(self, device_id: str) -> bool:
        """
        IDで指定されたデバイスに切り替え
        
        Args:
            device_id: デバイスID
            
        Returns:
            切り替えが成功したかどうか
        """
        if not self._audio_output:
            print("No audio output object set")
            return False
        
        for device in self._devices_cache:
            if device.id().data().decode('utf-8') == device_id:
                return self._switch_to_device(device)
        
        print(f"Device not found: {device_id}")
        return False
    
    def switch_to_default_device(self) -> bool:
        """
        デフォルトデバイスに切り替え
        
        Returns:
            切り替えが成功したかどうか
        """
        if not self._audio_output:
            print("No audio output object set")
            return False
        
        default_device = QMediaDevices.defaultAudioOutput()
        if default_device.isNull():
            print("No default audio output device found")
            return False
        
        return self._switch_to_device(default_device)
    
    def _switch_to_device(self, device: QAudioDevice) -> bool:
        """
        指定されたデバイスに切り替え
        
        Args:
            device: 切り替え先のデバイス
            
        Returns:
            切り替えが成功したかどうか
        """
        try:
            if device.isNull():
                print("Invalid audio device")
                return False
            
            self._audio_output.setDevice(device)
            self._current_device = device
            
            device_name = device.description()
            print(f"Switched to audio device: {device_name}")
            self.device_changed.emit(device_name)
            
            return True
            
        except Exception as e:
            print(f"Failed to switch audio device: {e}")
            return False
    
    def refresh_devices(self):
        """デバイスリストを手動で更新"""
        self._update_devices_cache()
        print(f"Found {len(self._devices_cache)} audio output devices")