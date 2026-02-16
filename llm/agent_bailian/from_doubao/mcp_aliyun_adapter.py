import os
import uuid
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, Optional
import aiohttp
# 安装依赖
# pip install fastapi uvicorn aiohttp pydantic
# Linux/Mac
# export ALIYUN_API_KEY="你的阿里云API Key"
# export ALIYUN_WORKSPACE_ID="你的工作空间ID"
# export ALIYUN_APP_ID="你的应用ID"

# # Windows
# set ALIYUN_API_KEY=你的阿里云API Key
# set ALIYUN_WORKSPACE_ID=你的工作空间ID
# set ALIYUN_APP_ID=你的应用ID
# python mcp_aliyun_adapter.py

# 配置阿里云百炼信息
ALIYUN_API_KEY = os.getenv("ALIYUN_API_KEY", "sk-0fa1679a354b4bbc8f480f553bc801ad")  # 从环境变量获取，不再硬编码
ALIYUN_WSS_URL = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"
ALIYUN_WORKSPACE_ID = os.getenv("ALIYUN_WORKSPACE_ID", "llm-nzu0viiu9sxvpjn9")
ALIYUN_APP_ID = os.getenv("ALIYUN_APP_ID", "mm_a6be48a8a95c4d45923ccef93def")
agentKey = os.getenv("AGENT_KEY", "e130978954b54081a98d7585f8f87afc_p_efm")

# 验证API密钥格式（阿里云API密钥通常以sk-开头且长度为32位字符）
def validate_api_key(api_key: str) -> bool:
    if not api_key or not api_key.startswith("sk-"):
        print(" api_key or len(api_key) != 32 or not api_key.startswith(sk-): "+api_key)
        return False
    # 检查是否是测试密钥
    if api_key == "sk-0fa1679a354b4bbc8f480f553bc801ad":
        print("api_key == sk-0fa1679a354b4bbc8f480f553bc801ad警告：检测到默认API密钥，这可能是无效的，请配置您自己的API密钥")
        return False
    return True

# 创建FastAPI应用（作为MCP服务端）
app = FastAPI(title="MCP-阿里云多模态转换服务")

# 存储MCP连接与阿里云连接的映射
connection_mapping: Dict[str, Any] = {}

class MCPRequest(BaseModel):
    """MCP请求基础模型"""
    type: str
    payload: Dict[str, Any]

async def aliyun_ws_client(
    aliyun_ws,
    mcp_ws: WebSocket,
    task_id: str,
    dialog_id: Optional[str] = None
):
    """处理阿里云WebSocket消息转发"""
    try:
        async for message in aliyun_ws:
            # 区分二进制消息（音频）和文本消息（控制指令）
            if message.type == aiohttp.WSMsgType.BINARY:
                # 音频数据直接转发给MCP客户端
                await mcp_ws.send_bytes(message.data)
            elif message.type == aiohttp.WSMsgType.TEXT:
                # 文本消息转换为MCP格式
                aliyun_msg = json.loads(message.data)
                print(f"从阿里云收到消息: {aliyun_msg}")
                mcp_msg = convert_aliyun_to_mcp(aliyun_msg, task_id, dialog_id)
                if mcp_msg:
                    print(f"转换为MCP消息: {mcp_msg}")
                    await mcp_ws.send_text(json.dumps(mcp_msg))
            elif message.type == aiohttp.WSMsgType.ERROR:
                error_msg = f"阿里云WebSocket连接错误: {aliyun_ws.exception()}"
                print(error_msg)
                await mcp_ws.send_text(json.dumps({
                    "type": "error",
                    "payload": {"message": error_msg}
                }))
                break
    except Exception as e:
        error_msg = f"阿里云WS处理错误: {str(e)}"
        print(error_msg)
        await mcp_ws.send_text(json.dumps({
            "type": "error",
            "payload": {"message": error_msg}
        }))

def convert_mcp_to_aliyun(mcp_msg: Dict[str, Any], task_id: str) -> Optional[Dict[str, Any]]:
    """将MCP请求转换为阿里云WebSocket协议格式"""
    mcp_type = mcp_msg.get("type")
    payload = mcp_msg.get("payload", {})
    
    # 初始化阿里云消息基础结构
    aliyun_msg = {
        "header": {
            "task_id": task_id,
            "streaming": "duplex"
        },
        "payload": {
            "input": {}
        }
    }

    # 1. 开始会话（MCP -> 阿里云Start指令）
    if mcp_type == "session_start":
        aliyun_msg["header"]["action"] = "run-task"
        aliyun_msg["payload"] = {
            "task_group": "aigc",
            "task": "multimodal-generation",
            "function": "generation",
            "model": "multimodal-dialog",
            "input": {
                "directive": "Start",
                "workspace_id": ALIYUN_WORKSPACE_ID,
                "app_id": ALIYUN_APP_ID,
                "dialog_id": payload.get("dialog_id")
            },
            "parameters": {
                "upstream": {
                    "type": payload.get("upstream_type", "AudioOnly"),
                    "mode": payload.get("mode", "duplex"),
                    "audio_format": payload.get("audio_format", "pcm"),
                    "sample_rate": payload.get("sample_rate", 16000)
                },
                "downstream": {
                    "voice": payload.get("voice", "longxiaochun_v2"),
                    "sample_rate": payload.get("tts_sample_rate", 24000)
                },
                "client_info": {
                    "user_id": payload.get("user_id", f"mcp_user_{uuid.uuid4().hex[:8]}"),
                    "device": {
                        "uuid": payload.get("device_uuid", f"mcp_device_{uuid.uuid4().hex[:8]}")
                    }
                }
            }
        }
        return aliyun_msg
    
    # 2. 发送文本请求（MCP -> 阿里云RequestToRespond）
    elif mcp_type == "text_request":
        aliyun_msg["header"]["action"] = "continue-task"
        aliyun_msg["payload"]["input"] = {
            "directive": "RequestToRespond",
            "dialog_id": payload.get("dialog_id"),
            "type": "prompt",
            "text": payload.get("text", "")
        }
        aliyun_msg["payload"]["parameters"] = {
            "images": payload.get("images", []),
            "biz_params": payload.get("biz_params", {})
        }
        return aliyun_msg
    
    # 3. 心跳请求（MCP -> 阿里云HeartBeat）
    elif mcp_type == "heartbeat":
        aliyun_msg["header"]["action"] = "continue-task"
        aliyun_msg["payload"]["input"] = {
            "directive": "HeartBeat",
            "dialog_id": payload.get("dialog_id")
        }
        return aliyun_msg
    
    # 4. 结束会话（MCP -> 阿里云Stop）
    elif mcp_type == "session_stop":
        aliyun_msg["header"]["action"] = "finish-task"
        aliyun_msg["payload"]["input"] = {
            "directive": "Stop",
            "dialog_id": payload.get("dialog_id")
        }
        return aliyun_msg
    
    # 其他类型暂不支持
    return None

def convert_aliyun_to_mcp(aliyun_msg: Dict[str, Any], task_id: str, dialog_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """将阿里云响应转换为MCP格式"""
    payload = aliyun_msg.get("payload", {})
    output = payload.get("output", {})
    event = output.get("event")
    
    # 1. 会话开始响应
    if event == "Started":
        return {
            "type": "session_started",
            "payload": {
                "task_id": task_id,
                "dialog_id": output.get("dialog_id"),
                "status": "success"
            }
        }
    
    # 2. 状态变更事件
    elif event == "DialogStateChanged":
        return {
            "type": "state_changed",
            "payload": {
                "dialog_id": output.get("dialog_id"),
                "state": output.get("state"),  # Listening/Thinking/Responding
                "task_id": task_id
            }
        }
    
    # 3. 语音识别结果
    elif event == "SpeechContent":
        return {
            "type": "asr_result",
            "payload": {
                "dialog_id": output.get("dialog_id"),
                "text": output.get("text"),
                "finished": output.get("finished"),
                "task_id": task_id
            }
        }
    
    # 4. AI回答结果
    elif event == "RespondingContent":
        return {
            "type": "llm_result",
            "payload": {
                "dialog_id": output.get("dialog_id"),
                "text": output.get("text"),
                "spoken": output.get("spoken"),
                "finished": output.get("finished"),
                "extra_info": output.get("extra_info", {}),
                "task_id": task_id
            }
        }
    
    # 5. 错误事件
    elif event == "Error":
        return {
            "type": "error",
            "payload": {
                "dialog_id": output.get("dialog_id"),
                "error_code": output.get("error_code"),
                "error_name": output.get("error_name"),
                "error_message": output.get("error_message"),
                "task_id": task_id
            }
        }
    
    # 6. 心跳响应
    elif event == "HeartBeat":
        return {
            "type": "heartbeat_response",
            "payload": {
                "dialog_id": output.get("dialog_id"),
                "task_id": task_id
            }
        }
    
    # 7. 会话结束响应
    elif event == "Stopped":
        return {
            "type": "session_stopped",
            "payload": {
                "dialog_id": output.get("dialog_id"),
                "task_id": task_id,
                "status": "success"
            }
        }
    
    # 其他事件可根据需要扩展
    return None

@app.websocket("/mcp/multimodal")
async def mcp_multimodal_endpoint(websocket: WebSocket):
    """MCP协议WebSocket端点"""
    await websocket.accept()
    
    # 生成唯一任务ID
    task_id = str(uuid.uuid4())
    dialog_id = None
    aliyun_ws = None
    
    try:
        # 检查必要的环境变量
        if not ALIYUN_API_KEY or ALIYUN_API_KEY == "":
            # 为了测试目的，如果环境变量未设置，使用默认值（但仍然会验证）
            temp_key = "sk-0fa1679a354b4bbc8f480f553bc801ad"
            if not validate_api_key(temp_key):
                # 提供一个更友好的错误信息，提示如何设置环境变量
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "payload": {
                        "message": "缺少ALIYUN_API_KEY环境变量，请设置后再试。如需测试，请设置有效的阿里云API密钥。"
                    }
                }))
                return
            actual_key = temp_key
        else:
            actual_key = ALIYUN_API_KEY
        
        if not validate_api_key(actual_key):
            print(" API密钥格式无效: {}".format(actual_key))
            await websocket.send_text(json.dumps({
                "type": "error",
                "payload": {"message": "API密钥格式无效，请检查ALIYUN_API_KEY是否正确设置"}
            }))
            return
        
        if not ALIYUN_WORKSPACE_ID or ALIYUN_WORKSPACE_ID == "your-workspace-id":
            await websocket.send_text(json.dumps({
                "type": "error",
                "payload": {"message": "请设置ALIYUN_WORKSPACE_ID环境变量"}
            }))
            return
            
        if ALIYUN_APP_ID == "your-app-id" or not ALIYUN_APP_ID:
            await websocket.send_text(json.dumps({
                "type": "error",
                "payload": {"message": "请设置ALIYUN_APP_ID环境变量"}
            }))
            return

        # 1. 建立与阿里云的WebSocket连接
        # 使用aiohttp创建带认证头的连接
        headers = {"Authorization": f"Bearer {actual_key}"}
        
        print(f"正在连接到阿里云API: {ALIYUN_WSS_URL}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(ALIYUN_WSS_URL, headers=headers) as aliyun_ws:
                    print("成功连接到阿里云API")
                    
                    # 2. 启动阿里云消息监听任务
                    aliyun_listener = asyncio.create_task(
                        aliyun_ws_client(aliyun_ws, websocket, task_id, dialog_id)
                    )
                    
                    # 3. 处理MCP客户端消息
                    async for data in websocket.iter_text():
                        try:
                            mcp_msg = json.loads(data)
                            
                            # 转换MCP消息为阿里云格式
                            aliyun_msg = convert_mcp_to_aliyun(mcp_msg, task_id)
                            if aliyun_msg:
                                # 更新dialog_id（会话开始后）
                                if mcp_msg.get("type") == "session_start" and aliyun_msg:
                                    dialog_id = aliyun_msg["payload"]["input"].get("dialog_id")
                                # 发送到阿里云
                                print(f"向阿里云发送消息: {json.dumps(aliyun_msg)[:200]}...")  # 只打印前200字符
                                await aliyun_ws.send_str(json.dumps(aliyun_msg))
                            
                        except json.JSONDecodeError:
                            # 如果不是JSON，尝试作为二进制数据处理
                            await aliyun_ws.send_bytes(data.encode() if isinstance(data, str) else data)
        except Exception as e:
            error_msg = f"连接阿里云API失败: {str(e)}"
            print(error_msg)
            await websocket.send_text(json.dumps({
                "type": "error",
                "payload": {"message": error_msg}
            }))
        
    except WebSocketDisconnect:
        print(f"MCP客户端断开连接: {task_id}")
    except Exception as e:
        print(f"处理MCP请求错误: {str(e)}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "payload": {"message": str(e)}
        }))
        # 注意：async with 会自动清理资源，不需要手动关闭

if __name__ == "__main__":
    import uvicorn
    # 启动MCP服务，默认端口8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
