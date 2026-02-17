# agent_sensevoice_intentdetection_emotion_vlm_tts.py

# 1,语音识别、2,意图识别/文本生成、3,情感识别、4,视觉识别 、5,语音合成

# 1，调用SenseVoice进行语音识别
from agent.asr.sensevoice_demo import SenseVoiceASR

# 2，调用意图识别/文本生成模型 从agent/llm/agent_bailian/test_intent_detection.py中获取
from agent.llm.agent_bailian.test_intent_detection import detect_intent

# 3，调用情感识别模型 从agent/中获取

# 4，调用视觉识别模型，vlm模型

# 5，调用语音合成模型，百炼的tts模型
