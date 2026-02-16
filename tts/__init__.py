"""
TTS模块初始化文件
"""

from .tts_engine import TTSEngine, select_tts_engine
from .local_tts import LocalTTSEngine, select_local_tts_engine

__all__ = ['TTSEngine', 'select_tts_engine', 'LocalTTSEngine', 'select_local_tts_engine']