extends Node

# 场景切换时传递的目标出生点（Vector2(-1,-1) 表示无待处理数据，用场景默认出生点）
var pending_spawn_pos: Vector2 = Vector2(-1, -1)

# 区域可访问状态
var zone_access: Dictionary = {
	1: true, 2: true, 3: false, 4: true,
	5: true, 6: false, 7: false, 8: false, 9: false,
}

# 城市危机等级（0-5）
var crisis_level: int = 0:
	set(value):
		crisis_level = clamp(value, 0, 5)
		_on_crisis_level_changed(crisis_level)

var active_berserk_count: Dictionary = {
	"zone_5": 0, "zone_7": 0, "zone_8": 0, "zone_9": 0
}

var game_hour: int = 10  # 0-23
var weather: String = "clear"

func _on_crisis_level_changed(new_level: int) -> void:
	EventBus.city_crisis_level_changed.emit(new_level)
	match new_level:
		2:
			EventBus.berserk_evolution_started.emit(null)
		3:
			zone_access[7] = false
		4:
			pass
		5:
			pass

func unlock_zone(zone_id: int) -> void:
	zone_access[zone_id] = true
	EventBus.zone_unlocked.emit(zone_id)
	FlagManager.set_flag("zone_" + str(zone_id) + "_unlocked", true)

func is_zone_accessible(zone_id: int) -> bool:
	return zone_access.get(zone_id, false)

func get_time_of_day() -> String:
	if game_hour >= 6 and game_hour < 18:
		return "day"
	elif game_hour >= 18 and game_hour < 20:
		return "dusk"
	return "night"

func get_save_data() -> Dictionary:
	return {
		"zone_access": zone_access,
		"crisis_level": crisis_level,
		"active_berserk_count": active_berserk_count,
		"game_hour": game_hour,
		"weather": weather,
	}

func load_save_data(data: Dictionary) -> void:
	zone_access = data.get("zone_access", zone_access)
	crisis_level = data.get("crisis_level", 0)
	active_berserk_count = data.get("active_berserk_count", active_berserk_count)
	game_hour = data.get("game_hour", 10)
	weather = data.get("weather", "clear")
