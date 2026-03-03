import pygame
import math
from config import WIDTH, HEIGHT

class LoadingScreen:
    def __init__(self, screen, menus):
        self.screen = screen
        self.menus = menus
        self.quotes = ["MANKIND IS DEAD.", "BLOOD IS FUEL.", "HELL IS FULL.", "JUDGMENT IS COMING."]

    def draw(self):
        self.screen.fill((10, 10, 15))
        
        # Основной текст
        label = self.menus.font.render("LOADING...", True, self.menus.GOLD)
        rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        # Эффект пульсации
        pulse = int(155 + 100 * math.sin(pygame.time.get_ticks() * 0.008))
        label.set_alpha(pulse)
        self.screen.blit(label, rect)
        
        # Подзаголовок
        quote_index = (pygame.time.get_ticks() // 2000) % len(self.quotes)
        sub_text = self.menus.small_font.render(self.quotes[quote_index], True, (100, 100, 100))
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        self.screen.blit(sub_text, sub_rect)
        
        pygame.display.flip()
