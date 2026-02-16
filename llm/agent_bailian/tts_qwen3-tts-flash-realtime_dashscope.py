# qwen3-tts-flash-realtime-2025-11-27
# https://help.aliyun.com/zh/model-studio/qwen-tts-realtime?spm=a2c4g.11186623.0.0.5b6b1bc2zr39Vi#bac280ddf5a1u
import os
import base64
import threading
import time
import dashscope
from dashscope.audio.qwen_tts_realtime import *
import pyaudio

# # 初始化播放器（在 MyCallback.__init__ 中）
# self.player = pyaudio.PyAudio()
# self.stream = self.player.open(
#     format=pyaudio.paInt16,
#     channels=1,
#     rate=24000,
#     output=True
# )

# # 在 on_event 中播放
# elif event_type == 'response.audio.delta':
#     audio_data = base64.b64decode(response['delta'])
#     self.stream.write(audio_data)  # 实时播放



qwen_tts_realtime: QwenTtsRealtime = None
text_to_synthesize = [
    '对吧~我就特别喜欢这种超市呢，',
    '尤其是过大年的时候',
    '去逛超市',
    '就会觉得',
    '超级超级开心！',
    '想买好多好多的东西呢！'
]
HONGXIA_API_KEY = "sk-0fa1679a354b4bbc8f480f553bc801ad"

DO_VIDEO_TEST = False

def init_dashscope_api_key():
    """
        Set your DashScope API-key. More information:
        https://github.com/aliyun/alibabacloud-bailian-speech-demo/blob/master/PREREQUISITES.md
    """

    # 从环境变量加载API密钥
    if 'DASHSCOPE_API_KEY' in os.environ:
        dashscope.api_key = os.environ['DASHSCOPE_API_KEY']
    else:
        # 为了向后兼容，如果环境变量未设置，则使用默认值（生产环境中应避免）
        dashscope.api_key = os.getenv('DASHSCOPE_API_KEY', HONGXIA_API_KEY)

class MyCallback(QwenTtsRealtimeCallback):
    def __init__(self):
        self.complete_event = threading.Event()
        self.file = open('result_24k.pcm', 'wb')
        # 初始化播放器
        self.player = pyaudio.PyAudio()
        self.stream = self.player.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            output=True
        )

    def on_open(self) -> None:
        print('connection opened, init player')

    def on_close(self, close_status_code, close_msg) -> None:
        self.file.close()
        self.stream.stop_stream()
        self.stream.close()
        self.player.terminate()
        print('connection closed with code: {}, msg: {}, destroy player'.format(close_status_code, close_msg))

    def on_event(self, response: str) -> None:
        try:
            global qwen_tts_realtime
            type = response['type']
            if 'session.created' == type:
                print('start session: {}'.format(response['session']['id']))
            if 'response.audio.delta' == type:
                recv_audio_b64 = response['delta']
                audio_data = base64.b64decode(recv_audio_b64)
                self.file.write(audio_data)
                # 实时播放音频
                self.stream.write(audio_data)
            if 'response.done' == type:
                print(f'response {qwen_tts_realtime.get_last_response_id()} done')
            if 'session.finished' == type:
                print('session finished')
                self.complete_event.set()
        except Exception as e:
            print('[Error] {}'.format(e))
            return

    def wait_for_finished(self):
        self.complete_event.wait()


def play_pcm_file(file_path, rate=24000):
    """播放保存的PCM文件"""
    chunk_size = 1024
    p = pyaudio.PyAudio()
    
    # 打开音频流
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    output=True)
    
    # 读取并播放音频文件
    with open(file_path, 'rb') as f:
        data = f.read(chunk_size)
        while data:
            stream.write(data)
            data = f.read(chunk_size)
    
    # 关闭流
    stream.stop_stream()
    stream.close()
    p.terminate()


def synthesize_text_to_speech(text, voice='Longhua', output_file=None):
    """
    将文本转换为语音并保存到文件
    :param text: 要转换的文本
    :param voice: 使用的声音类型，默认为'Longhua'
    :param output_file: 输出音频文件名，如果为None则使用默认名称
    :return: 音频文件路径，如果失败则返回None
    """
    if output_file is None:
        import uuid
        output_file = f"tts_output_{uuid.uuid4().hex}.pcm"
    
    try:
        init_dashscope_api_key()
        print('Initializing TTS...')

        callback = MyCallback()
        # 临时修改回调中的文件保存路径
        callback.file.close()  # 关闭原文件
        callback.file = open(output_file, 'wb')  # 打开新文件

        qwen_tts_realtime = QwenTtsRealtime(
            model='qwen3-tts-flash-realtime-2025-11-27',
            callback=callback, 
            url='wss://dashscope.aliyuncs.com/api-ws/v1/realtime'
        )

        qwen_tts_realtime.connect()
        qwen_tts_realtime.update_session(
            voice=voice,
            response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
            mode='server_commit'        
        )
        
        # 发送文本进行TTS转换
        qwen_tts_realtime.append_text(text)
        qwen_tts_realtime.finish()
        callback.wait_for_finished()
        callback.file.close()
        callback.cleanup()
        
        print(f'TTS completed, saved to: {output_file}')
        return output_file
    except Exception as e:
        print(f'TTS failed: {str(e)}')
        # 确保文件被关闭
        try:
            callback.file.close()
        except:
            pass
        return None


def synthesize_text_to_speech_stream(text, voice='Longhua'):
    """
    将文本转换为语音并返回音频数据（不保存到文件）
    :param text: 要转换的文本
    :param voice: 使用的声音类型，默认为'Longhua'
    :return: 音频数据bytes，如果失败则返回None
    """
    try:
        import io
        init_dashscope_api_key()
        print('Initializing TTS...')

        # 自定义回调类，只收集数据而不保存到文件
        class StreamCallback(QwenTtsRealtimeCallback):
            def __init__(self):
                self.complete_event = threading.Event()
                self.audio_data = b""

            def on_open(self) -> None:
                print('connection opened')

            def on_close(self, close_status_code, close_msg) -> None:
                print('connection closed with code: {}, msg: {}'.format(close_status_code, close_msg))

            def on_event(self, response: str) -> None:
                try:
                    type = response['type']
                    if 'response.audio.delta' == type:
                        recv_audio_b64 = response['delta']
                        audio_data = base64.b64decode(recv_audio_b64)
                        self.audio_data += audio_data
                    elif 'session.finished' == type:
                        print('session finished')
                        self.complete_event.set()
                except Exception as e:
                    print('[Error] {}'.format(e))
                    return

            def wait_for_finished(self):
                self.complete_event.wait()
                
            def cleanup(self):
                pass

        callback = StreamCallback()

        qwen_tts_realtime = QwenTtsRealtime(
            model='qwen3-tts-flash-realtime-2025-11-27',
            callback=callback, 
            url='wss://dashscope.aliyuncs.com/api-ws/v1/realtime'
        )

        qwen_tts_realtime.connect()
        qwen_tts_realtime.update_session(
            voice=voice,
            response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
            mode='server_commit'        
        )
        
        # 发送文本进行TTS转换
        qwen_tts_realtime.append_text(text)
        qwen_tts_realtime.finish()
        callback.wait_for_finished()
        callback.cleanup()
        
        print('TTS completed, audio data collected')
        return callback.audio_data
    except Exception as e:
        print(f'TTS failed: {str(e)}')
        return None


if __name__  == '__main__':
    # 测试TTS功能
    test_text = "你好，这是一段测试语音。"
    output_file = synthesize_text_to_speech(test_text)
    if output_file:
        print(f"语音已保存到: {output_file}")
    else:
        print("TTS转换失败")