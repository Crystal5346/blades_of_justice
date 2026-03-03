import pygame
import math
from characters.character import Character

class Enemy(Character):
    def __init__(self, x, y, hp, mp, speed, level, target):
        # Инициализируем базовый класс Character
        super().__init__(x, y, hp, mp, speed, level)
        
        self.target = target  # Ссылка на Габриэля
        self.game = None      # Будет назначено при спавне в StageManager
        
        # Состояние ИИ
        self.is_active = False  # Просыпается, когда игрок рядом
        self.activation_range = 800 # Дистанция "пробуждения"
        
        # Боевые параметры
        self.attack_distance = 60 
        self.attack_cooldown = 1000 
        self.last_attack_time = 0
        self.damage = 5 * level
        self.exp_reward = 25 * level

    def check_activation(self):
        """Проверяет, достаточно ли близко игрок, чтобы начать действовать"""
        if self.game and not self.is_active:
            dist = abs(self.target.rect.centerx - self.rect.centerx)
            if dist < self.activation_range:
                self.is_active = True
                # Добавляем себя в группу отрисовки, если проснулись
                self.game.all_sprites.add(self)

    def take_damage(self, amount):
        """Реакция на получение урона"""
        super().take_damage(amount)
        # Если ударили спящего врага — он мгновенно просыпается и агрится
        if not self.is_active:
            self.is_active = True
            if self.game: self.game.all_sprites.add(self)

    def attempt_attack(self):
        """Логика атаки ближнего боя"""
        now = pygame.time.get_ticks()
        if now - self.last_attack_time > self.attack_cooldown:
            # Проверяем реальное столкновение хитбоксов
            if self.rect.colliderect(self.target.rect):
                self.target.take_damage(self.damage)
                self.last_attack_time = now
                return True
        return False

    def die(self):
        """Смерть: даем опыт и удаляемся"""
        if self.is_alive:
            self.target.gain_exp(self.exp_reward)
            self.is_alive = False
            print(f"Враг повержен! +{self.exp_reward} EXP")
            self.kill() # Удаляет спрайт из всех групп Pygame

    def ai_behavior(self):
        """
        Метод-заглушка. Конкретную логику (стрелять или бежать) 
        мы пишем уже в классах Husk или StreetCleaner.
        """
        pass

    def update(self, keys=None):
        """Основной цикл обновления врага"""
        if not self.is_alive:
            self.kill() # На всякий случай подчищаем еще раз
            return

        # Если враг еще не активен — проверяем дистанцию до игрока
        if not self.is_active:
            self.check_activation()
            return

        # Применяем гравитацию
        self.vel_y += self.gravity
        
        # Выполняем индивидуальное поведение (переопределяется в подклассах)
        self.ai_behavior()

        # Применяем коллизии с миром (стены/пол)
        # Здесь используем логику из базового класса Character
        if self.game:
            # dx вычисляется внутри ai_behavior и должен применяться там 
            # через check_world_collisions
            pass
