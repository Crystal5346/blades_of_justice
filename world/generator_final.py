import pygame
from world.environment import Wall
import random
from config import WIDTH, HEIGHT
from characters.enemies.hamster import SmallHamster, GigaHamster


class DisappearingPlatform(pygame.sprite.Sprite):
    """
    Платформа, которая исчезает от луча или со временем,
    но ОБЯЗАТЕЛЬНО возрождается через respawn_delay кадров.
    """

    def __init__(self, x, y, w, h, color, game):
        super().__init__()
        self.game = game
        self.base_color = color
        self.original_pos = (x, y)
        self.original_size = (w, h)

        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        # Полоска сверху для визуала
        pygame.draw.rect(self.image, (255, 255, 255), (0, 0, w, 4))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.active = True
        self.timer = 0
        self.respawn_delay = 300        # 5 сек до возрождения
        self.life_timer = random.randint(400, 700)  # Живёт 7-12 сек

    def update(self):
        if not self.active:
            # Считаем таймер возрождения
            self.timer -= 1
            if self.timer <= 0:
                self._respawn()
        else:
            # Мерцание перед исчезновением
            self.life_timer -= 1
            if self.life_timer < 60:
                alpha = 255 if (self.life_timer % 10) < 5 else 60
                self.image.set_alpha(alpha)
            if self.life_timer <= 0:
                self.vanish()

            # Исчезает от луча (снаряды с большим уроном)
            hits = pygame.sprite.spritecollide(self, self.game.combat_system.projectiles, False)
            for proj in hits:
                if proj.damage >= 40:
                    self.vanish()
                    break

    def vanish(self):
        if self.active:
            self.active = False
            self.timer = self.respawn_delay
            self.game.walls.remove(self)
            self.game.all_sprites.remove(self)

    def _respawn(self):
        """Возрождаем платформу на исходном месте."""
        self.active = True
        self.life_timer = random.randint(400, 700)
        self.image = pygame.Surface(self.original_size)
        self.image.fill(self.base_color)
        pygame.draw.rect(self.image, (255, 255, 255), (0, 0, self.original_size[0], 4))
        self.image.set_alpha(255)
        self.rect = self.image.get_rect(topleft=self.original_pos)
        self.game.walls.add(self)
        self.game.all_sprites.add(self)


class FinalGenerator:
    def __init__(self, game):
        self.game = game

    def generate(self, name):
        if name == "FinalCorridor":
            self._build_corridor()
        elif name == "FinalArena":
            self._build_arena()

    def _build_corridor(self):
        """
        Длинный коридор с колоннами и стражем (SmallHamster).
        SmallHamster при смерти сам спавнит GigaHamster — никаких загрузочных экранов.
        Игрок просто проходит коридор, убивает стража, и сразу начинается бой.
        """
        length = 6000
        self.game.level_width = length
        self.game.init_camera(length, HEIGHT)

        # Пол и потолок
        floor = Wall(0, HEIGHT - 100, length, 100, (140, 140, 130))
        ceiling = Wall(0, 0, length, 100, (200, 200, 190))
        self.game.walls.add(floor, ceiling)
        self.game.all_sprites.add(floor, ceiling)

        # Колонны (декор)
        for x in range(400, length, 800):
            pillar_shadow = Wall(x - 20, 100, 100, HEIGHT - 200, (220, 220, 210))
            pillar = Wall(x, 100, 60, HEIGHT - 200, (255, 255, 250))
            self.game.all_sprites.add(pillar_shadow, pillar)

        # Страж — SmallHamster на 3/4 пути
        # При смерти он сам создаст GigaHamster прямо там
        monster = SmallHamster(4500, HEIGHT - 200, self.game.player, self.game)
        monster.name = "Minster"
        self.game.enemies.add(monster)
        self.game.all_sprites.add(monster)
        print("SYSTEM: Страж 'Minster' (SmallHamster) заспавнен. При смерти — появится GigaHamster.")

        # Финальные врата (визуальный маркер)
        gate = Wall(length - 150, HEIGHT - 400, 100, 300, (255, 215, 0))
        self.game.all_sprites.add(gate)

    def _build_arena(self):
        """
        Золотая арена для боя с GigaHamster.
        Платформы возрождаются сами — см. DisappearingPlatform._respawn().
        GigaHamster спавнится здесь только если зашли через stage_manager напрямую.
        Обычный путь: коридор → убили SmallHamster → GigaHamster появился прямо там.
        """
        self.game.level_width = WIDTH
        self.game.init_camera(WIDTH, HEIGHT)

        # Пол золотой
        floor = Wall(0, HEIGHT - 100, WIDTH, 100, (255, 215, 0))
        self.game.walls.add(floor)
        self.game.all_sprites.add(floor)

        # Боковые стены (арена закрытая)
        left_wall = Wall(-20, 0, 20, HEIGHT, (50, 50, 50))
        right_wall = Wall(WIDTH, 0, 20, HEIGHT, (50, 50, 50))
        self.game.walls.add(left_wall, right_wall)
        self.game.all_sprites.add(left_wall, right_wall)

        # Исчезающие платформы — возрождаются через ~5 сек
        platform_positions = [
            (WIDTH // 6,       HEIGHT - 300),
            (WIDTH // 6 * 4,   HEIGHT - 300),
            (WIDTH // 3,       HEIGHT - 480),
            (WIDTH // 3 * 2,   HEIGHT - 480),
        ]
        for pos in platform_positions:
            p = DisappearingPlatform(pos[0], pos[1], 200, 25, (255, 255, 255), self.game)
            self.game.all_sprites.add(p)
            self.game.walls.add(p)

        # Центральная платформа для босса (не исчезает)
        center_plat = Wall(WIDTH // 2 - 150, HEIGHT - 250, 300, 30, (200, 200, 200))
        self.game.walls.add(center_plat)
        self.game.all_sprites.add(center_plat)

        # Спавн GigaHamster (только при прямом заходе на FinalArena)
        boss = GigaHamster(WIDTH // 2, HEIGHT - 320, self.game.player, self.game)
        boss.game = self.game
        boss.name = "ВЕЛИКИЙ СВЯТОЙ ХОМЯК"
        self.game.enemies.add(boss)
        self.game.all_sprites.add(boss)
        print("SYSTEM: МЕГА ХОМЯК ПРИБЫЛ!")
