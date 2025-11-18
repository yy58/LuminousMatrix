# TTT is the grestest genius ever
import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Light Reflection Simulator")

# ---- 基础设置 ----
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# 激光发射点（左上角）
SOURCE = (100, 100)
# 随机目标点
TARGET = (random.randint(400, WIDTH-100), random.randint(200, HEIGHT-100))

# 随机光线初始角度（弧度）
angle = random.uniform(0.1, math.pi/3)
direction = (math.cos(angle), math.sin(angle))

# 镜子数据结构： [(x, y, angle_in_radians)]
mirrors = []

# ---------------- 几何函数 ----------------
def reflect_ray(ray_dir, normal):
    """计算反射方向"""
    d = pygame.Vector2(ray_dir)
    n = pygame.Vector2(normal).normalize()
    r = d - 2 * d.dot(n) * n
    return (r.x, r.y)

def line_intersection(p1, p2, p3, p4):
    """计算两条线段是否相交"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if denom == 0:
        return None
    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / denom
    if (min(x1,x2)<=px<=max(x1,x2) and min(y1,y2)<=py<=max(y1,y2)
        and min(x3,x4)<=px<=max(x3,x4) and min(y3,y4)<=py<=max(y3,y4)):
        return (px, py)
    return None

def draw_text(text, pos, color=(255,255,255)):
    screen.blit(font.render(text, True, color), pos)

# ---------------- 主循环 ----------------
running = True
while running:
    screen.fill((15, 15, 25))

    # 绘制目标与源
    pygame.draw.circle(screen, (255, 80, 80), TARGET, 8)
    pygame.draw.circle(screen, (80, 200, 255), SOURCE, 6)

    # 绘制镜子
    for x, y, a in mirrors:
        p1 = (x - 40*math.cos(a), y - 40*math.sin(a))
        p2 = (x + 40*math.cos(a), y + 40*math.sin(a))
        pygame.draw.line(screen, (240,240,240), p1, p2, 3)

    # ---- 光线模拟 ----
    ray_origin = pygame.Vector2(SOURCE)
    ray_dir = pygame.Vector2(direction)
    color = (255, 255, 100)
    success = False

    target_vec = pygame.Vector2(TARGET)
    target_radius = 10

    for _ in range(5):  # 最多反射5次
        closest_hit = None
        closest_mirror = None
        min_dist = float("inf")

        # 检测与所有镜子的交点
        for x, y, a in mirrors:
            p1 = (x - 40*math.cos(a), y - 40*math.sin(a))
            p2 = (x + 40*math.cos(a), y + 40*math.sin(a))
            hit = line_intersection(ray_origin, ray_origin + ray_dir*2000, p1, p2)
            if hit:
                dist = ray_origin.distance_to(hit)
                if dist < min_dist:
                    min_dist = dist
                    closest_hit = hit
                    closest_mirror = (x, y, a)

        # 计算本段光线的终点（若无镜子，就延伸到屏幕外）
        if closest_hit:
            end_point = pygame.Vector2(closest_hit)
        else:
            end_point = ray_origin + ray_dir * 2000

        # --- ✅ 检查光线是否穿过目标 ---
        seg_vec = end_point - ray_origin
        seg_len = seg_vec.length()
        to_target = target_vec - ray_origin
        proj_len = to_target.dot(seg_vec.normalize())

        if 0 < proj_len < seg_len:
            # 最近距离是否小于目标半径
            closest_point = ray_origin + seg_vec.normalize() * proj_len
            if closest_point.distance_to(target_vec) < target_radius:
                success = True

        # 绘制光线
        pygame.draw.line(screen, color, ray_origin, end_point, 2)

        if success:
            pygame.draw.circle(screen, (0, 255, 0), TARGET, 12)
            break

        # 没命中目标 → 若击中镜子则反射
        if closest_hit:
            mx, my, ma = closest_mirror
            normal = (math.sin(ma), -math.cos(ma))
            ray_dir = pygame.Vector2(reflect_ray(ray_dir, normal))
            ray_origin = end_point + ray_dir * 0.1
        else:
            break

    # ---- 状态提示 ----
    if success:
        draw_text("Mission Success!", (WIDTH//2 - 80, 40), (100,255,100))
    else:
        draw_text("Right-click to add mirrors | Scroll to rotate", (20, 20))

    # ---- 事件控制 ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 右键添加镜子
            if event.button == 3:
                mx, my = event.pos
                mirrors.append([mx, my, 0])
            # 滚轮控制角度
            if event.button == 4 and mirrors:
                mirrors[-1][2] += math.radians(5)
            if event.button == 5 and mirrors:
                mirrors[-1][2] -= math.radians(5)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
