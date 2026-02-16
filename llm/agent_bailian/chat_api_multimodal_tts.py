"""
多模态API服务
支持文本、图片、语音等多种输入方式的AI对话服务
"""

# 标准库导入
import os
import json
from threading import Thread
import base64
from io import BytesIO
import wave
import tempfile
import uuid
import time  # 添加time模块用于计算响应时间
import re
import logging  # 添加logging模块

# 第三方库导入
# Flask相关依赖
try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
except ImportError:
    print("错误: 缺少 Flask 依赖。请运行以下命令安装: pip install flask flask-cors")

# 音频处理相关依赖
try:
    import soundfile as sf
    import numpy as np
except ImportError:
    print("警告: 缺少音频处理依赖。请运行以下命令安装: pip install soundfile numpy")

# DashScope相关依赖
try:
    import dashscope
    from dashscope import Generation, MultiModalConversation
    from dashscope.audio.qwen_tts_realtime import QwenTtsRealtime, QwenTtsRealtimeCallback, AudioFormat
except ImportError:
    print("警告: 缺少DashScope依赖。请运行以下命令安装: pip install dashscope")

# PyAudio依赖
try:
    import pyaudio
except ImportError:
    print("警告: 缺少PyAudio依赖。请运行以下命令安装: pip install pyaudio")

# 语音识别相关依赖
try:
    import sys
    from funasr import AutoModel
    import torch
except ImportError:
    print("警告: 缺少FunASR依赖。请运行以下命令安装: pip install funasr torch")

# Pygame音频播放依赖
try:
    import pygame
except ImportError:
    print("警告: 缺少pygame依赖。请运行以下命令安装: pip install pygame")

# Playsound音频播放依赖
try:
    from playsound import playsound
except ImportError:
    print("警告: 缺少playsound依赖。请运行以下命令安装: pip install playsound")


# 本地模块导入
# 导入call_multimodal_model函数
try:
    from qwen3_omni_flash_multimodal import call_multimodal_model
except ImportError as e:
    print(f"警告: 无法导入call_multimodal_model: {e}")

# 导入新的TTS函数
try:
    import importlib.util
    
    # 构建模块文件的完整路径
    module_path = os.path.join(os.path.dirname(__file__), 'tts_qwen3-tts-flash-realtime_dashscope_test.py')
    
    # 使用importlib.util来导入包含连字符的模块名
    tts_spec = importlib.util.spec_from_file_location(
        "tts_qwen3-tts-flash-realtime_dashscope_test", 
        module_path
    )
    tts_module = importlib.util.module_from_spec(tts_spec)
    tts_spec.loader.exec_module(tts_module)
    synthesize_text_to_speech = tts_module.synthesize_text_to_speech
except Exception as e:
    print(f"警告: 无法导入新的TTS函数: {e}")
    synthesize_text_to_speech = None

# 情绪检测模块导入 - 增强错误处理
get_emotion_analysis_text = None
try:
    # 获取项目根目录路径
    project_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    emotion_module_path = os.path.join(project_root, 'emotion')
    if emotion_module_path not in sys.path:
        sys.path.append(emotion_module_path)
    
    # 尝试导入情绪检测模块
    from emotion_detection_onnx import get_emotion_analysis_text, detect_emotion
    print("情绪检测模块导入成功")
except ImportError as e:
    print(f"警告: 无法导入情绪检测模块: {e}")
   
# 定义系统消息和API密钥
detect_intent_prompt = {
    'role': 'system', 
    'content': '如果用户想让你通过图片回答则返回0，其他时候你是一个对话系统，并尽可能简要的回答问题，'
    + "返回0示例：1，这是什么 2，你看前边风景怎么样形容一下？3，你面前有几个人 ，4，他在做什么 ， 我穿了什么颜色的衣服。 "
}

# 定义默认API密钥
HONGXIA_API_KEY = "sk-0fa1679a354b4bbc8f480f553bc801ad"

# 初始化SenseVoice模型
def initialize_sense_voice_model():
    """
    初始化SenseVoice模型，实现一次加载多次使用
    """
    try:
        # 使用与sensevoice_demo.py中相同的模型路径
        model_path = r"C:\project\py\agent\asr\SenseVoice\models\SenseVoiceSmall"
        
        # 如果模型路径存在，则使用本地模型，否则使用远程模型
        if os.path.exists(model_path):
            model = AutoModel(model=model_path, trust_remote_code=False, disable_update=True)
        else:
            model = AutoModel(model="iic/SenseVoice-small", trust_remote_code=False, disable_update=True)
        
        return model
    except ImportError:
        print("注意：未安装funasr库，语音转文字功能将不可用。请运行: pip install funasr torch")
        return None
    except Exception as e:
        print(f"初始化SenseVoice模型时出错: {str(e)}")
        return None

# 全局模型实例，实现一次加载多次使用
SENSE_VOICE_MODEL = initialize_sense_voice_model()

# 创建Flask应用
app = Flask(__name__)
CORS(app, resources={
    r"/v1/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})  # 允许所有源访问API端点


# 内部辅助函数
def parse_request_data():
    """
    解析请求数据，返回data_dict, image_file, audio_file
    """
    print(f"Content-Type: {request.content_type}")  # 添加调试信息
    # 检查是否是multipart/form-data格式（包含文件）
    if request.content_type and 'multipart/form-data' in request.content_type:
        print("检测到multipart/form-data格式")  # 添加调试信息
        # 获取文本数据
        if 'data' in request.form:
            data_dict = json.loads(request.form['data'])
        else:
            data_dict = {}
            
        # 获取图片
        image_file = request.files.get('image')
        # 获取语音
        audio_file = request.files.get('audio')
        
        print(f"解析到的文件 - image: {bool(image_file)}, audio: {bool(audio_file)}")  # 添加调试信息
    else:
        print("检测到非multipart/form-data格式")  # 添加调试信息
        # 普通JSON请求
        data_dict = request.get_json()
        image_file = None
        audio_file = None
    print(f"解析到的数据: {data_dict}")  # 添加调试信息
    return data_dict, image_file, audio_file



def detect_intent(text, api_key=None, model="qwen-plus-2025-12-01"):
    """
    检测用户意图，如果需要通过图片回答则返回0，否则返回正常对话响应
    """
    start_time = time.time()
    if api_key is None:
        api_key = os.getenv('DASHSCOPE_API_KEY', HONGXIA_API_KEY)
    
    # 构建消息列表
    messages = [detect_intent_prompt, {"role": "user", "content": text}]

    dashscope.api_key = api_key
    try:
        api_start = time.time()
        response = dashscope.Generation.call(
            model=model,
            messages=messages,
            result_format='message'
        )
        api_end = time.time()
        print(f"意图检测API调用耗时: {api_end - api_start:.2f}秒")
        
        if response.status_code == 200:
            assistant_reply = response.output.choices[0].message.content
            # 尝试解析返回值是否为0
            try:
                if assistant_reply.strip() == "0":
                    result_time = time.time() - start_time
                    print(f"意图检测返回0，耗时: {result_time:.2f}秒")
                    return 0, assistant_reply
                else:
                    result_time = time.time() - start_time
                    print(f"意图检测返回非0，耗时: {result_time:.2f}秒")
                    return 1, assistant_reply  # 非0意图
            except:
                result_time = time.time() - start_time
                print(f"意图检测默认返回非0，耗时: {result_time:.2f}秒")
                return 1, assistant_reply  # 默认为非0意图
        else:
            result_time = time.time() - start_time
            print(f"意图检测API失败，耗时: {result_time:.2f}秒")
            return 1, f"意图检测失败: {response.code}, {response.message}"
    except Exception as e:
        result_time = time.time() - start_time
        print(f"意图检测异常，耗时: {result_time:.2f}秒，错误: {str(e)}")
        # 简单的本地意图检测逻辑，如果文本包含图片相关的词则返回0
        if any(keyword in text for keyword in ['这是什么', '看', '图片', '照片', '图像', '照片里', '图里', '前面', '风景', '几个人', '颜色']):
            print("本地意图检测返回0")
            return 0, "0"
        else:
            print("本地意图检测返回非0")
            return 1, "好的，我理解您的问题。"



def process_multimodal_input(audio_file, image_file):
    """
    处理多模态输入（音频和图片），返回结合语音转文字内容和图片的多模态消息
    """
    # 保存上传的音频文件到临时位置
    temp_dir = tempfile.gettempdir()
    temp_filename = os.path.join(temp_dir, f"temp_audio_{uuid.uuid4().hex}.wav")
    
    try:
        audio_file.save(temp_filename)
        
        # 使用全局SenseVoice模型实例进行语音识别
        if SENSE_VOICE_MODEL is not None:
            try:
                # 执行语音识别
                res = SENSE_VOICE_MODEL.generate(
                    input=temp_filename,
                    cache_chunk_on_gpu=True,
                    batch_size=1,
                    merge_vad=True, 
                    merge_length=30
                )
                
                # 提取识别结果
                audio_transcription = res[0]["text"] if res and len(res) > 0 else "语音识别未能提取到文本"
                
            except Exception as e:
                audio_transcription = f"语音识别出错: {str(e)}"
                print(f"语音识别错误: {str(e)}")
        else:
            audio_transcription = "语音识别模型未初始化，请检查funasr库是否已安装"
        
        # 清理ASR结果中的特殊标记
        # audio_transcription = clean_multimodal_text(audio_transcription)
        
        # 将语音转文字结果作为用户消息添加到消息列表
        messages = [{"role": "user", "content": audio_transcription}]
    finally:
        # 清理临时文件
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
    
    # 将图片转换为base64
    image_data = image_file.read()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # 创建多模态消息，结合语音转文字内容和图片
    multimodal_content = [
        {"text": messages[0]['content']},  # 使用索引0访问第一个消息
        {"image": f"data:image/jpeg;base64,{image_base64}"}
    ]
    
    # 更新最后一条消息为多模态消息
    messages[0] = {
        "role": "user",
        "content": multimodal_content
    }
    
    return messages, image_base64


def generate_fallback_response(messages, emotion_result=""):
    """
    生成备用响应，当API不可用时使用
    """
    # 简单的规则基础响应生成
    user_message = messages[0]['content'] if messages and len(messages) > 0 else ""
    
    # 根据用户输入和情绪分析结果生成响应
    if emotion_result:
        fallback_response = f"我理解您的感受。根据图像分析，您可能正在经历{emotion_result}。有什么我可以帮助您的吗？"
    else:
        fallback_response = "我理解您的问题，但目前服务暂时不可用，请稍后再试。"
    
    return fallback_response


def prepare_response_data(response, audio_filename, data_dict):
    """
    准备响应数据，包括对话历史和音频数据
    """
    # 获取对话历史
    messages_history = data_dict.get('messages', [])
    if not messages_history:
        messages_history = []
    
    # 将AI回复添加到对话历史
    # 清理响应文本
    cleaned_response = (response)
    messages_history.append({"role": "assistant", "content": cleaned_response})
    
    # 准备响应数据
    response_data = {
        "success": True,
        "data": {
            "response": cleaned_response,
            "messages": messages_history,
            "usage": {
                "input_tokens": 0,  # 这里应该根据实际API响应更新
                "output_tokens": 0,
                "total_tokens": 0
            }
        }
    }
    
    # 如果有音频文件，将其添加到响应中
    if audio_filename and os.path.exists(audio_filename):
        # 读取音频文件并编码为base64
        with open(audio_filename, 'rb') as audio_file:
            audio_data = audio_file.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        response_data["data"]["audio"] = audio_base64
        response_data["data"]["audio_filename"] = audio_filename
        
        # 在响应发送后删除音频文件
        def cleanup_audio_file():
            if os.path.exists(audio_filename):
                os.remove(audio_filename)
                print(f"已删除临时音频文件: {audio_filename}")
        
        # 使用线程在响应发送后删除文件
        cleanup_thread = Thread(target=cleanup_audio_file)
        cleanup_thread.start()
    
    return response_data


# API路由处理函数
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
        api_key = os.getenv('DASHSCOPE_API_KEY', HONGXIA_API_KEY)  # 默认使用硬编码的API key

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


@app.route('/v1/chat/completions-vl', methods=['POST'])
def chat_completions_with_image():
    """
    支持图片的聊天完成接口
    """
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        model = data.get('model', 'qwen-vl-plus')
        api_key = os.getenv('DASHSCOPE_API_KEY', HONGXIA_API_KEY)  # 默认使用硬编码的API key

        # 调用支持图片的模型
        response = detect_intent_with_image(messages, api_key, model)
        
        if response.status_code == 200:
            # 提取助手回复
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


def detect_intent_with_image(messages, api_key = None, model="qwen-vl-plus"):
    """
    使用通义千问视觉语言模型API检测意图
    
    Args:
        messages: 对话消息列表，可能包含图片
        api_key: API密钥，如果未提供则从环境变量获取或使用默认值
        model: 使用的模型名称
    
    Returns:
        API响应对象
    """
    if api_key is None:
        api_key = os.getenv('DASHSCOPE_API_KEY', HONGXIA_API_KEY)
    
    # 将系统消息插入到消息列表的开头
    full_messages = [detect_intent_prompt] + messages
    
    dashscope.api_key = api_key
    response = dashscope.MultiModalConversation.call(
        model=model,
        messages=full_messages
    )
    return response


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
    语音转文字 - 使用本地SenseVoice模型
    """
    try:
        # 获取上传的音频文件
        if 'file' not in request.files:
            return jsonify({"error": "没有上传音频文件"}), 400
            
        audio_file = request.files['file']
        
        # 保存上传的音频文件到临时位置
        temp_dir = tempfile.gettempdir()
        temp_filename = os.path.join(temp_dir, f"temp_audio_{uuid.uuid4().hex}.wav")
        
        try:
            audio_file.save(temp_filename)
            
            # 使用全局SenseVoice模型实例进行语音识别
            if SENSE_VOICE_MODEL is not None:
                try:
                    # 执行语音识别
                    res = SENSE_VOICE_MODEL.generate(
                        input=temp_filename,
                        cache_chunk_on_gpu=True,
                        batch_size=1,
                        merge_vad=True, 
                        merge_length=30
                    )
                    
                    # 提取识别结果
                    transcription = res[0]["text"] if res and len(res) > 0 else "语音识别未能提取到文本"
                    
                except Exception as e:
                    transcription = f"语音识别出错: {str(e)}"
                    print(f"语音识别错误: {str(e)}")
            else:
                transcription = "语音识别模型未初始化，请检查funasr库是否已安装"
            
            return jsonify({
                "text": transcription
            })
        finally:
            # 清理临时文件
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "api_error"
            }
        }), 500


@app.route('/v1/conversation', methods=['POST'])
def conversation():
    """
    支持图片和语音的多模态对话接口（要求图片和语音必须同时提供，messages可为空）
    """
    start_time = time.time()  # 记录开始时间
    print("收到 /v1/conversation 请求")  # 添加调试信息
    try:
        # 步骤1: 解析请求数据
        parse_start = time.time()
        data_dict, image_file, audio_file = parse_request_data()
        parse_end = time.time()
        print(f"解析请求数据耗时: {parse_end - parse_start:.2f}秒")
        
        print(f"解析到的数据 - data_dict: {bool(data_dict)}, image_file: {bool(image_file)}, audio_file: {bool(audio_file)}")  # 添加调试信息
        
        # 检查是否同时提供了图片和语音文件
        if image_file is None or audio_file is None:
            print("错误：必须同时提供图片和语音文件")  # 添加调试信息
            return jsonify({"error": "必须同时提供图片和语音文件"}), 400
        
        # 步骤2: 处理多模态输入，获取语音转文字结果和图片
        process_start = time.time()
        messages, image_base64 = process_multimodal_input(audio_file, image_file)
        process_end = time.time()
        print(f"处理多模态输入耗时: {process_end - process_start:.2f}秒")
        
        audio_transcription = messages[0]['content'][0]['text'] if isinstance(messages[0]['content'], list) else messages[0]['content']  # 获取语音转文字内容
        # 移除 <|zh|><|NEUTRAL|><|Speech|><|woitn|> 这样的字符串
        # audio_transcription = clean_multimodal_text(audio_transcription)
                
        print(f"语音转文字结果: {audio_transcription}")  # 添加调试信息
        emotion_result = detect_emotion(image_base64, include_prefix=True)
        
        # 将情绪识别结果添加到audio_transcription后
        # 如果emotion_result== "" 则不添加情绪分析结果
        updated_content = f"{audio_transcription} {emotion_result}"
        # 对于多模态内容，需要特别处理
        if isinstance(messages[0]['content'], list):
            # 如果是多模态内容，替换文本部分
            messages[0]['content'][0]['text'] = updated_content
        else:
            messages[0]['content'] = updated_content
        print(f"asr+情绪识别结果 print: {updated_content}")  # 添加调试信息
        # print("进行多模态查询 ，messages: ", messages)  # 添加调试信息
        # 进行多模态查询
        multimodal_start = time.time()
        
        # 检查API密钥是否有效
        # 调用call_multimodal_model
        if call_multimodal_model and image_base64:
            print(f"多模态查询开始")  # 添加调试信息
            result = call_multimodal_model(HONGXIA_API_KEY, image_base64, updated_content)
            print(f"多模态查询结果: {result}")  # 添加调试信息
            if result["success"]:
                response_text = result["text_content"]
            else:
                print(f"call_multimodal_model调用失败: {result['error']}")
                # 尝试使用本地处理作为备用方案
                response_text = "抱歉，多模态处理出现错误。"
        else:
            response_text = "多模态模型未初始化，请检查相关依赖。"
    
        multimodal_end = time.time()
        print(f"多模态查询耗时: {multimodal_end - multimodal_start:.2f}秒")
                
        # 使用TTS将文本转换为语音
        tts_start = time.time()
        if synthesize_text_to_speech is not None:
            # 设置环境变量，确保使用HONGXIA_API_KEY
            original_api_key = os.environ.get('DASHSCOPE_API_KEY')
            os.environ['DASHSCOPE_API_KEY'] = HONGXIA_API_KEY
            
            # 使用新的TTS函数，不播放音频
            try:
                audio_filename = synthesize_text_to_speech(response_text, play_audio=False)
            except Exception as tts_error:
                print(f"TTS合成失败: {str(tts_error)}")
                # 输出具体的错误信息，有助于调试WebSocket连接问题
                import traceback
                print(f"TTS错误详情: {traceback.format_exc()}")
                audio_filename = None
            finally:
                # 恢复原始API密钥（如果存在）
                if original_api_key is not None:
                    os.environ['DASHSCOPE_API_KEY'] = original_api_key
                else:
                    # 如果原来没有设置环境变量，则删除它
                    if 'DASHSCOPE_API_KEY' in os.environ:
                        del os.environ['DASHSCOPE_API_KEY']
        else:
            # 如果新的TTS函数不可用，使用原有的TTS功能
            print("使用备选TTS功能")
            # 原有的TTS功能
            audio_filename = None
        tts_end = time.time()
        print(f"TTS处理耗时: {tts_end - tts_start:.2f}秒")

        # 准备响应数据
        response_start = time.time()
        response_data = prepare_response_data(response_text, audio_filename, data_dict)
        response_end = time.time()
        print(f"准备响应数据耗时: {response_end - response_start:.2f}秒")
        
        total_time = time.time() - start_time
        print(f"返回结果: {response_data['success']}")  # 添加调试信息
        print(f"总响应时间: {total_time:.2f}秒")  # 打印总响应时间
        return jsonify(response_data)

    except Exception as e:
        print(f"处理请求时发生异常: {str(e)}")  # 添加调试信息
        return jsonify({
            "success": False,
            "error": {
                "message": str(e),
                "type": "api_error"
            }
        }), 500


@app.route('/v1/text-image-conversation', methods=['POST'])
def text_image_conversation():
    """
    支持仅文字、仅图片或文字图片组合的多模态对话接口
    """
    start_time = time.time()  # 记录开始时间
    print("收到 /v1/text-image-conversation 请求")  # 添加调试信息
    try:
        # 解析请求数据
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 处理表单数据
            text_content = request.form.get('text', '')
            image_file = request.files.get('image')
            data_dict = json.loads(request.form.get('data', '{}')) if 'data' in request.form else {}
        else:
            # 处理JSON数据
            data_dict = request.get_json()
            text_content = data_dict.get('text', '')
            image_file = None  # JSON请求中不会有文件对象，需要通过其他方式处理

        # 如果是multipart请求，需要特殊处理
        if request.content_type and 'multipart/form-data' in request.content_type:
            text_content = request.form.get('text', '')
            image_file = request.files.get('image')
            data_dict = json.loads(request.form.get('data', '{}')) if 'data' in request.form else {}
        else:
            data_dict = request.get_json() or {}
            text_content = data_dict.get('text', '')
            image_file = None

        print(f"接收到的文本: {text_content[:50]}{'...' if len(text_content) > 50 else ''}")  # 只打印前50个字符
        print(f"接收到的图片: {bool(image_file)}")

        # 验证输入参数
        if not text_content and not image_file:
            return jsonify({"error": "至少需要提供文本或图片之一"}), 400

        # 准备消息格式
        messages = []
        
        if image_file:
            # 读取并转换图片为base64
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 检测图片中的情绪
            emotion_result = detect_emotion(image_base64, include_prefix=True)
            # 构建多模态消息
            if text_content:
                # 同时有文字和图片
                multimodal_content = [
                    {"text": f"{text_content}{emotion_result}" if emotion_result else text_content},
                    {"image": f"data:image/jpeg;base64,{image_base64}"}
                ]
                messages.append({
                    "role": "user",
                    "content": multimodal_content
                })
            else:
                # 只有图片
                multimodal_content = [
                    {"text": f"请描述这张图片{emotion_result}" if emotion_result else "请描述这张图片"},
                    {"image": f"data:image/jpeg;base64,{image_base64}"}
                ]
                messages.append({
                    "role": "user",
                    "content": multimodal_content
                })
        else:
            # 只有文字
            messages.append({
                "role": "user",
                "content": text_content
            })

        # 进行多模态查询
        multimodal_start = time.time()
        
        # 调用call_multimodal_model
        if call_multimodal_model:
            print(f"多模态查询开始")  # 添加调试信息
            # 构建完整的提示内容
            full_content = text_content
            if 'image_base64' in locals() and image_base64:  # 有图片的情况
                result = call_multimodal_model(HONGXIA_API_KEY, image_base64, full_content)
            else:  # 没有图片，只处理文本
                # 调用LLM获取文本回复
                try:
                    response = Generation.call(
                        model='qwen-max',
                        api_key=HONGXIA_API_KEY,
                        prompt=full_content,
                        max_tokens=2000,
                        temperature=0.7
                    )
                    
                    if response.status_code == 200:
                        response_text = response.output.text
                        result = {
                            "success": True,
                            "text_content": response_text
                        }
                    else:
                        print(f"Qwen API调用失败: {response.code}, {response.message}")
                        result = {
                            "success": False,
                            "error": f"API调用失败: {response.message}"
                        }
                except Exception as e:
                    print(f"调用Qwen API时发生异常: {str(e)}")
                    result = {
                        "success": False,
                        "error": str(e)
                    }
            
            print(f"多模态查询结果: {result}")  # 添加调试信息
            if result["success"]:
                response_text = result["text_content"]
            else:
                print(f"call_multimodal_model调用失败: {result['error']}")
                # 使用备用方案生成响应
                response_text = generate_fallback_response(messages, "")
        else:
            print("多模态模型未初始化，使用备用方案生成响应")
            response_text = generate_fallback_response(messages, "")
    
        multimodal_end = time.time()
        print(f"多模态查询耗时: {multimodal_end - multimodal_start:.2f}秒")
                
        # 使用TTS将文本转换为语音（可选）
        tts_start = time.time()
        audio_filename = None
        if synthesize_text_to_speech is not None:
            # 设置环境变量，确保使用HONGXIA_API_KEY
            original_api_key = os.environ.get('DASHSCOPE_API_KEY')
            os.environ['DASHSCOPE_API_KEY'] = HONGXIA_API_KEY
            
            # 使用新的TTS函数，不播放音频
            try:
                audio_filename = synthesize_text_to_speech(response_text, play_audio=False)
            except Exception as tts_error:
                print(f"TTS合成失败: {str(tts_error)}")
                # 输出具体的错误信息，有助于调试WebSocket连接问题
                import traceback
                print(f"TTS错误详情: {traceback.format_exc()}")
                audio_filename = None
            finally:
                # 恢复原始API密钥（如果存在）
                if original_api_key is not None:
                    os.environ['DASHSCOPE_API_KEY'] = original_api_key
                else:
                    # 如果原来没有设置环境变量，则删除它
                    if 'DASHSCOPE_API_KEY' in os.environ:
                        del os.environ['DASHSCOPE_API_KEY']
        tts_end = time.time()
        print(f"TTS处理耗时: {tts_end - tts_start:.2f}秒")

        # 准备响应数据
        response_start = time.time()
        response_data = prepare_response_data(response_text, audio_filename, data_dict)
        response_end = time.time()
        print(f"准备响应数据耗时: {response_end - response_start:.2f}秒")
        
        total_time = time.time() - start_time
        print(f"返回结果: {response_data['success']}")  # 添加调试信息
        print(f"总响应时间: {total_time:.2f}秒")  # 打印总响应时间
        return jsonify(response_data)

    except Exception as e:
        print(f"处理请求时发生异常: {str(e)}")  # 添加调试信息
        return jsonify({
            "success": False,
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
            },
            {
                "id": "qwen-vl-plus",
                "object": "model",
                "created": 1677610602,
                "owned_by": "system"
            }
        ]
    }
    return jsonify(models)


def run_api_server(host='0.0.0.0', port=8080):
    """
    启动API服务器
    """
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # 只显示错误级别的日志
    
    print(f"启动多模态API服务器，地址: http://{host}:{port}")
    # print("请确保已安装依赖: pip install flask flask-cors dashscope")
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    run_api_server()