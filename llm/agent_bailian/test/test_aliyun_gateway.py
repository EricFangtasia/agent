#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试阿里云实时多模态交互网关

这个脚本用于测试阿里云实时多模态交互网关的功能
"""

import asyncio
import json
import uuid
import websockets
import base64
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 模拟图像数据（使用base64编码的简单图像）
SIMPLE_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


async def test_gateway():
    """测试网关的基本功能"""
    uri = "ws://localhost:8765"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("✅ 成功连接到阿里云网关")
            
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 1. 测试开始会话
            logger.info("\n📝 测试开始会话...")
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
                        "workspace_id": os.getenv("ALI_WORKSPACE_ID", "test-workspace-id"),
                        "app_id": os.getenv("ALI_APP_ID", "test-app-id")
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
            logger.info("📤 发送开始会话请求")
            
            # 接收Started响应
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            response_data = json.loads(response)
            logger.info(f"📥 收到响应: {response_data['payload']['output']['event']}")
            
            if response_data['payload']['output']['event'] == 'Started':
                dialog_id = response_data['payload']['output']['dialog_id']
                logger.info(f"✅ 会话已启动，对话ID: {dialog_id}")
                
                # 接收状态变更消息
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)
                state = response_data['payload']['output']['state']
                logger.info(f"📥 收到状态变更: {state}")
                
                # 2. 测试普通对话
                logger.info("\n💬 测试普通对话...")
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
                logger.info("📤 发送对话请求")
                
                # 接收响应
                responses_received = 0
                while responses_received < 5:  # 期望收到最多5个响应
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                        response_data = json.loads(response)
                        event_type = response_data['payload']['output']['event']
                        logger.info(f"📥 收到响应 #{responses_received+1}: {event_type}")
                        
                        if event_type == 'RespondingContent':
                            text = response_data['payload']['output'].get('text', '')
                            logger.info(f"💬 响应内容: {text[:100]}...")  # 只显示前100个字符
                        
                        if event_type == 'RespondingEnded':
                            logger.info("✅ 响应结束")
                            break
                            
                        responses_received += 1
                    except asyncio.TimeoutError:
                        logger.warning("⏰ 接收响应超时")
                        break
                
                # 3. 测试心跳
                logger.info("\n💓 测试心跳...")
                heartbeat_msg = {
                    "header": {
                        "action": "continue-task",
                        "task_id": task_id,
                        "streaming": "duplex"
                    },
                    "payload": {
                        "input": {
                            "directive": "HeartBeat",
                            "dialog_id": dialog_id
                        }
                    }
                }
                
                await websocket.send(json.dumps(heartbeat_msg))
                logger.info("📤 发送心跳请求")
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                event_type = response_data['payload']['output']['event']
                logger.info(f"📥 收到心跳响应: {event_type}")
                
                # 4. 测试停止会话
                logger.info("\n⏹️ 测试停止会话...")
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
                logger.info("📤 发送停止会话请求")
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                logger.info(f"📥 收到响应: {response_data['payload']['output']['event']}")
                
                if response_data['payload']['output']['event'] == 'Stopped':
                    logger.info("✅ 会话已成功停止")
                    
            else:
                logger.warning("❌ 会话启动失败")
                
    except websockets.exceptions.InvalidStatusCode as e:
        logger.error(f"❌ WebSocket连接失败: {e}")
    except asyncio.TimeoutError:
        logger.error("❌ 操作超时")
    except ConnectionRefusedError:
        logger.error("❌ 无法连接到网关，请确保网关服务正在运行")
    except Exception as e:
        logger.error(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


def run_test():
    """运行测试"""
    logger.info("🧪 开始测试阿里云实时多模态交互网关...")
    logger.info("="*50)
    
    asyncio.run(test_gateway())
    
    logger.info("="*50)
    logger.info("✅ 测试完成")


if __name__ == "__main__":
    run_test()