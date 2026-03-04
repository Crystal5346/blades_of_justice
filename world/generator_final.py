import pygame
from world.environment import Wall
import random
from config import WIDTH, HEIGHT
from characters.enemies.hamster import SmallHamster, GigaHamster

class DisappearingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color, game):
        super().__init__()
        self.game = game
        self.base_color = color
        self.image = pygame.Surface((w, h))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.active = True
        self.timer = 0
        self.respawn_delay = 300 # 5 секунд на восстановление
        self.life_timer = random.randint(200, 400) # Время жизни платформы (3-6 сек)

    #проверка коллизий с игроком и снарядами (лучами) для запуска разрушения.
    def update(self):
        if not self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.reset_platform()
        else:
            # 1. Естественный износ (платформа мерцает перед исчезновением)
            self.life_timer -= 1
            if self.life_timer < 60:
                # Мерцание в последнюю секунду
                alpha = 255 if self.life_timer % 10 < 5 else 0
                self.image.set_alpha(alpha)
            
            if self.life_timer <= 0:
                self.vanish()

            # 2. Проверка столкновения с Лучом (из группы projectiles)
            hits = pygame.sprite.spritecollide(self, self.game.combat_system.projectiles, False)
            for proj in hits:
                # Если в платформу влетел 'луч' (большой урон или размер)
                if proj.damage >= 40: 
                    self.vanish()

    #процесс деактивации платформы и запуска таймера восстановления.
    def vanish(self):
        if self.active:
            self.active = False
            self.timer = self.respawn_delay
            self.game.walls.remove(self)
            self.game.all_sprites.remove(self)

    #логика возрождения платформы.
    def reset_platform(self):
        self.active = True
        self.life_timer = random.randint(200, 400)
        self.image.set_alpha(255)
        self.game.walls.add(self)
        self.game.all_sprites.add(self)

class FinalGenerator:
    def __init__(self, game):
        self.game = game

    def generate(self, name):
        """Центральный метод выбора генерации"""
        if name == "FinalCorridor":
            self._build_corridor()
        elif name == "FinalArena":
            self._build_arena()

    def _build_corridor(self):
        """Создание Коридора Суда со стражем"""
        length = 6000 
        self.game.level_width = length
        self.game.init_camera(length, HEIGHT)
        
        # 1. Пол и Потолок
        floor = Wall(0, HEIGHT - 100, length, 100, (140, 140, 130))
        ceiling = Wall(0, 0, length, 100, (200, 200, 190))
        self.game.walls.add(floor, ceiling)
        self.game.all_sprites.add(floor, ceiling)

        # 2. Декорации (Колонны)
        for x in range(400, length, 800):
            pillar_shadow = Wall(x-20, 100, 100, HEIGHT-200, (220, 220, 210))
            pillar = Wall(x, 100, 60, HEIGHT-200, (255, 255, 250))
            self.game.all_sprites.add(pillar_shadow, pillar)

        # 3. СПАВН СТРАЖА (Мини-Хомяк)
        # Ставим его примерно на 3/4 пути (4500px)
        # ИСПРАВЛЕНИЕ ТУТ:
        # Спавним SmallHamster (того самого, который 'Minster')
        monster = SmallHamster(4500, HEIGHT - 200, self.game.player, self.game)
        monster.name = "Minster"  # Оставляем имя для логики двери в main.py
        
        self.game.enemies.add(monster)
        self.game.all_sprites.add(monster)
        print("SYSTEM: Страж 'Minster' (SmallHamster) заспавнен.")  # ТО САМОЕ ИМЯ ДЛЯ ОБНАРУЖЕНИЯ В main.py

        # 4. Финальные врата (Визуальный триггер)
        gate = Wall(length - 150, HEIGHT - 400, 100, 300, (255, 215, 0))
        self.game.all_sprites.add(gate)

    def _build_arena(self):
        """Создание Арены для битвы с Боссом"""
        self.game.level_width = WIDTH
        self.game.init_camera(WIDTH, HEIGHT)
        
        boss_platform = Wall(WIDTH//2 - 200, HEIGHT - 250, 400, 40, (200, 200, 200))
        self.game.walls.add(boss_platform)
        self.game.all_sprites.add(boss_platform)

        # Спавним хомяка прямо на неё
        boss = GigaHamster(WIDTH // 2, HEIGHT - 350, self.game.player, self.game)
        
        # 1. Пол (Золотой)
        floor = Wall(0, HEIGHT - 100, WIDTH, 100, (255, 215, 0))
        self.game.walls.add(floor)
        self.game.all_sprites.add(floor)

        # 2. Невидимые стены по бокам
        left_wall = Wall(-20, 0, 20, HEIGHT, (0, 0, 0))
        right_wall = Wall(WIDTH, 0, 20, HEIGHT, (0, 0, 0))
        self.game.walls.add(left_wall, right_wall)

        # 3. Исчезающие платформы
        platform_positions = [
            (WIDTH // 6, HEIGHT - 300),
            (WIDTH // 6 * 4, HEIGHT - 300),
            (WIDTH // 3, HEIGHT - 500),
            (WIDTH // 3 * 2, HEIGHT - 500)
        ]
        for pos in platform_positions:
            p = DisappearingPlatform(pos[0], pos[1], 200, 25, (255, 255, 255), self.game)
            self.game.all_sprites.add(p)
            self.game.walls.add(p)

        # 4. СПАВН БОЛЬШОГО ХОМЯКА
        boss = GigaHamster(WIDTH // 2, HEIGHT - 300, self.game.player, self.game)
        boss.game = self.game
        boss.name = "MegaHamster"
        boss.max_hp = 5000
        boss.hp = 5000
        # Если есть механика увеличения спрайта:
        # boss.image = pygame.transform.scale(boss.image, (150, 150))
        # boss.rect = boss.image.get_rect(center=boss.rect.center)
        
        self.game.enemies.add(boss)
        self.game.all_sprites.add(boss)
        print("SYSTEM: МЕГА ХОМЯК ПРИБЫЛ!")
