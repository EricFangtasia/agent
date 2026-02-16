# sensevoice_demo.py
import os
import warnings
import pyaudio
import wave
import tempfile
import threading
import time
import sys
import numpy as np
warnings.filterwarnings('ignore')

# 添加项目根目录和agent目录到sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
agent_dir = os.path.join(project_root, 'agent')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)

class SenseVoiceASR:
    def __init__(self, model_path=None):
        """初始化SenseVoice语音识别"""
        if model_path is None:
            # 使用默认路径
            # model_path = r"C:\Users\86138\.cache\modelscope\hub\models\iic\SenseVoiceSmall"
            model_path = r"C:\project\py\agent\asr\SenseVoice\models\SenseVoiceSmall"
        self.model_path = model_path
        self.pipeline = None
        self.is_recording = False
        # 初始化大模型API
        self.llm_api = None
        self.selected_llm = None
        # 初始化TTS引擎
        self.tts_engine = None
        
    def init_llm_api(self, llm_type="deepseek"):
        """初始化大模型API"""
        try:
            # 尝试导入agent/llm模块
            llm_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'llm')
            
            # 检查agent/llm目录是否存在
            if os.path.exists(llm_dir) and os.path.isdir(llm_dir):
                print(f"✅ 找到LLM目录: {llm_dir}")
                
                # 设置默认LLM类型
                os.environ["DEFAULT_LLM"] = llm_type
                
                # 优先查找路由器模块
                router_file = os.path.join(llm_dir, 'llm_router.py')
                if os.path.exists(router_file):
                    print("✅ 找到LLM路由器模块")
                    # 添加到Python路径
                    sys.path.insert(0, llm_dir)
                    # 动态导入路由器模块
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("llm_router", router_file)
                    llm_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(llm_module)
                    print("✅ 成功导入LLM路由器模块")
                    self.llm_api = llm_module
                    self.selected_llm = llm_type
                    return True
                
                # 查找其他LLM模块文件
                llm_files = [f for f in os.listdir(llm_dir) if f.endswith('.py') and not f.startswith('__')]
                if llm_files:
                    # 根据选择的LLM类型确定要加载的文件
                    target_file = None
                    for f in llm_files:
                        if llm_type.lower() in f.lower():
                            target_file = f
                            break
                    
                    # 如果没有找到匹配的文件，使用第一个文件
                    if not target_file:
                        target_file = llm_files[0]
                    
                    llm_module_name = os.path.splitext(target_file)[0]
                    print(f"✅ 找到LLM模块: {target_file}")
                    
                    # 添加到Python路径
                    sys.path.insert(0, llm_dir)
                    
                    # 动态导入LLM模块
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        llm_module_name, 
                        os.path.join(llm_dir, target_file)
                    )
                    llm_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(llm_module)
                    print("✅ 成功导入LLM模块")
                    self.llm_api = llm_module
                    self.selected_llm = llm_type
                    return True
                else:
                    print("⚠️ LLM目录中未找到Python模块文件")
                    return False
            else:
                print("⚠️ 未找到LLM目录，将使用默认回复逻辑")
                return False
        except Exception as e:
            print(f"⚠️ LLM模块导入失败: {e}")
            print("将使用默认回复逻辑")

    def init_tts_engine(self, tts_type="pyttsx3", local=False):
        """
        初始化TTS引擎
        
        Args:
            tts_type (str): TTS引擎类型
            local (bool): 是否使用本地TTS引擎
        """
        try:
            if local:
                # 使用本地TTS引擎
                from tts.local_tts import LocalTTSEngine
                self.tts_engine = LocalTTSEngine()
                success = self.tts_engine.init_engine(tts_type)
                if not success:
                    print("❌ 本地TTS引擎初始化失败，将继续使用文本回复")
                    print("\n💡 建议解决方案:")
                    print("   1. 安装基础TTS引擎: pip install pyttsx3")
                    print("   2. Windows系统还需要: pip install pypiwin32")
                    print("   3. 查看支持的引擎列表并选择可用的引擎")
                    # 显示可用引擎
                    available = self.tts_engine.list_available_engines()
                    if available:
                        print(f"   可用引擎: {', '.join(available)}")
                        print("   请重新运行程序并选择可用的引擎")
                    else:
                        print("   当前没有任何可用的TTS引擎")
                return success
            else:
                # 使用在线TTS引擎
                from tts.tts_engine import TTSEngine
                self.tts_engine = TTSEngine()
                return self.tts_engine.init_engine(tts_type)
        except Exception as e:
            print(f"⚠️ TTS引擎初始化失败: {e}")
            print("💡 请确保已安装所需的TTS引擎库")
            return False
    
    def load_model(self):
        """加载模型"""
        print("🔧 加载SenseVoice模型...")
        
        try:
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            
            self.pipeline = pipeline(
                task=Tasks.auto_speech_recognition,
                model=self.model_path,
                model_revision='v1.0.0'
            )
            print("✅ 模型加载成功！")
            return True
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            return False
    
    def transcribe_file(self, audio_path):
        """转录音频文件"""
        if self.pipeline is None:
            if not self.load_model():
                return None
        
        try:
            print(f"🎤 识别音频: {audio_path}")
            result = self.pipeline(audio_path)
            # 处理不同的返回格式
            if isinstance(result, list):
                # 如果返回是列表，取第一个元素
                if len(result) > 0:
                    item = result[0]
                    if isinstance(item, dict):
                        return item.get('text', '')
                    else:
                        return str(item)
                else:
                    return ''
            elif isinstance(result, dict):
                # 如果返回是字典，直接获取text
                return result.get('text', '')
            else:
                # 其他情况转换为字符串
                return str(result)
        except Exception as e:
            print(f"❌ 识别失败: {e}")
            return None
    
    def transcribe_bytes(self, audio_bytes, sample_rate=16000):
        """转录音频字节数据"""
        if self.pipeline is None:
            if not self.load_model():
                return None
        
        try:
            result = self.pipeline({'input': audio_bytes, 'sample_rate': sample_rate})
            # 处理不同的返回格式
            if isinstance(result, list):
                # 如果返回是列表，取第一个元素
                if len(result) > 0:
                    item = result[0]
                    if isinstance(item, dict):
                        return item.get('text', '')
                    else:
                        return str(item)
                else:
                    return ''
            elif isinstance(result, dict):
                # 如果返回是字典，直接获取text
                return result.get('text', '')
            else:
                # 其他情况转换为字符串
                return str(result)
        except Exception as e:
            print(f"❌ 识别失败: {e}")
            return None
    
    def record_audio(self, duration=5):
        """录制音频"""
        # 音频参数
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        
        audio = pyaudio.PyAudio()
        
        # 打开音频流
        stream = audio.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           input=True,
                           frames_per_buffer=CHUNK)
        
        print(f"🎙️ 开始录音 {duration} 秒...")
        
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("⏹️ 录音结束")
        
        # 停止并关闭流
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            wf = wave.open(tmp_file.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            return tmp_file.name
    
    def record_audio_vad(self, silence_threshold=500, silence_duration=2):
        """使用VAD录制音频，检测到语音活动并在停顿指定时间后结束录制"""
        # 音频参数
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        SILENCE_CHUNKS = int(silence_duration * RATE / CHUNK)  # 静音块数阈值
        
        audio = pyaudio.PyAudio()
        
        # 打开音频流
        stream = audio.open(format=FORMAT,
                           channels=CHANNELS,
                           rate=RATE,
                           input=True,
                           frames_per_buffer=CHUNK)
        
        print("🎙️ 开始录音 (VAD模式)...")
        print("🗣️ 请说话...")
        
        frames = []
        silent_chunks = 0
        audio_started = False
        
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            
            # 计算音频能量（均方根）
            audio_data = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_data**2))
            
            # 检测是否是静音
            is_silent = rms < silence_threshold
            
            if not audio_started:
                # 还未检测到语音
                if not is_silent:
                    audio_started = True
                    print("🔊 检测到语音活动...")
                    silent_chunks = 0
                else:
                    # 还没开始说话，保留一些前置静音
                    if len(frames) > 20:  # 保留约0.25秒的前置静音
                        frames.pop(0)
            else:
                # 已经开始录音
                if is_silent:
                    silent_chunks += 1
                    # 如果静音时间达到阈值，则结束录音
                    if silent_chunks > SILENCE_CHUNKS:
                        print("⏹️ 检测到停顿，录音结束")
                        break
                else:
                    silent_chunks = 0
        
        # 停止并关闭流
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            wf = wave.open(tmp_file.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            return tmp_file.name
    
    def live_transcribe(self):
        """实时语音识别"""
        print("🎙️ 开始实时语音识别 (按 Ctrl+C 停止)")
        try:
            while True:
                # 录制3秒音频
                audio_file = self.record_audio(duration=3)
                try:
                    # 识别音频
                    text = self.transcribe_file(audio_file)
                    if text:
                        print(f"📝 识别结果: {text}")
                finally:
                    # 确保删除临时文件
                    if os.path.exists(audio_file):
                        os.unlink(audio_file)
        except KeyboardInterrupt:
            print("\n⏹️ 实时语音识别已停止")
            
    def chat_mode(self):
        """对话模式"""
        print("💬 进入对话模式 (说'拜拜'可返回选项界面，按 Ctrl+C 退出)")
        print("🗣️ 请说话...")

        # 简单的对话逻辑，实际应用中可以接入大模型API
        conversation_history = []
        
        # 调试信息
        print(f"🔧 调试: 对话开始时TTS引擎状态 = {self.tts_engine is not None}")
        if self.tts_engine:
            print(f"🔧 调试: TTS引擎类型 = {getattr(self.tts_engine, 'engine_type', '未知')}")

        try:
            while True:
                # 使用VAD录制音频
                audio_file = self.record_audio_vad(silence_duration=2)
                try:
                    # 识别音频
                    user_input = self.transcribe_file(audio_file)

                    if user_input and not user_input.startswith("<|nospeech|>"):
                        print(f"👤 你说: {user_input}")
                        
                        # 调试信息
                        print(f"🔧 调试: 准备检查关键词")
                        
                        # 检查退出关键词
                        exit_keywords = ["你滚吧", "你赶紧去死吧", "滚吧", "滚", "滚啊", "退出", "退出吧", "关机吧"]
                        if any(keyword in user_input for keyword in exit_keywords):
                            print("👋 好的，再见！")
                            if self.tts_engine:
                                print("🔊 正在播放退出语音")
                                self.tts_engine.speak("好的，再见！")
                            break
                        
                        # 检查返回选项界面关键词
                        elif "拜拜" in user_input:
                            print("👋 好的，我们下次再聊！")
                            if self.tts_engine:
                                print("🔊 正在播放返回语音")
                                self.tts_engine.speak("好的，我们下次再聊！")
                            # 返回True表示需要回到选项界面
                            return True

                        # 使用大模型API生成回复（如果可用）
                        print("🤖 正在生成回复...")
                        response = self.generate_llm_response(user_input, conversation_history)
                        print(f"🤖 回复: {response}")

                        # 使用TTS播放回复（如果可用）
                        print(f"🔧 sensevoice_demo TTS引擎状态: {self.tts_engine is not None}")
                        if self.tts_engine:
                            print(f"🔊 播放回复: {response}")
                            success = self.tts_engine.speak(response)
                            print(f"🔧 TTS播放结果: {success}")
                        else:
                            print("🔇 TTS引擎未初始化，跳过语音播放")

                        # 将对话加入历史记录
                        conversation_history.append({"user": user_input, "bot": response})
                        # 限制历史记录长度
                        if len(conversation_history) > 10:
                            conversation_history.pop(0)
                finally:
                    # 确保删除临时文件
                    if os.path.exists(audio_file):
                        os.unlink(audio_file)
                        
        except KeyboardInterrupt:
            print("\n👋 对话结束，再见！")
        # 返回False表示是通过Ctrl+C退出的
        return False
    
    def generate_llm_response(self, user_input, conversation_history):
        """使用大模型API生成回复"""
        # 如果LLM API可用，使用它生成回复
        if self.llm_api is not None:
            try:
                # 检查LLM模块是否有generate_response方法
                if hasattr(self.llm_api, 'generate_response'):
                    # 构造对话历史
                    history = []
                    for exchange in conversation_history:
                        history.append({"role": "user", "content": exchange["user"]})
                        history.append({"role": "assistant", "content": exchange["bot"]})
                    
                    # 调用LLM API
                    response = self.llm_api.generate_response(user_input, history)
                    return response
                else:
                    print("⚠️ LLM模块缺少generate_response方法，使用默认回复逻辑")
                    return self.generate_response(user_input, conversation_history)
            except Exception as e:
                print(f"⚠️ LLM API调用失败: {e}")
                # 回退到默认回复逻辑
                return self.generate_response(user_input, conversation_history)
        else:
            # 使用默认回复逻辑
            return self.generate_response(user_input, conversation_history)
    
    def generate_response(self, user_input, conversation_history):
        """生成回复 - 简化版本，实际应用中可接入大模型"""
        # 这里是一个非常简单的回复逻辑，实际应用中应该替换为大模型API调用
        user_input = user_input.lower()
        
        if "你好" in user_input or "hello" in user_input:
            return "你好！有什么我可以帮助你的吗？"
        elif "谢谢" in user_input or "thank" in user_input:
            return "不客气！还有其他需要帮助的吗？"
        elif "再见" in user_input or "bye" in user_input:
            return "再见！期待下次与你交流！"
        elif "天气" in user_input:
            return "我无法获取实时天气信息，建议你查看天气预报应用。"
        elif "名字" in user_input or "你是谁" in user_input:
            return "我是基于SenseVoice的语音对话助手。"
        else:
            # 基于历史对话生成回复
            if conversation_history:
                last_exchange = conversation_history[-1]
                if "你好" in last_exchange["user"]:
                    return "很高兴见到你！今天过得怎么样？"
                elif "天气" in last_exchange["user"]:
                    return "虽然我不知道具体天气，但我希望是个好天气！"
            
            # 默认回复
            responses = [
                "很有趣！能告诉我更多吗？",
                "我明白了，还有别的吗？",
                "好的，我记住了。",
                "这很有意思呢！",
                "谢谢你分享这些信息。"
            ]
            import random
            return random.choice(responses)

# 使用示例
if __name__ == "__main__":
    # 1. 创建识别器
    asr = SenseVoiceASR()
    
    # 2. 加载模型
    if asr.load_model():
        print("🎯 SenseVoice准备就绪！")
        
        # 循环显示菜单直到用户选择退出
        while True:
            # 3. 提供选项
            print("\n请选择操作:")
            print("1. 识别测试文件")
            print("2. 实时麦克风语音识别")
            print("3. 语音对话模式")
            print("4. 语音对话模式（选择LLM）")
            print("5. 语音对话模式（选择LLM和在线TTS）")
            print("6. 语音对话模式（选择LLM和本地TTS）")
            
            choice = input("请输入选项 (1, 2, 3, 4, 5 或 6): ").strip()
            
            if choice == "1":
                # 识别测试文件
                test_file = "./SenseVoice/models/SenseVoiceSmall/example/zh.mp3"
                if os.path.exists(test_file):
                    text = asr.transcribe_file(test_file)
                    if text:
                        print(f"📝 识别结果: {text}")
                else:
                    print(f"⚠️  测试文件不存在: {test_file}")
                    print("💡 请先创建一个test_audio.wav文件")
                    
            elif choice == "2":
                # 实时语音识别
                asr.live_transcribe()
                
            elif choice == "3":
                # 对话模式 - 使用默认LLM
                asr.init_llm_api()
                back_to_menu = asr.chat_mode()
                # 如果是通过"拜拜"退出，则重新显示菜单
                if back_to_menu:
                    continue
                # 否则是通过Ctrl+C退出，结束程序
                else:
                    break
                
            elif choice == "4":
                # 对话模式 - 选择LLM
                print("\n请选择大语言模型:")
                print("1. DeepSeek")
                print("2. 豆包(Doubao)")
                print("3. 通义千问(Qwen)")
                
                llm_choice = input("请输入选项 (1, 2 或 3): ").strip()
                llm_type = "deepseek"
                
                if llm_choice == "1":
                    llm_type = "deepseek"
                elif llm_choice == "2":
                    llm_type = "doubao"
                elif llm_choice == "3":
                    llm_type = "qwen"
                else:
                    print("❌ 无效选项，使用默认模型: DeepSeek")
                    
                asr.init_llm_api(llm_type)
                if asr.selected_llm:
                    print(f"✅ 已选择 {asr.selected_llm} 模型")
                back_to_menu = asr.chat_mode()
                # 如果是通过"拜拜"退出，则重新显示菜单
                if back_to_menu:
                    continue
                # 否则是通过Ctrl+C退出，结束程序
                else:
                    break
                
            elif choice == "5":
                # 对话模式 - 选择LLM和在线TTS
                # 选择LLM
                print("\n请选择大语言模型:")
                print("1. DeepSeek")
                print("2. 豆包(Doubao)")
                print("3. 通义千问(Qwen)")
                
                llm_choice = input("请输入选项 (1, 2 或 3): ").strip()
                llm_type = "deepseek"
                
                if llm_choice == "1":
                    llm_type = "deepseek"
                elif llm_choice == "2":
                    llm_type = "doubao"
                elif llm_choice == "3":
                    llm_type = "qwen"
                else:
                    print("❌ 无效选项，使用默认模型: DeepSeek")
                    
                asr.init_llm_api(llm_type)
                if asr.selected_llm:
                    print(f"✅ 已选择 {asr.selected_llm} 模型")
                
                # 选择在线TTS
                print("\n请选择在线TTS引擎:")
                print("1. pyttsx3 (离线, 免费, 跨平台)")
                print("2. 百度TTS (在线, 需API密钥)")
                print("3. 阿里云TTS (在线, 需API密钥)")
                
                tts_choice = input("请输入选项 (1, 2 或 3): ").strip()
                tts_type = "pyttsx3"
                
                if tts_choice == "1":
                    tts_type = "pyttsx3"
                elif tts_choice == "2":
                    tts_type = "baidu"
                elif tts_choice == "3":
                    tts_type = "ali"
                else:
                    print("❌ 无效选项，使用默认TTS引擎: pyttsx3")
                    
                if asr.init_tts_engine(tts_type, local=False):
                    print(f"✅ 已选择 {tts_type} 在线TTS引擎")
                else:
                    print("❌ TTS引擎初始化失败，将继续使用文本回复")
                
                back_to_menu = asr.chat_mode()
                # 如果是通过"拜拜"退出，则重新显示菜单
                if back_to_menu:
                    continue
                # 否则是通过Ctrl+C退出，结束程序
                else:
                    break
                
            elif choice == "6":
                # 对话模式 - 选择LLM和本地TTS
                # 选择LLM
                print("\n请选择大语言模型:")
                print("1. DeepSeek")
                print("2. 豆包(Doubao)")
                print("3. 通义千问(Qwen)")
                
                llm_choice = input("请输入选项 (1, 2 或 3): ").strip()
                llm_type = "deepseek"
                
                if llm_choice == "1":
                    llm_type = "deepseek"
                elif llm_choice == "2":
                    llm_type = "doubao"
                elif llm_choice == "3":
                    llm_type = "qwen"
                else:
                    print("❌ 无效选项，使用默认模型: DeepSeek")
                    
                asr.init_llm_api(llm_type)
                if asr.selected_llm:
                    print(f"✅ 已选择 {asr.selected_llm} 模型")
                
                # 选择本地TTS
                print("\n请选择本地TTS引擎:")
                print("1. MeloTTS (推荐，支持中英混合)")
                print("2. PaddleSpeech (百度开源，中文优化)")
                print("3. Coqui TTS (多语言支持)")
                print("4. IndexTTS (B站开源，高质量语音)")
                print("5. Edge-TTS (微软语音，需要网络连接)")
                print("6. pyttsx3 (系统语音，轻量级，无需网络)")
                
                tts_choice = input("请输入选项 (1, 2, 3, 4, 5 或 6): ").strip()
                tts_type = "melotts"
                
                if tts_choice == "1":
                    tts_type = "melotts"
                elif tts_choice == "2":
                    tts_type = "paddlespeech"
                elif tts_choice == "3":
                    tts_type = "coqui"
                elif tts_choice == "4":
                    tts_type = "indextts"
                elif tts_choice == "5":
                    tts_type = "edge-tts"
                elif tts_choice == "6":
                    tts_type = "pyttsx3"
                else:
                    print("❌ 无效选项，使用默认本地TTS引擎: MeloTTS")
                    
                if asr.init_tts_engine(tts_type, local=True):
                    print(f"✅ 已选择 {tts_type} 本地TTS引擎")
                else:
                    print("❌ 本地TTS引擎初始化失败，将继续使用文本回复")
                
                back_to_menu = asr.chat_mode()
                # 如果是通过"拜拜"退出，则重新显示菜单
                if back_to_menu:
                    continue
                # 否则是通过Ctrl+C退出，结束程序
                else:
                    break
                
            else:
                print("❌ 无效选项")

    print("\n👋 感谢使用SenseVoice语音识别系统，再见！")
