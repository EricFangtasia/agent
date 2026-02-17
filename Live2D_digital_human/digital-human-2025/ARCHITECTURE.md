# 🏗️ 项目架构说明

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     浏览器 (Client)                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐      ┌──────────────────┐             │
│  │  主页面          │      │  连接设置         │             │
│  │  page.tsx       │◄─────┤  ConnectionSettings│            │
│  │                 │      │                   │             │
│  │  ┌───────────┐  │      └──────────────────┘             │
│  │  │Live2D区域│  │                                         │
│  │  └───────────┘  │                                         │
│  │                 │      ┌──────────────────┐             │
│  │  ┌───────────┐  │      │  状态管理         │             │
│  │  │聊天界面  │  │◄─────┤  Zustand Store   │             │
│  │  └───────────┘  │      │  - messages      │             │
│  └─────────────────┘      │  - connection    │             │
│          ▲                │  - emotions      │             │
│          │                └──────────────────┘             │
│          │                         ▲                        │
│          │                         │                        │
│  ┌───────┴────────────────────────┴─────────┐             │
│  │         Realtime Service                  │             │
│  │  - OpenAI Realtime API封装                │             │
│  │  - WebSocket管理                          │             │
│  │  - 音频处理                               │             │
│  │  - 口型同步                               │             │
│  └───────────────┬───────────────────────────┘             │
│                  │                                          │
└──────────────────┼──────────────────────────────────────────┘
                   │
                   │ WebSocket
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              OpenAI Realtime API                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   ASR    │─▶│   LLM    │─▶│   TTS    │                  │
│  │ Whisper  │  │  GPT-4o  │  │  Voice   │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## 技术栈详解

### 前端层 (Browser)

#### 1. UI框架
```typescript
Next.js 15           // React元框架，提供路由、SSR等
  ├─ React 19        // UI组件库
  ├─ TypeScript 5.7  // 类型系统
  └─ Tailwind CSS v4 // 样式框架
```

#### 2. 核心组件

**主页面** (`app/page.tsx`)
- 整体布局
- 组件编排
- 响应式设计

**Live2D数字人** (`components/Live2DCharacter.tsx`)
```typescript
PixiJS 8.6           // WebGL渲染引擎
  └─ Live2D SDK      // 2D数字人模型加载和控制
     ├─ 模型渲染
     ├─ 表情控制
     ├─ 口型同步
     └─ 动作播放
```

**聊天界面** (`components/ChatInterface.tsx`)
```typescript
Framer Motion 12     // 动画库
  ├─ 消息列表动画
  ├─ 按钮交互反馈
  └─ 状态转换动画
```

**连接设置** (`components/ConnectionSettings.tsx`)
- API密钥配置
- 连接状态管理
- 错误处理

#### 3. 状态管理 (`lib/store.ts`)
```typescript
Zustand 5.0
  ├─ 连接状态 (isConnected, isRecording, isSpeaking)
  ├─ 消息历史 (messages[])
  ├─ 数字人状态 (emotion, mouthOpenness)
  └─ Actions (setXXX, addMessage, etc.)
```

### 服务层

#### Realtime Service (`lib/realtime-service.ts`)

**核心功能**:
```typescript
class RealtimeService {
  // 1. 连接管理
  connect(apiKey)              // 建立WebSocket连接
  disconnect()                 // 断开连接
  
  // 2. 音频处理
  startRecording()             // 开始麦克风录音
  stopRecording()              // 停止录音
  handleAudioDelta(data)       // 处理AI返回的音频
  
  // 3. 口型同步
  analyzeAudioForLipSync()     // 实时分析音频控制口型
  
  // 4. 消息发送
  sendText(text)               // 发送文本消息
  interrupt()                  // 打断AI说话
}
```

**事件流程**:
```
用户录音 → MediaRecorder
         ↓
    base64编码
         ↓
    WebSocket发送 → OpenAI Realtime API
                           ↓
                    ASR (Whisper)
                           ↓
                    LLM (GPT-4o)
                           ↓
                    TTS (Voice)
                           ↓
    ← WebSocket接收 ← 音频流 (base64)
         ↓
    解码 + 播放
         ↓
    音频分析 → 控制数字人口型
```

### 后端API层

#### OpenAI Realtime API

**配置参数**:
```typescript
{
  model: 'gpt-4o-realtime-preview',
  voice: 'alloy',                    // 语音类型
  instructions: '系统提示词',          // AI人格设定
  input_audio_format: 'pcm16',       // 音频格式
  output_audio_format: 'pcm16',
  turn_detection: {                  // 语音活动检测
    type: 'server_vad',
    threshold: 0.5,
    silence_duration_ms: 500
  }
}
```

**主要事件**:
- `conversation.item.input_audio_transcription.completed` - 用户语音识别完成
- `response.text.delta` - AI文本响应片段
- `response.text.done` - AI文本响应完成
- `response.audio.delta` - AI音频响应片段（用于口型同步）
- `response.audio.done` - AI音频响应完成

## 数据流

### 用户发送消息流程

```
文本输入:
用户输入文字 → ChatInterface.tsx
              ↓
       store.addMessage(user)
              ↓
    realtimeService.sendText()
              ↓
       WebSocket.send()
              ↓
    OpenAI Realtime API处理
              ↓
       返回文本 + 音频
              ↓
    store.addMessage(assistant)
              ↓
       UI更新 + 数字人说话
```

```
语音输入:
用户点击麦克风 → realtimeService.startRecording()
                ↓
           MediaRecorder录音
                ↓
           每100ms发送音频片段
                ↓
           WebSocket.send(audioData)
                ↓
           用户点击停止
                ↓
           createResponse() 触发AI回复
                ↓
           (同上，返回音频)
```

### 口型同步流程

```
AI返回音频 → handleAudioDelta()
             ↓
        解码base64
             ↓
        AudioContext.decodeAudioData()
             ↓
        创建AnalyserNode
             ↓
        requestAnimationFrame循环
             ↓
        analyser.getByteFrequencyData()
             ↓
        计算平均音量
             ↓
        归一化 (0-1)
             ↓
        store.setMouthOpenness(value)
             ↓
        Live2DCharacter监听state变化
             ↓
        model.setParameter('ParamMouthOpenY', value)
             ↓
        数字人嘴巴动起来 ✨
```

## 性能优化点

### 1. 减少延迟
- ✅ 使用流式处理（边生成边播放）
- ✅ WebSocket长连接（避免HTTP握手）
- ✅ 音频分块发送（100ms/块）
- ✅ 服务端VAD（自动检测说话结束）

### 2. 资源优化
- ✅ PixiJS资源复用
- ✅ 动态import减少初始包体积
- ✅ 懒加载Live2D模型
- ✅ 音频流式播放（不等全部下载）

### 3. 用户体验
- ✅ Loading状态反馈
- ✅ 错误边界处理
- ✅ 优雅降级（API失败时的提示）
- ✅ 动画过渡（Framer Motion）

## 扩展点

### 添加新的AI服务

在 `lib/` 下创建新的service:

```typescript
// lib/deepgram-service.ts
export class DeepgramService {
  async transcribe(audio) {
    // ASR实现
  }
}

// lib/claude-service.ts
export class ClaudeService {
  async chat(text) {
    // LLM实现
  }
}

// lib/cartesia-service.ts
export class CartesiaService {
  async synthesize(text) {
    // TTS实现
  }
}
```

### 添加新的数字人模型

```typescript
// components/VRMCharacter.tsx
import { VRMLoaderPlugin } from '@pixiv/three-vrm';

export default function VRMCharacter() {
  // 3D数字人实现
}
```

### 添加新功能

**示例: 表情识别**
```typescript
// lib/emotion-detector.ts
export function detectEmotion(text: string): EmotionType {
  if (text.includes('哈哈') || text.includes('😄')) {
    return 'happy';
  }
  // ... 更多规则
  return 'neutral';
}

// 在 realtime-service.ts 中使用
const emotion = detectEmotion(responseText);
useDigitalHumanStore.getState().setEmotion(emotion);
```

## 部署架构

```
开发环境:
localhost:3000 → Next.js Dev Server

生产环境:
用户浏览器
    ↓
Vercel Edge Network (CDN)
    ↓
Next.js 服务器 (Serverless)
    ↓
OpenAI Realtime API
```

## 安全考虑

⚠️ **当前实现** (仅用于开发):
- API密钥存储在 `localStorage`
- 直接在浏览器调用API

✅ **生产环境应该**:
```
用户浏览器
    ↓
你的后端服务器 (中继)
    ↓
OpenAI Realtime API
```

**实现方式**:
```typescript
// app/api/realtime/route.ts
export async function POST(req: Request) {
  const { message } = await req.json();
  
  // 服务端调用OpenAI
  const response = await fetch('https://api.openai.com/v1/...', {
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}` // 服务端密钥
    }
  });
  
  return Response.json(response);
}
```

这样API密钥永远不会暴露给客户端。

---

**总结**: 这是一个现代化、模块化的实时互动数字人架构，
使用2025年最新技术栈，易于理解和扩展。
