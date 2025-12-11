# create_placeholder.py
from PIL import Image, ImageDraw, ImageFont
import os

# 创建占位图片
img = Image.new('RGB', (300, 200), color=(233, 236, 239))
d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("arial.ttf", 30)
except:
    font = ImageFont.load_default()

d.text((50, 80), "纹样图片", fill=(73, 80, 87), font=font)
d.text((80, 120), "加载中...", fill=(73, 80, 87), font=font)

# 保存到static目录
os.makedirs('static', exist_ok=True)
img.save('static/placeholder.jpg')
print("占位图片已创建")