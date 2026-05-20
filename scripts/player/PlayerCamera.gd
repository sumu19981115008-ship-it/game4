class_name PlayerCamera
extends Camera2D

@export var zoom_target: Vector2 = Vector2(2.0, 2.0)
@export var zoom_lerp_speed: float = 3.0

func _ready() -> void:
	position_smoothing_enabled = true
	position_smoothing_speed = 5.0
	offset = Vector2(0, -16)
	zoom = zoom_target
	EventBus.zone_entered.connect(_on_zone_entered)

func set_boundary(left: int, right: int, top: int, bottom: int) -> void:
	limit_left   = left
	limit_right  = right
	limit_top    = top
	limit_bottom = bottom
	EventBus.boundary_changed.emit({"left": left, "right": right, "top": top, "bottom": bottom})

func zoom_to(target_zoom: Vector2, duration: float = 0.4) -> void:
	var tween := create_tween()
	tween.tween_property(self, "zoom", target_zoom, duration).set_trans(Tween.TRANS_SINE)

func lock_to_position(world_pos: Vector2, duration: float = 1.0) -> void:
	set_as_top_level(true)
	var tween := create_tween()
	tween.tween_property(self, "global_position", world_pos, duration)
	EventBus.camera_locked.emit()

func release_lock() -> void:
	set_as_top_level(false)
	position = Vector2.ZERO
	EventBus.camera_released.emit()

func _on_zone_entered(_zone_id: String) -> void:
	pass  # 由 CameraManager 负责更新边界
