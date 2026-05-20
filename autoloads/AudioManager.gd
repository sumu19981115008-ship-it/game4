extends Node

var bgm_player: AudioStreamPlayer
var sfx_player: AudioStreamPlayer

var _current_bgm: String = ""
var _bgm_volume: float = 0.6
var _sfx_volume: float = 0.8

func _ready() -> void:
	bgm_player = AudioStreamPlayer.new()
	bgm_player.name = "BGMPlayer"
	bgm_player.bus = "BGM"
	add_child(bgm_player)
	sfx_player = AudioStreamPlayer.new()
	sfx_player.name = "SFXPlayer"
	sfx_player.bus = "SFX"
	add_child(sfx_player)

func play_bgm(stream: AudioStream, fade_in: float = 0.8) -> void:
	if not stream:
		return
	bgm_player.stream = stream
	bgm_player.volume_db = linear_to_db(0.0)
	bgm_player.play()
	var tween := create_tween()
	tween.tween_property(bgm_player, "volume_db", linear_to_db(_bgm_volume), fade_in)

func stop_bgm(fade_out: float = 0.5) -> void:
	var tween := create_tween()
	tween.tween_property(bgm_player, "volume_db", linear_to_db(0.0), fade_out)
	tween.tween_callback(bgm_player.stop)

func play_sfx(stream: AudioStream) -> void:
	if not stream:
		return
	sfx_player.stream = stream
	sfx_player.volume_db = linear_to_db(_sfx_volume)
	sfx_player.play()

func set_bgm_volume(vol: float) -> void:
	_bgm_volume = clamp(vol, 0.0, 1.0)
	if bgm_player.playing:
		bgm_player.volume_db = linear_to_db(_bgm_volume)

func set_sfx_volume(vol: float) -> void:
	_sfx_volume = clamp(vol, 0.0, 1.0)
