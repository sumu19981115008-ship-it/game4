class_name Player
extends CharacterBody2D

signal direction_changed(new_dir: int)
signal run_started
signal run_stopped
signal movement_stopped

@export var walk_speed: float = 80.0
@export var run_speed: float = 160.0
@export var acceleration: float = 800.0
@export var friction: float = 1200.0

var current_direction: int = 0  # 0=DOWN 1=UP 2=LEFT 3=RIGHT
var _is_running: bool = false

@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D

func _ready() -> void:
	add_to_group("player")

func _physics_process(delta: float) -> void:
	var input_dir := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var is_running := Input.is_action_pressed("run")
	var target_speed := run_speed if is_running else walk_speed

	if input_dir != Vector2.ZERO:
		velocity = velocity.move_toward(input_dir.normalized() * target_speed, acceleration * delta)
		_update_direction(input_dir)
	else:
		velocity = velocity.move_toward(Vector2.ZERO, friction * delta)

	move_and_slide()

func _update_direction(input_dir: Vector2) -> void:
	if abs(input_dir.x) >= abs(input_dir.y):
		current_direction = 3 if input_dir.x > 0 else 2
	else:
		current_direction = 0 if input_dir.y > 0 else 1
