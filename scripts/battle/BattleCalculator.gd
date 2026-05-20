class_name BattleCalculator

class DamageResult:
	var damage: int = 0
	var is_critical: bool = false
	var type_multiplier: float = 1.0
	var missed: bool = false

static func calculate_damage(
	attacker: PokemonInstance,
	defender: PokemonInstance,
	move: MoveData,
	current_weather: String = "clear"
) -> DamageResult:
	var result := DamageResult.new()

	if move.power <= 0:
		return result

	# 选择攻防数值
	var atk: int
	var def: int
	if move.category == PokemonEnums.MoveCategory.PHYSICAL:
		atk = attacker.attack
		def = defender.defense
	else:
		atk = attacker.sp_attack
		def = defender.sp_defense

	# 急所判定
	var is_critical := roll_critical(attacker.crit_stage + move.crit_bonus)
	if is_critical:
		# 急所：无视负面攻击等级变化和对方正面防御等级变化
		pass
	result.is_critical = is_critical

	# 基础伤害
	var base_dmg: int = int(int(2 * attacker.level / 5 + 2) * move.power * atk / max(def, 1) / 50 + 2)

	# 修正系数
	var critical_mod := 1.5 if is_critical else 1.0
	var random_mod := float(randi_range(85, 100)) / 100.0

	# STAB
	var attacker_types := _get_pokemon_types(attacker)
	var stab_mod := 1.5 if move.type in attacker_types else 1.0

	# 属性相克
	var defender_types := _get_pokemon_types(defender)
	var type_mod := get_type_effectiveness(move.type, defender_types)
	result.type_multiplier = type_mod

	# 无效直接返回
	if type_mod == 0.0:
		result.damage = 0
		return result

	# 灼伤减伤
	var burn_mod := 1.0
	if attacker.status == PokemonEnums.StatusCondition.BURN and \
	   move.category == PokemonEnums.MoveCategory.PHYSICAL and \
	   not move.ignores_burn:
		burn_mod = 0.5

	var total_mod := critical_mod * random_mod * stab_mod * type_mod * burn_mod
	result.damage = max(1, int(base_dmg * total_mod))
	return result

static func get_type_effectiveness(move_type: PokemonEnums.ElementType, defender_types: Array) -> float:
	var multiplier := 1.0
	for def_type in defender_types:
		multiplier *= TypeChart.get_effectiveness(move_type, def_type)
	return multiplier

static func roll_critical(crit_level: int) -> bool:
	match crit_level:
		0: return randi() % 24 == 0
		1: return randi() % 8 == 0
		2: return randi() % 2 == 0
		_: return true

static func check_hit(accuracy: int, attacker_acc_stage: int, defender_eva_stage: int) -> bool:
	if accuracy == 0:
		return true
	var stage_mod := _get_accuracy_stage_modifier(attacker_acc_stage - defender_eva_stage)
	return randf() < (accuracy / 100.0) * stage_mod

static func _get_accuracy_stage_modifier(stage: int) -> float:
	var clamped: int = clamp(stage, -6, 6)
	var table := [3.0/9.0, 3.0/8.0, 3.0/7.0, 3.0/6.0, 3.0/5.0, 3.0/4.0,
				  1.0,
				  4.0/3.0, 5.0/3.0, 6.0/3.0, 7.0/3.0, 8.0/3.0, 9.0/3.0]
	return table[clamped + 6]

static func _get_pokemon_types(pokemon: PokemonInstance) -> Array:
	if not pokemon.species_data:
		return [PokemonEnums.ElementType.NORMAL]
	var types := [pokemon.species_data.type1]
	if pokemon.species_data.has_secondary_type:
		types.append(pokemon.species_data.type2)
	return types

static func calc_escape_chance(player_speed: int, enemy_speed: int, escape_attempts: int) -> bool:
	var f := int(float(player_speed) * 128.0 / max(enemy_speed / 4, 1)) + 30 * escape_attempts
	f = f % 256
	return randi() % 256 < f
