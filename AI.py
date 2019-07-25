from sprites import Player, Bullet
from settings import *
import random
import pygame as pg

class Bot(Player):
    def __init__(self):
        pass

    def get_screen(self):
        pass


class FSM:
    def __init__(self):
        self.current_state = 0
        self.running = True
    
    def set_state(self, state):
        self.current_state = state

    def update(self):
        self.current_state


class State:
    def __init__(self):
        pass

    def action(self):
        pass


class Explorer(Player, pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        Player.__init__(self, game, x, y)
        self.bot = FSM()
        self.current_state = self.explore

    def explore(self):
        if "C" in self.game.get_screen_objects():
            self.current_state = self.collect_coins
        print("Exploring")
        # Move the player sprite around
        self.move_around()

    def collect_coins(self):
        if "C" not in self.game.get_screen_objects():
            self.current_state = self.explore
        print("Collecting")
        # Move the player sprite towards the nearest coin
        go_to = self.get_closest_coin()
        print(go_to)
        self.move_to_coin(self.get_closest_coin())

    def get_closest_coin(self):
        if len(self.game.coins.sprites()) == 0:
            return [self.x, self.y]

        closest_coin = [self.game.coins.sprites()[0].x,
                        self.game.coins.sprites()[0].y]

        for coin in self.game.coins.sprites():
            if (abs(self.x - coin.x) + abs(self.y - coin.y) <
                abs(self.x - closest_coin[0]) + abs(self.y - closest_coin[1])):
                closest = [coin.x, coin.y]
        return closest_coin

    def move_to_coin(self, coin_coord):

        coin_x = coin_coord[0]
        coin_y = coin_coord[1]
        print("moving to coin", coin_x, coin_y)
        print("current coords", self.x, self.y)

        if coin_x + TILESIZE / 4 > self.x > coin_x - TILESIZE / 4:

            if self.y > coin_y:
                self.y = -PLAYER_SPEED
            elif self.y < coin_y:
                self.y = PLAYER_SPEED
        elif self.x > coin_x:
            self.vx = -PLAYER_SPEED
        elif self.x < coin_x:
            self.vx = PLAYER_SPEED
        print(self.vx)

    def move_to_coin2(self, coin_coord):

        coin_x = coin_coord[0]
        coin_y = coin_coord[1]
        print("moving to coin", coin_x, coin_y)
        print("current coords", self.x, self.y)
        if self.x > coin_x:
            self.vx = -PLAYER_SPEED
        elif self.x < coin_x:
            self.vx = PLAYER_SPEED
        elif self.x == coin_x:

            if self.y > coin_y:
                self.y = -PLAYER_SPEED
            elif self.y < coin_y:
                self.y = PLAYER_SPEED
            else:
                pass
        print(self.vx)

    def move_around(self):
        # [x, y]
        print("moving around")
        move = random.choice([[1, 0], [0, 1], [-1, 0], [0, -1]])
        self.vx = PLAYER_SPEED * move[0]
        self.vy = PLAYER_SPEED * move[1]

    def update(self):
        # Pickup coin
        pg.sprite.spritecollide(self, self.game.coins, True)
        # print(self.vx, self.vy)
        #self.get_keys()
        self.vx, self.vy = 0, 0
        self.current_state()
        #self.move_around()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt

        if self.x < 0:
            self.x = 0
        if self.x > MAP_WIDTH:
            self.x = MAP_WIDTH
        if self.y < 0:
            self.y = 0
        if self.y > MAP_HEIGHT:
            self.y = MAP_HEIGHT

        self.rect.x = self.x
        self.collide_with_walls("x")
        self.rect.y = self.y
        self.collide_with_walls("y")




