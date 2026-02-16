#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复TTS引擎初始化问题的脚本
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

def test_current_main_flow():
    """测试当前主流程中TTS引擎的状态"""
    try:
        print("🔍 测试当前主流程中TTS引擎的状态")
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
        
        print("🔧 步骤3: 初始化TTS引擎...")
        tts_success = asr.init_tts_engine(tts_type="pyttsx3", local=True)
        print(f"✅ TTS初始化结果: {tts_success}")
        print(f"✅ TTS引擎状态: {asr.tts_engine is not None}")
        
        if asr.tts_engine:
            print(f"✅ TTS引擎类型: {getattr(asr.tts_engine, 'engine_type', '未知')}")
            
            # 测试播放
            print("🔊 测试TTS播放...")
            test_result = asr.tts_engine.speak("TTS引擎初始化成功")
            print(f"✅ TTS播放测试结果: {'成功' if test_result else '失败'}")
        else:
            print("❌ TTS引擎未正确初始化")
            return
        
        print("\n🔧 步骤4: 模拟chat_mode中的TTS状态检查...")
        # 模拟chat_mode开始时的状态检查
        print(f"🔧 对话模式开始时TTS引擎状态: {asr.tts_engine is not None}")
        if asr.tts_engine:
            print(f"🔧 对话模式TTS引擎类型: {getattr(asr.tts_engine, 'engine_type', '未知')}")
        
        # 模拟一次完整的对话循环
        print("\n💬 模拟对话循环...")
        user_input = "你好"
        print(f"👤 用户输入: {user_input}")
        
        # 检查退出关键词
        exit_keywords = ["你滚吧", "你赶紧去死吧", "滚吧", "滚", "滚啊", "退出", "退出吧", "关机吧"]
        if any(keyword in user_input for keyword in exit_keywords):
            print("👋 检测到退出关键词")
            print(f"🔧 退出前TTS引擎状态: {asr.tts_engine is not None}")
            if asr.tts_engine:
                asr.tts_engine.speak("好的，再见！")
        elif "拜拜" in user_input:
            print("👋 检测到返回选项界面关键词")
            print(f"🔧 拜拜时TTS引擎状态: {asr.tts_engine is not None}")
            if asr.tts_engine:
                asr.tts_engine.speak("好的，我们下次再聊！")
        else:
            print("🤖 生成回复...")
            response = "你好！有什么我可以帮助你的吗？"
            print(f"🤖 回复: {response}")
            
            print(f"🔧 回复生成后TTS引擎状态: {asr.tts_engine is not None}")
            if asr.tts_engine:
                print("🔊 播放回复...")
                speak_result = asr.tts_engine.speak(response)
                print(f"✅ 播放结果: {'成功' if speak_result else '失败'}")
            else:
                print("🔇 TTS引擎未初始化，跳过语音播放")
        
        print("\n🎉 测试完成!")
        print("\n💡 如果以上所有测试都显示成功，说明TTS引擎可以正常工作")
        print("💡 如果在实际使用中仍然遇到'TTS引擎状态: False'，请检查:")
        print("   1. 是否在每次对话开始前正确初始化了TTS引擎")
        print("   2. TTS引擎对象是否在对话过程中被意外覆盖或清空")
        print("   3. 是否在异常处理中意外重置了TTS引擎")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_current_main_flow()