import pygame
import random
import math
from .base_enemy import Enemy
from config import WIDTH, HEIGHT


class SmallHamster(Enemy):
    """
    Ложный босс. Убивается одним ударом.
    При смерти — спавнит GigaHamster на своём месте.
    НЕ запускает загрузочный экран — переход происходит прямо здесь.
    """

    def __init__(self, x, y, player, game=None):
        super().__init__(x, y, 1, 0, 1, 1, player)
        self.game = game
        self.name = "GIGA HAMSTER"

        self.image = pygame.Surface((20, 18))
        self.image.fill((150, 75, 0))
        pygame.draw.circle(self.image, (255, 0, 0), (5, 6), 2)
        pygame.draw.circle(self.image, (255, 0, 0), (15, 6), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.is_boss = True

    def ai_behavior(self):
        dist_x = self.target.rect.centerx - self.rect.centerx
        if abs(dist_x) > 5:
            self.rect.x += self.speed if dist_x > 0 else -self.speed

    def die(self):
        print("СИСТЕМА: Истинный облик врага раскрыт!")
        if self.game:
            # Спавним большого хомяка прямо на месте маленького
            big_boss = GigaHamster(self.rect.centerx, self.rect.centery - 150, self.target, self.game)
            self.game.enemies.add(big_boss)
            self.game.all_sprites.add(big_boss)
        # Сбрасываем флаги загрузочного экрана — переход больше не нужен
        if self.game:
            self.game.boss_loading_started = False
            self.game.mini_hamster_dead = True
        super().die()


class GigaHamster(Enemy):
    """
    Финальный босс: Великий Святой Хомяк (~6 метров, 120×100 px).
    Атаки по ТЗ: только Луч и Перекат.
    Луч — длинный прямоугольник В СТОРОНУ игрока (фиксируется позиция при начале атаки).
    Платформы возрождаются через respawn_delay (логика в DisappearingPlatform).
    """

    def __init__(self, x, y, player, game=None):
        super().__init__(x, y, 5000, 1000, 4, 20, player)
        self.game = game
        self.name = "ВЕЛИКИЙ СВЯТОЙ ХОМЯК"

        # --- Визуал ---
        self.image = pygame.Surface((120, 100), pygame.SRCALPHA)
        self._draw_hamster_image()
        self.rect = self.image.get_rect(center=(x, y))

        self.is_boss = True
        self.vel_y = 0
        self.attack_timer = 0
        self.current_action = "IDLE"
        self.action_duration = 0

        # --- Луч ---
        self.beam_active = False
        self.beam_rect = pygame.Rect(0, 0, 0, 0)
        self.beam_duration = 0
        # Позиция игрока ЗАФИКСИРОВАННАЯ в момент начала луча
        self.beam_target_x = 0
        self.beam_target_y = 0
        self.beam_direction = 1
        self.beam_damage_timer = 0

        # --- Перекат ---
        self.roll_direction = 1

        # --- Пауза между атаками ---
        self.idle_timer = 0
        self.idle_duration = 90

    def _draw_hamster_image(self):
        surf = self.image
        pygame.draw.rect(surf, (255, 215, 0), (0, 20, 120, 80), border_radius=15)
        pygame.draw.ellipse(surf, (255, 225, 80), (20, 0, 80, 60))
        pygame.draw.circle(surf, (200, 0, 0), (42, 22), 8)
        pygame.draw.circle(surf, (200, 0, 0), (78, 22), 8)
        pygame.draw.circle(surf, (255, 255, 255), (45, 20), 3)
        pygame.draw.circle(surf, (255, 255, 255), (81, 20), 3)
        pygame.draw.ellipse(surf, (180, 100, 80), (52, 34, 16, 10))
        pygame.draw.ellipse(surf, (255, 180, 60), (5, 30, 30, 25))
        pygame.draw.ellipse(surf, (255, 180, 60), (85, 30, 30, 25))

    # ------------------------------------------------------------------ #
    #  ФИЗИКА                                                              #
    # ------------------------------------------------------------------ #

    def _apply_gravity(self):
        self.vel_y += 1.0
        self.rect.y += int(self.vel_y)
        hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        for wall in hits:
            if self.vel_y > 0:
                self.rect.bottom = wall.rect.top
                self.vel_y = 0

    # ------------------------------------------------------------------ #
    #  ИИ                                                                  #
    # ------------------------------------------------------------------ #

    def ai_behavior(self):
        self._apply_gravity()

        if self.beam_active:
            self._update_beam()
            return

        self.attack_timer += 1

        if self.current_action == "IDLE":
            self._idle_movement()
            self.idle_timer += 1
            if self.idle_timer >= self.idle_duration:
                self.idle_timer = 0
                self._start_attack()

        elif self.current_action == "ROLL":
            self._perform_roll()

        if self.action_duration > 0:
            self.action_duration -= 1
            if self.action_duration <= 0:
                self.current_action = "IDLE"
                self.idle_timer = 0

    def _idle_movement(self):
        dist_x = self.target.rect.centerx - self.rect.centerx
        if abs(dist_x) > 150:
            self.rect.x += self.speed if dist_x > 0 else -self.speed
            self.direction = "right" if dist_x > 0 else "left"

    def _start_attack(self):
        self.current_action = random.choice(["BEAM", "ROLL"])

        if self.current_action == "BEAM":
            self.beam_active = True
            self.beam_duration = 200
            self.action_duration = self.beam_duration
            self.beam_damage_timer = 0

            # Фиксируем направление к игроку в момент начала атаки
            self.beam_direction = 1 if self.target.rect.centerx > self.rect.centerx else -1
            # Фиксируем Y-позицию игрока для высоты луча
            self.beam_target_y = self.target.rect.centery
            print("СИСТЕМА: СВЯТОЙ ЛУЧ АКТИВИРОВАН")

        elif self.current_action == "ROLL":
            self.roll_direction = 1 if self.target.rect.centerx > self.rect.centerx else -1
            self.action_duration = 45

    # ------------------------------------------------------------------ #
    #  ЛУЧ                                                                 #
    # ------------------------------------------------------------------ #

    def _update_beam(self):
        """
        Луч — очень длинный широкий прямоугольник в сторону игрока.
        Высота зафиксирована по Y-позиции игрока в момент начала атаки.
        Покрывает всю арену от хомяка до стены.
        """
        self.beam_duration -= 1

        beam_length = WIDTH + 300   # Перекрывает всю арену
        beam_height = 100           # Высокий луч — трудно перепрыгнуть

        # Луч начинается от центра хомяка и идёт в зафиксированном направлении
        beam_y_top = self.beam_target_y - beam_height // 2

        if self.beam_direction == 1:
            self.beam_rect = pygame.Rect(
                self.rect.centerx,
                beam_y_top,
                beam_length,
                beam_height,
            )
        else:
            self.beam_rect = pygame.Rect(
                self.rect.centerx - beam_length,
                beam_y_top,
                beam_length,
                beam_height,
            )

        # Урон раз в 10 кадров
        self.beam_damage_timer += 1
        if self.beam_damage_timer >= 10:
            self.beam_damage_timer = 0
            if self.beam_rect.colliderect(self.target.rect):
                self.target.take_damage(5)

        # Разрушение исчезающих платформ (они сами возрождаются)
        for wall in list(self.game.walls):
            if self.beam_rect.colliderect(wall.rect) and hasattr(wall, "vanish"):
                wall.vanish()

        if self.beam_duration <= 0:
            self.beam_active = False
            self.current_action = "IDLE"
            self.action_duration = 0

    # ------------------------------------------------------------------ #
    #  ПЕРЕКАТ                                                             #
    # ------------------------------------------------------------------ #

    def _perform_roll(self):
        self.rect.x += self.roll_direction * (self.speed * 3)

        # Отскок от стен арены
        if self.rect.left <= 0:
            self.rect.left = 0
            self.roll_direction = 1
        elif self.rect.right >= WIDTH:
            self.rect.right = WIDTH
            self.roll_direction = -1

        if self.rect.colliderect(self.target.rect):
            self.target.take_damage(25)
            # Отдача — отбрасываем игрока
            knockback_dir = 1 if self.roll_direction > 0 else -1
            self.target.rect.x += knockback_dir * 150
            self.target.vel_y = -10

    # ------------------------------------------------------------------ #
    #  ОТРИСОВКА ЛУЧА                                                      #
    # ------------------------------------------------------------------ #

    def draw(self, screen):
        if not self.game or not self.game.camera:
            return

        rel_pos = self.game.camera.apply(self)
        screen.blit(self.image, rel_pos)

        if self.beam_active:
            cam_x, cam_y = self.game.camera.camera.topleft
            draw_rect = self.beam_rect.move(cam_x, cam_y)

            # Внешнее золотое свечение
            outer = draw_rect.inflate(0, 24)
            pygame.draw.rect(screen, (255, 215, 0), outer, 8)
            # Белое тело луча
            pygame.draw.rect(screen, (255, 255, 255), draw_rect)
            # Жёлтая сердцевина
            inner = draw_rect.inflate(0, -30)
            if inner.height > 0:
                pygame.draw.rect(screen, (255, 240, 80), inner)

    # ------------------------------------------------------------------ #
    #  СМЕРТЬ                                                              #
    # ------------------------------------------------------------------ #

    def die(self):
        print("ПОБЕДА: Святой Хомяк повержен. Габриэль исполнил свой долг.")
        if self.game and hasattr(self.game, 'stage_manager'):
            self.game.stage_manager.trigger_boss_defeat_sequence()
        super().die()
