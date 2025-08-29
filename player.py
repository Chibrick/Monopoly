class Player:
    def __init__(self, id, name, color, money=1800, position=0, is_ready=False, in_jail=False, jail_turns=0, bankrupt=False, properties = None, is_spectator=False, must_resolve_tile=False):
        self.id = id
        self.name = name
        self.color = color
        self.money = money
        self.position = position
        self.is_ready = is_ready
        self.in_jail = in_jail
        self.jail_turns = jail_turns
        self.bankrupt = bankrupt
        self.properties = properties if properties is not None else []   # Список индексов клеток, которыми владеет игрок
        self.is_spectator = is_spectator
        self.must_resolve_tile = must_resolve_tile
    
    def reset(self):
        """Сброс состояния игрока для новой игры"""
        self.money = 1800
        self.position = 0
        self.is_ready = False
        self.in_jail = False
        self.jail_turns = 0
        self.bankrupt = False
        self.properties = []
    
    def to_dict(self):
        """Преобразование объекта игрока в словарь для передачи по сети"""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "money": self.money,
            "position": self.position,
            "is_ready": self.is_ready,
            "in_jail": self.in_jail,
            "jail_turns": self.jail_turns,
            "bankrupt": self.bankrupt,
            "properties": self.properties,
            "is_spectator": self.is_spectator,
            "must_resolve_tile": self.must_resolve_tile
        }