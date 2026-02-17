"""
抖音直播间消息客户端
用于接收和处理抖音直播间的互动消息
"""

import asyncio
import aiohttp
import json
import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DouyinLiveClient:
    """抖音直播间消息客户端"""
    
    # 抖音开放平台API地址
    API_BASE_URL = "https://open.douyin.com"
    
    def __init__(
        self,
        client_key: str,
        client_secret: str,
        access_token: Optional[str] = None
    ):
        """
        初始化抖音直播客户端
        
        Args:
            client_key: 应用的Client Key
            client_secret: 应用的Client Secret
            access_token: 用户授权的Access Token（可选，如果没有会引导授权）
        """
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token = access_token
        self.room_id = None
        self.is_running = False
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 消息处理回调
        self.on_comment: Optional[Callable] = None  # 评论消息
        self.on_gift: Optional[Callable] = None     # 礼物消息
        self.on_member: Optional[Callable] = None   # 进入直播间
        self.on_like: Optional[Callable] = None     # 点赞消息
        
    async def start(self, room_id: str):
        """
        启动直播间消息监听
        
        Args:
            room_id: 直播间ID
        """
        self.room_id = room_id
        self.is_running = True
        self.session = aiohttp.ClientSession()
        
        logger.info(f"[DouyinLive] 开始监听直播间: {room_id}")
        
        try:
            # 验证Access Token
            if not await self._verify_token():
                logger.error("[DouyinLive] Access Token验证失败")
                return
            
            # 启动消息拉取循环
            await self._message_loop()
            
        except Exception as e:
            logger.error(f"[DouyinLive] 启动失败: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """停止监听"""
        self.is_running = False
        if self.session:
            await self.session.close()
        logger.info("[DouyinLive] 已停止监听")
    
    async def _verify_token(self) -> bool:
        """验证Access Token是否有效"""
        if not self.access_token:
            logger.error("[DouyinLive] 缺少Access Token，请先完成授权")
            logger.info("[DouyinLive] 授权流程：")
            logger.info(f"1. 访问授权页面: {self.API_BASE_URL}/platform/oauth/connect")
            logger.info(f"2. 参数: client_key={self.client_key}&response_type=code&scope=user_info,live_data&redirect_uri=YOUR_CALLBACK_URL")
            logger.info("3. 用户授权后获取code，然后调用get_access_token方法")
            return False
        
        # TODO: 调用API验证token
        # 这里简化处理，实际需要调用 /oauth/userinfo/ 接口验证
        return True
    
    async def _message_loop(self):
        """消息拉取循环"""
        last_message_id = None
        
        while self.is_running:
            try:
                # 拉取新消息
                messages = await self._fetch_messages(last_message_id)
                
                # 处理每条消息
                for msg in messages:
                    await self._handle_message(msg)
                    last_message_id = msg.get('msg_id')
                
                # 等待一段时间再拉取（避免频繁请求）
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"[DouyinLive] 消息循环错误: {e}")
                await asyncio.sleep(5)
    
    async def _fetch_messages(self, after_msg_id: Optional[str] = None) -> list:
        """
        拉取直播间消息
        
        Args:
            after_msg_id: 上次消息ID，用于增量拉取
            
        Returns:
            消息列表
        """
        # 注意：这里使用的是示例API，实际抖音开放平台API可能不同
        # 需要根据官方文档调整
        url = f"{self.API_BASE_URL}/api/live/message/list/"
        
        params = {
            "access_token": self.access_token,
            "room_id": self.room_id,
        }
        
        if after_msg_id:
            params["after_msg_id"] = after_msg_id
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', {}).get('messages', [])
                else:
                    logger.error(f"[DouyinLive] API请求失败: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"[DouyinLive] 请求错误: {e}")
            return []
    
    async def _handle_message(self, msg: Dict[str, Any]):
        """
        处理单条消息
        
        Args:
            msg: 消息数据
        """
        msg_type = msg.get('type')
        
        try:
            if msg_type == 'comment':
                # 评论消息（观众提问）
                user = msg.get('user', {})
                content = msg.get('content', '')
                
                logger.info(f"[DouyinLive] 评论 - {user.get('nickname')}: {content}")
                
                if self.on_comment:
                    await self.on_comment(user, content)
                    
            elif msg_type == 'gift':
                # 礼物消息
                user = msg.get('user', {})
                gift_name = msg.get('gift', {}).get('name', '')
                count = msg.get('count', 1)
                
                logger.info(f"[DouyinLive] 礼物 - {user.get('nickname')} 送了 {count}个{gift_name}")
                
                if self.on_gift:
                    await self.on_gift(user, gift_name, count)
                    
            elif msg_type == 'member':
                # 进入直播间
                user = msg.get('user', {})
                
                logger.info(f"[DouyinLive] 进入 - {user.get('nickname')} 进入直播间")
                
                if self.on_member:
                    await self.on_member(user)
                    
            elif msg_type == 'like':
                # 点赞消息
                user = msg.get('user', {})
                count = msg.get('count', 1)
                
                if self.on_like:
                    await self.on_like(user, count)
                    
        except Exception as e:
            logger.error(f"[DouyinLive] 消息处理错误: {e}")
    
    async def get_access_token(self, code: str) -> Optional[str]:
        """
        通过授权码获取Access Token
        
        Args:
            code: 授权码
            
        Returns:
            Access Token
        """
        url = f"{self.API_BASE_URL}/oauth/access_token/"
        
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        access_token = result.get('data', {}).get('access_token')
                        self.access_token = access_token
                        logger.info("[DouyinLive] Access Token获取成功")
                        return access_token
                    else:
                        logger.error(f"[DouyinLive] 获取Token失败: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"[DouyinLive] 获取Token错误: {e}")
            return None


# ============ 使用示例 ============

async def example_usage():
    """使用示例"""
    
    # 初始化客户端
    client = DouyinLiveClient(
        client_key="YOUR_CLIENT_KEY",
        client_secret="YOUR_CLIENT_SECRET",
        access_token="YOUR_ACCESS_TOKEN"  # 如果已有token
    )
    
    # 定义消息处理回调
    async def handle_comment(user, content):
        """处理评论消息（观众提问）"""
        nickname = user.get('nickname', '观众')
        print(f"收到提问 - {nickname}: {content}")
        
        # TODO: 这里调用大模型生成回答
        # TODO: 然后让数字人语音播报
        
    # 绑定回调
    client.on_comment = handle_comment
    
    # 启动监听
    await client.start(room_id="YOUR_ROOM_ID")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_usage())
