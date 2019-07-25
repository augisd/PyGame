import pygame as pg
from settings import *
import random

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

    def update(self):
        # Pickup coin
        pg.sprite.spritecollide(self, self.game.coins, True)
        #print(self.vx, self.vy)
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

        self.rect.x = self.x
        self.collide_with_walls("x")
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
        if keys[pg.K_SPACE]:
            self.move_around()
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
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.bullets
        self.game = game
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((3, 3))
        self.image.fill(BULLET_COL)
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
            pg.sprite.spritecollideany(self, self.game.walls)):
            self.kill()
        # Bullet hits enemy
        pg.sprite.groupcollide(self.game.bullets, self.game.enemies, True, True)
        self.rect.centerx += self.speedx
        self.rect.centery += self.speedy


class Coin(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.coins
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
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(ENEMY_COL)
        self.rect = self.image.get_rect()
        self.hp = 10
        self.x = x
        self.y = y
        self.rect.centerx = self.x * TILESIZE + TILESIZE / 2
        self.rect.centery = self.y * TILESIZE + TILESIZE / 2
        self.speedx = 0
        self.speedy = 0