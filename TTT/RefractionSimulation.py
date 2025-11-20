#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math, random, sys
from typing import List, Tuple, Optional, Set
import pygame

WIDTH, HEIGHT = 1200, 700
NUM_SQUARES = 3
NUM_TRIANGLES = 3
SQUARE_SIZE = 120
TRI_SIZE = 130

REFRACTIVE_INDEX_AIR = 1.0
REFRACTIVE_INDEX_SHAPE = 1.5

MAX_BOUNCES = 80

BG = (20,20,30)
COL_SQ_EDGE = (230,230,230)
COL_TRI_EDGE = (255,200,120)
COL_FILL = (80,120,160,70)

COL_AIR = (255,220,60)
COL_INSIDE = (255,100,100)

# --- vector utils ---
def v_add(a,b): return (a[0]+b[0], a[1]+b[1])
def v_sub(a,b): return (a[0]-b[0], a[1]-b[1])
def v_mul(a,s): return (a[0]*s, a[1]*s)
def v_dot(a,b): return a[0]*b[0] + a[1]*b[1]
def v_len(a): return math.hypot(a[0],a[1])
def v_norm(a):
    L=v_len(a)
    return (a[0]/L,a[1]/L) if L>1e-9 else (0,0)
def perp(a): return (-a[1],a[0])

# ---- ray / segment intersection
def ray_seg(p,v,a,b):
    r=v
    s=v_sub(b,a)
    rxs = r[0]*s[1]-r[1]*s[0]
    if abs(rxs)<1e-12: return None
    ap=v_sub(a,p)
    t=(ap[0]*s[1]-ap[1]*s[0])/rxs
    u=(ap[0]*r[1]-ap[1]*r[0])/rxs
    return (t,u)

# ---- snell
def refract_or_reflect(v,n,n1,n2):
    if v_dot(n,v)>0: n=v_mul(n,-1)
    cos_i = -v_dot(n,v)
    ratio = n1/n2
    sin_t2 = ratio**2*(1-cos_i*cos_i)
    if sin_t2>1:
        # total reflection
        r = v_sub(v, v_mul(n,2*v_dot(v,n)))
        return ("reflect",v_norm(r))
    cos_t = math.sqrt(max(0,1-sin_t2))
    tdir = v_add(v_mul(v,ratio), v_mul(n, ratio*cos_i - cos_t))
    return ("refract", v_norm(tdir))

# --- shapes ---
def make_square(cx,cy,size,ang):
    h=size/2
    pts=[(-h,-h),(h,-h),(h,h),(-h,h)]
    ca,sa=math.cos(ang),math.sin(ang)
    out=[]
    for x,y in pts:
        rx=x*ca - y*sa
        ry=x*sa + y*ca
        out.append((cx+rx,cy+ry))
    return out

def make_triangle(cx,cy,size,ang):
    # 等边三角形
    h=size*math.sqrt(3)/2
    pts=[(0,-h/2),(size/2,h/2),(-size/2,h/2)]
    ca,sa=math.cos(ang),math.sin(ang)
    out=[]
    for x,y in pts:
        rx=x*ca - y*sa
        ry=x*sa + y*ca
        out.append((cx+rx,cy+ry))
    return out

def poly_aabb(poly):
    xs=[p[0] for p in poly]; ys=[p[1] for p in poly]
    return (min(xs),min(ys),max(xs),max(ys))

def overlap(a,b):
    return not (a[2]<b[0] or a[0]>b[2] or a[3]<b[1] or a[1]>b[3])

# --- outward normal ---
def outward_normal(a,b,poly):
    mid=((a[0]+b[0])*0.5, (a[1]+b[1])*0.5)
    cx=sum(p[0] for p in poly)/len(poly)
    cy=sum(p[1] for p in poly)/len(poly)
    to_center=v_sub((cx,cy),mid)
    n=v_norm(perp(v_sub(b,a)))
    if v_dot(n,to_center)>0:
        n=v_mul(n,-1)
    return n

# --- generate shapes ---
def generate_shapes():
    shapes=[]
    margin=100
    tries=0

    # square + triangle count
    target = NUM_SQUARES+NUM_TRIANGLES

    while len(shapes)<target:
        tries+=1
        if tries>8000: break

        is_square = (len(shapes)<NUM_SQUARES)
        if is_square:
            size=SQUARE_SIZE
            ang=random.uniform(0,math.pi*2)
            cx=random.uniform(margin,WIDTH-margin)
            cy=random.uniform(margin,HEIGHT-margin)
            poly=make_square(cx,cy,size,ang)
        else:
            size=TRI_SIZE
            ang=random.uniform(0,math.pi*2)
            cx=random.uniform(margin,WIDTH-margin)
            cy=random.uniform(margin,HEIGHT-margin)
            poly=make_triangle(cx,cy,size,ang)

        box=poly_aabb(poly)

        ok=True
        for s in shapes:
            if overlap(box,s["aabb"]):
                ok=False
                break
        if not ok: continue

        shapes.append({"poly":poly,"aabb":box,"is_square":is_square})
    return shapes

# --- trace ray ---
def trace_ray(origin,dir,shapes):
    p=origin
    v=v_norm(dir)
    segments=[]
    inside:set[int]=set()

    # edges
    edges=[]
    for i,sh in enumerate(shapes):
        poly=sh["poly"]
        n=len(poly)
        for j in range(n):
            a=poly[j]
            b=poly[(j+1)%n]
            edges.append((a,b,i))

    for _ in range(MAX_BOUNCES):
        hitE=None; hitT=1e18
        for (a,b,pid) in edges:
            r=ray_seg(p,v,a,b)
            if not r: continue
            t,u=r
            if t<1e-6 or u<0 or u>1: continue
            if t<hitT:
                hitT=t; hitE=(a,b,pid)
        if not hitE:
            # exit
            tx=(WIDTH-p[0])/v[0] if v[0]>0 else 1e18
            ty=(HEIGHT-p[1])/v[1] if v[1]>0 else 1e18
            tmin=min(tx,ty)
            endp=v_add(p,v_mul(v,tmin))
            segments.append((p,endp, len(inside)>0))
            break

        a,b,pid = hitE
        inter=v_add(p,v_mul(v,hitT))
        segments.append((p,inter, len(inside)>0))

        poly=shapes[pid]["poly"]
        n=outward_normal(a,b,poly)

        entering = pid not in inside
        n1 = REFRACTIVE_INDEX_AIR if entering else REFRACTIVE_INDEX_SHAPE
        n2 = REFRACTIVE_INDEX_SHAPE if entering else REFRACTIVE_INDEX_AIR

        mode,newv = refract_or_reflect(v,n,n1,n2)
        if mode=="refract":
            if entering: inside.add(pid)
            else: inside.discard(pid)

        p=v_add(inter,v_mul(newv,1e-4))
        v=newv

    return segments

# --- draw ---
def draw_scene(screen, shapes, rays):
    screen.fill(BG)
    surf=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)

    for sh in shapes:
        pygame.draw.polygon(surf, COL_FILL, sh["poly"])
    screen.blit(surf,(0,0))

    for sh in shapes:
        col = COL_SQ_EDGE if sh["is_square"] else COL_TRI_EDGE
        pygame.draw.polygon(screen, col, sh["poly"],2)

    for segs in rays:
        for a,b,inside in segs:
            col = COL_INSIDE if inside else COL_AIR
            pygame.draw.line(screen,col,a,b,3)
            pygame.draw.circle(screen,col,(int(b[0]),int(b[1])),3)

    pygame.display.flip()


# --- main ---
def main():
    pygame.init()
    screen=pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Squares + Triangles Refraction")

    shapes=generate_shapes()
    direction=(1,0)

    sources=[
        (0, HEIGHT*0.25),
        (0, HEIGHT*0.50),
        (0, HEIGHT*0.75)
    ]

    running=True
    clock=pygame.time.Clock()

    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_r:
                    shapes=generate_shapes()

        rays=[]
        for sx,sy in sources:
            rays.append(trace_ray((sx,sy),direction,shapes))

        draw_scene(screen, shapes, rays)
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()
