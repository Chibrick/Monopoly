import pygame
import sys
import random
import threading
import socket
import time
import pyperclip
from network import Network
from player import Player
from board import Board
from game import Game
from ui import UI
from animations import Animation
from server import Server
from constants import *

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class Client:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(500, 100)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Монополия")
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_medium = pygame.font.SysFont(None, 32)
        self.font_large = pygame.font.SysFont(None, 48)

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"  # menu, join_server, lobby, game, game_end
        self.server_ip = ""
        self.username = f"Игрок_{random.randint(1, 1000)}"
        self.player_color = PLAYER_COLORS[random.randint(0, 5)]
        self.is_ready = False
        self.is_mode = False
        self.selected_property = None
        self.board_id = 0
        self.count_circle = 1
        self.bank = 0

        self.network = None
        self.player_id = None
        self.players = []
        self.board = None
        self.game = None
        self.events = []
        self.abilities_by_player = []
        self.ability_input = ""
        self.showing_abilities = False
        
        self.ui = UI(self.screen)
        self.animation = None
        
        self.awaiting_property_decision = None

        self.editing_name = False
        self.name_input_rect = None
        self.name_input_text = ""

        # Состояние игры
        self.can_roll_dice = False
        self.waiting_for_trade_response = False
        self.waiting_for_auction = False

        self.last_positions = {}
        self.dice_result  = None
        self.last_dice_animation_id = None

        self.creating_trade = False
        self.trade_target_id = None
        self.selected_properties = [False] * 40
        self.trade_money_offer_input = ""
        self.selected_requested_properties = [False] * 40
        self.trade_money_request_input = ""
        self.rescue_decision = None

        self.quest_answer_input = ""
        self.answer_timer_start = None
        self.ANSWER_TIMEOUT = 35
        self.typing_answer = False
        self.casino_bet_input = ""
        self.auction_bid_input = ""
        self.typing_auction_bid = False
        self.typing_casino_bet = False

        self.button1 = None
        self.button2 = None

        self.typing_trade_offer = True  # True → левый (offer), False → правый (request)

        self.has_upgraded_this_category = {}  # category_id -> bool

        self.update_ui_elements(self.screen.get_size())
    
    def run(self):
        """Главный цикл клиента"""
        last_time = pygame.time.get_ticks()

        while self.running:
            current_time = pygame.time.get_ticks()
            delta_time = current_time - last_time
            last_time = current_time
            self.handle_events()
            self.update()
            
            # Ограничиваем частоту отрисовки, если игра не активна
            if self.state == "game" or current_time % 16 < 8:  # ~30 FPS для неигровых состояний
                self.draw()
            
            self.clock.tick(60)  # Все равно поддерживаем 60 FPS для плавности
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """Обработка событий"""
        events = pygame.event.get()

        # Сначала обрабатываем QUIT
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
        # Затем остальные события
        for event in events:
            my_player = self.get_my_player()
            if event.type == pygame.VIDEORESIZE:
                min_width = 950
                min_height = 750
                if self.state == "join_server":
                    min_width = 800
                    min_height = 600
                new_width = max(event.w, min_width)
                new_height = max(event.h, min_height)

                self.screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

                self.ui.update_ui_elements((new_width, new_height))
                self.animation.update_ui_elements((new_width, new_height))
                self.update_ui_elements((new_width, new_height))
                self.board.update_dimensions((event.w, event.h))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                key_map = {
                    pygame.K_0: "0", pygame.K_KP0: "0",
                    pygame.K_1: "1", pygame.K_KP1: "1",
                    pygame.K_2: "2", pygame.K_KP2: "2",
                    pygame.K_3: "3", pygame.K_KP3: "3",
                    pygame.K_4: "4", pygame.K_KP4: "4",
                    pygame.K_5: "5", pygame.K_KP5: "5",
                    pygame.K_6: "6", pygame.K_KP6: "6",
                    pygame.K_7: "7", pygame.K_KP7: "7",
                    pygame.K_8: "8", pygame.K_KP8: "8",
                    pygame.K_9: "9", pygame.K_KP9: "9",
                }
                if self.state == "join_server" and not self.editing_name:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.connect_to_server()
                    if event.key == pygame.K_BACKSPACE:
                        self.server_ip = self.server_ip[:-1]
                    elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL) and len(pyperclip.paste()) < 20 and len(self.server_ip) < 15:
                        self.server_ip += pyperclip.paste()
                    elif ((32 <= event.key <= 126) or event.key == pygame.K_KP_PERIOD) and len(self.server_ip) < 30:
                        if event.key in (pygame.K_COMMA, pygame.K_KP_PERIOD):
                            event.key = pygame.K_PERIOD
                        self.server_ip += chr(event.key)
                    elif event.key in key_map and len(self.server_ip) < 30:
                        self.server_ip += key_map[event.key]
                if self.state == "lobby" and self.editing_name:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.username = self.name_input_text
                        self.send_player_update()
                        self.editing_name = False
                    elif event.key == pygame.K_ESCAPE:
                        self.editing_name = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input_text = self.name_input_text[:-1]
                    elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL) and len(pyperclip.paste()) < 10 and len(self.name_input_text) < 5:
                        self.name_input_text += pyperclip.paste()
                    elif len(self.name_input_text) < 15:
                        self.name_input_text += event.unicode
                    elif event.key in key_map and len(self.name_input_text) < 15:
                        self.name_input_text += key_map[event.key]
                        
                if self.typing_answer and (self.awaiting_property_decision.get("type") == "quest" or self.awaiting_property_decision.get("type") == "jail_challenge"):
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # отправить ответ
                        self.network.send({
                            "command": "respond_property_choice",
                            "action": "answer_quest",
                            "answer": self.quest_answer_input,
                            "property_index": self.awaiting_property_decision["property_index"]
                        })
                        self.quest_answer_input = ""
                        self.typing_answer = False
                        self.awaiting_property_decision = None
                        self.answer_timer_start = None
                    elif event.key == pygame.K_BACKSPACE:
                        self.quest_answer_input = self.quest_answer_input[:-1]
                    elif event.unicode.isdigit() and len(self.quest_answer_input) < 7:
                        self.quest_answer_input += event.unicode
                    elif event.key in (pygame.K_PERIOD, pygame.K_KP_PERIOD, pygame.K_MINUS, pygame.K_KP_MINUS):
                        if event.key == pygame.K_KP_PERIOD:
                            event.key = pygame.K_PERIOD
                        elif event.key == pygame.K_KP_MINUS:
                            event.key = pygame.K_MINUS
                        self.quest_answer_input += chr(event.key)
                    elif event.key in key_map and len(self.quest_answer_input) < 7:
                        self.quest_answer_input += key_map[event.key]

                if self.typing_auction_bid:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.auction_bid_input != "":
                        try:
                            amount = int(self.auction_bid_input)
                            if (my_player.money >= amount) and amount>self.auction["current_bid"]:
                                self.network.send({
                                    "command": "bid",
                                    "amount": amount
                                })
                                self.typing_auction_bid = False
                                self.auction_bid_input = ""
                            else:
                                if (my_player.money < amount + 10):
                                    self.events.append(f"{my_player.name}, куда ты ставишь? У тебя нет столько денег")
                                else:
                                    self.events.append(f"{my_player.name}, милорд, ставку надо повышать")
                        except:
                            self.events.append(f"{my_player.name} вводить нужно число!")
                    elif event.key == pygame.K_BACKSPACE:
                        self.auction_bid_input = self.auction_bid_input[:-1]
                    elif event.unicode.isdigit() and len(self.auction_bid_input) < 7:
                        self.auction_bid_input += event.unicode
                    elif event.key in key_map:
                        self.auction_bid_input += key_map[event.key]

                if self.typing_casino_bet and self.awaiting_property_decision:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.casino_bet_input != "" and self.awaiting_property_decision["round"] == 1:
                        try:
                            int(self.casino_bet_input)
                            if (my_player.money >= int(self.casino_bet_input)) and int(self.casino_bet_input)>50:
                                if int(self.casino_bet_input) > 300:
                                    self.casino_bet_input = "1"
                                self.network.send({
                                    "command": "respond_property_choice",
                                    "action": "casino_bet",
                                    "bet": int(self.casino_bet_input),
                                    "property_index": self.awaiting_property_decision["property_index"]
                                })
                                self.typing_casino_bet = False
                                self.casino_bet_input = ""
                            else:
                                if (my_player.money < int(self.casino_bet_input)):
                                    self.events.append(f"{my_player.name}, куда ты ставишь? У тебя нет столько денег")
                                else:
                                    self.events.append(f"{my_player.name}, казино с мелочью не работает")
                        except:
                            self.events.append(f"{my_player.name} вводить нужно число!")
                    elif event.key == pygame.K_BACKSPACE:
                        self.casino_bet_input = self.casino_bet_input[:-1]
                    elif event.unicode.isdigit() and len(self.casino_bet_input) < 5:
                        self.casino_bet_input += event.unicode
                    elif event.key in key_map:
                        self.casino_bet_input += key_map[event.key]      
                if self.creating_trade:
                    if event.key == pygame.K_TAB:
                        self.typing_trade_offer = not self.typing_trade_offer

                    elif event.key == pygame.K_BACKSPACE:
                        if self.typing_trade_offer:
                            self.trade_money_offer_input = self.trade_money_offer_input[:-1]
                        else:
                            self.trade_money_request_input = self.trade_money_request_input[:-1]

                    elif event.unicode.isdigit() and len(event.unicode) == 1:
                        if self.typing_trade_offer and len(self.trade_money_offer_input) < 7:
                            self.trade_money_offer_input += event.unicode
                        elif not self.typing_trade_offer and len(self.trade_money_request_input) < 7:
                            self.trade_money_request_input += event.unicode
                
                if self.showing_abilities:
                    if event.key == pygame.K_BACKSPACE:
                        self.ability_input = self.ability_input[:-1]
                    elif event.unicode.isdigit() and len(self.ability_input) < 10:
                        self.ability_input += event.unicode
    
    def handle_mouse_click(self, pos):
        """Обработка кликов мыши"""
        if self.state == "menu":
            if self.ui.create_server_button.collidepoint(pos):
                self.start_server()
            elif self.ui.join_server_button.collidepoint(pos):
                self.state = "join_server"
        
        elif self.state == "join_server":
            if self.ui.connect_button.collidepoint(pos):
                self.connect_to_server()
            elif self.ui.back_button.collidepoint(pos):
                self.state = "menu"
        
        elif self.state == "lobby":
            # Обработка кликов в лобби         
            if self.ui.back_button.collidepoint(pos):
                self.disconnect_from_server()
                self.state = "menu"
            
            for i, player in enumerate(self.players):
                if player.id == self.player_id:
                    name_rect = pygame.Rect(95, 80 + i * 100 + 25, 200, 30)
                    if name_rect.collidepoint(pos):
                        self.editing_name = True
                        self.name_input_text = player.name
                        self.name_input_rect = name_rect
                        return
            # Клик по цветному квадрату
            for i, player in enumerate(self.players):
                if player.id == self.player_id:
                    color_rect = pygame.Rect(self.screen.get_width() - 150, 80 + i * 100 + 25, 30, 30)
                    if color_rect.collidepoint(pos):
                        self.select_next_color()
                        return
            # Клик по кнопке "ГОТОВ"
            if self.ui.ready_button.collidepoint(pos):
                self.toggle_ready()
            # Клик по кнопке "Режим"
            if self.ui.mode_button.collidepoint(pos):
                # Проверим, хост ли мы
                host_player = next((p for p in sorted(self.players, key=lambda p: p.id) if not p.is_spectator), None)
                if host_player and host_player.id == self.player_id:
                    self.toggle_mode()
        
        elif self.state == "game":
            # Обработка кликов во время игры
            my_player = self.get_my_player()
            current_cell = self.board.cells[my_player.position] if my_player else None

            if self.can_roll_dice and self.ui.roll_dice_button.collidepoint(pos) and not self.trade_offer and not self.creating_trade and not self.showing_abilities and self.awaiting_property_decision == None:
                self.has_upgraded_this_category = {}
                self.roll_dice()

            if self.auction and self.auction["awaiting_bidder"] == self.player_id and not self.trade_offer and not self.creating_trade and not self.showing_abilities:
                if hasattr(self.ui, "pass_button") and self.ui.pass_button.collidepoint(pos):
                    self.network.send({
                        "command": "pass_auction" })
                    self.ui.pass_button = None

            if self.awaiting_property_decision and self.awaiting_property_decision["player_id"] == self.player_id and "cell" in self.awaiting_property_decision:
                cell = self.awaiting_property_decision["cell"]
                cell_type = cell["type"]

                if self.ui.button1 and self.ui.button1.collidepoint(pos) and not self.trade_offer and not self.creating_trade and not self.showing_abilities:
                    if cell_type in ["property", "cars", "utility"]:
                        owner = cell["owner"]
                        price = cell.get("price", 0)
                        rent = cell.get("rent", 0)
                        if owner == None:
                            if my_player.money >= price:
                                self.network.send({
                                    "command": "respond_property_choice",
                                    "action": "buy",
                                    "property_index": self.awaiting_property_decision["property_index"]
                                })
                            else:
                                self.events.append(f"{my_player.name} нехватает денег для покупки. Не тяни резину")
                                self.rescue_decision = self.awaiting_property_decision

                        else:
                            if cell["type"] == "utility":
                            	rent *= self.dice_result["value"]
                            if my_player.money >= rent:
                                self.network.send({
                                    "command": "respond_property_choice",
                                    "action": "rent",
                                    "property_index": self.awaiting_property_decision["property_index"]
                                })
                            else:
                                self.events.append(f"{my_player.name} нехватает денег на оплату аренды")
                                self.rescue_decision = self.awaiting_property_decision

                    elif cell_type == "tax":
                        price = cell.get("price", 0)
                        if my_player.money >= price:
                            self.network.send({
                                "command": "respond_property_choice",
                                "action": "pay_tax",
                                "property_index": self.awaiting_property_decision["property_index"]
                            })
                        else:
                            self.events.append(f"{my_player.name} нехватает денег на налог")
                            self.rescue_decision = self.awaiting_property_decision

                    elif cell_type == "casino":
                        self.rescue_decision = self.awaiting_property_decision
                        self.network.send({
                            "command": "respond_property_choice",
                            "action": "casino_bet",
                            "bet": self.awaiting_property_decision["winnings"],
                            "property_index": self.awaiting_property_decision["property_index"]
                        })
                    elif (cell_type == "quest" or cell_type == "jail") and self.awaiting_property_decision["wrong"] == True:
                        price = self.awaiting_property_decision["reward"]
                        if my_player.money >= price:
                            self.network.send({
                                "command": "respond_property_choice",
                                "action": "quest_tax",
                                "property_index": self.awaiting_property_decision["property_index"]
                            })
                            self.typing_answer = False
                            self.answer_timer_start = None
                        else:
                            self.events.append(f"{my_player.name}, нехватает денег заплатить")
                            self.rescue_decision = self.awaiting_property_decision
                            self.typing_answer = False
                    else:
                        self.rescue_decision = self.awaiting_property_decision

                    self.awaiting_property_decision = None
                    self.awaiting_property_decision = self.rescue_decision
                    self.rescue_decision = None
                    self.ui.button1 = None
                    return

                elif self.ui.button2 and self.ui.button2.collidepoint(pos) and not self.trade_offer and not self.creating_trade and not self.showing_abilities:
                    if cell_type in ["property", "cars", "utility"]:
                        owner = self.awaiting_property_decision["cell"]["owner"]
                        if owner == None:
                            self.network.send({
                                "command": "respond_property_choice",
                                "action": "auction",
                                "property_index": self.awaiting_property_decision["property_index"]
                            })
                            self.typing_auction_bid = False
                        else:
                            self.network.send({
                                "command": "respond_property_choice",
                                "action": "bankrot",
                                "property_index": self.awaiting_property_decision["property_index"]
                            })

                    elif cell_type == "tax":
                        self.network.send({
                                "command": "respond_property_choice",
                                "action": "bankrot",
                                "property_index": self.awaiting_property_decision["property_index"]
                            })
                    elif cell_type == "casino":
                        self.network.send({
                            "command": "respond_property_choice",
                            "action": "casino_take",
                            "property_index": self.awaiting_property_decision["property_index"]
                        })
                        self.typing_casino_bet = False
                    elif (cell_type == "quest" or cell_type == "jail") and self.awaiting_property_decision["wrong"] == True:
                        self.network.send({
                                "command": "respond_property_choice",
                                "action": "bankrot",
                                "property_index": self.awaiting_property_decision["property_index"]
                            })
                        self.typing_answer = False
                        self.answer_timer_start = None
                    else:
                        self.rescue_decision = self.awaiting_property_decision

                    self.awaiting_property_decision = None
                    self.awaiting_property_decision = self.rescue_decision
                    self.rescue_decision = None
                    self.ui.button2 = None
                    return

            if self.showing_abilities and not self.trade_offer and not self.creating_trade:
                if self.ui.back_trade_button.collidepoint(pos):
                    self.showing_abilities = False
                    self.ability_input = ""
                    self.ui.ability_buttons = None
                    self.ui.back_trade_button = None
                    return
                for btn in self.ui.ability_buttons:
                    if btn["buy"].collidepoint(pos):                    	
                        self.network.send({
                            "command": "buy_ability",
                            "ability": btn["name"]
                        })
                    elif btn["use"].collidepoint(pos):
                        self.network.send({
                            "command": "use_ability",
                            "ability": btn["name"],
                            "value": int(self.ability_input or 0)
                        })
                        self.showing_abilities = False
                        self.ability_input = ""
                        self.ui.ability_buttons = None
                        self.ui.back_trade_button = None

            if self.selected_property is not None and ((self.awaiting_property_decision and self.awaiting_property_decision["player_id"] == self.player_id) or (self.auction and self.auction["awaiting_bidder"] == self.player_id) or self.can_roll_dice) and not self.trade_offer and not self.creating_trade and not self.showing_abilities:
                cell = self.board.cells[self.selected_property]

                category = cell["category"]
                cell_type = cell["type"]
                is_mortgaged = cell["Zalog"] is not None

                if self.ui.upgrade_button and self.ui.upgrade_button.collidepoint(pos):
                    if cell["Zalog"] is not None:
                        # Кнопка "Выкупить"
                        if my_player.money >= cell["price"]*0.6:
                            self.network.send({
                                "command": "unmortgage",
                                "property_index": self.selected_property
                            })
                            self.selected_property = None
                        else:
                            self.events.append(f"{my_player.name} нехватает денег для выкупа")
                    else:
                        # Кнопка "Улучшить"
                        if my_player.money >= cell["price"]*0.5:
                            self.network.send({
                                "command": "upgrade_property",
                                "property_index": self.selected_property
                            })
                            # Фиксируем, что игрок улучшил эту категорию
                            category = cell["category"]
                            self.has_upgraded_this_category[category] = True
                            self.selected_property = None
                        else:
                            self.events.append(f"{my_player.name} нехватает денег для улучшения")
                    self.ui.upgrade_button = None

                # Кнопка "Заложить" или "Понизить"
                elif self.ui.zalog_button and self.ui.zalog_button.collidepoint(pos):
                    if cell["type"] == "property" and cell["level"] > 0:
                        # Кнопка "Понизить"
                        self.network.send({
                            "command": "downgrade_property",
                            "property_index": self.selected_property
                        })
                        self.events.append(f"{my_player.name}, уровень понижен")
                        self.selected_property = None
                    else:
                        # Кнопка "Заложить"
                        self.network.send({
                            "command": "mortgage",
                            "property_index": self.selected_property
                        })
                        self.events.append(f"{my_player.name}, клетка заложена")
                        self.selected_property = None
                    self.ui.zalog_button = None
            
            # Выбор собственности для просмотра информации
            cell_index = self.board.get_cell_at_pos(pos)
            if cell_index is not None:
                self.selected_property = cell_index
                if self.creating_trade and not self.trade_offer:
                    cell = self.board.cells[cell_index]
                    if cell["level"] == 0:
                        if cell["owner"] == my_player.id:
                            self.selected_properties[cell_index] = not self.selected_properties[cell_index]
                        elif cell["owner"] == self.trade_target_id:
                            self.selected_requested_properties[cell_index] = not self.selected_requested_properties[cell_index]

            if self.creating_trade and not self.trade_offer and not self.showing_abilities:
                trade_player = self.get_player_by_id(self.trade_target_id)
                # Назад
                if self.ui.back_trade_button.collidepoint(pos):
                    self.creating_trade = False
                    self.can_roll_dice = True
                    self.ui.back_trade_button = None
                    self.ui.reset_trade_button = None
                    self.ui.send_trade_button = None
                    return

                if self.ui.reset_trade_button.collidepoint(pos):
                    self.selected_properties = [False] * 40
                    self.selected_requested_properties = [False] * 40
                    self.trade_money_offer_input = ""
                    self.trade_money_request_input = ""
                    return
                # Отправка сделки
                if self.ui.send_trade_button.collidepoint(pos):
                    if int(self.trade_money_offer_input or "0") == 0 and int(self.trade_money_request_input or "0") == 0 and all(i == False for i in self.selected_properties) and all(i == False for i in self.selected_requested_properties):
                        return  # ничего не выбрано — не отправляем
                    if self.ui.can_send:
                        if my_player.money >= int(self.trade_money_offer_input or "0") and trade_player.money >= int(self.trade_money_request_input or "0"):
                            self.network.send({
                                "command": "propose_trade",
                                "offering_id": self.player_id,
                                "receiving_id": self.trade_target_id,
                                "money_offer": int(self.trade_money_offer_input or "0"),
                                "money_request": int(self.trade_money_request_input or "0"),
                                "properties_offer": self.selected_properties,
                                "properties_request": self.selected_requested_properties,
                                "old_decision": self.awaiting_property_decision
                            })
                            self.creating_trade = False
                            if self.awaiting_property_decision == None:
                            	self.can_roll_dice = True
                            self.ui.back_trade_button = None
                            self.ui.reset_trade_button = None
                            self.ui.send_trade_button = None
                            return
                        else:
                            self.events.append(f"{my_player.name}, у кого-то нехватит денег")
                    else:
                        self.events.append(f"{my_player.name}, превышение 50% в сделке")

            for i, player in enumerate(self.players):
                rect = pygame.Rect(self.padding, prostranstvo + i * 100, self.sidebar_width, 80)
                if rect.collidepoint(pos) and player.id != self.player_id and (not player.is_spectator) and (not (player.id is None) and not self.creating_trade and not self.trade_offer) and not self.showing_abilities and self.can_roll_dice:
                    self.initiate_trade(player.id)
                elif rect.collidepoint(pos) and player.id == self.player_id and (not player.is_spectator) and (not (player.id is None) and not self.creating_trade and not self.trade_offer) and not self.showing_abilities and self.can_roll_dice and self.awaiting_property_decision == None:
                	self.showing_abilities = True

            if self.trade_offer and self.trade_offer["receiving_id"] == self.player_id and not self.creating_trade and not self.showing_abilities:
                offering_player = self.get_player_by_id(self.trade_offer["offering_id"])
                if self.ui.accept_trade_button.collidepoint(pos):
                    self.network.send({"command": "respond_trade", "accept": True})
                    self.trade_offer = None
                    self.creating_trade = False
                    offering_player.must_resolve_tile = False
                    self.awaiting_property_decision = None
                    self.selected_properties = [False] * 40
                    self.selected_requested_properties = [False] * 40
                    self.ui.accept_trade_button = None
                    return
                elif self.ui.decline_trade_button.collidepoint(pos):
                    self.network.send({"command": "respond_trade", "accept": False})
                    self.trade_offer = None
                    self.creating_trade = False
                    offering_player.must_resolve_tile = False
                    self.awaiting_property_decision = None
                    self.selected_properties = [False] * 40
                    self.selected_requested_properties = [False] * 40
                    self.ui.decline_trade_button = None
                    return


        elif self.state == "game_end":
            if self.new_game_button.collidepoint(pos):
                print("Перезапуск клиента")
                import os
                os.execl(sys.executable, sys.executable, *sys.argv)

            if self.exit_button.collidepoint(pos):
                pygame.quit()
                sys.exit()
    
    def get_player_by_id(self, player_id):
        """Получение объекта игрока по ID"""
        return next((p for p in self.players if p.id == player_id), None)

    def update_ui_elements(self, screen_size):
        self.screen_width, self.screen_height = screen_size
        self.scale_x = self.screen_width / SCREEN_WIDTH
        self.scale_y = self.screen_height / SCREEN_HEIGHT
        self.board_width = min(int(self.scale_x * 650), int(self.scale_y * 650))
        self.sidebar_width = min(int(self.scale_x * 200),400)
        self.scale = min(self.scale_x, self.scale_y)*0.95
        self.font_small = pygame.font.SysFont(None, int(24 * self.scale))
        self.font_medium = pygame.font.SysFont(None, int(32 * self.scale))
        self.font_large = pygame.font.SysFont(None, int(48 * self.scale))
        self.padding = (self.screen_width - self.board_width - self.sidebar_width - prostranstvo)/3
        self.cell_size = self.board_width // 13
        self.big_cell_size = 2*self.cell_size
        self.board_x = self.padding + self.sidebar_width + prostranstvo
        self.prompt = 10

    def initiate_trade(self, target_player_id):
        """Начать торговлю с другим игроком"""
        if not self.can_roll_dice:
            return

        self.creating_trade = True
        self.trade_target_id = target_player_id
        self.selected_properties = [False] * 40
        self.trade_money_offer_input = ""
        self.selected_requested_properties = [False] * 40
        self.trade_money_request_input = ""
        self.can_roll_dice = False

    def select_next_color(self):
        index = PLAYER_COLORS.index(self.player_color)
        for i in range(1, len(PLAYER_COLORS)):
            next_color = PLAYER_COLORS[(index + i) % len(PLAYER_COLORS)]
            if not any(p.color == next_color for p in self.players if p.id != self.player_id):
                self.player_color = next_color
                self.send_player_update()
                break

    def handle_key_press(self, key):
        if self.state == "join_server" and not self.editing_name:
            if key == pygame.K_BACKSPACE:
                self.server_ip = self.server_ip[:-1]
            elif 32 <= key <= 126:
                self.server_ip += chr(key)
        elif self.state == "lobby" and self.editing_name:
            if key == pygame.K_RETURN:
                self.username = self.name_input_text
                self.send_player_update()
                self.editing_name = False
            elif key == pygame.K_BACKSPACE:
                self.name_input_text = self.name_input_text[:-1]
            elif len(self.name_input_text) < 15:
                self.name_input_text += key.unicode
    
    def update(self):
        """Обновление состояния игры"""
        if self.state in ["lobby", "game"] and self.network:
            # Получаем обновления не чаще чем 10 раз в секунду
            current_time = pygame.time.get_ticks()
            if not hasattr(self, 'last_update_time') or current_time - self.last_update_time > 100:  # 100ms = 10 updates/sec
                game_state = self.network.receive()
                if game_state:
                    self.update_from_server(game_state)
                self.last_update_time = current_time
            if self.awaiting_property_decision and (self.awaiting_property_decision.get("type", None) == "quest" or self.awaiting_property_decision.get("type", None) == "jail_challenge") and self.answer_timer_start and self.typing_answer:
                elapsed = (pygame.time.get_ticks() - self.answer_timer_start) / 1000
                if elapsed >= self.ANSWER_TIMEOUT:
                    # Отправляем текущий ответ
                    self.network.send({
                        "command": "respond_property_choice",
                        "action": "answer_quest",
                        "answer": self.quest_answer_input,
                        "property_index": self.awaiting_property_decision["property_index"]
                    })
                    self.quest_answer_input = ""
                    self.typing_answer = False
                    self.awaiting_property_decision = None
                    print("Ответ отправлен автоматически по таймеру.")
                    self.answer_timer_start = None
        
    def update_from_server(self, game_state):
        """Обновление состояния клиента на основе данных от сервера"""

        self.count_circle = game_state.get("count_circle", 1)
        self.bank = game_state.get("bank", 1)
        self.auction = game_state.get("auction", None)
        self.abilities_by_player = game_state.get("abilities", [])
        self.trade_offer = game_state.get("trade_offer", None)

        if self.auction:
            if self.auction.get("awaiting_bidder") == self.player_id:
                self.typing_auction_bid = True
                self.auction_bid_input = ""
            else:
                self.typing_auction_bid = False

        self.awaiting_property_decision = game_state.get("awaiting_property_decision", None)

        if self.awaiting_property_decision:
            decision = self.awaiting_property_decision
            if (decision.get("type") == "quest" or decision.get("type") == "jail_challenge") and decision.get("player_id") == self.player_id and not decision.get("wrong"):
                self.typing_answer = True
                self.quest_answer_input = ""
                self.answer_timer_start = pygame.time.get_ticks()

            if decision.get("type") == "casino" and decision.get("player_id") == self.player_id:
                self.typing_casino_bet = True
                self.casino_bet_input = ""

        old_positions = {p.id: p.position for p in self.players} if self.players else {}
        self.players = [Player(**p_data) for p_data in game_state["players"]]
        if game_state.get("dice_result"):
            self.dice_result = game_state["dice_result"]

        # Обновление состояния игры
        if game_state["game"]:
            if not self.game:
                self.game = Game([p.id for p in self.players], game_state["game"]["current_player"])
            else:
                self.game.update_from_data(game_state["game"])

            if game_state['game']['current_player'] != None:
                self.state = "game"
            
            my_player = next((p for p in self.players if p.id == self.player_id), None)
            if my_player and my_player.is_spectator:
                self.can_roll_dice = False
                return  # зритель — не может ходить

            # Проверка, может ли текущий игрок бросать кубики
            self.can_roll_dice = (self.game and 
                                self.game.current_player == self.player_id and 
                                not self.game.winner and
                                not self.waiting_for_trade_response and
                                (self.auction is None))

            if self.can_roll_dice:
                roll_sounds = [
                    pygame.mixer.Sound("sounds/can_roll_dice.wav")
                ]
                random.choice(roll_sounds).play()
        
        # Обновление событий
        self.events = game_state.get("events", [])
        # Проверка на окончание игры
        if self.game and self.game.winner:
            winner = next((p for p in self.players if p.id == self.game.winner), None)
            if winner:
                self.state = "game_end"
                # if self.state == "game_end" and not hasattr(self, "_played_win_sound"):
                #     pygame.mixer.Sound("sounds/victory.wav").play()
                #     self._played_win_sound = True

        if self.dice_result and self.dice_result["animation"]:
            dice_anim = True       
            for new_player in self.players:
                old_pos = old_positions.get(new_player.id)
                if old_pos is not None and (new_player.position != old_pos or new_player.in_jail):
                    if self.dice_result["animation_dice"] and self.dice_result and self.dice_result["player_id"] == new_player.id:
                        self.animation.draw_dice_animation(new_player, self.dice_result)
                        self.last_dice_animation_id = self.dice_result["player_id"]
                        dice_anim = False
                    # Анимация перемещения
                    self.animation.draw_player_move(new_player, old_pos, new_player.position, (new_player.position - old_pos) % len(self.board.cells))
            self.dice_result["animation"] = False

        board_id = game_state["board_id"]
        if (self.board is None or (self.board_id != board_id)):
            if self.state == "game":
                self.fade_transition(game_state)
            else:
                self.board = Board(game_state["board"])
                self.animation = Animation(self.screen, self.board)
            self.board_id = board_id
        else:
            self.board.update_from_data(game_state["board"])

        pygame.display.flip()

    def draw(self):
        """Отрисовка игры"""
        self.screen.fill((200, 200, 200))
        
        if self.state == "menu":
            self.ui.draw_menu()
        
        elif self.state == "join_server":
            self.ui.draw_join_server(self.server_ip)
        
        elif self.state == "lobby":
            self.ui.draw_lobby(self.players, self.player_id, self.username, self.player_color, self.is_ready, self.is_mode, self.editing_name, self.name_input_text)
        
        elif self.state == "game":
            # Отрисовка игрового поля
            self.board.draw(self.screen)

            # Отрисовка лога событий
            self.ui.draw_events_log(self.events)

            # Отрисовка информации об игроках
            self.ui.draw_players_info(self.players, self.player_id, self.game.current_player if self.game else None)

            # Отрисовка информации о выбранной собственности
            if self.selected_property is not None and 0 <= self.selected_property < len(self.board.cells):
                cell = self.board.cells[self.selected_property]
                if not self.creating_trade and not self.trade_offer:
                    self.ui.upgrade_button = None
                    self.ui.zalog_button = None
                    if cell["type"] in ["property", "cars", "utility"]:
                        self.ui.draw_property_info(cell, self.board, self.player_id, self.can_roll_dice, self.has_upgraded_this_category, (self.awaiting_property_decision if self.awaiting_property_decision else None),  (self.auction if self.auction else None), self.count_circle)
                
            for player in self.players:
                self.board.draw_player(self.screen, player, self.players)

            if self.typing_auction_bid and self.auction and self.auction["awaiting_bidder"] == self.player_id:
                bid_input = self.auction_bid_input
                self.ui.draw_auction_menu(self.get_my_player(), self.auction, bid_input)

            elif self.awaiting_property_decision and self.awaiting_property_decision["player_id"] == self.player_id and self.awaiting_property_decision.get("type") != "trade" and (not self.auction):
                cell = self.board.cells[self.awaiting_property_decision["property_index"]]
                if self.typing_answer == True:
                    answer_input = self.quest_answer_input
                elif self.typing_casino_bet == True:
                    answer_input = self.casino_bet_input
                else:
                    answer_input = ""   
                self.ui.draw_action_prompt(cell, self.get_my_player(), self.awaiting_property_decision, answer_input)         
            # Отрисовка элементов управления
            my_player = self.get_my_player()
            # print(f"self.can_roll_dice, my_player.must_resolve_tile, {self.can_roll_dice}, {my_player.must_resolve_tile}")
            if self.awaiting_property_decision == None:
            	self.ui.draw_game_controls(self.can_roll_dice, my_player.must_resolve_tile if my_player else False)
            
            if self.creating_trade:
                self.ui.draw_trade_builder(
                    self.get_my_player(),
                    self.board.cells,
                    self.selected_properties,
                    int(self.trade_money_offer_input or "0"),
                    self.players,
                    self.trade_target_id,
                    self.selected_requested_properties,
                    int(self.trade_money_request_input or "0"),
                    self.typing_trade_offer
                )

            if self.showing_abilities:
            	abilities = next((ab["abilities"] for ab in self.abilities_by_player if ab["player_id"] == self.player_id), [])
            	self.ui.draw_abilities_panel(self.player_id, abilities, self.ability_input)


            if self.trade_offer and self.trade_offer["receiving_id"] == self.player_id:
                self.ui.draw_trade_menu(self.trade_offer, self.board.cells, self.players)

            if self.answer_timer_start:
                remaining = max(0, self.ANSWER_TIMEOUT - (pygame.time.get_ticks() - self.answer_timer_start) / 1000)
                text_string = f"{int(remaining)}"
                timer_text = self.font_medium.render(text_string, True, (200, 0, 0))
                self.screen.blit(timer_text, timer_text.get_rect(center = pygame.draw.rect(self.screen, (255, 255, 255), (self.board_x + self.big_cell_size + self.prompt + 20, prostranstvo + self.big_cell_size + self.prompt + 10, 10, 10)).center))
            
            count_circle = self.font_small.render(f"Круг: {self.count_circle}, Банк: {self.bank}", True, (0, 0, 0))
            self.screen.blit(count_circle, count_circle.get_rect(center=pygame.Rect(self.board_x - 30, prostranstvo - 25, self.big_cell_size, 25).center))


        elif self.state == "game_end":
            self.screen.fill((30, 30, 30))
            winner = next((p for p in self.players if p.id == self.game.winner), None)
            if winner:
                text = self.ui.font_large.render(f"Победитель: {winner.name}!", True, (255, 215, 0))
                self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100))

            # Кнопка "Новая игра"
            self.new_game_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250, 300, 60)
            pygame.draw.rect(self.screen, (100, 200, 100), self.new_game_button, border_radius=12)
            new_game_text = self.ui.font_medium.render("Новая игра", True, (255, 255, 255))
            self.screen.blit(new_game_text, new_game_text.get_rect(center=self.new_game_button.center))

            # Кнопка "Выход"
            self.exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 150, 330, 300, 60)
            pygame.draw.rect(self.screen, (200, 100, 100), self.exit_button, border_radius=12)
            exit_text = self.ui.font_medium.render("Выход", True, (255, 255, 255))
            self.screen.blit(exit_text, exit_text.get_rect(center=self.exit_button.center))
                # self.ui.draw_game_end(winner)
        
        pygame.display.flip()
    
    def get_local_ip(self):
        """Возвращает IP-адрес текущей машины в локальной сети"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Подключение к фейковому адресу для определения IP
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def start_server(self):
        """Запуск сервера в потоке и подключение к себе"""
        ready_event = threading.Event()
        def run_server():
            server = Server(host="0.0.0.0", port=5555, ready_event=ready_event)
            server.start()

        threading.Thread(target=run_server, daemon=True).start()

        time.sleep(0.5)
        if not ready_event.wait(timeout=3):
            print("❌ Сервер не успел запуститься за 3 секунды")
            return
        # Устанавливаем IP для подключения
        for _ in range(10):  # 10 попыток по 0.2 секунды = 2 сек макс
            try:
                self.server_ip = "localhost"
                self.connect_to_server()
                break
            except Exception as e:
                time.sleep(0.2)
        else:
            print("Не удалось подключиться к собственному серверу.")

        # Можно отобразить IP для друзей
        local_ip = self.get_local_ip()
        print(f"Сервер запущен. Подключение для других игроков: {local_ip}:7777")
    
    def connect_to_server(self):
        try:
            logger.info(f"Попытка подключения к серверу {self.server_ip}:7777")
            self.network = Network(self.server_ip)
            self.player_id = self.network.receive()
            print("Получен player_id:", self.player_id)
            logger.info(f"Подключено! ID игрока: {self.player_id}")
            self.state = "lobby"
            self.send_player_update()
            if self.player_id is None:
                logger.error("Не удалось получить ID игрока от сервера")
                return
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
    
    def get_my_player(self):
        return next((p for p in self.players if p.id == self.player_id), None)

    def disconnect_from_server(self):
        """Отключение от сервера"""
        if self.network:
            self.network.close()
            self.network = None
    
    def fade_transition(self, game_state, duration=1000):
        fade_surface = pygame.Surface(self.screen.get_size())
        fade_surface.fill((0, 0, 0))

        clock = pygame.time.Clock()
        steps = 30
        delay = duration // (steps * 2)  # fade out и fade in

        # Плавное затемнение
        for alpha in range(0, 256, 256 // steps):
            fade_surface.set_alpha(alpha)
            self.draw()  # или draw_screen, draw_board — что отрисовывает экран
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            clock.tick(1000 // delay)

        self.board = Board(game_state["board"])
        self.animation = Animation(self.screen, self.board)

        # Обновление доски должно быть вызвано после
        # (снаружи этого метода)

        # Плавное прояснение
        for alpha in range(255, -1, -256 // steps):
            fade_surface.set_alpha(alpha)
            self.draw()
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            clock.tick(1000 // delay)

    def send_player_update(self):
        """Отправка обновленных данных игрока на сервер"""
        if self.network:
            self.network.send({
                "command": "update_player",
                "name": self.username,
                "color": self.player_color,
                "is_ready": self.is_ready,
                "is_mode": self.is_mode
            })
    
    def toggle_ready(self):
        """Переключение состояния готовности"""
        self.is_ready = not self.is_ready
        self.send_player_update()
    
    def toggle_mode(self):
        self.is_mode = not self.is_mode
        self.send_player_update()

    def select_color(self, color):
        """Выбор цвета игрока"""
        # Проверяем, что цвет не занят
        if not any(p.color == color for p in self.players if p.id != self.player_id):
            self.player_color = color
            self.send_player_update()
    
    def roll_dice(self):
        """Бросок кубиков"""
        if self.network and self.can_roll_dice:
            # 1) запоминаем, где сейчас стоит наша фишка
            me = next((p for p in self.players if p.id == self.player_id), None)
            if me:
                self.last_position = me.position   # позиция ДО хода

            # 2) пока не знаем, сколько выпадет – сбрасываем счётчик
            self.dice_result = None                # узнаем после ответа сервера

            # 3) отправляем команду серверу
            self.network.send({"command": "roll_dice"})
            self.can_roll_dice = False
    
    def buy_property(self):
        """Покупка собственности"""
        if self.network:
            self.network.send({"command": "buy_property"})
    
    def auction_property(self):
        """Начало аукциона за собственность"""
        if self.network:
            self.network.send({"command": "auction_property"})

if __name__ == "__main__":
    client = Client()
    client.run()