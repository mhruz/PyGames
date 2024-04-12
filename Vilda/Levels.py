import numpy as np
import pygame as pg

from globals import *
from utils import load_image
from Tiles import SolidTile


def create_level_random(size):
    level_map = np.zeros(size)

    max_height = 8
    heights = np.random.randint(0, max_height, size=size[0])
    for i, h in enumerate(heights):
        level_map[i, size[1]-h:] = 1

    return level_map


class Level:
    def __init__(self, size=(20, 15)):
        self.size = size
        self.level_map = np.zeros(size)

        image = load_image("resources/Dirt.png")
        self.tiles = []

        for i in range(2):
            rect = pg.Rect(0, i * 40, 40, 40)
            tile = image.subsurface(rect)
            self.tiles.append(tile)

    def set_map(self, level_map):
        self.level_map = level_map

    def render_map(self, renders):
        tiles = pg.sprite.Group()

        coords = np.where(self.level_map == 1)

        for cx, cy in zip(coords[0], coords[1]):
            if self.level_map[cx, cy - 1] == 1:
                tiles.add(SolidTile(self.tiles[1], (cx * tile_size, cy * tile_size)))
            else:
                tiles.add(SolidTile(self.tiles[0], (cx * tile_size, cy * tile_size)))

        renders.add(tiles)

        return tiles
