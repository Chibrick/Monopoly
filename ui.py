import pygame
from board import Board
from constants import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_medium = pygame.font.SysFont(None, 32)
        self.font_large = pygame.font.SysFont(None, 48)
        
        # Кнопки меню
        self.create_server_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 250, 300, 50)
        self.join_server_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 320, 300, 50)
        self.back_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 500, 300, 50)
        self.connect_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 320, 300, 50)

        # кнопка в лобби
        self.ready_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 400, 300, 50)
        self.mode_button = pygame.Rect(SCREEN_WIDTH//2 - 300, 400, 300, 50)

        # кнопки в игре
        self.roll_dice_button = pygame.Rect(SCREEN_WIDTH - 200, 650, 150, 50) # бросить кубик

        # кнопки клеток
        self.button1 = None
        self.button2 = None

        #кнопки предприятий
        self.upgrade_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 400, 300, 50)
        self.zalog_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 400, 300, 50)

        # кнопки сделки
        self.accept_trade_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 400, 150, 50)
        self.decline_trade_button = pygame.Rect(SCREEN_WIDTH//2 + 10, 400, 150, 50)
        self.send_trade_button = pygame.Rect(SCREEN_WIDTH//2 + 10, 400, 150, 50)
        self.back_trade_button = pygame.Rect(SCREEN_WIDTH//2 + 10, 460, 150, 50)
        self.reset_trade_button = pygame.Rect(SCREEN_WIDTH//2 + 50, 460, 150, 50)

        # кнопки аукцион
        self.bid_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 400, 150, 50)
        self.pass_button = pygame.Rect(SCREEN_WIDTH//2 + 10, 400, 150, 50)

        self.can_send = False
        # Вызов метода для первичной настройки
        self.update_ui_elements(self.screen.get_size())
    
    def update_ui_elements(self, screen_size):
        self.screen_width, self.screen_height = screen_size
        self.scale_x = self.screen_width / SCREEN_WIDTH
        self.scale_y = self.screen_height / SCREEN_HEIGHT
        self.board_width = min(int(self.scale_x * 650), int(self.scale_y * 650))
        self.sidebar_width = min(int(self.scale_x * 200),400)
        self.padding = (self.screen_width - self.board_width - self.sidebar_width - prostranstvo)/3
        self.cell_size = self.board_width // 13
        self.big_cell_size = 2*self.cell_size
        self.board_x = self.padding + self.sidebar_width + prostranstvo
        self.scale = min(self.scale_x, self.scale_y)*0.95
        self.font_small = pygame.font.SysFont(None, int(24 * self.scale))
        self.font_medium = pygame.font.SysFont(None, int(32 * self.scale))
        self.font_large = pygame.font.SysFont(None, int(48 * self.scale))
        self.prompt = 10

        # Кнопки меню
        self.create_server_button = pygame.Rect(self.screen_width//2 - 150, 250, 300, 50)
        self.join_server_button = pygame.Rect(self.screen_width//2 - 150, 320, 300, 50)
        self.back_button = pygame.Rect(20, self.screen_height - 70, 120, 50)
        self.connect_button = pygame.Rect(self.screen_width//2 - 150, 320, 300, 50)
        
        # кнопка в лобби
        self.ready_button = pygame.Rect(self.screen_width - 200, self.screen_height - 70, 150, 50)
        self.mode_button = pygame.Rect(self.screen_width - 500, self.screen_height - 70, 250, 50)

        # кнопки в игре
        self.roll_dice_button = pygame.Rect(self.board_x + self.big_cell_size, prostranstvo + self.big_cell_size, 9*self.cell_size, 100)

        # кнопки клеток
        self.button1 = pygame.Rect(self.board_x + self.big_cell_size + self.prompt + 10, prostranstvo + self.big_cell_size + self.prompt + 50, 3*self.cell_size, 40)
        self.button2 = pygame.Rect(self.screen_width - 2*self.padding - self.big_cell_size - 10 - 3*self.cell_size - self.prompt, prostranstvo + self.big_cell_size + self.prompt + 50, 3*self.cell_size, 40)

        # кнопки сделки
        self.accept_trade_button = pygame.Rect(self.screen_width//2 - 150, 400, 150, 50)
        self.decline_trade_button = pygame.Rect(self.screen_width//2 + 10, 400, 150, 50)
        self.send_trade_button = pygame.Rect(SCREEN_WIDTH//2 + 10, 400, 150, 50)
        self.back_trade_button = pygame.Rect(SCREEN_WIDTH//2 + 10, 460, 150, 50)
        self.reset_trade_button = pygame.Rect(SCREEN_WIDTH//2 + 50, 460, 150, 50)

        # кнопки аукцион
        self.bid_button = pygame.Rect(self.board_x + self.big_cell_size + 10, prostranstvo + self.big_cell_size + 50, 3*self.cell_size, 50)
        self.pass_button = pygame.Rect(self.screen_width - 2*self.padding - self.big_cell_size - 10 - 3*self.cell_size - self.prompt, prostranstvo + self.big_cell_size + self.prompt +  50, 3*self.cell_size, 40)
        # self.back_to_lobby_button = pygame.Rect(self.screen_width//2 - 150, self.screen_height - 100, 300, 50)

    def draw_menu(self):
        """Отрисовка главного меню"""
        title = self.font_large.render("Монополия", True, (0, 0, 0))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        
        # Кнопка "Создать сервер"
        pygame.draw.rect(self.screen, (100, 200, 100), self.create_server_button)
        text = self.font_medium.render("Создать сервер", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center = self.create_server_button.center))
        
        # Кнопка "Подключиться к серверу"
        pygame.draw.rect(self.screen, (100, 100, 200), self.join_server_button)
        text = self.font_medium.render("Подключиться к серверу", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center = self.join_server_button.center))
    
    def draw_join_server(self, server_ip):
        """Отрисовка экрана подключения к серверу"""
        title = self.font_large.render("Подключение к серверу", True, (0, 0, 0))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        
        # Поле ввода IP
        pygame.draw.rect(self.screen, (100, 100, 100), (self.screen.get_width()//2 - 150, 200, 300, 50))
        text = self.font_medium.render(server_ip, True, (0, 0, 0))
        self.screen.blit(text, (self.screen.get_width()//2 - 140, 215))
        
        # Кнопка "Подключиться"
        pygame.draw.rect(self.screen, (100, 100, 200), self.connect_button)
        text = self.font_medium.render("Подключиться", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center = self.connect_button.center))
        
        # Кнопка "Назад"
        pygame.draw.rect(self.screen, (200, 100, 100), self.back_button)
        text = self.font_medium.render("Назад", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center = self.back_button.center))
    
    def draw_lobby(self, players, my_id, username, player_color, is_ready, is_mode, editing_name=False, name_input_text=""):
        self.screen.fill((240, 240, 240))
        SCREEN_WIDTH, SCREEN_HEIGHT = self.screen.get_size()
        
        # Динамическое позиционирование элементов
        title = self.font_large.render("ЛОББИ", True, (0, 0, 0))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 20))
        
        # Отрисовка игроков в занятых слотах (сверху вниз)
        for i, player in enumerate(sorted(players, key=lambda p: p.id)):
            if player.id is None or player.is_spectator:
                continue
            y = 80 + i * 100
            editing = (player.id == my_id and getattr(self, 'editing_name', False))
            name_text = getattr(self, 'name_input_text', "|") if editing else ""
            self.draw_player_slot(y, player, my_id, i, editing=(editing_name and player.id == my_id), name_text=name_input_text)
        
        # Отрисовка пустых слотов
        for i in range(len(players), MAX_PLAYERS):
            y = 80 + i * 100
            self.draw_empty_slot(y, i)
        
        # Кнопка "Назад"
        pygame.draw.rect(self.screen, (200, 100, 100), self.back_button)
        text = self.font_medium.render("Назад", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center = self.back_button.center))

        # Найдём первого активного игрока (не spectator)
        host_player = next((p for p in sorted(players, key=lambda p: p.id) if not p.is_spectator), None)
        # Проверим, мы ли хост
        is_host = (host_player and host_player.id == my_id)

        # Кнопка "Режим" — только для хоста
        if is_host:
            # Кнопка Режим
            mode_color = (100, 200, 100) if is_mode else (200, 100, 100)
            pygame.draw.rect(self.screen, mode_color, self.mode_button)
            mode_text = self.font_medium.render("Режим Включен" if is_mode else "Режим Выключен", True, (255, 255, 255))
            self.screen.blit(mode_text, mode_text.get_rect(center = self.mode_button.center))

        # Кнопка готовности справа
        ready_color = (100, 200, 100) if not is_ready else (200, 100, 100)
        pygame.draw.rect(self.screen, ready_color, self.ready_button)
        ready_text = self.font_medium.render("ГОТОВ" if not is_ready else "ОТМЕНА", True, (255, 255, 255))
        self.screen.blit(ready_text, ready_text.get_rect(center = self.ready_button.center))

    def draw_player_slot(self, y, player, my_id, index, editing, name_text=""):
        slot_color = (200, 255, 200) if player.id == my_id else (230, 230, 230)
        pygame.draw.rect(self.screen, slot_color, (50, y, self.screen.get_width()-100, 80))

        # Метка "Вы"
        if player.id == my_id:
            you_text = self.font_medium.render("Вы", True, (0, 0, 255))
            self.screen.blit(you_text, (60, y + 20))

        # Имя
        if player.id == my_id and editing:
            pygame.draw.rect(self.screen, (100, 100, 100), (95, y + 15, 200, 30))
            pygame.draw.rect(self.screen, (0, 0, 0), (95, y + 15, 200, 30), 2)
            name_render = self.font_medium.render(name_text + "|", True, (0, 0, 0))
        else:
            name_render = self.font_medium.render(player.name, True, (0, 0, 0))
        self.screen.blit(name_render, (100, y + 20))

        # Цветной квадрат
        pygame.draw.rect(self.screen, player.color, (self.screen.get_width() - 150, y + 25, 30, 30))
        if player.id == my_id:
            pygame.draw.rect(self.screen, (0, 0, 0), (self.screen.get_width() - 150, y + 25, 30, 30), 2)

        # Статус
        status_text = "ГОТОВ" if player.is_ready else "ОЖИДАЕТ"
        status_color = (0, 150, 0) if player.is_ready else (150, 0, 0)
        status_render = self.font_small.render(status_text, True, status_color)
        self.screen.blit(status_render, (100, y + 50))

    def draw_empty_slot(self, y, index):
        pygame.draw.rect(self.screen, (220, 220, 220), (50, y, self.screen.get_width()-100, 80))
        empty_text = f"Слот {index+1} (свободен)"
        empty = self.font_medium.render(empty_text, True, (150, 150, 150))
        self.screen.blit(empty, (70, y + 30))
    
    def draw_players_info(self, players, my_id, current_player_id):
        """Отрисовка информации об игроках"""
        for i, player in enumerate(players):
            # Фон блока игрока
            bg_color = (220, 220, 220)

            if player.id is None or player.is_spectator:
                bg_color = (50, 50, 50)

            x = self.padding
            y = prostranstvo + i * 100
            width = self.sidebar_width
            height = 80

            if player.id == current_player_id:
                bg_color = (200, 240, 200)  # Подсветка текущего игрока
            if player.bankrupt:
                bg_color = (240, 150, 150)  # Подсветка банкрота
                
            pygame.draw.rect(self.screen, bg_color, (x, y, width, height))
            
            # Цвет игрока
            pygame.draw.rect(self.screen, player.color, (x + 10, y + 10, 30, 30))
            
            # Имя и деньги
            name_text = self.font_small.render(player.name, True, (0, 0, 0))
            self.screen.blit(name_text, (x + 50, y + 10))
            
            money_text = self.font_small.render(f"{round(player.money)}$", True, (0, 0, 0))
            self.screen.blit(money_text, (x + 50, y + 40))
            
            # Маркер "Вы" для текущего игрока
            if player.id == my_id:
                you_text = self.font_small.render("Вы", True, (0, 0, 255))
                self.screen.blit(you_text, (x + width - 30, y + 10))
    
    def draw_events_log(self, events):
        log_box_x = self.board_x + self.big_cell_size
        log_box_y = prostranstvo + self.big_cell_size
        log_box_width = 9*self.cell_size
        line_height = 20
        max_lines = round((log_box_width - 20) / line_height)
        pygame.draw.rect(self.screen, (255, 255, 255), (log_box_x, log_box_y, log_box_width, log_box_width))

        wrapped_lines = []
        for event in events[-30:]:
            event_text = self.font_small.render(event, True, (0, 0, 0))
            width, _ = self.font_small.size(event)
            if width > log_box_width - 20:
                words = event.split()
                current_line = ""
                wrapped = False
                next_line = ""
                for word in words:
                    if wrapped:
                        next_line = next_line + " " + word
                    else:
                        test_line = current_line + " " + word
                        width, _ = self.font_small.size(test_line)
                        if width > log_box_width - 20:
                            current_line = current_line[1:]
                            wrapped_lines.insert(0, current_line)
                            next_line = word
                            wrapped = True
                        else:
                            current_line = test_line
                if next_line != "":
                    wrapped_lines.insert(0, next_line)
            else:
                wrapped_lines.insert(0, event)
        visible_lines = wrapped_lines[:max_lines]
        total_lines = len(visible_lines)
        for i, line in enumerate(reversed(visible_lines)):
            y = log_box_y + log_box_width - 20 - (total_lines - 1 - i) * line_height
            text_surface = self.font_small.render(line, True, (0, 0, 0))
            self.screen.blit(text_surface, (log_box_x + 10, y))
    
    def draw_action_prompt(self, cell, player, state, answer_input=""):
        x = self.board_x + self.big_cell_size + self.prompt
        y = prostranstvo + self.big_cell_size + self.prompt

        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 9*self.cell_size - 2*self.prompt, 100))


        message = ""
        show_buttons = False
        button_count = 0
        notext = False

        if cell["type"] in ["property", "cars", "utility"]:
            if cell["owner"] is None:
                text = self.font_small.render("Купить данное предприятие", True, (0, 0, 0))

                button1_color = (76,220,112) if (player.money >= cell["price"]) else (46,45,45)
                button2_color = (200,100,10)

                button1_text = self.font_small.render("Купить", True, (0, 0, 0))
                button2_text = self.font_small.render("Аукцион", True, (0, 0, 0))

                button_count = 2

            elif cell["owner"] != player.id:
                text = self.font_small.render("Заплатите за аренду", True, (0, 0, 0))

                button1_color = (25,126,174) if (player.money >= cell["rent"]) else (46,45,45)
                button1_text = self.font_small.render("Заплатить", True, (0, 0, 0))
                button2_color = (224,184,184)
                button2_text = self.font_small.render("Сдаться", True, (0, 0, 0))

                button_count = 2

        elif cell["type"] == "tax":
            text = self.font_small.render("А НУ-КА БЫСТРО ЗАПЛАТИЛ НАЛОГ ГОСУДАРСТВУ", True, (0, 0, 0))

            button1_color = (255,0,0) if (player.money >= cell["price"]) else (46,45,45)
            button1_text = self.font_small.render("заплатить", True, (0, 0, 0))
            button2_color = (224,184,184)
            button2_text = self.font_small.render("Сдаться", True, (0, 0, 0))

            button_count = 2

        elif cell["type"] == "casino":#######
            rounds = state["round"]
            if rounds > 1:
                text = self.font_small.render("Сыграешь ещё?", True, (0, 0, 0))

                button1_color = (95,217,74)
                button1_text = self.font_small.render("Попробуешь удвоить?", True, (0, 0, 0))

                button2_color = (133,133,133)
                button2_text = self.font_small.render("не, я боюсь", True, (0, 0, 0))

                button_count = 2
            else:               
                text = self.font_small.render("Сыграешь? Какова твоя ставка?", True, (0, 0, 0))

                # Поле ввода ставки
                bet_box = pygame.Rect(self.board_x + self.big_cell_size + self.prompt + 10, prostranstvo + self.big_cell_size + 50 + self.prompt, 3*self.cell_size, 40)
                pygame.draw.rect(self.screen, (255, 255, 255), bet_box)
                pygame.draw.rect(self.screen, (0, 0, 0), bet_box, 2)
                bet_text = self.font_small.render(answer_input, True, (0, 0, 0))
                self.screen.blit(bet_text, bet_text.get_rect(center = bet_box.center))
                

                button2_color = (133,133,133)
                button2_text = self.font_small.render("не, я боюсь", True, (0, 0, 0))

                button_count = 1
                self.button1 = None

        elif cell["type"] == "quest" or cell["type"] == "jail":
            wrong = state["wrong"]
            if (not wrong):
                question = state["question"]  # "Сколько будет (5 + 3)?"
                prefix = "Сколько будет "
                expr = question[len(prefix):-1]  # Удаляем "Сколько будет " и "?"
                prefix = "Сколько будет? (// - Целое, % - остаток)"
                text_prefix = self.font_small.render(prefix, True, (0, 0, 0))
                text_expr = self.font_small.render(expr, True, (0, 0, 0))
                self.screen.blit(text_prefix, text_prefix.get_rect(center = pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 9*self.cell_size - 2*self.prompt, 30)).center))
                self.screen.blit(text_expr, text_expr.get_rect(center = pygame.draw.rect(self.screen, (255, 255, 255), (x, y+30, 9*self.cell_size - 2*self.prompt, 30)).center))

                # Поле ввода
                input_box = pygame.Rect(self.board_x + self.big_cell_size + self.prompt + 10, prostranstvo + self.big_cell_size + self.prompt + 60, 8*self.cell_size, 30)
                pygame.draw.rect(self.screen, (255, 255, 255), input_box)
                pygame.draw.rect(self.screen, (0, 0, 0), input_box, 2)

                answer_text = self.font_small.render(answer_input, True, (0, 0, 0))
                self.screen.blit(answer_text, answer_text.get_rect(center = input_box.center))

                notext = True
                button_count = 0
                self.button1 = None
                self.button2 = None
            else:
                if state["type"] == "quest":
                    text = self.font_small.render("Ответ неправильный", True, (0, 0, 0))
                else:
                    text = self.font_small.render("Штраф", True, (0, 0, 0))

                button1_color = (25,126,174) if (player.money >= state["reward"]) else (46,45,45)
                button1_text = self.font_small.render("Заплатить", True, (0, 0, 0))
                button2_color = (224,184,184)
                button2_text = self.font_small.render("Сдаться", True, (0, 0, 0))

                button_count = 2

        if notext:
            notext = False
        else:
            self.screen.blit(text, text.get_rect(center = pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 9*self.cell_size - 2*self.prompt, 50)).center))

        if button_count == 1:
            self.button1 = None
            self.button2 = pygame.Rect(self.screen_width - 2*self.padding - self.big_cell_size - 10 - 3*self.cell_size - self.prompt, prostranstvo + self.big_cell_size + self.prompt + 50, 3*self.cell_size, 40)    
            pygame.draw.rect(self.screen, button2_color, self.button2)
            self.screen.blit(button2_text, button2_text.get_rect(center = self.button2.center))
        elif button_count == 2:
            self.button1 = pygame.Rect(self.board_x + self.big_cell_size + self.prompt + 10, prostranstvo + self.big_cell_size + self.prompt + 50, 3*self.cell_size, 40)
            self.button2 = pygame.Rect(self.screen_width - 2*self.padding - self.big_cell_size - 10 - 3*self.cell_size - self.prompt, prostranstvo + self.big_cell_size + self.prompt + 50, 3*self.cell_size, 40)

            self.button1 = pygame.Rect(self.board_x + self.big_cell_size + self.prompt + 10, prostranstvo + self.big_cell_size + self.prompt + 50, 4*self.cell_size, 40)
            pygame.draw.rect(self.screen, button1_color, self.button1)
            self.screen.blit(button1_text, button1_text.get_rect(center = self.button1.center))
            pygame.draw.rect(self.screen, button2_color, self.button2)
            self.screen.blit(button2_text, button2_text.get_rect(center = self.button2.center))

        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 9*self.cell_size - 2*self.prompt, 100), 2)

    def draw_game_controls(self, can_roll_dice, must_resolve_tile):
        """Отрисовка кнопок управления игрой"""
        # Кнопка "Бросить кубики"
        if can_roll_dice and (not must_resolve_tile):
            dice_color = (100, 255, 100)
            pygame.draw.rect(self.screen, dice_color, self.roll_dice_button)
            dice_text = self.font_large.render("Бросить кубики", True, (0, 0, 0))
            self.screen.blit(dice_text, dice_text.get_rect(center = self.roll_dice_button.center ))
    
    def draw_property_info(self, cell, board, current_player_id, can_roll_dice, has_upgraded_this_category, awaiting_property_decision, auction, count_circle):
        """Отрисовка информации о выбранной собственности"""
        info_x = self.board_x + self.big_cell_size + 6*self.cell_size
        info_y = prostranstvo + self.big_cell_size + 2*self.cell_size
        info_width = 3*self.cell_size
        info_height = self.cell_size
        
        name_color = cell["color"] if (cell["color"] is not None) else (255,255,255)
        pygame.draw.rect(self.screen, (name_color), (info_x, info_y, info_width, info_height))
        pygame.draw.aaline(self.screen, (0,0,0), [info_x, info_y], [info_x+info_width, info_y],2)

        # Название
        name_text = self.font_small.render(cell["name"], True, (0, 0, 0))
        self.screen.blit(name_text, (info_x + 10, info_y + 10 * self.scale))

        # Тип
        ####### изменить название категории
        type_text = self.font_small.render(f"Тип: {cell['category_name']}", True, (0, 0, 0))
        self.screen.blit(type_text, (info_x + 10, info_y + 30 * self.scale))

        # Владелец
        if cell['type'] == "property":
            info_x = self.board_x + self.big_cell_size + 6*self.cell_size
            info_y = prostranstvo + self.big_cell_size + 3*self.cell_size 
            info_width = 3*self.cell_size
            info_height = 4*self.cell_size
        
            pygame.draw.rect(self.screen, (177,229,241), (info_x, info_y, info_width, info_height))
            
            # Улучшение
            upgrade_text = self.font_small.render(f"Улучшение: {round(cell['price']/2)}", True, (0, 0, 0))
            self.screen.blit(upgrade_text, (info_x + 10, info_y + 65 * self.scale))

            # Аренда
            for i in [0,1,2,3,4,5]:
                rent_text = self.font_small.render(f"{i} звезд: {round(cell['price']*RENT_MULTIPLIERS[i])}$", True, (0, 150, 0) if (cell['rent'] == cell['price']*RENT_MULTIPLIERS[i]) else (0,0,0))
                self.screen.blit(rent_text, (info_x + 10, info_y + 90 * self.scale + 20*i * self.scale))

            category = cell.get("category")
            for i, cellis in enumerate(board.cells):
                group_indices = [
                    j for j, c in enumerate(board.cells)
                    if c.get("category") == category
                ]
                for j in group_indices:
                    highlighte = True
                    board.draw_cell(self.screen, j, board.cells[j], highlighte)

        elif cell['type'] == "cars":
            info_x = self.board_x + self.big_cell_size + 6*self.cell_size
            info_y = prostranstvo + self.big_cell_size + 3*self.cell_size
            info_width = 3*self.cell_size
            info_height = 3*self.cell_size

            pygame.draw.rect(self.screen, (177,229,241), (info_x, info_y, info_width, info_height))

            # Аренда
            for i in [0,1,2,3]:
                rent_text = self.font_small.render(f"{i+1} в наличии: {(25+(count_circle // 10)*7)*(2**(i))}", True, (0, 150, 0) if (cell['rent'] == (25+(count_circle // 10)*10)*(2**(i))) else (0,0,0))
                self.screen.blit(rent_text, (info_x + 10, info_y + 70 * self.scale + 20*i * self.scale))
            
            for i, cellis in enumerate(board.cells):
                group_indices = [
                    j for j, c in enumerate(board.cells)
                    if c.get("type") == "cars"
                ]
                for j in group_indices:
                    highlighte = True
                    board.draw_cell(self.screen, j, board.cells[j], highlighte)

        else:
            info_x = self.board_x + self.big_cell_size + 6*self.cell_size
            info_y = prostranstvo + self.big_cell_size + 3*self.cell_size
            info_width = 3*self.cell_size
            info_height = 3*self.cell_size

            pygame.draw.rect(self.screen, (177,229,241), (info_x, info_y, info_width, info_height))

            # Аренда
            for i in [0,1]:
                rent_text = self.font_small.render(f"{i+1} во владении: ", True, (0,0,0))
                self.screen.blit(rent_text, (info_x + 10, info_y + 70 * self.scale + 40*i * self.scale))
                rent_text = self.font_small.render(f"кол-во шагов * {i*15+10+(count_circle // 10)}", True, (0,0,0))
                self.screen.blit(rent_text, (info_x + 10, info_y + 90 * self.scale + 40*i * self.scale))

            for i, cellis in enumerate(board.cells):
                group_indices = [
                    j for j, c in enumerate(board.cells)
                    if c.get("type") == "utility"
                ]
                for j in group_indices:
                    highlighte = True
                    board.draw_cell(self.screen, j, board.cells[j], highlighte)

        # Цена
        price_text = self.font_small.render(f"Цена: {cell['price']}$", True, (0, 0, 0))
        self.screen.blit(price_text, (info_x + 10, info_y + 5 * self.scale))
            
        # Залог
        zalog_text = self.font_small.render(f"Залог: {round(cell['price']/2)}", True, (0, 0, 0))
        self.screen.blit(zalog_text, (info_x + 10, info_y + 25 * self.scale))

        # Выкуп
        vicup_text = self.font_small.render(f"Выкуп: {round(cell['price']*0.6)}", True, (0, 0, 0))
        self.screen.blit(vicup_text, (info_x + 10, info_y + 45 * self.scale))

        pygame.draw.aaline(self.screen, (0,0,0), [info_x-1, info_y - self.cell_size], [info_x-1, info_y + info_height],2)
        pygame.draw.aaline(self.screen, (0,0,0), [info_x, info_y + info_height], [info_x + info_width, info_y + info_height],2)

        if ((awaiting_property_decision and awaiting_property_decision["player_id"] == current_player_id) or (auction and auction.get("awaiting_bidder") == current_player_id) or can_roll_dice) and cell["owner"] == current_player_id:
            category = cell["category"]
            cell_type = cell["type"]
            is_mortgaged = cell["Zalog"] is not None

            # Собираем все клетки этой категории
            same_category_cells = [c for c in board.cells if c["type"] == "property" and c["category"] == category]
            player_owns_all = all(c["owner"] == current_player_id for c in same_category_cells)
            other_levels = [c["level"] for c in same_category_cells if c != cell]
            # 1. Если в залоге — можно выкупить
            if is_mortgaged:
                # нарисовать кнопку "Выкупить"
                self.upgrade_button = pygame.Rect(info_x, info_y + info_height, 3*self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (20, 200, 20), self.upgrade_button)
                btn_text = self.font_small.render("Выкупить", True, (0, 0, 0))
                self.screen.blit(btn_text, btn_text.get_rect(center = (self.upgrade_button).center))
                info_y += self.cell_size
            # 3. PROPERTY: улучшение (если всё соблюдено)
            elif (cell_type == "property" and not is_mortgaged and player_owns_all and can_roll_dice
                  and all(c["Zalog"] is None for c in same_category_cells)
                  and (cell["level"] <= min(other_levels or [5]))  # сравнение с другими
                  and (cell["level"] < 5)
                  and not has_upgraded_this_category.get(category, False)):
                self.upgrade_button = pygame.Rect(info_x, info_y + info_height, 3*self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (20, 255, 20), self.upgrade_button)
                btn_text = self.font_small.render("Улучшить", True, (0, 0, 0))
                self.screen.blit(btn_text, btn_text.get_rect(center = self.upgrade_button.center))
                info_y += self.cell_size

            # 2. Если НЕ property и НЕ в залоге — можно заложить
            if cell_type != "property" and not is_mortgaged:
                self.zalog_button = pygame.Rect(info_x, info_y + info_height, 3*self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (200, 20, 20), self.zalog_button)
                btn_text = self.font_small.render("Заложить", True, (0, 0, 0))
                self.screen.blit(btn_text, btn_text.get_rect(center = (self.zalog_button).center))

            # 4. PROPERTY: залог (если у всех уровень 0)
            elif (cell_type == "property" and not is_mortgaged
                  and all(c["level"] == 0 for c in same_category_cells)):
                self.zalog_button = pygame.Rect(info_x, info_y + info_height, 3*self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (200, 20, 20), self.zalog_button)
                btn_text = self.font_small.render("Заложить", True, (0, 0, 0))
                self.screen.blit(btn_text, btn_text.get_rect(center = (self.zalog_button).center))

            # 5. PROPERTY: понижение уровня
            elif (cell_type == "property" and player_owns_all and not is_mortgaged
                  and (cell["level"] >= max(other_levels or [0]))):
                self.zalog_button = pygame.Rect(info_x, info_y + info_height, 3*self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (250, 180, 60), self.zalog_button)
                btn_text = self.font_small.render("Понизить", True, (0, 0, 0))
                self.screen.blit(btn_text, btn_text.get_rect(center = (self.zalog_button).center))
    
    def draw_trade_menu(self, trade_offer, board, players):
        """Отрисовка меню предложения сделки"""
        trade_x = self.board_x + self.big_cell_size + self.prompt
        trade_y = prostranstvo + self.big_cell_size + self.prompt
        trade_width = 9*self.cell_size - 2*self.prompt
        trade_height = 9*self.cell_size - 2*self.prompt
        trade_x2 = trade_x + trade_width/2

        # Окно сделки
        pygame.draw.rect(self.screen, (255, 255, 255), (trade_x, trade_y, trade_width, trade_height))
        
        # Информация о сделке
        offering_player = next((p for p in players if p.id == trade_offer["offering_id"]), None)
        receiving_player = next((p for p in players if p.id == trade_offer["receiving_id"]), None)
        
        if offering_player and receiving_player:
            # Заголовок
            title = self.font_medium.render(f"Сделка от {offering_player.name}", True, (0, 0, 0))
            self.screen.blit(title, title.get_rect(center = pygame.draw.rect(self.screen, (255, 255, 255), (trade_x, trade_y, trade_width, 50)).center))
            
            # панели игроков
            pygame.draw.rect(self.screen, offering_player.color, (trade_x + 5, trade_y + 55, 40,40))
            name = self.font_small.render(f"{offering_player.name}", True, offering_player.color)
            self.screen.blit(name, (trade_x + 50, trade_y+55))
            action = self.font_small.render(f"Предлагает", True, (0,0,0))
            self.screen.blit(action, (trade_x + 50, trade_y+75))

            pygame.draw.rect(self.screen, receiving_player.color, (trade_x2 + 5, trade_y+55, 40,40))
            name = self.font_small.render("Вы", True, receiving_player.color)
            self.screen.blit(name, (trade_x2 + 50, trade_y+55))
            action = self.font_small.render(f"Отдаете", True, (0,0,0))
            self.screen.blit(action, (trade_x2 + 50, trade_y+75))

            # панель налички
            Text = self.font_small.render(f"Money", True, (0,255,0))
            self.screen.blit(Text, (trade_x + 5, trade_y + 100))
            Text = self.font_small.render(f"{trade_offer['offering_money']}", True, (0,255,0))
            self.screen.blit(Text, (trade_x + 60, trade_y + 100))

            Text = self.font_small.render(f"Money", True, (0,255,0))
            self.screen.blit(Text, (trade_x2 + 5, trade_y + 100))
            Text = self.font_small.render(f"{trade_offer['receiving_money']}", True, (0,255,0))
            self.screen.blit(Text, (trade_x2 + 5 + 60, trade_y + 100))

            # Список собственности
            y1 = trade_y + 130
            y2 = trade_y + 130
            self.total_money_give = trade_offer["offering_money"]
            self.total_money_requested = trade_offer["receiving_money"]
            # Список собственности
            for i, cell in enumerate(board):
                if trade_offer["offering_property"][i]:
                    rect = pygame.Rect(trade_x + 5, y1, 2*self.cell_size, 25)
                    text = self.font_small.render(cell["name"], True, (0, 0, 0))
                    self.screen.blit(text, rect)
                    rect = pygame.Rect(trade_x + 115, y1, 2*self.cell_size, 25)
                    if cell["Zalog"] is None:
                        money = self.font_small.render(f": {round(cell.get('price', 0))}$", True, (0, 0, 0))
                        self.total_money_give += cell["price"]
                    else: 
                        money = self.font_small.render(f": {round(cell.get('price', 0))/2}$", True, (255, 0, 0))
                        self.total_money_give += cell["price"]/2
                    self.screen.blit(money, rect)
                    y1 += 50
                elif trade_offer["receiving_property"][i]:
                    rect = pygame.Rect(trade_x2 + 5, y2, 2*self.cell_size, 25)
                    text = self.font_small.render(cell["name"], True, (0, 0, 0))
                    self.screen.blit(text, rect)
                    rect = pygame.Rect(trade_x2 + 115, y2, 2*self.cell_size, 25)
                    if cell["Zalog"] is None:
                        money = self.font_small.render(f": {round(cell.get('price', 0))}$", True, (0, 0, 0))
                        self.total_money_requested += cell["price"]
                    else: 
                        money = self.font_small.render(f": {round(cell.get('price', 0))/2}$", True, (255, 0, 0))
                        self.total_money_requested += cell["price"]/2
                    self.screen.blit(money, rect)
                    y2 += 50
            


            trade_y = trade_y + trade_height - 50

            Total = self.font_small.render(f"Всего", True, (0,0,0))
            self.screen.blit(Total, (trade_x + 5, trade_y - 20))
            Total = self.font_small.render(f"{self.total_money_give}", True, (0,0,0))
            self.screen.blit(Total, (trade_x + 60, trade_y - 20))

            Total = self.font_small.render(f"Всего", True, (0,0,0))
            self.screen.blit(Total, (trade_x2 + 5, trade_y - 20))
            Total = self.font_small.render(f"{self.total_money_requested}", True, (0,0,0))
            self.screen.blit(Total, (trade_x2 + 60, trade_y - 20))

            button_width = trade_width/3-20
            # Кнопки принятия/отклонения
            self.accept_trade_button = pygame.draw.rect(self.screen, (100, 200, 100), (trade_x+10,trade_y, button_width, 50))
            accept_text = self.font_small.render("Принять", True, (255, 255, 255))
            self.screen.blit(accept_text, accept_text.get_rect(center = self.accept_trade_button.center))
            
            self.decline_trade_button = pygame.draw.rect(self.screen, (200, 100, 100), (trade_x+10 + 2*button_width,trade_y, button_width, 50))
            decline_text = self.font_small.render("Отклонить", True, (255, 255, 255))
            self.screen.blit(decline_text, decline_text.get_rect(center = self.decline_trade_button.center))
    
    def draw_auction_menu(self, player, state, bid_input=""):
        """Отрисовка меню аукциона"""
        x = self.board_x + self.big_cell_size + self.prompt
        y = prostranstvo + self.big_cell_size + self.prompt

        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 9*self.cell_size - 2*self.prompt, 100), border_radius=5)
        # pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 9*self.cell_size, 100), 2)

        bid_text = self.font_medium.render(f"Текущая ставка: {state['current_bid']}$", True, (0, 0, 0))
        self.screen.blit(bid_text, bid_text.get_rect(center = pygame.draw.rect(self.screen, (255, 255, 255), (x, y, 9*self.cell_size - 2*self.prompt, 50)).center))

        self.pass_button = pygame.Rect(self.screen_width - 2*self.padding - self.big_cell_size - 10 - 3*self.cell_size - self.prompt, prostranstvo + self.big_cell_size + self.prompt +  50, 3*self.cell_size, 40)
        pygame.draw.rect(self.screen, (200,100,100), self.pass_button, border_radius=10)
        text2 = self.font_small.render("Отказаться", True, (0,0,0))
        self.screen.blit(text2, text2.get_rect(center=self.pass_button.center))

        input_box = pygame.Rect(self.board_x + self.big_cell_size + self.prompt + 10, prostranstvo + self.big_cell_size + self.prompt + 50, 3*self.cell_size, 40)
        pygame.draw.rect(self.screen, (255, 255, 255), input_box)
        pygame.draw.rect(self.screen, (0, 0, 0), input_box, 2)
        bid_text = self.font_small.render(bid_input, True, (0, 0, 0))
        self.screen.blit(bid_text, bid_text.get_rect(center = input_box.center))

        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, 9*self.cell_size - 2*self.prompt, 100), 2)
    
    def draw_trade_builder(self, player, board_cells, selected_properties, money_offer, players, target_id, selected_requested_properties, money_request, typing_trade_offer):
        trade_x = self.board_x + self.big_cell_size + self.prompt
        trade_y = prostranstvo + self.big_cell_size + self.prompt
        trade_width = 9*self.cell_size - 2*self.prompt
        trade_height = 9*self.cell_size - 2*self.prompt
        trade_x2 = trade_x + trade_width/2
        pygame.draw.rect(self.screen, (168,228,160), (trade_x, trade_y, trade_width,trade_height))
        
        # Заголовок
        target = next((p for p in players if p.id == target_id), None)
        if target:
            title = self.font_medium.render(f"Создание сделки с игроком {target.name}", True, (0, 0, 0))
            self.screen.blit(title, title.get_rect(center = pygame.draw.rect(self.screen, (168,228,160), (trade_x, trade_y, trade_width, 50)).center))

        # панели игроков
        pygame.draw.rect(self.screen, player.color, (trade_x + 5, trade_y + 55, 40,40))
        name = self.font_small.render(f"Вы", True, player.color)
        self.screen.blit(name, (trade_x + 50, trade_y+55))
        action = self.font_small.render(f"Предлагаете", True, (0,0,0))
        self.screen.blit(action, (trade_x + 50, trade_y+75))

        pygame.draw.rect(self.screen, target.color, (trade_x2 + 5, trade_y + 55, 40,40))
        name = self.font_small.render(f"{target.name}", True, target.color)
        self.screen.blit(name, (trade_x2 + 50, trade_y+55))
        action = self.font_small.render(f"Отдает", True, (0,0,0))
        self.screen.blit(action, (trade_x2 + 50, trade_y+75))

        # панель налички
        Text = self.font_small.render(f"Money", True, (0,255,0))
        self.screen.blit(Text, (trade_x + 5, trade_y + 100))
        input1_box = pygame.Rect(trade_x + 60, trade_y + 95, 2*self.cell_size, 20)
        pygame.draw.rect(self.screen, (255, 255, 255), input1_box)
        pygame.draw.rect(self.screen, (0, 255, 0) if typing_trade_offer else (0, 0, 0), input1_box, 2)
        offer_text = self.font_small.render(f"{money_offer}", True, (0, 0, 0))
        self.screen.blit(offer_text, offer_text.get_rect(left = input1_box.left + 5, centery = input1_box.centery))

        Text = self.font_small.render(f"Money", True, (0,255,0))
        self.screen.blit(Text, (trade_x2 + 5, trade_y + 100))
        input2_box = pygame.Rect(trade_x2 + 60, trade_y + 95, 2*self.cell_size, 20)
        pygame.draw.rect(self.screen, (255, 255, 255), input2_box)
        pygame.draw.rect(self.screen, (0, 255, 0) if not typing_trade_offer else (0, 0, 0), input2_box, 2)
        request_text = self.font_small.render(f"{money_request}", True, (0, 0, 0))
        self.screen.blit(request_text, request_text.get_rect(left = input2_box.left + 5, centery = input2_box.centery))

        # Список собственности
        y1 = trade_y + 130
        y2 = trade_y + 130
        self.total_money_give = money_offer
        self.total_money_requested = money_request
        # Список собственности
        for i, cell in enumerate(board_cells):
            if selected_properties[i]:
                rect = pygame.Rect(trade_x + 5, y1, 2*self.cell_size, 25)
                text = self.font_small.render(cell["name"], True, (0, 0, 0))
                self.screen.blit(text, rect)
                rect = pygame.Rect(trade_x + 115, y1, 2*self.cell_size, 25)
                if cell["Zalog"] is None:
                    money = self.font_small.render(f": {round(cell.get('price', 0))}$", True, (0, 0, 0))
                    self.total_money_give += cell["price"]
                else: 
                    money = self.font_small.render(f": {round(cell.get('price', 0))/2}$", True, (255, 0, 0))
                    self.total_money_give += cell["price"]/2
                self.screen.blit(money, rect)
                y1 += 20
            elif selected_requested_properties[i]:
                rect = pygame.Rect(trade_x2 + 5, y2, 2*self.cell_size, 25)
                text = self.font_small.render(cell["name"], True, (0, 0, 0))
                self.screen.blit(text, rect)
                rect = pygame.Rect(trade_x2 + 115, y2, 2*self.cell_size, 25)
                if cell["Zalog"] is None:
                    money = self.font_small.render(f": {round(cell.get('price', 0))}$", True, (0, 0, 0))
                    self.total_money_requested += cell["price"]
                else: 
                    money = self.font_small.render(f": {round(cell.get('price', 0))/2}$", True, (255, 0, 0))
                    self.total_money_requested += cell["price"]/2
                self.screen.blit(money, rect)
                y2 += 20

        trade_y = trade_y + trade_height - 50

        Total = self.font_small.render(f"Всего", True, (0,0,0))
        self.screen.blit(Total, (trade_x + 5, trade_y - 20))
        Total = self.font_small.render(f"{self.total_money_give}", True, (0,0,0))
        self.screen.blit(Total, (trade_x + 60, trade_y - 20))

        Total = self.font_small.render(f"Всего", True, (0,0,0))
        self.screen.blit(Total, (trade_x2 + 5, trade_y - 20))
        Total = self.font_small.render(f"{self.total_money_requested}", True, (0,0,0))
        self.screen.blit(Total, (trade_x2 + 60, trade_y - 20))

        self.can_send = (not(self.total_money_requested > 2*self.total_money_give or self.total_money_give > 2*self.total_money_requested))
        button_width = (trade_width-20)/3

        # Кнопка "Назад"
        back_button = pygame.Rect(trade_x+5, trade_y, button_width, 40)
        pygame.draw.rect(self.screen, (200, 100, 100), back_button)
        text = self.font_medium.render("Назад", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=back_button.center))

        reset_button = pygame.Rect(trade_x + button_width + 10, trade_y, button_width, 40)
        pygame.draw.rect(self.screen, (120, 120, 200), reset_button)
        text = self.font_medium.render("Сбросить", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=reset_button.center))

        # Кнопка "Отправить"
        send_button = pygame.Rect(trade_x + 2*button_width+15, trade_y, button_width, 40)
        pygame.draw.rect(self.screen, (100, 200, 100) if self.can_send else (150, 150, 150), send_button)
        text = self.font_small.render("Отправить сделку", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=send_button.center))

        # Сохраняем кнопки
        self.send_trade_button = send_button
        self.back_trade_button = back_button
        self.reset_trade_button = reset_button

    def draw_abilities_panel(self, player_id, abilities, ability_input):
	    
	    panel_x = self.board_x + self.big_cell_size + self.prompt
	    panel_y = prostranstvo + self.big_cell_size + self.prompt
	    width = 9*self.cell_size - 2*self.prompt
	    height = 9*self.cell_size - 2*self.prompt #len(abilities)*60 + 40

	    pygame.draw.rect(self.screen, (168,228,160), (panel_x, panel_y, width, height))
	    title = self.font_medium.render("Способности", True, (0, 0, 0))
	    self.screen.blit(title, title.get_rect(center = pygame.draw.rect(self.screen, (168,228,160), (panel_x, panel_y, width, self.cell_size)).center))

	    self.ability_buttons = []
	    for i, ab in enumerate(abilities):
	        y = panel_y + self.cell_size + i*60
	        name_text = self.font_small.render(f"{ab['name']} ({ab['count']})", True, (0, 0, 0))
	        price_text = self.font_small.render(f"{ab['price']}$", True, (0, 120, 0))
	        self.screen.blit(name_text, (panel_x + 10, y))
	        self.screen.blit(price_text, (panel_x + 10, y+30))

	        buy_btn = pygame.Rect(panel_x + 3.5*self.cell_size, y, 1.5*self.cell_size, 40)
	        pygame.draw.rect(self.screen, (100, 200, 100), buy_btn)
	        text = self.font_small.render("Купить", True, (255, 255, 255))
	        self.screen.blit(text, text.get_rect(center = buy_btn.center))
	        
	        use_btn = pygame.Rect(panel_x + 5.5*self.cell_size, y, 3*self.cell_size, 40)
	        pygame.draw.rect(self.screen, (100, 200, 100) if ab['count']>0 else (150, 150, 150), use_btn)
	        text = self.font_small.render("Использовать", True, (255, 255, 255))
	        self.screen.blit(text, text.get_rect(center = use_btn.center))

	        self.ability_buttons.append({
	            "name": ab["name"],
	            "buy": buy_btn,
	            "use": use_btn
	        })

	    # Кнопка "Назад"
	    back_button = pygame.Rect(panel_x + 10, panel_y + height - 50, 2*self.cell_size, 40)
	    pygame.draw.rect(self.screen, (200, 100, 100), back_button)
	    text = self.font_medium.render("Назад", True, (255, 255, 255))
	    self.screen.blit(text, text.get_rect(center=back_button.center))
	    self.back_trade_button = back_button

	    input1_box = pygame.Rect(panel_x + width - 5*self.cell_size, panel_y + height - 50, 4*self.cell_size, 40)
	    pygame.draw.rect(self.screen, (255, 255, 255), input1_box)
	    offer_text = self.font_small.render("Поле ввода" if ability_input == "" else f"{ability_input}", True, (0, 0, 0))
	    self.screen.blit(offer_text, offer_text.get_rect(left = input1_box.left + 5, centery = input1_box.centery))

    # def draw_game_end(self, winner):
    #     """Отрисовка экрана окончания игры"""
    #     # Полупрозрачный фон
    #     s = pygame.Surface((self.screen.get_width(), SCREEN_HEIGHT), pygame.SRCALPHA)
    #     s.fill((0, 0, 0, 128))
    #     self.screen.blit(s, (0, 0))
        
    #     # Окно победы
    #     pygame.draw.rect(self.screen, (255, 255, 255), (self.screen.get_width()//2 - 250, SCREEN_HEIGHT//2 - 150, 500, 300))
        
    #     # Сообщение о победе
    #     title = self.font_large.render("Игра окончена!", True, (0, 0, 0))
    #     self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 120))
        
    #     winner_text = self.font_medium.render(f"Победитель: {winner.name}", True, (0, 0, 0))
    #     self.screen.blit(winner_text, (self.screen.get_width()//2 - winner_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        
    #     # Кнопка возврата в лобби
    #     pygame.draw.rect(self.screen, (100, 100, 200), self.back_to_lobby_button)
    #     back_text = self.font_medium.render("Вернуться в лобби", True, (255, 255, 255))
    #     self.screen.blit(back_text, (self.back_to_lobby_button.x + 60, self.back_to_lobby_button.y + 15))