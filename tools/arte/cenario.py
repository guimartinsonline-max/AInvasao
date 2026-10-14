"""Camadas do cenário da fase 1 (caatinga), geradas por script.

Todas as camadas têm 384 px de largura e emendam nas bordas (repetem sem costura).
"""
import numpy as np
from scipy import ndimage

from motor import BAYER4, IDX, VAZIO, Tela

L = 384

NUVEM = ["ceu", "ceu_claro", "horizonte", "branco"]
SERRA = ["ceu", "ceu", "ceu_claro", "horizonte"]
ARENITO = ["terra_escura", "terra", "barro", "areia", "areia_clara"]
GALHO = ["sombra", "cinza_escuro", "cinza", "cinza_claro"]
FOLHA = ["sombra", "caatinga_esc", "caatinga", "mandacaru"]
CACTO = ["caatinga_esc", "caatinga_esc", "caatinga", "mandacaru"]
PEDRA = ["sombra", "azul_sombra", "cinza_escuro", "cinza", "cinza_claro"]
MADEIRA = ["couro_escuro", "couro", "couro_claro", "barro"]


def bayer(h, w, dx=0, dy=0):
    return np.roll(np.tile(BAYER4, (h // 4 + 2, w // 4 + 2)), (dy, dx), axis=(0, 1))[:h, :w]


def ruido(h, w, sigma, semente, wrap=True):
    rng = np.random.default_rng(semente)
    r = ndimage.gaussian_filter(rng.standard_normal((h, w)), sigma, mode="wrap" if wrap else "reflect")
    return r / (r.std() + 1e-9)


def degrade(t, y0, y1, cor_cima, cor_baixo, x0=0, x1=None, mascara=None):
    """Transição pontilhada (Bayer) entre duas cores nas linhas y0..y1."""
    x1 = t.w if x1 is None else x1
    b = bayer(t.h, t.w)
    for y in range(max(0, y0), min(t.h, y1)):
        f = (y - y0 + 0.5) / max(1, (y1 - y0))
        linha = np.where(b[y, x0:x1] < f, IDX[cor_baixo], IDX[cor_cima])
        if mascara is not None:
            m = mascara[y, x0:x1]
            t.px[y, x0:x1][m] = linha[m]
        else:
            t.px[y, x0:x1] = linha


def ceu(h=216):
    t = Tela(L, h)
    faixas = [(0, "ceu_escuro"), (56, "ceu"), (112, "ceu_claro"), (150, "horizonte")]
    for k, (y, cor) in enumerate(faixas):
        fim = faixas[k + 1][0] if k + 1 < len(faixas) else h
        t.px[y:fim] = IDX[cor]
        if k + 1 < len(faixas):
            degrade(t, fim - 10, fim + 6, cor, faixas[k + 1][1])
    return t


def nuvens(semente=3):
    t = Tela(L, 90)
    rng = np.random.default_rng(semente)
    for (cx, by, larg) in [(50, 46, 70), (190, 30, 56), (300, 60, 90)]:
        puffs = []
        n = int(larg / 9)
        for k in range(n):
            x = cx - larg / 2 + (k + 0.5) * larg / n + rng.uniform(-3, 3)
            centro = 1 - abs((k + 0.5) / n - 0.5) * 2
            r = 6 + centro * larg * 0.16 + rng.uniform(-2, 2)
            puffs.append((x, by - r * 0.55, r))
        # Puffs de trás (mais escuros) primeiro, depois os da frente.
        for k, (x, y, r) in enumerate(sorted(puffs, key=lambda p: -p[2])):
            m = t.elipse(x % L, y, r, r * 0.85) | t.elipse(x % L - L, y, r, r * 0.85) | t.elipse(x % L + L, y, r, r * 0.85)
            m &= t.yy < by
            t.cel(m, NUVEM, sombra=3, luz=2, linha=False, rebaixo=True)
        # Base reta e sombreada.
        base = (t.yy >= by - 3) & (t.yy < by) & (t.px != VAZIO)
        t.px[base] = IDX["ceu_claro"]
    return t


def serras():
    t = Tela(L, 70)
    x = np.arange(L)
    perfil = (26 + 10 * np.sin(x / L * 2 * np.pi * 2 + 1) + 5 * np.sin(x / L * 2 * np.pi * 5 + 2)
              + 1.5 * ruido(1, L, 6, 7)[0])
    m = t.yy >= perfil[None, :]
    t.cel(m, SERRA, sombra=0, luz=1, linha=False)
    # Lado sombreado das encostas: onde o perfil desce para a direita.
    desce = np.gradient(perfil) > 0.12
    for xx in np.where(desce)[0]:
        y0 = int(perfil[xx]) + 1
        col = t.px[y0:y0 + 26, xx]
        col[col != VAZIO] = IDX["ceu"]
    degrade(t, 52, 70, "ceu_claro", "horizonte", mascara=m)
    return t


def paredoes(semente=11):
    """Paredões de arenito com camadas, rachaduras e sombra fria."""
    h = 90
    t = Tela(L, h)
    rng = np.random.default_rng(semente)
    perfil = np.full(L, h, dtype=float)
    x = 0
    while x < L:
        largura = rng.integers(50, 110)
        topo = rng.integers(14, 46)
        rampa = rng.integers(4, 10)
        for k in range(largura):
            xx = (x + k) % L
            borda = min(k, largura - 1 - k)
            y = topo + max(0, rampa - borda) * 2.2 + rng.uniform(0, 1.2)
            perfil[xx] = min(perfil[xx], y)
        x += largura - rng.integers(0, 20)
    perfil = ndimage.uniform_filter1d(perfil, 3, mode="wrap")
    m = t.yy >= perfil[None, :]
    # Volume: topo iluminado, faces mais escuras, lado direito na sombra.
    t.cel(m, ARENITO, sombra=0, luz=2, linha=False)
    nivel = np.full((h, L), 2)
    prof = t.yy - perfil[None, :]
    nivel[prof < 3] = 3
    nivel[prof < 1.5] = 4
    # Camadas de sedimento.
    estratos = ruido(h, L, (0.6, 12), 5)
    faixa = (np.floor((t.yy + estratos * 3) / 9) % 3 == 0)
    nivel = np.where(faixa & (prof > 4), nivel - 1, nivel)
    # Sombra das faces que olham para a direita.
    desce = np.gradient(perfil) > 0.6
    sombra = ndimage.binary_dilation(np.repeat(desce[None, :], h, 0), structure=np.ones((1, 9)), origin=(0, -4))
    nivel = np.where(sombra & (prof > 1), np.minimum(nivel, 1), nivel)
    # Sulcos verticais de erosão.
    sulcos = ruido(h, L, (14, 1.2), 9)
    nivel = np.where((sulcos > 1.1) & (prof > 5), nivel - 1, nivel)
    nivel = np.where((sulcos < -1.4) & (prof > 5) & ~sombra, nivel + 1, nivel)
    # Rachaduras verticais.
    for _ in range(9):
        cx = rng.integers(0, L)
        y = perfil[cx] + rng.integers(4, 14)
        for _k in range(rng.integers(5, 12)):
            if 0 <= int(y) < h:
                nivel[int(y), cx % L] = 0
            y += 1
            if rng.random() < 0.25:
                cx += rng.choice((-1, 1))
    # Pé do paredão some na névoa quente.
    cores = np.array([IDX[c] for c in ARENITO])[np.clip(nivel, 0, 4)]
    t.px[m] = cores[m]
    degrade(t, h - 22, h, "barro", "areia", mascara=m & (prof > 6))
    return t


def planicie(h=40):
    """Chão distante entre os paredões e a caatinga."""
    t = Tela(L, h)
    t.px[:] = IDX["areia"]
    degrade(t, 0, 10, "areia_clara", "areia")
    degrade(t, h - 14, h, "areia", "barro")
    return t


def galho(t, x, y, ang, comp, esp, prof, rng):
    if prof == 0 or comp < 2:
        return
    x2 = x + np.cos(ang) * comp
    y2 = y - np.sin(ang) * comp
    for dx in (0, L, -L):
        t.cel(t.capsula(x + dx, y, x2 + dx, y2, esp, max(esp * 0.7, 0.5)), GALHO, sombra=1, luz=0, linha=False)
    n = 2 if prof > 1 else 3
    for k in range(n):
        da = rng.uniform(0.25, 0.7) * (1 if k % 2 else -1)
        galho(t, x2, y2, ang + da, comp * rng.uniform(0.55, 0.75), esp * 0.7, prof - 1, rng)
    if prof <= 2 and rng.random() < 0.6:
        for dx in (0, L, -L):
            t.cel(t.elipse(x2 + dx, y2, rng.uniform(2.5, 4.5), rng.uniform(1.6, 2.6)), FOLHA, sombra=1, luz=1)


def mandacaru(t, x, chao, altura, rng):
    corpo = t.capsula(x, chao, x, chao - altura, 3.2, 3.0)
    bracos = []
    for lado, hb, ab in ((-1, 0.45, 0.35), (1, 0.6, 0.3)):
        if rng.random() < 0.85:
            yb = chao - altura * hb
            xb = x + lado * 7
            bracos.append(t.capsula(x, yb, xb, yb, 2.2) | t.capsula(xb, yb, xb, yb - altura * ab, 2.3, 2.1))
    for m in bracos + [corpo]:
        t.cel(m, CACTO, sombra=1, luz=1)
        # Costelas: listras verticais claras e escuras.
        cols = np.where(m.any(0))[0]
        for c in cols[1:-1:2]:
            col = m[:, c] & (t.px[:, c] != IDX["caatinga_esc"])
            t.px[col, c] = IDX["mandacaru"] if c % 4 == 1 else IDX["caatinga"]
    # Espinhos.
    ys, xs = np.where(corpo | (bracos[0] if bracos else corpo))
    for k in range(0, len(xs), 11):
        t.ponto(xs[k] + (1 if xs[k] > x else -1), ys[k], "areia_clara")


def caatinga(semente=21):
    h = 80
    t = Tela(L, h)
    rng = np.random.default_rng(semente)
    chao = h - 6
    # Moitas de fundo.
    for _ in range(18):
        cx, r = rng.uniform(0, L), rng.uniform(6, 14)
        for dx in (0, L, -L):
            t.cel(t.elipse(cx + dx, chao - r * 0.4, r, r * 0.6), FOLHA, sombra=2, luz=1, linha=False, deslocar=-1)
    # Árvores secas retorcidas.
    for xa in (30, 150, 255, 345):
        galho(t, xa + rng.uniform(-8, 8), chao, np.pi / 2 + rng.uniform(-0.2, 0.2), rng.uniform(16, 22), 2.2, 4, rng)
    for xm in (95, 205, 310):
        mandacaru(t, xm, chao, rng.uniform(26, 38), rng)
    # Moitas da frente.
    for _ in range(14):
        cx, r = rng.uniform(0, L), rng.uniform(5, 11)
        for dx in (0, L, -L):
            t.cel(t.elipse(cx + dx, chao - r * 0.3, r, r * 0.55), FOLHA, sombra=2, luz=1)
    # Faixa de terra no pé.
    m = t.yy >= chao
    t.chapado(m, "areia")
    degrade(t, chao, h, "areia", "barro")
    t.contorno("caatinga_esc")
    return t


def chao_tile(w=128, h=24, semente=31):
    """Ladrilho do chão: borda de areia, terra com pedrinhas e sombra embaixo."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    t.px[:] = IDX["barro"]
    n = ruido(h, w, 1.2, semente)
    t.px[(n > 0.9) & (t.yy > 4)] = IDX["terra"]
    t.px[(n < -1.2) & (t.yy > 4)] = IDX["areia"]
    degrade(t, 12, h, "barro", "terra")
    degrade(t, 18, h + 6, "terra", "terra_escura", mascara=(t.yy >= 18))
    # Borda de cima.
    t.px[0:2] = IDX["areia_clara"]
    t.px[2:4] = IDX["areia"]
    t.px[4] = IDX["barro"]
    for x in range(0, w, 3):
        if rng.random() < 0.5:
            t.px[2, x] = IDX["areia_clara"]
    # Pedrinhas.
    for _ in range(5):
        px, py, r = rng.uniform(4, w - 4), rng.uniform(8, h - 3), rng.uniform(1.0, 2.2)
        t.cel(t.elipse(px, py, r * 1.3, r), PEDRA, sombra=1, luz=1, linha=False)
    return t


def touceira(semente):
    """Tufo de capim seco para enfeitar a beira do chão."""
    t = Tela(14, 10)
    rng = np.random.default_rng(semente)
    for _ in range(9):
        x = rng.uniform(2, 12)
        topo = rng.uniform(0, 5)
        inc = rng.uniform(-3, 3)
        cor = rng.choice(["areia_clara", "areia", "barro", "mandacaru"])
        t.linha(int(x), 9, int(x + inc), int(topo), cor)
    return t


def caixote():
    t = Tela(24, 18)
    m = t.retangulo(0, 0, 24, 18)
    t.cel(m, MADEIRA, sombra=1, luz=1, linha=False)
    for y in (6, 12):
        t.px[y, :] = IDX["couro_escuro"]
    for y0 in (1, 7, 13):
        for x in range(2, 22, 5):
            t.ponto(x, y0 + 2, "couro")
    # Travessas e cantoneiras de metal.
    for x0 in (2, 19):
        t.cel(t.retangulo(x0, 0, 3, 18), MADEIRA, sombra=1, luz=1, deslocar=-1)
    for (x, y) in ((0, 0), (21, 0), (0, 15), (21, 15)):
        t.cel(t.retangulo(x, y, 3, 3), PEDRA, sombra=1, luz=1)
    t.contorno("sombra")
    return t


def laje(w=32, h=12):
    t = Tela(w, h)
    t.cel(t.retangulo(0, 0, w, h), PEDRA, sombra=3, luz=2, linha=False, rebaixo=True)
    n = ruido(h, w, 1.0, 4)
    t.px[(n > 1.3) & (t.yy > 2) & (t.yy < h - 2)] = IDX["cinza_escuro"]
    t.linha(9, 3, 12, 7, "azul_sombra")
    t.linha(22, 4, 20, 8, "azul_sombra")
    t.px[0, :] = IDX["cinza_claro"]
    t.px[1, ::3] = IDX["branco"]
    return t
