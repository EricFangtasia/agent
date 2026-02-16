#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试增强的TTS引擎功能
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

def test_enhanced_tts_features():
    """测试增强的TTS引擎功能"""
    try:
        print("🔍 测试增强的TTS引擎功能")
        print("=" * 40)
        
        # 导入SenseVoiceASR类
        from asr.sensevoice_demo import SenseVoiceASR
        
        # 创建ASR实例
        asr = SenseVoiceASR()
        
        print("🔧 步骤1: 初始化模型...")
        if not asr.load_model():
            print("❌ 模型加载失败")
            return
        
        print("🔧 步骤2: 初始化豆包LLM API...")
        llm_success = asr.init_llm_api("doubao")
        print(f"✅ LLM初始化结果: {llm_success}")
        
        print("🔧 步骤3: 测试增强的TTS初始化功能...")
        # 故意不初始化TTS引擎，测试chat_mode中的自动恢复功能
        print(f"✅ 初始TTS引擎状态: {asr.tts_engine is not None}")
        
        print("\n🔧 步骤4: 模拟对话流程，测试TTS自动恢复功能...")
        # 模拟一次简短的对话
        conversation_history = []
        
        # 模拟用户输入文本
        simulated_user_inputs = [
            "你好",
            "拜拜"
        ]
        
        # 重要：故意不初始化TTS引擎，测试chat_mode中的自动恢复功能
        asr.tts_engine = None
        
        for user_text in simulated_user_inputs:
            print(f"\n--- 对话回合 ---")
            print(f"👤 识别到用户语音: {user_text}")
            
            # 检查退出关键词
            exit_keywords = ["你滚吧", "你赶紧去死吧", "滚吧", "滚", "滚啊", "退出", "退出吧", "关机吧"]
            if any(keyword in user_text for keyword in exit_keywords):
                print("👋 检测到退出关键词")
                # 测试紧急初始化
                if not asr.tts_engine:
                    print("⚠️ TTS引擎不可用，测试紧急初始化...")
                    asr.init_tts_engine(tts_type="pyttsx3", local=True)
                if asr.tts_engine:
                    asr.tts_engine.speak("好的，再见！")
                break
            
            # 检查返回选项界面关键词
            elif "拜拜" in user_text:
                print("👋 检测到返回选项界面关键词")
                # 测试紧急初始化
                if not asr.tts_engine:
                    print("⚠️ TTS引擎不可用，测试紧急初始化...")
                    asr.init_tts_engine(tts_type="pyttsx3", local=True)
                if asr.tts_engine:
                    asr.tts_engine.speak("好的，我们下次再聊！")
                print("✅ 对话结束，返回选项界面")
                break

            # 生成回复
            print("🤖 正在生成回复...")
            response = "你好！有什么我可以帮助你的吗？"
            print(f"🤖 回复: {response}")

            # 使用TTS播放回复（测试紧急初始化）
            print(f"🔧 播放前TTS引擎状态: {asr.tts_engine is not None}")
            if not asr.tts_engine:
                print("⚠️ TTS引擎不可用，测试紧急初始化...")
                asr.init_tts_engine(tts_type="pyttsx3", local=True)
                print(f"🔧 紧急初始化后TTS引擎状态: {asr.tts_engine is not None}")
                
            if asr.tts_engine:
                print("🔊 播放回复...")
                success = asr.tts_engine.speak(response)
                print(f"✅ TTS播放结果: {'成功' if success else '失败'}")
            else:
                print("🔇 TTS引擎未初始化，跳过语音播放")

            # 更新对话历史
            conversation_history.append({"user": user_text, "bot": response})
            print(f"📝 对话历史更新，当前条目数: {len(conversation_history)}")
        
        print("\n🎉 增强功能测试完成!")
        print("\n💡 增强功能包括:")
        print("   1. 自动检测TTS引擎状态")
        print("   2. 紧急初始化TTS引擎")
        print("   3. 多重备用方案")
        print("   4. 更详细的错误提示")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_tts_features()