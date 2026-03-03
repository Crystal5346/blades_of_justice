import pygame

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(100, 100, 100)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(150, 150, 150)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        # Декоративная полоска сверху
        pygame.draw.rect(self.image, (200, 200, 200), [0, 0, width, 5])
        self.rect = self.image.get_rect(topleft=(x, y))
