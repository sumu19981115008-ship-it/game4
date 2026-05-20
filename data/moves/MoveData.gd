class_name MoveData
extends Resource

@export var move_id: int = 0
@export var move_name: String = ""
@export var description: String = ""

@export var type: PokemonEnums.ElementType = PokemonEnums.ElementType.NORMAL
@export var category: PokemonEnums.MoveCategory = PokemonEnums.MoveCategory.PHYSICAL

@export var power: int = 0
@export var accuracy: int = 100
@export var pp: int = 10
@export var priority: int = 0

@export var effect_chance: int = 0
@export var effect_id: int = 0
@export var secondary_effect_id: int = 0
@export var target: int = 0

@export var makes_contact: bool = false
@export var is_sound_based: bool = false
@export var is_punch_based: bool = false
@export var is_bite_based: bool = false
@export var ignores_accuracy: bool = false
@export var ignores_burn: bool = false
@export var crit_bonus: int = 0
