class_name ProceduralMap
extends Node2D

# 地图参数
const TILE := 16  # 基础格子大小（像素）
const MAP_W := 40  # 地图宽（格数）
const MAP_H := 25  # 地图高（格数）

# 颜色定义
const COLOR_GROUND_A  := Color(0.22, 0.48, 0.22)
const COLOR_GROUND_B  := Color(0.20, 0.44, 0.20)
const COLOR_WALL      := Color(0.45, 0.35, 0.25)
const COLOR_WALL_TOP  := Color(0.60, 0.48, 0.32)
const COLOR_PATH      := Color(0.65, 0.58, 0.42)
const COLOR_WATER     := Color(0.20, 0.45, 0.75)
const COLOR_BUILDING  := Color(0.55, 0.42, 0.35)
const COLOR_ROOF      := Color(0.70, 0.30, 0.25)

# 地图数据：0=地面A 1=地面B 2=墙 3=小路 4=水 5=建筑 6=屋顶
var _map: Array = []

func _ready() -> void:
	_generate_map()
	_build_visuals()
	_build_collisions()

func _generate_map() -> void:
	# 初始化全部为地面A
	_map.resize(MAP_H)
	for y in MAP_H:
		_map[y] = []
		_map[y].resize(MAP_W)
		for x in MAP_W:
			_map[y][x] = (x + y) % 2  # 棋盘格地面

	# 外围墙壁
	for x in MAP_W:
		_map[0][x] = 2
		_map[MAP_H - 1][x] = 2
	for y in MAP_H:
		_map[y][0] = 2
		_map[y][MAP_W - 1] = 2

	# 中央十字小路
	var cx := MAP_W / 2
	var cy := MAP_H / 2
	for x in range(2, MAP_W - 2):
		_map[cy][x] = 3
		_map[cy - 1][x] = 3
	for y in range(2, MAP_H - 2):
		_map[y][cx] = 3
		_map[y][cx + 1] = 3

	# 左上建筑群
	_place_building(2, 2, 6, 4)
	_place_building(9, 2, 5, 4)

	# 右上建筑群
	_place_building(MAP_W - 8, 2, 6, 4)
	_place_building(MAP_W - 15, 2, 5, 3)

	# 左下建筑
	_place_building(2, MAP_H - 7, 7, 4)

	# 右下建筑
	_place_building(MAP_W - 9, MAP_H - 7, 7, 4)

	# 中央小广场（去掉路变成特殊地面）
	for y in range(cy - 2, cy + 3):
		for x in range(cx - 2, cx + 4):
			_map[y][x] = 3

	# 水池（左下角）
	for y in range(MAP_H - 6, MAP_H - 3):
		for x in range(11, 16):
			_map[y][x] = 4

func _place_building(bx: int, by: int, bw: int, bh: int) -> void:
	for y in range(by, by + bh):
		for x in range(bx, bx + bw):
			if y == by:
				_map[y][x] = 6  # 屋顶
			else:
				_map[y][x] = 5  # 建筑墙体（带碰撞）

func _build_visuals() -> void:
	var visuals := Node2D.new()
	visuals.name = "Visuals"
	add_child(visuals)

	for y in MAP_H:
		for x in MAP_W:
			var cell: int = _map[y][x]
			var color := _cell_color(cell)
			var poly := Polygon2D.new()
			poly.polygon = PackedVector2Array([
				Vector2(0, 0), Vector2(TILE, 0),
				Vector2(TILE, TILE), Vector2(0, TILE)
			])
			poly.color = color
			poly.position = Vector2(x * TILE, y * TILE)
			visuals.add_child(poly)

			# 墙顶高光
			if cell == 2:
				var top := Polygon2D.new()
				top.polygon = PackedVector2Array([
					Vector2(0, 0), Vector2(TILE, 0),
					Vector2(TILE, 3), Vector2(0, 3)
				])
				top.color = COLOR_WALL_TOP
				top.position = Vector2(x * TILE, y * TILE)
				visuals.add_child(top)

func _build_collisions() -> void:
	# 合并同行连续的墙块，减少碰撞体数量
	for y in MAP_H:
		var x := 0
		while x < MAP_W:
			var cell: int = _map[y][x]
			if _is_solid(cell):
				var start_x := x
				while x < MAP_W and _is_solid(_map[y][x]):
					x += 1
				_add_wall_body(start_x * TILE, y * TILE, (x - start_x) * TILE, TILE)
			else:
				x += 1

func _is_solid(cell: int) -> bool:
	return cell == 2 or cell == 5  # 墙和建筑有碰撞，屋顶/水无碰撞

func _add_wall_body(px: float, py: float, w: float, h: float) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 4   # WALL layer
	body.collision_mask = 0
	body.position = Vector2(px + w / 2.0, py + h / 2.0)
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(w, h)
	shape.shape = rect
	body.add_child(shape)
	add_child(body)

func _cell_color(cell: int) -> Color:
	match cell:
		0: return COLOR_GROUND_A
		1: return COLOR_GROUND_B
		2: return COLOR_WALL
		3: return COLOR_PATH
		4: return COLOR_WATER
		5: return COLOR_BUILDING
		6: return COLOR_ROOF
		_: return COLOR_GROUND_A

# 返回地图中心世界坐标（作为玩家出生点）
func get_spawn_position() -> Vector2:
	return Vector2(MAP_W / 2 * TILE, MAP_H / 2 * TILE)

# 返回地图世界边界
func get_bounds() -> Rect2:
	return Rect2(0, 0, MAP_W * TILE, MAP_H * TILE)
