extends Node

var _move_cache: Dictionary = {}

func _ready() -> void:
	_load_all_moves()

func _load_all_moves() -> void:
	var dir := DirAccess.open("res://data/moves/db/")
	if not dir:
		push_warning("技能数据库目录不存在，跳过加载")
		return
	dir.list_dir_begin()
	var file_name := dir.get_next()
	while file_name != "":
		if file_name.ends_with(".tres"):
			var res = load("res://data/moves/db/" + file_name)
			if res and res is MoveData:
				_move_cache[res.move_id] = res
		file_name = dir.get_next()

func get_move(move_id: int) -> MoveData:
	return _move_cache.get(move_id, null)

func get_move_by_name(move_name: String) -> MoveData:
	for move in _move_cache.values():
		if move.move_name == move_name:
			return move
	return null
