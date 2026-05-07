# scenes/gameover.py

import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TEXT_COLOR, BACKGROUND_COLOR, SUCCESS_COLOR, WARNING_COLOR
from ui.buttons import Button


class GameOverScene:
    def __init__(self, game, victory=False, score=0):
        self.game = game
        self.victory = victory
        self.score = score

        self.title_font = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 32)

        self.name = ""
        self.saved = False

        button_width = 240
        button_height = 48
        x = SCREEN_WIDTH // 2 - button_width // 2

        self.save_button = Button(
            x=x,
            y=390,
            width=button_width,
            height=button_height,
            text="Save Score",
            on_click=self.save_score,
        )

        self.title_button = Button(
            x=x,
            y=455,
            width=button_width,
            height=button_height,
            text="Back to Title",
            on_click=self.back_to_title,
        )

        self.buttons = [self.save_button, self.title_button]

    def save_score(self):
        if self.saved:
            return

        name = self.name.strip()

        if not name:
            name = "Player"

        self.game.save_ranking(name, self.score)
        self.saved = True
        self.save_button.set_text("Saved")

    def back_to_title(self):
        self.game.change_scene("title")

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if not self.saved:
                    if event.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]

                    elif event.key == pygame.K_RETURN:
                        self.save_score()

                    else:
                        if len(self.name) < 12 and event.unicode.isprintable():
                            self.name += event.unicode

            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        for button in self.buttons:
            button.update()

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)

        if self.victory:
            title = "VICTORY"
            title_color = SUCCESS_COLOR
        else:
            title = "DEFEAT"
            title_color = WARNING_COLOR

        title_text = self.title_font.render(title, True, title_color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)

        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 240))
        screen.blit(score_text, score_rect)

        guide = self.font.render("Enter your name:", True, TEXT_COLOR)
        guide_rect = guide.get_rect(center=(SCREEN_WIDTH // 2, 300))
        screen.blit(guide, guide_rect)

        name_text = self.font.render(self.name if self.name else "_", True, TEXT_COLOR)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 340))
        screen.blit(name_text, name_rect)

        for button in self.buttons:
            button.draw(screen)