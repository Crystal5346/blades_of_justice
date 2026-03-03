import pygame
import random
import math
from config import WIDTH, HEIGHT
from .base_enemy import Enemy   # Одна точка — ищем в той же папке (enemies)

class SmallHamster(Enemy):
    """
    Малый Хомяк: 'Ложный' босс. 
    Умирает с одного удара, запуская истинную битву.
    """
    def __init__(self, x, y, player, game=None):
        # hp=1, mp=0, speed=2, level=1, target=player
        super().__init__(x, y, 1, 0, 2, 1, player)
        self.game = game
        self.name = "GIGA HAMSTER" # Грозное имя для маленького существа
        
        # Визуал маленького хомяка
        self.image = pygame.Surface((30, 30))
        self.image.fill((150, 75, 0)) # Коричневый
        self.rect = self.image.get_rect(center=(x, y))
        
        self.is_boss = True # Чтобы HUD показал полоску HP

    def ai_behavior(self):
        """Простое движение в сторону игрока"""
        dist_x = self.target.rect.centerx - self.rect.centerx
        if abs(dist_x) > 5:
            self.rect.x += self.speed if dist_x > 0 else -self.speed

    def die(self):
        """Метод вызывается при HP <= 0. Спавнит настоящего босса."""
        print("СИСТЕМА: Истинный облик врага раскрыт!")
        
        # Создаем ГигаХомяка на том же месте
        # (Импорт внутри, чтобы избежать циклической зависимости)
        from characters.enemies.hamster import GigaHamster
        
        big_boss = GigaHamster(WIDTH // 2, HEIGHT - 300, self.target, self.game)
        
        if self.game:
            self.game.enemies.add(big_boss)
            self.game.all_sprites.add(big_boss)
        
        super().die() # Удаляем маленького хомяка


class GigaHamster(Enemy):
    """
    ГигаХомяк: Истинный финальный босс.
    Огромный размер, много HP и разрушительные атаки.
    """
    def __init__(self, x, y, player, game=None):
        # hp=5000, mp=1000, speed=4, level=20
        super().__init__(x, y, 5000, 1000, 4, 20, player)
        self.game = game
        self.name = "ВЕЛИКИЙ СВЯТОЙ ХОМЯК"
        
        # Визуал: Огромный золотой квадрат (или спрайт 250x250)
        self.image = pygame.Surface((250, 250))
        self.image.fill((255, 215, 0)) # Золотой цвет Святого Совета
        # Рисуем 'глаза' для устрашения
        pygame.draw.rect(self.image, (255, 255, 255), (50, 50, 40, 40))
        pygame.draw.rect(self.image, (255, 255, 255), (160, 50, 40, 40))
        
        self.rect = self.image.get_rect(center=(x, y))
        
        self.is_boss = True
        self.attack_timer = 0
        self.current_action = "IDLE"
        self.action_duration = 0

    def ai_behavior(self):
        """Основной цикл ИИ босса"""
        self.attack_timer += 1
        
        if self.current_action == "IDLE":
            # Выбор атаки каждые 2 секунды
            if self.attack_timer > 120:
                self.attack_timer = 0
                self.current_action = random.choice(["ROLL", "JUMP", "BEAM"])
                self.action_duration = 100 # Длительность фазы атаки
        
        elif self.current_action == "ROLL":
            self.perform_roll()
        elif self.current_action == "JUMP":
            self.perform_jump()
        elif self.current_action == "BEAM":
            self.perform_beam()

        # Возврат в IDLE по истечении времени
        if self.current_action != "IDLE":
            self.action_duration -= 1
            if self.action_duration <= 0:
                self.current_action = "IDLE"

    def perform_roll(self):
        """Атака перекатом: быстрое движение к игроку"""
        dist_x = self.target.rect.centerx - self.rect.centerx
        move_dir = 1 if dist_x > 0 else -1
        self.rect.x += move_dir * (self.speed * 2.5)
        
        # Урон при столкновении
        if self.rect.colliderect(self.target.rect):
            self.target.take_damage(20)

    def perform_jump(self):
        """Прыжок: босс пытается раздавить игрока"""
        if self.action_duration == 99: # В начале атаки даем импульс вверх
            self.vel_y = -20
        
        # Движение в воздухе к игроку
        dist_x = self.target.rect.centerx - self.rect.centerx
        if abs(dist_x) > 10:
            self.rect.x += (1 if dist_x > 0 else -1) * self.speed

    def perform_beam(self):
        """Логика динамического луча"""
        if self.action_duration > 70:
            # ФАЗА 1: Прицеливание (замирает и фиксирует позицию игрока)
            if self.action_duration == 99:
                self.beam_target_pos = (self.target.rect.centerx, self.target.rect.centery)
            self.rect.x += random.randint(-3, 3) # Эффект дрожания при зарядке
            
        elif self.action_duration == 70:
            # ФАЗА 2: Момент выстрела (создаем объект луча)
            self.spawn_mega_beam()
            
    def spawn_mega_beam(self):
        # Используем твой CombatSystem для создания луча
        # Передаем координаты Хомяка и зафиксированную точку цели
        self.game.combat_system.spawn_projectile(
            self.rect.center, 
            self.beam_target_pos, 
            damage=40, 
            is_spear=True, # Используем pierce=True для луча
            color=(255, 50, 50), # Красный лазер
            size=(800, 40) # Очень длинный и широкий луч
        )

    def die(self):
        print("ПОБЕДА: Святой Хомяк повержен. Габриэль исполнил свой долг.")
        super().die()
        
