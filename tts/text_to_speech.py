#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本转语音文件工具
使用pyttsx3引擎将输入的文本转换为语音文件
"""

import os
import tempfile
import pyttsx3


def text_to_speech_file(text, output_file=None, rate=200, volume=0.9):
    """
    将输入的文本转换为语音文件
    
    Args:
        text (str): 要转换为语音的文本
        output_file (str, optional): 输出的音频文件路径，如果为None则生成临时文件
        rate (int, optional): 语速，默认为200
        volume (float, optional): 音量，默认为0.9
    
    Returns:
        str: 生成的音频文件路径，如果失败则返回None
    """
    try:
        # 初始化pyttsx3引擎
        engine = pyttsx3.init()
        
        # 设置语音参数
        engine.setProperty('rate', rate)  # 语速
        engine.setProperty('volume', volume)  # 音量
        
        # 设置中文语音（如果可用）
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'zh' in voice.id.lower() or 'chinese' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        # 如果没有指定输出文件，则创建临时文件
        if output_file is None:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
        
        # 保存语音到文件
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        
        # 检查文件是否成功生成并且不为空
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            if file_size > 0:
                print(f"✅ 语音文件已生成: {output_file}")
                return output_file
            else:
                print("❌ 生成的音频文件为空")
                return None
        else:
            print("❌ 音频文件未生成")
            return None
            
    except Exception as e:
        print(f"❌ 文本转语音失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # 确保每次使用后清理引擎资源
        try:
            engine.stop()
        except:
            pass


def batch_text_to_speech(texts, output_dir=None):
    """
    批量将多个文本转换为语音文件
    
    Args:
        texts (list): 包含多个文本的列表
        output_dir (str, optional): 输出目录路径，如果为None则生成临时文件
    
    Returns:
        list: 生成的音频文件路径列表
    """
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = []
    for i, text in enumerate(texts):
        if output_dir:
            output_file = os.path.join(output_dir, f"speech_{i+1}.wav")
        else:
            output_file = None
        
        result = text_to_speech_file(text, output_file)
        if result:
            results.append(result)
        else:
            print(f"⚠️  第{i+1}个文本转换失败")
    
    return results


if __name__ == "__main__":
    # 测试单个文本转换
    sample_text = "你好，这是文本转语音功能的测试。"
    output_path = text_to_speech_file(sample_text)
    
    if output_path:
        print(f"生成的语音文件路径: {output_path}")
        
        # 测试批量转换
        sample_texts = [
            "这是第一个文本。",
            "这是第二个文本。",
            "这是第三个文本。"
        ]
        batch_results = batch_text_to_speech(sample_texts, "./output")
        
        print(f"批量转换完成，成功生成 {len(batch_results)} 个文件:")
        for path in batch_results:
            print(f"  - {path}")
    else:
        print("转换失败")