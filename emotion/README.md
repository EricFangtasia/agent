# 情绪分析 Agent 系统

这是一个基于深度学习的情绪分析智能代理系统，能够分析图片中人脸的情绪状态。系统包含MCP服务和阿里云多模态交互开发套件的集成。

## 项目结构

```
emotion/
├── emotion_detection_onnx.py           # 基于ONNX的情绪检测模型
├── emotion_analysis_skill.py           # 情绪分析技能封装
├── emotion_analysis_mcp_service.py     # 情绪分析MCP服务
├── emotion_intent_adapter.py           # 意图适配器（对接阿里云）
├── emotion_analysis_agentcard.json     # AgentCard配置文件
├── emotion_mcp_service_README.md       # MCP服务使用说明
├── emotion_agentcard_setup_guide.md    # AgentCard配置指南
├── emotion_mcp_client_example.py       # MCP服务客户端示例
├── AGENT_JSON_SETUP.md                 # .well-known/agent.json配置说明
├── run_emotion_mcp_service.py          # 启动MCP服务脚本
├── run_intent_adapter.py               # 启动意图适配器脚本
├── test_emotion_mcp.py                 # MCP服务测试脚本
├── test_intent_adapter.py              # 意图适配器测试脚本
├── final_test.py                       # 最终测试脚本
├── test_agent_json_endpoint.py         # 测试agent.json端点脚本
└── README.md                           # 本说明文件
```

## 功能模块

### 1. 情绪检测引擎

- 使用ONNX运行时的情绪检测模型
- 支持7种情绪识别：悲伤、厌恶、生气、中性、恐惧、惊讶、高兴
- 基于面部特征的情绪分析

### 2. 情绪分析技能

- 封装情绪检测功能为标准技能
- 支持MCP协议
- 提供统一的接口调用

### 3. MCP服务

- 提供HTTP接口的情绪分析服务
- 运行在端口8089
- 支持模型清单、执行和健康检查端点

### 4. 意图适配器

- 与阿里云多模态交互开发套件集成
- 运行在端口8090
- 解析意图并调用相应技能
- 提供`.well-known/agent.json`端点用于Agent注册

## 快速开始

### 启动MCP服务

```bash
cd agent/emotion
python run_emotion_mcp_service.py
```

### 启动意图适配器

```bash
python run_intent_adapter.py
```

## API端点

### MCP服务 (端口 8089)

- `GET /manifest`: 获取服务清单
- `POST /execute`: 执行情绪分析
- `GET /health`: 健康检查

### 意图适配器 (端口 8090)

- `GET /.well-known/agent.json`: 获取Agent配置（用于阿里云管控台集成）
- `GET /agentcard`: 获取AgentCard配置
- `POST /process-intent`: 处理意图请求
- `GET /health`: 健康检查

## 阿里云多模态交互开发套件集成

通过Intent扩展协议，系统可以与阿里云多模态交互开发套件集成：

1. AgentCard配置包含`emotion-analysis`技能
2. 支持从用户消息中提取图片数据
3. 自动执行情绪分析并返回结果
4. 支持`.well-known/agent.json`端点，可在阿里云管控台直接填写URL进行集成

## .well-known/agent.json 端点

我们实现了标准的 `.well-known/agent.json` 端点，用于向外部系统提供Agent配置信息：

- **URL**: `http://your-server-ip:8090/.well-known/agent.json`
- **用途**: 在阿里云管控台中填入此URL可快速集成自研Agent
- **内容**: 包含完整的Agent描述、技能定义和服务信息

## 测试

运行MCP服务测试：

```bash
python test_emotion_mcp.py
```

运行意图适配器测试：

```bash
python test_intent_adapter.py
```

## 依赖项

- Flask
- Flask-CORS
- onnxruntime
- opencv-python
- pillow
- numpy
- requests