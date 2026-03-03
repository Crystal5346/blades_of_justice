import pygame
import random
from characters.enemies.base_enemy import Enemy

class SisyphusBoss(Enemy):
    """
    Финальный босс локации Greed: Царь Сизиф.
    Теперь только ближний бой (Melee Only).
    """
    def __init__(self, x, y, target, game):
        # Оставляем высокие HP
        super().__init__(x, y, hp=1500, mp=0, speed=5, level=5, target=target)
        self.game = game
        self.max_hp = 1500
        self.name = "Царь Сизиф" # Нужно для HUD
        self.phase = 1
        self.is_boss = True
        
        # Визуал
        self.image = pygame.Surface((80, 100))
        self.image.fill((180, 150, 50)) 
        self.rect = self.image.get_rect(midbottom=(x, y))
        
        # Контроль атак
        self.attack_timer = 0
        self.combo_count = 0
        self.pause_timer = 0
        
        # Настройки баланса (без шанса ударной волны)
        self.combo_max = 3
        self.pause_duration = 100 
        self.attack_delay = 25    
        self.attack_range = 90    # Немного увеличим радиус меча
        self.shockwave_chance = 0.3  # ВОТ ЭТА СТРОКА БЫЛА ПРОПУЩЕНА

    def ai_behavior(self):
        if self.hp <= self.max_hp / 2 and self.phase == 1:
            self.trigger_phase_two()
            
        if self.pause_timer > 0:
            self.pause_timer -= 1
            self.apply_gravity()
            return 

        dist_x = self.target.rect.centerx - self.rect.centerx
        self.direction = "right" if dist_x > 0 else "left"
        
        # Сизиф идет на сближение для удара
        if abs(dist_x) > self.attack_range - 10: 
            self.rect.x += (1 if dist_x > 0 else -1) * self.speed
        else:
            # Вплотную — бьем
            if self.attack_timer <= 0:
                self.execute_attack()
            else:
                self.attack_timer -= 1
                
        self.apply_gravity()

    def apply_gravity(self):
        self.vel_y += 0.8
        self.rect.y += self.vel_y
        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                if self.vel_y > 0:
                    self.rect.bottom = wall.rect.top
                    self.vel_y = 0

    def trigger_phase_two(self):
        self.phase = 2
        self.speed = 9               # Еще быстрее во 2-й фазе
        self.combo_max = 6           # Очень длинные комбо
        self.pause_duration = 40     # Короткое окно для игрока
        self.attack_delay = 10       # Удары почти мгновенные
        self.shockwave_chance = 0.7  # Шанс волн увеличивается
        
        self.image.fill((200, 60, 40)) 
        print("Царь Сизиф: Фаза II активирована!")

    def execute_attack(self):
        """Логика комбо-атаки Сизифа согласно ТЗ"""
        self.combo_count += 1
        
        # 1. Прямой урон ближнего боя (основная атака) [cite: 765]
        dmg = 25 if self.phase == 1 else 35
        self.game.combat_system.process_melee_attack(self, [self.target], damage=dmg)
        
        # 2. Ударные волны по земле (согласно ТЗ [cite: 767, 771])
        # Шанс появления волны зависит от фазы
        if random.random() < self.shockwave_chance:
            self.spawn_shockwave()
            
        # 3. Управление темпом комбо
        if self.combo_count >= self.combo_max:
            self.combo_count = 0
            self.pause_timer = self.pause_duration 
        else:
            self.attack_timer = self.attack_delay

    def spawn_shockwave(self):
        """Создает эффект разлома земли, а не летящий снаряд"""
        dir_mult = 1 if self.direction == "right" else -1
        
        # Точка появления — прямо под ногами босса
        spawn_x = self.rect.centerx + (dir_mult * 50)
        spawn_y = self.rect.bottom - 20 # Почти на уровне пола
        
        # ВАЖНО: target_pos должен быть на той же высоте, что и spawn_y, 
        # чтобы волна шла горизонтально по земле, а не летела в игрока
        ground_target = (spawn_x + dir_mult * 1000, spawn_y)
        
        self.game.combat_system.spawn_projectile(
            pos=(spawn_x, spawn_y),
            target_pos=ground_target, # Летит строго горизонтально
            damage=20,
            targets=pygame.sprite.Group(self.target),
            color=(255, 215, 0), # Ярко-золотой
            size=(80, 10)         # Длинная и плоская (как волна)
        )

    def die(self):
        super().die()
        print("Сизиф обезглавлен. Душа запечатана в пирамиде.")
        if hasattr(self.game, 'stage_manager'):
            self.game.stage_manager.trigger_boss_defeat_sequence()
