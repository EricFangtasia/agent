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
    多模态聊天方法，支持实时文本和音频输出
    
    :param api_key: DashScope API密钥
    :param messages: 消息列表，格式为[{"role": "user", "content": "..."}]
    :param model: 使用的模型名称
    :param voice: 使用的语音类型
    :return: None
    """
    # 打印时间 
    time_start = time.time()
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

    # Qwen-Omni-Flash 音频参数：24kHz, 16-bit, 单声道
    SAMPLE_RATE = 24000
    DTYPE = np.int16
    # 打印用时
    time_end = time.time()
    print(f"模型回复耗时: {time_end - time_start:.2f}秒")

    # 添加计数器以跟踪音频片段
    audio_chunk_count = 0
    text_chunk_count = 0

    # 使用队列存储音频数据
    audio_queue = queue.Queue()

    def audio_player():
        """在单独线程中播放音频，使用高效流式播放避免卡顿"""
        if SOUNDDEVICE_AVAILABLE:
            try:
                with sd.OutputStream(samplerate=SAMPLE_RATE, channels=1, dtype=DTYPE, blocksize=1024) as stream:
                    while True:
                        try:
                            audio_np = audio_queue.get(timeout=0.5)
                            if audio_np is None:  # 收到结束信号
                                break
                            stream.write(audio_np.reshape(-1, 1))
                            audio_queue.task_done()
                        except queue.Empty:
                            continue
            except Exception as e:
                print(f"sounddevice 播放出错: {e}")
        else:
            p = pyaudio.PyAudio()
            try:
                stream = p.open(
                    format=p.get_format_from_width(2),
                    channels=1,
                    rate=SAMPLE_RATE,
                    output=True
                )
                while True:
                    try:
                        audio_np = audio_queue.get(timeout=0.5)
                        if audio_np is None:  # 收到结束信号
                            break
                        stream.write(audio_np.tobytes())
                        audio_queue.task_done()
                    except queue.Empty:
                        continue
            except Exception as e:
                print(f"PyAudio 播放出错: {e}")
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()

    # 启动音频播放线程
    player_thread = threading.Thread(target=audio_player, daemon=False)  # 改为非守护线程
    player_thread.start()

    for chunk in completion:
        if not chunk.choices:  # 跳过 usage chunk
            continue

        delta = chunk.choices[0].delta

        # 实时打印文本
        if hasattr(delta, 'content') and delta.content:
            print(delta.content, end="", flush=True)
            text_chunk_count += 1
        else:
            print(".", end="")  # 表示收到了一个没有文本的chunk

        # 实时播放音频片段
        if hasattr(delta, 'audio') and delta.audio:
            # 根据API响应格式，音频数据在 'data' 字段中
            audio_data = delta.audio
            b64_audio = None
            
            # 检查是否是包含多个字段的字典（如 {'data': '...', 'expires_at': ..., 'id': ...}）
            if isinstance(audio_data, dict):
                # 直接从字典中获取 'data' 字段
                if 'data' in audio_data and audio_data['data']:
                    b64_audio = audio_data['data']
                elif 'bytes' in audio_data and audio_data['bytes']:
                    b64_audio = audio_data['bytes']
            
            if b64_audio and b64_audio.strip():  # 确保音频数据不为空
                try:
                    audio_bytes = base64.b64decode(b64_audio)
                    audio_np = np.frombuffer(audio_bytes, dtype=DTYPE)
                    
                    # 将音频添加到播放队列
                    audio_queue.put(audio_np)
                    
                    audio_chunk_count += 1
                        
                except Exception as e:
                    print(f"音频处理错误: {e}")
            else:
                # 检查是否有其他音频相关字段
                pass  # 不再打印音频数据无效的信息

    # 所有音频数据已发送完毕，向队列放入结束信号
    audio_queue.put(None)

    # 等待播放线程完全结束
    player_thread.join(timeout=2.0)  # 给予最多2秒时间完成播放

    print(f"\n总共处理了 {text_chunk_count} 个文本片段，{audio_chunk_count} 个音频片段")
    print("处理完成")


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
    multimodal_chat_with_audio(
        api_key=os.getenv("DASHSCOPE_API_KEY", HONGXIA_API_KEY),
        messages=messages
    )