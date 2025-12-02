import os
import json
import math
from PIL import Image

# ================= 配置区域 =================
# 输入文件夹：把你即梦生成的图片都扔到这个文件夹里
INPUT_FOLDER = 'raw_images' 

# 输出文件夹：生成的雪碧图和JSON会放在这里
OUTPUT_FOLDER = 'assets'

# 目标尺寸：你想缩放到多大？(比如 64x64)
TARGET_SIZE = 64

# 间距：每个图标之间的空隙，防止出血 (像素)
PADDING = 2

# 是否尝试去除白色背景？(True=开启, False=关闭)
# 注意：这只是简单的去除纯白/接近白色的背景。如果是复杂背景建议用 rembg 库。
REMOVE_WHITE_BG = True 
# ===========================================

def make_transparent(img):
    """
    简单的去背逻辑：把接近白色的像素变透明
    """
    img = img.convert("RGBA")
    datas = img.getdata()
    
    newData = []
    for item in datas:
        # 如果像素点 R,G,B 都大于 240 (接近白色)
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            # 把它变成完全透明 (Alpha = 0)
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    
    img.putdata(newData)
    return img

def main():
    # 1. 确保文件夹存在
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"❌ 错误：找不到输入文件夹 '{INPUT_FOLDER}'，已自动创建。请把图片放进去再运行！")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # 2. 获取所有图片文件 (支持 jpg, jpeg, png)
    image_files = [f for f in os.listdir(INPUT_FOLDER) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print("❌ 文件夹里没有图片！")
        return

    print(f"🚀 开始处理 {len(image_files)} 张图片...")

    # 3. 计算大图尺寸
    count = len(image_files)
    # 计算列数 (开根号，尽量拼成正方形)
    cols = math.ceil(math.sqrt(count))
    # 计算行数
    rows = math.ceil(count / cols)

    # 大图的总宽高
    sheet_width = cols * (TARGET_SIZE + PADDING)
    sheet_height = rows * (TARGET_SIZE + PADDING)

    # 创建画布 (RGBA 模式，背景全透明)
    sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    # 坐标数据字典
    atlas_data = {}

    # 4. 循环处理每一张图
    for index, filename in enumerate(image_files):
        img_path = os.path.join(INPUT_FOLDER, filename)
        
        try:
            with Image.open(img_path) as img:
                # A. 简单的去白底 (如果开启)
                if REMOVE_WHITE_BG:
                    img = make_transparent(img)
                else:
                    img = img.convert("RGBA")

                # B. 核心步骤：缩放 (使用 NEAREST 算法保持像素锐利)
                img_resized = img.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.NEAREST)
                
                # C. 计算粘贴位置
                col = index % cols
                row = index // cols
                x = col * (TARGET_SIZE + PADDING)
                y = row * (TARGET_SIZE + PADDING)
                
                # D. 粘贴到大图上
                sprite_sheet.paste(img_resized, (x, y))
                
                # E. 记录坐标信息 (去掉后缀名作为 ID)
                item_name = os.path.splitext(filename)[0]
                atlas_data[item_name] = {
                    "x": x,
                    "y": y,
                    "w": TARGET_SIZE,
                    "h": TARGET_SIZE
                }
                
                print(f"✅ 已处理: {filename} -> {item_name}")
                
        except Exception as e:
            print(f"⚠️ 处理 {filename} 时出错: {e}")

    # 5. 保存结果
    output_image_path = os.path.join(OUTPUT_FOLDER, 'sprite_sheet.png')
    output_json_path = os.path.join(OUTPUT_FOLDER, 'sprite_map.json')
    
    sprite_sheet.save(output_image_path)
    
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(atlas_data, f, indent=4)

    print("-" * 30)
    print(f"🎉 大功告成！")
    print(f"🖼️  图片已保存: {output_image_path}")
    print(f"📄 数据已保存: {output_json_path}")

if __name__ == "__main__":
    main()