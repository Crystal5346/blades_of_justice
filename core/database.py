import sqlite3

class Database:
    def __init__(self, db_path="saves/saves.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS SaveSlots (
            slot_id INTEGER PRIMARY KEY,
            last_played DATETIME,
            is_empty BOOLEAN DEFAULT 1
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS CharacterStats (
            slot_id INTEGER PRIMARY KEY,
            level INTEGER, current_hp REAL, max_hp REAL,
            current_mp REAL, max_mp REAL, current_stage TEXT,
            FOREIGN KEY(slot_id) REFERENCES SaveSlots(slot_id)
        )''')
        # Инициализируем 3 слота
        for i in range(1, 4):
            self.cursor.execute("INSERT OR IGNORE INTO SaveSlots (slot_id, is_empty) VALUES (?, 1)", (i,))
        self.conn.commit()

    def _get_id(self, slot_str):
        return int(slot_str.split("_")[1]) if isinstance(slot_str, str) else slot_str

    def save_game(self, slot_id, stats):
        s_id = self._get_id(slot_id)
        self.cursor.execute("UPDATE SaveSlots SET is_empty = 0, last_played = datetime('now') WHERE slot_id = ?", (s_id,))
        self.cursor.execute('''INSERT OR REPLACE INTO CharacterStats 
            (slot_id, level, current_hp, max_hp, current_mp, max_mp, current_stage)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
            (s_id, stats['level'], stats['hp'], stats['max_hp'], stats['mp'], stats['max_mp'], stats['stage']))
        self.conn.commit()
        
    # Добавь эти методы в класс Database (core/database.py)
    
    def get_all_slots_info(self):
        """Возвращает информацию по всем 3 слотам для меню"""
        self.cursor.execute('''
            SELECT s.slot_id, s.is_empty, c.current_stage, c.level 
            FROM SaveSlots s
            LEFT JOIN CharacterStats c ON s.slot_id = c.slot_id
        ''')
        slots = {}
        for row in self.cursor.fetchall():
            slot_id = f"SLOT_{row[0]}"
            is_empty = bool(row[1])
            stage = row[2] if row[2] else "Lust 1-1"
            lvl = row[3] if row[3] else 1
            slots[slot_id] = {"empty": is_empty, "stage": stage, "level": lvl}
        return slots

    def clear_slot(self, slot_id):
        """Очищает слот для новой игры"""
        s_id = self._get_id(slot_id)
        self.cursor.execute("UPDATE SaveSlots SET is_empty = 1 WHERE slot_id = ?", (s_id,))
        self.cursor.execute("DELETE FROM CharacterStats WHERE slot_id = ?", (s_id,))
        self.conn.commit()

    def get_latest_save_stage(self, slot_id):
        s_id = self._get_id(slot_id)
        self.cursor.execute("SELECT current_stage FROM CharacterStats WHERE slot_id = ?", (s_id,))
        res = self.cursor.fetchone()
        return res[0] if res else None
        
    def update_stage(self, slot_id, stage_name):
        s_id = self._get_id(slot_id)
        # Проверяем, есть ли уже запись для этого слота
        self.cursor.execute("SELECT slot_id FROM CharacterStats WHERE slot_id = ?", (s_id,))
        if self.cursor.fetchone():
            query = "UPDATE CharacterStats SET current_stage = ? WHERE slot_id = ?"
            self.cursor.execute(query, (stage_name, s_id))
        else:
            # Если записи нет, создаем её с дефолтными статами
            query = "INSERT INTO CharacterStats (slot_id, current_stage, level) VALUES (?, ?, ?)"
            self.cursor.execute(query, (s_id, stage_name, 1))
        
        self.conn.commit()
        print(f"DB: Стадия для {slot_id} обновлена на {stage_name}")

    def get_player_stats(self, slot_id):
        s_id = self._get_id(slot_id)
        self.cursor.execute("SELECT * FROM CharacterStats WHERE slot_id = ?", (s_id,))
        row = self.cursor.fetchone()
        if row:
            return {
                'level': row[1], 'hp': row[2], 'max_hp': row[3],
                'mp': row[4], 'max_mp': row[5], 'current_stage': row[6]
            }
        return None
