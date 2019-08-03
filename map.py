import pygame as pg
import random
from settings import *
from sprites import *
from pygame.locals import *
class Map:
    def __init__(self, game):
        self.game = game
        self.grid = 0
        self.width = GRIDWIDTH * 2
        self.height = GRIDHEIGHT * 2
        self.map_layout = 0
        self.create_map()


    def create_map(self):
        walls = self.random_walk()
        self.print_map(walls)
        # self.fill_walls(walls)
        walls_adjacent = self.adjacent(walls)
        print()
        self.print_map(walls_adjacent)
        self.map_layout = walls_adjacent
        self.grid = walls_adjacent
        self.fill_walls(walls_adjacent)

    def print_map(self, grid):
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                print(grid[i][j], end=" ")
            print()

    def get_layout(self):
        return self.map_layout

    def random_walk(self, height=GRIDHEIGHT,
                    width=GRIDWIDTH,
                    max_tunnels=MAX_TUNNELS,
                    max_length=MAX_LENGTH,
                    tunnel_width=TUNNEL_WIDTH):
        gap = int((tunnel_width - 1) / 2)
        grid = [["#" for col in range(width)] for row in range(height)]
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
                                grid[current_row + drow][current_col + dcol] = "."
                    current_row += random_direction[0]
                    current_col += random_direction[1]
                    tunnel_length += 1

            last_direction = random_direction
            max_tunnels -= 1
        return grid

    def fill_walls(self, walls_grid):
        for row in range(len(walls_grid)):
            for col in range(len(walls_grid[0])):
                if walls_grid[row][col] == "#":
                    Wall(self.game, col, row)

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

    # Iterate through map to find suitable locations based on needed clearance
    # returns an array with random coordinates [row, col]
    def find_spawn(self, clearance):
        locations = []
        for row in range(0, len(self.grid) - 2 * clearance, 1):
            for col in range(0, len(self.grid[0]) - 2 * clearance, 1):
                if self.square_empty(row, col, 1 + 2 * clearance):
                    locations.append([row + clearance, col + clearance])
        if locations:
            return random.choice(locations)
        else:
            pass

    def find_spawn2(self, clearance=0, distance = 5):
        locations = []
        for row in range(-distance, distance + 1, 1):
            for col in range(-distance, distance + 1, 1):
                if self.grid[int(len(self.grid)/2) + row][int(len(self.grid)/2) + col] == ".":
                    locations.append([int(len(self.grid)/2) + row, int(len(self.grid)/2) + col])
        print(locations)
        if locations:
            return random.choice(locations)
        else:
            pass

    def spawn_sprite2(self, sprite):
        spawn = self.find_spawn2()
        if spawn:
            sprite(self.game, spawn[1], spawn[0])
        else:
            pass

    def square_empty(self, row, col, squaresize):
        for drow in range(squaresize):
            if self.grid[row + drow][col: col + squaresize] != ["."] * squaresize:
                return False
        return True

    def spawn_sprite(self, sprite):
        spawn = self.find_spawn(SPAWN_GAP)
        if spawn:
            sprite(self.game, spawn[1], spawn[0])
        else:
            pass

    def n_walkable_cells(self):
        self.n_cells = 0
        for row in self.map_layout:
            for cell in row:
                if cell == ".":
                    self.n_cells += 1
        return self.n_cells


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
