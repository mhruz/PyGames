from globals import *
import pygame as pg
from utils import load_image


class Vilda(pg.sprite.Sprite):
    speed = 6
    speed_coef = 1.0
    images = {"left": [], "right": []}
    images_walk = {"left": [], "right": []}
    facing = pg.math.Vector2(0, 0)

    anim_frame = 0
    anim_frames = 4
    anim_frames_walk = 4
    anim_tick = 0
    anim_trigger = 6
    anim_trigger_walk = 16

    sound_move = None
    sound_fade = 20
    sound_fading = 0

    idle_frame = 0
    idle_tick = 0
    idle_trigger = 6
    idle_moves_y = [0, 1, 2, 0, -2, -1]

    falling_speed = 0
    free_fall = False
    walking = False

    def __init__(self, sound):
        pg.sprite.Sprite.__init__(self)

        image = load_image("resources/Little_bee.png")
        image_walk = load_image("resources/Little_bee_walk.png")
        for i in range(self.anim_frames):
            rect = pg.Rect(0, i * 40, 40, 40)
            tile = image.subsurface(rect)
            self.mask = pg.mask.from_surface(tile)
            self.images["right"].append(tile)
            self.images["left"].append(pg.transform.flip(tile.copy(), True, False))

            tile = image_walk.subsurface(rect)
            self.images_walk["right"].append(tile)
            self.images_walk["left"].append(pg.transform.flip(tile.copy(), True, False))

        self.sound_move = sound
        self.image = self.images["right"][0]
        self.rect = self.image.get_rect(topleft=SCREEN_RECT.topleft)
        self.orig_top = self.rect.top
        self.facing = pg.math.Vector2(1, 0)

        self.hitbox = self.rect
        self.hitbox.left += 5
        self.hitbox.right -= 5

    def move(self, direction):
        self.walking = False
        if self.free_fall:
            self.falling_speed += GRAVITY_ACC
            self.speed_coef = 0.5
        else:
            self.falling_speed = 0
            self.speed_coef = 1.0

        # Movement detected
        if direction[0] != 0 or direction[1] != 0:
            if direction[0] != 0:
                self.facing[0] = direction[0]

            # Flying
            if not self.free_fall:
                self.sound_move.play()
                self.sound_fading = 0
                self.idle_tick = 1
            # Walking
            else:
                self.walking = True
        # NO Movement
        else:
            self.sound_fading += 1
            if self.sound_fading == self.sound_fade:
                self.sound_move.stop()
                self.sound_fading = 0

            if not self.free_fall:
                self.idle_tick += 1
            else:
                self.idle_tick = 1

        if self.facing[0] == 1:
            if self.free_fall:
                self.image = self.images_walk["right"][self.anim_frame]
            else:
                self.image = self.images["right"][self.anim_frame]
        elif self.facing[0] == -1:
            if self.free_fall:
                self.image = self.images_walk["left"][self.anim_frame]
            else:
                self.image = self.images["left"][self.anim_frame]

        if not self.free_fall:
            self.rect.move_ip(direction[0] * self.speed * self.speed_coef, direction[1] * self.speed)
        else:
            self.rect.move_ip(direction[0] * self.speed * self.speed_coef, self.falling_speed)

        rect_clamped = self.rect.clamp(SCREEN_RECT)
        if rect_clamped != self.rect:
            self.falling_speed = 0

        self.rect = rect_clamped

    def switch_free_fall(self):
        if self.free_fall:
            self.rect.move_ip(0, -tile_size / 10)
        else:
            self.anim_frame = 0

        self.free_fall = not self.free_fall

    def set_position(self, x, y):
        self.rect = pg.Rect(x, y, tile_size, tile_size)

    def put_on_top(self, obj, offset=0):
        y_dif = obj.rect.top - self.rect.bottom
        self.rect.move_ip(0, y_dif + offset)

    def put_on_left(self, obj, offset=0):
        x_dif = self.rect.right - obj.rect.left
        self.rect.move_ip(-x_dif - offset, 0)

    def put_on_right(self, obj, offset=0):
        x_dif = obj.rect.right - self.rect.left
        self.rect.move_ip(x_dif + offset, 0)

    def update(self, *args, **kwargs) -> None:
        self.anim_tick += 1

        if self.free_fall:
            if self.anim_tick % self.anim_trigger_walk == 0 and self.walking:
                self.anim_tick = 0
                self.anim_frame = (self.anim_frame + 1) % self.anim_frames_walk
        else:
            if self.anim_tick % self.anim_trigger == 0:
                self.anim_tick = 0
                self.anim_frame = (self.anim_frame + 1) % self.anim_frames

            if self.idle_tick % self.idle_trigger == 0:
                self.idle_tick = 0
                self.idle_frame = (self.idle_frame + 1) % len(self.idle_moves_y)
                self.rect.move_ip(0, self.idle_moves_y[self.idle_frame])