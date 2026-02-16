#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Coqui TTS引擎策略实现
"""

import os
import tempfile
from ..local_tts import TTSEngineBase


class CoquiStrategy(TTSEngineBase):
    """Coqui TTS引擎策略实现"""
    
    def initialize(self):
        """初始化Coqui TTS引擎"""
        try:
            from TTS.api import TTS
            # 尝试加载中文模型
            try:
                self.engine = TTS(model_name="tts_models/zh-CN/baker/tacotron2-DDC-GST")
            except:
                # 如果中文模型不可用，使用默认的英文模型
                self.engine = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            print("✅ Coqui TTS引擎初始化成功！")
            return True
        except ImportError:
            print("❌ Coqui TTS API导入失败")
            return False
        except Exception as e:
            print(f"❌ Coqui TTS引擎初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def speak(self, text):
        """使用Coqui TTS播放文本"""
        try:
            # 创建临时文件并确保其被正确关闭后再返回路径
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_filename = tmp_file.name
            self.engine.tts_to_file(text=text, file_path=temp_filename)
            # 返回文件路径，由主类处理播放
            return temp_filename
        except Exception as e:
            print(f"❌ Coqui TTS语音合成失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_to_file(self, text, filename):
        """使用Coqui TTS将文本保存到音频文件"""
        try:
            self.engine.tts_to_file(text=text, file_path=filename)
            return filename
        except Exception as e:
            print(f"❌ Coqui TTS保存文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None