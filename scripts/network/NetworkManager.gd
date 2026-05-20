# 联机系统预留模块
# 当前版本：单机模式，所有方法为空实现
# 未来联机版本需实现：
#   - 房间创建/加入（ENet/WebRTC）
#   - 战斗行动同步（BattleAction 序列化）
#   - 玩家状态同步（MultiplayerSynchronizer）
#   - 断线重连机制
#   - 反作弊（服务端伤害计算验证）

extends Node

enum NetworkMode {
	OFFLINE,      # 单机
	HOST,         # 主机
	CLIENT,       # 客户端
	DEDICATED     # 独立服务器（未来）
}

var current_mode: NetworkMode = NetworkMode.OFFLINE
var local_peer_id: int = 1
var connected_peers: Array[int] = []

signal peer_connected(peer_id: int)
signal peer_disconnected(peer_id: int)
signal connection_failed
signal server_disconnected

func is_online() -> bool:
	return current_mode != NetworkMode.OFFLINE

func is_host() -> bool:
	return current_mode == NetworkMode.HOST

func is_client() -> bool:
	return current_mode == NetworkMode.CLIENT

# TODO: 实现联机时填充以下方法
func host_game(_port: int = 7777) -> void:
	push_warning("NetworkManager: 联机功能尚未实现")

func join_game(_address: String, _port: int = 7777) -> void:
	push_warning("NetworkManager: 联机功能尚未实现")

func disconnect_from_game() -> void:
	current_mode = NetworkMode.OFFLINE
	connected_peers.clear()

# 联机战斗行动广播（预留接口）
func broadcast_battle_action(_action: Dictionary) -> void:
	if not is_online():
		return
	# TODO: RPC广播战斗行动

# 玩家位置同步（预留接口）
func sync_player_position(_position: Vector2) -> void:
	if not is_online():
		return
	# TODO: MultiplayerSynchronizer 驱动
