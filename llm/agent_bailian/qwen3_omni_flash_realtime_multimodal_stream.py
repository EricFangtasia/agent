import os
import base64
from openai import OpenAI
import numpy as np
import threading
import time
import queue

# 尝试导入sounddevice，如果失败则标记为不可用
try:
    import sounddevice as sd  # pip install sounddevice
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    print("sounddevice模块未安装，将使用pyaudio播放音频")
    SOUNDDEVICE_AVAILABLE = False
    sd = None

import pyaudio  # 需安装：pip install pyaudio

def multimodal_chat_with_audio(api_key, messages, model="qwen3-omni-flash-2025-12-01", voice="Cherry"):
    """
    多模态聊天方法，返回流式数据生成器
    
    :param api_key: DashScope API密钥
    :param messages: 消息列表，格式为[{"role": "user", "content": "..."}]
    :param model: 使用的模型名称
    :param voice: 使用的语音类型
    :return: 生成器，产生(text, audio_data)元组
    """
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        modalities=["text", "audio"],  # 必须设置此参数才能返回音频
        audio={"voice": voice, "format": "wav"},
        stream=True,
        stream_options={"include_usage": True}
    )

    for chunk in completion:
        if not chunk.choices:  # 跳过 usage chunk
            continue

        delta = chunk.choices[0].delta

        text_content = None
        audio_data = None

        # 提取文本内容
        if hasattr(delta, 'content') and delta.content:
            text_content = delta.content
        else:
            text_content = None

        # 提取音频数据
        if hasattr(delta, 'audio') and delta.audio:
            # 根据API响应格式，音频数据在 'data' 字段中
            audio_payload = delta.audio
            b64_audio = None
            
            # 检查是否是包含多个字段的字典（如 {'data': '...', 'expires_at': ..., 'id': ...}）
            if isinstance(audio_payload, dict):
                # 直接从字典中获取 'data' 字段
                if 'data' in audio_payload and audio_payload['data']:
                    b64_audio = audio_payload['data']
                elif 'bytes' in audio_payload and audio_payload['bytes']:
                    b64_audio = audio_payload['bytes']
            
            if b64_audio and b64_audio.strip():  # 确保音频数据不为空
                try:
                    audio_bytes = base64.b64decode(b64_audio)
                    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
                    audio_data = audio_np
                except Exception as e:
                    print(f"音频处理错误: {e}")
            else:
                audio_data = None

        yield (text_content, audio_data)


def play_audio(audio_data):
    """播放音频数据"""
    if audio_data is None:
        return
        
    if SOUNDDEVICE_AVAILABLE:
        try:
            # 使用sounddevice播放音频
            sd.play(audio_data, samplerate=24000, blocking=True)
        except Exception as e:
            print(f"sounddevice 播放出错: {e}")
    else:
        try:
            # 使用pyaudio播放音频
            p = pyaudio.PyAudio()
            stream = p.open(
                format=p.get_format_from_width(2),  # 16-bit
                channels=1,  # 单声道
                rate=24000,  # 24kHz
                output=True
            )
            
            # 写入音频数据并播放
            stream.write(audio_data.tobytes())
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"PyAudio 播放出错: {e}")


# 示例使用
if __name__ == "__main__":
    HONGXIA_API_KEY = "sk-0fa1679a354b4bbc8f480f553bc801ad"
    
    # 准备消息
    messages = [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"}},
            {"type": "text", "text": "图中描绘的是什么景象？"}
        ]
    }]
    
    print("开始请求模型...")
    print("模型回复：", end="", flush=True)
    
    # 计数器
    audio_chunk_count = 0
    text_chunk_count = 0
    
    # 处理流式数据
    for text_content, audio_data in multimodal_chat_with_audio(
        api_key=os.getenv("DASHSCOPE_API_KEY", HONGXIA_API_KEY),
        messages=messages
    ):
        # 处理文本内容
        if text_content:
            print(text_content, end="", flush=True)
            text_chunk_count += 1
        else:
            print(".", end="")  # 表示收到了一个没有文本的chunk

        # 处理音频数据
        if audio_data is not None:
            play_audio(audio_data)
            audio_chunk_count += 1

    print(f"\n总共处理了 {text_chunk_count} 个文本片段，{audio_chunk_count} 个音频片段")
    print("处理完成")