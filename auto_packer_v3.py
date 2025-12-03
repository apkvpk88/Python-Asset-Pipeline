import os
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

# 🔥 边缘阈值：范围 0-255
# 数值越大，切得越狠（去白边效果越好），但可能会误伤物体边缘
# 推荐：200 左右
ALPHA_THRESHOLD = 10
# ===========================================

# 🔴 新增：清理半透明边缘的函数
def clean_edges(img, threshold):
    """
    将所有半透明像素强制变为全透明，消除白边
    """
    # 获取图片的所有像素数据
    img = img.convert("RGBA")
    datas = img.getdata()
    
    newData = []
    for item in datas:
        # item[3] 是透明度 (Alpha 通道)
        # 如果透明度低于阈值，直接变成完全透明 (0)
        # 否则变成完全不透明 (255)
        if item[3] < threshold:
            newData.append((255, 255, 255, 0))  # 变透明
        else:
            # 这里的 item[:3] 是保留原来的 RGB 颜色，只把 Alpha 设为 255
            newData.append(item[:3] + (255,))
    
    img.putdata(newData)
    return img

def main():
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

    print(f"🚀 启动 AI 强力去边模式，处理 {len(image_files)} 张图片...")

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

            # 1. AI 智能去背
            output_data = remove(img_data)
            img = Image.open(io.BytesIO(output_data))

            # 2. 🔥 核心步骤：缩放前先清理边缘
            # 在图片还是大图的时候清理，效果最好
            img = clean_edges(img, ALPHA_THRESHOLD)

            # 3. 像素风缩放 (Nearest Neighbor)
            img_resized = img.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.NEAREST)
            
            # 4. 拼贴
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
            
            print(f"✨ 已净化: {filename}")
                
        except Exception as e:
            print(f"⚠️ 处理 {filename} 时出错: {e}")

    # 保存
    output_image_path = os.path.join(OUTPUT_FOLDER, 'sprite_sheet_v3.png')
    output_json_path = os.path.join(OUTPUT_FOLDER, 'sprite_map_v3.json')
    
    sprite_sheet.save(output_image_path)
    
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(atlas_data, f, indent=4)

    print("-" * 30)
    print(f"🎉 处理完成！白边已被消灭！")
    print(f"🖼️  新文件: {output_image_path}")

if __name__ == "__main__":
    main()