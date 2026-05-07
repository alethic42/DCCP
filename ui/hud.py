# ui/hud.py

import pygame

from settings import (
    SCREEN_WIDTH,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    GRID_WIDTH,
    GRID_HEIGHT,
    HUD_BG_COLOR,
    PANEL_BG_COLOR,
    TEXT_COLOR,
    WARNING_COLOR,
    SUCCESS_COLOR,
    FONT_SIZE_SMALL,
    FONT_SIZE_NORMAL,
    FONT_SIZE_LARGE,
    TOWER_TYPES,
)

from ui.buttons import TowerButton, Button


class HUD:
    def __init__(self):
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.font_normal = pygame.font.Font(None, FONT_SIZE_NORMAL)
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)

        self.selected_tower_type = None
        self.message = ""

        self.tower_buttons = []
        self.action_buttons = []

        self.create_tower_buttons()
        self.create_action_buttons()

    def create_tower_buttons(self):
        x = GRID_OFFSET_X + GRID_WIDTH + 25
        y = GRID_OFFSET_Y + 45
        size = 72
        gap = 14

        for index, (tower_type, data) in enumerate(TOWER_TYPES.items()):
            button = TowerButton(
                x=x,
                y=y + index * (size + gap),
                size=size,
                tower_type=tower_type,
                cost=data["cost"],
                on_click=lambda t=tower_type: self.select_tower_type(t),
            )
            self.tower_buttons.append(button)

    def create_action_buttons(self):
        x = GRID_OFFSET_X + GRID_WIDTH + 25
        y = GRID_OFFSET_Y + 340

        self.upgrade_button = Button(
            x=x,
            y=y,
            width=160,
            height=36,
            text="Upgrade",
            font_size=22,
        )

        self.sell_button = Button(
            x=x,
            y=y + 46,
            width=160,
            height=36,
            text="Sell",
            font_size=22,
        )

        self.merge_button = Button(
            x=x,
            y=y + 92,
            width=160,
            height=36,
            text="Merge",
            font_size=22,
        )

        self.action_buttons = [
            self.upgrade_button,
            self.sell_button,
            self.merge_button,
        ]

    def select_tower_type(self, tower_type):
        if self.selected_tower_type == tower_type:
            self.selected_tower_type = None
        else:
            self.selected_tower_type = tower_type

        for button in self.tower_buttons:
            button.selected = button.tower_type == self.selected_tower_type

    def clear_selected_tower_type(self):
        self.selected_tower_type = None

        for button in self.tower_buttons:
            button.selected = False

    def handle_event(self, event):
        for button in self.tower_buttons:
            if button.handle_event(event):
                return True

        for button in self.action_buttons:
            if button.handle_event(event):
                return True

        return False

    def update(self):
        for button in self.tower_buttons:
            button.update()

        for button in self.action_buttons:
            button.update()

    def draw(
        self,
        screen,
        gold,
        castle_hp,
        wave_number,
        total_waves,
        selected_tower=None,
        wave_message="",
        paused=False,
    ):
        self.draw_top_bar(screen, gold, castle_hp, wave_number, total_waves)
        self.draw_side_panel(screen, selected_tower)
        self.draw_buttons(screen)
        self.draw_message(screen, wave_message)

        if paused:
            self.draw_pause_overlay(screen)

    def draw_top_bar(self, screen, gold, castle_hp, wave_number, total_waves):
        rect = pygame.Rect(0, 0, SCREEN_WIDTH, 60)
        pygame.draw.rect(screen, HUD_BG_COLOR, rect)

        gold_text = self.font_normal.render(f"Gold: {gold}", True, TEXT_COLOR)
        hp_text = self.font_normal.render(f"Castle HP: {castle_hp}", True, TEXT_COLOR)
        wave_text = self.font_normal.render(
            f"Wave: {wave_number}/{total_waves}",
            True,
            TEXT_COLOR,
        )

        screen.blit(gold_text, (30, 20))
        screen.blit(hp_text, (190, 20))
        screen.blit(wave_text, (410, 20))

    def draw_side_panel(self, screen, selected_tower):
        panel_x = GRID_OFFSET_X + GRID_WIDTH
        panel_rect = pygame.Rect(panel_x, 60, SCREEN_WIDTH - panel_x, GRID_HEIGHT + 20)

        pygame.draw.rect(screen, PANEL_BG_COLOR, panel_rect)

        title = self.font_normal.render("TOWERS", True, TEXT_COLOR)
        screen.blit(title, (panel_x + 25, GRID_OFFSET_Y + 10))

        if selected_tower is not None:
            self.draw_selected_tower_info(screen, selected_tower, panel_x)
        else:
            guide_lines = [
                "Select tower",
                "then click",
                "an empty tile.",
            ]

            for i, line in enumerate(guide_lines):
                text = self.font_small.render(line, True, TEXT_COLOR)
                screen.blit(text, (panel_x + 25, GRID_OFFSET_Y + 285 + i * 22))

    def draw_selected_tower_info(self, screen, tower, panel_x):
        y = GRID_OFFSET_Y + 285

        lines = [
            f"Selected: {tower.name}",
            f"Merge Lv: {tower.merge_level}",
            f"Upgrade Lv: {tower.upgrade_level}",
            f"Damage: {tower.damage}",
            f"Range: {tower.range}",
            f"Upgrade: {tower.upgrade_cost}",
            f"Sell: {tower.sell_value}",
        ]

        for i, line in enumerate(lines):
            text = self.font_small.render(line, True, TEXT_COLOR)
            screen.blit(text, (panel_x + 25, y + i * 22))

    def draw_buttons(self, screen):
        for button in self.tower_buttons:
            button.draw(screen)

        for button in self.action_buttons:
            button.draw(screen)

    def draw_message(self, screen, wave_message):
        if not wave_message:
            return

        text = self.font_small.render(wave_message, True, SUCCESS_COLOR)
        screen.blit(text, (30, 620))

    def draw_pause_overlay(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, 640), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        text = self.font_large.render("PAUSED", True, WARNING_COLOR)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 320))
        screen.blit(text, rect)