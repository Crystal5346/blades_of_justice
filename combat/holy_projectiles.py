"""
combat/holy_projectiles.py
Визуальные снаряды Габриэля: топор и копьё.
Наследуют Projectile, переопределяют отрисовку.
Исчезают через 5 секунд если не попали в цель.
"""
import pygame
import math
from combat.damage_system import Projectile

# Цвета
C_GOLD       = (255, 215,  0)
C_GOLD_LIGHT = (255, 240, 120)
C_BLADE      = (210, 230, 255)
C_BLADE_EDGE = (255, 255, 255)
C_GLOW_AXE   = (255, 200,  50, 80)   # RGBA
C_GLOW_SPEAR = (180, 220, 255, 60)


def _alpha_surf(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


# ---------------------------------------------------------------------------
# Топор
# ---------------------------------------------------------------------------

class HolyAxe(Projectile):
    """
    Летящий топор Габриэля.
    Вращается вокруг своей оси. Исчезает через LIFETIME мс или при попадании.
    """
    LIFETIME = 5000   # мс

    def __init__(self, x, y, target_pos, damage, targets, game):
        super().__init__(
            x, y, target_pos,
            damage  = damage,
            speed   = 12,
            color   = C_GOLD,
            targets = targets,
            pierce  = False,
            size    = (32, 32),
            game    = game,
        )
        self._born   = pygame.time.get_ticks()
        self._angle  = 0.0   # угол вращения в градусах
        self._rebuild_image(0)

    def _rebuild_image(self, angle_deg: float):
        """Перерисовывает топор под нужным углом."""
        base = _alpha_surf(32, 32)
        cx, cy = 16, 16

        # Рукоять
        pygame.draw.line(base, C_GOLD,       (cx, cy - 6), (cx, cy + 10), 3)
        pygame.draw.line(base, C_GOLD_LIGHT, (cx, cy - 6), (cx, cy + 10), 1)

        # Лезвие (D-образная форма)
        blade_rect = pygame.Rect(cx - 10, cy - 12, 14, 18)
        pygame.draw.arc(base, C_BLADE,      blade_rect, math.pi * 0.1, math.pi * 0.9, 5)
        pygame.draw.arc(base, C_BLADE_EDGE, blade_rect, math.pi * 0.1, math.pi * 0.9, 1)

        # Обух (маленький шип справа)
        pygame.draw.polygon(base, C_GOLD, [
            (cx + 2, cy - 4),
            (cx + 9, cy - 1),
            (cx + 2, cy + 2),
        ])

        # Свечение
        glow = _alpha_surf(32, 32)
        pygame.draw.circle(glow, C_GLOW_AXE, (cx, cy), 14)
        base.blit(glow, (0, 0))

        self.image = pygame.transform.rotate(base, angle_deg)
        old_center = self.rect.center if hasattr(self, "rect") else (0, 0)
        self.rect  = self.image.get_rect(center=old_center)

    def update(self):
        # Таймер жизни
        if pygame.time.get_ticks() - self._born > self.LIFETIME:
            self.kill()
            return

        # Движение (из родителя)
        self.pos_x += self.velocity_x
        self.pos_y += self.velocity_y
        self.rect.centerx = int(self.pos_x)
        self.rect.centery  = int(self.pos_y)

        # Вращение
        self._angle = (self._angle + 12) % 360
        self._rebuild_image(self._angle)

        # Коллизии
        hits = pygame.sprite.spritecollide(self, self.targets, False)
        for target in hits:
            if hasattr(target, "take_damage"):
                target.take_damage(self.damage)
                self.kill()
                return

        # За пределами уровня
        if self.game:
            lw = getattr(self.game, "level_width", 99999)
            if not (-500 < self.pos_x < lw + 500):
                self.kill()


# ---------------------------------------------------------------------------
# Копьё
# ---------------------------------------------------------------------------

class HolySpear(Projectile):
    """
    Пронизывающее копьё Габриэля.
    Не вращается — летит наконечником вперёд, пронизывает до 4 врагов.
    Исчезает через LIFETIME мс.
    """
    LIFETIME = 5000

    def __init__(self, x, y, target_pos, damage, targets, game):
        super().__init__(
            x, y, target_pos,
            damage  = damage,
            speed   = 15,
            color   = C_BLADE,
            targets = targets,
            pierce  = True,
            size    = (48, 10),
            game    = game,
        )
        self._born = pygame.time.get_ticks()
        # Вычисляем угол полёта для корректного отображения
        dx = target_pos[0] - x
        dy = target_pos[1] - y
        self._fly_angle = math.degrees(-math.atan2(dy, dx))
        self._rebuild_image()

    def _rebuild_image(self):
        base = _alpha_surf(60, 12)

        # Древко
        pygame.draw.line(base, C_GOLD,        (4, 6),  (44, 6), 3)
        pygame.draw.line(base, C_GOLD_LIGHT,  (4, 5),  (44, 5), 1)

        # Наконечник
        pygame.draw.polygon(base, C_BLADE, [
            (44, 6), (58, 6), (44, 2), (44, 10)
        ])
        pygame.draw.polygon(base, C_BLADE_EDGE, [
            (44, 6), (58, 6)
        ])

        # Перья на хвосте
        pygame.draw.polygon(base, C_GOLD, [
            (4, 6), (0, 2), (8, 6)
        ])
        pygame.draw.polygon(base, C_GOLD, [
            (4, 6), (0, 10), (8, 6)
        ])

        # Свечение
        glow = _alpha_surf(60, 12)
        pygame.draw.rect(glow, C_GLOW_SPEAR, (0, 0, 60, 12), border_radius=4)
        base.blit(glow, (0, 0))

        self.image = pygame.transform.rotate(base, self._fly_angle)
        old_center = self.rect.center if hasattr(self, "rect") else (0, 0)
        self.rect  = self.image.get_rect(center=old_center)

    def update(self):
        if pygame.time.get_ticks() - self._born > self.LIFETIME:
            self.kill()
            return

        self.pos_x += self.velocity_x
        self.pos_y += self.velocity_y
        self.rect.centerx = int(self.pos_x)
        self.rect.centery  = int(self.pos_y)

        hits = pygame.sprite.spritecollide(self, self.targets, False)
        for target in hits:
            if not hasattr(target, "take_damage"):
                continue
            if target in self.hit_targets:
                continue
            falloff      = self.pierce_falloff ** len(self.hit_targets)
            actual_dmg   = int(self.damage * falloff)
            target.take_damage(actual_dmg)
            self.hit_targets.append(target)
            if len(self.hit_targets) >= self.max_pierce:
                self.kill()
                return

        if self.game:
            lw = getattr(self.game, "level_width", 99999)
            if not (-500 < self.pos_x < lw + 500):
                self.kill()
