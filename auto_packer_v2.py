import os
# ================= 🔥 救命配置：把模型存到 D 盘 🔥 =================
# 在导入 rembg 之前，强制指定模型下载路径到当前脚本所在的 D 盘文件夹
# 这样就不会占用你 C 盘那宝贵的 1GB 空间了
os.environ['U2NET_HOME'] = os.path.join(os.getcwd(), 'u2net_models')
# ===============================================================

import json
import math
import io
from PIL import Image
from rembg import remove 

# ================= 配置区域 =================
INPUT_FOLDER = 'raw_images' 
OUTPUT_FOLDER = 'assets'
TARGET_SIZE = 64
PADDING = 2
# ===========================================

def main():
    # 确保模型下载目录存在
    model_dir = os.environ['U2NET_HOME']
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        print(f"📦 AI 模型将下载到: {model_dir} (不占C盘空间)")

    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"❌ 错误：找不到输入文件夹 '{INPUT_FOLDER}'")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    image_files = [f for f in os.listdir(INPUT_FOLDER) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print("❌ 文件夹里没有图片！")
        return

    print(f"🚀 启动 AI 引擎，开始处理 {len(image_files)} 张图片...")
    
    # 计算大图尺寸
    count = len(image_files)
    cols = math.ceil(math.sqrt(count))
    rows = math.ceil(count / cols)
    sheet_width = cols * (TARGET_SIZE + PADDING)
    sheet_height = rows * (TARGET_SIZE + PADDING)

    sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    atlas_data = {}

    for index, filename in enumerate(image_files):
        img_path = os.path.join(INPUT_FOLDER, filename)
        
        try:
            with open(img_path, 'rb') as f:
                img_data = f.read()

            # 🔥 AI 智能去背
            output_data = remove(img_data)
            img = Image.open(io.BytesIO(output_data))

            # 像素风缩放
            img_resized = img.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.NEAREST)
            
            # 拼贴
            col = index % cols
            row = index // cols
            x = col * (TARGET_SIZE + PADDING)
            y = row * (TARGET_SIZE + PADDING)
            
            sprite_sheet.paste(img_resized, (x, y))
            
            item_name = os.path.splitext(filename)[0]
            atlas_data[item_name] = {
                "x": x,
                "y": y,
                "w": TARGET_SIZE,
                "h": TARGET_SIZE
            }
            
            print(f"✨ AI 已处理: {filename}")
                
        except Exception as e:
            print(f"⚠️ 处理 {filename} 时出错: {e}")

    # 保存
    output_image_path = os.path.join(OUTPUT_FOLDER, 'sprite_sheet_v2.png')
    output_json_path = os.path.join(OUTPUT_FOLDER, 'sprite_map_v2.json')
    
    sprite_sheet.save(output_image_path)
    
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(atlas_data, f, indent=4)

    print("-" * 30)
    print(f"🎉 完美处理完成！")
    print(f"🖼️  图片: {output_image_path}")

if __name__ == "__main__":
    main()