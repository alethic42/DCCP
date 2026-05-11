# entities/enemy.py

import math
import pygame

from settings import TILE_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y, ENEMY_TYPES


class Enemy:
    def __init__(self, enemy_type, path):
        if enemy_type not in ENEMY_TYPES:
            raise ValueError(f"Unknown enemy type: {enemy_type}")

        self.enemy_type = enemy_type
        data = ENEMY_TYPES[enemy_type]

        self.name = data["name"]
        self.max_hp = data["hp"]
        self.hp = self.max_hp
        self.base_speed = data["speed"]
        self.speed = self.base_speed
        self.reward = data["reward"]
        self.damage_to_castle = data["damage_to_castle"]
        self.color = data["color"]

        self.path = path
        self.path_index = 0

        self.radius = 13 if enemy_type != "boss" else 20

        self.alive = True
        self.reached_castle = False

        self.slow_timer = 0
        self.slow_ratio = 1.0

        self.x, self.y = self.grid_to_center(path[0])

    def grid_to_center(self, grid_pos):
        col, row = grid_pos
        x = GRID_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2
        y = GRID_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2
        return float(x), float(y)

    def update(self, dt):
        if not self.alive:
            return

        self.update_slow(dt)
        self.move(dt)

    def update_slow(self, dt):
        if self.slow_timer > 0:
            self.slow_timer -= dt

            if self.slow_timer <= 0:
                self.speed = self.base_speed
                self.slow_ratio = 1.0

    def move(self, dt):
        if self.path_index >= len(self.path) - 1:
            self.reach_castle()
            return

        target_pos = self.path[self.path_index + 1]
        target_x, target_y = self.grid_to_center(target_pos)

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance == 0:
            self.path_index += 1
            return

        move_distance = self.speed * dt

        if move_distance >= distance:
            self.x = target_x
            self.y = target_y
            self.path_index += 1
        else:
            self.x += dx / distance * move_distance
            self.y += dy / distance * move_distance

    def take_damage(self, damage):
        if not self.alive:
            return False

        self.hp -= damage

        if self.hp <= 0:
            self.hp = 0
            self.die()
            return True

        return False

    def apply_slow(self, ratio, duration):
        if not self.alive:
            return

        self.slow_ratio = ratio
        self.speed = self.base_speed * ratio
        self.slow_timer = duration

    def die(self):
        self.alive = False

    def reach_castle(self):
        self.alive = False
        self.reached_castle = True

    def set_new_path(self, new_path):
        """
        타워 설치/판매로 경로가 바뀌었을 때 호출한다.
        현재 위치에서 가장 가까운 경로 지점부터 다시 따라가게 한다.
        """
        if not new_path:
            return

        self.path = new_path

        nearest_index = 0
        nearest_distance = float("inf")

        for i, grid_pos in enumerate(new_path):
            px, py = self.grid_to_center(grid_pos)
            dist = math.hypot(px - self.x, py - self.y)

            if dist < nearest_distance:
                nearest_distance = dist
                nearest_index = i

        self.path_index = nearest_index

    def get_position(self):
        return self.x, self.y

    def get_progress(self):
        """
        타워가 '가장 앞선 적'을 고를 때 사용할 수 있는 값.
        값이 클수록 성에 가까운 적이다.
        """
        return self.path_index

    def get_state_data(self):
        return {
            "enemy_type": self.enemy_type,
            "hp": self.hp,
            "x": self.x,
            "y": self.y,
            "path_index": self.path_index,
            "slow_timer": self.slow_timer,
            "slow_ratio": self.slow_ratio,
            "speed": self.speed,
        }

    def load_state_data(self, data):
        self.hp = min(data.get("hp", self.max_hp), self.max_hp)
        self.x = float(data.get("x", self.x))
        self.y = float(data.get("y", self.y))
        self.path_index = data.get("path_index", self.path_index)
        self.slow_timer = data.get("slow_timer", 0)
        self.slow_ratio = data.get("slow_ratio", 1.0)
        self.speed = data.get("speed", self.base_speed)

        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def draw(self, screen):
        if not self.alive:
            return

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            self.radius,
        )

        self.draw_hp_bar(screen)

    def draw_hp_bar(self, screen):
        bar_width = self.radius * 2
        bar_height = 5

        x = self.x - bar_width / 2
        y = self.y - self.radius - 10

        hp_ratio = self.hp / self.max_hp

        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        hp_rect = pygame.Rect(x, y, bar_width * hp_ratio, bar_height)

        pygame.draw.rect(screen, (60, 60, 60), bg_rect)
        pygame.draw.rect(screen, (220, 60, 60), hp_rect)
