class_name Main
extends Node

func _ready() -> void:
	_ensure_save_dir()
	# 开发阶段直接跳转起始场景
	call_deferred("_load_start_scene")

func _load_start_scene() -> void:
	get_tree().change_scene_to_file("res://scenes/world/zones/StarterVillage.tscn")

func _ensure_save_dir() -> void:
	var dir := DirAccess.open("user://")
	if dir and not dir.dir_exists("saves"):
		DirAccess.make_dir_recursive_absolute("user://saves")
