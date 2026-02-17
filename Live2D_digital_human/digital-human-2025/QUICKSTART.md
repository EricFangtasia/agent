# 🚀 5分钟快速开始

## 最小化步骤，立即体验实时互动数字人

### 步骤 1: 准备API密钥 (2分钟)

1. 访问 https://platform.openai.com/api-keys
2. 登录你的OpenAI账户
3. 点击 "Create new secret key"
4. 复制密钥（格式: `sk-...`）
5. **确保账户有余额** (至少$5)

💡 **没有OpenAI账户？**
- 注册地址: https://platform.openai.com/signup
- 需要绑定信用卡充值

---

### 步骤 2: 下载并安装 (1分钟)

```bash
# 1. 下载项目
# （如果你已经有这些文件，跳过这步）

# 2. 进入项目目录
cd digital-human-2025

# 3. 安装依赖
npm install
```

---

### 步骤 3: 配置环境变量 (30秒)

```bash
# 创建 .env.local 文件
echo "NEXT_PUBLIC_OPENAI_API_KEY=你的API密钥" > .env.local
```

或者手动创建 `.env.local` 文件，内容如下:
```
NEXT_PUBLIC_OPENAI_API_KEY=sk-your-api-key-here
```

---

### 步骤 4: 启动项目 (1分钟)

```bash
npm run dev
```

打开浏览器访问: http://localhost:3000

---

### 步骤 5: 开始使用 (立即体验)

1. **连接API**
   - 点击右上角 ⚙️ 设置按钮
   - 输入API密钥
   - 点击"连接"
   - 看到绿色"已连接"提示

2. **文字对话**
   - 在底部输入框输入: "你好，介绍一下你自己"
   - 按Enter或点击发送按钮
   - 观察数字人说话时的口型同步

3. **语音对话** 🎤
   - 点击麦克风按钮
   - 对着麦克风说话
   - 再次点击麦克风停止录音
   - 等待AI语音回复

4. **测试语音打断**
   - 在AI说话时直接开始录音
   - 体验实时打断功能

---

## ✅ 成功标志

如果你看到:
- ✅ 右上角显示"已连接"
- ✅ 能发送消息并收到回复
- ✅ 数字人的嘴巴随着语音动
- ✅ 能听到AI的语音回复

**恭喜！你已经成功运行了一个2025最新技术的实时互动数字人！**

---

## 🐛 常见问题

### Q1: 连接失败
**A**: 
- 检查API密钥是否正确
- 确认账户有余额
- 尝试刷新页面

### Q2: 没有声音
**A**:
- 检查浏览器是否允许音频播放
- 查看浏览器控制台是否有错误
- 尝试调高音量

### Q3: 麦克风不工作
**A**:
- 允许浏览器访问麦克风权限
- 检查麦克风是否被其他应用占用
- 使用Chrome浏览器（兼容性最好）

### Q4: 报错 "API key not valid"
**A**:
- 确认密钥完整复制（以 `sk-` 开头）
- 检查 `.env.local` 文件格式
- 重启开发服务器: `Ctrl+C` 然后重新 `npm run dev`

---

## 🎯 下一步

现在你已经成功运行了基础版本，可以尝试:

### 🎨 自定义数字人
1. 下载Live2D模型
2. 放到 `public/models/` 目录
3. 修改 `components/Live2DCharacter.tsx` 中的模型路径

### 💬 调整AI性格
编辑 `lib/realtime-service.ts` 的系统提示词:
```typescript
instructions: `你是一个xxx，擅长xxx...`,
```

### 🎤 更换语音
修改语音类型:
```typescript
voice: 'shimmer', // 可选: alloy, echo, shimmer
```

### 🚀 部署上线
```bash
# 部署到Vercel
npm i -g vercel
vercel
```

---

## 📚 进阶学习

- 📖 [完整README](./README.md) - 详细文档
- 🔬 [技术对比](./TECH_COMPARISON.md) - 不同方案对比
- 💻 [源码解析](./components/) - 理解实现原理

---

## 💰 成本控制

每次对话的成本约:
- **文字对话**: < $0.01
- **语音对话**: $0.3-0.5 (1分钟)

💡 **省钱技巧**:
- 优先使用文字对话测试功能
- 缩短系统提示词
- 设置 `max_tokens` 限制

---

**🎉 祝你玩得开心！有问题随时查看文档或提Issue。**
