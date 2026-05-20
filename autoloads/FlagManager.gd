extends Node

# 持久化Flag（随存档保存）
var persistent_flags: Dictionary = {
	# 章节完成
	"ch1_complete": false,
	"ch2_complete": false,
	"ch3_complete": false,
	"ch4_complete": false,
	"ch5_complete": false,
	# 关键剧情
	"arrived_lumiose": false,
	"registered_royale": false,
	"met_liann": false,
	"witnessed_berserk_event": false,
	"joined_mz_introduction": false,
	"lysandre_mentioned": false,
	"l_stone_found": false,
	"lysandre_alive_confirmed": false,
	"lysandre_confronted": false,
	# 玩家选择
	"player_attitude": "",
	"dialogue_choice_1": "",
	# 收集进度
	"zygarde_cells_count": 0,
	# 竞技排名
	"royale_rank": "Z",
	"royale_rank_points": 0,
	# 区域解锁
	"zone_3_unlocked": false,
	"zone_6_unlocked": false,
	"zone_7_unlocked": false,
	"zone_8_unlocked": false,
	"zone_9_unlocked": false,
}

# 临时Flag（不存档）
var session_flags: Dictionary = {}

func set_flag(key: String, value) -> void:
	if persistent_flags.has(key):
		persistent_flags[key] = value
		EventBus.flag_changed.emit(key, value)
	else:
		session_flags[key] = value

func get_flag(key: String, default_value = null):
	if persistent_flags.has(key):
		return persistent_flags[key]
	if session_flags.has(key):
		return session_flags[key]
	return default_value

func check_condition(condition_expr: String) -> bool:
	if condition_expr.is_empty():
		return true
	return _evaluate_expression(condition_expr)

func _evaluate_expression(expr: String) -> bool:
	# 支持 AND / OR / NOT，示例："ch2_complete AND NOT ch3_complete"
	if " AND " in expr:
		var parts: PackedStringArray = expr.split(" AND ")
		for part in parts:
			if not _evaluate_expression(part.strip_edges()):
				return false
		return true
	if " OR " in expr:
		var parts: PackedStringArray = expr.split(" OR ")
		for part in parts:
			if _evaluate_expression(part.strip_edges()):
				return true
		return false
	if expr.begins_with("NOT "):
		return not _evaluate_expression(expr.substr(4).strip_edges())
	var val = get_flag(expr.strip_edges())
	if val is bool:
		return val
	if val is int:
		return val > 0
	if val is String:
		return val != ""
	return val != null

func get_save_data() -> Dictionary:
	return persistent_flags.duplicate(true)

func load_save_data(data: Dictionary) -> void:
	for key in data:
		if persistent_flags.has(key):
			persistent_flags[key] = data[key]
