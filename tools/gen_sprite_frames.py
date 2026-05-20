#!/usr/bin/env python3
"""
根据 animated/{variant}/{id}_meta.json 生成 Godot 4 SpriteFrames .tres 文件
输出：assets/sprites/animated/{variant}/{id}_frames.tres
用法：python3 tools/gen_sprite_frames.py
"""

import json
import math
from pathlib import Path

GAME_ROOT = Path(__file__).parent.parent
ANIM_BASE = GAME_ROOT / "assets" / "sprites" / "animated"
VARIANTS = ["front", "back", "shiny"]

# 动画名称对应 variant
ANIM_NAMES = {
    "front": "battle_front",
    "back":  "battle_back",
    "shiny": "battle_shiny",
}


def gen_tres(pokemon_id: int, variant: str, meta: dict) -> str:
    sheet_res_path = f"res://assets/sprites/animated/{variant}/{pokemon_id}_sheet.png"
    frame_count: int = meta["frame_count"]
    fw: int = meta["frame_width"]
    fh: int = meta["frame_height"]
    cols: int = meta["cols"]
    durations: list = meta["durations_ms"]
    anim_name: str = ANIM_NAMES[variant]

    lines = []
    # load_steps = 1(SpriteFrames脚本) + frame_count 个 AtlasTexture + 1 个 Texture2D
    load_steps = frame_count + 2
    lines.append(f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3]')
    lines.append("")

    # 精灵表纹理资源
    lines.append(f'[ext_resource type="Texture2D" path="{sheet_res_path}" id="1_sheet"]')
    lines.append("")

    # 每帧 AtlasTexture 子资源
    for i in range(frame_count):
        col = i % cols
        row = i // cols
        x = col * fw
        y = row * fh
        sub_id = i + 2
        lines.append(f'[sub_resource type="AtlasTexture" id="AtlasTexture_{sub_id}"]')
        lines.append(f'atlas = ExtResource("1_sheet")')
        lines.append(f'region = Rect2({x}, {y}, {fw}, {fh})')
        lines.append("")

    # SpriteFrames 主资源
    lines.append('[resource]')
    lines.append('animations = [{')
    lines.append(f'"frames": [')
    for i in range(frame_count):
        sub_id = i + 2
        dur_sec = durations[i] / 1000.0
        comma = "," if i < frame_count - 1 else ""
        lines.append(f'{{"duration": {dur_sec:.4f}, "texture": SubResource("AtlasTexture_{sub_id}")}}{comma}')
    lines.append('],')
    lines.append(f'"loop": true,')
    lines.append(f'"name": &"{anim_name}",')
    lines.append(f'"speed": 1.0')
    lines.append('}]')

    return "\n".join(lines) + "\n"


def main():
    total = 0
    for variant in VARIANTS:
        variant_dir = ANIM_BASE / variant
        if not variant_dir.exists():
            continue
        for meta_file in sorted(variant_dir.glob("*_meta.json")):
            pokemon_id = int(meta_file.stem.split("_")[0])
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            out_path = variant_dir / f"{pokemon_id}_frames.tres"
            out_path.write_text(gen_tres(pokemon_id, variant, meta), encoding="utf-8")
            print(f"  {out_path.name}  ({meta['frame_count']}帧)")
            total += 1
    print(f"\n共生成 {total} 个 SpriteFrames .tres 文件")


if __name__ == "__main__":
    main()
