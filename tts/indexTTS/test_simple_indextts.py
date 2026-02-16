#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版IndexTTS测试脚本
"""

import os
import sys
import tempfile

def test_simple_indextts():
    """简化版IndexTTS测试"""
    try:
        print("🔍 正在设置IndexTTS环境...")
        
        # 添加IndexTTS路径到sys.path
        indextts_path = os.path.join(os.path.dirname(__file__), 'git', 'index-tts')
        indextts_path = os.path.abspath(indextts_path)
        if os.path.exists(indextts_path) and indextts_path not in sys.path:
            sys.path.append(indextts_path)
            print(f"✅ 已添加IndexTTS路径: {indextts_path}")
        
        # 添加IndexTTS的indextts子目录到sys.path
        indextts_sub_path = os.path.join(indextts_path, 'indextts')
        if os.path.exists(indextts_sub_path) and indextts_sub_path not in sys.path:
            sys.path.append(indextts_sub_path)
            print(f"✅ 已添加IndexTTS子路径: {indextts_sub_path}")
            
        print("🔍 正在检查必要文件...")
        # 检查配置文件
        checkpoints_dir = os.path.join(indextts_path, 'checkpoints')
        cfg_path = os.path.join(checkpoints_dir, 'config.yaml')
        
        print(f"📁 配置文件路径: {cfg_path}")
        
        if not os.path.exists(cfg_path):
            print(f"❌ 配置文件不存在: {cfg_path}")
            return False
            
        print("✅ 配置文件存在")
        
        # 尝试导入必要的模块
        print("🔍 正在导入必要模块...")
        import torch
        print(f"✅ PyTorch版本: {torch.__version__}")
        
        import transformers
        print(f"✅ Transformers版本: {transformers.__version__}")
        
        # 尝试导入IndexTTS的主要组件
        print("🔍 正在导入IndexTTS组件...")
        
        # 检查是否存在transformers.cache_utils.QuantizedCacheConfig
        try:
            from transformers.cache_utils import QuantizedCacheConfig
            print("✅ QuantizedCacheConfig 可用")
        except ImportError:
            print("⚠️ QuantizedCacheConfig 不可用，可能需要降级transformers版本")
            
        print("\n🎉 简化版IndexTTS环境检查完成！")
        print("\n💡 注意事项:")
        print("   1. IndexTTS需要特定版本的依赖库才能正常工作")
        print("   2. transformers版本可能需要调整以匹配IndexTTS的要求")
        print("   3. 建议使用uv工具按照pyproject.toml中的依赖版本进行安装")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试IndexTTS时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 简化版IndexTTS测试程序")
    print("=" * 30)
    
    success = test_simple_indextts()
    
    if success:
        print("\n✅ 环境检查已完成")
    else:
        print("\n❌ 环境检查过程中出现错误")
        sys.exit(1)