"""
本地TTS引擎模块
支持多种可本地部署的TTS解决方案: MeloTTS, PaddleSpeech, Coqui TTS, IndexTTS, edge-tts等
"""

import os
import tempfile
import subprocess
import sys
from abc import ABC, abstractmethod

class TTSEngineBase(ABC):
    """TTS引擎抽象基类"""
    
    def __init__(self):
        self.engine = None
    
    @abstractmethod
    def initialize(self):
        """初始化引擎"""
        pass
    
    @abstractmethod
    def speak(self, text):
        """播放文本语音"""
        pass
    
    @abstractmethod
    def save_to_file(self, text, filename):
        """将文本语音保存到文件"""
        pass

class LocalTTSEngine:
    def __init__(self):
        """初始化本地TTS引擎"""
        self.engine = None
        self.engine_type = None
        self.engine_strategies = {}  # 在此处正确初始化engine_strategies属性
        self.available_engines = self._check_available_engines()
    
    def _check_available_engines(self):
        """检查可用的本地TTS引擎"""
        available = []
        
        # 检查MeloTTS
        try:
            import melo
            available.append("melotts")
            from .strategies.melotts_strategy import MeloTTSStrategy
            self.engine_strategies["melotts"] = MeloTTSStrategy
        except ImportError:
            pass
            
        # 检查PaddleSpeech
        try:
            import paddlespeech
            available.append("paddlespeech")
            from .strategies.paddlespeech_strategy import PaddleSpeechStrategy
            self.engine_strategies["paddlespeech"] = PaddleSpeechStrategy
        except ImportError:
            pass
            
        # 检查Coqui TTS
        try:
            import TTS
            available.append("coqui")
            from .strategies.coqui_strategy import CoquiStrategy
            self.engine_strategies["coqui"] = CoquiStrategy
        except ImportError:
            pass
            
        # 检查IndexTTS
        try:
            # 添加IndexTTS路径到sys.path
            import sys
            import os
            indextts_path = os.path.join(os.path.dirname(__file__), '..', '..', 'git', 'index-tts')
            indextts_path = os.path.abspath(indextts_path)
            indextts_sub_path = os.path.join(indextts_path, 'indextts')
            if os.path.exists(indextts_path) and indextts_path not in sys.path:
                sys.path.append(indextts_path)
            if os.path.exists(indextts_sub_path) and indextts_sub_path not in sys.path:
                sys.path.append(indextts_sub_path)
            from indextts.infer_v2 import IndexTTS2
            available.append("indextts")
            from .strategies.indextts_strategy import IndexTTSStrategy
            self.engine_strategies["indextts"] = IndexTTSStrategy
        except (ImportError, ModuleNotFoundError) as e:
            # print(f"⚠️ IndexTTS导入失败: {e}")  # 可选的调试信息
            pass
            
        # 检查edge-tts
        try:
            import edge_tts
            available.append("edge-tts")
            from .strategies.edge_tts_strategy import EdgeTTSStrategy
            self.engine_strategies["edge-tts"] = EdgeTTSStrategy
        except ImportError:
            pass
            
        # 检查pyttsx3 (作为后备选项)
        try:
            import pyttsx3
            available.append("pyttsx3")
            from .strategies.pyttsx3_strategy import Pyttsx3Strategy
            self.engine_strategies["pyttsx3"] = Pyttsx3Strategy
        except ImportError:
            pass
            
        return available
    
    def init_engine(self, engine_type="melotts"):
        """
        初始化指定类型的本地TTS引擎
        
        Args:
            engine_type (str): 引擎类型 ("melotts", "paddlespeech", "coqui", "indextts", "edge-tts", "pyttsx3")
        """
        print(f"🚀 初始化TTS引擎: {engine_type}")
        engine_type = engine_type.lower()
        
        if engine_type not in self.available_engines:
            print(f"⚠️  TTS引擎 {engine_type} 不可用，可用引擎: {', '.join(self.available_engines)}")
            # 尝试使用第一个可用的引擎
            if self.available_engines:
                engine_type = self.available_engines[0]
                print(f"🔄 切换到可用引擎: {engine_type}")
            else:
                print("❌ 没有可用的TTS引擎")
                print("💡 请安装以下任一TTS引擎:")
                print("   - pyttsx3: pip install pyttsx3")
                print("   - MeloTTS: pip install melo")
                print("   - PaddleSpeech: pip install paddlespeech")
                print("   - Coqui TTS: pip install coqui-tts")
                print("   - IndexTTS: 需要从GitHub下载")
                print("   - Edge-TTS: pip install edge-tts")
                return False
        
        # 使用策略模式初始化对应的引擎
        try:
            if engine_type in self.engine_strategies:
                strategy_class = self.engine_strategies[engine_type]
                self.engine = strategy_class()
                self.engine_type = engine_type
                success = self.engine.initialize()
                if success:
                    print(f"✅ {engine_type}引擎初始化成功！")
                else:
                    print(f"❌ {engine_type}引擎初始化失败！")
                return success
            else:
                print(f"❌ 尚未实现 {engine_type} 引擎策略")
                return False
        except Exception as e:
            print(f"❌ TTS引擎 {engine_type} 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
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
            print(f"🔊 播放语音: {text} (引擎类型: {self.engine_type})")
            result = self.engine.speak(text)
            
            # 如果返回的是文件路径，则播放该文件
            if isinstance(result, str) and os.path.exists(result):
                success = self._play_audio_file(result)
                # 清理临时文件
                if os.path.exists(result):
                    os.unlink(result)
                return success
            elif result is True:
                # 策略类已经直接播放了音频或者成功处理
                return True
            elif result is False:
                # 策略类处理失败
                return False
            elif result is None:
                # 策略类没有返回有意义的结果
                return False
            else:
                # 其他情况认为成功
                return True
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
                # Edge-TTS通常生成MP3文件
                if self.engine_type == "edge-tts":
                    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                else:
                    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                filename = temp_file.name
                temp_file.close()
            
            print(f"💾 保存语音到文件: {filename}")
            result = self.engine.save_to_file(text, filename)
            return result
        except Exception as e:
            print(f"❌ 语音保存失败: {e}")
            return None
    
    def _play_audio_file(self, filename):
        """
        播放音频文件
        
        Args:
            filename (str): 音频文件路径
        """
        print(f"🔊 正在播放音频文件: {filename}")
        
        # 检查文件是否存在和大小
        if not os.path.exists(filename):
            print(f"⚠️ 音频文件不存在: {filename}")
            return False
        
        file_size = os.path.getsize(filename)
        print(f"🔧 音频文件大小: {file_size} bytes")
        
        if file_size == 0:
            print("⚠️ 音频文件为空")
            return False
            
        # 确保pygame的显示模式不会干扰
        if 'pygame' in sys.modules:
            try:
                import pygame
                if pygame.mixer.get_init() is None:
                    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            except:
                pass
        
        # 尝试pygame播放（首选方法）
        try:
            print("🔧 尝试使用pygame播放")
            import pygame
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)  # 等待播放完成，每100毫秒检查一次
            
            pygame.mixer.quit()
            print("✅ pygame播放完成")
            return True
        except Exception as e:
            print(f"⚠️ pygame播放失败: {e}")
        
        # 尝试playsound
        try:
            print("🔧 尝试使用playsound播放")
            import playsound
            playsound.playsound(filename)
            print("✅ playsound播放完成")
            return True
        except ImportError:
            print("⚠️ playsound库未安装")
        except Exception as e:
            print(f"⚠️ playsound播放失败: {e}")
        
        # Windows 系统使用系统默认播放器
        if sys.platform.startswith('win'):
            try:
                print("🔧 使用系统默认播放器播放")
                import subprocess
                # 使用powershell播放音频文件
                result = subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{filename}').PlaySync()"], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print("✅ PowerShell播放完成")
                    return True
                else:
                    # 备用方法
                    os.startfile(filename)
                    # 等待一段时间确保播放完成
                    import time
                    time.sleep(max(1, file_size / 10000))  # 根据文件大小估算播放时间
                    print("✅ 系统播放器播放完成")
                    return True
            except Exception as e:
                print(f"⚠️ 系统播放器失败: {e}")
        
        # macOS系统命令播放
        try:
            print("🔧 尝试使用系统命令播放")
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.call(['afplay', filename])
                print("✅ afplay播放完成")
                return True
            elif sys.platform.startswith('linux'):
                subprocess.call(['aplay', filename])
                print("✅ aplay播放完成")
                return True
            else:
                print("⚠️ 不支持的操作系统")
                return False
        except Exception as e:
            print(f"⚠️ 系统命令播放失败: {e}")
            print("⚠️ 所有音频播放方法均已尝试失败，请检查系统音频设置")
            return False
    
    def list_available_engines(self):
        """列出所有可用的TTS引擎"""
        return self.available_engines

def select_local_tts_engine():
    """
    选择本地TTS引擎
    
    Returns:
        LocalTTSEngine: 配置好的本地TTS引擎实例
    """
    tts = LocalTTSEngine()
    available_engines = tts.list_available_engines()
    
    if not available_engines:
        print("❌ 没有找到可用的本地TTS引擎")
        print("💡 请安装以下任一TTS引擎:")
        print("   - MeloTTS: pip install melo")
        print("   - PaddleSpeech: pip install paddlespeech")
        print("   - Coqui TTS: pip install coqui-tts")
        print("   - IndexTTS: 需要从GitHub下载")
        print("   - Edge-TTS: pip install edge-tts")
        print("   - pyttsx3: pip install pyttsx3")
        return None
    
    print("\n请选择本地TTS引擎:")
    for i, engine in enumerate(available_engines, 1):
        engine_name = {
            "melotts": "MeloTTS (推荐，支持中英混合)",
            "paddlespeech": "PaddleSpeech (百度开源，中文优化)",
            "coqui": "Coqui TTS (多语言支持)",
            "indextts": "IndexTTS (B站开源，高质量语音)",
            "edge-tts": "Edge-TTS (微软语音，需要网络连接)",
            "pyttsx3": "pyttsx3 (系统语音，轻量级，无需网络)"
        }.get(engine, engine)
        print(f"{i}. {engine_name}")
    
    try:
        choice = int(input(f"请输入选项 (1-{len(available_engines)}): ").strip())
        if 1 <= choice <= len(available_engines):
            selected_engine = available_engines[choice - 1]
            if tts.init_engine(selected_engine):
                return tts
            else:
                return None
        else:
            print("❌ 无效选项")
            return None
    except ValueError:
        print("❌ 请输入有效的数字选项")
        return None

def test_all_local_tts_engines():
    """Test all available local TTS engines"""
    engines = []
    
    # Check available engines
    try:
        import pyttsx3
        engines.append("pyttsx3")
    except ImportError:
        pass
        
    try:
        import edge_tts
        engines.append("edge-tts")
    except ImportError:
        pass
        
    try:
        from melo.api import TTS
        engines.append("melotts")
    except ImportError:
        pass
        
    try:
        from TTS.api import TTS
        engines.append("coqui")
    except ImportError:
        pass
    
    # Check for IndexTTS
    try:
        import sys
        import os
        index_tts_path = os.path.join(os.path.dirname(__file__), 'index-tts')
        if os.path.exists(index_tts_path):
            sys.path.append(index_tts_path)
            from indextts.infer_v2 import IndexTTS2
            engines.append("indextts")
    except ImportError:
        pass
        
    print(f"🔍 发现 {len(engines)} 个可用的本地TTS引擎: {', '.join(engines)}")
    print()
    
    # Test each engine
    for engine_name in engines:
        print("="*50)
        # 为每个引擎提供更详细的描述
        engine_descriptions = {
            "melotts": "MeloTTS (推荐，支持中英混合)",
            "paddlespeech": "PaddleSpeech (百度开源，中文优化)",
            "coqui": "Coqui TTS (多语言支持)",
            "indextts": "IndexTTS (B站开源，高质量语音)",
            "edge-tts": "Edge-TTS (微软语音，需要网络连接)",
            "pyttsx3": "pyttsx3 (系统语音，轻量级，无需网络)"
        }
        description = engine_descriptions.get(engine_name, engine_name)
        print(f"正在测试 {description} 引擎...")
        print("="*50)
        
        try:
            tts = LocalTTSEngine()
            if tts.init_engine(engine_name):
                print(f"✅ {engine_name}引擎初始化成功！")
                test_text = f"这是 {engine_name} 引擎的测试语音输出"
                print(f"🔊 播放语音: {test_text}")
                tts.speak(test_text)
                print(f"✅ {engine_name} 引擎测试成功\n")
            else:
                print(f"❌ {engine_name} 引擎初始化失败\n")
        except Exception as e:
            print(f"❌ 测试 {engine_name} 引擎时出现错误: {e}\n")

def test_local_tts():
    """测试本地TTS功能"""
    print("请选择测试模式:")
    print("1. 选择单个TTS引擎进行测试")
    print("2. 测试所有可用的本地TTS引擎")
    
    choice = input("请输入选项 (1 或 2): ").strip()
    
    if choice == "1":
        tts = select_local_tts_engine()
        if tts:
            # 测试播放
            tts.speak("你好，这是一个本地TTS测试。")
            
            # 测试保存到文件
            filename = tts.save_to_file("这是保存到文件的测试语音。")
            if filename:
                print(f"✅ 语音已保存到: {filename}")
    elif choice == "2":
        test_all_local_tts_engines()
    else:
        print("❌ 无效选项")

def test_tts_speak():
    """测试TTS播报功能"""
    print("📢 TTS播报功能测试")
    tts = LocalTTSEngine()
    
    # 尝试初始化pyttsx3引擎
    if tts.init_engine("pyttsx3"):
        print("✅ pyttsx3引擎初始化成功")
        
        # 测试播报几段文字
        test_texts = [
            "你好，这是一个TTS播报测试。",
            "欢迎使用语音合成系统。",
            "这是第三条测试语音消息。"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n🧪 正在测试第{i}条语音: {text}")
            success = tts.speak(text)
            if success:
                print(f"✅ 第{i}条语音播报成功")
            else:
                print(f"❌ 第{i}条语音播报失败")
            
            # 添加一点间隔时间
            import time
            time.sleep(1)
        
        print("\n🎉 TTS播报测试完成！")
    else:
        print("❌ pyttsx3引擎初始化失败")

if __name__ == "__main__":
    # 检查命令行参数
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test-speak":
        test_tts_speak()
    else:
        test_local_tts()