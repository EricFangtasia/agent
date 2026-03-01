# 预生成音频目录
此目录存放预生成的名言和话术音频文件

运行以下命令生成音频：
```bash
cd d:\project\py\agent\adh\Live2D_digital_human\awesome-digital-human-live2d
python scripts/extract_and_generate_audio.py
```

音频文件命名规则：
- q_0001.mp3 ~ q_XXXX.mp3: 名言音频
- r_0001.mp3 ~ r_0020.mp3: 留人话术音频
- g_0001.mp3 ~ g_0020.mp3: 礼物话术音频
- index.json: 索引文件
