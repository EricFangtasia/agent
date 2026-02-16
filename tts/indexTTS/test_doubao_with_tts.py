#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试豆包API与TTS结合使用的脚本
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

def test_doubao_with_tts():
    """测试豆包API与TTS结合使用"""
    try:
        print("🔍 测试豆包API与TTS结合使用")
        print("=" * 30)
        
        # 导入SenseVoiceASR类
        from asr.sensevoice_demo import SenseVoiceASR
        
        # 创建ASR实例
        asr = SenseVoiceASR()
        
        print("🔧 步骤1: 初始化豆包LLM API...")
        llm_success = asr.init_llm_api("doubao")
        print(f"✅ LLM API初始化结果: {llm_success}")
        
        print("\n🔧 步骤2: 初始化pyttsx3 TTS引擎...")
        tts_success = asr.init_tts_engine(tts_type="pyttsx3", local=True)
        print(f"✅ TTS引擎初始化结果: {tts_success}")
        
        if not (llm_success and tts_success):
            print("❌ LLM或TTS初始化失败，无法继续测试")
            return
            
        print(f"🔧 当前TTS引擎状态: {asr.tts_engine}")
        print(f"🔧 TTS引擎类型: {getattr(asr.tts_engine, 'engine_type', '未知')}")
        
        # 测试几种不同的对话场景
        test_cases = [
            "你好",
            "今天天气怎么样？",
            "你能帮我做什么？"
        ]
        
        conversation_history = []
        
        print("\n💬 开始对话测试...")
        for i, user_input in enumerate(test_cases, 1):
            print(f"\n--- 测试 {i} ---")
            print(f"👤 用户: {user_input}")
            
            # 生成回复
            print("🤖 正在生成回复...")
            response = asr.generate_llm_response(user_input, conversation_history)
            print(f"🤖 豆包回复: {response}")
            
            # 播放回复
            if asr.tts_engine:
                print(f"🔊 正在播放回复...")
                success = asr.tts_engine.speak(response)
                print(f"✅ TTS播放结果: {'成功' if success else '失败'}")
            else:
                print("🔇 TTS引擎未初始化")
            
            # 更新对话历史
            conversation_history.append({"user": user_input, "bot": response})
            print(f"📝 对话历史更新，当前条目数: {len(conversation_history)}")
        
        print("\n🎉 所有测试完成!")
        print("\n💡 如果以上测试都能正常播放语音，说明豆包API与TTS集成正常工作")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_doubao_with_tts()