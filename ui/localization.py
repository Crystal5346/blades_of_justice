# ui/localization.py
# Файл переводов для Blades of Justice
# Добавить новый язык: создать новый словарь и добавить в LANGUAGES

LANGUAGES = {
    "RU": {
        # --- Главное меню ---
        "menu_title":       "BLADES OF JUSTICE",
        "menu_continue":    "ПРОДОЛЖИТЬ",
        "menu_new_game":    "НОВАЯ ИГРА",
        "menu_settings":    "НАСТРОЙКИ",
        "menu_exit":        "ВЫХОД",

        # --- Слоты ---
        "slot_title_load":  "ВЫБОР СОХРАНЕНИЯ",
        "slot_title_new":   "ВЫБОР СЛОТА ДЛЯ НОВОЙ ИГРЫ",
        "slot_empty":       "СЛОТ {n}  —  [ ПУСТО ]",
        "slot_used":        "СЛОТ {n}  —  УР. {lvl}  |  {stage}",
        "slot_back":        "НАЗАД",

        # --- Пауза ---
        "pause_resume":     "ПРОДОЛЖИТЬ",
        "pause_save":       "СОХРАНИТЬ",
        "pause_restart":    "РЕСТАРТ",
        "pause_settings":   "НАСТРОЙКИ",
        "pause_quit":       "ВЫЙТИ В МЕНЮ",

        # --- Настройки ---
        "settings_title":   "НАСТРОЙКИ",
        "settings_music":   "МУЗЫКА",
        "settings_sfx":     "ЭФФЕКТЫ",
        "settings_lang":    "ЯЗЫК",
        "settings_back":    "НАЗАД",
        "settings_wip":     "Больше настроек появится позже",

        # --- После босса ---
        "boss_continue":    "ПРОДОЛЖИТЬ ПУТЬ",
        "boss_menu":        "В ГЛАВНОЕ МЕНЮ",

        # --- Game Over ---
        "gameover_text":    "JUDGMENT",
        "gameover_hint":    "R — перезапустить     M — главное меню",

        # --- Loading ---
        "loading":          "ЗАГРУЗКА...",
        "loading_quotes": [
            "ЧЕЛОВЕЧЕСТВО МЕРТВО.",
            "КРОВЬ — ТОПЛИВО.",
            "АД ПЕРЕПОЛНЕН.",
            "СУД ГРЯДЁТ.",
        ],

        # --- HUD ---
        "hud_weapons":      "ОРУЖИЕ",
        "hud_lvl":          "УР.",
    },

    "EN": {
        # --- Main menu ---
        "menu_title":       "ULTRAKILL: GABRIEL'S JUDGMENT",
        "menu_continue":    "CONTINUE",
        "menu_new_game":    "NEW GAME",
        "menu_settings":    "SETTINGS",
        "menu_exit":        "EXIT",

        # --- Slots ---
        "slot_title_load":  "CHOOSE SAVE TO LOAD",
        "slot_title_new":   "CHOOSE SLOT FOR NEW GAME",
        "slot_empty":       "SLOT {n}  —  [ EMPTY ]",
        "slot_used":        "SLOT {n}  —  LVL {lvl}  |  {stage}",
        "slot_back":        "BACK",

        # --- Pause ---
        "pause_resume":     "RESUME",
        "pause_save":       "SAVE GAME",
        "pause_restart":    "RESTART",
        "pause_settings":   "SETTINGS",
        "pause_quit":       "QUIT TO MENU",

        # --- Settings ---
        "settings_title":   "SETTINGS",
        "settings_music":   "MUSIC",
        "settings_sfx":     "SFX",
        "settings_lang":    "LANGUAGE",
        "settings_back":    "BACK",
        "settings_wip":     "More settings coming soon",

        # --- Post boss ---
        "boss_continue":    "CONTINUE",
        "boss_menu":        "MAIN MENU",

        # --- Game Over ---
        "gameover_text":    "JUDGMENT",
        "gameover_hint":    "R — restart     M — main menu",

        # --- Loading ---
        "loading":          "LOADING...",
        "loading_quotes": [
            "MANKIND IS DEAD.",
            "BLOOD IS FUEL.",
            "HELL IS FULL.",
            "JUDGMENT IS COMING.",
        ],

        # --- HUD ---
        "hud_weapons":      "WEAPONS",
        "hud_lvl":          "LVL",
    },
}

# Текущий язык (меняется в настройках)
_current_lang = "RU"

def set_lang(lang: str):
    global _current_lang
    if lang in LANGUAGES:
        _current_lang = lang

def get_lang() -> str:
    return _current_lang

def t(key: str, **kwargs) -> str:
    """Получить перевод по ключу. kwargs подставляются в {placeholder}."""
    text = LANGUAGES.get(_current_lang, LANGUAGES["RU"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
