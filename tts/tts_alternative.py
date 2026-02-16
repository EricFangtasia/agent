import os
import sys
import time
import tempfile

def check_and_install_dependencies():
    """检查本地TTS引擎依赖"""
    engines_available = {}
    
    # 检查pyttsx3
    try:
        import pyttsx3
        engines_available['pyttsx3'] = True
        print("✓ pyttsx3 可用 - 本地TTS引擎")
    except ImportError:
        engines_available['pyttsx3'] = False
        print("✗ pyttsx3 不可用 - 请运行: pip install pyttsx3")
    
    # 检查edge_tts
    try:
        import edge_tts
        engines_available['edge_tts'] = True
        print("✓ edge_tts 可用 - 在线TTS引擎")
    except ImportError:
        engines_available['edge_tts'] = False
        print("✗ edge_tts 不可用 - 请运行: pip install edge-tts")
    
    # 检查pygame (用于播放)
    try:
        import pygame
        engines_available['pygame'] = True
        print("✓ pygame 可用 - 音频播放")
    except ImportError:
        engines_available['pygame'] = False
        print("✗ pygame 不可用 - 请运行: pip install pygame")
    
    return engines_available

def speak_with_pyttsx3(text, rate=200, volume=0.9, voice_id=None):
    """使用pyttsx3进行语音合成"""
    try:
        import pyttsx3
        
        # 初始化引擎
        engine = pyttsx3.init()
        
        # 设置语速
        engine.setProperty('rate', rate)
        
        # 设置音量
        engine.setProperty('volume', volume)
        
        # 如果指定了语音类型
        if voice_id:
            engine.setProperty('voice', voice_id)
        
        # 直接播放
        engine.say(text)
        engine.runAndWait()
        
        # 清理资源
        engine.stop()
        
        return True
    except Exception as e:
        print(f"pyttsx3播放失败: {e}")
        return False

def speak_with_edge_tts(text, voice="zh-CN-XiaoxiaoNeural", output_file=None):
    """使用edge_tts进行语音合成"""
    try:
        import edge_tts
        import asyncio
        
        if output_file is None:
            output_file = os.path.join(tempfile.gettempdir(), f"edge_tts_output_{int(time.time())}.mp3")
        
        async def _run_tts():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
        
        asyncio.run(_run_tts())
        
        # 播放音频
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.getBusy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()
        except:
            print(f"音频已保存到: {output_file}，请手动播放")
        
        return True
    except Exception as e:
        print(f"edge_tts播放失败: {e}")
        return False

def list_voices():
    """列出可用的语音"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print("\n可用语音列表:")
        for i, voice in enumerate(voices):
            print(f"  {i}: {voice.name} - {voice.languages}")
        return voices
    except:
        print("无法获取语音列表")
        return []

def main():
    """主函数 - 使用本地TTS引擎作为备选方案"""
    print("本地TTS引擎备选方案")
    print("=" * 40)
    
    # 检查可用的引擎
    available_engines = check_and_install_dependencies()
    
    if not any([available_engines.get('pyttsx3'), available_engines.get('edge_tts')]):
        print("\n错误：没有可用的TTS引擎，请安装至少一个TTS库。")
        print("推荐安装: pip install pyttsx3 pygame")
        return
    
    # 示例文本
    text = "你好，这是本地TTS引擎的演示。如果你的IndexTTS模型还没下载完成，可以先使用这个作为备选方案。"
    print(f"\n要播放的文本: {text}")
    
    # 尝试使用pyttsx3（本地引擎，无需网络）
    if available_engines.get('pyttsx3'):
        print("\n正在使用 pyttsx3 引擎...")
        success = speak_with_pyttsx3(text)
        if success:
            print("✓ pyttsx3 播放成功")
        else:
            print("✗ pyttsx3 播放失败")
    else:
        print("\npyttsx3 不可用，跳过...")
    
    # 如果有pygame，尝试使用edge_tts（在线引擎，需要网络）
    if available_engines.get('edge_tts') and available_engines.get('pygame'):
        print("\n正在使用 edge_tts 引擎...")
        success = speak_with_edge_tts(text)
        if success:
            print("✓ edge_tts 播放成功")
        else:
            print("✗ edge_tts 播放失败")
    else:
        print("\nedge_tts 或 pygame 不可用，跳过...")
    
    print("\n提示:")
    if not available_engines.get('pyttsx3'):
        print("- 安装 pyttsx3: pip install pyttsx3 (本地引擎，无需网络)")
    if not available_engines.get('edge_tts'):
        print("- 安装 edge_tts: pip install edge-tts (在线引擎，需要网络)")
    if not available_engines.get('pygame'):
        print("- 安装 pygame: pip install pygame (用于播放音频)")

if __name__ == "__main__":
    main()