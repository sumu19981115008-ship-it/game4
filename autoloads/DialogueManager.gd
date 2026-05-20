extends Node

signal line_displayed(line: Dictionary)
signal choices_presented(choices: Array)
signal node_completed(node_id: String)

var current_dialogue_id: String = ""
var current_node_id: String = ""
var current_line_index: int = 0
var is_playing: bool = false

var _dialogue_cache: Dictionary = {}
var _current_data: Dictionary = {}

func start_dialogue(dialogue_id: String) -> void:
	if is_playing:
		push_warning("对话已在播放中: " + current_dialogue_id)
		return
	var data := _load_dialogue(dialogue_id)
	if data.is_empty():
		push_error("找不到对话数据: " + dialogue_id)
		return
	current_dialogue_id = dialogue_id
	_current_data = data
	is_playing = true
	get_tree().paused = true
	EventBus.dialogue_started.emit(dialogue_id)
	_play_node("start")

func advance() -> void:
	if not is_playing:
		return
	current_line_index += 1
	_play_next_line()

func make_choice(choice_index: int) -> void:
	if not is_playing:
		return
	var node := _get_node(current_node_id)
	if not node or choice_index >= node.get("choices", []).size():
		return
	var choice: Dictionary = node["choices"][choice_index]
	for flag_key in choice.get("flag_set", {}).keys():
		FlagManager.set_flag(flag_key, choice["flag_set"][flag_key])
	_play_node(choice.get("next_node_id", ""))

func end_dialogue() -> void:
	is_playing = false
	get_tree().paused = false
	var finished_id := current_dialogue_id
	current_dialogue_id = ""
	_current_data = {}
	EventBus.dialogue_ended.emit(finished_id)

func _play_node(node_id: String) -> void:
	if node_id.is_empty():
		end_dialogue()
		return
	current_node_id = node_id
	current_line_index = 0
	_play_next_line()

func _play_next_line() -> void:
	var node := _get_node(current_node_id)
	if not node:
		end_dialogue()
		return
	var lines: Array = node.get("lines", [])
	if current_line_index >= lines.size():
		_on_node_complete(node)
		return
	var line: Dictionary = lines[current_line_index]
	for event_key in line.get("trigger_events", []):
		EventBus.emit_signal(event_key)
	line_displayed.emit(line)

func _on_node_complete(node: Dictionary) -> void:
	node_completed.emit(current_node_id)
	var choices: Array = node.get("choices", [])
	if choices.size() > 0:
		var valid_choices: Array = []
		for choice in choices:
			var cond: String = choice.get("condition", "")
			if FlagManager.check_condition(cond):
				valid_choices.append(choice)
		choices_presented.emit(valid_choices)
	else:
		var next_id: String = node.get("next_node_id", "")
		_play_node(next_id)

func _get_node(node_id: String) -> Dictionary:
	var nodes: Array = _current_data.get("nodes", [])
	for node in nodes:
		if node.get("node_id", "") == node_id:
			return node
	return {}

func _load_dialogue(dialogue_id: String) -> Dictionary:
	if _dialogue_cache.has(dialogue_id):
		return _dialogue_cache[dialogue_id]
	var path := "res://data/dialogues/" + dialogue_id + ".json"
	if not FileAccess.file_exists(path):
		return {}
	var file := FileAccess.open(path, FileAccess.READ)
	var json := JSON.new()
	if json.parse(file.get_as_text()) != OK:
		return {}
	_dialogue_cache[dialogue_id] = json.data
	return json.data
