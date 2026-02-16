#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IndexTTS引擎策略实现
"""

import os
import tempfile
import sys
from ..local_tts import TTSEngineBase


class IndexTTSStrategy(TTSEngineBase):
    """IndexTTS引擎策略实现"""
    
    def __init__(self, reference_audio_path=None):
        """初始化IndexTTS引擎，支持参考音频路径"""
        super().__init__()
        self.reference_audio_path = reference_audio_path
    
    def initialize(self):
        """初始化IndexTTS引擎"""
        try:
            # 添加IndexTTS路径到sys.path
            # 修复路径：从当前文件向上三级到项目根目录，然后进入git/index-tts
            current_dir = os.path.dirname(__file__)  # agent/tts/strategies/
            parent_dir = os.path.dirname(current_dir)  # agent/tts/
            grandparent_dir = os.path.dirname(parent_dir)  # agent/
            project_root = os.path.dirname(grandparent_dir)  # 项目根目录 (c:\project\py\)
            indextts_path = os.path.join(project_root, 'git', 'index-tts')
            indextts_path = os.path.abspath(indextts_path)
            print(f"🔍 检查IndexTTS路径: {indextts_path}")
            
            # 验证路径是否存在
            if not os.path.exists(indextts_path):
                print(f"❌ IndexTTS路径不存在: {indextts_path}")
                return False
            
            # 验证indextts子目录是否存在
            indextts_subdir = os.path.join(indextts_path, 'indextts')
            if not os.path.exists(indextts_subdir):
                print(f"❌ indextts子目录不存在: {indextts_subdir}")
                return False
            
            # 验证infer_v2.py是否存在
            infer_v2_path = os.path.join(indextts_subdir, 'infer_v2.py')
            if not os.path.exists(infer_v2_path):
                print(f"❌ infer_v2.py文件不存在: {infer_v2_path}")
                return False
            
            # 将包含indextts包的目录添加到sys.path
            if indextts_path not in sys.path:
                sys.path.insert(0, indextts_path)
                print(f"✅ 已将 {indextts_path} 添加到Python路径")
            else:
                print(f"ℹ️  {indextts_path} 已在Python路径中")
            
            # 验证模块是否可以导入
            try:
                import indextts
                print(f"✅ indextts模块可导入: {indextts.__file__}")
            except ImportError as e:
                print(f"❌ 无法导入indextts模块: {e}")
                return False
            
            # 导入IndexTTS2
            from indextts.infer_v2 import IndexTTS2
            print("✅ 成功导入IndexTTS2")
            
            # 构建默认的模型和配置路径（可根据实际部署调整）
            # 与indextts_path一样，使用项目根目录路径
            current_dir = os.path.dirname(__file__)  # agent/tts/strategies/
            parent_dir = os.path.dirname(current_dir)  # agent/tts/
            grandparent_dir = os.path.dirname(parent_dir)  # agent/
            project_root = os.path.dirname(grandparent_dir)  # 项目根目录 (c:\project\py\)
            checkpoints_dir = os.path.join(project_root, 'git', 'index-tts', 'checkpoints')
            checkpoints_dir = os.path.abspath(checkpoints_dir)
            cfg_path = os.path.join(checkpoints_dir, 'config.yaml')
            model_dir = checkpoints_dir
            
            if not os.path.exists(checkpoints_dir):
                print(f"⚠️  IndexTTS 检查点目录不存在: {checkpoints_dir}")
                print("💡 请确保已克隆index-tts仓库到 git/index-tts 目录")
                return False
                
            if not os.path.exists(cfg_path):
                print(f"⚠️  IndexTTS 配置文件未找到: {cfg_path}")
                print("💡 请确保检查点目录包含config.yaml文件")
                return False
            
            # 设置环境变量以使用本地缓存
            os.environ['HF_HUB_CACHE'] = os.path.join(checkpoints_dir, 'hf_cache')
            os.environ['TRANSFORMERS_OFFLINE'] = '1'  # 确保transformers库不尝试连接网络
            
            # 初始化 IndexTTS2 引擎
            self.engine = IndexTTS2(cfg_path=cfg_path, model_dir=model_dir)
            print("✅ IndexTTS引擎初始化成功！")
            return True
        except Exception as e:
            print(f"❌ 初始化 IndexTTS 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def speak_with_voice_clone(self, text, reference_audio_path):
        """使用IndexTTS进行声音克隆并播放文本"""
        try:
            # 检查参考音频是否存在
            if not os.path.exists(reference_audio_path):
                print(f"❌ 参考音频文件不存在: {reference_audio_path}")
                return None
                
            # IndexTTS处理
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                filename = tmp_file.name
            try:
                # 调用 IndexTTS2 的 infer 方法生成语音，使用声音克隆
                self.engine.infer(
                    spk_audio_prompt=reference_audio_path,  # 参考音频路径，用于声音克隆
                    text=text,
                    output_path=filename,
                    sdp_ratio=0.2,
                    noise_scale=0.6,
                    noise_scale_w=0.8,
                    length_scale=1.0
                )
                # 返回文件路径，由主类处理播放
                return filename
            except Exception as e:
                print(f"❌ IndexTTS语音合成失败: {e}")
                if os.path.exists(filename):
                    os.unlink(filename)
                return None
        except Exception as e:
            print(f"❌ IndexTTS播放处理失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def speak(self, text):
        """使用IndexTTS播放文本（如果设置了参考音频则使用声音克隆，否则使用默认声音）"""
        try:
            # 如果有参考音频，则使用声音克隆
            if self.reference_audio_path and os.path.exists(self.reference_audio_path):
                return self.speak_with_voice_clone(text, self.reference_audio_path)
            else:
                # 如果没有参考音频，则使用默认实现（固定说话人ID）
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    filename = tmp_file.name
                try:
                    # 调用 IndexTTS2 的 infer 方法生成语音
                    self.engine.infer(
                        text=text,
                        output_path=filename,
                        sdp_ratio=0.2,
                        noise_scale=0.6,
                        noise_scale_w=0.8,
                        length_scale=1.0,
                        speaker_id=0
                    )
                    # 返回文件路径，由主类处理播放
                    return filename
                except Exception as e:
                    print(f"❌ IndexTTS语音合成失败: {e}")
                    if os.path.exists(filename):
                        os.unlink(filename)
                    return None
        except Exception as e:
            print(f"❌ IndexTTS播放处理失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_to_file(self, text, filename, reference_audio_path=None):
        """使用IndexTTS将文本保存到音频文件，支持声音克隆"""
        try:
            # 如果指定了参考音频路径，则使用声音克隆
            if reference_audio_path and os.path.exists(reference_audio_path):
                # 检查参考音频是否存在
                if not os.path.exists(reference_audio_path):
                    print(f"❌ 参考音频文件不存在: {reference_audio_path}")
                    return None
                
                # 使用声音克隆进行语音合成
                self.engine.infer(
                    spk_audio_prompt=reference_audio_path,  # 参考音频路径，用于声音克隆
                    text=text,
                    output_path=filename,
                    sdp_ratio=0.2,
                    noise_scale=0.6,
                    noise_scale_w=0.8,
                    length_scale=1.0
                )
            else:
                # 如果没有参考音频，则使用默认方式
                self.engine.infer(
                    text=text,
                    output_path=filename,
                    sdp_ratio=0.2,
                    noise_scale=0.6,
                    noise_scale_w=0.8,
                    length_scale=1.0,
                    speaker_id=0
                )
            return filename
        except Exception as e:
            print(f"❌ IndexTTS保存文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None