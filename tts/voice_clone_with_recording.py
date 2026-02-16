#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IndexTTS声音克隆与录音脚本
此脚本允许用户录制自己的声音，然后用该声音克隆生成指定文本的语音
"""

import os
import sys
import tempfile
import wave
import pyaudio
from agent.tts.strategies.indextts_strategy import IndexTTSStrategy


def record_audio(duration=5, filename=None):
    """
    录制音频
    :param duration: 录制时长（秒）
    :param filename: 保存的文件名
    :return: 文件路径
    """
    if filename is None:
        filename = os.path.join(tempfile.gettempdir(), f"recorded_voice_{os.getpid()}.wav")
    
    # 录音参数
    chunk = 1024  # 每个缓冲区的帧数
    FORMAT = pyaudio.paInt16  # 采样位数
    CHANNELS = 1  # 单声道
    RATE = 16000  # 采样率（IndexTTS推荐16kHz）
    
    p = pyaudio.PyAudio()
    
    print(f"开始录制 {duration} 秒...")
    
    # 打开音频流
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=chunk
    )
    
    frames = []
    
    # 录制音频
    for i in range(0, int(RATE / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    print("录制完成！")
    
    # 停止录音
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # 保存为WAV文件
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return filename


def main():
    print("IndexTTS声音克隆与录音演示")
    print("="*60)
    print("此脚本将:")
    print("1. 录制您的声音（5秒）")
    print("2. 使用您的声音克隆生成指定文本的语音")
    print("="*60)
    
    # 检查是否安装了pyaudio
    try:
        import pyaudio
    except ImportError:
        print("❌ 未安装pyaudio，请运行: pip install pyaudio")
        return
    
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
    
    # 录制用户声音
    print("\n准备录制您的声音...")
    input("按Enter键开始录制5秒钟的声音（请清晰地说一些话）...")
    
    # 临时存储录制的音频
    reference_audio_path = os.path.join(tempfile.gettempdir(), f"temp_voice_ref_{os.getpid()}.wav")
    
    try:
        recorded_path = record_audio(duration=5, filename=reference_audio_path)
        print(f"✅ 声音录制完成: {recorded_path}")
    except Exception as e:
        print(f"❌ 录制失败: {e}")
        return
    
    # 初始化IndexTTS策略
    print("\n正在初始化IndexTTS引擎...")
    tts_strategy = IndexTTSStrategy(reference_audio_path=recorded_path)
    
    if not tts_strategy.initialize():
        print("❌ IndexTTS引擎初始化失败")
        return
    
    print("✅ IndexTTS引擎初始化成功！")
    
    # 循环生成语音
    while True:
        print("\n" + "="*60)
        text = input("请输入要转换为语音的文本 (输入'quit'退出): ").strip()
        
        if text.lower() in ['quit', 'exit', '退出']:
            print("感谢使用IndexTTS声音克隆！")
            # 清理临时文件
            if os.path.exists(reference_audio_path):
                os.remove(reference_audio_path)
            break
        
        if not text:
            print("❌ 文本不能为空，请重新输入")
            continue
        
        print("正在使用您的声音生成语音...")
        
        # 使用录制的声音作为参考，生成指定文本的语音
        output_file = tts_strategy.speak_with_voice_clone(text, recorded_path)
        
        if output_file:
            print(f"✅ 语音已生成: {output_file}")
            print("语音文件已保存，您可以使用任意音频播放器播放该文件")
            
            # 询问是否重新录制
            re_record = input("\n是否重新录制声音样本？(y/n): ").strip().lower()
            if re_record == 'y':
                input("按Enter键重新录制5秒钟的声音...")
                if os.path.exists(reference_audio_path):
                    os.remove(reference_audio_path)
                
                reference_audio_path = os.path.join(tempfile.gettempdir(), f"temp_voice_ref_{os.getpid()}.wav")
                try:
                    recorded_path = record_audio(duration=5, filename=reference_audio_path)
                    print(f"✅ 新的声音录制完成: {recorded_path}")
                    
                    # 更新策略的参考音频
                    tts_strategy.reference_audio_path = recorded_path
                except Exception as e:
                    print(f"❌ 重新录制失败: {e}")
                    continue
        else:
            print("❌ 语音生成失败")
            # 询问是否重新录制
            re_record = input("是否重新录制声音样本？(y/n): ").strip().lower()
            if re_record == 'y':
                input("按Enter键重新录制5秒钟的声音...")
                if os.path.exists(reference_audio_path):
                    os.remove(reference_audio_path)
                
                reference_audio_path = os.path.join(tempfile.gettempdir(), f"temp_voice_ref_{os.getpid()}.wav")
                try:
                    recorded_path = record_audio(duration=5, filename=reference_audio_path)
                    print(f"✅ 新的声音录制完成: {recorded_path}")
                    
                    # 更新策略的参考音频
                    tts_strategy.reference_audio_path = recorded_path
                except Exception as e:
                    print(f"❌ 重新录制失败: {e}")
                    continue


def simple_clone_with_existing_audio():
    """使用已有的音频文件进行声音克隆"""
    print("IndexTTS声音克隆（使用已有音频文件）")
    print("="*60)
    
    # 检查模型
    checkpoints_dir = os.path.join(os.path.dirname(__file__), 'git', 'index-tts', 'checkpoints')
    if not os.path.exists(checkpoints_dir):
        print(f"❌ IndexTTS 检查点目录不存在: {checkpoints_dir}")
        print("💡 请确保已克隆index-tts仓库并下载模型文件")
        return
    
    config_path = os.path.join(checkpoints_dir, 'config.yaml')
    if not os.path.exists(config_path):
        print(f"❌ IndexTTS 配置文件未找到: {config_path}")
        return
    
    # 获取用户提供的音频文件
    audio_path = input("请输入参考音频文件路径 (3-5秒清晰音频): ").strip()
    if not audio_path or not os.path.exists(audio_path):
        print("❌ 参考音频文件不存在，请检查路径是否正确")
        return
    
    # 初始化IndexTTS策略
    print("\n正在初始化IndexTTS引擎...")
    tts_strategy = IndexTTSStrategy(reference_audio_path=audio_path)
    
    if not tts_strategy.initialize():
        print("❌ IndexTTS引擎初始化失败")
        return
    
    print("✅ IndexTTS引擎初始化成功！")
    
    # 循环生成语音
    while True:
        print("\n" + "="*60)
        text = input("请输入要转换为语音的文本 (输入'quit'退出): ").strip()
        
        if text.lower() in ['quit', 'exit', '退出']:
            print("感谢使用IndexTTS声音克隆！")
            break
        
        if not text:
            print("❌ 文本不能为空，请重新输入")
            continue
        
        print("正在使用您的声音生成语音...")
        
        # 使用提供的音频作为参考，生成指定文本的语音
        output_file = tts_strategy.speak_with_voice_clone(text, audio_path)
        
        if output_file:
            print(f"✅ 语音已生成: {output_file}")
            print("语音文件已保存，您可以使用任意音频播放器播放该文件")
        else:
            print("❌ 语音生成失败")


if __name__ == "__main__":
    print("请选择操作模式:")
    print("1. 录制自己的声音并进行声音克隆")
    print("2. 使用已有的音频文件进行声音克隆")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        simple_clone_with_existing_audio()
    else:
        print("无效选择，使用默认模式（录制声音）")
        main()