# 情绪分析 Agent 接入阿里云多模态交互开发套件配置指南

本文档介绍如何将情绪分析 Agent 配置到阿里云多模态交互开发套件中，实现基于意图的智能交互。

## 1. AgentCard 配置说明

### AgentCard 文件结构

`emotion_analysis_agentcard.json` 包含以下关键部分：

```json
{
  "name": "emotion_analysis_agent",
  "description": "情绪分析智能代理，能够分析图片中人脸的情绪状态",
  "version": "1.0.0",
  "author": "Emotion Analysis Team",
  "capabilities": {
    "extensions": [
      {
        "uri": "https://help.aliyun.com/zh/model-studio/multimodal-integration-a2a-intent",
        "params": {
          "skills": [
            {
              "id": "emotion-analysis",
              "inputSchema": {
                "type": "object",
                "properties": {
                  "image_base64": {
                    "type": "string",
                    "description": "Base64编码的图片数据，用于情绪分析"
                  }
                },
                "required": ["image_base64"]
              }
            }
          ]
        }
      }
    ]
  },
  "services": [
    {
      "id": "emotion-mcp-service",
      "name": "情绪分析MCP服务",
      "description": "提供情绪分析能力的MCP服务",
      "endpoint": "http://localhost:8089",
      "type": "mcp"
    }
  ]
}
```

### 关键配置项说明

1. **URI**：`"https://help.aliyun.com/zh/model-studio/multimodal-integration-a2a-intent"` - 标识支持 Intent 扩展协议
2. **Skill ID**：`"emotion-analysis"` - 唯一技能标识符
3. **Input Schema**：定义了技能所需参数的 JSON Schema

## 2. 服务架构

### 三层架构

```
阿里云多模态交互开发套件
         ↓
意图适配器 (端口 8090)
         ↓
情绪分析MCP服务 (端口 8089)
         ↓
情绪分析模型
```

### 服务职责

- **意图适配器 (8090)**：接收来自阿里云平台的意图请求，解析意图和参数，转发给MCP服务
- **情绪分析MCP服务 (8089)**：提供标准化的MCP接口，执行实际的情绪分析任务

## 3. 部署步骤

### 步骤1：启动情绪分析MCP服务

```bash
cd c:\project\py
python run_emotion_mcp_service.py
```

### 步骤2：启动意图适配器

```bash
cd c:\project\py
python run_intent_adapter.py
```

### 步骤3：配置 AgentCard

在阿里云多模态交互开发套件中：

1. 进入 Agent 配置页面
2. 上传或指定 AgentCard 地址：`http://your-server-ip:8090/agentcard`
3. 确保 Intent 扩展协议已启用

## 4. API 接口说明

### 意图适配器接口

- **GET /agentcard** - 获取 AgentCard 配置
- **POST /process-intent** - 处理意图请求
- **GET /health** - 健康检查

### 请求示例

```json
{
  "message": {
    "parts": [
      { 
        "kind": "image", 
        "data": "base64编码的图片数据..." 
      },
      { 
        "kind": "text", 
        "text": "分析这张图片中人物的情绪" 
      }
    ],
    "metadata": {
      "intentInfos": [
        {
          "intent": "emotion-analysis",
          "slots": [
            { 
              "name": "image_base64", 
              "value": "base64编码的图片数据..." 
            }
          ]
        }
      ]
    }
  }
}
```

### 响应示例

```json
{
  "success": true,
  "responses": [
    {
      "intent": "emotion-analysis",
      "response": {
        "success": true,
        "result": "情绪分析：高兴（置信度：0.85）",
        "metadata": {
          "skill": "emotion_analysis",
          "input_type": "image",
          "output_type": "text"
        }
      }
    }
  ]
}
```

## 5. 故障排除

### 常见问题

1. **服务无法访问**
   - 检查端口 8089 和 8090 是否开放
   - 检查防火墙设置

2. **意图识别失败**
   - 确认 AgentCard 配置正确
   - 检查 Intent ID 与请求中的 intent 是否匹配

3. **图片分析失败**
   - 检查图片格式是否支持（JPG, PNG, BMP等）
   - 检查图片中是否有人脸

## 6. 安全注意事项

- 在生产环境中，应使用 HTTPS 协议
- 对请求进行身份验证和授权
- 限制请求频率以防止滥用
- 确保敏感数据的传输安全

## 7. 扩展建议

1. 可以添加更多技能到 AgentCard 中
2. 支持更多类型的图片分析功能
3. 增加对多个人脸的支持
4. 添加缓存机制提高性能