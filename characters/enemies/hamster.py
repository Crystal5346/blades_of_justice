import pygame
import random
import math
from config import WIDTH, HEIGHT
from .base_enemy import Enemy   # Одна точка — ищем в той же папке (enemies)

class SmallHamster(Enemy):
    """
    Малый Хомяк: 'Ложный' босс. 
    Умирает с одного удара, запуская истинную битву.
    """
    def __init__(self, x, y, player, game=None):
        # hp=1, mp=0, speed=2, level=1, target=player
        super().__init__(x, y, 1, 0, 2, 1, player)
        self.game = game
        self.name = "GIGA HAMSTER" # Грозное имя для маленького существа
        
        # Визуал маленького хомяка
        self.image = pygame.Surface((30, 30))
        self.image.fill((150, 75, 0)) # Коричневый
        self.rect = self.image.get_rect(center=(x, y))
        
        self.is_boss = True # Чтобы HUD показал полоску HP

    def ai_behavior(self):
        """Простое движение в сторону игрока"""
        dist_x = self.target.rect.centerx - self.rect.centerx
        if abs(dist_x) > 5:
            self.rect.x += self.speed if dist_x > 0 else -self.speed

    def die(self):
        """Метод вызывается при HP <= 0. Спавнит настоящего босса."""
        print("СИСТЕМА: Истинный облик врага раскрыт!")
        
        # Создаем ГигаХомяка на том же месте
        # (Импорт внутри, чтобы избежать циклической зависимости)
        from characters.enemies.hamster import GigaHamster
        
        big_boss = GigaHamster(WIDTH // 2, HEIGHT - 300, self.target, self.game)
        
        if self.game:
            self.game.enemies.add(big_boss)
            self.game.all_sprites.add(big_boss)
        
        super().die() # Удаляем маленького хомяка


class GigaHamster(Enemy):
    def __init__(self, x, y, player, game=None):
        super().__init__(x, y, 5000, 1000, 0, 20, player) # Скорость 0, он на троне
        self.game = game
        self.name = "ВЕЛИКИЙ СВЯТОЙ ХОМЯК"
        self.image = pygame.Surface((250, 250), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 215, 0), (0, 0, 250, 250), border_radius=20)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.is_boss = True
        self.attack_timer = 0
        self.current_action = "IDLE"
        
        # Параметры Луча
        self.beam_active = False
        self.beam_rect = pygame.Rect(0, 0, 0, 0)
        self.beam_duration = 0
        self.beam_direction = 1 # 1 вправо, -1 влево

    def ai_behavior(self):
        if self.beam_active:
            self.update_beam()
            return # Пока жарит лучом, другие атаки не выбирает

        self.attack_timer += 1
        if self.attack_timer > 150: # Раз в 2.5 секунды
            self.attack_timer = 0
            self.start_attack()

    def start_attack(self):
        choice = random.choice(["BEAM", "STOMP", "TIRED"])
        if choice == "BEAM":
            self.current_action = "BEAM"
            self.beam_active = True
            self.beam_duration = 240 # 4 секунды при 60 FPS
            # Стреляет в сторону игрока
            self.beam_direction = 1 if self.target.rect.centerx > self.rect.centerx else -1
            print("СИСТЕМА: СВЯТОЙ ЛУЧ АКТИВИРОВАН")
        else:
            self.current_action = "IDLE"

    def update_beam(self):
        self.beam_duration -= 1
        
        # Луч растет из центра хомяка
        beam_width = 1500 # Длина луча
        beam_height = 80   # Толщина луча
        
        if self.beam_direction == 1:
            self.beam_rect = pygame.Rect(self.rect.centerx, self.rect.centery - beam_height//2, beam_width, beam_height)
        else:
            self.beam_rect = pygame.Rect(self.rect.centerx - beam_width, self.rect.centery - beam_height//2, beam_width, beam_height)

        # Нанесение урона игроку
        if self.beam_rect.colliderect(self.target.rect):
            self.target.take_damage(2) # Частый мелкий урон (потоковый)

        # Разрушение платформ под лучом
        hits = [w for w in self.game.walls if self.beam_rect.colliderect(w.rect)]
        for wall in hits:
            if hasattr(wall, 'vanish'): # Если это исчезающая платформа
                wall.vanish()

        if self.beam_duration <= 0:
            self.beam_active = False
            self.current_action = "IDLE"

    def draw(self, screen):
        # Рисуем самого босса через камеру
        screen.blit(self.image, self.game.camera.apply(self))
        
        if self.beam_active:
            # Отрисовка луча (превращаем beam_rect в координаты экрана через камеру)
            draw_rect = self.game.camera.apply_rect(self.beam_rect)
            
            # Основное тело луча (бело-золотое)
            pygame.draw.rect(screen, (255, 255, 200), draw_rect)
            # Жирная обводка (призрачный прямоугольник)
            pygame.draw.rect(screen, (255, 215, 0), draw_rect, 5)
            
            # Эффект свечения (опционально)
            glow = draw_rect.inflate(20, 20)
            s = pygame.Surface((glow.width, glow.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 215, 0, 100), (0, 0, glow.width, glow.height), border_radius=10)
            screen.blit(s, glow.topleft)

    def perform_roll(self):
        """Атака перекатом: быстрое движение к игроку"""
        dist_x = self.target.rect.centerx - self.rect.centerx
        move_dir = 1 if dist_x > 0 else -1
        self.rect.x += move_dir * (self.speed * 2.5)
        
        # Урон при столкновении
        if self.rect.colliderect(self.target.rect):
            self.target.take_damage(20)

    def perform_jump(self):
        """Прыжок: босс пытается раздавить игрока"""
        if self.action_duration == 99: # В начале атаки даем импульс вверх
            self.vel_y = -20
        
        # Движение в воздухе к игроку
        dist_x = self.target.rect.centerx - self.rect.centerx
        if abs(dist_x) > 10:
            self.rect.x += (1 if dist_x > 0 else -1) * self.speed

    def die(self):
        print("ПОБЕДА: Святой Хомяк повержен. Габриэль исполнил свой долг.")
        super().die()
        
