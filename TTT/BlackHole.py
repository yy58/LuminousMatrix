import pygame, math, random

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("光线反射与黑洞模拟")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# ---------- 基础设置 ----------
SOURCE = (100, 100)
TARGET = (random.randint(400, WIDTH - 100), random.randint(200, HEIGHT - 100))
angle = random.uniform(0.1, math.pi / 3)
direction = pygame.Vector2(math.cos(angle), math.sin(angle))
mirrors = []

# ---------- 黑洞参数 ----------
BH = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
BH_RADIUS = 50        # 事件视界
BH_GRAVITY = 90000.0  # 引力强度（调高弯曲更明显）

# ---------- 几何函数 ----------
def reflect_ray(ray_dir, normal):
    d = pygame.Vector2(ray_dir)
    n = pygame.Vector2(normal).normalize()
    return d - 2 * d.dot(n) * n

def line_intersection(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) -
          (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) -
          (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    if (min(x1, x2) <= px <= max(x1, x2)
        and min(y1, y2) <= py <= max(y1, y2)
        and min(x3, x4) <= px <= max(x3, x4)
        and min(y3, y4) <= py <= max(y3, y4)):
        return (px, py)
    return None

def draw_text(text, pos, color=(255, 255, 255)):
    screen.blit(font.render(text, True, color), pos)

# ---------- 主循环 ----------
running = True
while running:
    screen.fill((10, 10, 20))

    # 黑洞视觉
    pygame.draw.circle(screen, (30, 30, 30), BH, BH_RADIUS)
    pygame.draw.circle(screen, (80, 80, 150), BH, int(BH_RADIUS * 1.5), 2)
    pygame.draw.circle(screen, (100, 100, 255), BH, int(BH_RADIUS * 2.5), 1)

    # 发射点 & 目标点
    pygame.draw.circle(screen, (80, 200, 255), SOURCE, 6)
    pygame.draw.circle(screen, (255, 80, 80), TARGET, 8)

    # 镜子绘制
    for x, y, a in mirrors:
        p1 = (x - 40 * math.cos(a), y - 40 * math.sin(a))
        p2 = (x + 40 * math.cos(a), y + 40 * math.sin(a))
        pygame.draw.line(screen, (240, 240, 240), p1, p2, 3)

    # -------- 光线模拟 --------
    ray_origin = pygame.Vector2(SOURCE)
    ray_dir = pygame.Vector2(direction)
    color = (255, 255, 120)
    success = False

    for bounce in range(6):  # 允许6次反射
        pos = pygame.Vector2(ray_origin)
        travelled = 0
        step = 5
        collided = False

        while 0 <= pos.x <= WIDTH and 0 <= pos.y <= HEIGHT:
            prev = pygame.Vector2(pos)
            pos += ray_dir * step
            travelled += step

            # --- 黑洞引力弯曲 ---
            to_bh = BH - pos
            r = to_bh.length()
            if r < BH_RADIUS:
                # 光线被吞噬
                pygame.draw.line(screen, color, prev, pos, 2)
                pygame.draw.circle(screen, (0, 0, 0), BH, BH_RADIUS)
                collided = True
                break
            elif r < 300:
                bend = BH_GRAVITY / (r ** 2)
                deflect = to_bh.normalize() * bend * 0.0005
                ray_dir = (ray_dir + deflect).normalize()

            # 绘制光线段
            pygame.draw.line(screen, color, prev, pos, 2)

            # 检测是否击中目标
            if pos.distance_to(TARGET) < 10:
                success = True
                pygame.draw.circle(screen, (0, 255, 0), TARGET, 12)
                collided = True
                break

            # 检测是否碰到镜子（逐段检测）
            for x, y, a in mirrors:
                p1 = (x - 40 * math.cos(a), y - 40 * math.sin(a))
                p2 = (x + 40 * math.cos(a), y + 40 * math.sin(a))
                hit = line_intersection(prev, pos, p1, p2)
                if hit:
                    # 碰到镜子，反射
                    mx, my, ma = x, y, a
                    normal = (math.sin(ma), -math.cos(ma))
                    ray_dir = pygame.Vector2(reflect_ray(ray_dir, normal))
                    ray_origin = pygame.Vector2(hit) + ray_dir * 0.1
                    collided = True
                    break
            if collided:
                break

        if not collided:
            break
        if success:
            break

    # -------- 文本显示 --------
    if success:
        draw_text("✨ Mission Success!", (WIDTH // 2 - 80, 30), (100, 255, 100))
    else:
        draw_text("右键添加镜子 | 滚轮旋转 | 黑洞会弯曲光线", (20, 20), (200, 200, 200))

    # -------- 事件处理 --------
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 3:  # 右键放置镜子
                mx, my = e.pos
                mirrors.append([mx, my, 0])
            if e.button == 4 and mirrors:
                mirrors[-1][2] += math.radians(5)
            if e.button == 5 and mirrors:
                mirrors[-1][2] -= math.radians(5)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
