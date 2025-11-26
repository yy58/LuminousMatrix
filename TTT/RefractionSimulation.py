import math
import random
import sys
from typing import List, Tuple, Optional, Set
import pygame

# ---------------- Config ----------------
WIDTH, HEIGHT = 1200, 720
NUM_SQUARES = 3
NUM_TRIANGLES = 3
SQUARE_SIZE = 120
TRI_SIZE = 140

REFRACTIVE_INDEX_AIR = 1.0
REFRACTIVE_INDEX_SHAPE = 1.5

MAX_BOUNCES = 160
EPS = 1e-8
TINY = 1e-4
SAFE_INF = 1e18

# Colors
BG = (18, 18, 28)
COL_FILL = (80, 120, 160, 70)
COL_SQ_EDGE = (220, 220, 220)
COL_TRI_EDGE = (255, 200, 120)
COL_AIR_LEFT = (255, 220, 60)
COL_INSIDE_LEFT = (255, 100, 100)
COL_AIR_RIGHT = (60, 250, 220)
COL_INSIDE_RIGHT = (100, 160, 255)
# Fresnel reflection colors
COL_REFLECT_LEFT = (255, 180, 0)      # 左侧光线的反射光（亮橙）
COL_REFLECT_RIGHT = (0, 180, 255)     # 右侧光线的反射光（亮蓝）

# ---------------- Grid Config ----------------
GRID_SIZE = 30   # 每个格子尺寸，你可改成 20 / 40 / 60 等
GRID_COLS = WIDTH // GRID_SIZE
GRID_ROWS = HEIGHT // GRID_SIZE

# 亮格子布尔表：True=光线走过
grid_lit = [[False for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

# ---------------- Vector utilities ----------------
def v_add(a, b): return (a[0] + b[0], a[1] + b[1])
def v_sub(a, b): return (a[0] - b[0], a[1] - b[1])
def v_mul(a, s): return (a[0] * s, a[1] * s)
def v_dot(a, b): return a[0] * b[0] + a[1] * b[1]
def v_len(a): return math.hypot(a[0], a[1])
def v_norm(a):
    L = v_len(a)
    if L < 1e-12:
        return (0.0, 0.0)
    return (a[0] / L, a[1] / L)
def perp(a): return (-a[1], a[0])

# ---------------- Safety checks ----------------
def is_valid_number(x):
    return isinstance(x, (int, float)) and (not math.isnan(x)) and (not math.isinf(x))

def is_valid_point(p):
    if not isinstance(p, (tuple, list)) or len(p) != 2:
        return False
    return is_valid_number(p[0]) and is_valid_number(p[1])

# ---------------- Geometry helpers ----------------
def ray_segment_intersection(p, v, a, b):
    r = v
    s = v_sub(b, a)
    rxs = r[0] * s[1] - r[1] * s[0]
    if abs(rxs) < 1e-12:
        return None
    ap = v_sub(a, p)
    t = (ap[0] * s[1] - ap[1] * s[0]) / rxs
    u = (ap[0] * r[1] - ap[1] * r[0]) / rxs
    return (t, u)

def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if ((y1 > y) != (y2 > y)):
            denom = (y2 - y1)
            if abs(denom) < 1e-12:
                continue
            xint = (x2 - x1) * (y - y1) / denom + x1
            if x < xint:
                inside = not inside
    return inside

def poly_aabb(poly):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    return (min(xs), min(ys), max(xs), max(ys))

def aabb_overlap(a, b):
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

# ---------------- Shape makers ----------------
def make_rotated_square(cx, cy, size, angle):
    h = size / 2.0
    pts = [(-h, -h), (h, -h), (h, h), (-h, h)]
    ca = math.cos(angle); sa = math.sin(angle)
    out = []
    for x, y in pts:
        rx = x * ca - y * sa
        ry = x * sa + y * ca
        out.append((cx + rx, cy + ry))
    return out

def make_rotated_triangle(cx, cy, size, angle):
    h = size * math.sqrt(3) / 2.0
    pts = [(0, -h * 2/3), (size/2, h/3), (-size/2, h/3)]
    ca = math.cos(angle); sa = math.sin(angle)
    out = []
    for x, y in pts:
        rx = x * ca - y * sa
        ry = x * sa + y * ca
        out.append((cx + rx, cy + ry))
    return out

# ---------------- Outward normal ----------------
def outward_normal(a, b, poly):
    mid = ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    to_center = v_sub((cx, cy), mid)
    n = v_norm(perp(v_sub(b, a)))
    if v_dot(n, to_center) > 0:
        n = v_mul(n, -1.0)
    return n

# ---------------- Snell / reflection ----------------
def refract_or_reflect(v, n, n1, n2):
    if v_dot(n, v) > 0:
        n = v_mul(n, -1.0)
    cos_i = -v_dot(n, v)
    cos_i = max(-1.0, min(1.0, cos_i))
    ratio = n1 / n2

    sin_t2 = ratio * ratio * max(0.0, 1.0 - cos_i*cos_i)
    if sin_t2 > 1.0 - 1e-12:
        refl = v_sub(v, v_mul(n, 2.0 * v_dot(v, n)))
        return ("reflect", v_norm(refl))

    cos_t = math.sqrt(max(0.0, 1.0 - sin_t2))
    tdir = v_add(v_mul(v, ratio), v_mul(n, ratio * cos_i - cos_t))
    return ("refract", v_norm(tdir))

# ---------------- Generate shapes ----------------
def generate_shapes(num_sq, num_tri, sq_size, tri_size, w, h, seed=None):
    if seed is not None:
        random.seed(seed)
    shapes = []
    margin = 100
    tries = 0
    target = num_sq + num_tri
    placed_sq = 0
    placed_tri = 0

    while len(shapes) < target and tries < 20000:
        tries += 1
        if placed_sq < num_sq:
            is_square = True
            size = sq_size
        else:
            is_square = False
            size = tri_size
        ang = random.uniform(0, math.pi * 2)
        cx = random.uniform(margin, w - margin)
        cy = random.uniform(margin, h - margin)

        poly = make_rotated_square(cx, cy, size, ang) if is_square else make_rotated_triangle(cx, cy, size, ang)
        aabb = poly_aabb(poly)

        ok = True
        for s in shapes:
            if aabb_overlap(aabb, s["aabb"]):
                ok = False
                break
        if not ok:
            continue

        shapes.append({"poly": poly, "aabb": aabb, "is_square": is_square})
        if is_square:
            placed_sq += 1
        else:
            placed_tri += 1

    return shapes

# ---------------- Ray tracer ----------------
def trace_ray(origin, direction, shapes):
    """
    返回：[(start, end, inside, is_reflect_branch), ...]
    is_reflect_branch=True → 使用反射颜色绘制
    """
    out_segments = []
    stack = [(origin, v_norm(direction), False)]   # (p, v, is_reflect_branch)

    while stack:
        p, v, is_reflect = stack.pop()

        segments = []
        v = v_norm(v)
        if v == (0.0, 0.0):
            continue

        # 构建边列表
        edges = []
        for pid, sh in enumerate(shapes):
            poly = sh["poly"]
            for j in range(len(poly)):
                a = poly[j]
                b = poly[(j + 1) % len(poly)]
                edges.append((a, b, pid))

        # 初始 inside 判断
        inside_set = set()
        for pid, sh in enumerate(shapes):
            if point_in_poly(v_add(p, v_mul(v, TINY)), sh["poly"]):
                inside_set.add(pid)

        for _ in range(MAX_BOUNCES):
            nearest_t = float("inf")
            nearest_edge = None

            # 找最近边
            for a, b, pid in edges:
                res = ray_segment_intersection(p, v, a, b)
                if res is None:
                    continue
                t, u = res
                if t <= EPS or not (0 <= u <= 1):
                    continue
                if t < nearest_t:
                    nearest_t = t
                    nearest_edge = (a, b, pid)

            # 出屏
            if nearest_edge is None:
                t_candidates = []
                if abs(v[0]) > 1e-9:
                    t_candidates.append((WIDTH + 50 - p[0]) / v[0] if v[0] > 0 else (-50 - p[0]) / v[0])
                if abs(v[1]) > 1e-9:
                    t_candidates.append((HEIGHT + 50 - p[1]) / v[1] if v[1] > 0 else (-50 - p[1]) / v[1])

                if t_candidates:
                    t_exit = min(tc for tc in t_candidates if tc > 0)
                    endp = v_add(p, v_mul(v, t_exit))
                    segments.append((p, endp, len(inside_set) > 0, is_reflect))
                break

            # 撞到最近边
            a, b, pid = nearest_edge
            inter = v_add(p, v_mul(v, nearest_t))
            segments.append((p, inter, len(inside_set) > 0, is_reflect))

            was_inside = point_in_poly(v_sub(inter, v_mul(v, TINY)), shapes[pid]["poly"])
            n1 = REFRACTIVE_INDEX_SHAPE if was_inside else REFRACTIVE_INDEX_AIR
            n2 = REFRACTIVE_INDEX_AIR if was_inside else REFRACTIVE_INDEX_SHAPE

            nvec = outward_normal(a, b, shapes[pid]["poly"])

            # Snell 分支
            mode, newv = refract_or_reflect(v, nvec, n1, n2)

            # === ⭐ 新增：反射分光（只在入射时产生：n1 < n2）===
            if not was_inside:  
                refl_dir = v_sub(v, v_mul(nvec, 2 * v_dot(v, nvec)))
                refl_dir = v_norm(refl_dir)
                stack.append((v_add(inter, v_mul(refl_dir, TINY)), refl_dir, True))

            # === 折射或全反射 ===
            p = v_add(inter, v_mul(newv, TINY))
            v = newv

            # inside 更新
            if point_in_poly(v_add(inter, v_mul(v, TINY)), shapes[pid]["poly"]):
                inside_set.add(pid)
            else:
                inside_set.discard(pid)

            # 若光线飞到很远则停止
            if p[0] < -200 or p[0] > WIDTH + 200 or p[1] < -200 or p[1] > HEIGHT + 200:
                break

        out_segments += segments

    return out_segments

# ---------------- Drawing ----------------
def safe_draw_circle(surface, color, point, radius):
    if is_valid_point(point):
        try:
            pygame.draw.circle(surface, color, (int(point[0]), int(point[1])), radius)
        except:
            pass

def mark_segment_on_grid(a, b):
    """将线段经过的格子设为 True"""
    x1, y1 = a; x2, y2 = b

    # 保证顺序
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    # 包围盒 → 降低计算量
    min_c = max(0, int(min(x1, x2) // GRID_SIZE))
    max_c = min(GRID_COLS - 1, int(max(x1, x2) // GRID_SIZE))
    min_r = max(0, int(min(y1, y2) // GRID_SIZE))
    max_r = min(GRID_ROWS - 1, int(max(y1, y2) // GRID_SIZE))

    # 对范围内格子检测线段是否穿过（中心点投影法）
    for cx in range(min_c, max_c + 1):
        for cy in range(min_r, max_r + 1):
            gx = cx * GRID_SIZE + GRID_SIZE * 0.5
            gy = cy * GRID_SIZE + GRID_SIZE * 0.5

            # 判断点(gx,gy)到线段的最小距离
            # 若 < GRID_SIZE/2 即认为光线经过该格子
            px, py = gx, gy
            vx, vy = x2 - x1, y2 - y1
            wx, wy = px - x1, py - y1
            L2 = vx * vx + vy * vy
            if L2 < 1e-12:
                continue
            t = max(0.0, min(1.0, (wx * vx + wy * vy) / L2))
            projx = x1 + vx * t
            projy = y1 + vy * t
            dx = px - projx; dy = py - projy
            if dx * dx + dy * dy <= (GRID_SIZE * 0.48) ** 2:
                grid_lit[cx][cy] = True

def draw_scene(screen, shapes, all_rays):
    screen.fill(BG)
    # --------- 绘制网格背景：亮格子白、暗格子黑 ----------
    for cx in range(GRID_COLS):
        for cy in range(GRID_ROWS):
            color = (255, 255, 255) if grid_lit[cx][cy] else (0, 0, 0)
            pygame.draw.rect(
                screen, color,
                pygame.Rect(cx * GRID_SIZE, cy * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            )

    alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for sh in shapes:
        pygame.draw.polygon(alpha_surf, COL_FILL, sh["poly"])
    screen.blit(alpha_surf, (0, 0))

    for sh in shapes:
        col = COL_SQ_EDGE if sh["is_square"] else COL_TRI_EDGE
        pygame.draw.polygon(screen, col, sh["poly"], 2)

    for segs in all_rays:
        if not segs:
            continue

        # 根据第一段判断光线源头（x 小=左边；x 大=右边）
        first_start = segs[0][0]
        from_right = first_start[0] > WIDTH * 0.5

        for a, b, inside, is_reflect in segs:
            if not is_valid_point(a) or not is_valid_point(b):
                continue

            if from_right:
                if is_reflect:
                    col = COL_REFLECT_RIGHT
                else:
                    col = COL_INSIDE_RIGHT if inside else COL_AIR_RIGHT
            else:
                if is_reflect:
                    col = COL_REFLECT_LEFT
                else:
                    col = COL_INSIDE_LEFT if inside else COL_AIR_LEFT

            pygame.draw.line(screen, col, a, b, 3)
            safe_draw_circle(screen, col, b, 3)

    pygame.display.flip()

# ---------------- Main ----------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Stable Refraction Simulation (Left + Right Rays)")

    shapes = generate_shapes(NUM_SQUARES, NUM_TRIANGLES, SQUARE_SIZE, TRI_SIZE, WIDTH, HEIGHT)

    # 左侧三条光线
    left_sources = [
        (0.0, HEIGHT * 0.25),
        (0.0, HEIGHT * 0.50),
        (0.0, HEIGHT * 0.75),
    ]

    # 右侧三条光线
    right_sources = [
        (WIDTH, HEIGHT * 0.25),
        (WIDTH, HEIGHT * 0.50),
        (WIDTH, HEIGHT * 0.75),
    ]

    sources = left_sources + right_sources

    clock = pygame.time.Clock()
    running = True
    recompute = True
    all_rays = []

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    shapes = generate_shapes(NUM_SQUARES, NUM_TRIANGLES, SQUARE_SIZE, TRI_SIZE, WIDTH, HEIGHT)
                    recompute = True
                elif ev.key == pygame.K_ESCAPE:
                    running = False

        if recompute:
            all_rays = []
            for sx, sy in sources:
                if sx < WIDTH * 0.5:
                    direction = (1.0, 0.0)
                else:
                    direction = (-1.0, 0.0)
                rays = trace_ray((sx, sy), direction, shapes)
                all_rays.append(rays)

                # === 新增：标记所有格子 ===
                for seg in rays:
                    if not isinstance(seg, (tuple, list)):
                        continue
                    if len(seg) < 3:
                        continue

                    a, b, inside = seg[:3]    # 自动裁剪为 3 个值

                    if is_valid_point(a) and is_valid_point(b):
                        mark_segment_on_grid(a, b)

            recompute = False

        draw_scene(screen, shapes, all_rays)
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
