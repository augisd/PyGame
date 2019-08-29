from settings import *
from playermodel import *


class GameAdapter:
    def __init__(self, game, player_model):
        self.game = game
        self.player_model = player_model

    def adapt_explorer_tendency(self):
        self.game.map.n_coins = self.player_model.explorer.tendency + N_COINS
        #self.game.map.wall_range = int(self.player_model.explorer.tendency)

        if self.player_model.explorer.tendency > self.player_model.explorer.previous_tendency:
            #self.game.map.grid = self.game.map.make_grid()
            self.game.map.reveal_walls(int(self.player_model.explorer.tendency))

        if self.player_model.explorer.tendency < self.player_model.explorer.previous_tendency:
            #self.game.map.grid = self.game.map.make_grid()
            self.game.map.hide_walls(int(round(self.player_model.explorer.tendency)))

        self.player_model.explorer.previous_tendency = self.player_model.explorer.tendency

    def adapt_explorer_skill(self):
        self.game.map.coin_spawn_distance = self.player_model.explorer.skill + SPAWN_DIST_COINS
        if self.game.map.coin_spawn_distance > MAPGRIDWIDTH - 30:
            self.game.map.coin_spawn_distance = MAPGRIDWIDTH - 30


    def adapt_killer_tendency(self):
        self.game.map.n_enemies = int(self.player_model.killer.tendency + N_ENEMIES)

        #for enemy in self.game.enemies:
        #    new_state = self.player_model.killer.tendency // 10
        #    if new_state > 3:
        #        new_state = 3
        #    enemy.state = new_state

    def adapt_killer_skill(self):
        bot_delay = (self.player_model.killer.skill / 10)
        for enemy in self.game.enemies:
            enemy.action_update_time = 10 / self.player_model.killer.skill

        self.game.map.enemy_spawn_distance = int(self.player_model.killer.skill) + SPAWN_DIST_ENEMIES
        if self.game.map.enemy_spawn_distance > MAPGRIDWIDTH - 30:
            self.game.map.enemy_spawn_distance = MAPGRIDWIDTH - 30

    def update(self):
        self.adapt_explorer_tendency()
        self.adapt_explorer_skill()

        self.adapt_killer_tendency()
        self.adapt_killer_skill()