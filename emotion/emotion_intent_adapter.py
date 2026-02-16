import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 情绪分析MCP服务地址
MCP_SERVICE_URL = "http://localhost:8089"


def call_emotion_analysis_service(image_base64):
    """
    调用情绪分析MCP服务
    """
    try:
        payload = {
            "image_base64": image_base64
        }
        
        response = requests.post(
            f"{MCP_SERVICE_URL}/execute",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # 设置超时时间
        )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            logger.error(f"调用情绪分析服务失败: {response.status_code}, {response.text}")
            return {
                "success": False,
                "error": f"服务调用失败: {response.status_code}",
                "result": None
            }
    except Exception as e:
        logger.error(f"调用情绪分析服务时发生异常: {str(e)}")
        return {
            "success": False,
            "error": f"调用服务时发生异常: {str(e)}",
            "result": None
        }


@app.route('/process-intent', methods=['POST'])
def process_intent():
    """
    处理来自阿里云多模态交互开发套件的意图请求
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "请求体不能为空",
                "result": None
            }), 400
        
        # 提取消息和元数据
        message = data.get("message", {})
        metadata = message.get("metadata", {})
        intent_infos = metadata.get("intentInfos", [])
        
        if not intent_infos:
            return jsonify({
                "success": False,
                "error": "未检测到意图信息",
                "result": "抱歉，我没有理解您的意图。"
            })
        
        # 处理每个意图
        responses = []
        for intent_info in intent_infos:
            intent = intent_info.get("intent")
            slots = intent_info.get("slots", [])
            
            # 检查是否是我们支持的意图
            if intent == "emotion-analysis":
                # 从slots中提取参数
                image_base64 = None
                for slot in slots:
                    if slot.get("name") == "image_base64":
                        image_base64 = slot.get("value")
                        break
                
                # 如果没有找到图片数据，尝试从消息中提取
                if not image_base64:
                    parts = message.get("parts", [])
                    for part in parts:
                        if part.get("kind") == "image" and "data" in part:
                            image_base64 = part["data"]
                        elif part.get("kind") == "text":
                            # 如果是文本，检查是否包含base64图片数据
                            text = part.get("text", "")
                            if text.startswith("data:image"):
                                image_base64 = text.split(",")[1] if "," in text else None
                
                if not image_base64:
                    response = {
                        "success": False,
                        "error": "未提供图片数据",
                        "result": "请提供一张图片以进行情绪分析。"
                    }
                else:
                    # 调用情绪分析服务
                    response = call_emotion_analysis_service(image_base64)
                
                responses.append({
                    "intent": intent,
                    "response": response
                })
            else:
                responses.append({
                    "intent": intent,
                    "response": {
                        "success": False,
                        "error": f"不支持的意图: {intent}",
                        "result": f"抱歉，我不支持 '{intent}' 这个功能。"
                    }
                })
        
        # 返回处理结果
        return jsonify({
            "success": True,
            "responses": responses
        })
        
    except Exception as e:
        logger.error(f"处理意图请求时出错: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"处理请求时出错: {str(e)}",
            "result": "处理请求时发生错误。"
        }), 500


@app.route('/agentCard', methods=['GET'])
def get_agent_card():
    """
    返回AgentCard信息，用于阿里云多模态交互开发套件
    """
    agent_card = {
        "name": "emotion_analysis_agent",
        "description": "情绪分析智能代理，能够分析图片中人脸的情绪状态",
        "version": "1.0.0",
        "author": "Emotion Analysis Team",
        "capabilities": {
            "extensions": [
                {
                    "uri": "https://help.aliyun.com/zh/model-studio/multimodal-integration-a2a-intent",
                    "params": {
                        "skills": [
                            {
                                "id": "emotion-analysis",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "image_base64": {
                                            "type": "string",
                                            "description": "Base64编码的图片数据，用于情绪分析"
                                        }
                                    },
                                    "required": ["image_base64"]
                                }
                            }
                        ]
                    }
                }
            ]
        },
        "services": [
            {
                "id": "emotion-mcp-service",
                "name": "情绪分析MCP服务",
                "description": "提供情绪分析能力的MCP服务",
                "endpoint": "http://a9f5d96b.natappfree.cc",  # 修改为natappfree域名
                "type": "mcp"
            }
        ],
        "metadata": {
            "category": "image-processing",
            "tags": ["emotion-detection", "ai", "image-analysis", "multimodal"]
        }
    }
    return jsonify(agent_card)


@app.route('/.well-known/agent.json', methods=['GET'])
def get_agent_json():
    """
    返回Agent配置文件，按照阿里云多模态交互开发套件要求的完整格式
    """
    agent_config = {
        "agentCard": {
            "skills": [
                {
                    "examples": [
                        "示例: 分析这张图片中人脸的情绪"
                    ],
                    "name": "情绪分析",
                    "description": "分析图片中人脸的情绪状态",
                    "id": "emotion-analysis",
                    "tags": [
                        "emotion",
                        "image-analysis",
                        "ai"
                    ]
                }
            ],
            "security": [],
            "capabilities": {
                "extensions": [
                    {
                        "uri": "https://help.aliyun.com/zh/model-studio/multimodal-integration-a2a-protocol"
                    },
                    {
                        "params": {
                            "skills": [
                                {
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "image_base64": {
                                                "description": "Base64编码的图片数据，用于情绪分析",
                                                "type": "string"
                                            }
                                        },
                                        "required": ["image_base64"]
                                    },
                                    "id": "emotion-analysis"
                                }
                            ]
                        },
                        "uri": "https://help.aliyun.com/zh/model-studio/multimodal-integration-a2a-intent"
                    }
                ],
                "streaming": False
            },
            "defaultOutputModes": [
                "text/plain"
            ],
            "name": "情绪分析AI助手",
            "description": "可以分析图片中人脸的情绪状态，支持悲伤、厌恶、生气、中性、恐惧、惊讶、高兴等情绪识别",
            "protocolVersion": "0.2.5",
            "version": "1.0.0",
            "defaultInputModes": [
                "text/plain"
            ],
            "url": "http://a9f5d96b.natappfree.cc"  # 这是natapp的公共URL，需要根据实际部署环境修改
        },
        "skillValidation": [
            {
                "valid": True,
                "id": "emotion-analysis",
                "supportExtension": True
            }
        ],
        "agentValidation": {
            "valid": True,
            "extensionTags": {
                "https://help.aliyun.com/zh/model-studio/multimodal-integration-a2a-protocol": "protocol",
                "https://help.aliyun.com/zh/model-studio/multimodal-integration-a2a-intent": "intent"
            },
            "supportExtension": True
        }
    }
    return jsonify(agent_config)


@app.route('/agentcard', methods=['GET'])
def get_agentcard():
    """
    返回AgentCard信息
    """
    try:
        with open('emotion_analysis_agentcard.json', 'r', encoding='utf-8') as f:
            agentcard = json.load(f)
        return jsonify(agentcard)
    except FileNotFoundError:
        # 尝试使用绝对路径
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'emotion_analysis_agentcard.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                agentcard = json.load(f)
            return jsonify(agentcard)
        except Exception as e:
            logger.error(f"读取AgentCard文件时出错: {str(e)}")
            return jsonify({
                "error": f"读取AgentCard文件时出错: {str(e)}"
            }), 500
    except Exception as e:
        logger.error(f"读取AgentCard文件时出错: {str(e)}")
        return jsonify({
            "error": f"读取AgentCard文件时出错: {str(e)}"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    """
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    logger.info("启动情绪分析意图适配器，端口: 8090")
    app.run(host='0.0.0.0', port=8090, debug=False)