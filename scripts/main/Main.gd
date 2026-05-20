class_name Main
extends Node

func _ready() -> void:
	_ensure_save_dir()
	# 开发阶段直接跳转测试地图，deferred 避免在 _ready 中修改场景树
	get_tree().change_scene_to_file.call_deferred("res://scenes/world/zones/TestZone.tscn")

func _ensure_save_dir() -> void:
	var dir := DirAccess.open("user://")
	if dir and not dir.dir_exists("saves"):
		DirAccess.make_dir_recursive_absolute("user://saves")
