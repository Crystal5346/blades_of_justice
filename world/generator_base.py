import pygame
import random

class BaseGenerator:
    def __init__(self, game):
        self.game = game

    def clear_world(self):
        """Общая очистка перед созданием уровня"""
        self.game.enemies.empty()
        self.game.walls.empty()
        self.game.all_sprites.empty()
        # Возвращаем игрока
        self.game.all_sprites.add(self.game.player)
        self.game.player.rect.topleft = (100, 100)
