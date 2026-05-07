# settings.py

# =========================
# 기본 화면 설정
# =========================

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

TITLE = "Tower Defense"


# =========================
# 격자 / 맵 설정
# =========================

TILE_SIZE = 40

GRID_COLS = 16
GRID_ROWS = 12

GRID_WIDTH = GRID_COLS * TILE_SIZE
GRID_HEIGHT = GRID_ROWS * TILE_SIZE

GRID_OFFSET_X = 40
GRID_OFFSET_Y = 80


# =========================
# UI 영역 설정
# =========================

HUD_HEIGHT = 70
SIDE_PANEL_WIDTH = 240

MAP_AREA_WIDTH = GRID_WIDTH
MAP_AREA_HEIGHT = GRID_HEIGHT


# =========================
# 색상 설정
# =========================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BACKGROUND_COLOR = (25, 30, 35)

GRID_LINE_COLOR = (55, 65, 70)

EMPTY_TILE_COLOR = (70, 95, 80)
PATH_TILE_COLOR = (210, 175, 95)
OBSTACLE_TILE_COLOR = (90, 75, 65)
START_TILE_COLOR = (80, 190, 110)
CASTLE_TILE_COLOR = (200, 70, 70)

HUD_BG_COLOR = (35, 40, 45)
PANEL_BG_COLOR = (45, 50, 55)

TEXT_COLOR = (240, 240, 240)
WARNING_COLOR = (230, 90, 80)
SUCCESS_COLOR = (90, 210, 120)


# =========================
# 타일 타입
# =========================

EMPTY = 0
PATH = 1
START = 2
CASTLE = 3
OBSTACLE = 4
TOWER = 5


# =========================
# 게임 기본 수치
# =========================

START_GOLD = 300
START_CASTLE_HP = 20

WAVE_CLEAR_BONUS = 50


# =========================
# 타워 기본 설정
# =========================

TOWER_MAX_MERGE_LEVEL = 3
TOWER_MAX_UPGRADE_LEVEL = 5

TOWER_TYPES = {
    "archer": {
        "name": "Archer",
        "cost": 80,
        "damage": 15,
        "range": 130,
        "attack_speed": 0.55,
        "projectile_speed": 360,
        "color": (80, 180, 255),
    },
    "cannon": {
        "name": "Cannon",
        "cost": 120,
        "damage": 35,
        "range": 110,
        "attack_speed": 1.25,
        "projectile_speed": 250,
        "color": (230, 130, 70),
        "splash_radius": 55,
    },
    "frost": {
        "name": "Frost",
        "cost": 100,
        "damage": 8,
        "range": 120,
        "attack_speed": 0.85,
        "projectile_speed": 300,
        "color": (120, 220, 255),
        "slow_ratio": 0.45,
        "slow_duration": 1.5,
    },
}


# =========================
# 적 기본 설정
# =========================

ENEMY_TYPES = {
    "goblin": {
        "name": "Goblin",
        "hp": 45,
        "speed": 75,
        "reward": 10,
        "damage_to_castle": 1,
        "color": (90, 220, 100),
    },
    "orc": {
        "name": "Orc",
        "hp": 95,
        "speed": 55,
        "reward": 18,
        "damage_to_castle": 2,
        "color": (80, 160, 90),
    },
    "troll": {
        "name": "Troll",
        "hp": 180,
        "speed": 38,
        "reward": 30,
        "damage_to_castle": 3,
        "color": (120, 100, 80),
    },
    "boss": {
        "name": "Boss",
        "hp": 650,
        "speed": 32,
        "reward": 120,
        "damage_to_castle": 6,
        "color": (180, 60, 180),
    },
}


# =========================
# 파일 경로
# =========================

WAVE_DATA_PATH = "data/waves.json"
SAVE_DATA_PATH = "data/save.json"
RANKING_DATA_PATH = "data/ranking.json"


# =========================
# 폰트 설정
# =========================

FONT_NAME = None
FONT_SIZE_SMALL = 18
FONT_SIZE_NORMAL = 24
FONT_SIZE_LARGE = 40