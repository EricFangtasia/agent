# patch_datasets.py
import sys
import datasets

# 尝试修复LargeList导入
try:
    # 尝试从不同位置导入
    from datasets.features import LargeList
    print("✅ LargeList从datasets.features导入成功")
except ImportError:
    try:
        # 尝试其他可能的位置
        from datasets.arrow_writer import LargeList
        print("✅ LargeList从datasets.arrow_writer导入成功")
    except ImportError:
        try:
            # 尝试创建虚拟的LargeList类
            from datasets.features import Sequence
            
            class LargeList(Sequence):
                """LargeList的简化实现"""
                pass
            
            # 将其注入到datasets模块
            datasets.LargeList = LargeList
            datasets.features.LargeList = LargeList
            
            print("✅ 创建了LargeList的虚拟实现")
        except Exception as e:
            print(f"❌ 无法修复LargeList: {e}")
            sys.exit(1)

# 测试modelscope能否工作
print("\n🔍 测试modelscope...")
try:
    import modelscope
    print(f"✅ modelscope版本: {modelscope.__version__}")
    
    # 现在应该可以正常导入了
    from modelscope.pipelines import pipeline
    from modelscope.utils.constant import Tasks
    
    print("✅ modelscope关键组件导入成功")
    
except ImportError as e:
    print(f"❌ modelscope导入失败: {e}")
    import traceback
    traceback.print_exc()