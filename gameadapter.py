from settings import *
from playermodel import *

class TendencyAdapter:
    pass


class SkillAdapter:
    pass


class GameAdapter:
    def __init__(self, game, player_model):
        self.game = game
        self.player_model = player_model

    def adapt_explorer_tendency(self):
        self.game.map.n_coins = self.player_model.explorer.tendency + N_COINS

    def adapt_explorer_skill(self):
        self.game.map.coin_spawn_distance = self.player_model.explorer.skill * 3 + SPAWN_DIST_COINS
        if self.game.map.coin_spawn_distance > MAPGRIDWIDTH - 30:
            self.game.map.coin_spawn_distance = MAPGRIDWIDTH - 30

    def adapt_killer_tendency(self):
        self.game.map.n_enemies = self.player_model.killer.enemies_killed // 10 + N_ENEMIES

    def adapt_killer_skill(self):
        pass

    def update(self):
        self.adapt_explorer_tendency()
        self.adapt_explorer_skill()