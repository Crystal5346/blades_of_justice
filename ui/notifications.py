"""
ui/notifications.py — система всплывающих уведомлений.

Использование в любом файле проекта:
    from ui.notifications import notify
    notify("Lust 1-1", color=(180, 100, 255))
    notify("Level Up!  Уровень 2", color=(255, 215, 0))

В Game.draw() добавить после hud.draw():
    from ui.notifications import draw_notifications
    draw_notifications(self.screen)
"""
import pygame
from config import WIDTH, HEIGHT

_queue: list = []
DURATION_MS  = 4000
FADE_MS      =  350
_BASE_X      = 30
_BASE_Y      = int(HEIGHT * 0.65)
_LINE_H      = 54


def notify(text: str, color=(230, 230, 230)):
    _queue.append({"text": text, "color": color, "born": pygame.time.get_ticks()})
    if len(_queue) > 4:
        _queue.pop(0)


def draw_notifications(screen):
    now  = pygame.time.get_ticks()
    font = pygame.font.Font(None, 21)
    dead = []

    for i, n in enumerate(_queue):
        age = now - n["born"]
        if age > DURATION_MS:
            dead.append(n)
            continue

        if age < FADE_MS:
            alpha = int(255 * age / FADE_MS)
        elif age > DURATION_MS - FADE_MS:
            alpha = int(255 * (DURATION_MS - age) / FADE_MS)
        else:
            alpha = 255

        slide = int(8 * max(0.0, 1.0 - age / FADE_MS))
        y     = _BASE_Y + i * _LINE_H + slide

        text_surf = font.render(n["text"], True, n["color"])
        tw, th    = text_surf.get_width(), text_surf.get_height()

        # Фоновая плашка
        bg = pygame.Surface((tw + 24, th + 10), pygame.SRCALPHA)
        bg.fill((8, 8, 12, int(alpha * 0.72)))
        screen.blit(bg, (_BASE_X - 4, y - 5))

        # Левая цветная полоска
        bar = pygame.Surface((3, th + 10), pygame.SRCALPHA)
        bar.fill((*n["color"][:3], alpha))
        screen.blit(bar, (_BASE_X - 4, y - 5))

        # Тень
        shadow = font.render(n["text"], True, (0, 0, 0))
        shadow.set_alpha(alpha // 3)
        screen.blit(shadow, (_BASE_X + 14, y + 2))

        # Текст
        text_surf.set_alpha(alpha)
        screen.blit(text_surf, (_BASE_X + 12, y))

    for n in dead:
        if n in _queue:
            _queue.remove(n)
