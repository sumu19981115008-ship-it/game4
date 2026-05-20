class_name TestZone
extends Node2D

@onready var debug_label: Label = $DebugCanvas/DebugLabel
@onready var proc_map: ProceduralMap = $ProceduralMap

var _player: CharacterBody2D

func _ready() -> void:
	_player = get_tree().get_first_node_in_group("player") as CharacterBody2D
	if _player:
		_player.global_position = proc_map.get_spawn_position()
		var bounds := proc_map.get_bounds()
		var cam: Camera2D = _player.get_node("PlayerCamera")
		cam.set_boundary(
			int(bounds.position.x),
			int(bounds.end.x),
			int(bounds.position.y),
			int(bounds.end.y)
		)
	else:
		debug_label.text = "错误：player 节点未找到"

func _process(_delta: float) -> void:
	if _player:
		debug_label.text = "位置:(%.0f,%.0f) | WASD移动 Shift奔跑" % [
			_player.global_position.x,
			_player.global_position.y
		]
