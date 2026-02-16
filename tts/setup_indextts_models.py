#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
整理IndexTTS模型文件到正确位置
"""

import os
import shutil
from pathlib import Path


def setup_models():
    """整理模型文件到正确位置"""
    print("正在整理IndexTTS模型文件到正确位置...")
    print("="*50)
    
    # 定义目标目录
    project_dir = Path(__file__).parent
    target_dir = project_dir / "git" / "index-tts" / "checkpoints"
    
    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 需要的文件列表
    required_files = [
        'config.yaml',
        'gpt.pth',
        'bigvgan.pth',
        's2mel.pth',
        'bpe.model',
        'campplus.onnx'
    ]
    
    # 源目录列表 - 按优先级排序
    source_dirs = [
        project_dir / "checkpoints",  # 本地checkpoints目录
        project_dir / "git" / "IndexTeam" / "IndexTTS-2",  # 另一个可能的目录
        Path.home()  # 用户主目录
    ]
    
    # 查找并复制文件
    found_files = {}
    for req_file in required_files:
        found = False
        for src_dir in source_dirs:
            if src_dir.exists():
                src_file = src_dir / req_file
                if src_file.exists():
                    found_files[req_file] = src_file
                    print(f"✅ 找到 {req_file} 在 {src_dir}")
                    found = True
                    break
            # 如果直接在源目录中没找到，递归搜索
            if not found:
                for root, dirs, files in os.walk(src_dir):
                    if req_file in files:
                        src_file = Path(root) / req_file
                        found_files[req_file] = src_file
                        print(f"✅ 找到 {req_file} 在 {src_file.parent}")
                        found = True
                        break
            if found:
                break
    
    print("\n正在复制文件到目标目录...")
    missing_files = []
    for req_file in required_files:
        if req_file in found_files:
            src_path = found_files[req_file]
            target_path = target_dir / req_file
            
            # 如果目标文件已存在，跳过
            if target_path.exists():
                print(f"⚠️  {req_file} 已存在于目标目录，跳过")
            else:
                try:
                    shutil.copy2(src_path, target_path)
                    print(f"✅ {req_file} 已复制到 {target_path}")
                except Exception as e:
                    print(f"❌ 复制 {req_file} 时出错: {e}")
                    missing_files.append(req_file)
        else:
            print(f"❌ 未找到 {req_file}")
            missing_files.append(req_file)
    
    print("\n" + "="*50)
    if missing_files:
        print(f"❌ 仍有 {len(missing_files)} 个文件缺失: {', '.join(missing_files)}")
        print("\n你需要获取以下文件:")
        print("方法1 (推荐国内用户):")
        print("   pip install modelscope")
        print("   modelscope download --model IndexTeam/IndexTTS-2 --local_dir git/index-tts/checkpoints")
        print("\n方法2 (推荐国外用户):")
        print("   pip install huggingface_hub")
        print("   hf download IndexTeam/IndexTTS-2 --local-dir=git/index-tts/checkpoints")
        print("   # 或使用镜像: HF_ENDPOINT=https://hf-mirror.com hf download IndexTeam/IndexTTS-2 --local-dir=git/index-tts/checkpoints")
        return False
    else:
        print("✅ 所有模型文件已整理到正确位置！")
        print(f"目标目录: {target_dir}")
        return True


def check_models():
    """检查目标目录中的模型文件"""
    project_dir = Path(__file__).parent
    target_dir = project_dir / "git" / "index-tts" / "checkpoints"
    
    if not target_dir.exists():
        print(f"❌ 目标目录不存在: {target_dir}")
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
    for req_file in required_files:
        file_path = target_dir / req_file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {req_file} 存在 ({size} bytes)")
        else:
            print(f"❌ {req_file} 缺失")
            missing_files.append(req_file)
    
    return len(missing_files) == 0


if __name__ == "__main__":
    print("IndexTTS模型文件整理工具")
    print("="*50)
    
    if check_models():
        print("\n✅ 所有必需的模型文件已存在于目标目录！")
        print("你现在可以直接运行声音克隆演示。")
    else:
        print("\n开始整理模型文件...")
        success = setup_models()
        
        if success:
            print("\n✅ 模型文件整理完成！")
            print("你现在可以运行声音克隆演示了。")
        else:
            print("\n❌ 模型文件整理未完成，请手动下载缺失的文件。")