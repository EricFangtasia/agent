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
    required_packages = [
        "torch",
        "torchaudio", 
        "omegaconf",
        "librosa",
        "transformers",
        "numpy",
        "safetensors"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少以下Python包: {missing_packages}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    return True

def check_model_files():
    """检查模型文件是否完整"""
    model_dir = "index-tts/checkpoints"
    required_files = [
        "config.yaml",
        "bpe.model",        # BPE模型文件
        "gpt.pth",          # GPT模型文件
        "bigvgan.pth",      # BigVGAN声码器文件
        "s2mel.pth",        # S2Mel模型文件
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(model_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"缺少模型文件: {missing_files}")
        return False
    else:
        print("✓ 所需模型文件已找到")
        return True

def download_model_instructions():
    """提供模型下载说明"""
    print("\n" + "="*60)
    print("模型文件下载说明:")
    print("="*60)
    print("IndexTTS需要以下模型文件才能运行:")
    print("1. config.yaml          - 模型配置文件")
    print("2. bpe.model            - BPE分词模型")
    print("3. gpt.pth              - GPT模型文件")
    print("4. bigvgan.pth          - BigVGAN声码器模型")
    print("5. s2mel.pth            - S2Mel模型文件")
    print("\n下载方法:")
    print("方法1 (Hugging Face):")
    print("  访问: https://huggingface.co/IndexTeam/IndexTTS-2")
    print("  下载所有.bin和.pth文件，以及config.yaml和bpe.model")
    print("\n方法2 (ModelScope):")
    print("  访问: https://modelscope.cn/models/IndexTeam/IndexTTS-2")
    print("  下载所有模型文件")
    print("\n将下载的文件放入: git/index-tts/checkpoints/ 目录")
    print("="*60)

def simple_speak(text, output_path=None, verbose=False):
    """
    简单的语音合成函数（使用内置参考音频）
    
    Args:
        text: 要合成的文本
        output_path: 输出音频路径（可选）
        verbose: 是否显示详细信息
    """
    if not check_and_install_dependencies():
        return False
    
    if not check_model_files():
        download_model_instructions()
        return False
    
    # 尝试导入IndexTTS
    try:
        # 尝试导入IndexTTS2（较新版本）
        from indextts.infer_v2 import IndexTTS2
        tts_class = IndexTTS2
        print("✓ 使用IndexTTS2模型")
    except ImportError:
        try:
            # 如果没有IndexTTS2，则使用IndexTTS（较早版本）
            from indextts.infer import IndexTTS
            tts_class = IndexTTS
            print("✓ 使用IndexTTS模型")
        except ImportError:
            print("错误：无法导入IndexTTS或IndexTTS2，请确保IndexTTS已正确安装")
            return False
    
    print("正在初始化IndexTTS...")
    
    try:
        # 初始化TTS模型
        tts = tts_class(
            cfg_path="index-tts/checkpoints/config.yaml",
            model_dir="index-tts/checkpoints",
            use_fp16=False  # CPU模式下使用FP32
        )
        print("✓ IndexTTS初始化成功")
    except Exception as e:
        print(f"✗ 初始化IndexTTS失败: {e}")
        return False
    
    # 生成输出路径
    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), f"indextts_output_{int(time.time())}.wav")
    
    print(f"正在生成语音: '{text}'")
    
    # 使用内置的参考音频或默认音频
    # 如果没有参考音频，我们先尝试使用项目中的音频作为参考
    reference_audio = None
    possible_refs = [
        "index-tts/assets/demo.wav",  # 如果有提供的话
        "index-tts/examples/ref_audio.wav",  # 示例参考音频
    ]
    
    for ref_path in possible_refs:
        if os.path.exists(ref_path):
            reference_audio = ref_path
            break
    
    if reference_audio is None:
        print("⚠ 没有找到合适的参考音频，这将影响语音合成质量。")
        print("请准备一个参考音频文件（如WAV格式）以获得最佳效果。")
        return False
    
    try:
        # 执行语音合成
        if hasattr(tts, 'infer_fast'):
            # 使用快速推理
            result_path = tts.infer_fast(
                audio_prompt=reference_audio,
                text=text,
                output_path=output_path,
                verbose=verbose
            )
        else:
            # 使用普通推理
            result_path = tts.infer(
                audio_prompt=reference_audio,
                text=text,
                output_path=output_path,
                verbose=verbose
            )
        
        if result_path and os.path.exists(result_path):
            print(f"✓ 语音已生成: {result_path}")
            
            # 尝试播放音频
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(result_path)
                pygame.mixer.music.play()
                print("正在播放生成的语音...")
                while pygame.mixer.music.getBusy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.quit()
                print("播放完成")
            except Exception as e:
                print(f"播放音频时出错 (可忽略): {e}")
                print(f"音频已保存到: {result_path}")
            
            return True
        else:
            print("✗ 语音生成失败")
            return False
            
    except Exception as e:
        print(f"✗ 语音合成过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("IndexTTS 语音合成演示")
    print("=" * 50)
    
    # 检查是否在正确的目录下
    if not os.path.exists("index-tts"):
        print("错误：未找到index-tts目录，请确保在正确的项目路径下运行此脚本")
        return
    
    print("提示：在使用前请确保已下载模型文件到 index-tts/checkpoints 目录")
    
    # 检查模型文件
    if not check_model_files():
        download_model_instructions()
        return
    
    # 示例文本
    text = "你好，这是IndexTTS文本转语音的演示。"
    
    # 提示用户需要参考音频
    print(f"\n要合成的文本: {text}")
    print("注意：IndexTTS需要参考音频来学习语音特征。")
    print("请准备一个高质量的参考音频（如WAV格式）作为语音风格的参考。")
    
    # 执行语音合成
    success = simple_speak(text, verbose=False)
    
    if success:
        print("\n✓ 语音合成完成！")
    else:
        print("\n✗ 语音合成失败，请检查上述错误信息。")

if __name__ == "__main__":
    main()