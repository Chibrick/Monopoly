import pygame
import os
import random
import math
from constants import *

class Board:
    def __init__(self, board_data):
        self.font_small = pygame.font.SysFont(None, 24)
        self.cells = board_data
        self.update_dimensions((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.cell_surfaces = {}
        self.scale_x = 1.0
        self.scale_y = 1.0

        for i, cell in enumerate(self.cells):
            image_path = cell.get("image")
            if image_path:
                try:
                    surface = pygame.image.load(image_path).convert_alpha()
                    max_width = 128
                    # при необходимости масштабируй сразу
                    if surface.get_width() > max_width:
                        scale = max_width / surface.get_width()
                        surface = pygame.transform.smoothscale(surface, (
                            int(surface.get_width() * scale),
                            int(surface.get_height() * scale)
                        ))
                    self.cell_surfaces[i] = surface
                except Exception as e:
                    print(f"[!] Ошибка загрузки {image_path}: {e}")
                    self.cell_surfaces[i] = None
            else:
                self.cell_surfaces[i] = None

        try:
            category_path = "images/General"
            image_files = [f for f in os.listdir(category_path) if f.lower().endswith(".png") and f.lower().startswith("звезда")]

            if image_files:
                selected = random.choice(image_files)
                self.star_image = os.path.join(category_path, selected)
                try:
                    surface = pygame.image.load(self.star_image).convert_alpha()
                    max_width = 128
                    # при необходимости масштабируй сразу
                    if surface.get_width() > max_width:
                        scale = max_width / surface.get_width()
                        surface = pygame.transform.smoothscale(surface, (
                            int(surface.get_width() * scale),
                            int(surface.get_height() * scale)
                        ))
                    self.star_image = surface
                except Exception as e:
                    print(f"[!] Ошибка загрузки {image_path}: {e}")
                    self.star_image = None
            else:
                self.star_image = None
        except FileNotFoundError:
            print(f"[assign_cell_images_and_names] Папка не найдена: {category_path}")
            self.star_image = None


    def update_dimensions(self, screen_size):
        screen_width, screen_height = screen_size
        self.scale_x = screen_width / SCREEN_WIDTH
        self.scale_y = screen_height / SCREEN_HEIGHT
        self.board_width = min(int(self.scale_x * 650), int(self.scale_y * 650))
        sidebar_width = min(int(self.scale_x * 200),400)
        padding = (screen_width - self.board_width - sidebar_width - prostranstvo)/3

        self.cell_size = self.board_width // 13
        self.big_cell_size = 2*self.cell_size
        self.board_height = self.board_width

        self.board_x = padding + sidebar_width + prostranstvo
        self.board_y = prostranstvo

    def update_from_data(self, board_data):
        self.cells = board_data

    def draw(self, screen):
        self.update_dimensions(screen.get_size())
        for i, cell in enumerate(self.cells):
            self.draw_cell(screen, i, cell, False)

    def draw_cell(self, screen, index, cell, highlighte):
        # row = index // 10
        # col = index % 10

        corner_cells = {0, 10, 20, 30}  # Пример для 40 клеток
        
        # Определяем, является ли клетка угловой
        is_corner = index in corner_cells
        
        # Рассчитываем позицию клетки
        if index == 0:  # Старт (левый верхний угол)
            x = self.board_x
            y = self.board_y
            width = self.big_cell_size
            height = self.big_cell_size
        elif index < 10:  # верхняя грань (слева направо)
            x = self.board_x + self.big_cell_size + (index-1)*self.cell_size
            y = self.board_y
            width = self.cell_size
            height = self.big_cell_size
        elif index == 10:  # Тюрьма (правый верхний угол)
            x = self.board_x + self.big_cell_size + 9*self.cell_size
            y = self.board_y
            width = self.big_cell_size
            height = self.big_cell_size
        elif index < 20:  # Правая грань (сверху вниз)
            x = self.board_x + self.big_cell_size + 9*self.cell_size
            y = self.board_y + self.big_cell_size + (index-11)*self.cell_size
            width = self.big_cell_size
            height = self.cell_size
        elif index == 20:  # Парковка (правый нижний угол)
            x = self.board_x + self.big_cell_size + 9*self.cell_size
            y = self.board_y + self.big_cell_size + 9*self.cell_size
            width = self.big_cell_size
            height = self.big_cell_size
        elif index < 30:  # Нижняя грань (справа налево)
            x = self.board_x + self.big_cell_size + (29-index)*self.cell_size
            y = self.board_y + self.big_cell_size + 9*self.cell_size
            width = self.cell_size
            height = self.big_cell_size
        elif index == 30:  # "Идите в тюрьму" (левый нижний угол)
            x = self.board_x
            y = self.board_y + self.big_cell_size + 9*self.cell_size
            width = self.big_cell_size
            height = self.big_cell_size
        else:  # Левая грань (снизу вверх)
            x = self.board_x
            y = self.board_y + self.big_cell_size + (39-index)*self.cell_size
            width = self.big_cell_size
            height = self.cell_size

        colori = [255,255,255]
        if (cell["color_owner"] is not None):
            for i in [0,1,2]:
                colori[i] = cell["color_owner"][i]
                if colori[i] == 0:
                    colori[i] = 150 
            cell["color_owner"] = (colori[0],colori[1],colori[2])
        ownercolor = cell["color_owner"] if (cell["color_owner"] is not None) else (255,255,255)
        Kletka = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, ownercolor, Kletka)
        pygame.draw.rect(screen, (0, 0, 0), Kletka, 1)

        # Изображение
        if cell["image"] is not None:
            image = self.cell_surfaces.get(index)
            img_rect = image.get_rect()

            # Вычисляем масштаб по максимальному размеру, сохраняя пропорции
            if width>height:
                if (img_rect.width+5)<img_rect.height:
                    rotate = -90 if index <20 else (90)
                    image = pygame.transform.rotate(image, rotate)
                    img_rect = image.get_rect()
            elif width<height:
                if img_rect.width>(img_rect.height+5):
                    rotate = -90 if index <20 else 90
                    image = pygame.transform.rotate(image, rotate)
                    img_rect = image.get_rect()

            scale_w = width / img_rect.width
            scale_h = height / img_rect.height
            scale = min(scale_w, scale_h)

            new_width = int(img_rect.width * scale)*0.9
            new_height = int(img_rect.height * scale)*0.9

            image = pygame.transform.smoothscale(image, (new_width, new_height))

            # Центрируем внутри клетки
            offset_x = x + (width - new_width) // 2
            offset_y = y + (height - new_height) // 2

            screen.blit(image, (offset_x, offset_y))

        if cell["Zalog"] is not None:
            pygame.draw.line(screen, (246,96,108), [x, y], [x+width, y+height],3)
            pygame.draw.line(screen, (246,96,108), [x, y+height], [x+width, y],3)
            pygame.draw.circle(screen, (246,96,108), Kletka.center, 15)
            zalog_text = self.font_small.render(str(round(cell.get("Zalog",""))), True, (0, 0, 0))
            screen.blit(zalog_text, zalog_text.get_rect(center = Kletka.center))

        if highlighte:
            # Пульсирующая прозрачность
            time_now = pygame.time.get_ticks() / 1000  # секунды
            alpha = int(192 + 63 * math.sin(time_now * 2))  # значение от 1 до 255
            beta = int(15 - 5 * math.sin(time_now * 2))
            highlight_color = [random.randint(50, 100) for _ in range(3)]
            color = (*highlight_color, alpha)

            # Создаем прозрачную поверхность
            highlight_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surf, color, (0, 0, width, height), beta)
            screen.blit(highlight_surf, (x, y))
            
            # pygame.draw.rect(screen, (255, 255, 0), (x, y, width, height))

        # Изображение звезды
        if cell["level"] > 0:
            image = self.star_image
            img_rect = image.get_rect()
            if width < height:
                scale = (width/4) / img_rect.width
            elif height < width:
                scale = (height/4) / img_rect.height

            new_width = (img_rect.width * scale)
            new_height = (img_rect.height * scale)

            if cell["level"] < 5:
                image = pygame.transform.smoothscale(image, (new_width, new_height))
                for star in range(cell["level"]):
                    if index<10:
                        offset_x = x + star * new_width
                        offset_y = y + self.big_cell_size - new_width
                    elif index<20:
                        offset_x = x
                        offset_y = y + star * new_width
                    elif index<30:
                        offset_x = x + star * new_width
                        offset_y = y
                    elif index<40:
                        offset_x = x + self.big_cell_size - new_width
                        offset_y = y + self.cell_size - (star+1) * new_width
                    screen.blit(image, (offset_x, offset_y))
            else:
                if index<10:
                    offset_x = x + new_width
                    offset_y = y + self.big_cell_size - new_width*2
                elif index<20:
                    offset_x = x
                    offset_y = y + new_width
                elif index<30:
                    offset_x = x + new_width
                    offset_y = y
                elif index<40:
                    offset_x = x + self.big_cell_size - new_width*2
                    offset_y = y + new_width
                new_width *= 2
                new_height *= 2
                image = pygame.transform.smoothscale(image, (new_width, new_height))
                screen.blit(image, (offset_x, offset_y))

        # прямоугольник рядом с предприятиями
        if cell['type'] == "property" or cell['type'] == "cars" or cell['type'] == "utility":
            step = 25
            if index<10:
                y -= step
                height = step
                rotate = 0
            elif index<20:
                x += self.big_cell_size
                width = step
                rotate = -90
            elif index<30:
                y += self.big_cell_size
                height = step
                rotate = 0
            else:
                x -= step
                width = step
                rotate = 90
            # Цвет клетки
            color = cell["color"] if cell["color"] else (230, 230, 230)
            pygame.draw.rect(screen, color, (x, y, width, height))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height), 1)
            if cell['owner'] is None:
                cost = self.font_small.render(str(round(cell.get("price", ""))), True, (0, 0, 0))
            else:
                if cell['type'] == "utility":
                    cost = self.font_small.render(f"*{str(round(cell.get('rent', '')))}", True, (0, 0, 0))
                else:
                    cost = self.font_small.render(str(round(cell.get("rent", ""))), True, (0, 0, 0))
            cost = pygame.transform.rotate(cost, rotate)
            screen.blit(cost, cost.get_rect(center=pygame.Rect(x, y, width, height).center))

    def draw_player(self, screen, player, players):
        if player.bankrupt:
            return

        index = player.position

        corner_cells = {0, 10, 20, 30}  # Пример для 40 клеток
        
        # Определяем, является ли клетка угловой
        is_corner = index in corner_cells
        # Рассчитываем позицию клетки
        if index == 0:  # Старт (левый верхний угол)
            x = self.board_x
            y = self.board_y
            another = 0
        elif index < 10:  # верхняя грань (слева направо)
            x = self.board_x + self.big_cell_size + (index-1)*self.cell_size
            y = self.board_y
            another = 1
        elif index == 10:  # Тюрьма (правый верхний угол)
            x = self.board_x + self.big_cell_size + 9*self.cell_size
            y = self.board_y
            another = 0
        elif index < 20:  # Правая грань (сверху вниз)
            x = self.board_x + self.big_cell_size + 9*self.cell_size
            y = self.board_y + self.big_cell_size + (index-11)*self.cell_size
            another = 2
        elif index == 20:  # Парковка (правый нижний угол)
            x = self.board_x + self.big_cell_size + 9*self.cell_size
            y = self.board_y + self.big_cell_size + 9*self.cell_size
            another = 0
        elif index < 30:  # Нижняя грань (справа налево)
            x = self.board_x + self.big_cell_size + (29-index)*self.cell_size
            y = self.board_y + self.big_cell_size + 9*self.cell_size
            another = 1
        elif index == 30:  # "Идите в тюрьму" (левый нижний угол)
            x = self.board_x
            y = self.board_y + self.big_cell_size + 9*self.cell_size
            another = 0
        else:  # Левая грань (снизу вверх)
            x = self.board_x
            y = self.board_y + self.big_cell_size + (39-index)*self.cell_size
            another = 2

        # Несколько игроков на одной клетке — разносим
        same_pos_players = [p for p in players if p.position == index and not p.bankrupt]
        player_index = same_pos_players.index(player)

        Razmer = round(self.cell_size / 6)
        Otstup = round((Razmer*2)/3)

        if another == 1:
            offset_x = Razmer + Otstup + (player_index % 2) * (Razmer*2 + Otstup)
            offset_y = Razmer + Otstup + (player_index // 2) * (Razmer*2 + Otstup*3)
        elif another == 2: 
            offset_x = Razmer + Otstup + (player_index % 3) * (Razmer*2 + Otstup*3)
            offset_y = Razmer + Otstup + (player_index // 3) * (Razmer*2 + Otstup)
        else:
            Razmer *= 1.5
            offset_x = Razmer + Otstup + (player_index % 3) * (Razmer*2 + Otstup*2)
            offset_y = Razmer + Otstup + (player_index // 3) * (Razmer*2 + Otstup*2)

        pygame.draw.circle(screen, player.color,
                           (x + offset_x, y + offset_y), Razmer)
        pygame.draw.circle(screen, (0,0,0),
                           (x + offset_x, y + offset_y), Razmer, round(Razmer/10*3))
        # pygame.draw.circle(screen, (255,255,255),
        #                    (x + offset_x, y + offset_y), Razmer-1, 1)

    def get_cell_at_pos(self, pos):
        x, y = pos

        if (self.board_x <= x <= self.board_x + self.board_width and
            self.board_y <= y <= self.board_y + self.board_height):

            if (self.board_x + self.big_cell_size <= x <= self.board_x + self.big_cell_size + 9*self.cell_size and
                self.board_y + self.big_cell_size <= y <= self.board_y + self.big_cell_size + 9*self.cell_size):
                return None

            elif (self.board_y <= y <= self.board_y + self.big_cell_size):
                if (self.board_x <= x <= self.board_x + self.big_cell_size):
                    index = 0
                elif (self.board_x + self.big_cell_size + 9*self.cell_size <= x <= self.board_x + 2*self.big_cell_size + 9*self.cell_size):
                    index = 10
                else:
                    index = int((x - self.board_x - self.cell_size) // self.cell_size)

            elif (self.board_y + self.big_cell_size + 9*self.cell_size <= y <= self.board_y + 2*self.big_cell_size + 9*self.cell_size):
                if (self.board_x <= x <= self.board_x + self.big_cell_size):
                    index = 30
                elif (self.board_x + self.big_cell_size + 9*self.cell_size <= x <= self.board_x + 2*self.big_cell_size + 9*self.cell_size):
                    index = 20
                else:
                    index = 30 - int((x - self.board_x - self.cell_size) // self.cell_size)

            else:
                if (self.board_x <= x <= self.board_x + self.big_cell_size):
                    index = 40 - int((y - self.board_y - self.cell_size) // self.cell_size) 
                else:
                    index = 10 + int((y - self.board_y - self.cell_size) // self.cell_size) 

            if 0 <= index < len(self.cells):
                return index
        return None
