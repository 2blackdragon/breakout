import math
from os import path
import pygame
import sqlite3

# Используемые цвета
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
YELLOW = pygame.Color('yellow')
GREEN = pygame.Color('green')
ORANGE = pygame.Color('orange')
RED = pygame.Color('red')
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

# Размеры блока
block_width = 60
block_height = 20

# Инициализация pygame
pygame.init()

# Размеры экрана
screen_width = 870
screen_height = 550

screen = pygame.display.set_mode((screen_width, screen_height))
screen.fill(BLACK)
pygame.display.set_caption('Breakout')

play_game_over = False
running = True
running2 = False
game_over = False
life = 3
score = 0
count = 0  # счётчик попаданий
count_of_red = 0  # счётчик попаданий в красные блоки
count_of_orange = 0  # счётчик попаданий в оранжевые блоки
font = pygame.font.Font(None, 24)
font_for_game_over = pygame.font.Font(None, 40)
game_over_text = font_for_game_over.render('', True, WHITE)
clock = pygame.time.Clock()
snd_dir = path.join(path.dirname(__file__), 'sounds')
pygame.mouse.set_visible(False)  # убираем курсор


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.name = ''
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.name = self.text
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Block(pygame.sprite.Sprite):
    def __init__(self, block_color, x, y):
        super().__init__()
        self.color = block_color

        self.image = pygame.Surface([block_width, block_height])
        self.image.fill(self.color)
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, x, y):
        super().__init__()
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, WHITE,
                           (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)

        self.speed = 10
        self.direction = 140

    def update(self):
        direction_radians = math.radians(self.direction)
        self.rect.x += self.speed * math.sin(direction_radians)
        self.rect.y -= self.speed * math.cos(direction_radians)

        # Проверка на столкновение с рамками
        if self.rect.y <= 0:
            self.direction = (180 - self.direction) % 360
            self.rect.y = 1
        if self.rect.x <= 0:
            self.direction = (360 - self.direction) % 360
            self.rect.x = 1
        if self.rect.x > screen_width - 2 * self.radius:
            self.direction = (360 - self.direction) % 360
            self.rect.x = screen_width - 2 * self.radius - 1


class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()

        self.width = width
        self.height = height
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(WHITE)

        self.rect = self.image.get_rect()

        self.rect.x = 0
        # 40 пикселей - место для текста о кол-ве жизней и счёте
        self.rect.y = screen_height - self.height - 40

    def update(self):
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(WHITE)
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0]
        if self.rect.x > screen_width - self.width:
            self.rect.x = screen_width - self.width


# Группы спрайтов
blocks = pygame.sprite.Group()
balls = pygame.sprite.Group()
allsprites = pygame.sprite.Group()

# Платформа
platform = Platform(150, 15)
allsprites.add(platform)

# Мяч
ball = Ball(10, 100, 250)
allsprites.add(ball)
balls.add(ball)

# Мелодии
bounce_sound = pygame.mixer.Sound(path.join(snd_dir, 'bounce.wav'))
game_over_sound = pygame.mixer.Sound(path.join(snd_dir, 'game_over.wav'))

# Отступ от верхней грани до блоков
top = 50

# Отрисовываем блоки
for i in range(8):
    for j in range(14):
        if i == 0 or i == 1:
            color = RED
        elif i == 2 or i == 3:
            color = ORANGE
        elif i == 4 or i == 5:
            color = GREEN
        else:
            color = YELLOW
        block = Block(color, j * (block_width + 2) + 2, top)
        blocks.add(block)
        allsprites.add(block)
    top += block_height + 2

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running2 = True
            running = False

    if game_over:
        if play_game_over:
            game_over_sound.play()
            play_game_over = False
        game_over_text = font_for_game_over.render('Game over', True, WHITE)
        pygame.mouse.set_visible(True)  # возвращаем курсор
    else:
        # Проверка на завершение игры
        if life == 0:
            game_over = True
            play_game_over = True

        # Если мяч упал ниже платформы
        if ball.rect.y >= screen_height - 40:
            speed = ball.speed
            ball.kill()
            if life > 0:
                life -= 1
            if life != 0:
                ball = Ball(10, 100, 250)
                ball.speed = speed
                allsprites.add(ball)
                balls.add(ball)

        # Столкновение с платформой
        if pygame.sprite.spritecollide(platform, balls, False):
            diff = (platform.rect.x + platform.width / 2) - (ball.rect.x + ball.radius)
            ball.direction = (180 - ball.direction) % 360 - diff

        # Убираем блок/блоки, в который/которые попал мяч
        deadblocks = pygame.sprite.spritecollide(ball, blocks, True)

        # Считаем попадания
        if deadblocks:
            bounce_sound.play()
            ball.direction = (180 - ball.direction) % 360
            for i in range(len(deadblocks)):
                count += 1
                if deadblocks[i].color == (255, 0, 0, 255):
                    count_of_red += 1
                if deadblocks[i].color == (255, 165, 0, 255):
                    count_of_orange += 1
                # Увеличение скорости мяча
                if count == 4 or count == 12 or count_of_red == 1 or count_of_orange == 1:
                    ball.speed += 2
                    if count_of_orange == 1:
                        count_of_orange += 1  # счётчик нам больше не пригодится,
                        # чтобы избежать неправильного подсчёта скорости, добавим 1
                    if count_of_red == 1:
                        count_of_red += 1  # делаем тоже самое, что и с счётчиком оранжевых блоков
                        # Укорачиваем платформу
                        x = platform.rect.x + platform.rect.width // 4
                        platform.kill()
                        platform = Platform(75, 15)
                        platform.rect.x = x
                        allsprites.add(platform)

            # Начисление очков
            for i in deadblocks:
                if i.color == (255, 255, 0, 255):  # жёлтый блок
                    score += 1
                if i.color == (0, 255, 0, 255):  # зелённый блок
                    score += 3
                if i.color == (255, 165, 0, 255):  # оранжевый блок
                    score += 5
                if i.color == (255, 0, 0, 255):  # красный блок
                    score += 7

            # Если первый экран блоков пройлен
            if len(blocks) == 0 and count == 8 * 14:
                # Убираем старый шарик и создаём новый
                speed = ball.speed
                ball.kill()
                ball = Ball(10, 100, 250)
                ball.speed = speed
                allsprites.add(ball)
                balls.add(ball)

                # Отступ от верхней грани до блоков
                top = 50

                # Отрисовываем блоки
                for i in range(8):
                    for j in range(14):
                        if i == 0 or i == 1:
                            color = RED
                        elif i == 2 or i == 3:
                            color = ORANGE
                        elif i == 4 or i == 5:
                            color = GREEN
                        else:
                            color = YELLOW
                        block = Block(color, j * (block_width + 2) + 2, top)
                        blocks.add(block)
                        allsprites.add(block)
                    top += block_height + 2
            # Если пройдено 2 экрана с блоками
            elif len(blocks) == 0:
                game_over = True
                play_game_over = True

    life_text = font.render(f"Жизни: {life}", True, WHITE)
    score_text = font.render(f"Счёт: {score}", True, WHITE)
    screen.fill(BLACK)
    clock.tick(30)
    allsprites.draw(screen)
    allsprites.update()
    screen.blit(life_text, (50, screen_height - 30))
    screen.blit(score_text, (175, screen_height - 30))
    screen.blit(game_over_text, (screen_width // 2 - 80, screen_height // 2 - 20))
    pygame.display.flip()

# Запрашиваем у игрока имя
screen = pygame.display.set_mode((500, 200))
screen.fill(BLACK)
pygame.display.set_caption('Breakout')
input_box = pygame.Rect(150, 85, 100, 30)
name_text = font.render("Введите имя игрока:", True, WHITE)
active = False
text = ''
rect_color = COLOR_INACTIVE
database = sqlite3.connect("top_players.db")
cur = database.cursor()

while running2:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running2 = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            rect_color = COLOR_ACTIVE if active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    # Заносим имя в БД
                    if text and score:
                        cur.execute(f"INSERT INTO top(player_name, score) "
                                    f"VALUES('{text}', {score})")
                    database.commit()
                    text = ''
                    running2 = False
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
    screen.fill(BLACK)
    txt_surface = font.render(text, True, rect_color)
    width = max(200, txt_surface.get_width() + 10)
    input_box.w = width
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, rect_color, input_box, 2)
    screen.blit(name_text, (150, 60))
    pygame.display.flip()
    clock.tick(30)

# Отрисовываем таблицу топ-10 лучших игроков
screen = pygame.display.set_mode((900, 550))
screen.fill(BLACK)
pygame.display.set_caption('Breakout')
running3 = True
top = cur.execute(f"SELECT player_name, score FROM top").fetchall()
top = sorted(top, key=lambda a: -a[-1])[:10]
table_width = 600
table_height = 400
line_height = 40
line_width = 200

while running3:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running3 = False
    screen.fill(BLACK)
    text = font_for_game_over.render('ТОП-10 лучших игроков', True, WHITE)
    row = 115

    for i in range(4):
        pygame.draw.line(screen, WHITE, (150 + i * table_width // 3, 100),
                         (150 + i * table_width // 3, 100 + table_height), 2)
    for i in range(11):
        pygame.draw.line(screen, WHITE, (150, 100 + i * table_height // 10),
                         (150 + table_width, 100 + i * table_height // 10), 2)

    for i in range(len(top)):
        num = font.render(f"{i + 1}", True, WHITE)
        name = font.render(f"{top[i][0]}", True, WHITE)
        score = font.render(f"{top[i][1]}", True, WHITE)
        screen.blit(num, (170, row))
        screen.blit(name, (170 + line_width, row))
        screen.blit(score, (170 + 2 * line_width, row))
        row += line_height

    screen.blit(text, (300, 35))
    pygame.display.flip()

database.close()
pygame.quit()
