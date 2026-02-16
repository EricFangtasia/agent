"""
情绪分析技能模块
提供情绪分析相关的agent技能和MCP接口
"""
import base64
import json
from typing import Dict, Any, Optional


def clean_multimodal_text(text: str) -> str:
    """
    清理多模态文本，移除系统标签和冗余描述
    Args:
        text: 原始文本
    Returns:
        清理后的文本
    """
    import re
    # 移除所有形如<|.*?|>的标签序列
    cleaned_text = re.sub(r'<\|[^|]+\|>', '', text)
    
    # 移除"情绪识别结果:"、"情绪分析结果："等冗余描述
    cleaned_text = re.sub(r'情绪识别结果:\s*', '', cleaned_text)
    cleaned_text = re.sub(r'情绪分析结果:\s*', '', cleaned_text)
    cleaned_text = re.sub(r'主要情绪:\s*', '', cleaned_text)
    cleaned_text = re.sub(r'各情绪类别概率:\s*', '', cleaned_text)
    
    # 清理多余的空白字符
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


def get_emotion_result(image_base64: str) -> str:
    """
    获取情绪分析结果的封装函数
    Args:
        image_base64: base64编码的图片数据
    Returns:
        格式化的情绪分析结果字符串
    """
    # 导入现有的detect_emotion函数
    from agent.emotion.emotion_detection_onnx import detect_emotion, EMOTION_DETECTOR
    
    # 先检测是否存在人脸
    if EMOTION_DETECTOR and not EMOTION_DETECTOR.detect_face_from_base64(image_base64):
        return "图片中未检测到人脸，无法进行情绪分析"
    
    # 调用 detect_emotion 函数，确保 include_prefix=True 来获得完整结果
    result = detect_emotion(image_base64, include_prefix=True)
    
    # 如果结果为空，但模型检测到了人脸，可能是情绪分析结果为空
    if not result and EMOTION_DETECTOR and EMOTION_DETECTOR.detect_face_from_base64(image_base64):
        # 尝试直接获取情绪分析文本
        analysis_text = EMOTION_DETECTOR.get_emotion_analysis_text(image_base64)
        if analysis_text:
            result = f"情绪分析：{analysis_text}"
    
    return result


class EmotionAnalysisSkill:
    """
    情绪分析技能类，提供情绪分析相关的功能
    """
    
    @staticmethod
    def name() -> str:
        """
        返回技能名称
        """
        return "emotion_analysis"
    
    @staticmethod
    def description() -> str:
        """
        返回技能描述
        """
        return "分析图片中的人脸情绪，返回情绪分析结果"
    
    @staticmethod
    def parameters() -> Dict[str, Any]:
        """
        返回技能参数定义
        """
        return {
            "type": "object",
            "properties": {
                "image_base64": {
                    "type": "string",
                    "description": "base64编码的图片数据"
                }
            },
            "required": ["image_base64"]
        }
    
    @staticmethod
    def execute(image_base64: str) -> Dict[str, Any]:
        """
        执行情绪分析技能
        Args:
            image_base64: base64编码的图片数据
        Returns:
            包含情绪分析结果的字典
        """
        try:
            result = get_emotion_result(image_base64)
            return {
                "success": True,
                "result": result,
                "message": "情绪分析完成"
            }
        except Exception as e:
            return {
                "success": False,
                "result": "",
                "message": f"情绪分析失败: {str(e)}"
            }


class EmotionAnalysisMCP:
    """
    情绪分析MCP接口类，提供标准化的多模态通信接口
    """
    
    @staticmethod
    def call(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP标准调用接口
        Args:
            params: 包含调用参数的字典
        Returns:
            包含结果的字典
        """
        try:
            image_base64 = params.get("image_base64", "")
            
            # 验证参数
            if not image_base64:
                return {
                    "success": False,
                    "error": "缺少必需参数: image_base64",
                    "result": None
                }
            
            # 执行情绪分析
            result = get_emotion_result(image_base64)
            
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "skill": "emotion_analysis",
                    "input_type": "image",
                    "output_type": "text"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    @staticmethod
    def manifest() -> Dict[str, Any]:
        """
        返回MCP接口的清单信息
        """
        return {
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


# 便捷函数，用于直接调用情绪分析
def analyze_emotion(image_base64: str) -> Dict[str, Any]:
    """
    便捷函数：分析图片情绪
    Args:
        image_base64: base64编码的图片数据
    Returns:
        包含分析结果的字典
    """
    return EmotionAnalysisMCP.call({"image_base64": image_base64})