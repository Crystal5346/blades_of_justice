import pygame
import random
import math
from config import WIDTH, HEIGHT
from ..base_enemy import Enemy

class MinosBoss(Enemy):
    def __init__(self, x, y, player):
        # Передаем: x, y, hp, mp, speed, level, target
        super().__init__(x, y, 1000, 500, 4, 10, player)
        
        # Визуал
        self.image = pygame.Surface((120, 180))
        self.image.fill((150, 0, 255))
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.is_boss = True
        self.phase = 1
        self.is_active = True
        
        # Таймеры атак
        self.attack_cooldown = 0
        self.dash_timer = 0
        self.is_dashing = False

    def check_phase(self):
        """Переход во вторую фазу"""
        if self.hp < 500 and self.phase == 1:
            self.phase = 2
            self.speed = 7
            self.image.fill((255, 0, 100))
            print("МИНОС: СУД ИДЕТ!")

    def ai_behavior(self):
        """
        Этот метод автоматически вызывается из Enemy.update().
        Гравитация там уже применяется, так что здесь только логика!
        """
        self.check_phase()
        
        # В base_enemy игрок называется self.target
        dist_to_player = self.target.rect.centerx - self.rect.centerx
        
        # 1. Логика движения и рывка
        if self.is_dashing:
            self.rect.x += (15 if dist_to_player > 0 else -15)
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
            if abs(dist_to_player) > 120:
                dir_x = 1 if dist_to_player > 0 else -1
                self.rect.x += dir_x * self.speed

        # 2. Логика атак
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        else:
            attack_choice = random.random()
            if attack_choice < 0.02:
                self.is_dashing = True
                self.dash_timer = 20
                self.attack_cooldown = 60
            elif attack_choice < 0.04:
                self.shoot_homing()
                self.attack_cooldown = 90

    def shoot_homing(self):
        # Создаем снаряд (используем self.target как цель)
        proj = HomingProjectile(self.rect.centerx, self.rect.centery, self.target)
        if self.game:
            self.game.all_sprites.add(proj)

class HomingProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 255), (15, 15), 15)
        self.rect = self.image.get_rect(center=(x, y))
        self.target = target
        self.speed = 5

    def update(self):
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed
        
        if self.rect.colliderect(self.target.rect):
            self.target.take_damage(15)
            self.kill()
