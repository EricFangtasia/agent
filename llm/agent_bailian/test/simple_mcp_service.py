#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的实时多模态交互MCP服务
用于演示和测试目的
"""

import asyncio
import json
import uuid
import websockets
import random
from enum import Enum

class DialogState(Enum):
    LISTENING = "Listening"
    THINKING = "Thinking"
    RESPONDING = "Responding"

async def handle_client(websocket):
    """处理客户端连接"""
    print(f"[INFO] 新客户端连接: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                await process_message(websocket, data)
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

async def process_message(websocket, data: dict):
    """处理来自客户端的消息"""
    if 'header' in data and 'action' in data['header']:
        action = data['header']['action']
        
        if action == "run-task":
            await handle_start_task(websocket, data)
        elif action == "finish-task":
            await handle_stop_task(websocket, data)
        elif action == "continue-task":
            await handle_continue_task(websocket, data)
    else:
        print("[WARNING] 未知消息类型")

async def handle_start_task(websocket, data: dict):
    """处理开始任务请求"""
    task_id = data['header']['task_id']
    payload = data['payload']
    
    # 创建对话ID
    dialog_id = str(uuid.uuid4())
    
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

async def handle_stop_task(websocket, data: dict):
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

async def detect_emotion(image_base64):
    """模拟情绪检测函数"""
    emotions = ["happy", "sad", "angry", "surprise", "fear", "disgust", "neutral"]
    return {
        "detected_emotion": random.choice(emotions),
        "confidence": round(random.uniform(0.5, 1.0), 2),
        "details": f"Detected emotion: {random.choice(emotions)}"
    }

async def handle_continue_task(websocket, data: dict):
    """处理继续任务请求"""
    task_id = data['header']['task_id']
    payload = data['payload']
    input_data = payload['input']
    directive = input_data['directive']
    
    dialog_id = input_data.get('dialog_id')
    
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
                emotion_result = await detect_emotion(image_data['value'])
                
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
            await asyncio.sleep(0.05)  # 模拟流式传输延迟
        
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

async def start_server():
    """启动服务器"""
    print("[INFO] 启动简化版实时多模态MCP服务在 localhost:8766")
    
    async with websockets.serve(handle_client, "localhost", 8766):
        print("[INFO] 服务器已启动并监听 localhost:8766")
        await asyncio.Future()  # 保持服务器运行

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n[INFO] 正在关闭服务器...")
    print("[INFO] 服务器已关闭")