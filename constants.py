# Размеры экрана
SCREEN_WIDTH = 950
SCREEN_HEIGHT = 750
prostranstvo = 50
BG_COLOR = (240, 240, 240)

# Прочее
MAX_PLAYERS = 6
MIN_PLAYERS = 2

# Цвета игроков
PLAYER_COLORS = [
    (255, 0, 0),    # Красный
    (0, 0, 255),    # Синий
    (0, 255, 0),    # Зеленый
    (255, 255, 0),  # Желтый
    (255, 0, 255),  # Розовый
    (0, 255, 255),  # Голубой
]

# Шрифты
FONT_SMALL = None
FONT_MEDIUM = None
FONT_LARGE = None

# Игровое поле
BOARD1 = [
    {"name" : "Старт",           "type" : "start",   "price" : 0,  "color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 1",    "type" : "property","price" : 50, "color" : (241,131,235), "color_owner" : None,   "level" : 0,"rent" : 5, "owner" : None,"category" : "1", "category_name" : "Духи", "Zalog" : None},
    {"name" : "Вопрос",          "type" : "quest",   "price" : 0,  "color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 2",    "type" : "property","price" : 60, "color" : (241,131,235), "color_owner" : None,   "level" : 0,"rent" : 6, "owner" : None,"category" : "1", "category_name" : "Духи", "Zalog" : None},
    {"name" : "Подоходный налог","type" : "tax",     "price" : 200,"color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Машинки 1",       "type" : "cars",    "price" : 200,"color" : (104,49,191),  "color_owner" : None,   "level" : 0,"rent" : 25,"owner" : None,"category" : "0", "category_name" : "cars", "Zalog" : None},
    {"name" : "Преприятие 3",    "type" : "property","price" : 100,"color" : (158,131,241), "color_owner" : None,   "level" : 0,"rent" : 10,"owner" : None,"category" : "2", "category_name" : "Фастфуд", "Zalog" : None},
    {"name" : "Вопрос",          "type" : "quest",   "price" : 0,  "color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 4",    "type" : "property","price" : 110,"color" : (158,131,241), "color_owner" : None,   "level" : 0,"rent" : 11,"owner" : None,"category" : "2", "category_name" : "Фастфуд", "Zalog" : None},
    {"name" : "Преприятие 5",    "type" : "property","price" : 130,"color" : (158,131,241), "color_owner" : None,   "level" : 0,"rent" : 13,"owner" : None,"category" : "2", "category_name" : "Фастфуд", "Zalog" : None},
    {"name" : "Тюрьма",          "type" : "jail",    "price" : 0,  "color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 6",    "type" : "property","price" : 150,"color" : (235,92,95),   "color_owner" : None,   "level" : 0,"rent" : 15,"owner" : None,"category" : "3", "category_name" : "Мессенджер", "Zalog" : None},
    {"name" : "Игры 1",          "type" : "utility", "price" : 150,"color" : (251,99,19),   "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : "Game", "Zalog" : None},
    {"name" : "Преприятие 7",    "type" : "property","price" : 170,"color" : (235,92,95),   "color_owner" : None,   "level" : 0,"rent" : 17,"owner" : None,"category" : "3", "category_name" : "Мессенджер", "Zalog" : None},
    {"name" : "Преприятие 8",    "type" : "property","price" : 190,"color" : (235,92,95),   "color_owner" : None,   "level" : 0,"rent" : 19,"owner" : None,"category" : "3", "category_name" : "Мессенджер", "Zalog" : None},
    {"name" : "Машинки 2",       "type" : "cars",    "price" : 200,"color" : (104,49,191),  "color_owner" : None,   "level" : 0,"rent" : 25,"owner" : None,"category" : "0", "category_name" : "cars", "Zalog" : None},
    {"name" : "Преприятие 9",    "type" : "property","price" : 200,"color" : (82,209,100),  "color_owner" : None,   "level" : 0,"rent" : 20,"owner" : None,"category" : "4", "category_name" : "Смартфон", "Zalog" : None},
    {"name" : "Вопрос",          "type" : "quest",   "price" : 0,  "color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 10",   "type" : "property","price" : 210,"color" : (82,209,100),  "color_owner" : None,   "level" : 0,"rent" : 21,"owner" : None,"category" : "4", "category_name" : "Смартфон", "Zalog" : None},
    {"name" : "Преприятие 11",   "type" : "property","price" : 240,"color" : (82,209,100),  "color_owner" : None,   "level" : 0,"rent" : 24,"owner" : None,"category" : "4", "category_name" : "Смартфон", "Zalog" : None},
    {"name" : "Казино",          "type" : "casino",  "price" : 0,  "color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 12",   "type" : "property","price" : 250,"color" : (49,190,196),  "color_owner" : None,   "level" : 0,"rent" : 25,"owner" : None,"category" : "5", "category_name" : "Киберспорт", "Zalog" : None},
    {"name" : "Вопрос",          "type" : "quest",   "price" : 0,  "color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 13",   "type" : "property","price" : 270,"color" : (49,190,196),  "color_owner" : None,   "level" : 0,"rent" : 27,"owner" : None,"category" : "5", "category_name" : "Киберспорт", "Zalog" : None},
    {"name" : "Преприятие 14",   "type" : "property","price" : 280,"color" : (49,190,196),  "color_owner" : None,   "level" : 0,"rent" : 28,"owner" : None,"category" : "5", "category_name" : "Киберспорт", "Zalog" : None},
    {"name" : "Машинки 3",       "type" : "cars",    "price" : 200,"color" : (104,49,191),  "color_owner" : None,   "level" : 0,"rent" : 25,"owner" : None,"category" : "0", "category_name" : "cars", "Zalog" : None},
    {"name" : "Преприятие 15",   "type" : "property","price" : 300,"color" : (231,235,112), "color_owner" : None,   "level" : 0,"rent" : 30,"owner" : None,"category" : "6", "category_name" : "Нейросеть", "Zalog" : None},
    {"name" : "Преприятие 16",   "type" : "property","price" : 320,"color" : (231,235,112), "color_owner" : None,   "level" : 0,"rent" : 32,"owner" : None,"category" : "6", "category_name" : "Нейросеть", "Zalog" : None},
    {"name" : "Игры 2",          "type" : "utility", "price" : 150,"color" : (251,99,19),   "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : "Game", "Zalog" : None},
    {"name" : "Преприятие 17",   "type" : "property","price" : 330,"color" : (231,235,112), "color_owner" : None,   "level" : 0,"rent" : 33,"owner" : None,"category" : "6", "category_name" : "Нейросеть", "Zalog" : None},
    {"name" : "Идите в тюрьму",  "type" : "gotojail","price" : 0,  "color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 18",   "type" : "property","price" : 350,"color" : (6,64,132),    "color_owner" : None,   "level" : 0,"rent" : 35,"owner" : None,"category" : "7", "category_name" : "Банк", "Zalog" : None},
    {"name" : "Преприятие 19",   "type" : "property","price" : 360,"color" : (6,64,132),    "color_owner" : None,   "level" : 0,"rent" : 36,"owner" : None,"category" : "7", "category_name" : "Банк", "Zalog" : None},
    {"name" : "Вопрос",          "type" : "quest",   "price" : 0,  "color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 20",   "type" : "property","price" : 380,"color" : (6,64,132),    "color_owner" : None,   "level" : 0,"rent" : 38,"owner" : None,"category" : "7", "category_name" : "Банк", "Zalog" : None},
    {"name" : "Машинки 4",       "type" : "cars",    "price" : 200,"color" : (104,49,191),  "color_owner" : None,   "level" : 0,"rent" : 25,"owner" : None,"category" : "0", "category_name" : "cars", "Zalog" : None},
    {"name" : "Налог на роскошь","type" : "tax",     "price" : 100,"color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 21",   "type" : "property","price" : 400,"color" : (148,148,148), "color_owner" : None,   "level" : 0,"rent" : 40,"owner" : None,"category" : "8", "category_name" : "Крипта", "Zalog" : None},
    {"name" : "Вопрос",          "type" : "quest",   "price" : 100,"color" : None,          "color_owner" : None,   "level" : 0,"rent" : 0, "owner" : None,"category" : "0", "category_name" : None, "Zalog" : None},
    {"name" : "Преприятие 22",   "type" : "property","price" : 450,"color" : (148,148,148), "color_owner" : None,   "level" : 0,"rent" : 45,"owner" : None,"category" : "8", "category_name" : "Крипта", "Zalog" : None}
]

RENT_MULTIPLIERS = [0.1, 0.5, 1, 2, 3, 4]
# залог = 1/2 (0.5), выкуп = 3/5 (0.6), прокачка 1/2 (0.5)

QUESTIONS = [
    {"question": "Столица Франции?", "answer": "париж", "reward": 100},
    {"question": "5 + 7 = ?", "answer": "12", "reward": 80},
    {"question": "Цвет неба в ясный день?", "answer": "синий", "reward": 50},
    {"question": "Python — это язык ...?", "answer": "программирования", "reward": 70},
]

# Порты и настройки сети
SERVER_PORT = 5555
BUFFER_SIZE = 4096