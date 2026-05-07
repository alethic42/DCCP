# scenes/title.py

import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, TEXT_COLOR, BACKGROUND_COLOR
from ui.buttons import Button


class TitleScene:
    def __init__(self, game):
        self.game = game

        self.title_font = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 32)

        button_width = 220
        button_height = 50
        x = SCREEN_WIDTH // 2 - button_width // 2

        self.start_button = Button(
            x=x,
            y=280,
            width=button_width,
            height=button_height,
            text="Start",
            on_click=self.start_game,
        )

        self.continue_button = Button(
            x=x,
            y=345,
            width=button_width,
            height=button_height,
            text="Continue",
            on_click=self.continue_game,
        )

        self.ranking_button = Button(
            x=x,
            y=410,
            width=button_width,
            height=button_height,
            text="Ranking",
            on_click=self.show_ranking,
        )

        self.quit_button = Button(
            x=x,
            y=475,
            width=button_width,
            height=button_height,
            text="Quit",
            on_click=self.quit_game,
        )

        self.buttons = [
            self.start_button,
            self.continue_button,
            self.ranking_button,
            self.quit_button,
        ]

        self.showing_ranking = False

    def start_game(self):
        self.game.start_new_game()

    def continue_game(self):
        self.game.load_game()

    def show_ranking(self):
        self.showing_ranking = not self.showing_ranking

    def quit_game(self):
        self.game.running = False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.showing_ranking = False

            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        for button in self.buttons:
            button.update()

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)

        title_text = self.title_font.render(TITLE, True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 160))
        screen.blit(title_text, title_rect)

        subtitle = self.font.render("Design. Build. Defend the Castle.", True, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(subtitle, subtitle_rect)

        for button in self.buttons:
            button.draw(screen)

        if self.showing_ranking:
            self.draw_ranking(screen)

    def draw_ranking(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.font.render("Ranking", True, TEXT_COLOR)
        screen.blit(title, (SCREEN_WIDTH // 2 - 50, 120))

        rankings = self.game.load_rankings()

        if not rankings:
            text = self.font.render("No ranking data yet.", True, TEXT_COLOR)
            screen.blit(text, (SCREEN_WIDTH // 2 - 120, 200))
            return

        for i, record in enumerate(rankings[:10]):
            line = f"{i + 1}. {record['name']} - {record['score']}"
            text = self.font.render(line, True, TEXT_COLOR)
            screen.blit(text, (SCREEN_WIDTH // 2 - 150, 180 + i * 34))