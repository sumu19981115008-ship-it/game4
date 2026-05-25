#!/usr/bin/env python3
"""
生成 primary_general metatile 预览图（放大3倍，带编号）。
输出：assets/maps/preview_general_metatiles.png
"""
import urllib.request, struct
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw

GAME_ROOT = Path(__file__).parent.parent
GEN_DIR   = GAME_ROOT / 'assets/tilesets/primary_general'
OUT_PNG   = GAME_ROOT / 'assets/maps/preview_general_metatiles.png'
CACHE     = Path(__file__).parent / '_gen_meta.bin'
BASE_URL  = 'https://raw.githubusercontent.com/pret/pokeemerald/master'
TILE_PX   = 8
META_PX   = 16
COLS      = 16

def dl(url):
    return urllib.request.urlopen(url, timeout=15).read()

def parse_pal(path):
    colors = []
    with open(path, 'r', errors='replace') as f:
        for line in f.readlines()[3:]:
            parts = line.split()
            if len(parts) == 3:
                try: colors.append(tuple(int(x) for x in parts))
                except: pass
    return (colors + [(0,0,0)]*16)[:16]

def load_pals(d):
    return [parse_pal(d/'palettes'/f'{i:02d}.pal')
            if (d/'palettes'/f'{i:02d}.pal').exists()
            else [(0,0,0)]*16 for i in range(16)]

def get_tile_rgba(arr, cols, idx, hflip, vflip, ps, combined, is_bottom=False):
    tx = (idx%cols)*TILE_PX; ty = (idx//cols)*TILE_PX
    if ty+TILE_PX>arr.shape[0] or tx+TILE_PX>arr.shape[1]:
        return np.full((TILE_PX,TILE_PX,4),[80,80,80,255],dtype=np.uint8)
    block = arr[ty:ty+TILE_PX, tx:tx+TILE_PX]
    rgba = np.zeros((TILE_PX,TILE_PX,4),dtype=np.uint8)
    for py in range(TILE_PX):
        for px in range(TILE_PX):
            li = int(block[py,px]) % 16
            ci = ps*16+li
            r,g,b = combined[ci] if ci<len(combined) else (0,0,0)
            is_mag = (r==255 and g==0 and b==255)
            if li==0: alpha=0
            elif is_mag:
                if is_bottom:
                    for d in range(1,16):
                        ci2=ps*16+((li+d)%16)
                        if ci2<len(combined):
                            rr,gg,bb=combined[ci2]
                            if not(rr==255 and gg==0 and bb==255):
                                r,g,b=rr,gg,bb; break
                    alpha=255
                else: alpha=0
            else: alpha=255
            rgba[py,px]=[r,g,b,alpha]
    if hflip: rgba=rgba[:,::-1,:]
    if vflip: rgba=rgba[::-1,:,:]
    return rgba

def render_meta(i, meta_raw, arr, cols, combined):
    off = i*16
    if off+16>len(meta_raw): return np.zeros((META_PX,META_PX,4),dtype=np.uint8)
    entries = struct.unpack_from('<8H',meta_raw,off)
    canvas = np.zeros((META_PX,META_PX,4),dtype=np.uint8)
    for layer in range(2):
        for sub in range(4):
            e=entries[layer*4+sub]
            tidx=e&0x3FF; hflip=bool(e&0x400); vflip=bool(e&0x800); ps=(e>>12)&0xF
            px=(sub%2)*TILE_PX; py=(sub//2)*TILE_PX
            tile=get_tile_rgba(arr,cols,tidx,hflip,vflip,ps,combined,layer==0)
            if layer==0:
                canvas[py:py+TILE_PX,px:px+TILE_PX]=tile
            else:
                mask=tile[:,:,3]>0
                for ch in range(4):
                    canvas[py:py+TILE_PX,px:px+TILE_PX,ch][mask]=tile[:,:,ch][mask]
    return canvas

CELL = META_PX*3+14

def main():
    if CACHE.exists():
        print(f'使用缓存 {CACHE.name}')
        meta_raw = CACHE.read_bytes()
    else:
        print('下载 primary_general metatiles.bin...')
        meta_raw = dl(f'{BASE_URL}/data/tilesets/primary/general/metatiles.bin')
        CACHE.write_bytes(meta_raw)

    pals = load_pals(GEN_DIR)
    combined = []
    for n in range(16):
        combined.extend(pals[n][:16])

    img_src = Image.open(GEN_DIR/'tiles.png')
    arr = np.array(img_src)
    cols = img_src.width // TILE_PX

    total = len(meta_raw)//16
    print(f'primary_general: {total} 个metatile')

    rows = (total+COLS-1)//COLS
    out = Image.new('RGB',(COLS*CELL, rows*CELL),(30,30,30))
    draw = ImageDraw.Draw(out)

    for i in range(total):
        tile = render_meta(i, meta_raw, arr, cols, combined)
        rgb = np.where(tile[:,:,3:4]>0, tile[:,:,:3], np.full_like(tile[:,:,:3],50))
        t_img = Image.fromarray(rgb.astype(np.uint8),'RGB').resize((META_PX*3,META_PX*3),Image.NEAREST)
        cx=(i%COLS)*CELL+1; cy=(i//COLS)*CELL+1
        out.paste(t_img,(cx,cy))
        draw.text((cx, cy+META_PX*3+1), str(i), fill=(200,200,100))

    out.save(OUT_PNG)
    print(f'已保存：{OUT_PNG}（{out.width}×{out.height}px）')

if __name__=='__main__':
    main()
