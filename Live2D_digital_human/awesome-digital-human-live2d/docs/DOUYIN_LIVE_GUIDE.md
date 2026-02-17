# 抖音直播数字人集成指南

## 功能说明

数字人可以实时读取抖音直播间的互动消息，自动回答观众提问，营造更生动的直播氛围！

## 功能特性

- ✅ **实时问答**：自动识别观众提问并生成回答
- ✅ **语音播报**：数字人语音朗读回答，同步口型动画
- ✅ **礼物感谢**：自动感谢送礼观众
- ✅ **欢迎新人**：欢迎新进入直播间的观众
- ✅ **智能过滤**：可配置关键词过滤和回答策略

---

## 快速开始

### 第一步：申请抖音开放平台权限

1. **注册开发者**
   - 访问 [https://open.douyin.com/](https://open.douyin.com/)
   - 使用抖音账号登录
   - 完成开发者认证（个人或企业）

2. **创建应用**
   - 进入「应用管理」
   - 点击「创建应用」
   - 填写应用信息（名称、分类、描述）
   - 选择「网页应用」类型

3. **申请权限**
   - 在应用详情中找到「权限管理」
   - 申请以下权限：
     - `user_info`：获取用户信息
     - `live.room`：获取直播间信息
     - `live.data`：获取直播数据
   - 等待审核通过（通常1-3个工作日）

4. **获取密钥**
   - 审核通过后，在应用详情中查看：
     - **Client Key**（客户端密钥）
     - **Client Secret**（客户端密钥）
   - 妥善保管这两个密钥！

---

### 第二步：获取Access Token

#### 方法1：通过OAuth授权（推荐）

1. **生成授权链接**
```python
client_key = "YOUR_CLIENT_KEY"
redirect_uri = "http://localhost:8880/douyin/callback"  # 回调地址
scope = "user_info,live.room,live.data"

auth_url = f"https://open.douyin.com/platform/oauth/connect/?client_key={client_key}&response_type=code&scope={scope}&redirect_uri={redirect_uri}"

print(f"请在浏览器中打开以下链接进行授权：\n{auth_url}")
```

2. **用户授权**
   - 在浏览器中打开上述链接
   - 登录抖音账号
   - 确认授权

3. **获取授权码**
   - 授权成功后会跳转到回调地址
   - URL中包含授权码：`http://localhost:8880/douyin/callback?code=AUTHORIZATION_CODE`

4. **兑换Access Token**
```python
from digitalHuman.engine.douyin_live_client import DouyinLiveClient

client = DouyinLiveClient(
    client_key="YOUR_CLIENT_KEY",
    client_secret="YOUR_CLIENT_SECRET"
)

# 使用授权码获取token
access_token = await client.get_access_token(code="AUTHORIZATION_CODE")
print(f"Access Token: {access_token}")
```

#### 方法2：手动配置（测试用）

如果您已经有了Access Token，可以直接配置：

```python
access_token = "YOUR_ACCESS_TOKEN"
```

---

### 第三步：启动直播服务

在后端main.py中添加启动代码：

```python
from digitalHuman.engine.douyin_live_service import DouyinLiveService

# 在服务器启动时初始化
douyin_service = DouyinLiveService(
    agent_pool=agent_pool,  # Agent引擎池
    tts_engine_pool=engine_pool  # TTS引擎池
)

# 启动抖音直播监听
await douyin_service.start(
    client_key="YOUR_CLIENT_KEY",
    client_secret="YOUR_CLIENT_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    room_id="YOUR_ROOM_ID",  # 您的直播间ID
    agent_name="OpenAI",  # 使用的LLM引擎
    tts_engine="EdgeTTS"  # 使用的TTS引擎
)
```

---

## 配置说明

### 基础配置

在 `configs/config.yaml` 中添加：

```yaml
DOUYIN_LIVE:
  ENABLED: true  # 是否启用抖音直播功能
  CLIENT_KEY: "your_client_key"
  CLIENT_SECRET: "your_client_secret"
  ACCESS_TOKEN: "your_access_token"
  ROOM_ID: "your_room_id"
  
  # Agent配置
  AGENT:
    ENGINE: "OpenAI"  # 使用的LLM引擎
    MODEL: "gpt-3.5-turbo"  # 模型名称
    TEMPERATURE: 0.7  # 生成温度
    MAX_TOKENS: 100  # 最大token数
  
  # TTS配置
  TTS:
    ENGINE: "EdgeTTS"  # 使用的TTS引擎
    VOICE: "zh-CN-XiaoxiaoNeural"  # 语音角色
    RATE: 0  # 语速
  
  # 功能开关
  FEATURES:
    AUTO_REPLY: true  # 自动回复问题
    REPLY_TO_GIFTS: true  # 回复礼物感谢
    WELCOME_NEW_MEMBERS: false  # 欢迎新观众
    
  # 回答策略
  REPLY_STRATEGY:
    MAX_ANSWER_LENGTH: 50  # 回答最大字数
    REPLY_DELAY: 2  # 回答延迟（秒）
    FILTER_KEYWORDS:  # 过滤关键词
      - "广告"
      - "刷单"
      - "加微信"
```

### 高级配置

```yaml
  # 智能过滤
  SMART_FILTER:
    ENABLED: true
    MIN_QUESTION_LENGTH: 3  # 最短问题长度
    MAX_QUESTION_LENGTH: 200  # 最长问题长度
    DUPLICATE_CHECK: true  # 检查重复问题
    DUPLICATE_WINDOW: 60  # 重复检查时间窗口（秒）
  
  # 回答模板
  ANSWER_TEMPLATES:
    GREETING: "你好{nickname}！"
    THANKS: "感谢{nickname}的{gift}！"
    WELCOME: "欢迎{nickname}来到直播间！"
    NO_ANSWER: "这个问题有点难哦，让我想想~"
```

---

## 使用示例

### 示例1：基础使用

```python
import asyncio
from digitalHuman.engine.douyin_live_service import DouyinLiveService

async def main():
    # 初始化服务
    service = DouyinLiveService(agent_pool, tts_pool)
    
    # 启动监听
    await service.start(
        client_key="your_key",
        client_secret="your_secret",
        access_token="your_token",
        room_id="your_room_id"
    )

asyncio.run(main())
```

### 示例2：自定义回调

```python
# 自定义问题处理逻辑
async def custom_question_handler(user, question):
    # 添加自定义逻辑
    if "价格" in question:
        return "我们的产品性价比超高哦！"
    elif "优惠" in question:
        return "现在下单有优惠，快来抢购！"
    return None  # 返回None使用默认处理

# 绑定自定义回调
service.custom_handler = custom_question_handler
```

---

## 常见问题

### Q1: 如何获取直播间ID？

A: 
1. 打开抖音APP或网页版
2. 进入您的直播间
3. 直播间URL中包含room_id，例如：
   - APP分享链接：`https://live.douyin.com/123456789`
   - room_id就是：`123456789`

### Q2: Access Token多久过期？

A: 抖音的Access Token有效期一般为30天，过期后需要重新授权。建议实现自动刷新机制。

### Q3: API调用有频率限制吗？

A: 有的。抖音开放平台对API调用有频率限制：
- 单个用户：100次/分钟
- 单个应用：10000次/分钟
建议合理控制拉取频率，避免被限流。

### Q4: 能否同时监听多个直播间？

A: 可以。为每个直播间创建一个独立的service实例即可。

### Q5: 如何测试功能？

A: 
1. 先在抖音APP中开启直播
2. 启动数字人服务
3. 在另一个账号发送评论测试
4. 观察控制台日志和数字人反应

---

## 注意事项

⚠️ **重要提示**：

1. **遵守平台规则**
   - 不要发送违规内容
   - 不要频繁刷屏
   - 遵守抖音直播公约

2. **保护密钥安全**
   - 不要将Client Secret提交到代码仓库
   - 使用环境变量或配置文件管理密钥
   - 定期更换Access Token

3. **优化用户体验**
   - 回答要简洁明了
   - 避免过长的等待时间
   - 可以设置回答队列避免冲突

4. **性能优化**
   - 合理设置拉取频率
   - 使用缓存减少重复计算
   - 监控API调用次数

---

## 技术支持

如有问题，请查看：
- [抖音开放平台文档](https://open.douyin.com/platform/doc)
- 项目GitHub Issues
- 技术交流群

---

## 更新日志

### v1.0.0 (2026-02-09)
- ✨ 初始版本
- ✅ 支持实时问答
- ✅ 支持礼物感谢
- ✅ 支持新人欢迎

---

祝您使用愉快！🎉
