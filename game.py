class Game:
    def __init__(self, players, first_player):
        self.players = players  # Список ID игроков
        self.current_player = first_player
        self.winner = None
        self.next_circle = False
    
    def update_from_data(self, game_data):
        """Обновление состояния игры из полученных данных"""
        self.current_player = game_data["current_player"]
        self.winner = game_data.get("winner")
    
    def next_turn(self, players):
        """Переход хода к следующему активному игроку"""
        if self.winner:
            return

        current_index = self.players.index(self.current_player)
        total_players = len(self.players)
        
        for i in range(1, total_players + 1):
            next_index = (current_index + i) % total_players
            if next_index < current_index:
                self.next_circle = True
            next_player_id = self.players[next_index]
            player = next((p for p in players if p.id == next_player_id), None)

            if player and not player.bankrupt and not player.is_spectator:
                self.current_player = next_player_id
                return

        # Остался только один активный игрок
        active = [p.id for p in players if not p.bankrupt and not p.is_spectator]
        if len(active) == 1:
            self.winner = active[0]