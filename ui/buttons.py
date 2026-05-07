# ui/buttons.py

import pygame

from settings import TEXT_COLOR, PANEL_BG_COLOR, SUCCESS_COLOR, WARNING_COLOR


class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text="",
        on_click=None,
        font_size=24,
        bg_color=PANEL_BG_COLOR,
        hover_color=None,
        text_color=TEXT_COLOR,
        border_color=None,
    ):
        self.rect = pygame.Rect(x, y, width, height)

        self.text = text
        self.on_click = on_click

        self.font = pygame.font.Font(None, font_size)

        self.bg_color = bg_color
        self.hover_color = hover_color if hover_color else self._brighten(bg_color, 30)
        self.text_color = text_color
        self.border_color = border_color

        self.enabled = True
        self.visible = True

        self.hovered = False

    def _brighten(self, color, amount):
        return tuple(min(255, c + amount) for c in color)

    def handle_event(self, event):
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                if self.on_click:
                    self.on_click()
                return True

        return False

    def update(self):
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        if not self.visible:
            return

        color = self.hover_color if self.hovered else self.bg_color

        pygame.draw.rect(screen, color, self.rect, border_radius=6)

        if self.border_color:
            pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=6)

        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def set_enabled(self, enabled):
        self.enabled = enabled

    def set_visible(self, visible):
        self.visible = visible

    def set_text(self, text):
        self.text = text


class ToggleButton(Button):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text_on="ON",
        text_off="OFF",
        initial=False,
        on_toggle=None,
        **kwargs,
    ):
        super().__init__(x, y, width, height, **kwargs)

        self.text_on = text_on
        self.text_off = text_off

        self.state = initial
        self.on_toggle = on_toggle

        self.update_text()

    def update_text(self):
        self.text = self.text_on if self.state else self.text_off

    def handle_event(self, event):
        if super().handle_event(event):
            self.state = not self.state
            self.update_text()

            if self.on_toggle:
                self.on_toggle(self.state)

            return True

        return False


class TowerButton(Button):
    def __init__(
        self,
        x,
        y,
        size,
        tower_type,
        cost,
        on_click=None,
        **kwargs,
    ):
        super().__init__(
            x,
            y,
            size,
            size,
            text="",
            on_click=on_click,
            **kwargs,
        )

        self.tower_type = tower_type
        self.cost = cost

        self.selected = False

    def draw(self, screen):
        if not self.visible:
            return

        color = self.hover_color if self.hovered else self.bg_color

        pygame.draw.rect(screen, color, self.rect, border_radius=6)

        if self.selected:
            pygame.draw.rect(screen, SUCCESS_COLOR, self.rect, 3, border_radius=6)

        elif self.border_color:
            pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=6)

        font = pygame.font.Font(None, 20)

        text_surf = font.render(self.tower_type.upper(), True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery - 8))
        screen.blit(text_surf, text_rect)

        cost_surf = font.render(f"{self.cost}", True, WARNING_COLOR)
        cost_rect = cost_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 12))
        screen.blit(cost_surf, cost_rect)