"""Peças da caatinga de dia (fase 1) no nível do Metal Slug.

Estudo: MSX Missão 3 (floresta de outono e a estação com a locomotiva) e Missão 1
(casas de adobe, rochedo em camadas e areia), MS2 Missão 3 (troncos torcidos). O que
eles fazem e daqui segue:
- árvore com tronco torcido de veio em espiral, galhos que afinam, copa feita de muitos
  tufos de folha, cada tufo com luz própria em cima à esquerda e os de trás mais escuros;
- pedra com relevo de verdade (campo de altura -> luz), facetas, rachaduras, líquen;
- casa de taipa com reboco caindo e a trama de varas aparecendo, telha canal uma a uma,
  beiral fazendo sombra, barra suja de chão, porta de tábuas, janela de taramela;
- chão com a beirada iluminada, tufos, pedrinhas e o corte em camadas embaixo.
Mesmas ferramentas de base_detalhe.py (pintar, cilindro, corda, letreiro), com rampas de dia.
"""
import math

import numpy as np
from scipy import ndimage

from motor import IDX, VAZIO, Tela
from fase2 import ruido
import base_detalhe as bd
from base_detalhe import pintar, cilindro, corda

MAD = ["marrom_noite", "couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz", "couro_claro"]
CASCA = ["sombra", "couro_profundo", "terra_escura", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]
FOLHA = ["sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru", "mandacaru_luz"]
FOLHA_SECA = ["couro_profundo", "terra_escura", "terra", "terra_media", "barro", "areia_media"]
TERRA = ["marrom_noite", "terra_escura", "terra", "terra_media", "barro", "areia_media", "areia", "areia_luz"]
TAIPA = ["terra_escura", "terra", "terra_media", "barro", "areia_media", "areia", "areia_luz"]
CAL = ["cinza_medio", "cinza", "cinza_luz", "cinza_claro", "areia_clara", "branco"]
TELHA = ["marrom_noite", "vermelho_esc", "vermelho_medio", "laranja_escuro", "laranja_fogo", "couro_luz"]
PEDRA = ["sombra", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "cinza_claro"]
PEDRA_Q = ["sombra", "terra_escura", "terra", "terra_media", "barro", "areia_media", "areia_luz"]
CACTO = ["sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru", "mandacaru_luz"]
CORDA = ["terra_escura", "terra_media", "areia", "areia_luz"]
FERRO = ["preto", "sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]


def contornar(t, cor="sombra"):
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX[cor]


# ------------------------------------------------------------------ árvore
def tufo(t, cx, cy, r, rampa, semente=0, atras=False):
    """Tufo de folhas: borda recortada em folhinhas, luz em cima à esquerda, folhas
    miúdas marcadas por dentro (claras do lado da luz, escuras do outro)."""
    rng = np.random.default_rng(semente)
    m = t.elipse(cx, cy, r, r * 0.8)
    for k in range(int(r * 2.2)):
        a = rng.uniform(0, 2 * math.pi)
        m |= t.elipse(cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.72, r * 0.32, r * 0.26)
    d = ((t.xx - cx) * -0.6 + (t.yy - cy) * -0.8) / r
    v = 0.48 + d * 0.3 - (0.22 if atras else 0)
    folhas = ruido(t.h, t.w, 0.7, semente)
    v = v + folhas * 0.12
    pintar(t, m, v, rampa)
    # Folhinhas: pares claro/escuro em diagonal dentro do tufo.
    ys, xs = np.where(m)
    for _ in range(len(ys) // 14):
        i = rng.integers(0, len(ys))
        y, x = ys[i], xs[i]
        lado = ((x - cx) * -0.6 + (y - cy) * -0.8) / r
        if lado > 0.1 and not atras:
            t.ponto(x, y, rampa[-1])
            t.ponto(x + 1, y + 1, rampa[-3])
        elif lado < -0.3:
            t.ponto(x, y, rampa[1])
    return m


def galho(t, x, y, ang, comp, r, prof, semente, pontas, rampa=CASCA):
    """Galho recursivo torto: segmentos com o ângulo variando, bifurcando."""
    rng = np.random.default_rng(semente)
    n = 3
    for k in range(n):
        a = ang + rng.uniform(-0.25, 0.25)
        x1 = x + math.cos(a) * comp / n
        y1 = y - math.sin(a) * comp / n
        r1 = max(0.7, r * 0.94)
        cilindro(t, x, y, x1, y1, r, r1, rampa=rampa, semente=semente + k, rachas=1 if r > 1.6 else 0,
                 nos=1 if r > 2.2 and k == 1 else 0)
        x, y, r = x1, y1, r1
    if prof <= 0 or r < 0.75:
        pontas.append((x, y))
        return
    filhos = 2 if rng.random() < 0.6 else 3
    for j in range(filhos):
        da = (j - (filhos - 1) / 2) * rng.uniform(0.7, 1.1) + rng.uniform(-0.15, 0.15)
        # Os galhos abrem para os lados (copa larga e baixa da caatinga), sem descer.
        na = ang + da
        na = min(max(na, 0.25), math.pi - 0.25)
        galho(t, x, y, na, comp * rng.uniform(0.68, 0.86), max(0.75, r * 0.74), prof - 1, semente * 3 + j + 1, pontas,
              rampa)


def arvore(altura=120, semente=0, folhas=True, seca=0.25, largura=None):
    """Árvore da caatinga (umburana/juazeiro): tronco cinza torcido com raízes saindo
    do chão, galhos tortos e copa de tufos verdes misturados com tufos secos; seca=1
    deixa só os galhos (pau seco)."""
    W = largura or int(altura * 1.6)
    t = Tela(W, altura)
    rng = np.random.default_rng(semente)
    base = altura - 1
    cx = W / 2 + rng.uniform(-6, 6)
    pontas = []
    tmp = Tela(W, altura)
    # Raízes.
    for s_ in (-1, 1):
        cilindro(tmp, cx + s_ * 1.5, base - 6, cx + s_ * 9, base, 2.6, 1.2, rampa=CASCA, semente=semente + 20 + s_,
                 rachas=0, nos=0)
    r0 = altura / 30
    ang = math.pi / 2 + rng.uniform(-0.18, 0.18)
    galho(tmp, cx, base, ang, altura * 0.3, r0, 4, semente + 1, pontas)
    if folhas and seca < 1:
        # Tufos de trás (escuros) e da frente, em volta das pontas.
        lista = []
        for (px, py) in pontas:
            for _ in range(3):
                lista.append((px + rng.uniform(-7, 7), py + rng.uniform(-6, 4), rng.uniform(5, 9) * altura / 110))
        lista.sort(key=lambda e: e[1])
        for k, (px, py, r) in enumerate(lista):
            tufo(t, px, py + 3, r * 1.1, FOLHA if rng.random() > seca else FOLHA_SECA, semente + 100 + k, atras=True)
        t.colar(tmp, 0, 0)
        for k, (px, py, r) in enumerate(lista):
            if rng.random() < 0.7:
                tufo(t, px - 1, py - 1, r * 0.85, FOLHA if rng.random() > seca else FOLHA_SECA, semente + 300 + k)
    else:
        t.colar(tmp, 0, 0)
        # Pau seco: gravetos finos nas pontas.
        for (px, py) in pontas:
            for _ in range(2):
                a = rng.uniform(0.3, 2.8)
                L = rng.uniform(4, 9)
                t.linha(px, py, px + math.cos(a) * L, py - math.sin(a) * L, "cinza_escuro")
    contornar(t)
    return t


# ------------------------------------------------------------------ cactos
def mandacaru(altura=80, semente=0, bracos=3):
    """Mandacaru grande: colunas com gomos (arestas claras e vales escuros), espinhos em
    pontinhos, braços que saem de lado e sobem em curva, flor branca e fruto roxo."""
    W = int(altura * 0.9)
    t = Tela(W, altura)
    rng = np.random.default_rng(semente)
    base = altura - 1
    cx = W / 2

    def coluna(x0, y0, x1, y1, r):
        m = t.capsula(x0, y0, x1, y1, r)
        u = (t.xx - (x0 + (x1 - x0) * np.clip((y0 - t.yy) / max(1, y0 - y1), 0, 1))) / r
        gomo = np.cos(u * math.pi * 2.2) * 0.5 + 0.5
        v = 0.35 + (1 - np.abs(u + 0.3)) * 0.35 + gomo * 0.22
        pintar(t, m, v, CACTO)
        for _ in range(int(r * abs(y0 - y1) / 6)):
            yy = rng.uniform(min(y0, y1), max(y0, y1))
            xx = x0 + (x1 - x0) * (y0 - yy) / max(1, y0 - y1) + rng.choice([-1, 1]) * rng.uniform(0.2, 0.9) * r
            t.ponto(xx, yy, "areia_clara")
        t.chapado(t.elipse(x1, y1 - r * 0.2, r * 0.9, r * 0.5) & m, "mandacaru_luz")
        return m
    r = altura / 13
    # Braços (atrás) primeiro.
    for k in range(bracos):
        lado = -1 if k % 2 == 0 else 1
        yb = base - altura * rng.uniform(0.3, 0.55)
        xb = cx + lado * (r * 2.6 + k * 1.5)
        alto = yb - altura * rng.uniform(0.18, 0.32)
        m1 = t.capsula(cx, yb + r * 0.5, xb, yb, r * 0.8)
        pintar(t, m1, 0.55 - (t.yy - yb) / (r * 3), CACTO)
        coluna(xb, yb, xb + lado * 0.5, alto, r * 0.8)
        if rng.random() < 0.6:
            t.chapado(t.elipse(xb, alto - r * 0.9, 1.6, 1.4), "branco")
            t.ponto(xb, alto - r * 0.9, "amarelo_claro")
    coluna(cx, base, cx + rng.uniform(-1, 1), base - altura * 0.92, r)
    t.chapado(t.elipse(cx + 1, base - altura * 0.92 - r * 0.6, 1.6, 1.6), "vermelho_medio")
    t.ponto(cx + 0.5, base - altura * 0.92 - r * 0.9, "rosa_poeira")
    contornar(t)
    return t


def xiquexique(w=30, semente=0):
    """Touceira de xique-xique: braços deitados e levantando, gomos e espinhos."""
    h = int(w * 0.6)
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    chao = h - 1
    for k in range(int(rng.integers(5, 8))):
        x0 = rng.uniform(w * 0.2, w * 0.8)
        a = rng.uniform(0.3, 2.8)
        L = rng.uniform(h * 0.5, h * 0.95)
        x1, y1 = x0 + math.cos(a) * L * 0.8, chao - math.sin(a) * L
        m = t.capsula(x0, chao, x1, y1, 2.2)
        v = 0.5 + np.cos((t.xx + t.yy) * 1.4) * 0.12 - ((t.xx - x0) + (t.yy - chao)) / (L * 3)
        pintar(t, m, v + rng.uniform(-0.1, 0.1), CACTO)
        for j in range(int(L / 3)):
            f = j / max(1, L / 3)
            t.ponto(x0 + (x1 - x0) * f + rng.uniform(-2, 2), chao + (y1 - chao) * f, "areia_clara")
    contornar(t)
    return t


def capim(w=16, h=12, semente=0, seco=True):
    """Tufo de capim panasco: folhas finas em leque, as de trás escuras, pontas claras."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    chao = h - 1
    cores = (["terra", "barro", "areia_media", "areia_luz"] if seco else ["caatinga_esc", "caatinga", "mandacaru", "mandacaru_luz"])
    for k in range(int(w * 0.9)):
        x0 = w / 2 + rng.uniform(-w * 0.25, w * 0.25)
        a = math.pi / 2 + rng.uniform(-1.1, 1.1)
        L = rng.uniform(h * 0.5, h)
        c = rng.integers(0, len(cores) - 1)
        for j in range(int(L)):
            f = j / L
            x = x0 + math.cos(a) * j + math.cos(a) * f * f * 3
            y = chao - math.sin(a) * j
            t.ponto(x, y, cores[min(len(cores) - 1, c + (1 if f > 0.7 else 0))])
    return t


# ------------------------------------------------------------------ pedras
def pedra(w=40, h=26, semente=0, rampa=PEDRA, liquen=True, plana=False):
    """Matacão de granito com relevo: campo de altura em blocos (facetas), luz pela
    inclinação, rachaduras escuras com a borda clara, líquen laranja e verde, capim na base."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    cx, cy = w / 2, h * 0.62
    forma = ((t.xx - cx) / (w * 0.48)) ** 2 + ((t.yy - cy) / (h * 0.62)) ** 2 + ruido(h, w, 3, semente) * 0.18
    m = (forma < 1) & (t.yy < h)
    if plana:
        m &= t.yy > h * 0.15
    alt = np.sqrt(np.clip(1 - forma, 0, 1)) * h * 0.55
    # Facetas: degraus de altura em células irregulares.
    cel = ruido(h, w, (h / 6, w / 7), semente + 1)
    alt = alt + np.round(cel * 2) * 1.6
    gy, gx = np.gradient(ndimage.gaussian_filter(alt, 0.9))
    n = np.sqrt(gx * gx + gy * gy + 1)
    lum = (-gx * bd.LUZ[0] - gy * bd.LUZ[1] + bd.LUZ[2]) / n
    v = 0.05 + np.clip(lum, 0, 1) * 0.9 + ruido(h, w, 0.6, semente + 2) * 0.05
    pintar(t, m, v, rampa)
    # Rachaduras.
    for _ in range(max(1, w // 18)):
        x, y = rng.uniform(w * 0.25, w * 0.75), rng.uniform(h * 0.2, h * 0.5)
        a = rng.uniform(1.2, 2.0)
        for k in range(int(h * 0.6)):
            x += math.cos(a) + rng.uniform(-0.6, 0.6)
            y += 0.8
            if 0 <= int(y) < h and 0 <= int(x) < w and m[int(y), int(x)]:
                t.ponto(x, y, rampa[0])
                if 0 <= int(x) - 1:
                    t.ponto(x - 1, y, rampa[-2])
    if liquen:
        lq = m & (ruido(h, w, 1.4, semente + 5) > 1.9) & (t.yy < h * 0.7)
        t.px[lq] = IDX["laranja_escuro"]
        t.px[lq & (ruido(h, w, 0.6, semente + 6) > 0.6)] = IDX["ouro_escuro"]
        lv = m & (ruido(h, w, 1.2, semente + 7) > 2.0)
        t.px[lv] = IDX["mandacaru_luz"]
    contornar(t)
    return t


# ------------------------------------------------------------------ casa de taipa
def casa_taipa(w=150, h=104, semente=0, quebrada=True, alpendre=True):
    """Casa de taipa do sertão: parede de barro com reboco caindo e a trama de varas
    aparecendo, caiação gasta na frente, barra de terra embaixo, telhado de telha canal
    (cada telha com a luz em cima e a boca escura), cumeeira, beiral com sombra, porta
    de tábuas com taramela, janela com a folha aberta, alpendre em forquilhas com o pote,
    o pilão, a rede e as cabaças penduradas."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    chao = h - 1
    px0, px1 = 10, w - (40 if alpendre else 10)
    beiral = int(h * 0.36)
    cume = 4
    # --- parede
    parede = t.retangulo(px0, beiral, px1 - px0, chao - beiral + 1)
    v = 0.6 + ruido(h, w, (2, 5), semente) * 0.06 - (t.xx - px0) / (px1 - px0) * 0.12
    pintar(t, parede, v, CAL)
    # Reboco caído em manchas: aparece o barro e as varas da taipa.
    caido = parede & (ruido(h, w, (4, 6), semente + 1) > 0.75) & (t.yy > beiral + 6)
    pintar(t, caido, 0.45 + ruido(h, w, 0.7, semente + 2) * 0.1, TAIPA)
    varas = caido & ((t.xx.astype(int) % 5 == 0) | (t.yy.astype(int) % 7 == 0))
    t.px[varas] = IDX["couro_escuro"]
    borda_c = caido & ~ndimage.binary_erosion(caido)
    t.px[borda_c & (t.yy < t.yy[caido].mean() if caido.any() else borda_c)] = IDX["cinza_claro"]
    t.px[ndimage.binary_dilation(caido) & ~caido & parede & (np.roll(caido, -1, 0))] = IDX["cinza_medio"]
    # Barra de terra subindo do chão e respingos.
    barra = parede & (t.yy > chao - 10 + ruido(h, w, (1, 4), semente + 3) * 2)
    pintar(t, barra, 0.42 + ruido(h, w, 0.6, semente + 4) * 0.08, TAIPA)
    # Rachaduras.
    for _ in range(3):
        x, y = rng.uniform(px0 + 8, px1 - 8), beiral + rng.uniform(4, 12)
        for k in range(int(rng.integers(8, 20))):
            x += rng.uniform(-1, 1)
            y += 1
            t.ponto(x, y, "terra")
    # Sombra do beiral.
    t.px[parede & (t.yy < beiral + 6)] = np.where(t.px[parede & (t.yy < beiral + 6)] >= 0,
                                                    IDX["cinza_medio"], VAZIO)
    t.px[parede & (t.yy < beiral + 3)] = IDX["cinza_escuro"]
    # --- porta de tábuas
    pa = px0 + int((px1 - px0) * 0.58)
    pw, ph = 18, 34
    porta = t.retangulo(pa, chao - ph, pw, ph)
    for k, x in enumerate(range(pa, pa + pw, 4)):
        bd.tabua(t, x, chao - ph, 4, ph, semente=semente + 30 + k, rampa=MAD, vertical=True)
    t.chapado(t.retangulo(pa, chao - ph + 6, pw, 2), "couro_escuro")
    t.chapado(t.retangulo(pa, chao - 10, pw, 2), "couro_escuro")
    t.linha(pa, chao - ph + 7, pa + pw - 1, chao - 11, "couro_medio")
    t.ponto(pa + pw - 4, chao - 18, "cinza_luz")  # taramela
    t.linha(pa - 1, chao - ph - 1, pa + pw, chao - ph - 1, "couro_profundo")
    for y in range(chao - ph - 1, chao):
        t.ponto(pa - 1, y, "couro_profundo")
        t.ponto(pa + pw, y, "couro_profundo")
    # --- janela com a folha aberta
    ja = px0 + 12
    jw, jh = 16, 15
    jy = beiral + 12
    t.chapado(t.retangulo(ja, jy, jw, jh), "sombra")
    t.chapado(t.retangulo(ja + 2, jy + 2, jw - 4, jh - 4), "couro_profundo")
    t.chapado(t.retangulo(ja + 3, jy + jh - 6, 5, 4), "couro_escuro")  # vulto de pote no parapeito
    for k, x in enumerate(range(ja - 9, ja - 1, 4)):
        bd.tabua(t, x, jy - 1, 4, jh + 2, semente=semente + 50 + k, rampa=MAD, vertical=True)
    t.linha(ja - 1, jy + jh, ja + jw, jy + jh, "couro_medio")
    t.linha(ja - 1, jy + jh + 1, ja + jw, jy + jh + 1, "couro_escuro")
    # --- telhado de telha canal
    tel = t.poligono([(px0 - 6, beiral + 1), (px0 + 6, cume), (px1 - 6, cume), (px1 + 6, beiral + 1)])
    if quebrada:
        tel &= ~t.elipse(px0 + (px1 - px0) * 0.72, cume + 8, 9, 5)
    linhas_t = np.arange(cume, beiral + 2, 4)
    v = np.full(t.px.shape, 0.5)
    for k, y0 in enumerate(linhas_t):
        f = (t.yy - y0) / 4
        fila = (f >= 0) & (f < 1)
        desloc = (k % 2) * 3
        u = ((t.xx + desloc) % 6) / 6
        tom = 0.75 - np.abs(u - 0.4) * 0.9 - f * 0.25
        v = np.where(fila, tom, v)
    v = v - (t.yy - cume) / (beiral - cume) * 0.1 + ruido(h, w, (1, 3), semente + 8) * 0.05
    pintar(t, tel, v, TELHA)
    # Telhas mais escuras/claras soltas e lodo.
    for _ in range(14):
        x, y = rng.uniform(px0, px1), rng.uniform(cume + 2, beiral - 2)
        e = t.elipse(x, y, 2.5, 1.2) & tel
        pintar(t, e, 0.35 + rng.uniform(-0.15, 0.25), TELHA)
    lodo = tel & (ruido(h, w, (1, 4), semente + 9) > 1.2)
    t.px[lodo] = IDX["caatinga_media"]
    # Cumeeira e as bocas das telhas no beiral.
    cume_m = t.retangulo(px0 + 4, cume - 2, px1 - px0 - 8, 3)
    pintar(t, cume_m, 0.7 - (t.yy - cume + 2) / 6, TELHA)
    for x in range(px0 - 5, px1 + 6, 6):
        t.chapado(t.elipse(x + 2, beiral + 1.5, 2.4, 1.6), "marrom_noite")
        t.ponto(x + 1, beiral + 0.5, "laranja_fogo")
    if quebrada:
        # Buraco no telhado mostrando os caibros.
        bx_, by_ = px0 + (px1 - px0) * 0.72, cume + 8
        for k in range(-8, 9, 4):
            cilindro(t, bx_ + k, by_ - 4, bx_ + k + 1, by_ + 5, 0.9, 0.9, rampa=MAD, semente=k + 90, rachas=0, nos=0)
    # --- alpendre
    if alpendre:
        ax0, ax1 = px1, w - 4
        for k, x in enumerate((ax0 + 6, ax1 - 3)):
            cilindro(t, x, chao, x + rng.uniform(-0.6, 0.6), beiral + 8, 1.9, 1.6, rampa=MAD, semente=semente + 70 + k,
                     rachas=2, nos=1)
            t.chapado(t.elipse(x, beiral + 7, 3, 1.2), "couro_escuro")  # forquilha
        cilindro(t, ax0 - 2, beiral + 6, ax1 + 2, beiral + 7, 1.6, 1.6, rampa=MAD, semente=semente + 80, rachas=1,
                 nos=0)
        tel2 = t.poligono([(ax0 - 4, beiral - 4), (ax1 + 4, beiral + 4), (ax1 + 4, beiral + 7), (ax0 - 4, beiral + 2)])
        v2 = 0.6 + ((t.xx % 6) < 3) * 0.12 - (t.yy - beiral) / 30
        pintar(t, tel2, v2, TELHA)
        # Sombra do alpendre no chão de terra batida e na parede.
        # Pote de barro, pilão e rede.
        pote = t.elipse(ax0 + 14, chao - 6, 5.5, 6)
        pintar(t, pote, 0.75 - ((t.xx - (ax0 + 9)) + (t.yy - (chao - 12))) / 14, TELHA)
        t.chapado(t.retangulo(ax0 + 11.5, chao - 13, 5, 2), "couro")
        t.ponto(ax0 + 12, chao - 9, "couro_luz")
        pil = t.retangulo(ax0 + 23, chao - 11, 6, 11)
        pintar(t, pil, 0.7 - (t.xx - (ax0 + 23)) / 8, MAD)
        cilindro(t, ax0 + 26, chao - 11, ax0 + 30, chao - 26, 0.9, 0.9, rampa=MAD, semente=3, rachas=0, nos=0)
        pts = corda(t, ax0 + 6, beiral + 14, ax1 - 3, beiral + 14, 9, rampa=CORDA)
        for k, (x, y) in enumerate(pts[3:-3]):
            if k % 2 == 0:
                t.ponto(x, y + 1, "vermelho_medio")
                t.ponto(x, y + 2, "amarelo_fogo" if k % 4 == 0 else "vermelho")
        for k, x in enumerate((ax0 + 12, ax0 + 18)):
            t.linha(x, beiral + 8, x, beiral + 12, "terra_escura")
            cab = t.elipse(x, beiral + 15, 2.4, 3)
            pintar(t, cab, 0.8 - (t.xx - x + 2) / 6, ["terra", "barro", "areia_media", "areia", "areia_luz"])
    contornar(t)
    return t


# ------------------------------------------------------------------ cerca e curral
def cerca_varas(w=120, h=34, semente=0):
    """Cerca de varas tortas amarradas em três travessas, com mourões mais grossos."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    chao = h - 1
    for x in range(2, w - 2, 4):
        grosso = (x % 24) < 4
        alt = h - (0 if grosso else rng.integers(2, 8))
        cilindro(t, x, chao, x + rng.uniform(-1.2, 1.2), chao - alt + 2, 1.7 if grosso else 1.0, 1.4 if grosso else 0.8,
                 rampa=CASCA, semente=semente + x, rachas=1 if grosso else 0, nos=0, topo_cortado=grosso)
    for hy in (0.3, 0.55, 0.8):
        y = chao - (h - 4) * hy
        cilindro(t, 0, y + rng.uniform(-1, 1), w - 1, y + rng.uniform(-1, 1), 1.0, 1.0, rampa=CASCA,
                 semente=semente + int(hy * 100), rachas=0, nos=0)
        for x in range(4, w, 24):
            bd.amarracao(t, x, y, 1.4)
    contornar(t)
    return t


# ------------------------------------------------------------------ chão
def chao_caatinga(w, h=26, semente=0, rachado=False):
    """Terra batida do sertão: beirada de cima clara com tufos e pedrinhas, sulcos de
    carro de boi, pegadas, galhos secos e o corte embaixo em camadas com pedras e raízes."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    yy, xx = t.yy, t.xx
    sup = 2 + (ruido(1, w, 7, semente)[0] * 0.9).round()
    m = yy >= sup[None, :]
    prof = yy - sup[None, :]
    v = 0.75 - prof / h * 0.55 + ruido(h, w, (1.2, 5), semente) * 0.06
    v = np.where(prof < 1.2, 0.95, v)
    v = np.where((prof >= 1.2) & (prof < 2.2), 0.82, v)
    # Estratos do corte (faixas onduladas) mais para baixo.
    estr = np.sin((yy + ruido(h, w, (2, 30), semente + 1) * 2.5) * 1.1)
    v = np.where(prof > 9, v + estr * 0.06, v)
    for y0 in (6, 10):
        yb = y0 + np.sin(xx / 120 + y0) * 1.2
        v = np.where(np.abs(yy - yb) < 0.6, v - 0.22, v)
        v = np.where(np.abs(yy - yb + 1) < 0.5, v + 0.08, v)
    if rachado:
        rach = (np.abs(ruido(h, w, 2.2, semente + 9)) < 0.08) & (prof > 2)
        v = np.where(rach, v - 0.4, v)
    pintar(t, m, v, TERRA)
    # Pedras com luz.
    for _ in range(w // 16):
        x, y = rng.uniform(0, w), rng.uniform(3, h - 2)
        r = rng.uniform(0.8, 2.8) * (0.5 + y / h)
        e = t.elipse(x, y, r * 1.3, r)
        pintar(t, e, 0.75 - ((xx - x) + (yy - y)) / (3 * r), PEDRA if rng.random() < 0.5 else PEDRA_Q)
        t.ponto(x + r, y + r * 0.8, "terra_escura")
    # Raízes no corte.
    for _ in range(w // 70):
        x, y = rng.uniform(0, w), rng.uniform(12, h - 4)
        for k in range(int(rng.integers(6, 14))):
            t.ponto(x + k, y + math.sin(k / 2) * 1.2, "couro_escuro")
    # Galhos secos e pegadas na beirada.
    for _ in range(w // 40):
        x = rng.uniform(0, w)
        y = sup[int(min(w - 1, x))] + rng.uniform(1, 4)
        a = rng.uniform(-0.3, 0.3)
        L = rng.uniform(4, 10)
        t.linha(x, y, x + math.cos(a) * L, y + math.sin(a) * L, "cinza_escuro")
        t.ponto(x + L / 2, y - 1, "cinza_luz")
    for _ in range(w // 25):
        x, y = rng.uniform(0, w), rng.uniform(4, 8)
        t.chapado(t.elipse(x, y, 1.6, 0.7), "terra_media")
    return t


# ------------------------------------------------------------------ lajedo (plataforma)
def lajedo(w, h=40, semente=0):
    """Lajedo em camadas, como as pedras do Metal Slug: placas horizontais de pedra
    (cada uma com a beirada de cima acesa, a frente em degradê e a barriga escura),
    recuando e avançando um pouco, blocos separados por juntas, quinas gastas e redondas,
    topo plano claro onde se pisa, líquen e capim na beirada."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    rampa = ["sombra", "terra_escura", "terra", "terra_media", "barro", "areia_media", "areia", "areia_luz"]
    y = 0
    k = 0
    while y < h:
        esp = int(rng.integers(5, 13)) if y else min(5, h)
        recuo = 0 if y == 0 else int(rng.integers(0, 6))
        x = recuo - rng.uniform(0, 2)
        while x < w - recuo:
            larg = rng.uniform(28, 72)
            x0, x1 = max(recuo, x), min(w - recuo, x + larg)
            r = min(2.5, esp * 0.35)
            bloco = (t.retangulo(x0 + r, y, x1 - x0 - 2 * r, esp) | t.retangulo(x0, y + r, x1 - x0, esp - 2 * r) |
                     t.elipse(x0 + r, y + r, r, r) | t.elipse(x1 - r, y + r, r, r) |
                     t.elipse(x0 + r, y + esp - r, r, r) | t.elipse(x1 - r, y + esp - r, r, r))
            bloco &= t.px == VAZIO
            f = (t.yy - y) / max(1, esp)
            v = 0.82 - f * 0.55 - ((t.xx - x0) / max(1, x1 - x0)) * 0.12 + ruido(h, w, (0.5, 4), semente + k) * 0.05
            v = np.where(t.yy < y + 1.2, 0.98, v)
            if y == 0:
                v = np.where(t.yy < y + 2.5, 0.92, v - 0.05)
            pintar(t, bloco, v + rng.uniform(-0.06, 0.06), rampa)
            # Lasca: uma face clara em diagonal na quina de cima.
            if rng.random() < 0.4 and esp > 6:
                lx_ = x0 + rng.uniform(2, max(3, x1 - x0 - 8))
                lasca = t.poligono([(lx_, y + 1), (lx_ + 6, y + 1), (lx_ + 3, y + esp * 0.6)]) & bloco
                pintar(t, lasca, 0.9 + 0 * t.yy, rampa)
            x = x1 + 1
            k += 1
        y += esp
    m = t.px != VAZIO
    # Barriga escura de cada placa (sombra embaixo da de cima).
    for yy_ in range(1, h):
        sob = m[yy_] & ~m[yy_ - 1] if False else None
    # Líquen e capim.
    lq = m & (ruido(h, w, 1.3, semente + 5) > 2.0) & (t.yy > 3)
    t.px[lq] = IDX["laranja_escuro"]
    t.px[lq & (ruido(h, w, 0.6, semente + 6) > 0.5)] = IDX["ouro_escuro"]
    lv = m & (ruido(h, w, 1.1, semente + 7) > 2.1)
    t.px[lv] = IDX["caatinga_media"]
    t.px[lv & ~ndimage.binary_erosion(lv)] = IDX["mandacaru_luz"]
    contornar(t)
    for _ in range(max(1, w // 26)):
        c = capim(int(rng.integers(8, 14)), int(rng.integers(5, 9)), semente=int(rng.integers(0, 999)))
        x = int(rng.uniform(2, w - c.w - 2))
        sub = t.px[0:c.h, x:x + c.w]
        mm = (c.px != VAZIO) & (sub == VAZIO)
        mm[-2:] = False
        sub[mm] = c.px[mm]
    return t


# ------------------------------------------------------------------ céu e nuvens
def nuvens_cumulus(L=768, h=110, semente=3):
    """Cúmulos de Metal Slug: montes de gomos redondos, topo claro quase branco, sombra
    azul embaixo e base reta, com tufos menores soltos em volta."""
    t = Tela(L, h)
    rng = np.random.default_rng(semente)
    CEU_N = ["ceu_medio", "ceu_claro", "ceu_luz", "horizonte", "branco"]
    for (cx, base, larg, alto) in ((70, 70, 120, 46), (260, 52, 90, 34), (430, 84, 150, 56), (640, 60, 110, 40),
                                   (180, 98, 60, 18), (560, 100, 70, 20)):
        m = np.zeros((h, L), bool)
        gomos = []
        for k in range(int(larg / 10) + 3):
            gx = cx + rng.uniform(-larg / 2, larg / 2)
            f = 1 - abs(gx - cx) / (larg / 2)
            gr = 6 + f * alto * 0.45 + rng.uniform(-2, 3)
            gy = base - gr * 0.6 - f * alto * 0.35
            gomos.append((gx, gy, gr))
        for (gx, gy, gr) in gomos:
            for dx in (-L, 0, L):
                m |= t.elipse(gx + dx, gy, gr, gr * 0.85)
        m &= t.yy < base
        luz = np.zeros((h, L))
        for (gx, gy, gr) in gomos:
            for dx in (-L, 0, L):
                d = ((t.xx - gx - dx) * -0.5 + (t.yy - gy) * -0.85) / gr
                dentro = ((t.xx - gx - dx) / gr) ** 2 + ((t.yy - gy) / (gr * 0.85)) ** 2 < 1
                luz = np.where(dentro, np.maximum(luz, 0.5 + d * 0.45), luz)
        v = luz - np.clip((t.yy - (base - 8)) / 8, 0, 1) * 0.35
        pintar(t, m, v, CEU_N)
    return t


def ceu_dia(h=308, w=548):
    """Céu do sertão: azul fundo em cima clareando até o horizonte quase branco, as
    faixas misturando em manchas (sem degrau duro)."""
    t = Tela(w, h)
    for y0, y1, cor in ((0, 60, "ceu_escuro"), (60, 104, "ceu"), (104, 140, "ceu_medio"), (140, 176, "ceu_claro"),
                        (176, 214, "ceu_luz"), (214, h, "horizonte")):
        t.px[y0:y1] = IDX[cor]
        # Linha intercalada de 2 px na emenda (como nos céus do Metal Slug).
        if y0 > 0:
            t.px[y0:y0 + 2, ::2] = IDX[cor]
            t.px[y0 - 2:y0, 1::2] = IDX[cor]
    return t


_NEVOA = {}


def nevoa(t, k=0.3, cor="ceu_claro"):
    """Perspectiva aérea: mistura cada cor com o céu (k) e pega a mais parecida entre as
    cores antigas da paleta (fundo mais claro, azulado e de menos contraste)."""
    from motor import RGB, N_BASE
    ch = (round(k, 2), cor)
    if ch not in _NEVOA:
        alvo = RGB[IDX[cor]].astype(float)
        mix = RGB.astype(float) * (1 - k) + alvo * k
        d = ((mix[:, None, :] - RGB[None, :N_BASE, :].astype(float)) ** 2).sum(-1)
        _NEVOA[ch] = d.argmin(1)
    m = t.px != VAZIO
    t.px[m] = _NEVOA[ch][t.px[m]]
    return t


# ------------------------------------------------------------------ paredão de arenito (fundo)
ARENITO = ["terra_escura", "terra", "terra_media", "barro", "areia_media", "areia", "areia_luz"]


def paredao(W, h=130, semente=11):
    """Chapada de arenito ao fundo, pintada inteira (sem repetir): mesas de topo reto com
    a beirada de capim e moitas, paredão com caneluras verticais de erosão (cristas claras
    e sulcos escuros), faixas de estratos, quinas arredondadas pela luz de cima à
    esquerda, sombra fria nos recortes e o tálus de pedras e moitas na base."""
    t = Tela(W, h)
    rng = np.random.default_rng(semente)
    xs = np.arange(W)
    topo = np.full(W, float(h))
    quina = np.zeros(W)
    x = 0
    while x < W:
        larg = int(rng.integers(110, 260))
        alto = float(rng.integers(8, 50))
        rampa = int(rng.integers(6, 16))
        for k in range(larg):
            if x + k >= W:
                break
            b = min(k, larg - 1 - k)
            topo[x + k] = alto + max(0, rampa - b) * 1.8 + rng.uniform(0, 0.8)
            quina[x + k] = max(0, rampa - b) / rampa
        x += larg - int(rng.integers(0, 20))
    topo = ndimage.gaussian_filter1d(topo, 1.2)
    m = t.yy >= topo[None, :]
    # Campo de altura: caneluras (ruído esticado na vertical), estratos e a quina arredondada.
    flut = ruido(h, W, (14, 1.6), semente) * 0.7 + ruido(h, W, (6, 10), semente + 1) * 1.4
    camada = (t.yy + ruido(h, W, (2, 40), semente + 2) * 4) / 11
    estr = np.floor(camada)
    frac = camada - estr
    prof = t.yy - topo[None, :]
    # Cada estrato avança um pouco (beirada) e recua embaixo (barriga em sombra).
    alt = flut + estr * 0.4 - frac * 2.2 - quina[None, :] * 6 - np.clip(4 - prof, 0, 4) * 1.2
    gy, gx = np.gradient(ndimage.gaussian_filter(alt, 0.7))
    gx = gx * 1.6
    n = np.sqrt(gx * gx + gy * gy + 1)
    lum = (-gx * bd.LUZ[0] - gy * bd.LUZ[1] * 0.5 + bd.LUZ[2]) / n
    v = 0.25 + np.clip(lum, 0, 1) * 0.6 - np.clip(prof / h, 0, 1) * 0.15
    v = np.where(prof < 1.5, 0.95, v)
    v = np.where((prof >= 1.5) & (prof < 3), 0.8, v)
    # Sombra fria nos sulcos mais fundos.
    v = np.where((frac < 0.12) & (prof > 3), v + 0.22, v)
    v = np.where((frac > 0.85) & (prof > 3), v - 0.2, v)
    sulco = (ruido(h, W, (10, 1.0), semente + 3) < -1.6) & (prof > 6)
    bd.CONTRASTE = 0.8
    pintar(t, m, v + 0.08, ARENITO)
    bd.CONTRASTE = 1.0
    t.px[sulco & m] = IDX["terra"]
    # Tálus na base: rampa de pedras e terra subindo do pé do paredão.
    talus_h = 24 + ruido(1, W, 10, semente + 5)[0] * 5
    tal = t.yy >= (h - talus_h)[None, :]
    vt = 0.62 - (t.yy - (h - talus_h)[None, :]) / 40 + ruido(h, W, (1, 2), semente + 6) * 0.08
    pintar(t, tal & m, vt, ARENITO)
    for _ in range(W // 9):
        px = rng.uniform(0, W)
        py = rng.uniform(h - 22, h - 2)
        r = rng.uniform(1.2, 3.5)
        e = t.elipse(px, py, r * 1.3, r)
        pintar(t, e, 0.8 - ((t.xx - px) + (t.yy - py)) / (3 * r), ARENITO)
    # Moitas na beirada de cima e no tálus.
    for _ in range(W // 14):
        px = int(rng.uniform(1, W - 2))
        on_top = rng.random() < 0.55
        py = int(topo[px]) + (0 if on_top else int(rng.uniform(h - 30 - topo[px], h - 6 - topo[px])))
        r = rng.uniform(1.6, 3.4)
        e = t.elipse(px, py - r * 0.4, r * 1.3, r)
        pintar(t, e, 0.8 - ((t.xx - px) + (t.yy - py)) / (3 * r), FOLHA)
    return t


def moita(w=40, h=22, semente=0, seca=0.5):
    """Moita baixa da caatinga: tufos de folha miúda verdes e secos embolados, gravetos
    secos espetados para fora e a sombra no pé."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    for k in range(int(w / 6)):
        x = rng.uniform(w * 0.15, w * 0.85)
        y = h - rng.uniform(4, h * 0.6)
        r = rng.uniform(4, min(9, h * 0.45))
        tufo(t, x, y, r, FOLHA if rng.random() > seca else FOLHA_SECA, semente + k, atras=k % 3 == 0)
    for k in range(int(w / 8)):
        x0 = rng.uniform(w * 0.2, w * 0.8)
        a = rng.uniform(0.4, 2.7)
        L = rng.uniform(5, h * 0.8)
        t.linha(x0, h - 3, x0 + math.cos(a) * L, h - 3 - math.sin(a) * L, "cinza_escuro")
    t.px[(t.yy > h - 2) & (t.px != VAZIO)] = IDX["caatinga_esc"]
    contornar(t)
    return t
