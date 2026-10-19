"""Aliens da fase 2, desenho final (nível Metal Slug), feitos por relevo.

Cada parte é um campo de altura; a luz (de cima, à esquerda) vira tons da rampa,
com brilho molhado no topo. Assim o cérebro ganha giros de verdade, a lesma ganha
anéis e dobras e a pele fica úmida.

    python3 tools/arte/aliens.py      -> prévia em tools/arte/pixel/aliens_previa.png
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela, IDX, RAIZ, VAZIO  # noqa: E402

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

CEREBRO = ["roxo_escuro", "roxo", "lilas", "rosa_poeira", "pele_luz", "pele_brilho"]
SULCO = "roxo_escuro"
LESMA = ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz", "alien_brilho"]
CARNE = ["roxo_escuro", "vermelho_esc", "pele_sombra", "pele_media", "pele", "pele_luz"]
QUITINA = ["sombra", "couro_profundo", "couro_escuro", "couro", "couro_claro", "areia_luz"]
METAL = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "aco_brilho"]
VIDRO = ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz", "alien_brilho"]


def suave(m, s):
    return ndimage.gaussian_filter(m.astype(float), s)


def domo(t, cx, cy, rx, ry):
    """Altura de uma elipse em domo (0 na borda, 1 no centro)."""
    d = ((t.xx - cx) / rx) ** 2 + ((t.yy - cy) / ry) ** 2
    return np.sqrt(np.clip(1 - d, 0, 1))


def relevo(t, mascara, H, rampa, luz=(-0.6, -0.8), ambiente=0.15, contraste=1.0,
           brilho=0.0, linha=True, dither=True):
    """Pinta a máscara pelo campo de altura H. brilho > 0 põe reflexo molhado."""
    if not mascara.any():
        return mascara
    gy, gx = np.gradient(H)
    lx, ly = luz
    lz = 0.75
    nl = math.sqrt(lx * lx + ly * ly + lz * lz)
    n = np.sqrt(gx * gx + gy * gy + 1.0)
    nx, ny, nz = -gx / n, -gy / n, 1.0 / n
    lam = (nx * lx + ny * ly + nz * lz) / nl
    lum = (lam - 0.45) * 1.9 * contraste + 0.5 + ambiente
    if brilho:
        # Reflexo especular (meio caminho entre luz e olho).
        hx, hy, hz = lx / nl, ly / nl, lz / nl + 1
        hn = math.sqrt(hx * hx + hy * hy + hz * hz)
        spec = np.clip((nx * hx + ny * hy + nz * hz) / hn, 0, 1) ** 40
        lum = lum + spec * brilho
    k = len(rampa)
    v = np.clip(lum, 0, 0.999) * k
    base = np.floor(v)
    if dither:
        frac = v - base
        h, w = mascara.shape
        lim = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
        base = base + ((frac > 0.8) & (lim < (frac - 0.8) * 4))
    nivel = np.clip(base, 0, k - 1).astype(int)
    cores = np.array([IDX[c] for c in rampa])[nivel]
    if linha:
        borda = mascara & ~ndimage.binary_erosion(mascara)
        ja = t.px != VAZIO
        viz = ndimage.binary_dilation(ja & ~mascara)
        cores = np.where(borda & viz, IDX[rampa[0]], cores)
    t.px[mascara] = cores[mascara]
    return mascara


def ruido(shape, s, semente):
    rng = np.random.default_rng(semente)
    r = ndimage.gaussian_filter(rng.standard_normal(shape), s)
    return r / (np.abs(r).max() + 1e-9)


# ---------------------------------------------------------------- cerebrão

def cerebro(t, cx, cy, rx, ry, fase=0.0, semente=5):
    """Cérebro com fissura central, giros roliços separados por sulcos, veias e reflexo molhado."""
    m = t.elipse(cx, cy, rx, ry) & ~(t.elipse(cx + rx * 0.2, cy + ry * 1.3, rx * 0.75, ry * 0.5))
    base = domo(t, cx, cy, rx, ry)
    # Labirinto de giros: ruído passa-banda (diferença de gaussianas); os sulcos
    # ficam onde ele cruza o zero, e cada giro é um tubo roliço entre eles.
    rng = np.random.default_rng(semente)
    r0 = rng.standard_normal(m.shape)
    bp = ndimage.gaussian_filter(r0, 1.25) - ndimage.gaussian_filter(r0, 2.6)
    bp = bp / (np.abs(bp[m]).max() + 1e-9)
    # Fissura entre os hemisférios: de trás de cima para a frente.
    fiss = np.abs((t.xx - cx + 1) - (t.yy - cy) * 0.35 + np.sin(t.yy * 0.8) * 0.5)
    bp = np.where(fiss < 1.0, 0, bp)
    tubo = np.tanh(np.abs(bp) * 6)
    sulcos = (np.abs(bp) < 0.07) | (fiss < 0.6)
    H = base * 6.5 * (1 + 0.05 * fase) + tubo * 2.2
    H = ndimage.gaussian_filter(H, 0.45)
    relevo(t, m, H, CEREBRO, ambiente=0.05, contraste=1.25, brilho=1.4)
    t.px[m & sulcos & (base > 0.25)] = IDX[SULCO]
    # Duas veias inchadas descendo pela lateral.
    for (x, y, a) in ((cx - rx * 0.5, cy + ry * 0.75, -1.9), (cx + rx * 0.35, cy + ry * 0.8, -1.4)):
        for k in range(int(ry * 0.9)):
            a += rng.uniform(-0.35, 0.35)
            x += math.cos(a) * 0.9
            y += math.sin(a) * 0.9
            xi, yi = int(x), int(y)
            if 0 <= xi < t.w and 0 <= yi < t.h and m[yi, xi] and not sulcos[yi, xi]:
                t.px[yi, xi] = IDX["vermelho_medio"] if k % 4 else IDX["vermelho"]
    return m


def cerebrao(fase=0.0, pose="parado", k=0):
    """Cerebrão: cérebro exposto enorme, cara de três olhos com mandíbulas,
    corpo de lesma babando, bracinhos com a pistola de raio. Olha para a direita.
    pose: parado, anda (k 0-3, rasteja), atira (tranco e bulbo aceso), grito, morte."""
    anda = pose == "anda"
    berra = pose in ("grito", "morte")
    cauda = 4 + ((0, 2, 3, 1)[k] if anda else 0)
    ph = fase * 0.6 + (k * 1.57 if anda else 0)
    rx_ = -1.5 if pose == "atira" else 0
    t = Tela(60, 52)
    chao = 50
    xx, yy = t.xx, t.yy

    def parte(m, rampa, s=1.0, alt=3.0, amb=0.05, br=0.8, linha=True):
        relevo(t, m, suave(m, s) * alt, rampa, ambiente=amb, brilho=br, linha=linha)
        return m

    # Poça de gosma.
    t.chapado(t.elipse(25, chao + 0.2, 24, 1.8) & (yy > chao - 1), "alien_esc")
    t.chapado(t.elipse(23, chao + 0.4, 17, 1.0) & (yy > chao - 0.5), "alien_medio")
    for x in (5, 14, 34, 44):
        t.ponto(x, chao, "alien_luz")

    # Corpo de lesma: rabo comprido à esquerda subindo para o tronco à direita.
    rabo = t.capsula(cauda, chao - 3, 29, chao - 7, 3, 8.5)
    tronco = t.capsula(30, chao - 8, 37, 30, 8.5, 7)
    saia = t.elipse(22, chao - 2, 20, 3.5) & (yy < chao)
    corpo = (rabo | tronco | saia) & (yy < chao + 0.5)
    H = suave(corpo, 2.6) * 6
    s_ = xx * 0.9 - yy * 0.45
    H = H + np.clip(np.sin(s_ * 1.05 + ph), -0.2, 1) * 1.1 * suave(corpo, 1.5)
    H = H + ruido(corpo.shape, 0.8, 21) * 0.35
    relevo(t, corpo, H, ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz"],
           ambiente=-0.42, contraste=1.2, brilho=1.2, dither=False)
    # Crista de calombos nas costas, do rabo ao tronco.
    for k in range(1, 7, 2):
        bx = 7 + k * 3.4
        by = chao - 6.2 - k * 1.35 - (k > 4) * (k - 4) * 1.6
        cm = t.elipse(bx, by + 0.6, 1.4, 1.0)
        relevo(t, cm, domo(t, bx, by, 1.5, 1.2) * 2.5, ["alien_profundo", "alien_esc", "alien_medio", "alien_luz", "alien_brilho"],
               ambiente=0.0, brilho=1.6)
    dobra = corpo & (np.sin(s_ * 1.05 + ph) < -0.8) & (suave(corpo, 1.5) > 0.6)
    t.px[dobra] = IDX["alien_profundo"]
    # Pé ondulado embaixo.
    pe = saia & (yy > chao - 2.5) & corpo
    t.chapado(pe, "alien_esc")
    t.chapado(pe & (np.sin(xx * 1.4 + ph * 1.6) > 0.3) & (yy > chao - 1.5), "alien_medio")
    # Barriga translúcida com órgãos brilhando.
    barriga = t.elipse(36, 41, 4.2, 6.5) & corpo
    parte(barriga, ["alien_esc", "alien_medio", "alien", "alien_luz", "alien_brilho"], s=1.4, alt=4, amb=0.2, br=1.2)
    for (ox, oy, r, c) in ((35.5, 38.5, 1.6, "amarelo_claro"), (37, 42.5, 1.3, "alien_brilho"), (35, 45, 1.0, "amarelo_claro")):
        t.chapado(t.elipse(ox, oy, r, r * 0.8), c)
    # Pústulas no rabo.
    for (px, py, r) in ((10, chao - 5.5, 1.6), (17, chao - 8, 1.3), (24, chao - 10, 1.8), (28, chao - 13.5, 1.2)):
        pm = t.elipse(px, py, r, r)
        relevo(t, pm, domo(t, px, py, r, r) * 3, ["alien_esc", "alien", "alien_luz", "alien_brilho", "amarelo_claro"],
               ambiente=0.15, brilho=1.5)

    def braco(pts, r, rampa=LESMA):
        for a, b in zip(pts, pts[1:]):
            parte(t.capsula(a[0], a[1], b[0], b[1], r, r * 0.85), rampa, s=0.9, alt=3, amb=-0.05)
    # Braço de trás.
    braco([(31, 34), (27, 39), (30, 43)], 1.4)
    for k in range(3):
        braco([(30, 43), (32 + k * 0.8, 44 + k * 0.6), (33 + k, 43.5 + k * 1.2)], 0.55)

    # Gola de carne enrugada onde o cérebro assenta, com fiapos pendurados.
    gola = t.elipse(32, 22.5, 11, 3.6)
    relevo(t, gola, suave(gola, 1.2) * 3 + np.sin(xx * 1.7) * 0.6, CARNE, ambiente=0.05, brilho=0.8)
    for (x0, y0, x1, y1) in ((22, 23, 19, 29), (25, 25, 23, 31), (28, 25, 28, 28)):
        parte(t.capsula(x0, y0, x1, y1, 1.1, 0.5), CARNE, s=0.7, alt=2)
    t.ponto(19, 30, "alien_luz")

    # Cara embaixo da frente do cérebro.
    cara = t.elipse(41, 28.5, 7, 6)
    relevo(t, cara, domo(t, 41, 28.5, 7, 6) * 4, CARNE, ambiente=0.4, brilho=1.0)
    # Rugas da testa.
    # Mandíbulas de quitina abertas.
    mands = ((((43, 31.5), (49, 31), (50.5, 35)), ((38.5, 32), (37.5, 37), (41, 39.5))) if berra
             else (((43, 31.5), (47.5, 33), (48, 37.5)), ((38.5, 32), (39.5, 36.5), (44, 38))))
    for pts in mands:
        for a, b in zip(pts, pts[1:]):
            parte(t.capsula(a[0], a[1], b[0], b[1], 1.5, 0.55), ["sombra", "cinza_escuro", "cinza", "cinza_luz", "cinza_claro", "branco"], s=0.6, alt=2.5, amb=0.1, br=1.6)
    # Boca redonda com dentinhos e baba.
    bb = 1.7 if berra else 1.0
    t.chapado(t.elipse(43.5, 32.8 + (bb - 1), 2.1 * min(bb, 1.3), 1.5 * bb), "preto")
    t.chapado(t.elipse(43.5, 33.2 + (bb - 1) * 1.5, 1.2, 0.7 * bb), "vermelho_esc")
    for x in (42, 43.5, 45):
        t.ponto(x, 31.6, "cinza_claro")
    t.linha(44, 34, 44, 39, "alien_luz")
    t.ponto(44, 40, "alien_brilho")

    # Três olhos em órbitas fundas.
    def olho(x, y, r, olhar=0.6):
        orb = t.elipse(x, y + 0.2, r + 1.0, r + 0.8)
        t.chapado(orb, "vermelho_esc")
        bola = t.elipse(x, y, r, r)
        relevo(t, bola, domo(t, x, y, r, r) * 3, ["cinza", "cinza_luz", "cinza_claro", "branco", "branco"],
               ambiente=0.3, brilho=1.0, linha=False)
        ix = x + olhar * r * 0.35
        if pose == "morte":
            t.chapado(t.elipse(x, y + r * 0.6, r * 0.6, r * 0.35) & bola, "amarelo_claro")
        elif pose == "grito":
            t.chapado(t.elipse(ix, y, r * 0.4, r * 0.45) & bola, "amarelo_fogo")
            t.ponto(ix, y, "preto")
        else:
            t.chapado(t.elipse(ix, y + 0.2, r * 0.65, r * 0.72) & bola, "amarelo_fogo")
            t.chapado(t.elipse(ix + 0.15, y + 0.2, max(r * 0.22, 0.5), r * 0.6) & bola, "preto")
        t.ponto(x - r * 0.4, y - r * 0.4, "branco")
        pal = t.elipse(x, y - r * (1.1 if pose == "grito" else 0.75), r + 1.0, r * 0.5) & orb
        relevo(t, pal, suave(pal, 0.5) * 2, CARNE, ambiente=0.15, linha=False)
    olho(42, 28.2, 2.6)
    olho(37, 29, 1.7)
    olho(46.3, 28.8, 1.6)

    # Cérebro enorme por cima, inclinado para a frente.
    fase = 1.6 if berra else fase
    cerebro(t, 29, 12.5 - fase * 0.4, 16 + fase * 0.7, 11 + fase * 0.6, fase=fase)
    if pose == "morte":
        # Cérebro rachando: fendas escuras com gosma verde vazando.
        for (x0, y0, pts) in ((24, 3, ((26, 7), (24, 11), (27, 15))), (35, 5, ((33, 9), (36, 13), (34, 17)))):
            xa, ya = x0, y0
            for (xb, yb) in pts:
                t.linha(xa, ya, xb, yb, "preto")
                t.linha(xa + 1, ya, xb + 1, yb, "alien")
                xa, ya = xb, yb
        for (gx, gy) in ((27, 16), (34, 18), (20, 20)):
            t.linha(gx, gy, gx, gy + 3, "alien_luz")
            t.ponto(gx, gy + 4, "alien_brilho")
    # Gota de líquido escorrendo de baixo do cérebro.
    t.linha(21, 21, 21, 24 + int(fase * 2), "rosa_poeira")
    t.ponto(21, 25 + int(fase * 2), "pele_brilho")

    # Braço da frente estendido com a pistola de raio.
    braco([(38, 37), (43 + rx_ * 0.5, 42), (48 + rx_, 40)], 1.5)
    corpo_p = t.capsula(47 + rx_, 39, 54 + rx_, 39, 2.3, 1.7)
    parte(corpo_p, METAL, s=0.7, alt=3, amb=0.1, br=1.5)
    for x in (50 + rx_, 52 + rx_):
        t.linha(x, 37, x, 41, "cinza_escuro")
    bulbo = t.elipse(49.5 + rx_, 36.3, 2.4, 2.0)
    relevo(t, bulbo, domo(t, 49.5 + rx_, 36.3, 2.4, 2.0) * 3, VIDRO, ambiente=0.3, brilho=2.0)
    t.ponto(49 + rx_, 36, "alien_brilho")
    cano = t.retangulo(54 + rx_, 38, 4, 2)
    parte(cano, METAL, s=0.5, alt=2, amb=0.2)
    t.ponto(58 + rx_, 38, "alien_brilho")
    t.ponto(58 + rx_, 39, "alien")
    parte(t.capsula(48 + rx_, 40, 47 + rx_, 43.5, 1.1), QUITINA, s=0.5, alt=2)
    for k in range(3):
        parte(t.capsula(47.5 + rx_, 40 + k, 49.5 + rx_, 41 + k * 1.1, 0.6), LESMA, s=0.5, alt=2, amb=0.05)

    if pose == "atira":
        # Bulbo aceso descarregando.
        t.chapado(t.elipse(49.5 + rx_, 36.3, 1.6, 1.3), "alien_brilho")
        t.ponto(49 + rx_, 35.5, "branco")
    t.contorno("sombra")
    return t


PELE_O = ["sombra", "sombra_media", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "cinza_claro"]
JUNTA = ["roxo_escuro", "vermelho_esc", "rosa_poeira", "pele_luz", "pele_brilho"]


def olheiro(fase=0.0, pose="parado", k=0):
    """Olheiro: magrelo encurvado de costelas aparecendo, pernas viradas para trás,
    dedos compridos, boca vertical na barriga e o pescoço terminando num olho gigante
    com veias e pálpebra. Olha para a direita. fase: 0 parado, 1 passo/piscada.
    pose: parado, anda (k 0-3), mira (olho acendendo, avisa), atira (raio saindo), grito, morte."""
    ciclo = ((2, -2), (0.5, -0.5), (-2, 2), (-0.5, 0.5))
    pf, pb = ciclo[k] if pose == "anda" else ((1.5 * fase, -1.5 * fase) if pose == "parado" else (0, 0))
    mirando = pose in ("mira", "atira")
    if mirando:
        pesc, (ex, ey) = [(28, 19), (32, 18.5), (36, 20), (40, 22)], (45.5, 25)
        mao, garras, dedao = (40, 33), ((5, -3, 8, -3.5), (5.5, 0, 8.5, 1), (4, 3, 6.5, 5)), (1, 4, 2, 6)
        braco_f = [(30, 21), (35, 28), (40, 33)]
    elif pose == "grito":
        pesc, (ex, ey) = [(28, 19), (27.5, 14.5), (29, 11.5), (31, 9)], (35, 8.5)
        mao, garras, dedao = (45, 17), ((3, -6, 4, -9), (5, -5, 7, -7), (6, -2, 9, -3)), (2, 2, 4, 3)
        braco_f = [(30, 21), (38, 22), (45, 17)]
    elif pose == "morte":
        pesc, (ex, ey) = [(28, 19), (31, 17), (34, 17), (37, 16)], (41, 13)
        mao, garras, dedao = (41, 29), ((4, 2, 6, 5), (3, 3, 4.5, 6.5), (1.5, 3.5, 2, 7)), (0, 3, 0.5, 5)
        braco_f = [(30, 21), (36, 27), (41, 29)]
    else:
        pesc, (ex, ey) = [(28, 19), (30, 15.5), (33, 14), (36, 12.5)], (41, 9)
        mao, garras, dedao = (42, 26), ((5, -4, 8, -5), (6, -1, 9, -0.5), (5, 2, 7.5, 4)), (1.5, 3.5, 3, 5)
        braco_f = [(30, 21), (36, 27), (42, 26)]
    fecha = {"mira": 0.12, "atira": 0.06, "grito": 0.0, "morte": 0.55}.get(pose, 0.2 + 0.4 * fase)
    if pose == "anda" and k == 2:
        fecha = 0.3
    t = Tela(60, 60)
    chao = 58
    xx, yy = t.xx, t.yy

    def osso(pts, r0, r1, rampa=PELE_O, amb=0.0, br=0.6, s=0.8):
        n = len(pts) - 1
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            ra = r0 + (r1 - r0) * k / n
            rb = r0 + (r1 - r0) * (k + 1) / n
            m = t.capsula(a[0], a[1], b[0], b[1], ra, rb)
            relevo(t, m, suave(m, s) * 3, rampa, ambiente=amb, brilho=br, dither=False)
        for a in pts[1:-1]:
            j = t.elipse(a[0], a[1], r0 * 0.9, r0 * 0.9)
            relevo(t, j, domo(t, a[0], a[1], r0 * 0.9, r0 * 0.9) * 2.5, rampa, ambiente=amb + 0.1, brilho=br, dither=False)

    # Sombra no chão.
    t.chapado(t.elipse(28, chao + 0.4, 13, 1.3) & (yy > chao - 0.6), "couro_profundo")

    # Perna de trás (mais escura): quadril, joelho para trás, jarrete, pé de dedos.
    # (joelho para a frente, jarrete para trás, pé de dedos compridos: perna de bicho)
    osso([(23, 37), (26 + pb, 44), (19 + pb, 50), (21 + pb, chao - 1)], 1.6, 0.9, amb=-0.12)
    for dx in (3, 5):
        osso([(21 + pb, chao - 1), (21 + pb + dx, chao - 0.4)], 0.7, 0.45, amb=-0.12)
    # Perna da frente.
    osso([(25, 37), (30 + pf, 43), (25 + pf, 50), (27 + pf, chao - 1)], 1.8, 1.0, amb=0.18)
    for j, dx in enumerate((3, 5, 6)):
        osso([(27 + pf, chao - 1), (27 + pf + dx, chao - 0.4 + (j == 2) * 0.3)], 0.75, 0.45, amb=0.18)
    t.ponto(33.5 + pf, chao, "cinza_claro")

    # Braço de trás pendurado, compridíssimo.
    osso([(24, 23), (17, 29), (15, 37)], 1.3, 0.85, amb=-0.12)
    for k in range(3):
        osso([(15, 37), (13.5 + k * 1.2, 41), (13 + k * 1.8, 45)], 0.55, 0.35, amb=-0.12)

    # Tronco encurvado: caixa de costelas, cintura fina, barriga murcha.
    pelve = t.elipse(24.5, 36, 3.6, 2.6)
    peito = t.elipse(27, 24, 5.5, 7, ang=0.35)
    cintura = t.capsula(24.5, 34.5, 26.5, 28, 2.4, 4)
    tronco = pelve | peito | cintura
    H = suave(tronco, 1.8) * 5
    # Costelas: arcos que sobem para as costas.
    u = (yy - 18) - (xx - 27) * 0.35
    cost = (np.sin(u * 1.35) > 0.35) & peito & (yy > 18.5) & (yy < 29.5)
    H = H + cost * 0.9
    H = ndimage.gaussian_filter(H, 0.45)
    relevo(t, tronco, H, PELE_O, ambiente=0.2, contraste=1.2, brilho=0.9, dither=False)
    # Costelas desenhadas: sulco escuro embaixo, aresta clara em cima.
    for k in range(5):
        y0 = 19.5 + k * 2.2
        for x in np.arange(22.5, 32.5, 0.5):
            yc = y0 + (x - 22.5) * 0.42 - ((x - 27) / 5) ** 2 * 1.2
            xi, yi = int(x), int(yc)
            if 0 <= yi < t.h - 1 and peito[yi, xi] and peito[yi + 1, xi]:
                t.px[yi + 1, xi] = IDX["sombra_media"]
                if x < 30:
                    t.px[yi, xi] = IDX["cinza_luz"] if x < 27.5 else IDX["cinza"]
    # Vértebras saltadas nas costas.
    for k in range(5):
        vx, vy = 21.2 + k * 0.35, 19 + k * 2.4
        vm = t.elipse(vx, vy, 1.2, 1.0)
        relevo(t, vm, domo(t, vx, vy, 1.2, 1.0) * 2, PELE_O, ambiente=0.2, brilho=1.0)
    # Boca vertical na barriga, entreaberta, com dentes e baba.
    bx, by = 28, 31
    t.chapado(t.elipse(bx, by, 1.4, 3.0), "vermelho_esc")
    t.chapado(t.elipse(bx, by, 0.7, 2.3), "preto")
    for k in range(4):
        t.ponto(bx - 1, by - 2 + k * 1.3, "cinza_claro")
        t.ponto(bx + 1, by - 1.5 + k * 1.3, "branco")
    t.linha(bx, by + 3, bx + 0.5, by + 6, "alien_luz")
    t.ponto(bx + 0.5, by + 7, "alien_brilho")

    # Pescoço comprido em S, com anéis de cartilagem, até o olho.
    for a, b in zip(pesc, pesc[1:]):
        m = t.capsula(a[0], a[1], b[0], b[1], 2.1, 1.8)
        relevo(t, m, suave(m, 0.8) * 3, PELE_O, ambiente=0.18, brilho=0.7, dither=False)
    for (a, b) in zip(pesc[:2], pesc[1:3]):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        t.linha(mx - dy / L * 1.6, my + dx / L * 1.6, mx + dy / L * 1.6, my - dx / L * 1.6, "azul_sombra")
    t.linha(pesc[0][0], pesc[0][1] - 2, pesc[1][0], pesc[1][1] - 1.8, "cinza_luz")

    # Braço da frente esticado, garras de quatro juntas abertas.
    osso(braco_f, 1.7, 1.1, amb=0.18)
    hx, hy = mao
    for (a1, b1, a2, b2) in garras:
        x1, y1, x2, y2 = hx + a1, hy + b1, hx + a2, hy + b2
        osso([(hx, hy), (x1, y1), (x2, y2)], 0.7, 0.45, amb=0.2, br=0.8)
        t.ponto(x2 + (x2 - x1) * 0.3, y2 + (y2 - y1) * 0.3, "cinza_claro")
    osso([(hx, hy), (hx + dedao[0], hy + dedao[1]), (hx + dedao[2], hy + dedao[3])], 0.65, 0.45, amb=0.2)

    # Olho gigante na ponta do pescoço: órbita de carne, esclera com veias, íris verde.
    r = 7.5
    orb = t.elipse(ex - 0.5, ey + 0.3, r + 1.6, r + 1.4)
    relevo(t, orb, domo(t, ex - 0.5, ey + 0.3, r + 1.6, r + 1.4) * 3, JUNTA, ambiente=0.0, brilho=0.6)
    bola = t.elipse(ex, ey, r, r)
    relevo(t, bola, domo(t, ex, ey, r, r) * 5,
           ["cinza", "cinza_luz", "cinza_claro", "branco", "branco"], ambiente=0.25, brilho=1.0, linha=False)
    rng = np.random.default_rng(12)
    for k in range(9):
        a = rng.uniform(0, 2 * math.pi)
        x, y = ex + math.cos(a) * (r - 0.3), ey + math.sin(a) * (r - 0.3)
        cor = "vermelho_medio" if k % 3 else "vermelho"
        for _ in range(int(r * 0.55)):
            x += (ex - x) * 0.14 + rng.uniform(-0.7, 0.7)
            y += (ey - y) * 0.14 + rng.uniform(-0.7, 0.7)
            xi, yi = int(x), int(y)
            if 0 <= xi < t.w and 0 <= yi < t.h and bola[yi, xi]:
                t.px[yi, xi] = IDX[cor]
    ix, iy = ex + 2.8, ey + 0.8
    iris = t.elipse(ix, iy, 4.0, 4.2) & bola
    if pose == "morte":
        rampa_i = ["cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "cinza_claro"]
    elif mirando:
        rampa_i = ["alien_medio", "alien", "alien_luz", "alien_brilho", "amarelo_claro"]
    else:
        rampa_i = ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz"]
    relevo(t, iris, domo(t, ix, iy, 4.0, 4.2) * 2, rampa_i, ambiente=0.0, linha=False)
    # Raios da íris.
    for k in range(10):
        a = k * math.pi / 5
        t.ponto(ix + math.cos(a) * 3, iy + math.sin(a) * 3.2, "alien_profundo")
    pup = {"grito": (0.6, 0.9), "atira": (0.5, 1.4), "mira": (0.8, 2.0), "morte": (1.6, 1.6)}.get(pose, (1.1, 2.6))
    t.chapado(t.elipse(ix + 0.3, iy, pup[0], pup[1]) & bola, "preto" if pose != "morte" else "cinza_escuro")
    if pose == "atira":
        t.chapado(t.elipse(ix + 0.3, iy, 2.2, 2.4) & bola & (t.px != IDX["preto"]), "branco")
    t.ponto(ix - 1.8, iy - 2, "branco")
    t.ponto(ix - 1.2, iy - 2, "branco")
    t.ponto(ix - 1.8, iy - 1.3, "branco")
    # Pálpebras de carne: a de cima pesada (fecha mais no quadro 1), a de baixo inchada.
    pal = t.elipse(ex - 0.5, ey - r * (1 - 2 * fecha) - r, r + 1.7, r + 0.4) & orb
    relevo(t, pal, suave(pal, 0.8) * 3, JUNTA, ambiente=0.1, brilho=1.0)
    borda = pal & ~ndimage.binary_erosion(pal) & bola
    t.px[borda] = IDX["roxo_escuro"]
    inf = t.elipse(ex, ey + r + 1.6, r + 1.2, 3.3) & orb
    relevo(t, inf, suave(inf, 0.7) * 2.5, JUNTA, ambiente=0.0, brilho=0.8)
    # Cílios duros espetados.
    for k in range(5):
        cx_ = ex - 5 + k * 2.6
        cy_ = ey - r * (1 - 2 * fecha) - 0.8 - math.sin(k / 4 * math.pi) * 1.2
        t.linha(cx_, cy_, cx_ + 0.6, cy_ - 2.2, "sombra")
    if pose == "mira":
        # Brilho em volta do olho avisando o raio.
        aro = t.elipse(ex - 0.5, ey + 0.3, r + 2.6, r + 2.4) & ~t.elipse(ex - 0.5, ey + 0.3, r + 1.7, r + 1.5)
        t.px[aro & (np.sin((t.xx + t.yy) * 1.3) > 0.2)] = IDX["alien_brilho"]
    if pose == "morte":
        # Olho estourando: rachaduras e gosma escorrendo.
        for (a, b, c, d) in ((ex - 2, ey - 3, ex + 1, ey + 1), (ex + 1, ey + 1, ex - 1, ey + 5), (ex + 1, ey + 1, ex + 5, ey)):
            t.linha(a, b, c, d, "vermelho_esc")
        for gx in (ex - 3, ex + 2, ex + 5):
            t.linha(gx, ey + 5, gx, ey + 10, "alien_luz")
            t.ponto(gx, ey + 11, "alien_brilho")
    # Lágrima de gosma.
    t.linha(ex + r - 1, ey + 4, ex + r - 0.5, ey + 7, "alien_luz")
    t.ponto(ex + r - 0.5, ey + 8, "alien_brilho")

    t.contorno("sombra")
    return t


def previa(ims, saida, escala=4):
    from PIL import Image
    W = sum(i.width for i in ims) + 10 * (len(ims) + 1)
    H = max(i.height for i in ims) + 10
    o = Image.new("RGBA", (W, H), (176, 142, 102, 255))
    x = 10
    for i in ims:
        o.alpha_composite(i, (x, H - 4 - i.height))
        x += i.width + 10
    o.resize((W * escala, H * escala), Image.NEAREST).save(saida)
    return saida


if __name__ == "__main__":
    from PIL import Image
    lamp = Image.open(RAIZ / "assets/sprites/lampiao.png").crop((0, 0, 60, 72))
    lamp = lamp.crop(lamp.getbbox())
    saida = sys.argv[1] if len(sys.argv) > 1 else RAIZ / "tools/arte/pixel/aliens_previa.png"
    print(previa([lamp, cerebrao().imagem(), olheiro().imagem(), olheiro(fase=1.0).imagem()], saida))
