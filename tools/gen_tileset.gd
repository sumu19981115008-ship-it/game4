@tool
# 在 Godot 编辑器中执行：
#   Script 菜单 → Run → 选择本文件
# 功能：
#   读取 assets/tilesets/primary_general/tiles.png，
#   生成含物理碰撞层的 TileSet 资源，
#   保存到 assets/tilesets/emerald_tileset.tres
extends EditorScript

const TILE_SIZE := 8          # GBA 原始图块 8×8
const PHYSICS_LAYER := 0      # 碰撞层索引（TileSet 内部）

# 图块集图像路径（res:// 相对）
const TILESET_IMG := "res://assets/tilesets/primary_general/tiles.png"
const OUTPUT_PATH := "res://assets/tilesets/emerald_tileset.tres"

func _run() -> void:
	print("=== 生成 emerald_tileset.tres ===")

	# 加载纹理
	var tex: Texture2D = load(TILESET_IMG)
	if not tex:
		push_error("无法加载: " + TILESET_IMG)
		return
	print("纹理加载成功: %d×%d" % [tex.get_width(), tex.get_height()])

	# 创建 TileSet
	var ts := TileSet.new()
	ts.tile_size = Vector2i(TILE_SIZE, TILE_SIZE)

	# 添加物理碰撞层（layer 0 = WALL，碰撞位掩码参考 CollisionLayers.gd）
	ts.add_physics_layer(PHYSICS_LAYER)
	ts.set_physics_layer_collision_layer(PHYSICS_LAYER, 4)   # WALL = bit2
	ts.set_physics_layer_collision_mask(PHYSICS_LAYER, 0)

	# 创建 TileSetAtlasSource（整张 tiles.png 作为 Atlas）
	var src := TileSetAtlasSource.new()
	src.texture = tex
	src.texture_region_size = Vector2i(TILE_SIZE, TILE_SIZE)

	# 计算图块数量
	var cols: int = tex.get_width()  / TILE_SIZE
	var rows: int = tex.get_height() / TILE_SIZE
	print("图块网格: %d 列 × %d 行 = %d 图块" % [cols, rows, cols * rows])

	# 注册所有图块（每格创建一个 TileData）
	for row in rows:
		for col in cols:
			var coords := Vector2i(col, row)
			src.create_tile(coords)

	# 将 source 添加到 TileSet（固定 id=0）
	ts.add_source(src, 0)

	# 保存
	var err := ResourceSaver.save(ts, OUTPUT_PATH)
	if err == OK:
		print("已保存: " + OUTPUT_PATH)
	else:
		push_error("保存失败，错误码: %d" % err)

	print("=== 完成 ===")
	print("下一步：")
	print("  1. 在 Godot 编辑器中打开 emerald_tileset.tres")
	print("  2. 选择需要碰撞的图块，在 Physics 面板手动绘制碰撞形状")
	print("  3. 或运行游戏，TileMapZone 会用代码地图自动推断碰撞")
