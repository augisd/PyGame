import pygame as pg
import random
from settings import *
from sprites import *
from pygame.locals import *
import math
import numpy as np
from copy import deepcopy
class Map:
    def __init__(self, game):
        self.game = game
        self.grid = 0
        self.grid_walls_only = 0
        self.wall_range = 0
        self.grid_explored = 0
        self.cells_explored = 0
        self.cells_unexplored = 0
        self.percentage_map_explored = 0
        self.width = GRIDWIDTH * 2
        self.height = GRIDHEIGHT * 2
        self.n_coins = N_COINS
        self.n_enemies = N_ENEMIES
        self.cluster_sizes = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 4, 9, 9, 9, 9, 16, 16, 16, 25, 25, 36, 36, 64, 100]
        self.coin_spawn_distance = SPAWN_DIST_COINS
        self.enemy_spawn_distance = SPAWN_DIST_ENEMIES
        self.wall_coordinates = 0
        self.map_percentage_revealed = 0.5
        self.n_walls = 0
        self.walls = 0


        # Initial player position (to be used for spawning sprites
        # around player):
        self.player_row = int(MAPGRIDHEIGHT / 2)
        self.player_col = int(MAPGRIDWIDTH / 2)

        random.seed(13)
        self.create_map()

    def update(self):

        if len(self.game.coins) == 0:
            self.grid = self.make_grid()
            self.coin_clusters = self.cluster_sprites(self.n_coins)

            for cluster in self.coin_clusters:
                location_choices = self.find_sprite_spawn_locs(distance=self.coin_spawn_distance,
                                                               cluster_size=int(math.sqrt(cluster)))
                if location_choices:
                    location = random.choice(location_choices)

                    for coin_row in range(int(math.sqrt(cluster))):
                        for coin_col in range(int(math.sqrt(cluster))):
                            Coin(self.game, location[1] + coin_col, location[0] + coin_row)
                            #self.grid[location[0] + coin_row][location[1] + coin_col] = "C"

                    self.grid = self.make_grid()
                else:
                    continue

        if len(self.game.enemies) == 0:
            #for enemy in range(self.n_enemies):
            #    self.grid = self.make_grid()
            #    self.spawn_sprite(Enemy, self.enemy_spawn_distance)

            self.grid = self.make_grid()
            self.enemy_clusters = self.cluster_sprites(self.n_enemies)

            for cluster in self.enemy_clusters:
                location_choices = self.find_sprite_spawn_locs(distance=self.enemy_spawn_distance,
                                                               cluster_size=int(math.sqrt(cluster)))
                if location_choices:
                    location = random.choice(location_choices)

                    for enemy_row in range(int(math.sqrt(cluster))):
                        for enemy_col in range(int(math.sqrt(cluster))):
                            Enemy(self.game, location[1] + enemy_col, location[0] + enemy_row)
                            # self.grid[location[0] + coin_row][location[1] + coin_col] = "C"

                    self.grid = self.make_grid()
                else:
                    continue

        # Check where in the grid the player has been
        # and update percentage of grid explored
        #self.n_cells_explored()
        #self.cells_unexplored = self.cells_unexplored - self.cells_explored
        #self.percentage_map_explored = self.cells_explored / self.cells_unexplored

        # Reveal the map
        #if self.wall_coordinates:
        #    for wall in self.wall_coordinates:
        #        Wall(self.game, wall[1], wall[0])
        #        self.wall_coordinates.remove(wall)

    def reveal_walls(self, length):
        # Top and bottom rows
        for col_index in range(-length, length + 1, 1):

            if self.walls[self.player_row - length][self.player_col + col_index] == "W":
                Wall(self.game, self.player_col + col_index, self.player_row - length)

            if self.walls[self.player_row + length][self.player_col + col_index] == "W":
                Wall(self.game, self.player_col + col_index, self.player_row + length)

        # Left + right cols
        for row_index in range(-length + 1, length, 1):

            if self.walls[self.player_row + row_index][self.player_col - length] == "W":
                Wall(self.game, self.player_col - length, self.player_row + row_index)

            if self.walls[self.player_row + row_index][self.player_col + length] == "W":
                Wall(self.game, self.player_col + length, self.player_row + row_index)

    def hide_walls(self, length):

        for wall in self.game.walls.sprites():

            for col_index in range(-length, length + 1, 1):

                if ((wall.x == self.player_col + col_index and wall.y == self.player_row - length) or
                    (wall.x == self.player_col + col_index and wall.y == self.player_row + length)):
                    wall.kill()

            for row_index in range(-length + 1, length, 1):

                if ((wall.x == self.player_col - length and wall.y == self.player_row + row_index) or
                    (wall.x == self.player_col + length and wall.y == self.player_row + row_index)):
                    wall.kill()

    def create_map(self):
        self.walls = self.random_walk()

        # First create map layout (walls and walkable areas)
        # including player sprite starting position
        self.grid_walls_only = self.walls
        self.grid = deepcopy(self.walls)

        # Next, determine initial spawn locations for coin
        # and enemy sprites
        # First spawn the coins:
        # Randomly select cluster sizes from number of coins
        self.coin_clusters = self.cluster_sprites(self.n_coins)

        for cluster in self.coin_clusters:
            location_choices = self.find_sprite_spawn_locs(distance=self.coin_spawn_distance, cluster_size=int(math.sqrt(cluster)))
            if location_choices:
                location = random.choice(location_choices)

                for coin_row in range(int(math.sqrt(cluster))):
                    for coin_col in range(int(math.sqrt(cluster))):
                        self.grid[location[0] + coin_row][location[1] + coin_col] = "C"
            else:
                continue

        # Then enemies:
        for enemy in range(self.n_enemies):
            choices = self.find_sprite_spawn_locs(distance=self.enemy_spawn_distance)
            loc = random.choice(choices)
            self.grid[loc[0]][loc[1]] = "E"

        # Make a copy of the grid for exploration purpose
        self.grid_explored = self.grid

        # Initialize number of empty cells for map exploration skill
        #self.cells_unexplored = self.n_cells_unexplored()

        # Get starting wall location coordinates for revealing the map
        self.wall_coordinates = self.get_wall_coordinates(grid_size=2 * GRIDWIDTH)

        # Initialize number of walls for percentage calculations
        #self.n_walls = len(self.wall_coordinates)

        self.fill_map(self.grid)

    def cluster_sprites(self, n):
        choices = n
        clusters = []

        while choices != 0:
            # Min and max sizes of clusters
            cluster_size_choices = []
            for i in range(len(self.cluster_sizes)):
                cluster_size_choices.append(self.cluster_sizes[i])

                if self.cluster_sizes[i] > choices:
                    cluster_size_choices = cluster_size_choices[:-1]
                    break

            if not cluster_size_choices:
                cluster_size = 1
            else:
                cluster_size = random.choice(cluster_size_choices)

            clusters.append(cluster_size)
            choices = choices - cluster_size
            if choices < 0:
                break

        return clusters

    def find_sprite_spawn_locs(self, clearance=1, distance=5, cluster_size=1):
        locations = []
        for row in range(-distance - clearance, distance + 1 - clearance, 1):
            for col in range(-distance - clearance, distance + 1 - clearance, 1):

                check_row = self.player_row + row
                check_col = self.player_col + col

                if self.square_empty(check_row, check_col, cluster_size + 2 * clearance):
                    locations.append([check_row + clearance, check_col + clearance])

        return locations

    def square_empty(self, row, col, squaresize):
        for drow in range(squaresize):
            if self.grid[row + drow][col: col + squaresize] != [" "] * squaresize:
                return False
        return True

    def fill_map(self, walls_grid):
        for row in range(len(walls_grid)):
            for col in range(len(walls_grid[0])):
                if walls_grid[row][col] == "W":
                    Wall(self.game, col, row)
                if walls_grid[row][col] == "C":
                    Coin(self.game, col, row)
                if walls_grid[row][col] == "E":
                    Enemy(self.game, col, row)

    def spawn_sprite(self, sprite, spawn_distance, cluster_size= 1):
        choices = self.find_sprite_spawn_locs(distance=spawn_distance, cluster_size=cluster_size)
        if choices:
            loc = random.choice(choices)
            if cluster_size == 1:
                sprite(self.game, loc[1], loc[0])
            if cluster_size == 4:
                for row in range(cluster_size):
                    for col in range(cluster_size):
                        sprite(self.game, loc[1] + col, loc[0] + row)
        else:
            pass

    def n_cells_unexplored(self):
        self.n_cells = 0
        for row in self.grid:
            for cell in row:
                if cell == " ":
                    self.n_cells += 1
        return self.n_cells

    def n_cells_explored(self):

        x_lower = int(self.game.player.rect.x / TILESIZE - ((SCREEN_WIDTH / 2) / TILESIZE))
        x_upper = int(self.game.player.rect.x / TILESIZE + ((SCREEN_WIDTH / 2) / TILESIZE))
        y_lower = int(self.game.player.rect.y / TILESIZE - ((SCREEN_HEIGHT / 2) / TILESIZE))
        y_upper = int(self.game.player.rect.y / TILESIZE + ((SCREEN_HEIGHT / 2) / TILESIZE))

        if x_lower < 0:
            x_lower = 0
        if y_lower < 0:
            y_lower = 0
        if x_upper > MAPGRIDWIDTH:
            x_upper = MAPGRIDWIDTH
        if y_upper > MAPGRIDHEIGHT:
            y_upper = MAPGRIDHEIGHT

        for row in range(y_lower, y_upper, 1):
            for col in range(x_lower, x_upper, 1):
                if self.grid_explored[row][col] == " ":
                    self.grid_explored[row][col] = "."
                    self.cells_explored += 1

    def make_grid(self):
        # First, copy walls layout
        grid = deepcopy(self.grid_walls_only)
        # Next, find locations of existing coins
        for coin in self.game.coins:
            y = int(coin.rect.y / TILESIZE)
            x = int(coin.rect.x / TILESIZE)
            grid[y][x] = "C"

        # Same for enemy sprites
        for enemy in self.game.enemies:
            y = int(enemy.rect.y / TILESIZE)
            x = int(enemy.rect.x / TILESIZE)
            grid[y][x] = "E"

        # Lastly, add players location
        y = int(self.game.player.rect.y / TILESIZE)
        x = int(self.game.player.rect.x / TILESIZE)
        grid[y][x] = "P"

        #grid = [[" " for col in range(MAPGRIDWIDTH + 1)] for row in range(MAPGRIDHEIGHT + 1)]
        #for sprite in self.game.all_sprites:
        #    name = sprite.__class__.__name__
        #    y = int(sprite.rect.y / TILESIZE)
        #    x = int(sprite.rect.x / TILESIZE)
        #    grid[y][x] = name[0]
        return grid

    def print_map(self, grid):
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                print(grid[i][j], end=" ")
            print()

    def get_wall_coordinates(self, grid_size=GRIDWIDTH):

        # grid_size parameter determines the size of the grid around the player
        # which will have the walls revealed

        # coords list will have the coordinates of each wall location
        # which will be used to spawn wall sprites
        coords = []

        # iterate through the grid around the center of the map and get wall locations
        for row in range(int(-grid_size / 2), int(grid_size / 2), 1):

            for col in range(int(-grid_size / 2), int(grid_size / 2), 1):

                check_row = row + PLAYER_START_POS[1]
                check_col = col + PLAYER_START_POS[0]

                if self.grid[check_row][check_col] == "W":
                    coords.append([check_row, check_col])

        return coords

    def random_walk(self, height=GRIDHEIGHT * 3,
                    width=GRIDWIDTH * 3,
                    max_tunnels=MAX_TUNNELS,
                    max_length=MAX_LENGTH,
                    tunnel_width=TUNNEL_WIDTH):
        gap = int((tunnel_width - 1) / 2)
        grid = [["W" for col in range(width)] for row in range(height)]

        # Starting location of the walk. Also
        # a starting location of player
        current_row = int(MAPGRIDHEIGHT / 2)
        current_col = int(MAPGRIDWIDTH / 2)

        directions = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        random_direction = random.choice(directions)
        last_direction = [2, 2]
        while max_tunnels > 0:

            # Check if different direction was chosen
            while ((random_direction[0] == last_direction[0] and
                    random_direction[1] == last_direction[1]) or
                   (random_direction[0] == -last_direction[0] and
                    random_direction[1] == -last_direction[1])):
                random_direction = random.choice(directions)

            random_length = random.randint(gap, max_length)
            tunnel_length = 0

            while tunnel_length < random_length:
                if ((current_row <= 0 + gap and random_direction[0] == -1 or
                     current_col <= 0 + gap and random_direction[1] == -1) or
                        (current_row > height - 1 - gap and random_direction[0] == 1 or
                         current_col > width - 1 - gap and random_direction[1] == 1)):
                    break
                else:
                    for drow in range(-gap, gap + 1, 1):
                        for dcol in range(-gap, gap + 1, 1):
                            if ((current_row + drow < 0 or current_row + drow > height - 1) or
                                    (current_col + dcol < 0 or current_col + dcol > width - 1)):
                                break
                            else:
                                grid[current_row + drow][current_col + dcol] = " "
                    current_row += random_direction[0]
                    current_col += random_direction[1]
                    tunnel_length += 1

            last_direction = random_direction
            max_tunnels -= 1

        # Put player starting position on the grid
        grid[int(MAPGRIDHEIGHT / 2)][int(MAPGRIDWIDTH / 2)] = "P"
        return grid

    def adjacent(self, grid):
        dims = len(grid)
        adjacent = [[1 for col in range(dims * 3)] for row in range(dims * 3)]
        adjacent_rw = self.random_walk(GRIDHEIGHT * 3,
                                       GRIDWIDTH * 3,
                                       MAX_TUNNELS * 1,
                                       MAX_LENGTH * 1,
                                       TUNNEL_WIDTH)
        # Put RW generated grid in the middle of adjacent
        for row in range(dims * 3):
            for col in range(dims * 3):
                # Put grid in the center of adjacent
                if ((row >= dims and row < 2 * dims) and
                        (col >= dims and col < 2 * dims)):
                    adjacent[row][col] = grid[row - dims][col - dims]
                # Replicate sides onto adjacent
                if row == dims and col >= dims and col < 2 * dims:
                    adjacent[row - 1][col] = grid[row - dims][col - dims]
                if row == 2 * dims - 1 and col >= dims and col < 2 * dims:
                    adjacent[row + 1][col] = grid[row - dims][col - dims]
                if col == dims and row >= dims and row < 2 * dims:
                    adjacent[row][col - 1] = grid[row - dims][col - dims]
                if col == 2 * dims - 1 and row >= dims and row < 2 * dims:
                    adjacent[row][col + 1] = grid[row - dims][col - dims]
        # Replicate corners onto adjacent
        adjacent[dims - 1][dims - 1] = grid[0][0]
        adjacent[dims - 1][dims * 2] = grid[0][dims - 1]
        adjacent[dims * 2][dims * 2] = grid[dims - 1][dims - 1]
        adjacent[dims * 2][dims - 1] = grid[dims - 1][0]
        # Copy middle of adjacent onto center of RW grid
        for row in range(dims - 1, 2 * dims + 1, 1):
            for col in range(dims - 1, 2 * dims + 1, 1):
                adjacent_rw[row][col] = adjacent[row][col]
        return adjacent_rw

class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + int(SCREEN_WIDTH / 2)
        y = -target.rect.y + int(SCREEN_HEIGHT / 2)
        self.camera = pg.Rect(x, y, self.width, self.height)
