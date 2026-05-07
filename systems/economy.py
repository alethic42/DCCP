# systems/economy.py

from settings import START_GOLD, START_CASTLE_HP


class Economy:
    def __init__(self):
        self.gold = START_GOLD
        self.castle_hp = START_CASTLE_HP

    def can_afford(self, amount):
        return self.gold >= amount

    def spend_gold(self, amount):
        if amount <= 0:
            return True

        if self.can_afford(amount):
            self.gold -= amount
            return True

        return False

    def add_gold(self, amount):
        if amount > 0:
            self.gold += amount

    def damage_castle(self, damage):
        if damage <= 0:
            return

        self.castle_hp -= damage

        if self.castle_hp < 0:
            self.castle_hp = 0

    def is_defeated(self):
        return self.castle_hp <= 0

    def calculate_score(self, wave_number=0):
        return wave_number * 1000 + self.castle_hp * 100 + self.gold

    def get_state_data(self):
        return {
            "gold": self.gold,
            "castle_hp": self.castle_hp,
        }

    def load_state_data(self, data):
        self.gold = data.get("gold", START_GOLD)
        self.castle_hp = data.get("castle_hp", START_CASTLE_HP)