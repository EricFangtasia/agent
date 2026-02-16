#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IndexTTS声音克隆运行脚本
此脚本检查模型完整性并运行声音克隆功能
"""

import os
import sys
from pathlib import Path


def check_model_files():
    """检查模型文件是否完整"""
    project_dir = Path(__file__).parent
    checkpoints_dir = project_dir / "git" / "index-tts" / "checkpoints"
    
    if not checkpoints_dir.exists():
        print(f"❌ 检查点目录不存在: {checkpoints_dir}")
        return False
    
    required_files = [
        'config.yaml',
        'gpt.pth',
        'bigvgan.pth',
        's2mel.pth',
        'bpe.model',
        'campplus.onnx'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = checkpoints_dir / file
        if not file_path.exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少模型文件: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 所有模型文件完整")
        return True


def run_demo():
    """运行演示"""
    if not check_model_files():
        print("\n❌ 模型文件不完整，无法运行演示")
        print("\n请先下载缺失的模型文件:")
        print("方法1 (推荐国内用户):")
        print("   pip install modelscope")
        print("   modelscope download --model IndexTeam/IndexTTS-2 --local_dir ./temp_model")
        print("   # 然后将缺失文件复制到 git/index-tts/checkpoints 目录")
        print("\n方法2 (推荐国外用户):")
        print("   pip install huggingface_hub")
        print("   hf download IndexTeam/IndexTTS-2 --local-dir=./temp_model")
        print("   # 然后将缺失文件复制到 git/index-tts/checkpoints 目录")
        return False
    
    print("\n✅ 模型文件完整，可以运行声音克隆演示")
    print("\n运行演示的命令:")
    print("   python simple_voice_clone_demo.py")
    print("\n或者运行带录音功能的演示:")
    print("   python voice_clone_with_recording.py")
    
    run_now = input("\n是否现在运行简单演示? (y/N): ").strip().lower()
    if run_now in ['y', 'yes']:
        import subprocess
        try:
            subprocess.run([sys.executable, "simple_voice_clone_demo.py"])
        except Exception as e:
            print(f"❌ 运行演示时出错: {e}")
    
    return True


if __name__ == "__main__":
    print("IndexTTS声音克隆运行检查")
    print("="*50)
    
    run_demo()