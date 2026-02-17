"""
抖音直播数字人服务
整合抖音直播消息和数字人系统
"""

import asyncio
import logging
from typing import Optional
from .douyin_live_client import DouyinLiveClient

logger = logging.getLogger(__name__)


class DouyinLiveService:
    """抖音直播数字人服务"""
    
    def __init__(self, agent_pool, tts_engine_pool):
        """
        初始化服务
        
        Args:
            agent_pool: Agent引擎池（用于生成回答）
            tts_engine_pool: TTS引擎池（用于语音合成）
        """
        self.agent_pool = agent_pool
        self.tts_engine_pool = tts_engine_pool
        self.douyin_client: Optional[DouyinLiveClient] = None
        self.is_running = False
        
        # 配置
        self.auto_reply = True  # 是否自动回复
        self.reply_to_gifts = False  # 是否回复礼物感谢
        self.welcome_new_members = False  # 是否欢迎新观众
        
    async def start(
        self,
        client_key: str,
        client_secret: str,
        access_token: str,
        room_id: str,
        agent_name: str = "OpenAI",
        tts_engine: str = "EdgeTTS"
    ):
        """
        启动抖音直播服务
        
        Args:
            client_key: 抖音应用Client Key
            client_secret: 抖音应用Client Secret
            access_token: 用户授权Token
            room_id: 直播间ID
            agent_name: 使用的Agent引擎名称
            tts_engine: 使用的TTS引擎名称
        """
        logger.info("[DouyinLiveService] 启动服务...")
        
        # 初始化抖音客户端
        self.douyin_client = DouyinLiveClient(
            client_key=client_key,
            client_secret=client_secret,
            access_token=access_token
        )
        
        # 绑定消息处理回调
        self.douyin_client.on_comment = lambda user, content: asyncio.create_task(
            self._handle_question(user, content, agent_name, tts_engine)
        )
        self.douyin_client.on_gift = lambda user, gift, count: asyncio.create_task(
            self._handle_gift(user, gift, count, agent_name, tts_engine)
        )
        self.douyin_client.on_member = lambda user: asyncio.create_task(
            self._handle_new_member(user, agent_name, tts_engine)
        )
        
        # 启动监听
        self.is_running = True
        await self.douyin_client.start(room_id)
        
    async def stop(self):
        """停止服务"""
        logger.info("[DouyinLiveService] 停止服务...")
        self.is_running = False
        if self.douyin_client:
            await self.douyin_client.stop()
    
    async def _handle_question(
        self,
        user: dict,
        question: str,
        agent_name: str,
        tts_engine: str
    ):
        """
        处理观众提问
        
        Args:
            user: 用户信息
            question: 问题内容
            agent_name: Agent引擎名称
            tts_engine: TTS引擎名称
        """
        if not self.auto_reply:
            return
        
        nickname = user.get('nickname', '观众')
        logger.info(f"[DouyinLiveService] 处理提问 - {nickname}: {question}")
        
        try:
            # 1. 使用Agent生成回答
            agent = self.agent_pool.get_engine(agent_name)
            if not agent:
                logger.error(f"[DouyinLiveService] Agent引擎 {agent_name} 不存在")
                return
            
            # 构造prompt（可以加入角色设定）
            prompt = f"观众 {nickname} 问: {question}\n请简洁回答（控制在50字以内）："
            
            # 调用Agent生成回答
            response = ""
            async for chunk in agent.chat_completions(
                messages=[{"role": "user", "content": prompt}],
                model="",  # 使用默认模型
                stream=True
            ):
                if chunk:
                    response += chunk
            
            logger.info(f"[DouyinLiveService] 生成回答: {response}")
            
            # 2. 使用TTS合成语音
            tts = self.tts_engine_pool.get_engine(tts_engine)
            if not tts:
                logger.error(f"[DouyinLiveService] TTS引擎 {tts_engine} 不存在")
                return
            
            # 合成语音
            audio_data = await tts.synthesize(response)
            
            # 3. 通过WebSocket发送给前端播放
            # TODO: 需要添加WebSocket消息发送逻辑
            # 格式: {"type": "live_answer", "user": nickname, "question": question, "answer": response, "audio": audio_data}
            
            logger.info(f"[DouyinLiveService] 已回答 {nickname} 的问题")
            
        except Exception as e:
            logger.error(f"[DouyinLiveService] 处理提问失败: {e}")
    
    async def _handle_gift(
        self,
        user: dict,
        gift_name: str,
        count: int,
        agent_name: str,
        tts_engine: str
    ):
        """
        处理礼物消息
        
        Args:
            user: 用户信息
            gift_name: 礼物名称
            count: 数量
            agent_name: Agent引擎名称
            tts_engine: TTS引擎名称
        """
        if not self.reply_to_gifts:
            return
        
        nickname = user.get('nickname', '观众')
        logger.info(f"[DouyinLiveService] 处理礼物 - {nickname} 送了 {count}个{gift_name}")
        
        try:
            # 生成感谢话术
            thanks_messages = [
                f"感谢 {nickname} 送的 {gift_name}！",
                f"谢谢 {nickname} 的 {gift_name}，爱你哦~",
                f"{nickname} 太大方了！谢谢 {gift_name}！",
                f"收到 {nickname} 的 {count}个{gift_name}，么么哒~"
            ]
            
            import random
            thanks = random.choice(thanks_messages)
            
            # 合成语音并播放
            tts = self.tts_engine_pool.get_engine(tts_engine)
            if tts:
                audio_data = await tts.synthesize(thanks)
                # TODO: 发送给前端播放
                
            logger.info(f"[DouyinLiveService] 已感谢 {nickname}")
            
        except Exception as e:
            logger.error(f"[DouyinLiveService] 处理礼物失败: {e}")
    
    async def _handle_new_member(
        self,
        user: dict,
        agent_name: str,
        tts_engine: str
    ):
        """
        处理新观众进入
        
        Args:
            user: 用户信息
            agent_name: Agent引擎名称
            tts_engine: TTS引擎名称
        """
        if not self.welcome_new_members:
            return
        
        nickname = user.get('nickname', '观众')
        logger.info(f"[DouyinLiveService] 欢迎新观众 - {nickname}")
        
        try:
            # 欢迎话术
            welcome_messages = [
                f"欢迎 {nickname} 来到直播间！",
                f"{nickname} 来啦！欢迎欢迎~",
                f"大家欢迎 {nickname}！"
            ]
            
            import random
            welcome = random.choice(welcome_messages)
            
            # 合成语音并播放
            tts = self.tts_engine_pool.get_engine(tts_engine)
            if tts:
                audio_data = await tts.synthesize(welcome)
                # TODO: 发送给前端播放
                
            logger.info(f"[DouyinLiveService] 已欢迎 {nickname}")
            
        except Exception as e:
            logger.error(f"[DouyinLiveService] 欢迎新观众失败: {e}")
