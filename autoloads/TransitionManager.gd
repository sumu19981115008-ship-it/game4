extends CanvasLayer

var _overlay: ColorRect

func _ready() -> void:
	layer = 20
	_overlay = ColorRect.new()
	_overlay.color = Color.BLACK
	_overlay.modulate.a = 0.0
	_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_overlay)

func fade_to_black(duration: float = 0.5) -> void:
	var tween := create_tween()
	tween.tween_property(_overlay, "modulate:a", 1.0, duration)
	await tween.finished

func fade_from_black(duration: float = 0.5) -> void:
	var tween := create_tween()
	tween.tween_property(_overlay, "modulate:a", 0.0, duration)
	await tween.finished

func flash_white(count: int = 3, interval: float = 0.15) -> void:
	var original_color := _overlay.color
	_overlay.color = Color.WHITE
	for i in range(count):
		_overlay.modulate.a = 0.9
		await get_tree().create_timer(interval / 2.0).timeout
		_overlay.modulate.a = 0.0
		await get_tree().create_timer(interval / 2.0).timeout
	_overlay.color = original_color

func transition_to_battle() -> void:
	await flash_white(3, 0.15)
	await fade_to_black(0.2)

func transition_from_battle() -> void:
	await fade_from_black(0.4)

func transition_zone(target_scene: String) -> void:
	await fade_to_black(0.3)
	get_tree().change_scene_to_file(target_scene)
	await fade_from_black(0.3)
