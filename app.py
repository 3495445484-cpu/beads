"""
拼豆图纸AI生成器 - Perler Bead Pattern Generator
作者：廖佳煜
学号：202535720114
版本：v2 - 基于221色拼豆色库
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import numpy as np
import io
import base64
import cv2

app = Flask(__name__)
CORS(app)

# 拼豆221色色库（从Excel提取的Mard品牌色号）
PERLER_COLORS = {
    # A列 - 黄色系
    'A1': '#FAF4C8', 'A2': '#FFFFD5', 'A3': '#FEFF8B', 'A4': '#FBED56',
    'A5': '#F4D738', 'A6': '#FEAC4C', 'A7': '#FE8B4C', 'A8': '#FFDA45',
    'A9': '#FF995B', 'A10': '#F77C31', 'A11': '#FFDD99', 'A12': '#FE9F72',
    'A13': '#FFC365', 'A14': '#FD543D', 'A15': '#FFF365', 'A16': '#FFFF9F',
    'A17': '#FFE36E', 'A18': '#FEBE7D', 'A19': '#FD7C72', 'A20': '#FFD568',
    'A21': '#FFE395', 'A22': '#F4F57D', 'A23': '#E6C9B7', 'A24': '#F7F8A2',
    'A25': '#FFD67D', 'A26': '#FFC830',
    # B列 - 绿色系（部分）
    'B1': '#E6EE31', 'B2': '#63F347', 'B3': '#9EF780', 'B4': '#5DE035',
    'B5': '#35E352', 'B6': '#65E2A6', 'B7': '#3DAF80', 'B8': '#1C9C4F',
    'B9': '#27523A', 'B10': '#95D3C2', 'B11': '#5D722A', 'B12': '#166F41',
    'B13': '#CAEB7B', 'B14': '#ADE946', 'B15': '#2E5132', 'B16': '#C5ED9C',
    'B17': '#9BB13A', 'B18': '#E6EE49', 'B19': '#24B88C', 'B20': '#C2F0CC',
    'B21': '#156A6B', 'B22': '#0B3C43', 'B23': '#303A21', 'B24': '#EEFCA5',
    'B25': '#4E846D', 'B26': '#8D7A35', 'B27': '#CCE1AF', 'B28': '#9EE5B9',
    'B29': '#C5E254', 'B30': '#E2FCB1', 'B31': '#B0E792', 'B32': '#9CAB5A',
    # C列 - 蓝青色系（部分）
    'C1': '#E8FFE7', 'C2': '#A9F9FC', 'C3': '#A0E2FB', 'C4': '#41CCFF',
    'C5': '#01ACEB', 'C6': '#50AAF0', 'C7': '#3677D2', 'C8': '#0F54C0',
    'C9': '#324BCA', 'C10': '#3EBCE2', 'C11': '#28DDDE', 'C12': '#1C334D',
    'C13': '#CDE8FF', 'C14': '#D5FDFF', 'C15': '#22C4C6', 'C16': '#1557A8',
    'C17': '#04D1F6', 'C18': '#1D3344', 'C19': '#1887A2', 'C20': '#176DAF',
    'C21': '#BEDDFF', 'C22': '#67B4BE', 'C23': '#C8E2FF', 'C24': '#7CC4FF',
    'C25': '#A9E5E5', 'C26': '#3CAED8', 'C27': '#D3DFFA', 'C28': '#BBCFED',
    'C29': '#34488E',
    # D列 - 紫色系（补充）
    'D1': '#AEB4F2', 'D4': '#182A84', 'D5': '#B843C5', 'D6': '#AC7BDE',
    'D8': '#E2D3FF', 'D9': '#5B9F8', 'D10': '#361B51', 'D11': '#B9BAE1',
    'D12': '#DE9AD5', 'D13': '#00095', 'D14': '#8B279B', 'D15': '#2F1E90',
    'D16': '#E3E1EE', 'D17': '#C4D4F6', 'D18': '#A45EC7', 'D19': '#E3C3D7',
    'D20': '#9C32B2', 'D21': '#9A009B', 'D22': '#33A95', 'D23': '#EBDAFC',
    'D24': '#778E5', 'D25': '#49FC7', 'D26': '#DFC2F8',
    # E列 - 粉色系（部分）
    'E1': '#FDD3CC', 'E2': '#EC0DF', 'E3': '#FFB7E7', 'E4': '#8E649E',
    'E5': '#F551A2', 'E6': '#F13D74', 'E7': '#C63478', 'E8': '#FFDBE9',
    'E9': '#E970CC', 'E10': '#D3793', 'E11': '#FCDD2', 'E12': '#F78FC3',
    'E13': '#B5006D', 'E14': '#FFD1BA', 'E15': '#F8C7C9', 'E16': '#FFF3EB',
    'E17': '#3B2EA', 'E18': '#FFC7DB', 'E19': '#FEBAD5', 'E20': '#D8C7D1',
    'E21': '#BD79A1', 'E22': '#B85A', 'E23': '#937A8D', 'E24': '#E1BCE8',
    # F列 - 红色系（部分）
    'F1': '#EEFCA5', 'F2': '#FC3D46', 'F3': '#C5ED9C', 'F4': '#FC283C',
    'F5': '#E7002F', 'F6': '#943630', 'F7': '#971937', 'F8': '#BC0028',
    'F9': '#E26777', 'F10': '#5A2111', 'F11': '#1C9C4F', 'F12': '#F35744',
    'F13': '#FFA9AD', 'F15': '#FEC2A6', 'F16': '#E69C79', 'F17': '#E370C8',
    'F18': '#4E846D', 'F19': '#CD9391', 'F20': '#CCE1AF', 'F21': '#FDC0D0',
    'F22': '#67E6', 'F23': '#E698AA', 'F24': '#E54B4F', 'F25': '#FFE2CE',
    # G列 - 棕黄色系（部分）
    'G1': '#FFE2CE', 'G2': '#FFFC4A', 'G3': '#F4C3A5', 'G4': '#E1B3B5',
    'G5': '#ED0098', 'G6': '#E99C17', 'G8': '#E6B483', 'G9': '#D98C39',
    'G10': '#E0C593', 'G11': '#FFC890', 'G12': '#B7714A', 'G13': '#8D614C',
    'G14': '#FCF9BA', 'G15': '#2E9BA', 'G16': '#7B524B', 'G17': '#FF4CC',
    'G18': '#E0795', 'G19': '#A94023', 'G20': '#B8558', 'G21': '#FDBFF',
    # H列 - 灰黑色系（部分）
    'H1': '#74941', 'H2': '#FFFFFF', 'H3': '#B61BA', 'H4': '#898C',
    'H5': '#48464', 'H6': '#000000', 'H7': '#000000', 'H8': '#E7D9DB',
    'H9': '#EDEDED', 'H10': '#EEE9EA', 'H11': '#CECD5', 'H12': '#FFF5',
    'H13': '#F5ED', 'H14': '#CFD7D3', 'H15': '#98A6A8', 'H16': '#1D1414',
    'H17': '#F1DEDD', 'H18': '#FFED', 'H19': '#F6EF2', 'H20': '#9FA93',
    'H21': '#FFBE1', 'H22': '#CACAD4', 'H23': '#3EBCE2', 'H24': '#1887A2',
    'H25': '#67B4BE', 'H26': '#C8E2FF', 'H27': '#A9E5E5', 'H28': '#3CAED8',
    'H29': '#D3DFFA', 'H30': '#BBCFED', 'H31': '#34488E', 'H32': '#34488E',
    # M列 - 大地色系（部分）
    'M1': '#BCC6B8', 'M2': '#8AA386', 'M3': '#697D80', 'M4': '#E3D2BC',
    'M5': '#D0CCAA', 'M6': '#B0A782', 'M7': '#B4A497', 'M8': '#B38281',
    'M9': '#A58767', 'M10': '#C5B2BC', 'M11': '#9F7594', 'M12': '#644749',
    'M13': '#D19066', 'M14': '#C77362', 'M15': '#757D7B',
    # P/Q/R/Y列 - 特殊色
    'P1': '#FFFFFF', 'P2': '#FD6FB4', 'P3': '#FEB481', 'P4': '#D7FAA0',
    'P5': '#8BDBFA', 'P6': '#E987EA',
    'Q1': '#D50D21', 'Q2': '#F92F83', 'Q3': '#FD8324', 'Q4': '#F8EC31',
    'Q5': '#35C75B',
}

# 将hex转为RGB元组
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def color_distance(c1, c2):
    """计算两个颜色的欧几里得距离"""
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def find_closest_perler_color(rgb):
    """找到最接近的拼豆颜色"""
    min_dist = float('inf')
    closest = 'A1'
    for name, hex_color in PERLER_COLORS.items():
        perler_rgb = hex_to_rgb(hex_color)
        dist = color_distance(rgb, perler_rgb)
        if dist < min_dist:
            min_dist = dist
            closest = name
    return closest


def generate_pattern(image_data, bead_width=32, bead_height=32):
    """生成拼豆图纸"""
    # 读取图片
    img = Image.open(io.BytesIO(image_data))
    
    # 调整尺寸（每个像素变成一个珠子）
    img = img.resize((bead_width, bead_height), Image.Resampling.LANCZOS)
    
    # 转换为RGB
    img = img.convert('RGB')
    pixels = np.array(img)
    
    # 为每个像素分配拼豆颜色
    pattern = []
    color_counts = {}
    
    for y in range(bead_height):
        row = []
        for x in range(bead_width):
            pixel_rgb = tuple(pixels[y, x])
            perler_color = find_closest_perler_color(pixel_rgb)
            row.append(perler_color)
            
            # 统计颜色使用
            color_counts[perler_color] = color_counts.get(perler_color, 0) + 1
        pattern.append(row)
    
    # 生成图纸图片
    bead_size = 20  # 每个珠子显示的像素大小
    pattern_img = Image.new('RGB', (bead_width * bead_size, bead_height * bead_size))
    
    for y, row in enumerate(pattern):
        for x, color_name in enumerate(row):
            hex_color = PERLER_COLORS.get(color_name, '#FFFFFF')
            color_rgb = hex_to_rgb(hex_color)
            for dy in range(bead_size):
                for dx in range(bead_size):
                    pattern_img.putpixel((x * bead_size + dx, y * bead_size + dy), color_rgb)
    
    # 添加网格线
    for y in range(bead_height):
        for x in range(bead_width):
            for i in range(bead_size):
                # 垂直线
                pattern_img.putpixel((x * bead_size + i, y * bead_size), (200, 200, 200))
                pattern_img.putpixel((x * bead_size + i, y * bead_size + bead_size - 1), (200, 200, 200))
                # 水平线
                pattern_img.putpixel((x * bead_size, y * bead_size + i), (200, 200, 200))
                pattern_img.putpixel((x * bead_size + bead_size - 1, y * bead_size + i), (200, 200, 200))
    
    # 转换为base64
    img_buffer = io.BytesIO()
    pattern_img.save(img_buffer, format='PNG')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return {
        'pattern': pattern,
        'pattern_image': img_base64,
        'color_counts': color_counts,
        'width': bead_width,
        'height': bead_height,
        'total_beads': bead_width * bead_height
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
    
    # 限制参数范围
    width = max(8, min(64, width))
    height = max(8, min(64, height))
    
    try:
        image_data = file.read()
        result = generate_pattern(image_data, width, height)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/colors')
def get_colors():
    """获取所有拼豆颜色"""
    return jsonify(PERLER_COLORS)


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
