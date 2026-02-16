# 实时多模态交互MCP服务

基于WebSocket协议的实时多模态交互API实现，支持与阿里云多模态交互开发套件的对接。

## 文件说明

- `realtime_multimodal_mcp_service.py`: 主要的MCP服务实现
- `test_realtime_multimodal_mcp_service.py`: 服务测试脚本
- `start_mcp_service.py`: 启动脚本，可同时启动服务和测试
- `README.md`: 本说明文件

## 功能特性

- 基于WebSocket的全双工通信
- 支持实时语音识别和语音合成
- 支持图像情绪检测
- 支持多模态交互（语音+图像）
- 支持会话管理（开始、停止、继续）
- 心跳机制保持连接活跃

## 安装依赖

```bash
pip install websockets
```

## 运行服务

### 方法1：单独运行服务

```bash
python realtime_multimodal_mcp_service.py
```

### 方法2：使用启动脚本（包含测试）

```bash
python start_mcp_service.py
```

### 方法3：分别运行服务和测试

先启动服务：

```bash
python realtime_multimodal_mcp_service.py
```

然后在另一个终端运行测试：

```bash
python test_realtime_multimodal_mcp_service.py
```

## API接口

### 连接地址

```
ws://localhost:8766
```

### 鉴权

在WebSocket握手时，通过HTTP Header传递API Key：

```
"Authorization": "Bearer your_api_key"
```

### 消息格式

#### 开始会话

```json
{
    "header": {
        "action":"run-task",
        "task_id": "f894c16f-f20e-4c1d-837e-89e0fbc63a43",
        "streaming":"duplex"
    },
    "payload": {
        "task_group":"aigc",
        "task":"multimodal-generation",
        "function":"generation",
        "model":"multimodal-dialog",
        "input":{
          "directive": "Start",
          "workspace_id": "llm-***********",
          "app_id": "****************"
        },
        "parameters":{
          "upstream":{
            "type": "AudioOnly",
            "mode": "duplex"
          },
          "downstream":{
            "voice": "longxiaochun_v2",
            "sample_rate": 24000
          },
          "client_info":{
            "user_id": "bin********207"
          }
        }
    }
}
```

#### 情绪检测请求

```json
{
    "header": {
        "action":"continue-task",
        "task_id": "f894c16f-f20e-4c1d-837e-89e0fbc63a43",
        "streaming":"duplex"
    },
    "payload": {
        "input":{
          "directive": "RequestToRespond",
          "dialog_id": "dialog-id-here",
          "type": "prompt",
          "text": "请分析这张图片中的情绪"
        },
        "parameters":{
          "images":[{
              "type": "base64",
              "value": "base64-encoded-image-data"
          }]
        }
    }
}
```

## 消息类型

- `Start`: 开始会话
- `Started`: 服务端确认会话已开始
- `DialogStateChanged`: 对话状态变更（Listening, Thinking, Responding）
- `RequestToRespond`: 客户端请求响应
- `RespondingStarted`: 服务端开始响应
- `RespondingContent`: 响应内容（流式）
- `RespondingEnded`: 服务端响应结束
- `LocalRespondingEnded`: 客户端播放完成
- `Stop`: 客户端停止会话
- `Stopped`: 服务端确认会话已停止
- `HeartBeat`: 心跳消息

## 情绪检测集成

服务集成了情绪检测功能，可通过发送带图片的`RequestToRespond`消息触发情绪分析。

## 错误处理

服务实现了基本的错误处理机制，包括：

- 连接异常处理
- JSON解析错误处理
- 消息格式验证
- 超时处理

## 扩展性

服务设计为模块化结构，易于扩展：

- 可以轻松添加新的消息类型处理
- 支持集成其他AI能力
- 可以扩展多模态输入输出方式

## 注意事项

- 确保端口8766未被其他服务占用
- 服务启动后会一直监听直到手动停止
- 在生产环境中应添加适当的身份验证和安全措施
- 需要根据实际需求调整并发连接数限制