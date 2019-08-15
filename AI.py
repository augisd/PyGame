from sprites import Player, Bullet
from settings import *
from astar import *
import random
import pygame as pg

class BaseBot(Player, pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        Player.__init__(self, game, x, y)
        self.game = game
        self.skill = 1
        self.directions = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        self.random_direction = random.choice(self.directions)
        self.last_direction = [2, 2]
        self.max_steps = int(SCREEN_WIDTH / 2)
        self.steps_to_take = random.randint(TILESIZE, self.max_steps)
        self.steps_taken = 0
        self.current_state = self.explore

    def explore(self):
        # Move the player sprite around
        self.move_around()

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

    def obstacle_in_front(self, direction, distance):
        # Direction : [x, y] (-1,0,1)
        x = int(SCREEN_WIDTH / 2) + direction[0] * distance
        y = int(SCREEN_HEIGHT / 2) + direction[1] * distance

        return self.game.screen.get_at((x, y)) == WALL_COL or \
               self.game.screen.get_at((x, y)) == ENEMY_COL

    def update(self):
        # Pickup coin
        self.game.clock.tick(BOT_DELAY)
        self.coin_picked_up = False
        if pg.sprite.spritecollide(self, self.game.coins, True):
            self.coins_collected += 1
            self.coin_picked_up = True

        self.vx, self.vy = 0, 0
        self.current_state()
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

    def get_screen_objects(self):
        objects = []

        screen_top_left_x = int(self.rect.x / TILESIZE) - int(GRIDWIDTH / 2)
        screen_top_left_y = int(self.rect.y / TILESIZE) - int(GRIDHEIGHT / 2)
        screen_grid = self.game.map.grid[screen_top_left_y:(screen_top_left_y + GRIDHEIGHT)][screen_top_left_x:(screen_top_left_x + GRIDWIDTH)]

        for row in range(screen_top_left_y, screen_top_left_y + GRIDHEIGHT, 1):
            for col in range(screen_top_left_x, screen_top_left_x + GRIDWIDTH, 1):
                if self.game.map.grid[row][col] == "C":
                    objects.append("C")
                elif self.game.map.grid[row][col] == "E":
                    objects.append("E")
        return objects

class ExplorerBot(BaseBot):
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
        grid = self.game.map.grid
        # (row, col)
        path = astar(grid, start, target)
        if len(path) == 1:
            next_move = path[0]
        else:
            next_move = path[1]
        self.vx = PLAYER_SPEED * (next_move[1] - start_x)
        self.vy = PLAYER_SPEED * (next_move[0] - start_y)

class KillerBot(BaseBot):
    def explore(self):
        if "E" in self.get_screen_objects():
            self.current_state = self.kill_enemies
        # Move the player sprite around
        self.move_around()

    def kill_enemies(self):
        if "E" not in self.get_screen_objects():
            print("No enemies")
            self.current_state = self.explore

        # Find closest enemy
        closest_enemy = self.get_closest_enemy()
        # Get enemy in sight
        # Shoot in enemy's direction
        self.seek_enemy(closest_enemy)

    def get_closest_enemy(self):

        if len(self.game.enemies.sprites()) == 0:
            return [self.x, self.y]

        closest_enemy = [self.game.enemies.sprites()[0].x,
                        self.game.enemies.sprites()[0].y]

        for enemy in self.game.enemies.sprites():
            if (abs(self.x - enemy.x) + abs(self.y - enemy.y) <
                    abs(self.x - closest_enemy[0]) + abs(self.y - closest_enemy[1])):
                closest_enemy = [enemy.x, enemy.y]
        return closest_enemy

    def seek_enemy(self, coord):

        target_x = coord[0]
        target_y = coord[1]

        distance_x = int(self.rect.x / TILESIZE) - target_x
        distance_y = int(self.rect.y / TILESIZE) - target_y

        distance_x_abs = abs(int(self.rect.x / TILESIZE) - target_x)
        distance_y_abs = abs(int(self.rect.y / TILESIZE) - target_y)

        if distance_x_abs < distance_y_abs:
            move_in = "x"
        if distance_x_abs > distance_y_abs:
            move_in = "y"
        if distance_x_abs == distance_y_abs:
            move_in = random.choice(["x", "y"])

        if move_in == "x":

            if distance_x > 0:
                self.vx = -PLAYER_SPEED
            elif distance_x < 0:
                self.vx = PLAYER_SPEED

            else:

                if distance_y > 0:
                    if not self.game.bullets:
                        self.shoot("UP")

                if distance_y < 0:
                    if not self.game.bullets:
                       self.shoot("DOWN")

        if move_in == "y":

            if distance_y > 0:
                self.vy = -PLAYER_SPEED
            elif distance_y < 0:
                self.vy = PLAYER_SPEED

            else:

                if distance_x > 0:
                    if not self.game.bullets:
                        self.shoot("LEFT")

                if distance_x < 0:
                    if not self.game.bullets:
                        self.shoot("RIGHT")

