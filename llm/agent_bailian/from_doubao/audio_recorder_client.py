import pyaudio
import wave
import asyncio
import websockets
import json
import threading
import queue
import struct
import numpy as np


class AudioRecorder:
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1, rate=16000):
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.p = pyaudio.PyAudio()
        
        # 创建队列存储音频数据
        self.audio_queue = queue.Queue()

    def start_recording(self):
        """开始录制音频"""
        def record():
            stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print("开始录音...按Enter键停止录音")
            
            while True:
                data = stream.read(self.chunk, exception_on_overflow=False)
                self.audio_queue.put(data)
                
                # 检查是否需要停止
                if hasattr(self, '_stop_flag') and self._stop_flag:
                    break
            
            stream.stop_stream()
            stream.close()
        
        # 在单独线程中开始录音
        self.recording_thread = threading.Thread(target=record)
        self.recording_thread.start()
        
    def stop_recording(self):
        """停止录制音频"""
        self._stop_flag = True
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join()
        
    def get_audio_data(self):
        """获取音频数据"""
        frames = []
        while not self.audio_queue.empty():
            frames.append(self.audio_queue.get())
        return b''.join(frames)
        
    def close(self):
        """关闭音频接口"""
        self.p.terminate()


async def send_audio_to_mcp():
    """发送音频数据到MCP服务"""
    uri = "ws://localhost:8000/mcp/multimodal"
    
    async with websockets.connect(uri) as websocket:
        # 1. 启动会话
        start_msg = {
            "type": "session_start",
            "payload": {
                "upstream_type": "AudioOnly",
                "mode": "duplex",
                "audio_format": "pcm",
                "sample_rate": 16000,
                "voice": "longxiaochun_v2",
                "user_id": "test_user_001",
                "device_uuid": "test_device_001"
            }
        }
        await websocket.send(json.dumps(start_msg))
        
        # 等待会话启动响应
        response = await websocket.recv()
        print("会话启动响应:", response)
        
        response_data = json.loads(response)
        if response_data.get("type") == "error":
            print(f"错误: {response_data['payload']['message']}")
            return
            
        dialog_id = response_data["payload"].get("dialog_id")
        if not dialog_id:
            print("未获得有效的dialog_id")
            return

        # 创建音频录制器
        recorder = AudioRecorder()
        print("按Enter键开始录音...")
        input()
        
        print("录音中...说话吧！按Enter键停止录音")
        recorder.start_recording()
        
        # 等待用户输入以停止录音
        input()
        recorder.stop_recording()
        
        # 获取录制的音频数据
        audio_data = recorder.get_audio_data()
        print(f"录制了 {len(audio_data)} 字节的音频数据")
        
        # 发送音频数据
        await websocket.send(audio_data)
        print("音频数据已发送")
        
        # 接收响应
        response_count = 0
        while response_count < 10:  # 最多接收10条消息
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print("收到消息:", msg)
                response_count += 1
                
                # 检测是否收到完整回答
                try:
                    msg_data = json.loads(msg) if isinstance(msg, str) else {}
                    if isinstance(msg_data, dict) and msg_data.get("type") == "llm_result" and msg_data.get("payload", {}).get("finished"):
                        print("收到完整回答，结束接收")
                        break
                except json.JSONDecodeError:
                    continue
            except asyncio.TimeoutError:
                print("等待消息超时")
                break
        
        recorder.close()


if __name__ == "__main__":
    print("MCP音频录制客户端")
    print("确保MCP服务器正在运行 (python run_mcp_server.py)")
    print("然后按Enter键开始...")
    input()
    
    asyncio.run(send_audio_to_mcp())