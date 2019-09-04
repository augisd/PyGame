from settings import *
from playermodel import *

class GameAdapterBot:
    """goal of this class is to track performance of the bots. tendency is tracker is
        the same as that of the player, while skill is increased automatically """
    def __init__(self, game, bot_model):
        self.game = game
        self.bot_model = bot_model
        self.walls_revealed = {1 : False}

    def adapt_tendency(self):

        # Explorer
        self.game.map.n_coins = self.bot_model.explorer.tendency + N_COINS
        """
        if (self.bot_model.explorer.tendency > self.bot_model.explorer.previous_tendency and
            self.bot_model.explorer.tendency < 50):
            self.game.map.reveal_walls(int(self.bot_model.explorer.tendency))
        """
        if (self.bot_model.explorer.tendency > self.bot_model.explorer.previous_tendency and
            self.bot_model.explorer.tendency < 50 and
            not self.game.map.wall_dict_flags[int(self.bot_model.explorer.tendency)]):

            self.game.map.reveal_walls(int(self.bot_model.explorer.tendency))
            self.game.map.wall_dict_flags[int(self.bot_model.explorer.tendency)] = True

        # Killer
        self.game.map.n_enemies = int(self.bot_model.killer.tendency + N_ENEMIES)

    def adapt_skill(self):

        # Explorer
        self.game.map.coin_spawn_distance = self.bot_model.explorer.skill + SPAWN_DIST_COINS

        # Killer
        self.game.map.enemy_spawn_distance = self.bot_model.killer.skill + SPAWN_DIST_ENEMIES

        bot_delay = (self.bot_model.killer.skill / 10)
        for enemy in self.game.enemies:
            enemy.action_update_time = 10 / self.bot_model.killer.skill

    def update(self):
        self.adapt_tendency()
        self.adapt_skill()

class GameAdapter:
    def __init__(self, game, player_model):
        self.game = game
        self.player_model = player_model

    def adapt_explorer_tendency(self):
        self.game.map.n_coins = self.player_model.explorer.tendency + N_COINS
        #self.game.map.wall_range = int(self.player_model.explorer.tendency)
        if (self.player_model.explorer.tendency > self.player_model.explorer.previous_tendency and
            self.player_model.explorer.tendency < 50 and
            not self.game.map.wall_dict_flags[int(self.player_model.explorer.tendency)]):

            self.game.map.reveal_walls(int(round(self.player_model.explorer.tendency)))
            self.game.map.wall_dict_flags[int(self.player_model.explorer.tendency)] = True

        elif (self.player_model.explorer.tendency < self.player_model.explorer.previous_tendency and
            self.player_model.explorer.tendency > 0 and
            self.game.map.wall_dict_flags[int(self.player_model.explorer.tendency)]):

            self.game.map.hide_walls(int(round(self.player_model.explorer.tendency)))
            self.game.map.wall_dict_flags[int(self.player_model.explorer.tendency)] = False

        self.player_model.explorer.previous_tendency = self.player_model.explorer.tendency

    def adapt_explorer_skill(self):
        self.game.map.coin_spawn_distance = self.player_model.explorer.skill + SPAWN_DIST_COINS
        if self.game.map.coin_spawn_distance > MAPGRIDWIDTH - 30:
            self.game.map.coin_spawn_distance = MAPGRIDWIDTH - 30

    def adapt_killer_tendency(self):
        self.game.map.n_enemies = int(self.player_model.killer.tendency + N_ENEMIES)

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