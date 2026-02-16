import os
import json
from threading import Thread
import base64
from io import BytesIO
import wave
import tempfile
import uuid
import soundfile as sf
import numpy as np
import time  # 添加time模块用于计算响应时间

# 检查并导入 Flask 相关库
try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
except ImportError:
    print("错误: 缺少 Flask 依赖。请运行以下命令安装: pip install flask flask-cors dashscope")
    raise

# 检查并导入情绪检测相关库
try:
    import sys
    import os
    # 添加情绪检测模块所在的目录到Python路径
    emotion_module_path = os.path.join(os.path.dirname(__file__), '../../../onnxDemo/img_emotion_onnx')
    if emotion_module_path not in sys.path:
        sys.path.append(emotion_module_path)
    from emotion_detection_onnx import get_emotion_analysis_text
except ImportError as e:
    print(f"警告: 无法导入情绪检测模块: {e}")
    get_emotion_analysis_text = None
except Exception as e:
    print(f"情绪检测模块导入时发生错误: {e}")
    get_emotion_analysis_text = None

import dashscope

# 定义系统消息作为引用
# old_detect_intent_prompt = {
#     'role': 'system', 
#     'content': '如果用户想让你通过图片回答则返回0，其他时候你是一个对话系统，并尽可能的简答问题，返回助手的回答，'
#     + "返回0示例：1，这是什么 2，你看前边风景怎么样形容一下？3，你面前有几个人 ，4，他在做什么 ， 我穿了什么颜色的衣服。 "
# }


detect_intent_prompt = {
    'role': 'system', 
    'content': '如果用户想让你通过图片回答则返回0，其他时候你是一个对话系统，并尽可能简要的回答问题，'
    + "返回0示例：1，这是什么 2，你看前边风景怎么样形容一下？3，你面前有几个人 ，4，他在做什么 ， 我穿了什么颜色的衣服。 "
}

# all_modalities_prompts = {
#     'role': 'system', 
#     "text": "你是一个对话机器人，并尽可能的回答问题，返回助手的回答",
#     "image": None,
#     "audio": None,
#     "content": "你是一个对话机器人，并尽可能的回答问题，返回助手的回答"
# }
# qwen3-omni-flash-2025-12-01
# 1 对于包含base64图片和文字的输入：
# messages = [
#     {
#         "role": "user",
#         "content": [
#             {
#                 "type": "text", 
#                 "text": "您的问题文字内容"
#             }
#         ]
#     }
# ]
your_base64_image_string = "your_base64_image_string"
base64_img_text_prompts_messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{your_base64_image_string}"  # 这里是base64字符串
                }
            },
            {
                "type": "text", 
                "text": "您的问题文字内容"
            }
        ]
    }
]

# 2 对于只输入文字的输入：
text_prompts_messages = {
    'role': 'system', 
    # 'role': 'user', 

    # 'content': '如果用户想让你通过图片回答则返回0，其他时候你是一个对话系统，并尽可能简要的回答问题，'
    # + "返回0示例：1，这是什么 2，你看前边风景怎么样形容一下？3，你面前有几个人 ，4，他在做什么 ， 我穿了什么颜色的衣服。 "

    'content': '你是一个对话机器人，并按照以下要求尽可能的简答问题，返回助手的回答。'
    + '如果识别到用户想让你通过图片回答则根据图片回答问题,如：1，这是什么 2，你看前边风景怎么样形容一下？3，你面前有几个人 ，4，他在做什么 ， 我穿了什么颜色的衣服。，其他时候你是一个对话系统，并尽可能简要的回答问题，'
    + '如果我的输入中有情绪的七维向量值不要把它显示出来，只需要根据情绪值分析我的情绪并给我回复就行了。'
    + '如果情绪中平静最大则无需根据情绪回答，只需要回答我的问题就行了.',
}

# 3 或者使用多内容格式：
all_modalities_prompts=[
        {
            "role": "system",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg"
                    },
                },
                {"type": "text", "text": "图中描绘的是什么景象？"},
            ],
        },
    ],



# 定义默认API密钥作为引用
HONGXIA_API_KEY = "sk-ff11853c431f4e9a99766d454b062ca2"

# 初始化SenseVoice模型
def initialize_sense_voice_model():
    """
    初始化SenseVoice模型，实现一次加载多次使用
    """
    try:
        from funasr import AutoModel
        import torch
        
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

app = Flask(__name__)
CORS(app, resources={
    r"/v1/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})  # 允许所有源访问API端点


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


def detect_intent(messages, api_key=None, model="qwen-plus-2025-12-01"):
    """
    使用通义千问API检测意图
    
    Args:
        messages: 对话消息列表
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
    
    return data_dict, image_file, audio_file


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


def detect_intent(text, api_key=None, model="qwen-plus-2025-12-01"):
# def detect_intent(text, api_key=None, model="qwen3-omni-flash-2025-12-01"):

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


def detect_emotion(image_base64, api_key=None, model="qwen-plus-2025-12-01"):
    """
    使用本地情绪检测模型检测图片中的情绪
    Args:
        image_base64: base64编码的图片数据
    Returns:
        情绪分析结果文本
    """
    if get_emotion_analysis_text:
        try:
            # 使用本地情绪检测模型
            emotion_result = get_emotion_analysis_text(image_base64)
            return emotion_result
        except Exception as e:
            print(f"本地情绪检测出错: {str(e)}")
            return ""
    else:
        # 如果本地情绪检测不可用，返回错误信息
        return ""

# qwen3_omni_flash_model = "qwen3-omni-flash-2025-12-01"
qwen3_omni_flash_model = "qwen3-omni-flash"


def process_multimodal_query(messages, api_key=None, model=qwen3_omni_flash_model):
    """
    处理多模态查询
    """
    start_time = time.time()
    if api_key is None:
        api_key = os.getenv('DASHSCOPE_API_KEY', HONGXIA_API_KEY)
    
    # 添加系统消息到对话开始
    # base64_img_text_prompts_messages,text_prompts_messages

    messages_with_system = [text_prompts_messages] + messages
    
    # print(f"处理多模态查询，消息内容: {messages_with_system}")  # 添加调试信息
    # 使用视觉语言模型处理多模态输入
    dashscope.api_key = api_key
    try:
        api_start = time.time()
        responses = dashscope.MultiModalConversation.call(
            model=model,
            messages=messages_with_system,
            modalities=["text", "audio"],
            
            audio={"voice": "Cherry", "format": "wav"},
            stream=True,  # 使用流式响应以获取音频
            stream_options={"include_usage": True},  # 根据规范添加此参数
        )
        api_end = time.time()
        print(f"API调用耗时: {api_end - api_start:.2f}秒")
        
        # 对于流式响应，我们需要迭代获取结果
        full_response = ""
        audio_base64 = ""
        
        stream_start = time.time()
        request_id = ""
        for chunk in responses:
            # print(f"接收到响应: {chunk}")  # 添加调试信息
                        # {
            # "status_code": 200,
            # "request_id": "222daf50-f700-41c5-a715-95db009e32af",
            # "code": "",
            # "message": "",
            # "output": {
            #     "text": null,
            #     "finish_reason": null,
            #     "choices": [{
            #     "finish_reason": "null",
            #     "message": {
            #         "role": "assistant",
            #         "content": [{
            #         "audio": {"data": "8foN/YX9t..."}
            #         }]
            #     }
            #     }]
            # }
            # }
            # 根据实际API返回的数据格式处理
            request_id = chunk.request_id
            if 'output' in chunk and 'choices' in chunk['output']:
                choice = chunk['output']['choices'][0]
                message = choice.get('message', {})
                
                # 检查是否有音频数据
                if 'content' in message and isinstance(message['content'], list):
                    for content_item in message['content']:
                        if isinstance(content_item, dict):
                            if 'audio' in content_item and 'data' in content_item['audio']:
                                # 累积音频数据 - 只添加新的数据部分
                                new_audio_data = content_item['audio']['data']
                                # 检查新数据是否是已有数据的一部分
                                if new_audio_data not in audio_base64:
                                    audio_base64 += new_audio_data
                                # print(f"音频数据: {content_item['audio']['data'][:100]}...")  # 只打印前100个字符
                            elif 'text' in content_item:
                                # 累积文本内容
                                new_text = content_item['text']
                                # 检查新文本是否是已有文本的一部分
                                if new_text not in full_response:
                                    full_response += new_text
            # if 'usage' in chunk:
            #     print(f"使用情况: {chunk['usage']}")
        stream_end = time.time()
        messages[0]["content"][1]["image"] = ""
        print(f"请求的messages: {messages}")
        print(f"Request ID: {request_id}")  # 打印requestid

        print(f"流式响应处理耗时: {stream_end - stream_start:.2f}秒")
        
        # 如果有音频数据，保存、播放并返回文件路径
        audio_filename = None
        if audio_base64:
            save_start = time.time()
            try:
                wav_bytes = base64.b64decode(audio_base64)
                audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
                # 生成唯一的音频文件名
                audio_filename = f"response_audio_{uuid.uuid4().hex}.wav"
                sf.write(audio_filename, audio_np, samplerate=24000)  # 采样率固定为24kHz
                print(f"音频已保存为: {audio_filename}")
                
                # 播放音频
                # play_audio_file(audio_filename)
                        
            except Exception as decode_e:
                print(f"解码音频数据失败: {decode_e}")
            save_end = time.time()
            print(f"音频保存和播放耗时: {save_end - save_start:.2f}秒")
        
        print(f"文字回复内容: {full_response}")  # 打印输出的文字内容
        total_time = time.time() - start_time
        print(f"多模态查询总耗时: {total_time:.2f}秒")
        return full_response, audio_filename  # 返回文字回复和音频文件路径
    except Exception as e:
        import traceback
        print(f"处理多模态查询时发生异常: {str(e)}")
        print(f"异常追踪: {traceback.format_exc()}")
        return f"多模态查询失败: {str(e)}"

def play_audio_file(audio_filename):
    """
    播放音频文件
    """
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(audio_filename)
        pygame.mixer.music.play()
        
        # 等待音频播放完成
        while pygame.mixer.get_busy():
            pygame.time.wait(100)
            
    except Exception as e:
        print(f"播放音频时出错: {e}")
        # 如果pygame播放失败，尝试使用playsound
        try:
            from playsound import playsound
            playsound(audio_filename)
        except Exception as play_e:
            print(f"使用playsound播放也失败: {play_e}")


def prepare_response_data(response, audio_filename, data_dict):
    """
    准备响应数据，包括对话历史和音频数据
    """
    # 获取对话历史
    messages_history = data_dict.get('messages', [])
    if not messages_history:
        messages_history = []
    
    # 将AI回复添加到对话历史
    messages_history.append({"role": "assistant", "content": response})
    
    # 准备响应数据
    response_data = {
        "success": True,
        "data": {
            "response": response,
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
        
        print(f"语音转文字结果: {audio_transcription}")  # 添加调试信息
        
        # 步骤3: 使用qwen-plus模型对语音转文字进行意图识别
        # intent_start = time.time()
        # intent_result, intent_response = detect_intent(audio_transcription)
        # intent_end = time.time()
        # print(f"意图识别耗时: {intent_end - intent_start:.2f}秒")
        # print(f"意图识别结果: {intent_result}, 响应: {intent_response}")  # 添加调试信息
        
        # 步骤3: 根据意图识别结果决定后续处理
        # response, audio_filename = process_multimodal_query(messages)

        # if intent_result == 0:
        #     print("意图识别返回0，进行多模态查询")  # 添加调试信息
        #     # 如果意图识别返回0，直接进行多模态查询
        # else:
        # print("意图识别返回非0，进行情绪识别")  # 添加调试信息
        # 如果意图识别返回非0，进行情绪识别（使用图片进行情绪识别）

        emotion_result = detect_emotion(image_base64)
        
        print(f"情绪识别结果: {emotion_result}")  # 添加调试信息
        
        # 将情绪识别结果添加到audio_transcription后
        # 如果emotion_result== "" 则不添加情绪分析结果
        updated_content = f"{audio_transcription}"
        if emotion_result != "":
            updated_content = f"{audio_transcription}\n情绪分析：{emotion_result}"
        # 对于多模态内容，需要特别处理
        if isinstance(messages[0]['content'], list):
            # 如果是多模态内容，替换文本部分
            messages[0]['content'][0]['text'] = updated_content
        else:
            messages[0]['content'] = updated_content
        
        # print("进行多模态查询 ，messages: ", messages)  # 添加调试信息
        # 进行多模态查询
        multimodal_start = time.time()

        response, audio_filename = process_multimodal_query(messages)

        multimodal_end = time.time()
        print(f"多模态查询耗时: {multimodal_end - multimodal_start:.2f}秒")
        
        # 准备响应数据
        response_start = time.time()
        response_data = prepare_response_data(response, audio_filename, data_dict)
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