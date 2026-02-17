# 🤖 实时互动数字人 - 2025最新技术

基于OpenAI Realtime API和Live2D的现代化实时互动数字人系统。

## ✨ 特性

- ⚡ **超低延迟** - 端到端延迟 < 1秒，使用OpenAI Realtime API
- 🎙️ **语音交互** - 支持实时语音输入和语音打断
- 💬 **智能对话** - 基于GPT-4o的自然对话能力
- 🎭 **口型同步** - 实时音频分析，精确的嘴型同步
- 🎨 **现代化UI** - 使用Framer Motion的流畅动画
- 📱 **响应式设计** - 完美支持桌面和移动设备

## 🛠️ 技术栈（2025最新）

### 前端框架
- **Next.js 15** - React元框架
- **React 19** - 最新React特性
- **TypeScript 5.7** - 类型安全

### UI/UX
- **Tailwind CSS v4** - 实用优先的CSS框架
- **Framer Motion 12** - 高性能动画库
- **Lucide React** - 现代化图标库

### 数字人渲染
- **PixiJS 8** - 2D WebGL渲染引擎
- **Live2D Cubism SDK** - 2D数字人模型（需单独安装）

### AI服务
- **OpenAI Realtime API** - 2024年10月发布的革命性API
  - 集成ASR（语音识别）
  - 集成LLM（对话生成）
  - 集成TTS（语音合成）
  - 端到端流式处理

### 状态管理
- **Zustand 5** - 轻量级状态管理

## 📦 安装

### 1. 克隆项目

```bash
# 如果从GitHub克隆
git clone https://github.com/your-username/digital-human-2025.git
cd digital-human-2025

# 或直接使用这些文件
```

### 2. 安装依赖

```bash
npm install
# 或
pnpm install
# 或
yarn install
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env.local

# 编辑 .env.local，填入你的OpenAI API密钥
```

获取API密钥: https://platform.openai.com/api-keys

**重要提示**: Realtime API需要OpenAI付费账户，确保账户有足够余额。

### 4. 启动开发服务器

```bash
npm run dev
```

打开 http://localhost:3000 查看效果。

## 🎯 使用指南

### 基础使用

1. **连接API**
   - 点击右上角设置按钮
   - 输入OpenAI API密钥
   - 点击"连接"

2. **开始对话**
   - **文本输入**: 在底部输入框输入消息，按Enter或点击发送
   - **语音输入**: 点击麦克风按钮开始录音，再次点击停止
   - **语音打断**: 说话时可以随时打断AI

3. **查看效果**
   - 观察数字人的口型同步
   - 查看实时对话记录
   - 体验低延迟语音交互

## 🔧 进阶配置

### 添加真实Live2D模型

项目默认使用占位符，要使用真实Live2D模型:

1. **获取Live2D模型**
   ```bash
   # 下载官方示例模型
   https://www.live2d.com/en/download/sample-data/
   ```

2. **安装Live2D SDK**
   ```bash
   npm install @cubism/live2d-web-sdk
   ```

3. **放置模型文件**
   ```
   public/models/
   └── your-character/
       ├── character.model3.json
       ├── character.moc3
       ├── textures/
       └── motions/
   ```

4. **更新代码**
   在 `components/Live2DCharacter.tsx` 中修改模型路径:
   ```typescript
   const model = await Live2DModel.from('/models/your-character/character.model3.json');
   ```

### 自定义AI行为

编辑 `lib/realtime-service.ts` 中的系统提示词:

```typescript
instructions: `你是一个友好、活泼的AI助手...`,
voice: 'alloy', // 可选: alloy, echo, shimmer
temperature: 0.8, // 控制创造性 (0-1)
```

### 使用其他AI服务

如果不想用OpenAI Realtime API，可以替换为:

**方案A: Deepgram + Claude + Cartesia**
```typescript
// 需要分别实现ASR、LLM、TTS
// 参考 lib/alternative-services/ (需自行创建)
```

**方案B: Azure OpenAI**
```typescript
// 修改endpoint即可
const client = new RealtimeClient({
  apiKey: AZURE_API_KEY,
  endpoint: 'https://your-resource.openai.azure.com',
});
```

## 📂 项目结构

```
digital-human-2025/
├── app/
│   ├── page.tsx              # 主页面
│   ├── layout.tsx            # 根布局
│   └── globals.css           # 全局样式
├── components/
│   ├── Live2DCharacter.tsx   # 数字人渲染组件
│   ├── ChatInterface.tsx     # 聊天界面
│   └── ConnectionSettings.tsx # 连接设置
├── lib/
│   ├── store.ts              # Zustand状态管理
│   └── realtime-service.ts   # Realtime API封装
├── public/
│   └── models/               # Live2D模型文件
├── package.json
├── tsconfig.json
├── next.config.js
└── README.md
```

## 🚀 部署

### Vercel (推荐)

```bash
# 安装Vercel CLI
npm i -g vercel

# 部署
vercel
```

### 其他平台

```bash
# 构建生产版本
npm run build

# 启动生产服务器
npm start
```

## 💰 成本估算

使用OpenAI Realtime API的成本:

- **输入音频**: $0.06 / 分钟
- **输出音频**: $0.24 / 分钟
- **文本输入**: $5 / 1M tokens
- **文本输出**: $20 / 1M tokens

**示例**: 10分钟对话 ≈ $3-5

💡 **省钱技巧**:
- 使用文本输入代替语音（便宜很多）
- 简短的系统提示词
- 使用较小的max_tokens

## ⚠️ 注意事项

1. **浏览器兼容性**
   - Chrome/Edge 90+ ✅
   - Firefox 88+ ✅
   - Safari 14+ ✅（需HTTPS）

2. **API密钥安全**
   - 当前示例在客户端使用API密钥
   - **生产环境必须使用服务端中继**
   - 参考: [OpenAI Best Practices](https://platform.openai.com/docs/guides/production-best-practices)

3. **延迟优化**
   - 确保网络连接稳定
   - 使用距离较近的服务器区域
   - 考虑使用WebRTC优化

## 🐛 故障排除

### 无法连接API
- 检查API密钥是否正确
- 确认账户有余额
- 检查网络连接

### 没有声音
- 检查浏览器权限（麦克风/音频）
- 确认音频输出设备正常
- 查看浏览器控制台错误

### 口型不同步
- 检查音频分析器是否工作
- 确认Live2D模型参数名称正确
- 调整音量阈值

## 📚 学习资源

- [OpenAI Realtime API文档](https://platform.openai.com/docs/guides/realtime)
- [Live2D Cubism SDK](https://www.live2d.com/en/sdk/)
- [Next.js 15文档](https://nextjs.org/docs)
- [PixiJS 8教程](https://pixijs.com/8.x/guides)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

**🎉 享受使用最新技术构建的实时互动数字人！**

有问题？欢迎提Issue或联系作者。
