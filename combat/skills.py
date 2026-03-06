import pygame
import math
from combat.damage_system import Projectile


class TimedProjectile(Projectile):
    """Снаряд с таймером жизни 5 секунд."""
    LIFETIME = 5000  # мс

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._born = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self._born > self.LIFETIME:
            self.kill()
            return
        super().update()


class GabrielSkills:
    @staticmethod
    def throw_axe(player, combat_system, mouse_pos):
        if player.mp >= 20:
            player.mp -= 20
            x, y = player.rect.center
            proj = TimedProjectile(
                x, y, mouse_pos,
                damage  = 25,
                speed   = 12,
                color   = (255, 215, 0),
                targets = combat_system.game.enemies,
                pierce  = False,
                size    = (25, 25),
                game    = combat_system.game,
            )
            combat_system.game.all_sprites.add(proj)
            combat_system.projectiles.add(proj)

    @staticmethod
    def throw_spear(player, combat_system, mouse_pos):
        if player.mp >= 40:
            player.mp -= 40
            x, y = player.rect.center
            proj = TimedProjectile(
                x, y, mouse_pos,
                damage  = 60,
                speed   = 15,
                color   = (255, 255, 255),
                targets = combat_system.game.enemies,
                pierce  = True,
                size    = (25, 25),
                game    = combat_system.game,
            )
            combat_system.game.all_sprites.add(proj)
            combat_system.projectiles.add(proj)
