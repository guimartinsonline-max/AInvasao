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


def cerebrao(fase=0.0):
    """Cerebrão: cérebro exposto enorme, cara de três olhos com mandíbulas,
    corpo de lesma babando, bracinhos com a pistola de raio. Olha para a direita."""
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
    rabo = t.capsula(4, chao - 3, 29, chao - 7, 3, 8.5)
    tronco = t.capsula(30, chao - 8, 37, 30, 8.5, 7)
    saia = t.elipse(22, chao - 2, 20, 3.5) & (yy < chao)
    corpo = (rabo | tronco | saia) & (yy < chao + 0.5)
    H = suave(corpo, 2.6) * 6
    s_ = xx * 0.9 - yy * 0.45
    H = H + np.clip(np.sin(s_ * 1.05 + fase * 0.6), -0.2, 1) * 1.1 * suave(corpo, 1.5)
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
    dobra = corpo & (np.sin(s_ * 1.05 + fase * 0.6) < -0.8) & (suave(corpo, 1.5) > 0.6)
    t.px[dobra] = IDX["alien_profundo"]
    # Pé ondulado embaixo.
    pe = saia & (yy > chao - 2.5) & corpo
    t.chapado(pe, "alien_esc")
    t.chapado(pe & (np.sin(xx * 1.4 + fase) > 0.3) & (yy > chao - 1.5), "alien_medio")
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
    for pts in (((43, 31.5), (47.5, 33), (48, 37.5)), ((38.5, 32), (39.5, 36.5), (44, 38))):
        for a, b in zip(pts, pts[1:]):
            parte(t.capsula(a[0], a[1], b[0], b[1], 1.5, 0.55), ["sombra", "cinza_escuro", "cinza", "cinza_luz", "cinza_claro", "branco"], s=0.6, alt=2.5, amb=0.1, br=1.6)
    # Boca redonda com dentinhos e baba.
    t.chapado(t.elipse(43.5, 32.8, 2.1, 1.5), "preto")
    t.chapado(t.elipse(43.5, 33.2, 1.2, 0.7), "vermelho_esc")
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
        t.chapado(t.elipse(ix, y + 0.2, r * 0.65, r * 0.72) & bola, "amarelo_fogo")
        t.chapado(t.elipse(ix + 0.15, y + 0.2, max(r * 0.22, 0.5), r * 0.6) & bola, "preto")
        t.ponto(x - r * 0.4, y - r * 0.4, "branco")
        pal = t.elipse(x, y - r * 0.75, r + 1.0, r * 0.5) & orb
        relevo(t, pal, suave(pal, 0.5) * 2, CARNE, ambiente=0.15, linha=False)
    olho(42, 28.2, 2.6)
    olho(37, 29, 1.7)
    olho(46.3, 28.8, 1.6)

    # Cérebro enorme por cima, inclinado para a frente.
    cerebro(t, 29, 12.5 - fase * 0.4, 16 + fase * 0.7, 11 + fase * 0.6, fase=fase)
    # Gota de líquido escorrendo de baixo do cérebro.
    t.linha(21, 21, 21, 24 + int(fase * 2), "rosa_poeira")
    t.ponto(21, 25 + int(fase * 2), "pele_brilho")

    # Braço da frente estendido com a pistola de raio.
    braco([(38, 37), (43, 42), (48, 40)], 1.5)
    corpo_p = t.capsula(47, 39, 54, 39, 2.3, 1.7)
    parte(corpo_p, METAL, s=0.7, alt=3, amb=0.1, br=1.5)
    for x in (50, 52):
        t.linha(x, 37, x, 41, "cinza_escuro")
    bulbo = t.elipse(49.5, 36.3, 2.4, 2.0)
    relevo(t, bulbo, domo(t, 49.5, 36.3, 2.4, 2.0) * 3, VIDRO, ambiente=0.3, brilho=2.0)
    t.ponto(49, 36, "alien_brilho")
    cano = t.retangulo(54, 38, 4, 2)
    parte(cano, METAL, s=0.5, alt=2, amb=0.2)
    t.ponto(58, 38, "alien_brilho")
    t.ponto(58, 39, "alien")
    parte(t.capsula(48, 40, 47, 43.5, 1.1), QUITINA, s=0.5, alt=2)
    for k in range(3):
        parte(t.capsula(47.5, 40 + k, 49.5, 41 + k * 1.1, 0.6), LESMA, s=0.5, alt=2, amb=0.05)

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
    print(previa([lamp, cerebrao().imagem(), cerebrao(fase=1.0).imagem()], saida))
