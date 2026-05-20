class_name EvolutionCondition
extends Resource

enum EvolutionTrigger {
	LEVEL_UP, USE_ITEM, TRADE, HIGH_FRIENDSHIP, SPECIAL
}

@export var trigger: EvolutionTrigger = EvolutionTrigger.LEVEL_UP
@export var target_species_id: int = 0
@export var min_level: int = 0
@export var required_item_id: int = -1
@export var time_of_day: String = ""
@export var location_tag: String = ""
@export var held_item_id: int = -1
@export var min_friendship: int = 0
@export var required_move_id: int = -1
