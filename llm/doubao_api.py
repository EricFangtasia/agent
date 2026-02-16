"""
豆包(Doubao) API 集成模块
连接豆包大语言模型
"""

import requests
import json
import os

# 豆包API URL - 使用火山引擎的正式API地址
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"  

# 豆包模型标识符 - 需要替换为实际的模型ID
DOUBAO_MODEL_ID = "doubao-1-5-vision-pro-32k-250115"  # 请替换为实际的模型ID

# 豆包 API 配置
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY", "5e406c6c-60b1-4842-be32-9b9964068792")
# DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
# DOUBAO_MODEL_ID = "doubao-1-5-pro-32k-250115"  # 请替换为实际的模型ID

def generate_response(user_input, conversation_history=None):
    """
    使用豆包 API 生成回复
    
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
            "model": DOUBAO_MODEL_ID,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        # 设置请求头
        headers = {
            "Authorization": f"Bearer {DOUBAO_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 发送请求到豆包 API
        response = requests.post(
            DOUBAO_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 提取回复内容
        if "choices" in result and len(result["choices"]) > 0:
            reply = result["choices"][0]["message"]["content"]
            return reply.strip()
        else:
            return "抱歉，我没有理解您的意思，请再说一遍。"
            
    except requests.exceptions.RequestException as e:
        print(f"豆包 API 请求错误: {e}")
        return "网络连接出现问题，请稍后再试。"
    except KeyError as e:
        print(f"豆包 API 响应格式错误: {e}")
        return "系统出现了一些问题，请稍后再试。"
    except Exception as e:
        print(f"豆包 API 未知错误: {e}")
        return "系统出现了一些问题，请稍后再试。"