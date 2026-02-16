#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情绪检测功能测试脚本
用于验证MCP服务的情绪检测功能
"""

import asyncio
import json
import uuid
import websockets
import base64

async def emotion_detection_test():
    """测试情绪检测功能"""
    try:
        # 连接到服务
        async with websockets.connect("ws://localhost:8766") as websocket:
            print("✅ 成功连接到MCP服务")
            
            # 创建任务ID
            task_id = str(uuid.uuid4())
            
            # 发送开始会话消息
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
            
            # 等待Started响应
            response = await websocket.recv()
            response_data = json.loads(response)
            
            print(f"📥 收到响应: {response_data['payload']['output']['event']}")
            
            if response_data['payload']['output']['event'] == 'Started':
                dialog_id = response_data['payload']['output']['dialog_id']
                print(f"✅ 会话已启动，对话ID: {dialog_id}")
                
                # 接收状态变更消息
                state_response = await websocket.recv()
                state_data = json.loads(state_response)
                print(f"📥 收到状态变更: {state_data['payload']['output']['state']}")
                
                # 发送情绪检测请求（使用一个简单的base64图片）
                # 这里使用一个非常简单的1x1像素的PNG图片的base64编码
                simple_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                
                emotion_request = {
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
                                "value": simple_image_base64
                            }]
                        }
                    }
                }
                
                await websocket.send(json.dumps(emotion_request))
                print("📤 发送情绪检测请求")
                
                # 接收多个响应
                responses_received = 0
                while responses_received < 5:  # 期待接收5个响应
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        response_data = json.loads(response)
                        
                        event_type = response_data['payload']['output']['event']
                        print(f"📥 收到响应 #{responses_received+1}: {event_type}")
                        
                        if event_type == 'RespondingContent':
                            text = response_data['payload']['output'].get('text', '')
                            spoken = response_data['payload']['output'].get('spoken', '')
                            print(f"💬 文本内容: {text}")
                            print(f"🗣️  语音内容: {spoken}")
                            
                            if '情绪分析结果' in text:
                                print("😊 情绪检测功能工作正常！")
                                
                        elif event_type == 'RespondingStarted':
                            print("🔊 响应开始")
                            
                        elif event_type == 'RespondingEnded':
                            print("🔇 响应结束")
                            break
                            
                        elif event_type == 'LocalRespondingEnded':
                            print("📱 本地响应结束")
                            break
                            
                        responses_received += 1
                    except asyncio.TimeoutError:
                        print("⏰ 接收响应超时")
                        break
                
                # 发送停止会话消息
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
                
                # 等待停止响应
                stop_response = await websocket.recv()
                stop_data = json.loads(stop_response)
                print(f"📥 收到响应: {stop_data['payload']['output']['event']}")
                
                if stop_data['payload']['output']['event'] == 'Stopped':
                    print("✅ 会话已成功停止")
                else:
                    print("❌ 会话停止失败")
            else:
                print("❌ 会话启动失败")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def run_emotion_test():
    """运行情绪检测测试"""
    print("🧪 开始情绪检测功能测试...")
    print("="*50)
    
    try:
        asyncio.run(emotion_detection_test())
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
    
    print("="*50)
    print("✅ 情绪检测功能测试完成")


if __name__ == "__main__":
    run_emotion_test()