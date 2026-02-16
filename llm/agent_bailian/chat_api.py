import os
import json
import base64
from io import BytesIO
import wave

# 检查并导入 Flask 相关库
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("错误: 缺少 Flask 依赖。请运行以下命令安装: pip install flask flask-cors dashscope")
    raise

import dashscope


app = Flask(__name__)
CORS(app)  # 允许跨域请求


def detect_intent(messages, api_key = "sk-ff11853c431f4e9a99766d454b062ca2"
, model="qwen-plus-2025-12-01"):
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
    
    # 添加系统消息到对话开始
    system_message = {
        'role': 'system', 
        'content': '如果用户想让你通过图片回答则返回0，其他时候你是一个语音对话系统，并尽可能的简答问题，返回正常语音助手的简答，'
        + "返回0示例：1，这是什么 2，你看前边风景怎么样形容一下？3，你面前有几个人 ，4，他在做什么 ， 我穿了什么颜色的衣服。 "
    }
    
    # 将系统消息插入到消息列表的开头
    full_messages = [system_message] + messages
    
    dashscope.api_key = api_key
    response = dashscope.Generation.call(
        model=model,
        messages=full_messages,
        result_format='message'
    )
    return response


@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """
    OpenAI风格的聊天完成接口
    """
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        model = data.get('model', 'qwen-plus-2025-12-01')
        stream = data.get('stream', False)
        api_key = os.getenv('DASHSCOPE_API_KEY', 'sk-ff11853c431f4e9a99766d454b062ca2')  # 默认使用硬编码的API key

        if stream:
            # 流式响应
            def generate():
                response = detect_intent(messages, api_key, model)
                if response.status_code == 200:
                    content = response.output.choices[0].message.content
                    # 模拟流式输出
                    for i, char in enumerate(content):
                        chunk = {
                            "id": "chatcmpl-" + str(i),
                            "object": "chat.completion.chunk",
                            "created": i,
                            "model": model,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {"content": char},
                                    "finish_reason": None
                                }
                            ]
                        }
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                    
                    # 发送结束标记
                    end_chunk = {
                        "id": "chatcmpl-end",
                        "object": "chat.completion.chunk",
                        "created": len(content),
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {},
                                "finish_reason": "stop"
                            }
                        ]
                    }
                    yield f"data: {json.dumps(end_chunk, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                else:
                    error_chunk = {
                        "error": {
                            "message": f"API调用出错: {response.code}, {response.message}",
                            "type": "api_error",
                            "code": response.code
                        }
                    }
                    yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
            
            return app.response_class(generate(), mimetype='text/event-stream')
        else:
            # 非流式响应
            response = detect_intent(messages, api_key, model)
            
            if response.status_code == 200:
                assistant_reply = response.output.choices[0].message.content
                
                result = {
                    "id": "chatcmpl-123",
                    "object": "chat.completion",
                    "created": 1677652288,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": assistant_reply
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 9,
                        "completion_tokens": 12,
                        "total_tokens": 21
                    }
                }
                return jsonify(result)
            else:
                return jsonify({
                    "error": {
                        "message": f"API调用出错: {response.code}, {response.message}",
                        "type": "api_error",
                        "code": response.code
                    }
                }), 500
                
    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "api_error"
            }
        }), 500


@app.route('/dashscope/chat/completions', methods=['POST'])
def dashscope_chat_completions():
    """
    直接使用dashscope的聊天完成接口
    """
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        model = data.get('model', 'qwen-plus-2025-12-01')
        api_key = os.getenv('DASHSCOPE_API_KEY', 'sk-ff11853c431f4e9a99766d454b062ca2')  # 默认使用硬编码的API key

        response = detect_intent(messages, api_key, model)
        
        if response.status_code == 200:
            assistant_reply = response.output.choices[0].message.content
            
            result = {
                "request_id": response.request_id,
                "output": {
                    "text": assistant_reply,
                    "finish_reason": "stop"
                },
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            return jsonify(result)
        else:
            return jsonify({
                "error": {
                    "message": f"API调用出错: {response.code}, {response.message}",
                    "type": "api_error",
                    "code": response.code
                }
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "api_error"
            }
        }), 500




@app.route('/v1/audio/speech', methods=['POST'])
def text_to_speech():
    """
    将文本转换为语音
    """
    try:
        # 这里可以集成TTS服务，如edge-tts、pyttsx3等
        # 为了演示，我们返回一个模拟的音频响应
        data = request.get_json()
        text = data.get('input', '')
        voice = data.get('voice', 'zh-CN-XiaoxiaoNeural')
        
        # 这里应该是实际的TTS处理逻辑
        # 暂时返回一个模拟响应，使用ASCII字符
        audio_content = b"Simulated audio content"  # 实际应用中应是真实的音频数据
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        return jsonify({
            "audio": audio_base64
        })
    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "api_error"
            }
        }), 500


@app.route('/v1/audio/transcriptions', methods=['POST'])
def speech_to_text():
    """
    语音转文字
    """
    try:
        # 获取上传的音频文件
        if 'file' not in request.files:
            return jsonify({"error": "没有上传音频文件"}), 400
            
        audio_file = request.files['file']
        
        # 这里应该是实际的ASR处理逻辑
        # 暂时返回一个模拟响应
        transcription = "模拟语音转文字结果"  # 实际应用中应是真实的转录结果
        
        return jsonify({
            "text": transcription
        })
    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "api_error"
            }
        }), 500


@app.route('/v1/models', methods=['GET'])
def list_models():
    """
    列出可用模型
    """
    models = {
        "object": "list",
        "data": [
            {
                "id": "qwen-plus-2025-12-01",
                "object": "model",
                "created": 1677610602,
                "owned_by": "system"
            }
        ]
    }
    return jsonify(models)


@app.route('/v1/conversation', methods=['POST'])
def conversation():
    """
    语音对话接口，结合语音识别和文本生成
    """
    try:
        data = request.get_json()
        
        # 获取对话历史，如果不存在则创建一个空列表
        messages = data.get('messages', [])
        
        # 如果messages为空且没有单独的message字段，则返回错误
        if not messages:
            user_message = data.get('message', '')
            if not user_message:
                # 如果没有文本消息，尝试进行语音识别
                if 'audio' in data:
                    # 模拟语音识别
                    user_message = "模拟语音转文字结果"
                    messages = [{"role": "user", "content": user_message}]
                else:
                    return jsonify({"error": "缺少消息内容"}), 400
            else:
                # 将单个消息添加到对话历史
                messages = [{"role": "user", "content": user_message}]
        
        model = data.get('model', 'qwen-plus-2025-12-01')
        api_key = os.getenv('DASHSCOPE_API_KEY', 'sk-ff11853c431f4e9a99766d454b062ca2')
        
        # 获取AI回复
        response = detect_intent(messages, api_key, model)
        
        if response.status_code == 200:
            assistant_reply = response.output.choices[0].message.content
            
            # 将AI回复添加到对话历史
            messages.append({"role": "assistant", "content": assistant_reply})
            
            result = {
                "success": True,
                "data": {
                    "response": assistant_reply,
                    "messages": messages,
                    "request_id": response.request_id,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            }
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "error": {
                    "message": f"API调用出错: {response.code}, {response.message}",
                    "type": "api_error",
                    "code": response.code
                }
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "message": str(e),
                "type": "api_error"
            }
        }), 500


def run_api_server(host='0.0.0.0', port=8000):
    """
    启动API服务器
    """
    print(f"启动API服务器，地址: http://{host}:{port}")
    print("请确保已安装依赖: pip install flask flask-cors dashscope")
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    run_api_server()