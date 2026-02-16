#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启动SenseVoice语音对话系统的脚本
"""

import os
import sys

def main():
    """主函数"""
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 构建sensevoice_demo.py的完整路径
        demo_path = os.path.join(current_dir, 'agent', 'asr', 'sensevoice_demo.py')
        
        # 检查文件是否存在
        if not os.path.exists(demo_path):
            print(f"❌ 错误: 找不到文件 {demo_path}")
            print("请确保项目结构正确，sensevoice_demo.py文件存在")
            return 1
            
        # 添加项目根目录到Python路径
        sys.path.insert(0, current_dir)
        
        # 动态导入并运行主程序
        print("🔧 正在启动SenseVoice语音对话系统...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("sensevoice_demo", demo_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 创建并运行主程序
        from agent.asr.sensevoice_demo import SenseVoiceASR
        
        # 创建ASR实例
        asr = SenseVoiceASR()
        
        # 显示欢迎信息
        print("=" * 50)
        print("🤖 SenseVoice语音对话系统")
        print("=" * 50)
        
        # 主循环
        while True:
            print("\n📋 请选择功能:")
            print("1. 实时语音识别")
            print("2. 语音对话模式 (在线TTS)")
            print("3. 语音对话模式 (本地TTS)")
            print("4. 退出程序")
            
            try:
                choice = input("\n请输入选项 (1-4): ").strip()
                
                if choice == "1":
                    # 加载模型
                    if not asr.load_model():
                        print("❌ 模型加载失败")
                        continue
                        
                    # 实时语音识别
                    asr.live_transcribe()
                    
                elif choice == "2":
                    # 加载模型
                    if not asr.load_model():
                        print("❌ 模型加载失败")
                        continue
                        
                    # 初始化LLM API
                    print("🔧 初始化LLM API...")
                    if not asr.init_llm_api():
                        print("⚠️ LLM API初始化失败，将使用默认回复")
                    
                    # 初始化TTS引擎
                    print("🔧 初始化在线TTS引擎...")
                    if not asr.init_tts_engine(local=False):
                        print("⚠️ 在线TTS引擎初始化失败")
                    
                    # 进入对话模式
                    asr.chat_mode()
                    
                elif choice == "3":
                    # 加载模型
                    if not asr.load_model():
                        print("❌ 模型加载失败")
                        continue
                        
                    # 初始化LLM API
                    print("🔧 初始化LLM API...")
                    if not asr.init_llm_api():
                        print("⚠️ LLM API初始化失败，将使用默认回复")
                    
                    # 初始化本地TTS引擎
                    print("🔧 初始化本地TTS引擎...")
                    print("请选择本地TTS引擎:")
                    print("1. MeloTTS (推荐，支持中英混合)")
                    print("2. PaddleSpeech (百度开源，中文优化)")
                    print("3. Coqui TTS (多语言支持)")
                    print("4. IndexTTS (B站开源，高质量语音)")
                    print("5. Edge-TTS (微软语音，需要网络连接)")
                    print("6. pyttsx3 (系统语音，轻量级，无需网络)")
                    
                    tts_choice = input("请选择TTS引擎 (1-6，默认为6): ").strip()
                    tts_type_map = {
                        "1": "melotts",
                        "2": "paddlespeech",
                        "3": "coqui",
                        "4": "indextts",
                        "5": "edge-tts",
                        "6": "pyttsx3"
                    }
                    
                    tts_type = tts_type_map.get(tts_choice, "pyttsx3")
                    if not asr.init_tts_engine(tts_type=tts_type, local=True):
                        print("⚠️ 本地TTS引擎初始化失败")
                    
                    # 进入对话模式
                    asr.chat_mode()
                    
                elif choice == "4":
                    print("👋 再见!")
                    break
                    
                else:
                    print("❌ 无效选项，请重新选择")
                    
            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断，再见!")
                break
            except Exception as e:
                print(f"❌ 程序运行出错: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())