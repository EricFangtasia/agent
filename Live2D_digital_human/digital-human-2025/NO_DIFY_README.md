# 无Dify依赖的数字人系统

本项目提供了一个无需Dify和Docker的数字人系统版本，可以直接在本地运行。

## 特性

- ⚡ **零依赖启动** - 无需Dify和Docker
- 🎭 **实时互动** - 支持语音和文本交互
- 🎨 **Live2D渲染** - 2D数字人形象
- 🧠 **智能对话** - 内置简化AI服务
- 🎤 **语音交互** - 支持语音输入和输出

## 安装和运行

### 前提条件

- Node.js 18+ (推荐使用 LTS 版本)
- npm 包管理器

### 快速启动

1. **确保安装了 Node.js**

   ```bash
   node --version
   npm --version
   ```

2. **运行启动脚本**

   Windows 用户：
   ```bash
   双击 START_HERE.bat
   ```

   macOS/Linux 用户：
   ```bash
   npm install
   npm run dev
   ```

3. **访问应用**

   打开浏览器，访问 `http://localhost:3000/no-dify`

### 手动启动

如果你想手动启动项目：

1. 安装依赖：
   ```bash
   npm install
   ```

2. 启动开发服务器：
   ```bash
   npm run dev
   ```

## 使用说明

### 连接设置

1. 打开 `http://localhost:3000/no-dify`
2. 在连接设置区域输入API密钥（可选，可以使用任意非空字符串）
3. 点击"连接服务"按钮

### 文本对话

1. 在底部输入框中输入消息
2. 点击"发送"按钮或按 Enter 键发送
3. 等待AI回复并在数字人上看到口型同步

### 语音对话

1. 点击"语音输入"按钮开始录音
2. 说出你想说的话
3. 再次点击按钮停止录音
4. 系统将自动识别语音并生成AI回复

## 项目架构

```
digital-human-2025/
├── app/
│   ├── no-dify/page.tsx          # 无Dify版本主页
│   └── page.tsx                  # 根页面（重定向到no-dify）
├── components/
│   └── Live2DCharacter.tsx       # 数字人渲染组件
├── lib/
│   ├── store.ts                  # Zustand状态管理
│   ├── realtime-service.ts       # 实时服务（已修改）
│   └── simplified-ai-service.ts  # 简化AI服务
├── public/
│   └── models/                   # Live2D模型文件
├── START_HERE.bat                # Windows启动脚本
└── NO_DIFY_README.md             # 本文档
```

## 技术栈

- **Next.js 15** - React元框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式设计
- **Framer Motion** - 动画效果
- **PixiJS 8** - 2D渲染引擎
- **Live2D** - 2D角色渲染
- **Zustand** - 状态管理

## 配置自定义模型

要使用自己的Live2D模型：

1. 将模型文件放入 `public/models/` 目录
2. 模型应包含 `.model3.json` 配置文件
3. 修改 `components/Live2DCharacter.tsx` 中的模型路径

示例结构：
```
public/models/
└── my-character/
    ├── character.model3.json
    ├── character.moc3
    ├── textures/
    └── motions/
```

## 疑难解答

### 无法启动

- 确保 Node.js 版本 >= 18
- 检查端口 3000 是否被占用
- 删除 `.next` 目录并重新运行 `npm run dev`

### 麦克风权限

- 确保浏览器允许访问麦克风
- 检查操作系统是否阻止了麦克风访问

### 数字人不显示

- 检查浏览器控制台是否有错误
- 确保 WebGL 已启用

## 自定义开发

如需自定义功能：

1. 修改 `lib/simplified-ai-service.ts` 来改变AI响应逻辑
2. 调整 `components/Live2DCharacter.tsx` 来修改数字人外观
3. 编辑 `app/no-dify/page.tsx` 来更改界面布局

## 许可证

MIT License