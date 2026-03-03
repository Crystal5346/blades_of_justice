import pygame
import random
import math
from config import WIDTH, HEIGHT  # <-- ДОБАВЬ ЭТУ СТРОКУ
from characters.enemies.base_enemy import Enemy

class GreedEnemy(Enemy):
    """Базовый класс для врагов слоя Greed"""
    def __init__(self, x, y, hp, speed, level, game):
        super().__init__(x, y, hp=hp, mp=0, speed=speed, level=level, target=game.player)
        self.game = game
        self.gravity = 0.8

    def apply_physics(self, dx=0):
        self.vel_y += self.gravity
        self.check_world_collisions(self.game.walls, dx, self.vel_y)

class Husk5(Enemy):
    """Летающая оболочка. Пикирует на игрока """
    def __init__(self, x, y, game):
        super().__init__(x, y, hp=70, mp=0, speed=4, level=3, target=game.player)
        self.game = game
        self.image = pygame.Surface((40, 40))
        self.image.fill((200, 200, 100)) # Песочный цвет
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dive_cooldown = 0
        self.is_diving = False

    def ai_behavior(self):
        dist_x = self.target.rect.centerx - self.rect.centerx
        dist_y = self.target.rect.centery - self.rect.centery
        distance = math.hypot(dist_x, dist_y)

        if not self.is_diving:
            # Парим над игроком
            target_y = self.target.rect.y - 200
            self.rect.y += (target_y - self.rect.y) * 0.05
            self.rect.x += (1 if dist_x > 0 else -1) * self.speed
            
            if distance < 400 and self.dive_cooldown <= 0:
                self.is_diving = True
                self.dive_cooldown = 180
        else:
            # Пикирование 
            norm = distance if distance > 0 else 1
            self.rect.x += (dist_x / norm) * 12
            self.rect.y += (dist_y / norm) * 12
            
            if self.rect.colliderect(self.target.rect):
                self.target.take_damage(15)
                self.is_diving = False
            
            if distance > 600 or self.rect.y > HEIGHT: # Если промахнулся
                self.is_diving = False

        if self.dive_cooldown > 0: self.dive_cooldown -= 1

class Husk6(GreedEnemy):
    """Поддерживающий враг. Песочная бомба повышает защиту союзников """
    def __init__(self, x, y, game):
        super().__init__(x, y, 120, 2, 4, game)
        self.image = pygame.Surface((45, 55))
        self.image.fill((255, 220, 150))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.buff_cooldown = 200

    def ai_behavior(self):
        self.buff_cooldown -= 1
        dist_x = self.target.rect.centerx - self.rect.centerx
        dx = (1 if dist_x > 0 else -1) * self.speed
        
        # Если рядом есть союзники и КД прошел — кидает бомбу 
        if self.buff_cooldown <= 0:
            self.throw_sand_bomb()
            self.buff_cooldown = 300
            
        self.apply_physics(dx)

    def throw_sand_bomb(self):
        # Логика взрыва, который ищет спрайты в self.game.enemies и хилит/баффает их
        for enemy in self.game.enemies:
            dist = math.hypot(enemy.rect.centerx - self.rect.centerx, 
                              enemy.rect.centery - self.rect.centery)
            if dist < 250:
                # Временно повышаем защиту союзников 
                enemy.defense = getattr(enemy, 'defense', 0) + 5 

class Husk7(GreedEnemy):
    """Особый враг с валуном. Бросает и притягивает обратно """
    def __init__(self, x, y, game):
        super().__init__(x, y, 300, 1, 5, game)
        self.image = pygame.Surface((60, 80))
        self.image.fill((100, 100, 100)) # Каменный цвет
        self.rect = self.image.get_rect(topleft=(x, y))
        self.attack_timer = 0
        self.boulder_active = False

    def ai_behavior(self):
        self.attack_timer += 1
        dist_x = self.target.rect.centerx - self.rect.centerx
        
        # Малоподвижен, атакует на расстоянии [cite: 138]
        if abs(dist_x) < 700 and self.attack_timer % 240 == 0:
            self.throw_boulder()
            
        self.apply_physics(0)

    def throw_boulder(self):
        # Теперь просто вызываем тяжелый снаряд без передачи self
        self.game.combat_system.spawn_heavy_projectile(
            pos=self.rect.center,
            target_pos=self.target.rect.center,
            damage=30 # Увеличим урон, раз он больше не возвращается
        )
