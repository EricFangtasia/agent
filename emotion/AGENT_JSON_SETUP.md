# .well-known/agent.json 配置说明

## 概述

为了将您的情绪分析 Agent 集成到阿里云多模态交互开发套件中，我们实现了 `.well-known/agent.json` 端点，允许通过 URL 方式访问 Agent 配置。

## 配置详情

### 端点信息

- **URL**: `http://your-server-ip:8090/.well-known/agent.json`
- **方法**: GET
- **内容类型**: application/json

### 端点结构

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
  ],
  "metadata": {
    "category": "image-processing",
    "tags": ["emotion-detection", "ai", "image-analysis", "multimodal"]
  }
}
```

## 使用方法

### 1. 本地测试

在本地启动服务后，可以通过以下 URL 访问配置：

```
http://localhost:8090/.well-known/agent.json
```

### 2. 阿里云管控台配置

要在阿里云多模态交互开发套件中配置您的 Agent：

1. 确保您的服务在公网可访问
2. 将您的公网 IP 或域名替换 URL 中的 localhost
3. 在阿里云管控台中填入以下 URL：

```
http://your-public-ip:8090/.well-known/agent.json
```

或者如果您配置了域名：

```
http://your-domain.com:8090/.well-known/agent.json
```

## 部署注意事项

### 1. 网络访问

为了让阿里云平台能够访问您的 Agent 配置：

- 确保端口 8090 在防火墙中开放
- 如果在内网，需要配置端口转发或使用反向代理
- 考虑使用 HTTPS（推荐）或配置安全认证

### 2. 服务可用性

- 确保情绪分析 MCP 服务（端口 8089）和意图适配器（端口 8090）都在运行
- 设置适当的服务监控和重启机制
- 考虑服务的容错和恢复机制

### 3. 生产环境部署

在生产环境中，建议：

- 使用反向代理（如 Nginx）处理请求
- 配置 SSL/TLS 证书支持 HTTPS
- 实现请求认证和授权机制
- 设置适当的请求速率限制

## 测试命令

使用 curl 测试端点：

```bash
curl http://localhost:8090/.well-known/agent.json
```

使用 Python requests 测试：

```python
import requests

response = requests.get("http://localhost:8090/.well-known/agent.json")
print(response.json())
```

## 故障排查

### 常见问题

1. **无法访问端点**
   - 检查服务是否正在运行
   - 检查防火墙设置
   - 验证端口是否开放

2. **配置无效**
   - 验证 JSON 格式是否正确
   - 检查必填字段是否完整

3. **集成失败**
   - 确认 MCP 服务（端口 8089）是否正常运行
   - 验证 AgentCard 中的端点地址是否正确