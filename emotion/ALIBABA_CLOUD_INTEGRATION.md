# 阿里云多模态交互开发套件集成指南

## 概述

本文档介绍如何将您的情绪分析 Agent 集成到阿里云多模态交互开发套件中。

## 集成方式

### 方法一：使用 .well-known/agent.json 端点

1. 确保您的服务已启动并可从公网访问
2. 在阿里云管控台中填入以下 URL：

```
http://your-public-ip:8090/.well-known/agent.json
```

3. 替换 `your-public-ip` 为您服务器的公网 IP 地址

### 方法二：使用 AgentCard 端点

1. 在阿里云管控台中填入以下 URL：

```
http://your-public-ip:8090/agentcard
```

2. 替换 `your-public-ip` 为您服务器的公网 IP 地址

## 部署要求

### 1. 服务可用性

- 情绪分析 MCP 服务运行在端口 8089
- 意图适配器服务运行在端口 8090
- 两个服务都需要正常运行

### 2. 网络配置

- 确保端口 8089 和 8090 在防火墙中开放
- 如果服务部署在内网，需要配置端口转发或使用反向代理
- 确保阿里云服务器能够访问您的服务端点

### 3. 安全考虑

- 在生产环境中建议使用 HTTPS
- 实现适当的请求认证机制
- 考虑添加访问频率限制

## 集成验证步骤

### 1. 本地验证

在将服务暴露给公网之前，先在本地验证：

```bash
# 检查 MCP 服务
curl http://localhost:8089/health

# 检查意图适配器
curl http://localhost:8090/health

# 检查 agent.json 端点
curl http://localhost:8090/.well-known/agent.json

# 检查 agentcard 端点
curl http://localhost:8090/agentcard
```

### 2. 公网验证

在将服务部署到公网后，验证可以从外部访问：

```bash
curl http://your-public-ip:8090/.well-known/agent.json
```

### 3. 功能测试

测试端到端功能：

1. 启动 MCP 服务（端口 8089）
2. 启动意图适配器（端口 8090）
3. 通过阿里云多模态交互开发套件调用服务
4. 验证情绪分析结果返回正常

## 常见问题

### 1. 端点无法访问

- 检查服务是否正在运行
- 验证防火墙设置
- 确认端口映射是否正确

### 2. 集成失败

- 确认 JSON 格式是否正确
- 检查必填字段是否完整
- 验证服务端点 URL 是否可访问

### 3. 功能异常

- 检查 MCP 服务是否正常运行
- 验证网络连通性
- 查看服务日志获取更多信息

## 生产环境部署建议

### 1. 使用反向代理

使用 Nginx 等反向代理工具：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /.well-known/agent.json {
        proxy_pass http://localhost:8090/.well-known/agent.json;
    }

    location /agentcard {
        proxy_pass http://localhost:8090/agentcard;
    }

    location /process-intent {
        proxy_pass http://localhost:8090/process-intent;
    }

    location /health {
        proxy_pass http://localhost:8090/health;
    }
}
```

### 2. 启用 HTTPS

配置 SSL 证书以启用 HTTPS：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # ... 代理配置
}
```

### 3. 添加认证

实现基本认证保护服务端点：

```python
from functools import wraps
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization')
        # 实现认证逻辑
        if not auth or not validate_auth(auth):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

## 故障排查

### 日志查看

查看服务日志以诊断问题：

```bash
# 检查服务日志
tail -f /var/log/your-app.log
```

### 网络测试

使用工具测试网络连通性：

```bash
# 检查端口是否开放
telnet your-domain.com 8090

# 检查 HTTP 响应
curl -v http://your-domain.com:8090/.well-known/agent.json
```

## 技术支持

如需技术支持，请参考：

- 检查服务运行状态
- 验证网络连通性
- 查阅错误日志
- 联系阿里云技术支持