import pygame as pg
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
        #self.player = Player(self, PLAYER_START_POS[0], PLAYER_START_POS[1])
        self.player = ExplorerBot(self, PLAYER_START_POS[0], PLAYER_START_POS[1])
        #self.player = KillerBot(self, PLAYER_START_POS[0], PLAYER_START_POS[1])
        #self.player = ScorerBot(self, PLAYER_START_POS[0], PLAYER_START_POS[1])

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player_model = PlayerModel(self)
        self.game_adapter = GameAdapter(self, self.player_model)

    def run(self):
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.render()

    def update(self):

        self.player.update()
        self.all_sprites.update()
        self.camera.update(self.player)
        # Update player model tendencies before respawning sprites
        self.player_model.update()
        self.game_adapter.update()
        self.map.update()


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
                    for wall in self.walls:
                        print(wall.rect)

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


