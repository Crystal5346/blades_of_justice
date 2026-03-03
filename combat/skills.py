import pygame

class GabrielSkills:
    @staticmethod
    def throw_axe(player, combat_system, mouse_pos):
        if player.mp >= 20:
            player.mp -= 20
            # Передаем координаты ЦЕНТРА игрока как один аргумент
            combat_system.spawn_projectile(player.rect.center, mouse_pos, damage=25, is_spear=False)

    @staticmethod
    def throw_spear(player, combat_system, mouse_pos):
        if player.mp >= 40:
            player.mp -= 40
            combat_system.spawn_projectile(player.rect.center, mouse_pos, damage=60, is_spear=True)
