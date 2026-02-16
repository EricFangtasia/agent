#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试edge-tts的脚本
"""

import os
import sys
import asyncio
import tempfile

def test_edge_tts_basic():
    """基本测试edge-tts功能"""
    try:
        print("🔍 正在导入edge-tts...")
        import edge_tts
        print("✅ edge-tts导入成功")
        
        # 测试文本
        text = "你好，这是edge-tts语音合成测试。"
        print(f"📝 测试文本: {text}")
        
        # 获取可用的中文语音
        async def get_voices():
            voices = await edge_tts.list_voices()
            chinese_voices = [v for v in voices if v["Locale"].startswith("zh")]
            return chinese_voices
        
        print("🔍 正在获取中文语音列表...")
        chinese_voices = asyncio.run(get_voices())
        if chinese_voices:
            print(f"✅ 找到 {len(chinese_voices)} 个中文语音:")
            for voice in chinese_voices[:5]:  # 只显示前5个
                print(f"  - {voice['ShortName']}: {voice['FriendlyName']}")
        else:
            print("⚠️ 未找到中文语音")
            return False
        
        # 选择第一个中文语音
        voice = chinese_voices[0]["ShortName"]
        print(f"🔊 使用语音: {voice}")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            filename = tmp_file.name
        print(f"📁 临时文件: {filename}")
        
        # 合成语音
        print("🔊 正在合成语音...")
        async def synthesize():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(filename)
        
        asyncio.run(synthesize())
        print("✅ 语音合成完成")
        
        # 检查文件是否存在
        if os.path.exists(filename):
            print(f"✅ 音频文件已生成，大小: {os.path.getsize(filename)} 字节")
            
            # 尝试播放音频
            print("🔊 正在尝试播放音频...")
            try:
                # 使用系统默认播放器播放
                if sys.platform.startswith('win'):
                    print("🔊 使用Windows默认播放器播放...")
                    os.startfile(filename)
                    print("✅ 音频已在默认播放器中打开")
                else:
                    print("⚠️ 非Windows系统，无法自动播放")
                    
            except Exception as e:
                print(f"⚠️ 音频播放失败: {e}")
            
            # 询问用户是否听到声音
            input("\n❓ 您听到了语音播放吗？(按回车继续)")
            
            # 清理临时文件
            if os.path.exists(filename):
                os.unlink(filename)
                print("🗑️  已清理临时文件")
            
            return True
        else:
            print("❌ 音频文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 测试edge-tts时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_local_tts_with_edge():
    """测试本地TTS引擎中的edge-tts"""
    try:
        # 添加路径
        sys.path.append(os.path.join(os.path.dirname(__file__), 'agent', 'tts'))
        
        print("🔍 正在导入LocalTTSEngine...")
        from local_tts import LocalTTSEngine
        
        print("🔧 创建TTS引擎实例...")
        tts_engine = LocalTTSEngine()
        
        print("🔧 初始化edge-tts引擎...")
        if not tts_engine.init_engine("edge-tts"):
            print("❌ edge-tts引擎初始化失败")
            return False
        
        print("✅ edge-tts引擎初始化成功")
        
        # 测试文本
        text = "你好，这是通过LocalTTSEngine播放的edge-tts语音。"
        print(f"📝 测试文本: {text}")
        
        print("🔊 正在播放语音...")
        success = tts_engine.speak(text)
        
        if success:
            print("✅ 语音播放成功")
            return True
        else:
            print("❌ 语音播放失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试LocalTTSEngine中的edge-tts时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 edge-tts测试程序")
    print("=" * 30)
    
    print("\n📍 测试1: 基本edge-tts功能")
    success1 = test_edge_tts_basic()
    
    print("\n📍 测试2: LocalTTSEngine中的edge-tts")
    success2 = test_local_tts_with_edge()
    
    print("\n" + "=" * 30)
    if success1 or success2:
        print("🎉 至少一个测试成功")
    else:
        print("❌ 所有测试都失败了")
        
    print("\n💡 可能的问题和解决方案:")
    print("   1. 确保网络连接正常（edge-tts需要联网）")
    print("   2. 检查系统音频设置和音量")
    print("   3. 确认Windows默认媒体播放器正常工作")
    print("   4. 检查防火墙是否阻止了网络请求")