# AWESOME-DIGITAL-HUMAN
**打造有温度的数字人**  
**给数字人注入灵魂**  
---  
🎉🎉🎉 社区官网公测版本正式发布: https://www.light4ai.com  
[B站视频-社区官网介绍](https://www.bilibili.com/video/BV1YN72z7EBz)  
官网在开源版本基础上额外支持(详情见[操作指南](https://light4ai.feishu.cn/docx/XmGFd5QJwoBdDox8M7zcAcRJnje)):  
* 个人应用管理  
* 内置服务接入  
* 限定主题  
* 应用分享(链接分享、网页嵌入分享)
###### *社区业余时间发电，你的star是我们最大的动力，感谢！*
---  

## 演示
https://github.com/user-attachments/assets/6596fdb6-d9a1-4936-8c3d-312c683690b6

## 主要特性
* 支持 Docker 快速部署
* 超轻量级，配置要求低于2核2G
* 支持 Dify/FastGPT/Coze 等编排框架服务接入
* 支持 ASR、LLM、TTS、Agent 模块化扩展
* 支持 Live2d 人物模型扩展和控制方式
* 支持PC端和移动端web访问
* 支持沉浸式智能对话  
PC端页面预览：  
![](./assets/pc_web.png)  
移动端页面预览：  
![](./assets/phone_web.png)

## 设计架构
大模型的厂商众多、各种工具繁多、要打造自己的数字人需要一定的代码能力和时间投入。  
可通过Coding扩展模块，让一切变得高度定制化。  
可通过Agent编排框架，让一切变得更加简单。  
![](./assets/arch.png)

## 模式支持
> **交互模式**  
* 对话模式：专注于数字人文字交互  
* 沉浸模式：专注与数字人之间拟人方式的直接交互  
* 新闻模式：循环展示财经新闻，两边布局，自动朗读
> **Agent模式**
* ReapterAgent（测试使用）：重复用户输入的语句  
* DifyAgent：接入Dify的服务  
* FastgptAgent：接入fastgpt的服务  
* CozeAgent：接入coze的服务
* OpenaiAgent：接入适配openai接口的服务

## 模式说明

### 新闻模式 vs 对话模式

| 特性 | 新闻模式 | 对话模式 |
|------|---------|---------|
| 点击屏幕 | 无响应（禁用） | 触发默认话术 |
| 输入框 | 隐藏 | 显示 |
| 内容展示 | 新闻列表（两边布局） | 对话记录 |
| 自动朗读 | 自动朗读新闻内容 | 用户发送后朗读 |
| 数据来源 | 财经新闻爬虫 | 大模型对话 |

### 新闻模式功能
- **自动循环**：每15秒自动切换下一条新闻
- **语音合成**：自动朗读新闻标题和内容
- **两边展示**：左侧显示当前新闻，右侧显示下一条新闻预览
- **分类标签**：显示行业、级别、板块、投资评级等信息

### 启用新闻模式
点击顶部工具栏的「新闻模式」按钮即可切换。

## 财经新闻爬虫

本项目集成了财经新闻爬虫功能，位于 `digitalHuman/crawler/` 目录。

### 功能特性
- 财联社电报新闻自动采集
- AI智能分析（行业分类、投资评级）
- 火山引擎豆包大模型集成
- 定时任务支持

### 目录结构
```
digitalHuman/crawler/
├── crawler/          # 爬虫模块
├── ai_analyzer/      # AI分析模块
├── database/         # 数据库模块
├── config/           # 配置模块
├── rating_system/    # 评级系统
└── utils/            # 工具函数
```

### 依赖安装
```bash
cd digitalHuman/crawler
pip install -r requirements.txt
```  

## 版本记录
> ### v1.0.0
**界面简约，注重模块扩展性**
* [v1.0.0 - 2024-06-25](https://github.com/wan-h/awesome-digital-human-live2d/tree/v1.0.0)
  * 前端架构：react + antD
  * 后端架构：fastapi
  * ASR已接入：baiduAPI、googleAPI
  * LLM已接入：baiduAPI、openaiAPI
  * TTS已接入：baiduAPI、edgeAPI
  * Agent支持：repeater(复读机)、dialogue(对话)
  * 人物类型支持：女友（1）、心理师（1）、素人（11）
> ### v2.0.0
**拥抱Dify生态，打造自己的数字人灵魂**
* [v2.0.0 - 2024-08-08](https://github.com/wan-h/awesome-digital-human-live2d/tree/v2.0.0)
  * 前端页面全面升级：nextjs + nextui + tailwind
  * 前端页面兼容移动端访问
  * 前端支持两种交互模式：聊天模式、数字人模式
  * 前端支持人物模型和背景切换以及个人定制扩展
  * Agent支持：difyAgent（ASR、TTS均可接入Dify）、FastGPTAgent、OpenaiAgent
> ### v3.0.0
**强化交互体验**
* [v3.0.0 - 2025-06-01](https://github.com/wan-h/awesome-digital-human-live2d/tree/main)
  * 前端页面全面升级：nextjs + heroui + tailwind
  * 支持动态背景
  * 沉浸模式（实时交互、对话打断等等直接交互方式优化）
  * 支持流式引擎([协议文档](./docs/streaming_protocol.md))
    * FunASR streaming(在沉浸模式可选)  
  * Agent扩展支持：CozeAgent（ASR、TTS均可接入Coze）

## TODOList
- [ ] rtc音视频流支持
- [ ] 跨模态交互支持(麦克风/摄像头)
- [ ] 人物模型AI生成尝试
- [ ] 情感控制人物表情动作支持

## 部署&开发
[部署说明](./docs/deploy_instrction.md)  
[开发说明](./docs/developer_instrction.md)  
[v2.0.0 常见问题](./docs/Q&A.md)  

[v2.0.0 B站视频教程-部署](https://www.bilibili.com/video/BV1szePeaEak/)  
[v2.0.0 B站视频教程-All-in-Dify部署](https://www.bilibili.com/video/BV1kZWvesE25/)

## Love & Share
**知乎板块**  
[数字人-定义数字世界中的你](https://zhuanlan.zhihu.com/p/676746017)  
[RAG架构浅析](https://zhuanlan.zhihu.com/p/703262854)  
[dify源码解析-RAG](https://zhuanlan.zhihu.com/p/704341817)  
[RAG-索引之PDF文档解析](https://zhuanlan.zhihu.com/p/707271297)  
[Dify打造专属数字人灵魂](https://zhuanlan.zhihu.com/p/714961925)  
[数字人的All in Dify](https://zhuanlan.zhihu.com/p/716359038)  
[数字人的All in Coze](https://zhuanlan.zhihu.com/p/1928506957968413871)
  
**微信公众号板块**  
[数字人-定义数字世界中的你](https://mp.weixin.qq.com/s/SQvFysHO8daN0HMA0AaJZw)  
[RAG架构浅析](https://mp.weixin.qq.com/s/4iWrJonD8_kjxw4ILibzSw)  
[dify源码解析-RAG](https://mp.weixin.qq.com/s/muCTFTWLY8j5UtxwCaW93A)  
[RAG-索引之PDF文档解析](https://mp.weixin.qq.com/s/innbTL6aeOsl9vyJSN6yBw)  
[Dify打造专属数字人灵魂](https://mp.weixin.qq.com/s/3B4YgYjDY42DNTgE76XOtw)  
[数字人的All in Dify](https://mp.weixin.qq.com/s/Uf17jWpjVzAfzX42TP09gw)  
[数字人的All in Coze](https://mp.weixin.qq.com/s/DbFUmmxBmlPgMOQ16tRDfw)

**Dify 官方板块**  
[Dify公众号文章：使用 Dify 打造数字人灵魂](https://mp.weixin.qq.com/s?__biz=Mzg5MDkyOTY3NA==&mid=2247486070&idx=3&sn=0911ba8723278a83c1554afd2de861ab&chksm=cefc58effe2456e39a9f0f0afac4ec5447bb1aafff42a68d05b2a3f523baae299b93d7ae6ff9&mpshare=1&scene=1&srcid=1021NXKMC2W697dCXEwqsCkN&sharer_shareinfo=93041ce9bdefcde0aa121d27a3f3f6dd&sharer_shareinfo_first=8c8f03435bc9af5236a4505b831d1388&exportkey=n_ChQIAhIQQaNAHzm7bGdYinsq2L2zbRKfAgIE97dBBAEAAAAAANTKKNX7j3cAAAAOpnltbLcz9gKNyK89dVj0%2F3Ojxo5%2FA9C00dmnAyJraAwSYIfMr4csl8xZvE%2FSwCi3nKbPJZ4mnLdQdVm2EQP2SNJQIMUqV1PGB%2BGpSSdjOs6L7ejtFS9GCpkr6LMmAKVW904Tu4tGhZwjaU14QjLRGXZ7rQEKMOQjdQTyDf%2BluwFEDAXlLMozezq6ypTwXIu0HoLjs4Q6x4gtHS%2BpH6vhOfGgR7LtVbZcXAFFWokyvREiMuHayOSrjtpDD9CQK5KYELY7Ejd%2B48JRj7dRJZiAGebg2KRYtB7%2BpJqgyKaNO4mCcT%2BT9KjHq4WIssWaF0Vq5G4D2el%2FhIgfuEpreoR1hUKOMkcBiAXZ&acctmode=0&pass_ticket=Tg8MLw6UPqgdcjRxs7YP26i09LNlJcKEH%2Bw9YwPdaE4OzNwhW7RbDzgVM3X5rkY1&wx_header=0#rd)

**产研板块**  
[数字人调研问卷](https://ec5cjmeodk.feishu.cn/share/base/dashboard/shrcnu1DNMUCTU18f5tF2q9qoQh)（感谢 [@plumixius](https://github.com/plumixius) 同学）

## Thanks
### 开源项目
* [Dify](https://github.com/langgenius/dify)  
* [Live2D](https://github.com/Live2D)  
* [FunASR](https://github.com/modelscope/FunASR)
* 源码中涉及到的所有库作者

## 社区联系
**扫码请备注 ADH**    
| 商务合作 | 兴趣小组 |
| --- | --- |
| ![](assets/wechat_2.png) | ![](assets/wechat_1.png) |


这是财经新闻数据表的字段说明：
字段名	类型	含义说明
id	int	主键ID，自增，唯一标识每条新闻
title	varchar(500)	新闻标题，必填
content	text	新闻正文内容，必填
source_url	varchar(1000)	新闻原始链接，如 https://www.cls.cn/detail/xxx
publish_time	datetime	新闻发布时间，从财联社页面获取
category	varchar(100)	新闻分类，如：快讯、公告、行业动态等
crawl_time	datetime	爬取时间，默认当前时间，记录何时入库
ai_summary	text	AI摘要，LLM生成的新闻摘要
accuracy_score	float	准确率评分（已废弃），之前用于校准性分析
investment_rating	int	投资评级，1-10分，分数越高投资价值越大
investment_type	varchar(20)	投资类型：短期 / 长期
is_viral	tinyint(1)	是否重磅：0=普通新闻，1=重磅新闻
industry	varchar(100)	所属行业，如：科技、金融、医药、汽车等
industry_level	varchar(20)	行业等级：A级（高景气）/ B级（一般）/ C级（低景气）
sector	varchar(100)	细分板块，如：人工智能、新能源汽车、创新药等
analysis_time	datetime	分析时间（已废弃，用analyzed_at替代）
recommended_industry	varchar(500)	推荐行业（已废弃）
concepts	varchar(500)	相关概念，如：AI芯片、固态电池等
related_stocks	varchar(500)	相关股票，提及的上市公司
analyzed_at	timestamp	AI分析完成时间，记录何时完成LLM分析
source	varchar(50)	新闻来源，默认"财联社"
analysis	text	AI分析内容，LLM生成的投资建议和分析报告
