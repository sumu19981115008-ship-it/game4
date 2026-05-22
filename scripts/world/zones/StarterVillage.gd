class_name StarterVillage
extends Node2D

const TILE       := 16
const MAP_W      := 22
const MAP_H      := 20
const MAP_IMG    := "res://assets/maps/starter_village.png"
const MAP_JSON   := "res://assets/maps/starter_village.json"

const SPAWN_X    := 10
const SPAWN_Y    := 16

var _map_data: Dictionary = {}

func _ready() -> void:
	_load_map_data()
	_build_background()
	_build_collisions()
	_setup_player()

func _load_map_data() -> void:
	var file := FileAccess.open(MAP_JSON, FileAccess.READ)
	if not file:
		push_error("StarterVillage: 无法读取 " + MAP_JSON)
		return
	_map_data = JSON.parse_string(file.get_as_text())
	file.close()

func _build_background() -> void:
	var tex: Texture2D = load(MAP_IMG)
	if not tex:
		push_error("StarterVillage: 无法加载 " + MAP_IMG)
		return
	var sprite := Sprite2D.new()
	sprite.name          = "Background"
	sprite.texture       = tex
	sprite.centered      = false
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(sprite)

func _build_collisions() -> void:
	if not _map_data.has("collision"):
		push_warning("StarterVillage: 无碰撞数据，使用默认边框")
		_build_default_border()
		return

	var coll: Array = _map_data["collision"]
	var wall_count := 0
	for row in MAP_H:
		var col := 0
		while col < MAP_W:
			if row < coll.size() and col < coll[row].size() and coll[row][col] == 1:
				var start := col
				while col < MAP_W and row < coll.size() and col < coll[row].size() and coll[row][col] == 1:
					col += 1
				_add_wall(start * TILE, row * TILE, (col - start) * TILE, TILE)
				wall_count += 1
			else:
				col += 1
	print("StarterVillage: 碰撞体创建完成，共 %d 个" % wall_count)

func _add_wall(px: float, py: float, w: float, h: float) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 4
	body.collision_mask  = 0
	body.position = Vector2(px + w * 0.5, py + h * 0.5)
	var shape := CollisionShape2D.new()
	var rect  := RectangleShape2D.new()
	rect.size  = Vector2(w, h)
	shape.shape = rect
	body.add_child(shape)
	add_child(body)

func _build_default_border() -> void:
	_add_wall(0,                   0,                   MAP_W * TILE, TILE)
	_add_wall(0,                   (MAP_H-1) * TILE,    MAP_W * TILE, TILE)
	_add_wall(0,                   0,                   TILE,         MAP_H * TILE)
	_add_wall((MAP_W-1) * TILE,    0,                   TILE,         MAP_H * TILE)

func _setup_player() -> void:
	var player = get_tree().get_first_node_in_group("player")
	if not player:
		return

	var pending := WorldStateManager.pending_spawn_pos
	if pending.x >= 0 and pending.y >= 0:
		player.global_position = Vector2((pending.x + 0.5) * TILE, (pending.y + 0.5) * TILE)
		WorldStateManager.pending_spawn_pos = Vector2(-1, -1)
	else:
		var sx: int = SPAWN_X
		var sy: int = SPAWN_Y
		if _map_data.has("spawn"):
			sx = _map_data["spawn"]["x"]
			sy = _map_data["spawn"]["y"]
		player.global_position = Vector2((sx + 0.5) * TILE, (sy + 0.5) * TILE)

	var cam: Camera2D = player.get_node_or_null("PlayerCamera")
	if cam:
		cam.set_boundary(MAP_W * TILE, MAP_H * TILE)

func get_spawn_position() -> Vector2:
	var sx: int = SPAWN_X
	var sy: int = SPAWN_Y
	if _map_data.has("spawn"):
		sx = _map_data["spawn"]["x"]
		sy = _map_data["spawn"]["y"]
	return Vector2((sx + 0.5) * TILE, (sy + 0.5) * TILE)

func get_bounds() -> Rect2:
	return Rect2(0, 0, MAP_W * TILE, MAP_H * TILE)
