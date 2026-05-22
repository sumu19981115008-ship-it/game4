class_name ZoneTransition
extends Area2D

enum TransitionType { SEAMLESS, FADE, LOAD }

@export var target_scene: String = ""
# 目标场景的出生格子坐标（metatile 单位，-1 表示用目标场景默认出生点）
@export var spawn_x: int = -1
@export var spawn_y: int = -1
@export var transition_type: TransitionType = TransitionType.FADE
@export var require_direction: bool = false
@export var entry_direction: int = 0  # 0=DOWN 1=UP 2=LEFT 3=RIGHT

var _triggered: bool = false

func _ready() -> void:
	collision_layer = CollisionLayers.TRIGGER
	collision_mask = CollisionLayers.PLAYER
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
	if _triggered:
		return
	if not body.is_in_group("player"):
		return
	if require_direction and body.current_direction != entry_direction:
		return
	_triggered = true
	_execute_transition()

func _execute_transition() -> void:
	EventBus.scene_transition_started.emit(target_scene)
	var spawn := Vector2(-1, -1)
	if spawn_x >= 0 and spawn_y >= 0:
		spawn = Vector2(spawn_x, spawn_y)
	match transition_type:
		TransitionType.SEAMLESS:
			EventBus.zone_entered.emit(target_scene)
		TransitionType.FADE, TransitionType.LOAD:
			TransitionManager.transition_zone(target_scene, spawn)
