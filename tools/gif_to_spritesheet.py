#!/usr/bin/env python3
"""
GIF 战斗动画 → 精灵表 PNG 转换工具
来源：https://play.pokemonshowdown.com/sprites/ani/{英文名}.gif
输出：assets/sprites/animated/{front|back|shiny}/{编号}_sheet.png
      同目录下生成 {编号}_meta.json（帧数、帧宽、帧高、帧延迟）
"""

import os
import sys
import json
import math
import subprocess
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("缺少 Pillow，请先运行：pip install Pillow")

# 宝可梦编号 → Showdown 英文名映射（只列本项目用到的）
POKEMON_NAMES = {
    1:   "bulbasaur",
    2:   "ivysaur",
    3:   "venusaur",
    4:   "charmander",
    5:   "charmeleon",
    6:   "charizard",
    7:   "squirtle",
    8:   "wartortle",
    9:   "blastoise",
    25:  "pikachu",
    94:  "gengar",
    149: "dragonite",
    152: "chikorita",
    158: "totodile",
    498: "tepig",
    650: "chespin",
    653: "fennekin",
    656: "froakie",
    718: "zygarde",
}

BASE_FRONT  = "https://play.pokemonshowdown.com/sprites/ani/{name}.gif"
BASE_BACK   = "https://play.pokemonshowdown.com/sprites/ani-back/{name}.gif"
BASE_SHINY  = "https://play.pokemonshowdown.com/sprites/ani-shiny/{name}.gif"

GAME_ROOT = Path(__file__).parent.parent
OUT_BASE  = GAME_ROOT / "assets" / "sprites" / "animated"


UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"

def download(url: str, dest: Path) -> bool:
    result = subprocess.run(
        ["curl", "-s", "--max-time", "30", "-L", "-A", UA, url, "-o", str(dest)],
        capture_output=True
    )
    if result.returncode != 0 or not dest.exists() or dest.stat().st_size < 100:
        print(f"  下载失败 {url}")
        return False
    # 验证是 GIF
    header = dest.read_bytes()[:6]
    if header[:3] != b"GIF":
        print(f"  非 GIF 文件，跳过 {url}")
        dest.unlink(missing_ok=True)
        return False
    return True


def gif_to_sheet(gif_path: Path, out_png: Path, out_meta: Path) -> bool:
    try:
        img = Image.open(gif_path)
    except Exception as e:
        print(f"  无法打开 GIF {gif_path}: {e}")
        return False

    frames = []
    durations = []
    try:
        while True:
            frame = img.convert("RGBA")
            frames.append(frame.copy())
            durations.append(img.info.get("duration", 100))
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    if not frames:
        return False

    fw, fh = frames[0].size
    cols = math.ceil(math.sqrt(len(frames)))
    rows = math.ceil(len(frames) / cols)

    sheet = Image.new("RGBA", (fw * cols, fh * rows), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        x = (i % cols) * fw
        y = (i // cols) * fh
        sheet.paste(frame, (x, y))

    sheet.save(out_png)

    meta = {
        "frame_count": len(frames),
        "frame_width": fw,
        "frame_height": fh,
        "cols": cols,
        "rows": rows,
        "durations_ms": durations,
    }
    out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  → {out_png.name}  ({len(frames)}帧 {fw}×{fh})")
    return True


def process_pokemon(pokemon_id: int, name: str):
    tmp = Path(os.environ.get("TEMP", "/tmp"))

    variants = [
        ("front", BASE_FRONT.format(name=name),  OUT_BASE / "front"),
        ("back",  BASE_BACK.format(name=name),   OUT_BASE / "back"),
        ("shiny", BASE_SHINY.format(name=name),  OUT_BASE / "shiny"),
    ]

    for variant, url, out_dir in variants:
        out_dir.mkdir(parents=True, exist_ok=True)
        gif_tmp = tmp / f"{pokemon_id}_{variant}.gif"
        out_png  = out_dir / f"{pokemon_id}_sheet.png"
        out_meta = out_dir / f"{pokemon_id}_meta.json"

        print(f"  [{variant}] {url}")
        if not download(url, gif_tmp):
            continue
        gif_to_sheet(gif_tmp, out_png, out_meta)
        gif_tmp.unlink(missing_ok=True)


def main():
    ids = list(POKEMON_NAMES.keys())
    print(f"开始处理 {len(ids)} 只宝可梦 GIF 动画...")
    for pid in ids:
        name = POKEMON_NAMES[pid]
        print(f"\n#{pid:03d} {name}")
        process_pokemon(pid, name)
    print("\n全部完成。")


if __name__ == "__main__":
    main()
