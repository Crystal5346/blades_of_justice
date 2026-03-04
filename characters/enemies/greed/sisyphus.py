import pygame
import random
from characters.enemies.base_enemy import Enemy


class SisyphusBoss(Enemy):
    """
    Царь Сизиф — босс ближнего боя без дальних атак.
    Комбо: обычный удар / прыжок с волной при приземлении / ударная волна с отдачей.
    Фаза I (100–50% HP): серии по 3 удара, редкие волны.
    Фаза II (50–0% HP): серии по 6, короткие паузы, волны чаще, быстрее.
    Хитбокс: 50×80 — человеческий рост.
    """

    def __init__(self, x, y, target, game):
        super().__init__(x, y, hp=1500, mp=0, speed=5, level=5, target=target)
        self.game = game
        self.max_hp = 1500
        self.name = "Царь Сизиф"
        self.phase = 1
        self.is_boss = True

        # --- Визуал ---
        self.image = pygame.Surface((50, 80))
        self.image.fill((180, 150, 50))
        pygame.draw.rect(self.image, (255, 215, 0), (0, 36, 50, 8))
        self.rect = self.image.get_rect(midbottom=(x, y))

        # --- Комбо ---
        self.attack_timer = 0
        self.combo_count = 0
        self.pause_timer = 0
        self.is_jumping = False
        self.jump_vel_x = 0
        self.jump_landing_done = False

        # --- Баланс Фаза I ---
        self.combo_max = 3
        self.pause_duration = 100
        self.attack_delay = 25
        self.attack_range = 80
        self.shockwave_chance = 0.25
        self.jump_chance = 0.20

    # ------------------------------------------------------------------ #
    #  ФАЗЫ                                                                #
    # ------------------------------------------------------------------ #

    def trigger_phase_two(self):
        self.phase = 2
        self.speed = 9
        self.combo_max = 6
        self.pause_duration = 40
        self.attack_delay = 10
        self.shockwave_chance = 0.45
        self.jump_chance = 0.30
        self.image.fill((200, 60, 40))
        pygame.draw.rect(self.image, (255, 215, 0), (0, 36, 50, 8))
        print("Царь Сизиф: Фаза II активирована!")

    # ------------------------------------------------------------------ #
    #  ИИ                                                                  #
    # ------------------------------------------------------------------ #

    def ai_behavior(self):
        if self.hp <= self.max_hp / 2 and self.phase == 1:
            self.trigger_phase_two()

        if self.is_jumping:
            self._update_jump()
            self._apply_gravity()
            return

        if self.pause_timer > 0:
            self.pause_timer -= 1
            self._apply_gravity()
            return

        dist_x = self.target.rect.centerx - self.rect.centerx
        self.direction = "right" if dist_x > 0 else "left"

        if abs(dist_x) > self.attack_range - 10:
            self.rect.x += (1 if dist_x > 0 else -1) * self.speed
        else:
            if self.attack_timer <= 0:
                self._choose_attack()
            else:
                self.attack_timer -= 1

        self._apply_gravity()

    def _choose_attack(self):
        roll = random.random()
        if roll < self.jump_chance and self.on_ground:
            self._start_jump()
        elif roll < self.jump_chance + self.shockwave_chance:
            self._spawn_shockwave()
            self.combo_count += 1
            self._advance_combo()
        else:
            self._execute_melee()

    # ------------------------------------------------------------------ #
    #  АТАКИ                                                               #
    # ------------------------------------------------------------------ #

    def _execute_melee(self):
        self.combo_count += 1
        dmg = 25 if self.phase == 1 else 35
        self.game.combat_system.process_melee_attack(self, [self.target], damage=dmg)
        self._advance_combo()

    def _advance_combo(self):
        if self.combo_count >= self.combo_max:
            self.combo_count = 0
            self.pause_timer = self.pause_duration
        else:
            self.attack_timer = self.attack_delay

    def _start_jump(self):
        self.is_jumping = True
        self.jump_landing_done = False
        self.vel_y = -18
        dist_x = self.target.rect.centerx - self.rect.centerx
        self.jump_vel_x = (1 if dist_x > 0 else -1) * (self.speed * 1.5)

    def _update_jump(self):
        self.rect.x += int(self.jump_vel_x)
        if self.on_ground and not self.jump_landing_done:
            self.jump_landing_done = True
            self.is_jumping = False
            # Волна в обе стороны при приземлении
            self._spawn_shockwave(both_directions=True)
            if self.rect.colliderect(self.target.rect):
                dmg = 30 if self.phase == 1 else 45
                self.target.take_damage(dmg)
            self.combo_count += 1
            self._advance_combo()

    def _spawn_shockwave(self, both_directions=False):
        directions = [1, -1] if both_directions else [1 if self.direction == "right" else -1]
        for dir_mult in directions:
            spawn_x = self.rect.centerx + dir_mult * 40
            spawn_y = self.rect.bottom - 15
            ground_target = (spawn_x + dir_mult * 1200, spawn_y)
            self.game.combat_system.spawn_projectile(
                pos=(spawn_x, spawn_y),
                target_pos=ground_target,
                damage=20 if self.phase == 1 else 30,
                targets=pygame.sprite.Group(self.target),
                color=(255, 215, 0),
                size=(80, 10),
            )
        self._apply_knockback()

    def _apply_knockback(self):
        dist_x = self.target.rect.centerx - self.rect.centerx
        knockback_dir = 1 if dist_x > 0 else -1
        knockback = 120 if self.phase == 1 else 180
        self.target.rect.x += knockback_dir * knockback
        self.target.vel_y = -8

    # ------------------------------------------------------------------ #
    #  ФИЗИКА                                                              #
    # ------------------------------------------------------------------ #

    def _apply_gravity(self):
        self.vel_y += 0.8
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                if self.vel_y > 0:
                    self.rect.bottom = wall.rect.top
                    self.vel_y = 0
                    self.on_ground = True

    # ------------------------------------------------------------------ #
    #  СМЕРТЬ                                                              #
    # ------------------------------------------------------------------ #

    def die(self):
        super().die()
        print("Сизиф обезглавлен. Душа запечатана в пирамиде.")
        if hasattr(self.game, "stage_manager"):
            self.game.stage_manager.trigger_boss_defeat_sequence()
