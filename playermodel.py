from tabulate import tabulate
import pygame as pg
#from game import Game
from settings import *


class PlayerType():

    def __init__(self, game):
        self.game = game
        self.tendency = 0
        self.skill = 0
        self.tendency_modifier = 0.01
        self.skill_modifier = 0.01
        self.tendency_increment = 5
        self.skill_increment = 5

    def increase_tendency(self):
        self.tendency += self.tendency_increment

    def increase_skill(self):
        self.skill += self.skill_increment

    def get_tendency(self):
        return self.tendency

    def get_skill(self):
        return self.skill

    def update_tendency(self):
        pass

    def update_skill(self):
        pass

    def update(self):
        self.update_tendency()
        self.tendency -= self.tendency_modifier
        self.skill -= self.skill_modifier
        if self.tendency < 0:
            self.tendency = 0
        if self.skill < 0:
            self.skill = 0


class Explorer(PlayerType):
    # Coin pickup event increases tendency
    def __init__(self, game):
        PlayerType.__init__(self, game)

    def update_tendency(self):
        if len(self.game.coins) < N_COINS:
            self.increase_tendency()

class Killer(PlayerType):
    # Enemy kill event increases killer tendency
    def __init__(self, game):
        PlayerType.__init__(self, game)

    def update_tendency(self):
        if len(self.game.enemies) < N_ENEMIES:
            self.increase_tendency()

class Scorer(PlayerType):
    # Both of the above (consecutively, order does not matter)
    def __init__(self, game):
        PlayerType.__init__(self, game)
        self.enemy_killed = False
        self.coin_collected = False

    def update_tendency(self):
        if len(self.game.enemies) < N_ENEMIES:
            self.enemy_killed = True
            if self.coin_collected:
                self.increase_tendency()

        if self.enemy_killed and len(self.game.enemies) < N_ENEMIES:
            self.coin_collected = False

        if len(self.game.coins) < N_COINS:
            self.coin_collected = True
            if self.enemy_killed:
                self.increase_tendency()

        if self.coin_collected and len(self.game.coins) < N_COINS:
            self.enemy_killed = False


class PlayerModel():

    def __init__(self, game):
        self.explorer = Explorer(game)
        self.killer = Killer(game)
        self.scorer = Scorer(game)

    def print_model(self):
        print(tabulate([["Explorer", self.explorer.get_tendency(), self.explorer.get_skill()],
                        ["Killer", self.killer.get_tendency(), self.killer.get_skill()],
                        ["Scorer", self.scorer.get_tendency(), self.scorer.get_skill()]],
                       headers=["Type", "Tendency", "Skill"]))

    def update(self):
        self.explorer.update()
        self.killer.update()
        self.scorer.update()



