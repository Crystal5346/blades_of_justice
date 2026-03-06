import pygame
import sys
from config import *

from characters.gabriel import Gabriel
from combat.damage_system import CombatSystem
from world.stage_manager import StageManager
from core.database import Database
from ui.hud import HUD
from ui.menus import GameMenus
from core.camera import Camera
from ui.loading_screen import LoadingScreen
from ui.notifications import notify, draw_notifications
from ui.localization import t
from ui.notifications import notify


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT),
            pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Blades of Justice")
        self.clock = pygame.time.Clock()

        self.db           = Database()
        self.menus        = GameMenus(self.screen)
        self.loading      = LoadingScreen(self.screen, self.menus)
        self.stage_manager = StageManager(self)
        self.combat_system = CombatSystem(self)

        self.state        = 'MENU'
        self.current_slot = None
        self.running      = True

        self.player      = None
        self.hud         = None
        self.camera      = None
        self.enemies     = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.walls       = pygame.sprite.Group()
        self.boss_loading_started = False

    def init_camera(self, width, height):
        self.camera = Camera(width, height)
        return self.camera

    def init_world(self, stage_name="FinalCorridor"):
        self.state = 'LOADING'

        if self.player is None:
            saved_stats = self.db.get_player_stats(self.current_slot) if self.current_slot else None
            self.player = Gabriel(200, HEIGHT - 300)
            self.player.game = self
            if saved_stats:
                self.player.level = saved_stats.get('level', 1)
                self.player.exp   = saved_stats.get('exp', 0)
                self.player.hp    = saved_stats.get('hp', self.player.max_hp)
                self.player.refresh_abilities()

        self.all_sprites.empty()
        self.walls.empty()
        self.enemies.empty()
        self.mini_hamster_dead    = False
        self.boss_loading_started = False

        self.all_sprites.add(self.player)
        self.player.rect.topleft = (200, HEIGHT - 300)
        self.player.vel_y        = 0

        self.stage_manager.load_stage(stage_name)
        self.hud   = HUD(self.screen, self.player)
        self.state = 'PLAYING'

        # Уведомление о загруженном уровне
        notify(f"▶  {stage_name}", color=(255, 215, 0))

    # ------------------------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == 'PLAYING':
                    self.state = 'PAUSE'
                    self.menus.state = 'PAUSE'
                elif self.state == 'PAUSE':
                    # ESC из настроек → пауза; ESC из паузы → игра
                    if self.menus.state == 'SETTINGS':
                        self.menus.state = 'PAUSE'
                    else:
                        self.state = 'PLAYING'
                        self.menus.state = 'NONE'

            if self.state == 'GAMEOVER':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.process_menu_action("RESTART")
                    elif event.key == pygame.K_m:
                        self.process_menu_action("TO_MENU")

            if self.state in ['MENU', 'PAUSE', 'CUTSCENE', 'GAMEOVER']:
                action = self.menus.handle_input(event)
                if action:
                    self.process_menu_action(action)
                continue

            if self.state == 'PLAYING' and self.player:
                self.player.handle_input(event)

    # ------------------------------------------------------------------
    def process_menu_action(self, action):
        if action == "CONTINUE":
            self.menus.state = 'SAVES_LOAD'

        elif action == "NEW_GAME":
            self.menus.state = 'SAVES_NEW'

        elif action.startswith("SLOT_"):
            self.current_slot = action
            self.state        = 'LOADING'
            if self.menus.state == 'SAVES_NEW':
                self.db.clear_slot(action)
                self.init_world("Polygon")
            elif self.menus.state == 'SAVES_LOAD':
                saved_stage = self.db.get_latest_save_stage(action)
                self.init_world(saved_stage if saved_stage else "Polygon")

        elif action == "RESUME":
            self.state       = 'PLAYING'
            self.menus.state = 'NONE'

        elif action == "NEXT_AFTER_BOSS":
            self.state = 'LOADING'
            self.save_game_data()
            self.init_world("Polygon")

        elif action == "RESTART":
            self.state = 'LOADING'
            if self.player:
                self.player.hp       = self.player.max_hp
                self.player.is_alive = True
            self.init_world(self.stage_manager.current_stage)

        elif action == "TO_MENU":
            self.state       = 'MENU'
            self.menus.state = 'MAIN'
            self.player      = None
            self.all_sprites.empty()

        elif action == "EXIT_GAME":
            self.running = False

        elif action == "SAVE_PROGRESS":
            self.save_game_data()
            notify("Игра сохранена", color=(80, 220, 80))

    # ------------------------------------------------------------------
    def save_game_data(self):
        if not self.current_slot or not self.player:
            return
        self.db.save_game(self.current_slot, {
            'level': self.player.level,
            'hp':    self.player.hp,
            'max_hp': self.player.max_hp,
            'mp':    getattr(self.player, 'mp',     100),
            'max_mp': getattr(self.player, 'max_mp', 100),
            'stage': self.stage_manager.current_stage,
        })

    # ------------------------------------------------------------------
    def update(self):
        if self.boss_loading_started and self.state == 'LOADING':
            now     = pygame.time.get_ticks()
            elapsed = (now - self.loading_timer) / 1000
            if elapsed >= 10:
                self.boss_loading_started = False
                self.init_world("FinalArena")
            return

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

        keys = pygame.key.get_pressed()
        if self.player:
            self.player.update(keys)

        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.update()

        if self.camera:
            self.camera.update(self.player)

        self.combat_system.enemy_attack_logic()
        self.stage_manager.update()

        if self.player and self.player.hp <= 0 and self.state == 'PLAYING':
            self.state = 'GAMEOVER'

    # ------------------------------------------------------------------
    def draw(self):
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

            # Уведомления поверх HUD, но под меню
            draw_notifications(self.screen)

        self.draw_ui_overlays()
        pygame.display.flip()

    # ------------------------------------------------------------------
    def draw_ui_overlays(self):
        # === ГЛАВНОЕ МЕНЮ ===
        if self.state == 'MENU':
            if self.menus.state == "MAIN":
                self.menus.draw_main_menu()
            elif self.menus.state == "SETTINGS":
                self.menus.draw_settings()
            elif self.menus.state in ("SAVES_LOAD", "SAVES_NEW"):
                self.menus.draw_save_slots(
                    self.db.get_all_slots_info(), self.menus.state)

        # === ПАУЗА — показываем паузу ИЛИ настройки поверх игры ===
        elif self.state == 'PAUSE':
            if self.menus.state == "SETTINGS":
                self.menus.draw_settings()       # ← это и была пропущенная строка
            else:
                self.menus.draw_pause_menu()

        # === КАТСЦЕНА ===
        elif self.state == 'CUTSCENE':
            if self.menus.state == "POST_BOSS_CHOICE":
                self.menus.draw_post_boss_menu()
            else:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))

        # === GAME OVER ===
        elif self.state == 'GAMEOVER':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((100, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            text = self.menus.font_big.render(t("gameover_text"), True, (255, 0, 0))
            self.screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

            hint = self.menus.small_font.render(t("gameover_hint"), True, (220, 220, 220))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

    # ------------------------------------------------------------------
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
