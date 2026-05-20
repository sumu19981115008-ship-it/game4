class_name MegaEvolutionSystem
extends Node

signal mega_evolution_started(pokemon: PokemonInstance)
signal mega_evolution_completed(pokemon: PokemonInstance)
signal mega_evolution_reverted(pokemon: PokemonInstance)

var _has_mega_evolved_this_battle: bool = false

func can_trigger_mega(pokemon: PokemonInstance) -> bool:
	if _has_mega_evolved_this_battle:
		return false
	if not pokemon.species_data or not pokemon.species_data.can_mega_evolve:
		return false
	if pokemon.held_item_id != pokemon.species_data.mega_stone_item_id:
		return false
	return true

func trigger_mega_evolution(pokemon: PokemonInstance) -> void:
	if not can_trigger_mega(pokemon):
		return
	_has_mega_evolved_this_battle = true
	mega_evolution_started.emit(pokemon)
	var mega_data := PokemonDatabase.get_species(pokemon.species_data.mega_species_id)
	if not mega_data:
		push_error("超级进化形态数据未找到: %d" % pokemon.species_data.mega_species_id)
		return
	pokemon.mega_species_data = mega_data
	pokemon.is_mega_evolved = true
	var original_species := pokemon.species_data
	pokemon.species_data = mega_data
	pokemon.calculate_stats()
	pokemon.current_hp = min(pokemon.current_hp, pokemon.max_hp)
	pokemon.species_data = original_species
	mega_evolution_completed.emit(pokemon)

func revert_mega_evolution(pokemon: PokemonInstance) -> void:
	if not pokemon.is_mega_evolved:
		return
	pokemon.is_mega_evolved = false
	pokemon.mega_species_data = null
	pokemon.calculate_stats()
	pokemon.current_hp = min(pokemon.current_hp, pokemon.max_hp)
	mega_evolution_reverted.emit(pokemon)

func reset_battle_flag() -> void:
	_has_mega_evolved_this_battle = false
