#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试脚本，用于验证MCP服务是否正常工作
"""

import asyncio
import json
import uuid
import websockets

async def simple_test():
    """简单测试连接"""
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
            
            # 等待响应
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


def run_simple_test():
    """运行简单测试"""
    print("🧪 开始简单测试...")
    print("="*50)
    
    try:
        asyncio.run(simple_test())
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
    
    print("="*50)
    print("✅ 测试完成")


if __name__ == "__main__":
    run_simple_test()