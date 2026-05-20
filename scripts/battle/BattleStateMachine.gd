class_name BattleStateMachine
extends Node

enum BattlePhase {
	PHASE_INTRO,
	PHASE_PLAYER_INPUT,
	PHASE_ENEMY_THINK,
	PHASE_ORDER_RESOLVE,
	PHASE_EXECUTE_ACTION,
	PHASE_END_OF_TURN,
	PHASE_CHECK_FAINT,
	PHASE_BATTLE_END
}

signal phase_changed(new_phase: BattlePhase)
signal battle_ended(outcome: PokemonEnums.BattleOutcome)

var current_phase: BattlePhase = BattlePhase.PHASE_INTRO
var action_queue: Array = []
var turn_count: int = 0
var escape_attempts: int = 0

func transition_to(new_phase: BattlePhase) -> void:
	current_phase = new_phase
	phase_changed.emit(new_phase)

func start_battle() -> void:
	turn_count = 0
	escape_attempts = 0
	transition_to(BattlePhase.PHASE_INTRO)

func next_turn() -> void:
	turn_count += 1
	action_queue.clear()
	transition_to(BattlePhase.PHASE_PLAYER_INPUT)
