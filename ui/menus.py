"""
ui/menus.py
Полностью переработанное меню Blades of Justice.
- Красивые шрифты без пикселей (SysFont с антиалиасингом)
- Рабочие Настройки из паузы и главного меню
- Ползунок громкости (заготовка)
- Переключатель языка
"""
import pygame
import math
from config import WIDTH, HEIGHT
from ui.localization import t, set_lang, get_lang

# ---------------------------------------------------------------------------
# Вспомогательный класс: ползунок
# ---------------------------------------------------------------------------

class Slider:
    """Горизонтальный ползунок. value: 0.0 → 1.0"""

    BAR_W  = 340
    BAR_H  = 6
    KNOB_R = 11

    def __init__(self, cx, cy, initial=0.7):
        self.cx    = cx
        self.cy    = cy
        self.value = initial
        self._drag = False

    # Координаты ручки
    def _knob_x(self):
        return int(self.cx - self.BAR_W // 2 + self.value * self.BAR_W)

    def handle_event(self, event):
        kx = self._knob_x()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if math.hypot(event.pos[0] - kx, event.pos[1] - self.cy) < self.KNOB_R + 6:
                self._drag = True
        if event.type == pygame.MOUSEBUTTONUP:
            self._drag = False
        if event.type == pygame.MOUSEMOTION and self._drag:
            left  = self.cx - self.BAR_W // 2
            right = self.cx + self.BAR_W // 2
            self.value = max(0.0, min(1.0, (event.pos[0] - left) / self.BAR_W))

    def draw(self, screen, label: str, font_small, gold, white, gray):
        # Метка
        lbl = font_small.render(label, True, gray)
        screen.blit(lbl, lbl.get_rect(midright=(self.cx - self.BAR_W // 2 - 18, self.cy)))

        left  = self.cx - self.BAR_W // 2
        right = self.cx + self.BAR_W // 2

        # Фоновая полоса
        pygame.draw.rect(screen, (60, 60, 70),
                         (left, self.cy - self.BAR_H // 2, self.BAR_W, self.BAR_H),
                         border_radius=3)
        # Заполненная часть
        fill_w = int(self.value * self.BAR_W)
        if fill_w > 0:
            pygame.draw.rect(screen, gold,
                             (left, self.cy - self.BAR_H // 2, fill_w, self.BAR_H),
                             border_radius=3)

        # Ручка
        kx = self._knob_x()
        pygame.draw.circle(screen, white,  (kx, self.cy), self.KNOB_R)
        pygame.draw.circle(screen, gold,   (kx, self.cy), self.KNOB_R, 2)

        # Процент справа
        pct = font_small.render(f"{int(self.value * 100)}%", True, gray)
        screen.blit(pct, pct.get_rect(midleft=(right + 18, self.cy)))


# ---------------------------------------------------------------------------
# Главный класс меню
# ---------------------------------------------------------------------------

class GameMenus:

    # Цветовая схема
    GOLD       = (255, 215,   0)
    GOLD_DIM   = (180, 140,   0)
    WHITE      = (240, 240, 240)
    GRAY       = (110, 110, 120)
    DARK       = ( 12,  12,  18)
    DARK2      = ( 20,  20,  30)
    ACCENT     = (255, 240, 100)
    RED_DIM    = (160,  30,  30)

    def __init__(self, screen):
        self.screen = screen
        self.state          = "MAIN"
        self.previous_state = "MAIN"

        # --- Шрифты (без пикселей) ---
        self.font_title  = pygame.font.Font(None, 52)
        self.font        = pygame.font.Font(None, 36)
        self.font_big    = pygame.font.Font(None, 62)
        self.small_font  = pygame.font.Font(None, 22)
        self.font_micro  = pygame.font.Font(None, 16)

        # --- Данные ---
        self.boss_title    = "СУД СВЕРШИЛСЯ"
        self.boss_subtitle = "Дух восстания сломлен."
        self.current_slots_info = {}

        # --- Настройки (значения) ---
        self.slider_music = Slider(WIDTH // 2 + 60, 310, 0.7)
        self.slider_sfx   = Slider(WIDTH // 2 + 60, 400, 0.8)

        # --- Фоновая анимация (звёзды) ---
        import random
        self._stars = [
            (random.randint(0, WIDTH), random.randint(0, HEIGHT),
             random.uniform(0.3, 1.0))
            for _ in range(120)
        ]

    # -----------------------------------------------------------------------
    # Внутренние утилиты
    # -----------------------------------------------------------------------

    def _draw_bg(self):
        """Тёмный фон со звёздами."""
        self.screen.fill(self.DARK)
        t_ms = pygame.time.get_ticks()
        for (sx, sy, speed) in self._stars:
            alpha = int(80 + 60 * math.sin(t_ms * 0.001 * speed))
            r = 1 if speed < 0.6 else 2
            col = (alpha, alpha, alpha)
            pygame.draw.circle(self.screen, col, (sx, sy), r)

    def _draw_divider(self, y, width=500):
        """Тонкая золотая линия-разделитель."""
        cx = WIDTH // 2
        pygame.draw.line(self.screen, self.GOLD_DIM,
                         (cx - width // 2, y), (cx + width // 2, y), 1)

    def _draw_button(self, text: str, y: int, mouse_pos,
                     color=None, font=None, hovered_color=None) -> pygame.Rect:
        """Кнопка с hover-эффектом: золотой цвет + боковые черточки."""
        font        = font or self.font
        color       = color or self.WHITE
        hov_color   = hovered_color or self.GOLD

        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, y))

        hovered = rect.inflate(20, 10).collidepoint(mouse_pos)
        if hovered:
            surf = font.render(text, True, hov_color)
            rect = surf.get_rect(center=(WIDTH // 2, y))
            # Боковые черточки
            lx = rect.left  - 48
            rx = rect.right + 12
            for dx, length in [(lx, 30), (rx, 30)]:
                pygame.draw.line(self.screen, self.GOLD,
                                 (dx, y), (dx + length, y), 2)

        self.screen.blit(surf, rect)
        return rect

    def _get_button_rect(self, text: str, y: int, font=None) -> pygame.Rect:
        font = font or self.font
        surf = font.render(text, True, self.WHITE)
        return surf.get_rect(center=(WIDTH // 2, y))

    # -----------------------------------------------------------------------
    # Главное меню
    # -----------------------------------------------------------------------

    def draw_main_menu(self):
        self._draw_bg()
        mouse_pos = pygame.mouse.get_pos()

        # Заголовок
        title = self.font_title.render(t("menu_title"), True, self.GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 130)))
        self._draw_divider(170, 600)

        # Кнопки
        for text_key, y in [
            ("menu_continue", 280),
            ("menu_new_game", 355),
            ("menu_settings", 430),
            ("menu_exit",     505),
        ]:
            self._draw_button(t(text_key), y, mouse_pos)

        # Версия
        ver = self.font_micro.render("v0.9  |  Blades of Justice", True, (50, 50, 60))
        self.screen.blit(ver, ver.get_rect(bottomright=(WIDTH - 16, HEIGHT - 10)))

    # -----------------------------------------------------------------------
    # Слоты сохранений
    # -----------------------------------------------------------------------

    def draw_save_slots(self, slots_info, menu_mode):
        self._draw_bg()
        mouse_pos = pygame.mouse.get_pos()
        self.current_slots_info = slots_info

        title_key = "slot_title_load" if menu_mode == "SAVES_LOAD" else "slot_title_new"
        title = self.font.render(t(title_key), True, self.GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
        self._draw_divider(130, 520)

        y_pos = 240
        for i in range(1, 4):
            info     = slots_info.get(f"SLOT_{i}", {"empty": True})
            is_empty = info.get("empty", True)

            if is_empty:
                label = t("slot_empty", n=i)
                color = self.GRAY
            else:
                label = t("slot_used", n=i,
                          lvl=info.get("level", 1),
                          stage=info.get("stage", "—"))
                color = self.WHITE

            # Карточка слота
            card_rect = pygame.Rect(WIDTH // 2 - 310, y_pos - 24, 620, 52)
            pygame.draw.rect(self.screen, (25, 25, 35), card_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.GOLD_DIM if not is_empty else (50, 50, 60),
                             card_rect, 1, border_radius=8)

            self._draw_button(label, y_pos, mouse_pos, color=color)
            y_pos += 110

        self._draw_divider(y_pos - 30, 400)
        self._draw_button(t("slot_back"), y_pos + 20, mouse_pos, color=self.GRAY)

    # -----------------------------------------------------------------------
    # Пауза
    # -----------------------------------------------------------------------

    def draw_pause_menu(self):
        # Затемнение поверх игры
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        # Заголовок
        pause_lbl = self.font.render("— ПАУЗА —" if get_lang() == "RU" else "— PAUSED —",
                                     True, self.GOLD)
        self.screen.blit(pause_lbl, pause_lbl.get_rect(center=(WIDTH // 2, 190)))
        self._draw_divider(220, 400)

        for text_key, y in [
            ("pause_resume",   295),
            ("pause_save",     365),
            ("pause_restart",  435),
            ("pause_settings", 505),
            ("pause_quit",     575),
        ]:
            col = self.GOLD if text_key == "pause_save" else self.WHITE
            self._draw_button(t(text_key), y, mouse_pos, color=col)

    # -----------------------------------------------------------------------
    # Настройки (рабочие)
    # -----------------------------------------------------------------------

    def draw_settings(self):
        self._draw_bg()
        mouse_pos = pygame.mouse.get_pos()

        title = self.font.render(t("settings_title"), True, self.GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
        self._draw_divider(135, 500)

        # Ползунки
        self.slider_music.draw(self.screen, t("settings_music"),
                               self.small_font, self.GOLD, self.WHITE, self.GRAY)
        self.slider_sfx.draw(self.screen, t("settings_sfx"),
                             self.small_font, self.GOLD, self.WHITE, self.GRAY)

        # Разделитель перед языком
        self._draw_divider(460, 400)

        # Переключатель языка
        lang_lbl = self.small_font.render(t("settings_lang") + ":", True, self.GRAY)
        self.screen.blit(lang_lbl, lang_lbl.get_rect(midright=(WIDTH // 2 - 20, 510)))

        for lang_code, lx in [("RU", WIDTH // 2 + 10), ("EN", WIDTH // 2 + 80)]:
            is_active = get_lang() == lang_code
            col  = self.GOLD  if is_active else self.GRAY
            surf = self.font.render(lang_code, True, col)
            rect = surf.get_rect(midleft=(lx, 510))
            self.screen.blit(surf, rect)
            if is_active:
                pygame.draw.line(self.screen, self.GOLD,
                                 (rect.left, rect.bottom + 3),
                                 (rect.right, rect.bottom + 3), 2)

        # Подпись
        wip = self.font_micro.render(t("settings_wip"), True, (55, 55, 65))
        self.screen.blit(wip, wip.get_rect(center=(WIDTH // 2, 580)))

        self._draw_divider(610, 400)
        self._draw_button(t("settings_back"), 650, mouse_pos, color=self.GRAY)

    # -----------------------------------------------------------------------
    # После босса
    # -----------------------------------------------------------------------

    def draw_post_boss_menu(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        title = self.font_big.render(self.boss_title, True, self.GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
        self._draw_divider(HEIGHT // 3 + 50, 500)

        sub = self.small_font.render(self.boss_subtitle, True, self.WHITE)
        self.screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 80)))

        self._draw_button(t("boss_continue"), 480, mouse_pos)
        self._draw_button(t("boss_menu"),     555, mouse_pos, color=self.GRAY)

    # -----------------------------------------------------------------------
    # Вспомогательные
    # -----------------------------------------------------------------------

    def draw_cutscene_text(self, text):
        self._draw_bg()
        surf = self.small_font.render(text, True, self.WHITE)
        self.screen.blit(surf, surf.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        hint = self.font_micro.render("[SPACE — продолжить]", True, self.GRAY)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 50)))

    def _slot_label(self, slot_key: str, index: int) -> str:
        info = self.current_slots_info.get(slot_key, {"empty": True})
        if info.get("empty", True):
            return t("slot_empty", n=index)
        return t("slot_used", n=index,
                 lvl=info.get("level", 1),
                 stage=info.get("stage", "—"))

    # -----------------------------------------------------------------------
    # Обработка ввода
    # -----------------------------------------------------------------------

    def handle_input(self, event):
        # Ползунки обрабатываем всегда когда открыты настройки
        if self.state == "SETTINGS":
            self.slider_music.handle_event(event)
            self.slider_sfx.handle_event(event)

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        mp = event.pos

        # --- Главное меню ---
        if self.state == "MAIN":
            if self._get_button_rect(t("menu_continue"), 280).collidepoint(mp):
                return "CONTINUE"
            if self._get_button_rect(t("menu_new_game"), 355).collidepoint(mp):
                self.state = "SAVES_NEW"
            if self._get_button_rect(t("menu_settings"), 430).collidepoint(mp):
                self.previous_state = "MAIN"
                self.state = "SETTINGS"
            if self._get_button_rect(t("menu_exit"), 505).collidepoint(mp):
                return "EXIT_GAME"

        # --- Слоты ---
        elif self.state in ("SAVES_LOAD", "SAVES_NEW"):
            y_pos = 240
            for i in range(1, 4):
                if self._get_button_rect(self._slot_label(f"SLOT_{i}", i), y_pos).collidepoint(mp):
                    return f"SLOT_{i}"
                y_pos += 110
            if self._get_button_rect(t("slot_back"), y_pos + 20).collidepoint(mp):
                self.state = "MAIN"

        # --- Пауза ---
        elif self.state == "PAUSE":
            if self._get_button_rect(t("pause_resume"),   295).collidepoint(mp): return "RESUME"
            if self._get_button_rect(t("pause_save"),     365).collidepoint(mp): return "SAVE_PROGRESS"
            if self._get_button_rect(t("pause_restart"),  435).collidepoint(mp): return "RESTART"
            if self._get_button_rect(t("pause_settings"), 505).collidepoint(mp):
                self.previous_state = "PAUSE"
                self.state = "SETTINGS"
            if self._get_button_rect(t("pause_quit"),     575).collidepoint(mp): return "TO_MENU"

        # --- Настройки ---
        elif self.state == "SETTINGS":
            # Переключатель языка
            for lang_code, lx in [("RU", WIDTH // 2 + 10), ("EN", WIDTH // 2 + 80)]:
                surf = self.font.render(lang_code, True, self.WHITE)
                rect = surf.get_rect(midleft=(lx, 510))
                if rect.inflate(12, 12).collidepoint(mp):
                    set_lang(lang_code)
            if self._get_button_rect(t("settings_back"), 650).collidepoint(mp):
                self.state = self.previous_state

        # --- После босса ---
        elif self.state == "POST_BOSS_CHOICE":
            if self._get_button_rect(t("boss_continue"), 480).collidepoint(mp):
                return "NEXT_AFTER_BOSS"
            if self._get_button_rect(t("boss_menu"),     555).collidepoint(mp):
                return "TO_MENU"

        return None
