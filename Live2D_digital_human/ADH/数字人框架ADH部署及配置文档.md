# DIFY+数字人框架ADH部署及配置文档

## 1. 前言

数字人框架ADH部署及配置文档，主要介绍了数字人框架ADH的部署和配置方法，包括Awesome Digital Human的安装和配置等。

本项目旨在通过dify提供数字人的LLM（大模型） ASR（语音识别） TTS（文本转语音） 的能力，通过ADH前端展示。

来自与开源项目：https://github.com/wan-h/awesome-digital-human-live2d

B站的地址：https://space.bilibili.com/14600648 一力辉

资源网盘地址：https://pan.quark.cn/s/f12c1f5b733c

## 2. 部署方法

### 下载

从githug拉取或直接在上述网盘中下载：

```
git clone https://github.com/wan-h/awesome-digital-human-live2d.git
```

### 配置文件的修改

切换到 configs 目录下，执行下述代码：

```
# 使用 all in dify 配置文件，默认使用 config_template.yaml 配置文件
cd configs
cp config_all_in_dify.yaml config.yaml
```

### docker容器部署

两种方式：

#### 方式一：快速启动(体验)
```
# 项目根目录下执行
docker-compose -f docker-compose-quickStart.yaml up -d
```
#### 方式二：可开发启动(可额外配置)
```
# 项目根目录下执行
docker-compose up --build -d
```
执行完上述命令之后在浏览器中输入：http://localhost:3000/ 即可访问ADH。

## 3.dify的配置

### 获取api及服务url

打开dify中任意一个工作流或对话流，点击右上角的 `发布`-`API` 按钮，即可访问到API页面。

点击右上角的`api密钥-创建密钥-复制密钥`。

需要说明的是，由于我们的dify和ADH都是部署在docker中，所以服务器的url地址应设置为`http://本地局域网下ip/v1`，或者是`http://host.docker.internal/v1`，如果部署在其他服务器上，则需要修改为相应的地址。

### 去ADH中配置dify服务

回到`http://localhost:3000/` 打开左上角的settings-服务，依次将上述的API密钥、服务url填入相应的输入框中，点击保存即可。

### 测试响应

在输入框中测试输入文本，查看是否有对话响应。

### 配置dify的语音识别和文本转语音

- 打开右上角的`设置-模型提供商-添加模型提供商`，选择`阿里百炼`，输入api密钥信息，点击保存即可。
- 点击`系统默认模型-设置默认模型`，选择`qwen-tts`，点击保存。
- 语音识别模型配置同上。

### 在工作流或对话流中配置上述两个模型

打开对应的工作流或对话流（聊天助手），点击右下角的`管理`，设置`文字转语音`和`语音转文字`的配置项。

**点击右上角`发布-发布更新`**。

### ADH中测试语音沟通能力

打开ADH，`麦克风`按钮，说一句话，点击`发送`按钮，查看是否有语音响应。

如何显示`未获取麦克风权限`，则需要在浏览器设置中打开麦克风权限。

打开方式如下：

- 打开浏览器设置，`网站设置-权限设置-麦克风`，打开`麦克风`权限。

## 4. ADH的配置

### 端口配置

**后端端口配置**

打开项目源码中的`awesome-digital-human-live2d-main\docker-compose-quickStart.yaml`或`awesome-digital-human-live2d-main\docker-compose.yaml`
修改`ports`的值，其中3000为前端端口，8000为后端端口。

### 修改默认人物模型

打开项目源码中的`awesome-digital-human-live2d-main\web\app\lib\live2d\lappdefine.ts`
找到：
```
//模型定义----------------------------------
export const ModelsDesc: string[] = [
  'Kei', 'Haru-1', 'Haru-2', 'Chitose', 'Mao', 'Miara', 'Tsumiki', 'Rice', 'Epsilon', 'Hibiki', 'Izumi', 'Shizuku', 'Hiyori'
];
export const ModelDefault = 'Haru-2';
```
此时，我们就将`ModelDefault`改为我们想要的模型，比如`Haru-2`。

### 添加背景图片

粘贴一张图片至：`awesome-digital-human-live2d-main\web\public\backgrounds`文件夹下，jpg格式确认可用，其他格式自行测试

打开项目源码中的`awesome-digital-human-live2d-main\web\app\lib\live2d\lappdefine.ts`
找到：
```
// 模型后面的背景图像文件
export const BackImages: string[] = [
  'forest_trail', 'night_street' , 'mine_background'
];
```
其中`mine_background`就是我们自己添加的图片
**注意：图片名称要与文件名称一致，但不包括拓展名，即.jpg**。

### 配置默认dify服务参数

找到`awesome-digital-human-live2d-main\configs\agents\difyAgent.yaml`,
```
NAME: "DifyAgent"
VERSION: "v0.0.1"
# 暴露给前端的参数选项以及默认值
PARAMETERS: [
  {
    NAME: "DIFY_API_URL",
    DEFAULT: "" # 这里填入dify的api地址
  },
  {
    NAME: "DIFY_API_KEY",
    DEFAULT: "" # 这里填入dify的api密钥
  },
  {
    NAME: "DIFY_API_USER",
    DEFAULT: "adh"
  }
]
```

### 设置模型默认动作

由于框架中的部门人物模型，有怪异的表现，我们需要新增或删除部分动作，这里以`haru-2`模型为例，删除部分动作：

打开项目源码中的`awesome-digital-human-live2d-main\web\public\characters\Haru-2\Haru-2.model3.json`
找到：
```
"Motions": {
			"Idle": [
				{
					"File": "motions/微笑-正常.motion3.json",
					"FadeInTime": 0.5,
					"FadeOutTime": 0.5
				},
				{
					"File": "motions/微笑-背手点头.motion3.json",
					"FadeInTime": 0.5,
					"FadeOutTime": 0.5
				},
				{
					"File": "motions/高兴-身体前倾眯眼.motion3.json",
					"FadeInTime": 0.5,
					"FadeOutTime": 0.5
				}
			],

```

删除其中`高兴-身体前倾眯眼.motion3.json`和`微笑-向前浅鞠躬.motion3.json`这两行，保存文件。
**注意：要删除掉整个{}及包裹中的内容和逗号，ctrl+s保存**。

至此，基本配置都已经完成。

## 5. 启动修改配置后的ADH

```
# 项目根目录下执行
docker-compose up --build -d
```

打开浏览器，输入：http://localhost:3000/ 即可访问ADH。