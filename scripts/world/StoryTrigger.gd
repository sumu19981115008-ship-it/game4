class_name StoryTrigger
extends Area2D

@export var trigger_id: String = ""
@export var dialogue_to_start: String = ""
@export var required_flag: String = ""
@export var required_flag_value = true
@export var one_shot: bool = true

var _triggered: bool = false

func _ready() -> void:
	collision_layer = CollisionLayers.TRIGGER
	collision_mask = CollisionLayers.PLAYER
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return
	if one_shot and _triggered:
		return
	if not _check_conditions():
		return
	_triggered = true
	if not trigger_id.is_empty():
		EventBus.emit_signal(trigger_id)
	if not dialogue_to_start.is_empty():
		DialogueManager.start_dialogue(dialogue_to_start)

func _check_conditions() -> bool:
	if required_flag.is_empty():
		return true
	return FlagManager.get_flag(required_flag) == required_flag_value
