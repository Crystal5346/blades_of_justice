import pygame
import random
from .base_enemy import Enemy
from config import WIDTH, HEIGHT

class SmallHamster(Enemy):
    """
    Класс 'ложного' босса. Маленький хомяк, который провоцирует игрока.
    Смерть этого объекта триггерит появление истинной формы босса.
    """
    def __init__(self, x, y, player, game=None):
        super().__init__(x, y, 1, 0, 2, 1, player)
        self.game = game
        self.name = "GIGA HAMSTER" 
        self.image = pygame.Surface((30, 30))
        self.image.fill((150, 75, 0)) # Коричневый
        self.rect = self.image.get_rect(center=(x, y))
        self.is_boss = True 

    def ai_behavior(self):
        dist_x = self.target.rect.centerx - self.rect.centerx
        if abs(dist_x) > 5:
            self.rect.x += self.speed if dist_x > 0 else -self.speed

    """При смерти спавнит настоящего Громовержца Ада"""
    def die(self):
        print("СИСТЕМА: Истинный облик врага раскрыт!")
        from characters.enemies.hamster import GigaHamster
        # Спавним настоящего босса [cite: 949]
        big_boss = GigaHamster(self.rect.centerx, self.rect.centery - 100, self.target, self.game)
        if self.game:
            self.game.enemies.add(big_boss)
            self.game.all_sprites.add(big_boss)
        super().die()

    """
    Истинный финальный босс: Святой Хомяк.
    Обладает огромным запасом HP, умеет прыгать, перекатываться и жечь лучом.
    """
class GigaHamster(Enemy):
    #настройка характеристик (HP, скорость) и параметров луча.
    def __init__(self, x, y, player, game=None):
        # HP=5000, Скорость=4 
        super().__init__(x, y, 5000, 1000, 4, 20, player)
        self.game = game
        self.name = "ВЕЛИКИЙ СВЯТОЙ ХОМЯК"
        
        # Визуал: Золотой гигант 
        self.image = pygame.Surface((250, 250), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 215, 0), (0, 0, 250, 250), border_radius=20)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.is_boss = True # Флаг для UI
        self.vel_y = 0      # Вертикальная скорость для гравитации
        self.attack_timer = 0
        self.current_action = "IDLE" # Текущее состояние (отдых/атака)
        self.action_duration = 0      # Сколько кадров длится текущая атака
        
        # Параметры Святого Луча 
        self.beam_active = False
        self.beam_rect = pygame.Rect(0, 0, 0, 0)
        self.beam_duration = 0
        self.beam_direction = 1

    def apply_gravity(self):
        """Физика падения и коллизия с платформами"""
        self.vel_y += 1.2 # Гравитация
        self.rect.y += self.vel_y
        
        # Коллизия с полом, чтобы не левитировал
        hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        for wall in hits:
            if self.vel_y > 0:
                self.rect.bottom = wall.rect.top
                self.vel_y = 0

    def ai_behavior(self):
        self.apply_gravity() # Босс всегда подвластен гравитации

        if self.beam_active:
            self.update_beam()
            return # Во время луча босс не двигается
        # Если активен луч — блокируем другие действия
        self.attack_timer += 1
        
        if self.current_action == "IDLE":
            # Движение к игроку
            dist_x = self.target.rect.centerx - self.rect.centerx
            if abs(dist_x) > 100:
                self.rect.x += (self.speed if dist_x > 0 else -self.speed)
            
            # Рандомный выбор атаки [cite: 951]
            if self.attack_timer > 120:
                self.attack_timer = 0
                self.start_attack()
        
        elif self.current_action == "ROLL":
            self.perform_roll() # Логика переката
        elif self.current_action == "JUMP":
            self.perform_jump() # Логика прыжка

        # Уменьшаем время действия атаки
        if self.action_duration > 0:
            self.action_duration -= 1
            if self.action_duration <= 0:
                self.current_action = "IDLE"

    def start_attack(self):
        # Рандом атак: Луч, Перекат или Прыжок
        self.current_action = random.choice(["BEAM", "ROLL", "JUMP"])
        self.action_duration = 120 # Длительность фазы
        
        if self.current_action == "BEAM":
            self.beam_active = True
            self.beam_duration = 240 # Длительность 4 секунды
            self.beam_direction = 1 if self.target.rect.centerx > self.rect.centerx else -1
            print("СИСТЕМА: СВЯТОЙ ЛУЧ АКТИВИРОВАН")

    def update_beam(self):
        """Логика Святого Луча (один большой прямоугольник)"""
        self.beam_duration -= 1
        beam_width = 1800
        beam_height = 120
        
        # Луч выходит из "глаз" или центра, не задевая самого хомяка
        if self.beam_direction == 1:
            self.beam_rect = pygame.Rect(self.rect.right, self.rect.centery - beam_height//2, beam_width, beam_height)
        else:
            self.beam_rect = pygame.Rect(self.rect.left - beam_width, self.rect.centery - beam_height//2, beam_width, beam_height)

        # Урон Габриэлю
        if self.beam_rect.colliderect(self.target.rect):
            self.target.take_damage(2) # Частый мелкий урон

        # Разрушение платформ 
        for wall in self.game.walls:
            if self.beam_rect.colliderect(wall.rect) and hasattr(wall, 'vanish'):
                wall.vanish()

        if self.beam_duration <= 0:
            self.beam_active = False
            self.current_action = "IDLE"

    def perform_roll(self):
        """Атака перекатом """
        move_dir = 1 if self.target.rect.centerx > self.rect.centerx else -1
        self.rect.x += move_dir * (self.speed * 3)
        if self.rect.colliderect(self.target.rect):
            self.target.take_damage(20)

    def perform_jump(self):
        """Прыжок (попытка раздавить)"""
        if self.action_duration == 119:
            self.vel_y = -25
        dist_x = self.target.rect.centerx - self.rect.centerx
        self.rect.x += (1 if dist_x > 0 else -1) * (self.speed * 1.5)

    def draw(self, screen):
        """Визуализация босса и спецэффектов луча"""
        # Рисуем хомяка с учетом камеры
        rel_pos = self.game.camera.apply(self)
        screen.blit(self.image, rel_pos)
        
        if self.beam_active:
            # Отрисовка луча через смещение камеры
            cam_x, cam_y = self.game.camera.camera.topleft
            draw_rect = self.beam_rect.move(cam_x, cam_y)
            
            # Цветовая схема Габриэля: Белый и Золотой 
            # 1. Золотая жирная обводка (призрачный прямоугольник)
            pygame.draw.rect(screen, (255, 215, 0), draw_rect, 8)
            # 2. Основное тело луча (белое свечение)
            inner_rect = draw_rect.inflate(0, -30)
            pygame.draw.rect(screen, (255, 255, 255), inner_rect)

    def die(self):
        print("ПОБЕДА: Святой Хомяк повержен. Габриэль исполнил свой долг.")
        super().die()
