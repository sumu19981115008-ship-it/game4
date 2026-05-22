class_name TestZone
extends Node2D

@onready var debug_label: Label = $DebugCanvas/DebugLabel
@onready var proc_map: TileMapZone = $TileMapZone

var _player: CharacterBody2D

func _ready() -> void:
	_player = get_tree().get_first_node_in_group("player") as CharacterBody2D
	if _player:
		_player.global_position = proc_map.get_spawn_position()
		var bounds := proc_map.get_bounds()
		var cam: Camera2D = _player.get_node("PlayerCamera")
		cam.set_boundary(int(bounds.size.x), int(bounds.size.y))
	else:
		debug_label.text = "错误：player 节点未找到"
	_spawn_pikachu_preview()

func _process(_delta: float) -> void:
	if _player:
		debug_label.text = "位置:(%.0f,%.0f) | WASD移动 Shift奔跑" % [
			_player.global_position.x,
			_player.global_position.y
		]

func _spawn_pikachu_preview() -> void:
	var tex: Texture2D = PokemonDatabase.get_sprite_texture(25)
	if not tex:
		push_warning("皮卡丘精灵图未找到，跳过视觉验证")
		return
	var sprite := Sprite2D.new()
	sprite.texture = tex
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.scale = Vector2(2.0, 2.0)
	sprite.position = proc_map.get_spawn_position() + Vector2(40, 0)
	add_child(sprite)
