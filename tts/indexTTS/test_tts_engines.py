#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试不同TTS引擎的脚本
"""

import os
import sys
import tempfile

# 添加项目路径到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent', 'tts'))

def test_tts_engines():
    """测试各种TTS引擎"""
    try:
        # 导入本地TTS引擎
        from local_tts import LocalTTSEngine
        
        print("🔍 检测可用的TTS引擎...")
        
        # 创建TTS引擎实例
        tts_engine = LocalTTSEngine()
        available_engines = tts_engine.list_available_engines()
        
        print(f"✅ 可用的TTS引擎: {', '.join(available_engines)}")
        
        # 测试文本
        test_text = "你好，这是语音合成测试。"
        
        # 按优先级测试引擎
        engine_priority = ["pyttsx3", "edge-tts", "coqui", "melotts", "indextts"]
        
        for engine_type in engine_priority:
            if engine_type in available_engines:
                print(f"\n🔍 正在测试 {engine_type} 引擎...")
                try:
                    # 初始化引擎
                    if tts_engine.init_engine(engine_type):
                        print(f"✅ {engine_type} 引擎初始化成功")
                        
                        # 测试语音播放
                        print(f"🔊 播放测试文本: {test_text}")
                        success = tts_engine.speak(test_text)
                        
                        if success:
                            print(f"✅ {engine_type} 语音播放成功")
                            return engine_type  # 返回第一个成功的引擎
                        else:
                            print(f"❌ {engine_type} 语音播放失败")
                    else:
                        print(f"❌ {engine_type} 引擎初始化失败")
                except Exception as e:
                    print(f"❌ 测试 {engine_type} 时发生错误: {e}")
            else:
                print(f"⚠️  {engine_type} 引擎不可用")
        
        print("\n❌ 所有TTS引擎都无法正常工作")
        return None
        
    except Exception as e:
        print(f"❌ 测试TTS引擎时发生错误: {e}")
        return None

def test_indextts_specifically():
    """专门测试IndexTTS引擎"""
    try:
        print("\n🔍 专门测试IndexTTS引擎...")
        
        # 添加IndexTTS路径到sys.path
        indextts_path = os.path.join(os.path.dirname(__file__), 'git', 'index-tts')
        indextts_path = os.path.abspath(indextts_path)
        if os.path.exists(indextts_path) and indextts_path not in sys.path:
            sys.path.append(indextts_path)
            print(f"✅ 已添加IndexTTS路径: {indextts_path}")
        
        # 检查配置文件
        checkpoints_dir = os.path.join(indextts_path, 'checkpoints')
        cfg_path = os.path.join(checkpoints_dir, 'config.yaml')
        
        if not os.path.exists(cfg_path):
            print(f"❌ IndexTTS配置文件不存在: {cfg_path}")
            return False
            
        print(f"✅ IndexTTS配置文件存在: {cfg_path}")
        
        # 尝试导入IndexTTS
        try:
            from indextts.infer_v2 import IndexTTS2
            print("✅ 成功导入IndexTTS模块")
            
            # 初始化IndexTTS
            tts = IndexTTS2(cfg_path=cfg_path, model_dir=checkpoints_dir)
            print("✅ IndexTTS初始化成功")
            
            # 测试文本合成
            test_text = "你好，这是IndexTTS语音合成测试。"
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_path = tmp_file.name
            
            print(f"🔊 合成文本: {test_text}")
            tts.infer(
                text=test_text,
                output_path=output_path,
                sdp_ratio=0.2,
                noise_scale=0.6,
                noise_scale_w=0.8,
                length_scale=1.0,
                speaker_id=0
            )
            
            print(f"✅ 语音合成成功，保存到: {output_path}")
            
            # 清理临时文件
            if os.path.exists(output_path):
                os.unlink(output_path)
                print("🗑️  已清理临时文件")
            
            return True
            
        except ImportError as e:
            print(f"❌ 导入IndexTTS失败，可能是依赖版本问题: {e}")
            print("💡 建议:")
            print("   1. 使用uv工具安装IndexTTS指定的依赖版本")
            print("   2. 或者手动将transformers降级到4.52.1版本")
            return False
        except Exception as e:
            print(f"❌ IndexTTS测试失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 测试IndexTTS时发生错误: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TTS引擎测试程序")
    print("=" * 30)
    
    # 测试常规TTS引擎
    working_engine = test_tts_engines()
    
    if working_engine:
        print(f"\n🎉 推荐使用 {working_engine} 作为TTS引擎")
    else:
        print("\n⚠️  没有找到可以正常工作的TTS引擎")
        
        # 询问是否要专门测试IndexTTS
        choice = input("\n是否要专门测试IndexTTS? (y/n): ").strip().lower()
        if choice == 'y':
            success = test_indextts_specifically()
            if success:
                print("\n🎉 IndexTTS测试成功!")
            else:
                print("\n❌ IndexTTS测试失败")
    
    print("\n💡 建议:")
    print("   1. 如果需要使用IndexTTS，请确保依赖版本正确")
    print("   2. 可以使用pyttsx3作为备用方案，它最稳定且无需额外配置")
    print("   3. edge-tts需要网络连接，但效果较好")