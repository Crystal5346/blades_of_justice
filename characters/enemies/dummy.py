import pygame
# Предположим, Character — это твой базовый класс с HP и rect
from characters.character import Character 

class Dummy(Character):
    def __init__(self, x, y):
        # Передаем базовые параметры: HP=1000, скорость=0
        super().__init__(x, y, hp=1000, mp=0, speed=0)
        
        self.image = pygame.Surface((40, 60))
        self.image.fill((180, 140, 100)) # Дерево
        self.rect = self.image.get_rect(bottomleft=(x, y))
        
        # Настройки "безопасности"
        self.is_dummy = True
        self.damage = 0 
        self.is_boss = False

    def update(self, *args):
        # Переопределяем update, чтобы манекен не пытался ходить или прыгать
        pass

    def take_damage(self, amount):
        # Манекен просто впитывает урон
        self.hp -= amount
        if self.hp <= 0:
            self.hp = self.max_hp # Опционально: манекен бессмертен
