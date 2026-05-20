extends CanvasLayer

@onready var _time_label: Label = $MarginContainer/HBoxContainer/TimeLabel
@onready var _party_container: HBoxContainer = $MarginContainer/HBoxContainer/PartyContainer

var _time_seconds: float = 0.0

func _ready() -> void:
	EventBus.party_updated.connect(_on_party_updated)
	EventBus.dialogue_started.connect(_on_dialogue_started)
	EventBus.dialogue_ended.connect(_on_dialogue_ended)

func _process(delta: float) -> void:
	_time_seconds += delta
	_update_time_display()

func _update_time_display() -> void:
	var h := int(_time_seconds / 3600)
	var m := int(fmod(_time_seconds, 3600.0) / 60)
	_time_label.text = "%02d:%02d" % [h, m]

func _on_party_updated() -> void:
	# 刷新队伍显示（待战斗系统接入后完善）
	pass

func _on_dialogue_started(_id: String) -> void:
	hide()

func _on_dialogue_ended(_id: String) -> void:
	show()
