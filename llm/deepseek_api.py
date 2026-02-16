"""
DeepSeek API 集成模块
连接 DeepSeek 大语言模型
使用官方推荐的OpenAI SDK方式调用
curl https://api.deepseek.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${sk-ae4c5cc9f74e4ea9adaa08d765bcc271}" \
  -d '{
        "model": "deepseek-chat",
        "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Hello!"}
        ],
        "stream": false
      }'
"""

import os
from openai import OpenAI

def generate_response(user_input, conversation_history=None):
    """
    使用 DeepSeek API 生成回复
    
    Args:
        user_input (str): 用户输入
        conversation_history (list): 对话历史，格式为 [{"role": "user", "content": "..."}, ...]
    
    Returns:
        str: 生成的回复
    """
    try:
        # 初始化客户端
        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY', 'sk-ae4c5cc9f74e4ea9adaa08d765bcc271'),
            base_url="https://api.deepseek.com"
        )
        
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
        
        # 发送请求到 DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )
        
        # 提取回复内容
        reply = response.choices[0].message.content
        return reply.strip()
            
    except Exception as e:
        print(f"DeepSeek API 请求错误: {e}")
        return "网络连接出现问题，请稍后再试。"