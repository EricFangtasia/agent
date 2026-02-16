#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试实时多模态交互MCP服务

这个脚本用于测试实时多模态交互MCP服务的功能
"""

import asyncio
import json
import uuid
import websockets
import base64
import threading
import time

# 模拟图像数据（使用base64编码的简单图像）
SIMPLE_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

async def test_mcp_service():
    """测试MCP服务的基本功能"""
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 成功连接到MCP服务")
            
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 1. 测试开始会话
            print("\n📝 测试开始会话...")
            start_msg = {
                "header": {
                    "action": "run-task",
                    "task_id": task_id,
                    "streaming": "duplex"
                },
                "payload": {
                    "task_group": "aigc",
                    "task": "multimodal-generation",
                    "function": "generation",
                    "model": "multimodal-dialog",
                    "input": {
                        "directive": "Start",
                        "workspace_id": "test-workspace-id",
                        "app_id": "test-app-id"
                    },
                    "parameters": {
                        "upstream": {
                            "type": "AudioOnly",
                            "mode": "duplex"
                        },
                        "downstream": {
                            "voice": "longxiaochun_v2",
                            "sample_rate": 24000
                        },
                        "client_info": {
                            "user_id": "test-user-id"
                        }
                    }
                }
            }
            
            await websocket.send(json.dumps(start_msg))
            print("📤 发送开始会话请求")
            
            # 接收响应
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            print(f"📥 收到响应: {response_data['payload']['output']['event']}")
            
            if response_data['payload']['output']['event'] == 'Started':
                dialog_id = response_data['payload']['output']['dialog_id']
                print(f"✅ 会话已启动，对话ID: {dialog_id}")
                
                # 接收状态变更消息
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                print(f"📥 收到状态变更: {response_data['payload']['output']['state']}")
                
                # 2. 测试情绪检测（通过图片）
                print("\n😊 测试情绪检测...")
                emotion_test_msg = {
                    "header": {
                        "action": "continue-task",
                        "task_id": task_id,
                        "streaming": "duplex"
                    },
                    "payload": {
                        "input": {
                            "directive": "RequestToRespond",
                            "dialog_id": dialog_id,
                            "type": "prompt",
                            "text": "请分析这张图片中的情绪"
                        },
                        "parameters": {
                            "images": [{
                                "type": "base64",
                                "value": SIMPLE_IMAGE_BASE64  # 使用简单图像
                            }]
                        }
                    }
                }
                
                await websocket.send(json.dumps(emotion_test_msg))
                print("📤 发送情绪检测请求")
                
                # 接收多个响应
                for i in range(4):  # 我们期望收到几个响应
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        response_data = json.loads(response)
                        event_type = response_data['payload']['output']['event']
                        print(f"📥 收到响应 #{i+1}: {event_type}")
                        
                        if event_type == 'RespondingContent':
                            text = response_data['payload']['output'].get('text', '')
                            print(f"💬 响应内容: {text}")
                            
                        if event_type == 'RespondingEnded':
                            print("✅ 响应结束")
                            
                    except asyncio.TimeoutError:
                        print("⏰ 接收响应超时")
                        break
                        
                # 3. 测试普通对话
                print("\n💬 测试普通对话...")
                dialog_msg = {
                    "header": {
                        "action": "continue-task",
                        "task_id": task_id,
                        "streaming": "duplex"
                    },
                    "payload": {
                        "input": {
                            "directive": "RequestToRespond",
                            "dialog_id": dialog_id,
                            "type": "prompt",
                            "text": "你好，这是一次测试对话"
                        }
                    }
                }
                
                await websocket.send(json.dumps(dialog_msg))
                print("📤 发送对话请求")
                
                # 接收多个响应
                for i in range(3):  # 我们期望收到几个响应
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        response_data = json.loads(response)
                        event_type = response_data['payload']['output']['event']
                        print(f"📥 收到响应 #{i+1}: {event_type}")
                        
                        if event_type == 'RespondingContent':
                            text = response_data['payload']['output'].get('text', '')
                            print(f"💬 响应内容: {text}")
                            
                    except asyncio.TimeoutError:
                        print("⏰ 接收响应超时")
                        break
                
                # 4. 测试停止会话
                print("\n⏹️ 测试停止会话...")
                stop_msg = {
                    "header": {
                        "action": "finish-task",
                        "task_id": task_id,
                        "streaming": "duplex"
                    },
                    "payload": {
                        "input": {
                            "directive": "Stop",
                            "dialog_id": dialog_id
                        }
                    }
                }
                
                await websocket.send(json.dumps(stop_msg))
                print("📤 发送停止会话请求")
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                print(f"📥 收到响应: {response_data['payload']['output']['event']}")
                
                if response_data['payload']['output']['event'] == 'Stopped':
                    print("✅ 会话已成功停止")
                    
            else:
                print("❌ 会话启动失败")
                
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket连接失败: {e}")
    except asyncio.TimeoutError:
        print("❌ 操作超时")
    except ConnectionRefusedError:
        print("❌ 无法连接到服务器，请确保MCP服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")


def run_test():
    """运行测试"""
    print("🧪 开始测试实时多模态MCP服务...")
    print("="*50)
    
    asyncio.run(test_mcp_service())
    
    print("="*50)
    print("✅ 测试完成")


if __name__ == "__main__":
    run_test()