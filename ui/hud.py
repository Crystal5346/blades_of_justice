"""
ui/hud.py — Крупный красивый HUD для Blades of Justice.
HP / MP / EXP — широкие полоски с блик-эффектом.
Уровень и оружие — под полосками.
Полоска HP босса — вверху по центру с пульсацией при низком HP.
"""
import pygame
import math
from config import WIDTH, HEIGHT
from ui.localization import t


def _rounded_bar(surf, x, y, w, h, ratio, bg, fill, border, r=6):
    ratio  = max(0.0, min(1.0, ratio))
    fill_w = max(0, int(w * ratio))
    pygame.draw.rect(surf, bg,     (x, y, w,      h), border_radius=r)
    if fill_w > 0:
        pygame.draw.rect(surf, fill,   (x, y, fill_w, h), border_radius=r)
        # Блик сверху
        pygame.draw.rect(surf, (255, 255, 255),
                         (x + 2, y + 2, fill_w - 4, max(1, h // 5)),
                         border_radius=r)
    pygame.draw.rect(surf, border, (x, y, w,      h), 1, border_radius=r)


class HUD:
    # Цвета полосок
    HP_FILL  = (210,  38,  38)
    HP_BG    = ( 48,   8,   8)
    MP_FILL  = ( 28, 100, 215)
    MP_BG    = (  8,  18,  48)
    EXP_FILL = ( 42, 195,  62)
    EXP_BG   = (  8,  32,  10)
    BORDER   = ( 75,  75,  88)
    GOLD     = (255, 215,   0)
    WHITE    = (232, 232, 232)
    GRAY     = (135, 135, 148)
    PANEL_BG = ( 10,  10,  16, 185)

    BAR_W = 290
    BAR_H =  23
    PX    =  18   # отступ X
    PY    =  16   # отступ Y

    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.f_lbl    = pygame.font.Font(None, 13)
        self.f_val    = pygame.font.Font(None, 13)
        self.f_lvl    = pygame.font.Font(None, 18)
        self.f_weapon = pygame.font.Font(None, 16)
        self.f_bname  = pygame.font.Font(None, 22)
        self.f_bval   = pygame.font.Font(None, 14)

    # --- фоновая панель ---
    def _panel(self, x, y, w, h):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(self.PANEL_BG)
        pygame.draw.rect(s, (52, 52, 64, 190), (0, 0, w, h), 1, border_radius=7)
        self.screen.blit(s, (x, y))

    # --- полоска с подписью ---
    def _bar(self, x, y, cur, mx, label, fill, bg):
        lbl = self.f_lbl.render(label, True, self.GRAY)
        self.screen.blit(lbl, (x, y))
        by  = y + lbl.get_height() + 3
        _rounded_bar(self.screen, x, by, self.BAR_W, self.BAR_H,
                     cur / mx if mx else 0, bg, fill, self.BORDER)
        val = self.f_val.render(f"{int(cur)} / {int(mx)}", True, self.WHITE)
        self.screen.blit(val, val.get_rect(midleft=(x + 8, by + self.BAR_H // 2)))
        return by + self.BAR_H   # нижняя граница

    # ----------------------------------------------------------------
    def draw(self):
        data = self.player.get_hud_data()
        x, y = self.PX, self.PY

        ph = 232 + len(data["weapons"]) * 21
        self._panel(x - 7, y - 7, self.BAR_W + 18, ph)

        b = self._bar(x, y, data["hp"], data["max_hp"], "HP",
                      self.HP_FILL, self.HP_BG)
        b = self._bar(x, b + 11, data["mp"], data["max_mp"], "MP",
                      self.MP_FILL, self.MP_BG)
        b = self._bar(x, b + 11, data["exp"], max(data["exp_to_next"], 1), "EXP",
                      self.EXP_FILL, self.EXP_BG)

        lvl = self.f_lvl.render(f"{t('hud_lvl')}  {data['lvl']}", True, self.GOLD)
        self.screen.blit(lvl, (x, b + 9))

        wy = b + lvl.get_height() + 16
        wl = self.f_weapon.render(t("hud_weapons") + ":", True, self.GRAY)
        self.screen.blit(wl, (x, wy))
        wy += wl.get_height() + 5

        for i, weapon in enumerate(data["weapons"]):
            col  = self.GOLD if i == len(data["weapons"]) - 1 else self.WHITE
            ws   = self.f_weapon.render(f"  ›  {weapon}", True, col)
            self.screen.blit(ws, (x + 4, wy))
            wy  += ws.get_height() + 3

    # ----------------------------------------------------------------
    def draw_boss_hp(self, boss):
        BW, BH = 700, 27
        bx = WIDTH  // 2 - BW // 2
        by = 38

        name  = boss.name.upper() if hasattr(boss, "name") else "BOSS"
        hcol  = ( 75, 125, 228)
        bgcol = ( 10,  10,  32)
        fcol  = (115, 115, 158)

        if "СИЗИФ" in name:
            ph    = getattr(boss, "phase", 1)
            hcol  = (208, 158,  18) if ph == 1 else (225, 52, 0)
            bgcol = ( 38,  25,   0)
            fcol  = (255, 215,   0)
        elif "ХОМЯК" in name or "GIGA" in name:
            hcol  = (255, 215,   0)
            bgcol = ( 75,  38,   5)
            fcol  = (255, 255, 255)
            name  = "ВЕЛИКИЙ СВЯТОЙ ХОМЯК"
        elif "МИНОС" in name or "MINOS" in name:
            hcol  = ( 88,  38, 198)
            bgcol = ( 18,   4,  38)
            fcol  = (155,  75, 255)

        # Панель
        panel = pygame.Surface((BW + 24, BH + 58), pygame.SRCALPHA)
        panel.fill((4, 4, 10, 195))
        self.screen.blit(panel, (bx - 12, by - 32))

        # Имя
        ns = self.f_bname.render(name, True, (228, 228, 228))
        self.screen.blit(ns, ns.get_rect(center=(WIDTH // 2, by - 14)))

        ratio = max(0.0, boss.hp / boss.max_hp)
        _rounded_bar(self.screen, bx, by, BW, BH, ratio, bgcol, hcol, fcol, r=5)

        # Пульсация при низком HP
        if ratio < 0.25:
            p = int(55 + 38 * math.sin(pygame.time.get_ticks() * 0.008))
            gl = pygame.Surface((BW, BH), pygame.SRCALPHA)
            gl.fill((*hcol, p))
            self.screen.blit(gl, (bx, by))

        ht = self.f_bval.render(f"{int(boss.hp)} / {int(boss.max_hp)}", True, (218, 218, 218))
        self.screen.blit(ht, ht.get_rect(center=(WIDTH // 2, by + BH // 2)))
