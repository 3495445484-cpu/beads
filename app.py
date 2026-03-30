"""
拼豆图纸AI生成器 - Perler Bead Pattern Generator
作者：廖佳煜
学号：202535720114
版本：v6 - 优化性能，支持大图片
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import base64

app = Flask(__name__)
CORS(app)

# 预加载字体（只加载一次）
DEFAULT_FONT = None
BOLD_FONT = None

def get_fonts(size=10):
    global DEFAULT_FONT, BOLD_FONT
    if DEFAULT_FONT is None or DEFAULT_FONT.size != size:
        try:
            DEFAULT_FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
            BOLD_FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except:
            DEFAULT_FONT = ImageFont.load_default()
            BOLD_FONT = ImageFont.load_default()
    return DEFAULT_FONT, BOLD_FONT

# 拼豆完整色库
PERLER_COLORS = {
    # A列 - 黄色系
    'A1': '#FAF4C8', 'A2': '#FFFFD5', 'A3': '#FEFF8B', 'A4': '#FBED56',
    'A5': '#F4D738', 'A6': '#FEAC4C', 'A7': '#FE8B4C', 'A8': '#FFDA45',
    'A9': '#FF995B', 'A10': '#F77C31', 'A11': '#FFDD99', 'A12': '#FE9F72',
    'A13': '#FFC365', 'A14': '#FD543D', 'A15': '#FFF365', 'A16': '#FFFF9F',
    'A17': '#FFE36E', 'A18': '#FEBE7D', 'A19': '#FD7C72', 'A20': '#FFD568',
    'A21': '#FFE395', 'A22': '#F4F57D', 'A23': '#E6C9B7', 'A24': '#F7F8A2',
    'A25': '#FFD67D', 'A26': '#FFC830',
    # B列 - 绿色系
    'B1': '#E6EE31', 'B2': '#63F347', 'B3': '#9EF780', 'B4': '#5DE035',
    'B5': '#35E352', 'B6': '#65E2A6', 'B7': '#3DAF80', 'B8': '#1C9C4F',
    'B9': '#27523A', 'B10': '#95D3C2', 'B11': '#5D722A', 'B12': '#166F41',
    'B13': '#CAE7B', 'B14': '#ADE946', 'B15': '#2E5132', 'B16': '#C5ED9C',
    'B17': '#9BB13A', 'B18': '#E6EE49', 'B19': '#24B88C', 'B20': '#C2F0CC',
    'B21': '#156A6B', 'B22': '#0B3C43', 'B23': '#303A21', 'B24': '#EEFCA5',
    'B25': '#4E846D', 'B26': '#8D7A35', 'B27': '#CCE1AF', 'B28': '#9EE5B9',
    'B29': '#C5E254', 'B30': '#E2FCB1', 'B31': '#B0E792', 'B32': '#9CAB5A',
    # C列 - 蓝青色系
    'C1': '#E8FFE7', 'C2': '#A9F9FC', 'C3': '#A0E2FB', 'C4': '#41CCFF',
    'C5': '#01ACEB', 'C6': '#50AAF0', 'C7': '#3677D2', 'C8': '#0F54C0',
    'C9': '#324BCA', 'C10': '#3EBCE2', 'C11': '#28DDDE', 'C12': '#1C334D',
    'C13': '#CDE8FF', 'C14': '#D5FDFF', 'C15': '#22C4C6', 'C16': '#1557A8',
    'C17': '#04D1F6', 'C18': '#1D3344', 'C19': '#1887A2', 'C20': '#176DAF',
    'C21': '#BEDDFF', 'C22': '#67B4BE', 'C23': '#C8E2FF', 'C24': '#7CC4FF',
    'C25': '#A9E5E5', 'C26': '#3CAED8', 'C27': '#D3FFA', 'C28': '#BBCFED',
    'C29': '#34488E',
    # D列 - 蓝紫色系
    'D1': '#AEB4F2', 'D2': '#858EDD', 'D3': '#2F54AF', 'D4': '#182A84',
    'D5': '#B843C5', 'D6': '#AC7BDE', 'D7': '#8854B3', 'D8': '#E2D3FF',
    'D9': '#D5B9F8', 'D10': '#361B51', 'D11': '#B9BAE1', 'D12': '#DE9AD5',
    'D13': '#B90095', 'D14': '#8B279B', 'D15': '#2F1E90', 'D16': '#E3E1EE',
    'D17': '#C4D4F6', 'D18': '#A45EC7', 'D19': '#D8C3D7', 'D20': '#9C32B2',
    'D21': '#9A009B', 'D22': '#333A95', 'D23': '#EBDAFC', 'D24': '#7786E5',
    'D25': '#494FC7', 'D26': '#DFC2F8',
    # E列 - 粉色系
    'E1': '#FDD3CC', 'E2': '#FEC0DF', 'E3': '#FFB7E7', 'E4': '#E8649E',
    'E5': '#F551A2', 'E6': '#F13D74', 'E7': '#C63478', 'E8': '#FFDBE9',
    'E9': '#E970CC', 'E10': '#D33793', 'E11': '#FCDDD2', 'E12': '#F78FC3',
    'E13': '#B5006D', 'E14': '#FFD1BA', 'E15': '#F8C7C9', 'E16': '#FFF3EB',
    'E17': '#FFE2EA', 'E18': '#FFC7DB', 'E19': '#FEBAD5', 'E20': '#D8C7D1',
    'E21': '#BD9DA1', 'E22': '#B785A1', 'E23': '#937A8D', 'E24': '#E1BCE8',
    # F列 - 红色系
    'F1': '#FD957B', 'F2': '#FC3D46', 'F3': '#F74941', 'F4': '#FC283C',
    'F5': '#E7002F', 'F6': '#943630', 'F7': '#971937', 'F8': '#BC0028',
    'F9': '#E2677A', 'F10': '#8A4526', 'F11': '#5A2111', 'F12': '#FD4E6A',
    'F13': '#F35744', 'F14': '#FFA9AD', 'F15': '#D30022', 'F16': '#FEC2A6',
    'F17': '#E69C79', 'F18': '#D37C46', 'F19': '#C1444A', 'F20': '#CD9391',
    'F21': '#F7B4C6', 'F22': '#FDC0D0', 'F23': '#F67E66', 'F24': '#E698AA',
    'F25': '#E54B4F',
    # G列 - 棕黄色系
    'G1': '#FFE2CE', 'G2': '#FFC4AA', 'G3': '#F4C3A5', 'G4': '#E1B383',
    'G5': '#EDB045', 'G6': '#E99C17', 'G7': '#9D5B3E', 'G8': '#753B32',
    'G9': '#E6B483', 'G10': '#D98C39', 'G11': '#E0C593', 'G12': '#FFC890',
    'G13': '#B7714A', 'G14': '#8D614C', 'G15': '#FCF9E0', 'G16': '#F2D9BA',
    'G17': '#7B524B', 'G18': '#FFE4CC', 'G19': '#E07935', 'G20': '#A94023',
    'G21': '#B8558',
    # H列 - 灰黑色系
    'H1': '#FDFBFF', 'H2': '#FEFFFF', 'H3': '#B6B1BA', 'H4': '#89858C',
    'H5': '#48464E', 'H6': '#2F2B2F', 'H7': '#000000', 'H8': '#E7D6DB',
    'H9': '#EDEDED', 'H10': '#EEE9EA', 'H11': '#CECDD5', 'H12': '#FFF5ED',
    'H13': '#F5ECD2', 'H14': '#CFD7D3', 'H15': '#98A6A8', 'H16': '#1D1414',
    'H17': '#F1EDED', 'H18': '#FFFDF0', 'H19': '#F6EFE2', 'H20': '#949FA3',
    'H21': '#FFFBE1', 'H22': '#CACAD4', 'H23': '#9A9D94',
    # M列 - 大地色系
    'M1': '#BCC6B8', 'M2': '#8AA386', 'M3': '#697D80', 'M4': '#E3D2BC',
    'M5': '#D0CCAA', 'M6': '#B0A782', 'M7': '#B4A497', 'M8': '#B38281',
    'M9': '#A58767', 'M10': '#C5B2BC', 'M11': '#9F7594', 'M12': '#644749',
    'M13': '#D19066', 'M14': '#C77362', 'M15': '#757D7B',
    # P列
    'P1': '#FCF7F8', 'P2': '#B0A9AC', 'P3': '#AFDCAB', 'P4': '#FEA49F',
    'P5': '#EE8C3E', 'P6': '#5FD0A7', 'P7': '#EB9270', 'P8': '#F0D958',
    'P9': '#D9D9D9', 'P10': '#D9C7EA', 'P11': '#F3ECC9', 'P12': '#E6EEF2',
    'P13': '#AACBEF', 'P14': '#3376B0', 'P15': '#668575', 'P16': '#FEBF45',
    'P17': '#FEA324', 'P18': '#FEB89F', 'P19': '#FFE0E9', 'P20': '#FEBECF',
    'P21': '#ECBEBF', 'P22': '#E4A89F', 'P23': '#A56268',
    # Q列
    'Q1': '#F2A5E8', 'Q2': '#E9EC91', 'Q3': '#FFFF00', 'Q4': '#FFEBFA', 'Q5': '#76CEDE',
    # R列
    'R1': '#D50D21', 'R2': '#F92F83', 'R3': '#FD8324', 'R4': '#F8EC31',
    'R5': '#35C75B', 'R6': '#23B891', 'R7': '#19779D', 'R8': '#1A60C3',
    'R9': '#9A56B4', 'R10': '#FFDB4C', 'R11': '#FFEBFA', 'R12': '#D8D5CE',
    'R13': '#55514C', 'R14': '#9FE4DF', 'R15': '#77CEE9', 'R16': '#3ECFCA',
    'R17': '#4A867A', 'R18': '#7FCD9D', 'R19': '#CDE55D', 'R20': '#E8C7B4',
    'R21': '#AD6F3C', 'R22': '#6C372F', 'R23': '#FEB872', 'R24': '#F3C1C0',
    'R25': '#C9675E', 'R26': '#D293BE', 'R27': '#EA8CB1', 'R28': '#9C87D6',
    # T列
    'T1': '#FFFFFF',
    # ZG列
    'ZG1': '#DAABB3', 'ZG2': '#D6AA87', 'ZG3': '#C1BD8D', 'ZG4': '#96B69F',
    'ZG5': '#849DC6', 'ZG6': '#94BFE2', 'ZG7': '#E2A9D2', 'ZG8': '#AB91C0',
}

# 预计算RGB值
PERLER_RGB = {name: tuple(int(c[i:i+2], 16) for i in (0, 2, 4)) 
              for name, c in PERLER_COLORS.items()}
COLOR_LIST = list(PERLER_RGB.keys())
COLOR_ARRAY = np.array([PERLER_RGB[c] for c in COLOR_LIST], dtype=np.float32)


def find_closest_perler_color_fast(rgb):
    """快速找到最接近的拼豆颜色"""
    rgb = np.array(rgb, dtype=np.float32)
    dists = np.sqrt(np.sum((COLOR_ARRAY - rgb) ** 2, axis=1))
    idx = np.argmin(dists)
    return COLOR_LIST[idx]


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_pattern(image_data, width=None, height=None, max_size=104):
    """生成拼豆图纸 - 优化版"""
    # 读取图片
    img = Image.open(io.BytesIO(image_data))
    orig_w, orig_h = img.size
    
    # 如果没有指定尺寸，使用原图但限制最大尺寸
    if width is None or height is None:
        # 等比例缩放，限制最大尺寸
        ratio = min(max_size / orig_w, max_size / orig_h, 1.0)
        width = int(orig_w * ratio)
        height = int(orig_h * ratio)
    
    # 确保尺寸在合理范围内
    width = max(8, min(width, max_size))
    height = max(8, min(height, max_size))
    
    # 调整图片
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    img = img.convert('RGB')
    pixels = np.array(img)
    
    # 预计算所有像素的颜色
    pattern = np.array([[find_closest_perler_color_fast(tuple(pixels[y, x])) 
                         for x in range(width)] for y in range(height)])
    
    # 统计颜色
    flat_pattern = pattern.flatten()
    unique, counts = np.unique(flat_pattern, return_counts=True)
    color_counts = dict(zip(unique, counts.tolist()))
    
    # 预计算边缘掩码
    edge_mask = np.zeros((height, width), dtype=bool)
    for y in range(height):
        for x in range(width):
            if y == 0 or y == height-1 or x == 0 or x == width-1:
                edge_mask[y, x] = True
            elif pattern[y, x] != pattern[y-1, x] or pattern[y, x] != pattern[y+1, x] or pattern[y, x] != pattern[y, x-1] or pattern[y, x] != pattern[y, x+1]:
                edge_mask[y, x] = True
    
    # 生成图纸
    cell_size = 28
    margin = 10
    header = cell_size
    left_w = cell_size
    
    # 统计区域高度
    lines_needed = max(2, len(color_counts) // 15 + 2)
    stats_height = lines_needed * 16 + 20
    
    canvas_w = left_w + (width + margin * 2) * cell_size
    canvas_h = header + (height + margin * 2) * cell_size + stats_height
    
    canvas = Image.new('RGB', (canvas_w, canvas_h), 'white')
    draw = ImageDraw.Draw(canvas)
    
    # 获取字体
    font_small, font_bold = get_fonts(8)
    
    # 绘制图案
    for y in range(height):
        for x in range(width):
            color_name = pattern[y, x]
            hex_color = PERLER_COLORS[color_name]
            rgb = hex_to_rgb(hex_color)
            
            px = left_w + (x + margin) * cell_size
            py = header + (y + margin) * cell_size
            
            # 填充颜色
            draw.rectangle([px, py, px + cell_size - 1, py + cell_size - 1], fill=rgb)
            
            # 边缘勾勒
            if edge_mask[y, x]:
                draw.rectangle([px, py, px + cell_size - 1, py + cell_size - 1], outline='#000000', width=2)
            
            # 网格线
            draw.rectangle([px, py, px + cell_size - 1, py + cell_size - 1], outline='#CCCCCC', width=1)
            
            # 写色号
            bbox = draw.textbbox((0, 0), color_name, font=font_bold)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text((px + (cell_size - tw) // 2, py + (cell_size - th) // 2), color_name, fill='#000000', font=font_bold)
    
    # 顶部行号
    for x in range(width):
        px = left_w + (x + margin) * cell_size + cell_size // 2
        num = str(x + 1)
        bbox = draw.textbbox((0, 0), num, font=font_small)
        tw = bbox[2] - bbox[0]
        draw.text((px - tw // 2, 3), num, fill='#666666', font=font_small)
    
    # 左侧列号
    for y in range(height):
        py = header + (y + margin) * cell_size + cell_size // 2
        num = str(y + 1)
        bbox = draw.textbbox((0, 0), num, font=font_small)
        th = bbox[3] - bbox[1]
        draw.text((2, py - th // 2), num, fill='#666666', font=font_small)
    
    # 底部统计
    col_order = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'M': 8, 'P': 9, 'Q': 10, 'R': 11, 'T': 12, 'ZG': 13}
    
    sorted_colors = sorted(color_counts.items(), key=lambda item: (
        -item[1], 
        col_order.get(item[0][:1], 14),
        col_order.get(''.join(c for c in item[0] if c.isalpha()), 14),
        int(''.join(c for c in item[0] if c.isdigit()) or '0')
    ))
    
    stats_text = ' '.join(f'{n}({c})' for n, c in sorted_colors)
    
    stats_y = header + (height + margin * 2) * cell_size + 10
    font_stats, _ = get_fonts(9)
    
    max_chars = (canvas_w - 10) // 7
    words = stats_text.split()
    line = ''
    line_y = stats_y
    for word in words:
        if len(line) + len(word) + 1 <= max_chars:
            line += (' ' if line else '') + word
        else:
            draw.text((5, line_y), line, fill='#333333', font=font_stats)
            line_y += 14
            line = word
    if line:
        draw.text((5, line_y), line, fill='#333333', font=font_stats)
    
    # 输出
    img_buffer = io.BytesIO()
    canvas.save(img_buffer, format='PNG')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return {
        'pattern_image': img_base64,
        'color_counts': color_counts,
        'width': width,
        'height': height,
        'total_beads': width * height,
        'stats': stats_text
    }


@app.route('/')
def index():
    return render_template('index.html', 
                         student_id='202535720114',
                         student_name='廖佳煜')


@app.route('/generate', methods=['POST'])
def generate():
    if 'image' not in request.files:
        return jsonify({'error': '请上传图片'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    width = request.form.get('width', type=int)
    height = request.form.get('height', type=int)
    
    try:
        image_data = file.read()
        result = generate_pattern(image_data, width, height)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/colors')
def get_colors():
    return jsonify(PERLER_COLORS)


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'total_colors': len(PERLER_COLORS)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
