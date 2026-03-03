import pygame
from config import WIDTH, HEIGHT

class Camera:
    def __init__(self, width, height):
        # Храним область видимости
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        """Возвращает смещенный прямоугольник для отрисовки объекта"""
        # Если это спрайт, берем его rect. Если уже Rect - используем его напрямую.
        target_rect = entity.rect if hasattr(entity, 'rect') else entity
        return target_rect.move(self.camera.topleft)

    def update(self, target):
        """Следит за целью (обычно игроком) и центрирует экран"""
        # Рассчитываем положение, чтобы игрок был в центре экрана
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # Ограничиваем камеру границами уровня, чтобы не видеть пустоту
        # Ограничение слева (0) и справа (ширина уровня - ширина экрана)
        x = min(0, x)
        x = max(-(self.width - WIDTH), x)
        
        # Ограничение сверху и снизу
        y = min(0, y)
        y = max(-(self.height - HEIGHT), y)

        self.camera = pygame.Rect(x, y, self.width, self.height)
