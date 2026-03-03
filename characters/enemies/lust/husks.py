import pygame
import random
import math
from characters.enemies.base_enemy import Enemy

class LustEnemy(Enemy):
    """Общий класс для физики и базовой логики всех врагов Lust"""
    def __init__(self, x, y, hp, speed, level, game):
        super().__init__(x, y, hp=hp, mp=0, speed=speed, level=level, target=game.player)
        self.game = game
        self.gravity = 0.8

    def apply_physics(self, dx=0):
        self.vel_y += self.gravity
        self.check_world_collisions(self.game.walls, dx, self.vel_y)

class Husk1(LustEnemy):
    def __init__(self, x, y, game):
        super().__init__(x, y, 60, 3, 1, game)
        self.image = pygame.Surface((40, 50))
        self.image.fill((180, 150, 200)) 
        self.rect = self.image.get_rect(topleft=(x, y))
        self.attack_cooldown = 0

    def ai_behavior(self):
        dist_x = self.target.rect.centerx - self.rect.centerx
        dx = 0
        if abs(dist_x) < 500:
            if abs(dist_x) > 50: dx = (1 if dist_x > 0 else -1) * self.speed
            else:
                if self.attack_cooldown <= 0:
                    self.target.take_damage(5)
                    self.attack_cooldown = 60
        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        self.apply_physics(dx)

class Husk2(LustEnemy):
    def __init__(self, x, y, game):
        super().__init__(x, y, 80, 2, 2, game)
        self.image = pygame.Surface((40, 60))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.shoot_cooldown = 0

    def ai_behavior(self):
        self.shoot_cooldown -= 1
        dist_x = self.target.rect.centerx - self.rect.centerx
        dx = 0
        if abs(dist_x) > 400: dx = (1 if dist_x > 0 else -1) * self.speed
        elif abs(dist_x) < 250: dx = (-1 if dist_x > 0 else 1) * self.speed
        
        if abs(dist_x) < 600 and self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = 120
        self.apply_physics(dx)

    def shoot(self):
        # ЗАМЕНЕНО НА combat_system
        self.game.combat_system.spawn_projectile(
            pos=self.rect.center,
            target_pos=self.target.rect.center,
            damage=10,
            targets=pygame.sprite.Group(self.target)
        )

class Husk3(Husk2):
    def __init__(self, x, y, game):
        super().__init__(x, y, game)
        self.hp = 150
        self.image.fill((120, 0, 180))

    def shoot(self):
        tx, ty = self.target.rect.center
        for offset_y in [-60, -30, 0, 30, 60]:
            self.game.combat_system.spawn_projectile(
                pos=self.rect.center,
                target_pos=(tx, ty + offset_y),
                damage=12,
                targets=pygame.sprite.Group(self.target)
            )

class StreetCleaner(LustEnemy):
    def __init__(self, x, y, game):
        super().__init__(x, y, 200, 4, 5, game)
        self.image = pygame.Surface((45, 65))
        self.image.fill((240, 240, 240))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.flame_timer = 0
        self.is_flaming = False

    def ai_behavior(self):
        dist_x = self.target.rect.centerx - self.rect.centerx
        dx = 0
        if abs(dist_x) < 100: dx = (-1 if dist_x > 0 else 1) * 8
        elif not self.is_flaming: dx = (1 if dist_x > 0 else -1) * self.speed
            
        if abs(dist_x) < 200 and not self.is_flaming:
            self.is_flaming = True
            self.flame_timer = 180
            
        if self.is_flaming:
            self.flame_timer -= 1
            if random.random() < 0.2: self.target.take_damage(2)
            if self.flame_timer <= 0: self.is_flaming = False
        self.apply_physics(dx)

class LustDrone(Enemy):
    def __init__(self, x, y, game):
        super().__init__(x, y, hp=50, mp=0, speed=5, level=2, target=game.player)
        self.game = game
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 200, 255))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_deadly_fly = False
        self.shoot_timer = 60

    def take_damage(self, amount):
        super().take_damage(amount)
        if self.hp <= 0 and not self.is_deadly_fly:
            self.hp = 1 
            self.is_deadly_fly = True
            self.image.fill((255, 0, 0))

    def ai_behavior(self):
        dist_x = self.target.rect.centerx - self.rect.centerx
        dist_y = self.target.rect.centery - self.rect.centery
        if self.is_deadly_fly:
            norm = math.hypot(dist_x, dist_y)
            if norm > 0:
                self.rect.x += (dist_x / norm) * 10
                self.rect.y += (dist_y / norm) * 10
            if self.rect.colliderect(self.target.rect):
                self.target.take_damage(20)
                self.kill()
        else:
            target_y = self.target.rect.y - 100
            self.rect.y += (target_y - self.rect.y) * 0.05
            self.rect.x += (1 if dist_x > 0 else -1) * 2
            self.shoot_timer -= 1
            if self.shoot_timer <= 0 and abs(dist_x) < 500:
                self.shoot_triple()
                self.shoot_timer = 120

    def shoot_triple(self):
        for i in range(3):
            self.game.combat_system.spawn_projectile(
                pos=(self.rect.centerx, self.rect.centery + (i-1)*20),
                target_pos=self.target.rect.center,
                damage=5,
                targets=pygame.sprite.Group(self.target)
            )

class HellGuardian(Enemy):
    def __init__(self, x, y, game):
        super().__init__(x, y, hp=1000, mp=0, speed=0, level=10, target=game.player)
        self.game = game
        self.image = pygame.Surface((150, 150))
        self.image.fill((200, 0, 0))
        pygame.draw.rect(self.image, (255, 255, 0), (40, 40, 70, 70), 5) 
        self.rect = self.image.get_rect(topleft=(x, y))
        self.attack_timer = 0
        self.phase = "BALLS"
        self.balls_count = 0
        self.is_boss = True # Чтобы HUD рисовал полоску HP

    def ai_behavior(self):
        self.attack_timer += 1
        is_enraged = self.hp < 500
        if self.phase == "BALLS":
            if self.attack_timer % 30 == 0:
                self.shoot_single_ball()
                self.balls_count += 1
            if self.balls_count >= 7:
                self.balls_count = 0
                self.phase = "BEAM"
                self.attack_timer = 0
        elif self.phase == "BEAM":
            if self.attack_timer == 60: self.fire_beam()
            limit = 120 if not is_enraged else 60
            if self.attack_timer > limit:
                self.phase = "BALLS"
                self.attack_timer = 0

    def shoot_single_ball(self):
        self.game.combat_system.spawn_projectile(
            pos=self.rect.center,
            target_pos=self.target.rect.center,
            damage=15,
            targets=pygame.sprite.Group(self.target)
        )

    def fire_beam(self):
        player_group = pygame.sprite.Group(self.target)
        for i in range(10):
            self.game.combat_system.spawn_projectile(
                pos=self.rect.center,
                target_pos=self.target.rect.center,
                damage=5,
                targets=player_group
            )
