# qwen3-tts-flash-realtime-2025-11-27
# https://help.aliyun.com/zh/model-studio/qwen-tts-realtime?spm=a2c4g.11186623.0.0.5b6b1bc2zr39Vi#bac280ddf5a1u
import os
import base64
import threading
import time
import dashscope
from dashscope.audio.qwen_tts_realtime import *
import pyaudio
import uuid

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
    def __init__(self, output_file=None, play_audio=True, output_format='pcm'):
        self.complete_event = threading.Event()
        self.output_format = output_format.lower()
        
        if output_file:
            self.file = open(output_file, 'wb')
        else:
            extension = 'wav' if self.output_format == 'wav' else 'pcm'
            self.file = open(f'result_24k.{extension}', 'wb')
        
        # 控制是否播放音频
        self.play_audio = play_audio
        if play_audio:
            # 初始化播放器
            self.player = pyaudio.PyAudio()
            self.stream = self.player.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True
            )
        else:
            self.player = None
            self.stream = None

    def on_open(self) -> None:
        if self.play_audio:
            print('connection opened, init player')
        else:
            print('connection opened')

    def on_close(self, close_status_code, close_msg) -> None:
        self.file.close()
        # 只有在播放音频时才关闭播放器
        if self.play_audio and self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.player:
            self.player.terminate()
        if self.play_audio:
            print('connection closed with code: {}, msg: {}, destroy player'.format(close_status_code, close_msg))
        else:
            print('connection closed with code: {}, msg: {}'.format(close_status_code, close_msg))

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
                # 只有在播放音频时才实时播放
                if self.play_audio and self.stream:
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
        
    def cleanup(self):
        try:
            self.file.close()
            # 只有在播放音频时才关闭播放器
            if self.play_audio and self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.player:
                self.player.terminate()
        except:
            pass

# 专门用于不播放音频的回调类
class MyCallbackNoPlay(QwenTtsRealtimeCallback):
    def __init__(self, output_file=None, output_format='pcm'):
        self.complete_event = threading.Event()
        self.output_format = output_format.lower()
        
        if output_file:
            self.file = open(output_file, 'wb')
        else:
            extension = 'wav' if self.output_format == 'wav' else 'pcm'
            self.file = open(f'result_24k.{extension}', 'wb')
        
        # 不初始化播放器相关组件
        self.player = None
        self.stream = None
        self.play_audio = False

    def on_open(self) -> None:
        # 避免输出任何与播放器相关的消息
        pass

    def on_close(self, close_status_code, close_msg) -> None:
        # 确保文件已关闭
        try:
            self.file.close()
        except:
            pass  # 文件可能已经被关闭
        
        # 打印更准确的连接关闭信息
        if close_status_code is not None:
            print(f'connection closed with code: {close_status_code}, msg: {close_msg}')
        else:
            # 即使状态码为None也记录连接关闭
            print('connection closed')

    def on_event(self, response: str) -> None:
        try:
            global qwen_tts_realtime
            type = response['type']
            if 'session.created' == type:
                # 仅在调试时输出
                # print('start session: {}'.format(response['session']['id']))
                pass
            if 'response.audio.delta' == type:
                recv_audio_b64 = response['delta']
                audio_data = base64.b64decode(recv_audio_b64)
                self.file.write(audio_data)
                # 不播放音频
            if 'response.done' == type:
                # print(f'response {qwen_tts_realtime.get_last_response_id()} done')
                pass
            if 'session.finished' == type:
                # print('session finished')
                self.complete_event.set()
        except Exception as e:
            print('[Error] {}'.format(e))
            return

    def wait_for_finished(self):
        self.complete_event.wait()
        
    def cleanup(self):
        try:
            if not self.file.closed:
                self.file.close()
        except:
            pass

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


def synthesize_text_to_speech(text, voice='Chelsie', output_file=None, play_audio=False, output_format='pcm'):
    """
    将文本转换为语音并保存到文件
    :param text: 要转换的文本
    :param voice: 使用的声音类型，默认为'Chelsie'
    :param output_file: 输出音频文件名，如果为None则生成随机文件名
    :param play_audio: 是否实时播放音频，默认为False
    :param output_format: 输出音频格式，默认为'pcm'，可选'wav'(会先生成pcm再转换)
    :return: 音频文件路径，如果失败则返回None
    """
    if output_file is None:
        extension = 'wav' if output_format.lower() == 'wav' else 'pcm'  # 根据输出格式决定扩展名
        output_file = f"tts_output_{uuid.uuid4().hex}.{extension}"
    
    # 如果指定了WAV格式，我们需要先生成PCM再转换
    original_output_file = output_file
    pcm_file = output_file if output_format.lower() == 'pcm' else f"{output_file.rsplit('.', 1)[0]}.pcm"  # 将输出文件扩展名改为.pcm用于中间处理
    
    tts_client = None
    callback = None
    
    try:
        init_dashscope_api_key()
        print(f'Synthesizing TTS for: "{text[:30]}..."')
        execution_start_time = time.time()

        if play_audio:
            callback = MyCallback(output_file=pcm_file, play_audio=True)
        else:
            # 当不播放音频时，使用一个不初始化播放器的回调
            callback = MyCallbackNoPlay(output_file=pcm_file)

        tts_client = QwenTtsRealtime(
            model='qwen3-tts-flash-realtime-2025-11-27',
            callback=callback, 
            url='wss://dashscope.aliyuncs.com/api-ws/v1/realtime'
        )

        connect_start = time.time()
        tts_client.connect()
        connect_time = time.time() - connect_start
        print(f'TTS连接耗时: {connect_time:.2f}秒')
        
        session_update_start = time.time()
        tts_client.update_session(
            voice=voice,
            response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,  # 实时API只支持PCM
            mode='server_commit'        
        )
        session_update_time = time.time() - session_update_start
        print(f'TTS会话更新耗时: {session_update_time:.2f}秒')
        
        # 发送文本进行TTS转换
        text_send_start = time.time()
        tts_client.append_text(text)
        tts_client.finish()
        text_send_time = time.time() - text_send_start
        print(f'TTS文本发送耗时: {text_send_time:.2f}秒')
        
        wait_start = time.time()
        callback.wait_for_finished()
        wait_time = time.time() - wait_start
        print(f'TTS等待完成耗时: {wait_time:.2f}秒')
        
        total_execution_time = time.time() - execution_start_time
        print(f'TTS总耗时: {total_execution_time:.2f}秒')
        
        # 如果需要WAV格式，则将PCM转换为WAV
        if output_format.lower() == 'wav':
            import wave
            wav_file = original_output_file  # 这是原始请求的输出文件名（.wav）
            # 确保回调已关闭文件句柄
            callback.cleanup()  # 确保文件句柄已关闭
            
            # 将PCM文件转换为WAV格式
            with open(pcm_file, 'rb') as pcmf:
                pcm_data = pcmf.read()
            
            # 创建WAV文件
            with wave.open(wav_file, 'wb') as wavf:
                wavf.setnchannels(1)  # 单声道
                wavf.setsampwidth(2)  # 16位，即2字节
                wavf.setframerate(24000)  # 24kHz采样率
                wavf.writeframes(pcm_data)
            
            # 删除临时PCM文件，添加重试机制以防文件被占用
            max_retries = 5
            retry_count = 0
            while retry_count < max_retries:
                try:
                    os.remove(pcm_file)
                    break  # 成功删除，跳出循环
                except PermissionError:
                    print(f"删除文件失败，重试 {retry_count + 1}/{max_retries}")
                    time.sleep(0.5)  # 等待片刻，使用全局time模块
                    retry_count += 1
            else:
                print(f"经过 {max_retries} 次尝试后仍无法删除文件: {pcm_file}")
            
            print(f'TTS completed, converted to WAV and saved to: {wav_file}')
            return wav_file
        else:
            print(f'TTS completed, saved to: {pcm_file}')
            return pcm_file
        
    except Exception as e:
        print(f"TTS synthesis failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # 确保资源被正确释放
        if callback:
            try:
                callback.cleanup()
            except Exception as e:
                print(f"Callback cleanup error: {e}")
        if tts_client:
            try:
                tts_client.close()
            except Exception as e:
                print(f"TTS client close error: {e}")


def synthesize_text_to_speech_stream(text, voice='Chelsie'):
    """
    将文本转换为语音并返回音频数据（不保存到文件）
    :param text: 要转换的文本
    :param voice: 使用的声音类型，默认为'Chelsie'
    :return: 音频数据bytes，如果失败则返回None
    """
    tts_client = None
    callback = None
    
    try:
        import io
        init_dashscope_api_key()
        print(f'Synthesizing TTS for: "{text[:30]}..."')

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

        tts_client = QwenTtsRealtime(
            model='qwen3-tts-flash-realtime-2025-11-27',
            callback=callback, 
            url='wss://dashscope.aliyuncs.com/api-ws/v1/realtime'
        )

        tts_client.connect()
        tts_client.update_session(
            voice=voice,
            response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
            mode='server_commit'        
        )
        
        # 发送文本进行TTS转换
        tts_client.append_text(text)
        tts_client.finish()
        callback.wait_for_finished()
        audio_data = callback.audio_data
        
        print('TTS completed, audio data collected')
        return audio_data
    except Exception as e:
        print(f'TTS failed: {str(e)}')
        return None
    finally:
        # 确保资源被正确释放
        if callback:
            callback.cleanup()
        if tts_client:
            try:
                tts_client.disconnect()
            except:
                pass


def interactive_tts_test():
    """交互式TTS测试，通过while循环持续接收用户输入"""
    print("="*50)
    print("欢迎使用交互式TTS测试")
    print("输入 'quit' 或 'exit' 退出程序")
    print("输入 'voices' 查看可用声音列表")
    print("输入 'format' 查看/切换输出格式")
    print("输入 'play' 开启/关闭实时播放")
    print("="*50)
    
    # 定义可用的声音类型
    available_voices = {
        '1': 'Longhua',
        '2': 'Zhitian',
        '3': 'Suxin',
        '4': 'Zhizhe',
        '5': 'Chelsie'
    }
    
    # 默认设置
    current_voice = 'Chelsie'
    current_format = 'pcm'  # 可选 'pcm' 或 'wav'
    play_audio = True  # 是否实时播放
    
    while True:
        status_line = f"\n当前语音: {current_voice}, 格式: {current_format}"
        if play_audio:
            status_line += ", 实时播放: 开启"
        else:
            status_line += ", 实时播放: 关闭"
        print(status_line)
        
        user_input = input("请输入要转换的文字 (或输入命令): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("退出程序...")
            break
        elif user_input.lower() == 'voices':
            print("\n可用的声音类型:")
            for key, value in available_voices.items():
                print(f"  {key}: {value}")
            continue
        elif user_input in available_voices:
            current_voice = available_voices[user_input]
            print(f"已切换到语音: {current_voice}")
            continue
        elif user_input.lower() == 'format':
            # 切换输出格式
            current_format = 'wav' if current_format == 'pcm' else 'pcm'
            print(f"已切换输出格式为: {current_format}")
            continue
        elif user_input.lower() == 'play':
            play_audio = not play_audio
            state = "开启" if play_audio else "关闭"
            print(f"实时播放已{state}")
            continue
        elif user_input == '':
            print("输入不能为空，请重新输入")
            continue
            
        # 进行TTS转换，添加时间测量
        start_time = time.time()
        output_file = synthesize_text_to_speech(
            user_input, 
            voice=current_voice, 
            play_audio=play_audio,
            output_format=current_format
        )
        end_time = time.time()
        
        if output_file:
            print(f"音频已保存到: {output_file}")
            print(f"本次TTS总耗时: {end_time - start_time:.2f}秒")
        else:
            print("TTS转换失败")


if __name__ == '__main__':
    interactive_tts_test()