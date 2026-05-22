#!/usr/bin/env python3
"""
为 assets/tilesets/ 下每个图块集生成彩色预览图。

GBA 图块集使用调色板模式（mode=P），每个图块集目录含：
  - tiles.png        原始像素（索引色，128px 宽，8×8 图块）
  - palettes/00~15.pal  16个调色板，每个16色（JASC-PAL格式）

本脚本将16个调色板合并为256色调色板应用到 tiles.png，
输出放大预览图到 assets/tilesets/<名称>/preview.png。

最后生成一张汇总图 assets/tilesets/_all_preview.png。

用法：
    python3 tools/preview_tilesets.py
"""

from pathlib import Path
from PIL import Image, ImageDraw
import sys

GAME_ROOT = Path(__file__).parent.parent
TILESETS_DIR = GAME_ROOT / "assets" / "tilesets"
SCALE = 4        # 放大倍数（8px图块 → 32px，看得清楚）
LABEL_H = 16     # 底部标签高度
COLS = 3         # 汇总图每行列数


def load_palette(pal_dir: Path) -> list[tuple[int, int, int]]:
    """合并16个 JASC-PAL 调色板为256色列表。"""
    full = []
    for i in range(16):
        path = pal_dir / f"{i:02d}.pal"
        if path.exists():
            colors = parse_jasc_pal(path)
            full.extend(colors[:16])
        else:
            full.extend([(0, 0, 0)] * 16)
    return full[:256]


def parse_jasc_pal(path: Path) -> list[tuple[int, int, int]]:
    """解析 JASC-PAL 文本文件，返回 RGB 元组列表。"""
    colors = []
    with open(path, "r", errors="replace") as f:
        lines = [l.strip() for l in f.readlines()]
    # 格式：JASC-PAL / 0100 / 色数 / R G B ...
    for line in lines[3:]:
        parts = line.split()
        if len(parts) == 3:
            try:
                colors.append((int(parts[0]), int(parts[1]), int(parts[2])))
            except ValueError:
                pass
    return colors


def palette_to_bytes(palette: list[tuple[int, int, int]]) -> bytes:
    result = []
    for r, g, b in palette:
        result.extend([r, g, b])
    while len(result) < 768:
        result.extend([0, 0, 0])
    return bytes(result)


def colorize(tiles_path: Path, pal_dir: Path) -> Image.Image:
    """将调色板应用到索引色图像，返回 RGBA 图像。"""
    img = Image.open(tiles_path)
    if img.mode != "P":
        return img.convert("RGBA")
    palette = load_palette(pal_dir)
    img.putpalette(palette_to_bytes(palette))
    return img.convert("RGBA")


def make_preview(tileset_dir: Path) -> Image.Image | None:
    tiles_path = tileset_dir / "tiles.png"
    pal_dir = tileset_dir / "palettes"
    if not tiles_path.exists():
        print(f"  [跳过] 未找到 tiles.png: {tileset_dir.name}")
        return None

    img = colorize(tiles_path, pal_dir)

    # 缩放
    w, h = img.width * SCALE, img.height * SCALE
    big = img.resize((w, h), Image.NEAREST)

    # 加底部标签
    canvas = Image.new("RGBA", (w, h + LABEL_H), (20, 20, 20, 255))
    canvas.paste(big, (0, 0), big)
    draw = ImageDraw.Draw(canvas)
    draw.text((4, h + 2), tileset_dir.name, fill=(255, 220, 80, 255))

    out_path = tileset_dir / "preview.png"
    canvas.save(out_path)
    print(f"  [OK] {tileset_dir.name}/preview.png  ({img.width}×{img.height} → {w}×{h}px)")
    return canvas


def make_summary(previews: list[tuple[str, Image.Image]]) -> None:
    if not previews:
        return

    max_w = max(img.width for _, img in previews)
    max_h = max(img.height for _, img in previews)
    rows = (len(previews) + COLS - 1) // COLS
    PAD = 8

    canvas_w = COLS * (max_w + PAD) + PAD
    canvas_h = rows * (max_h + PAD) + PAD
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (15, 15, 15, 255))

    for i, (name, img) in enumerate(previews):
        col = i % COLS
        row = i // COLS
        x = PAD + col * (max_w + PAD)
        y = PAD + row * (max_h + PAD)
        canvas.paste(img, (x, y), img)

    out_path = TILESETS_DIR / "_all_preview.png"
    canvas.save(out_path)
    print(f"\n汇总图: {out_path}  ({canvas.width}×{canvas.height}px)")


def main():
    try:
        from PIL import Image
    except ImportError:
        sys.exit("缺少依赖：pip install Pillow")

    if not TILESETS_DIR.exists():
        sys.exit(f"目录不存在：{TILESETS_DIR}")

    tileset_dirs = sorted(
        d for d in TILESETS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )

    if not tileset_dirs:
        sys.exit("未找到任何图块集子目录")

    print(f"找到 {len(tileset_dirs)} 个图块集，开始生成预览...\n")

    previews = []
    for d in tileset_dirs:
        preview = make_preview(d)
        if preview:
            previews.append((d.name, preview))

    make_summary(previews)
    print(f"\n完成：{len(previews)}/{len(tileset_dirs)} 个预览图已生成")


if __name__ == "__main__":
    main()
