"""
LLM 路由器模块
根据配置选择使用哪个大语言模型
"""

import os
import importlib.util
import sys

# 添加当前目录到路径中
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 默认模型配置
DEFAULT_LLM = os.environ.get("DEFAULT_LLM", "deepseek")  # 可选: deepseek, doubao, qwen

def generate_response(user_input, conversation_history=None):
    """
    根据配置路由到相应的 LLM API 生成回复
    
    Args:
        user_input (str): 用户输入
        conversation_history (list): 对话历史，格式为 [{"role": "user", "content": "..."}, ...]
    
    Returns:
        str: 生成的回复
    """
    # 获取要使用的模型
    llm_type = DEFAULT_LLM.lower()
    
    try:
        if llm_type == "deepseek":
            # 导入并使用 DeepSeek API
            deepseek_spec = importlib.util.find_spec("deepseek_api")
            if deepseek_spec is None:
                deepseek_spec = importlib.util.spec_from_file_location(
                    "deepseek_api", 
                    os.path.join(current_dir, "deepseek_api.py")
                )
            deepseek_module = importlib.util.module_from_spec(deepseek_spec)
            deepseek_spec.loader.exec_module(deepseek_module)
            return deepseek_module.generate_response(user_input, conversation_history)
            
        elif llm_type == "doubao":
            # 导入并使用 豆包 API
            doubao_spec = importlib.util.find_spec("doubao_api")
            if doubao_spec is None:
                doubao_spec = importlib.util.spec_from_file_location(
                    "doubao_api", 
                    os.path.join(current_dir, "doubao_api.py")
                )
            doubao_module = importlib.util.module_from_spec(doubao_spec)
            doubao_spec.loader.exec_module(doubao_module)
            return doubao_module.generate_response(user_input, conversation_history)
            
        elif llm_type == "qwen":
            # 导入并使用 通义千问 API
            qwen_spec = importlib.util.find_spec("qwen_api")
            if qwen_spec is None:
                qwen_spec = importlib.util.spec_from_file_location(
                    "qwen_api", 
                    os.path.join(current_dir, "qwen_api.py")
                )
            qwen_module = importlib.util.module_from_spec(qwen_spec)
            qwen_spec.loader.exec_module(qwen_module)
            return qwen_module.generate_response(user_input, conversation_history)
            
        else:
            # 默认使用 DeepSeek
            deepseek_spec = importlib.util.find_spec("deepseek_api")
            if deepseek_spec is None:
                deepseek_spec = importlib.util.spec_from_file_location(
                    "deepseek_api", 
                    os.path.join(current_dir, "deepseek_api.py")
                )
            deepseek_module = importlib.util.module_from_spec(deepseek_spec)
            deepseek_spec.loader.exec_module(deepseek_module)
            return deepseek_module.generate_response(user_input, conversation_history)
            
    except ImportError as e:
        print(f"导入 LLM 模块失败: {e}")
        return "系统暂时无法连接到智能大脑，请稍后再试。"
    except Exception as e:
        print(f"LLM 路由错误: {e}")
        return "系统出现了一些问题，请稍后再试。"

def set_default_llm(llm_type):
    """
    设置默认使用的 LLM
    
    Args:
        llm_type (str): LLM 类型 ("deepseek", "doubao", "qwen")
    """
    global DEFAULT_LLM
    DEFAULT_LLM = llm_type.lower()