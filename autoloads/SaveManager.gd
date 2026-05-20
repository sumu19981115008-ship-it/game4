extends Node

const SAVE_DIR := "user://saves/"
const AUTOSAVE_PATH := "user://saves/autosave.json"
const META_PATH := "user://saves/save_meta.json"
const SAVE_VERSION := "1.0"

var current_save_slot: int = -1

func _ready() -> void:
	_ensure_save_dir()

func _ensure_save_dir() -> void:
	if not DirAccess.dir_exists_absolute(SAVE_DIR):
		DirAccess.make_dir_recursive_absolute(SAVE_DIR)

func save_to_slot(slot: int) -> bool:
	var data := _collect_game_state()
	data["save_slot"] = slot
	data["save_time"] = Time.get_datetime_string_from_system()
	data["version"] = SAVE_VERSION
	var json_str := JSON.stringify(data, "\t")
	var file := FileAccess.open(SAVE_DIR + "save_slot_%d.json" % slot, FileAccess.WRITE)
	if file == null:
		push_error("存档失败：无法写入文件 slot %d" % slot)
		return false
	file.store_string(json_str)
	_update_meta(slot, data)
	current_save_slot = slot
	EventBus.save_completed.emit(slot)
	return true

func load_from_slot(slot: int) -> bool:
	var path := SAVE_DIR + "save_slot_%d.json" % slot
	if not FileAccess.file_exists(path):
		push_warning("存档槽 %d 不存在" % slot)
		return false
	var file := FileAccess.open(path, FileAccess.READ)
	var json := JSON.new()
	if json.parse(file.get_as_text()) != OK:
		push_error("读档失败：JSON解析错误")
		return false
	_apply_game_state(json.data)
	current_save_slot = slot
	EventBus.load_completed.emit(slot)
	return true

func autosave() -> void:
	var data := _collect_game_state()
	data["save_time"] = Time.get_datetime_string_from_system()
	data["version"] = SAVE_VERSION
	var file := FileAccess.open(AUTOSAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(data, "\t"))
	EventBus.autosave_completed.emit()

func slot_exists(slot: int) -> bool:
	return FileAccess.file_exists(SAVE_DIR + "save_slot_%d.json" % slot)

func get_save_meta() -> Dictionary:
	if not FileAccess.file_exists(META_PATH):
		return {}
	var file := FileAccess.open(META_PATH, FileAccess.READ)
	var json := JSON.new()
	if json.parse(file.get_as_text()) != OK:
		return {}
	return json.data

func _collect_game_state() -> Dictionary:
	var data: Dictionary = {}
	data["flags"] = FlagManager.get_save_data()
	data["world_state"] = WorldStateManager.get_save_data()
	# 玩家位置由 PlayerManager 提供（战斗外）
	var player := get_tree().get_first_node_in_group("player")
	if player:
		data["player_position"] = {"x": player.global_position.x, "y": player.global_position.y}
		data["current_scene"] = get_tree().current_scene.scene_file_path
	return data

func _apply_game_state(data: Dictionary) -> void:
	if data.has("flags"):
		FlagManager.load_save_data(data["flags"])
	if data.has("world_state"):
		WorldStateManager.load_save_data(data["world_state"])

func _update_meta(slot: int, data: Dictionary) -> void:
	var meta := get_save_meta()
	if not meta.has("slots"):
		meta["slots"] = [{}, {}, {}]
	meta["slots"][slot] = {
		"slot": slot,
		"exists": true,
		"save_time": data.get("save_time", ""),
		"chapter": FlagManager.get_flag("ch5_complete", false) if FlagManager.get_flag("ch5_complete", false) else 1,
		"preview_scene": data.get("current_scene", ""),
	}
	var file := FileAccess.open(META_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(meta, "\t"))
