import pygame
from config import WIDTH, HEIGHT

class GameMenus:
    def __init__(self, screen, font_path=None):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 42, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.font_big = pygame.font.SysFont("Arial", 64, bold=True) 
        
        self.state = "MAIN"  # MAIN, SETTINGS, SAVES_LOAD, SAVES_NEW, PAUSE
        self.previous_state = "MAIN" 
        
        # Палитра
        self.GOLD = (255, 215, 0)
        self.WHITE = (240, 240, 240)
        self.DARK = (15, 15, 20)
        self.GRAY = (120, 120, 130) # Цвет для пустых слотов
        
        self.boss_title = "СУД СВЕРШИЛСЯ"
        self.boss_subtitle = "Дух восстания сломлен."

        # Здесь будем хранить актуальную инфу по слотам
        self.current_slots_info = {}

    def _get_button_rect(self, text, y_pos):
        text_surf = self.font.render(text, True, self.WHITE)
        return text_surf.get_rect(center=(WIDTH // 2, y_pos))

    def _draw_button(self, text, y_pos, mouse_pos, custom_color=None):
        base_color = custom_color if custom_color else self.WHITE
        text_surf = self.font.render(text, True, base_color)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, y_pos))
        
        is_hovered = text_rect.collidepoint(mouse_pos)
        if is_hovered:
            text_surf = self.font.render(text, True, self.GOLD)
            pygame.draw.line(self.screen, self.GOLD, (text_rect.left - 40, y_pos), (text_rect.left - 10, y_pos), 3)
            pygame.draw.line(self.screen, self.GOLD, (text_rect.right + 10, y_pos), (text_rect.right + 40, y_pos), 3)
            
        self.screen.blit(text_surf, text_rect)
        return text_rect

    def draw_main_menu(self):
        self.screen.fill(self.DARK)
        mouse_pos = pygame.mouse.get_pos()
        
        title = self.font.render("ULTRAKILL: GABRIEL'S JUDGMENT", True, self.GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

        self._draw_button("CONTINUE", 280, mouse_pos)
        self._draw_button("NEW GAME", 360, mouse_pos)
        self._draw_button("SETTINGS", 440, mouse_pos)
        self._draw_button("EXIT", 520, mouse_pos)

    def draw_settings(self):
        """Простая заглушка, чтобы игра не крашилась при нажатии на Настройки"""
        self.screen.fill(self.DARK)
        mouse_pos = pygame.mouse.get_pos()
        title = self.font.render("SETTINGS (WORK IN PROGRESS)", True, self.WHITE)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 200)))
        self._draw_button("BACK", 550, mouse_pos)

    def draw_save_slots(self, slots_info, menu_mode):
        self.screen.fill(self.DARK)
        mouse_pos = pygame.mouse.get_pos()
        self.current_slots_info = slots_info # Запоминаем для генерации клик-зон
        
        title_text = "CHOOSE SAVE TO LOAD" if menu_mode == "SAVES_LOAD" else "CHOOSE SLOT FOR NEW GAME"
        title = self.font.render(title_text, True, self.GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

        y_offset = 250
        for i in range(1, 4):
            button_text = self._get_slot_text(f"SLOT_{i}", i)
            info = slots_info.get(f"SLOT_{i}", {"empty": True})
            color = self.GRAY if info["empty"] else self.WHITE

            self._draw_button(button_text, y_offset, mouse_pos, custom_color=color)
            y_offset += 130 
            
        self._draw_button("BACK", 650, mouse_pos)

    def draw_pause_menu(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        self._draw_button("RESUME",       250, mouse_pos)
        self._draw_button("SAVE GAME",    330, mouse_pos, custom_color=self.GOLD)
        self._draw_button("RESTART",      410, mouse_pos)
        self._draw_button("SETTINGS",     490, mouse_pos)
        self._draw_button("QUIT TO MENU", 570, mouse_pos)

    def _get_slot_text(self, slot_key, index):
        """Вспомогательный метод для генерации текста кнопки (нужен для ширины Rect)"""
        info = self.current_slots_info.get(slot_key, {"empty": True})
        if info["empty"]: 
            return f"SLOT {index} - [ EMPTY ]"
        return f"SLOT {index} - LVL {info['level']} ({info['stage']})"
        
    def draw_post_boss_menu(self):
        """Универсальное меню после босса"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220)) 
        self.screen.blit(overlay, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Динамический заголовок
        title = self.font_big.render(self.boss_title, True, self.GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 3)))

        # Динамический подзаголовок
        sub_title = self.small_font.render(self.boss_subtitle, True, self.WHITE)
        self.screen.blit(sub_title, sub_title.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 60)))

        # Универсальная кнопка продолжения
        self._draw_button("ПРОДОЛЖИТЬ ПУТЬ", 480, mouse_pos)
        self._draw_button("В ГЛАВНОЕ МЕНЮ", 560, mouse_pos)

    def draw_cutscene_text(self, text):
        """Отрисовка текста катсцены на черном фоне"""
        self.screen.fill(self.DARK)
        text_surf = self.small_font.render(text, True, self.WHITE)
        self.screen.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        
        hint = self.small_font.render("[Нажмите SPACE, чтобы продолжить]", True, self.GRAY)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 50)))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            
            if self.state == "MAIN":
                if self._get_button_rect("CONTINUE", 280).collidepoint(m_pos): return "CONTINUE"
                # NEW GAME теперь не возвращает состояние в main.py, а меняет меню
                if self._get_button_rect("NEW GAME", 360).collidepoint(m_pos): self.state = "SAVES_NEW"
                if self._get_button_rect("SETTINGS", 440).collidepoint(m_pos): 
                    self.previous_state = "MAIN"
                    self.state = "SETTINGS"
                if self._get_button_rect("EXIT", 520).collidepoint(m_pos): return "EXIT_GAME"
                
            # Обработка обоих экранов слотов
            elif self.state in ["SAVES_LOAD", "SAVES_NEW"]:
                if self._get_button_rect(self._get_slot_text("SLOT_1", 1), 250).collidepoint(m_pos): return "SLOT_1"
                if self._get_button_rect(self._get_slot_text("SLOT_2", 2), 380).collidepoint(m_pos): return "SLOT_2"
                if self._get_button_rect(self._get_slot_text("SLOT_3", 3), 510).collidepoint(m_pos): return "SLOT_3"
                if self._get_button_rect("BACK", 650).collidepoint(m_pos): self.state = "MAIN"

            elif self.state == "PAUSE":
                if self._get_button_rect("RESUME",       250).collidepoint(m_pos): return "RESUME"
                if self._get_button_rect("SAVE GAME",    330).collidepoint(m_pos): return "SAVE_PROGRESS"
                if self._get_button_rect("RESTART",      410).collidepoint(m_pos): return "RESTART"
                if self._get_button_rect("SETTINGS",     490).collidepoint(m_pos):
                    self.previous_state = "PAUSE"
                    self.state = "SETTINGS"
                if self._get_button_rect("QUIT TO MENU", 570).collidepoint(m_pos): return "TO_MENU"

            elif self.state == "SETTINGS":
                if self._get_button_rect("BACK", 550).collidepoint(m_pos):
                    self.state = self.previous_state
            # ДОБАВЬ ЭТОТ БЛОК В КОНЕЦ:
            elif self.state == "POST_BOSS_CHOICE":
                # Теперь проверяем универсальный текст кнопки
                if self._get_button_rect("ПРОДОЛЖИТЬ ПУТЬ", 480).collidepoint(m_pos):
                    return "NEXT_AFTER_BOSS" # Изменили возвращаемое значение!
                
                if self._get_button_rect("В ГЛАВНОЕ МЕНЮ", 560).collidepoint(m_pos):
                    return "TO_MENU"
        return None
