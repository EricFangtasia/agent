"""
通义千问(Qwen) API 集成模块
连接阿里通义千问大语言模型
"""

import requests
import json
import os

# 通义千问 API 配置
QWEN_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "your_qwen_api_key_here")
QWEN_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
QWEN_MODEL = "qwen-plus"  # 或 "qwen-max"、"qwen-turbo" 等根据需要选择

def generate_response(user_input, conversation_history=None):
    """
    使用通义千问 API 生成回复
    
    Args:
        user_input (str): 用户输入
        conversation_history (list): 对话历史，格式为 [{"role": "user", "content": "..."}, ...]
    
    Returns:
        str: 生成的回复
    """
    try:
        # 构建消息历史
        messages = []
        
        # 添加系统提示（可选）
        messages.append({
            "role": "system", 
            "content": "你是一个智能语音助手，使用自然、简洁的语言进行对话。"
        })
        
        # 添加历史对话（如果有）
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加当前用户输入
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        # 构建请求负载
        payload = {
            "model": QWEN_MODEL,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 1024
            }
        }
        
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {QWEN_API_KEY}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable"
        }
        
        # 发送请求到通义千问 API
        response = requests.post(
            QWEN_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 提取回复内容
        if "output" in result and "text" in result["output"]:
            reply = result["output"]["text"]
            return reply.strip()
        elif "output" in result and "choices" in result["output"]:
            reply = result["output"]["choices"][0]["message"]["content"]
            return reply.strip()
        else:
            return "抱歉，我没有理解您的意思，请再说一遍。"
            
    except requests.exceptions.RequestException as e:
        print(f"通义千问 API 请求错误: {e}")
        return "网络连接出现问题，请稍后再试。"
    except KeyError as e:
        print(f"通义千问 API 响应格式错误: {e}")
        return "系统出现了一些问题，请稍后再试。"
    except Exception as e:
        print(f"通义千问 API 未知错误: {e}")
        return "系统出现了一些问题，请稍后再试。"