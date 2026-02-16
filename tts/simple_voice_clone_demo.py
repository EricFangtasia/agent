#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IndexTTS声音克隆简单演示脚本
此脚本演示如何使用IndexTTS进行声音克隆
"""

import os
import sys
from agent.tts.strategies.indextts_strategy import IndexTTSStrategy


def check_model_files(checkpoints_dir):
    """检查模型文件是否存在"""
    required_files = [
        'config.yaml',
        'gpt.pth',
        'bigvgan.pth',
        's2mel.pth',
        'bpe.model',
        'campplus.onnx',
        'wav2vec2bert_stats.pt'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(checkpoints_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    return missing_files


def main():
    print("IndexTTS声音克隆演示")
    print("="*50)
    
    # 检查git/index-tts目录是否存在
    indextts_dir = os.path.join(os.path.dirname(__file__), 'git', 'index-tts')
    if not os.path.exists(indextts_dir):
        print(f"❌ IndexTTS 代码目录不存在: {indextts_dir}")
        print("💡 请先克隆IndexTTS代码仓库:")
        print("   git clone https://github.com/index-tts/index-tts.git git/index-tts")
        return False
    
    # 检查模型是否已下载
    checkpoints_dir = os.path.join(os.path.dirname(__file__), 'git', 'index-tts', 'checkpoints')
    if not os.path.exists(checkpoints_dir):
        print(f"❌ IndexTTS 检查点目录不存在: {checkpoints_dir}")
        print("💡 请先下载IndexTTS模型文件到该目录")
        print("\n下载模型方法:")
        print("方法1 (国内用户推荐):")
        print("   pip install modelscope")
        print("   modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints")
        print("\n方法2 (国外用户):")
        print("   pip install huggingface_hub")
        print("   hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints")
        print("   # 或使用镜像: HF_ENDPOINT=https://hf-mirror.com hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints")
        return False
    
    # 检查必要的模型文件是否存在
    missing_files = check_model_files(checkpoints_dir)
    if missing_files:
        print(f"❌ 模型文件不完整，缺少以下文件: {', '.join(missing_files)}")
        print("💡 请重新下载模型文件")
        print("\n下载模型方法:")
        print("方法1 (国内用户推荐):")
        print("   pip install modelscope")
        print(f"   cd {indextts_dir}")
        print("   modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints")
        print("\n方法2 (国外用户):")
        print("   pip install huggingface_hub")
        print(f"   cd {indextts_dir}")
        print("   hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints")
        print("   # 或使用镜像: HF_ENDPOINT=https://hf-mirror.com hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints")
        return False
    
    config_path = os.path.join(checkpoints_dir, 'config.yaml')
    if not os.path.exists(config_path):
        print(f"❌ IndexTTS 配置文件未找到: {config_path}")
        return False
    
    # 获取参考音频路径
    reference_audio_path = input("请输入参考音频文件路径（用于声音克隆，3-5秒清晰音频即可）: ").strip()
    if not reference_audio_path or not os.path.exists(reference_audio_path):
        print("❌ 参考音频文件不存在，请检查路径是否正确")
        return False
    
    # 初始化IndexTTS策略
    print("\n正在初始化IndexTTS引擎...")
    tts_strategy = IndexTTSStrategy(reference_audio_path=reference_audio_path)
    
    if not tts_strategy.initialize():
        print("❌ IndexTTS引擎初始化失败")
        return False
    
    print("✅ IndexTTS引擎初始化成功！")
    
    # 获取用户要转换的文本
    text = input("\n请输入要转换为语音的文本: ").strip()
    if not text:
        print("❌ 文本不能为空")
        return False
    
    print("正在生成声音克隆语音...")
    
    # 使用声音克隆生成语音
    output_file = tts_strategy.speak_with_voice_clone(text, reference_audio_path)
    
    if output_file:
        print(f"✅ 语音已生成: {output_file}")
        print("语音文件已保存，您可以使用任意音频播放器播放该文件")
        return True
    else:
        print("❌ 语音生成失败")
        return False


def batch_demo():
    """批量演示声音克隆功能"""
    print("IndexTTS声音克隆批量演示")
    print("="*50)
    
    # 检查git/index-tts目录是否存在
    indextts_dir = os.path.join(os.path.dirname(__file__), 'git', 'index-tts')
    if not os.path.exists(indextts_dir):
        print(f"❌ IndexTTS 代码目录不存在: {indextts_dir}")
        print("💡 请先克隆IndexTTS代码仓库:")
        print("   git clone https://github.com/index-tts/index-tts.git git/index-tts")
        return False
    
    # 检查模型是否已下载
    checkpoints_dir = os.path.join(os.path.dirname(__file__), 'git', 'index-tts', 'checkpoints')
    if not os.path.exists(checkpoints_dir):
        print(f"❌ IndexTTS 检查点目录不存在: {checkpoints_dir}")
        print("💡 请先下载IndexTTS模型文件到该目录")
        print("\n下载模型方法:")
        print("方法1 (国内用户推荐):")
        print("   pip install modelscope")
        print(f"   cd {indextts_dir}")
        print("   modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints")
        print("\n方法2 (国外用户):")
        print("   pip install huggingface_hub")
        print(f"   cd {indextts_dir}")
        print("   hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints")
        print("   # 或使用镜像: HF_ENDPOINT=https://hf-mirror.com hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints")
        return False
    
    # 检查必要的模型文件是否存在
    missing_files = check_model_files(checkpoints_dir)
    if missing_files:
        print(f"❌ 模型文件不完整，缺少以下文件: {', '.join(missing_files)}")
        print("💡 请重新下载模型文件")
        print("\n下载模型方法:")
        print("方法1 (国内用户推荐):")
        print("   pip install modelscope")
        print(f"   cd {indextts_dir}")
        print("   modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints")
        print("\n方法2 (国外用户):")
        print("   pip install huggingface_hub")
        print(f"   cd {indextts_dir}")
        print("   hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints")
        print("   # 或使用镜像: HF_ENDPOINT=https://hf-mirror.com hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints")
        return False
    
    config_path = os.path.join(checkpoints_dir, 'config.yaml')
    if not os.path.exists(config_path):
        print(f"❌ IndexTTS 配置文件未找到: {config_path}")
        return False
    
    # 获取参考音频路径
    reference_audio_path = input("请输入参考音频文件路径（用于声音克隆，3-5秒清晰音频即可）: ").strip()
    if not reference_audio_path or not os.path.exists(reference_audio_path):
        print("❌ 参考音频文件不存在，请检查路径是否正确")
        return False
    
    # 初始化IndexTTS策略
    print("\n正在初始化IndexTTS引擎...")
    tts_strategy = IndexTTSStrategy(reference_audio_path=reference_audio_path)
    
    if not tts_strategy.initialize():
        print("❌ IndexTTS引擎初始化失败")
        return False
    
    print("✅ IndexTTS引擎初始化成功！")
    
    # 预设的文本列表
    demo_texts = [
        "你好，这是使用我的声音生成的语音。",
        "IndexTTS的声音克隆功能非常强大。",
        "只需要几秒钟的参考音频，就能复刻我的声音。",
        "现在你可以用我的声音说任何你想说的话。",
        "感谢使用IndexTTS声音克隆功能。"
    ]
    
    print(f"\n将为您生成 {len(demo_texts)} 段语音...")
    
    for i, text in enumerate(demo_texts, 1):
        print(f"\n正在生成第 {i} 段语音: {text}")
        
        # 为每段文本生成一个唯一的输出文件
        import tempfile
        import os
        output_file = os.path.join(tempfile.gettempdir(), f"indextts_demo_{i}.wav")
        
        # 使用声音克隆生成语音
        result = tts_strategy.save_to_file(text, output_file, reference_audio_path)
        
        if result:
            print(f"✅ 第 {i} 段语音已生成: {result}")
        else:
            print(f"❌ 第 {i} 段语音生成失败")
    
    print(f"\n✅ 所有语音已生成完成！文件保存在临时目录中。")
    return True


if __name__ == "__main__":
    print("请选择演示模式:")
    print("1. 单次声音克隆演示")
    print("2. 批量声音克隆演示")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        success = main()
    elif choice == "2":
        success = batch_demo()
    else:
        print("无效选择，使用默认模式（单次演示）")
        success = main()
    
    if success:
        print("\n🎉 演示完成！")
    else:
        print("\n❌ 演示失败！")