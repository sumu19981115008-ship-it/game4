class_name PokemonInstance
extends Resource

signal stats_changed

@export var species_id: int = 0
var species_data: PokemonSpeciesData

@export var nickname: String = ""
@export var level: int = 1
@export var experience: int = 0
@export var is_shiny: bool = false

var max_hp: int = 0
var current_hp: int = 0
var attack: int = 0
var defense: int = 0
var sp_attack: int = 0
var sp_defense: int = 0
var speed: int = 0

@export var iv_hp: int = 0
@export var iv_attack: int = 0
@export var iv_defense: int = 0
@export var iv_sp_attack: int = 0
@export var iv_sp_defense: int = 0
@export var iv_speed: int = 0

@export var ev_hp: int = 0
@export var ev_attack: int = 0
@export var ev_defense: int = 0
@export var ev_sp_attack: int = 0
@export var ev_sp_defense: int = 0
@export var ev_speed: int = 0

@export var nature_id: int = 0
@export var ability_slot: int = 0
var current_ability_id: int = 0

@export var move_slots: Array[int] = []
@export var move_pp: Array[int] = []
@export var move_max_pp: Array[int] = []

@export var status: PokemonEnums.StatusCondition = PokemonEnums.StatusCondition.NONE
@export var toxic_counter: int = 0
@export var sleep_turns: int = 0

@export var held_item_id: int = -1

@export var original_trainer_name: String = ""
@export var original_trainer_id: int = 0
@export var is_traded: bool = false

@export var friendship: int = 70

@export var pokeball_id: int = 0
@export var met_location: String = ""
@export var met_level: int = 1
@export var is_egg: bool = false

@export var is_mega_evolved: bool = false
var mega_species_data: PokemonSpeciesData

# 战斗中临时能力等级变化（-6 到 +6）
var stat_stage_attack: int = 0
var stat_stage_defense: int = 0
var stat_stage_sp_attack: int = 0
var stat_stage_sp_defense: int = 0
var stat_stage_speed: int = 0
var stat_stage_accuracy: int = 0
var stat_stage_evasion: int = 0
var crit_stage: int = 0

func calculate_stats() -> void:
	if not species_data:
		return
	max_hp = _calc_hp()
	attack = _calc_stat(species_data.base_attack, iv_attack, ev_attack)
	defense = _calc_stat(species_data.base_defense, iv_defense, ev_defense)
	sp_attack = _calc_stat(species_data.base_sp_attack, iv_sp_attack, ev_sp_attack)
	sp_defense = _calc_stat(species_data.base_sp_defense, iv_sp_defense, ev_sp_defense)
	speed = _calc_stat(species_data.base_speed, iv_speed, ev_speed)
	_apply_nature_modifier()
	stats_changed.emit()

func _calc_hp() -> int:
	var base := species_data.base_hp
	return int(floor((2.0 * base + iv_hp + floor(ev_hp / 4.0)) * level / 100.0)) + level + 10

func _calc_stat(base: int, iv: int, ev: int) -> int:
	return int(floor(floor((2.0 * base + iv + floor(ev / 4.0)) * level / 100.0) + 5.0))

func _apply_nature_modifier() -> void:
	var nm := NatureTable.get_modifier(nature_id)
	attack = int(attack * nm["attack_mult"])
	defense = int(defense * nm["defense_mult"])
	sp_attack = int(sp_attack * nm["sp_attack_mult"])
	sp_defense = int(sp_defense * nm["sp_defense_mult"])
	speed = int(speed * nm["speed_mult"])

func get_display_name() -> String:
	if nickname != "":
		return nickname
	if species_data:
		return species_data.species_name
	return "???"

func is_fainted() -> bool:
	return current_hp <= 0

func hp_percent() -> float:
	if max_hp <= 0:
		return 0.0
	return float(current_hp) / float(max_hp)

func reset_battle_stats() -> void:
	stat_stage_attack = 0
	stat_stage_defense = 0
	stat_stage_sp_attack = 0
	stat_stage_sp_defense = 0
	stat_stage_speed = 0
	stat_stage_accuracy = 0
	stat_stage_evasion = 0
	crit_stage = 0
	is_mega_evolved = false
	mega_species_data = null
