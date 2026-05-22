class_name TileMapZone
extends Node2D

# 地图参数（与 ProceduralMap 保持一致，可无缝替换）
const TILE := 16           # 世界格子大小（像素）— 2×GBA原始8px
const MAP_W := 40
const MAP_H := 25

# GBA 原始图块尺寸
const SRC_TILE := 8

# 地图图块集 Atlas 中使用的图块坐标（primary_general/tiles.png）
# 图块排列：16列 × 32行，从左到右、从上到下编号
# 这里只取最常用的几行（0~3行）做初步对应，后续可在编辑器细调
const TILE_GRASS_A   := Vector2i(0, 0)   # 浅草
const TILE_GRASS_B   := Vector2i(1, 0)   # 深草（棋盘格副色）
const TILE_PATH      := Vector2i(4, 0)   # 小路
const TILE_WATER     := Vector2i(8, 0)   # 水面
const TILE_WALL      := Vector2i(0, 8)   # 外墙 / 岩石
const TILE_BUILDING  := Vector2i(2, 4)   # 建筑墙体
const TILE_ROOF      := Vector2i(2, 2)   # 屋顶

# 地图数据类型常量（与 ProceduralMap 一致）
const T_GRASS_A  := 0
const T_GRASS_B  := 1
const T_WALL     := 2
const T_PATH     := 3
const T_WATER    := 4
const T_BUILDING := 5
const T_ROOF     := 6

var _map: Array = []
var _tilemap: TileMap

func _ready() -> void:
	_generate_map()
	_build_tilemap()
	_build_collisions()

# ── 地图数据生成（逻辑与 ProceduralMap 完全相同）──────────────────────────

func _generate_map() -> void:
	_map.resize(MAP_H)
	for y in MAP_H:
		_map[y] = []
		_map[y].resize(MAP_W)
		for x in MAP_W:
			_map[y][x] = (x + y) % 2

	for x in MAP_W:
		_map[0][x] = T_WALL
		_map[MAP_H - 1][x] = T_WALL
	for y in MAP_H:
		_map[y][0] = T_WALL
		_map[y][MAP_W - 1] = T_WALL

	var cx := MAP_W / 2
	var cy := MAP_H / 2
	for x in range(2, MAP_W - 2):
		_map[cy][x] = T_PATH
		_map[cy - 1][x] = T_PATH
	for y in range(2, MAP_H - 2):
		_map[y][cx] = T_PATH
		_map[y][cx + 1] = T_PATH

	_place_building(2, 2, 6, 4)
	_place_building(9, 2, 5, 4)
	_place_building(MAP_W - 8, 2, 6, 4)
	_place_building(MAP_W - 15, 2, 5, 3)
	_place_building(2, MAP_H - 7, 7, 4)
	_place_building(MAP_W - 9, MAP_H - 7, 7, 4)

	for y in range(cy - 2, cy + 3):
		for x in range(cx - 2, cx + 4):
			_map[y][x] = T_PATH

	for y in range(MAP_H - 6, MAP_H - 3):
		for x in range(11, 16):
			_map[y][x] = T_WATER

func _place_building(bx: int, by: int, bw: int, bh: int) -> void:
	for y in range(by, by + bh):
		for x in range(bx, bx + bw):
			_map[y][x] = T_ROOF if y == by else T_BUILDING

# ── TileMap 构建 ──────────────────────────────────────────────────────────

func _build_tilemap() -> void:
	var tex: Texture2D = load("res://assets/tilesets/primary_general/tiles_rgba.png")
	if not tex:
		push_error("TileMapZone: 无法加载 primary_general/tiles.png")
		_fallback_procedural()
		return

	# 创建 TileSet
	var ts := TileSet.new()
	ts.tile_size = Vector2i(TILE, TILE)

	# 物理碰撞层（WALL layer = bit2 = 4）
	ts.add_physics_layer(0)
	ts.set_physics_layer_collision_layer(0, 4)
	ts.set_physics_layer_collision_mask(0, 0)

	# Atlas Source：将 8×8 原始图块 2× 拉伸到 16×16 世界格
	var src := TileSetAtlasSource.new()
	src.texture = tex
	# tiles_rgba.png 已经 2× 放大（8px→16px），直接用 TILE 尺寸
	src.texture_region_size = Vector2i(TILE, TILE)

	# 注册所有用到的图块坐标
	var used_coords: Array[Vector2i] = [
		TILE_GRASS_A, TILE_GRASS_B, TILE_PATH,
		TILE_WATER, TILE_WALL, TILE_BUILDING, TILE_ROOF
	]
	for coord in used_coords:
		if not src.has_tile(coord):
			src.create_tile(coord)

	# 为有碰撞的图块添加全格碰撞形状
	for coord in [TILE_WALL, TILE_BUILDING]:
		var td: TileData = src.get_tile_data(coord, 0)
		if td:
			var shape := RectangleShape2D.new()
			shape.size = Vector2(TILE, TILE)
			td.add_collision_polygon(0)
			td.set_collision_polygon_points(
				0, 0,
				PackedVector2Array([
					Vector2(-TILE / 2.0, -TILE / 2.0),
					Vector2( TILE / 2.0, -TILE / 2.0),
					Vector2( TILE / 2.0,  TILE / 2.0),
					Vector2(-TILE / 2.0,  TILE / 2.0),
				])
			)

	ts.add_source(src, 0)

	# 创建 TileMap（单层：ground）
	_tilemap = TileMap.new()
	_tilemap.name = "TileMap"
	_tilemap.tile_set = ts
	_tilemap.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	# tiles_rgba.png 已预先 2× 放大，scale 保持 1:1
	add_child(_tilemap)

	# 铺地图
	for y in MAP_H:
		for x in MAP_W:
			var cell: int = _map[y][x]
			var atlas_coord := _cell_to_atlas(cell)
			# TileMap 坐标用 SRC_TILE 单位，scale 已 ×2，所以格子坐标不变
			_tilemap.set_cell(0, Vector2i(x, y), 0, atlas_coord)

	print("TileMapZone: TileMap 构建完成 (%d × %d 格)" % [MAP_W, MAP_H])

func _cell_to_atlas(cell: int) -> Vector2i:
	match cell:
		T_GRASS_A:  return TILE_GRASS_A
		T_GRASS_B:  return TILE_GRASS_B
		T_PATH:     return TILE_PATH
		T_WATER:    return TILE_WATER
		T_WALL:     return TILE_WALL
		T_BUILDING: return TILE_BUILDING
		T_ROOF:     return TILE_ROOF
		_:          return TILE_GRASS_A

# ── 碰撞体（TileData 里的碰撞多边形已处理墙体，这里补静态 NPC 不可走边界）──

func _build_collisions() -> void:
	# TileMap 自身会处理 WALL/BUILDING 碰撞，
	# 此函数保留以便将来添加额外触发区域
	pass

# ── 回退：TileMap 失败时退化为颜色色块（与 ProceduralMap 相同逻辑）─────────

func _fallback_procedural() -> void:
	push_warning("TileMapZone: 退回程序化色块地图")
	var colors := [
		Color(0.22, 0.48, 0.22), Color(0.20, 0.44, 0.20),
		Color(0.45, 0.35, 0.25), Color(0.65, 0.58, 0.42),
		Color(0.20, 0.45, 0.75), Color(0.55, 0.42, 0.35),
		Color(0.70, 0.30, 0.25),
	]
	var visuals := Node2D.new()
	visuals.name = "Visuals"
	add_child(visuals)
	for y in MAP_H:
		for x in MAP_W:
			var poly := Polygon2D.new()
			poly.polygon = PackedVector2Array([
				Vector2(0, 0), Vector2(TILE, 0),
				Vector2(TILE, TILE), Vector2(0, TILE)
			])
			poly.color = colors[_map[y][x]]
			poly.position = Vector2(x * TILE, y * TILE)
			visuals.add_child(poly)

	_build_fallback_collisions()

func _build_fallback_collisions() -> void:
	for y in MAP_H:
		var x := 0
		while x < MAP_W:
			var cell: int = _map[y][x]
			if cell == T_WALL or cell == T_BUILDING:
				var sx := x
				while x < MAP_W and (_map[y][x] == T_WALL or _map[y][x] == T_BUILDING):
					x += 1
				var body := StaticBody2D.new()
				body.collision_layer = 4
				body.collision_mask = 0
				body.position = Vector2((sx + x) / 2.0 * TILE, (y + 0.5) * TILE)
				var shape := CollisionShape2D.new()
				var rect := RectangleShape2D.new()
				rect.size = Vector2((x - sx) * TILE, TILE)
				shape.shape = rect
				body.add_child(shape)
				add_child(body)
			else:
				x += 1

# ── 公共接口（与 ProceduralMap 相同，TestZone 无需改动）─────────────────────

func get_spawn_position() -> Vector2:
	return Vector2(MAP_W / 2 * TILE, MAP_H / 2 * TILE)

func get_bounds() -> Rect2:
	return Rect2(0, 0, MAP_W * TILE, MAP_H * TILE)
