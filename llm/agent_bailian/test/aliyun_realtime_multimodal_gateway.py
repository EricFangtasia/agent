#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
阿里云实时多模态交互网关

这个网关将作为本地客户端和阿里云实时多模态交互服务之间的桥梁，
实现协议转换和消息转发。
"""

import asyncio
import json
import uuid
import websockets
import os
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class TaskMapping:
    local_task_id: str
    ali_task_id: str
    ali_dialog_id: Optional[str] = None
    local_dialog_id: Optional[str] = None


class AliyunRealtimeMultimodalGateway:
    def __init__(self, ali_host="wss://dashscope.aliyuncs.com/api-ws/v1/inference", 
                 local_host="localhost", local_port=8765):
        self.ali_host = ali_host
        self.local_host = local_host
        self.local_port = local_port
        self.api_key = os.getenv("DASHSCOPE_API_KEY")  # 从环境变量获取API密钥
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")
        
        # 存储连接和映射关系
        self.local_connections: Dict[str, Any] = {}  # local_task_id -> websocket
        self.ali_connections: Dict[str, Any] = {}   # local_task_id -> websocket
        self.task_mappings: Dict[str, TaskMapping] = {}  # local_task_id -> TaskMapping
        self.running = False

    async def handle_local_client(self, local_websocket):
        """处理本地客户端连接"""
        logger.info(f"本地客户端连接: {local_websocket.remote_address}")
        
        try:
            async for message in local_websocket:
                try:
                    data = json.loads(message)
                    await self.process_local_message(local_websocket, data)
                except json.JSONDecodeError:
                    logger.error("无法解析本地客户端JSON消息")
                    continue
                except Exception as e:
                    logger.error(f"处理本地消息时出错: {e}")
                    continue
        except websockets.exceptions.ConnectionClosed:
            logger.info("本地客户端断开连接")
        except Exception as e:
            logger.error(f"本地连接处理错误: {e}")
        finally:
            await self.cleanup_connection(local_websocket)

    async def process_local_message(self, local_ws, data: dict):
        """处理来自本地客户端的消息"""
        header = data.get('header', {})
        local_task_id = header.get('task_id')
        
        if not local_task_id:
            logger.warning("消息缺少task_id")
            return
        
        # 获取或创建阿里云连接
        ali_ws = await self.get_or_create_ali_connection(local_task_id)
        if not ali_ws:
            logger.error(f"无法创建阿里云连接，task_id: {local_task_id}")
            return
        
        # 获取或创建任务映射
        task_map = self.task_mappings.get(local_task_id)
        if not task_map:
            ali_task_id = str(uuid.uuid4())
            task_map = TaskMapping(
                local_task_id=local_task_id,
                ali_task_id=ali_task_id
            )
            self.task_mappings[local_task_id] = task_map
        else:
            ali_task_id = task_map.ali_task_id
        
        # 转换消息为阿里云格式
        ali_message = self.convert_local_to_ali(data, ali_task_id)
        
        try:
            await ali_ws.send(json.dumps(ali_message))
            logger.info(f"已转发消息到阿里云，本地task_id: {local_task_id}, 阿里云task_id: {ali_task_id}")
        except Exception as e:
            logger.error(f"发送到阿里云失败: {e}")

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
            
            logger.info("已连接到阿里云服务")
            return ali_ws
        except Exception as e:
            logger.error(f"无法连接到阿里云服务: {e}")
            return None

    def convert_local_to_ali(self, local_data: dict, ali_task_id: str) -> dict:
        """将本地消息格式转换为阿里云格式"""
        header = local_data.get('header', {})
        ali_header = {
            "action": header.get('action'),
            "task_id": ali_task_id,
            "streaming": header.get('streaming', 'duplex')
        }
        
        ali_payload = local_data.get('payload', {})
        
        # 如果是Start消息，确保包含必需的参数
        if ali_payload.get('input', {}).get('directive') == 'Start':
            # 添加阿里云所需的参数
            params = ali_payload.setdefault('parameters', {})
            upstream = params.setdefault('upstream', {})
            upstream.setdefault('type', 'AudioOnly')
            upstream.setdefault('mode', 'duplex')
            upstream.setdefault('sample_rate', 16000)
        
        return {
            "header": ali_header,
            "payload": ali_payload
        }

    def convert_ali_to_local(self, ali_data: dict, local_task_id: str) -> dict:
        """将阿里云消息格式转换为本地格式"""
        header = ali_data.get('header', {})
        ali_task_id = header.get('task_id', '')
        
        # 查找对应的本地task_id
        actual_local_task_id = local_task_id
        for tid, tmap in self.task_mappings.items():
            if tmap.ali_task_id == ali_task_id:
                actual_local_task_id = tid
                break
        
        local_header = {
            "event": header.get('event', ''),
            "task_id": actual_local_task_id
        }
        
        local_payload = ali_data.get('payload', {})
        output = local_payload.get('output', {})
        
        # 如果是Started事件，保存dialog_id映射
        if output.get('event') == 'Started':
            ali_dialog_id = output.get('dialog_id')
            if ali_dialog_id:
                task_map = self.task_mappings[actual_local_task_id]
                local_dialog_id = str(uuid.uuid4())
                task_map.local_dialog_id = local_dialog_id
                task_map.ali_dialog_id = ali_dialog_id
                
                # 更新payload中的dialog_id
                local_payload['output']['dialog_id'] = local_dialog_id
                logger.info(f"会话已启动，本地dialog_id: {local_dialog_id}, 阿里云dialog_id: {ali_dialog_id}")
        elif 'dialog_id' in output:
            # 替换dialog_id为本地ID
            ali_dialog_id = output['dialog_id']
            task_map = self.task_mappings.get(actual_local_task_id)
            if task_map and task_map.ali_dialog_id == ali_dialog_id:
                output['dialog_id'] = task_map.local_dialog_id
                local_payload['output'] = output
        
        return {
            "header": local_header,
            "payload": local_payload
        }

    async def forward_from_ali_to_local(self, local_task_id: str, ali_ws):
        """从阿里云转发消息到本地客户端"""
        try:
            async for message in ali_ws:
                try:
                    ali_data = json.loads(message)
                    local_data = self.convert_ali_to_local(ali_data, local_task_id)
                    
                    # 获取本地WebSocket连接
                    local_ws = self.local_connections.get(local_task_id)
                    if local_ws and not local_ws.closed:
                        await local_ws.send(json.dumps(local_data))
                    
                    logger.info(f"已从阿里云转发消息，本地task_id: {local_task_id}")
                except json.JSONDecodeError:
                    logger.error("无法解析阿里云JSON消息")
                    continue
                except Exception as e:
                    logger.error(f"处理阿里云消息时出错: {e}")
                    continue
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"阿里云连接已断开，task_id: {local_task_id}")
        except Exception as e:
            logger.error(f"阿里云连接错误: {e}")

    async def cleanup_connection(self, local_ws):
        """清理连接资源"""
        # 查找对应的task_id并清理相关资源
        for local_task_id, ws in list(self.local_connections.items()):
            if ws == local_ws:
                logger.info(f"清理连接资源，task_id: {local_task_id}")
                
                # 关闭阿里云连接
                ali_ws = self.ali_connections.get(local_task_id)
                if ali_ws and not ali_ws.closed:
                    try:
                        await ali_ws.close()
                    except Exception as e:
                        logger.error(f"关闭阿里云连接失败: {e}")
                
                # 清理映射
                self.local_connections.pop(local_task_id, None)
                self.ali_connections.pop(local_task_id, None)
                self.task_mappings.pop(local_task_id, None)
                
                logger.info(f"已清理连接资源，task_id: {local_task_id}")
                break

    def start_local_server(self):
        """启动本地服务器"""
        self.running = True
        logger.info(f"启动本地代理服务器在 {self.local_host}:{self.local_port}")
        logger.info(f"阿里云服务地址: {self.ali_host}")
        
        async def run_server():
            try:
                async with websockets.serve(self.handle_local_client, self.local_host, self.local_port):
                    logger.info(f"本地代理服务器已启动并监听 {self.local_host}:{self.local_port}")
                    await asyncio.Future()  # 保持服务器运行
            except Exception as e:
                logger.error(f"启动服务器失败: {e}")

        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(run_server())
        except KeyboardInterrupt:
            logger.info("正在关闭本地代理服务器...")
        finally:
            loop.close()
            logger.info("本地代理服务器已关闭")


def main():
    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.error("DASHSCOPE_API_KEY 环境变量未设置")
        logger.info("请设置您的阿里云API密钥:")
        logger.info("export DASHSCOPE_API_KEY='your-api-key-here'")
        return
    
    # 创建并启动网关
    gateway = AliyunRealtimeMultimodalGateway(
        local_host="localhost", 
        local_port=8765  # 保持与测试文件相同的端口
    )
    gateway.start_local_server()


if __name__ == "__main__":
    main()