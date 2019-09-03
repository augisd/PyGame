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
        #pg.key.set_repeat(500, 100)
        self.playing = True


    def new_game(self):
        self.map = Map(self)
        self.player = Player(self, PLAYER_START_POS[0], PLAYER_START_POS[1])
        #self.player = ExplorerBot(self, PLAYER_START_POS[0], PLAYER_START_POS[1])
        #self.player = KillerBot(self, PLAYER_START_POS[0], PLAYER_START_POS[1])
        #self.player = ScorerBot(self, PLAYER_START_POS[0], PLAYER_START_POS[1])

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        #self.player_model = BotModel(self)
        #self.game_adapter = GameAdapterBot(self, self.player_model)
        self.player_model = PlayerModel(self)
        self.game_adapter = GameAdapter(self, self.player_model)
        self.data_coll = ExplorerDataCollector(self)

    def run(self):
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()

            self.update()
            #debug_time_start = time.perf_counter()
            self.render()
            #debug_time_end = time.perf_counter()
            #print(debug_time_end - debug_time_start)
    def update(self):

        self.player.update()
        self.all_sprites.update()
        self.camera.update(self.player)
        # Update player model tendencies before respawning sprites

        self.player_model.update()
        self.game_adapter.update()
        self.map.update()
        self.data_coll.update()


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
                if event.key == pg.K_m:
                    self.map.print_map(self.map.grid)
                if event.key == pg.K_t:
                    self.map.print_map(self.map.grid_explored)

                # Testing
                if event.key == pg.K_SPACE:
                    print(self.player_model.print_model())
                if event.key == pg.K_x:
                    self.map.spawn_sprite2(Coin)
                if event.key == pg.K_p:
                    self.data_coll.get_frame()

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

class ExplorerDataCollector(DataCollector):
    def __init__(self, game):
        DataCollector.__init__(self, game)

        # Data frame variables
        self.playing_time = 0
        self.coins_collected = 0
        self.tendency = 0
        self.skill = 0
        self.data = {"TIME" : [0], "COINS" : [0], "TENDENCY" : [0], "SKILL" : [0]}
        self.data_frame = pd.DataFrame()
        self.start_time = time.perf_counter()
        self.update_start_time = time.perf_counter()


    def update(self):
        self.end_time = time.perf_counter()
        self.playing_time = round(self.end_time - self.start_time, 2)
        self.update_end_time = time.perf_counter()
        self.update_time = self.update_end_time - self.update_start_time

        if self.skill == 50:
            self.data_frame_to_csv("explorer_bot_data.csv")

        if self.update_time > 1:
            self.coins_collected = self.game.player.coins_collected
            self.tendency = self.game.player_model.explorer.tendency
            self.skill = self.game.player_model.explorer.skill

            self.data = { "TIME" : [self.playing_time],
                          "COINS" : [self.coins_collected],
                          "TENDENCY" : [self.tendency],
                          "SKILL" : [self.skill] }

            self.data_frame = self.data_frame.append(pd.DataFrame(self.data))

            self.update_start_time = time.perf_counter()


        #self.data_frame.append(pd.DataFrame(self.data))
        #print(self.data_frame)



