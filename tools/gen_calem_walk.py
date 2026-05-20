#!/usr/bin/env python3
"""
从 Showdown Calem 立绘提取配色，生成俯视角4方向行走精灵表
输出：assets/sprites/characters/player/calem_walk.png  (16×24 每帧，4方向×3帧)
精灵表布局：
  行0: 下(DOWN)  帧0,1,2
  行1: 左(LEFT)  帧0,1,2
  行2: 右(RIGHT) 帧0,1,2
  行3: 上(UP)    帧0,1,2
总尺寸: 48×96 px
"""

import subprocess
import sys
import os
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("pip install Pillow numpy")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
GAME_ROOT = Path(__file__).parent.parent
OUT_DIR   = GAME_ROOT / "assets" / "sprites" / "characters" / "player"
OUT_PATH  = OUT_DIR / "calem_walk.png"
TMP_SRC   = Path(os.environ.get("TEMP", "/tmp")) / "calem_src.png"

# ---------- Calem 配色（从立绘采样） ----------
# 皮肤
SKIN_L  = (248, 208, 184, 255)
SKIN_D  = (212, 160, 128, 255)
# 头发（深棕）
HAIR_L  = (93,  92,  92,  255)
HAIR_D  = (56,  64,  64,  255)
# 帽子（深蓝）
HAT_L   = (89, 110, 173, 255)
HAT_D   = (43,  46,  74,  255)
# 上衣（蓝灰）
SHIRT_L = (74,  94, 127, 255)
SHIRT_D = (56,  67,  84,  255)
# 裤子（深蓝灰）
PANTS_L = (74,  86, 128, 255)
PANTS_D = (43,  50,  80,  255)
# 鞋子
SHOE    = (34,  41,  51,  255)
# 轮廓
OUTLINE = (0,    0,   0,  255)
# 透明
T       = (0,    0,   0,   0)

W, H = 16, 24  # 每帧尺寸


def px(draw, x, y, c):
    draw.point((x, y), fill=c)


def draw_down(frame: int) -> Image.Image:
    """朝下（正面）"""
    img = Image.new("RGBA", (W, H), T)
    d = ImageDraw.Draw(img)
    # 帽子
    for x in range(4, 12):
        px(d, x, 0, OUTLINE)
    for x in range(3, 13):
        px(d, x, 1, HAT_L)
        px(d, x, 2, HAT_L)
    for x in range(3, 13):
        px(d, x, 3, HAT_D)
    # 头发两侧
    for y in range(1, 4):
        px(d, 2, y, HAIR_D)
        px(d, 13, y, HAIR_D)
    # 脸
    for x in range(3, 13):
        for y in range(4, 9):
            px(d, x, y, SKIN_L)
    # 眼睛
    if frame == 1:  # 眨眼帧
        for x in range(5, 7):   px(d, x, 6, OUTLINE)
        for x in range(9, 11):  px(d, x, 6, OUTLINE)
    else:
        for x in range(5, 7):   px(d, x, 6, HAIR_D)
        for x in range(9, 11):  px(d, x, 6, HAIR_D)
    # 嘴
    px(d, 7, 8, SKIN_D); px(d, 8, 8, SKIN_D)
    # 轮廓（头）
    for x in range(3, 13): px(d, x, 9, OUTLINE)
    for y in range(4, 9):
        px(d, 2, y, OUTLINE); px(d, 13, y, OUTLINE)
    # 上衣
    for x in range(3, 13):
        for y in range(10, 16):
            px(d, x, y, SHIRT_L)
    for x in range(3, 13): px(d, x, 10, SHIRT_D)
    # 衣领皮肤
    px(d, 7, 10, SKIN_L); px(d, 8, 10, SKIN_L)
    # 手臂
    for y in range(10, 16):
        px(d, 2, y, SHIRT_D); px(d, 13, y, SHIRT_D)
    # 腿步（走路动画）
    leg_offset = [0, 1, -1][frame]
    for x in range(4, 8):
        for y in range(16, 22):
            px(d, x, y + (leg_offset if x < 8 else 0), PANTS_L)
    for x in range(8, 12):
        for y in range(16, 22):
            px(d, x, y + (-leg_offset if x >= 8 else 0), PANTS_L)
    # 鞋
    for x in range(4, 8):   px(d, x, 22 + (leg_offset if x < 8 else 0), SHOE)
    for x in range(8, 12):  px(d, x, 22 + (-leg_offset if x >= 8 else 0), SHOE)
    return img


def draw_up(frame: int) -> Image.Image:
    """朝上（背面）"""
    img = Image.new("RGBA", (W, H), T)
    d = ImageDraw.Draw(img)
    # 帽子背面
    for x in range(3, 13):
        for y in range(0, 4):
            px(d, x, y, HAT_D)
    # 头发（后脑）
    for x in range(3, 13):
        for y in range(4, 7):
            px(d, x, y, HAIR_D)
    for y in range(4, 9):
        px(d, 2, y, HAIR_D); px(d, 13, y, HAIR_D)
    # 脖子
    for x in range(6, 10):
        for y in range(7, 10):
            px(d, x, y, SKIN_L)
    # 背部衣服
    for x in range(3, 13):
        for y in range(10, 16):
            px(d, x, y, SHIRT_L)
    for x in range(3, 13): px(d, x, 10, SHIRT_D)
    for y in range(10, 16):
        px(d, 2, y, SHIRT_D); px(d, 13, y, SHIRT_D)
    # 腿
    leg_offset = [0, 1, -1][frame]
    for x in range(4, 8):
        for y in range(16, 22):
            px(d, x, y + (leg_offset if x < 8 else 0), PANTS_L)
    for x in range(8, 12):
        for y in range(16, 22):
            px(d, x, y + (-leg_offset if x >= 8 else 0), PANTS_L)
    for x in range(4, 8):   px(d, x, 22 + (leg_offset if x < 8 else 0), SHOE)
    for x in range(8, 12):  px(d, x, 22 + (-leg_offset if x >= 8 else 0), SHOE)
    return img


def draw_side(frame: int, facing_right: bool) -> Image.Image:
    """朝左或朝右（侧面）"""
    img = Image.new("RGBA", (W, H), T)
    d = ImageDraw.Draw(img)
    flip = facing_right
    # 帽子
    hx = range(3, 12) if not flip else range(4, 13)
    for x in hx:
        px(d, x, 0, OUTLINE)
        px(d, x, 1, HAT_L)
        px(d, x, 2, HAT_L)
        px(d, x, 3, HAT_D)
    brim_x = 2 if not flip else 13
    for y in range(1, 4): px(d, brim_x, y, HAT_D)
    # 脸
    fx = range(4, 12) if not flip else range(4, 12)
    for x in fx:
        for y in range(4, 9):
            px(d, x, y, SKIN_L)
    # 眼睛（侧面单眼）
    eye_x = 4 if not flip else 11
    px(d, eye_x, 6, HAIR_D)
    px(d, eye_x, 7, HAIR_D) if frame != 1 else px(d, eye_x, 6, OUTLINE)
    # 鼻子
    nose_x = 3 if not flip else 12
    px(d, nose_x, 7, SKIN_D)
    # 头发
    hair_x = range(12, 14) if not flip else range(2, 4)
    for x in hair_x:
        for y in range(4, 8):
            px(d, x, y, HAIR_D)
    # 身体
    for x in range(3, 13):
        for y in range(10, 16):
            px(d, x, y, SHIRT_L)
    for x in range(3, 13): px(d, x, 10, SHIRT_D)
    # 手臂前后
    arm_front = 2 if not flip else 13
    arm_back  = 13 if not flip else 2
    for y in range(10, 15):
        px(d, arm_front, y, SHIRT_L)
        px(d, arm_back, y, SHIRT_D)
    # 腿步动画
    leg_offset = [0, 2, -2][frame]
    for x in range(5, 11):
        for y in range(16, 22):
            px(d, x, y, PANTS_L)
    # 前腿偏移
    front_leg = range(5, 8) if not flip else range(8, 11)
    back_leg  = range(8, 11) if not flip else range(5, 8)
    for x in front_leg:
        for y in range(16, 22):
            px(d, x, y, PANTS_L)
        px(d, x, 22, SHOE)
    if frame != 0:
        for x in back_leg:
            shift = leg_offset
            for y in range(16, min(22, 22 + shift)):
                if 0 <= y + shift < H:
                    px(d, x, y, PANTS_D)
    result = img if not flip else img.transpose(Image.FLIP_LEFT_RIGHT)
    return result


def build_spritesheet() -> None:
    # 布局: 4行(DOWN/LEFT/RIGHT/UP) × 3列(帧0/1/2)
    sheet = Image.new("RGBA", (W * 3, H * 4), T)
    generators = [
        lambda f: draw_down(f),
        lambda f: draw_side(f, False),
        lambda f: draw_side(f, True),
        lambda f: draw_up(f),
    ]
    for row, gen in enumerate(generators):
        for col in range(3):
            frame_img = gen(col)
            sheet.paste(frame_img, (col * W, row * H))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_PATH)
    print(f"精灵表已生成: {OUT_PATH}  ({W*3}×{H*4}px, 4方向×3帧)")


if __name__ == "__main__":
    build_spritesheet()
