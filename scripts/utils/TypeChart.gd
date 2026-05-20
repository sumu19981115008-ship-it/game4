# 完整18×18属性相克表
# 用法：TypeChart.get_effectiveness(攻击属性, 防御属性)
class_name TypeChart

# [攻击属性][防御属性] -> 倍率
# 0=无效, 0.5=效果不佳, 1=普通, 2=效果拔群
const CHART: Dictionary = {
	PokemonEnums.ElementType.NORMAL: {
		PokemonEnums.ElementType.ROCK: 0.5,
		PokemonEnums.ElementType.GHOST: 0.0,
		PokemonEnums.ElementType.STEEL: 0.5,
	},
	PokemonEnums.ElementType.FIRE: {
		PokemonEnums.ElementType.FIRE: 0.5, PokemonEnums.ElementType.WATER: 0.5,
		PokemonEnums.ElementType.GRASS: 2.0, PokemonEnums.ElementType.ICE: 2.0,
		PokemonEnums.ElementType.BUG: 2.0, PokemonEnums.ElementType.ROCK: 0.5,
		PokemonEnums.ElementType.DRAGON: 0.5, PokemonEnums.ElementType.STEEL: 2.0,
	},
	PokemonEnums.ElementType.WATER: {
		PokemonEnums.ElementType.FIRE: 2.0, PokemonEnums.ElementType.WATER: 0.5,
		PokemonEnums.ElementType.GRASS: 0.5, PokemonEnums.ElementType.GROUND: 2.0,
		PokemonEnums.ElementType.ROCK: 2.0, PokemonEnums.ElementType.DRAGON: 0.5,
	},
	PokemonEnums.ElementType.ELECTRIC: {
		PokemonEnums.ElementType.WATER: 2.0, PokemonEnums.ElementType.ELECTRIC: 0.5,
		PokemonEnums.ElementType.GRASS: 0.5, PokemonEnums.ElementType.GROUND: 0.0,
		PokemonEnums.ElementType.FLYING: 2.0, PokemonEnums.ElementType.DRAGON: 0.5,
	},
	PokemonEnums.ElementType.GRASS: {
		PokemonEnums.ElementType.FIRE: 0.5, PokemonEnums.ElementType.WATER: 2.0,
		PokemonEnums.ElementType.GRASS: 0.5, PokemonEnums.ElementType.POISON: 0.5,
		PokemonEnums.ElementType.GROUND: 2.0, PokemonEnums.ElementType.FLYING: 0.5,
		PokemonEnums.ElementType.BUG: 0.5, PokemonEnums.ElementType.ROCK: 2.0,
		PokemonEnums.ElementType.DRAGON: 0.5, PokemonEnums.ElementType.STEEL: 0.5,
	},
	PokemonEnums.ElementType.ICE: {
		PokemonEnums.ElementType.WATER: 0.5, PokemonEnums.ElementType.GRASS: 2.0,
		PokemonEnums.ElementType.ICE: 0.5, PokemonEnums.ElementType.GROUND: 2.0,
		PokemonEnums.ElementType.FLYING: 2.0, PokemonEnums.ElementType.DRAGON: 2.0,
		PokemonEnums.ElementType.STEEL: 0.5,
	},
	PokemonEnums.ElementType.FIGHTING: {
		PokemonEnums.ElementType.NORMAL: 2.0, PokemonEnums.ElementType.ICE: 2.0,
		PokemonEnums.ElementType.POISON: 0.5, PokemonEnums.ElementType.FLYING: 0.5,
		PokemonEnums.ElementType.PSYCHIC: 0.5, PokemonEnums.ElementType.BUG: 0.5,
		PokemonEnums.ElementType.ROCK: 2.0, PokemonEnums.ElementType.GHOST: 0.0,
		PokemonEnums.ElementType.DARK: 2.0, PokemonEnums.ElementType.STEEL: 2.0,
		PokemonEnums.ElementType.FAIRY: 0.5,
	},
	PokemonEnums.ElementType.POISON: {
		PokemonEnums.ElementType.GRASS: 2.0, PokemonEnums.ElementType.POISON: 0.5,
		PokemonEnums.ElementType.GROUND: 0.5, PokemonEnums.ElementType.ROCK: 0.5,
		PokemonEnums.ElementType.GHOST: 0.5, PokemonEnums.ElementType.STEEL: 0.0,
		PokemonEnums.ElementType.FAIRY: 2.0,
	},
	PokemonEnums.ElementType.GROUND: {
		PokemonEnums.ElementType.FIRE: 2.0, PokemonEnums.ElementType.ELECTRIC: 2.0,
		PokemonEnums.ElementType.GRASS: 0.5, PokemonEnums.ElementType.POISON: 2.0,
		PokemonEnums.ElementType.FLYING: 0.0, PokemonEnums.ElementType.BUG: 0.5,
		PokemonEnums.ElementType.ROCK: 2.0, PokemonEnums.ElementType.STEEL: 2.0,
	},
	PokemonEnums.ElementType.FLYING: {
		PokemonEnums.ElementType.ELECTRIC: 0.5, PokemonEnums.ElementType.GRASS: 2.0,
		PokemonEnums.ElementType.FIGHTING: 2.0, PokemonEnums.ElementType.BUG: 2.0,
		PokemonEnums.ElementType.ROCK: 0.5, PokemonEnums.ElementType.STEEL: 0.5,
	},
	PokemonEnums.ElementType.PSYCHIC: {
		PokemonEnums.ElementType.FIGHTING: 2.0, PokemonEnums.ElementType.POISON: 2.0,
		PokemonEnums.ElementType.PSYCHIC: 0.5, PokemonEnums.ElementType.DARK: 0.0,
		PokemonEnums.ElementType.STEEL: 0.5,
	},
	PokemonEnums.ElementType.BUG: {
		PokemonEnums.ElementType.FIRE: 0.5, PokemonEnums.ElementType.GRASS: 2.0,
		PokemonEnums.ElementType.FIGHTING: 0.5, PokemonEnums.ElementType.POISON: 0.5,
		PokemonEnums.ElementType.FLYING: 0.5, PokemonEnums.ElementType.PSYCHIC: 2.0,
		PokemonEnums.ElementType.GHOST: 0.5, PokemonEnums.ElementType.DARK: 2.0,
		PokemonEnums.ElementType.STEEL: 0.5, PokemonEnums.ElementType.FAIRY: 0.5,
	},
	PokemonEnums.ElementType.ROCK: {
		PokemonEnums.ElementType.FIRE: 2.0, PokemonEnums.ElementType.ICE: 2.0,
		PokemonEnums.ElementType.FIGHTING: 0.5, PokemonEnums.ElementType.GROUND: 0.5,
		PokemonEnums.ElementType.FLYING: 2.0, PokemonEnums.ElementType.BUG: 2.0,
		PokemonEnums.ElementType.STEEL: 0.5,
	},
	PokemonEnums.ElementType.GHOST: {
		PokemonEnums.ElementType.NORMAL: 0.0, PokemonEnums.ElementType.PSYCHIC: 2.0,
		PokemonEnums.ElementType.GHOST: 2.0, PokemonEnums.ElementType.DARK: 0.5,
	},
	PokemonEnums.ElementType.DRAGON: {
		PokemonEnums.ElementType.DRAGON: 2.0, PokemonEnums.ElementType.STEEL: 0.5,
		PokemonEnums.ElementType.FAIRY: 0.0,
	},
	PokemonEnums.ElementType.DARK: {
		PokemonEnums.ElementType.FIGHTING: 0.5, PokemonEnums.ElementType.PSYCHIC: 2.0,
		PokemonEnums.ElementType.GHOST: 2.0, PokemonEnums.ElementType.DARK: 0.5,
		PokemonEnums.ElementType.FAIRY: 0.5,
	},
	PokemonEnums.ElementType.STEEL: {
		PokemonEnums.ElementType.FIRE: 0.5, PokemonEnums.ElementType.WATER: 0.5,
		PokemonEnums.ElementType.ELECTRIC: 0.5, PokemonEnums.ElementType.ICE: 2.0,
		PokemonEnums.ElementType.ROCK: 2.0, PokemonEnums.ElementType.STEEL: 0.5,
		PokemonEnums.ElementType.FAIRY: 2.0,
	},
	PokemonEnums.ElementType.FAIRY: {
		PokemonEnums.ElementType.FIRE: 0.5, PokemonEnums.ElementType.FIGHTING: 2.0,
		PokemonEnums.ElementType.POISON: 0.5, PokemonEnums.ElementType.DRAGON: 2.0,
		PokemonEnums.ElementType.DARK: 2.0, PokemonEnums.ElementType.STEEL: 0.5,
	},
}

static func get_effectiveness(attack_type: PokemonEnums.ElementType, defend_type: PokemonEnums.ElementType) -> float:
	if CHART.has(attack_type) and CHART[attack_type].has(defend_type):
		return CHART[attack_type][defend_type]
	return 1.0

static func get_effectiveness_vs_dual(attack_type: PokemonEnums.ElementType, type1: PokemonEnums.ElementType, type2: PokemonEnums.ElementType) -> float:
	return get_effectiveness(attack_type, type1) * get_effectiveness(attack_type, type2)
