# -*- coding: utf-8 -*-
'''
@File    :   tts_api_v0_impl.py
@Author  :   一力辉
'''


from typing import List, Dict
from digitalHuman.engine import EnginePool, BaseTTSEngine
from digitalHuman.utils import config
from digitalHuman.protocol import ParamDesc, EngineDesc, ENGINE_TYPE, UserDesc, AudioMessage, TextMessage, VoiceDesc
from digitalHuman.server.models import TTSEngineInput

# 导入抖音敏感词过滤
try:
    from digitalHuman.utils.douyin_filter import filter_text_for_douyin
    DOUYIN_FILTER_ENABLED = True
except ImportError:
    DOUYIN_FILTER_ENABLED = False

enginePool = EnginePool()

def get_tts_list() -> List[EngineDesc]:
    engines = enginePool.listEngine(ENGINE_TYPE.TTS)
    return [enginePool.getEngine(ENGINE_TYPE.TTS, engine).desc() for engine in engines]

def get_tts_default() -> EngineDesc:
    return enginePool.getEngine(ENGINE_TYPE.TTS, config.SERVER.ENGINES.TTS.DEFAULT).desc()

async def get_tts_voice(name: str, **kwargs) -> List[VoiceDesc]:
    engine: BaseTTSEngine = enginePool.getEngine(ENGINE_TYPE.TTS, name)
    voices = await engine.voices(**kwargs)
    return voices

def get_tts_param(name: str) -> List[ParamDesc]:
    engine = enginePool.getEngine(ENGINE_TYPE.TTS, name)
    return engine.parameters()

async def tts_infer(user: UserDesc, item: TTSEngineInput) -> AudioMessage:
    if item.engine.lower() == "default":
        item.engine = config.SERVER.ENGINES.TTS.DEFAULT
    
    # 抖音敏感词过滤
    text_data = item.data
    if DOUYIN_FILTER_ENABLED:
        text_data = filter_text_for_douyin(item.data)
    
    input = TextMessage(data=text_data)
    engine = enginePool.getEngine(ENGINE_TYPE.TTS, item.engine)
    output: AudioMessage = await engine.run(input=input, user=user, **item.config)
    return output