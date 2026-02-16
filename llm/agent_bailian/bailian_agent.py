import base64
import os
from dashscope import MultiModalConversation
import dashscope 
import json

# 设置 API 密钥（推荐方式：优先使用环境变量，其次使用默认密钥）
# 建议通过环境变量设置：export DASHSCOPE_API_KEY="sk-xxxx"
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY", "sk-ff11853c431f4e9a99766d454b062ca2")

# 若使用新加坡地域的模型，请取消下列注释
# dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

# 编码函数：将本地文件转换为 Base64 编码的字符串
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 图片路径（你可以替换为实际的图片路径）
# image_path = "./47658.jpg"
image_path = "./47629.jpg"
# image_path = "./47799.jpg"


# 检查是否有本地图片，否则使用在线示例图片
if not os.path.exists(image_path):
    print(f"提示：找不到本地图片 {image_path}，使用在线示例图片")
    messages = [
        {
            "role": "user",
            "content": [
                {"image": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"},
                {"text": "图中描绘的是什么景象?"},
            ],
        },
    ]
else:
    base64_image = encode_image(image_path)
    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"data:image/png;base64,{base64_image}"},
                # {"text": "图中的人是什么表情，请用7维向量表示，分别对应sad, disgust, angry, neutral, fear, surprise, happy，使用归一处理,使用向量表示?"},
                {"text": "图中的人是积极消极表情，积极请返回1，消极返回0？"},
            ],
        },
    ]

# 调用多模态模型（不再传 api_key，已通过 dashscope.api_key 全局设置）
response = MultiModalConversation.call(
    model="qwen3-vl-plus-2025-12-19",  # 使用更稳定的视觉语言模型
    messages=messages,
)

# 输出结果，确保中文正确显示
try:
    if response and response.output.choices:
        # result = completion.model_dump()
        # print(json.dumps(result, ensure_ascii=False, indent=2))
        result_text = response.output.choices[0].message.content[0]["text"]
        print(json.dumps(result_text, ensure_ascii=False))
    else:
        print("未能获取到有效的响应内容")
        if response:
            print(f"响应状态码: {response.status_code}")
            print(f"错误信息: {response.message}")
        else:
            print("无响应返回")
except Exception as e:
    print(f"处理响应时出错: {e}")