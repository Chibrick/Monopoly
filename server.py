import socket
import threading
import pickle
import struct
import time
import logging
import random
import math
import os
import select
import traceback
import operator
from player import Player
from game import Game
from constants import *

class Server:
    def __init__(self, host="localhost", port=5555, ready_event=None):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.players = []
        self.lock = threading.Lock()
        self.game = None
        self.ready_event = ready_event

        self.board_data = BOARD1
        self.count_circle = 1
        self.refresh_board()
        self.board_id = 1
        self.is_mode = False
        self.bank = 0

        self.events = []
        self.running = True
        self.next_player_id = 0
        self.trade_offer = None
        self.roll_dice_count = 0
        self.awaiting_property_decision = None  # dict with player_id and property_index
        self.dice1 = 0
        self.dice2 = 0
        self.auction = None
        self.last_dice_result = None

        self.abilities_by_player = {}  # {player_id: [{"name": str, "count": int, "price": int}]}

        self.BINARY_OPS = [
            ("+", lambda a, b: a + b, 1),
            ("-", lambda a, b: a - b, 1),
            ("*", lambda a, b: a * b, 2),
            # ("**", lambda a, b: a ** b if abs(b) < 5 else float('inf'), 4),
            # ("//", lambda a, b: a // b if b != 0 else float('inf'), 2),
            # ("%", lambda a, b: a % b if b != 0 else float('inf'), 2)
        ]

        self.UNARY_OPS = [
            ("abs({x})", lambda x: abs(x), 2),
            # ("√({x})", lambda x: math.sqrt(x) if x >= 0 else float('inf'), 3),
            ("-({x})", lambda x: -x, 1)
        ]
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)

    def refresh_board(self):
        fixed_indices = [0, 10, 20, 30]

        # 1. Сохраняем старые клетки и владельцев
        old_board = self.board_data
        index_to_owner = {}
        for i, cell in enumerate(old_board):
            owner_id = cell.get("owner")
            if owner_id is not None:
                index_to_owner[i] = owner_id

        # 2. Отделяем и перемешиваем только неприкосновенные клетки
        fixed_cells = {i: old_board[i] for i in fixed_indices}
        shuffle_cells = [cell for i, cell in enumerate(old_board) if i not in fixed_indices]
        random.shuffle(shuffle_cells)

        # 3. Собираем новую доску
        new_board = []
        shuffle_iter = iter(shuffle_cells)
        new_index_mapping = {}  # ключ: старый индекс → новый индекс
        for i in range(len(old_board)):
            if i in fixed_cells:
                new_board.append(fixed_cells[i])
                new_index_mapping[i] = i  # остались на месте
            else:
                old_cell = next(shuffle_iter)
                old_index = old_board.index(old_cell)
                new_board.append(old_cell)
                new_index_mapping[old_index] = i

        # 4. Обновляем board_data
        self.board_data = new_board

        # 5. Переназначаем владельцев на основе новой доски
        for cell in self.board_data:
            cell["owner"] = None
            cell["color_owner"] = None

        for old_index, owner_id in index_to_owner.items():
            new_index = new_index_mapping.get(old_index)
            if new_index is not None:
                self.board_data[new_index]["owner"] = owner_id
                player = self.get_player_by_id(owner_id)
                if player:
                    self.board_data[new_index]["color_owner"] = player.color

        # 6. Обновляем player.properties
        for player in self.players:
            player.properties = [
                i for i, cell in enumerate(self.board_data)
                if cell.get("owner") == player.id
            ]

        # 7. Дополнительно
        if self.count_circle == 1:
            self.assign_cell_images_and_names()
        else:
            self.board_id += 1
            self.events.append(f"🔀 Перемешивание доски")

    def assign_cell_images_and_names(self):
        used_images_by_type = {
            "property": {},
            "cars": set(),
            "utility": set(),
            "tax": set(),
            "quest": set(),
            "start": set(),
            "jail": set(),
            "casino": set(),
            "gotojail": set(),
        }

        for i, cell in enumerate(self.board_data):
            cell_type = cell["type"]

            if cell_type == "property":
                category_path = f"images/property/{int(cell['category'])}"
                used = used_images_by_type[cell_type].setdefault(int(cell.get("category", 0)), set())
            elif cell_type == "cars":
                category_path = "images/cars"
                used = used_images_by_type[cell_type]
            elif cell_type == "utility":
                category_path = f"images/utility"
                used = used_images_by_type[cell_type]
            elif cell_type == "tax":
                category_path = f"images/tax"
                used = used_images_by_type[cell_type]
            elif cell_type == "quest":
                category_path = f"images/quest"
                used = used_images_by_type[cell_type]
            elif cell_type in ("start", "jail", "casino", "gotojail"):
                category_path = "images/General"
                used = used_images_by_type[cell_type]
            else:
                continue  # для других типов не трогаем

            prefix = cell["type"].lower() if cell["type"] in ("start", "jail", "casino", "gotojail", "quest", "tax") else ""
            try:
                image_files = [f for f in os.listdir(category_path) if f.lower().endswith(".png")]

                # Если спец. тип — отбираем только нужный префикс
                if cell_type in ("start", "jail", "casino", "gotojail"):
                    prefix = cell_type.lower()
                    image_files = [f for f in image_files if f.lower().startswith(prefix)]

                # Исключаем уже использованные
                available = [f for f in image_files if f not in used]

                if available:
                    selected = random.choice(available)
                    used.add(selected)
                    cell["image"] = os.path.join(category_path, selected)
                    cell["name"] = os.path.splitext(selected)[0]
                else:
                    # Нет доступных уникальных файлов — не назначаем
                    cell["image"] = None
                if prefix:
                    cell["name"] = prefix

            except FileNotFoundError:
                print(f"[assign_cell_images_and_names] Папка не найдена: {category_path}")
                cell["image"] = None

    def start(self):
        """Запуск сервера"""
        try:
            self.server.bind(self.addr)
            self.server.listen()
            self.logger.info(f"Сервер запущен на {self.host}:{self.port}")
            if self.ready_event:
                self.ready_event.set()
            
            # Запускать приём клиентов в отдельном потоке!
            threading.Thread(target=self.accept_connections, daemon=True).start()
            # Поток для обработки подключений
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True  # Помечаем как daemon-поток
            accept_thread.start()

            # Главный цикл сервера
            while self.running:
                time.sleep(1)  # Чтобы не грузить процессор
                
        except socket.error as e:
            self.logger.error(f"Ошибка сервера: {e}")
        finally:
            self.running = False
            self.server.close()
            self.logger.info("Сервер остановлен")
    
    def accept_connections(self):
        """Принятие новых подключений"""
        while self.running:
            
            try:
                conn, addr = self.server.accept()
                self.logger.info(f"Новое подключение от {addr}")
                
                with self.lock:
                    player_id = self.next_player_id
                    self.next_player_id += 1
                    player = Player(player_id, f"Игрок {player_id + 1}", PLAYER_COLORS[random.randint(0, 5)])
                    player.conn = conn  # Сохраняем соединение
                    self.abilities_by_player[player.id] = [
                        {"name": "Телепорт", "count": 0, "price": 300},
                        # {"name": "Кража денег", "count": 0, "price": 200}
                        # {"name": "Казино", "count": 0, "price": 100}
                        # {"name": "Выход из тюрьмы", "count": 0, "price": 100}
                    ]
                    self.players.append(player)
                
                # Запускаем поток для обработки клиента
                thread = threading.Thread(target=self.handle_client, args=(conn, player))
                thread.daemon = True  # Помечаем как daemon-поток
                thread.start()
                
            except socket.error as e:
                if self.running:  # Логируем только если сервер должен работать
                    self.logger.error(f"Ошибка при принятии подключения: {e}")
                break
    
    def handle_client(self, conn, player):
        try:
            self.logger.info(f"Обработка клиента {player.id} ({player.name})")
            self.send_data(conn, player.id)
            while self.running:
                data = self.receive_data(conn)
                if not data:
                    break
                self.logger.debug(f"Получены данные от {player.name}: {data}")
                self.process_client_command(conn, player, data)
        except Exception as e:
            self.logger.error(f"Ошибка обработки клиента {player.id}: {e}\n{traceback.format_exc()}")
        finally:
            with self.lock:
                self.players = [p for p in self.players if p.id != player.id]

                # Освобождаем все клетки игрока
                for cell in self.board_data:
                    if cell["owner"] == player.id:
                        cell["owner"] = None

                if self.game:
                    # Удаляем игрока из списка игровых ID
                    self.game.players = [pid for pid in self.game.players if pid != player.id]

                    # Если сейчас был его ход — переходим к следующему
                    if self.game.current_player == player.id:
                        if player.must_resolve_tile:
                            self.events.append("Сначала завершите взаимодействие с клеткой.")
                            return
                        # Найти следующего активного игрока
                        remaining_ids = [p.id for p in self.players if not p.bankrupt and not p.is_spectator]
                        if remaining_ids:
                            self.game.current_player = remaining_ids[0]
                            self.game.next_turn(self.players)
                            if self.game.next_circle:
                                self.decrement_zalogs()
                                self.game.next_circle = False
                            self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                        else:
                            self.events.append("Нет активных игроков для продолжения игры")

                    # Проверка: остался один активный игрок
                    active_players = [p for p in self.players if not p.bankrupt and not p.is_spectator]
                    if len(active_players) == 1:
                        self.game.winner = active_players[0].id
                        self.events.append(f"Победитель: {active_players[0].name}")
                        self.check_game_end()

            self.broadcast_game_state()
    
    def receive_data(self, conn):
        """Получение данных от клиента с таймаутом"""
        try:
            ready = select.select([conn], [], [], 0.1)  # 100мс таймаут
            size_data = conn.recv(4)
            if not size_data:
                return None
            data_size = struct.unpack('!I', size_data)[0]
            received_data = b""
            while len(received_data) < data_size:
                packet = conn.recv(min(4096, data_size - len(received_data)))
                if not packet:
                    return None
                received_data += packet
            return pickle.loads(received_data)
        except Exception as e:
            self.logger.warning(f"Ошибка при получении данных: {e}")
            return None
    
    def send_data(self, conn, data):
        """Отправка данных клиенту"""
        try:
            # Сериализация данных и отправка их размера перед основными данными
            serialized_data = pickle.dumps(data)
            conn.send(struct.pack('!I', len(serialized_data)))
            conn.send(serialized_data)
        except socket.error as e:
            print(f"Ошибка отправки данных: {e}")
    
    def process_client_command(self, conn, player, data):
        """Обработка команд от клиента"""
        command = data.get("command")
        if self.last_dice_result:
            self.last_dice_result["animation_dice"] = False
        with self.lock:
            if command == "update_player":
                # Обновление данных игрока (имя, цвет, готовность)
                player.name = data.get("name", player.name)
                player.color = data.get("color", player.color)
                player.is_ready = data.get("is_ready", player.is_ready)
                host_player = next((p for p in sorted(self.players, key=lambda p: p.id) if not p.is_spectator), None)
                if host_player and host_player.id == player.id:
                    self.is_mode = data.get("is_mode", False)
                
                # Проверяем, можно ли начать игру
                if all(p.is_ready for p in self.players) and len(self.players) >= 2 and (not self.game):
                    print(f"начинаем игру:")
                    self.start_game()
                
            elif command == "roll_dice" and self.game and self.game.current_player == player.id:
                if player.must_resolve_tile:
                            self.events.append("Сначала завершите взаимодействие с клеткой.")
                            return
                # Бросок кубиков
                self.dice1 = random.randint(1, 6)
                self.dice2 = random.randint(1, 6)
                total_roll = self.dice1 + self.dice2
                self.last_dice_result = {
                    "player_id": player.id,
                    "value": total_roll,
                    "dice1": self.dice1,
                    "dice2": self.dice2,
                    "animation": True,
                    "animation_dice": True
                }
                self.events.append(f"{player.name} выбросил {self.dice1} и {self.dice2}")
                if (self.roll_dice_count == 2 and self.dice1 == self.dice2 and (not player.in_jail)):
                        player.position = next(i for i, c in enumerate(self.board_data) if c["type"] == "jail")
                        player.in_jail = True
                        self.events.append(f"{player.name} отправлен в тюрьму!")
                        self.game.next_turn(self.players)
                        if self.game.next_circle:
                                self.decrement_zalogs()
                                self.game.next_circle = False
                        self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                        self.roll_dice_count = 0
                elif (player.in_jail and self.dice1 == self.dice2):    
                    player.in_jail = False
                    self.events.append(f"{player.name} выходит из тюрьмы")
                    self.roll_dice_count = 0
                    self.move_player(player, self.dice1 + self.dice2)
                else:
                    self.move_player(player, self.dice1 + self.dice2)
                
            elif command == "use_ability":
                ability_name = data.get("ability")
                value = data.get("value")
                player_abilities = self.abilities_by_player.get(player.id, [])
                for ab in player_abilities:
                    if ab["name"] == ability_name and ab["count"] > 0:
                        if ability_name == "Телепорт" and isinstance(value, int):
                            if value>0 and value<13:
                                ab["count"] -= 1
                                self.events.append(f"{player.name} использует способность: {ability_name}")
                                self.dice1 = value
                                self.dice2 = 0
                                total_roll = self.dice1 + self.dice2
                                self.last_dice_result = {
                                    "player_id": player.id,
                                    "value": total_roll,
                                    "dice1": self.dice1,
                                    "dice2": self.dice2,
                                    "animation": True,
                                    "animation_dice": False
                                }
                                self.move_player(player, self.dice1 + self.dice2)
                            else:
                                self.events.append(f"{player.name}, значение должно быть от 1 до 12")

                        # обработка эффектов
                        
                        # ... добавь другие эффекты здесь ...
                # self.broadcast_game_state()

            elif command == "buy_ability":
                ability_name = data.get("ability")
                player_abilities = self.abilities_by_player.get(player.id, [])
                for ab in player_abilities:
                    if ab["name"] == ability_name:
                        if player.money >= ab["price"]:
                            ab["count"] += 1
                            player.money -= ab["price"]
                            self.events.append(f"{player.name} купил способность: {ability_name}")
                        else:
                            self.events.append(f"{player.name} нехватает денег на способность: {ability_name}")
                # self.broadcast_game_state()

            elif command == "bid" and self.game:
                # Участие в аукционе
                self.process_bid(player, data.get("amount", 0))
                
            elif command == "pass_auction" and self.game:
                # Пропуск аукциона
                try:
                    self.process_pass(player)
                except Exception as e:
                    self.logger.error(f"Ошибка в process_pass для игрока {player.id}: {e}")
                
            elif command == "mortgage" and self.game:
                # Залог собственности
                self.mortgage_property(player, data.get("property_index"))
                
            elif command == "unmortgage" and self.game:
                # Выкуп собственности из залога
                self.unmortgage_property(player, data.get("property_index"))
                
            elif command == "upgrade_property" and self.game:
                # Улучшение собственности
                self.upgrade_property(player, data.get("property_index"))
                
            elif command == "downgrade_property" and self.game:
                # Продажа улучшения
                self.downgrade_property(player, data.get("property_index"))
                
            elif command == "propose_trade" and self.game:
                # Предложение сделки
                self.propose_trade(player, data)
                
            elif command == "respond_trade" and self.game and hasattr(self, 'trade_offer'):
                # Ответ на предложение сделки
                accepted = data.get("accept")
                self.process_trade_response(player, data.get("accept", False))

            elif command == "respond_property_choice":
                action = data.get("action")
                prop_index = data.get("property_index")
                cell = self.board_data[prop_index]

                # Проверка: нет ли активного аукциона
                if hasattr(self, 'auction') and self.auction is not None:
                    self.events.append("Сначала завершите аукцион!")
                    return

                if self.awaiting_property_decision and self.awaiting_property_decision["player_id"] == player.id:
                    casino_decision = None
                    jail_decision = False
                    if action == "buy":
                        self.buy_property(player)
                        self.awaiting_property_decision = None
                        player.must_resolve_tile = False

                    elif action == "auction":
                        if cell["type"] not in ["property", "cars", "utility"]:
                            self.events.append(f"Аукцион невозможен на клетке типа {cell['type']}")
                            return
                        self.events.append(f"{player.name} отказался от покупки {cell['name']} — аукцион")
                        self.start_auction(player)
                        return

                    elif action == "quest_tax":
                        if self.awaiting_property_decision["type"] == "quest":
                            tax = self.awaiting_property_decision["reward"]
                            player.money -= tax

                            # Получаем список других активных игроков
                            other_players = [p for p in self.players if p.id != player.id and not p.is_spectator]
                            if other_players:
                                portion = tax // (len(other_players) + 1)
                                self.bank += portion + (tax % (len(other_players) + 1))
                                self.events.append(f"Банк пополнен на {portion + (tax % (len(other_players) + 1))}$.")
                                for p in other_players:
                                    p.money += portion
                                self.events.append(f"{player.name} заплатил за ошибку {tax}$, по {portion}$ досталось остальным игрокам.")
                            else:
                                self.bank += tax
                                self.events.append(f"{player.name} заплатил за ошибку {tax}$ (все ушло в банк).")

                        elif self.awaiting_property_decision["type"] == "bonus_for_upgrades":
                            tax = self.awaiting_property_decision["reward"]
                            player.money -= tax
                            self.bank += (tax // 50) * 25
                            self.events.append(f"{player.name} заплатил за прокачку {tax}$. Банк пополнен на {(tax // 50) * 25}$ ")

                        elif self.awaiting_property_decision["type"] == "donate_to_bank":
                            tax = self.awaiting_property_decision["reward"]
                            player.money -= tax
                            self.bank += tax
                            self.events.append(f"{player.name} пожертвовал в Банк {tax}$ ")

                        elif self.awaiting_property_decision["type"] == "share_with_others":
                            tax = self.awaiting_property_decision["reward"]
                            others = [p for p in self.players if p.id != player.id and not p.is_spectator]
                            if others:
                                per_player = round(tax / len(others))
                                for p in others:
                                    p.money += per_player
                                player.money -= tax
                            self.events.append(f"{player.name} дал всем денег на развитие")

                        elif self.awaiting_property_decision["type"] == "exit_jail":
                            tax = self.awaiting_property_decision["reward"]
                            player.money -= tax
                            self.bank += tax
                            self.events.append(f"{player.name} Заплатил за выход из тюрьмы {tax}$")
                            player.in_jail = False
                            player.jail_turns = 0
                            jail_decision = True
                            self.awaiting_property_decision = None
                            player.must_resolve_tile = False
                            self.move_player(player, self.dice1 + self.dice2)

                        else:
                            self.events.append(f"{player.name} Что ты сделал?????!!!!!!!!!!!!!!!!!!!!!!")
                            
                        self.awaiting_property_decision = None
                        player.must_resolve_tile = False


                    elif action == "pay_tax":
                        tax = cell["price"]
                        player.money -= tax
                        self.events.append(f"{player.name} заплатил налог: {tax}$")
                        self.bank += tax
                        self.awaiting_property_decision = None
                        player.must_resolve_tile = False

                    elif action == "casino_bet":
                        amount = 0
                        winnings = data.get("bet", 0)
                        rounds = self.awaiting_property_decision["round"]
                        if rounds == 1:
                            amount = data.get("bet", 0)
                            player.money -= amount
                        ########!!!!!!!!!!!!!!!!!!!!!!!! придумать казино
                        win = random.choice([False, True])
                        if win:
                            if rounds == 1:
                                winnings = amount * 2
                                self.events.append(f"{player.name} поставил {amount} и выиграл {winnings} в казино! Порадуйтесь")
                            else:
                                winnings = winnings * 2
                                self.events.append(f"{player.name} рискнул еще раз и выиграл {winnings} в казино!")
                            rounds += 1

                            if rounds > 3:
                                player.money += winnings
                                self.events.append(f"{player.name} забирает {winnings} после 3 раундов!")
                                casino_decision = False
                                self.awaiting_property_decision = None
                                player.must_resolve_tile = False
                            else:
                                self.events.append(f"{player.name}, хотите продолжить или заберете {winnings}?")
                                casino_decision = True
                                player.must_resolve_tile = True
                                self.awaiting_property_decision = {
                                    "player_id": player.id,
                                    "property_index": player.position,
                                    "cell": cell,
                                    "type": "casino",
                                    "round": rounds,
                                    "winnings": winnings
                                }
                        else:
                            if rounds == 1:
                                self.events.append(f"{player.name} проиграл ставку {amount}! ")
                            else:
                                self.events.append(f"{player.name} проиграл ставку {amount}, хотя мог забрать {winnings}!")
                            casino_decision = False
                            self.awaiting_property_decision = None
                            player.must_resolve_tile = False

                    elif action == "casino_take":
                        if self.awaiting_property_decision["winnings"] == 0:
                            self.events.append(f"{player.name} не рискнул")
                        else:
                            winnings = self.awaiting_property_decision["winnings"]
                            player.money += winnings
                            self.events.append(f"{player.name} забрал {winnings}$ из казино.")
                        self.awaiting_property_decision = None
                        player.must_resolve_tile = False

                    elif action == "rent":
                        self.pay_rent(player, cell, self.last_dice_result["value"])
                        self.awaiting_property_decision = None
                        player.must_resolve_tile = False
                    elif action == "bankrot":
                        self.declare_bankruptcy(player)

                    elif action == "answer_quest":
                        user_answer = data.get("answer", "").strip().lower()
                        user_answer = f"{float(user_answer):.1f}" if user_answer != "" else 1001.0
                        correct = self.awaiting_property_decision["answer"].strip().lower()
                        reward = self.awaiting_property_decision["reward"]

                        if user_answer == correct:
                            if self.awaiting_property_decision["type"] == "jail_challenge":
                                self.events.append(f"{player.name} ответил правильно и освобождается из тюрьмы")
                                player.in_jail = False
                                player.jail_turns = 0
                                jail_decision = True
                                self.awaiting_property_decision = None
                                player.must_resolve_tile = False
                                self.move_player(player, self.dice1 + self.dice2)
                            else:
                                player.money += reward
                                self.events.append(f"{player.name} ответил правильно и получил {reward}$")
                                self.awaiting_property_decision = None
                                player.must_resolve_tile = False
                        else:
                            if self.awaiting_property_decision["type"] == "jail_challenge":
                                self.events.append(f"{player.name} остается в тюрьме. Верный ответ: {correct}.")
                                self.awaiting_property_decision = None
                                player.must_resolve_tile = False
                                jail_decision = True
                                self.game.next_turn(self.players)
                                if self.game.next_circle:
                                    self.decrement_zalogs()
                                    self.game.next_circle = False
                                self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                                self.roll_dice_count = 0
                            else:
                                self.events.append(f"{player.name} ошибся! Верный ответ: {correct}. Оплата {reward}$")
                                self.awaiting_property_decision["wrong"] = True

                    if not casino_decision and self.awaiting_property_decision == None and not jail_decision:
                        # Завершаем ожидание
                        self.awaiting_property_decision = None
                        player.must_resolve_tile = False 
                        if self.dice1 != self.dice2:
                            self.game.next_turn(self.players)
                            if self.game.next_circle:
                                self.decrement_zalogs()
                                self.game.next_circle = False
                            self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                            self.roll_dice_count = 0
                        else:
                            self.roll_dice_count += 1
                            self.events.append(f"{player.name} ходит еще раз")
            
            # Отправляем обновленное состояние всем клиентам
            self.broadcast_game_state()

    def start_game(self):
        """Начало новой игры"""
        player_ids = [p.id for p in self.players if not p.is_spectator]
        first_player = random.choice(player_ids)
        self.game = Game(player_ids, first_player)
        self.events.append("Игра началась!")
        self.events.append(f"Первым ходит {self.get_player_by_id(first_player).name}")
    
    def move_player(self, player, steps):
        """Перемещение игрока на поле"""
        # По умолчанию — требуется обработка действия

        if player.in_jail:
            # Логика для игрока в тюрьме
            player.jail_turns += 1
            if player.jail_turns >= 3:
                ###### не выбросил дубль должен заплатить
                reward = 100
                cell = self.board_data[player.position]
                self.events.append(f"{player.name} плати за выход")
                player.must_resolve_tile = True
                self.awaiting_property_decision = {
                    "player_id": player.id,
                    "property_index": player.position,
                    "cell": cell,
                    "type": "exit_jail",
                    "question": "1",
                    "answer": "2",
                    "reward": reward,
                    "wrong": True
                }
                return
            else:
                cell = self.board_data[player.position]
                question = self.generate_math_question()
                self.events.append(f"{player.name} может выйти если ответит на вопрос: {question['question']}")
                player.must_resolve_tile = True
                self.awaiting_property_decision = {
                    "player_id": player.id,
                    "property_index": player.position,
                    "cell": cell,
                    "type": "jail_challenge",
                    "question": question["question"],
                    "answer": question["answer"],
                    "reward": question["reward"],
                    "wrong": False
                }
                return     
        new_position = (player.position + steps) % len(self.board_data)
        if player.position > new_position and steps > 0:
            self.events.append(f"{player.name} получает 200 за прохождение круга")
            player.money += 200
        player.position = new_position
        cell = self.board_data[player.position]

        self.events.append(f"{player.name} попадает на поле {cell['name']}")
        if cell["type"] == "start":
            self.events.append(f"{player.name} получает 100 за попадание на старт")
            player.money += 100
            if self.dice1 != self.dice2:
                self.game.next_turn(self.players)
                if self.game.next_circle:
                                self.decrement_zalogs()
                                self.game.next_circle = False
                self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                self.roll_dice_count = 0
            else:
                self.roll_dice_count += 1
                self.events.append(f"{player.name} ходит еще раз")

        elif cell["type"] in ["property", "cars", "utility"]:
            if cell["owner"] is None:
                # Ничего не делаем — клиент предложит купить или аукцион
                self.events.append(f"{player.name} может купить {cell['name']} за ${cell['price']}")
                player.must_resolve_tile = True
                self.awaiting_property_decision = {
                    "player_id": player.id,
                    "property_index": player.position,
                    "cell": cell
                }
            elif cell["owner"] != player.id and cell["Zalog"] == None:
                owner = self.get_player_by_id(cell["owner"])
                rent = cell["rent"]
                if cell["type"] == "utility":
                    rent = cell["rent"] * steps
                player.must_resolve_tile = True
                self.events.append(f"{player.name} должен заплатить {rent} игроку {owner.name}")
                self.awaiting_property_decision = {
                    "player_id": player.id,
                    "property_index": player.position,
                    "cell": cell
                }
            else:
                if self.dice1 != self.dice2:
                    self.game.next_turn(self.players)
                    if self.game.next_circle:
                                self.decrement_zalogs()
                                self.game.next_circle = False
                    self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                    self.roll_dice_count = 0
                else:
                    self.roll_dice_count += 1
                    self.events.append(f"{player.name} ходит еще раз")
        
        elif cell["type"] == "quest":
            event_type, specific_event = self.generate_random_quest_event()

            if specific_event == "math_question":
                question_data = self.generate_math_question()
                self.events.append(f"{player.name} получил задание: {question_data['question']}")
                player.must_resolve_tile = True
                self.awaiting_property_decision = {
                    "player_id": player.id,
                    "property_index": player.position,
                    "cell": cell,
                    "type": "quest",
                    "question": question_data["question"],
                    "answer": question_data["answer"],
                    "reward": question_data["reward"],
                    "wrong": False
                }

            elif specific_event == "free_upgrade":
                # Если есть хотя бы одна property
                upgradable = [i for i, cell in enumerate(self.board_data)
                              if cell.get("owner") == player.id and cell["type"] == "property" and cell["Zalog"] is None and cell["level"] < 5]
                if upgradable:
                    cell_index = random.choice(upgradable)
                    cell = self.board_data[cell_index]
                    cell["level"] = min(cell["level"] + 1, 5)
                    self.events.append(f"{player.name} бесплатно улучшил клетку {cell['name']}")
                else:
                    self.events.append(f"{player.name} не получил бесплатного улучшения")

                if self.dice1 != self.dice2:
                    self.game.next_turn(self.players)
                    if self.game.next_circle:
                                    self.decrement_zalogs()
                                    self.game.next_circle = False
                    self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                    self.roll_dice_count = 0
                else:
                    self.roll_dice_count += 1
                    self.events.append(f"{player.name} ходит еще раз")

            elif specific_event == "fire":
                owned = [i for i, cell in enumerate(self.board_data)
                         if cell.get("owner") == player.id and cell["type"] in ["property", "cars", "utility"] and cell["Zalog"] is None]
                if owned:
                    index = random.choice(owned)
                    cell = self.board_data[index]
                    if cell["level"] > 0:
                        cell["level"] -= 1
                        self.bank += round(cell['price']/2)
                        cell["rent"] = cell["price"]*RENT_MULTIPLIERS[cell["level"]]
                        self.events.append(f"На клетке {cell['name']} был пожар! Уровень снижен.")
                    elif cell["Zalog"] is None:
                        cell["Zalog"] = 15
                        self.events.append(f"{cell['name']} был заложен из-за пожара.")
                else:
                    self.events.append(f"{player.name} ничего не имеет")
                if self.dice1 != self.dice2:
                    self.game.next_turn(self.players)
                    if self.game.next_circle:
                                    self.decrement_zalogs()
                                    self.game.next_circle = False
                    self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                    self.roll_dice_count = 0
                else:
                    self.roll_dice_count += 1
                    self.events.append(f"{player.name} ходит еще раз")

            elif specific_event == "jump_to_utility": ####cars
                current_pos = player.position
                for i in range(1, len(self.board_data)):
                    check_index = (current_pos + i) % len(self.board_data)
                    if self.board_data[check_index]["type"] == "cars":
                        self.events.append(f"{player.name} прыгнул на ближайшую cars: {self.board_data[check_index]['name']}")
                        self.move_player(player, i)
                        break

            elif specific_event == "stumble_steps":
                direction = random.choice([-1, 1])
                steps = random.randint(1, 6)
                new_pos = (player.position + direction * steps) % len(self.board_data)
                self.events.append(f"{player.name} загулял и переместился на {steps} клеток {'назад' if direction == -1 else 'вперёд'}")
                self.move_player(player, direction * steps)

            elif specific_event == "bonus_from_bank":
                bonus = self.bank // 4
                player.money += bonus
                self.bank -= bonus
                self.events.append(f"{player.name} получил {bonus}$ от банка")
                if self.dice1 != self.dice2:
                    self.game.next_turn(self.players)
                    if self.game.next_circle:
                                    self.decrement_zalogs()
                                    self.game.next_circle = False
                    self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                    self.roll_dice_count = 0
                else:
                    self.roll_dice_count += 1
                    self.events.append(f"{player.name} ходит еще раз")

            elif specific_event == "old_insurance":
                zalogged = sum(1 for cell in self.board_data if cell.get("owner") == player.id and cell.get("Zalog") is not None)
                reward = zalogged * 25
                player.money += reward
                self.events.append(f"{player.name} получил страховку: {reward}$ за {zalogged} заложенных клеток")
                if self.dice1 != self.dice2:
                    self.game.next_turn(self.players)
                    if self.game.next_circle:
                                    self.decrement_zalogs()
                                    self.game.next_circle = False
                    self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                    self.roll_dice_count = 0
                else:
                    self.roll_dice_count += 1
                    self.events.append(f"{player.name} ходит еще раз")

            elif specific_event == "bonus_for_upgrades":
                upgraded = sum(1 for cell in self.board_data if cell.get("owner") == player.id and cell.get("level", 0) > 0)
                reward = upgraded * 50
                if reward>0:
                    self.events.append(f"{player.name} должен заплатить: {reward}$ за {upgraded} улучшений")
                    player.must_resolve_tile = True
                    self.awaiting_property_decision = {
                        "player_id": player.id,
                        "property_index": player.position,
                        "cell": cell,
                        "type": "bonus_for_upgrades",
                        "question": "1",
                        "answer": "2",
                        "reward": reward,
                        "wrong": True
                    }
                else:
                    self.events.append(f"{player.name} прокачай что-нибудь")
                    if self.dice1 != self.dice2:
                        self.game.next_turn(self.players)
                        if self.game.next_circle:
                                        self.decrement_zalogs()
                                        self.game.next_circle = False
                        self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                        self.roll_dice_count = 0
                    else:
                        self.roll_dice_count += 1
                        self.events.append(f"{player.name} ходит еще раз")

            elif specific_event == "donate_to_bank":
                amount = max(100, (player.money//50)*10)
                self.events.append(f"{player.name} должен пожертвовал {amount}$ в банк")
                player.must_resolve_tile = True
                self.awaiting_property_decision = {
                    "player_id": player.id,
                    "property_index": player.position,
                    "cell": cell,
                    "type": "donate_to_bank",
                    "question": "1",
                    "answer": "2",
                    "reward": amount,
                    "wrong": True
                }


            elif specific_event == "share_with_others":
                per_player = max(50, (player.money//500)*25)
                others = [p for p in self.players if p.id != player.id and not p.is_spectator]
                if others:
                    total = per_player * len(others)
                    self.events.append(f"{player.name} очень хочет поделиться со всеми, каждому игроку по {per_player}$")
                    player.must_resolve_tile = True
                    self.awaiting_property_decision = {
                        "player_id": player.id,
                        "property_index": player.position,
                        "cell": cell,
                        "type": "share_with_others",
                        "question": "1",
                        "answer": "2",
                        "reward": total,
                        "wrong": True
                    }
                else:
                    self.events.append(f"{player.name} никого нет?")


        elif cell["type"] == "tax":
            tax = cell["price"]
            self.events.append(f"{player.name} должен заплатить {tax} за налог")
            player.must_resolve_tile = True
            self.awaiting_property_decision = {
                    "player_id": player.id,
                    "property_index": player.position,
                    "cell": cell
                }

        elif cell["type"] == "casino":
            self.events.append(f"{player.name} зашел в казино! Сколько он там оставит?")
            player.must_resolve_tile = True
            self.awaiting_property_decision = {
                "player_id": player.id,
                "property_index": player.position,
                "cell": cell,
                "type": "casino",
                "round": 1,
                "winnings": 0
            }

        elif cell["type"] == "gotojail":
            self.events.append(f"{player.name} отправлен в тюрьму за сопротивление без сопротивления!")
            player.position = next(i for i, c in enumerate(self.board_data) if c["type"] == "jail")
            player.in_jail = True
            player.jail_turns = 0
            self.game.next_turn(self.players)
            if self.game.next_circle:
                                self.decrement_zalogs()
                                self.game.next_circle = False
            self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
            self.roll_dice_count = 0
            return

        elif cell["type"] == "jail":
            self.events.append(f"{player.name} посетил кое-кого в тьрьме! Посиди, поговори")
            self.game.next_turn(self.players)
            if self.game.next_circle:
                                self.decrement_zalogs()
                                self.game.next_circle = False
            self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
            self.roll_dice_count = 0

        # После обработки клетки сразу сообщаем клиенту
        self.broadcast_game_state()

    def generate_random_operand(self):
        values = [i for i in range(-15, 15) if i != 0]
        return random.choice(values)

    def generate_expression(self, depth=0, max_depth=3):
        if depth >= max_depth or random.random() < 0.3:
            # Базовое значение или обернутое унарной функцией
            operand = self.generate_random_operand()
            if random.random() < 0.4:
                template, _, _ = random.choice(self.UNARY_OPS)
                return template.format(x=operand)
            else:
                return operand

        # Генерация бинарного выражения
        left = self.generate_expression(depth + 1, max_depth)
        right = self.generate_expression(depth + 1, max_depth)
        op, _, _ = random.choice(self.BINARY_OPS)
        return f"({left} {op} {right})"

    def safe_eval(self, expr):
        try:
            return eval(expr, {"__builtins__": None, "math": math})
        except Exception:
            return None

    def generate_math_question(self):
        for _ in range(100):  # ограничиваем попытки, чтобы не застревать
            expr = self.generate_expression(max_depth=random.randint(3, 4))
            result = self.safe_eval(expr)

            if result is None:
                continue

            try:
                result = round(result, 1)
            except Exception:
                continue

            if abs(result) > 1000:
                continue

            if abs(result) == 0:
                result = abs(result)
            # Пример простого подсчета сложности
            difficulty = expr.count('+') + expr.count('-') + \
                         expr.count('*') * 2 + expr.count('/') * 2 + \
                         expr.count('%') * 3 + expr.count('**') * 3 + \
                         expr.count('abs') + expr.count('sqrt') * 4
            if (difficulty < 5 or difficulty > 10):
                continue
            reward = min(round((10 + difficulty * 15)/2), 100)
            print(f"question: {expr}, answer: {result:.1f}, reward: {reward}, difficulty: {difficulty}")
            return {
                "question": f"Сколько будет {expr}?",
                "answer": f"{result:.1f}",
                "reward": reward
            }

        # 💡 Если не удалось сгенерировать сложный вопрос — выдаём запасной
        expr = "2 + 2"
        result = 4
        reward = 10
        print("⚠️ Использован запасной вопрос.")
        return {
            "question": f"Сколько будет {expr}?",
            "answer": f"{result:.1f}",
            "reward": reward
        }

    def generate_random_quest_event(self):
        x = random.randint(1,10)
        
        if x < 3:
            event_type = "task"
        elif x < 5:
            event_type = "upgrade"
        elif x < 7:
            event_type = "move"
        elif x < 9:
            event_type = "bonus"
        else:
            event_type = "penalty"

        QUEST_EVENTS = {
            "task": [
                "math_question"
            ],
            "upgrade": [
                # "free_upgrade",    # «Торгаш»
                "fire"             # «Пожар»
            ],
            "move": [
                "jump_to_utility", # «Прыжок через поле»
                "stumble_steps"    # «Ты загулял»
            ],
            "bonus": [
                "bonus_from_bank",         # «Банк»
                "old_insurance",           # «Старая страховка»
            ],
            "penalty": [
                "bonus_for_upgrades",      # «"Премия"»
                "donate_to_bank",          # «Благотворительность»
                "share_with_others"        # «Поделись с бедными»
            ]
        }

        specific_event = random.choice(QUEST_EVENTS[event_type])
        return event_type, specific_event

    def buy_property(self, player):
        """Покупка собственности игроком"""
        cell = self.board_data[player.position]
            
        if player.money >= cell["price"]:
            player.money -= cell["price"]
            cell["owner"] = player.id
            cell["color_owner"] = player.color
            player.properties.append(player.position)
            self.events.append(f"{player.name} покупает {cell['name']} за ${cell['price']}")
        else:
            # Если у игрока недостаточно денег, начинаем аукцион
            self.events.append(f"{player.name} недостаточно средств для покупки {cell['name']} за ${cell['price']}")
    
    def pay_rent(self, player, cell, value):
        """Оплата аренды за собственность"""
        owner = self.get_player_by_id(cell["owner"])
        
        if owner.bankrupt or cell["Zalog"] is not None:
            return  # Не платим, если владелец обанкротился или собственность в залоге
                
        rent = cell["rent"]
        if cell["type"] == "utility":
            rent = cell["rent"]*value
        
        player.money -= rent
        owner.money += rent
        self.events.append(f"{player.name} платит {owner.name} {rent}$ за аренду {cell['name']}")
    
    def start_auction(self, player):
        """Начало аукциона за собственность"""
        cell = self.board_data[player.position]
        self.auction = {
            "property_index": player.position,
            "cell": cell,
            "current_bid": cell["price"] - 1,
            "leader_id": None,
            "active_bidders": [
                p.id for p in self.players if not p.bankrupt and not p.is_spectator and p.id != player.id
            ],
            "bid_history": {},
            "already_bid": set(),
            "turn_index": 0,
            "starter_id": player.id,
            "awaiting_bidder": None  # Добавим это поле для отслеживания текущего участника аукциона
        }
        
        # Set the first bidder
        if self.auction["active_bidders"]:
            self.auction["awaiting_bidder"] = self.auction["active_bidders"][0]
            self.events.append(f"Аукцион за {cell['name']} начался! Минимальная ставка: ${self.auction['current_bid'] + 1}")
            self.events.append(f"Ход в аукционе: {self.get_player_by_id(self.auction['awaiting_bidder']).name}")

            self.awaiting_property_decision = {
                                    "player_id": self.auction["awaiting_bidder"],
                                    "property_index": self.auction["property_index"],
                                    "cell": self.auction["cell"],
                                    "type": "auction"
            }
            player.must_resolve_tile = False

        else:
            # No other players to participate in auction
            self.events.append(f"Некому участвовать в аукционе за {cell['name']}")
            self.awaiting_property_decision = None
            player.must_resolve_tile = False
            # End auction and move to next player
            if self.dice1 != self.dice2:
                self.game.next_turn(self.players)
                if self.game.next_circle:
                                self.decrement_zalogs()
                                self.game.next_circle = False
                self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                self.roll_dice_count = 0
            else:
                self.roll_dice_count += 1
                self.events.append(f"{player.name} ходит еще раз")
            self.auction = None
            
        self.broadcast_game_state()
    
    def process_bid(self, player, amount):
        """Обработка ставки на аукционе"""
        if not self.auction or player.id != self.auction.get("awaiting_bidder"):
            return

        self.auction["current_bid"] = amount
        self.auction["leader_id"] = player.id
        self.auction["bid_history"][player.id] = amount
        self.auction["already_bid"].add(player.id)
        self.events.append(f"{player.name} поставил ${amount}!")
        self._next_auction_turn(player)
        self.broadcast_game_state()

    def process_pass(self, player):
        if not self.auction or player.id != self.auction.get("awaiting_bidder"):
            return

        if player.id in self.auction["bid_history"]:
            penalty = self.auction["bid_history"][player.id] // 10
            player.money -= penalty
            self.events.append(f"{player.name} выходит из аукциона и теряет ${penalty}")
        else:
            self.events.append(f"{player.name} отказывается от участия в аукционе")

        if player.id in self.auction["active_bidders"]:
            self.auction["active_bidders"].remove(player.id)

        if len(self.auction["active_bidders"]) == 1 and not self.auction['bid_history']:
            self._next_auction_turn(player)
        else:
            self.end_auction(player)

    def end_auction(self, player):
        """Игрок пропускает аукцион"""
        if not self.auction or player.id != self.auction.get("awaiting_bidder"):
            return

        if len(self.auction["active_bidders"]) == 1:
            # One bidder left - they win
            winner_id = self.auction["active_bidders"][0]
            winner = self.get_player_by_id(winner_id)
            cell = self.auction["cell"]

            # If leader was set, use their bid, otherwise use minimum bid
            if self.auction["leader_id"] is not None:
                final_bid = self.auction["current_bid"]
            else:
                final_bid = cell["price"]
            
            winner.money -= final_bid
            cell["owner"] = winner.id
            cell["color_owner"] = winner.color
            winner.properties.append(self.auction["property_index"])
            self.events.append(f"{winner.name} выигрывает аукцион и покупает {cell['name']} за ${final_bid}")

            # End auction and move to next player's turn
            starter_id = self.auction["starter_id"]
            self.auction = None
            player = self.get_player_by_id(starter_id)

            self.awaiting_property_decision = None
            player.must_resolve_tile = False

            if self.dice1 != self.dice2:
                self.game.next_turn(self.players)
                if self.game.next_circle:
                                self.decrement_zalogs()
                                self.game.next_circle = False
                self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                self.roll_dice_count = 0
            else:
                self.roll_dice_count += 1
                self.events.append(f"{player.name} ходит еще раз")

        elif len(self.auction["active_bidders"]) == 0:
            # All players passed - no one gets the property
            self.events.append("Все игроки отказались — никто не получает клетку")
            
            # End auction and move to next player's turn
            starter_id = self.auction["starter_id"]
            self.auction = None

            self.awaiting_property_decision = None
            player.must_resolve_tile = False

            if self.dice1 != self.dice2:
                self.game.next_turn(self.players)
                if self.game.next_circle:
                                self.decrement_zalogs()
                                self.game.next_circle = False
                self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
                self.roll_dice_count = 0
            else:
                self.roll_dice_count += 1
                self.events.append(f"{player.name} ходит еще раз")
        else:
            # Continue to next bidder
            self._next_auction_turn()
            
        self.broadcast_game_state()
    
    def get_next_player_id(self, current_id):
        ids = [p.id for p in self.players if not p.bankrupt and not p.is_spectator]
        if current_id not in ids:
            return ids[0]
        index = ids.index(current_id)
        return ids[(index + 1) % len(ids)]

    def _next_auction_turn(self, player):
        """Переход хода в аукционе к следующему участнику"""
        if not self.auction or not self.auction["active_bidders"]:
            return
        if len(self.auction["active_bidders"]) < 2 and self.auction['bid_history']:
            print("go")
            self.end_auction(player)
            return
        # Find next active bidder
        current_idx = 0
        if self.auction["awaiting_bidder"] in self.auction["active_bidders"]:
            current_idx = self.auction["active_bidders"].index(self.auction["awaiting_bidder"])
        
        next_idx = (current_idx + 1) % len(self.auction["active_bidders"])
        self.auction["awaiting_bidder"] = self.auction["active_bidders"][next_idx]
        
        # Update events
        next_player = self.get_player_by_id(self.auction["awaiting_bidder"])
        if next_player:
            self.events.append(f"Ход в аукционе: {next_player.name}, текущая ставка: ${self.auction['current_bid']}")

    def mortgage_property(self, player, property_index):
        """Залог собственности"""
        if property_index not in player.properties:
            return
            
        cell = self.board_data[property_index]
        
        if cell["Zalog"] is not None:
            return  # Уже в залоге
            
        mortgage_value = cell["price"] / 2
        player.money += mortgage_value
        cell["Zalog"] = 15  # 15 ходов на выкуп
        self.events.append(f"{player.name} закладывает {cell['name']}")
    
    def unmortgage_property(self, player, property_index):
        """Выкуп собственности из залога"""
        if property_index not in player.properties:
            return
            
        cell = self.board_data[property_index]
        
        if cell["Zalog"] is None:
            return  # Не в залоге
            
        unmortgage_cost = int(cell["price"] * 0.6)  # 120% от залоговой стоимости
        player.money -= unmortgage_cost
        cell["Zalog"] = None
        self.events.append(f"{player.name} выкупает {cell['name']} за ${unmortgage_cost}")
    
    def upgrade_property(self, player, property_index):
        """Улучшение собственности"""
        if property_index not in player.properties:
            return
            
        cell = self.board_data[property_index]
        
        if cell["type"] != "property" or cell["Zalog"] is not None:
            return
            
        upgrade_cost = cell["price"] / 2
        player.money -= upgrade_cost
        cell["level"] += 1
        cell["rent"] = cell["price"]*RENT_MULTIPLIERS[cell["level"]]
        self.events.append(f"{player.name} улучшает {cell['name']} до уровня {cell['level']}")
    
    def downgrade_property(self, player, property_index):
        """Продажа улучшения собственности"""
        if property_index not in player.properties:
            return
            
        cell = self.board_data[property_index]
        
        if cell["type"] != "property" or cell["level"] == 0 or cell["Zalog"] is not None:
            return
            
        sell_value = cell["price"] / 2
        player.money += sell_value
        cell["level"] -= 1
        cell["rent"] = cell["price"]*RENT_MULTIPLIERS[cell["level"]]
        self.events.append(f"{player.name} понижает уровень {cell['name']} до {cell['level']}")
    
    def decrement_zalogs(self):
        """Уменьшает залог у всех клеток, если есть. Обнуляет владение при истечении"""
        self.count_circle += 1
        self.bank += 10
        for cell in self.board_data:
            if cell.get("Zalog") is not None:
                cell["Zalog"] -= 1
                if cell["Zalog"] <= 0:
                    prev_owner = cell["owner"]
                    cell["Zalog"] = None
                    cell["owner"] = None
                    cell["color_owner"] = None
                    self.events.append(f"{self.get_player_by_id(prev_owner).name} теряет предприятие: {cell['name']}")

        if (self.count_circle % 10) == 0:
            self.bank = round(self.bank * 1.5)

            bonus = 0
            player_values = []
            for player in self.players:
                if player.bankrupt:
                    continue
                wasmoney = player.money
                total = 0
                for i in player.properties:
                    cell = self.board_data[i]
                    if cell["type"] == "property":
                        if cell["Zalog"] is None:
                            bonus += round(abs(cell["level"] - 5) * 0.1 * round(cell["price"] / 2))
                        total += cell["level"] * round(cell["price"] / 2)
                    if cell["Zalog"] is None:
                        total += cell["price"]
                    else:
                        total += round(cell["price"] / 2)
                player.money += bonus
                self.events.append(f"{player.name} получает бонус на развитие: {bonus}$")
                
                total += player.money
                self.events.append(f"{player.name} имел {wasmoney}$, теперь имеет {player.money} и всего активов на {total}$")
                if (self.count_circle % 25) == 0:
                    player.money -= total * min((self.count_circle // 25) * 0.05, 0.5)
                    player.money -= (self.count_circle // 25)*200
                    self.bank = round(self.bank * 0.5)
                player_values.append((player, total))

            if (self.count_circle % 25) == 0:
                self.events.append(f"Инфляция")

            if player_values:
                poorest_player, min_value = min(player_values, key=lambda item: item[1])
                bonus = min(self.count_circle // 10 * 100, 500)
                if bonus > self.bank:
                    bonus = self.bank
                    self.events.append(f"Банк маленький")
                poorest_player.money += bonus
                self.bank -= bonus
                self.events.append(f"{poorest_player.name} получает помощь из банка: {bonus}$")

            if self.is_mode:
                self.refresh_board()
        
        self.broadcast_game_state()

    def propose_trade(self, player, trade_data):
        """Предложение сделки между игроками"""
        receiving_id = trade_data.get("receiving_id")
        if receiving_id == player.id:
            return  # Нельзя предложить сделку самому себе
            
        receiving_player = self.get_player_by_id(receiving_id)
        if not receiving_player or receiving_player.bankrupt:
            return 
        self.trade_offer = {
            "offering_id": player.id,
            "receiving_id": receiving_id,
            "offering_property": list(trade_data["properties_offer"]),
            "receiving_property": list(trade_data["properties_request"]),
            "offering_money": trade_data.get("money_offer", 0),
            "receiving_money": trade_data.get("money_request", 0),
            "old_decision": trade_data.get("old_decision", None)
        }

        player.must_resolve_tile = True
        self.awaiting_property_decision = {
            "player_id": player.id,
            "property_index": player.position,
            "type": "trade"
        }
            
        self.events.append(f"{player.name} предлагает сделку {receiving_player.name}")
    
    def process_trade_response(self, player, accepted):
        """Обработка ответа на предложение сделки"""
        if not hasattr(self, 'trade_offer') or player.id != self.trade_offer["receiving_id"]:
            return

        offering_player = self.get_player_by_id(self.trade_offer["offering_id"])
        receiving_player = player

        if accepted:
            # Деньги
            offering_player.money -= self.trade_offer["offering_money"]
            offering_player.money += self.trade_offer["receiving_money"]

            receiving_player.money += self.trade_offer["offering_money"]
            receiving_player.money -= self.trade_offer["receiving_money"]

            # Собственность от предлагающего
            for i, selected in enumerate(self.trade_offer["offering_property"]):
                if selected:
                    offering_player.properties.remove(i)
                    receiving_player.properties.append(i)
                    self.board_data[i]["owner"] = receiving_player.id
                    self.board_data[i]["color_owner"] = receiving_player.color

            # Собственность от получателя
            for i, selected in enumerate(self.trade_offer["receiving_property"]):
                if selected:
                    receiving_player.properties.remove(i)
                    offering_player.properties.append(i)
                    self.board_data[i]["owner"] = offering_player.id
                    self.board_data[i]["color_owner"] = offering_player.color

            self.events.append(f"Сделка между {offering_player.name} и {receiving_player.name} состоялась!"
            )
        else:
            self.events.append(f"{receiving_player.name} отклонил сделку от {offering_player.name}")

        self.awaiting_property_decision = self.trade_offer["old_decision"]
        self.trade_offer = None
        offering_player.must_resolve_tile = False
        self.broadcast_game_state()
    
    def declare_bankruptcy(self, player):
        """Объявление банкротства игрока"""
        # Освобождаем все собственности игрока
        for prop_index in player.properties:
            if self.board_data[prop_index]["type"] == "property":
                player.money += self.board_data[prop_index]["level"]*round(self.board_data[prop_index]["price"]/2)
            if self.board_data[prop_index]["Zalog"] == None:
                player.money += self.board_data[prop_index]["price"]
            else:
                player.money += round(self.board_data[prop_index]["price"]/2)
            self.board_data[prop_index]["owner"] = None
            self.board_data[prop_index]["level"] = 0
            self.board_data[prop_index]["rent"] = self.board_data[prop_index]["price"]//10
            self.board_data[prop_index]["Zalog"] = None
            self.board_data[prop_index]["color_owner"] = None

        if self.awaiting_property_decision["cell"]["owner"] == None:
            self.bank += player.money
        else:
            owner_player = self.get_player_by_id(self.awaiting_property_decision["cell"]["owner"])
            if player.money < self.awaiting_property_decision["cell"]["rent"]:
                owner_player.money += player.money
            else:
                owner_player.money += self.awaiting_property_decision["cell"]["rent"]
                self.bank += player.money - self.awaiting_property_decision["cell"]["rent"]
        player.money = 0

        self.awaiting_property_decision = None
        player.must_resolve_tile = False

        if self.dice1 == self.dice2:
            self.game.next_turn(self.players)
            if self.game.next_circle:
                self.decrement_zalogs()
                self.game.next_circle = False
            self.events.append(f"Ход переходит к {self.get_player_by_id(self.game.current_player).name}")
            self.roll_dice_count = 0
        player.bankrupt = True
        
        player.properties.clear()
        self.events.append(f"{player.name} объявлен банкротом!")

        player.is_spectator = True
        player.id = None  # делает его "анонимным"

        # Проверяем, не закончилась ли игра
        self.check_game_end()
        self.broadcast_game_state()
    
    def check_game_end(self):
        """Проверка условий окончания игры"""
        active_players = [p for p in self.players if not p.bankrupt]
        if len(active_players) == 1:
            self.game.winner = active_players[0].id
            self.events.append(f"{active_players[0].name} побеждает в игре!")
        self.broadcast_game_state()

    
    def get_player_by_id(self, player_id):
        """Получение объекта игрока по ID"""
        return next((p for p in self.players if p.id == player_id), None)
    
    def update_board_rents_and_zalogs(self):
        """Обновляет аренду и состояние залогов всех клеток"""
        for cell in self.board_data:
            owner_id = cell.get("owner")
            if owner_id is not None:
                if cell["type"] == "property":
                    group_cells = [c for c in self.board_data if c.get("category") == cell.get("category")]
                    if all(c.get("owner") == owner_id for c in group_cells) and cell.get("level", 0) == 0:
                        cell["rent"] = cell["price"] * RENT_MULTIPLIERS[0] * 2

                elif cell["type"] == "cars":
                    owner_cells = [c for c in self.board_data if c["type"] == "cars" and c.get("owner") == owner_id]
                    count = len(owner_cells)
                    cell["rent"] = (25+(self.count_circle // 10)*7)*(2**(count-1))

                elif cell["type"] == "utility":
                    owner_cells = [c for c in self.board_data if c["type"] == "utility" and c.get("owner") == owner_id]
                    count = len(owner_cells)
                    if count == 1:
                        rent = 10 + (self.count_circle // 10)
                    elif count >= 2:
                        rent = 25 + (self.count_circle // 10)
                    else:
                        rent = 0
                    cell["rent"] = rent
    
    def broadcast_game_state(self):
        """Оптимизированная отправка состояния игры"""
        # Создаем состояние только если оно изменилось
        self.update_board_rents_and_zalogs()  # ⬅ ДО обновления состояния

        current_state = {
            "players": [p.to_dict() for p in self.players],
            "board": self.board_data,
            "game": {
                "current_player": self.game.current_player if self.game else None,
                "winner": self.game.winner if self.game else None
            },
            "events": self.events[-30:],
            # "auction": getattr(self, 'auction', None),
            "trade_offer": getattr(self, 'trade_offer', None),
            "abilities": [
                {"player_id": pid, "abilities": ab_list}
                for pid, ab_list in self.abilities_by_player.items()
            ]
        }
        if hasattr(self, "last_dice_result"):
            current_state["dice_result"] = self.last_dice_result
        else:
            current_state["dice_result"] = None

        if self.awaiting_property_decision:
            current_state["awaiting_property_decision"] = self.awaiting_property_decision

        # Добавляем информацию об аукционе, если он активен
        if hasattr(self, 'auction') and self.auction is not None:
            current_state["auction"] = {
                "property_index": self.auction["property_index"],
                "cell_name": self.auction["cell"]["name"],
                "current_bid": self.auction["current_bid"],
                "leader_id": self.auction["leader_id"],
                "awaiting_bidder": self.auction["awaiting_bidder"],
                "active_bidders": self.auction["active_bidders"]
            }
        else:
            current_state["auction"] = None
        current_state["board_id"] = self.board_id
        current_state["count_circle"] = self.count_circle
        current_state["bank"] = self.bank

        # Кэшируем последнее состояние
        if not hasattr(self, 'last_broadcast_state') or current_state != self.last_broadcast_state:
            self.last_broadcast_state = current_state
            serialized_state = pickle.dumps(current_state)
            size_data = struct.pack('!I', len(serialized_state))
            
            for player in self.players:
                try:
                    player.conn.send(size_data)
                    player.conn.send(serialized_state)
                except:
                    pass  # Игрок отключился

        if self.trade_offer:
            current_state["trade_offer"] = self.trade_offer


if __name__ == "__main__":
    server = Server()
    server.start()