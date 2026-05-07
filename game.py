# game.py

import json
import os

from settings import SAVE_DATA_PATH, RANKING_DATA_PATH

from scenes.title import TitleScene
from scenes.play import PlayScene
from scenes.gameover import GameOverScene


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

        self.current_scene_name = "title"
        self.current_scene = TitleScene(self)

    def handle_events(self, events):
        self.current_scene.handle_events(events)

    def update(self, dt):
        self.current_scene.update(dt)

    def draw(self):
        self.current_scene.draw(self.screen)

    def change_scene(self, scene_name, **kwargs):
        self.current_scene_name = scene_name

        if scene_name == "title":
            self.current_scene = TitleScene(self)

        elif scene_name == "play":
            self.current_scene = PlayScene(self, **kwargs)

        elif scene_name == "gameover":
            self.current_scene = GameOverScene(self, **kwargs)

        else:
            raise ValueError(f"Unknown scene: {scene_name}")

    def start_new_game(self):
        self.change_scene("play")

    def load_game(self):
        if not os.path.exists(SAVE_DATA_PATH):
            self.start_new_game()
            return

        try:
            with open(SAVE_DATA_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.change_scene("play", load_data=data)

        except (json.JSONDecodeError, OSError):
            self.start_new_game()

    def end_game(self, victory, score):
        self.change_scene(
            "gameover",
            victory=victory,
            score=score,
        )

    def load_rankings(self):
        if not os.path.exists(RANKING_DATA_PATH):
            return []

        try:
            with open(RANKING_DATA_PATH, "r", encoding="utf-8") as file:
                rankings = json.load(file)

            if isinstance(rankings, list):
                return rankings

        except (json.JSONDecodeError, OSError):
            pass

        return []

    def save_ranking(self, name, score):
        rankings = self.load_rankings()

        rankings.append(
            {
                "name": name,
                "score": score,
            }
        )

        rankings.sort(key=lambda record: record["score"], reverse=True)
        rankings = rankings[:20]

        os.makedirs(os.path.dirname(RANKING_DATA_PATH), exist_ok=True)

        with open(RANKING_DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(rankings, file, indent=4, ensure_ascii=False)