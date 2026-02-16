# IndexTTS-2 声音克隆解决方案

## 问题说明

你遇到了IndexTTS-2模型文件不完整的问题，缺少 `bigvgan.pth` 和 `campplus.onnx` 两个文件。

## 实际情况

经过仔细研究，发现这两个文件**不是IndexTTS-2模型本身的一部分**，而是其依赖模型：

1. `bigvgan.pth` - 实际上来自 `nvidia/bigvgan_v2_22khz_80band_256x` 模型，原始文件名是 `bigvgan_generator.pt`
2. `campplus.onnx` - 来自 `funasr/campplus` 模型，原始文件名是 `campplus_cn_common.bin`

## 解决方案

### 1. 使用Hugging Face镜像下载BigVGAN模型（推荐）

```powershell
# 在PowerShell中设置环境变量（仅当前会话有效）
$env:HF_ENDPOINT="https://hf-mirror.com"

# 下载BigVGAN模型 - 注意文件名是 bigvgan_generator.pt
hf download nvidia/bigvgan_v2_22khz_80band_256x bigvgan_generator.pt --local-dir ./temp_bigvgan

# 也可能需要config.json文件
hf download nvidia/bigvgan_v2_22khz_80band_256x config.json --local-dir ./temp_bigvgan
```

### 2. 下载说话人识别模型

```powershell
# 设置环境变量并下载
$env:HF_ENDPOINT="https://hf-mirror.com"

# 下载funasr/campplus模型
hf download funasr/campplus campplus_cn_common.bin --local-dir ./temp_campplus
```

### 3. 确认文件名并复制到正确位置

```powershell
# 检查下载的文件
Get-ChildItem temp_bigvgan
Get-ChildItem temp_campplus

# 将BigVGAN模型重命名并复制
Copy-Item temp_bigvgan\bigvgan_generator.pt git\index-tts\checkpoints\bigvgan.pth

# 将campplus模型重命名
Copy-Item temp_campplus\campplus_cn_common.bin git\index-tts\checkpoints\campplus.onnx
```

### 4. 验证模型完整性

完成后，你的 `git/index-tts/checkpoints/` 目录应该包含以下文件：

- ✅ config.yaml
- ✅ gpt.pth
- ✅ bigvgan.pth (从 bigvgan_generator.pt 重命名)
- ✅ s2mel.pth
- ✅ bpe.model
- ✅ campplus.onnx (从 campplus_cn_common.bin 重命名)

## 替代方案

如果上述方法仍无法下载模型，你可以尝试以下方法：

### 从Hugging Face Hub直接下载文件
```powershell
# 使用浏览器直接下载
# BigVGAN: https://huggingface.co/nvidia/bigvgan_v2_22khz_80band_256x/resolve/main/bigvgan_generator.pt
# 或镜像: https://hf-mirror.com/nvidia/bigvgan_v2_22khz_80band_256x/resolve/main/bigvgan_generator.pt

# CampPlus: https://huggingface.co/funasr/campplus/resolve/main/campplus_cn_common.bin
# 或镜像: https://hf-mirror.com/funasr/campplus/resolve/main/campplus_cn_common.bin
```

### 手动下载并放置到正确位置
1. 使用浏览器下载模型文件
2. 将 `bigvgan_generator.pt` 重命名为 `bigvgan.pth`
3. 将 `campplus_cn_common.bin` 重命名为 `campplus.onnx`
4. 将文件复制到 `git/index-tts/checkpoints/` 目录

## 运行声音克隆

当所有模型文件都存在后，你可以运行：

```powershell
python simple_voice_clone_demo.py
```

## 注意事项

1. `bigvgan_generator.pt` 需要重命名为 `bigvgan.pth` 才能被IndexTTS-2正确加载
2. `campplus_cn_common.bin` 需要重命名为 `campplus.onnx`
3. 这些是IndexTTS-2的依赖模型，需要单独下载
4. BigVGAN是声码器模型，用于将声谱图转换为波形音频
5. CampPlus是说话人识别模型，用于声音克隆功能

## 参考资料

- IndexTTS-2模型: https://www.modelscope.cn/models/IndexTeam/IndexTTS-2
- BigVGAN模型: https://huggingface.co/nvidia/bigvgan_v2_22khz_80band_256x 或 https://hf-mirror.com/nvidia/bigvgan_v2_22khz_80band_256x
- CampPlus模型: https://huggingface.co/funasr/campplus 或 https://hf-mirror.com/funasr/campplus

现在你有了准确的解决方案，可以获取缺失的模型文件了。