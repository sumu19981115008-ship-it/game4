class_name PokemonSpeciesData
extends Resource

@export var species_id: int = 0
@export var species_name: String = ""
@export var species_name_en: String = ""
@export var category: String = ""
@export var pokedex_entry: String = ""

@export var type1: PokemonEnums.ElementType = PokemonEnums.ElementType.NORMAL
@export var type2: PokemonEnums.ElementType = PokemonEnums.ElementType.NORMAL
@export var has_secondary_type: bool = false

@export var base_hp: int = 0
@export var base_attack: int = 0
@export var base_defense: int = 0
@export var base_sp_attack: int = 0
@export var base_sp_defense: int = 0
@export var base_speed: int = 0

@export var ability1_id: int = 0
@export var ability2_id: int = -1
@export var hidden_ability_id: int = -1

@export var growth_rate: PokemonEnums.GrowthRate = PokemonEnums.GrowthRate.MEDIUM_FAST
@export var base_experience_yield: int = 0
@export var ev_yield_hp: int = 0
@export var ev_yield_attack: int = 0
@export var ev_yield_defense: int = 0
@export var ev_yield_sp_attack: int = 0
@export var ev_yield_sp_defense: int = 0
@export var ev_yield_speed: int = 0

@export var catch_rate: int = 45
@export var base_friendship: int = 70

@export var egg_group1: PokemonEnums.EggGroup = PokemonEnums.EggGroup.UNDISCOVERED
@export var egg_group2: PokemonEnums.EggGroup = PokemonEnums.EggGroup.UNDISCOVERED
@export var hatch_steps: int = 5120
@export var gender_ratio: float = 0.5

@export var height_m: float = 0.0
@export var weight_kg: float = 0.0

@export var learnable_moves: Array[LearnableMove] = []
@export var evolutions: Array[EvolutionCondition] = []
@export var pre_evolution_id: int = -1

@export var front_sprite: Texture2D
@export var back_sprite: Texture2D
@export var shiny_front_sprite: Texture2D
@export var shiny_back_sprite: Texture2D
@export var icon_sprite: Texture2D
@export var cry_audio: AudioStream

@export var can_mega_evolve: bool = false
@export var mega_species_id: int = -1
@export var mega_stone_item_id: int = -1
