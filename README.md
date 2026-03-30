# 🎨 拼豆图纸AI生成器

> 把任意图片转换成拼豆制作图纸 (Perler Bead Pattern Generator)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📚 项目信息

- **学号**：202535720114
- **姓名**：廖佳煜
- **课程**：人工智能应用实践

---

## 🎯 项目简介

本项目是一个基于AI的拼豆（Perler Bead）图纸自动生成工具。用户上传任意图片，系统自动：

1. 🎨 智能分析图片颜色
2. 🔢 K-Means颜色量化（匹配拼豆颜色库）
3. 📋 输出可制作的拼豆图纸

---

## ✨ 功能特点

- 📤 支持上传任意图片（JPG/PNG/GIF等）
- 🎨 自动颜色量化和最优匹配
- ⚙️ 可调节参数：图纸尺寸、颜色数量
- 📊 显示所需颜色清单和数量统计
- 🎯 实时预览生成的拼豆图纸

---

## 🛠️ 技术栈

| 技术 | 说明 |
|------|------|
| **Python** | 后端核心语言 |
| **Flask** | Web 框架 |
| **OpenCV** | K-Means 颜色量化 |
| **Pillow** | 图片处理 |
| **HTML/CSS/JS** | 前端界面 |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/3495445484-cpu/beads.git
cd beads
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行项目

```bash
python app.py
```

### 4. 打开浏览器

访问 http://127.0.0.1:5000

---

## 📖 使用方法

1. **上传图片** - 点击上传区域，选择要转换的图片
2. **设置参数** - 调整宽度、高度和颜色数量
3. **生成图纸** - 点击按钮，AI自动处理
4. **保存图纸** - 右键保存生成的拼豆图纸

---

## 🎓 项目原理

### 颜色量化 (K-Means)

```
原始图片 (可能包含上百万种颜色)
        ↓
K-Means 聚类 (聚合成N种主要颜色)
        ↓
匹配拼豆颜色库 (从几十种拼豆颜色中选择最接近的)
        ↓
输出拼豆图纸 (每个位置对应一种拼豆颜色)
```

### 拼豆颜色匹配

系统内置了30种常用拼豆颜色，通过欧几里得距离计算，找出最接近的颜色进行替换。

---

## 📂 项目结构

```
beads/
├── app.py                 # Flask 主程序
├── requirements.txt       # 依赖列表
├── templates/
│   └── index.html         # 前端页面
├── README.md              # 项目说明
└── LICENSE                # MIT 许可证
```

---

## 🔧 参数说明

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| 宽度 | 32 | 8-64 | 拼豆图纸的横向珠子数 |
| 高度 | 32 | 8-64 | 拼豆图纸的纵向珠子数 |
| 颜色数量 | 16 | 4-32 | 最终使用的颜色种类数 |

---

## 💡 扩展方向

- [ ] 添加更多拼豆颜色
- [ ] 支持拼豆品牌选择（Hama/Perler/Pegboard）
- [ ] 添加熨烫方向指导
- [ ] 支持批量处理
- [ ] 添加颜色统计导出

---

## 📝 核心算法

```python
# K-Means 颜色量化
cv2.kmeans(pixels, n_colors, criteria, 10, flags)

# 颜色距离计算
distance = sqrt((r1-r2)² + (g1-g2)² + (b1-b2)²)

# 最优颜色匹配
closest_color = min(colors, key=lambda c: color_distance(rgb, c))
```

---

## 👤 作者

**廖佳煜**  
学号：202535720114

---

## 📄 许可证

MIT License

---

> 🎨 *用AI让创意变成现实！*
