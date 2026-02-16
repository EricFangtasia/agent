"""
测试情绪分析技能(Skills)和MCP接口的功能
此文件位于 agent/emotion 目录下
"""
import base64
import os
import sys
# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from agent.emotion.emotion_analysis_skill import EmotionAnalysisSkill, EmotionAnalysisMCP, analyze_emotion, clean_multimodal_text


def load_test_image(image_path):
    """
    加载测试图片并转换为base64格式
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"测试图片不存在: {image_path}")
    
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    return image_base64


def test_emotion_skills():
    """
    测试 EmotionAnalysisSkill 的功能
    """
    print("=" * 60)
    print("开始测试 EmotionAnalysisSkill...")
    
    try:
        # 尝试加载测试图片
        # 由于我们不知道用户的具体图片位置，这里创建一个模拟的base64字符串进行测试
        # 实际使用时，请替换为真实的人脸图片
        print("注意：需要提供一张人脸图片进行实际测试")
        
        # 测试技能描述和参数
        print(f"技能名称: {EmotionAnalysisSkill.name()}")
        print(f"技能描述: {EmotionAnalysisSkill.description()}")
        print(f"技能参数: {EmotionAnalysisSkill.parameters()}")
        
        # 如果有测试图片，可以取消下面的注释进行实际测试
        # test_image_path = "path/to/your/test_image.jpg"  # 替换为实际图片路径
        # image_base64 = load_test_image(test_image_path)
        # result = EmotionAnalysisSkill.execute(image_base64=image_base64)
        # print(f"技能执行结果: {result}")
        
        print("EmotionAnalysisSkill 测试完成")
        
    except Exception as e:
        print(f"测试 EmotionAnalysisSkill 时出现错误: {e}")


def test_emotion_mcp():
    """
    测试 EmotionAnalysisMCP 的功能
    """
    print("=" * 60)
    print("开始测试 EmotionAnalysisMCP...")
    
    try:
        # 测试 MCP 接口
        print(f"MCP 接口清单: {EmotionAnalysisMCP.manifest()}")
        
        # 如果有测试图片，可以取消下面的注释进行实际测试
        # test_image_path = "path/to/your/test_image.jpg"  # 替换为实际图片路径
        # image_base64 = load_test_image(test_image_path)
        # params = {"image_base64": image_base64}
        # result = EmotionAnalysisMCP.call(params)
        # print(f"MCP 调用结果: {result}")
        
        print("EmotionAnalysisMCP 测试完成")
        
    except Exception as e:
        print(f"测试 EmotionAnalysisMCP 时出现错误: {e}")


def test_clean_multimodal_text():
    """
    测试文本清理功能
    """
    print("=" * 60)
    print("开始测试 clean_multimodal_text 函数...")
    
    test_cases = [
        "情绪识别结果: <|happy|> 开心",
        "情绪分析结果：主要情绪是 <|sad|> 悲伤",
        " <|angry|> 生气 <|fearful|> 害怕 各情绪类别概率:",
        "正常文本没有标签",
        "情绪识别结果: happy 情绪分析结果： sad 主要情绪: angry 各情绪类别概率: fear"
    ]
    
    for i, text in enumerate(test_cases, 1):
        cleaned = clean_multimodal_text(text)
        print(f"测试案例 {i}:")
        print(f"  原文: {text}")
        print(f"  清理后: {cleaned}")
        print()
    
    print("clean_multimodal_text 测试完成")


def test_analyze_emotion():
    """
    测试便捷函数 analyze_emotion
    """
    print("=" * 60)
    print("开始测试 analyze_emotion 便捷函数...")
    
    try:
        # 如果有测试图片，可以取消下面的注释进行实际测试
        # test_image_path = "path/to/your/test_image.jpg"  # 替换为实际图片路径
        # image_base64 = load_test_image(test_image_path)
        # result = analyze_emotion(image_base64=image_base64)
        # print(f"便捷函数调用结果: {result}")
        
        print("analyze_emotion 测试完成（需要提供实际图片才能完整测试）")
        
    except Exception as e:
        print(f"测试 analyze_emotion 时出现错误: {e}")


def interactive_test():
    """
    交互式测试，允许用户输入图片路径
    """
    print("=" * 60)
    print("交互式测试")
    
    image_path = input("请输入要测试的图片路径（直接回车跳过此步骤）: ").strip()
    
    if not image_path:
        print("跳过交互式测试")
        return
    
    if not os.path.exists(image_path):
        print(f"错误：图片路径不存在: {image_path}")
        return
    
    try:
        image_base64 = load_test_image(image_path)
        
        print("\n正在测试 EmotionAnalysisSkill...")
        skill_result = EmotionAnalysisSkill.execute(image_base64=image_base64)
        print(f"技能执行结果: {skill_result}")
        
        print("\n正在测试 EmotionAnalysisMCP...")
        mcp_params = {"image_base64": image_base64}
        mcp_result = EmotionAnalysisMCP.call(mcp_params)
        print(f"MCP 调用结果: {mcp_result}")
        
        print("\n正在测试便捷函数 analyze_emotion...")
        shortcut_result = analyze_emotion(image_base64=image_base64)
        print(f"便捷函数调用结果: {shortcut_result}")
        
    except Exception as e:
        print(f"交互式测试出错: {e}")


def main():
    """
    主测试函数
    """
    print("情绪分析技能(Skills)和MCP接口测试程序")
    print("此文件位于 agent/emotion 目录下，与 emotion_analysis_skill.py 在上级目录中")
    print("本程序将测试情绪分析功能的各种接口")
    
    # 运行各项测试
    test_emotion_skills()
    test_emotion_mcp()
    test_clean_multimodal_text()
    test_analyze_emotion()
    
    # 询问是否进行交互式测试
    print("\n" + "=" * 60)
    response = input("是否进行交互式测试？(y/n): ").strip().lower()
    if response in ['y', 'yes', '是']:
        interactive_test()
    
    print("\n所有测试完成！")


if __name__ == "__main__":
    main()