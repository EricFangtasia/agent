import os
import pytest
from unittest.mock import patch
from intent_detection_by_qwen_plus_dashscope import detect_intent, main


def test_detect_intent():
    """测试意图检测函数"""
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': '你好'}
    ]
    
    # 由于真实的API调用需要网络连接，我们模拟API响应
    with patch('dashscope.Generation.call') as mock_call:
        mock_response = {
            'status_code': 200,
            'output': {
                'choices': [{'message': {'role': 'assistant', 'content': '你好！'}}]
            }
        }
        mock_call.return_value = mock_response
        
        result = detect_intent(
            messages=messages,
            api_key="fake-api-key"
        )
        
        # 验证调用参数
        mock_call.assert_called_once()
        assert result == mock_response


def test_main_function():
    """测试主函数"""
    with patch('dashscope.Generation.call') as mock_call:
        mock_response = {
            'status_code': 200,
            'output': {
                'choices': [{'message': {'role': 'assistant', 'content': '测试响应'}}]
            }
        }
        mock_call.return_value = mock_response
        
        # 运行主函数
        main()
        
        # 验证是否调用了API
        mock_call.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])