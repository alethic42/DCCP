# systems/wave_manager.py

import json
import os
import pygame

from settings import WAVE_DATA_PATH, WAVE_CLEAR_BONUS
from entities.enemy import Enemy


class WaveManager:
    def __init__(self, path):
        self.path = path

        self.waves = self.load_waves()
        self.current_wave_index = 0

        self.spawn_queue = []
        self.spawn_timer = 0
        self.spawn_interval = 0.8

        self.wave_active = False
        self.all_waves_cleared = False

        self.waiting_for_next_wave = True
        self.message = "Press SPACE to start wave"

    def load_waves(self):
        if os.path.exists(WAVE_DATA_PATH):
            with open(WAVE_DATA_PATH, "r", encoding="utf-8") as file:
                return json.load(file)

        return self.default_waves()

    def default_waves(self):
        return [
            {
                "wave": 1,
                "enemies": [
                    {"type": "goblin", "count": 8, "interval": 0.7}
                ],
            },
            {
                "wave": 2,
                "enemies": [
                    {"type": "goblin", "count": 10, "interval": 0.6},
                    {"type": "orc", "count": 4, "interval": 0.9},
                ],
            },
            {
                "wave": 3,
                "enemies": [
                    {"type": "goblin", "count": 12, "interval": 0.5},
                    {"type": "orc", "count": 8, "interval": 0.8},
                ],
            },
            {
                "wave": 4,
                "enemies": [
                    {"type": "orc", "count": 10, "interval": 0.7},
                    {"type": "troll", "count": 4, "interval": 1.0},
                ],
            },
            {
                "wave": 5,
                "enemies": [
                    {"type": "goblin", "count": 10, "interval": 0.4},
                    {"type": "orc", "count": 8, "interval": 0.6},
                    {"type": "troll", "count": 5, "interval": 0.9},
                    {"type": "boss", "count": 1, "interval": 1.5},
                ],
            },
        ]

    def start_next_wave(self):
        if self.wave_active:
            return False

        if self.current_wave_index >= len(self.waves):
            self.all_waves_cleared = True
            return False

        wave_data = self.waves[self.current_wave_index]

        self.spawn_queue = []

        for group in wave_data["enemies"]:
            enemy_type = group["type"]
            count = group["count"]
            interval = group.get("interval", 0.8)

            for _ in range(count):
                self.spawn_queue.append(
                    {
                        "type": enemy_type,
                        "interval": interval,
                    }
                )

        self.spawn_timer = 0
        self.wave_active = True
        self.waiting_for_next_wave = False

        self.message = f"Wave {self.current_wave_number()} started!"

        return True

    def update(self, dt, enemies):
        if not self.wave_active:
            return 0

        spawned_count = 0

        if self.spawn_queue:
            self.spawn_timer -= dt

            if self.spawn_timer <= 0:
                enemy_data = self.spawn_queue.pop(0)
                enemy = Enemy(enemy_data["type"], self.path)
                enemies.append(enemy)

                self.spawn_timer = enemy_data["interval"]
                spawned_count += 1

        if not self.spawn_queue and self.no_alive_enemies(enemies):
            self.finish_current_wave()

        return spawned_count

    def no_alive_enemies(self, enemies):
        for enemy in enemies:
            if enemy.alive:
                return False

        return True

    def finish_current_wave(self):
        self.wave_active = False
        self.current_wave_index += 1

        if self.current_wave_index >= len(self.waves):
            self.all_waves_cleared = True
            self.waiting_for_next_wave = False
            self.message = "All waves cleared!"
        else:
            self.waiting_for_next_wave = True
            self.message = "Wave cleared! Press SPACE for next wave"

    def current_wave_number(self):
        return self.current_wave_index + 1

    def total_waves(self):
        return len(self.waves)

    def get_wave_bonus(self):
        return WAVE_CLEAR_BONUS

    def set_path(self, new_path):
        self.path = new_path

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return self.start_next_wave()

        return False

    def is_finished(self):
        return self.all_waves_cleared

    def get_state_data(self):
        return {
            "current_wave_index": self.current_wave_index,
            "wave_active": self.wave_active,
            "waiting_for_next_wave": self.waiting_for_next_wave,
            "all_waves_cleared": self.all_waves_cleared,
        }

    def load_state_data(self, data):
        self.current_wave_index = data.get("current_wave_index", 0)
        self.wave_active = data.get("wave_active", False)
        self.waiting_for_next_wave = data.get("waiting_for_next_wave", True)
        self.all_waves_cleared = data.get("all_waves_cleared", False)