import pygame
from world.environment import Wall
from config import WIDTH, HEIGHT

class DisappearingPlatform(pygame.sprite.Sprite):
    """Платформа, которая исчезает после касания или попадания"""
    def __init__(self, x, y, w, h, color, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        # Добавим золотистую обводку для стиля
        pygame.draw.rect(self.image, (255, 215, 0), self.image.get_rect(), 2)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.active = True
        self.timer = 0
        self.respawn_delay = 180 # 3 секунды при 60 FPS

    def update(self):
        if not self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = True
                self.game.walls.add(self)
                self.game.all_sprites.add(self) # ДОБАВИТЬ ЭТО, чтобы она снова появилась на экране
        else:
            # Исчезает при касании игрока
            if self.rect.colliderect(self.game.player.rect):
                # Проверка: игрок должен быть сверху платформы, чтобы она «сработала»
                if self.game.player.vel_y > 0 and self.game.player.rect.bottom <= self.rect.bottom + 10:
                    self.vanish()
            
            # Или при попадании снарядов
            for projectile in self.game.combat_system.projectiles:
                if self.rect.colliderect(projectile.rect):
                    self.vanish()

    def vanish(self):
        if self.active:
            self.active = False
            self.timer = self.respawn_delay
            self.game.walls.remove(self)
            self.game.all_sprites.remove(self)

    def draw(self, screen):
        if self.active:
            # Рисуем с учетом камеры
            screen.blit(self.image, self.game.camera.apply(self))

class FinalGenerator:
    """Генератор финальных локаций: Коридор Суда и Золотая Арена"""
    def __init__(self, game):
        self.game = game

    def generate(self, name):
        if name == "FinalCorridor":
            self._build_corridor()
        elif name == "FinalArena":
            self._build_arena()

    def _build_corridor(self):
        """Создание длинного величественного коридора (Walk of Judgment)"""
        length = 6000 # Сделаем его еще длиннее для атмосферы
        self.game.level_width = length
        self.game.init_camera(length, HEIGHT)
        
        # 1. Пол (Белый мрамор с золотом)
        floor = Wall(0, HEIGHT - 100, length, 100, (245, 245, 240))
        self.game.walls.add(floor)
        self.game.all_sprites.add(floor)

        # 2. Потолок
        ceiling = Wall(0, 0, length, 100, (200, 200, 190))
        self.game.walls.add(ceiling)
        self.game.all_sprites.add(ceiling)

        # 3. Декорации: Колонны на заднем фоне
        # Мы добавляем их в all_sprites, но НЕ в walls, чтобы сквозь них можно было ходить
        for x in range(400, length, 800):
            # Тень колонны
            pillar_shadow = Wall(x-20, 100, 100, HEIGHT-200, (220, 220, 210))
            # Сама колонна (чуть светлее)
            pillar = Wall(x, 100, 60, HEIGHT-200, (255, 255, 250))
            
            self.game.all_sprites.add(pillar_shadow)
            self.game.all_sprites.add(pillar)

        # 4. Окна / Источники света (Визуальный эффект)
        for x in range(800, length, 1600):
            window = Wall(x, 150, 300, 400, (255, 253, 220)) # Свет из окон
            self.game.all_sprites.add(window)

        # 5. Финальные врата в конце
        gate = Wall(length - 150, HEIGHT - 400, 100, 300, (255, 215, 0))
        self.game.all_sprites.add(gate)
        # Сохраняем ссылку на врата для StageManager, если нужно
        self.game.exit_gate = gate

    def _build_arena(self):
        """Золотой Колизей для битвы с ГигаХомяком"""
        self.game.level_width = WIDTH
        self.game.init_camera(WIDTH, HEIGHT)
        
        # 1. Пол
        floor = Wall(0, HEIGHT - 100, WIDTH, 100, (255, 215, 0))
        self.game.walls.add(floor)
        self.game.all_sprites.add(floor) # Это было на месте

        # 2. Боковые ограничители (НЕВИДИМЫЕ СТЕНЫ)
        left_wall = Wall(-20, 0, 20, HEIGHT, (0, 0, 0))
        right_wall = Wall(WIDTH, 0, 20, HEIGHT, (0, 0, 0))
        self.game.walls.add(left_wall, right_wall)
        # СОВЕТ: Если хочешь их видеть, добавь их в all_sprites. 
        # Если хочешь, чтобы они были просто преградой — оставь так.
        self.game.all_sprites.add(left_wall) 
        self.game.all_sprites.add(right_wall)

        # 3. Исчезающие платформы
        platform_positions = [
            (WIDTH // 6, HEIGHT - 300),
            (WIDTH // 6 * 4, HEIGHT - 300),
            (WIDTH // 3, HEIGHT - 500),
            (WIDTH // 3 * 2, HEIGHT - 500)
        ]
        
        for pos in platform_positions:
            p = DisappearingPlatform(pos[0], pos[1], 200, 25, (255, 255, 255), self.game)
            self.game.walls.add(p)
            self.game.all_sprites.add(p) # Проверь, чтобы эта строка была тут!
