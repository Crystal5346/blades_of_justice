import pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, mp, speed, level=1):
        super().__init__()
        # --- ФИЗИКА (DEAD CELLS STYLE) ---
        self.vel_y = 0
        self.on_ground = False
        self.gravity = 0.8
        self.jump_power = -16
        
        # --- ХАРАКТЕРИСТИКИ ---
        self.level = level
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp
        self.speed = speed
        self.is_alive = True
        self.direction = "right"
        self.is_active = False # Флаг активации для ИИ

        # --- ГРАФИКА ---
        self.image = pygame.Surface((50, 60))
        self.rect = self.image.get_rect(topleft=(x, y))

	# --- СИСТЕМА УРОНА ---
    def take_damage(self, amount):
        if not self.is_alive: return
        
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            # Вместо того чтобы просто ставить False, вызываем метод смерти
            if hasattr(self, 'die'):
                self.die()
            else:
                # На случай, если у кого-то нет метода die
                self.is_alive = False

    def check_world_collisions(self, walls, dx, dy):
        # 1. Горизонтальное движение и коллизии
        self.rect.x += dx
        hits = pygame.sprite.spritecollide(self, walls, False)
        for wall in hits:
            if dx > 0: # Движемся вправо
                self.rect.right = wall.rect.left
            elif dx < 0: # Движемся влево
                self.rect.left = wall.rect.right

        # 2. Вертикальное движение и коллизии
        self.rect.y += dy
        self.on_ground = False # По умолчанию считаем, что мы в воздухе
        
        hits = pygame.sprite.spritecollide(self, walls, False)
        for wall in hits:
            if dy > 0: # Падаем вниз (Приземление)
                # Проверяем, действительно ли мы над платформой, а не задели её сбоку
                if self.rect.bottom > wall.rect.top:
                    self.rect.bottom = wall.rect.top
                    self.vel_y = 0
                    self.on_ground = True
            elif dy < 0: # Летим вверх (Удар головой)
                if self.rect.top < wall.rect.bottom:
                    self.rect.top = wall.rect.bottom
                    self.vel_y = 0
