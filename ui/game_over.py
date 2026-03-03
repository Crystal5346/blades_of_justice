import pygame
from config import WIDTH, HEIGHT

class GameOverScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont("Georgia", 100, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 30)

    def draw(self):
        # Полупрозрачная красная заливка на весь экран
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((50, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Текст смерти
        text_dead = self.font_big.render("YOU ARE DEAD", True, (255, 0, 0))
        rect_dead = text_dead.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(text_dead, rect_dead)

        # Инструкция
        text_hint = self.font_small.render("PRESS 'R' TO RESTART OR 'M' FOR MENU", True, (200, 200, 200))
        rect_hint = text_hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(text_hint, rect_hint)
