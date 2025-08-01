import base64
import os
def encode_image_to_base64(image_path):
    """
    将本地图片文件转换为base64编码
    
    Args:
        image_path (str): 图片文件路径
        
    Returns:
        str: base64编码的图片数据
    """
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
        # 获取文件扩展名
        _, ext = os.path.splitext(image_path)
        ext = ext.lower().replace('.', '')
        
        # 确定MIME类型
        mime_types = {
            'png': 'png',
            'jpg': 'jpeg',
            'jpeg': 'jpeg',
            'gif': 'gif',
            'bmp': 'bmp',
            'webp': 'webp'
        }
        
        image_format = mime_types.get(ext, 'png')  # 默认为png
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/{image_format};base64,{encoded_image}"
    except Exception as e:
        print(f"图片编码错误: {e}")
        return None