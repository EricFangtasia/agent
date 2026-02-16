# IndexTTS 本地化部署与声音克隆指南

## 简介

IndexTTS 是一个先进的多语言文本转语音系统，支持零样本声音克隆功能。本项目提供了一个本地化部署的解决方案，无需依赖网络API。

## 功能特性

- 支持多语言文本转语音
- 零样本声音克隆（仅需3-5秒参考音频）
- 高质量语音合成
- 本地化部署，保护隐私

## 系统要求

- Python 3.8 或更高版本
- 至少16GB RAM（推荐32GB）
- 足够的磁盘空间存储模型文件（约8GB）
- （可选）支持CUDA的GPU以加速推理

## 依赖安装

1. 创建虚拟环境（推荐）：
   ```bash
   python -m venv indextts_env
   .\indextts_env\Scripts\Activate.ps1  # Windows PowerShell
   # 或
   source indextts_env/bin/activate     # Linux/Mac
   ```

2. 安装基础依赖：
   ```bash
   pip install torch torchaudio
   pip install cn2an pypinyin jieba librosa omegaconf safetensors transformers>=4.46.0 einops json5 sentencepiece munch matplotlib wetext descript-audiotools
   ```

## 模型下载

IndexTTS需要多个模型文件才能正常运行。请按以下步骤下载：

1. 克隆IndexTTS代码仓库：
   ```bash
   git clone https://github.com/index-tts/index-tts.git git/index-tts
   cd git/index-tts
   git lfs pull  # 获取大文件
   ```

2. 下载模型文件到checkpoints目录：
   ```bash
   cd checkpoints
   ```

   **国内用户（推荐）：**
   ```bash
   pip install modelscope
   modelscope download --model IndexTeam/IndexTTS-2 --local_dir .
   ```

   **国外用户：**
   ```bash
   pip install huggingface_hub
   # 使用镜像下载（可选但推荐）
   $env:HF_ENDPOINT="https://hf-mirror.com"; hf download IndexTeam/IndexTTS-2 --local-dir=.
   # 或直接从Hugging Face下载
   hf download IndexTeam/IndexTTS-2 --local-dir=.
   ```

3. **特别注意：** 如果使用模型下载工具下载的模型文件不完整（如缺少w2v-bert-2.0模型权重文件），请确保下载完整的模型文件。可能需要单独下载facebook/w2v-bert-2.0模型：
   ```bash
   # 使用HuggingFace Hub下载
   hf download facebook/w2v-bert-2.0 --local-dir ./hf_cache/models--facebook--w2v-bert-2.0/snapshots/{snapshot_id}
   # 或使用镜像
   $env:HF_ENDPOINT="https://hf-mirror.com"; hf download facebook/w2v-bert-2.0 --local-dir ./hf_cache/models--facebook--w2v-bert-2.0/snapshots/{snapshot_id}
   ```

   其中`{snapshot_id}`是Hugging Face缓存中的实际快照ID，例如`da985ba0987f70aaeb84a80f2851cfac8c697a7b`。

## 使用方法

1. 运行声音克隆演示：
   ```bash
   python simple_voice_clone_demo.py
   ```

2. 根据提示输入参考音频路径和要转换的文本

## 常见问题

### 模型文件不完整
如果遇到"无法在本地找到 w2v-bert-2.0 模型"错误，说明模型文件下载不完整。请确保下载了完整的模型文件，特别是w2v-bert-2.0的权重文件。

### 音频质量不佳
如果生成的音频质量不佳或出现噪音，可能是由于模型权重加载不正确或mel谱处理问题。请检查所有模型文件是否完整下载。

### 网络请求错误
如果看到任何网络请求或下载提示，说明系统未正确使用本地模型。请确保所有模型文件已下载到本地并设置为离线模式。

## 性能优化

- 使用GPU可显著加速语音生成过程
- 调整diffusion steps参数可在质量和速度之间取得平衡
- 使用FP16可减少内存使用并提高速度（如果GPU支持）

## 故障排除

1. **找不到indextts模块**：确保已克隆IndexTTS代码仓库到`git/index-tts`目录
2. **缺少模型文件**：确保所有必需的模型文件都已下载到checkpoints目录
3. **网络请求错误**：确保系统设置为离线模式，所有模型从本地加载
4. **生成噪音**：检查模型文件完整性，特别是w2v-bert-2.0和BigVGAN相关文件

## 注意事项

- 本项目使用本地模型，所有数据处理均在本地进行，保护用户隐私
- 首次运行可能需要较长时间初始化模型
- 声音克隆效果与参考音频质量密切相关，请使用清晰、噪音少的参考音频
- 确保模型文件完整性，特别是w2v-bert-2.0模型，否则可能导致初始化失败