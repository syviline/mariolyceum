import pygame
import sys
import os


FPS = 50

running = True

xwidth = 11
ywidth = 11

pygame.init()
size = WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
    image = pygame.image.load(fullname)
    if colorkey is None:
        image.convert_alpha()
    else:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mario.png')

tile_width = tile_height = 50

player = None

tiles_group = pygame.sprite.Group()
collideable = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'wall':
            super().__init__(tiles_group, all_sprites, collideable)
        else:
            super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def move(self, dir_x, dir_y):
        self.pos_x += dir_x
        self.pos_y += dir_y
        self.rect.x += dir_x * tile_width
        self.rect.y += dir_y * tile_height
        if pygame.sprite.spritecollideany(self, collideable):
            self.rect.x -= dir_x * tile_width
            self.rect.y -= dir_y * tile_height
            self.pos_x -= dir_x
            self.pos_y -= dir_y

def generate_more_tiles(px, py, level):
    print("GEN TILES: " + str(px) + " " + str(py))
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x + px * xwidth, y + py * ywidth)
            elif level[y][x] == '#':
                Tile('wall', x + px * xwidth, y + py * ywidth)
            elif level[y][x] == "@":
                Tile('empty', x + px * xwidth, y + py * ywidth)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)

level = input('Введите название карты: ')
# level = 'map.txt'
levelmap = load_level(level)
try:
    player, level_x, level_y = generate_level(levelmap)
except FileNotFoundError:
    print('Файл не найден')
except Exception as e:
    print('Произошла непредвиденная ошибка: ' + str(e))
start_screen()
camera = Camera()
for x in range(-1, 1):
    for y in range(-1, 1):
        generate_more_tiles(x, y, levelmap)
minseey = 5
mingeneratedy = 0
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.move(0, -1)
            if event.key == pygame.K_d:
                player.move(1, 0)
            if event.key == pygame.K_s:
                player.move(0, 1)
            if event.key == pygame.K_a:
                player.move(-1, 0)
    print(player.pos_x, player.pos_y)
    if player.pos_y <= -7:
        player.move(0, 11)
    if player.pos_y >= 6:
        player.move(0, -11)
    if player.pos_x <= -7:
        player.move(11, 0)
    if player.pos_x >= 6:
        player.move(-11, 0)
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    tiles_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)