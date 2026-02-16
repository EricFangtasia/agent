#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pyttsx3 TTS引擎策略实现
"""

import os
import tempfile
import sys
import threading
import time
from ..local_tts import TTSEngineBase


class Pyttsx3Strategy(TTSEngineBase):
    """pyttsx3 TTS引擎策略实现"""
    
    def __init__(self):
        super().__init__()
        self.rate = 200
        self.volume = 0.9
        self.voice = None
    
    def initialize(self):
        """初始化pyttsx3引擎"""
        try:
            import pyttsx3
            print("🔧 正在初始化pyttsx3引擎...")
            print("🔧 pyttsx3模块导入成功")
            self.engine = pyttsx3.init()
            print("🔧 pyttsx3引擎实例化成功")
            
            # 配置语音参数
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            print("🔧 pyttsx3参数设置完成")
            
            # 设置中文语音（如果可用）
            voices = self.engine.getProperty('voices')
            print(f"🔧 发现 {len(voices)} 个语音")
            for voice in voices:
                if 'zh' in voice.id.lower() or 'chinese' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    print(f"🔧 设置中文语音: {voice.name}")
                    break
            
            return True
        except Exception as e:
            print(f"❌ pyttsx3引擎初始化失败: {e}")
            print("💡 解决方案:")
            print("   1. 确保已安装: pip install pyttsx3")
            print("   2. Windows系统还需要: pip install pypiwin32")
            import traceback
            traceback.print_exc()
            return False
    
    def _ensure_engine_ready(self):
        """确保pyttsx3引擎处于可用状态，如果不可用则重新初始化"""
        # 检查引擎是否有效
        engine_valid = False
        if self.engine:
            try:
                # 尝试执行一个简单操作来检查引擎是否正常工作
                self.engine.getProperty('rate')
                engine_valid = True
                print("🔧 使用现有pyttsx3引擎实例")
            except:
                print("⚠️ 现有pyttsx3引擎实例无效")
                engine_valid = False
        
        # 如果引擎无效，则重新初始化
        if not engine_valid:
            print("🔧 重新初始化pyttsx3引擎")
            # 保存当前配置
            current_rate = self.rate
            current_volume = self.volume
            current_voice = self.voice
            
            if self.engine:
                try:
                    current_rate = self.engine.getProperty('rate')
                    current_volume = self.engine.getProperty('volume')
                    current_voice = self.engine.getProperty('voice')
                except:
                    pass
            
            # 重新初始化引擎
            import pyttsx3
            self.engine = pyttsx3.init()
            
            # 恢复配置
            try:
                self.engine.setProperty('rate', current_rate)
                self.engine.setProperty('volume', current_volume)
                if current_voice:
                    self.engine.setProperty('voice', current_voice)
            except:
                pass
            
            print("✅ pyttsx3引擎初始化完成")
    
    def _force_engine_reset(self):
        """强制重置pyttsx3引擎，解决runAndWait卡住的问题"""
        try:
            if self.engine:
                # 尝试正常停止
                try:
                    self.engine.stop()
                except:
                    pass
                
                # 强制销毁引擎实例
                try:
                    del self.engine
                except:
                    pass
                    
            # 重新创建引擎
            import pyttsx3
            self.engine = pyttsx3.init()
            
            # 恢复配置
            try:
                self.engine.setProperty('rate', self.rate)
                self.engine.setProperty('volume', self.volume)
                if self.voice:
                    self.engine.setProperty('voice', self.voice)
            except:
                pass
                
            print("🔧 pyttsx3引擎强制重置完成")
        except Exception as e:
            print(f"⚠️ pyttsx3引擎强制重置失败: {e}")
    
    def _safe_run_wait(self):
        """安全执行runAndWait并确保资源清理"""
        try:
            if self.engine:
                self.engine.runAndWait()
                return True
        except Exception as e:
            print(f"⚠️ runAndWait执行出错: {e}")
            # 如果runAndWait卡住了，强制重置引擎
            self._force_engine_reset()
            return False
        finally:
            # 确保每次使用后清理引擎资源，防止状态残留导致下次调用卡住
            try:
                self.engine.stop()
            except:
                pass
    
    def _direct_speak(self, text):
        """直接播放文本，不生成文件"""
        try:
            self._ensure_engine_ready()
            self.engine.say(text)
            return self._safe_run_wait()
        except Exception as e:
            print(f"⚠️ 直接播放失败: {e}")
            return False
    
    def speak(self, text):
        """使用pyttsx3生成文本语音文件（不播放）"""
        try:
            # 确保引擎可用
            self._ensure_engine_ready()
            
            # 生成临时音频文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                filename = tmp_file.name
            
            print(f"🔧 开始保存到文件: {filename}")
            
            # 直接调用save_to_file和安全的runAndWait
            try:
                self.engine.save_to_file(text, filename)
                print(f"🔧 engine.save_to_file success")
                
                if self._safe_run_wait():
                    print(f"🔧 音频文件已生成: {filename}")
                else:
                    print("⚠️ runAndWait执行失败")
                    # 清理临时文件
                    # if os.path.exists(filename):
                    #     os.unlink(filename)
                    return False
            except Exception as save_error:
                print(f"⚠️ save_to_file过程中出现异常: {save_error}")
                # 清理临时文件
                # if os.path.exists(filename):
                #     os.unlink(filename)
                return False
            
            # 检查文件是否成功生成并且不为空
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"🔧 音频文件大小: {file_size} bytes")
                if file_size > 0:
                    # 返回文件路径
                    print(f"✅ 音频已生成: {filename}")
                    return filename
                else:
                    print("⚠️ 音频文件为空")
                    # 清理空文件
                    if os.path.exists(filename):
                        os.unlink(filename)
                    return False
            else:
                print("❌ 音频文件未生成")
                return False
            
        except Exception as e:
            print(f"⚠️ pyttsx3处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_to_file(self, text, filename):
        """使用pyttsx3将文本保存到音频文件"""
        try:
            # 确保引擎可用
            self._ensure_engine_ready()
            
            # 使用有效的引擎实例进行语音合成
            if self.engine is not None:
                # 执行语音合成
                try:
                    self.engine.save_to_file(text, filename)
                    if not self._safe_run_wait():
                        return None
                except Exception as save_error:
                    print(f"⚠️ save_to_file过程中出现异常: {save_error}")
                    return None
                
                # 验证输出文件
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    print(f"✅ 音频文件已生成: {filename}, 大小: {file_size} bytes")
                    if file_size == 0:
                        print("❌ 生成的音频文件为空")
                        # 尝试使用say+runAndWait直接播放作为备选
                        try:
                            self.engine.say(text)
                            if self._safe_run_wait():
                                print("✅ 直接播放完成")
                                # 删除空文件
                                if os.path.exists(filename):
                                    os.unlink(filename)
                                return filename
                        except Exception as direct_error:
                            print(f"⚠️ 直接播放也失败: {direct_error}")
                            if os.path.exists(filename):
                                os.unlink(filename)
                            return None
                else:
                    print("❌ 音频文件未生成")
                    return None
            else:
                print("❌ TTS引擎未正确初始化")
                return None
                
        except Exception as e:
            print(f"❌ pyttsx3保存文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None
            
        return filename