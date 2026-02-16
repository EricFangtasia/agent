#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实时多模态交互MCP服务演示脚本
演示服务的核心功能，包括会话管理和情绪检测
"""

import asyncio
import json
import uuid
import websockets
import base64

async def run_demo():
    """运行演示"""
    try:
        print("🎬 开始实时多模态交互MCP服务演示...")
        print("="*60)
        
        # 连接到服务
        async with websockets.connect("ws://localhost:8766") as websocket:
            print("✅ 成功连接到MCP服务")
            
            # 创建任务ID
            task_id = str(uuid.uuid4())
            print(f"🆔 生成任务ID: {task_id}")
            
            # 1. 开始会话
            print("\n1️⃣  开始会话...")
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
                            "user_id": "demo-user"
                        }
                    }
                }
            }
            
            await websocket.send(json.dumps(start_msg))
            print("📤 发送开始会话请求")
            
            # 等待Started响应
            response = await websocket.recv()
            response_data = json.loads(response)
            
            if response_data['payload']['output']['event'] == 'Started':
                dialog_id = response_data['payload']['output']['dialog_id']
                print(f"✅ 会话已启动，对话ID: {dialog_id}")
                
                # 接收状态变更消息
                state_response = await websocket.recv()
                state_data = json.loads(state_response)
                print(f"🔄 状态变更为: {state_data['payload']['output']['state']}")
                
                # 2. 演示情绪检测功能
                print("\n2️⃣  演示情绪检测功能...")
                
                # 使用一个简单的base64图片
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
                
                # 接收情绪检测结果
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if response_data['payload']['output']['event'] == 'RespondingContent':
                    text = response_data['payload']['output'].get('text', '')
                    spoken = response_data['payload']['output'].get('spoken', '')
                    print(f"😊 情绪分析结果: {text}")
                    print(f"📢 语音内容: {spoken}")
                
                # 接收响应结束事件
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if response_data['payload']['output']['event'] == 'RespondingEnded':
                    print("✅ 响应结束")
                
                # 3. 演示普通对话功能
                print("\n3️⃣  演示普通对话功能...")
                
                dialog_request = {
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
                            "text": "你好，这是一次多模态交互演示"
                        }
                    }
                }
                
                await websocket.send(json.dumps(dialog_request))
                print("📤 发送对话请求")
                
                # 接收响应开始事件
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data['payload']['output']['event'] == 'RespondingStarted':
                        print("🔊 响应开始")
                    
                    # 接收实际响应
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data['payload']['output']['event'] == 'RespondingContent':
                        text = response_data['payload']['output'].get('text', '')
                        print(f"💬 响应内容: {text}")
                    
                    # 接收响应结束事件
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    
                    if response_data['payload']['output']['event'] == 'RespondingEnded':
                        print("✅ 响应结束")
                except asyncio.TimeoutError:
                    print("⏰ 接收对话响应超时")
                
                # 4. 结束会话
                print("\n4️⃣  结束会话...")
                
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
                
                if stop_data['payload']['output']['event'] == 'Stopped':
                    print("✅ 会话已成功停止")
                else:
                    print("❌ 会话停止失败")
            else:
                print("❌ 会话启动失败")
        
        print("\n🎉 演示完成！")
        print("="*60)
                
    except Exception as e:
        print(f"❌ 演示失败: {e}")


def main():
    """主函数"""
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()