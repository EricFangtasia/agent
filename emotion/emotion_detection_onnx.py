import os
import numpy as np
import cv2
from PIL import Image
import onnxruntime as ort
import base64
from io import BytesIO
import logging  # 添加logging模块
import re  # 添加re模块以支持正则表达式操作

# 情绪标签 - 与原模型保持一致
emotion_labels = {
    0: "sad",        # 悲伤
    1: "disgust",    # 厌恶
    2: "angry",      # 生气
    3: "neutral",    # 中性
    4: "fear",       # 恐惧
    5: "surprise",   # 惊讶
    6: "happy"       # 高兴
}

# 中文情绪标签
emotion_labels_cn = {
    0: "悲伤",        # 悲伤
    1: "厌恶",        # 厌恶
    2: "生气",        # 生气
    3: "中性",        # 中性
    4: "恐惧",       # 恐惧
    5: "惊讶",   # 惊讶
    6: "高兴"       # 高兴
}

class EmotionDetectorONNX:
    """使用ONNX模型的情绪检测器"""
    
    def __init__(self, onnx_model_path, processor_config_path=None):
        """
        初始化情绪检测器
        Args:
            onnx_model_path: ONNX模型文件路径
            processor_config_path: 处理器配置文件路径（可选）
        """
        print("🔍 正在加载ONNX模型...")
        
        # 创建ONNX Runtime会话
        self.session = ort.InferenceSession(onnx_model_path)
        
        # 获取输入输出名称
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        
        # 从配置文件加载预处理参数
        if processor_config_path and os.path.exists(processor_config_path):
            import json
            with open(processor_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.image_mean = np.array(config.get("image_mean", [0.5, 0.5, 0.5]))
            self.image_std = np.array(config.get("image_std", [0.5, 0.5, 0.5]))
            self.do_normalize = config.get("do_normalize", True)
            self.do_rescale = config.get("do_rescale", True)
            self.rescale_factor = config.get("rescale_factor", 1/255.0)
        else:
            # 使用从模型配置文件中提取的默认参数
            self.image_mean = np.array([0.5, 0.5, 0.5])
            self.image_std = np.array([0.5, 0.5, 0.5])
            self.do_normalize = True
            self.do_rescale = True
            self.rescale_factor = 0.00392156862745098  # 1/255
            
        # 初始化人脸检测器
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        print("✅ ONNX模型加载成功!")

    def detect_face_from_base64(self, image_base64):
        """
        从base64编码的图像数据检测是否存在人脸
        Args:
            image_base64: base64编码的图像数据
        Returns:
            bool: 是否检测到人脸
        """
        try:
            # 将base64图片数据转换为图像
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            
            # 转换为numpy数组并转换为BGR格式
            image_np = np.array(image)
            if len(image_np.shape) == 3:
                # RGB to BGR
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            # 转换为灰度图进行人脸检测
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
            
            # 检测人脸
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # 返回是否检测到人脸
            return len(faces) > 0
            
        except Exception as e:
            print(f"❌ 人脸检测失败: {e}")
            return False

    def softmax(self, x):
        """使用numpy实现softmax函数"""
        e_x = np.exp(x - np.max(x))  # 为了数值稳定性，减去最大值
        return e_x / e_x.sum(axis=0)

    def preprocess_image(self, image):
        """
        预处理图像以匹配ViT模型的输入要求
        根据模型配置文件中的参数进行精确预处理
        """
        # 调整图像大小为224x224
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, bytes):
            # 如果输入是字节流，转换为PIL图像
            image = Image.open(BytesIO(image)).convert('RGB')
        elif hasattr(image, 'read') and callable(getattr(image, 'read')):
            # 如果输入是文件对象，转换为PIL图像
            image = Image.open(image).convert('RGB')
        
        # 调整大小
        image = image.resize((224, 224))
        
        # 转换为numpy数组
        image_array = np.array(image).astype(np.float32)
        
        # 转换为CHW格式（通道，高度，宽度）在归一化之前
        image_array = np.transpose(image_array, (2, 0, 1))
        
        # 应用重缩放因子（如果需要）
        if self.do_rescale:
            image_array = image_array * self.rescale_factor
            
        # 归一化（如果需要）
        if self.do_normalize:
            # 调整均值和标准差的形状以适应图像数组 (3, 224, 224)
            mean = self.image_mean.reshape(-1, 1, 1)
            std = self.image_std.reshape(-1, 1, 1)
            image_array = (image_array - mean) / std
        
        # 添加批次维度并确保数据类型为float32
        image_array = np.expand_dims(image_array, axis=0).astype(np.float32)
        
        return image_array

    def predict_emotion_from_base64(self, image_base64):
        """
        从base64编码的图像数据预测情绪
        Args:
            image_base64: base64编码的图像数据
        Returns:
            emotion: 英文情绪标签
            emotion_cn: 中文情绪标签
            confidence: 置信度
            emotion_details: 各情绪类别概率
        """
        try:
            # 将base64图片数据转换为图像
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            
            # 预处理图像
            processed_image = self.preprocess_image(image)
            
            # 运行推理
            result = self.session.run([self.output_name], {self.input_name: processed_image})
            
            # 处理输出
            logits = result[0][0]
            # 使用自定义softmax函数确保数值稳定性
            probabilities = self.softmax(logits)
            
            # 获取预测结果
            predicted_class = int(np.argmax(probabilities))
            confidence = float(probabilities[predicted_class])
            emotion = emotion_labels[predicted_class]
            emotion_cn = emotion_labels_cn[predicted_class]
            
            # 创建详细结果字典
            emotion_details = {}
            for i, prob in enumerate(probabilities):
                emotion_details[emotion_labels_cn[i]] = float(prob)
            
            return emotion, emotion_cn, confidence, emotion_details
            
        except Exception as e:
            print(f"❌ 预测失败: {e}")
            return None, None, 0, None

    def get_emotion_analysis_text(self, image_base64):
        """
        获取情绪分析结果的文本描述
        Args:
            image_base64: base64编码的图像数据
        Returns:
            emotion_text: 情绪分析结果文本
        """
        emotion, emotion_cn, confidence, emotion_details = self.predict_emotion_from_base64(image_base64)
        
        if emotion is not None:
            # 构建详细的情绪分析结果
            # result_text = f"情绪分析结果："
            # result_text += f"主要情绪：{emotion_cn}（置信度：{confidence:.3f}）\n"
            result_text = f"{emotion_cn}（置信度：{confidence:.3f}）"
            # result_text += "各情绪类别概率：\n"
            
            # 按概率从高到低排序显示
            # sorted_emotions = sorted(emotion_details.items(), key=lambda x: x[1], reverse=True)
            # for emotion_name, prob in sorted_emotions:
                # result_text += f"  {emotion_name}：{prob:.4f} ({prob*100:.1f}%)\n"
                # result_text += f"  {emotion_name}：{prob:.4f} ({prob*100:.1f}%)\n"

                
            return result_text
        else:
            return "情绪检测失败"

    def predict_emotion(self, image):
        """预测图像的情绪"""
        try:
            # 预处理图像
            processed_image = self.preprocess_image(image)
            
            # 运行推理
            result = self.session.run([self.output_name], {self.input_name: processed_image})
            
            # 处理输出
            logits = result[0][0]
            # 使用自定义softmax函数确保数值稳定性
            probabilities = self.softmax(logits)
            
            # 获取预测结果
            predicted_class = int(np.argmax(probabilities))
            confidence = float(probabilities[predicted_class])
            emotion = emotion_labels[predicted_class]
            
            return emotion, confidence, probabilities
            
        except Exception as e:
            print(f"❌ 预测失败: {e}")
            return None, 0, None

    def estimate_head_pose_influence(self, image):
        """
        估计头部姿态对情绪识别的影响
        返回一个调整系数，用于修正情绪预测结果
        """
        # 这里可以集成一个头部姿态估计模型
        # 目前返回默认值1.0表示无影响
        return 1.0

    def predict_emotion_with_pose_correction(self, image):
        """
        结合头部姿态校正的情绪预测
        """
        emotion, confidence, probabilities = self.predict_emotion(image)
        
        if emotion is not None:
            # 估计姿态影响
            pose_influence = self.estimate_head_pose_influence(image)
            
            # 对特定情绪（如悲伤）进行姿态校正
            if emotion == "sad" and confidence > 0.5:
                # 如果识别为悲伤且置信度较高，但可能是由于低头姿态造成的
                adjusted_confidence = confidence * pose_influence
                return emotion, adjusted_confidence, probabilities
            
        return emotion, confidence, probabilities

    def predict_emotion_from_path(self, image_path):
        """从图像路径预测情绪"""
        try:
            print(f"📷 加载图像: {image_path}")
            
            # 检查文件是否存在
            if not os.path.exists(image_path):
                print(f"❌ 图像文件不存在: {image_path}")
                return None, 0, None
                
            # 预处理和预测
            emotion, confidence, probabilities = self.predict_emotion_with_pose_correction(image_path)
            
            if emotion is not None:
                # 显示详细结果
                print(f"\n🎭 情绪分析结果:")
                print("=" * 50)
                for i, prob in enumerate(probabilities):
                    marker = " 🎯" if i == np.argmax(probabilities) else "   "
                    print(f"{marker} {emotion_labels[i]:8}: {prob:.4f} ({prob*100:.1f}%)")
                print("=" * 50)
                print(f"📊 主要情绪: {emotion}")
                print(f"✅ 置信度: {confidence:.3f} ({confidence*100:.1f}%)")
                
            return emotion, confidence, probabilities
            
        except Exception as e:
            print(f"❌ 预测失败: {e}")
            return None, 0, None

    def real_time_detection(self):
        """实时摄像头情绪检测"""
        print("\n🎥 启动实时情绪检测...")
        print("按 'q' 退出摄像头")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ 无法打开摄像头")
            return
        
        # 加载人脸检测器
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # 用于保存人脸的计数器
        face_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 转换为灰度图进行人脸检测
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in faces:
                # 提取人脸区域
                face_roi = frame[y:y+h, x:x+w]
                
                try:
                    # 转换格式并预测
                    face_pil = Image.fromarray(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))
                    emotion, confidence, _ = self.predict_emotion(face_pil)
                    
                    if emotion is not None:
                        # 根据情绪选择颜色
                        color_map = {
                            "happy": (0, 255, 0),      # 绿色
                            "surprise": (255, 255, 0), # 黄色
                            "neutral": (255, 165, 0),  # 橙色
                            "sad": (0, 0, 255),        # 红色
                            "angry": (0, 0, 255),      # 红色
                            "fear": (128, 0, 128),     # 紫色
                            "disgust": (165, 42, 42)   # 棕色
                        }
                        color = color_map.get(emotion, (0, 255, 0))
                        
                        # 绘制结果
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        label = f"{emotion} ({confidence:.2f})"
                        cv2.putText(frame, label, (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                        
                        # 保存识别到的人脸到 emotion_face 文件夹
                        if not os.path.exists("emotion_face"):
                            os.makedirs("emotion_face")
                            
                        face_filename = f"emotion_face/face_{face_count}_{emotion}.jpg"
                        cv2.imwrite(face_filename, face_roi)
                        face_count += 1
                    
                except Exception as e:
                    print(f"处理人脸时出错: {e}")
            
            # 显示画面
            cv2.imshow('实时情绪识别 - 按 q 退出', frame)
            
            # 按q退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

    def predict_folder_images(self, folder_path, output_file="emotion_results_onnx.txt"):
        """识别文件夹下所有图片的情绪并保存结果到文本文件"""
        if not os.path.exists(folder_path):
            print(f"❌ 文件夹不存在: {folder_path}")
            return
        
        # 支持的图片格式
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')
        
        # 获取文件夹下所有图片文件
        image_files = [f for f in os.listdir(folder_path) 
                       if f.lower().endswith(supported_formats) and 
                       os.path.isfile(os.path.join(folder_path, f))]
        
        if not image_files:
            print(f"❌ 在 {folder_path} 中未找到图片文件")
            return
        
        print(f"📁 找到 {len(image_files)} 张图片")
        
        # 构建输出文件的完整路径
        output_path = os.path.join(folder_path, output_file)
        
        # 打开结果文件准备写入
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"情绪识别结果 (ONNX版本)\n")
            f.write(f"文件夹: {folder_path}\n")
            f.write(f"总共 {len(image_files)} 张图片\n")
            f.write("=" * 50 + "\n\n")
            
            # 处理每张图片
            for i, image_file in enumerate(image_files, 1):
                image_path = os.path.join(folder_path, image_file)
                print(f"\n处理进度: {i}/{len(image_files)} - {image_file}")
                
                try:
                    # 预测情绪
                    emotion, confidence, probabilities = self.predict_emotion_from_path(image_path)
                    
                    if emotion is not None:
                        # 输出到控制台
                        print(f"  📊 情绪: {emotion} (置信度: {confidence:.3f})")
                        
                        # 写入到文件
                        f.write(f"图片 {i}: {image_file}\n")
                        f.write(f"情绪: {emotion}\n")
                        f.write(f"置信度: {confidence:.3f} ({confidence*100:.1f}%)\n")
                        
                        # 写入详细概率
                        f.write("各类别概率:\n")
                        for j, prob in enumerate(probabilities):
                            marker = " >>> " if j == np.argmax(probabilities) else "     "
                            f.write(f"{marker}{emotion_labels[j]:8}: {prob:.4f} ({prob*100:.1f}%)\n")
                        f.write("\n")
                    else:
                        f.write(f"图片 {i}: {image_file}\n")
                        f.write("错误: 无法处理该图片\n\n")
                        
                except Exception as e:
                    error_msg = f"处理图片 {image_file} 时出错: {e}"
                    print(f"❌ {error_msg}")
                    f.write(f"图片 {i}: {image_file}\n")
                    f.write(f"错误: {error_msg}\n\n")
        
        print(f"\n✅ 所有图片处理完成，结果已保存到 {output_path}")

def initialize_emotion_detector():
    """
    初始化情绪检测器
    """
    try:
        # 使用相对于当前文件的绝对路径来定位模型文件
        import os
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_file_dir, "emotion_model.onnx")
        
        if not os.path.exists(model_path):
            print(f"❌ 情绪检测模型文件不存在: {model_path}")
            return None
        
        # 初始化情绪检测器
        processor_config_path = os.path.join(current_file_dir, "train_emotion_model/disgust_fine_tuned_model_1.1/preprocessor_config.json")
        detector = EmotionDetectorONNX(model_path, processor_config_path)
        return detector
    except Exception as e:
        print(f"初始化情绪检测器失败: {e}")
        return None

# 全局情绪检测器实例，实现一次加载多次使用
EMOTION_DETECTOR = initialize_emotion_detector()

def clean_multimodal_text(text):
    """
    清理多模态API返回的文本，移除系统标签和冗余描述
    """
    if not text:
        return text
    
    # 移除所有形如<|.*?|>的标签序列
    cleaned_text = re.sub(r'<\|[\w]+\|>', '', text)
    
    # 移除"情绪识别结果:"等冗余描述
    cleaned_text = re.sub(r'情绪识别结果:\s*', '', cleaned_text)
    
    # 清理多余的空白字符
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


def detect_emotion(image_base64, include_prefix=True):
    """
    使用本地情绪检测模型检测图片中的情绪
    Args:
        image_base64: base64编码的图片数据
        api_key: API密钥
        model: 使用的模型名称
        include_prefix: 是否包含"情绪分析："前缀
    Returns:
        情绪分析结果文本
    """
    if EMOTION_DETECTOR:
        try:
            # 使用本地情绪检测模型
            emotion_result = get_emotion_analysis_text(image_base64)
            
            # 过滤掉不需要的内容
            if emotion_result:
                # 清理情绪识别结果
                filtered_result = clean_multimodal_text(emotion_result)
                # 如果结果为空，返回空字符串
                result = filtered_result if filtered_result else ""
                
                # 根据include_prefix参数决定是否添加前缀
                if include_prefix and result:
                    result = "情绪分析：" + result
                return result
            return ""
        except Exception as e:
            logging.error(f"本地情绪检测出错: {str(e)}")
            return ""
    else:
        # 如果本地情绪检测不可用，返回错误信息
        logging.error("本地情绪检测模块未初始化")
        return ""


def get_emotion_analysis_text(image_base64):
    """
    供外部调用的情绪分析函数
    Args:
        image_base64: base64编码的图像数据
    Returns:
        emotion_text: 情绪分析结果文本
    """
    if EMOTION_DETECTOR is None:
        return "情绪检测器未初始化，请检查模型文件是否存在"
    
    try:
        # 先进行图像分析是否存在人脸
        if not EMOTION_DETECTOR.detect_face_from_base64(image_base64):
            return ""
        return EMOTION_DETECTOR.get_emotion_analysis_text(image_base64)
    except Exception as e:
        print(f"情绪检测出错: {str(e)}")
        return ""

def main():
    print("🎯 ONNX人脸情绪识别系统")
    print("=" * 50)
    
    # 初始化情绪检测器，传入预处理器配置文件路径
    detector = EMOTION_DETECTOR
    
    if detector is None:
        print("❌ 无法初始化情绪检测器")
        return
    
    while True:
        print("\n请选择模式:")
        print("1. 📷 测试单张图片")
        print("2. 🎥 实时摄像头检测")
        print("3. 📁 识别文件夹下所有图片情绪")
        print("4. 🚪 退出")
        
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == '1':
            image_path = input("请输入图片路径: ").strip()
            detector.predict_emotion_from_path(image_path)
        
        elif choice == '2':
            detector.real_time_detection()
        
        elif choice == '3':
            folder_path = input("请输入图片文件夹路径: ").strip()
            output_file = input("请输入结果保存文件名 (默认为 emotion_results_onnx.txt): ").strip()
            if not output_file:
                output_file = "emotion_results_onnx.txt"
            detector.predict_folder_images(folder_path, output_file)
        
        elif choice == '4':
            print("👋 再见!")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()