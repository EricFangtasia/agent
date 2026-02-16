#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试IndexTTS的脚本
"""

import os
import sys
import tempfile

# 添加项目路径到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent', 'tts'))

def test_indextts():
    """测试IndexTTS引擎"""
    try:
        # 导入本地TTS引擎
        from local_tts import LocalTTSEngine
        
        print("🔍 正在初始化IndexTTS引擎...")
        
        # 创建TTS引擎实例
        tts_engine = LocalTTSEngine()
        
        # 初始化IndexTTS引擎
        if not tts_engine.init_engine("indextts"):
            print("❌ IndexTTS引擎初始化失败")
            return False
            
        print("✅ IndexTTS引擎初始化成功！")
        
        # 测试文本列表
        test_texts = [
            "你好，我是IndexTTS语音合成引擎。",
            "今天天气怎么样？",
            "欢迎使用IndexTTS语音合成系统。",
            "这个系统可以将文字转换为自然流畅的语音。",
            "感谢您对IndexTTS的关注和支持！"
        ]
        
        print("\n🔊 开始测试语音播放...")
        for i, text in enumerate(test_texts, 1):
            print(f"\n[{i}/{len(test_texts)}] 播放文本: {text}")
            try:
                success = tts_engine.speak(text)
                if success:
                    print(f"✅ 文本{i}播放成功")
                else:
                    print(f"❌ 文本{i}播放失败")
            except Exception as e:
                print(f"❌ 播放文本{i}时发生错误: {e}")
                
        print("\n💾 开始测试语音保存...")
        for i, text in enumerate(test_texts[:2], 1):
            try:
                # 创建临时文件名
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    filename = tmp_file.name
                
                print(f"\n[{i}/2] 保存文本到文件: {text}")
                saved_filename = tts_engine.save_to_file(text, filename)
                if saved_filename:
                    print(f"✅ 文本{i}已保存到: {saved_filename}")
                    # 清理临时文件
                    if os.path.exists(saved_filename):
                        os.unlink(saved_filename)
                else:
                    print(f"❌ 文本{i}保存失败")
            except Exception as e:
                print(f"❌ 保存文本{i}时发生错误: {e}")
        
        print("\n🎉 IndexTTS测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试IndexTTS时发生错误: {e}")
        return False

if __name__ == "__main__":
    print("🧪 IndexTTS测试程序")
    print("=" * 30)
    
    success = test_indextts()
    
    if success:
        print("\n✅ 所有测试已完成")
    else:
        print("\n❌ 测试过程中出现错误")
        sys.exit(1)