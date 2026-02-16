import os
import dashscope


def detect_intent(messages, api_key=None, model="qwen-plus-2025-12-01"):
    """
    使用通义千问API检测意图
    
    Args:
        messages: 对话消息列表
        api_key: API密钥，如果未提供则从环境变量获取
        model: 使用的模型名称
    
    Returns:
        API响应对象
    """
    if api_key is None:
        api_key = os.getenv('DASHSCOPE_API_KEY')
    
    response = dashscope.Generation.call(
        api_key=api_key,
        model=model,
        messages=messages,
        result_format='message'
    )
    return response


def demo_intent_detection(api_key=None):
    """
    演示意图检测功能的函数
    """
    messages = [
        # {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'system', 'content': '如果用户想让你通过图片回答则返回0，其他时候你是一个对话系统，并尽可能的回答问题，返回助手的回答，'
        + "返回0示例：1，这是什么 2，你看前边风景怎么样形容一下？3，你面前有几个人 ，4，他在做什么 ， 我穿了什么颜色的衣服。 "},
        {'role': 'user', 'content': '你看面前的天气怎么样？'},
    ]
    
    # 使用传入的API密钥，也可以从环境变量获取
    response = detect_intent(
        messages=messages,
        api_key=api_key
    )
    print(response)
    return response


def interactive_intent_detection(api_key=None):
    """
    交互式意图检测，支持循环输入和回答
    """
    print("开始交互式意图检测，输入'quit'退出")
    
    # 初始化对话历史
    messages = [
        {'role': 'system', 'content': '如果用户想让你通过图片回答则返回0，其他时候你是一个拟人的对话系统也有情绪，并尽可能快速的简答问题'
        + '返回0示例：1，这是什么 2，你看前边风景怎么样形容一下？3，你面前 ，4，他在做什么 5， 我穿了什么颜色的衣服。 '},
    ]
    
    while True:
        user_input = input("\n请输入您的问题 (输入'quit'退出): ")
        
        if user_input.lower() == 'quit':
            print("结束对话")
            break
            
        # 添加用户输入到消息历史
        messages.append({'role': 'user', 'content': user_input})
        
        try:
            # 调用意图检测
            response = detect_intent(
                messages=messages,
                api_key=api_key
            )
            
            if response.status_code == 200:
                # 获取助手回复
                assistant_reply = response.output.choices[0].message.content
                print(f"助手回复: {assistant_reply}")
                
                # 将助手回复添加到对话历史
                messages.append({'role': 'assistant', 'content': assistant_reply})
            else:
                print(f"API调用出错: {response.code}, {response.message}")
                
        except Exception as e:
            print(f"发生错误: {str(e)}")


def main():
    """主函数，演示意图检测功能"""
    # 使用硬编码的API密钥，也可以通过参数传入或从环境变量获取
    api_key = "sk-ff11853c431f4e9a99766d454b062ca2"
    
    # 运行交互式意图检测
    interactive_intent_detection(api_key=api_key)


if __name__ == "__main__":
    main()