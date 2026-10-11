#!/usr/bin/env python3
"""Procedural World Generation v3 — PySide6 Ultimate Edition
New: Day/Night, Animated Water, Elevation Profile, Annotations, Region Names,
Coastline Highlight, Export JSON, Climate Zones, Village Variety, Minimap Villages."""

import sys, math, random, heapq, json
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QSlider, QSpinBox, QCheckBox, QPushButton,
    QComboBox, QProgressBar, QScrollArea, QFileDialog, QSplitter,
    QSizePolicy, QSpacerItem, QToolButton, QMenu, QLineEdit, QDialog,
    QDialogButtonBox, QFormLayout
)
from PySide6.QtCore import Qt, QThread, Signal, QPoint, Slot, QTimer
from PySide6.QtGui import (QPainter, QImage, QColor, QPen, QFont, QPolygon,
                            QRadialGradient)

DEEP_WATER, SHALLOW_WATER, BEACH = 0, 1, 2
DESERT, GRASSLAND, FOREST, SWAMP = 3, 4, 5, 6
TUNDRA, TAIGA, MOUNTAIN, SNOW = 7, 8, 9, 10
BIOME_CT = 11

BIOME_RGB = {
    DEEP_WATER:(26,60,138), SHALLOW_WATER:(50,102,184), BEACH:(210,195,145),
    DESERT:(210,178,106), GRASSLAND:(106,178,64), FOREST:(40,115,45),
    SWAMP:(72,108,52), TUNDRA:(178,188,198), TAIGA:(30,90,48),
    MOUNTAIN:(128,118,106), SNOW:(238,238,248),
}
WINTER_RGB = {
    DEEP_WATER:(20,45,110), SHALLOW_WATER:(38,78,155), BEACH:(195,205,218),
    DESERT:(188,178,158), GRASSLAND:(188,198,212), FOREST:(55,98,82),
    SWAMP:(78,92,88), TUNDRA:(218,228,238), TAIGA:(42,82,72),
    MOUNTAIN:(158,155,165), SNOW:(245,245,252),
}
BIOME_NAME = {
    DEEP_WATER:"Deep Water", SHALLOW_WATER:"Shallow Water", BEACH:"Beach",
    DESERT:"Desert", GRASSLAND:"Grassland", FOREST:"Forest", SWAMP:"Swamp",
    TUNDRA:"Tundra", TAIGA:"Taiga", MOUNTAIN:"Mountain", SNOW:"Snow Peak",
}
BIOME_EMOJI = {
    DEEP_WATER:"🌊", SHALLOW_WATER:"💧", BEACH:"🏖", DESERT:"🏜",
    GRASSLAND:"🌾", FOREST:"🌲", SWAMP:"🌿", TUNDRA:"❄",
    TAIGA:"🌳", MOUNTAIN:"⛰", SNOW:"🏔",
}
RESOURCE_COLOR = {"gold":(255,215,0), "iron":(170,170,180), "gem":(200,80,255)}
CLIMATE_NAME = {0:"Polar", 1:"Subarctic", 2:"Temperate", 3:"Subtropical", 4:"Tropical"}
CLIMATE_COLOR = {0:(180,200,240), 1:(140,180,220), 2:(100,200,100), 3:(220,200,80), 4:(240,120,60)}
BIOME_LUT = np.array([BIOME_RGB[i] for i in range(BIOME_CT)], dtype=np.float64)
WINTER_LUT = np.array([WINTER_RGB[i] for i in range(BIOME_CT)], dtype=np.float64)

DARK_CSS = """
QMainWindow,QWidget{background:#1e1e2e;color:#cdd6f4;font-family:'Segoe UI',Arial,sans-serif;font-size:12px}
QGroupBox{border:1px solid #45475a;border-radius:6px;margin-top:14px;padding:14px 8px 8px;font-weight:bold;color:#89b4fa}
QGroupBox::title{subcontrol-origin:margin;left:12px;padding:0 6px}
QPushButton{background:#45475a;border:1px solid #585b70;border-radius:5px;padding:6px 12px;color:#cdd6f4;font-weight:bold}
QPushButton:hover{background:#585b70}QPushButton:pressed{background:#313244}
QPushButton:disabled{background:#313244;color:#6c7086}
QPushButton#genBtn{background:#89b4fa;color:#1e1e2e;font-size:13px;padding:10px;border:none}
QPushButton#genBtn:hover{background:#b4d0fb}QPushButton#genBtn:disabled{background:#45475a;color:#6c7086}
QPushButton#isoBtn{background:#a6e3a1;color:#1e1e2e;border:none}
QPushButton#isoBtn:hover{background:#c4f0c0}
QPushButton#fitBtn{background:#f9e2af;color:#1e1e2e;border:none;padding:4px 8px;font-size:11px}
QPushButton#fitBtn:hover{background:#fce8c8}
QPushButton#histBtn{background:#45475a;border:1px solid #585b70;padding:4px 8px;min-width:28px}
QPushButton#histBtn:hover{background:#585b70}QPushButton#histBtn:disabled{color:#313244;border-color:#313244}
QPushButton#profBtn{background:#74c7ec;color:#1e1e2e;border:none;padding:4px 10px;font-size:11px}
QPushButton#profBtn:hover{background:#9ee0f5}QPushButton#profBtn:checked{background:#f38ba8;color:#1e1e2e}
QSlider::groove:horizontal{height:6px;background:#313244;border-radius:3px}
QSlider::handle:horizontal{background:#89b4fa;width:16px;height:16px;margin:-5px 0;border-radius:8px}
QSpinBox,QComboBox,QLineEdit{background:#313244;border:1px solid #45475a;border-radius:4px;padding:4px 8px;color:#cdd6f4;min-height:22px}
QComboBox QAbstractItemView{background:#313244;color:#cdd6f4;selection-background-color:#45475a}
QCheckBox{spacing:7px}QCheckBox::indicator{width:16px;height:16px;border-radius:3px;border:1px solid #585b70;background:#313244}
QCheckBox::indicator:checked{background:#89b4fa;border-color:#89b4fa}
QProgressBar{background:#313244;border-radius:4px;height:7px;text-align:center;color:transparent}
QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #89b4fa,stop:1 #a6e3a1);border-radius:4px}
QStatusBar{background:#181825;color:#a6adc8;border-top:1px solid #313244;font-size:11px}
QScrollArea{border:none}QLabel{background:transparent}QSplitter::handle{background:#313244}
QToolButton{background:#45475a;border:1px solid #585b70;border-radius:5px;padding:5px 10px;color:#cdd6f4;font-weight:bold}
QToolButton:hover{background:#585b70}QToolButton::menu-indicator{image:none}
QMenu{background:#313244;color:#cdd6f4;border:1px solid #45475a;padding:4px}
QMenu::item{padding:5px 22px;border-radius:3px}QMenu::item:selected{background:#45475a}
QToolTip{background:#313244;color:#cdd6f4;border:1px solid #585b70;padding:4px;border-radius:3px}
"""


class PerlinNoise:
    def __init__(self, seed=0):
        rng = random.Random(seed); p = list(range(256)); rng.shuffle(p)
        self.perm = np.array(p + p, dtype=np.int32)
        self.gx = np.array([1,-1,1,-1,1,-1,0,0], dtype=np.float64)
        self.gy = np.array([1,1,-1,-1,0,0,1,-1], dtype=np.float64)
    def _grid(self, x, y):
        X = np.floor(x).astype(np.int32)&255; Y = np.floor(y).astype(np.int32)&255
        xf = x-np.floor(x); yf = y-np.floor(y)
        u = xf*xf*xf*(xf*(xf*6-15)+10); v = yf*yf*yf*(yf*(yf*6-15)+10)
        p = self.perm
        aa=p[p[X]+Y]&7; ab=p[p[X]+Y+1]&7; ba=p[p[X+1]+Y]&7; bb=p[p[X+1]+Y+1]&7
        d = lambda gi,dx,dy: self.gx[gi]*dx+self.gy[gi]*dy
        x1=d(aa,xf,yf)+u*(d(ba,xf-1,yf)-d(aa,xf,yf))
        x2=d(ab,xf,yf-1)+u*(d(bb,xf-1,yf-1)-d(ab,xf,yf-1))
        return x1+v*(x2-x1)
    def fractal(self, x, y, octaves=6, persistence=0.5):
        r=np.zeros_like(x,dtype=np.float64); a=1.0; ma=0.0; f=1.0
        for _ in range(octaves): r+=self._grid(x*f,y*f)*a; ma+=a; a*=persistence; f*=2.0
        return r/ma
    def ridge(self, x, y, octaves=6, persistence=0.5):
        r=np.zeros_like(x,dtype=np.float64); a=1.0; ma=0.0; f=1.0
        for _ in range(octaves):
            v=self._grid(x*f,y*f); r+=(1.0-np.abs(v))*a; ma+=a; a*=persistence; f*=2.0
        return r/ma


class NameGenerator:
    _pre=["Ash","Elm","Oak","Pine","Stone","Iron","Gold","Silver","Red","White","Black",
          "North","South","East","West","High","New","Old","Great","Little","Falcon","Wolf",
          "Bear","Deer","Raven","Storm","Clear","Mist","Shadow","Bright","Dawn","Dusk","Sun",
          "Moon","Star","Cloud","Frost","Amber","Cedar","Maple","Birch","Willow","Coral","Ivy","Sage","Thorn"]
    _suf=["wood","ford","bridge","haven","field","dale","vale","ton","ham","wick","mouth",
          "worth","stead","fell","moor","gate","cross","well","mill","port","hold","keep",
          "watch","rest","fall","rise","brook","lake","bury","crest","holm"]
    _cache={}
    @classmethod
    def village(cls, seed):
        if seed in cls._cache: return cls._cache[seed]
        rng=random.Random(seed); n=rng.choice(cls._pre)+rng.choice(cls._suf)
        cls._cache[seed]=n; return n


class RegionGenerator:
    _pre=["North","South","East","West","Upper","Lower","Great","Little","New","Old","High","Far","Outer","Inner"]
    _suf=["march","reach","vale","dale","heath","moor","fields","plains","coast","shore","hills","wood","land","wold"]
    @classmethod
    def generate(cls, biomes, seed, w, h, n_regions=10):
        rng=random.Random(seed+8000); land=(biomes!=DEEP_WATER)&(biomes!=SHALLOW_WATER)
        lys,lxs=np.where(land)
        if len(lxs)==0: return np.full((h,w),-1,dtype=np.int32),[]
        indices=rng.sample(range(len(lxs)),min(n_regions,len(lxs)))
        sx=np.array([lxs[i] for i in indices],dtype=np.float64)
        sy=np.array([lys[i] for i in indices],dtype=np.float64)
        regions=np.full((h,w),-1,dtype=np.int32); yy,xx=np.mgrid[:h,:w]
        best_d=np.full((h,w),1e18); n_seeds=len(sx)
        for ri in range(n_seeds):
            d=(xx-sx[ri])**2+(yy-sy[ri])**2
            better=land&(d<best_d); regions[better]=ri; best_d[better]=d[better]
        names=[f"{rng.choice(cls._pre)}{rng.choice(cls._suf)}" for _ in range(n_seeds)]
        return regions, names


class WorldGenerator:
    def __init__(self, w, h, seed, scale, octaves, persistence, preset="island", erosion=True):
        self.w,self.h,self.seed=w,h,seed
        self.scale,self.octaves,self.persistence=scale,octaves,persistence
        self.preset,self.erosion=preset,erosion
        self.heightmap=self.moisture=self.temperature=self.biomes=None
        self.rivers=self.trees=self.lakes=self.regions=self.climate=None
        self._river_paths=[]; self._river_flow=None
        self.villages=[]; self.roads=[]; self.resources=[]; self.region_names=[]
        self._xs=np.arange(w,dtype=np.float64)*scale
        self._ys=np.arange(h,dtype=np.float64)*scale
        self._X,self._Y=np.meshgrid(self._xs,self._ys)

    def gen_heightmap(self):
        n=PerlinNoise(self.seed); s,oc,pe=self.scale,self.octaves,self.persistence
        X,Y=self._X,self._Y
        if self.preset=="mountains":
            hm=n.ridge(X,Y,oc,pe); hm=(hm-hm.min())/(hm.max()-hm.min()+1e-10)
        else: hm=(n.fractal(X,Y,oc,pe)+1)*0.5
        hw,hh=self.w/2,self.h/2; dy,dx=np.ogrid[:self.h,:self.w]
        d=np.sqrt(((dx-hw)/hw)**2+((dy-hh)/hh)**2)
        if self.preset=="island": mask=np.clip(1-np.clip((d-0.5)*2,0,None),0,1)**0.6
        elif self.preset=="continent":
            mask=np.clip(0.35+0.65*np.clip(1-np.clip((d-0.7)*3,0,None),0,1),0,1)
            nm=(PerlinNoise(self.seed+999).fractal(X,Y,3,0.5)+1)*0.12
            mask=np.clip(mask+nm-0.1,0,1)
        elif self.preset=="archipelago":
            rng=random.Random(self.seed+123); mask=np.zeros((self.h,self.w),dtype=np.float64)
            for _ in range(rng.randint(5,12)):
                cx,cy=rng.uniform(0.2,0.8)*self.w,rng.uniform(0.2,0.8)*self.h
                r=rng.uniform(0.12,0.3)*min(self.w,self.h)
                dd=np.sqrt(((dx[...]-cx)/r)**2+((dy[...]-cy)/r)**2)
                mask=np.maximum(mask,np.clip(1-np.clip((dd-0.4)*2.5,0,None),0,1)**0.5)
        elif self.preset=="mountains":
            mask=np.clip(1-np.clip((d-0.8)*4,0,None),0,1)**0.4; mask=np.maximum(mask,0.3)
        else: mask=np.clip(1-np.clip((d-0.5)*2,0,None),0,1)**0.6
        self.heightmap=np.clip(hm*mask,0,1)
        if self.erosion and self.preset!="archipelago": self._erode()

    def _erode(self):
        hm=self.heightmap; w,h=self.w,self.h
        ys,xs=np.where(hm>0.38)
        if len(xs)==0: return
        n_part=min(40000,len(xs)); rng=random.Random(self.seed+7777)
        for _ in range(n_part):
            idx=rng.randint(0,len(xs)); px,py=float(xs[idx]),float(ys[idx])
            dx=dy=0.0; spd=1.0; wat=1.0; sed=0.0
            for _ in range(25):
                ix,iy=int(px),int(py)
                if not(1<=ix<w-1 and 1<=iy<h-1): break
                gx=(hm[iy,ix+1]-hm[iy,ix-1])*0.5; gy=(hm[iy+1,ix]-hm[iy-1,ix])*0.5
                dx=dx*0.2-gx; dy=dy*0.2-gy; ln=math.sqrt(dx*dx+dy*dy+1e-10); dx/=ln; dy/=ln
                npx,npy=px+dx,py+dy; nix,niy=int(npx),int(npy)
                if not(0<=nix<w and 0<=niy<h): break
                dh=hm[iy,ix]-hm[niy,nix]
                if dh<=0: break
                cap=max(dh,0.01)*spd*wat*4.0
                if sed>cap: dep=(sed-cap)*0.25; hm[iy,ix]+=dep; sed-=dep
                else: ero=min((cap-sed)*0.25,dh); hm[iy,ix]-=ero; sed+=ero
                spd=math.sqrt(max(0,spd*spd+dh*0.5)); wat*=0.995; px,py=npx,npy
        for _ in range(2):
            p2=np.pad(hm,1,mode='edge')
            hm=(p2[:-2,:-2]+p2[:-2,1:-1]+p2[:-2,2:]+p2[1:-1,:-2]+p2[1:-1,1:-1]+p2[1:-1,2:]+p2[2:,:-2]+p2[2:,1:-1]+p2[2:,2:])/9.0
        self.heightmap = np.clip(hm, 0, 1)

    def gen_moisture(self):
        n = PerlinNoise(self.seed + 1000); s = self.scale * 0.8; oc = max(1, self.octaves - 1)
        X, Y = np.meshgrid(np.arange(self.w, dtype=np.float64) * s,
                           np.arange(self.h, dtype=np.float64) * s)
        self.moisture = (n.fractal(X, Y, oc, self.persistence) + 1) * 0.5

    def gen_temperature(self):
        lat = 1.0 - 2.0 * np.abs(np.arange(self.h, dtype=np.float64) - self.h / 2) / (self.h / 2)
        base = (lat * 0.7 + 0.15).reshape(-1, 1)
        n = PerlinNoise(self.seed + 2000); s = self.scale * 0.6; oc = max(1, self.octaves - 2)
        X, Y = np.meshgrid(np.arange(self.w, dtype=np.float64) * s,
                           np.arange(self.h, dtype=np.float64) * s)
        noise = (n.fractal(X, Y, oc, self.persistence) + 1) * 0.25
        ep = np.clip(self.heightmap - 0.4, 0, 1) * 0.5
        self.temperature = np.clip(base + noise - ep, 0, 1)

    def gen_climate(self):
        self.climate = np.clip((self.temperature * 4.5), 0, 4).astype(np.int32)

    def gen_biomes(self):
        h, m, t = self.heightmap, self.moisture, self.temperature
        bm = np.full((self.h, self.w), GRASSLAND, dtype=np.int32)
        bm[h < 0.25] = DEEP_WATER; bm[(h >= 0.25) & (h < 0.32)] = SHALLOW_WATER
        bm[(h >= 0.32) & (h < 0.36)] = BEACH
        land = (h >= 0.36) & (h < 0.65); high = (h >= 0.65) & (h < 0.75)
        hot = land & (t > 0.6); bm[hot & (m < 0.3)] = DESERT
        bm[hot & (m >= 0.3) & (m < 0.5)] = GRASSLAND
        bm[hot & (m >= 0.5) & (m < 0.75)] = FOREST; bm[hot & (m >= 0.75)] = SWAMP
        tmp = land & (t > 0.3) & (t <= 0.6); bm[tmp & (m < 0.3)] = GRASSLAND
        bm[tmp & (m >= 0.3) & (m < 0.65)] = FOREST; bm[tmp & (m >= 0.65)] = SWAMP
        cold = land & (t <= 0.3); bm[cold & (m < 0.4)] = TUNDRA; bm[cold & (m >= 0.4)] = TAIGA
        bm[high & (t <= 0.35)] = TUNDRA; bm[high & (t > 0.35)] = TAIGA
        bm[(h >= 0.75) & (h < 0.85)] = MOUNTAIN; bm[h >= 0.85] = SNOW
        if self.lakes is not None: bm[self.lakes] = SHALLOW_WATER
        self.biomes = bm

    def gen_lakes(self):
        water = self.biomes == SHALLOW_WATER; ocean = np.zeros_like(water)
        ocean[0, :] |= water[0, :]; ocean[-1, :] |= water[-1, :]
        ocean[:, 0] |= water[:, 0]; ocean[:, -1] |= water[:, -1]
        for _ in range(max(self.w, self.h)):
            nw = np.zeros_like(ocean)
            nw[1:, :] |= ocean[:-1, :]; nw[:-1, :] |= ocean[1:, :]
            nw[:, 1:] |= ocean[:, :-1]; nw[:, :-1] |= ocean[:, 1:]
            g = (nw & water) & ~ocean
            if not np.any(g): break
            ocean |= g
        self.lakes = water & ~ocean

    def gen_rivers(self):
        rm = np.zeros((self.h, self.w), dtype=bool); self._river_paths = []
        rng = random.Random(self.seed + 500)
        srcs = [(x, y) for y in range(4, self.h - 4, 6) for x in range(4, self.w - 4, 6)
                if self.biomes[y, x] in (MOUNTAIN, SNOW, TAIGA, TUNDRA) and self.heightmap[y, x] > 0.72]
        rng.shuffle(srcs)
        for sx, sy in srcs[:min(len(srcs), max(4, self.w * self.h // 18000))]:
            path = self._river(sx, sy, rm, rng)
            if len(path) > 5: self._river_paths.append(path)
        self.rivers = rm; self._compute_river_width()

    def _river(self, sx, sy, rm, rng):
        path = []; x, y, vis = sx, sy, set()
        for _ in range(self.w + self.h):
            if (x, y) in vis or not (0 <= x < self.w and 0 <= y < self.h): break
            vis.add((x, y)); path.append((x, y))
            for dy2 in range(-1, 2):
                for dx2 in range(-1, 2):
                    nx, ny = x + dx2, y + dy2
                    if 0 <= nx < self.w and 0 <= ny < self.h: rm[ny, nx] = True
            if self.biomes[y, x] in (DEEP_WATER, SHALLOW_WATER): break
            best, bh = (x, y), self.heightmap[y, x]
            for dy2 in range(-1, 2):
                for dx2 in range(-1, 2):
                    if dx2 == 0 and dy2 == 0: continue
                    nx, ny = x + dx2, y + dy2
                    if 0 <= nx < self.w and 0 <= ny < self.h and self.heightmap[ny, nx] < bh:
                        bh = self.heightmap[ny, nx]; best = (nx, ny)
            if best == (x, y): x += rng.choice([-1, 0, 1]); y += rng.choice([-1, 0, 1])
            else: x, y = best
        return path

    def _compute_river_width(self):
        flow = np.zeros((self.h, self.w), dtype=np.int32)
        for path in self._river_paths:
            for x, y in path: flow[y, x] += 1
        self._river_flow = flow; wide = self.rivers.copy()
        for thresh in [3, 8]:
            mask = flow >= thresh
            if np.any(mask):
                d = np.zeros_like(mask)
                d[1:, :] |= mask[:-1, :]; d[:-1, :] |= mask[1:, :]
                d[:, 1:] |= mask[:, :-1]; d[:, :-1] |= mask[:, 1:]
                wide |= d
                if thresh >= 8:
                    d2 = np.zeros_like(mask)
                    d2[1:, :] |= d[:-1, :]; d2[:-1, :] |= d[1:, :]
                    d2[:, 1:] |= d[:, :-1]; d2[:, :-1] |= d[:, 1:]
                    wide |= d2
        self.rivers = wide

    def gen_forests(self):
        tm = np.zeros((self.h, self.w), dtype=bool); rng = random.Random(self.seed + 2000)
        probs = np.zeros(BIOME_CT); probs[FOREST] = 0.14; probs[TAIGA] = 0.11; probs[GRASSLAND] = 0.025
        rands = rng.random((self.h, self.w))
        for bi, pr in zip(range(BIOME_CT), probs):
            if pr > 0: tm[(self.biomes == bi) & (rands < pr)] = True
        self.trees = tm

    def gen_resources(self):
        self.resources = []; rng = random.Random(self.seed + 6000)
        ys, xs = np.where(self.biomes == MOUNTAIN)
        if len(xs) == 0: return
        for i in range(len(xs)):
            x, y = xs[i], ys[i]; ht = self.heightmap[y, x]; r = rng.random()
            if ht > 0.82 and r < 0.004: self.resources.append((x, y, 'gem'))
            elif ht > 0.78 and r < 0.008: self.resources.append((x, y, 'gold'))
            elif ht > 0.75 and r < 0.02: self.resources.append((x, y, 'iron'))

    def gen_villages(self):
        self.villages = []; rng = random.Random(self.seed + 3000); cands = []
        for y in range(14, self.h - 14, 3):
            for x in range(14, self.w - 14, 3):
                b, ht = self.biomes[y, x], self.heightmap[y, x]
                if b not in (GRASSLAND, FOREST, DESERT) or not (0.38 < ht < 0.60): continue
                patch = self.heightmap[max(0, y - 8):y + 9, max(0, x - 8):x + 9]
                if np.ptp(patch) > 0.05: continue
                nw = False
                for dy2 in range(-14, 15, 3):
                    for dx2 in range(-14, 15, 3):
                        nx, ny = x + dx2, y + dy2
                        if 0 <= nx < self.w and 0 <= ny < self.h:
                            if self.rivers[ny, nx] or self.biomes[ny, nx] in (SHALLOW_WATER, DEEP_WATER):
                                nw = True; break
                    if nw: break
                if nw: cands.append((x, y))
        rng.shuffle(cands); md = max(45, min(self.w, self.h) // 5)
        for cx, cy in cands:
            if len(self.villages) >= max(3, min(15, len(cands) // 6)): break
            if all(math.hypot(cx - vx, cy - vy) >= md for vx, vy, _, _, _ in self.villages):
                houses = [(cx + rng.randint(-8, 8), cy + rng.randint(-8, 8)) for _ in range(rng.randint(4, 9))]
                pop = rng.randint(20, 500)
                ns = hash((cx, cy, self.seed)) & 0xFFFFFFFF
                vtype = rng.choice(["Town", "Village", "Hamlet", "City" if pop > 300 else "Village"])
                self.villages.append((cx, cy, houses, NameGenerator.village(ns), pop, vtype))

    def gen_roads(self):
        self.roads = []; n = len(self.villages)
        if n < 2: return
        conn, rem = {0}, set(range(1, n))
        while rem:
            bd, bp = 1e18, None
            for ci in conn:
                cx, cy = self.villages[ci][0], self.villages[ci][1]
                for ri in rem:
                    rx, ry = self.villages[ri][0], self.villages[ri][1]
                    d = math.hypot(cx - rx, cy - ry)
                    if d < bd: bd, bp = d, (ci, ri)
            if bp is None: break
            ci, ri = bp
            p = self._astar((self.villages[ci][0], self.villages[ci][1]),
                            (self.villages[ri][0], self.villages[ri][1]))
            if p: self.roads.append(p)
            conn.add(ri); rem.discard(ri)
        rng = random.Random(self.seed + 4000)
        for _ in range(min(3, n // 2)):
            i, j = rng.sample(range(n), 2)
            p = self._astar((self.villages[i][0], self.villages[i][1]),
                            (self.villages[j][0], self.villages[j][1]))
            if p: self.roads.append(p)

    def _astar(self, start, end):
        sx = max(0, min(self.w - 1, start[0])); sy = max(0, min(self.h - 1, start[1]))
        ex = max(0, min(self.w - 1, end[0])); ey = max(0, min(self.h - 1, end[1]))
        heap = [(0, sx, sy)]; came = {}; gs = {(sx, sy): 0}; closed = set()
        h = lambda x, y: math.hypot(x - ex, y - ey); it = 0; lim = self.w * self.h // 3
        while heap and it < lim:
            it += 1; _, cx, cy = heapq.heappop(heap)
            if (cx, cy) in closed: continue
            closed.add((cx, cy))
            if cx == ex and cy == ey:
                path, cur = [], (ex, ey)
                while cur in came: path.append(cur); cur = came[cur]
                path.append((sx, sy)); path.reverse(); return path
            for dx2, dy2 in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = cx + dx2, cy + dy2
                if not (0 <= nx < self.w and 0 <= ny < self.h) or (nx, ny) in closed: continue
                if self.biomes[ny, nx] in (DEEP_WATER, SNOW): continue
                hd = abs(self.heightmap[ny, nx] - self.heightmap[cy, cx])
                cost = math.sqrt(dx2 * dx2 + dy2 * dy2) + hd * 12
                if self.biomes[ny, nx] == SHALLOW_WATER: cost += 6
                elif self.biomes[ny, nx] == MOUNTAIN: cost += 4
                ng = gs[(cx, cy)] + cost
                if ng < gs.get((nx, ny), 1e18):
                    gs[(nx, ny)] = ng; came[(nx, ny)] = (cx, cy)
                    heapq.heappush(heap, (ng + h(nx, ny), nx, ny))
        return None

    def gen_regions(self):
        self.regions, self.region_names = RegionGenerator.generate(
            self.biomes, self.seed, self.w, self.h, n_regions=max(4, min(12, self.w * self.h // 12000)))

    def to_dict(self):
        return {
            "seed": self.seed, "width": self.w, "height": self.h,
            "preset": self.preset, "villages": [
                {"name": n, "x": int(cx), "y": int(cy), "population": pop, "type": vt}
                for cx, cy, _, n, pop, vt in self.villages],
            "resources": [{"x": int(x), "y": int(y), "type": t} for x, y, t in self.resources],
            "regions": [{"name": n, "id": i} for i, n in enumerate(self.region_names)],
            "biome_counts": {BIOME_NAME[i]: int(np.sum(self.biomes == i)) for i in range(BIOME_CT)},
        }


class GenWorker(QObject):
    progress = Signal(str, int); done = Signal(object); error = Signal(str)

    @Slot()
    def run(self, params):
        try:
            g = WorldGenerator(**params)
            g.gen_heightmap(); self.progress.emit("Generating moisture...", 14); g.gen_moisture()
            self.progress.emit("Computing temperature...", 22); g.gen_temperature()
            self.progress.emit("Computing climate...", 28); g.gen_climate()
            self.progress.emit("Detecting lakes...", 34); g.gen_lakes()
            self.progress.emit("Determining biomes...", 42); g.gen_biomes()
            self.progress.emit("Carving rivers...", 54); g.gen_rivers()
            self.progress.emit("Planting forests...", 64); g.gen_forests()
            self.progress.emit("Placing resources...", 70); g.gen_resources()
            self.progress.emit("Naming regions...", 76); g.gen_regions()
            self.progress.emit("Founding villages...", 84); g.gen_villages()
            self.progress.emit("Laying roads...", 93); g.gen_roads()
            self.progress.emit("Complete!", 100); self.done.emit(g)
        except Exception as e:
            self.error.emit(str(e))


def _qi(colors):
    h, w, _ = colors.shape; buf = np.zeros((h, w, 4), dtype=np.uint8)
    buf[:, :, 0] = colors[:, :, 2]; buf[:, :, 1] = colors[:, :, 1]
    buf[:, :, 2] = colors[:, :, 0]; buf[:, :, 3] = 255
    return QImage(buf.data, w, h, w * 4, QImage.Format_RGB32).copy()


def _draw_compass(p, x, y, sz):
    p.save(); p.translate(x, y)
    p.setPen(QPen(QColor(200, 200, 220, 130), 1)); p.setBrush(QColor(30, 30, 46, 140))
    p.drawEllipse(-sz, -sz, sz * 2, sz * 2)
    p.setPen(Qt.NoPen); p.setBrush(QColor(220, 55, 55))
    p.drawPolygon(QPoint(0, -sz + 5), QPoint(-5, 0), QPoint(5, 0))
    p.setBrush(QColor(200, 200, 220, 170))
    p.drawPolygon(QPoint(0, sz - 5), QPoint(-5, 0), QPoint(5, 0))
    p.setPen(QPen(QColor(200, 200, 220, 100), 1)); p.drawLine(-sz + 5, 0, sz - 5, 0)
    p.setFont(QFont("Segoe UI", 7, QFont.Bold))
    p.setPen(QColor(220, 55, 55)); p.drawText(-4, -sz + 17, "N")
    p.setPen(QColor(200, 200, 220, 180))
    p.drawText(-3, sz - 6, "S"); p.drawText(sz - 13, 4, "E"); p.drawText(-sz + 7, 4, "W")
    p.restore()


def render_world(gen, show_biomes, show_rivers, show_forests, show_villages,
                 show_roads, show_hmap, show_grid=False, show_contours=False,
                 show_temp=False, show_clouds=False, show_compass=False,
                 show_resources=False, winter=False, highlight_biome=-1,
                 night=0.0, anim_t=0.0, show_climate=False, show_coast=False,
                 show_regions=False, show_minimap_villages=False, annotations=None):
    w, h = gen.w, gen.h
    if show_hmap:
        gray = (gen.heightmap * 255).astype(np.uint8)
        c = np.stack([gray, gray, gray], axis=-1).astype(np.float64)
        if show_contours:
            for lv in np.arange(0.1, 0.95, 0.05):
                ab = gen.heightmap >= lv; cm = np.zeros_like(ab)
                cm[:, :-1] |= ab[:, :-1] != ab[:, 1:]; cm[:, 1:] |= ab[:, :-1] != ab[:, 1:]
                cm[:-1, :] |= ab[:-1, :] != ab[1:, :]; cm[1:, :] |= ab[:-1, :] != ab[1:, :]
                c[cm] *= 0.5
        if show_grid:
            gs2 = max(8, min(w, h) // 16); c[::gs2, :] *= 0.6; c[:, ::gs2] *= 0.6
        img = _qi(np.clip(c, 0, 255).astype(np.uint8))
        if show_compass:
            p2 = QPainter(img); _draw_compass(p2, w - 35, h - 35, 22); p2.end()
        return img

    lut = WINTER_LUT if winter else BIOME_LUT
    colors = lut[gen.biomes].copy()
    gx = np.zeros((h, w), dtype=np.float64); gy = np.zeros_like(gx)
    gx[:, 1:-1] = (gen.heightmap[:, 2:] - gen.heightmap[:, :-2]) * 0.5
    gy[1:-1, :] = (gen.heightmap[2:, :] - gen.heightmap[:-2, :]) * 0.5
    shade = 0.5 + 0.6 * (-gx + gy) / np.sqrt(gx * gx + gy * gy + 0.01)
    colors *= np.clip(shade, 0.45, 1.15)[:, :, None]

    if show_biomes:
        bm = gen.biomes; edge = np.zeros((h, w), dtype=bool)
        eh = bm[:-1, :] != bm[1:, :]; ev = bm[:, :-1] != bm[:, 1:]
        edge[:-1, :] |= eh; edge[1:, :] |= eh; edge[:, :-1] |= ev; edge[:, 1:] |= ev
        shifts = [np.roll(np.roll(colors, -dy, 0), -dx, 1) for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        avg = np.mean(shifts + [colors], axis=0); orig = colors.copy()
        colors[edge] = avg[edge]; colors[0, :] = orig[0, :]; colors[-1, :] = orig[-1, :]
        colors[:, 0] = orig[:, 0]; colors[:, -1] = orig[:, -1]

    xv = ((np.arange(w)[None, :] * 17 + np.arange(h)[:, None] * 31) % 17 - 8).astype(np.float64)
    colors += xv[:, :, None]

    water = (gen.biomes == SHALLOW_WATER) | (gen.biomes == DEEP_WATER); land = ~water
    foam = np.zeros((h, w), dtype=bool)
    foam[1:, :] |= water[1:, :] & land[:-1, :]; foam[:-1, :] |= water[:-1, :] & land[1:, :]
    foam[:, 1:] |= water[:, 1:] & land[:, :-1]; foam[:, :-1] |= water[:, :-1] & land[:, 1:]

    if show_coast:
        coast = np.zeros((h, w), dtype=bool)
        coast[1:, :] |= land[1:, :] & water[:-1, :]; coast[:-1, :] |= land[:-1, :] & water[1:, :]
        coast[:, 1:] |= land[:, 1:] & water[:, :-1]; coast[:, :-1] |= land[:, :-1] & water[:, 1:]
        colors[coast] = np.clip(colors[coast] * 1.15 + 20, 0, 255)

    if show_rivers and gen.rivers is not None:
        # Animated water shimmer
        shimmer = 0
        if anim_t > 0:
            phase = (anim_t % 100) / 100.0 * math.pi * 2
            shimmer = int(8 * math.sin(phase))
        colors[gen.rivers] = [45 + shimmer, 105 + shimmer, 210]
        if gen._river_flow is not None:
            deep = gen._river_flow >= 5
            colors[deep & gen.rivers] = [30 + shimmer, 78 + shimmer, 175]
    else:
        foam[:] = False

    if gen.lakes is not None:
        lf = np.zeros((h, w), dtype=bool)
        lf[1:, :] |= gen.lakes[1:, :] & ~gen.lakes[:-1, :]; lf[:-1, :] |= gen.lakes[:-1, :] & ~gen.lakes[1:, :]
        lf[:, 1:] |= gen.lakes[:, 1:] & ~gen.lakes[:, :-1]; lf[:, :-1] |= gen.lakes[:, :-1] & ~gen.lakes[:, 1:]
        colors[lf] = [65, 135, 215]

    if show_temp:
        t = gen.temperature; colors[:, :, 0] += np.clip((t - 0.4) * 90, 0, 55)
        colors[:, :, 2] += np.clip((0.4 - t) * 90, 0, 55)

    if show_climate and gen.climate is not None:
        for cid, (r2, g2, b2) in CLIMATE_COLOR.items():
            mask = gen.climate == cid
            colors[mask] = colors[mask] * 0.5 + np.array([r2, g2, b2]) * 0.5

    if show_regions and gen.regions is not None:
        rng_r = random.Random(gen.seed + 9000)
        n_reg = len(gen.region_names)
        reg_colors = np.zeros((n_reg, 3))
        for i in range(n_reg):
            hue = (i / max(n_reg, 1)) * 360
            reg_colors[i] = _hsv_to_rgb(hue, 0.3, 0.9)
        for ri in range(n_reg):
            mask = gen.regions == ri
            colors[mask] = colors[mask] * 0.65 + reg_colors[ri] * 0.35
        # Region borders
        rb = np.zeros((h, w), dtype=bool)
        rb[:, :-1] |= gen.regions[:, :-1] != gen.regions[:, 1:]
        rb[:, 1:] |= gen.regions[:, :-1] != gen.regions[:, 1:]
        rb[:-1, :] |= gen.regions[:-1, :] != gen.regions[1:, :]
        rb[1:, :] |= gen.regions[:-1, :] != gen.regions[1:, :]
        land_mask = (gen.biomes != DEEP_WATER) & (gen.biomes != SHALLOW_WATER)
        colors[rb & land_mask] *= 0.5

    if show_clouds:
        cn = PerlinNoise(gen.seed + 5000)
        cs = gen.scale * 0.4
        cx2, cy2 = np.meshgrid(np.arange(w, dtype=np.float64) * cs,
                                np.arange(h, dtype=np.float64) * cs)
        cl = (cn.fractal(cx2, cy2, 4, 0.5) + 1) * 0.5
        cloud_mask = cl > 0.58
        alpha = np.clip((cl[cloud_mask] - 0.58) * 5, 0, 0.55)
        for i in range(3): colors[cloud_mask, i] = colors[cloud_mask, i] * (1 - alpha) + 255 * alpha

    if show_contours:
        for lv in np.arange(0.1, 0.95, 0.05):
            ab = gen.heightmap >= lv; cm = np.zeros_like(ab)
            cm[:, :-1] |= ab[:, :-1] != ab[:, 1:]; cm[:, 1:] |= ab[:, :-1] != ab[:, 1:]
            cm[:-1, :] |= ab[:-1, :] != ab[1:, :]; cm[1:, :] |= ab[:-1, :] != ab[1:, :]
            colors[cm] *= 0.55

    if show_grid:
        gs2 = max(8, min(w, h) // 16); colors[::gs2, :] *= 0.6; colors[:, ::gs2] *= 0.6

    if highlight_biome >= 0:
        hm2 = gen.biomes == highlight_biome
        r2, g2, b2 = BIOME_RGB[highlight_biome]
        colors[hm2] = [min(255, r2 + 60), min(255, g2 + 60), min(255, b2 + 60)]
        colors[~hm2] *= 0.35

    if night > 0:
        light = np.clip(1.0 - night * 0.85, 0.12, 1.0)
        colors *= light
        # Village glow at night
        if show_villages and night > 0.3:
            for vx, vy, _, _, _, _ in gen.villages:
                yy, xx = np.ogrid[:h, :w]
                dist = np.sqrt(((xx - vx) / 6.0) ** 2 + ((yy - vy) / 6.0) ** 2)
                glow = np.clip(1.0 - dist, 0, 1) * night * 180
                colors[:, :, 0] += glow; colors[:, :, 1] += glow * 0.7

    img = _qi(np.clip(colors, 0, 255).astype(np.uint8))
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)

    if show_forests and gen.trees is not None and w <= 400:
        rng2 = random.Random(gen.seed + 9999)
        ys2, xs2 = np.where(gen.trees)
        for i in range(len(xs2)):
            tx, ty = int(xs2[i]), int(ys2[i]); sz = rng2.choice([1, 1, 1, 2, 2, 3])
            sh = rng2.randint(-18, 18); g = max(30, min(120, 72 + sh))
            if gen.biomes[ty, tx] == TAIGA: c = QColor(12, g - 10, 20)
            elif winter: c = QColor(30, g, 50)
            else: c = QColor(14, g, 14)
            p.setPen(Qt.NoPen); p.setBrush(c); p.drawEllipse(tx - sz, ty - sz, sz * 2, sz * 2 + 1)

    if show_villages:
        rng3 = random.Random(gen.seed + 6000)
        fc = [QColor(170, 175, 65, 100), QColor(90, 145, 55, 100), QColor(150, 130, 55, 100)]
        if winter: fc = [QColor(200, 205, 210, 80), QColor(180, 190, 200, 80), QColor(190, 195, 205, 80)]
        for cx, cy, houses, name, pop, vtype in gen.villages:
            for _ in range(rng3.randint(8, 18)):
                fx, fy = cx + rng3.randint(-13, 13), cy + rng3.randint(-13, 13)
                if 0 <= fx < w and 0 <= fy < h and gen.biomes[fy, fx] in (GRASSLAND, FOREST) and not gen.rivers[fy, fx]:
                    p.setPen(Qt.NoPen); p.setBrush(rng3.choice(fc)); p.drawRect(fx - 2, fy - 2, 5, 5)
            for hx, hy in houses:
                p.setBrush(QColor(160, 100, 50)); p.drawRect(hx - 2, hy - 3, 5, 5)
                p.setBrush(QColor(125, 65, 30))
                p.drawConvexPolygon([QPoint(hx - 3, hy - 3), QPoint(hx + 3, hy - 3), QPoint(hx, hy - 6)])
            # Night glow circle
            if night > 0.3:
                grad = QRadialGradient(cx, cy, 12)
                grad.setColorAt(0, QColor(255, 200, 80, int(night * 120)))
                grad.setColorAt(1, QColor(255, 200, 80, 0))
                p.setPen(Qt.NoPen); p.setBrush(grad); p.drawEllipse(cx - 12, cy - 12, 24, 24)
            marker_col = {"City": QColor(255, 50, 50), "Town": QColor(230, 120, 40),
                          "Village": QColor(230, 55, 55), "Hamlet": QColor(180, 80, 80)}
            p.setBrush(marker_col.get(vtype, QColor(230, 55, 55)))
            msz = 5 if vtype == "City" else 3
            p.drawEllipse(cx - msz, cy - msz, msz * 2, msz * 2)
            p.setPen(QPen(QColor(255, 255, 255, 200))); p.setFont(QFont("Segoe UI", 7, QFont.Bold))
            p.drawText(cx - p.fontMetrics().horizontalAdvance(name) // 2, cy - 10, name)

    if show_roads:
        for path in gen.roads:
            if len(path) < 2: continue
            p.setPen(QPen(QColor(85, 65, 35), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            for i in range(len(path) - 1): p.drawLine(*path[i], *path[i + 1])
            p.setPen(QPen(QColor(165, 140, 90), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            for i in range(len(path) - 1): p.drawLine(*path[i], *path[i + 1])
            for i in range(len(path) - 1):
                mx2 = (path[i][0] + path[i + 1][0]) // 2; my2 = (path[i][1] + path[i + 1][1]) // 2
                if 0 <= mx2 < w and 0 <= my2 < h and gen.rivers[my2, mx2]:
                    p.setPen(Qt.NoPen); p.setBrush(QColor(120, 80, 40)); p.drawRect(mx2 - 4, my2 - 3, 8, 6)
                    p.setBrush(QColor(160, 115, 60)); p.drawRect(mx2 - 3, my2 - 2, 6, 4)
                    p.setPen(QPen(QColor(90, 60, 30), 1))
                    p.drawLine(mx2 - 4, my2 - 3, mx2 + 4, my2 - 3)
                    p.drawLine(mx2 - 4, my2 + 3, mx2 + 4, my2 + 3)

    if show_resources:
        for rx, ry, rt in gen.resources:
            r2, g2, b2 = RESOURCE_COLOR[rt]
            p.setPen(QPen(QColor(0, 0, 0, 120), 1)); p.setBrush(QColor(r2, g2, b2))
            p.drawConvexPolygon([QPoint(rx, ry - 4), QPoint(rx + 3, ry), QPoint(rx, ry + 4), QPoint(rx - 3, ry)])

    # Region name labels
    if show_regions and gen.regions is not None:
        p.setFont(QFont("Segoe UI", 8, QFont.Bold)); p.setPen(QPen(QColor(255, 255, 255, 160)))
        for ri, rname in enumerate(gen.region_names):
            mask = gen.regions == ri
            if not np.any(mask): continue
            ys_r, xs_r = np.where(mask)
            cy_r, cx_r = int(ys_r.mean()), int(xs_r.mean())
            if 0 <= cx_r < w and 0 <= cy_r < h:
                p.drawText(cx_r - p.fontMetrics().horizontalAdvance(rname) // 2, cy_r, rname)

    # Annotations
    if annotations:
        p.setFont(QFont("Segoe UI", 9, QFont.Bold))
        for ax, ay, atext, acol in annotations:
            if 0 <= ax < w and 0 <= ay < h:
                tw = p.fontMetrics().horizontalAdvance(atext)
                p.setPen(Qt.NoPen); p.setBrush(QColor(0, 0, 0, 120))
                p.drawRoundedRect(ax - tw // 2 - 4, ay - 14, tw + 8, 18, 3, 3)
                p.setPen(QPen(QColor(acol))); p.drawText(ax - tw // 2, ay, atext)

    if show_compass: _draw_compass(p, w - 38, h - 38, 24)
    p.end(); return img


def _hsv_to_rgb(h, s, v):
    h2 = (h % 360) / 60.0; i = int(h2); f = h2 - i
    p2 = v * (1 - s); q = v * (1 - s * f); t = v * (1 - s * (1 - f))
    if i == 0: return [v * 255, t * 255, p2 * 255]
    elif i == 1: return [q * 255, v * 255, p2 * 255]
    elif i == 2: return [p2 * 255, v * 255, t * 255]
    elif i == 3: return [p2 * 255, q * 255, v * 255]
    elif i == 4: return [t * 255, p2 * 255, v * 255]
    else: return [v * 255, p2 * 255, q * 255]


def render_isometric(gen, max_dim=110):
    sc = min(1.0, max_dim / max(gen.w, gen.h))
    sw, sh = max(2, int(gen.w * sc)), max(2, int(gen.h * sc))
    yi = np.linspace(0, gen.h - 1, sh).astype(int); xi = np.linspace(0, gen.w - 1, sw).astype(int)
    hm = gen.heightmap[np.ix_(yi, xi)]; bm = gen.biomes[np.ix_(yi, xi)]
    tw, thh, hs = 3, 2, 38
    C, R = np.meshgrid(np.arange(sw), np.arange(sh))
    sx = (C - R).astype(float) * tw; sy = (C + R).astype(float) * thh - hm * hs
    bsy = (C + R).astype(float) * thh
    ox = -sx.min() + tw * 3; oy = -sy.min() + hs + thh * 3
    iw = int(sx.max() - sx.min()) + tw * 6; ih = int(sy.max() - sy.min()) + hs + thh * 6
    img = QImage(iw, ih, QImage.Format_RGB32); img.fill(QColor(18, 18, 30))
    p = QPainter(img)
    for r in range(sh):
        for c in range(sw):
            cx2, cy2 = int(sx[r, c] + ox), int(sy[r, c] + oy); by = int(bsy[r, c] + oy)
            rgb = BIOME_RGB.get(int(bm[r, c]), (128, 128, 128))
            top = QColor(*rgb); s1 = top.darker(155); s2 = top.darker(195)
            p.setPen(Qt.NoPen); p.setBrush(top)
            p.drawConvexPolygon([QPoint(cx2, cy2 - thh), QPoint(cx2 + tw, cy2),
                                 QPoint(cx2, cy2 + thh), QPoint(cx2 - tw, cy2)])
            if by > cy2 + thh:
                p.setBrush(s1)
                p.drawConvexPolygon([QPoint(cx2 - tw, cy2), QPoint(cx2, cy2 + thh),
                                     QPoint(cx2, by), QPoint(cx2 - tw, by - thh)])
                p.setBrush(s2)
                p.drawConvexPolygon([QPoint(cx2, cy2 + thh), QPoint(cx2 + tw, cy2),
                                     QPoint(cx2 + tw, by - thh), QPoint(cx2, by)])
    vsc = gen.w / sw
    for vx, vy, _, name, _, _ in gen.villages:
        vc, vr = int(vx / vsc), int(vy / vsc)
        if 0 <= vr < sh and 0 <= vc < sw:
            mcx = int(sx[vr, vc] + ox); mcy = int(sy[vr, vc] + oy) - 4
            p.setBrush(QColor(230, 55, 55)); p.drawEllipse(mcx - 3, mcy - 3, 6, 6)
            p.setPen(QPen(Qt.white)); p.setFont(QFont("Segoe UI", 6, QFont.Bold))
            p.drawText(mcx - 15, mcy - 6, name[:12])
    p.end(); return img


class MiniMap(QWidget):
    nav_requested = Signal(float, float)

    def __init__(self):
        super().__init__(); self.setFixedSize(155, 155); self.img = None; self._vr = None; self._gen = None

    def set_image(self, qimg):
        self.img = qimg.scaled(155, 155, Qt.KeepAspectRatio, Qt.FastTransformation)

    def set_gen(self, gen):
        self._gen = gen

    def set_viewport(self, rect):
        self._vr = rect; self.update()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.fillRect(self.rect(), QColor(24, 24, 37))
        if not self.img: p.end(); return
        x = (155 - self.img.width()) // 2; y = (155 - self.img.height()) // 2
        p.drawImage(x, y, self.img)
        if self._gen:
            sx = 155 / self._gen.w; sy = 155 / self._gen.h
            for vx, vy, _, _, _, _ in self._gen.villages:
                px = int(x + vx * sx); py = int(y + vy * sy)
                p.setPen(Qt.NoPen); p.setBrush(QColor(230, 55, 55, 200))
                p.drawEllipse(px - 2, py - 2, 4, 4)
        if self._vr and self.img.width() > 0:
            fx1, fy1, fx2, fy2 = self._vr; mw = self.img.width(); mh = self.img.height()
            ow = self._gen.w if self._gen else mw; oh = self._gen.h if self._gen else mh
            if fx2 > fx1 and fy2 > fy1:
                r = QRect(int(x + fx1 / ow * mw), int(y + fy1 / oh * mh),
                          int((fx2 - fx1) / ow * mw), int((fy2 - fy1) / oh * mh))
                p.setPen(QPen(QColor(255, 255, 255, 180), 1)); p.setBrush(QColor(255, 255, 255, 30))
                p.drawRect(r)
        p.setPen(QPen(QColor(69, 71, 90), 1)); p.setBrush(Qt.NoBrush)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1)); p.end()

    def mousePressEvent(self, e):
        if self.img:
            fx = (e.pos().x() - (155 - self.img.width()) // 2) / self.img.width()
            fy = (e.pos().y() - (155 - self.img.height()) // 2) / self.img.height()
            self.nav_requested.emit(max(0, min(1, fx)), max(0, min(1, fy)))


class MapWidget(QWidget):
    hover_info = Signal(str); viewport_changed = Signal(tuple)
    profile_requested = Signal(int, int, int, int)

    def __init__(self):
        super().__init__(); self.img = None; self.gen = None
        self.zoom = 1.0; self.off = QPoint(0, 0)
        self._drag = False; self._last = None; self._prof_start = None
        self.setMinimumSize(400, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True); self.setFocusPolicy(Qt.StrongFocus)

    def set_world(self, gen, img):
        self.gen = gen; self.img = img
        self.zoom = 1.0; self.off = QPoint(0, 0); self.update()
        self.viewport_changed.emit(self.visible_rect())

    def visible_rect(self):
        if not self.img: return None
        sw = self.img.width() * self.zoom; sh = self.img.height() * self.zoom
        ix = (self.width() - sw) / 2 + self.off.x(); iy = (self.height() - sh) / 2 + self.off.y()
        return (max(0, -ix / self.zoom), max(0, -iy / self.zoom),
                min(self.img.width(), (self.width() - ix) / self.zoom),
                min(self.img.height(), (self.height() - iy) / self.zoom))

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.fillRect(self.rect(), QColor(24, 24, 37))
        if not self.img: p.end(); return
        sw = int(self.img.width() * self.zoom); sh = int(self.img.height() * self.zoom)
        x = (self.width() - sw) // 2 + self.off.x(); y = (self.height() - sh) // 2 + self.off.y()
        p.drawImage(x, y, self.img.scaled(sw, sh, Qt.KeepAspectRatio, Qt.FastTransformation))
        # Elevation profile preview line
        if self._prof_start and self._last:
            p.setPen(QPen(QColor(116, 199, 236, 180), 1, Qt.DashLine))
            p.drawLine(self._prof_start, self._last)
        p.end()

    def wheelEvent(self, e):
        f = 1.15 if e.angleDelta().y() > 0 else 1 / 1.15; old = self.zoom
        self.zoom = max(0.3, min(15.0, self.zoom * f))
        r = self.zoom / old; mx, my = e.position().x(), e.position().y()
        cx2, cy2 = self.width() / 2, self.height() / 2
        self.off.setX(int((self.off.x() - (mx - cx2)) * r + (mx - cx2)))
        self.off.setY(int((self.off.y() - (my - cy2)) * r + (my - cy2)))
        self.update(); self.viewport_changed.emit(self.visible_rect())

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if e.modifiers() & Qt.ShiftModifier:
                self._prof_start = e.pos()
            else:
                self._drag = True; self._prof_start = None
            self._last = e.pos()

    def mouseMoveEvent(self, e):
        if self._drag and self._last:
            self.off += e.pos() - self._last; self._last = e.pos()
            self.update(); self.viewport_changed.emit(self.visible_rect())
        elif self._prof_start:
            self._last = e.pos(); self.update()
        elif self.gen:
            mp = self._to_map(e.pos())
            if mp:
                mx, my = mp; h = self.gen.heightmap[my, mx]; m = self.gen.moisture[my, mx]
                t = self.gen.temperature[my, mx]; bn = BIOME_NAME.get(self.gen.biomes[my, mx], "?")
                lk = " 🏞LAKE" if self.gen.lakes is not None and self.gen.lakes[my, mx] else ""
                cl = f" │ {CLIMATE_NAME.get(self.gen.climate[my, mx], '?')}" if self.gen.climate is not None else ""
                rg = ""
                if self.gen.regions is not None and self.gen.regions[my, mx] >= 0:
                    ri = self.gen.regions[my, mx]
                    if ri < len(self.gen.region_names): rg = f" │ {self.gen.region_names[ri]}"
                vn = ""
                for vx, vy, _, name, pop, vt in self.gen.villages:
                    if math.hypot(mx - vx, my - vy) < 12:
                        vn = f"  │  🏘 {name} ({vt}, pop {pop})"; break
                self.hover_info.emit(
                    f"  ({mx},{my})  │  Elev:{h:.3f}  Moist:{m:.3f}  Temp:{t:.2f}{cl}  │  {bn}{lk}{rg}{vn}  │  {self.zoom:.1f}x")
            else: self.hover_info.emit("")

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self._prof_start and self._last and (e.modifiers() & Qt.ShiftModifier):
            p1 = self._to_map(self._prof_start); p2 = self._to_map(e.pos())
            if p1 and p2:
                self.profile_requested.emit(p1[0], p1[1], p2[0], p2[1])
        self._drag = False; self._prof_start = None; self._last = None; self.update()

    def _to_map(self, pos):
        if not self.img: return None
        sw = self.img.width() * self.zoom; sh = self.img.height() * self.zoom
        ix = (self.width() - sw) / 2 + self.off.x(); iy = (self.height() - sh) / 2 + self.off.y()
        mx, my = int((pos.x() - ix) / self.zoom), int((pos.y() - iy) / self.zoom)
        if 0 <= mx < self.img.width() and 0 <= my < self.img.height(): return (mx, my)
        return None

    def zoom_to_fit(self):
        if not self.img: return
        self.zoom = min(self.width() / self.img.width(), self.height() / self.img.height()) * 0.95
        self.off = QPoint(0, 0); self.update(); self.viewport_changed.emit(self.visible_rect())

    def navigate_to(self, fx, fy):
        if not self.img: return
        self.zoom = min(self.width() / self.img.width(), self.height() / self.img.height()) * 0.95
        tx, ty = fx * self.img.width(), fy * self.img.height()
        self.off = QPoint(int(-tx * self.zoom), int(-ty * self.zoom))
        self.update(); self.viewport_changed.emit(self.visible_rect())


class ProfileDialog(QDialog):
    def __init__(self, gen, x1, y1, x2, y2, parent=None):
        super().__init__(parent); self.setWindowTitle("Elevation Profile")
        self.setMinimumSize(500, 250); self.resize(600, 280)
        self.gen = gen; self.img = None
        # Bresenham line
        pts = []
        dx2, dy2 = abs(x2 - x1), abs(y2 - y1); sx = 1 if x1 < x2 else -1; sy = 1 if y1 < y2 else -1
        err = dx2 - dy2; cx, cy = x1, y1
        while True:
            pts.append((cx, cy))
            if cx == x2 and cy == y2: break
            e2 = 2 * err
            if e2 > -dy2: err -= dy2; cx += sx
            if e2 < dx2: err += dx2; cy += sy
        self.elevations = [gen.heightmap[y, x] for x, y in pts if 0 <= x < gen.w and 0 <= y < gen.h]
        self.biome_pts = [(x, y) for x, y in pts if 0 <= x < gen.w and 0 <= y < gen.h]
        self.dist = math.hypot(x2 - x1, y2 - y1)
        lay = QVBoxLayout(self)
        info = QLabel(f"From ({x1},{y1}) to ({x2},{y2}) — Distance: {self.dist:.0f} tiles — "
                      f"{len(self.elevations)} samples — Max: {max(self.elevations):.3f} — Min: {min(self.elevations):.3f}")
        info.setStyleSheet("color:#a6adc8;font-size:11px;padding:4px"); lay.addWidget(info)
        self.profile_w = QWidget(); self.profile_w.setMinimumHeight(180)
        lay.addWidget(self.profile_w); btn = QPushButton("Close")
        btn.clicked.connect(self.accept); lay.addWidget(btn)

    def paintEvent(self, e):
        if not self.elevations: return
        p = QPainter(self.profile_w); w = self.profile_w.width(); h = self.profile_w.height()
        p.fillRect(0, 0, w, h, QColor(24, 24, 37))
        margin = 40; pw = w - margin * 2; ph = h - margin * 2
        # Grid
        p.setPen(QPen(QColor(69, 71, 90), 1, Qt.DotLine))
        for i in range(5):
            y = margin + int(i * ph / 4)
            p.drawLine(margin, y, w - margin, y)
            p.setPen(QColor(120, 120, 140)); p.setFont(QFont("Segoe UI", 8))
            val = 1.0 - i * 0.25
            p.drawText(2, y + 4, f"{val:.2f}")
            p.setPen(QPen(QColor(69, 71, 90), 1, Qt.DotLine))
        # Profile fill
        n = len(self.elevations)
        poly = QPolygon()
        poly.append(QPoint(margin, margin + ph))
        for i, ev in enumerate(self.elevations):
            px = margin + int(i / max(n - 1, 1) * pw)
            py = margin + ph - int(ev * ph)
            poly.append(QPoint(px, py))
        poly.append(QPoint(margin + pw, margin + ph))
        p.setPen(Qt.NoPen); p.setBrush(QColor(89, 182, 250, 60)); p.drawPolygon(poly)
        # Profile line
        p.setPen(QPen(QColor(89, 182, 250), 2))
        for i in range(n - 1):
            px1 = margin + int(i / max(n - 1, 1) * pw)
            py1 = margin + ph - int(self.elevations[i] * ph)
            px2 = margin + int((i + 1) / max(n - 1, 1) * pw)
            py2 = margin + ph - int(self.elevations[i + 1] * ph)
            p.drawLine(px1, py1, px2, py2)
        # Biome color dots
        for i, (bx, by) in enumerate(self.biome_pts[:n]):
            px = margin + int(i / max(n - 1, 1) * pw)
            py = margin + ph - int(self.elevations[i] * ph)
            if i % max(1, n // 30) == 0:
                r2, g2, b2 = BIOME_RGB.get(self.gen.biomes[by, bx], (128, 128, 128))
                p.setPen(Qt.NoPen); p.setBrush(QColor(r2, g2, b2)); p.drawEllipse(px - 2, py - 2, 4, 4)
        # Water line
        wy = margin + ph - int(0.32 * ph)
        p.setPen(QPen(QColor(50, 102, 184, 120), 1, Qt.DashLine))
        p.drawLine(margin, wy, w - margin, wy)
        p.setPen(QColor(80, 130, 210)); p.setFont(QFont("Segoe UI", 7))
        p.drawText(w - margin + 3, wy + 4, "Water")
        # Axes
        p.setPen(QPen(QColor(150, 150, 170), 1))
        p.drawLine(margin, margin, margin, margin + ph)
        p.drawLine(margin, margin + ph, w - margin, margin + ph)
        p.end()


class StatBars(QWidget):
    def __init__(self): super().__init__(); self.data = []; self.setFixedHeight(10)

    def set_data(self, gen):
        counts = np.bincount(gen.biomes.ravel(), minlength=BIOME_CT); total = gen.w * gen.h
        self.data = [(i, counts[i] / total) for i in range(BIOME_CT) if counts[i] > 0 and counts[i] / total > 0.003]
        self.setFixedHeight(max(10, len(self.data) * 17 + 4)); self.update()

    def paintEvent(self, e):
        p = QPainter(self); bh = 13; y = 0
        for bid, pct in sorted(self.data, key=lambda x: -x[1]):
            r2, g2, b2 = BIOME_RGB[bid]
            p.setPen(QColor(180, 180, 200)); p.setFont(QFont("Segoe UI", 8))
            p.drawText(0, y + bh - 3, BIOME_NAME[bid][:11])
            bx = 72; bw = self.width() - bx - 42
            p.setPen(Qt.NoPen); p.setBrush(QColor(40, 40, 55)); p.drawRoundedRect(bx, y, bw, bh - 2, 3, 3)
            fw = int(bw * min(pct * 3.5, 1.0)); p.setBrush(QColor(r2, g2, b2))
            p.drawRoundedRect(bx, y, fw, bh - 2, 3, 3)
            p.setPen(QColor(160, 160, 180)); p.drawText(bx + bw + 3, y + bh - 3, f"{pct * 100:.1f}%")
            y += bh + 3
        p.end()


class BiomeLegBtn(QPushButton):
    clicked_biome = Signal(int)

    def __init__(self, bid, parent=None):
        super().__init__(parent); self.bid = bid
        r2, g2, b2 = BIOME_RGB[bid]
        self.setText(f"  {BIOME_EMOJI.get(bid, '')} {BIOME_NAME[bid]}")
        self.setCheckable(True); self.setFixedHeight(22)
        self.setStyleSheet(
            f"QPushButton{{text-align:left;padding:1px 6px;border:1px solid transparent;"
            f"border-radius:3px;background:transparent;color:#cdd6f4;font-size:11px}}"
            f"QPushButton:hover{{background:#313244}}"
            f"QPushButton:checked{{background:rgba({r2},{g2},{b2},70);"
            f"border-color:rgba({r2},{g2},{b2},160);color:#fff}}")
        self.clicked.connect(lambda: self.clicked_biome.emit(self.bid))


class AnnotationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Add Annotation")
        self.setFixedSize(280, 140); lay = QFormLayout(self)
        self.text_edit = QLineEdit(); self.text_edit.setPlaceholderText("Label text")
        lay.addRow("Text:", self.text_edit)
        self.color_combo = QComboBox()
        self.color_combo.addItems(["White", "Red", "Yellow", "Cyan", "Green", "Magenta"])
        lay.addRow("Color:", self.color_combo)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject); lay.addRow(btns)

    def get_result(self):
        cols = {"White": "#ffffff", "Red": "#ff5555", "Yellow": "#f9e2af",
                "Cyan": "#74c7ec", "Green": "#a6e3a1", "Magenta": "#cba6f7"}
        return cols.get(self.color_combo.currentText(), "#ffffff"), self.text_edit.text()


class ControlPanel(QScrollArea):
    generate_requested = Signal(dict); layer_changed = Signal(); save_requested = Signal(str)

    def __init__(self):
        super().__init__(); self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.setFixedWidth(275)
        c = QWidget(); lay = QVBoxLayout(c); lay.setSpacing(4); lay.setContentsMargins(6, 6, 6, 6)
        t = QLabel("⛰  World Generator"); t.setFont(QFont("Segoe UI", 13, QFont.Bold))
        t.setAlignment(Qt.AlignCenter); t.setStyleSheet("color:#cba6f7;padding:2px 0"); lay.addWidget(t)

        pg = QGroupBox("Parameters"); pl = QVBoxLayout(pg)
        sl2 = QHBoxLayout(); sl2.addWidget(QLabel("Seed:"))
        self.seed_spin = QSpinBox(); self.seed_spin.setRange(0, 999999); self.seed_spin.setValue(42)
        sl2.addWidget(self.seed_spin)
        rb = QPushButton("🎲"); rb.setFixedSize(28, 28); rb.setToolTip("Random seed (R)")
        rb.clicked.connect(lambda: self.seed_spin.setValue(random.randint(0, 999999))); sl2.addWidget(rb)
        hl2 = QHBoxLayout()
        self.back_btn = QPushButton("◀"); self.back_btn.setObjectName("histBtn")
        self.back_btn.setEnabled(False); self.back_btn.setToolTip("Previous seed (Ctrl+Z)")
        self.fwd_btn = QPushButton("▶"); self.fwd_btn.setObjectName("histBtn")
        self.fwd_btn.setEnabled(False); self.fwd_btn.setToolTip("Next seed (Ctrl+Y)")
        hl2.addWidget(self.back_btn); hl2.addWidget(self.fwd_btn)
        pl.addLayout(sl2); pl.addLayout(hl2)
        szl = QHBoxLayout(); szl.addWidget(QLabel("Size:")); self.size_combo = QComboBox()
        self.size_combo.addItems(["128×128", "256×256", "384×384", "512×512", "640×640"])
        self.size_combo.setCurrentIndex(1); szl.addWidget(self.size_combo); pl.addLayout(szl)
        prl = QHBoxLayout(); prl.addWidget(QLabel("Preset:")); self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Island", "Continent", "Archipelago", "Mountains"])
        prl.addWidget(self.preset_combo); pl.addLayout(prl)
        self.scale_sl, self.scale_lb = self._sl(pl, "Scale", 3, 30, 10)
        self.oct_sl, self.oct_lb = self._sl(pl, "Octaves", 1, 8, 6)
        self.per_sl, self.per_lb = self._sl(pl, "Persist.", 10, 80, 50)
        self.cb_erosion = QCheckBox("Hydraulic Erosion"); self.cb_erosion.setChecked(True); pl.addWidget(self.cb_erosion)
        lay.addWidget(pg)

        lg = QGroupBox("Terrain"); ll = QVBoxLayout(lg)
        self.cb_biomes = QCheckBox("🌿 Biome Blend"); self.cb_biomes.setChecked(True)
        self.cb_hmap = QCheckBox("🏔  Height Map")
        self.cb_contours = QCheckBox("〰  Contours"); self.cb_grid = QCheckBox("📐 Grid")
        self.cb_coast = QCheckBox("🟡 Coastline Highlight")
        for cb in [self.cb_biomes, self.cb_hmap, self.cb_contours, self.cb_grid, self.cb_coast]:
            cb.toggled.connect(self._ltog); ll.addWidget(cb)
        lay.addWidget(lg)

        fg = QGroupBox("Features"); fl = QVBoxLayout(fg)
        self.cb_rivers = QCheckBox("🌊 Rivers"); self.cb_rivers.setChecked(True)
        self.cb_forests = QCheckBox("🌲 Forests"); self.cb_forests.setChecked(True)
        self.cb_villages = QCheckBox("🏘 Villages"); self.cb_villages.setChecked(True)
        self.cb_roads = QCheckBox("🛤  Roads"); self.cb_roads.setChecked(True)
        self.cb_resources = QCheckBox("💎 Resources")
        self.cb_regions = QCheckBox("🗺  Regions")
        for cb in [self.cb_rivers, self.cb_forests, self.cb_villages, self.cb_roads, self.cb_resources, self.cb_regions]:
            cb.toggled.connect(self._ltog); fl.addWidget(cb)
        lay.addWidget(fg)

        og = QGroupBox("Overlays"); ol = QVBoxLayout(og)
        self.cb_temp = QCheckBox("🌡  Temperature"); self.cb_clouds = QCheckBox("☁  Clouds")
        self.cb_compass = QCheckBox("🧭 Compass"); self.cb_compass.setChecked(True)
        self.cb_climate = QCheckBox("🌐 Climate Zones")
        for cb in [self.cb_temp, self.cb_clouds, self.cb_compass, self.cb_climate]:
            cb.toggled.connect(self._ltog); ol.addWidget(cb)
        slay = QHBoxLayout(); slay.addWidget(QLabel("Season:"))
        self.season_btn = QPushButton("☀ Summer"); self.season_btn.setFixedHeight(24)
        self.season_btn.clicked.connect(self._toggle_season); slay.addWidget(self.season_btn)
        nlay = QHBoxLayout(); nlay.addWidget(QLabel("Night:"))
        self.night_sl, self.night_lb = self._sl(ol, "", 0, 100, 0, suffix="%")
        ol.addLayout(nlay)
        ol.addLayout(slay); lay.addWidget(og)

        vg = QGroupBox("View"); vl2 = QHBoxLayout(vg)
        self.gen_btn = QPushButton("✦ Generate"); self.gen_btn.setObjectName("genBtn")
        self.gen_btn.setToolTip("Generate (Space)"); self.gen_btn.clicked.connect(self._ogen); vl2.addWidget(self.gen_btn)
        self.iso_btn = QPushButton("🔷 3D"); self.iso_btn.setObjectName("isoBtn")
        self.iso_btn.clicked.connect(self._oiso); vl2.addWidget(self.iso_btn)
        lay.addWidget(vg)
        bl2 = QHBoxLayout()
        fb = QPushButton("⊞ Fit"); fb.setObjectName("fitBtn"); fb.setToolTip("Zoom to fit (F)")
        fb.clicked.connect(lambda: self.parent().parent().map_widget.zoom_to_fit()); bl2.addWidget(fb)
        self.prof_btn = QPushButton("📏 Profile"); self.prof_btn.setObjectName("profBtn")
        self.prof_btn.setCheckable(True); self.prof_btn.setToolTip("Shift+Drag for elevation profile")
        bl2.addWidget(self.prof_btn)
        self.ann_btn = QPushButton("📌 Annotate"); self.ann_btn.setObjectName("profBtn")
        self.ann_btn.setToolTip("Click map to place annotation"); self.ann_btn.clicked.connect(self._start_annotate)
        bl2.addWidget(self.ann_btn)
        self.save_btn = QToolButton(); self.save_btn.setText("💾 Save"); self.save_btn.setEnabled(False)
        self.save_btn.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(self.save_btn)
        menu.addAction("Colored Map (PNG)", lambda: self.save_requested.emit("color"))
        menu.addAction("Heightmap Grayscale", lambda: self.save_requested.emit("height"))
        menu.addAction("Moisture Map", lambda: self.save_requested.emit("moisture"))
        menu.addAction("Temperature Map", lambda: self.save_requested.emit("temperature"))
        menu.addSeparator()
        menu.addAction("World Data (JSON)", lambda: self.save_requested.emit("json"))
        self.save_btn.setMenu(menu); bl2.addWidget(self.save_btn); lay.addLayout(bl2)
        self.progress = QProgressBar(); self.progress.setRange(0, 100); self.progress.setValue(0)
        self.progress.setTextVisible(False); self.progress.setFixedHeight(6); lay.addWidget(self.progress)
        self.status_lbl = QLabel("Ready"); self.status_lbl.setStyleSheet("color:#a6adc8;font-size:10px")
        self.status_lbl.setWordWrap(True); lay.addWidget(self.status_lbl)

        sg = QGroupBox("Statistics"); sl3 = QVBoxLayout(sg)
        self.stat_bars = StatBars(); sl3.addWidget(self.stat_bars)
        self.extra_stats = QLabel(""); self.extra_stats.setStyleSheet("color:#a6adc8;font-size:10px")
        self.extra_stats.setWordWrap(True); sl3.addWidget(self.extra_stats); lay.addWidget(sg)

        leg = QGroupBox("Biome Legend"); ll2 = QVBoxLayout(leg)
        self.leg_btns = []; self._hl_biome = -1
        for bid in [DEEP_WATER, SHALLOW_WATER, BEACH, DESERT, GRASSLAND, FOREST,
                     SWAMP, TAIGA, TUNDRA, MOUNTAIN, SNOW]:
            btn = BiomeLegBtn(bid); btn.clicked_biome.connect(self._hl_toggle); ll2.addWidget(btn)
            self.leg_btns.append(btn)
        lay.addWidget(leg)
        hl3 = QLabel("Space:Gen R:Rand F:Fit G:Grid 1-5:Layers Shift+Drag:Profile")
        hl3.setWordWrap(True); hl3.setStyleSheet("color:#6c7086;font-size:9px;padding:2px 0"); lay.addWidget(hl3)
        lay.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setWidget(c)
        self._iso = False; self._winter = False; self._history = []; self._hist_idx = -1
        self._annotate_mode = False; self._annotations = []

    def _sl(self, layout, name, lo, hi, val, suffix=""):
        hl = QHBoxLayout()
        if name: hl.addWidget(QLabel(name + ":"))
        lb = QLabel(str(val) + suffix); lb.setFixedWidth(32); hl.addWidget(lb); layout.addLayout(hl)
        s = QSlider(Qt.Horizontal); s.setRange(lo, hi); s.setValue(val)
        s.valueChanged.connect(lambda v, l=lb, n=name, sf=suffix: self._scb(l, n, v, sf))
        layout.addWidget(s); return s, lb

    def _scb(self, lb, n, v, sf=""):
        if n == "Scale": lb.setText(f"{v / 1000:.3f}")
        elif n == "Persist.": lb.setText(f"{v / 100:.2f}")
        else: lb.setText(str(v) + sf)

    def _ltog(self):
        if self.cb_hmap.isChecked():
            for cb in [self.cb_biomes, self.cb_rivers, self.cb_forests, self.cb_villages,
                        self.cb_roads, self.cb_temp, self.cb_resources, self.cb_coast, self.cb_regions,
                        self.cb_climate]:
                cb.setChecked(False); cb.setEnabled(False)
        else:
            for cb in [self.cb_biomes, self.cb_rivers, self.cb_forests, self.cb_villages,
                        self.cb_roads, self.cb_temp, self.cb_resources, self.cb_coast, self.cb_regions,
                        self.cb_climate]:
                cb.setEnabled(True)
        self.layer_changed.emit()

    def _hl_toggle(self, bid):
        if self._hl_biome == bid:
            self._hl_biome = -1
            for b in self.leg_btns: b.setChecked(False)
        else:
            self._hl_biome = bid
            for b in self.leg_btns: b.setChecked(b.bid == bid)
        self.layer_changed.emit()

    def _toggle_season(self):
        self._winter = not self._winter
        self.season_btn.setText("❄ Winter" if self._winter else "☀ Summer")
        self.layer_changed.emit()

    def _start_annotate(self):
        self._annotate_mode = True
        self.ann_btn.setText("📌 Click map...")
        self.status_lbl.setText("Click on the map to place an annotation")

    def add_annotation_at(self, mx, my):
        if not self._annotate_mode: return False
        dlg = AnnotationDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            col, text = dlg.get_result()
            if text: self._annotations.append((mx, my, text, col))
        self._annotate_mode = False; self.ann_btn.setText("📌 Annotate")
        self.layer_changed.emit(); return True

    def _ogen(self):
        sz = int(self.size_combo.currentText().split("×")[0].strip())
        params = {"w": sz, "h": sz, "seed": self.seed_spin.value(),
                  "scale": self.scale_sl.value() / 1000, "octaves": self.oct_sl.value(),
                  "persistence": self.per_sl.value() / 100,
                  "preset": self.preset_combo.currentText().lower(), "erosion": self.cb_erosion.isChecked()}
        if self._hist_idx < len(self._history) - 1: self._history = self._history[:self._hist_idx + 1]
        self._history.append(params); self._hist_idx = len(self._history) - 1
        self._update_hist_btns(); self._annotations = []
        self.generate_requested.emit(params)

    def _oiso(self):
        self._iso = not self._iso
        self.iso_btn.setText("🔷 3D" if not self._iso else "🗺 2D"); self.layer_changed.emit()

    def go_back(self):
        if self._hist_idx > 0:
            self._hist_idx -= 1; self._update_hist_btns(); self._apply_hist()

    def go_forward(self):
        if self._hist_idx < len(self._history) - 1:
            self._hist_idx += 1; self._update_hist_btns(); self._apply_hist()

    def _apply_hist(self):
        p = self._history[self._hist_idx].copy(); self.seed_spin.setValue(p["seed"])
        self.size_combo.setCurrentText(f"{p['w']}×{p['h']}")
        self.scale_sl.setValue(int(p["scale"] * 1000)); self.oct_sl.setValue(p["octaves"])
        self.per_sl.setValue(int(p["persistence"] * 100))
        self.preset_combo.setCurrentText(p["preset"].title())
        self.cb_erosion.setChecked(p["erosion"]); self._annotations = []
        self.generate_requested.emit(p)

    def _update_hist_btns(self):
        self.back_btn.setEnabled(self._hist_idx > 0)
        self.fwd_btn.setEnabled(self._hist_idx < len(self._history) - 1)

    def get_layers(self):
        return (self.cb_biomes.isChecked(), self.cb_rivers.isChecked(), self.cb_forests.isChecked(),
                self.cb_villages.isChecked(), self.cb_roads.isChecked(), self.cb_hmap.isChecked(),
                self.cb_grid.isChecked(), self.cb_contours.isChecked(), self.cb_temp.isChecked(),
                self.cb_clouds.isChecked(), self.cb_compass.isChecked(), self.cb_resources.isChecked(),
                self._winter, self._hl_biome, self.night_sl.value() / 100.0, 0.0,
                self.cb_climate.isChecked(), self.cb_coast.isChecked(), self.cb_regions.isChecked(),
                False, self._annotations if self._annotations else None)

    def set_generating(self, on):
        self.gen_btn.setEnabled(not on)
        for w in [self.seed_spin, self.size_combo, self.scale_sl, self.oct_sl,
                   self.per_sl, self.preset_combo, self.cb_erosion]:
            w.setEnabled(not on)

    def set_progress(self, msg, val): self.progress.setValue(val); self.status_lbl.setText(msg)

    def update_stats(self, gen):
        self.stat_bars.set_data(gen)
        nv = len(gen.villages); nr = len(gen.roads)
        nriv = int(gen.rivers.sum()) if gen.rivers is not None else 0
        nlk = int(gen.lakes.sum()) if gen.lakes is not None else 0
        ntr = int(gen.trees.sum()) if gen.trees is not None else 0
        ng = sum(1 for *_, t in gen.resources if t == 'gold')
        ni = sum(1 for *_, t in gen.resources if t == 'iron')
        nm = sum(1 for *_, t in gen.resources if t == 'gem')
        cities = sum(1 for *_, vt in gen.villages if vt == "City")
        self.extra_stats.setText(
            f"🏘 {nv} villages ({cities} cities)  │  🛤 {nr} roads\n"
            f"🌊 {nriv} river  │  🏞 {nlk} lake  │  🌲 {ntr} trees\n"
            f"💎 Gold:{ng} Iron:{ni} Gems:{nm}  │  🗺 {len(gen.region_names)} regions")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Procedural World Generation v3")
        self.resize(1300, 820); self.gen = None; self.current_img = None
        self.thread = None; self.worker = None
        central = QWidget(); self.setCentralWidget(central)
        ml = QHBoxLayout(central); ml.setContentsMargins(4, 4, 4, 4); ml.setSpacing(4)
        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(0, 0, 0, 0); ll.setSpacing(4)
        self.map_widget = MapWidget(); ll.addWidget(self.map_widget, 1)
        mb = QHBoxLayout(); self.minimap = MiniMap(); mb.addWidget(self.minimap)
        mb.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)); ll.addLayout(mb)
        self.ctrl = ControlPanel(); ml.addWidget(left, 1); ml.addWidget(self.ctrl, 0)
        self.sb = self.statusBar()
        self.sb.showMessage("  Adjust parameters and press Space or click Generate.")
        self.ctrl.generate_requested.connect(self.start_gen)
        self.ctrl.layer_changed.connect(self.re_render)
        self.ctrl.save_requested.connect(self.save_map)
        self.ctrl.back_btn.clicked.connect(self.ctrl.go_back)
        self.ctrl.fwd_btn.clicked.connect(self.ctrl.go_forward)
        self.map_widget.hover_info.connect(self.sb.showMessage)
        self.map_widget.viewport_changed.connect(self.minimap.set_viewport)
        self.map_widget.profile_requested.connect(self.show_profile)
        self.minimap.nav_requested.connect(self.map_widget.navigate_to)
        # Water animation timer
        self._anim_t = 0.0
        self._anim_timer = QTimer(); self._anim_timer.timeout.connect(self._anim_tick)
        self._anim_timer.start(80)
        QTimer.singleShot(100, self.ctrl._ogen)

    def _anim_tick(self):
        if self.ctrl.cb_rivers.isChecked() and not self.ctrl.cb_hmap.isChecked():
            self._anim_t += 1.0; self.re_render()

    def start_gen(self, params):
        if self.thread and self.thread.isRunning(): return
        self.thread = QThread(); self.worker = GenWorker(); self.worker.moveToThread(self.thread)
        self.thread.started.connect(lambda: self.worker.run(params))
        self.worker.progress.connect(self.ctrl.set_progress)
        self.worker.done.connect(self.on_done); self.worker.error.connect(self.on_err)
        self.thread.finished.connect(self.thread.deleteLater)
        self.ctrl.set_generating(True); self.thread.start()

    def on_done(self, gen):
        self.gen = gen; self.ctrl.set_generating(False); self.ctrl.save_btn.setEnabled(True)
        self.minimap.set_gen(gen)
        self.re_render(); self.ctrl.update_stats(gen)
        nv = len(gen.villages); nr = len(gen.roads)
        self.sb.showMessage(
            f"  ✅ {gen.preset.title()} generated!  │  {gen.w}×{gen.h}  │  "
            f"Villages:{nv}  Roads:{nr}  │  Scroll=Zoom  Drag=Pan  Shift+Drag=Profile")

    def on_err(self, msg): self.ctrl.set_generating(False); self.ctrl.set_progress(f"Error: {msg}", 0)

    def re_render(self):
        if not self.gen: return
        layers = list(self.ctrl.get_layers())
        layers[15] = self._anim_t  # anim_t
        if self.ctrl._iso: self.current_img = render_isometric(self.gen)
        else: self.current_img = render_world(self.gen, *layers)
        self.minimap.set_image(self.current_img)
        self.map_widget.set_world(self.gen, self.current_img)
        self.map_widget.viewport_changed.emit(self.map_widget.visible_rect())

    def save_map(self, mode):
        if not self.gen: return
        if mode == "json":
            path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "world.json", "JSON (*.json)")
            if path:
                with open(path, 'w') as f: json.dump(self.gen.to_dict(), f, indent=2)
                self.sb.showMessage(f"  💾 Saved JSON to {path}"); return
        defs = {"color": "world.png", "height": "heightmap.png",
                "moisture": "moisture.png", "temperature": "temperature.png"}
        path, _ = QFileDialog.getSaveFileName(self, "Save", defs.get(mode, "map.png"), "PNG (*.png)")
        if not path: return
        w, h = self.gen.w, self.gen.h
        if mode == "color":
            if self.current_img: self.current_img.save(path)
        else:
            data = {"height": self.gen.heightmap, "moisture": self.gen.moisture,
                    "temperature": self.gen.temperature}[mode]
            g = (data * 255).astype(np.uint8)
            buf = np.stack([g, g, g, np.full((h, w), 255, dtype=np.uint8)], axis=-1)
            _qi(buf.astype(np.uint8)).save(path)
        self.sb.showMessage(f"  💾 Saved to {path}")

    def show_profile(self, x1, y1, x2, y2):
        if self.gen:
            dlg = ProfileDialog(self.gen, x1, y1, x2, y2, self)
            dlg.exec()

    def keyPressEvent(self, e):
        k = e.key()
        if k == Qt.Key_Space and not (self.thread and self.thread.isRunning()): self.ctrl._ogen()
        elif k == Qt.Key_R: self.ctrl.seed_spin.setValue(random.randint(0, 999999))
        elif k == Qt.Key_F: self.map_widget.zoom_to_fit()
        elif k == Qt.Key_G: self.ctrl.cb_grid.setChecked(not self.ctrl.cb_grid.isChecked())
        elif k == Qt.Key_1: self.ctrl.cb_rivers.setChecked(not self.ctrl.cb_rivers.isChecked())
        elif k == Qt.Key_2: self.ctrl.cb_forests.setChecked(not self.ctrl.cb_forests.isChecked())
        elif k == Qt.Key_3: self.ctrl.cb_villages.setChecked(not self.ctrl.cb_villages.isChecked())
        elif k == Qt.Key_4: self.ctrl.cb_roads.setChecked(not self.ctrl.cb_roads.isChecked())
        elif k == Qt.Key_5: self.ctrl.cb_resources.setChecked(not self.ctrl.cb_resources.isChecked())
        elif k == Qt.Key_S and e.modifiers() & Qt.ControlModifier:
            if self.current_img: self.ctrl.save_btn.showMenu()
        elif k == Qt.Key_Z and e.modifiers() & Qt.ControlModifier: self.ctrl.go_back()
        elif k == Qt.Key_Y and e.modifiers() & Qt.ControlModifier: self.ctrl.go_forward()
        else: super().keyPressEvent(e)

    def mousePressEvent(self, e):
        if self.ctrl._annotate_mode and e.button() == Qt.LeftButton:
            mp = self.map_widget._to_map(e.pos())
            if mp and self.ctrl.add_annotation_at(*mp): return
        super().mousePressEvent(e)


if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyleSheet(DARK_CSS)
    win = MainWindow(); win.show(); sys.exit(app.exec())