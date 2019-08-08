from tabulate import tabulate
import pygame as pg
#from game import Game
from settings import *
import time


class PlayerType():

    def __init__(self, game):
        self.game = game
        self.tendency = 1
        self.skill = 1
        self.tendency_decrement = -0.5
        self.skill_modifier = 0.01
        self.tendency_increment = 1
        self.skill_increment = 5

    def increase_tendency(self):
        self.tendency += self.tendency_increment

    def decrease_tendency(self):
        self.tendency += self.tendency_decrement

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
        self.update_skill()

        #self.skill -= self.skill_modifier
        if self.tendency < 0:
            self.tendency = 0
        if self.skill < 0:
            self.skill = 0

        if self.tendency > 100:
            self.tendency = 100



class Explorer(PlayerType):
    # Coin pickup event increases tendency
    def __init__(self, game):
        PlayerType.__init__(self, game)
        self.start_time = time.perf_counter()
        self.coins_collected = 0
        self.total_coins = 0
        self.end_time = time.perf_counter()
        self.time_elapsed = self.end_time - self.start_time
        self.skill = 1
        self.avg_skill = []
        self.all_times = []

        self.tendency_timer_start = time.perf_counter()
        self.tendency_timer_end = 0
        self.tendency_timer = 0

        self.percentage_map_explored = self.game.map.percentage_map_explored

    def update_tendency(self):

        self.coins_collected = self.game.player.coins_collected

        if self.coins_collected >= 10:
            self.game.map.n_coins = self.coins_collected // 10 + N_COINS

        self.tendency_timer_end = time.perf_counter()
        self.tendency_timer = self.tendency_timer_end - self.tendency_timer_start

        if self.game.player.coin_picked_up:
            self.tendency_timer_start = time.perf_counter()
            self.increase_tendency()

        if self.tendency_timer > 5:
            self.decrease_tendency()
            self.tendency_timer_start = time.perf_counter()


    def update_skill(self):

        # Scale spawn distance with skill
        if self.skill > 10:
            self.game.map.coin_spawn_distance = int(self.skill) * 3 // 10 + SPAWN_DIST_COINS

        # 1. Number of coins collected
        self.coins_collected = self.game.player.coins_collected

        # 2. Percentage of Map explored
        self.percentage_map_explored = self.game.map.percentage_map_explored

        # Get time played
        self.end_time = time.perf_counter()
        self.time_elapsed = self.end_time - self.start_time

        self.skill = 100 * self.coins_collected * self.percentage_map_explored / self.time_elapsed

class Killer(PlayerType):
    # Enemy kill event increases killer tendency
    def __init__(self, game):
        PlayerType.__init__(self, game)
        self.game = game
        self.last_n_enemies_killed = 0
        self.enemies_killed = self.game.player.enemies_killed
        self.kills_per_minute = 0
        self.bullets_fired = self.game.player.bullets_fired
        self.accuracy = 0
        self.start_killing_time = time.perf_counter()
        self.skill_update_time = 10

    def update_tendency(self):

        self.enemies_killed = self.game.player.enemies_killed

        if self.enemies_killed >= 10:

            if self.enemies_killed % 5 == 0 and self.enemies_killed != 0:
                self.increase_tendency()

            self.game.map.n_enemies = self.enemies_killed // 10 + N_ENEMIES

    def update_skill(self):
        self.bullets_fired = self.game.player.bullets_fired
        print(self.kills_per_minute)
        if self.skill > 10:
            self.game.map.enemy_spawn_distance = int(self.skill) * 3 // 10 + SPAWN_DIST_ENEMIES

        if self.bullets_fired > 0:
            self.accuracy = round(self.enemies_killed / self.bullets_fired, 2)

        self.end_killing_time = time.perf_counter()
        self.killing_time = self.end_killing_time - self.start_killing_time

        self.kills_per_minute = self.enemies_killed * 60 / self.killing_time

        self.skill = self.kills_per_minute * self.accuracy 

        for enemy in self.game.enemies:
            new_state = self.skill // 10
            if new_state > 3:
                new_state = 3
            enemy.state = new_state


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

    def update_skill(selfs):
        pass


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



