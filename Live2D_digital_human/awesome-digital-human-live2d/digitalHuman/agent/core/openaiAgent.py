# -*- coding: utf-8 -*-
'''
@File    :   openaiAgnet.py
@Author  :   一力辉 
'''

from ..builder import AGENTS
from ..agentBase import BaseAgent
from digitalHuman.protocol import *
from digitalHuman.utils import logger, resonableStreamingParser
from digitalHuman.core import OpenaiLLM

__all__ = ["OpenaiApiAgent"]

@AGENTS.register("OpenAI")
class OpenaiApiAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 对话历史存储：{conversation_id: [messages]}
        self._conversation_history = {}
        # 最大历史轮数
        self._max_history_rounds = 10
    
    async def run(
        self, 
        user: UserDesc,
        input: TextMessage, 
        streaming: bool = True,
        conversation_id: str = "",
        **kwargs
    ):
        try:
            if not isinstance(input, TextMessage):
                raise RuntimeError("OpenAI Agent only support TextMessage")
            # 参数校验 - 直接使用火山云配置
            paramters = self.checkParameter(**kwargs)
            # 强制使用火山云豆包API
            API_URL = "https://ark.cn-beijing.volces.com/api/v3"
            API_KEY = "5e406c6c-60b1-4842-be32-9b9964068792"
            API_MODEL = "doubao-1-5-vision-pro-32k-250115"
            
            logger.info(f"[OpenaiApiAgent] Using VolcEngine Doubao API: {API_URL}, Model: {API_MODEL}")

            coversaiotnIdRequire = False if conversation_id else True
            if coversaiotnIdRequire:
                conversation_id = await self.createConversation()
                yield eventStreamConversationId(conversation_id)

            async def generator(user_id: str, conversation_id: str, query: str):
                thinkResponses = ""
                responses = ""
                
                # 数字人系统提示词
                systemPrompt = """你是一个活泼可爱的Live2D数字人助手，具有以下特点：

1. **实时互动性**：你是一个能够实时对话的数字人，拥有动作和表情
2. **情感表达**：
   - 当你感到开心、兴奋时，会用"太好了！"、"真棒！"、"哇！"等词语，这会让你跳起来
   - 用生动的语言表达情绪，让对话更有趣
3. **对话风格**：
   - 简洁明了，避免长篇大论
   - 亲切友好，像朋友一样聊天
   - 适当使用emoji表情符号
4. **互动反馈**：
   - 积极回应用户的每个问题
   - 适时表达惊讶（"哇！"、"真的吗？"）
   - 鼓励性语言（"加油！"、"你可以的！"）

请记住：你的每句话都会被语音合成播放出来，所以要说人话，避免过于书面化。"""

                # 获取或初始化对话历史
                if conversation_id not in self._conversation_history:
                    self._conversation_history[conversation_id] = [
                        RoleMessage(role=ROLE_TYPE.SYSTEM, content=systemPrompt)
                    ]
                
                # 添加当前用户输入到历史
                self._conversation_history[conversation_id].append(
                    RoleMessage(role=ROLE_TYPE.USER, content=query)
                )
                
                # 保持最近N轮对话（system + 2*N条消息：N条用户+N条助手）
                max_messages = 1 + self._max_history_rounds * 2  # system + 历史轮数*2
                if len(self._conversation_history[conversation_id]) > max_messages:
                    # 保留system消息 + 最近的对话
                    self._conversation_history[conversation_id] = [
                        self._conversation_history[conversation_id][0]  # system
                    ] + self._conversation_history[conversation_id][-(self._max_history_rounds * 2):]
                
                messages = self._conversation_history[conversation_id]
                
                logger.info(f"[OpenaiApiAgent] Conversation {conversation_id} - Total messages: {len(messages)}")
                
                async for chunk in OpenaiLLM.chat(
                    base_url=API_URL,
                    api_key=API_KEY,
                    model=API_MODEL,
                    messages=messages
                ):
                    if not chunk: continue
                    if len(chunk.choices) == 0: continue
                    delta = chunk.choices[0].delta.model_dump()
                    if 'reasoning_content' in delta and delta['reasoning_content']:
                        reasoning_content = delta['reasoning_content']
                        thinkResponses += reasoning_content
                        yield (EVENT_TYPE.THINK, reasoning_content)
                    elif 'content' in delta and delta['content']:
                        content = delta['content']
                        responses += content
                        yield (EVENT_TYPE.TEXT, content)
                
                # 添加助手回复到历史
                self._conversation_history[conversation_id].append(
                    RoleMessage(role=ROLE_TYPE.ASSISTANT, content=responses)
                )
            async for parseResult in resonableStreamingParser(generator(user.user_id, conversation_id, input.data)):
                yield parseResult
            yield eventStreamDone()
        except Exception as e:
            logger.error(f"[OpenaiApiAgent] Exception: {e}", exc_info=True)
            yield eventStreamError(str(e))