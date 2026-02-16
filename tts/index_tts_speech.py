import os
import sys
import time
import tempfile
import torch
import torchaudio
from pathlib import Path

# 添加IndexTTS模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
index_tts_dir = os.path.join(current_dir, "index-tts")
sys.path.append(index_tts_dir)
sys.path.append(os.path.join(index_tts_dir, "indextts"))

try:
    # 尝试导入IndexTTS2（较新版本）
    from indextts.infer_v2 import IndexTTS2
    IndexTTS_class = IndexTTS2
    print("使用IndexTTS2模型")
except ImportError:
    try:
        # 如果没有IndexTTS2，则使用IndexTTS（较早版本）
        from indextts.infer import IndexTTS
        IndexTTS_class = IndexTTS
        print("使用IndexTTS模型")
    except ImportError:
        print("错误：无法导入IndexTTS或IndexTTS2，请确保IndexTTS已正确安装")
        sys.exit(1)

def check_model_files(model_dir):
    """检查模型文件是否存在"""
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
        print(f"缺少以下模型文件: {missing_files}")
        print(f"请确保模型文件位于 {model_dir} 目录中")
        return False
    return True

def play_audio_with_pygame(audio_path):
    """使用pygame播放音频"""
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
        return True
    except Exception as e:
        print(f"使用pygame播放失败: {e}")
        return False

def play_audio_with_powershell(audio_path):
    """在Windows上使用PowerShell播放音频"""
    try:
        import subprocess
        subprocess.run([
            "powershell", 
            "-c", 
            f"(New-Object Media.SoundPlayer '{audio_path}').PlaySync();"
        ], check=True)
        return True
    except Exception as e:
        print(f"使用PowerShell播放失败: {e}")
        return False

def speak_text(text, reference_audio_path=None, output_path=None, model_dir="index-tts/checkpoints", verbose=False):
    """
    使用IndexTTS进行语音播报
    
    Args:
        text: 要播报的文本
        reference_audio_path: 参考音频路径（可选）
        output_path: 输出音频路径（可选）
        model_dir: 模型目录
        verbose: 是否输出详细信息
    """
    print("正在初始化IndexTTS...")
    
    # 检查模型文件
    if not check_model_files(model_dir):
        print("模型文件不完整，无法继续执行。请下载完整的模型文件。")
        return False
    
    # 初始化TTS模型
    try:
        tts = IndexTTS_class(
            cfg_path=os.path.join(model_dir, "config.yaml"),
            model_dir=model_dir,
            use_fp16=False,  # 使用CPU时建议设置为False
        )
        print("IndexTTS初始化成功")
    except Exception as e:
        print(f"初始化IndexTTS失败: {e}")
        return False
    
    # 如果没有提供参考音频，则尝试使用默认的
    if reference_audio_path is None or not os.path.exists(reference_audio_path):
        # 尝试寻找默认参考音频
        possible_refs = [
            os.path.join(model_dir, "default_ref.wav"),
            os.path.join(model_dir, "demo.wav"),
            os.path.join(index_tts_dir, "assets", "demo.wav"),
        ]
        
        for ref_path in possible_refs:
            if os.path.exists(ref_path):
                reference_audio_path = ref_path
                print(f"使用默认参考音频: {ref_path}")
                break
    
    if reference_audio_path is None or not os.path.exists(reference_audio_path):
        print("警告：未提供有效的参考音频，这可能会影响语音合成质量。")
        print("请准备一个参考音频文件（如WAV格式）以获得最佳效果。")
        return False
    
    # 生成输出路径
    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), f"indextts_output_{int(time.time())}.wav")
    
    # 执行语音合成
    print(f"正在生成语音: '{text}'")
    try:
        # 根据模型版本调用不同的方法
        if hasattr(tts, 'infer_fast'):
            # 使用快速推理
            result_path = tts.infer_fast(
                audio_prompt=reference_audio_path,
                text=text,
                output_path=output_path,
                verbose=verbose
            )
        else:
            # 使用普通推理
            result_path = tts.infer(
                audio_prompt=reference_audio_path,
                text=text,
                output_path=output_path,
                verbose=verbose
            )
        
        if result_path:
            print(f"语音已生成: {result_path}")
            
            # 播放生成的音频
            print("正在播放生成的语音...")
            
            # 尝试使用pygame播放
            if not play_audio_with_pygame(result_path):
                # 如果pygame失败，尝试PowerShell（仅Windows）
                if sys.platform.startswith('win'):
                    if not play_audio_with_powershell(result_path):
                        print("无法播放音频，请手动播放文件:", result_path)
                else:
                    print("无法播放音频，请手动播放文件:", result_path)
            
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
    """主函数，演示如何使用IndexTTS进行语音播报"""
    print("IndexTTS语音播报演示")
    print("=" * 50)
    
    # 检查是否在正确的目录下
    if not os.path.exists("index-tts"):
        print("错误：未找到index-tts目录，请确保在正确的项目路径下运行此脚本")
        return
    
    # 示例文本
    text = "你好，这是IndexTTS语音合成系统的演示。"
    
    # 参考音频路径 - 请替换为你自己的参考音频
    reference_audio = "index-tts/assets/demo.wav"  # 根据实际情况修改
    
    # 如果参考音频不存在，提示用户
    if not os.path.exists(reference_audio):
        print(f"参考音频不存在: {reference_audio}")
        print("请下载或准备一个参考音频文件。")
        print("你也可以使用其他音频文件作为参考。")
        return
    
    # 执行语音播报
    success = speak_text(
        text=text,
        reference_audio_path=reference_audio,
        model_dir="index-tts/checkpoints",
        verbose=False
    )
    
    if success:
        print("语音播报完成！")
    else:
        print("语音播报失败，请检查错误信息。")

if __name__ == "__main__":
    main()