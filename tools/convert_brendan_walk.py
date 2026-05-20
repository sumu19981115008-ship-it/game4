#!/usr/bin/env python3
"""
下载 pret/pokeemerald Brendan 行走精灵表并转换为项目格式
来源：绿宝石原版 GBA 像素图（pret 开源反编译仓库）
输出：assets/sprites/characters/player/calem_walk.png
格式：4行(DOWN/LEFT/RIGHT/UP) × 3列(帧0/1/2)，每帧16×32px，总48×128px
"""

import subprocess
import sys
import os
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit("pip install Pillow numpy")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
SRC_URL = "https://raw.githubusercontent.com/pret/pokeemerald/master/graphics/object_events/pics/people/brendan/walking.png"

GAME_ROOT = Path(__file__).parent.parent
OUT_PATH  = GAME_ROOT / "assets" / "sprites" / "characters" / "player" / "calem_walk.png"
TMP       = Path(os.environ.get("TEMP", "/tmp")) / "brendan_walk_src.png"

# 原始精灵表帧映射（144×32，9帧横排，每帧16×32）
# 原图布局: [下0, 下1, 下2, 上0, 上1, 上2, 左0, 左1, 左2]
SRC_FRAME_ORDER = {
    "down":  [0, 1, 2],
    "up":    [3, 4, 5],
    "left":  [6, 7, 8],
    # right = left 水平翻转
}

FW, FH = 16, 32  # 每帧尺寸


def download_src() -> Image.Image:
    result = subprocess.run(
        ["curl", "-s", "--max-time", "20", "-L", "-A", UA, SRC_URL, "-o", str(TMP)],
        capture_output=True
    )
    if result.returncode != 0 or not TMP.exists():
        sys.exit(f"下载失败: {SRC_URL}")
    img = Image.open(TMP).convert("RGBA")
    print(f"原图下载成功: {img.size}")
    return img


def remove_background(img: Image.Image) -> Image.Image:
    arr = np.array(img)
    bg = tuple(arr[0, 0, :3])
    mask = (arr[:, :, 0] == bg[0]) & (arr[:, :, 1] == bg[1]) & (arr[:, :, 2] == bg[2])
    arr[mask, 3] = 0
    print(f"背景色 RGB{bg} 已去除")
    return Image.fromarray(arr)


def extract_frame(img: Image.Image, index: int) -> Image.Image:
    return img.crop((index * FW, 0, (index + 1) * FW, FH))


def build_spritesheet(img: Image.Image) -> Image.Image:
    # 输出布局：4行(DOWN/LEFT/RIGHT/UP) × 3列
    sheet = Image.new("RGBA", (FW * 3, FH * 4), (0, 0, 0, 0))

    directions = ["down", "left", "right", "up"]
    for row, dir_name in enumerate(directions):
        if dir_name == "right":
            src_frames = SRC_FRAME_ORDER["left"]
            flip = True
        else:
            src_frames = SRC_FRAME_ORDER[dir_name]
            flip = False
        for col, src_idx in enumerate(src_frames):
            frame = extract_frame(img, src_idx)
            if flip:
                frame = frame.transpose(Image.FLIP_LEFT_RIGHT)
            sheet.paste(frame, (col * FW, row * FH))
        print(f"  行{row} {dir_name}: 帧{src_frames}{' (翻转)' if flip else ''}")

    return sheet


def main():
    print("=== Brendan 行走精灵转换 ===")
    src_img = download_src()
    src_img = remove_background(src_img)
    sheet = build_spritesheet(src_img)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_PATH)
    print(f"\n输出: {OUT_PATH}  ({sheet.width}×{sheet.height}px)")
    TMP.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
