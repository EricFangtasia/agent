#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实时多模态交互MCP服务

基于WebSocket协议的实时多模态交互API实现
支持与阿里云多模态交互开发套件的对接
"""

import asyncio
import json
import uuid
import websockets
import threading
import queue
import time
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# 模拟情绪检测函数，实际使用时应该从emotion_detection_onnx.py导入
def detect_emotion(image_base64):
    """
    模拟情绪检测函数
    实际使用时应该从emotion_detection_onnx.py导入真实函数
    """
    # 这里是模拟实现，实际应用中应替换为真实的检测函数
    import random
    emotions = ["happy", "sad", "angry", "surprise", "fear", "disgust", "neutral"]
    return {
        "detected_emotion": random.choice(emotions),
        "confidence": round(random.uniform(0.5, 1.0), 2),
        "details": f"Detected emotion: {random.choice(emotions)}"
    }


class DialogState(Enum):
    LISTENING = "Listening"
    THINKING = "Thinking"
    RESPONDING = "Responding"


@dataclass
class TaskHeader:
    action: str
    task_id: str
    streaming: str = "duplex"


@dataclass
class EventHeader:
    event: str
    task_id: str


class RealtimeMultimodalMCPService:
    def __init__(self, host="localhost", port=8766):  # 修改为8766端口
        self.host = host
        self.port = port
        self.active_connections: Dict[str, Dict] = {}  # task_id -> connection_info
        self.dialog_states: Dict[str, DialogState] = {}  # dialog_id -> state
        self.dialog_ids: Dict[str, str] = {}  # task_id -> dialog_id
        self.client_queues: Dict[str, queue.Queue] = {}  # task_id -> client_queue
        self.server_queues: Dict[str, queue.Queue] = {}  # task_id -> server_queue
        self.running = False

    async def handle_client(self, websocket):
        """处理客户端连接"""
        print(f"[INFO] 新客户端连接: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(websocket, data)
                except json.JSONDecodeError:
                    print("[ERROR] 无法解析JSON消息")
                    continue
                except Exception as e:
                    print(f"[ERROR] 处理消息时出错: {e}")
                    continue
        except websockets.exceptions.ConnectionClosed:
            print("[INFO] 客户端断开连接")
        except Exception as e:
            print(f"[ERROR] 连接处理错误: {e}")
        finally:
            await self.cleanup_connection(websocket)

    async def process_message(self, websocket, data: dict):
        """处理来自客户端的消息"""
        if 'header' in data and 'action' in data['header']:
            action = data['header']['action']
            
            if action == "run-task":
                await self.handle_start_task(websocket, data)
            elif action == "finish-task":
                await self.handle_stop_task(websocket, data)
            elif action == "continue-task":
                await self.handle_continue_task(websocket, data)
        else:
            print("[WARNING] 未知消息类型")

    async def handle_start_task(self, websocket, data: dict):
        """处理开始任务请求"""
        task_id = data['header']['task_id']
        payload = data['payload']
        
        # 创建对话ID
        dialog_id = str(uuid.uuid4())
        self.dialog_ids[task_id] = dialog_id
        
        # 设置初始状态为Listening
        self.dialog_states[dialog_id] = DialogState.LISTENING
        
        # 发送Started响应
        started_msg = {
            "header": {
                "event": "result-generated",
                "task_id": task_id
            },
            "payload": {
                "output": {
                    "event": "Started",
                    "dialog_id": dialog_id
                }
            }
        }
        await websocket.send(json.dumps(started_msg))
        
        # 发送DialogStateChanged事件，通知客户端现在处于Listening状态
        state_msg = {
            "header": {
                "event": "result-generated",
                "task_id": task_id
            },
            "payload": {
                "output": {
                    "event": "DialogStateChanged",
                    "state": DialogState.LISTENING.value,
                    "dialog_id": dialog_id
                }
            }
        }
        await websocket.send(json.dumps(state_msg))
        
        print(f"[INFO] 会话已启动 - task_id: {task_id}, dialog_id: {dialog_id}")

    async def handle_stop_task(self, websocket, data: dict):
        """处理停止任务请求"""
        task_id = data['header']['task_id']
        payload = data['payload']
        dialog_id = payload['input'].get('dialog_id')
        
        # 发送Stopped响应
        stopped_msg = {
            "header": {
                "event": "result-generated",
                "task_id": task_id
            },
            "payload": {
                "output": {
                    "event": "Stopped",
                    "dialog_id": dialog_id
                }
            }
        }
        await websocket.send(json.dumps(stopped_msg))
        
        print(f"[INFO] 会话已停止 - task_id: {task_id}, dialog_id: {dialog_id}")

    async def handle_continue_task(self, websocket, data: dict):
        """处理继续任务请求"""
        task_id = data['header']['task_id']
        payload = data['payload']
        input_data = payload['input']
        directive = input_data['directive']
        
        dialog_id = input_data.get('dialog_id') or self.dialog_ids.get(task_id)
        
        if directive == "RequestToSpeak":
            # 处理请求说话指令
            response = {
                "header": {
                    "event": "result-generated",
                    "task_id": task_id
                },
                "payload": {
                    "output": {
                        "event": "RequestAccepted",
                        "dialog_id": dialog_id
                    }
                }
            }
            await websocket.send(json.dumps(response))
            
        elif directive == "RequestToRespond":
            # 处理请求响应指令
            response_type = input_data.get('type', 'prompt')
            text = input_data.get('text', '')
            
            # 检查是否有图片需要情绪分析
            images = payload.get('parameters', {}).get('images', [])
            if images and len(images) > 0:
                # 假设我们只处理第一个图片
                image_data = images[0]
                if image_data['type'] == 'base64':
                    emotion_result = detect_emotion(image_data['value'])
                    
                    # 发送情绪分析结果
                    emotion_msg = {
                        "header": {
                            "event": "result-generated",
                            "task_id": task_id
                        },
                        "payload": {
                            "output": {
                                "event": "RespondingContent",
                                "dialog_id": dialog_id,
                                "round_id": str(uuid.uuid4()),
                                "llm_request_id": str(uuid.uuid4()),
                                "text": f"情绪分析结果: {emotion_result['detected_emotion']}，置信度: {emotion_result['confidence']}",
                                "spoken": f"我分析了您提供的图片，检测到的情绪是{emotion_result['detected_emotion']}，置信度为{emotion_result['confidence']*100:.0f}%",
                                "finished": True,
                                "extra_info": {
                                    "commands": "[]"
                                }
                            }
                        }
                    }
                    await websocket.send(json.dumps(emotion_msg))
                    
                    # 发送响应结束事件
                    responding_ended_msg = {
                        "header": {
                            "event": "result-generated",
                            "task_id": task_id
                        },
                        "payload": {
                            "output": {
                                "event": "RespondingEnded",
                                "dialog_id": dialog_id
                            }
                        }
                    }
                    await websocket.send(json.dumps(responding_ended_msg))
                    
                    # 发送本地响应结束事件
                    local_responding_ended_msg = {
                        "header": {
                            "action": "continue-task",
                            "task_id": task_id,
                            "streaming": "duplex"
                        },
                        "payload": {
                            "input": {
                                "directive": "LocalRespondingEnded",
                                "dialog_id": dialog_id
                            }
                        }
                    }
                    await websocket.send(json.dumps(local_responding_ended_msg))
                    
                    return
            
            # 如果没有图片或者只是普通对话，根据请求类型生成响应
            if response_type == 'transcript':
                # 直接文本转语音
                response_text = f"我将直接朗读您提供的文本: {text}"
            else:
                # 通过大模型处理
                response_text = f"您说: '{text}'。这是通过多模态交互系统处理的结果。很高兴能与您交流！"
            
            # 发送响应开始事件
            responding_started_msg = {
                "header": {
                    "event": "result-generated",
                    "task_id": task_id
                },
                "payload": {
                    "output": {
                        "event": "RespondingStarted",
                        "dialog_id": dialog_id
                    }
                }
            }
            await websocket.send(json.dumps(responding_started_msg))
            
            # 发送响应内容（模拟流式传输）
            words = response_text.split()
            full_text = ""
            for i, word in enumerate(words):
                full_text += word + " "
                finished = i == len(words) - 1
                
                content_msg = {
                    "header": {
                        "event": "result-generated",
                        "task_id": task_id
                    },
                    "payload": {
                        "output": {
                            "event": "RespondingContent",
                            "dialog_id": dialog_id,
                            "round_id": str(uuid.uuid4()),
                            "llm_request_id": str(uuid.uuid4()),
                            "text": full_text.strip(),
                            "spoken": full_text.strip(),
                            "finished": finished,
                            "extra_info": {
                                "commands": "[]"
                            }
                        }
                    }
                }
                await websocket.send(json.dumps(content_msg))
                await asyncio.sleep(0.1)  # 模拟流式传输延迟
            
            # 发送响应结束事件
            responding_ended_msg = {
                "header": {
                    "event": "result-generated",
                    "task_id": task_id
                },
                "payload": {
                    "output": {
                        "event": "RespondingEnded",
                        "dialog_id": dialog_id
                    }
                }
            }
            await websocket.send(json.dumps(responding_ended_msg))
            
            # 发送本地响应结束事件
            local_responding_ended_msg = {
                "header": {
                    "action": "continue-task",
                    "task_id": task_id,
                    "streaming": "duplex"
                },
                "payload": {
                    "input": {
                        "directive": "LocalRespondingEnded",
                        "dialog_id": dialog_id
                    }
                }
            }
            await websocket.send(json.dumps(local_responding_ended_msg))

        elif directive == "HeartBeat":
            # 处理心跳事件
            heartbeat_response = {
                "header": {
                    "event": "result-generated",
                    "task_id": task_id
                },
                "payload": {
                    "output": {
                        "event": "HeartBeat",
                        "dialog_id": dialog_id
                    }
                }
            }
            await websocket.send(json.dumps(heartbeat_response))

    async def cleanup_connection(self, websocket):
        """清理连接资源"""
        # 查找对应的task_id并清理相关资源
        for task_id, conn_info in list(self.active_connections.items()):
            if conn_info['websocket'] == websocket:
                self.active_connections.pop(task_id, None)
                self.dialog_states.pop(self.dialog_ids.get(task_id, ""), None)
                self.dialog_ids.pop(task_id, None)
                self.client_queues.pop(task_id, None)
                self.server_queues.pop(task_id, None)
                break

    def start_server(self):
        """启动服务器"""
        self.running = True
        print(f"[INFO] 启动实时多模态MCP服务在 {self.host}:{self.port}")
        
        async def run_server():
            # 根据websockets版本适配API
            try:
                # 尝试新版API
                async with websockets.serve(self.handle_client, self.host, self.port):
                    print(f"[INFO] 服务器已启动并监听 {self.host}:{self.port}")
                    await asyncio.Future()  # 保持服务器运行
            except TypeError:
                # 如果失败，尝试旧版API
                server = websockets.serve(self.handle_client, self.host, self.port)
                print(f"[INFO] 服务器已启动并监听 {self.host}:{self.port}")
                await server
                await asyncio.Future()  # 保持服务器运行

        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(run_server())
        except KeyboardInterrupt:
            print("\n[INFO] 正在关闭服务器...")
        finally:
            loop.close()
            print("[INFO] 服务器已关闭")


def main():
    service = RealtimeMultimodalMCPService(host="localhost", port=8766)  # 修改为8766端口
    service.start_server()


if __name__ == "__main__":
    main()