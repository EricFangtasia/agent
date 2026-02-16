#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PaddleSpeech TTS引擎策略实现
"""

import os
import tempfile
from ..local_tts import TTSEngineBase


class PaddleSpeechStrategy(TTSEngineBase):
    """PaddleSpeech TTS引擎策略实现"""
    
    def initialize(self):
        """初始化PaddleSpeech引擎"""
        try:
            from paddlespeech.cli.tts.infer import TTSExecutor
            self.engine = TTSExecutor()
            print("✅ PaddleSpeech引擎初始化成功！")
            return True
        except ImportError:
            print("❌ PaddleSpeech API导入失败")
            return False
        except Exception as e:
            print(f"❌ PaddleSpeech引擎初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def speak(self, text):
        """使用PaddleSpeech播放文本"""
        try:
            # PaddleSpeech处理
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_path = tmp_file.name
            wav_file = self.engine(
                text=text,
                output=temp_path,
                am='fastspeech2_csmsc',
                voc='hifigan_csmsc',
                lang='zh'
            )
            # 确保返回的是实际生成的文件路径
            return wav_file or temp_path
        except Exception as e:
            print(f"❌ PaddleSpeech语音合成失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_to_file(self, text, filename):
        """使用PaddleSpeech将文本保存到音频文件"""
        try:
            self.engine(
                text=text,
                output=filename,
                am='fastspeech2_csmsc',
                voc='hifigan_csmsc',
                lang='zh'
            )
            # 直接返回请求的文件名，因为引擎会将其写入该路径
            return filename
        except Exception as e:
            print(f"❌ PaddleSpeech保存文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None