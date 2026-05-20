class_name LearnableMove
extends Resource

enum LearnMethod {
	LEVEL_UP, TM, TUTOR, EGG, EVOLUTION
}

@export var move_id: int = 0
@export var learn_method: LearnMethod = LearnMethod.LEVEL_UP
@export var learn_level: int = 1
