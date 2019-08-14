from tabulate import tabulate
import pygame as pg
#from game import Game
from settings import *
import time
import pandas as pd


class PlayerType():

    def __init__(self, game):
        self.game = game
        self.tendency = 1
        self.skill = 1
        self.tendency_decrement = -0.001
        self.skill_decrement = -1
        self.tendency_increment = 1
        self.skill_increment = 1

        # Variables for skill data collection and calculation
        self.skill_data = {"n_coins" : [], "dist" : [], "time" : []}
        self.skill_data_csv = pd.read_csv('test_data.csv')
        #del self.skill_data_csv["Unnamed: 0"]
        #print(self.skill_data_csv)

        self.tendency_timer_start = 0
        self.tendency_timer_end = 0
        self.tendency_timer = 0

    def increase_tendency(self):
        self.tendency += self.tendency_increment

    def decrease_tendency(self):
        self.tendency += self.tendency_decrement

    def increase_skill(self):
        self.skill += self.skill_increment

    def decrease_skill(self):
        self.skill += self.skill_decrement

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


class Explorer(PlayerType):
    # Coin pickup event increases tendency
    def __init__(self, game):
        PlayerType.__init__(self, game)
        self.start_time = time.perf_counter()
        self.coins_collected = 0
        self.coins_collected_previous = 0
        self.coin_streak = 0
        self.skill_coin_streak = 0
        self.total_coins = 0
        self.end_time = time.perf_counter()
        self.time_elapsed = self.end_time - self.start_time
        self.avg_skill = []
        self.all_times = []

        self.skill_timer_start = time.perf_counter()
        self.skill_timer_end = 0
        self.skill_timer = 0
        self.skill_decrease_flag = False
        self.previous_tendency = 0
        self.percentage_map_explored = self.game.map.percentage_map_explored

    def update_tendency(self):

        # Calculate tendency

        # Check if a coin was collected

        if self.coin_collected():
            # Start tendency timer
            self.tendency_timer_start = time.perf_counter()

            self.coin_streak += 1
            #self.coins_collected_previous = self.coins_collected

        self.tendency_timer_end = time.perf_counter()
        self.tendency_timer = self.tendency_timer_end - self.tendency_timer_start

        # If another coin was not picked up in next 5 seconds,
        # assume it was not intentional and decrease tendency and reset streak
        if self.tendency_timer > 5:
            self.decrease_tendency()
            self.coin_streak = 0

        # Else, increase explorer tendency after collection of 5 coins
        if self.coin_streak >= 5:
            # Save previous state of tendency for adaptation
            self.previous_tendency = self.tendency
            self.increase_tendency()
            self.coin_streak = 0
            #self.game.map.n_coins = self.coins_collected // 10 + N_COINS

    def update_skill(self):

        # Calculate skill
        # If currently on streak and coin picked up, increase streak by 1
        if self.coin_collected() and self.skill_coin_streak > 0:
            self.skill_coin_streak += 1

            # And if picked up coin was the last one on the screen, update the skill
            if self.skill_coin_streak == self.game.map.n_coins:
                self.skill_timer_end = time.perf_counter()
                self.skill_timer = round(self.skill_timer_end - self.skill_timer_start, 1)

                self.time_to_beat = round(self.game.map.n_coins * self.game.map.coin_spawn_distance / 10, 1)

                # If player is faster than estimated skillfull time, increase skill
                if self.skill_timer <= self.time_to_beat:
                    self.increase_skill()

                # Else if not, set flag to true
                elif self.skill_timer > self.time_to_beat and not self.skill_decrease_flag:
                    self.skill_decrease_flag = True

                # If failed to match the time twice in a row, decrease skill
                elif self.skill_timer > self.time_to_beat and self.skill_decrease_flag:
                    self.decrease_skill()
                    self.skill_decrease_flag = False

                # Write skill data to CSV
                self.skill_data["n_coins"].append(self.skill_coin_streak)
                self.skill_data["dist"].append(self.game.map.coin_spawn_distance)
                self.skill_data["time"].append(self.skill_timer)
                self.skill_data_csv = self.skill_data_csv.append(pd.DataFrame(self.skill_data).tail(1))
                self.skill_data_csv.to_csv("test_data.csv", index=False)

                self.skill_coin_streak = 0

        # Else, start new streak and skill timer
        if self.coin_collected() and self.skill_coin_streak == 0:
            self.skill_coin_streak += 1
            self.skill_timer_start = time.perf_counter()

        # Scale spawn distance with skill
        #self.game.map.coin_spawn_distance = (int(self.skill) * 2 // 10) + SPAWN_DIST_COINS

        # 1. Number of coins collected
        #self.coins_collected = self.game.player.coins_collected

        # 2. Percentage of Map explored
        #self.percentage_map_explored = self.game.map.percentage_map_explored

        # Get time played
        #self.end_time = time.perf_counter()
        #self.time_elapsed = self.end_time - self.start_time
        #self.skill = 100 * self.coins_collected * self.percentage_map_explored / (self.time_elapsed * 0.5)
        # Update coin collection
        self.coins_collected_previous = self.coins_collected
        self.coins_collected = self.game.player.coins_collected

    def coin_collected(self):
        return self.coins_collected > self.coins_collected_previous

class Killer(PlayerType):
    # Enemy kill event increases killer tendency
    def __init__(self, game):
        PlayerType.__init__(self, game)
        self.game = game
        self.last_n_enemies_killed = 0
        self.enemies_killed = 0
        self.enemies_killed_previous = 0
        self.enemy_streak_tendency = 0

        self.kills_per_minute = 0
        self.bullets_fired = self.game.player.bullets_fired
        self.accuracy = 0
        self.start_killing_time = time.perf_counter()
        self.skill_update_time = 10

    def update_tendency(self):

        if self.enemy_killed():
            # Start tendency timer
            self.tendency_timer_start = time.perf_counter()
            self.enemy_streak_tendency += 1

        self.tendency_timer_end = time.perf_counter()
        self.tendency_timer = self.tendency_timer_end - self.tendency_timer_start

        # If another enemy was not killed in next 5 seconds,
        # assume it was not intentional and decrease tendency and reset streak
        if self.tendency_timer > 5:
            self.decrease_tendency()
            self.enemy_streak_tendency = 0

        # Else, increase killer tendency after collection of 5 coins
        if self.enemy_streak_tendency >= 5:
            self.increase_tendency()
            self.enemy_streak_tendency = 0

    def update_skill(self):
        self.bullets_fired = self.game.player.bullets_fired
        if self.skill > 10:
            self.game.map.enemy_spawn_distance = int(self.skill) // 10 + SPAWN_DIST_ENEMIES

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

        self.enemies_killed_previous = self.enemies_killed
        self.enemies_killed = self.game.player.enemies_killed

    def enemy_killed(self):
        return self.enemies_killed > self.enemies_killed_previous


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



