extends Node

# 战斗事件
signal battle_started(battle_type: String)
signal battle_ended(outcome: String)
signal berserk_evolution_started(pokemon_entity)
signal berserk_evolution_ended(pokemon_entity)

# 区域事件
signal zone_entered(zone_id: String)
signal zone_exited(zone_id: String)
signal scene_transition_started(target: String)

# 相机事件
signal camera_locked
signal camera_released
signal boundary_changed(new_boundary)

# 宝可梦事件
signal pokemon_caught(pokemon)
signal pokemon_fainted(pokemon)
signal party_updated

# 剧情事件
signal dialogue_started(dialogue_id: String)
signal dialogue_ended(dialogue_id: String)
signal cutscene_started(cutscene_id: String)
signal cutscene_ended(cutscene_id: String)
signal flag_changed(key: String, value)

# 任务事件
signal quest_started(quest_id: String)
signal quest_completed(quest_id: String)
signal quest_objective_updated(quest_id: String, obj_id: String)

# 竞技事件
signal royale_rank_promoted(old_rank: String, new_rank: String)

# 世界事件
signal city_crisis_level_changed(new_level: int)
signal zone_unlocked(zone_id: int)
signal zygarde_cell_collected(total: int)

# 存档事件
signal save_completed(slot: int)
signal load_completed(slot: int)
signal autosave_completed
