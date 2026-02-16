import os
import base64
from dashscope import MultiModalConversation
import dashscope

import time

def call_multimodal_model(api_key, base64_image, user_text, system_prompt=None):
    print("qwen3_omni_flash_multimodal.call_multimodal_model 开始多模态查询")
    """
    调用多模态模型的接口函数
    
    Args:
        api_key (str): DashScope API密钥
        base64_image (str): base64编码的图像数据
        user_text (str): 用户输入的文本
        system_prompt (str, optional): 系统提示词，默认为情绪识别相关提示词
    
    Returns:
        dict: 包含响应文本和响应时间的字典
    """
    # 设置默认系统提示词
    if system_prompt is None:
        system_prompt = ('你是一个对话机器人，并按照以下要求尽可能的简答问题（最好在20个字之内），返回助手的回答，'
                        + '如果识别到用户想让你通过图片回答则根据图片回答问题,如：1，这是什么 2，你看前边风景怎么样形容一下？3，你面前有几个人 ，4，他在做什么 ， 我穿了什么颜色的衣服。，其他时候你是一个对话系统，并尽可能简要的回答问题，'
                        + '如果我的输入中有情绪的七维向量值不要把它显示出来，只需要根据情绪值分析我的情绪并给我回复就行了。'
                        + '如果情绪中平静最大则无需根据情绪回答，只需要回答我的问题就行了.')
    
    # 验证并处理base64图像数据
    if base64_image.startswith("data:image"):
        # 如果base64_image已经包含data URL前缀，直接使用
        image_data_url = base64_image
    else:
        # 否则添加data URL前缀
        image_data_url = f"data:image/jpeg;base64,{base64_image}"

    # 构建消息
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {"image": image_data_url},
                {"text": user_text}
            ]
        }
    ]

    # 记录请求开始时间
    start_time = time.time()
    
    try:
        # 调用多模态模型
        response = MultiModalConversation.call(
            api_key=api_key,
            model="qwen3-omni-flash-2025-12-01",
            messages=messages
        )

        # 提取文本内容
        text_content = response.output.choices[0].message.content[0]["text"]
        
        # 计算反应时间
        end_time = time.time()
        response_time = end_time - start_time

        return {
            "text_content": text_content,
            "response_time": response_time,
            "success": True
        }
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        return {
            "error": str(e),
            "response_time": response_time,
            "success": False
        }

# 示例调用
if __name__ == "__main__":
    # 示例调用参数
    API_KEY = "sk-0fa1679a354b4bbc8f480f553bc801ad"  # 实际使用时请替换为有效密钥
    
    # 读取图像并转换为base64
    with open("C:\\project\\py\\onnxDemo\\img_emotion_onnx\\train_emotion_model\\dataset\\dataset_images_self\\angry\\angry.png", "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    
    user_query = "他在干啥"
    
    result = call_multimodal_model(API_KEY, base64_image, user_query)
    
    if result["success"]:
        print(result["text_content"])
        print(f"\n反应时间: {result['response_time']:.2f}秒")
    else:
        print(f"请求失败: {result['error']}")
        print(f"反应时间: {result['response_time']:.2f}秒")