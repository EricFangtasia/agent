#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
阿里云实时多模态交互客户端

这个客户端将作为桥梁，连接本地客户端和阿里云实时多模态交互服务
"""

import asyncio
import json
import uuid
import websockets
import threading
import queue
import os
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class DialogState(Enum):
    LISTENING = "Listening"
    THINKING = "Thinking"
    RESPONDING = "Responding"


@dataclass
class TaskHeader:
    action: str
    task_id: str
    streaming: str = "duplex"


class AliyunRealtimeMultimodalClient:
    def __init__(self, ali_host="wss://dashscope.aliyuncs.com/api-ws/v1/inference", 
                 local_host="localhost", local_port=8765):
        self.ali_host = ali_host
        self.local_host = local_host
        self.local_port = local_port
        self.api_key = os.getenv("DASHSCOPE_API_KEY")  # 从环境变量获取API密钥
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")
        
        # 本地连接存储
        self.local_connections: Dict[str, Any] = {}
        self.ali_connections: Dict[str, Any] = {}
        
        # 任务映射表：本地task_id -> 阿里云task_id
        self.task_mappings: Dict[str, str] = {}
        
        # 阿里云对话ID映射
        self.dialog_mappings: Dict[str, str] = {}
        
        self.running = False

    async def handle_local_client(self, local_websocket):
        """处理本地客户端连接"""
        print(f"[INFO] 本地客户端连接: {local_websocket.remote_address}")
        
        try:
            async for message in local_websocket:
                try:
                    data = json.loads(message)
                    await self.process_local_message(local_websocket, data)
                except json.JSONDecodeError:
                    print("[ERROR] 无法解析本地客户端JSON消息")
                    continue
                except Exception as e:
                    print(f"[ERROR] 处理本地消息时出错: {e}")
                    continue
        except websockets.exceptions.ConnectionClosed:
            print("[INFO] 本地客户端断开连接")
        except Exception as e:
            print(f"[ERROR] 本地连接处理错误: {e}")
        finally:
            await self.cleanup_local_connection(local_websocket)

    async def process_local_message(self, local_ws, data: dict):
        """处理来自本地客户端的消息"""
        if 'header' in data and 'action' in data['header']:
            action = data['header']['action']
            local_task_id = data['header']['task_id']
            
            # 创建或获取阿里云WebSocket连接
            ali_ws = await self.get_or_create_ali_connection(local_task_id)
            if not ali_ws:
                print(f"[ERROR] 无法创建阿里云连接")
                return
            
            # 映射本地task_id到阿里云task_id
            ali_task_id = self.task_mappings.get(local_task_id)
            if not ali_task_id:
                ali_task_id = str(uuid.uuid4())
                self.task_mappings[local_task_id] = ali_task_id
            
            # 转换消息为阿里云格式
            ali_message = self.convert_to_ali_format(data, ali_task_id)
            
            try:
                await ali_ws.send(json.dumps(ali_message))
                print(f"[INFO] 已转发消息到阿里云，本地task_id: {local_task_id}, 阿里云task_id: {ali_task_id}")
            except Exception as e:
                print(f"[ERROR] 发送到阿里云失败: {e}")
        else:
            print("[WARNING] 未知本地消息类型")

    async def get_or_create_ali_connection(self, local_task_id: str):
        """获取或创建到阿里云的WebSocket连接"""
        ali_ws = self.ali_connections.get(local_task_id)
        if ali_ws and not ali_ws.closed:
            return ali_ws
        
        # 创建新连接到阿里云
        try:
            ali_ws = await websockets.connect(
                self.ali_host,
                extra_headers={"Authorization": f"Bearer {self.api_key}"}
            )
            self.ali_connections[local_task_id] = ali_ws
            
            # 启动接收阿里云消息的任务
            asyncio.create_task(self.forward_from_ali_to_local(local_task_id, ali_ws))
            
            print(f"[INFO] 已连接到阿里云服务")
            return ali_ws
        except Exception as e:
            print(f"[ERROR] 无法连接到阿里云服务: {e}")
            return None

    def convert_to_ali_format(self, local_data: dict, ali_task_id: str):
        """将本地消息格式转换为阿里云格式"""
        ali_data = {
            "header": {
                "action": local_data['header']['action'],
                "task_id": ali_task_id,
                "streaming": local_data['header'].get('streaming', 'duplex')
            },
            "payload": local_data.get('payload', {})
        }
        return ali_data

    def convert_from_ali_format(self, ali_data: dict, local_task_id: str):
        """将阿里云消息格式转换为本地格式"""
        # 获取对应的本地task_id
        ali_task_id = ali_data['header'].get('task_id', '')
        local_task_id = self.get_local_task_id(ali_task_id)
        
        local_data = {
            "header": {
                "event": ali_data['header'].get('event', ''),
                "task_id": local_task_id or ali_task_id  # 如果找不到本地ID，使用阿里云ID
            },
            "payload": ali_data.get('payload', {})
        }
        return local_data

    def get_local_task_id(self, ali_task_id: str) -> Optional[str]:
        """根据阿里云task_id获取本地task_id"""
        for local_id, ali_id in self.task_mappings.items():
            if ali_id == ali_task_id:
                return local_id
        return None

    def get_local_dialog_id(self, ali_dialog_id: str) -> Optional[str]:
        """根据阿里云dialog_id获取本地dialog_id"""
        for local_id, ali_id in self.dialog_mappings.items():
            if ali_id == ali_dialog_id:
                return local_id
        return None

    async def forward_from_ali_to_local(self, local_task_id: str, ali_ws):
        """从阿里云转发消息到本地客户端"""
        try:
            async for message in ali_ws:
                try:
                    ali_data = json.loads(message)
                    local_data = self.convert_from_ali_format(ali_data, local_task_id)
                    
                    # 获取本地WebSocket连接
                    local_ws = self.local_connections.get(local_task_id)
                    if local_ws and not local_ws.closed:
                        await local_ws.send(json.dumps(local_data))
                        
                        # 如果是Started事件，保存dialog_id映射
                        payload = ali_data.get('payload', {})
                        output = payload.get('output', {})
                        if output.get('event') == 'Started':
                            ali_dialog_id = output.get('dialog_id')
                            if ali_dialog_id:
                                # 生成本地dialog_id并保存映射
                                local_dialog_id = str(uuid.uuid4())
                                self.dialog_mappings[local_dialog_id] = ali_dialog_id
                                
                                print(f"[INFO] 会话已启动，本地dialog_id: {local_dialog_id}, 阿里云dialog_id: {ali_dialog_id}")
                    
                    print(f"[INFO] 已从阿里云转发消息，本地task_id: {local_task_id}")
                except json.JSONDecodeError:
                    print("[ERROR] 无法解析阿里云JSON消息")
                    continue
                except Exception as e:
                    print(f"[ERROR] 处理阿里云消息时出错: {e}")
                    continue
        except websockets.exceptions.ConnectionClosed:
            print(f"[INFO] 阿里云连接已断开，task_id: {local_task_id}")
        except Exception as e:
            print(f"[ERROR] 阿里云连接错误: {e}")

    async def cleanup_local_connection(self, local_ws):
        """清理本地连接资源"""
        # 查找对应的task_id并清理相关资源
        for local_task_id, ws in list(self.local_connections.items()):
            if ws == local_ws:
                # 关闭阿里云连接
                ali_ws = self.ali_connections.get(local_task_id)
                if ali_ws and not ali_ws.closed:
                    await ali_ws.close()
                
                # 清理映射
                self.local_connections.pop(local_task_id, None)
                self.ali_connections.pop(local_task_id, None)
                self.task_mappings.pop(local_task_id, None)
                
                print(f"[INFO] 已清理连接资源，task_id: {local_task_id}")
                break

    def start_local_server(self):
        """启动本地服务器"""
        self.running = True
        print(f"[INFO] 启动本地代理服务器在 {self.local_host}:{self.local_port}")
        print(f"[INFO] 阿里云服务地址: {self.ali_host}")
        
        async def run_server():
            try:
                async with websockets.serve(self.handle_local_client, self.local_host, self.local_port):
                    print(f"[INFO] 本地代理服务器已启动并监听 {self.local_host}:{self.local_port}")
                    await asyncio.Future()  # 保持服务器运行
            except Exception as e:
                print(f"[ERROR] 启动服务器失败: {e}")

        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(run_server())
        except KeyboardInterrupt:
            print("\n[INFO] 正在关闭本地代理服务器...")
        finally:
            loop.close()
            print("[INFO] 本地代理服务器已关闭")


def main():
    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误: DASHSCOPE_API_KEY 环境变量未设置")
        print("请设置您的阿里云API密钥:")
        print("export DASHSCOPE_API_KEY='your-api-key-here'")
        return
    
    # 创建并启动客户端
    client = AliyunRealtimeMultimodalClient(
        local_host="localhost", 
        local_port=8765  # 保持与测试文件相同的端口
    )
    client.start_local_server()


if __name__ == "__main__":
    main()