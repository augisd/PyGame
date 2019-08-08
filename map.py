import pygame as pg
import random
from settings import *
from sprites import *
from pygame.locals import *
class Map:
    def __init__(self, game):
        self.game = game
        self.grid = 0
        self.grid_explored = 0
        self.cells_explored = 0
        self.cells_unexplored = 0
        self.percentage_map_explored = 0
        self.width = GRIDWIDTH * 2
        self.height = GRIDHEIGHT * 2
        self.n_coins = N_COINS
        self.n_enemies = N_ENEMIES
        self.cluster_sizes = [1, 4, 9, 16, 25, 36]
        self.sprite_spawn_distance = SPAWN_DIST #int(GRIDWIDTH / 2)
        random.seed(6)
        self.create_map()

    def update(self):
        #self.player_row = int(self.game.player.y / TILESIZE)
        #self.player_col = int(self.game.player.x / TILESIZE)
        if len(self.game.coins) == 0:
            #random.seed(COIN_SEED)
            for coin in range(self.n_coins):
                self.grid = self.make_grid()
                self.spawn_sprite(Coin)

        if len(self.game.enemies) < N_ENEMIES:
            self.grid = self.make_grid()
            self.spawn_sprite(Enemy)

        # Check where in the grid the player has been
        # and update percentage of grid explored
        self.n_cells_explored()
        #self.cells_unexplored = self.cells_unexplored - self.cells_explored
        self.percentage_map_explored = self.cells_explored / self.cells_unexplored

    def create_map(self):
        walls = self.random_walk()
        #walls_adjacent = self.adjacent(walls)
        #self.grid = walls_adjacent

        # First create map layout (walls and walkable areas)
        # including player sprite starting position
        self.grid = walls

        # Initial player position (to be used for spawning sprites
        # around player):
        self.player_row = int(MAPGRIDHEIGHT / 2)
        self.player_col = int(MAPGRIDWIDTH / 2)

        # Next, determine initial spawn locations for coin
        # and enemy sprites
        # First spawn the coins:
        for coin in range(self.n_coins):
            choices = self.find_sprite_spawn_locs(distance=self.sprite_spawn_distance)
            loc = random.choice(choices)
            self.grid[loc[0]][loc[1]] = "C"


        # Then enemies:
        for enemy in range(self.n_enemies):
            choices = self.find_sprite_spawn_locs(distance=self.sprite_spawn_distance)
            loc = random.choice(choices)
            self.grid[loc[0]][loc[1]] = "E"

        # Make a copy of the grid for exploration purpose
        self.grid_explored = self.grid

        # Initialize number of empty cells for map exploration skill
        self.cells_unexplored = self.n_cells_unexplored()
        print(self.cells_unexplored)

        self.fill_map(self.grid)

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
                elif walls_grid[row][col] == "C":
                    Coin(self.game, col, row)
                elif walls_grid[row][col] == "E":
                    Enemy(self.game, col, row)

    def spawn_sprite(self, sprite, cluster_size= 1):

        choices = self.find_sprite_spawn_locs(distance=self.sprite_spawn_distance, cluster_size=cluster_size)
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

    #print(self.player.rect.x / TILESIZE - ((SCREEN_WIDTH / 2) / TILESIZE), self.player.rect.x / TILESIZE + ((SCREEN_WIDTH / 2) / TILESIZE))

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
        grid = [[" " for col in range(MAPGRIDWIDTH)] for row in range(MAPGRIDHEIGHT)]
        for sprite in self.game.all_sprites:
            name = sprite.__class__.__name__
            y = int(sprite.rect.y / TILESIZE)
            x = int(sprite.rect.x / TILESIZE)
            grid[y][x] = name[0]

        return grid

    def print_map(self, grid):
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                print(grid[i][j], end=" ")
            print()

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
