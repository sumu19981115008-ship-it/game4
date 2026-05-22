class_name PlayerCamera
extends Camera2D

@export var zoom_target: Vector2 = Vector2(2.0, 2.0)

# 地图边界（世界坐标，由 Zone 调用 set_boundary 传入）
var _map_left:   int = 0
var _map_right:  int = 320
var _map_top:    int = 0
var _map_bottom: int = 320

# 边缘遮罩节点（漆黑魅影风格：四周贴黑色面板遮住地图外区域）
var _overlay: CanvasLayer
var _border_rects: Array = []   # [top, bottom, left, right]

func _ready() -> void:
	position_smoothing_enabled = true
	position_smoothing_speed   = 8.0
	zoom = zoom_target
	_build_border_overlay()
	EventBus.zone_entered.connect(_on_zone_entered)

# ── 边界设置 ──────────────────────────────────────────────────────────────────

func set_boundary(map_w_px: int, map_h_px: int) -> void:
	"""
	传入地图像素尺寸。
	Camera2D limit 使用世界坐标（与 zoom 无关）。
	"""
	_map_left   = 0
	_map_right  = map_w_px
	_map_top    = 0
	_map_bottom = map_h_px

	limit_left   = _map_left
	limit_right  = _map_right
	limit_top    = _map_top
	limit_bottom = _map_bottom

	EventBus.boundary_changed.emit({
		"left": _map_left, "right": _map_right,
		"top": _map_top,   "bottom": _map_bottom
	})

# ── 黑色边框遮罩（跟随摄像机的 CanvasLayer）────────────────────────────────

func _build_border_overlay() -> void:
	"""
	在屏幕四周叠加黑色面板，遮住地图外的空白区域。
	面板足够大（2048px），无论分辨率如何都能覆盖。
	CanvasLayer layer = -1 置于地图背景之下，layer = 10 置于地图之上。
	这里用 layer=10 覆盖在地图上，只在到达地图边缘时才可见。
	"""
	_overlay = CanvasLayer.new()
	_overlay.layer = 10
	_overlay.follow_viewport_enabled = false
	add_child(_overlay)

	# 屏幕视口半宽/半高（缩放前，逻辑像素）
	# 在 _process 里动态更新位置，此处先建节点
	var black := Color(0, 0, 0, 1)
	for i in 4:
		var rect := ColorRect.new()
		rect.color = black
		_overlay.add_child(rect)
		_border_rects.append(rect)

	_update_border_rects()

func _update_border_rects() -> void:
	"""
	根据当前视口尺寸和地图边界更新四块遮罩面板的位置/尺寸。
	遮罩在屏幕坐标系中定位，始终覆盖地图范围外的区域。
	"""
	if _border_rects.is_empty():
		return

	var vp       := get_viewport()
	if not vp:
		return
	var vp_size  := vp.get_visible_rect().size          # 屏幕像素
	var zoom_v   := zoom                                 # 当前 zoom
	# 地图在屏幕上的像素尺寸
	var map_screen_w := (_map_right  - _map_left) * zoom_v.x
	var map_screen_h := (_map_bottom - _map_top)  * zoom_v.y

	# 屏幕中心 = 摄像机位置（在世界坐标中）投影到屏幕后是屏幕正中
	# 摄像机被 limit 夹住后，地图左边缘在屏幕上的 x 位置：
	#   screen_x = (0 - cam_world_x) * zoom + vp_size.x/2
	# 但我们直接用 CanvasLayer 的屏幕坐标，摄像机总在屏幕中心
	# 地图左边缘相对屏幕中心的偏移 = (map_left_world - cam_world_x) * zoom
	# 当摄像机贴着左边界时 cam_world_x = vp_size.x/(2*zoom)，地图左边缘正好在屏幕左侧
	# 遮罩需要盖住 屏幕左边 → 地图左边缘 这段区域

	# 简化策略：遮罩面板足够大（4096px），位置随摄像机世界坐标实时算
	# top 板：覆盖地图上方
	# bottom 板：覆盖地图下方
	# left 板：覆盖地图左侧
	# right 板：覆盖地图右侧

	# 在 _process 里每帧更新，这里只设尺寸
	var big := 4096.0
	# top
	_border_rects[0].size = Vector2(big * 2, big)
	# bottom
	_border_rects[1].size = Vector2(big * 2, big)
	# left
	_border_rects[2].size = Vector2(big, big * 2)
	# right
	_border_rects[3].size = Vector2(big, big * 2)

func _process(_delta: float) -> void:
	_reposition_borders()

func _reposition_borders() -> void:
	if _border_rects.is_empty():
		return
	var vp := get_viewport()
	if not vp:
		return

	var vp_size := vp.get_visible_rect().size
	var zoom_v  := zoom
	var big     := 4096.0

	# get_screen_center_position() 返回已经被 limit 夹住后的实际渲染中心（世界坐标）
	# 用 global_position 会得到 limit 前的位置，导致边界处遮罩反向偏移
	var center := get_screen_center_position()

	# 地图四条边在屏幕坐标系中的像素位置（屏幕左上角为原点）
	var screen_left   := (float(_map_left)   - center.x) * zoom_v.x + vp_size.x * 0.5
	var screen_right  := (float(_map_right)  - center.x) * zoom_v.x + vp_size.x * 0.5
	var screen_top    := (float(_map_top)    - center.y) * zoom_v.y + vp_size.y * 0.5
	var screen_bottom := (float(_map_bottom) - center.y) * zoom_v.y + vp_size.y * 0.5

	# top 板：下边缘对齐 screen_top，向上延伸 big px
	_border_rects[0].position = Vector2(screen_left - big, screen_top - big)
	_border_rects[0].size     = Vector2((screen_right - screen_left) + big * 2, big)

	# bottom 板：上边缘对齐 screen_bottom，向下延伸 big px
	_border_rects[1].position = Vector2(screen_left - big, screen_bottom)
	_border_rects[1].size     = Vector2((screen_right - screen_left) + big * 2, big)

	# left 板：右边缘对齐 screen_left，向左延伸 big px
	_border_rects[2].position = Vector2(screen_left - big, screen_top - big)
	_border_rects[2].size     = Vector2(big, (screen_bottom - screen_top) + big * 2)

	# right 板：左边缘对齐 screen_right，向右延伸 big px
	_border_rects[3].position = Vector2(screen_right, screen_top - big)
	_border_rects[3].size     = Vector2(big, (screen_bottom - screen_top) + big * 2)

# ── 其他接口 ─────────────────────────────────────────────────────────────────

func zoom_to(target_zoom: Vector2, duration: float = 0.4) -> void:
	var tween := create_tween()
	tween.tween_property(self, "zoom", target_zoom, duration).set_trans(Tween.TRANS_SINE)

func lock_to_position(world_pos: Vector2, duration: float = 1.0) -> void:
	set_as_top_level(true)
	var tween := create_tween()
	tween.tween_property(self, "global_position", world_pos, duration)
	EventBus.camera_locked.emit()

func release_lock() -> void:
	set_as_top_level(false)
	position = Vector2.ZERO
	EventBus.camera_released.emit()

func _on_zone_entered(_zone_id: String) -> void:
	pass
