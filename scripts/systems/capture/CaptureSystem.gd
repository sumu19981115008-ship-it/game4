class_name CaptureSystem

static func calculate_catch_result(
	target: PokemonInstance,
	ball_modifier: float,
	is_always_catch: bool,
	current_turn: int
) -> int:
	if is_always_catch:
		return 3

	if not target.species_data:
		return 0

	var catch_rate_base: float = float(target.species_data.catch_rate) * ball_modifier

	# HP修正
	var a: float = floor(
		(3.0 * target.max_hp - 2.0 * target.current_hp)
		* catch_rate_base
		/ (3.0 * target.max_hp)
	)

	# 状态修正
	a *= _get_status_bonus(target.status)
	a = clamp(a, 1.0, 255.0)

	# 阈值
	var b: float = 1048560.0 / sqrt(sqrt(16711680.0 / a))

	# 4次随机判定
	var shake_count: int = 0
	for _i in range(4):
		var roll := randi_range(0, 65535)
		if roll < int(b):
			shake_count += 1
		else:
			break

	return shake_count

static func _get_status_bonus(status: PokemonEnums.StatusCondition) -> float:
	match status:
		PokemonEnums.StatusCondition.SLEEP, PokemonEnums.StatusCondition.FREEZE:
			return 2.5
		PokemonEnums.StatusCondition.BURN, PokemonEnums.StatusCondition.POISON, \
		PokemonEnums.StatusCondition.TOXIC, PokemonEnums.StatusCondition.PARALYSIS:
			return 1.5
		_:
			return 1.0
