# move_model.py
import os
import shutil

# 源路径（下载的位置）
src_path = r"C:\Users\86138\.cache\modelscope\hub\models\iic\SenseVoiceSmall"

# 目标路径（项目目录）
dst_path = r"C:\project\py\agent\SenseVoice\models\SenseVoiceSmall"

# 复制模型文件
if os.path.exists(src_path):
    os.makedirs(dst_path, exist_ok=True)
    
    for item in os.listdir(src_path):
        src_item = os.path.join(src_path, item)
        dst_item = os.path.join(dst_path, item)
        
        if os.path.isdir(src_item):
            shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
        else:
            shutil.copy2(src_item, dst_item)
    
    print(f"✅ 模型已复制到: {dst_path}")
else:
    print("❌ 源路径不存在")