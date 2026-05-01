"""
gen_screenshots.py — 将截图 mockup HTML 导出为 App Store 所需分辨率的 PNG

App Store iPhone 6.7" 要求: 1290 × 2796 px

用法:
    python gen_screenshots.py

输出: docs/screenshots/ 目录下 5 张 PNG
"""

import subprocess, sys, os

def install_if_needed(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

install_if_needed('playwright')

from playwright.sync_api import sync_playwright

# ── 配置 ──────────────────────────────────────────────────────────────────────
MOCKUP_URL = 'http://localhost:3456/docs/screenshots-mockup.html'
OUT_DIR    = os.path.join(os.path.dirname(__file__), 'docs', 'screenshots')

# App Store iPhone 6.7" 分辨率
TARGET_W = 1290
TARGET_H = 2796

# 每张截图对应的 .phone-wrap 索引 (0-based) 和文件名
SHOTS = [
    (0, '01-map-screen.png',       '关卡地图'),
    (1, '02-classic-gameplay.png', '经典游戏'),
    (2, '03-time-attack.png',      '时间挑战'),
    (3, '04-survival-mode.png',    '生存模式'),
    (4, '05-perfect-clear.png',    '完美通关'),
]

# phone-wrap 在 mockup 中实际宽度 = 300px，需放大到 1290px
# device pixel ratio = 1290 / 300 ≈ 4.3
DPR = TARGET_W / 300  # ≈ 4.3

os.makedirs(OUT_DIR, exist_ok=True)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # 视口宽度足够宽，让所有截图横向排列都能渲染
        page = browser.new_page(
            viewport={'width': 1600, 'height': 900},
            device_scale_factor=DPR,
        )
        page.goto(MOCKUP_URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1500)  # 等动画稳定

        # 获取所有 phone-wrap 元素
        wraps = page.query_selector_all('.phone-wrap')
        if len(wraps) < len(SHOTS):
            print(f'Warning: found {len(wraps)} phone-wrap elements, expected {len(SHOTS)}')

        for idx, filename, label in SHOTS:
            if idx >= len(wraps):
                print(f'  跳过 #{idx} ({label}) — 元素不存在')
                continue

            el = wraps[idx]
            out_path = os.path.join(OUT_DIR, filename)

            # 截取元素（playwright 会自动应用 device_scale_factor）
            el.screenshot(path=out_path)

            # 验证尺寸
            from PIL import Image
            img = Image.open(out_path)
            w, h = img.size
            print(f'  OK {filename} {w}x{h} ({label})')

            # 如果高度不足 TARGET_H，用深色背景填充到正确比例
            if h < TARGET_H or w != TARGET_W:
                canvas = Image.new('RGB', (TARGET_W, TARGET_H), (15, 8, 36))
                paste_x = (TARGET_W - w) // 2
                paste_y = (TARGET_H - h) // 2
                canvas.paste(img, (paste_x, paste_y))
                canvas.save(out_path, 'PNG')
                print(f'     padded to {TARGET_W}x{TARGET_H}')

        browser.close()
        print(f'\nDone! Screenshots saved to {OUT_DIR}')
        print('Upload to App Store Connect under iPhone 6.7" slot')

if __name__ == '__main__':
    run()
