import pygame
import math

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos, damage, speed, color, targets, 
                 pierce=False, size=(25, 25), game=None):
        super().__init__()
        self.game = game
        self.targets = targets
        self.damage = damage
        self.pierce = pierce # Сохраняем для логики
        self.speed = speed
        
        # Визуал
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        if self.pierce:
             # Рисуем копье/топор
             pygame.draw.rect(self.image, color, (0, size[1]//4, size[0], size[1]//2), border_radius=5)
        else:
             # Рисуем валун/пулю
             pygame.draw.circle(self.image, color, (size[0]//2, size[1]//2), size[0]//2)
             if size[0] > 30: # Доп. текстура для больших камней
                 pygame.draw.circle(self.image, (60, 60, 60), (size[0]//3, size[1]//3), 5)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        # Направление рассчитывается один раз при создании
        self.calculate_direction(target_pos)

    def calculate_direction(self, target_pos):
        angle = math.atan2(target_pos[1] - self.pos_y, target_pos[0] - self.pos_x)
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed
        
        if self.pierce:
            deg = math.degrees(-angle)
            self.image = pygame.transform.rotate(self.image, deg)

    def update(self):
        # Движение
        self.pos_x += self.velocity_x
        self.pos_y += self.velocity_y
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        # Коллизии
        hits = pygame.sprite.spritecollide(self, self.targets, False)
        if hits:
            for target in hits:
                if hasattr(target, 'take_damage'):
                    target.take_damage(self.damage)
            # Если не пронзает — уничтожается. Валун Husk7 теперь всегда уничтожается.
            if not self.pierce:
                self.kill()
                
        # В Projectile.update
        if hasattr(self, 'is_warning_phase') and self.is_warning_phase:
            self.image.set_alpha(100) # Прозрачный
        else:
            self.image.set_alpha(255) # Опасный

        # Удаление за границами
        if self.game:
            if not (-1000 < self.pos_x < self.game.stage_manager.level_width + 1000):
                self.kill()

class CombatSystem:
    def __init__(self, game):
        self.game = game
        self.projectiles = pygame.sprite.Group()

    def spawn_projectile(self, pos, target_pos, damage, is_spear=False, targets=None, color=None, size=(25, 25)):
        """Стандартный снаряд для Габриэля и мелких врагов"""
        x, y = pos
        if targets is None: targets = self.game.enemies
        if color is None:
            color = (255, 215, 0) if not is_spear else (255, 255, 255)
        speed = 15 if is_spear else 12
        
        proj = Projectile(x, y, target_pos, damage, speed, color, targets, 
                          pierce=is_spear, size=size, game=self.game)
        self.game.all_sprites.add(proj)
        self.projectiles.add(proj)

    def spawn_heavy_projectile(self, pos, target_pos, damage):
        """Тяжелый валун для Husk7 (Greed)"""
        x, y = pos
        proj = Projectile(
            x, y, target_pos, damage, 
            speed=7, 
            color=(100, 90, 80), 
            targets=pygame.sprite.Group(self.game.player), 
            pierce=False, 
            size=(50, 50),
            game=self.game
        )
        self.game.all_sprites.add(proj)
        self.projectiles.add(proj)

    def apply_area_buff(self, pos, radius, buff_amount):
        for enemy in self.game.enemies:
            dist = math.hypot(enemy.rect.centerx - pos[0], enemy.rect.centery - pos[1])
            if dist <= radius:
                if hasattr(enemy, 'defense'):
                    enemy.defense += buff_amount

    def process_melee_attack(self, attacker, targets, damage=20):
        hit_box = 90
        y_offset = attacker.rect.centery - 45
        rect = pygame.Rect(attacker.rect.right if attacker.direction == "right" else attacker.rect.left - hit_box, 
                           y_offset, hit_box, hit_box)
        for target in targets:
            if rect.colliderect(target.rect):
                target.take_damage(damage)
                target.rect.x += 20 if attacker.direction == "right" else -20

    def enemy_attack_logic(self):
        now = pygame.time.get_ticks()
        for enemy in self.game.enemies:
            if enemy.is_alive and enemy.rect.inflate(40, 40).colliderect(self.game.player.rect):
                if not hasattr(enemy, 'last_attack'): enemy.last_attack = 0
                if now - enemy.last_attack > 1000:
                    self.game.player.take_damage(10)
                    enemy.last_attack = now
