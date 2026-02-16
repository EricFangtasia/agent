# 情绪分析MCP服务

情绪分析MCP服务提供了一个基于HTTP的API，用于分析图片中人脸的情绪。

## 服务信息

- **端口**: 8089
- **主机**: 0.0.0.0 (所有网络接口)

## API端点

### GET /manifest

获取服务的清单信息，包括服务名称、描述和参数要求。

#### 响应

```json
{
  "name": "emotion_analysis",
  "description": "分析图片中的人脸情绪",
  "parameters": {
    "type": "object",
    "properties": {
      "image_base64": {
        "type": "string",
        "description": "base64编码的图片数据"
      }
    },
    "required": ["image_base64"]
  }
}
```

### POST /execute

执行情绪分析技能。

#### 请求体

```json
{
  "image_base64": "base64编码的图片数据"
}
```

#### 响应

成功时返回:

```json
{
  "success": true,
  "result": "情绪分析结果",
  "metadata": {
    "skill": "emotion_analysis",
    "input_type": "image",
    "output_type": "text"
  }
}
```

失败时返回:

```json
{
  "success": false,
  "error": "错误信息",
  "result": null
}
```

### GET /health

检查服务健康状况。

#### 响应

```json
{
  "status": "healthy"
}
```

## 如何启动服务

### 直接运行

```bash
cd c:\project\py
python run_emotion_mcp_service.py
```

### 在后台运行

服务已经设计为可在后台持续运行，等待HTTP请求。

## 如何测试服务

运行测试脚本：

```bash
python test_emotion_mcp.py
```

## 错误处理

- 如果图片中未检测到人脸，服务将返回相应提示信息
- 如果模型未正确加载，服务将返回错误信息
- 如果请求格式不正确，服务将返回400错误

## 依赖项

- Flask
- Flask-CORS
- onnxruntime
- opencv-python
- pillow
- numpy

## 注意事项

- 确保模型文件 `emotion_model.onnx` 存在于 `agent/emotion/` 目录中
- 服务会在首次启动时加载模型，这可能需要一些时间
- 服务支持多线程请求处理