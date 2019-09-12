import pygame as pg
import pandas as pd
from sprites import *
from settings import *
from AI import *
from map import *
from playermodel import *
from gameadapter import *


class Game:
    def __init__(self):
        self.running = True
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Sprite groups
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.enemies = pg.sprite.Group()

        self.clock = pg.time.Clock()
        pg.key.set_repeat(10, 10)
        self.playing = True


    def new_game(self):
        self.map = Map(self)
        self.player = Player(self, PLAYER_START_POS[0], PLAYER_START_POS[1])
        #self.player = ExplorerBot(self, PLAYER_START_POS[0], PLAYER_START_POS[1])
        #self.player = KillerBot(self, PLAYER_START_POS[0], PLAYER_START_POS[1])

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.player_model = PlayerModel(self)
        self.game_adapter = GameAdapter(self, self.player_model)

        #self.data_coll = ExplorerDataCollector(self)
        #self.data_coll = KillerDataCollector(self)
        #self.data_coll = MixedDataCollector(self)

    def run(self):
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000

            self.events()
            self.update()
            self.render()

    def update(self):

        self.player.update()
        self.all_sprites.update()

        self.player_model.update()
        self.game_adapter.update()

        self.camera.update(self.player)
        self.map.update()
        #self.data_coll.update()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # Controls
            if event.type == pg.KEYDOWN:

                # Shooting
                if event.key == pg.K_w:
                    self.player.shoot("UP")
                if event.key == pg.K_s:
                    self.player.shoot("DOWN")
                if event.key == pg.K_a:
                    self.player.shoot("LEFT")
                if event.key == pg.K_d:
                    self.player.shoot("RIGHT")

                # Testing
                if event.key == pg.K_SPACE:
                    print(self.player_model.print_model())

    def render(self):
        self.screen.fill(SCREEN_COL)
        #self.draw_grid()
        #self.player.draw(self.screen)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        pg.display.flip()

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, TILESIZE):
            pg.draw.line(self.screen, GRIDLINE_COL, (x, 0), (x, SCREEN_HEIGHT))

        for y in range(0, SCREEN_HEIGHT, TILESIZE):
            pg.draw.line(self.screen, GRIDLINE_COL, (0, y), (SCREEN_WIDTH, y))


class DataCollector():
    def __init__(self, game):
        self.game = game
        self.data = {}
        self.data_frame = 0

    def add_data_to_frame(self):
        self.data_frame = pd.DataFrame(self.data)

    def data_frame_to_csv(self, name):
        self.data_frame.to_csv(name)

    def get_frame(self):
        return self.data_frame

class MixedDataCollector(DataCollector):
    def __init__(self, game):
        DataCollector.__init__(self, game)

        # Data frame variables
        self.playing_time = 0

        self.tendency_killer = 1
        self.tendency_killer_previous = 1
        self.n_enemies = N_ENEMIES
        self.enemy_spawn_distance = SPAWN_DIST_ENEMIES

        self.tendency_explorer = 1
        self.tendency_explorer_previous = 1
        self.n_coins = N_COINS
        self.percentange_map_revealed = round(self.game.map.n_walls_spawned / self.game.map.n_walls, 2) * 100

        self.data = {"TIME": [0],
                     "N_ENEMIES": [self.n_enemies],
                     "ENEMY_SPAWN_DISTANCE": [self.enemy_spawn_distance],
                     "TENDENCY_KILLER": [self.tendency_killer],
                     "TENDENCY_EXPLORER": [self.tendency_explorer],
                     "N_COINS": [self.n_coins],
                     "PERCENTAGE_MAP": [self.percentange_map_revealed]}
        self.data_frame = pd.DataFrame(pd.DataFrame(self.data))
        self.start_time = time.perf_counter()

    def update(self):
        self.end_time = time.perf_counter()
        self.playing_time = round(self.end_time - self.start_time, 2)

        if self.tendency_explorer == 50:
            print("start killing")

        if self.tendency_killer == 50:
            self.data_frame_to_csv("mixed_player_data.csv")

        if self.tendency_killer > self.tendency_killer_previous or\
                self.tendency_explorer > self.tendency_explorer_previous:
            self.percentange_map_revealed = round(self.game.map.n_walls_spawned / self.game.map.n_walls, 2) * 100

            self.data = {"TIME": [self.playing_time],
                         "N_ENEMIES": [self.game.map.n_enemies],
                         "ENEMY_SPAWN_DISTANCE": [self.game.map.enemy_spawn_distance],
                         "TENDENCY_KILLER": [self.tendency_killer],
                         "TENDENCY_EXPLORER": [self.tendency_explorer],
                         "N_COINS": [self.game.map.n_coins],
                         "PERCENTAGE_MAP": [self.percentange_map_revealed]}

            self.data_frame = self.data_frame.append(pd.DataFrame(self.data))
            self.start_time = time.perf_counter()
            print(self.data_frame)

        self.tendency_killer_previous = self.tendency_killer
        self.tendency_killer = self.game.player_model.killer.tendency

        self.tendency_explorer_previous = self.tendency_explorer
        self.tendency_explorer = self.game.player_model.explorer.tendency

class KillerDataCollector(DataCollector):
    def __init__(self, game):
        DataCollector.__init__(self, game)

        # Data frame variables
        self.playing_time = 0
        self.enemies_killed = 0
        self.tendency = 1
        self.tendency_previous = 1
        self.skill = 1
        self.skill_previous = 1
        self.bullets_fired = 0
        self.bullets_taken = 0
        self.data = {"TIME" : [0],
                     "ENEMIES_KILLED" : [0],
                     "N_ENEMIES" : [0],
                     "ENEMY_SPAWN_DISTANCE" : [0],
                     "ENEMY_UPDATE_TIME" : [0],
                     "BULLETS_FIRED" : [0],
                     "BULLETS_TAKEN": [0],
                     "TENDENCY" : [0],
                     "SKILL" : [0]}
        self.data_frame = pd.DataFrame(pd.DataFrame(self.data))
        self.start_time = time.perf_counter()
        self.update_start_time = time.perf_counter()

    def update(self):
        self.end_time = time.perf_counter()
        self.playing_time = round(self.end_time - self.start_time, 2)
        self.update_end_time = time.perf_counter()
        self.update_time = self.update_end_time - self.update_start_time
        print(self.tendency)
        if self.tendency == 20:
            self.data_frame_to_csv("killer_bot_data_x10.csv")

        if self.tendency > self.tendency_previous:
            self.enemies_killed = self.game.player.enemies_killed
            self.bullets_fired = self.game.player.bullets_fired
            self.bullets_taken = self.game.player.bullets_taken
            self.data = {"TIME": [self.playing_time],
                         "ENEMIES_KILLED": [self.enemies_killed],
                         "N_ENEMIES" : [self.game.map.n_enemies],
                         "ENEMY_SPAWN_DISTANCE" : [self.game.map.enemy_spawn_distance],
                         "ENEMY_UPDATE_TIME" : [10 / self.skill],
                         "BULLETS_FIRED": [self.bullets_fired],
                         "BULLETS_TAKEN": [self.bullets_taken],
                         "TENDENCY": [self.tendency],
                         "SKILL": [self.skill]}
            self.data_frame = self.data_frame.append(pd.DataFrame(self.data))

        self.skill_previous = self.skill
        self.tendency_previous = self.tendency
        self.skill = self.game.player_model.killer.skill
        self.tendency = self.game.player_model.killer.tendency

class ExplorerDataCollector(DataCollector):
    def __init__(self, game):
        DataCollector.__init__(self, game)

        # Data frame variables
        self.playing_time = 0
        self.coins_collected = 0
        self.tendency = self.game.player_model.explorer.tendency
        self.tendency_previous = 1
        self.skill = self.game.player_model.explorer.skill
        self.skill_previous = 1
        self.data = {"TIME" : [0],
                     "COINS" : [0],
                     "TENDENCY" : [1],
                     "SKILL" : [1],
                     "COINS_SPAWNED": [self.game.map.n_coins],
                     "COIN_SPAWN_DISTANCE": [self.game.map.coin_spawn_distance],
                     "PERCENTAGE_MAP": [0]}
        self.data_frame = pd.DataFrame(pd.DataFrame(self.data))
        self.start_time = time.perf_counter()
        self.update_start_time = time.perf_counter()


    def update(self):
        self.end_time = time.perf_counter()
        self.playing_time = round(self.end_time - self.start_time, 2)
        print(self.tendency)
        if self.tendency == 20:
            self.data_frame_to_csv("explorer_bot_data_x10.csv")
        if self.tendency > self.tendency_previous: #or self.tendency > self.tendency_previous:
            self.update_end_time = time.perf_counter()
            self.update_time = self.update_end_time - self.update_start_time
            self.coins_collected = self.game.player.coins_collected
            self.percentange_map_revealed = round(self.game.map.n_walls_spawned / self.game.map.n_walls, 2) * 100
            self.data = {"TIME": [self.update_time],
                         "COINS_COLLECTED": [self.coins_collected],
                         "TENDENCY": [self.tendency],
                         "SKILL": [self.skill],
                         "COINS_SPAWNED": [self.game.map.n_coins],
                         "COIN_SPAWN_DISTANCE": [self.game.map.coin_spawn_distance],
                         "PERCENTAGE_MAP": [self.percentange_map_revealed]}
            self.data_frame = self.data_frame.append(pd.DataFrame(self.data))
            self.update_start_time = time.perf_counter()

        self.skill_previous = self.skill
        self.tendency_previous = self.tendency
        self.skill = self.game.player_model.explorer.skill
        self.tendency = self.game.player_model.explorer.tendency