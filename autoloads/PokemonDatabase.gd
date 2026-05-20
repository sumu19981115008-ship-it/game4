extends Node

var _species_cache: Dictionary = {}
var _is_loaded: bool = false

func _ready() -> void:
	_load_all_species()

func _load_all_species() -> void:
	var dir := DirAccess.open("res://data/species/db/")
	if not dir:
		push_warning("宝可梦数据库目录不存在，跳过加载")
		_is_loaded = true
		return
	dir.list_dir_begin()
	var file_name := dir.get_next()
	while file_name != "":
		if file_name.ends_with(".tres"):
			var res = load("res://data/species/db/" + file_name)
			if res and res is PokemonSpeciesData:
				_species_cache[res.species_id] = res
		file_name = dir.get_next()
	_is_loaded = true

func get_species(species_id: int) -> PokemonSpeciesData:
	return _species_cache.get(species_id, null)

func get_total_species_count() -> int:
	return _species_cache.size()

func create_pokemon(species_id: int, level: int) -> PokemonInstance:
	var instance := PokemonInstance.new()
	instance.species_id = species_id
	instance.species_data = get_species(species_id)
	instance.level = level
	# 随机IV
	instance.iv_hp = randi_range(0, 31)
	instance.iv_attack = randi_range(0, 31)
	instance.iv_defense = randi_range(0, 31)
	instance.iv_sp_attack = randi_range(0, 31)
	instance.iv_sp_defense = randi_range(0, 31)
	instance.iv_speed = randi_range(0, 31)
	# 随机性格
	instance.nature_id = randi_range(0, 24)
	# 计算能力值
	if instance.species_data:
		instance.calculate_stats()
		instance.current_hp = instance.max_hp
	return instance
