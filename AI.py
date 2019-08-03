from sprites import Player, Bullet
from settings import *
from astar import *
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


class ExplorerBot(Player, pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        Player.__init__(self, game, x, y)
        self.game = game
        self.bot = FSM()
        self.current_state = self.explore
        # [x, y]
        self.directions = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        self.random_direction = random.choice(self.directions)
        self.last_direction = [2, 2]
        self.max_steps = int(SCREEN_WIDTH / 2)
        self.steps_to_take = random.randint(TILESIZE, self.max_steps)
        self.steps_taken = 0

    def explore(self):
        if "C" in self.get_screen_objects():
            self.current_state = self.collect_coins
        # Move the player sprite around
        self.move_around()

    def collect_coins(self):
        if "C" not in self.get_screen_objects():
            self.current_state = self.explore
        # Move the player sprite towards the nearest coin
        go_to = self.get_closest_coin()
        self.go_to_coin(go_to)

    def get_closest_coin(self):
        if len(self.game.coins.sprites()) == 0:
            return [self.x, self.y]

        closest_coin = [self.game.coins.sprites()[0].x,
                        self.game.coins.sprites()[0].y]

        for coin in self.game.coins.sprites():
            if (abs(self.x - coin.x) + abs(self.y - coin.y) <
                abs(self.x - closest_coin[0]) + abs(self.y - closest_coin[1])):
                closest_coin = [coin.x, coin.y]
        return closest_coin

    def go_to_coin(self, coord):
        # coord : [x, y] (pixels)
        target_x = int(coord[0] / TILESIZE)
        target_y = int(coord[1] / TILESIZE)
        target = (target_y, target_x)
        start_x = int(self.x / TILESIZE)
        start_y = int(self.y / TILESIZE)
        start = (start_y, start_x)
        grid = self.game.map.map_layout
        # (row, col)
        path = astar(grid, start, target)
        if len(path) == 1:
            next_move = path[0]
        else:
            next_move = path[1]
        self.vx = PLAYER_SPEED * (next_move[1] - start_x)
        self.vy = PLAYER_SPEED * (next_move[0] - start_y)

    def move_around(self):
        # Re-implement Random Walk

        if self.steps_taken == self.steps_to_take:
            self.last_direction = self.random_direction
            self.random_direction = random.choice(self.directions)

            # Check if walk direction is not the same or backwards:
            while ((self.random_direction[0] == self.last_direction[0] and
                    self.random_direction[1] == self.last_direction[1]) or
                   (self.random_direction[0] == -self.last_direction[0] and
                    self.random_direction[1] == -self.last_direction[1])):
                self.random_direction = random.choice(self.directions)

            self.steps_to_take = random.randint(TILESIZE, self.max_steps)
            self.steps_taken = 0

        self.vx = PLAYER_SPEED * self.random_direction[0]
        self.vy = PLAYER_SPEED * self.random_direction[1]
        self.steps_taken += 1

        # Check if no obstacles in front (walls / out of bounds)

        if ((self.x < TILESIZE and self.random_direction[0] == -1 or
             self.y < TILESIZE and self.random_direction[1] == -1) or
                (self.x > MAP_WIDTH - TILESIZE and self.random_direction[0] == 1 or
                 self.y > MAP_HEIGHT - TILESIZE and self.random_direction[1] == 1)):
            self.steps_taken = self.steps_to_take


        if self.obstacle_in_front(self.random_direction, 2 * TILESIZE):
            self.steps_taken = self.steps_to_take


        #if pg.sprite.spritecollideany(self, self.game.walls, pg.sprite.collide_rect_ratio(2)):
        #    self.steps_taken = self.steps_to_take
        #    self.last_direction = self.random_direction
        #    return

    def obstacle_in_front(self, direction, distance):
        # Direction : [x, y] (-1,0,1)
        x = int(SCREEN_WIDTH / 2) + direction[0] * distance
        y = int(SCREEN_HEIGHT / 2) + direction[1] * distance

        return self.game.screen.get_at((x, y)) == WALL_COL or \
               self.game.screen.get_at((x, y)) == ENEMY_COL

    def get_screen_objects(self):
        objects = []
        for row in range(int(TILESIZE / 2), SCREEN_HEIGHT - TILESIZE, TILESIZE):
            for col in range(int(TILESIZE / 2), SCREEN_WIDTH - TILESIZE, TILESIZE):
                check = self.game.screen.get_at((col, row))
                if check == SCREEN_COL:
                    objects.append(" ")
                if check == COIN_COL:
                    objects.append("C")
                if check == ENEMY_COL:
                    objects.append("E")
                if check == WALL_COL:
                    objects.append("W")
                if check == PLAYER_COL:
                    objects.append("P")
        return objects

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

        self.rect.x = int(self.x / TILESIZE) * TILESIZE
        self.collide_with_walls("x")
        self.rect.y = int(self.y / TILESIZE) * TILESIZE
        self.collide_with_walls("y")




