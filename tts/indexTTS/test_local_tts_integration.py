#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试本地TTS引擎集成
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

def test_local_tts_integration():
    """测试本地TTS引擎集成"""
    try:
        print("🔍 正在测试本地TTS引擎集成...")
        
        # 导入SenseVoiceASR类
        from asr.sensevoice_demo import SenseVoiceASR
        
        # 创建ASR实例
        asr = SenseVoiceASR()
        
        print("🔧 初始化本地TTS引擎...")
        # 初始化本地TTS引擎，使用edge-tts
        success = asr.init_tts_engine(tts_type="edge-tts", local=True)
        
        if success:
            print("✅ 本地TTS引擎初始化成功")
            
            # 测试语音播放
            test_text = "你好，这是本地TTS引擎的测试语音。"
            print(f"🔊 播放测试文本: {test_text}")
            
            if asr.tts_engine:
                play_success = asr.tts_engine.speak(test_text)
                if play_success:
                    print("✅ 语音播放成功")
                    return True
                else:
                    print("❌ 语音播放失败")
                    return False
            else:
                print("❌ TTS引擎未正确初始化")
                return False
        else:
            print("❌ 本地TTS引擎初始化失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试本地TTS引擎集成时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_tts_engines():
    """测试不同的本地TTS引擎"""
    try:
        print("\n🔍 测试不同的本地TTS引擎...")
        
        # 导入SenseVoiceASR类
        from asr.sensevoice_demo import SenseVoiceASR
        
        # 创建ASR实例
        asr = SenseVoiceASR()
        
        # 测试的TTS引擎列表
        tts_engines = ["pyttsx3", "edge-tts", "coqui", "melotts"]
        
        for engine in tts_engines:
            print(f"\n🔧 尝试初始化 {engine} 引擎...")
            success = asr.init_tts_engine(tts_type=engine, local=True)
            
            if success:
                print(f"✅ {engine} 引擎初始化成功")
                
                # 测试语音播放
                test_text = f"这是{engine}引擎的测试语音。"
                print(f"🔊 播放测试文本: {test_text}")
                
                if asr.tts_engine:
                    play_success = asr.tts_engine.speak(test_text)
                    if play_success:
                        print(f"✅ {engine} 语音播放成功")
                        # 成功一个就可以退出了
                        return True
                    else:
                        print(f"❌ {engine} 语音播放失败")
                else:
                    print(f"❌ {engine} 引擎未正确初始化")
            else:
                print(f"❌ {engine} 引擎初始化失败")
        
        return False
        
    except Exception as e:
        print(f"❌ 测试不同TTS引擎时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 本地TTS引擎集成测试")
    print("=" * 30)
    
    # 测试本地TTS引擎集成
    success1 = test_local_tts_integration()
    
    # 测试不同的TTS引擎
    success2 = test_different_tts_engines()
    
    print("\n" + "=" * 30)
    if success1 or success2:
        print("🎉 本地TTS引擎集成测试成功")
        print("💡 现在您可以在语音对话中使用本地TTS引擎了")
    else:
        print("❌ 本地TTS引擎集成测试失败")
        print("💡 建议检查TTS引擎的安装和配置")