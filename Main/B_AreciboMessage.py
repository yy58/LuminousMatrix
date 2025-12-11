import math
import pygame
from typing import List, Tuple

# ---------------- Config ----------------
WIDTH, HEIGHT = 1280, 720
NUM_SQUARES = 3
NUM_TRIANGLES = 3
SQUARE_SIZE = 120
TRI_SIZE = 140

REFRACTIVE_INDEX_AIR = 1.0
REFRACTIVE_INDEX_SHAPE = 1.5

MAX_BOUNCES = 160
EPS = 1e-8
TINY = 1e-4

# ---------------- Colors ----------------
BG = (18, 18, 28)
COL_FILL = (80, 120, 160, 70)
COL_SQ_EDGE = (220, 220, 220)
COL_TRI_EDGE = (255, 200, 120)

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

# ---------------- Geometry helpers ----------------
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

# ---------------- Shape makers ----------------
def make_rotated_square(cx, cy, size, angle):
    h = size / 2.0
    pts = [(-h, -h), (h, -h), (h, h), (-h, h)]
    ca = math.cos(angle); sa = math.sin(angle)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]

def make_rotated_triangle(cx, cy, size, angle):
    h = size * math.sqrt(3) / 2.0
    pts = [(0, -h * 2/3), (size/2, h/3), (-size/2, h/3)]
    ca = math.cos(angle); sa = math.sin(angle)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]

# ---------------- Outward normal ----------------
def outward_normal(a, b, poly):
    mid = ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    to_center = (cx - mid[0], cy - mid[1])
    n = v_norm(perp(v_sub(b, a)))
    if v_dot(n, to_center) > 0:
        n = v_mul(n, -1.0)
    return n

# ---------------- Shapes from prism data ----------------
def generate_shapes_from_params(params):
    shapes = []
    for pid, cx, cy, ang in params:
        if pid in [1, 2, 3]:  # 三角形
            poly = make_rotated_triangle(cx, cy, TRI_SIZE, ang)
            is_square = False
        elif pid in [4, 5, 6]:  # 正方形
            poly = make_rotated_square(cx, cy, SQUARE_SIZE, ang)
            is_square = True
        else:
            continue

        shapes.append({
            "id": pid,
            "poly": poly,
            "aabb": poly_aabb(poly),
            "is_square": is_square
        })
    return shapes

# ---------------- Dummy Ray Tracer ----------------
def trace_ray(origin, direction, shapes):
    """保持空逻辑，用于未来扩展"""
    return []

# ===================================================
#                  RAY SIMULATOR CLASS
# ===================================================
class RaySimulator:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Prism Simulation")

        self.prism_data = []
        self.shapes = []
        self.clock = pygame.time.Clock()

    def set_window_size(self, w, h):
        # Fixed size; ignore external setting
        pass

    def update_prism_data(self, data):
        """由 A 模块更新棱镜数据"""
        self.prism_data = list(data)
        self.shapes = generate_shapes_from_params(self.prism_data)

    def remove_prisms(self, id_set):
        """由 A 模块发送消失 ID"""
        self.shapes = [s for s in self.shapes if s["id"] not in id_set]

    def draw(self):
        """每帧绘制场景"""
        screen = self.screen
        screen.fill(BG)

        # 透明填充
        alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for sh in self.shapes:
            pygame.draw.polygon(alpha_surf, COL_FILL, sh["poly"])
        screen.blit(alpha_surf, (0, 0))

        # 边框
        for sh in self.shapes:
            col = COL_SQ_EDGE if sh["is_square"] else COL_TRI_EDGE
            pygame.draw.polygon(screen, col, sh["poly"], 2)

        pygame.display.flip()
        self.clock.tick(60)
