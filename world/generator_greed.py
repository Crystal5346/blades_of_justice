import pygame
import random
from config import WIDTH, HEIGHT
from world.environment import Wall
from .generator_base import BaseGenerator
from characters.enemies.greed.husks import Husk5, Husk6, Husk7


class GreedGenerator(BaseGenerator):
    def __init__(self, game):
        super().__init__(game)
        self.FLOOR_COLOR = (70, 50, 20)
        self.PLATFORM_COLOR = (218, 165, 32)
        self.PLATFORM_OUTLINE = (255, 215, 0)

    def generate(self, name):
        level_width = 6000
        self.game.level_width = level_width
        self.game.camera = self.game.init_camera(level_width, HEIGHT)

        floor = Wall(0, HEIGHT - 70, level_width, 70, self.FLOOR_COLOR)
        self.game.walls.add(floor)
        self.game.all_sprites.add(floor)

        self._generate_platforms(level_width)
        self._add_world_boundaries(level_width)
        self._spawn_greed_enemies(level_width, name)

        print(f"Greed Generator: Этап {name} готов.")

    def _generate_platforms(self, level_width):
        for x in range(800, level_width - 800, 600):
            w = random.randint(400, 600)
            y = random.randint(250, 450)
            plat = Wall(x, y, w, 40, self.PLATFORM_COLOR)
            pygame.draw.rect(plat.image, self.PLATFORM_OUTLINE, [0, 0, w, 40], 4)
            self.game.walls.add(plat)
            self.game.all_sprites.add(plat)

    def _spawn_greed_enemies(self, level_width, name):
        if "1-1" in name:
            pool = [Husk5, Husk6]
            count = 20
        elif "1-2" in name:
            pool = [Husk5, Husk6, Husk6]
            count = 25
            self._spawn_heavy_units(level_width, 2)
        elif "1-3" in name:
            pool = [Husk5, Husk6]
            count = 45
            self._spawn_heavy_units(level_width, 4)
        else:
            pool = [Husk5, Husk6]
            count = 15

        for i in range(count):
            ex = random.randint(1000, level_width - 500)
            etype = random.choice(pool)
            ey = random.randint(50, 200) if etype == Husk5 else random.randint(200, 500)
            enemy = etype(ex, ey, self.game)
            self.game.enemies.add(enemy)
            self.game.all_sprites.add(enemy)

    def _spawn_heavy_units(self, level_width, count):
        """Husk7 спавнятся равномерно, но СТРОГО в пределах уровня."""
        for i in range(count):
            ex = (level_width // 2) + (i * 800)
            # Не спавним за 400px до конца уровня — там портал
            if ex >= level_width - 400:
                break
            enemy = Husk7(ex, 400, self.game)
            self.game.enemies.add(enemy)
            self.game.all_sprites.add(enemy)

    def _add_world_boundaries(self, level_width):
        left = Wall(-10, 0, 10, HEIGHT, (0, 0, 0))
        self.game.walls.add(left)
        exit_p = Wall(level_width - 100, 0, 100, HEIGHT, (255, 255, 200))
        exit_p.image.set_alpha(100)
        self.game.all_sprites.add(exit_p)
