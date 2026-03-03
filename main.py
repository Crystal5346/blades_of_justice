import pygame
import sys
from config import *

# Импорты
from characters.gabriel import Gabriel
from combat.damage_system import CombatSystem
from world.stage_manager import StageManager
from core.camera import Camera
from core.database import Database
from ui.hud import HUD
from ui.menus import GameMenus
from ui.loading_screen import LoadingScreen
from core.save_manager import SaveManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("ULTRAKILL: GABRIEL'S JUDGMENT")
        self.clock = pygame.time.Clock()

        # --- СИСТЕМЫ ---
        self.db = Database()
        self.menus = GameMenus(self.screen)
        self.save_manager = SaveManager(self.db)
        self.loading = LoadingScreen(self.screen, self.menus)
        self.stage_manager = StageManager(self)
        self.combat_system = CombatSystem(self)
        
        # --- СОСТОЯНИЕ ---
        self.state = 'MENU'
        self.current_slot = None
        self.running = True

        # --- ГРУППЫ ---
        self.player = None
        self.hud = None
        self.camera = None
        self.enemies = pygame.sprite.Group()
        self.mini_hamster_dead = False
        self.boss_loading_started = False
        self.loading_timer = 0
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()

    def init_camera(self, width, height):
        """Фабрика камеры: вызывается из генераторов уровней"""
        self.camera = Camera(width, height)
        return self.camera

    def init_world(self, stage_name="FinalCorridor"):
        self.state = 'LOADING'
        
        # 1. Если игрока НЕТ в памяти, пробуем достать его из базы или создать
        if self.player is None:
            print(f"DEBUG: Игрок потерян! Пытаемся восстановить...")
            # Пытаемся загрузить данные из последнего слота
            saved_stats = self.db.get_player_stats(self.current_slot) if self.current_slot else None
            
            self.player = Gabriel(200, HEIGHT - 300)
            self.player.game = self
            
            # Если в базе что-то было — возвращаем честно заработанное
            if saved_stats:
                self.player.level = saved_stats.get('level', 1)
                self.player.exp = saved_stats.get('exp', 0)
                self.player.hp = saved_stats.get('hp', self.player.max_hp)
                self.player.refresh_abilities()
                print(f"DEBUG: Статы восстановлены из БД. Уровень: {self.player.level}")
        
        # 2. Теперь, когда игрок ТОЧНО есть, чистим мир
        self.all_sprites.empty()
        self.walls.empty()
        self.enemies.empty()

        # 3. Возвращаем нашего (уже существующего или только что воскрешенного) игрока
        self.all_sprites.add(self.player)
        self.player.rect.topleft = (200, HEIGHT - 300)
        self.player.vel_y = 0

        # 4. Загружаем уровень
        self.stage_manager.load_stage(stage_name)
        
        # 5. Обновляем HUD
        self.hud = HUD(self.screen, self.player)
        
        print(f"DEBUG: Загрузка {stage_name} завершена. Итоговый уровень: {self.player.level}")
        self.state = 'PLAYING'

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == 'PLAYING':
                    self.state = 'PAUSE'
                    self.menus.state = 'PAUSE'
                elif self.state == 'PAUSE':
                    self.state = 'PLAYING'
                    self.menus.state = 'NONE'

            if self.state in ['MENU', 'PAUSE', 'CUTSCENE', 'GAMEOVER']:
                action = self.menus.handle_input(event)
                if action: 
                    self.process_menu_action(action)
                continue

            if self.state == 'PLAYING' and self.player:
                self.player.handle_input(event)

    def process_menu_action(self, action):
        if action == "CONTINUE":
            self.menus.state = 'SAVES_LOAD'
            
        elif action == "NEW_GAME":
            self.menus.state = 'SAVES_NEW'
            
        elif action.startswith("SLOT_"):
            self.current_slot = action
            self.state = 'LOADING'
            if self.menus.state == 'SAVES_NEW':
                self.db.clear_slot(action)
                self.init_world("Polygon")
            elif self.menus.state == 'SAVES_LOAD':
                saved_stage = self.db.get_latest_save_stage(action)
                target = saved_stage if saved_stage else "Polygon"
                self.init_world(target)

        elif action == "RESUME":
            self.state = 'PLAYING'
            self.menus.state = 'NONE'

        elif action == "NEXT_AFTER_BOSS":
            self.state = 'LOADING'
            self.save_game_data() 
            # Не меняем стадию в БД здесь, чтобы Полигон знал, откуда мы пришли!
            self.init_world("Polygon")

        elif action == "RESTART":
            self.state = 'LOADING'
            self.init_world(self.stage_manager.current_stage)

        elif action == "TO_MENU":
            self.state = 'MENU'
            self.menus.state = 'MAIN'
            self.player = None
            self.all_sprites.empty()

        elif action == "EXIT_GAME":
            self.running = False
            
    def save_game_data(self):
        if not self.current_slot or not self.player:
            return 
            
        stats_to_save = {
            'level': self.player.level,
            'hp': self.player.hp,
            'max_hp': self.player.max_hp,
            'mp': getattr(self.player, 'mp', 100),
            'max_mp': getattr(self.player, 'max_mp', 100),
            'stage': self.stage_manager.current_stage
        }
        self.db.save_game(self.current_slot, stats_to_save)

    def update(self):
        # 1. Если идет загрузка босса — считаем таймер
        if self.boss_loading_started and self.state == 'LOADING':
            now = pygame.time.get_ticks()
            elapsed = (now - self.loading_timer) / 1000 
            
            if elapsed >= 10: 
                self.boss_loading_started = False
                self.init_world("FinalArena") # Тут заспавнится Большой Хомяк
            return # Пока грузимся, остальной апдейт не нужен

        # 2. Состояние меню/паузы/катсцены
        if self.state in ['MENU', 'PAUSE', 'GAMEOVER', 'CUTSCENE']:
            if self.state == 'CUTSCENE':
                keys = pygame.key.get_pressed() 
                for sprite in self.all_sprites:
                    if sprite == self.player:
                        sprite.update(keys) 
                    else:
                        sprite.update()
                if self.camera: 
                    self.camera.update(self.player)
            return
            
        # 3. ОБЫЧНОЕ СОСТОЯНИЕ ИГРЫ (PLAYING)
        keys = pygame.key.get_pressed()

        # Проверка условий перехода на Арену
        if self.stage_manager.current_stage == "FinalCorridor":
            # Проверка смерти Мини-Хомяка
            if not self.mini_hamster_dead:
                minsters = [e for e in self.enemies if getattr(e, 'name', '') == "Minster"]
                if not minsters: 
                    self.mini_hamster_dead = True
                    print("СИСТЕМА: Страж пал. Врата Арены разблокированы.")

            # Проверка приближения к двери (если страж убит)
            if self.mini_hamster_dead and not self.boss_loading_started:
                if self.player.rect.x > 5750:
                    self.boss_loading_started = True
                    self.loading_timer = pygame.time.get_ticks()
                    self.state = 'LOADING'
                    print("СИСТЕМА: Подготовка Арены...")

        # Стандартное обновление спрайтов
        if self.player:
            self.player.update(keys) 
        
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.update() 
        
        if self.camera:
            self.camera.update(self.player)
            
        self.combat_system.enemy_attack_logic()
        self.stage_manager.update()

        if self.player and self.player.hp <= 0:
            self.state = 'GAMEOVER'

    def draw(self):
        # ЭКРАН ЗАГРУЗКИ БОССА
        if self.state == 'LOADING' and self.boss_loading_started:
            self.screen.fill((0, 0, 0))
            now = pygame.time.get_ticks()
            elapsed = int((now - self.loading_timer) / 1000)
            remaining = max(0, 30 - elapsed)
            
            font = pygame.font.SysFont("Arial", 48)
            text = font.render(f"ПРИБЛИЖЕНИЕ ГРЫЗУНА... {remaining}с", True, (255, 215, 0))
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(text, rect)
            
            hint = pygame.font.SysFont("Arial", 24).render("Совет: Его прыжок смертелен, используйте рывок (L-Shift)", True, (200, 200, 200))
            self.screen.blit(hint, (WIDTH // 2 - 250, HEIGHT // 2 + 100))
            pygame.display.flip()
            return

        # ОБЫЧНАЯ ОТРИСОВКА
        self.screen.fill(self.stage_manager.get_bg_color())

        if self.state in ['PLAYING', 'PAUSE', 'GAMEOVER', 'CUTSCENE']:
            for sprite in self.all_sprites:
                if self.camera:
                    self.screen.blit(sprite.image, self.camera.apply(sprite))
                else:
                    self.screen.blit(sprite.image, sprite.rect)

            if self.hud:
                for enemy in self.enemies:
                    if getattr(enemy, 'max_hp', 0) >= 500 and enemy.is_alive:
                        self.hud.draw_boss_hp(enemy)
                self.hud.draw()

        self.draw_ui_overlays()
        pygame.display.flip()

    def draw_ui_overlays(self):
        if self.state == 'MENU':
            if self.menus.state == "MAIN": 
                self.menus.draw_main_menu()
            elif self.menus.state == "SETTINGS": 
                self.menus.draw_settings()
            elif self.menus.state in ["SAVES_LOAD", "SAVES_NEW"]: 
                slots_info = self.db.get_all_slots_info()
                self.menus.draw_save_slots(slots_info, self.menus.state)
        
        elif self.state == 'CUTSCENE':
            if self.menus.state == "POST_BOSS_CHOICE":
                self.menus.draw_post_boss_menu()
            else:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))
                
        elif self.state == 'PAUSE':
            self.menus.draw_pause_menu()
            
        elif self.state == 'GAMEOVER':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((100, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            text = self.menus.font_big.render("JUDGMENT", True, (255, 0, 0))
            self.screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    def quit_game(self):
        if self.player and self.current_slot:
            self.save_game_data()
        pygame.quit()
        sys.exit()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
