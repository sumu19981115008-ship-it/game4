extends CanvasLayer

@onready var _panel: PanelContainer = $PanelContainer
@onready var _speaker_label: Label = $PanelContainer/VBoxContainer/SpeakerLabel
@onready var _text_label: RichTextLabel = $PanelContainer/VBoxContainer/TextLabel
@onready var _choices_container: VBoxContainer = $PanelContainer/VBoxContainer/ChoicesContainer
@onready var _continue_indicator: Label = $PanelContainer/VBoxContainer/ContinueIndicator

var _is_typing: bool = false
var _full_text: String = ""
var _typing_speed: float = 0.03
var _typing_timer: float = 0.0
var _char_index: int = 0

func _ready() -> void:
	hide()
	DialogueManager.line_displayed.connect(_on_line_displayed)
	DialogueManager.choices_presented.connect(_on_choices_presented)
	EventBus.dialogue_started.connect(_on_dialogue_started)
	EventBus.dialogue_ended.connect(_on_dialogue_ended)

func _process(delta: float) -> void:
	if not _is_typing:
		return
	_typing_timer += delta
	if _typing_timer >= _typing_speed:
		_typing_timer = 0.0
		_char_index += 1
		_text_label.visible_characters = _char_index
		if _char_index >= _full_text.length():
			_is_typing = false
			_continue_indicator.show()

func _input(event: InputEvent) -> void:
	if not visible:
		return
	if event.is_action_pressed("ui_accept"):
		if _is_typing:
			# 跳字：立即显示全部文字
			_is_typing = false
			_text_label.visible_characters = -1
			_continue_indicator.show()
		elif _choices_container.get_child_count() == 0:
			DialogueManager.advance()

func _on_dialogue_started(_id: String) -> void:
	_choices_container.visible = false
	show()

func _on_dialogue_ended(_id: String) -> void:
	hide()

func _on_line_displayed(line: Dictionary) -> void:
	_choices_container.visible = false
	_continue_indicator.hide()
	var speaker: String = line.get("speaker", "")
	_speaker_label.text = speaker
	_speaker_label.visible = not speaker.is_empty()
	_full_text = line.get("text", "")
	_text_label.text = _full_text
	_text_label.visible_characters = 0
	_char_index = 0
	_typing_timer = 0.0
	_is_typing = true

func _on_choices_presented(choices: Array) -> void:
	_continue_indicator.hide()
	for child in _choices_container.get_children():
		child.queue_free()
	for i in choices.size():
		var btn := Button.new()
		btn.text = choices[i].get("text", "")
		var idx := i
		btn.pressed.connect(func(): DialogueManager.make_choice(idx))
		_choices_container.add_child(btn)
	_choices_container.visible = true
