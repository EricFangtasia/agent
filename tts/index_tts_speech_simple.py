import os
import sys
import time
import tempfile
from pathlib import Path

# 添加IndexTTS模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
index_tts_dir = os.path.join(current_dir, "index-tts")
sys.path.append(index_tts_dir)
sys.path.append(os.path.join(index_tts_dir, "indextts"))

def check_and_install_dependencies():
    """检查并安装必要的依赖"""
    try:
        import torch
        print(f"PyTorch版本: {torch.__version__}")
    except ImportError:
        print("错误：需要安装PyTorch。请运行: pip install torch torchvision torchaudio")
        return False

    try:
        import torchaudio
    except ImportError:
        print("错误：需要安装torchaudio。请运行: pip install torchaudio")
        return False

    try:
        import omegaconf
    except ImportError:
        print("错误：需要安装omegaconf。请运行: pip install omegaconf")
        return False

    return True

def download_model_if_needed(model_dir="index-tts/checkpoints"):
    """检查并下载模型文件"""
    required_files = [
        "config.yaml",
        "bpe.model",
        "gpt.pth",  # 或者可能是 gpt.ckpt
        "bigvgan.pth",  # 或者可能是其他生成器文件
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(model_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"缺少模型文件: {missing_files}")
        print("请下载IndexTTS模型文件到 checkpoints 目录:")
        print("1. 访问 https://huggingface.co/IndexTeam/IndexTTS-2")
        print("2. 下载所有必需的模型文件")
        print("3. 将文件保存到 index-tts/checkpoints 目录")
        return False
    return True

def simple_speak(text, reference_audio_path, output_path=None, verbose=False):
    """
    简单的语音合成函数
    
    Args:
        text: 要合成的文本
        reference_audio_path: 参考音频路径
        output_path: 输出音频路径（可选）
        verbose: 是否显示详细信息
    """
    if not check_and_install_dependencies():
        return False
    
    if not download_model_if_needed():
        return False
    
    if not os.path.exists(reference_audio_path):
        print(f"参考音频文件不存在: {reference_audio_path}")
        return False
    
    try:
        # 导入IndexTTS
        from indextts.infer_v2 import IndexTTS2
        tts = IndexTTS2(
            cfg_path="index-tts/checkpoints/config.yaml",
            model_dir="index-tts/checkpoints",
            use_fp16=False  # CPU模式下使用FP32
        )
    except ImportError:
        try:
            from indextts.infer import IndexTTS
            tts = IndexTTS(
                cfg_path="index-tts/checkpoints/config.yaml",
                model_dir="index-tts/checkpoints",
                use_fp16=False  # CPU模式下使用FP32
            )
        except ImportError:
            print("无法导入IndexTTS，请检查安装")
            return False
    
    # 生成输出路径
    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), f"indextts_output_{int(time.time())}.wav")
    
    print(f"正在生成语音: '{text}'")
    
    try:
        # 执行语音合成
        if hasattr(tts, 'infer_fast'):
            result_path = tts.infer_fast(
                audio_prompt=reference_audio_path,
                text=text,
                output_path=output_path,
                verbose=verbose
            )
        else:
            result_path = tts.infer(
                audio_prompt=reference_audio_path,
                text=text,
                output_path=output_path,
                verbose=verbose
            )
        
        if result_path and os.path.exists(result_path):
            print(f"语音已生成: {result_path}")
            
            # 尝试播放音频
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(result_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.getBusy():
                    pygame.time.Clock().tick(10)
            except Exception as e:
                print(f"播放音频时出错 (可忽略): {e}")
                print(f"音频已保存到: {result_path}")
            
            return True
        else:
            print("语音生成失败")
            return False
            
    except Exception as e:
        print(f"语音合成过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("IndexTTS 简单语音播报")
    print("=" * 40)
    
    # 示例文本和音频
    text = "你好，这是IndexTTS文本转语音的演示。"
    reference_audio = "index-tts/assets/demo.wav"  # 请根据实际情况修改路径
    
    print(f"要合成的文本: {text}")
    print(f"参考音频: {reference_audio}")
    
    # 检查参考音频是否存在
    if not os.path.exists(reference_audio):
        print("\n错误：参考音频文件不存在!")
        print(f"请确保 {reference_audio} 文件存在。")
        print("\n你可能需要:")
        print("1. 下载IndexTTS项目中的示例音频")
        print("2. 或使用你自己的WAV格式音频作为参考")
        return
    
    # 执行语音合成
    success = simple_speak(text, reference_audio, verbose=False)
    
    if success:
        print("\n语音播报完成！")
    else:
        print("\n语音播报失败，请检查上述错误信息。")

if __name__ == "__main__":
    main()