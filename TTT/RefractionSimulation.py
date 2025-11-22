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
TINY = 1e-4  # 用于测试点移动，避免粘边
SAFE_INF = 1e18

# Colors
BG = (18, 18, 28)
COL_FILL = (80, 120, 160, 70)
COL_SQ_EDGE = (220, 220, 220)
COL_TRI_EDGE = (255, 200, 120)
COL_AIR = (255, 220, 60)
COL_INSIDE = (255, 100, 100)

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
def ray_segment_intersection(p, v, a, b) -> Optional[Tuple[float, float]]:
    r = v
    s = v_sub(b, a)
    rxs = r[0] * s[1] - r[1] * s[0]
    if abs(rxs) < 1e-12:
        return None
    ap = v_sub(a, p)
    t = (ap[0] * s[1] - ap[1] * s[0]) / rxs
    u = (ap[0] * r[1] - ap[1] * r[0]) / rxs
    return (t, u)

def point_in_poly(pt, poly) -> bool:
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        # avoid division by zero
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
    # 等边三角形，基于边长 size
    h = size * math.sqrt(3) / 2.0
    pts = [(0, -h / 3.0 * 2.0 + h/3.0), (size / 2.0, h * 2.0 / 3.0 - h/3.0), (-size / 2.0, h * 2.0 / 3.0 - h/3.0)]
    # simpler: use centered approx triangle
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
    # if n points toward interior, flip
    if v_dot(n, to_center) > 0:
        n = v_mul(n, -1.0)
    return n

# ---------------- Snell / reflection (stable) ----------------
def refract_or_reflect(v, n, n1, n2):
    # ensure n opposes v
    if v_dot(n, v) > 0:
        n = v_mul(n, -1.0)
    cos_i = -v_dot(n, v)
    ratio = n1 / n2
    # clamp numeric
    cos_i = max(-1.0, min(1.0, cos_i))
    sin_t2 = ratio * ratio * max(0.0, 1.0 - cos_i * cos_i)
    if sin_t2 > 1.0 - 1e-12:
        # total internal reflection
        refl = v_sub(v, v_mul(n, 2.0 * v_dot(v, n)))
        return ("reflect", v_norm(refl))
    cos_t = math.sqrt(max(0.0, 1.0 - sin_t2))
    term1 = v_mul(v, ratio)
    term2 = v_mul(n, (ratio * cos_i - cos_t))
    tdir = v_add(term1, term2)
    return ("refract", v_norm(tdir))

# ---------------- Generate non-overlapping shapes ----------------
def generate_shapes(num_sq, num_tri, sq_size, tri_size, w, h, seed=None):
    if seed is not None:
        random.seed(seed)
    shapes = []
    margin = 100
    tries = 0
    target = num_sq + num_tri
    # place squares first then triangles (could mix)
    placed_sq = 0; placed_tri = 0
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
                ok = False; break
        if not ok:
            continue
        shapes.append({"poly": poly, "aabb": aabb, "is_square": is_square})
        if is_square: placed_sq += 1
        else: placed_tri += 1
        # ensure we switch to triangles after squares placed
        if placed_sq >= num_sq and placed_tri < num_tri:
            pass
    return shapes

# ---------------- Ray tracer (stable) ----------------
def trace_ray(origin, direction, shapes):
    segments = []
    p = origin
    v = v_norm(direction)
    if v == (0.0, 0.0):
        return segments

    # build edge list
    edges = []
    for i, sh in enumerate(shapes):
        poly = sh["poly"]
        for j in range(len(poly)):
            a = poly[j]; b = poly[(j + 1) % len(poly)]
            edges.append((a, b, i))

    # initial inside set based on tiny step from origin
    inside_set: Set[int] = set()
    for i, sh in enumerate(shapes):
        testp = v_add(p, v_mul(v, TINY))
        if point_in_poly(testp, sh["poly"]):
            inside_set.add(i)

    for _ in range(MAX_BOUNCES):
        # find nearest intersection
        nearest_t = float("inf")
        nearest_edge = None
        for a, b, pid in edges:
            res = ray_segment_intersection(p, v, a, b)
            if res is None:
                continue
            t, u = res
            if t <= EPS:
                continue
            if u < -1e-9 or u > 1 + 1e-9:
                continue
            if t < nearest_t:
                nearest_t = t
                nearest_edge = (a, b, pid)
        if nearest_edge is None:
            # compute t to exit screen box robustly
            t_candidates = []
            if abs(v[0]) > 1e-9:
                if v[0] > 0:
                    t_candidates.append((WIDTH + 50 - p[0]) / v[0])
                else:
                    t_candidates.append((-50 - p[0]) / v[0])
            if abs(v[1]) > 1e-9:
                if v[1] > 0:
                    t_candidates.append((HEIGHT + 50 - p[1]) / v[1])
                else:
                    t_candidates.append((-50 - p[1]) / v[1])
            if not t_candidates:
                break
            t_exit = min(tc for tc in t_candidates if tc > 0) if any(tc > 0 for tc in t_candidates) else max(t_candidates)
            if not is_valid_number(t_exit) or t_exit > SAFE_INF:
                break
            endp = v_add(p, v_mul(v, t_exit))
            segments.append((p, endp, len(inside_set) > 0))
            break

        a, b, pid = nearest_edge
        inter = v_add(p, v_mul(v, nearest_t))
        segments.append((p, inter, len(inside_set) > 0))

        # determine if ray was inside this polygon before hitting the edge
        pre_test = v_sub(inter, v_mul(v, TINY))
        was_inside = point_in_poly(pre_test, shapes[pid]["poly"])

        # choose n1,n2 accordingly
        if was_inside:
            n1 = REFRACTIVE_INDEX_SHAPE; n2 = REFRACTIVE_INDEX_AIR
        else:
            n1 = REFRACTIVE_INDEX_AIR; n2 = REFRACTIVE_INDEX_SHAPE

        nvec = outward_normal(a, b, shapes[pid]["poly"])

        mode, newv = refract_or_reflect(v, nvec, n1, n2)

        # protect against invalid newv
        if not (is_valid_number(newv[0]) and is_valid_number(newv[1])):
            # fallback to mirror reflection
            refl = v_sub(v, v_mul(nvec, 2.0 * v_dot(v, nvec)))
            newv = v_norm(refl)
        # avoid near-zero vector
        if v_len(newv) < 1e-12:
            refl = v_sub(v, v_mul(nvec, 2.0 * v_dot(v, nvec)))
            newv = v_norm(refl)
        newv = v_norm(newv)

        # update inside_set according to post-test point (robust)
        post_test = v_add(inter, v_mul(newv, TINY))
        if point_in_poly(post_test, shapes[pid]["poly"]):
            inside_set.add(pid)
        else:
            inside_set.discard(pid)

        # advance slightly and continue
        p = v_add(inter, v_mul(newv, TINY))
        v = newv

        # safety bounds
        if p[0] < -500 or p[0] > WIDTH + 500 or p[1] < -500 or p[1] > HEIGHT + 500:
            break

    return segments

# ---------------- Drawing ----------------
def safe_draw_circle(surface, color, point, radius):
    if is_valid_point(point):
        try:
            pygame.draw.circle(surface, color, (int(point[0]), int(point[1])), radius)
        except Exception:
            pass

def draw_scene(screen, shapes, all_rays):
    screen.fill(BG)
    alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for sh in shapes:
        pygame.draw.polygon(alpha_surf, COL_FILL, sh["poly"])
    screen.blit(alpha_surf, (0, 0))

    for sh in shapes:
        col = COL_SQ_EDGE if sh["is_square"] else COL_TRI_EDGE
        pygame.draw.polygon(screen, col, sh["poly"], 2)

    for segs in all_rays:
        for a, b, inside in segs:
            if not is_valid_point(a) or not is_valid_point(b):
                continue
            col = COL_INSIDE if inside else COL_AIR
            try:
                pygame.draw.line(screen, col, a, b, 3)
            except Exception:
                continue
            safe_draw_circle(screen, col, b, 3)
    pygame.display.flip()

# ---------------- Main ----------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Stable Refraction Simulation")

    shapes = generate_shapes(NUM_SQUARES, NUM_TRIANGLES, SQUARE_SIZE, TRI_SIZE, WIDTH, HEIGHT, seed=None)

    # three left-side rays
    sources = [
        (0.0, HEIGHT * 0.25),
        (0.0, HEIGHT * 0.50),
        (0.0, HEIGHT * 0.75)
    ]
    direction = (1.0, 0.0)

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
                    shapes = generate_shapes(NUM_SQUARES, NUM_TRIANGLES, SQUARE_SIZE, TRI_SIZE, WIDTH, HEIGHT, seed=None)
                    recompute = True
                elif ev.key == pygame.K_ESCAPE:
                    running = False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    # move middle source to click Y (interactive)
                    mx, my = ev.pos
                    sources[1] = (0.0, float(my))
                    recompute = True

        if recompute:
            all_rays = []
            for sx, sy in sources:
                rayseg = trace_ray((sx, sy), direction, shapes)
                all_rays.append(rayseg)
            recompute = False

        draw_scene(screen, shapes, all_rays)
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
