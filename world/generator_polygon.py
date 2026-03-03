import pygame
from world.generator_base import BaseGenerator
from world.environment import Wall, Platform
from characters.enemies.dummy import Dummy
from config import HEIGHT, FPS

class TextSign(pygame.sprite.Sprite):
    """Класс для надписей на стенах"""
    def __init__(self, x, y, text, size=24, color=(140, 140, 150)):
        super().__init__()
        # Используем стандартный шрифт, если Arial недоступен
        font = pygame.font.SysFont("Arial", size, bold=True)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))

class DummySpawner(pygame.sprite.Sprite):
    """Скрытый объект, который следит за возрождением манекена"""
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.pos = (x, y)
        self.image = pygame.Surface((1,1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.timer = 0
        self.interval = 30 * FPS 
        self.current_dummy = None
        
        # Инициализируем группу целей в объекте game, если её нет
        if not hasattr(self.game, 'targets'):
            self.game.targets = pygame.sprite.Group()
            
        self.spawn()

    def spawn(self):
        self.current_dummy = Dummy(self.pos[0], self.pos[1])
        # ВАЖНО: Добавляем в targets, а не в enemies!
        self.game.targets.add(self.current_dummy)
        self.game.all_sprites.add(self.current_dummy)

    def update(self):
        # Проверяем, жив ли манекен
        if not self.current_dummy or not self.current_dummy.is_alive:
            self.timer += 1
            if self.timer >= self.interval:
                self.spawn()
                self.timer = 0

class PolygonGenerator(BaseGenerator):
    def generate(self, name):
        self.clear_world()
        
        level_width = 2500
        self.game.level_width = level_width
        self.game.init_camera(level_width, HEIGHT)

        # Пол
        floor = Wall(0, HEIGHT - 60, level_width, 60, (220, 220, 230))
        self.game.walls.add(floor)
        self.game.all_sprites.add(floor)

        # 1. Тренировочная зона
        self.add_sign(400, 200, "ТРЕНИРОВКА НА МАНЕКЕНАХ", 36)
        
        p1 = Platform(300, HEIGHT - 180, 200, 20)
        self.game.walls.add(p1)
        self.game.all_sprites.add(p1)

        # Спавнеры
        self.game.all_sprites.add(DummySpawner(self.game, 400, p1.rect.top))
        self.game.all_sprites.add(DummySpawner(self.game, 700, floor.rect.top))
        self.game.all_sprites.add(DummySpawner(self.game, 150, floor.rect.top))
        self.game.all_sprites.add(DummySpawner(self.game, 900, floor.rect.top))

        # 2. Подсказки
        self.add_sign(1300, 250, "ВЫХОД ИЗ КОМНАТЫ", 28, (100, 100, 100))
        self.add_sign(1500, 450, "Shift — рывок сквозь снаряды", 22)
        self.add_sign(1800, 350, "Следи за полоской маны", 22)
        # Подсказка про новую кнопку
        self.add_sign(2350, 250, "Нажми O чтобы войти", 24, (255, 215, 0))

        # 3. Финальная дверь
        self.ready_door = Wall(2350, floor.rect.top - 150, 100, 150, (255, 215, 0))
        font = pygame.font.SysFont("Arial", 22, bold=True)
        txt = font.render("ГОТОВ?", True, (0, 0, 0))
        self.ready_door.image.blit(txt, (12, 60))
        
        self.game.all_sprites.add(self.ready_door)
        self.game.ready_door = self.ready_door 

    def add_sign(self, x, y, text, size=24, color=(140, 140, 150)):
        sign = TextSign(x, y, text, size, color)
        self.game.all_sprites.add(sign)
