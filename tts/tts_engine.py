"""
多平台TTS引擎模块
支持多种TTS服务: pyttsx3, 百度, 阿里云等
"""

import os
import tempfile

class TTSEngine:
    def __init__(self):
        """初始化TTS引擎"""
        self.engine = None
        self.engine_type = None
    
    def init_engine(self, engine_type="pyttsx3"):
        """
        初始化指定类型的TTS引擎
        
        Args:
            engine_type (str): 引擎类型 ("pyttsx3", "baidu", "ali")
        """
        self.engine_type = engine_type.lower()
        
        try:
            if self.engine_type == "pyttsx3":
                import pyttsx3
                self.engine = pyttsx3.init()
                self.setup_pyttsx3_voice()
                print("✅ pyttsx3 TTS引擎初始化成功！")
                return True
                
            elif self.engine_type == "baidu":
                # 百度TTS需要安装baidu-aip包
                try:
                    from aip import AipSpeech
                    # 需要设置百度API密钥
                    bd_app_id = os.environ.get("BAIDU_TTS_APP_ID", "")
                    bd_api_key = os.environ.get("BAIDU_TTS_API_KEY", "")
                    bd_secret_key = os.environ.get("BAIDU_TTS_SECRET_KEY", "")
                    
                    if not (bd_app_id and bd_api_key and bd_secret_key):
                        print("⚠️  百度TTS需要配置API密钥，请设置环境变量: BAIDU_TTS_APP_ID, BAIDU_TTS_API_KEY, BAIDU_TTS_SECRET_KEY")
                        return False
                        
                    self.engine = AipSpeech(bd_app_id, bd_api_key, bd_secret_key)
                    print("✅ 百度TTS引擎初始化成功！")
                    return True
                except ImportError:
                    print("❌ 请先安装百度TTS库: pip install baidu-aip")
                    return False
                    
            elif self.engine_type == "ali":
                # 阿里云TTS需要安装aliyun-python-sdk-core和alibabacloud-dyvmsapi20170525
                try:
                    from aliyunsdkcore.client import AcsClient
                    print("✅ 阿里云TTS引擎初始化成功！")
                    # 阿里云TTS配置较为复杂，此处仅作示意
                    print("⚠️ 阿里云TTS需要额外配置，详见官方文档")
                    return True
                except ImportError:
                    print("❌ 请先安装阿里云TTS库: pip install aliyun-python-sdk-core alibabacloud-dyvmsapi20170525")
                    return False
                    
            else:
                print(f"❌ 不支持的TTS引擎类型: {engine_type}")
                return False
                
        except Exception as e:
            print(f"❌ TTS引擎初始化失败: {e}")
            self.engine = None
            return False
    
    def setup_pyttsx3_voice(self):
        """配置pyttsx3语音参数"""
        if self.engine and self.engine_type == "pyttsx3":
            # 设置语速（默认值为200）
            self.engine.setProperty('rate', 200)
            
            # 设置音量（0-1之间，默认为1）
            self.engine.setProperty('volume', 0.9)
            
            # 获取可用的语音列表并设置默认语音
            voices = self.engine.getProperty('voices')
            if voices:
                # 尝试选择中文语音
                for voice in voices:
                    if any(lang in voice.id.lower() for lang in ['zh', 'chinese', 'mandarin']):
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # 如果没有找到中文语音，使用第一个语音
                    self.engine.setProperty('voice', voices[0].id)
    
    def speak(self, text):
        """
        播放文本语音
        
        Args:
            text (str): 要转换为语音的文本
        """
        if not self.engine:
            print("❌ TTS引擎未初始化")
            return False
            
        try:
            print(f"🔊 播放语音: {text}")
            
            if self.engine_type == "pyttsx3":
                self.engine.say(text)
                self.engine.runAndWait()
                return True
                
            elif self.engine_type == "baidu":
                # 百度TTS需要先合成再播放
                result = self.engine.synthesis(text, 'zh', 1, {
                    'vol': 9, 'per': 0, 'spd': 4, 'pit': 5
                })
                
                # 识别结果
                if not isinstance(result, dict):
                    # 保存到临时文件并播放
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                        tmp_file.write(result)
                        filename = tmp_file.name
                    
                    # 播放音频文件（需要pygame或其他音频播放库）
                    self._play_audio_file(filename)
                    # 删除临时文件
                    os.unlink(filename)
                    return True
                else:
                    print("❌ 百度TTS合成失败")
                    return False
                    
            else:
                print(f"❌ 尚未实现 {self.engine_type} 的播放功能")
                return False
                
        except Exception as e:
            print(f"❌ 语音播放失败: {e}")
            return False
    
    def save_to_file(self, text, filename=None):
        """
        将文本语音保存到文件
        
        Args:
            text (str): 要转换为语音的文本
            filename (str): 保存的文件名，如果不提供则使用临时文件
            
        Returns:
            str: 保存的文件路径，如果失败则返回None
        """
        if not self.engine:
            print("❌ TTS引擎未初始化")
            return None
            
        try:
            # 如果没有提供文件名，创建临时文件
            if not filename:
                if self.engine_type == "baidu":
                    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                else:
                    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                filename = temp_file.name
                temp_file.close()
            
            print(f"💾 保存语音到文件: {filename}")
            
            if self.engine_type == "pyttsx3":
                self.engine.save_to_file(text, filename)
                self.engine.runAndWait()
                return filename
                
            elif self.engine_type == "baidu":
                result = self.engine.synthesis(text, 'zh', 1, {
                    'vol': 9, 'per': 0, 'spd': 4, 'pit': 5
                })
                
                # 识别结果
                if not isinstance(result, dict):
                    with open(filename, 'wb') as f:
                        f.write(result)
                    return filename
                else:
                    print("❌ 百度TTS合成失败")
                    return None
                    
            else:
                print(f"❌ 尚未实现 {self.engine_type} 的保存功能")
                return None
                
        except Exception as e:
            print(f"❌ 语音保存失败: {e}")
            return None
    
    def _play_audio_file(self, filename):
        """
        播放音频文件
        
        Args:
            filename (str): 音频文件路径
        """
        try:
            # 使用pygame播放音频（首选）
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            return True
        except Exception as e:
            print(f"⚠️  pygame音频播放失败: {e}")
            
            # 尝试使用playsound作为备选方案
            try:
                from playsound import playsound
                playsound(filename)
                return True
            except ImportError:
                print("❌ 请先安装音频播放库: pip install pygame 或 pip install playsound")
                return False
            except Exception as e:
                print(f"❌ playsound播放失败: {e}")
                return False
    
    def set_rate(self, rate):
        """
        设置语速
        
        Args:
            rate (int): 语速，范围取决于具体引擎
        """
        if not self.engine:
            return
            
        if self.engine_type == "pyttsx3":
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """
        设置音量
        
        Args:
            volume (float): 音量，范围取决于具体引擎
        """
        if not self.engine:
            return
            
        if self.engine_type == "pyttsx3":
            self.engine.setProperty('volume', volume)

def select_tts_engine():
    """
    选择TTS引擎
    
    Returns:
        TTSEngine: 配置好的TTS引擎实例
    """
    print("\n请选择TTS引擎:")
    print("1. pyttsx3 (离线, 免费, 跨平台)")
    print("2. 百度TTS (在线, 需API密钥)")
    print("3. 阿里云TTS (在线, 需API密钥)")
    
    choice = input("请输入选项 (1, 2, 或 3): ").strip()
    
    tts = TTSEngine()
    
    if choice == "1":
        if tts.init_engine("pyttsx3"):
            return tts
    elif choice == "2":
        if tts.init_engine("baidu"):
            return tts
    elif choice == "3":
        if tts.init_engine("ali"):
            return tts
    else:
        print("❌ 无效选项，使用默认的pyttsx3引擎")
        if tts.init_engine("pyttsx3"):
            return tts
    
    return None

def test_tts():
    """测试TTS功能"""
    tts = select_tts_engine()
    
    if tts:
        # 测试播放
        tts.speak("你好，这是一个多平台TTS测试。")
        
        # 测试保存到文件
        filename = tts.save_to_file("这是保存到文件的测试语音。")
        if filename:
            print(f"✅ 语音已保存到: {filename}")

if __name__ == "__main__":
    test_tts()