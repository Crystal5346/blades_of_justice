import pygame
import random
from config import WIDTH, HEIGHT
from world.environment import Wall
from .generator_base import BaseGenerator
# Импортируем новых врагов Жадности
from characters.enemies.greed.husks import Husk5, Husk6, Husk7

class GreedGenerator(BaseGenerator):
    def __init__(self, game):
        super().__init__(game)
        # Цветовая палитра Жадности (Золото, песок, выжженная земля)
        self.FLOOR_COLOR = (70, 50, 20)      # Темный песок
        self.PLATFORM_COLOR = (218, 165, 32) # Золотистый (Goldenrod)
        self.PLATFORM_OUTLINE = (255, 215, 0) # Яркое золото

    def generate(self, name):
        """Генерация этапов Жадности (2-1, 2-2, 2-3)"""
        level_width = 6000 # Уровни Жадности чуть длиннее для маневров
        self.game.level_width = level_width
        self.game.camera = self.game.init_camera(level_width, HEIGHT)

        # 1. Пол
        floor_h = 70
        floor = Wall(0, HEIGHT - floor_h, level_width, floor_h, self.FLOOR_COLOR)
        self.game.walls.add(floor)
        self.game.all_sprites.add(floor)

        # 2. Платформы (в Greed их сделаем шире для массовых драк)
        self._generate_platforms(level_width)

        # 3. Границы и выход
        self._add_world_boundaries(level_width)

        # 4. Спавн врагов (самое важное)
        self._spawn_greed_enemies(level_width, name)

        print(f"Greed Generator: Этап {name} готов. Дроны отсутствуют по протоколу.")

    def _generate_platforms(self, level_width):
        # В Greed платформы — это длинные "золотые" плиты
        for x in range(800, level_width - 800, 600):
            w = random.randint(400, 600)
            y = random.randint(250, 450)
            plat = Wall(x, y, w, 40, self.PLATFORM_COLOR)
            pygame.draw.rect(plat.image, self.PLATFORM_OUTLINE, [0, 0, w, 40], 4)
            self.game.walls.add(plat)
            self.game.all_sprites.add(plat)

    def _spawn_greed_enemies(self, level_width, name):
        """Логика спавна по этапам из ТЗ"""
        
        # Настраиваем сложность в зависимости от этапа
        if "1-1" in name: # Начало Жадности
            pool = [Husk5, Husk6] # Летающие и Поддержка
            count = 20
        elif "1-2" in name: # Глубже в пески
            pool = [Husk5, Husk6, Husk6] # Больше поддержки
            count = 25
            # Спавним пару тяжеловесов Husk7 в ключевых точках
            self._spawn_heavy_units(level_width, 2)
        elif "1-3" in name: # Восстание (Массовое сражение)
            pool = [Husk5, Husk6] 
            count = 45 # Резкое увеличение количества оболочек
            self._spawn_heavy_units(level_width, 4)

        # Основной спавн
        for i in range(count):
            ex = random.randint(1000, level_width - 500)
            etype = random.choice(pool)
            
            # Летающие Husk5 спавнятся высоко
            ey = random.randint(50, 200) if etype == Husk5 else random.randint(200, 500)
            
            enemy = etype(ex, ey, self.game)
            self.game.enemies.add(enemy)
            self.game.all_sprites.add(enemy)

    def _spawn_heavy_units(self, level_width, count):
        """Отдельный спавн для Husk7 (Враг с валуном)"""
        for i in range(count):
            # Ставим их на ровном расстоянии во второй половине уровня
            ex = (level_width // 2) + (i * 1000) 
            enemy = Husk7(ex, 400, self.game)
            self.game.enemies.add(enemy)
            self.game.all_sprites.add(enemy)

    def _add_world_boundaries(self, level_width):
        # Левая невидимая стена
        left = Wall(-10, 0, 10, HEIGHT, (0,0,0))
        self.game.walls.add(left)
        
        # Портал выхода (Белое марево пустыни)
        exit_p = Wall(level_width - 100, 0, 100, HEIGHT, (255, 255, 200))
        exit_p.image.set_alpha(100)
        self.game.all_sprites.add(exit_p)
