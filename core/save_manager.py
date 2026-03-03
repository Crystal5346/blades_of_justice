class SaveManager:
    def __init__(self, db):
        self.db = db

    def save_game(self, slot_id, player, stage_name):
        """Собирает данные из объекта игрока и отправляет в БД"""
        if not slot_id or not player:
            return
            
        # Извлекаем только нужные значения
        stats = {
            'level': player.level,
            'hp': player.hp,
            'max_hp': player.max_hp,
            'mp': getattr(player, 'mp', 0),
            'max_mp': getattr(player, 'max_mp', 0),
            'stage': stage_name
        }
        
        self.db.save_game(slot_id, stats)

    def load_game(self, slot_id, player):
        """Загружает данные из БД и применяет их к игроку"""
        data = self.db.get_player_stats(slot_id)
        if data and player:
            player.level = data['level']
            player.hp = data['hp']
            player.max_hp = data['max_hp']
            if hasattr(player, 'mp'):
                player.mp = data['mp']
                player.max_mp = data['max_mp']
            return data['current_stage']
        return "Polygon"
