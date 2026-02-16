import json
import logging
from typing import Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS

# 导入情绪分析技能
from agent.emotion.emotion_analysis_skill import EmotionAnalysisMCP

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

@app.route('/manifest', methods=['GET'])
def get_manifest():
    """
    返回MCP服务的清单信息
    """
    manifest_info = {
        "name": "emotion_analysis",
        "description": "分析图片中的人脸情绪",
        "parameters": {
            "type": "object",
            "properties": {
                "image_base64": {
                    "type": "string",
                    "description": "base64编码的图片数据"
                }
            },
            "required": ["image_base64"]
        }
    }
    return jsonify(manifest_info)


@app.route('/execute', methods=['POST'])
def execute_skill():
    """
    执行情绪分析技能
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
        
        # 调用情绪分析MCP接口
        result = EmotionAnalysisMCP.call(data)
        
        # 返回结果
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"执行情绪分析技能时出错: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"执行情绪分析技能时出错: {str(e)}",
            "result": None
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    """
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    logger.info("启动情绪分析MCP服务，端口: 8089")
    app.run(host='0.0.0.0', port=8089, debug=False)