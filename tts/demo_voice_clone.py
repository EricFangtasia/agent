#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IndexTTS声音克隆演示脚本
此脚本演示如何使用IndexTTS进行声音克隆
"""

import os
import sys
from agent.tts.strategies.indextts_strategy import IndexTTSStrategy


def main():
    print("IndexTTS声音克隆演示")
    print("="*50)
    
    # 首先检查模型是否已下载
    checkpoints_dir = os.path.join(os.path.dirname(__file__), 'git', 'index-tts', 'checkpoints')
    if not os.path.exists(checkpoints_dir):
        print(f"❌ IndexTTS 检查点目录不存在: {checkpoints_dir}")
        print("💡 请确保已克隆index-tts仓库并下载模型文件")
        return
    
    config_path = os.path.join(checkpoints_dir, 'config.yaml')
    if not os.path.exists(config_path):
        print(f"❌ IndexTTS 配置文件未找到: {config_path}")
        return
    
    # 获取参考音频路径
    reference_audio_path = input("请输入参考音频文件路径（用于声音克隆，3-5秒清晰音频即可）: ").strip()
    if not reference_audio_path or not os.path.exists(reference_audio_path):
        print("❌ 参考音频文件不存在，请检查路径是否正确")
        return
    
    # 初始化IndexTTS策略
    tts_strategy = IndexTTSStrategy(reference_audio_path=reference_audio_path)
    
    # 初始化引擎
    print("\n正在初始化IndexTTS引擎...")
    if not tts_strategy.initialize():
        print("❌ IndexTTS引擎初始化失败")
        return
    
    print("✅ IndexTTS引擎初始化成功！")
    
    # 循环演示
    while True:
        print("\n" + "="*50)
        print("1. 输入文本并生成声音克隆语音")
        print("2. 使用默认声音（不使用声音克隆）")
        print("3. 退出")
        
        choice = input("请选择操作 (1-3): ").strip()
        
        if choice == "1":
            text = input("\n请输入要转换为语音的文本: ").strip()
            if not text:
                print("❌ 文本不能为空")
                continue
                
            print("正在生成声音克隆语音...")
            output_file = tts_strategy.speak_with_voice_clone(text, reference_audio_path)
            
            if output_file:
                print(f"✅ 语音已生成: {output_file}")
                print("语音文件已保存，您可以使用任意音频播放器播放该文件")
            else:
                print("❌ 语音生成失败")
                
        elif choice == "2":
            text = input("\n请输入要转换为语音的文本: ").strip()
            if not text:
                print("❌ 文本不能为空")
                continue
                
            print("正在生成默认语音...")
            output_file = tts_strategy.speak(text)
            
            if output_file:
                print(f"✅ 语音已生成: {output_file}")
                print("语音文件已保存，您可以使用任意音频播放器播放该文件")
            else:
                print("❌ 语音生成失败")
                
        elif choice == "3":
            print("感谢使用IndexTTS声音克隆演示！")
            break
        else:
            print("❌ 无效选择，请重新输入")


def quick_demo():
    """快速演示函数，用于直接调用"""
    print("IndexTTS声音克隆快速演示")
    print("="*50)
    
    # 检查模型
    checkpoints_dir = os.path.join(os.path.dirname(__file__), 'git', 'index-tts', 'checkpoints')
    if not os.path.exists(checkpoints_dir):
        print(f"❌ IndexTTS 检查点目录不存在: {checkpoints_dir}")
        print("💡 请确保已克隆index-tts仓库并下载模型文件")
        return False
    
    config_path = os.path.join(checkpoints_dir, 'config.yaml')
    if not os.path.exists(config_path):
        print(f"❌ IndexTTS 配置文件未找到: {config_path}")
        return False
    
    # 这里需要用户指定参考音频
    reference_audio = input("请输入参考音频路径: ").strip()
    if not reference_audio or not os.path.exists(reference_audio):
        print("❌ 参考音频文件不存在")
        return False
    
    text = input("请输入要转换的文本: ").strip()
    if not text:
        print("❌ 文本不能为空")
        return False
    
    # 初始化并生成语音
    tts_strategy = IndexTTSStrategy(reference_audio_path=reference_audio)
    if not tts_strategy.initialize():
        print("❌ IndexTTS引擎初始化失败")
        return False
    
    print("正在生成语音...")
    output_file = tts_strategy.speak_with_voice_clone(text, reference_audio)
    
    if output_file:
        print(f"✅ 语音已生成: {output_file}")
        print("语音文件已保存，您可以使用任意音频播放器播放该文件")
        return True
    else:
        print("❌ 语音生成失败")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_demo()
    else:
        main()