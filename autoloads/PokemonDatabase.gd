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

func get_anim_frames_path(pokemon_id: int, back: bool = false, shiny: bool = false) -> String:
	if shiny:
		return "res://assets/sprites/animated/shiny/%d_frames.tres" % pokemon_id
	if back:
		return "res://assets/sprites/animated/back/%d_frames.tres" % pokemon_id
	return "res://assets/sprites/animated/front/%d_frames.tres" % pokemon_id

func get_anim_frames(pokemon_id: int, back: bool = false, shiny: bool = false) -> SpriteFrames:
	var path := get_anim_frames_path(pokemon_id, back, shiny)
	if ResourceLoader.exists(path):
		return load(path)
	# 回退到正面普通动画
	var fallback := "res://assets/sprites/animated/front/%d_frames.tres" % pokemon_id
	if ResourceLoader.exists(fallback):
		return load(fallback)
	return null

func get_sprite_path(pokemon_id: int, back: bool = false, shiny: bool = false) -> String:
	if back:
		# 背面无闪光单独目录，闪光背面放 shiny_back
		if shiny:
			return "res://assets/sprites/pokemon/shiny_back/%d.png" % pokemon_id
		return "res://assets/sprites/pokemon/back/%d.png" % pokemon_id
	if shiny:
		return "res://assets/sprites/pokemon/shiny_front/%d.png" % pokemon_id
	return "res://assets/sprites/pokemon/front/%d.png" % pokemon_id

func get_sprite_texture(pokemon_id: int, back: bool = false, shiny: bool = false) -> Texture2D:
	var path := get_sprite_path(pokemon_id, back, shiny)
	if ResourceLoader.exists(path):
		return load(path)
	# 回退到正面普通图
	var fallback := "res://assets/sprites/pokemon/front/%d.png" % pokemon_id
	if ResourceLoader.exists(fallback):
		return load(fallback)
	return null

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
