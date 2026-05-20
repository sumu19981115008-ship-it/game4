extends Node

const SETTINGS_PATH := "user://settings.cfg"

var _config := ConfigFile.new()

var _defaults: Dictionary = {
	"audio/master_volume": 0.75,
	"audio/bgm_volume": 0.6,
	"audio/sfx_volume": 0.8,
	"audio/mute": false,
	"video/fullscreen": false,
	"video/pixel_filter": "nearest",
	"video/vsync": true,
	"video/fps_limit": 60,
	"gameplay/dialogue_speed": "normal",
	"gameplay/battle_animation_speed": "normal",
	"gameplay/auto_save": true,
	"gameplay/auto_save_interval": 10,
	"language/game_language": "zh_CN",
}

func _ready() -> void:
	_load_settings()

func get_setting(key: String) -> Variant:
	var parts: PackedStringArray = key.split("/")
	if parts.size() < 2:
		return _defaults.get(key)
	return _config.get_value(parts[0], parts[1], _defaults.get(key))

func set_setting(key: String, value: Variant) -> void:
	var parts: PackedStringArray = key.split("/")
	if parts.size() < 2:
		return
	_config.set_value(parts[0], parts[1], value)

func save_settings() -> void:
	_config.save(SETTINGS_PATH)

func _load_settings() -> void:
	if FileAccess.file_exists(SETTINGS_PATH):
		_config.load(SETTINGS_PATH)
	for key: String in _defaults:
		var parts: PackedStringArray = key.split("/")
		if parts.size() >= 2:
			if not _config.has_section_key(parts[0], parts[1]):
				_config.set_value(parts[0], parts[1], _defaults[key])
