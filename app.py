"""
拼豆图纸AI生成器 - Perler Bead Pattern Generator
作者：廖佳煜
学号：202535720114
"""

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from PIL import Image
import numpy as np
import io
import base64
import cv2
from collections import Counter

app = Flask(__name__)
CORS(app)

# 拼豆颜色 palette（Perler 官方颜色表 - 精选常用色）
PERLER_COLORS = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'orange': (255, 165, 0),
    'yellow': (255, 255, 0),
    'lime': (0, 255, 0),
    'green': (0, 128, 0),
    'teal': (0, 128, 128),
    'sky_blue': (135, 206, 235),
    'blue': (0, 0, 255),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'brown': (139, 69, 19),
    'beige': (245, 245, 220),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
    'light_gray': (192, 192, 192),
    'peach': (255, 218, 185),
    'salmon': (250, 128, 114),
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
    'navy': (0, 0, 128),
    'maroon': (128, 0, 0),
    'olive': (128, 128, 0),
    'coral': (255, 127, 80),
    'turquoise': (64, 224, 208),
    'lavender': (230, 230, 250),
    'burgundy': (128, 0, 32),
    'mint': (189, 252, 201),
    'rose': (255, 0, 127),
}


def color_distance(c1, c2):
    """计算两个颜色的欧几里得距离"""
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def find_closest_perler_color(rgb):
    """找到最接近的拼豆颜色"""
    min_dist = float('inf')
    closest = 'white'
    for name, perler_rgb in PERLER_COLORS.items():
        dist = color_distance(rgb, perler_rgb)
        if dist < min_dist:
            min_dist = dist
            closest = name
    return closest


def quantize_colors(colors, n_colors=16):
    """K-Means 颜色量化"""
    pixels = np.array(colors)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(
        pixels.astype(np.float32),
        n_colors,
        None,
        criteria,
        10,
        flags
    )
    return palette.astype(int)


def generate_pattern(image_data, bead_width=32, bead_height=32, n_colors=16):
    """生成拼豆图纸"""
    # 读取图片
    img = Image.open(io.BytesIO(image_data))
    
    # 调整尺寸（每个像素变成一个珠子）
    img = img.resize((bead_width, bead_height), Image.Resampling.LANCZOS)
    
    # 转换为RGB
    img = img.convert('RGB')
    pixels = np.array(img)
    
    # 收集所有像素颜色
    all_colors = pixels.reshape(-1, 3).tolist()
    
    # K-Means 量化颜色
    quantized = quantize_colors(all_colors, n_colors)
    color_map = {i: tuple(quantized[i]) for i in range(len(quantized))}
    
    # 为每个像素分配最接近的拼豆颜色
    pattern = []
    color_counts = {}
    
    for y in range(bead_height):
        row = []
        for x in range(bead_width):
            pixel_rgb = tuple(pixels[y, x])
            # 找到量化后的颜色
            distances = [color_distance(pixel_rgb, c) for c in color_map.values()]
            closest_idx = distances.index(min(distances))
            original_rgb = color_map[closest_idx]
            # 再匹配到实际拼豆颜色
            perler_color = find_closest_perler_color(original_rgb)
            row.append(perler_color)
            
            # 统计颜色使用
            color_counts[perler_color] = color_counts.get(perler_color, 0) + 1
        pattern.append(row)
    
    # 生成图纸图片
    bead_size = 20  # 每个珠子显示的像素大小
    pattern_img = Image.new('RGB', (bead_width * bead_size, bead_height * bead_size))
    
    for y, row in enumerate(pattern):
        for x, color_name in enumerate(row):
            color_rgb = PERLER_COLORS[color_name]
            for dy in range(bead_size):
                for dx in range(bead_size):
                    pattern_img.putpixel((x * bead_size + dx, y * bead_size + dy), color_rgb)
    
    # 转换为base64
    img_buffer = io.BytesIO()
    pattern_img.save(img_buffer, format='PNG')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return {
        'pattern': pattern,
        'pattern_image': img_base64,
        'color_counts': color_counts,
        'width': bead_width,
        'height': bead_height
    }


@app.route('/')
def index():
    """首页"""
    return render_template('index.html', 
                         student_id='202535720114',
                         student_name='廖佳煜')


@app.route('/generate', methods=['POST'])
def generate():
    """生成拼豆图纸"""
    if 'image' not in request.files:
        return jsonify({'error': '请上传图片'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    # 获取参数
    width = request.form.get('width', 32, type=int)
    height = request.form.get('height', 32, type=int)
    n_colors = request.form.get('colors', 16, type=int)
    
    # 限制参数范围
    width = max(8, min(64, width))
    height = max(8, min(64, height))
    n_colors = max(4, min(32, n_colors))
    
    try:
        image_data = file.read()
        result = generate_pattern(image_data, width, height, n_colors)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
