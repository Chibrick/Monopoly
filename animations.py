import pygame
import random
from constants import *

class Animation:
    def __init__(self, screen, board):
        self.screen = screen
        self.board = board  # добавляем board
        self.dice_images = []
        self.load_dice_images()
        pygame.mixer.init()
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

    def load_dice_images(self):
        """Загрузка изображений кубиков"""
        for i in range(1, 7):
            try:
                image = pygame.image.load(f"images/dice_{i}.png")
                self.dice_images.append(image)
            except:
                # Если изображений нет, создаем простые кубики
                surf = pygame.Surface((50, 50))
                surf.fill((255, 255, 255))
                pygame.draw.rect(surf, (0, 0, 0), (0, 0, 50, 50), 2)
                
                # Точки на кубиках
                dots = {
                    1: [(25, 25)],
                    2: [(15, 15), (35, 35)],
                    3: [(15, 15), (25, 25), (35, 35)],
                    4: [(15, 15), (15, 35), (35, 15), (35, 35)],
                    5: [(15, 15), (15, 35), (25, 25), (35, 15), (35, 35)],
                    6: [(15, 15), (15, 35), (25, 15), (25, 35), (35, 15), (35, 35)]
                }
                
                for dot in dots[i]:
                    pygame.draw.circle(surf, (0, 0, 0), dot, 5)
                
                self.dice_images.append(surf)
    
    def draw_dice_animation(self, player, dice_result):
	    """Анимация броска кубиков с вращением и результатом"""
	    clock = pygame.time.Clock()

	    # Длительность броска: 0.6 сек
	    roll_duration = 600  # миллисекунд
	    start_time = pygame.time.get_ticks()

	    roll_sounds = [
	        pygame.mixer.Sound("sounds/dice_roll.wav")
	    ]
	    random.choice(roll_sounds).play()

	    while pygame.time.get_ticks() - start_time < roll_duration:
	        # Случайные значения
	        r1 = random.randint(1, 6)
	        r2 = random.randint(1, 6)

	        self._draw_dice_window(r1, r2, text="Бросаем кубики...")
	        pygame.display.flip()
	        clock.tick(30)

	    # Финальное выпадение
	    final1 = dice_result["dice1"]
	    final2 = dice_result["dice2"]
	    self._draw_dice_window(final1, final2, text="Выпало:")
	    pygame.display.flip()

	    # Пауза перед движением
	    pygame.time.delay(1000)
    
    def _draw_dice_window(self, dice1, dice2, text=""):
        # Кубиковое окно
        pygame.draw.rect(self.screen, (170, 170, 170), (self.board_x + self.big_cell_size + 2*self.cell_size, prostranstvo + self.big_cell_size + 3*self.cell_size, 5*self.cell_size, 3*self.cell_size), border_radius=15)
        self.screen.blit(self.dice_images[dice1 - 1], (self.board_x + self.big_cell_size + 3*self.cell_size, prostranstvo + self.big_cell_size + 4.5*self.cell_size))
        self.screen.blit(self.dice_images[dice2 - 1], (self.board_x + self.big_cell_size + 5*self.cell_size, prostranstvo + self.big_cell_size + 4.5*self.cell_size))

        # Белая зона под текст
        text_box = pygame.Rect(self.board_x + self.big_cell_size + 2*self.cell_size, prostranstvo + self.big_cell_size + 3*self.cell_size, 5*self.cell_size, self.cell_size)

        # Текст
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, text_surface.get_rect(center=text_box.center))

    def draw_player_move(self, player, start_pos, end_pos, steps):
        """Плавная анимация перемещения игрока по клеткам"""
        clock = pygame.time.Clock()
        path = [(start_pos + i) % len(BOARD1) for i in range(1, steps + 1)]
        frozen_ui = self.screen.copy()
        for intermediate_pos in path:
            player.position = intermediate_pos
            self.screen.blit(frozen_ui, (0, 0))
            for _ in range(10):  # 6 кадров на каждую клетку (~100ms при 60fps)
                self.board.draw_player(self.screen, player, [player])
                pygame.display.flip()
                clock.tick(60)  # 60 кадров в секунду