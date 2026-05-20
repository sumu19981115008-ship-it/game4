class_name ZoneTransition
extends Area2D

enum TransitionType { SEAMLESS, FADE, LOAD }

@export var target_scene: String = ""
@export var target_spawn_id: String = ""
@export var transition_type: TransitionType = TransitionType.FADE
@export var require_direction: bool = false
@export var entry_direction: PokemonEnums.Direction = PokemonEnums.Direction.DOWN

func _ready() -> void:
	collision_layer = CollisionLayers.TRIGGER
	collision_mask = CollisionLayers.PLAYER
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return
	if require_direction:
		var player := body as Player
		if player and player.current_direction != entry_direction:
			return
	_execute_transition()

func _execute_transition() -> void:
	EventBus.scene_transition_started.emit(target_scene)
	match transition_type:
		TransitionType.SEAMLESS:
			EventBus.zone_entered.emit(target_scene)
		TransitionType.FADE:
			TransitionManager.transition_zone(target_scene)
		TransitionType.LOAD:
			TransitionManager.transition_zone(target_scene)
