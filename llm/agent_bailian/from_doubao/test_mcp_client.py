import websockets
import json
import asyncio

async def test_mcp_client():
    print("正在连接到MCP服务...")
    try:
        # 连接MCP服务
        async with websockets.connect("ws://localhost:8000/mcp/multimodal") as websocket:
            print("成功连接到MCP服务")
            
            # 1. 启动会话
            start_msg = {
                "type": "session_start",
                "payload": {
                    "upstream_type": "AudioOnly",
                    "mode": "duplex",
                    "audio_format": "pcm",
                    "sample_rate": 16000,
                    "voice": "longxiaochun_v2",
                    "user_id": "test_user_001",
                    "device_uuid": "test_device_001"
                }
            }
            print("发送会话启动消息:", json.dumps(start_msg))
            await websocket.send(json.dumps(start_msg))
            
            print("等待会话启动响应...")
            # 设置超时时间以避免无限等待
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print("会话启动响应:", response)
            except asyncio.TimeoutError:
                print("错误: 等待会话启动响应超时，请检查:")
                print("  1. MCP服务器是否已启动？")
                print("  2. 环境变量是否已正确设置？")
                print("  3. 网络连接是否正常？")
                return
            
            # 解析响应
            response_data = json.loads(response)
            if response_data.get("type") == "error":
                print(f"错误: {response_data['payload']['message']}")
                return
                
            dialog_id = response_data["payload"].get("dialog_id")
            if not dialog_id:
                print("未获得有效的dialog_id")
                return

            # 2. 发送文本请求
            text_msg = {
                "type": "text_request",
                "payload": {
                    "dialog_id": dialog_id,
                    "text": "你好，介绍一下自己"
                }
            }
            await websocket.send(json.dumps(text_msg))
            
            # 接收响应
            response_count = 0
            while response_count < 10:  # 最多接收10条消息
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    print("收到消息:", msg)
                    response_count += 1
                    
                    # 检测是否收到完整回答
                    msg_data = json.loads(msg) if isinstance(msg, str) else {"type": "audio_data"}
                    if isinstance(msg_data, dict) and msg_data.get("type") == "llm_result" and msg_data.get("payload", {}).get("finished"):
                        print("收到完整回答，结束接收")
                        break
                except asyncio.TimeoutError:
                    print("等待消息超时，结束接收")
                    break

    except ConnectionRefusedError:
        print("错误: 无法连接到MCP服务，请确保服务已在 http://localhost:8000/mcp/multimodal 上启动")
    except Exception as e:
        print(f"发生错误: {str(e)}")

asyncio.run(test_mcp_client())