import pygame
import random
import math
from config import WIDTH, HEIGHT
from ..base_enemy import Enemy


class MinosBoss(Enemy):
    """
    Царь Минос — быстрый босс с рывками, прыжками и самонаводящимися снарядами.
    Фаза I (100–50% HP): рывки, одиночные снаряды, редкие волны.
    Фаза II (50–0% HP): быстрее, залп из 3 снарядов, частые волны, прыжки.
    Хитбокс: 50×80 — человеческий рост.
    """

    def __init__(self, x, y, player):
        super().__init__(x, y, 1000, 500, 4, 10, player)

        # --- Визуал ---
        self.image = pygame.Surface((50, 80))
        self.image.fill((150, 0, 255))
        pygame.draw.rect(self.image, (255, 215, 0), (10, 0, 30, 12))  # корона
        self.rect = self.image.get_rect(topleft=(x, y))

        self.name = "Царь Минос"
        self.is_boss = True
        self.phase = 1
        self.is_active = True

        # --- Таймеры ---
        self.attack_cooldown = 0
        self.dash_timer = 0
        self.is_dashing = False
        self.shockwave_cooldown = 0

        # --- Прыжок ---
        self.is_jumping = False
        self.jump_vel_x = 0
        self.jump_landing_done = False
        self.jump_cooldown = 0

        # --- Баланс Фаза I ---
        self.dash_speed = 15
        self.dash_duration = 20
        self.homing_chance = 0.015
        self.shockwave_chance = 0.008
        self.jump_chance = 0.008
        self.max_homing_projectiles = 1

    # ------------------------------------------------------------------ #
    #  ФАЗЫ                                                                #
    # ------------------------------------------------------------------ #

    def check_phase(self):
        if self.hp < 500 and self.phase == 1:
            self.phase = 2
            self.speed = 8
            self.dash_speed = 22
            self.dash_duration = 25
            self.homing_chance = 0.035
            self.shockwave_chance = 0.020
            self.jump_chance = 0.018
            self.max_homing_projectiles = 3
            self.image.fill((255, 0, 100))
            pygame.draw.rect(self.image, (255, 215, 0), (10, 0, 30, 12))
            print("МИНОС: СУД ИДЕТ!")

    # ------------------------------------------------------------------ #
    #  ИИ                                                                  #
    # ------------------------------------------------------------------ #

    def ai_behavior(self):
        self.check_phase()

        # Прыжок
        if self.is_jumping:
            self._update_jump()
            self._apply_gravity()
            return

        # Рывок
        if self.is_dashing:
            self.rect.x += self.dash_speed if (self.target.rect.centerx > self.rect.centerx) else -self.dash_speed
            self.dash_timer -= 1
            if self.rect.colliderect(self.target.rect):
                self.target.take_damage(20 if self.phase == 1 else 30)
            if self.dash_timer <= 0:
                self.is_dashing = False
            self._apply_gravity()
            return

        dist_x = self.target.rect.centerx - self.rect.centerx
        if abs(dist_x) > 80:
            dir_x = 1 if dist_x > 0 else -1
            self.rect.x += dir_x * self.speed
            self.direction = "right" if dir_x > 0 else "left"

        # Ближний удар при контакте
        if self.rect.colliderect(self.target.rect) and self.attack_cooldown <= 0:
            dmg = 15 if self.phase == 1 else 25
            self.target.take_damage(dmg)
            self.attack_cooldown = 45 if self.phase == 1 else 25

        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        if self.shockwave_cooldown > 0: self.shockwave_cooldown -= 1
        if self.jump_cooldown > 0: self.jump_cooldown -= 1

        roll = random.random()

        if roll < 0.012 and not self.is_dashing and abs(dist_x) > 100:
            self.is_dashing = True
            self.dash_timer = self.dash_duration

        elif roll < self.jump_chance and self.on_ground and self.jump_cooldown == 0:
            self._start_jump()

        elif roll < self.homing_chance and self.attack_cooldown == 0:
            for _ in range(self.max_homing_projectiles):
                self._shoot_homing()
            self.attack_cooldown = 90 if self.phase == 1 else 55

        elif roll < self.shockwave_chance and self.shockwave_cooldown == 0:
            self._spawn_shockwave()
            self.shockwave_cooldown = 120 if self.phase == 1 else 70

        self._apply_gravity()

    # ------------------------------------------------------------------ #
    #  ПРЫЖОК                                                              #
    # ------------------------------------------------------------------ #

    def _start_jump(self):
        self.is_jumping = True
        self.jump_landing_done = False
        self.vel_y = -20
        dist_x = self.target.rect.centerx - self.rect.centerx
        self.jump_vel_x = (1 if dist_x > 0 else -1) * (self.speed * 2)
        self.jump_cooldown = 180

    def _update_jump(self):
        self.rect.x += int(self.jump_vel_x)
        if self.on_ground and not self.jump_landing_done:
            self.jump_landing_done = True
            self.is_jumping = False
            # Волна в обе стороны при приземлении
            self._spawn_shockwave(both_directions=True)
            if self.rect.colliderect(self.target.rect):
                self.target.take_damage(25 if self.phase == 1 else 40)

    # ------------------------------------------------------------------ #
    #  АТАКИ                                                               #
    # ------------------------------------------------------------------ #

    def _shoot_homing(self):
        proj = HomingProjectile(
            self.rect.centerx, self.rect.centery,
            self.target,
            speed=5 if self.phase == 1 else 7
        )
        if self.game:
            self.game.all_sprites.add(proj)

    def _spawn_shockwave(self, both_directions=False):
        if not self.game:
            return
        directions = [1, -1] if both_directions else [1 if self.direction == "right" else -1]
        for dir_mult in directions:
            spawn_x = self.rect.centerx + dir_mult * 30
            spawn_y = self.rect.bottom - 15
            ground_target = (spawn_x + dir_mult * 1200, spawn_y)
            self.game.combat_system.spawn_projectile(
                pos=(spawn_x, spawn_y),
                target_pos=ground_target,
                damage=15 if self.phase == 1 else 22,
                targets=pygame.sprite.Group(self.target),
                color=(150, 0, 255),
                size=(60, 8),
            )
        self._apply_knockback()

    def _apply_knockback(self):
        dist_x = self.target.rect.centerx - self.rect.centerx
        knockback_dir = 1 if dist_x > 0 else -1
        self.target.rect.x += knockback_dir * 100
        self.target.vel_y = -7

    # ------------------------------------------------------------------ #
    #  ФИЗИКА                                                              #
    # ------------------------------------------------------------------ #

    def _apply_gravity(self):
        self.vel_y += self.gravity
        self.on_ground = False
        if self.game:
            self.check_world_collisions(self.game.walls, 0, self.vel_y)
            # check_world_collisions двигает rect и обновляет on_ground

    def update(self, keys=None):
        if not self.is_alive:
            self.kill()
            return
        if not self.is_active:
            self.check_activation()
            return
        self.vel_y += self.gravity
        self.ai_behavior()


# ------------------------------------------------------------------ #
#  САМОНАВОДЯЩИЙСЯ СНАРЯД                                              #
# ------------------------------------------------------------------ #

class HomingProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target, speed=5):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (180, 0, 255), (10, 10), 10)
        pygame.draw.circle(self.image, (255, 150, 255), (10, 10), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.target = target
        self.speed = speed
        self.lifetime = 300

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        dx = self.target.rect.centerx - self.rect.centerx
        dy = self.target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.rect.x += int((dx / dist) * self.speed)
            self.rect.y += int((dy / dist) * self.speed)
        if self.rect.colliderect(self.target.rect):
            self.target.take_damage(15)
            self.kill()
