# scenes/play.py

import json
import os
import pygame

from settings import (
    TILE_SIZE,
    GRID_COLS,
    GRID_ROWS,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    EMPTY,
    START,
    CASTLE,
    OBSTACLE,
    TOWER,
    EMPTY_TILE_COLOR,
    PATH_TILE_COLOR,
    START_TILE_COLOR,
    CASTLE_TILE_COLOR,
    OBSTACLE_TILE_COLOR,
    GRID_LINE_COLOR,
    BACKGROUND_COLOR,
    TOWER_TYPES,
    SAVE_DATA_PATH,
)

from systems.pathfinding import PathFinder
from systems.wave_manager import WaveManager
from systems.economy import Economy
from entities.enemy import Enemy
from entities.tower import Tower
from ui.hud import HUD


class PlayScene:
    def __init__(self, game, load_data=None):
        self.game = game

        self.start = (0, 5)
        self.castle = (15, 5)

        self.grid = self.create_stage_one()

        self.pathfinder = PathFinder(self.grid)
        self.path = self.pathfinder.find_path(self.start, self.castle)

        self.economy = Economy()
        self.wave_manager = WaveManager(self.path)

        self.towers = []
        self.enemies = []
        self.projectiles = []

        self.hud = HUD()
        self.hud.upgrade_button.on_click = self.upgrade_selected_tower
        self.hud.sell_button.on_click = self.sell_selected_tower
        self.hud.merge_button.on_click = self.merge_selected_tower
        self.selected_tower = None

        self.dragging_tower = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.drag_start_pos = None

        self.paused = False
        self.message = ""

        if load_data is not None:
            self.load_state(load_data)

    def create_stage_one(self):
        grid = [[EMPTY for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        start_col, start_row = self.start
        castle_col, castle_row = self.castle

        grid[start_row][start_col] = START
        grid[castle_row][castle_col] = CASTLE

        obstacles = [
            (2, 2), (3, 2), (5, 2),
            (6, 4), (8, 8), (9, 8),
            (12, 7), (13, 7),
            (3, 5), (3, 6), (3, 7),
            (7, 3), (7, 4), (7, 5),
            (11, 5), (11, 6), (11, 7),
        ]

        for col, row in obstacles:
            if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
                if grid[row][col] == EMPTY:
                    grid[row][col] = OBSTACLE

        return grid

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.save_game()
                    self.game.change_scene("title")

                elif event.key == pygame.K_p:
                    self.paused = not self.paused

                elif event.key == pygame.K_SPACE and not self.paused:
                    started = self.wave_manager.handle_event(event)
                    if started:
                        self.message = "Wave started"

            if self.hud.handle_event(event):
                continue

            if not self.paused:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_mouse_down(event.pos)

                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.handle_mouse_up(event.pos)

    def handle_mouse_down(self, pos):
        col_row = self.pixel_to_grid(*pos)

        if col_row is None:
            self.clear_tower_selection()
            return

        col, row = col_row
        tower = self.get_tower_at(col, row)

        if tower is not None:
            self.select_tower(tower)
            self.dragging_tower = tower
            self.drag_start_pos = (tower.col, tower.row)

            self.drag_offset_x = pos[0] - tower.x
            self.drag_offset_y = pos[1] - tower.y
            return

        if self.hud.selected_tower_type is not None:
            self.try_place_tower(col, row)
        else:
            self.clear_tower_selection()

    def handle_mouse_motion(self, pos):
        if self.dragging_tower is None:
            return

        self.dragging_tower.x = pos[0] - self.drag_offset_x
        self.dragging_tower.y = pos[1] - self.drag_offset_y

    def handle_mouse_up(self, pos):
        if self.dragging_tower is None:
            return

        dragged = self.dragging_tower
        target = self.get_tower_under_mouse(pos, exclude=dragged)

        if target is not None and dragged.can_merge_with(target):
            self.merge_towers(dragged, target)
            self.message = "Merged!"
        else:
            dragged.x, dragged.y = dragged.grid_to_center(dragged.col, dragged.row)

            if target is not None:
                self.message = "Cannot merge these towers."

        self.dragging_tower = None
        self.drag_start_pos = None

    def try_place_tower(self, col, row):
        tower_type = self.hud.selected_tower_type
        cost = TOWER_TYPES[tower_type]["cost"]

        if self.grid[row][col] != EMPTY:
            self.message = "Only empty tiles can hold towers."
            return

        if not self.pathfinder.can_place_tower(col, row, self.start, self.castle):
            self.message = "Cannot block the path."
            return

        if not self.economy.spend_gold(cost):
            self.message = "Not enough gold."
            return

        tower = Tower(tower_type, col, row)
        self.towers.append(tower)

        self.grid[row][col] = TOWER
        self.recompute_path()

        self.message = f"{tower.name} placed."

    def merge_towers(self, dragged, target):
        target.merge()

        self.grid[dragged.row][dragged.col] = EMPTY

        if dragged in self.towers:
            self.towers.remove(dragged)

        self.selected_tower = target
        target.selected = True
        target.x, target.y = target.grid_to_center(target.col, target.row)

        for tower in self.towers:
            if tower is not target:
                tower.selected = False

        self.recompute_path()

    def upgrade_selected_tower(self):
        tower = self.selected_tower

        if tower is None:
            self.message = "Select a tower first."
            return

        if not tower.can_upgrade():
            self.message = "Tower is already max level."
            return

        if not self.economy.spend_gold(tower.upgrade_cost):
            self.message = "Not enough gold."
            return

        tower.upgrade()
        self.message = f"{tower.name} upgraded."

    def sell_selected_tower(self):
        tower = self.selected_tower

        if tower is None:
            self.message = "Select a tower first."
            return

        self.economy.add_gold(tower.sell_value)
        self.grid[tower.row][tower.col] = EMPTY

        if tower in self.towers:
            self.towers.remove(tower)

        self.selected_tower = None
        tower.selected = False
        self.recompute_path()
        self.message = f"{tower.name} sold."

    def merge_selected_tower(self):
        tower = self.selected_tower

        if tower is None:
            self.message = "Select a tower first."
            return

        for other in self.towers:
            if other is tower:
                continue

            if tower.can_merge_with(other):
                tower.merge()
                self.grid[other.row][other.col] = EMPTY
                self.towers.remove(other)
                self.recompute_path()
                self.message = "Merged!"
                return

        self.message = "No matching tower to merge."

    def get_tower_under_mouse(self, pos, exclude=None):
        x, y = pos

        for tower in self.towers:
            if tower is exclude:
                continue

            if tower.contains_point(x, y):
                return tower

        return None

    def select_tower(self, selected):
        self.selected_tower = selected

        for tower in self.towers:
            tower.selected = tower is selected

    def clear_tower_selection(self):
        self.selected_tower = None

        for tower in self.towers:
            tower.selected = False

    def recompute_path(self):
        self.pathfinder.update_grid(self.grid)
        self.path = self.pathfinder.find_path(self.start, self.castle)

        self.wave_manager.set_path(self.path)

        for enemy in self.enemies:
            if enemy.alive:
                enemy.set_new_path(self.path)

    def update(self, dt):
        self.hud.update()

        if self.paused:
            return

        self.wave_manager.update(dt, self.enemies)

        for enemy in self.enemies:
            enemy.update(dt)

            if enemy.reached_castle:
                self.economy.damage_castle(enemy.damage_to_castle)
                enemy.reached_castle = False

        for tower in self.towers:
            tower.update(dt, self.enemies, self.projectiles)

        for projectile in self.projectiles:
            projectile.update(dt, self.enemies)

        self.handle_dead_enemies()

        self.enemies = [enemy for enemy in self.enemies if enemy.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]

        if self.economy.is_defeated():
            self.clear_save()
            self.game.end_game(
                victory=False,
                score=self.economy.calculate_score(
                    self.wave_manager.current_wave_number()
                ),
            )

        if self.wave_manager.is_finished():
            self.clear_save()
            self.game.end_game(
                victory=True,
                score=self.economy.calculate_score(
                    self.wave_manager.current_wave_number()
                ),
            )

    def handle_dead_enemies(self):
        for enemy in self.enemies:
            if not enemy.alive and not enemy.reached_castle:
                if not hasattr(enemy, "reward_given"):
                    self.economy.add_gold(enemy.reward)
                    enemy.reward_given = True

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)

        self.draw_grid(screen)

        for tower in self.towers:
            tower.draw(screen)

        for enemy in self.enemies:
            enemy.draw(screen)

        for projectile in self.projectiles:
            projectile.draw(screen)

        self.hud.draw(
            screen=screen,
            gold=self.economy.gold,
            castle_hp=self.economy.castle_hp,
            wave_number=self.wave_manager.current_wave_number(),
            total_waves=self.wave_manager.total_waves(),
            selected_tower=self.selected_tower,
            wave_message=self.wave_manager.message or self.message,
            paused=self.paused,
        )

    def draw_grid(self, screen):
        path_set = set(self.path)

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                cell = self.grid[row][col]

                rect = pygame.Rect(
                    GRID_OFFSET_X + col * TILE_SIZE,
                    GRID_OFFSET_Y + row * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )

                if (col, row) in path_set:
                    color = PATH_TILE_COLOR
                elif cell == EMPTY:
                    color = EMPTY_TILE_COLOR
                elif cell == START:
                    color = START_TILE_COLOR
                elif cell == CASTLE:
                    color = CASTLE_TILE_COLOR
                elif cell == OBSTACLE:
                    color = OBSTACLE_TILE_COLOR
                elif cell == TOWER:
                    color = EMPTY_TILE_COLOR
                else:
                    color = EMPTY_TILE_COLOR

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

    def pixel_to_grid(self, x, y):
        col = (x - GRID_OFFSET_X) // TILE_SIZE
        row = (y - GRID_OFFSET_Y) // TILE_SIZE

        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
            return int(col), int(row)

        return None

    def get_tower_at(self, col, row):
        for tower in self.towers:
            if tower.col == col and tower.row == row:
                return tower

        return None

    def save_game(self):
        data = {
            "economy": self.economy.get_state_data(),
            "wave": self.wave_manager.get_state_data(),
            "towers": [
                {
                    "tower_type": tower.tower_type,
                    "col": tower.col,
                    "row": tower.row,
                    "merge_level": tower.merge_level,
                    "upgrade_level": tower.upgrade_level,
                }
                for tower in self.towers
            ],
            "enemies": [
                enemy.get_state_data()
                for enemy in self.enemies
                if enemy.alive
            ],
        }

        os.makedirs(os.path.dirname(SAVE_DATA_PATH), exist_ok=True)

        with open(SAVE_DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_state(self, data):
        self.economy.load_state_data(data.get("economy", {}))

        for tower_data in data.get("towers", []):
            tower = Tower(
                tower_data["tower_type"],
                tower_data["col"],
                tower_data["row"],
            )

            tower.merge_level = tower_data.get("merge_level", 1)
            tower.upgrade_level = tower_data.get("upgrade_level", 1)

            self.towers.append(tower)
            self.grid[tower.row][tower.col] = TOWER

        self.recompute_path()
        self.wave_manager.load_state_data(data.get("wave", {}))
        self.load_enemies(data.get("enemies", []))

    def load_enemies(self, enemies_data):
        if not self.path:
            return

        for enemy_data in enemies_data:
            enemy_type = enemy_data.get("enemy_type")

            if enemy_type is None:
                continue

            enemy = Enemy(enemy_type, self.path)
            enemy.load_state_data(enemy_data)

            if enemy.alive:
                self.enemies.append(enemy)

    def clear_save(self):
        if os.path.exists(SAVE_DATA_PATH):
            os.remove(SAVE_DATA_PATH)
