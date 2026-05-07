# entities/tower.py

import math
import pygame

from settings import (
    TILE_SIZE,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    TOWER_TYPES,
    TOWER_MAX_MERGE_LEVEL,
    TOWER_MAX_UPGRADE_LEVEL,
)

from entities.projectile import Projectile


class Tower:
    def __init__(self, tower_type, col, row):
        if tower_type not in TOWER_TYPES:
            raise ValueError(f"Unknown tower type: {tower_type}")

        self.tower_type = tower_type
        self.col = col
        self.row = row

        data = TOWER_TYPES[tower_type]

        self.name = data["name"]
        self.base_cost = data["cost"]
        self.base_damage = data["damage"]
        self.base_range = data["range"]
        self.base_attack_speed = data["attack_speed"]
        self.projectile_speed = data["projectile_speed"]
        self.color = data["color"]

        self.merge_level = 1
        self.upgrade_level = 1

        self.attack_timer = 0

        self.selected = False

        self.splash_radius = data.get("splash_radius", 0)
        self.slow_ratio = data.get("slow_ratio", None)
        self.slow_duration = data.get("slow_duration", 0)

        self.x, self.y = self.grid_to_center(col, row)

    def grid_to_center(self, col, row):
        x = GRID_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2
        y = GRID_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2
        return float(x), float(y)

    @property
    def damage(self):
        return int(self.base_damage * (1 + 0.35 * (self.merge_level - 1)) * (1 + 0.25 * (self.upgrade_level - 1)))

    @property
    def range(self):
        return int(self.base_range * (1 + 0.08 * (self.upgrade_level - 1)))

    @property
    def attack_speed(self):
        return max(0.15, self.base_attack_speed * (1 - 0.06 * (self.upgrade_level - 1)))

    @property
    def upgrade_cost(self):
        return int(self.base_cost * 0.55 * self.upgrade_level)

    @property
    def sell_value(self):
        return int(self.base_cost * 0.55 + (self.upgrade_level - 1) * self.base_cost * 0.25)

    def update(self, dt, enemies, projectiles):
        if self.attack_timer > 0:
            self.attack_timer -= dt

        if self.attack_timer <= 0:
            target = self.find_target(enemies)

            if target is not None:
                self.attack(target, projectiles)
                self.attack_timer = self.attack_speed

    def find_target(self, enemies):
        candidates = []

        for enemy in enemies:
            if not enemy.alive:
                continue

            enemy_x, enemy_y = enemy.get_position()
            distance = math.hypot(enemy_x - self.x, enemy_y - self.y)

            if distance <= self.range:
                candidates.append(enemy)

        if not candidates:
            return None

        return max(candidates, key=lambda enemy: enemy.get_progress())

    def attack(self, target, projectiles):
        projectile = Projectile(
            x=self.x,
            y=self.y,
            target=target,
            damage=self.damage,
            speed=self.projectile_speed,
            color=self.color,
            splash_radius=self.splash_radius,
            slow_ratio=self.slow_ratio,
            slow_duration=self.slow_duration,
        )

        projectiles.append(projectile)

    def can_merge_with(self, other):
        if other is None:
            return False

        return (
            self.tower_type == other.tower_type
            and self.merge_level == other.merge_level
            and self.merge_level < TOWER_MAX_MERGE_LEVEL
        )

    def merge(self):
        if self.merge_level < TOWER_MAX_MERGE_LEVEL:
            self.merge_level += 1
            return True

        return False

    def can_upgrade(self):
        return self.upgrade_level < TOWER_MAX_UPGRADE_LEVEL

    def upgrade(self):
        if self.can_upgrade():
            self.upgrade_level += 1
            return True

        return False

    def contains_point(self, x, y):
        left = GRID_OFFSET_X + self.col * TILE_SIZE
        top = GRID_OFFSET_Y + self.row * TILE_SIZE

        rect = pygame.Rect(left, top, TILE_SIZE, TILE_SIZE)
        return rect.collidepoint(x, y)

    def draw(self, screen, show_range=False):
        if show_range or self.selected:
            pygame.draw.circle(
                screen,
                (120, 120, 120),
                (int(self.x), int(self.y)),
                self.range,
                1,
            )

        tower_rect = pygame.Rect(
            GRID_OFFSET_X + self.col * TILE_SIZE + 6,
            GRID_OFFSET_Y + self.row * TILE_SIZE + 6,
            TILE_SIZE - 12,
            TILE_SIZE - 12,
        )

        pygame.draw.rect(screen, self.color, tower_rect, border_radius=6)

        if self.selected:
            pygame.draw.rect(screen, (255, 255, 255), tower_rect, 2, border_radius=6)

        self.draw_level_text(screen)

    def draw_level_text(self, screen):
        font = pygame.font.Font(None, 18)

        text = font.render(f"M{self.merge_level}/U{self.upgrade_level}", True, (255, 255, 255))

        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)