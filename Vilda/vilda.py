import numpy as np

# import basic pygame modules
from pygame import mixer
from utils import load_image
from globals import *
from Vilda.Levels import Level, create_level_random

from Little_Bees import Vilda
from Tiles import SolidTile


def main():
    pg.init()
    mixer.init()

    screen = pg.display.set_mode((RESOLUTION[0], RESOLUTION[1]), pg.FULLSCREEN)
    # screen = pg.display.set_mode((RESOLUTION[0], RESOLUTION[1]))

    # create the background, tile the bgd image
    background = pg.Surface(SCREEN_RECT.size)
    background.fill((0, 200, 250))
    screen.blit(background, (0, 0))
    pg.display.flip()

    clock = pg.time.Clock()

    # Images
    wooden_floor = load_image("resources/wooden_floor.png")
    cave = load_image("resources/Cave.png")
    hive = load_image("resources/Bee_Hive.png")

    # Audio
    sound_bzz = mixer.Sound("resources/vilda_bzz.wav")
    # sound_bzz_2 = mixer.Sound("resources/vilda_bzz.wav")

    # Init entities
    vilda = Vilda(sound_bzz)
    # vilda_2 = Vilda(vilda_img, sound_bzz_2)

    wooden_floors = pg.sprite.Group()
    wooden_floors.add(SolidTile(wooden_floor, (400, 320)))
    wooden_floors.add(SolidTile(wooden_floor, (440, 320)))
    #
    # # under cave
    # wooden_floors.add(SolidTile(wooden_floor, (400, RESOLUTION[1] - 40)))
    # wooden_floors.add(SolidTile(wooden_floor, (440, RESOLUTION[1] - 40)))
    # wooden_floors.add(SolidTile(wooden_floor, (480, RESOLUTION[1] - 40)))
    # wooden_floors.add(SolidTile(wooden_floor, (520, RESOLUTION[1] - 40)))
    # wooden_floors.add(SolidTile(wooden_floor, (560, RESOLUTION[1] - 40)))
    #
    # # under hive
    # wooden_floors.add(SolidTile(wooden_floor, (100, 520)))
    # wooden_floors.add(SolidTile(wooden_floor, (140, 520)))
    # wooden_floors.add(SolidTile(wooden_floor, (180, 520)))
    #
    # large_objects = pg.sprite.Group()
    # large_objects.add(SolidTile(cave, (400, RESOLUTION[1] - 240)))
    # large_objects.add(SolidTile(hive, (100, 400)))
    #

    # Init sprites
    all_sprites = pg.sprite.RenderUpdates()
    collision_sprites_top = pg.sprite.Group()
    collision_sprites = pg.sprite.Group()

    level01 = Level()
    level01.set_map(create_level_random((20, 15)))
    level01_tiles = level01.render_map(all_sprites)

    # floor_sprites = pg.sprite.RenderUpdates()
    # large_objects_sprites = pg.sprite.RenderUpdates()
    #
    # for wf in wooden_floors:
    #     all_sprites.add(wf)
    #     floor_sprites.add(wf)
    all_sprites.add(wooden_floors)
    collision_sprites_top.add(wooden_floors)
    collision_sprites.add(level01_tiles)

    # for lo in large_objects:
    #     all_sprites.add(lo)
    #     large_objects_sprites.add(lo)

    all_sprites.add(vilda)
    # all_sprites.add(vilda_2)

    vilda.containers = all_sprites
    # vilda_2.containers = all_sprites

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return
                if event.key == pg.K_SPACE:
                    vilda.switch_free_fall()
                if event.key == pg.K_UP:
                    if vilda.free_fall:
                        vilda.switch_free_fall()

        key_state = pg.key.get_pressed()
        direction = (key_state[pg.K_RIGHT] - key_state[pg.K_LEFT], key_state[pg.K_DOWN] - key_state[pg.K_UP])
        vilda.move(direction)
        vilda.update()

        # direction_2 = (key_state[pg.K_d] - key_state[pg.K_a], key_state[pg.K_s] - key_state[pg.K_w])
        # vilda_2.move(direction_2)

        # if pg.sprite.spritecollide(self.player, self.enemies, False, pg.sprite.collide_mask):
        collided = pg.sprite.spritecollide(vilda, collision_sprites, False)
        if collided:
            blocking_left = None
            blocking_right = None
            blocking_bottom = None

            rect_right = vilda.rect.right
            rect_left = vilda.rect.left

            if vilda.walking:
                if vilda.facing == pg.math.Vector2(1, 0):
                    rect_right -= 12
                    rect_left += 8
                else:
                    rect_right -= 8
                    rect_left += 12

            for obj in collided:

                if vilda.walking:
                    walk_collide = pg.Rect.colliderect(
                        pg.Rect(rect_left, vilda.rect.top, rect_right-rect_left, vilda.rect.height),
                        obj)

                    if not walk_collide:
                        continue

                dist_left = rect_right - obj.rect.left
                dist_right = obj.rect.right - rect_left
                dist_top = vilda.rect.bottom - obj.rect.top

                if dist_left <= 0:
                    dist_left = np.inf
                if dist_right <= 0:
                    dist_right = np.inf
                if dist_top <= 0 or level01.level_map[obj.tile_pos[0], obj.tile_pos[1] - 1] == 1:
                    dist_top = np.inf

                idx = np.argmin(np.array([dist_left, dist_right, dist_top]))

                if idx == 0:
                    blocking_right = obj
                elif idx == 1:
                    blocking_left = obj
                elif idx == 2:
                    blocking_bottom = obj

            if blocking_bottom is not None:
                vilda.falling_speed = 0
                vilda.put_on_top(blocking_bottom)

            if blocking_right is not None:
                if vilda.walking:
                    vilda.put_on_left(blocking_right, offset=-12)
                else:
                    vilda.put_on_left(blocking_right)

            if blocking_left is not None:
                if vilda.walking:
                    vilda.put_on_right(blocking_left, offset=-12)
                else:
                    vilda.put_on_right(blocking_left)

        if vilda.free_fall:
            collided = pg.sprite.spritecollide(vilda, collision_sprites_top, False)

            if collided:
                right_leg_support = False
                left_leg_support = False
                supporting_obj = None

                for obj in collided:
                    if vilda.rect.bottom - obj.rect.top < tile_size / 4 + vilda.falling_speed:
                        if vilda.facing == pg.math.Vector2(1, 0):
                            if obj.rect.left <= vilda.rect.left + 8 < obj.rect.right:
                                left_leg_support = True
                                supporting_obj = obj
                            if obj.rect.left < vilda.rect.right - 12 <= obj.rect.right:
                                right_leg_support = True
                                supporting_obj = obj
                        else:
                            if obj.rect.left <= vilda.rect.left + 12 < obj.rect.right:
                                right_leg_support = True
                                supporting_obj = obj
                            if obj.rect.left < vilda.rect.right - 8 <= obj.rect.right:
                                left_leg_support = True
                                supporting_obj = obj

                    if left_leg_support or right_leg_support:
                        vilda.falling_speed = 0
                        vilda.put_on_top(supporting_obj)
                        break

        # clear/erase the last drawn sprites
        all_sprites.clear(screen, background)

        # update all the sprites
        all_sprites.update()

        # draw the scene
        dirty = all_sprites.draw(screen)
        pg.display.update(dirty)

        # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
        clock.tick(60)


if __name__ == "__main__":
    main()
