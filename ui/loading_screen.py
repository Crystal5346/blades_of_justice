import pygame
import math
from config import WIDTH, HEIGHT
from ui.localization import t

class LoadingScreen:
    def __init__(self, screen, menus):
        self.screen = screen
        self.menus  = menus

    def draw(self):
        self.screen.fill((10, 10, 15))

        font_load  = pygame.font.Font(None, 48)
        font_quote = pygame.font.Font(None, 22)

        label = font_load.render(t("loading"), True, (255, 215, 0))
        rect  = label.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        pulse = int(155 + 100 * math.sin(pygame.time.get_ticks() * 0.008))
        label.set_alpha(pulse)
        self.screen.blit(label, rect)

        quotes     = t("loading_quotes")
        quote_idx  = (pygame.time.get_ticks() // 2000) % len(quotes)
        sub_text   = font_quote.render(quotes[quote_idx], True, (90, 90, 100))
        self.screen.blit(sub_text, sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))

        pygame.display.flip()
