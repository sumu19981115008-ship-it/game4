extends Node

const PLAYER      : int = 1        # bit 0 -> value 1
const NPC         : int = 1 << 1   # bit 1 -> value 2
const WALL        : int = 1 << 2   # bit 2 -> value 4
const TRIGGER     : int = 1 << 3   # bit 3 -> value 8
const WILD_ZONE   : int = 1 << 4   # bit 4 -> value 16
const ITEM        : int = 1 << 5   # bit 5 -> value 32
const PROJECTILE  : int = 1 << 6   # bit 6 -> value 64
const CAMERA_ZONE : int = 1 << 7   # bit 7 -> value 128
