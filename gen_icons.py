"""
生成星星扫雷 PWA 图标 v2
设计：深紫蓝渐变 + 发光金色大星星 + 闪光粒子
"""
from PIL import Image, ImageDraw, ImageFilter
import math, os

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def star_polygon(cx, cy, ro, ri, n, angle=0):
    pts = []
    for i in range(n * 2):
        r = ro if i % 2 == 0 else ri
        a = angle + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def make_icon(size):
    s = size
    cx, cy = s // 2, s // 2
    r_corner = int(s * 0.22)

    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))

    # ── 1. 渐变背景（紫→蓝）────────────────────────────────
    bg = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)
    top_col = (80,  44, 195)   # 亮紫
    bot_col = (28, 110, 235)   # 蓝
    for y in range(s):
        t = y / (s - 1)
        col = lerp_color(top_col, bot_col, t)
        bg_draw.line([(0, y), (s - 1, y)], fill=col + (255,))
    mask = Image.new('L', (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s-1, s-1], radius=r_corner, fill=255)
    bg.putalpha(mask)
    img = Image.alpha_composite(img, bg)

    # ── 2. 中心辐射光晕 ─────────────────────────────────────
    glow = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for rr in range(int(s * 0.52), 0, -max(1, s // 60)):
        a = int(50 * (1 - rr / (s * 0.52)) ** 1.6)
        gd.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=(180, 150, 255, a))
    img = Image.alpha_composite(img, glow)

    # ── 3. 星星光晕（先模糊）───────────────────────────────
    star_r  = int(s * 0.36)
    star_ri = int(s * 0.148)
    angle   = -math.pi / 2

    halo = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    max_expand = int(s * 0.10)
    for ex in range(max_expand, 0, -max(1, max_expand // 60)):
        a = int(110 * (1 - ex / max_expand) ** 2.2)
        pts = star_polygon(cx, cy, star_r + ex, star_ri + ex // 3, 5, angle)
        hd.polygon(pts, fill=(255, 200, 50, a))
    halo = halo.filter(ImageFilter.GaussianBlur(radius=int(s * 0.022)))
    img = Image.alpha_composite(img, halo)

    # ── 4. 星星主体（三层模拟渐变）─────────────────────────
    draw = ImageDraw.Draw(img)
    # 底层：深金
    pts_outer = star_polygon(cx, cy, star_r, star_ri, 5, angle)
    draw.polygon(pts_outer, fill=(200, 130, 0, 255))
    # 中层：亮金
    pts_mid = star_polygon(cx, cy, int(star_r * 0.86), int(star_ri * 0.86), 5, angle)
    draw.polygon(pts_mid, fill=(255, 200, 30, 255))
    # 高光层（左上偏移）
    hx = cx - int(s * 0.04)
    hy = cy - int(s * 0.06)
    pts_hi = star_polygon(hx, hy, int(star_r * 0.56), int(star_ri * 0.58), 5, angle)
    draw.polygon(pts_hi, fill=(255, 242, 140, 210))
    # 核心白光
    cr = int(s * 0.075)
    draw.ellipse([hx-cr, hy-cr, hx+cr, hy+cr], fill=(255, 255, 240, 140))
    # 星星描边
    draw.polygon(pts_outer, outline=(160, 100, 0, 200),
                 width=max(1, int(s * 0.006)))

    # ── 5. 闪光粒子 ✦ ──────────────────────────────────────
    sparks = [
        (cx + int(s*0.32), cy - int(s*0.30), 0.12),
        (cx - int(s*0.33), cy - int(s*0.28), 0.09),
        (cx + int(s*0.30), cy + int(s*0.27), 0.09),
        (cx - int(s*0.28), cy + int(s*0.30), 0.08),
        (cx + int(s*0.00), cy - int(s*0.40), 0.07),
        (cx + int(s*0.38), cy + int(s*0.06), 0.06),
    ]
    for sx, sy, sr in sparks:
        pr = int(s * sr)
        for a in [0, math.pi / 2]:
            x1 = sx + int(pr * 1.5 * math.cos(a))
            y1 = sy + int(pr * 1.5 * math.sin(a))
            x2 = sx - int(pr * 1.5 * math.cos(a))
            y2 = sy - int(pr * 1.5 * math.sin(a))
            draw.line([(x1, y1), (x2, y2)],
                      fill=(255, 240, 160, 210),
                      width=max(1, int(pr * 0.20)))
        r2 = max(1, pr // 3)
        draw.ellipse([sx-r2, sy-r2, sx+r2, sy+r2],
                     fill=(255, 255, 230, 240))

    # ── 6. 底部小字 "★" 暗纹（仅大尺寸）──────────────────
    # (可选，视觉太小省略)

    # ── 7. 最终圆角裁切 ────────────────────────────────────
    final_mask = Image.new('L', (s, s), 0)
    ImageDraw.Draw(final_mask).rounded_rectangle(
        [0, 0, s-1, s-1], radius=r_corner, fill=255)
    img.putalpha(final_mask)
    return img

out_dir = os.path.dirname(os.path.abspath(__file__)) + '/icons'
os.makedirs(out_dir, exist_ok=True)

for size, name in [(180,'icon-180'),(192,'icon-192'),(512,'icon-512')]:
    icon = make_icon(size)
    icon.save(f'{out_dir}/{name}.png', 'PNG')
    print(f'OK {name}.png {size}x{size}')
print('Done')
