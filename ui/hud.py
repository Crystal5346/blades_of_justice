import pygame
from config import WIDTH

class HUD:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.name = "Царь Сизиф"
        self.name = "Царь Минос"
        
        # Шрифты
        self.font_main = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 14, bold=True)

        # Размеры полосок
        self.bar_width = 250
        self.bar_height = 20
        self.x_offset = 20
        self.y_offset = 20

    def draw_bar(self, x, y, current, maximum, color, label):
        """Универсальный метод для рисования полоски с рамкой и текстом"""
        # Рассчитываем ширину заполнения
        fill_width = int((current / maximum) * self.bar_width)
        
        # Фон полоски (темный)
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, self.bar_width, self.bar_height))
        
        # Заполнение (сама полоска)
        if fill_width > 0:
            # Рисуем основной цвет
            pygame.draw.rect(self.screen, color, (x, y, fill_width, self.bar_height))
            # Добавляем светлую полоску сверху для эффекта объема
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, fill_width, 2), 1)

        # Рамка
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, self.bar_width, self.bar_height), 2)

        # Текст (Название и значения)
        text_surf = self.font_small.render(f"{label}: {int(current)}/{int(maximum)}", True, (255, 255, 255))
        self.screen.blit(text_surf, (x + 5, y + 2))
        
    def draw_boss_hp(self, boss):
        bar_width = 700
        bar_height = 25
        x = WIDTH // 2 - bar_width // 2
        y = 40
        
        # --- ОПРЕДЕЛЕНИЕ СТИЛЯ ---
        boss_name = boss.name.upper() if hasattr(boss, 'name') else "БОСС"
        
        # По умолчанию (Минос)
        hp_color = (100, 149, 237)  # Синий
        bg_color = (20, 20, 40)
        frame_color = (200, 200, 200)

        if "СИЗИФ" in boss_name:
            phase = getattr(boss, 'phase', 1)
            hp_color = (218, 165, 32) if phase == 1 else (255, 69, 0)
            bg_color = (60, 40, 0)
            frame_color = (255, 215, 0)
        
        # НОВОЕ: Стиль для ГигаХомяка
        elif "ХОМЯК" in boss_name or "GIGA" in boss_name:
            hp_color = (255, 215, 0)    # Ярко-золотой
            bg_color = (139, 69, 19)   # Коричневый подшерсток
            frame_color = (255, 255, 255) # Белый мрамор
            boss_name = "ВЕЛИКИЙ СВЯТОЙ ХОМЯК"

        # --- ОТРИСОВКА ---
        # Тень
        pygame.draw.rect(self.screen, (10, 10, 10), (x - 4, y - 4, bar_width + 8, bar_height + 8))
        pygame.draw.rect(self.screen, bg_color, (x, y, bar_width, bar_height))

        # Текущее HP
        hp_ratio = max(0, boss.hp / boss.max_hp)
        if hp_ratio > 0:
            pygame.draw.rect(self.screen, hp_color, (x, y, int(bar_width * hp_ratio), bar_height))
            # Эффект блеска
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, int(bar_width * hp_ratio), 2), 0)

        # Рамка
        pygame.draw.rect(self.screen, frame_color, (x, y, bar_width, bar_height), 2)

        # Текст
        font = pygame.font.SysFont("Georgia", 24, bold=True)
        name_surf = font.render(boss_name, True, (255, 255, 255))
        self.screen.blit(name_surf, (WIDTH // 2 - name_surf.get_width() // 2, y - 35))

        hp_text = self.font_small.render(f"{int(boss.hp)} / {int(boss.max_hp)}", True, (255, 255, 255))
        self.screen.blit(hp_text, (WIDTH // 2 - hp_text.get_width() // 2, y + 4))

    def draw(self):
        # 1. Получаем свежие данные от игрока
        data = self.player.get_hud_data()

        # 2. Отрисовка HP (Здоровье) - Красный
        self.draw_bar(self.x_offset, self.y_offset, data["hp"], data["max_hp"], (200, 30, 30), "HP")

        # 3. Отрисовка MP (Мана) - Синий
        self.draw_bar(self.x_offset, self.y_offset + 30, data["mp"], data["max_mp"], (30, 100, 200), "MP")

        # 4. Отрисовка Уровня и Опыта
        level_text = self.font_main.render(f"LVL: {data['lvl']}", True, (255, 215, 0))
        self.screen.blit(level_text, (self.x_offset, self.y_offset + 60))

        # Полоска опыта (под уровнем)
        exp_width = int((data["exp"] / (100 * data["lvl"])) * 100)
        pygame.draw.rect(self.screen, (40, 40, 40), (self.x_offset + 80, self.y_offset + 68, 100, 8))
        pygame.draw.rect(self.screen, (50, 200, 50), (self.x_offset + 80, self.y_offset + 68, exp_width, 8))
        pygame.draw.rect(self.screen, (150, 150, 150), (self.x_offset + 80, self.y_offset + 68, 100, 8), 1)

        # 5. Индикатор разблокированного оружия (справа внизу)
        y_weapon = 110
        weapon_label = self.font_small.render("WEAPONS:", True, (180, 180, 180))
        self.screen.blit(weapon_label, (self.x_offset, self.y_offset + 90))
        
        for weapon in data["weapons"]:
            w_text = self.font_small.render(f"• {weapon}", True, (255, 255, 255))
            self.screen.blit(w_text, (self.x_offset + 10, self.y_offset + y_weapon))
            y_weapon += 18
