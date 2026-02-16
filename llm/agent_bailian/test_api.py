import requests
import json

# 测试纯文本请求
print("测试纯文本请求...")
try:
    response = requests.post(
        'http://localhost:8080/v1/text-image-conversation',
        headers={'Content-Type': 'application/json'},
        json={'text': 'Hello World'}
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")

print("\n测试带图片和文字的请求...")
try:
    # 测试multipart请求
    files = {
        'text': (None, 'Hello with image'),
    }
    data = {
        'data': (None, json.dumps({
            'messages': [{'role': 'user', 'content': 'Hello with image'}],
            'model': 'qwen-plus-2025-12-01'
        }))
    }
    response = requests.post(
        'http://localhost:8080/v1/text-image-conversation',
        files=files
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")