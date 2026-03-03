import pygame
import random
from config import WIDTH, HEIGHT
from world.environment import Wall
from .generator_base import BaseGenerator
# Импортируем только те классы, которые есть в husks.py
from characters.enemies.lust.husks import Husk1, Husk2, Husk3, StreetCleaner, LustDrone, HellGuardian

class LustGenerator(BaseGenerator):
    def __init__(self, game):
        super().__init__(game)
        # Цвета для "черновика" (яркие границы, чтобы видеть коллизии)
        self.FLOOR_COLOR = (40, 20, 60)
        self.PLATFORM_COLOR = (80, 40, 120)
        self.PLATFORM_OUTLINE = (120, 80, 180) # Цвет границ для подгонки ассетов

    def generate(self, name):
        """Основной метод генерации этапов Похоти (1-1, 1-2 и т.д.)"""
        # 1. Устанавливаем длину уровня
        level_width = 5000
        self.game.level_width = level_width # СОХРАНЯЕМ ШИРИНУ ДЛЯ ГЕЙМПЛЕЯ
        self.game.camera = self.game.init_camera(level_width, HEIGHT)

        # 2. Генерируем "Пол" уровня
        floor_height = 60
        floor = Wall(0, HEIGHT - floor_height, level_width, floor_height, self.FLOOR_COLOR)
        self.game.walls.add(floor)
        self.game.all_sprites.add(floor)

        # 3. Генерируем платформы
        self._generate_platforms(level_width)

        # 4. Границы и ПОРТАЛ ВЫХОДА
        self._add_world_boundaries(level_width)

        # 5. Спавним врагов
        self._spawn_lust_enemies(level_width, name)

        print(f"Lust Generator: Этап {name} построен. Ширина: {level_width}")

    def _add_world_boundaries(self, level_width):
        """Создает границы уровня и финишный портал"""
        WALL_COLOR = (120, 0, 255)
        
        # ЛЕВАЯ СТЕНА (Твердая, не дает уйти назад)
        left_border = Wall(-20, 0, 60, HEIGHT, WALL_COLOR)
        self.game.walls.add(left_border)
        self.game.all_sprites.add(left_border)
        
        # ПРАВАЯ ГРАНИЦА (Портал выхода)
        # Мы НЕ добавляем его в self.game.walls, чтобы игрок мог пройти СКВОЗЬ него
        exit_portal = Wall(level_width - 150, 0, 150, HEIGHT, (255, 255, 255))
        
        # Рисуем "свечение" портала
        exit_portal.image.set_alpha(150) # Делаем полупрозрачным
        pygame.draw.rect(exit_portal.image, (200, 240, 255), [0, 0, 150, HEIGHT], 10)
        
        # Добавляем их в группы
        self.game.all_sprites.add(exit_portal)
        self.game.walls.add(left_border)
        self.game.all_sprites.add(left_border)

    def _generate_platforms(self, level_width):
        """Создание островков с защитой от слипания"""
        last_y = HEIGHT // 2 # Начинаем от середины экрана
        
        # Увеличиваем шаг по X, чтобы платформы не стояли слишком плотно
        for x in range(600, level_width - 500, 480):
            # Решаем, сколько платформ будет в этом секторе (1 или 2)
            num_plats = random.randint(1, 2)
            
            for i in range(num_plats):
                w = random.randint(250, 400)
                h = 35 
                
                # --- ЛОГИКА РАССТОЯНИЯ ---
                # Если платформ две в одном секторе, разносим их по высоте минимум на 180 пикселей
                if i == 0:
                    # Первая платформа в секторе зависит от предыдущего сектора
                    y = last_y + random.randint(-150, 150)
                else:
                    # Вторая платформа в том же секторе должна быть сильно выше или ниже первой
                    y = last_y + random.choice([-200, 200])
                
                # Ограничиваем Y, чтобы платформы не уходили за края экрана
                y = max(150, min(y, HEIGHT - 250))
                last_y = y # Запоминаем для следующего итерации
                
                # Добавляем случайное смещение по X
                offset_x = random.randint(-100, 100)
                
                plat = Wall(x + offset_x, y, w, h, self.PLATFORM_COLOR)
                
                # Рисуем рамку чуть жирнее, чтобы на слабом ноуте было четче видно края
                pygame.draw.rect(plat.image, self.PLATFORM_OUTLINE, [0, 0, w, h], 3)
                
                self.game.walls.add(plat)
                self.game.all_sprites.add(plat)

    def _spawn_lust_enemies(self, level_width, name):
        """Расселение врагов по уровню с учетом новых типов"""
        
        # 1. Определяем список обычных врагов для этапа
        if "1-1" in name:
            # На первом этапе только простые враги и дроны
            enemy_pool = [Husk1, Husk2, LustDrone]
            count = 20
        else:
            # На 1-2 и далее добавляем элиту (Husk3) и Чистильщиков
            enemy_pool = [Husk1, Husk2, Husk3, StreetCleaner, LustDrone]
            count = 30
        
        # 2. Спавним обычных врагов
        for i in range(count):
            ex = random.randint(800, level_width - 600)
            # Для летающих дронов можно сделать спавн повыше, для остальных — на уровне платформ
            etype = random.choice(enemy_pool)
            
            if etype == LustDrone:
                ey = random.randint(100, 300) # Дроны парят в небе
            else:
                ey = random.randint(100, 400) # Остальные падают на платформы
            
            enemy = etype(ex, ey, self.game)
            self.game.enemies.add(enemy)
            self.game.all_sprites.add(enemy)

        # 3. СПАВН МИНИБОССА ( HellGuardian )
        # Добавим условие: он появляется только в конце этапа 1-2 или 1-3
        if "1-2" in name or "1-3" in name:
            # Ставим его ближе к концу уровня (например, за 1000 пикселей до портала)
            boss_x = level_width - 1200
            boss_y = 250 # Он парит в воздухе
            
            boss = HellGuardian(boss_x, boss_y, self.game)
            
            # Важно: Минибосс тоже должен быть в этих группах
            self.game.enemies.add(boss)
            self.game.all_sprites.add(boss)
            print(f"Lust Generator: Минибосс Страж Ада размещен на {boss_x}")
