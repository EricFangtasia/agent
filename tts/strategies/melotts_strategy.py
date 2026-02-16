#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MeloTTS TTS引擎策略实现
"""

import os
import tempfile
from ..local_tts import TTSEngineBase


class MeloTTSStrategy(TTSEngineBase):
    """MeloTTS TTS引擎策略实现"""
    
    def initialize(self):
        """初始化MeloTTS引擎"""
        try:
            from melo.api import TTS
            # 初始化中文TTS引擎
            self.engine = TTS(language='ZH', device='cpu')
            print("✅ MeloTTS引擎初始化成功！")
            return True
        except ImportError:
            print("❌ MeloTTS API导入失败")
            return False
        except Exception as e:
            print(f"❌ MeloTTS引擎初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def speak(self, text):
        """使用MeloTTS播放文本"""
        try:
            # MeloTTS处理
            speaker_ids = list(self.engine.hps.data.spk2id.values())
            speaker_id = speaker_ids[0] if speaker_ids else 0
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                filename = tmp_file.name
            self.engine.tts_to_file(text, speaker_id, filename)
            
            # 返回文件路径，由主类处理播放
            return filename
        except Exception as e:
            print(f"❌ MeloTTS语音合成失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_to_file(self, text, filename):
        """使用MeloTTS将文本保存到音频文件"""
        try:
            speaker_ids = list(self.engine.hps.data.spk2id.values())
            speaker_id = speaker_ids[0] if speaker_ids else 0
            self.engine.tts_to_file(text, speaker_id, filename)
            return filename
        except Exception as e:
            print(f"❌ MeloTTS保存文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None