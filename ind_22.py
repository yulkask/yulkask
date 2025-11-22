import pygame
import math

pygame.init()

W, H = 800, 600
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

# ---------------------------
# Базовые алгоритмы
# ---------------------------

def bresenham_line(surface, x1, y1, x2, y2, color):
    # Ensure integer coordinates
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    w, h = surface.get_size()

    while True:
        # draw pixel if within surface bounds
        if 0 <= x1 < w and 0 <= y1 < h:
            surface.set_at((x1, y1), color)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


def bresenham_circle(surface, xc, yc, r, color):
    # Work with integers and avoid drawing outside the surface
    xc = int(xc)
    yc = int(yc)
    r = int(round(r))
    if r <= 0:
        return

    x = 0
    y = r
    d = 3 - 2 * r

    w, h = surface.get_size()

    def draw_circle_points():
        pts = [
            (xc + x, yc + y),
            (xc - x, yc + y),
            (xc + x, yc - y),
            (xc - x, yc - y),
            (xc + y, yc + x),
            (xc - y, yc + x),
            (xc + y, yc - x),
            (xc - y, yc - x),
        ]
        for px, py in pts:
            if 0 <= px < w and 0 <= py < h:
                surface.set_at((px, py), color)

    while x <= y:
        draw_circle_points()
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
        x += 1


# ---------------------------
# Описание фигуры
# ---------------------------

# Фигура в локальных координатах
R = 40
Hh = 120
A = 70
B = 60

circles = [
    (0, -Hh, R),
    (0, Hh, R)
]

lines = [
    # Верхняя вертикаль
    (0, -Hh, 0, -B),
    # Треугольник
    (0, -B, -A, 0),
    (0, -B, A, 0),
    (-A, 0, A, 0),
    # Нижняя вертикаль
    (0, 0, 0, Hh)
]


# Преобразования фигуры

def rotate_point(x, y, cx, cy, angle):
    s = math.sin(angle)
    c = math.cos(angle)

    x -= cx
    y -= cy

    x_new = x * c - y * s
    y_new = x * s + y * c

    return x_new + cx, y_new + cy


def scale_point(x, y, cx, cy, k):
    return cx + (x - cx) * k, cy + (y - cy) * k


# ---------------------------
# Рисование
# ---------------------------

def draw_figure(surface, lines, circles):
    for (x1, y1, x2, y2) in lines:
        bresenham_line(surface, int(x1), int(y1), int(x2), int(y2), (255, 255, 255))

    for (xc, yc, r) in circles:
        bresenham_circle(surface, int(xc), int(yc), int(r), (255, 255, 255))


# ---------------------------
# Аффинные преобразования
# ---------------------------

def apply_rotation(lines, circles, angle):
    cx, cy = W//2, H//2

    new_lines = []
    new_circles = []

    for x1, y1, x2, y2 in lines:
        x1r, y1r = rotate_point(x1, y1, cx, cy, angle)
        x2r, y2r = rotate_point(x2, y2, cx, cy, angle)
        new_lines.append((x1r, y1r, x2r, y2r))

    for xc, yc, r in circles:
        xcr, ycr = rotate_point(xc, yc, cx, cy, angle)
        new_circles.append((xcr, ycr, r))

    return new_lines, new_circles


def apply_scale(lines, circles, k):
    cx, cy = W//2, H//2

    new_lines = []
    new_circles = []

    for x1, y1, x2, y2 in lines:
        x1s, y1s = scale_point(x1, y1, cx, cy, k)
        x2s, y2s = scale_point(x2, y2, cx, cy, k)
        new_lines.append((x1s, y1s, x2s, y2s))

    for xc, yc, r in circles:
        # Ignore non-positive scale factors
        if k <= 0:
            xcs, ycs = xc, yc
            r_new = r
        else:
            xcs, ycs = scale_point(xc, yc, cx, cy, k)
            r_new = r * k
            if r_new < 1:
                r_new = 1
        new_circles.append((xcs, ycs, r_new))

    return new_lines, new_circles


# Преобразования по варианту
transform_mode = 0   # 0 — rotate, 1 — scale

# Начальное размещение фигуры в центре экрана
def move_to_center(lines, circles):
    cx, cy = W//2, H//2
    return (
        [(x1+cx, y1+cy, x2+cx, y2+cy) for x1,y1,x2,y2 in lines],
        [(xc+cx, yc+cy, r) for xc,yc,r in circles]
    )

lines_world, circles_world = move_to_center(lines, circles)

# ---------------------------
# Основной цикл
# ---------------------------

running = True
angle_step = 0.1
scale_step = 1.1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                transform_mode = (transform_mode + 1) % 2  # ПКМ – переключение
            elif event.button == 1:
                # ЛКМ – выполнить преобразование
                if transform_mode == 0:   # rotate
                    lines_world, circles_world = apply_rotation(
                        lines_world, circles_world, angle_step
                    )
                else:                     # scale
                    lines_world, circles_world = apply_scale(
                        lines_world, circles_world, scale_step
                    )

    # Двойной буфер
    buffer = pygame.Surface((W, H))
    buffer.fill((0, 0, 0))

    draw_figure(buffer, lines_world, circles_world)

    screen.blit(buffer, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
