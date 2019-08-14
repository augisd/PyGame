import pygame as pg
from settings import *
import random
import time

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill((PLAYER_COL))
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.vx = 0
        self.vy = 0
        self.coins_collected = 0
        self.enemies_killed = 0

        self.coin_picked_up = False
        self.bullets_fired = 0

    def update(self):
        # Pickup coin (Bool statements for player model tendency)
        self.coin_picked_up = False
        if pg.sprite.spritecollide(self, self.game.coins, True):
            self.coins_collected += 1
            self.coin_picked_up = True

        self.get_keys()
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

        #self.rect.x = int(self.x / TILESIZE) * TILESIZE
        self.rect.x = self.x
        self.collide_with_walls("x")
        #self.rect.y = int(self.y / TILESIZE) * TILESIZE
        self.rect.y = self.y
        self.collide_with_walls("y")

    def get_keys(self):
        self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()
        # Movement
        if keys[pg.K_LEFT]:
            self.vx = -PLAYER_SPEED
        if keys[pg.K_RIGHT]:
            self.vx = PLAYER_SPEED
        if keys[pg.K_UP]:
            self.vy = -PLAYER_SPEED
        if keys[pg.K_DOWN]:
            self.vy = PLAYER_SPEED
        # Normalize diagonal speed
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def collide_with_walls(self, dir):

        if dir == "x":
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0:
                    self.x = hits[0].rect.left - self.rect.width
                if self.vx < 0:
                    self.x = hits[0].rect.right
                self.vx = 0
                self.rect.x = self.x

        if dir == "y":
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0:
                    self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0:
                    self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y

    def shoot(self, dir):
        self.bullets_fired += 1
        bullet = Bullet(self.game, self.rect.centerx, self.rect.centery)
        if dir == "LEFT":
            bullet.speedx = -5
        elif dir == "RIGHT":
            bullet.speedx = 5
        elif dir == "UP":
            bullet.speedy = -5
        elif dir == "DOWN":
            bullet.speedy = 5


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(WALL_COL)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, fired_by_player=True):
        self.fired_by_player = fired_by_player

        if self.fired_by_player:
            self.groups = game.all_sprites, game.bullets
        elif not self.fired_by_player:
            self.groups = game.all_sprites, game.enemy_bullets

        self.game = game
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((3, 3))

        if self.fired_by_player:
            self.image.fill(BULLET_COL)
        else:
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = 0
        self.speedx = 0

    def update(self):
        if (self.rect.right > MAP_WIDTH or
            self.rect.left < 0 or
            self.rect.top < 0 or
            self.rect.bottom > MAP_HEIGHT or
            pg.sprite.spritecollideany(self, self.game.walls) or
            self.rect.right > self.game.player.rect.centerx + SCREEN_WIDTH / 2 or
            self.rect.left < self.game.player.rect.centerx - SCREEN_WIDTH / 2 or
            self.rect.top > self.game.player.rect.centery + SCREEN_HEIGHT / 2 or
            self.rect.bottom < self.game.player.rect.centery - SCREEN_HEIGHT / 2):
            self.kill()
        # Bullet collision ( fired by player or enemy )
        if self.fired_by_player:
            if pg.sprite.groupcollide(self.game.bullets, self.game.enemies, True, True):
                self.game.player.enemies_killed += 1
        elif not self.fired_by_player:
            pg.sprite.spritecollide(self.game.player, self.game.enemy_bullets, True)

        self.rect.centerx += self.speedx
        self.rect.centery += self.speedy


class Coin(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.coins
        self.game = game
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE / 2, TILESIZE / 2))
        self.image.fill(COIN_COL)
        self.rect = self.image.get_rect()
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.centerx = self.x + TILESIZE / 2
        self.rect.centery = self.y + TILESIZE / 2


class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.enemies
        self.game = game
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(ENEMY_COL)
        self.rect = self.image.get_rect()
        self.hp = 10
        self.x = x
        self.y = y
        self.rect.centerx = self.x * TILESIZE + TILESIZE / 2
        self.rect.centery = self.y * TILESIZE + TILESIZE / 2
        self.vx = 0
        self.vy = 0

        self.action_timer_start = time.perf_counter()
        self.action_update_time = 1

        self.states = {
            0 : self.stationary,
            1 : self.move_around,
            2 : self.shoot_back,
            3 : self.seek_player
        }

        self.state = 0

    def update(self):
        # Check update time
        self.action_timer_end = time.perf_counter()
        self.action_timer = self.action_timer_end - self.action_timer_start

        if self.action_timer > self.action_update_time:
            self.states.get(self.state)()
            self.action_timer_start = time.perf_counter()

    def stationary(self):
        pass

    def move_around(self):

        # NEED TO FIX MOVING INTO THE WALLS HERE

        move_to = random.choice([[1, 0], [0, 1], [-1, 0], [0, -1]])

        self.vx = move_to[0]
        self.vy = move_to[1]

        self.x += self.vx
        self.y += self.vy

        #self.rect.x = self.x * TILESIZE
        self.collide_with_walls("x")
        #self.rect.y = self.y * TILESIZE
        self.collide_with_walls("y")

    def shoot_back(self):

        # Move around (previous state)
        self.move_around()

        # Plus if player in sight - shoot
        if self.rect.x == self.game.player.rect.x:

            self.shoot_in_y_direction()

        elif self.rect.y == self.game.player.rect.y:

            self.shoot_in_x_direction()

        else:
            pass

    def shoot_in_x_direction(self):
        bullet = Bullet(self.game, self.rect.centerx, self.rect.centery, False)

        if self.rect.x > self.game.player.rect.x:
            bullet.speedx = -5
        else:
            bullet.speedx = 5

    def shoot_in_y_direction(self):
        bullet = Bullet(self.game, self.rect.centerx, self.rect.centery, False)

        if self.rect.y > self.game.player.rect.y:
            bullet.speedy = -5
        else:
            bullet.speedy = 5

    def seek_player(self):

        # Check which direction needs less moves (x or y) to put player in sight
        x = int(abs(self.game.player.rect.x - self.rect.x))
        y = int(abs(self.game.player.rect.y - self.rect.y))

        if x < y:
            direction = "x"
        if x > y:
            direction = "y"
        if x == y:
            direction = random.choice(["x", "y"])

        if direction == "x":

            if self.game.player.rect.x > self.rect.x:
                self.rect.x -= TILESIZE

            elif self.game.player.rect.x < self.rect.x:
                self.rect.x += TILESIZE

            else:
                self.shoot_in_y_direction()

        if direction == "y":

            if self.game.player.rect.y > self.rect.y:
                self.rect.y += TILESIZE

            elif self.game.player.rect.y < self.rect.y:
                self.rect.y -= TILESIZE

            else:
                self.shoot_in_x_direction()

    def collide_with_walls(self, dir):

        if dir == "x":
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0:
                    self.x = self.x - 1
                if self.vx < 0:
                    self.x = self.x + 1
                self.vx = 0
                #self.rect.x = self.x * TILESIZE

        self.rect.x = self.x * TILESIZE

        if dir == "y":
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0:
                    self.y = self.y - 1
                if self.vy < 0:
                    self.y = self.y + 1
                self.vy = 0
                #self.rect.y = self.y * TILESIZE

        self.rect.y = self.y * TILESIZE

        self.vx = 0
        self.vy = 0