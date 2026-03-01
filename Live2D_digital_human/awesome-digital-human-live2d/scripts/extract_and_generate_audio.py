# -*- coding: utf-8 -*-
"""
从quotes.tsx提取名言并预生成音频
运行方式: python scripts/extract_and_generate_audio.py
"""

import asyncio
import edge_tts
import os
import json
import re
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path(__file__).parent.parent / "web" / "public" / "quotes_audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# quotes.tsx路径
QUOTES_TSX_PATH = Path(__file__).parent.parent / "web" / "app" / "(products)" / "sentio" / "components" / "news" / "quotes.tsx"

# 音频配置
VOICE = "zh-CN-XiaoxiaoNeural"  # 默认女声
RATE = "+0%"
VOLUME = "+0%"
PITCH = "+0Hz"

def extract_quotes_from_tsx():
    """从quotes.tsx提取名言"""
    with open(QUOTES_TSX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取QUOTES数组
    quotes_match = re.search(r'const QUOTES = \[(.*?)\];', content, re.DOTALL)
    quotes = []
    if quotes_match:
        quotes_content = quotes_match.group(1)
        # 匹配引号中的内容
        quotes = re.findall(r'"(.*?)"', quotes_content)
    
    # 提取RETENTION_SCRIPTS数组
    retention_match = re.search(r'const RETENTION_SCRIPTS = \[(.*?)\];', content, re.DOTALL)
    retention_scripts = []
    if retention_match:
        retention_scripts = re.findall(r'"(.*?)"', retention_match.group(1))
    
    # 提取GIFT_SCRIPTS数组
    gift_match = re.search(r'const GIFT_SCRIPTS = \[(.*?)\];', content, re.DOTALL)
    gift_scripts = []
    if gift_match:
        gift_scripts = re.findall(r'"(.*?)"', gift_match.group(1))
    
    return quotes, retention_scripts, gift_scripts

async def generate_audio(text: str, output_path: Path) -> bool:
    """生成单个音频文件"""
    # 提取名言内容（去掉作者）
    content = text.split('。——')[0] if '。——' in text else text
    
    try:
        communicate = edge_tts.Communicate(
            text=content,
            voice=VOICE,
            rate=RATE,
            volume=VOLUME,
            pitch=PITCH
        )
        
        with open(output_path, 'wb') as f:
            async for message in communicate.stream():
                if message["type"] == "audio":
                    f.write(message["data"])
        return True
    except Exception as e:
        print(f"生成失败: {text[:20]}... - {e}")
        return False

async def main():
    print(f"从 {QUOTES_TSX_PATH} 提取名言...")
    quotes, retention_scripts, gift_scripts = extract_quotes_from_tsx()
    
    print(f"提取结果:")
    print(f"  名言: {len(quotes)} 条")
    print(f"  留人话术: {len(retention_scripts)} 条")
    print(f"  礼物话术: {len(gift_scripts)} 条")
    print(f"输出目录: {OUTPUT_DIR}")
    
    # 创建索引文件
    index_data = {
        "quotes": [],
        "retention_scripts": [],
        "gift_scripts": [],
        "voice": VOICE,
        "total": len(quotes) + len(retention_scripts) + len(gift_scripts)
    }
    
    total = len(quotes) + len(retention_scripts) + len(gift_scripts)
    completed = 0
    
    # 生成名言音频
    print(f"\n开始生成名言音频 ({len(quotes)} 条)...")
    for i, quote in enumerate(quotes):
        filename = f"q_{i:04d}.mp3"
        output_path = OUTPUT_DIR / filename
        
        if output_path.exists():
            print(f"[{i+1}/{len(quotes)}] 已存在: {filename}")
            index_data["quotes"].append({"index": i, "text": quote, "file": filename})
            completed += 1
            continue
        
        success = await generate_audio(quote, output_path)
        if success:
            print(f"[{i+1}/{len(quotes)}] 完成: {filename}")
            index_data["quotes"].append({"index": i, "text": quote, "file": filename})
            completed += 1
        else:
            print(f"[{i+1}/{len(quotes)}] 失败: {quote[:30]}...")
    
    # 生成留人话术音频
    print(f"\n开始生成留人话术音频 ({len(retention_scripts)} 条)...")
    for i, script in enumerate(retention_scripts):
        filename = f"r_{i:04d}.mp3"
        output_path = OUTPUT_DIR / filename
        
        if output_path.exists():
            print(f"[{i+1}/{len(retention_scripts)}] 已存在: {filename}")
            index_data["retention_scripts"].append({"index": i, "text": script, "file": filename})
            completed += 1
            continue
        
        success = await generate_audio(script, output_path)
        if success:
            print(f"[{i+1}/{len(retention_scripts)}] 完成: {filename}")
            index_data["retention_scripts"].append({"index": i, "text": script, "file": filename})
            completed += 1
        else:
            print(f"[{i+1}/{len(retention_scripts)}] 失败: {script[:30]}...")
    
    # 生成礼物话术音频
    print(f"\n开始生成礼物话术音频 ({len(gift_scripts)} 条)...")
    for i, script in enumerate(gift_scripts):
        filename = f"g_{i:04d}.mp3"
        output_path = OUTPUT_DIR / filename
        
        if output_path.exists():
            print(f"[{i+1}/{len(gift_scripts)}] 已存在: {filename}")
            index_data["gift_scripts"].append({"index": i, "text": script, "file": filename})
            completed += 1
            continue
        
        success = await generate_audio(script, output_path)
        if success:
            print(f"[{i+1}/{len(gift_scripts)}] 完成: {filename}")
            index_data["gift_scripts"].append({"index": i, "text": script, "file": filename})
            completed += 1
        else:
            print(f"[{i+1}/{len(gift_scripts)}] 失败: {script[:30]}...")
    
    # 保存索引文件
    index_path = OUTPUT_DIR / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"生成完成!")
    print(f"总计: {total} 条")
    print(f"成功: {completed} 条")
    print(f"失败: {total - completed} 条")
    print(f"索引文件: {index_path}")
    print(f"音频目录: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
