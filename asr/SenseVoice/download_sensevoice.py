# download_sensevoice.py
import os
import sys
import traceback

print("=" * 60)
print("SenseVoice模型下载工具")
print(f"Python路径: {sys.executable}")
print(f"Python版本: {sys.version}")
print("=" * 60)

# 设置国内镜像缓存
os.environ['MODELSCOPE_CACHE'] = './model_cache'

try:
    # 尝试导入modelscope
    from modelscope import snapshot_download
    
    print("✅ Modelscope导入成功")
    
    # 下载模型
    print("\n🔍 开始下载 SenseVoiceSmall 模型...")
    print("📦 模型ID: iic/SenseVoiceSmall")
    print("💾 缓存目录: ./model_cache")
    print("-" * 50)
    
    model_dir = snapshot_download(
        'iic/SenseVoiceSmall',
        cache_dir='./models',
        revision='v1.0.0'
    )
    
    print("🎉 下载成功！")
    print(f"📁 模型路径: {model_dir}")
    
    # 显示文件
    import os
    files = os.listdir(model_dir)
    print(f"📄 文件数量: {len(files)}")
    
    print("\n📋 主要模型文件:")
    for file in sorted(files):
        if file.endswith(('.bin', '.pt', '.pth', '.json', '.txt', '.yaml', '.onnx')):
            file_path = os.path.join(model_dir, file)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  - {file:<30} ({size_mb:.1f} MB)")
    
except ImportError as e:
    print("❌ Modelscope未安装或导入失败")
    print(f"错误详情: {e}")
    print("\n💡 安装命令:")
    print(f'{sys.executable} -m pip install modelscope -i https://mirrors.aliyun.com/pypi/simple/')
    
except Exception as e:
    print(f"❌ 下载过程中出错: {e}")
    print("\n🔧 堆栈跟踪:")
    traceback.print_exc()

print("=" * 60)