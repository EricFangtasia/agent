#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Edge-TTS引擎策略实现
"""

import os
import tempfile
import asyncio
from ..local_tts import TTSEngineBase


class EdgeTTSStrategy(TTSEngineBase):
    """Edge-TTS引擎策略实现"""
    
    def __init__(self, voice=None, rate="+0%", volume="+0%", pitch="+0Hz"):
        """
        初始化Edge-TTS引擎配置
        
        Args:
            voice (str): 指定的语音名称，如 'zh-CN-XiaoxiaoNeural'
            rate (str): 语速调整，如 '-5%', '+10%'
            volume (str): 音量调整，如 '-5%', '+10%'
            pitch (str): 音调调整，如 '-5Hz', '+10Hz'
        """
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
    
    def initialize(self):
        """初始化Edge-TTS引擎"""
        try:
            import edge_tts
            # edge-tts是微软提供的在线TTS服务，需要网络连接
            self.engine = edge_tts
            print("✅ Edge-TTS引擎初始化成功！(需要网络连接)")
            return True
        except ImportError:
            print("❌ Edge-TTS API导入失败")
            return False
        except Exception as e:
            print(f"❌ Edge-TTS引擎初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _edge_tts_synthesize(self, text, filename):
        """
        Edge-TTS语音合成异步函数
        
        Args:
            text (str): 要合成的文本
            filename (str): 输出文件名
        """
        # 如果没有指定voice，自动选择一个合适的语音
        if self.voice is None:
            # 获取可用的语音
            voices = await self.engine.list_voices()
            
            # 如果是中文文本，优先选择中文语音
            if self._is_chinese_text(text):
                chinese_voices = [v for v in voices if v["Locale"].startswith("zh")]
                self.voice = chinese_voices[0]["ShortName"] if chinese_voices else "zh-CN-XiaoxiaoNeural"
            else:
                # 默认使用英文语音
                english_voices = [v for v in voices if v["Locale"].startswith("en")]
                self.voice = english_voices[0]["ShortName"] if english_voices else "en-US-AriaNeural"
        
        # 使用SSML格式来设置语音属性
        ssml_text = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="{self.voice}">
                <prosody rate="{self.rate}" volume="{self.volume}" pitch="{self.pitch}">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        
        # 合成语音
        communicate = self.engine.Communicate(ssml_text, self.voice)
        await communicate.save(filename)
    
    def _is_chinese_text(self, text):
        """检测文本是否包含中文字符"""
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False
    
    def speak(self, text):
        """使用Edge-TTS播放文本"""
        try:
            # Edge-TTS处理 (异步操作)
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                filename = tmp_file.name
            
            # 运行异步函数
            asyncio.run(self._edge_tts_synthesize(text, filename))
            # 返回文件路径，由主类处理播放
            return filename
        except Exception as e:
            print(f"❌ Edge-TTS语音合成失败: {e}")
            return False
    
    def save_to_file(self, text, filename):
        """使用Edge-TTS将文本保存到音频文件"""
        try:
            asyncio.run(self._edge_tts_synthesize(text, filename))
            return filename
        except Exception as e:
            print(f"❌ Edge-TTS保存文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None