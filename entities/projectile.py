# entities/projectile.py

import math
import pygame


class Projectile:
    def __init__(
        self,
        x,
        y,
        target,
        damage,
        speed,
        color,
        splash_radius=0,
        slow_ratio=None,
        slow_duration=0,
    ):
        self.x = float(x)
        self.y = float(y)

        self.target = target

        self.damage = damage
        self.speed = speed
        self.color = color

        self.splash_radius = splash_radius
        self.slow_ratio = slow_ratio
        self.slow_duration = slow_duration

        self.radius = 5
        self.alive = True

    def update(self, dt, enemies):
        if not self.alive:
            return

        if self.target is None or not self.target.alive:
            self.alive = False
            return

        target_x, target_y = self.target.get_position()

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance == 0:
            self.hit(enemies)
            return

        move_distance = self.speed * dt

        if move_distance >= distance:
            self.x = target_x
            self.y = target_y
            self.hit(enemies)
        else:
            self.x += dx / distance * move_distance
            self.y += dy / distance * move_distance

    def hit(self, enemies):
        if self.splash_radius > 0:
            self.apply_splash_damage(enemies)
        else:
            self.apply_single_damage(self.target)

        self.alive = False

    def apply_single_damage(self, enemy):
        if enemy is None or not enemy.alive:
            return

        enemy.take_damage(self.damage)

        if self.slow_ratio is not None and self.slow_duration > 0:
            enemy.apply_slow(self.slow_ratio, self.slow_duration)

    def apply_splash_damage(self, enemies):
        for enemy in enemies:
            if not enemy.alive:
                continue

            enemy_x, enemy_y = enemy.get_position()
            distance = math.hypot(enemy_x - self.x, enemy_y - self.y)

            if distance <= self.splash_radius:
                enemy.take_damage(self.damage)

    def draw(self, screen):
        if not self.alive:
            return

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            self.radius,
        )

        if self.splash_radius > 0:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.x), int(self.y)),
                self.radius + 2,
                1,
            )