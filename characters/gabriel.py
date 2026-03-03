import pygame
import math
from .character import Character

class Gabriel(Character):
    def __init__(self, x, y):
        # Начальные характеристики (Уровень 1)
        # HP и MP по 10000 как в твоем коде
        super().__init__(x, y, hp=10000, mp=10000, speed=25) 
        self.level = 1
        self.image.fill((255, 215, 0)) # Золотой Габриэль
        
        # Регенерация ресурсов (согласно ТЗ)
        self.mana_regen_speed = 0.05 
        
        # Оружие
        self.unlocked_weapons = ["Blades"]

        # --- СИСТЕМА ПРОГРЕССИИ ---
        self.exp = 0
        self.exp_to_next_level = 100

        # --- НАСТРОЙКИ РЫВКА (DASH) ---
        self.is_dashing = False
        self.dash_speed = 22
        self.dash_duration = 150 
        self.dash_cooldown = 1000 
        self.last_dash_time = 0
        self.dash_start_time = 0
        self.is_invulnerable = False 

    def get_hud_data(self):
        """Данные для интерфейса (HP, MP, LVL, EXP)"""
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mp": self.mp,
            "max_mp": self.max_mp,
            "lvl": self.level,
            "exp": getattr(self, 'exp', 0),
            "exp_to_next": self.exp_to_next_level,
            "weapons": self.unlocked_weapons
        }

    def handle_input(self, event):
        if self.game.camera and hasattr(self.game.camera, 'camera'):
            world_mouse_x = mx - self.game.camera.camera.x
        else:
            world_mouse_x = mx # Фоллбек, если камеры нет
        """ОБРАБОТКА НАЖАТИЙ (Сюда переехал код из main.py)"""
        # Ближний бой (Левая кнопка мыши)
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Сначала всегда получаем координаты мыши
            mx, my = pygame.mouse.get_pos() 
            
            # Теперь делаем расчеты с камерой, только если она есть
            if self.game.camera and hasattr(self.game.camera, 'camera'):
                world_mouse_x = mx - self.game.camera.camera.x
                world_mouse_y = my - self.game.camera.camera.y
            else:
                # Фоллбек: если камеры нет, используем экранные координаты
                world_mouse_x, world_mouse_y = mx, my
        
        # Способности (E и Q)
        if event.type == pygame.KEYDOWN:
            mx, my = pygame.mouse.get_pos()
            # Учет смещения камеры для точного прицеливания
            world_mouse_x = mx - self.game.camera.camera.x
            
            if event.key == pygame.K_e:
                self.cast_axe(self.game.combat_system, (world_mouse_x, my))
            if event.key == pygame.K_q:
                self.cast_spear(self.game.combat_system, (world_mouse_x, my))

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5) 
        
        self.max_hp += 20
        self.hp = self.max_hp
        self.max_mp += 10
        self.mp = self.max_mp
        
        self.refresh_abilities() # Обновляем список оружия
        print(f"Level Up! Current Level: {self.level}")

    def dash(self):
        now = pygame.time.get_ticks()
        if now - self.last_dash_time > self.dash_cooldown and not self.is_dashing:
            self.is_dashing = True
            self.is_invulnerable = True
            self.dash_start_time = now
            self.last_dash_time = now

    def take_damage(self, amount):
        if not self.is_invulnerable:
            super().take_damage(amount)

    def get_nearest_alive_enemy(self):
        alive_enemies = [e for e in self.game.enemies if getattr(e, 'is_alive', True)]
        if not alive_enemies: return None
        return min(alive_enemies, key=lambda e: math.hypot(e.rect.x - self.rect.x, e.rect.y - self.rect.y))

    def update(self, keys):
        if not self.is_alive: return

        now = pygame.time.get_ticks()

        # 1. ЛОГИКА РЫВКА
        if self.is_dashing:
            if now - self.dash_start_time < self.dash_duration:
                dx = self.dash_speed if self.direction == "right" else -self.dash_speed
                self.check_world_collisions(self.game.walls, dx, 0)
                return 
            else:
                self.is_dashing = False
                self.is_invulnerable = False

        # 2. АКТИВАЦИЯ РЫВКА (Зажатая клавиша)
        if keys[pygame.K_LSHIFT]:
            self.dash()

        # 3. ОБЫЧНОЕ ДВИЖЕНИЕ
        dx = 0
        if keys[pygame.K_a]: 
            dx = -self.speed
            self.direction = "left"
        if keys[pygame.K_d]: 
            dx = self.speed
            self.direction = "right"

        # 4. ПОЛЕТ И ГРАВИТАЦИЯ
        self.vel_y += self.gravity
        flying = False
        
        if keys[pygame.K_SPACE]:
            if self.mp > 0:
                self.mp -= 0.6 # Расход маны
                if self.vel_y > -6: self.vel_y -= 1.8 
                flying = True
                self.on_ground = False
            else:
                if self.vel_y < 0: self.vel_y = 0 
                if self.vel_y > 3: self.vel_y = 3 # Планирование
        
        if keys[pygame.K_w] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        if not keys[pygame.K_SPACE] and self.vel_y > 15:
            self.vel_y = 15

        # 5. РЕГЕНЕРАЦИЯ МАНЫ
        if not flying and self.mp < self.max_mp:
            self.mp += self.mana_regen_speed
            if self.mp > self.max_mp: self.mp = self.max_mp 

        # 6. КОЛЛИЗИИ
        self.check_world_collisions(self.game.walls, dx, self.vel_y)

    def cast_axe(self, combat_system, mouse_pos):
        if "Holy Axes" in self.unlocked_weapons:
            from combat.skills import GabrielSkills
            GabrielSkills.throw_axe(self, combat_system, mouse_pos)
        else:
            print("Level too low for Holy Axes!")

    def cast_spear(self, combat_system, mouse_pos):
        if "Holy Spear" in self.unlocked_weapons:
            from combat.skills import GabrielSkills
            GabrielSkills.throw_spear(self, combat_system, mouse_pos)
        else:
            print("Level too low for Holy Spear!")
            
    def refresh_abilities(self):
        """Синхронизирует список доступного оружия с уровнем"""
        if "Blades" not in self.unlocked_weapons:
            self.unlocked_weapons.append("Blades")
        if self.level >= 2 and "Holy Axes" not in self.unlocked_weapons:
            self.unlocked_weapons.append("Holy Axes")
        if self.level >= 4 and "Holy Spear" not in self.unlocked_weapons:
            self.unlocked_weapons.append("Holy Spear")
