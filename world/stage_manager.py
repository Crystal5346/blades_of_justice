import pygame
from config import WIDTH, HEIGHT
# Прямые импорты из папки world
from world.generator_polygon import PolygonGenerator
from world.generator_greed import GreedGenerator
from world.generator_lust import LustGenerator
from world.environment import Wall # Для Арены
from characters.enemies.greed.sisyphus import SisyphusBoss
from world.generator_final import FinalGenerator
from characters.enemies.hamster import SmallHamster, GigaHamster

class StageManager:
    def __init__(self, game):
        self.game = game
        self.current_stage = "Lust 1-1"
        self.level_width = WIDTH
        
        self.level_sequence = [
    "Lust 1-1", "Lust 1-2", "Lust 1-3", "Arena",      # Акт 1: Похоть и Минос
    "Greed 1-1", "Greed 1-2", "Greed 1-3", "ArenaS", # Акт 2: Жадность и Сизиф
    "Polygon",                                       # Перевалочный пункт перед финалом
    "FinalCorridor",                                 # Тот самый длинный коридор (бело-золотой)
    "FinalArena"                                     # Колизей Святого Совета (ГигаХомяк)
]
        
        # Словарь генераторов (Arena тут нет, так как она генерируется методом ниже)
        self.generators = {
            "Lust": LustGenerator(game),
            "Greed": GreedGenerator(game),
            "Polygon": PolygonGenerator(game),
            "Final": FinalGenerator(game)  # Добавили финальный
        }
        
        self.transition_timer = 0
        self.transition_delay = 120 # Обычно 120 кадров = 2 сек (исправил число с 12000)

    def update(self):
        if not self.game.player:
            return

        keys = pygame.key.get_pressed()

        # 1. Логика Полигона (Хаба)
        if self.current_stage == "Polygon":
            if hasattr(self.game, 'ready_door'):
                if self.game.player.rect.colliderect(self.game.ready_door.rect):
                    if keys[pygame.K_w] or keys[pygame.K_o]:
                        # Получаем последнюю ПЕРЕЖИТУЮ арену из БД
                        last_boss_stage = self.game.db.get_latest_save_stage(self.game.current_slot)
                        print(f"LOG: Полигон считал из БД стадию: {last_boss_stage}")
                        
                        if last_boss_stage == "ArenaS":
                            target = "FinalCorridor"
                            print("DEBUG: Путь к Финалу открыт!")
                        elif last_boss_stage == "Arena":
                            target = "Greed 1-1"
                            print("DEBUG: Путь в Жадность открыт.")
                        else:
                            # Это сработает, если в базе стадия "Polygon" или пусто
                            target = "Lust 1-1"
                            print(f"DEBUG: Прогресс неочевиден ({last_boss_stage}), начало игры.")
                        
                        self.game.state = 'LOADING'
                        self.game.init_world(target)
            return

        # 2. Логика Арены (Боссы)
        if "Arena" in self.current_stage:
            if len(self.game.enemies) == 0 and self.game.state == 'PLAYING':
                self.trigger_boss_defeat_sequence()
            return

        # 3. Обычные уровни (Lust, Greed, FinalCorridor)
        alive_enemies = [e for e in self.game.enemies if getattr(e, 'is_alive', True) and not getattr(e, 'is_dummy', False)]
        at_exit_zone = self.game.player.rect.right > self.level_width - 200
        
        if at_exit_zone:
            if keys[pygame.K_w] or keys[pygame.K_o]:
                if len(alive_enemies) == 0:
                    print(f"DEBUG: Переход с {self.current_stage} разрешен.")
                    self.game.save_game_data()
                    self.load_next_stage()
                else:
                    print(f"DEBUG: Нельзя уйти! Осталось врагов: {len(alive_enemies)}")

    def load_stage(self, name):
        """Единая точка входа для смены уровня"""
        print(f"StageManager: Развертывание {name}...")
        self.current_stage = name
        self.clear_world()
        
        base = name.split()[0]
        
        # 1. АРЕНА МИНОСА (Lust)
        if name == "Arena":
            self._generate_boss_arena()
            from characters.enemies.lust.minos import MinosBoss
            boss = MinosBoss(WIDTH // 2, HEIGHT - 300, self.game.player)
            boss.game = self.game
            self.game.enemies.add(boss)
            self.game.all_sprites.add(boss)
            
        # 2. АРЕНА СИЗИФА (Greed)
        elif name == "ArenaS":
            self._generate_boss_arena()
            boss = SisyphusBoss(WIDTH // 2, HEIGHT - 100, self.game.player, self.game)
            self.game.enemies.add(boss)
            self.game.all_sprites.add(boss)
            for wall in self.game.walls:
                if wall.rect.height == 100:
                    wall.image.fill((100, 80, 20))

        # 3. ФИНАЛЬНЫЙ КОРИДОР
        elif name == "FinalCorridor":
            # Вызываем генератор (он сам создаст стены и Мини-Хомяка "Minster")
            self.generators["Final"].generate("FinalCorridor")
            # Уровни ширины берем из того, что прописал генератор
            self.level_width = getattr(self.game, 'level_width', 6000)
            print("SYSTEM: Коридор Суда развернут. Ожидание битвы со стражем.")

        # 4. ФИНАЛЬНАЯ АРЕНА (БОСС)
        elif name == "FinalArena":
            # Вызываем генератор арены (он создаст коробку и GigaHamster)
            self.generators["Final"].generate("FinalArena")
            self.level_width = WIDTH
            print("SYSTEM: Золотая Арена готова. Грызун ждет.")

        # 5. ВСЕ ОСТАЛЬНЫЕ УРОВНИ (Lust, Greed, Polygon)
        elif base in self.generators:
            self.generators[base].generate(name)
            if base == "Polygon": 
                self.level_width = 2500
            else: 
                self.level_width = getattr(self.game, 'level_width', WIDTH)

        print(f"StageManager: Уровень '{name}' готов.")

    def clear_world(self):
        self.game.enemies.empty()
        self.game.walls.empty()
        self.game.all_sprites.empty()
        if self.game.player:
            self.game.all_sprites.add(self.game.player)
            # Ставим игрока чуть выше пола (пол на HEIGHT-100)
            self.game.player.rect.topleft = (150, HEIGHT - 250) 
            self.game.player.vel_y = 0

    def _generate_boss_arena(self):
        self.level_width = WIDTH
        self.game.init_camera(WIDTH, HEIGHT)
        floor = Wall(0, HEIGHT - 100, WIDTH, 100, (230, 230, 250))
        self.game.walls.add(floor)
        self.game.all_sprites.add(floor)
        # Невидимые стены по бокам
        self.game.walls.add(Wall(-50, 0, 50, HEIGHT, (0,0,0)))
        self.game.walls.add(Wall(WIDTH, 0, 50, HEIGHT, (0,0,0)))

    def load_next_stage(self):
        try:
            current_index = self.level_sequence.index(self.current_stage)
            if current_index + 1 < len(self.level_sequence):
                next_level = self.level_sequence[current_index + 1]
                self.game.init_world(next_level)
            else:
                self.game.state = 'MENU'
        except ValueError:
            self.game.init_world("Polygon")

    def trigger_boss_defeat_sequence(self):
        if self.game.state == 'CUTSCENE': return
        self.game.state = 'CUTSCENE'
        self.game.player.vel_y = 0
        
        # 1. Фиксируем победу в базе ПРЯМО СЕЙЧАС
        # Это гарантирует, что на Полигоне last_boss_stage будет "Arena" или "ArenaS"
        self.game.db.update_stage(self.game.current_slot, self.current_stage)
        print(f"DB: Победа подтверждена. Стадия {self.current_stage} сохранена как текущая.")

        # 2. Настраиваем текст меню
        if self.current_stage == "ArenaS":
            self.game.menus.boss_title = "СИЗИФ ОБЕЗГЛАВЛЕН"
            self.game.menus.boss_subtitle = "Восстание в Жадности подавлено. Его душа запечатана."
        else:
            self.game.menus.boss_title = "МИНОС ПОВЕРЖЕН"
            self.game.menus.boss_subtitle = "Судья Ада пал. Путь в Жадность открыт."

        self.game.menus.state = "POST_BOSS_CHOICE"
        # Сохраняем HP и накопленный опыт за босса
        self.game.save_game_data()

    def get_bg_color(self):
        configs = {
            "Polygon": (230, 240, 245),
            "Lust": (30, 10, 50),
            "Greed": (60, 45, 10),
            "Arena": (20, 0, 0),
            "ArenaS": (45, 35, 5),
            "FinalCorridor": (245, 245, 235), # Светлый мрамор
            "FinalArena": (255, 250, 210)     # Золотистый Колизей
        }
        base = self.current_stage.split()[0]
        return configs.get(base, (0, 0, 0))
