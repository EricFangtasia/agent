#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试完整的语音对话流程，使用豆包API
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

def test_voice_conversation():
    """测试完整的语音对话流程"""
    try:
        print("🔍 测试完整的语音对话流程")
        print("=" * 30)
        
        # 导入SenseVoiceASR类
        from asr.sensevoice_demo import SenseVoiceASR
        
        # 创建ASR实例
        asr = SenseVoiceASR()
        
        print("🔧 步骤1: 加载SenseVoice模型...")
        if not asr.load_model():
            print("❌ SenseVoice模型加载失败")
            return
            
        print("🔧 步骤2: 初始化豆包LLM API...")
        llm_success = asr.init_llm_api("doubao")
        print(f"✅ LLM API初始化结果: {llm_success}")
        
        print("\n🔧 步骤3: 初始化pyttsx3 TTS引擎...")
        tts_success = asr.init_tts_engine(tts_type="pyttsx3", local=True)
        print(f"✅ TTS引擎初始化结果: {tts_success}")
        
        if not (llm_success and tts_success):
            print("❌ LLM或TTS初始化失败，无法继续测试")
            return
        
        print(f"🔧 TTS引擎类型: {getattr(asr.tts_engine, 'engine_type', '未知')}")
        
        # 模拟一次简短的对话
        print("\n💬 模拟语音对话流程...")
        
        # 模拟对话历史
        conversation_history = []
        
        # 模拟用户输入文本（在真实场景中这会通过语音识别获得）
        simulated_user_inputs = [
            "你好",
            "你能做什么？",
            "拜拜"
        ]
        
        for user_text in simulated_user_inputs:
            print(f"\n--- 对话回合 ---")
            print(f"👤 识别到用户语音: {user_text}")
            
            # 检查退出关键词
            exit_keywords = ["你滚吧", "你赶紧去死吧", "滚吧", "滚", "滚啊", "退出", "退出吧", "关机吧"]
            if any(keyword in user_text for keyword in exit_keywords):
                print("👋 检测到退出关键词")
                if asr.tts_engine:
                    asr.tts_engine.speak("好的，再见！")
                break
            
            # 检查返回选项界面关键词
            elif "拜拜" in user_text:
                print("👋 检测到返回选项界面关键词")
                if asr.tts_engine:
                    asr.tts_engine.speak("好的，我们下次再聊！")
                print("✅ 对话结束，返回选项界面")
                break

            # 生成回复
            print("🤖 正在生成回复...")
            response = asr.generate_llm_response(user_text, conversation_history)
            print(f"🤖 豆包回复: {response}")

            # 使用TTS播放回复
            if asr.tts_engine:
                print(f"🔊 播放回复...")
                success = asr.tts_engine.speak(response)
                print(f"✅ TTS播放结果: {'成功' if success else '失败'}")
            else:
                print("🔇 TTS引擎未初始化")

            # 更新对话历史
            conversation_history.append({"user": user_text, "bot": response})
            print(f"📝 对话历史更新，当前条目数: {len(conversation_history)}")
        
        print("\n🎉 语音对话流程测试完成!")
        print("\n💡 如果以上测试都能正常播放语音，说明完整的语音对话流程正常工作")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_voice_conversation()