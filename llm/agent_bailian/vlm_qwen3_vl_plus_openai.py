import os
import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-ff11853c431f4e9a99766d454b062ca2",  # 直接设置密钥
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen3-vl-plus-2025-12-19",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"
                    }
                },
                {"type": "text", "text": "这是什么"},
            ],
        }
    ],
)

# 解析并格式化输出，确保中文正确显示
result = completion.model_dump()
print(json.dumps(result, ensure_ascii=False, indent=2))