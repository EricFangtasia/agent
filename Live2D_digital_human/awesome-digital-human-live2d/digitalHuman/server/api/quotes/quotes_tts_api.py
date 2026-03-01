# -*- coding: utf-8 -*-
'''
名言TTS缓存API - 预生成并持久化存储名言音频
'''

import os
import json
import hashlib
import asyncio
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from digitalHuman.utils import logger
from digitalHuman.engine import EnginePool
from digitalHuman.server.reponse import Response

router = APIRouter(prefix="/quotes")
enginePool = EnginePool()

# 缓存目录
CACHE_DIR = Path("outputs/quotes_tts_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 映射文件
MAPPING_FILE = CACHE_DIR / "quotes_mapping.json"

class QuoteTTSRequest(BaseModel):
    text: str
    index: Optional[int] = None  # 名言编号

class PreloadRequest(BaseModel):
    quotes: list  # 名言列表
    start_index: int = 0  # 起始编号

def load_mapping() -> dict:
    """加载映射文件"""
    if MAPPING_FILE.exists():
        with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_mapping(mapping: dict):
    """保存映射文件"""
    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

def get_text_hash(text: str) -> str:
    """获取文本的MD5哈希"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def get_cache_path(index: int) -> Path:
    """获取缓存文件路径"""
    return CACHE_DIR / f"quote_{index:05d}.wav"

async def generate_tts(text: str) -> Optional[bytes]:
    """生成TTS音频"""
    try:
        from digitalHuman.server.core.api_tts_v0_impl import tts_infer
        from digitalHuman.server.models import TTSEngineInput
        from digitalHuman.server.header import HeaderInfo
        from digitalHuman.utils import config
        
        engine = config.SERVER.ENGINES.TTS.DEFAULT
        tts_config = {}
        
        item = TTSEngineInput(
            engine=engine,
            config=tts_config,
            text=text
        )
        header = HeaderInfo()
        
        output = await tts_infer(header, item)
        if output and output.data:
            # 解码base64音频
            import base64
            audio_data = base64.b64decode(output.data)
            return audio_data
    except Exception as e:
        logger.error(f"[QuotesTTS] 生成TTS失败: {e}")
    return None

# ========================= 获取缓存状态 ===========================
@router.get("/cache/status")
async def get_cache_status():
    """获取缓存状态"""
    mapping = load_mapping()
    cached_count = len([f for f in CACHE_DIR.glob("quote_*.wav")])
    
    return JSONResponse({
        "code": 0,
        "data": {
            "cached_count": cached_count,
            "mapping_count": len(mapping),
            "cache_dir": str(CACHE_DIR)
        }
    })

# ========================= 预生成名言TTS ===========================
@router.post("/cache/preload")
async def preload_quotes(request: PreloadRequest):
    """预生成名言TTS缓存"""
    mapping = load_mapping()
    results = []
    success_count = 0
    
    for i, quote_text in enumerate(request.quotes):
        index = request.start_index + i
        
        # 检查是否已缓存
        cache_path = get_cache_path(index)
        if cache_path.exists():
            mapping[str(index)] = {
                "text": quote_text[:50] + "..." if len(quote_text) > 50 else quote_text,
                "hash": get_text_hash(quote_text),
                "cached": True
            }
            results.append({"index": index, "status": "already_cached"})
            success_count += 1
            continue
        
        # 生成TTS
        audio_data = await generate_tts(quote_text)
        if audio_data:
            # 保存WAV文件
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
            
            mapping[str(index)] = {
                "text": quote_text[:50] + "..." if len(quote_text) > 50 else quote_text,
                "hash": get_text_hash(quote_text),
                "cached": True
            }
            results.append({"index": index, "status": "success"})
            success_count += 1
            logger.info(f"[QuotesTTS] 缓存成功: {index}")
        else:
            results.append({"index": index, "status": "failed"})
            logger.error(f"[QuotesTTS] 缓存失败: {index}")
        
        # 每10个保存一次映射
        if (i + 1) % 10 == 0:
            save_mapping(mapping)
    
    save_mapping(mapping)
    
    return JSONResponse({
        "code": 0,
        "data": {
            "total": len(request.quotes),
            "success": success_count,
            "results": results
        }
    })

# ========================= 获取单个名言TTS ===========================
@router.get("/cache/{index}")
async def get_quote_tts(index: int, text: Optional[str] = None):
    """获取名言TTS缓存，如果不存在则生成"""
    cache_path = get_cache_path(index)
    
    # 如果缓存存在，直接返回
    if cache_path.exists():
        return FileResponse(
            cache_path,
            media_type="audio/wav",
            filename=f"quote_{index}.wav"
        )
    
    # 如果缓存不存在但有文本，生成
    if text:
        audio_data = await generate_tts(text)
        if audio_data:
            # 保存缓存
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
            
            # 更新映射
            mapping = load_mapping()
            mapping[str(index)] = {
                "text": text[:50] + "..." if len(text) > 50 else text,
                "hash": get_text_hash(text),
                "cached": True
            }
            save_mapping(mapping)
            
            return FileResponse(
                cache_path,
                media_type="audio/wav",
                filename=f"quote_{index}.wav"
            )
    
    return JSONResponse({
        "code": 404,
        "message": "缓存不存在且无法生成"
    }, status_code=404)

# ========================= 批量检查缓存状态 ===========================
@router.post("/cache/check")
async def check_cache(indices: list):
    """批量检查缓存状态"""
    mapping = load_mapping()
    results = {}
    
    for index in indices:
        cache_path = get_cache_path(index)
        results[str(index)] = {
            "cached": cache_path.exists(),
            "path": str(cache_path) if cache_path.exists() else None
        }
    
    return JSONResponse({
        "code": 0,
        "data": results
    })

# ========================= 清除缓存 ===========================
@router.delete("/cache/clear")
async def clear_cache():
    """清除所有缓存"""
    import shutil
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("quote_*.wav"):
            f.unlink()
    
    # 清除映射
    save_mapping({})
    
    return JSONResponse({
        "code": 0,
        "message": "缓存已清除"
    })
