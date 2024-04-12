from globals import *
import pygame as pg


class SolidTile(pg.sprite.Sprite):

    def __init__(self, image, position, sound=None):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect(topleft=position)
        self.tile_pos = (position[0] // tile_size, position[1] // tile_size)
