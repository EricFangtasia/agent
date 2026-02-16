import asyncio
import json
import os
import sys
import time
import uuid
from typing import Optional
import threading
import queue
import io

import websockets

try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("警告: pyaudio未安装，无法播放音频。请运行: pip install pyaudio")

WS_URL = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"


# ALIYUN_API_KEY = os.getenv("ALIYUN_API_KEY", "sk-0fa1679a354b4bbc8f480f553bc801ad")  # 从环境变量获取，不再硬编码
# ALIYUN_WSS_URL = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"
# ALIYUN_WORKSPACE_ID = os.getenv("ALIYUN_WORKSPACE_ID", "llm-nzu0viiu9sxvpjn9")
# ALIYUN_APP_ID = os.getenv("ALIYUN_APP_ID", "mm_a6be48a8a95c4d45923ccef93def")


# === 在此处硬编码配置 ===
API_KEY = "sk-0fa1679a354b4bbc8f480f553bc801ad"
WORKSPACE_ID = "llm-nzu0viiu9sxvpjn9"
APP_ID = "mm_a6be48a8a95c4d45923ccef93def"
DEFAULT_USER_ID: Optional[str] = None  # 例如 "test-user-001"，留空则自动生成
# ======================


class AudioPlayer:
    def __init__(self, sample_rate=24000, channels=1, sample_width=2):
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = sample_width
        self.audio_queue = queue.Queue()
        self.is_playing = False
        self.should_stop = False
        self.player_thread = None
        self.pyaudio_instance = None
        self.stream = None
        self.total_received_bytes = 0
        self.total_played_bytes = 0
        self.playback_finished = threading.Event()
        self.data_finished = False  # 标记数据是否接收完成
        
        if AUDIO_AVAILABLE:
            self.pyaudio_instance = pyaudio.PyAudio()
    
    def start_playback(self):
        """开始音频播放"""
        if not AUDIO_AVAILABLE:
            return
            
        if self.is_playing:
            return
            
        print("初始化音频播放...")
        self.is_playing = True
        self.should_stop = False
        self.data_finished = False
        self.total_received_bytes = 0
        self.total_played_bytes = 0
        self.playback_finished.clear()
        
        # 清空队列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        self.player_thread = threading.Thread(target=self._play_audio_thread)
        self.player_thread.daemon = True
        self.player_thread.start()
    
    def stop_playback(self, wait_for_finish=True):
        """停止音频播放"""
        print("请求停止音频播放...")
        self.should_stop = True
        
        if wait_for_finish:
            # 等待播放完成或超时
            timeout = 10.0  # 增加超时时间
            if self.playback_finished.wait(timeout=timeout):
                print("音频播放正常完成")
            else:
                print(f"音频播放超时({timeout}秒)，强制停止")
        
        self.is_playing = False
        
        # 等待播放线程结束
        if self.player_thread and self.player_thread.is_alive():
            self.player_thread.join(timeout=3.0)
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"关闭音频流时出错: {e}")
            finally:
                self.stream = None
        
        print(f"音频播放统计: 接收 {self.total_received_bytes} 字节, 播放 {self.total_played_bytes} 字节")
    
    def add_audio_data(self, audio_data):
        """添加音频数据到播放队列"""
        if not AUDIO_AVAILABLE or not self.is_playing:
            return
        
        self.total_received_bytes += len(audio_data)
        try:
            self.audio_queue.put(audio_data, timeout=1.0)
        except queue.Full:
            print("音频队列已满，丢弃数据")
    
    def finish_receiving(self):
        """标记音频数据接收完成"""
        print("标记音频数据接收完成")
        self.data_finished = True
        if self.is_playing:
            # 添加一个特殊标记表示数据接收完成
            try:
                self.audio_queue.put(None, timeout=1.0)
            except queue.Full:
                print("无法添加结束标记，队列已满")
    
    def _play_audio_thread(self):
        """音频播放线程"""
        try:
            # 初始化音频流
            chunk_size = 1024
            self.stream = self.pyaudio_instance.open(
                format=self.pyaudio_instance.get_format_from_width(self.sample_width),
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=chunk_size
            )
            
            print("音频流初始化成功")
            
            # 等待一些初始数据
            initial_buffer = b''
            initial_packets = 0
            max_initial_wait = 30  # 减少初始等待包数
            
            while self.is_playing and initial_packets < max_initial_wait:
                try:
                    audio_data = self.audio_queue.get(timeout=1.0)
                    if audio_data is None:  # 接收完成标记
                        print("在初始缓冲阶段收到结束标记")
                        break
                    if audio_data:
                        initial_buffer += audio_data
                        initial_packets += 1
                        # 当有足够数据时开始播放
                        if len(initial_buffer) >= 4096:  # 减少初始缓冲要求
                            break
                except queue.Empty:
                    if self.data_finished:
                        print("数据接收已完成，开始播放现有缓冲")
                        break
                    continue
            
            if not self.is_playing:
                print("播放已停止，退出播放线程")
                return
            
            print(f"开始播放音频数据，初始缓冲: {len(initial_buffer)} 字节")
            
            # 播放初始缓冲数据
            if initial_buffer:
                self._write_audio_data(initial_buffer)
            
            # 继续播放剩余数据
            empty_count = 0
            max_empty_count = 100  # 增加最大空队列等待次数
            
            while self.is_playing:
                try:
                    audio_data = self.audio_queue.get(timeout=0.1)
                    
                    if audio_data is None:  # 接收完成标记
                        print("收到数据接收完成标记，继续播放剩余数据")
                        empty_count = 0
                        continue
                    
                    if audio_data:
                        empty_count = 0
                        self._write_audio_data(audio_data)
                    
                except queue.Empty:
                    empty_count += 1
                    
                    # 只有在数据接收完成且队列持续为空时才考虑结束
                    if self.data_finished and empty_count >= 50:  # 数据完成后等待更久
                        print(f"数据接收完成且队列空闲{empty_count}次，播放结束")
                        break
                    
                    # 如果数据接收未完成，等待更长时间
                    if not self.data_finished and empty_count >= max_empty_count:
                        print(f"数据接收未完成但队列长时间为空({empty_count}次)，可能网络问题")
                        break
                
                # 检查是否被要求停止（但要等数据播放完）
                if self.should_stop and self.data_finished and empty_count >= 10:
                    print("收到停止请求，数据接收完成且队列基本为空，退出播放线程")
                    break
            
            # 给音频流一些时间播放完剩余数据
            if self.stream:
                try:
                    print("等待音频流播放完成...")
                    time.sleep(0.5)  # 增加等待时间
                except Exception:
                    pass
            
            print("音频播放线程正常结束")
                    
        except Exception as e:
            print(f"音频播放线程异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.playback_finished.set()  # 标记播放完成
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except Exception:
                    pass
                self.stream = None
    
    def _write_audio_data(self, audio_data):
        """写入音频数据"""
        try:
            if self.stream and audio_data:
                # 分块写入，避免一次写入过多数据
                chunk_size = 1024
                for i in range(0, len(audio_data), chunk_size):
                    if not self.is_playing:
                        break
                    chunk = audio_data[i:i + chunk_size]
                    if chunk:
                        self.stream.write(chunk)
                        self.total_played_bytes += len(chunk)
        except Exception as e:
            print(f"写入音频数据时出错: {e}")
    
    def close(self):
        """关闭音频播放器"""
        self.stop_playback(wait_for_finish=False)
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except Exception as e:
                print(f"关闭pyaudio时出错: {e}")


class TextChatClient:
    def __init__(self,
                 api_key: Optional[str] = None,
                 workspace_id: Optional[str] = None,
                 app_id: Optional[str] = None,
                 user_id: Optional[str] = None,
                 upstream_type: str = "AudioOnly",
                 upstream_mode: str = "push2talk",
                 downstream_voice: str = "longanyang",
                 downstream_sample_rate: int = 24000,
                 enable_audio_playback: bool = True):
        # 改为使用硬编码常量，允许通过入参覆盖
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise RuntimeError("请在 ws_client.py 顶部填写 API_KEY")
        self.workspace_id = workspace_id or WORKSPACE_ID
        self.app_id = app_id or APP_ID
        if not self.workspace_id or not self.app_id:
            raise RuntimeError("请在 ws_client.py 顶部填写 WORKSPACE_ID 与 APP_ID")
        self.user_id = user_id or DEFAULT_USER_ID or f"user-{uuid.uuid4().hex[:8]}"
        self.upstream_type = upstream_type
        self.upstream_mode = upstream_mode
        self.downstream_voice = downstream_voice
        self.downstream_sample_rate = downstream_sample_rate
        self.enable_audio_playback = enable_audio_playback and AUDIO_AVAILABLE
        
        self.dialog_id: Optional[str] = None
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._last_heartbeat = 0.0
        self.state: Optional[str] = None
        self.task_id = uuid.uuid4().hex
        self._running = False
        self._recv_task = None
        self._heartbeat_task = None
        self._waiting_for_input = False
        
        # 音频播放器
        self.audio_player = None
        if self.enable_audio_playback:
            self.audio_player = AudioPlayer(
                sample_rate=self.downstream_sample_rate,
                channels=1,
                sample_width=2  # 16bit = 2 bytes
            )
        
        # 音频数据统计
        self.audio_data_count = 0
        self.total_audio_bytes = 0

    async def connect(self):
        headers = {
            "Authorization": self.api_key,
        }
        self.websocket = await websockets.connect(WS_URL, additional_headers=headers, max_size=None)
        self._running = True
        # 启动后台任务
        self._recv_task = asyncio.create_task(self._recv_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def close(self):
        self._running = False
        
        # 停止音频播放
        if self.audio_player:
            self.audio_player.close()
        
        # 取消后台任务
        if self._recv_task and not self._recv_task.done():
            self._recv_task.cancel()
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
        
        # 关闭WebSocket连接
        if self.websocket and not getattr(self.websocket, 'closed', False):
            try:
                await self.websocket.close()
            except Exception:
                pass

    async def _heartbeat_loop(self):
        """心跳循环"""
        while self._running and self.websocket and not getattr(self.websocket, 'closed', False):
            try:
                await asyncio.sleep(50)
                if self._running:
                    await self.send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"心跳发送失败: {e}")

    async def _recv_loop(self):
        """消息接收循环"""
        if not self.websocket:
            return
            
        try:
            while self._running and not getattr(self.websocket, 'closed', False):
                try:
                    # 设置超时，避免无限等待
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    
                    if isinstance(message, (bytes, bytearray)):
                        # 音频数据
                        self.audio_data_count += 1
                        self.total_audio_bytes += len(message)
                        
                        if self.audio_player and self.audio_player.is_playing:
                            self.audio_player.add_audio_data(message)
                        continue
                    
                    try:
                        data = json.loads(message)
                        await self._handle_event(data)
                    except Exception as e:
                        print(f"解析消息失败: {e}")
                        
                except asyncio.TimeoutError:
                    # 超时是正常的，继续循环
                    continue
                except asyncio.CancelledError:
                    break
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket连接已关闭")
                    break
                except Exception as e:
                    print(f"接收消息时出错: {e}")
                    break
                    
        except asyncio.CancelledError:
            pass
        finally:
            self._running = False

    def _print_with_prompt_reset(self, message):
        """打印消息并重新显示输入提示"""
        if self._waiting_for_input:
            # 清除当前行并打印消息
            print(f"\r{message}")
            # 重新显示输入提示
            print("你: ", end="", flush=True)
        else:
            print(message)

    async def _handle_event(self, data: dict):
        payload = data.get("payload", {})
        output = payload.get("output", {})
        event_name = output.get("event")
        
        if event_name == "Started":
            self.dialog_id = output.get("dialog_id")
            print(f"会话创建成功，dialog_id={self.dialog_id}")
        elif event_name == "Stopped":
            print("会话结束")
        elif event_name == "DialogStateChanged":
            self.state = output.get("state")
            self._print_with_prompt_reset(f"状态切换: {self.state}")
        elif event_name == "RequestAccepted":
            self._print_with_prompt_reset("请求已被接受")
        elif event_name == "HeartBeat":
            # 心跳回复不显示
            pass
        elif event_name == "Error":
            code = output.get("error_code")
            msg = output.get("error_message")
            self._print_with_prompt_reset(f"服务端错误: {code} {msg}")
        elif event_name == "RespondingContent":
            # AI回复的文本内容
            text = output.get("text", "")
            finished = output.get("finished", False)
            if text and finished:
                self._print_with_prompt_reset(f"AI: {text}")
        elif event_name == "SpeechContent":
            # 用户语音识别结果
            text = output.get("text", "")
            finished = output.get("finished", False)
            if text and finished:
                self._print_with_prompt_reset(f"识别: {text}")
        elif event_name == "RespondingStarted":
            # 重置音频统计
            self.audio_data_count = 0
            self.total_audio_bytes = 0
            
            if self.enable_audio_playback:
                self._print_with_prompt_reset("开始播放AI语音")
                if self.audio_player:
                    self.audio_player.start_playback()
            else:
                self._print_with_prompt_reset("开始接收AI语音")
        elif event_name == "RespondingEnded":
            if self.enable_audio_playback:
                self._print_with_prompt_reset(f"AI语音数据接收完成 (收到 {self.audio_data_count} 个音频包，共 {self.total_audio_bytes} 字节)")
                # 通知音频播放器数据接收完成
                if self.audio_player:
                    self.audio_player.finish_receiving()
                # 等待播放完成，增加等待时间
                await asyncio.sleep(2.0)  # 增加等待时间
                if self.audio_player:
                    self.audio_player.stop_playback(wait_for_finish=True)
            else:
                self._print_with_prompt_reset(f"AI语音接收完成 (收到 {self.audio_data_count} 个音频包，共 {self.total_audio_bytes} 字节)")
            
            # 自动发送播放完成通知
            await self.send_local_responding_ended()

    async def send_json(self, obj: dict):
        if not self.websocket or getattr(self.websocket, 'closed', False):
            print("WebSocket连接已关闭，无法发送消息")
            return
        try:
            text = json.dumps(obj, ensure_ascii=False)
            await self.websocket.send(text)
        except Exception as e:
            print(f"发送消息失败: {e}")

    async def send_start(self):
        start_msg = {
            "header": {
                "action": "run-task",
                "task_id": self.task_id,
                "streaming": "duplex"
            },
            "payload": {
                "task_group": "aigc",
                "task": "multimodal-generation",
                "function": "generation",
                "model": "multimodal-dialog",
                "input": {
                    "directive": "Start",
                    "workspace_id": self.workspace_id,
                    "app_id": self.app_id
                },
                "parameters": {
                    "upstream": {
                        "type": self.upstream_type,
                        "mode": self.upstream_mode,
                        "audio_format": "pcm",
                        "sample_rate": 16000
                    },
                    "downstream": {
                        "voice": self.downstream_voice,
                        "sample_rate": self.downstream_sample_rate,
                        "audio_format": "pcm"
                    },
                    "intermediate_text": "transcript,dialog",
                    "client_info": {
                        "user_id": self.user_id,
                        "device": {
                            "uuid": uuid.uuid4().hex
                        },
                        "network": {
                            "ip": "127.0.0.1"
                        },
                        "location": {
                            "city_name": "北京市"
                        }
                    }
                }
            }
        }
        await self.send_json(start_msg)

    async def send_stop(self):
        stop_msg = {
            "header": {
                "action": "finish-task",
                "task_id": self.task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {
                    "directive": "Stop",
                    **({"dialog_id": self.dialog_id} if self.dialog_id else {})
                }
            }
        }
        await self.send_json(stop_msg)

    async def send_heartbeat(self):
        now = time.time()
        if now - self._last_heartbeat < 45:
            return
        self._last_heartbeat = now
        hb_msg = {
            "header": {
                "action": "continue-task",
                "task_id": self.task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {
                    "directive": "HeartBeat",
                    **({"dialog_id": self.dialog_id} if self.dialog_id else {})
                }
            }
        }
        await self.send_json(hb_msg)

    async def send_text_message(self, text: str):
        """发送文本消息给AI"""
        if not self.dialog_id:
            print("会话未建立，无法发送消息")
            return
        
        msg = {
            "header": {
                "action": "continue-task",
                "task_id": self.task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {
                    "directive": "RequestToRespond",
                    "dialog_id": self.dialog_id,
                    "type": "prompt",
                    "text": text
                }
            }
        }
        await self.send_json(msg)

    async def send_local_responding_ended(self):
        """发送本地播放结束通知"""
        if not self.dialog_id:
            return
        
        msg = {
            "header": {
                "action": "continue-task",
                "task_id": self.task_id,
                "streaming": "duplex"
            },
            "payload": {
                "input": {
                    "directive": "LocalRespondingEnded",
                    "dialog_id": self.dialog_id
                }
            }
        }
        await self.send_json(msg)


async def get_user_input():
    """异步获取用户输入"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input)


async def interactive_loop(client: TextChatClient):
    print("\n" + "="*50)
    print("文本对话模式已启动")
    if client.enable_audio_playback:
        print("音频播放已启用")
    else:
        print("音频播放未启用（需要安装pyaudio）")
    print("输入文本发送消息，输入 'quit' 或 'q' 退出")
    print("="*50 + "\n")
    
    # 等待状态变为Listening
    max_wait = 20
    wait_count = 0
    while client.state != "Listening" and wait_count < max_wait and client._running:
        await asyncio.sleep(0.5)
        wait_count += 1
    
    if client.state != "Listening":
        print("等待超时，当前状态不是Listening，但仍可尝试发送消息")
    
    while client._running:
        try:
            # 标记正在等待用户输入
            client._waiting_for_input = True
            print("你: ", end="", flush=True)
            
            # 异步获取用户输入
            user_input = await get_user_input()
            
            # 取消等待输入标记
            client._waiting_for_input = False
            
            if user_input.lower() in ['quit', 'q', 'exit', '退出']:
                print("正在退出...")
                break
            
            if user_input.strip():
                await client.send_text_message(user_input.strip())
            
        except KeyboardInterrupt:
            print("\n正在退出...")
            break
        except Exception as e:
            print(f"输入错误: {e}")
            client._waiting_for_input = False


async def main():
    # 可以通过参数控制是否启用音频播放
    enable_audio = True  # 设置为False可以禁用音频播放
    
    client = TextChatClient(enable_audio_playback=enable_audio)
    
    try:
        print("正在连接服务器...")
        await client.connect()
        print("连接成功")
        
        print("正在启动会话...")
        await client.send_start()
        
        # 等待会话建立
        await asyncio.sleep(2)
        
        if not client.dialog_id:
            print("会话建立失败，请检查配置")
            return
        
        await interactive_loop(client)
        
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("正在关闭会话...")
        try:
            await client.send_stop()
            await asyncio.sleep(1)
            await client.close()
        except Exception:
            pass
        print("会话已关闭")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行错误: {e}")