#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接测试IndexTTS的脚本
"""

import os
import sys
import tempfile

def test_indextts_direct():
    """直接测试IndexTTS引擎"""
    try:
        print("🔍 正在设置IndexTTS环境...")
        
        # 添加IndexTTS路径到sys.path
        indextts_path = os.path.join(os.path.dirname(__file__), 'git', 'index-tts')
        indextts_path = os.path.abspath(indextts_path)
        if os.path.exists(indextts_path) and indextts_path not in sys.path:
            sys.path.append(indextts_path)
            print(f"✅ 已添加IndexTTS路径: {indextts_path}")
        
        print("🔍 正在导入IndexTTS模块...")
        from indextts.infer_v2 import IndexTTS2
        
        # 构建模型和配置路径
        checkpoints_dir = os.path.join(indextts_path, 'checkpoints')
        cfg_path = os.path.join(checkpoints_dir, 'config.yaml')
        model_dir = checkpoints_dir
        
        print(f"📁 配置文件路径: {cfg_path}")
        print(f"📁 模型目录路径: {model_dir}")
        
        if not os.path.exists(cfg_path):
            print(f"❌ 配置文件不存在: {cfg_path}")
            return False
            
        if not os.path.exists(model_dir):
            print(f"❌ 模型目录不存在: {model_dir}")
            return False
            
        print("🔍 正在初始化IndexTTS引擎...")
        
        # 初始化 IndexTTS2 引擎
        engine = IndexTTS2(cfg_path=cfg_path, model_dir=model_dir)
        print("✅ IndexTTS引擎初始化成功！")
        
        # 测试文本列表
        test_texts = [
            "你好，我是IndexTTS语音合成引擎。",
            "今天天气怎么样？",
            "欢迎使用IndexTTS语音合成系统。"
        ]
        
        print("\n🔊 开始测试语音合成...")
        for i, text in enumerate(test_texts, 1):
            try:
                # 创建临时文件
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    filename = tmp_file.name
                
                print(f"\n[{i}/{len(test_texts)}] 合成文本: {text}")
                # 调用 IndexTTS2 的 infer 方法生成语音
                engine.infer(
                    text=text,
                    output_path=filename,
                    sdp_ratio=0.2,
                    noise_scale=0.6,
                    noise_scale_w=0.8,
                    length_scale=1.0,
                    speaker_id=0
                )
                
                print(f"✅ 文本{i}合成成功，保存到: {filename}")
                
                # 清理临时文件
                if os.path.exists(filename):
                    os.unlink(filename)
                    print(f"🗑️  已清理临时文件: {filename}")
                    
            except Exception as e:
                print(f"❌ 合成文本{i}时发生错误: {e}")
                
        print("\n🎉 IndexTTS直接测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试IndexTTS时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 IndexTTS直接测试程序")
    print("=" * 30)
    
    success = test_indextts_direct()
    
    if success:
        print("\n✅ 所有测试已完成")
    else:
        print("\n❌ 测试过程中出现错误")
        sys.exit(1)