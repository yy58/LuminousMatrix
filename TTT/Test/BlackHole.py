import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Curved Light Reflection + Black Hole (with Mirror Normal)")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

SOURCE = (100, 100)
TARGET = (random.randint(400, WIDTH - 100), random.randint(200, HEIGHT - 100))
angle = random.uniform(0.1, math.pi / 3)
direction = pygame.Vector2(math.cos(angle), math.sin(angle))
mirrors = []

BLACK_HOLE_CENTER = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
EVENT_HORIZON_RADIUS = 150
ABSORB_RADIUS = 40
GRAVITY_STRENGTH = 0.004

def reflect_ray(ray_dir, normal):
    d = pygame.Vector2(ray_dir)
    n = pygame.Vector2(normal).normalize()
    return (d - 2 * d.dot(n) * n).normalize()

def point_to_segment_distance(pt, seg_a, seg_b):
    ap = pt - seg_a
    ab = seg_b - seg_a
    t = max(0, min(1, ap.dot(ab) / ab.dot(ab)))
    proj = seg_a + ab * t
    return (pt - proj).length(), proj

def draw_text(text, pos, color=(255, 255, 255)):
    screen.blit(font.render(text, True, color), pos)

running = True
while running:
    screen.fill((10, 10, 20))

    # 绘制黑洞
    pygame.draw.circle(screen, (30, 30, 50), BLACK_HOLE_CENTER, EVENT_HORIZON_RADIUS, 2)
    pygame.draw.circle(screen, (0, 0, 0), BLACK_HOLE_CENTER, ABSORB_RADIUS)

    # 绘制目标与光源
    pygame.draw.circle(screen, (255, 80, 80), TARGET, 8)
    pygame.draw.circle(screen, (80, 200, 255), SOURCE, 6)

    # 绘制镜子 + 正反可视化
    for x, y, a in mirrors:
        center = pygame.Vector2(x, y)
        dir_vec = pygame.Vector2(math.cos(a), math.sin(a))
        normal = pygame.Vector2(math.sin(a), -math.cos(a))

        # 镜子主体
        p1 = center - dir_vec * 40
        p2 = center + dir_vec * 40
        pygame.draw.line(screen, (240, 240, 240), p1, p2, 3)

        # 正面方向（红线）
        front_end = center + normal * 20
        pygame.draw.line(screen, (255, 100, 100), center, front_end, 2)
        pygame.draw.circle(screen, (255, 100, 100), front_end, 3)

        # 背面方向（蓝线）
        back_end = center - normal * 20
        pygame.draw.line(screen, (100, 100, 255), center, back_end, 1)

    # ---- 光线模拟 ----
    ray_pos = pygame.Vector2(SOURCE)
    ray_dir = pygame.Vector2(direction)
    color = (255, 255, 100)
    success = False
    absorbed = False

    for bounce in range(5):
        step_size = 5
        for _ in range(2000 // step_size):
            next_pos = ray_pos + ray_dir * step_size
            dist_to_bh = ray_pos.distance_to(BLACK_HOLE_CENTER)

            # 黑洞引力弯曲
            if dist_to_bh < EVENT_HORIZON_RADIUS:
                to_bh = (BLACK_HOLE_CENTER - ray_pos).normalize()
                factor = GRAVITY_STRENGTH * (EVENT_HORIZON_RADIUS / max(dist_to_bh, 5))
                ray_dir = (ray_dir + to_bh * factor).normalize()

            # 黑洞吸收
            if dist_to_bh < ABSORB_RADIUS:
                pygame.draw.line(screen, color, ray_pos, next_pos, 2)
                absorbed = True
                break

            # 镜子反射检测
            reflected = False
            for x, y, a in mirrors:
                p1 = pygame.Vector2(x - 40 * math.cos(a), y - 40 * math.sin(a))
                p2 = pygame.Vector2(x + 40 * math.cos(a), y + 40 * math.sin(a))
                normal = pygame.Vector2(math.sin(a), -math.cos(a))

                dist, nearest = point_to_segment_distance(ray_pos, p1, p2)
                facing = ray_dir.dot(normal) < 0  # 仅反射正面光线

                if dist < 3 and facing:
                    ray_dir = reflect_ray(ray_dir, normal)
                    ray_pos = nearest + ray_dir * 3
                    reflected = True
                    break

            if reflected:
                break

            # 绘制光线轨迹
            pygame.draw.line(screen, color, ray_pos, next_pos, 2)
            ray_pos = next_pos

            # 命中目标
            if ray_pos.distance_to(TARGET) < 10:
                success = True
                break

        if success or absorbed:
            break

    # ---- 状态提示 ----
    if absorbed:
        draw_text("Light absorbed by black hole!", (WIDTH // 2 - 140, 40), (255, 60, 60))
    elif success:
        pygame.draw.circle(screen, (0, 255, 0), TARGET, 12)
        draw_text("Mission Success!", (WIDTH // 2 - 80, 40), (100, 255, 100))
    else:
        draw_text("Right-click to add mirrors | Scroll to rotate", (20, 20))

    # ---- 控制事件 ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                mx, my = event.pos
                mirrors.append([mx, my, 0])
            if event.button == 4 and mirrors:
                mirrors[-1][2] += math.radians(5)
            if event.button == 5 and mirrors:
                mirrors[-1][2] -= math.radians(5)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
