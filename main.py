from game import Game
import pygame as pg
import cProfile
import re

def main():
    g = Game()
    temp = 0
    while g.running:
        g.new_game()
        g.run()

    pg.quit()

main()