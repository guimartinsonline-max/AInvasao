"""Peças do acampamento da base no nível de detalhe do Metal Slug (estudo: MS2 missão 3,
MS6 missão 2 com o acampamento de torres e paliçada).

O que o Metal Slug faz e as peças daqui seguem:
- cada material tem a própria rampa de 5 a 7 tons (madeira, lona, corda, ferro, terra),
  com luz de cima à esquerda calculada pela forma (cilindro, plano caído, dobra);
- textura em tudo: veio e rachadura na madeira, casca, nó; costura, remendo, mancha d'água,
  dobra puxada pela corda e barra suja de barro na lona; farpa e brilho no arame;
- contato com o chão escurecido, sombra projetada e pequenos objetos de apoio
  (estaca, corda com esticador, saco de areia, caixote, garrafão);
- letreiro grande e pintado à mão, com sombra, que dá para ler (fonte 5x7).

As cores de crepúsculo (mad_n*, lona_n*, lona_q*, oliva_n*, chao_n*, corda_n*) já são da
hora do acampamento: as peças daqui não passam pelo anoitecer() por troca de cor.
"""
import math

import numpy as np
from scipy import ndimage

from motor import IDX, VAZIO, Tela
from fase2 import ruido, pintar_niveis

MAD = ["mad_n1", "mad_n2", "mad_n3", "mad_n4", "mad_n5", "mad_n6"]
LONA = ["lona_n1", "lona_n2", "lona_n3", "lona_n4", "lona_n5", "lona_n6"]
QUENTE = ["mad_n3", "lona_q1", "lona_q2", "lona_q3", "lona_q4"]
OLIVA = ["mad_n1", "oliva_n1", "oliva_n2", "oliva_n3", "oliva_n4", "oliva_n5"]
CORDA = ["mad_n2", "corda_n1", "corda_n2", "corda_n3"]
FERRO = ["preto", "sombra", "sombra_media", "cinza_escuro", "cinza_medio", "cinza_luz"]
CHAO = ["chao_n1", "chao_n2", "chao_n3", "chao_n4", "chao_n5", "chao_n6"]
VERMELHO = ["mad_n1", "vermelho_esc", "vermelho_medio", "vermelho"]
LUZ = np.array([-0.62, -0.55, 0.56])
LUZ = LUZ / np.linalg.norm(LUZ)


NOITE = 0.0  # escurece tudo que for pintado (negativo clareia): a hora do ponto do trecho
CONTRASTE = 1.0  # menor que 1 nas camadas de fundo (perspectiva aérea: tons mais juntos)


def pintar(t, m, v, rampa):
    v = 0.5 + (np.broadcast_to(np.asarray(v, float), m.shape) - 0.5) * CONTRASTE - NOITE
    pintar_niveis(t, m, v, rampa)


# ------------------------------------------------------------------ fonte de letreiro
FONTE5 = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00000", "00100"],
    "0": ["01110", "10011", "10101", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    " ": ["00000"] * 7,
}
ACENTOS = {"Ó": ("O", "agudo"), "Á": ("A", "agudo"), "É": ("E", "agudo"), "Í": ("I", "agudo"),
           "Ã": ("A", "til"), "Õ": ("O", "til"), "Ç": ("C", "cedilha")}


def largura_texto(texto, esp=1):
    return len(texto) * (5 + esp) - esp


def letreiro(t, texto, x, y, cor, sombra="mad_n1", esp=1, gasto=0.0, semente=0):
    """Escreve em letras 5x7 pintadas à mão, com sombra embaixo à direita. Os acentos
    ficam nas 2 linhas acima (y-2). gasto: fração da tinta descascada."""
    rng = np.random.default_rng(semente)
    pts = []
    cx = x
    for ch in texto:
        base, ac = ACENTOS.get(ch, (ch, None))
        g = FONTE5.get(base, FONTE5[" "])
        for j, l in enumerate(g):
            for i, b in enumerate(l):
                if b == "1":
                    pts.append((cx + i, y + j))
        if ac == "agudo":
            pts += [(cx + 2, y - 1), (cx + 3, y - 2)]
        elif ac == "til":
            pts += [(cx + 1, y - 1), (cx + 2, y - 2), (cx + 3, y - 1), (cx + 4, y - 2)]
        elif ac == "cedilha":
            pts += [(cx + 2, y + 7), (cx + 1, y + 8)]
        cx += 5 + esp
    if sombra:
        for (px, py) in pts:
            t.ponto(px + 1, py + 1, sombra)
    for (px, py) in pts:
        if gasto and rng.random() < gasto:
            continue
        t.ponto(px, py, cor)


# ------------------------------------------------------------------ madeira roliça
def cilindro(t, x0, y0, x1, y1, r0, r1=None, rampa=MAD, semente=0, casca=True, rachas=2, nos=1,
             topo_cortado=False, escurecer=0.0):
    """Tora/mourão roliço de (x0,y0) a (x1,y1): luz de cilindro, veio e casca ao longo do
    eixo, rachaduras, nós e, se pedido, o topo cortado com os anéis."""
    r1 = r0 if r1 is None else r1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) + 1e-9
    ax, ay = dx / L, dy / L
    nx, ny = -ay, ax  # perpendicular
    px, py = t.xx - x0, t.yy - y0
    s = px * ax + py * ay
    d = px * nx + py * ny
    r = r0 + (r1 - r0) * np.clip(s / L, 0, 1)
    m = (s >= -0.5) & (s <= L + 0.5) & (np.abs(d) <= r)
    if not m.any():
        return m
    u = np.clip(d / np.maximum(r, 0.5), -1, 1)
    # Normal do cilindro: lateral (u na direção perpendicular) + frente.
    nz = np.sqrt(np.clip(1 - u * u, 0, 1))
    lum = (u * nx * LUZ[0] + u * ny * LUZ[1] + nz * LUZ[2])
    v = 0.12 + np.clip(lum, 0, 1) * 0.78
    # Veio: listras finas ao longo do eixo, quebradas.
    rng = np.random.default_rng(semente)
    ncol = 9
    G = ndimage.gaussian_filter(rng.standard_normal((int(L) + 3, ncol)), (2.5, 0.6))
    G /= G.std() + 1e-9
    si = np.clip(s, 0, L + 1).astype(int)
    ui = np.clip(((u + 1) / 2 * (ncol - 1)).round(), 0, ncol - 1).astype(int)
    v = v + G[si, ui] * (0.09 if casca else 0.05) - escurecer
    pintar(t, m, v, rampa)
    # Rachaduras escuras compridas ao longo do eixo.
    for _ in range(rachas):
        uu = rng.uniform(-0.5, 0.4)
        a = rng.uniform(0.05, 0.5) * L
        b = a + rng.uniform(0.25, 0.5) * L
        for ss in np.arange(a, min(b, L), 0.7):
            rr = r0 + (r1 - r0) * ss / L
            w = uu + math.sin(ss / 5 + uu * 9) * 0.12
            qx, qy = x0 + ax * ss + nx * w * rr, y0 + ay * ss + ny * w * rr
            t.ponto(qx, qy, rampa[0])
            if rng.random() < 0.5:
                t.ponto(qx - nx * 0.9 * np.sign(LUZ[0] * nx + 1e-9), qy, rampa[min(3, len(rampa) - 1)])
    # Nós: olho escuro com borda clara.
    for _ in range(nos):
        ss = rng.uniform(0.2, 0.85) * L
        uu = rng.uniform(-0.3, 0.3)
        rr = r0 + (r1 - r0) * ss / L
        qx, qy = x0 + ax * ss + nx * uu * rr, y0 + ay * ss + ny * uu * rr
        e = t.elipse(qx, qy, max(1.0, rr * 0.45), max(1.0, rr * 0.35)) & m
        t.px[e] = IDX[rampa[1]]
        t.ponto(qx, qy, rampa[0])
        t.ponto(qx - 1, qy - 1, rampa[-2])
    if topo_cortado:
        cx_, cy_ = x1, y1
        e = t.elipse(cx_, cy_, r1 + 0.2, max(1.0, r1 * 0.45))
        t.px[e] = IDX[rampa[-1]]
        t.px[t.elipse(cx_, cy_, r1 * 0.55, max(0.6, r1 * 0.25))] = IDX[rampa[-2]]
        t.ponto(cx_, cy_, rampa[2])
    return m


def corda(t, x0, y0, x1, y1, flecha=1.0, rampa=CORDA, torcida=True):
    """Corda de sisal: 1 px com a torção marcada (claro/escuro alternando) e caimento."""
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 1.3) + 2
    pts = []
    for k in range(n + 1):
        f = k / n
        x = x0 + (x1 - x0) * f
        y = y0 + (y1 - y0) * f + math.sin(f * math.pi) * flecha
        pts.append((x, y))
    for k, (x, y) in enumerate(pts):
        cor = rampa[2] if (not torcida or (k // 2) % 2 == 0) else rampa[1]
        t.ponto(x, y, cor)
    for k, (x, y) in enumerate(pts[::3]):
        t.ponto(x, y - 1, rampa[3]) if torcida and k % 3 == 0 else None
    return pts


def amarracao(t, x, y, r=2.0):
    """Voltas de corda amarrando duas peças, com as pontas soltas."""
    for k in range(-1, 2):
        yy = y + k * 1.4
        for xx in np.arange(x - r - 0.5, x + r + 1, 0.5):
            f = (xx - (x - r)) / (2 * r)
            t.ponto(xx, yy + f * 1.2, CORDA[2] if f < 0.6 else CORDA[1])
        t.ponto(x - r - 0.5, yy, CORDA[0])
    t.ponto(x + r + 1, y + 2.5, CORDA[2])
    t.ponto(x + r + 1.5, y + 3.8, CORDA[1])


def estaca(t, x, chao, h=7, semente=0):
    """Estaca de madeira cravada no chão (com a cabeça amassada de marreta)."""
    cilindro(t, x, chao, x - 0.6, chao - h, 1.4, 1.1, semente=semente, rachas=0, nos=0, topo_cortado=True)
    t.ponto(x - 2, chao, "chao_n1")
    t.ponto(x + 2, chao, "chao_n1")


def esticador(t, pts, f=0.55):
    """Esticador de madeira (taquinho com dois furos) na corda."""
    x, y = pts[int(len(pts) * f)]
    t.chapado(t.retangulo(x - 1.5, y - 1, 4, 2.5), MAD[3])
    t.ponto(x - 1, y - 1, MAD[5])
    t.ponto(x + 2, y + 1, MAD[1])


# ------------------------------------------------------------------ objetos de apoio
def garrafao(t, x, chao, semente=0):
    """Garrafão de vidro num cesto de vime (reagente do laboratório), líquido verde."""
    corpo = t.elipse(x, chao - 7, 5.5, 6.5)
    v = 0.55 - (t.xx - x) / 12 - (t.yy - (chao - 7)) / 18
    pintar(t, corpo, v, ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz"])
    t.chapado(t.retangulo(x - 1.5, chao - 17, 3, 4), "cinza_luz")
    t.ponto(x - 1, chao - 17, "branco")
    t.chapado(t.retangulo(x - 2, chao - 18, 4, 1.2), "mad_n3")
    # Cesto de vime trançado na metade de baixo.
    cesto = corpo & (t.yy > chao - 8)
    vv = 0.5 + ((t.xx.astype(int) + t.yy.astype(int)) % 3 == 0) * 0.25 - (t.xx - x) / 14
    pintar(t, cesto, vv, MAD)
    t.ponto(x - 3, chao - 11, "branco")
    t.ponto(x - 3, chao - 10, "alien_luz")


def caixote(t, x, chao, w=20, h=14, texto="", semente=0, rampa=MAD):
    """Caixote de tábuas com face de cima em perspectiva, tábuas, pregos e estêncil."""
    topo_h = 3
    frente = t.retangulo(x, chao - h, w, h)
    rng = np.random.default_rng(semente)
    v = 0.48 + ruido(t.h, t.w, (0.5, 3), semente) * 0.07
    for k in range(1, 3):
        v = np.where(np.abs(t.yy - (chao - h + k * h / 3)) < 0.6, 0.18, v)
    v = np.where((t.xx < x + 1.2) | (t.xx > x + w - 1.2), 0.62, v)
    pintar(t, frente, v, rampa)
    t.px[frente & (t.xx > x + w - 1.2)] = IDX[rampa[1]]
    tampa = t.poligono([(x, chao - h), (x + 2, chao - h - topo_h), (x + w + 2, chao - h - topo_h), (x + w, chao - h)])
    pintar(t, tampa & ~frente, 0.8 + ruido(t.h, t.w, (0.4, 3), semente + 1) * 0.06, rampa)
    for (px, py) in ((x + 1, chao - h + 1), (x + w - 2, chao - h + 1), (x + 1, chao - 2), (x + w - 2, chao - 2)):
        t.ponto(px, py, "cinza_luz")
    if texto:
        lx = x + w / 2 - largura_texto(texto) / 2
        letreiro(t, texto, int(lx), int(chao - h + (h - 7) / 2 + 1), "corda_n3", sombra="mad_n1", gasto=0.04,
                 semente=semente)
    # Contorno escuro na silhueta.
    m = frente | tampa
    borda = ndimage.binary_dilation(m) & ~m & (t.px == VAZIO)
    t.px[borda] = IDX["mad_n1"]
    _ = rng


def saco(t, x, chao, w=16, h=8, semente=0):
    """Saco de areia estufado com costura e orelha amarrada."""
    m = t.elipse(x + w / 2, chao - h / 2, w / 2, h / 2)
    m |= t.retangulo(x + 2, chao - h + 1, w - 4, h - 1)
    v = 0.6 - (t.yy - (chao - h)) / h * 0.4 - (t.xx - x) / w * 0.18 + ruido(t.h, t.w, 0.8, semente) * 0.05
    pintar(t, m, v, ["corda_n1", "chao_n5", "corda_n2", "chao_n6", "corda_n3"])
    for xx in range(int(x + 3), int(x + w - 3), 2):
        t.ponto(xx, chao - h + 2, "corda_n1")
    t.ponto(x + w - 1, chao - h / 2 - 1, "corda_n3")
    t.ponto(x + w, chao - h / 2 - 2, "corda_n2")
    borda = ndimage.binary_dilation(m) & ~m & (t.px == VAZIO)
    t.px[borda] = IDX["mad_n1"]


def lampiao(t, x, y, aceso=True):
    """Lampião de querosene de lata pendurado: alça, chaminé de vidro com a chama."""
    t.linha(x - 2, y - 3, x, y - 5, "cinza_escuro")
    t.linha(x + 2, y - 3, x, y - 5, "cinza_escuro")
    t.chapado(t.retangulo(x - 2.5, y - 3, 5, 1.5), "cinza_medio")
    vidro = t.elipse(x, y + 0.5, 2.4, 3)
    t.chapado(vidro, "amarelo_claro" if aceso else "sombra_media")
    if aceso:
        t.chapado(t.elipse(x, y + 1, 0.9, 1.6), "branco")
    t.chapado(t.retangulo(x - 3, y + 3, 6, 2), "cinza_escuro")
    t.ponto(x - 2, y + 3, "cinza_luz")


# ------------------------------------------------------------------ barraca do laboratório
SUJA = ["mad_n1", "chao_n3", "chao_n4", "corda_n1", "corda_n2", "corda_n3"]
TIPOS_BARRACA = {
    "lab": {"rampa": LONA, "letreiro": "LABORATÓRIO"},
    "tropa": {"rampa": OLIVA, "letreiro": ""},
    "quarentena": {"rampa": SUJA, "letreiro": "QUARENTENA"},
}
PORTA_BARRACA = 123  # centro da porta, em x local (os soldados saem por ali)


def placa_madeira(t, txt, x, y, pendurada=True, rampa=MAD, cor="lona_n6"):
    """Tábua com o texto pintado (5x7 com sombra), pregos e, se pendurada, os dois arames."""
    w = largura_texto(txt) + 8
    h = 13
    p = Tela(w, h)
    m = p.retangulo(0, 0, w, h)
    v = 0.55 + ruido(h, w, (0.4, 3.5), len(txt)) * 0.08
    v = np.where(np.abs(p.yy - h / 2) < 0.5, 0.2, v)
    v = np.where(p.yy < 1.2, 0.85, v)
    v = np.where(p.yy > h - 1.2, 0.25, v)
    pintar(p, m, v, rampa)
    letreiro(p, txt, 4, 4, cor, sombra="mad_n1")
    for (a, b) in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
        p.ponto(a, b, "cinza_luz")
    p.contorno("mad_n1")
    t.colar(p, x, y)
    if pendurada:
        for k in (x + 5, x + w - 6):
            t.linha(k, y - 7, k, y, "cinza_escuro")
            t.ponto(k, y - 7, "cinza_luz")
    return w


def fuzis_ensarilhados(t, x, chao):
    """Três fuzis Mauser em pé, apoiados uns nos outros pela boca do cano (ensarilhados)."""
    topo = chao - 26
    for k, bx in enumerate((x - 7, x, x + 7)):
        cilindro(t, bx, chao - 1, x + (bx - x) * 0.05, topo, 1.3, 0.7, semente=k + 3, rachas=0, nos=0)
        t.linha(bx * 0.75 + x * 0.25, chao - 9, bx * 0.55 + x * 0.45, chao - 18, "cinza_escuro")
        t.ponto(bx * 0.6 + x * 0.4, chao - 15, "cinza_luz")
        t.chapado(t.retangulo(bx - 1.6, chao - 6, 3.2, 5), "mad_n4")
        t.ponto(bx - 1, chao - 6, "mad_n6")
    t.linha(x - 1, topo, x + 1, topo, "cinza_luz")


def balde(t, x, chao):
    m = t.poligono([(x - 4, chao - 8), (x + 4, chao - 8), (x + 3, chao), (x - 3, chao)])
    pintar(t, m, 0.75 - (t.xx - x + 4) / 10, FERRO)
    t.linha(x - 4, chao - 8, x + 4, chao - 8, "cinza_luz")
    for k in range(9):
        a = math.pi * k / 8
        t.ponto(x - math.cos(a) * 4, chao - 9 - math.sin(a) * 4, "cinza_escuro")


def tambor_caveira(t, x, chao):
    """Tambor de lata com caveira pintada e gosma escorrendo da tampa."""
    m = t.retangulo(x - 6, chao - 16, 12, 16)
    v = 0.3 + np.clip(1 - np.abs((t.xx - x + 2) / 6), 0, 1) * 0.6
    for yy in (chao - 12, chao - 5):
        v = np.where(np.abs(t.yy - yy) < 0.6, v + 0.25, v)
    pintar(t, m, v, ["mad_n1", "oliva_n1", "oliva_n2", "oliva_n3", "oliva_n4", "oliva_n5"])
    t.chapado(t.elipse(x, chao - 16, 6, 1.4), "oliva_n4")
    t.chapado(t.elipse(x, chao - 9, 2.4, 2), "lona_n5")
    t.ponto(x - 1, chao - 9, "mad_n1")
    t.ponto(x + 1, chao - 9, "mad_n1")
    t.linha(x - 2, chao - 6, x + 2, chao - 6, "lona_n4")
    t.linha(x - 3, chao - 4, x + 3, chao - 8, "lona_n4")
    t.linha(x - 3, chao - 8, x + 3, chao - 4, "lona_n4")
    for k, d in ((-3, 5), (2, 8), (4, 3)):
        t.linha(x + k, chao - 16, x + k, chao - 16 + d, "alien_medio")
        t.ponto(x + k, chao - 16 + d, "alien_luz")


def barraca(tipo="lab", semente=0, dentro_luz=True):
    """Barraca grande de lona da base (196x108). tipo: lab (lona clara, cruz vermelha,
    laboratório aceso dentro), tropa (lona oliva com VOLANTE em estêncil, catres, fuzis e
    chaminé de lata), quarentena (lona encardida, caveira pintada, fita listrada na porta,
    maca com um corpo coberto e brilho verde).
    Teto com caimento entre os paus, vincos, costura, remendo, manchas d'água, sanefa
    recortada; parede com dobras puxadas pelas estacas e barra de barro; cordas com
    esticadores até as estacas. Porta centrada em x=123."""
    cfg = TIPOS_BARRACA[tipo]
    LN = cfg["rampa"]
    W, H = 196, 108
    t = Tela(W, H)
    rng = np.random.default_rng(semente)
    chao = H - 1
    xa, xb = 30, 166
    beiral = 54
    cume = 13
    ra, rb = 46, 150
    paus = (ra, (ra + rb) / 2, rb)
    porta = (110, 136)
    yy, xx = t.yy, t.xx
    borda_e = (xa - 6) + (ra - (xa - 6)) * (beiral - yy) / (beiral - cume)
    borda_d = (xb + 6) + (rb - (xb + 6)) * (beiral - yy) / (beiral - cume)

    def caida(x, pontos, amp):
        x = np.asarray(x, float)
        out = np.zeros_like(x)
        for a, b in zip(pontos[:-1], pontos[1:]):
            sel = (x >= a) & (x <= b)
            out[sel] = np.sin((x[sel] - a) / (b - a) * math.pi) * amp
        return out
    cordas_beiral = (xa - 6, 72, 104, 142, xb + 6)
    cume_y = cume + caida(xx, paus, 2.2)
    beiral_y = beiral + caida(xx, cordas_beiral, 1.6)
    teto = (yy >= cume_y) & (yy <= beiral_y) & (xx >= borda_e) & (xx <= borda_d)
    prof = (yy - cume_y) / (beiral_y - cume_y + 1e-9)
    entre = np.zeros_like(xx)
    for a, b in zip(paus[:-1], paus[1:]):
        sel = (xx >= a) & (xx <= b)
        entre[sel] = np.sin((xx[sel] - a) / (b - a) * math.pi)
    v = 0.86 - prof * 0.3 - entre * np.sin(prof * math.pi) * 0.34 - (xx - W / 2) / W * 0.2
    for px_ in paus:
        v = v + np.clip(1 - np.abs(xx - px_) / 7, 0, 1) * (1 - prof) * 0.12
    v = np.where(yy < cume_y + 1.5, v + 0.1, v)
    rugas = np.zeros_like(xx, dtype=bool)
    for cxb in cordas_beiral[1:-1]:
        for alvo in (cxb - 14, cxb + 2, cxb + 15):
            comp = rng.uniform(0.22, 0.42)
            fase = rng.uniform(0, 6)
            for f in np.linspace(0, comp, 50):
                rx = cxb + (alvo - cxb) * f + math.sin(f * 14 + fase) * 1.1
                ry = beiral - (beiral - cume) * f
                ix, iy = int(round(rx)), int(round(ry))
                if 0 <= ix < W and 0 <= iy < H:
                    rugas[iy, ix] = True
    for px_ in paus:
        for alvo in (px_ - 26, px_ + 26):
            if not (xa - 6 <= alvo <= xb + 6):
                continue
            ax_, ay_ = alvo - px_, beiral - cume
            Lv = math.hypot(ax_, ay_)
            nxv, nyv = -ay_ / Lv, ax_ / Lv
            if nxv > 0:
                nxv, nyv = -nxv, -nyv
            sv = ((xx - px_) * ax_ + (yy - cume) * ay_) / Lv
            dv = (xx - px_) * nxv + (yy - cume) * nyv
            perto = (sv > 2) & (sv < Lv * 0.8)
            forca = np.clip(1 - sv / Lv, 0, 1) * 0.22
            v = np.where(perto & (dv > -2.2) & (dv <= 0), v + forca, v)
            v = np.where(perto & (dv > 0) & (dv < 2.5), v - forca * 1.1, v)
    v = np.where(rugas, v - 0.14, v)
    v = np.where(np.roll(rugas, 1, 1) & ~rugas, v + 0.08, v)
    cost_y = cume_y + (beiral_y - cume_y) * 0.52
    v = np.where(np.abs(yy - cost_y) < 0.5, v - 0.2, v)
    v = np.where(np.abs(yy - cost_y - 1) < 0.5, v + 0.1, v)
    v = v + ruido(H, W, (0.6, 2.5), semente) * 0.035
    for (mx, my, rx_, ry_) in ((126 + semente % 9, 44, 8, 3), (74 - semente % 7, 22, 5, 2.5)):
        e = ((xx - mx) / rx_) ** 2 + ((yy - my) / ry_) ** 2 + ruido(H, W, 1.2, mx) * 0.3
        v = np.where(e < 1, v - 0.06, v)
        v = np.where((e >= 1) & (e < 1.3), v - 0.12, v)
    if tipo == "quarentena":
        # Encardida: manchas grandes de mofo e gosma seca.
        v = v - (ruido(H, W, 3, semente + 70) > 0.9) * 0.12
    pintar(t, teto, v, LN)
    # Remendo costurado.
    rx0 = 54 if tipo != "tropa" else 128
    rem = t.retangulo(rx0, 36, 12, 9) & teto
    pintar(t, rem, 0.42 + ruido(H, W, 0.6, 9) * 0.04 - (yy - 36) / 40, LN)
    for k in range(0, 12, 2):
        t.ponto(rx0 + k, 35, LN[1])
        t.ponto(rx0 + k, 45, LN[1])
    for k in range(0, 9, 2):
        t.ponto(rx0 - 1, 36 + k, LN[1])
        t.ponto(rx0 + 12, 36 + k, LN[1])
    # Emblema pintado no teto (com a dobra passando por cima).
    cx, cy = 98, 33
    if tipo == "lab":
        circ = t.elipse(cx, cy, 11, 9) & teto
        pintar(t, circ & (ruido(H, W, 0.7, 31) > -1.3), v + 0.2, LN)
        cruz = (t.retangulo(cx - 2, cy - 7, 4, 14) | t.retangulo(cx - 7, cy - 2, 14, 4)) & teto
        pintar(t, cruz & (ruido(H, W, 0.6, 33) > -1.3), v * 0.9, VERMELHO)
    elif tipo == "tropa":
        tmp = Tela(W, H)
        letreiro(tmp, "VOLANTE", int(cx - largura_texto("VOLANTE") / 2), int(cy - 3), "lona_n5", sombra=None,
                 gasto=0.12, semente=semente)
        m = (tmp.px != VAZIO) & teto
        pintar(t, m, v * 0.55 + 0.42, ["oliva_n3", "corda_n2", "corda_n3", "lona_n5", "lona_n6"])
    else:
        # Caveira grande pintada a pincel.
        cav = (t.elipse(cx, cy - 2, 7, 6) | t.retangulo(cx - 4, cy + 2, 8, 5)) & teto
        pintar(t, cav & (ruido(H, W, 0.6, 35) > -1.4), v * 0.6 + 0.45, ["corda_n2", "lona_n4", "lona_n5", "lona_n6"])
        for ex in (cx - 3, cx + 3):
            t.chapado(t.elipse(ex, cy - 2, 1.8, 2), "mad_n1")
        t.ponto(cx, cy + 1, "mad_n1")
        for k in range(-3, 4, 2):
            t.linha(cx + k, cy + 3, cx + k, cy + 6, "mad_n2")
        for (a, b) in ((-12, -1), (12, 1)):
            t.linha(cx + a, cy + 8 - b * 3, cx - a, cy + 8 + b * 3, "lona_n5")
    # Sanefa e parede.
    sanefa = (yy > beiral_y) & (yy <= beiral_y + 5 + (np.sin(xx / 4.5 * math.pi) > 0) * 1.5) & \
             (xx >= xa - 6) & (xx <= xb + 6)
    hem = chao - 2 - caida(xx, np.arange(xa, xb + 1, 22.6), 1.4)
    parede = (xx >= xa) & (xx <= xb) & (yy > beiral_y) & (yy <= hem)
    dobras = np.sin(xx / 3.1 + ruido(1, W, 6, 5 + semente)[0][None, :] * 2) * np.clip((yy - beiral) / 46, 0, 1)
    vp = 0.62 + dobras * 0.13 - (xx - xa) / (xb - xa) * 0.16
    for px_ in np.arange(xa, xb + 1, 22.6):
        for k in range(1, 12):
            for sgn in (-1, 1):
                ix, iy = int(round(px_ + sgn * k * 0.7)), int(round(chao - 3 - k))
                if 0 <= ix < W:
                    vp[iy, ix] -= 0.12
    for cxs in (64, 98, 148):
        vp = np.where(np.abs(xx - cxs) < 0.5, vp - 0.2, vp)
        vp = np.where(np.abs(xx - cxs - 1) < 0.5, vp + 0.08, vp)
    vp = np.where(yy < beiral_y + 10, vp - 0.2, vp)
    vp = np.where(yy < beiral_y + 7.5, vp - 0.14, vp)
    barro = (yy > hem - 7 + ruido(H, W, (1, 3), 41) * 2.2)
    vp = vp + ruido(H, W, (0.6, 2), semente + 3) * 0.035
    pintar(t, parede, vp, LN)
    pintar(t, parede & barro, vp * 0.9 + 0.05, CHAO)
    for _ in range(26):
        sx, sy = rng.uniform(xa, xb), rng.uniform(chao - 16, chao - 8)
        t.ponto(sx, sy, "chao_n4" if rng.random() < 0.5 else "chao_n3")
    if tipo == "quarentena":
        # Gosma verde escorrendo da sanefa pela parede.
        for gx in (52, 88, 150):
            comp = int(rng.integers(8, 20))
            for d in range(comp):
                t.ponto(gx + math.sin(d / 3) * 0.6, beiral + 6 + d, "alien_esc" if d % 3 else "alien_medio")
            t.chapado(t.elipse(gx, beiral + 6 + comp, 1.2, 1.6), "alien_medio")
            t.ponto(gx - 0.5, beiral + 5 + comp, "alien_luz")
    vs = 0.86 - (yy - beiral_y) / 7 * 0.3 + np.sin(xx / 4.5 * math.pi) * 0.06
    vs = np.where(np.abs(yy - beiral_y - 0.5) < 0.6, 0.2, vs)
    pintar(t, sanefa, vs, LN)
    t.px[sanefa & ~np.roll(sanefa, -1, 0)] = IDX[LN[0]]
    # Janela.
    jx, jy, jw, jh = 42, 76, 20, 13
    if tipo == "quarentena":
        # Tábuas pregadas em X por cima da janela, e brilho verde vazando.
        t.chapado(t.retangulo(jx, jy, jw, jh), "alien_profundo")
        t.chapado(t.elipse(jx + jw / 2, jy + jh / 2, 6, 4), "alien_esc")
        for (a, b, c, d) in ((jx - 2, jy, jx + jw + 1, jy + jh - 1), (jx - 2, jy + jh - 1, jx + jw + 1, jy)):
            cilindro(t, a, b, c, d, 1.6, 1.6, semente=a + b, rachas=1, nos=0, casca=False)
        for (a, b) in ((jx - 1, jy), (jx + jw, jy), (jx - 1, jy + jh - 1), (jx + jw, jy + jh - 1)):
            t.ponto(a, b, "cinza_luz")
    else:
        luz = ["lona_q1", "lona_q2", "lona_q3"]
        t.chapado(t.retangulo(jx, jy, jw, jh), luz[0])
        t.chapado(t.retangulo(jx + 2, jy + 2, jw - 4, jh - 5), luz[1])
        t.chapado(t.elipse(jx + jw * 0.45, jy + jh * 0.45, 4, 3), luz[2])
        for k in range(jx, jx + jw, 2):
            t.linha(k, jy, k, jy + jh - 1, luz[0])
        if tipo == "lab":
            t.chapado(t.retangulo(jx + 12, jy + 3, 2, 8), "mad_n2")
            t.chapado(t.elipse(jx + 13, jy + 3, 2, 1.4), "mad_n2")
        else:
            # Vulto de soldado sentado de quepe lá dentro.
            t.chapado(t.elipse(jx + 8, jy + 5, 2.4, 2.6), "mad_n2")
            t.chapado(t.retangulo(jx + 5, jy + 2, 6, 1.6), "mad_n2")
            t.chapado(t.elipse(jx + 8, jy + 11, 4, 4), "mad_n2")
        for (a, b) in ((jx - 1, jx + jw),):
            t.linha(a, jy - 1, b, jy - 1, LN[1])
            t.linha(a, jy + jh, b, jy + jh, LN[1])
            t.linha(a, jy - 1, a, jy + jh, LN[1])
            t.linha(b, jy - 1, b, jy + jh, LN[1])
        rolo = t.capsula(jx - 1, jy - 3, jx + jw, jy - 3, 1.8)
        pintar(t, rolo, 0.75 - (yy - (jy - 4)) / 5, LN)
        for k in (jx + 3, jx + jw - 4):
            corda(t, k, jy - 5, k, jy - 1, 0)
    # Porta e o que se vê dentro.
    pa, pb = porta
    vao = (xx >= pa) & (xx <= pb) & (yy > beiral_y + 4) & (yy <= hem)
    dentro = 0.35 + (1 - np.hypot((xx - (pa + pb) / 2) / 16, (yy - (beiral + 14)) / 22)) * 0.55
    if tipo == "quarentena":
        pintar(t, vao, dentro, ["preto", "mad_n1", "alien_profundo", "alien_esc", "alien_medio"])
    else:
        pintar(t, vao, dentro * (1 if dentro_luz else 0.4), ["mad_n1", "mad_n2", "lona_q1", "lona_q2", "lona_q3"])
    if tipo == "lab":
        t.chapado(t.retangulo(pa + 2, beiral + 17, pb - pa - 4, 1.2), "mad_n2")
        for k, cor in enumerate(("alien_medio", "lona_q4", "alien", "vermelho_medio", "alien_luz")):
            bx = pa + 4 + k * 4.3
            t.chapado(t.retangulo(bx, beiral + 12 + (k % 2), 2.4, 5 - (k % 2)), cor)
            t.ponto(bx, beiral + 12 + (k % 2), "branco")
        vx_, vy_ = pb - 7, chao - 21
        t.chapado(t.retangulo(vx_ - 4, vy_ - 9, 8, 11), "alien_esc")
        t.chapado(t.retangulo(vx_ - 3, vy_ - 7, 6, 8), "alien_medio")
        t.chapado(t.elipse(vx_, vy_ - 3, 2.2, 2.2), "lona_n6")
        t.ponto(vx_ + 0.5, vy_ - 3, "preto")
        t.linha(vx_ - 1, vy_ - 1, vx_ - 2, vy_ + 1, "vermelho_medio")
        t.chapado(t.retangulo(vx_ - 4, vy_ - 10, 8, 1.4), "cinza_medio")
        t.linha(vx_ - 3, vy_ - 7, vx_ - 3, vy_, "alien_luz")
        t.chapado(t.retangulo(pa + 1, chao - 14, 17, 2), "mad_n4")
        t.linha(pa + 1, chao - 14, pa + 17, chao - 14, "mad_n5")
        t.chapado(t.retangulo(pa + 2, chao - 12, 2, 10), "mad_n2")
        t.chapado(t.retangulo(pa + 15, chao - 12, 2, 10), "mad_n2")
        t.chapado(t.elipse(pa + 6, chao - 17, 2, 2.4), "alien")
        t.chapado(t.retangulo(pa + 5.5, chao - 22, 1.2, 4), "cinza_luz")
        t.ponto(pa + 5, chao - 18, "alien_brilho")
        t.chapado(t.retangulo(pa + 9, chao - 19, 2, 5), "lona_q4")
        lampiao(t, pa + 14, chao - 19)
    elif tipo == "tropa":
        # Catre de lona, mochila e cantil pendurados, botas, lampião.
        t.chapado(t.retangulo(pa + 1, chao - 10, pb - pa - 2, 2.4), "oliva_n3")
        t.linha(pa + 1, chao - 10, pb - 1, chao - 10, "oliva_n4")
        for k in (pa + 2, pb - 3):
            t.linha(k, chao - 8, k + 1, chao - 2, "mad_n2")
        t.chapado(t.elipse(pa + 7, chao - 12, 4, 2), "lona_q2")  # cobertor
        t.chapado(t.retangulo(pa + 15, beiral + 13, 7, 9), "oliva_n2")
        t.linha(pa + 15, beiral + 13, pa + 21, beiral + 13, "oliva_n4")
        t.chapado(t.elipse(pa + 6, beiral + 16, 2.4, 3), "cinza_medio")
        t.ponto(pa + 5, beiral + 15, "cinza_luz")
        for k in (pa + 16, pa + 20):
            t.chapado(t.retangulo(k, chao - 5, 3, 4), "mad_n1")
            t.ponto(k, chao - 5, "mad_n3")
        lampiao(t, (pa + pb) / 2, beiral + 9)
    else:
        # Maca com um corpo coberto pelo lençol e a mão verde pendurada; gosma no chão.
        t.chapado(t.retangulo(pa + 1, chao - 12, pb - pa - 2, 2), "cinza_medio")
        for k in (pa + 2, pb - 3):
            t.linha(k, chao - 10, k, chao - 2, "cinza_escuro")
        corpo = t.elipse((pa + pb) / 2, chao - 15, 11, 4) | t.elipse(pa + 6, chao - 17, 4, 4)
        pintar(t, corpo & vao, 0.75 - (yy - (chao - 19)) / 9, ["alien_profundo", "lona_n3", "lona_n4", "lona_n5"])
        t.linha(pb - 6, chao - 11, pb - 5, chao - 6, "alien_medio")
        t.ponto(pb - 5, chao - 5, "alien_luz")
        t.chapado(t.elipse((pa + pb) / 2, chao - 2, 8, 1.2), "alien_medio")
        t.ponto((pa + pb) / 2 - 2, chao - 2, "alien_luz")
    # Abas e rolo da porta.
    for lado, x0_ in ((-1, pa), (1, pb)):
        aba = t.poligono([(x0_, beiral_y.min() + 6), (x0_ + lado * 9, beiral + 9), (x0_ + lado * 4, chao - 22),
                          (x0_, chao - 10)])
        va = 0.66 + np.sin((xx - x0_) * lado / 2.2) * 0.07 - (yy - beiral) / 120
        pintar(t, aba, va, LN)
        t.linha(x0_, beiral + 6, x0_, chao - 10, LN[0])
        t.ponto(x0_ + lado * 4, chao - 22, LN[1])
        corda(t, x0_ + lado * 2, beiral + 22, x0_ + lado * 8, beiral + 20, 0.6)
    rolo = t.capsula(pa - 2, beiral + 6, pb + 2, beiral + 6, 2.4)
    pintar(t, rolo, 0.78 - (yy - (beiral + 4)) / 6, LN)
    t.linha(pa - 1, beiral + 8, pb + 1, beiral + 8, LN[1])
    if tipo == "quarentena":
        # Fita listrada amarela e preta cruzando a porta em X, frouxa.
        for (a, b) in ((beiral + 12, chao - 8), (chao - 8, beiral + 12)):
            for k in range(int(pb - pa + 10)):
                f = k / (pb - pa + 10)
                x = pa - 5 + k
                y = a + (b - a) * f + math.sin(f * math.pi) * 3
                cor = "amarelo_fogo" if (k // 3) % 2 else "mad_n1"
                t.ponto(x, y, cor)
                t.ponto(x, y + 1, "ouro_escuro" if cor == "amarelo_fogo" else "mad_n1")
    # Paus.
    for px_ in (ra, rb):
        cilindro(t, px_, cume + 3, px_, cume - 6, 1.5, 1.2, semente=int(px_), rachas=0, nos=0)
        t.chapado(t.elipse(px_, cume - 7, 1.8, 1.4), "cinza_medio")
        t.ponto(px_ - 0.6, cume - 7.6, "cinza_luz")
    for px_ in porta:
        cilindro(t, px_, chao - 1, px_, beiral + 4, 1.3, 1.2, semente=int(px_) + 5, rachas=1, nos=0)
    if tipo == "tropa":
        # Chaminé de lata do fogareiro saindo do teto, com chapéu e fuligem.
        cx0 = 132
        cilindro(t, cx0, 34, cx0, 4, 2.0, 2.0, rampa=FERRO, semente=4, rachas=0, nos=0, casca=False)
        t.chapado(t.retangulo(cx0 - 4, 2, 8, 2), "cinza_medio")
        t.linha(cx0 - 4, 2, cx0 + 3, 2, "cinza_luz")
        for k in range(4, 30, 7):
            t.linha(cx0 - 2, k, cx0 + 2, k, "sombra")
        t.chapado(t.elipse(cx0, 36, 4, 1.6) & teto, LN[1])
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    # Cordas e estacas.
    for (x0_, y0_, x1_, y1_, fl) in ((xa - 6, beiral + 1, 6, chao, 2.0), (xb + 6, beiral + 1, W - 7, chao, 2.0),
                                     (72, beiral + 4, 64, chao, 0.5), (142, beiral + 4, 152, chao, 0.5)):
        pts = corda(t, x0_, y0_, x1_, y1_, fl)
        esticador(t, pts, 0.62)
        estaca(t, x1_, chao, semente=int(x1_))
    for px_ in np.arange(xa, xb + 1, 22.6):
        estaca(t, px_, chao, 5, semente=int(px_) + 1)
    if cfg["letreiro"]:
        rampa_p = MAD if tipo == "lab" else ["mad_n1", "vermelho_esc", "vermelho_esc", "vermelho_medio", "vermelho_medio"]
        placa_madeira(t, cfg["letreiro"], 34, beiral + 8, rampa=rampa_p,
                      cor="lona_n6" if tipo == "lab" else "amarelo_claro")
    # Coisas em volta.
    if tipo == "lab":
        saco(t, xa - 12, chao, 16, 8, semente=3)
        saco(t, xa - 4, chao, 15, 8, semente=4)
        saco(t, xa - 9, chao - 7, 15, 7, semente=5)
        garrafao(t, pb + 9, chao, semente=2)
        garrafao(t, pb + 19, chao, semente=3)
        caixote(t, 68, chao, 38, 15, "FRÁGIL", semente=6)
    elif tipo == "tropa":
        fuzis_ensarilhados(t, 92, chao)
        balde(t, 150, chao)
        caixote(t, 26, chao, 48, 13, "MUNIÇÃO", semente=7)
        caixote(t, 34, chao - 13, 22, 10, semente=8)
    else:
        tambor_caveira(t, 92, chao)
        tambor_caveira(t, 150, chao)
        saco(t, 36, chao, 16, 8, semente=9)
        saco(t, 50, chao, 15, 8, semente=10)
    return t


def barraca_lab(semente=0):
    return barraca("lab", semente)


# ------------------------------------------------------------------ cerca de arame farpado
def cerca(w, h=46, semente=0, placas=(("ÁREA MILITAR", 40),)):
    """Cerca da base: mourões de aroeira tortos e rachados com o topo cortado, escora em
    diagonal a cada tanto, quatro fios de arame farpado com caimento, farpas e brilho,
    latas de alarme penduradas, trapo preso no arame e placa pregada num mourão."""
    t = Tela(w, h + 2)
    chao = h + 1
    rng = np.random.default_rng(semente)
    xs = [6]
    while xs[-1] < w - 10:
        xs.append(xs[-1] + int(rng.integers(30, 40)))
    topos = {}
    for k, x in enumerate(xs):
        incl = rng.uniform(-1.6, 1.6)
        alt = h - rng.integers(0, 6)
        topos[x] = (x + incl, chao - alt)
        cilindro(t, x, chao, x + incl, chao - alt, 2.4, 1.9, semente=semente + k, rachas=2, nos=1,
                 topo_cortado=True)
        t.chapado(t.elipse(x, chao, 4, 1.2), "chao_n1")
        if k % 4 == 2:
            # Escora: tora mais fina em diagonal até o chão.
            cilindro(t, x + incl * 0.6, chao - alt * 0.55, x + 16, chao, 1.4, 1.6, semente=semente + 50 + k,
                     rachas=1, nos=0)
            amarracao(t, x + incl * 0.6, chao - alt * 0.55, 2.4)
    # Fios de arame farpado em quatro alturas.
    for j, hy in enumerate((0.2, 0.42, 0.64, 0.86)):
        for a, b in zip(xs[:-1], xs[1:]):
            ya = chao - (chao - topos[a][1]) * hy
            yb = chao - (chao - topos[b][1]) * hy
            n = b - a
            for k in range(n + 1):
                f = k / n
                x = a + k
                y = ya + (yb - ya) * f + math.sin(f * math.pi) * (1.4 + j * 0.2)
                t.ponto(x, y, "cinza_escuro")
                if k % 3 == 0:
                    t.ponto(x, y - 1, "cinza_luz") if k % 6 == 0 else None
                if k % 7 == 3:  # farpa (X pequeno)
                    t.ponto(x - 1, y - 1, "cinza_medio")
                    t.ponto(x + 1, y + 1, "sombra")
                    t.ponto(x + 1, y - 1, "cinza_medio")
                    t.ponto(x - 1, y + 1, "sombra")
            amarracao(t, a + topos[a][0] - a, ya, 1.2) if j == 3 else None
    # Latas de alarme penduradas no fio do meio.
    for a, b in zip(xs[:-1], xs[1:]):
        if rng.random() < 0.45:
            x = a + (b - a) * rng.uniform(0.3, 0.7)
            y = chao - (chao - topos[a][1]) * 0.64 + 1.6
            t.linha(x, y, x, y + 3, "cinza_escuro")
            lata = t.retangulo(x - 2, y + 3, 4, 5)
            pintar(t, lata, 0.6 - (t.xx - x) / 6, FERRO)
            t.ponto(x - 1, y + 3, "aco_brilho")
            t.ponto(x, y + 8, "mad_n1")
    # Trapo de farda preso no arame de cima.
    x = xs[min(2, len(xs) - 1)] + 14
    y = chao - (chao - topos[xs[min(2, len(xs) - 1)]][1]) * 0.86 + 1
    trapo = t.poligono([(x, y), (x + 6, y + 1), (x + 4, y + 5), (x + 6, y + 9), (x + 1, y + 6)])
    pintar(t, trapo, 0.55 - (t.yy - y) / 20, OLIVA)
    # Placas pregadas.
    for txt, xp in placas:
        k = int(np.argmin([abs(x - xp) for x in xs]))
        x0 = int(xs[k] - largura_texto(txt) / 2 - 4)
        pw = largura_texto(txt) + 8
        p = Tela(pw, 13)
        m = p.retangulo(0, 0, pw, 13)
        v = 0.52 + ruido(13, pw, (0.4, 3), 3) * 0.08
        v = np.where(p.yy < 1.2, 0.8, v)
        pintar(p, m, v, ["vermelho_esc", "vermelho_esc", "vermelho_medio", "vermelho_medio", "vermelho"])
        letreiro(p, txt, 4, 4, "lona_n6", sombra="mad_n1")
        p.ponto(2, 2, "cinza_luz")
        p.ponto(pw - 3, 2, "cinza_luz")
        p.contorno("mad_n1")
        t.colar(p, x0, int(chao - h * 0.62))
    return t


# ------------------------------------------------------------------ torre do holofote
def tabua(t, x, y, w, h, semente=0, rampa=MAD, vertical=False):
    """Tábua com veio, junta escura, ponta clara e prego."""
    m = t.retangulo(x, y, w, h)
    n = ruido(t.h, t.w, (0.4, 3.5) if not vertical else (3.5, 0.4), semente)
    v = 0.55 + n * 0.08
    if vertical:
        v = v + np.where(t.xx < x + 1, 0.22, 0) - np.where(t.xx > x + w - 1, 0.25, 0)
    else:
        v = v + np.where(t.yy < y + 1, 0.22, 0) - np.where(t.yy > y + h - 1, 0.25, 0)
    pintar(t, m, v, rampa)
    return m


def torre_holofote(altura=118, semente=0):
    """Torre de vigia de toras (64 x altura): quatro pernas abertas (as de trás mais
    escuras), travessas em X amarradas com corda, escada de toras do lado, plataforma
    de tábuas com as pontas aparecendo, parapeito de tábuas pregadas com sacos de areia,
    cabo elétrico com isoladores descendo pela perna e lampião pendurado. A plataforma
    fica de x 9 a 55, em y 14 (é sólida no jogo)."""
    W = 64
    t = Tela(W, altura)
    rng = np.random.default_rng(semente)
    base = altura - 1
    plat = 14
    # Pernas de trás (mais finas e escuras).
    for (xb_, xt_) in ((14, 18), (50, 46)):
        cilindro(t, xb_, base, xt_, plat, 1.8, 1.5, semente=semente + xb_, rachas=1, nos=1, escurecer=0.28)
    # Travessas em X entre as pernas de trás e da frente (atrás das pernas da frente).
    niveis = [plat + 6 + k * (base - plat - 10) / 4 for k in range(5)]
    def xe(y):
        f = (y - plat) / (base - plat)
        return 12 - 10 * f + 2, 52 + 10 * f - 2
    for y0, y1 in zip(niveis[:-1], niveis[1:]):
        a0, b0 = xe(y0)
        a1, b1 = xe(y1)
        cilindro(t, a0, y0, b1, y1, 1.1, 1.1, semente=int(y0), rachas=0, nos=0, escurecer=0.08)
        cilindro(t, b0, y0, a1, y1, 1.1, 1.1, semente=int(y0) + 1, rachas=0, nos=0, escurecer=0.14)
        cilindro(t, a1, y1, b1, y1, 1.2, 1.2, semente=int(y1) + 2, rachas=0, nos=0)
    # Pernas da frente.
    for (xb_, xt_) in ((3, 11), (61, 53)):
        cilindro(t, xb_, base, xt_, plat - 1, 2.5, 2.1, semente=semente + xb_ + 7, rachas=2, nos=1)
    for y in niveis[1:]:
        a, b = xe(y)
        amarracao(t, a - 1, y, 2.0)
        amarracao(t, b + 1, y, 2.0)
        cx_ = (a + b) / 2
        amarracao(t, cx_, (y + niveis[max(0, niveis.index(y) - 1)]) / 2, 1.6)
    # Plataforma: vigas e tábuas com as pontas aparecendo.
    cilindro(t, 4, plat + 5, 60, plat + 5, 2.0, 2.0, semente=semente + 30, rachas=1, nos=1)
    for k, x in enumerate(range(7, 57, 5)):
        tabua(t, x, plat, 5, 3, semente=semente + k, vertical=True)
    t.linha(7, plat, 56, plat, "mad_n6")
    # Parapeito: tábuas verticais pregadas numa travessa, uma quebrada.
    for k, x in enumerate(range(9, 55, 4)):
        topo = 4 + (2 if k == 6 else 0) + int(rng.integers(0, 2))
        tabua(t, x, topo, 4, plat - topo, semente=semente + 40 + k, vertical=True)
        t.ponto(x + 1, 7, "cinza_luz")
        t.ponto(x + 1, plat - 3, "cinza_luz")
    cilindro(t, 8, 7, 56, 7, 1.2, 1.2, semente=semente + 50, rachas=0, nos=0)
    # Sacos de areia no canto do parapeito.
    saco(t, 40, plat - 1, 13, 6, semente=semente + 3)
    saco(t, 46, plat - 6, 11, 5, semente=semente + 4)
    # Escada de toras do lado esquerdo, encostada.
    for (xb_, xt_) in ((-1, 5), (7, 12)):
        pass
    lx0, lx1 = 20, 30
    for x in (lx0, lx1):
        cilindro(t, x, base, x + 2, plat + 2, 1.3, 1.1, semente=semente + x + 60, rachas=0, nos=0)
    for y in range(plat + 8, base - 2, 7):
        f = (y - plat) / (base - plat)
        cilindro(t, lx0 + 2 - 2 * f - 0.5, y, lx1 + 2 - 2 * f + 0.5, y + 0.5, 0.9, 0.9, semente=y, rachas=0, nos=0)
    # Cabo elétrico com isoladores descendo pela perna da direita.
    for y in range(plat + 4, base, 2):
        f = (y - plat) / (base - plat)
        t.ponto(55 + 6 * f + math.sin(y / 5) * 1.2, y, "preto")
    for y in (plat + 20, plat + 55, plat + 90):
        f = (y - plat) / (base - plat)
        x = 55 + 6 * f
        t.chapado(t.elipse(x + 1, y, 1.4, 1.8), "lona_n5")
        t.ponto(x + 0.5, y - 1, "branco")
    # Lampião pendurado num prego da plataforma.
    lampiao(t, 14, plat + 12)
    t.linha(14, plat + 5, 14, plat + 7, "cinza_escuro")
    # Sacos de areia ao pé da torre.
    saco(t, 0, base, 14, 7, semente=semente + 8)
    saco(t, 48, base, 15, 7, semente=semente + 9)
    corpo = t.px != VAZIO
    borda = ndimage.binary_dilation(corpo) & ~corpo
    t.px[borda] = IDX["mad_n1"]
    return t


def zinco(t, m, semente=0, v0=0.6):
    """Chapa de zinco ondulada: ondas verticais claro/escuro, ferrugem e prego."""
    onda = np.sin(t.xx * math.pi / 2.0)
    v = v0 + onda * 0.16 - (t.yy - t.yy[m].min()) / 60 + ruido(t.h, t.w, 0.8, semente) * 0.04
    pintar(t, m, v, FERRO)
    fer = m & (ruido(t.h, t.w, (2, 1), semente + 5) > 1.1)
    pintar(t, fer, 0.4 + onda * 0.15, ["mad_n2", "couro_escuro", "couro", "couro_medio"])


def roda_dentada(t, x, y, r, dentes=10, rampa=FERRO, ang=0.0):
    m = t.elipse(x, y, r, r)
    for k in range(dentes):
        a = ang + k * 2 * math.pi / dentes
        m |= t.elipse(x + math.cos(a) * r, y + math.sin(a) * r, 1.0, 1.0)
    v = 0.6 - ((t.xx - x) + (t.yy - y)) / (4 * r)
    pintar(t, m, v, rampa)
    t.px[t.elipse(x, y, r * 0.55, r * 0.55) & m] = IDX[rampa[1]]
    for k in range(4):
        a = ang + k * math.pi / 2
        t.linha(x, y, x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8, rampa[3])
    t.chapado(t.elipse(x, y, 1.2, 1.2), rampa[-1])


def guindaste(semente=0):
    """Guindaste de toras (190x160): torre treliçada com pernas da frente e de trás,
    travessas amarradas, mastro com o pendural, lança dupla treliçada com cintas de ferro,
    cabos de aço, roldana de raios na ponta, cabine de tábuas com telhado de zinco, janela
    acesa com o operador, sarilho com o cabo enrolado e engrenagem, contrapeso de pedras
    num caixote e tranqueira em volta. Ponta da lança em (176, 40); teto da cabine em y
    base-44 (sólido no jogo)."""
    W, H = 190, 160
    t = Tela(W, H)
    base = H - 1
    rng = np.random.default_rng(semente)
    # Contrapeso: caixote de pedras atrás da torre.
    cp = t.retangulo(0, base - 20, 26, 20)
    tabua(t, 0, base - 20, 26, 20, semente=semente + 1)
    for k in range(1, 4):
        t.linha(0, base - 20 + k * 5, 25, base - 20 + k * 5, "mad_n2")
    for k in range(6):
        e = t.elipse(3 + k * 4, base - 21, 2.8, 2.4)
        pintar(t, e, 0.7 - (t.yy - (base - 23)) / 6 - (t.xx - (3 + k * 4)) / 8, CHAO)
    _ = cp
    # Pernas de trás e travessas.
    for (xb_, xt_) in ((14, 24), (38, 30)):
        cilindro(t, xb_, base, xt_, 30, 2.0, 1.6, semente=semente + xb_, rachas=1, nos=1, escurecer=0.28)
    for k, y in enumerate(range(40, base - 6, 18)):
        f0 = (y - 30) / (base - 30)
        f1_ = (y + 16 - 30) / (base - 30)
        xa0, xb0 = 22 - 16 * f0 + 2, 30 + 16 * f0 - 2
        xa1, xb1 = 22 - 16 * f1_ + 2, 30 + 16 * f1_ - 2
        cilindro(t, xa0, y, xb1, y + 16, 1.2, 1.2, semente=y, rachas=0, nos=0, escurecer=0.1)
        cilindro(t, xb0, y, xa1, y + 16, 1.2, 1.2, semente=y + 1, rachas=0, nos=0, escurecer=0.16)
        cilindro(t, xa1, y + 16, xb1, y + 16, 1.3, 1.3, semente=y + 2, rachas=0, nos=0)
    # Pernas da frente.
    for (xb_, xt_) in ((4, 22), (48, 30)):
        cilindro(t, xb_, base, xt_, 30, 2.8, 2.2, semente=semente + xb_ + 3, rachas=2, nos=1)
    for y in range(56, base - 6, 18):
        f0 = (y - 30) / (base - 30)
        amarracao(t, 22 - 16 * f0 + 1, y, 2.2)
        amarracao(t, 30 + 16 * f0 + 1, y, 2.2)
    # Mastro com o pendural (sobe acima da torre).
    cilindro(t, 26, 40, 26, 8, 2.2, 1.8, semente=semente + 20, rachas=1, nos=0, topo_cortado=True)
    # Lança dupla treliçada até a ponta.
    px, py = 176, 40
    cilindro(t, 30, 46, px - 4, py + 5, 2.4, 1.8, semente=semente + 8, rachas=1, nos=1, escurecer=0.12)
    cilindro(t, 26, 34, px, py, 3.2, 2.4, semente=semente + 7, rachas=2, nos=2)
    for k in range(1, 10):
        f = k / 10
        xa_ = 26 + (px - 26) * f
        ya_ = 34 + (py - 34) * f
        xb2 = 30 + (px - 4 - 30) * (f + 0.05)
        yb2 = 46 + (py + 5 - 46) * (f + 0.05)
        cilindro(t, xa_, ya_ + 1, xb2, yb2, 0.9, 0.9, semente=k + 90, rachas=0, nos=0, escurecer=0.08)
        if k % 3 == 0:
            for d in (-1, 0, 1):
                t.ponto(xa_ + d, ya_ - 1.5, "cinza_medio")
                t.ponto(xa_ + d, ya_ + 2, "sombra")
            t.ponto(xa_, ya_ - 2, "cinza_luz")
    # Cabos de aço: do mastro à ponta e ao contrapeso.
    for (a, b, c, d, fl) in ((26, 8, px - 1, py - 4, 6.0), (26, 8, 8, base - 22, 2.0)):
        n = int(math.hypot(c - a, d - b)) + 2
        for k in range(n + 1):
            f = k / n
            x = a + (c - a) * f
            y = b + (d - b) * f + math.sin(f * math.pi) * fl
            t.ponto(x, y, "sombra" if k % 4 else "cinza_medio")
    # Roldana de raios na ponta, com a caixa de ferro.
    t.chapado(t.retangulo(px - 3, py - 4, 7, 6), "sombra")
    roda_dentada(t, px, py + 2, 4.2, dentes=0)
    t.ponto(px - 2, py - 1, "cinza_luz")
    # Cabine do sarilho.
    cx0, cy0, cw, ch = 30, base - 36, 32, 36
    for k, x in enumerate(range(cx0, cx0 + cw, 4)):
        tabua(t, x, cy0, 4, ch, semente=semente + 100 + k, vertical=True)
    telhado = t.poligono([(cx0 - 4, cy0 + 1), (cx0 + cw / 2, cy0 - 8), (cx0 + cw + 4, cy0 + 1)])
    zinco(t, telhado, semente + 3, 0.62)
    t.linha(cx0 - 4, cy0 + 1, cx0 + cw + 4, cy0 + 1, "sombra")
    t.linha(cx0 - 4, cy0 + 2, cx0 + cw + 4, cy0 + 2, "mad_n1")
    # Janela acesa com o operador de quepe.
    jx, jy = cx0 + 6, cy0 + 7
    t.chapado(t.retangulo(jx, jy, 13, 9), "lona_q2")
    t.chapado(t.elipse(jx + 5, jy + 4, 4, 3), "lona_q3")
    t.chapado(t.elipse(jx + 8, jy + 5, 2, 2.3), "mad_n2")
    t.chapado(t.retangulo(jx + 5.5, jy + 2.4, 5, 1.4), "mad_n2")
    t.chapado(t.retangulo(jx + 6, jy + 7, 5, 3), "mad_n2")
    t.linha(jx + 6.5, jy, jx + 6.5, jy + 8, "mad_n3")
    for (a, b, c, d) in ((jx - 1, jy - 1, jx + 13, jy - 1), (jx - 1, jy + 9, jx + 13, jy + 9)):
        t.linha(a, b, c, d, "mad_n5")
    # Sarilho: tambor com o cabo enrolado e engrenagem grande.
    sx, sy = cx0 + cw - 2, base - 12
    tam = t.retangulo(sx - 6, sy - 5, 12, 10)
    pintar(t, tam, 0.65 - (t.yy - (sy - 5)) / 14, FERRO)
    for y in range(int(sy - 4), int(sy + 5), 2):
        t.linha(sx - 6, y, sx + 5, y + 0.5, "sombra_media")
    roda_dentada(t, sx + 8, sy, 6, dentes=12)
    t.linha(sx + 8, sy, sx + 14, sy - 7, "cinza_escuro")
    t.chapado(t.retangulo(sx + 13, sy - 9, 2, 3), "mad_n4")
    # Tambor de óleo e caixa de ferramentas no pé.
    tamb = t.retangulo(64, base - 14, 10, 14)
    pintar(t, tamb, 0.25 + np.clip(1 - np.abs((t.xx - 67) / 5), 0, 1) * 0.55 +
           (np.abs(t.yy - (base - 9)) < 0.6) * 0.2, VERMELHO + ["laranja_escuro"])
    t.chapado(t.elipse(69, base - 14, 5, 1.2), "vermelho_medio")
    t.chapado(t.elipse(68, base - 2, 7, 1.2), "preto")
    caixote(t, 76, base, 16, 8, semente=semente + 5, rampa=["mad_n1", "vermelho_esc", "vermelho_esc", "vermelho_medio", "vermelho_medio", "vermelho"])
    corpo = t.px != VAZIO
    borda = ndimage.binary_dilation(corpo) & ~corpo
    t.px[borda] = IDX["mad_n1"]
    _ = rng
    return t


def elevador(semente=0):
    """Castelete do elevador de carga (100x150): dois postes de tora com escoras, travessa
    dupla com cintas de ferro, duas roldanas de raios, cabos descendo, guias de trilho,
    grade de ferro dos lados, placa DESCE e lampião aceso. A plataforma é peça de jogo."""
    W, H = 100, 150
    t = Tela(W, H)
    base = H - 1
    cx = W / 2
    # Escoras dos dois lados.
    cilindro(t, 0, base, 12, 60, 2.0, 1.6, semente=semente + 1, rachas=1, nos=0, escurecer=0.1)
    cilindro(t, W - 1, base, W - 13, 60, 2.0, 1.6, semente=semente + 2, rachas=1, nos=0, escurecer=0.1)
    for x0 in (14, W - 15):
        cilindro(t, x0, base, x0, 10, 3.2, 2.8, semente=semente + x0, rachas=3, nos=2)
        for y in (30, 70, 110):
            t.chapado(t.retangulo(x0 - 3.5, y, 7, 2), "sombra_media")
            t.ponto(x0 - 2, y, "cinza_luz")
            t.ponto(x0 + 2, y + 1, "cinza_medio")
    amarracao(t, 12, 61, 2.4)
    amarracao(t, W - 12, 61, 2.4)
    # Travessa dupla com cintas.
    cilindro(t, 4, 10, W - 4, 10, 3.2, 3.2, semente=semente + 3, rachas=2, nos=1)
    cilindro(t, 8, 19, W - 8, 19, 2.2, 2.2, semente=semente + 4, rachas=1, nos=0, escurecer=0.08)
    for x in (16, W - 17, cx):
        t.chapado(t.retangulo(x - 1, 6, 3, 16), "sombra_media")
        t.ponto(x, 7, "cinza_luz")
    # Roldanas e cabos.
    for xr in (cx - 11, cx + 11):
        roda_dentada(t, xr, 4, 5, dentes=0)
        t.ponto(xr - 2, 1, "aco_brilho")
        for y in range(9, base - 16):
            t.ponto(xr + 4, y, "sombra")
            if y % 5 == 0:
                t.ponto(xr + 4, y, "cinza_medio")
    # Guias de trilho nos postes e grade de ferro dos lados da gaiola.
    for x in (18, W - 20):
        t.chapado(t.retangulo(x, 24, 2, base - 24), "sombra_media")
        t.linha(x, 24, x, base, "cinza_medio")
    for x in range(22, W - 22, 5):
        t.linha(x, base - 50, x, base - 18, "sombra_media")
        t.ponto(x, base - 50, "cinza_luz")
    t.linha(20, base - 50, W - 20, base - 50, "cinza_medio")
    t.linha(20, base - 49, W - 20, base - 49, "sombra")
    t.linha(20, base - 34, W - 20, base - 34, "sombra_media")
    # Placa DESCE e lampião.
    w = largura_texto("DESCE") + 8
    tmp = Tela(W, H)
    placa_madeira(tmp, "DESCE", int(cx - w / 2), 26, pendurada=True,
                  rampa=["mad_n1", "vermelho_esc", "vermelho_esc", "vermelho_medio", "vermelho"], cor="amarelo_claro")
    m = tmp.px != VAZIO
    t.px[m] = tmp.px[m]
    lampiao(t, 22, 32)
    corpo = t.px != VAZIO
    borda = ndimage.binary_dilation(corpo) & ~corpo
    t.px[borda] = IDX["mad_n1"]
    return t


# ------------------------------------------------------------------ peças vivas (sprites)
def holofote(q=0):
    """Holofote de campanha (24x18): tambor de chapa com aletas atrás, aro grosso
    rebitado, vidro de anéis (Fresnel) aceso (q0), aceso forte (q1) ou estilhaçado (q2),
    forquilha e pino de giro."""
    t = Tela(24, 18)
    # Forquilha e base.
    t.chapado(t.retangulo(9, 14, 6, 4), "sombra")
    t.chapado(t.retangulo(10, 14, 4, 1), "cinza_medio")
    t.linha(6, 13, 6, 7, "sombra_media")
    t.linha(17, 13, 17, 7, "sombra_media")
    t.linha(6, 13, 17, 13, "sombra_media")
    # Tambor.
    corpo = t.capsula(4, 8, 15, 8, 6, 5.5)
    v = 0.55 - (t.yy - 2) / 18 + np.clip(1 - np.abs(t.yy - 5) / 2, 0, 1) * 0.25
    pintar(t, corpo, v, FERRO)
    for x in (4, 6, 8):
        t.linha(x, 3, x, 13, "sombra")
        t.linha(x + 1, 3, x + 1, 13, "cinza_medio")
    t.chapado(t.elipse(11, 2.5, 2, 1), "sombra")  # respiro
    # Aro.
    aro = t.elipse(17, 8, 4.4, 6.8)
    pintar(t, aro, 0.7 - (t.yy - 1) / 16, FERRO)
    for y in (3, 8, 13):
        t.ponto(15, y, "aco_brilho")
    vidro = t.elipse(18, 8, 3.0, 5.4)
    if q == 2:
        t.chapado(vidro, "preto")
        for (a, b, c, d) in ((16, 4, 19, 9), (19, 6, 17, 12), (17, 9, 20, 11)):
            t.linha(a, b, c, d, "cinza_luz")
        t.ponto(18, 3, "cinza_medio")
    else:
        d = np.hypot((t.xx - 18) / 3.0, (t.yy - 8) / 5.4)
        pintar(t, vidro, 1.0 - d * 0.5 + (q == 1) * 0.2, ["ouro_escuro", "amarelo_fogo", "amarelo_claro", "branco"])
        for r in (0.45, 0.8):
            t.px[vidro & (np.abs(d - r) < 0.08)] = IDX["amarelo_fogo" if q == 0 else "amarelo_claro"]
        if q == 1:
            t.chapado(t.elipse(21.5, 8, 2, 5.5) & ~vidro, "amarelo_claro")
    t.contorno("mad_n1")
    return t


def gerador(q=0):
    """Gerador a gasolina (46x34) num chassi de viga rebitada: bloco oliva com aletas,
    volante de raios girando (q0/q1), tanque vermelho com bocal, escapamento com fuligem,
    painel com relógio e lâmpada, cabos saindo e mancha de óleo. q2: arrebentado (chapa
    rasgada para fora, volante solto, fogo dentro)."""
    t = Tela(46, 34)
    d = 1 if q == 1 else 0
    quebrado = q == 2
    # Chassi.
    ch = t.retangulo(1, 28, 44, 5)
    pintar(t, ch, 0.62 - (t.yy - 28) / 8, FERRO)
    t.linha(1, 28, 44, 28, "cinza_luz")
    for x in range(4, 44, 6):
        t.ponto(x, 30, "aco_brilho")
    for x in (3, 40):
        t.chapado(t.retangulo(x, 31, 4, 3), "preto")
    # Tanque.
    tq = t.capsula(9, 6 + d, 29, 6 + d, 4.4)
    pintar(t, tq, 0.85 - (t.yy - (2 + d)) / 9, VERMELHO + ["laranja_escuro"])
    t.linha(12, 3 + d, 26, 3 + d, "laranja_escuro")
    t.chapado(t.retangulo(25, 0 + d, 4, 2.4), "cinza_medio")
    t.ponto(25, 0 + d, "cinza_luz")
    for x in (12, 26):
        t.linha(x, 10 + d, x, 12 + d, "sombra")
    # Bloco do motor com aletas.
    bl = t.retangulo(10, 11 + d, 21, 17)
    v = 0.6 - (t.xx - 10) / 50
    for y in range(13, 27, 2):
        v = np.where(np.abs(t.yy - (y + d)) < 0.5, v - 0.28, v)
        v = np.where(np.abs(t.yy - (y + d + 1)) < 0.5, v + 0.12, v)
    pintar(t, bl, v, OLIVA)
    t.linha(10, 11 + d, 30, 11 + d, "oliva_n5")
    # Escapamento com fuligem.
    cilindro(t, 15, 11 + d, 15, 1 + d, 1.4, 1.4, rampa=FERRO, rachas=0, nos=0, casca=False)
    t.chapado(t.elipse(15, 1 + d, 2, 1), "preto")
    # Volante.
    vx, vy = 37, 18 + d
    anel = t.elipse(vx, vy, 7.4, 7.4) & ~t.elipse(vx, vy, 5.2, 5.2)
    pintar(t, anel, 0.75 - ((t.xx - vx) + (t.yy - vy)) / 20, FERRO)
    rot = math.pi / 6 if q == 1 else 0
    for k in range(3):
        a = rot + k * math.pi / 3
        t.linha(vx - math.cos(a) * 5, vy - math.sin(a) * 5, vx + math.cos(a) * 5, vy + math.sin(a) * 5, "cinza_medio")
    t.chapado(t.elipse(vx, vy, 1.6, 1.6), "cinza_luz")
    t.ponto(vx - 5, vy - 4, "aco_brilho")
    # Painel com relógio e lâmpada.
    pn = t.retangulo(1, 13 + d, 8, 11)
    pintar(t, pn, 0.55 - (t.yy - 13) / 30, FERRO)
    t.chapado(t.elipse(5, 16.5 + d, 2.4, 2.4), "lona_n6")
    t.linha(5, 16.5 + d, 6.4, 15 + d, "vermelho")
    t.ponto(5, 21 + d, "vermelho" if not quebrado else "sombra")
    t.ponto(3, 21 + d, "alien_luz" if not quebrado else "sombra")
    # Cabos saindo do painel.
    for k, y in enumerate((22, 25)):
        for x in range(0, 4):
            t.ponto(x, y + d + (x % 2) * 0.5 + k, "preto")
    if quebrado:
        rasgo = t.poligono([(12, 13), (21, 10), (29, 17), (21, 26), (13, 23)])
        t.chapado(rasgo, "preto")
        t.chapado(t.elipse(20, 18, 3.2, 3) & rasgo, "laranja_fogo")
        t.chapado(t.elipse(20, 18, 1.4, 1.4) & rasgo, "amarelo_fogo")
        for (a, b, c, d_) in ((12, 13, 9, 9), (29, 17, 33, 14), (21, 26, 23, 30)):
            t.linha(a, b, c, d_, "cinza_luz")
        t.px[(t.xx > 29) & (t.yy < 27) & (t.px != VAZIO)] = IDX["sombra"]
        t.chapado(t.elipse(38, 30, 6, 2), "cinza_escuro")
        t.linha(33, 30, 43, 30, "cinza_medio")
    t.contorno("mad_n1")
    return t


def jaula(q=0, w=40, h=44):
    """Grade da frente da jaula (40x44): barras grossas roliças de ferro com brilho,
    quadro de cantoneira rebitado em cima e embaixo, travessa com corrente e cadeado de
    latão e uma plaquinha com caveira; q1: arrebentada (barras tortas para fora,
    corrente partida)."""
    t = Tela(w, h)
    base = h - 1
    aberta = q == 1
    for k, x in enumerate(range(4, w - 3, 5)):
        if aberta and 1 <= k <= 5:
            cilindro(t, x, 4, x - (k - 3) * 3, 17, 1.1, 1.1, rampa=FERRO, rachas=0, nos=0, casca=False)
            cilindro(t, x, base - 4, x + (k - 3) * 4, base - 15, 1.1, 1.1, rampa=FERRO, rachas=0, nos=0, casca=False)
            continue
        cilindro(t, x, 3, x, base - 3, 1.1, 1.1, rampa=FERRO, rachas=0, nos=0, casca=False)
        t.ponto(x - 0.5, 8 + (k * 7) % 20, "aco_brilho")
    for y in (2, base - 2):
        q_ = t.retangulo(0, y - 2, w, 4)
        pintar(t, q_, 0.65 - (t.yy - (y - 2)) / 7, FERRO)
        for x in range(2, w, 5):
            t.ponto(x, y, "aco_brilho")
    if not aberta:
        cilindro(t, 1, h * 0.5, w - 2, h * 0.5, 1.1, 1.1, rampa=FERRO, rachas=0, nos=0, casca=False)
        for k in range(5):
            e = t.elipse(w * 0.5 - 6 + k * 3, h * 0.5 + 1 + (k % 2), 1.6, 1.0)
            t.chapado(e & ~t.elipse(w * 0.5 - 6 + k * 3, h * 0.5 + 1 + (k % 2), 0.6, 0.3), "cinza_medio")
        cad = t.retangulo(w * 0.5 + 3, h * 0.5 + 1, 6, 6)
        pintar(t, cad, 0.85 - (t.yy - (h * 0.5 + 1)) / 8, ["mad_n2", "couro", "ouro_escuro", "amarelo_fogo", "amarelo_claro"])
        t.chapado(t.elipse(w * 0.5 + 6, h * 0.5 + 1, 2, 2) & ~t.elipse(w * 0.5 + 6, h * 0.5 + 1, 1, 1), "cinza_luz")
        t.ponto(w * 0.5 + 6, h * 0.5 + 4, "mad_n1")
    else:
        for k in range(3):
            t.chapado(t.elipse(w * 0.5 - 8 + k * 3, base - 4 + k % 2, 1.6, 1.0), "cinza_medio")
    # Plaquinha com caveira.
    py = 6 if not aberta else 28
    p = t.retangulo(w / 2 - 6, py, 12, 9)
    pintar(t, p, 0.8 - (t.yy - py) / 14, ["mad_n1", "ouro_escuro", "amarelo_fogo", "amarelo_claro"])
    t.chapado(t.elipse(w / 2, py + 3.6, 2.6, 2.2), "mad_n1")
    t.chapado(t.retangulo(w / 2 - 1.5, py + 5, 3, 2.4), "mad_n1")
    t.ponto(w / 2 - 1, py + 3.5, "amarelo_fogo")
    t.ponto(w / 2 + 1, py + 3.5, "amarelo_fogo")
    t.contorno("mad_n1")
    return t


def pedaco_disco(q=0):
    """Pedaço do casco do disco pendurado (56x40): chapa curva de liga lisa com reflexo
    esverdeado, nervuras, runas acesas que pulsam (q0/q1), furo com a corrente, borda
    arrancada em dentes com a chapa descascada em camadas e fios soltos faiscando."""
    t = Tela(56, 40)
    casco = t.elipse(28, 34, 27, 26) & (t.yy > 10) & (t.yy < 36)
    v = 0.95 - (t.yy - 10) / 32 - np.abs(t.xx - 22) / 70
    v = np.where(np.abs(t.yy - 15) < 1.4, v + 0.15, v)  # reflexo da curva
    for x in (14, 28, 42):
        v = np.where(np.abs(t.xx - x) < 0.6, v - 0.25, v)
        v = np.where(np.abs(t.xx - x - 1) < 0.6, v + 0.1, v)
    pintar(t, casco, v, ["preto", "sombra", "sombra_media", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "aco_brilho"])
    for x in range(3, 54, 4):
        dente = t.poligono([(x, 35), (x + 2, 39 - (x % 3)), (x + 4, 35)])
        t.chapado(dente, "cinza_escuro")
        t.ponto(x + 2, 36, "cinza_medio")
    t.chapado(casco & (np.abs(t.yy - 24) < 1.2), "sombra")
    cor = "alien_brilho" if q else "alien"
    for k, x in enumerate(range(9, 49, 5)):
        g = [(0, 0), (2, 0), (2, 1), (0, 2), (1, 2)] if k % 2 else [(0, 0), (0, 2), (1, 1), (2, 2), (2, 0)]
        for (a, b) in g:
            t.ponto(x + a, 21 + b, cor)
    if q:
        for k, x in enumerate(range(9, 49, 5)):
            t.ponto(x + 1, 20, "alien_luz")
    t.chapado(t.elipse(28, 17, 4, 3), "preto")
    t.chapado(t.elipse(28, 17, 4, 3) & ~t.elipse(28, 17, 3, 2), "cinza_escuro")
    t.ponto(27, 16, "alien_esc" if q else "alien_profundo")
    for x, cor in ((8, "vermelho_medio"), (44, "amarelo_fogo"), (47, "alien_medio")):
        t.linha(x, 35, x + 1, 39, cor)
    if q:
        t.ponto(9, 39, "amarelo_claro")
    t.contorno("mad_n1")
    return t


def lampada(q=0):
    """Lâmpada do varal (6x8): soquete de baquelite e bulbo aceso (q0), forte (q1) ou apagado (q2)."""
    t = Tela(6, 8)
    t.chapado(t.retangulo(2, 0, 2, 2.4), "preto")
    t.ponto(2, 0, "cinza_medio")
    if q == 2:
        t.chapado(t.elipse(3, 4.6, 2, 2.4), "sombra_media")
        t.ponto(2, 4, "cinza_medio")
    else:
        t.chapado(t.elipse(3, 4.6, 2.2, 2.6), "ouro_escuro" if q == 0 else "amarelo_fogo")
        t.chapado(t.elipse(2.8, 4.4, 1.3, 1.6), "amarelo_fogo" if q == 0 else "amarelo_claro")
        t.ponto(2.4, 3.8, "branco")
    return t


def bandeira(q=0):
    """Bandeira da Volante tremulando (34x20, 4 quadros): pano oliva com volume, dobras
    claras e escuras correndo, losango amarelo com a estrela, borda puída."""
    t = Tela(34, 20)
    pts_c, pts_b = [], []
    for k in range(13):
        x = 1 + k * 2.6
        o = math.sin(k * 0.7 - q * math.pi / 2) * (k / 12) * 3
        pts_c.append((x, 2 + o))
        pts_b.append((x, 17 + o * 0.8))
    fl = t.poligono(pts_c + pts_b[::-1])
    onda = np.cos(t.xx / 2.6 * 0.7 - q * math.pi / 2) * np.clip(t.xx / 30, 0, 1)
    v = 0.55 + onda * 0.25 - (t.yy - 2) / 60
    pintar(t, fl, v, OLIVA)
    los = t.poligono([(9, 10), (17, 5), (25, 10), (17, 15)]) & fl
    pintar(t, los, 0.6 + onda * 0.3, ["ouro_escuro", "amarelo_fogo", "amarelo_claro"])
    t.ponto(17, 10, "vermelho_medio")
    for (a, b) in ((16, 10), (18, 10), (17, 9), (17, 11)):
        t.ponto(a, b, "vermelho_medio")
    for k in range(0, 13, 3):
        x, y = pts_b[k]
        t.ponto(x, y + 1, "oliva_n3")
    t.contorno("mad_n1")
    return t


def poste_lampadas(altura=60, semente=0):
    """Poste de pau com cruzeta, isoladores de louça e o fio descendo."""
    t = Tela(16, altura)
    cilindro(t, 8, altura - 1, 8, 3, 1.8, 1.5, semente=semente, rachas=2, nos=1, topo_cortado=True)
    cilindro(t, 1, 6, 15, 6, 1.0, 1.0, semente=semente + 1, rachas=0, nos=0)
    for x in (2, 14):
        t.chapado(t.elipse(x, 4, 1.2, 1.5), "lona_n5")
        t.ponto(x - 0.4, 3.4, "branco")
    for y in range(8, altura - 2, 2):
        t.ponto(10 + math.sin(y / 6) * 0.7, y, "preto")
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    return t


def base_gerador():
    """Laje de cimento rachada (54x6) com a mancha de óleo e os calços do gerador."""
    t = Tela(54, 6)
    m = t.retangulo(0, 1, 54, 5)
    v = 0.6 - (t.yy - 1) / 10 + ruido(6, 54, 0.6, 3) * 0.05
    v = np.where(t.yy < 2, 0.82, v)
    pintar(t, m, v, ["sombra", "chao_n3", "chao_n4", "chao_n5", "chao_n6", "lona_n4"])
    t.chapado(t.elipse(36, 3, 9, 1.6), "preto")
    t.ponto(33, 3, "azul_medio")
    t.linha(12, 2, 16, 5, "chao_n2")
    t.linha(40, 1, 42, 4, "chao_n2")
    t.contorno("mad_n1")
    return t



# ------------------------------------------------------------------ chão do acampamento
def chao_acampamento(w, h=26, semente=0, noite=None, luzes=(), verdes=()):
    """Terra batida pisoteada: beirada de cima clara (a superfície vista de lado), sulcos
    de pneu com a borda iluminada, pegadas de bota, pedras com luz e sombra, tufos de
    capim seco, palha, tábua largada, cápsulas de bala, bitucas e poças de óleo refletindo
    o céu. noite: array (w,) com o escurecimento por coluna. luzes: [(x, raio)] manchas
    quentes de lâmpada; verdes: [(x, raio)] brilho verde da cratera."""
    global NOITE
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    yy, xx = t.yy, t.xx
    nn = np.zeros(w) if noite is None else np.asarray(noite)
    escuro = nn[None, :].repeat(h, 0)
    sup = 2 + (ruido(1, w, 6, semente)[0] * 0.8).round()
    m = yy >= sup[None, :]
    v = 0.62 - (yy - 2) / h * 0.38 + ruido(h, w, (1.2, 4), semente) * 0.07 + ruido(h, w, 0.6, semente + 1) * 0.04
    v = np.where(yy < sup[None, :] + 1.2, 0.78, v)
    # Sulcos de pneu.
    for y0 in (6, 11):
        yb = y0 + np.sin(xx / 90 + y0) * 1.5
        v = np.where(np.abs(yy - yb) < 0.7, v - 0.3, v)
        v = np.where(np.abs(yy - yb - 1.2) < 0.5, v + 0.12, v)
        v = np.where((np.abs(yy - yb) < 0.7) & ((xx.astype(int) % 4) == 0), v + 0.1, v)
    # Luz das lâmpadas e do brilho verde no chão (antes do escuro).
    quente = np.zeros((h, w), bool)
    for (lx, r) in luzes:
        d = np.hypot((xx - lx) / r, (yy - 4) / 9)
        v = v + np.clip(1 - d, 0, 1) * 0.3
        quente |= d < 0.5
    v = v - escuro
    NOITE, salvo = 0.0, NOITE
    pintar(t, m, v, CHAO)
    pintar(t, m & quente, v + 0.1, ["chao_n3", "chao_n5", "lona_q1", "lona_q2", "lona_q3"])
    for (gx, r) in verdes:
        d = np.hypot((xx - gx) / r, (yy - 5) / 10)
        g = m & (d < 1) & (ruido(h, w, 1.5, int(gx)) > -0.3 + d)
        pintar(t, g, 0.9 - d * 0.6, ["chao_n2", "alien_profundo", "alien_esc", "alien_medio"])
    # Pegadas de bota.
    for _ in range(w // 18):
        x, y = rng.uniform(0, w), rng.uniform(5, h - 4)
        t.chapado(t.elipse(x, y, 1.8, 0.8), "chao_n2")
        t.ponto(x - 1, y - 1, "chao_n4")
    # Pedras com luz e sombra.
    for _ in range(w // 22):
        x, y = rng.uniform(0, w), rng.uniform(3, h - 2)
        r = rng.uniform(0.9, 2.6) * (0.6 + y / h * 0.6)
        e = t.elipse(x, y, r * 1.3, r)
        k = int(min(w - 1, max(0, x)))
        pintar(t, e, 0.75 - ((xx - x) + (yy - y)) / (3 * r) - nn[k] - (1 - y / h) * 0.1,
               ["chao_n1", "chao_n2", "chao_n3", "chao_n4", "chao_n5", "chao_n6"])
        t.ponto(x + r, y + r * 0.8, "chao_n1")
    # Capim seco em tufos na beirada e palha espalhada.
    for _ in range(w // 14):
        x = rng.uniform(0, w)
        y = sup[int(min(w - 1, x))] + rng.uniform(0, 3)
        for k in range(int(rng.integers(3, 6))):
            a = rng.uniform(-0.9, 0.9)
            L = rng.uniform(2, 5)
            t.linha(x, y, x + math.sin(a) * L, y - math.cos(a) * L, "corda_n2" if k % 2 else "corda_n1")
            t.ponto(x + math.sin(a) * L, y - math.cos(a) * L, "corda_n3")
    for _ in range(w // 10):
        x, y = rng.uniform(0, w), rng.uniform(4, h - 3)
        a = rng.uniform(0, math.pi)
        t.linha(x, y, x + math.cos(a) * 2.5, y + math.sin(a) * 0.8, "corda_n2")
    # Cápsulas e bitucas.
    for _ in range(w // 30):
        x, y = rng.uniform(0, w), rng.uniform(5, h - 3)
        t.ponto(x, y, "ouro_escuro")
        t.ponto(x + 1, y, "amarelo_fogo")
    for _ in range(w // 60):
        x, y = rng.uniform(0, w), rng.uniform(5, h - 3)
        t.ponto(x, y, "lona_n5")
        t.ponto(x + 1, y, "laranja_escuro")
    # Poças de óleo refletindo o céu.
    for _ in range(w // 110):
        x, y = rng.uniform(10, w - 10), rng.uniform(6, h - 6)
        e = t.elipse(x, y, rng.uniform(5, 10), 1.4)
        t.chapado(e, "preto")
        t.chapado(t.elipse(x - 1, y - 0.3, 3, 0.5), "roxo")
        t.ponto(x - 3, y - 0.4, "lilas")
    NOITE = salvo
    return t


def plataforma_elevador():
    """Estrado do elevador (60x12): chapa xadrez de ferro com vigas, rebites, borda
    gasta clara e as correntes subindo dos cantos."""
    t = Tela(60, 12)
    m = t.retangulo(0, 6, 60, 6)
    v = 0.55 - (t.yy - 6) / 10 + (((t.xx.astype(int) // 3 + t.yy.astype(int)) % 2) == 0) * 0.08
    pintar(t, m, v, FERRO)
    t.linha(0, 6, 59, 6, "cinza_luz")
    t.linha(0, 9, 59, 9, "sombra")
    for x in range(3, 58, 6):
        t.ponto(x, 7, "aco_brilho")
        t.ponto(x, 10, "cinza_medio")
    for x in (2, 57):
        for y in range(0, 6):
            t.ponto(x, y, "cinza_medio" if y % 2 else "sombra")
    t.contorno("mad_n1")
    return t



# ------------------------------------------------------------------ fundo: construções
def barracao(w=110, h=62, texto="ALMOXARIFADO", semente=0, antena=False):
    """Barracão de tábuas com telhado de zinco de uma água: tábuas verticais com mata-junta,
    janelas acesas com vulto, porta de tábuas com tranca, letreiro, chaminé de lata, beiral
    com sombra, base suja, tambores e caixotes encostados; antena de rádio opcional."""
    t = Tela(w + 8, h + (26 if antena else 0))
    off = 26 if antena else 0
    chao = t.h - 1
    rng = np.random.default_rng(semente)
    topo_par = off + 16
    # Parede de tábuas.
    for k, x in enumerate(range(4, w + 4, 5)):
        tabua(t, x, topo_par, 5, chao - topo_par + 1, semente=semente + k, vertical=True)
    par = t.retangulo(4, topo_par, w, chao - topo_par + 1)
    # Sombra do beiral e sujeira subindo da base.
    sombra = par & (t.yy < topo_par + 5)
    t.px[sombra] = IDX["mad_n2"]
    suja = par & (t.yy > chao - 6 + ruido(t.h, t.w, (1, 3), semente) * 1.5)
    pintar(t, suja, 0.35, MAD)
    # Telhado de zinco.
    tel = t.poligono([(0, topo_par + 2), (0, topo_par - 6), (w + 8, off + 1), (w + 8, off + 9)])
    zinco(t, tel, semente + 1, 0.62)
    t.linha(0, topo_par + 2, w + 8, off + 9, "mad_n1")
    t.linha(0, topo_par + 1, w + 8, off + 8, "cinza_luz")
    # Parede acompanha a água do telhado até a beira.
    for x in range(4, w + 4):
        ytel = topo_par + 2 + (off + 9 - topo_par - 2) * x / (w + 8)
        for yv in range(int(ytel) + 1, topo_par):
            t.ponto(x, yv, "mad_n2")
    # Janelas acesas.
    for k, jx in enumerate(range(12, w - 14, 34)):
        jy = topo_par + 12
        t.chapado(t.retangulo(jx, jy, 14, 10), "lona_q2")
        t.chapado(t.elipse(jx + 6, jy + 4, 5, 3.5), "lona_q3")
        if rng.random() < 0.6:
            t.chapado(t.elipse(jx + 9, jy + 5, 2, 2.2), "mad_n2")
            t.chapado(t.retangulo(jx + 6.5, jy + 7, 5, 3), "mad_n2")
        t.linha(jx + 7, jy, jx + 7, jy + 9, "mad_n3")
        t.linha(jx, jy + 5, jx + 13, jy + 5, "mad_n3")
        for (a, b, c, d) in ((jx - 1, jy - 1, jx + 14, jy - 1), (jx - 1, jy + 10, jx + 14, jy + 10)):
            t.linha(a, b, c, d, "mad_n5")
        t.linha(jx - 1, jy + 11, jx + 14, jy + 11, "mad_n2")
    # Porta.
    px = w - 16
    porta = t.retangulo(px, chao - 26, 13, 26)
    pintar(t, porta, 0.42 + ruido(t.h, t.w, (3, 0.4), semente + 3) * 0.06, MAD)
    t.linha(px, chao - 26, px + 12, chao - 1, "mad_n4")
    t.chapado(t.retangulo(px + 9, chao - 14, 2, 2), "cinza_medio")
    # Letreiro.
    if texto:
        lw = largura_texto(texto) + 8
        placa_madeira(t, texto, int(4 + (w - lw) / 2), topo_par + 1, pendurada=False)
    # Chaminé de lata.
    cx_ = 18
    cilindro(t, cx_, topo_par - 2, cx_, topo_par - 14, 1.6, 1.6, rampa=FERRO, rachas=0, nos=0, casca=False)
    t.chapado(t.retangulo(cx_ - 3, topo_par - 16, 6, 2), "cinza_medio")
    if antena:
        cilindro(t, w - 6, off + 6, w - 6, 1, 0.8, 0.6, rampa=FERRO, rachas=0, nos=0, casca=False)
        for k in (0, 3):
            t.linha(w - 6, 1 + k, w - 34 + k * 6, off + 4, "sombra")
        t.ponto(w - 6, 0, "vermelho")
    # Tambores e caixote encostados.
    for k, bx in enumerate((6, 15)):
        tb = t.retangulo(bx, chao - 13, 8, 13)
        pintar(t, tb, 0.25 + np.clip(1 - np.abs((t.xx - bx - 3) / 4), 0, 1) * 0.6 +
               (np.abs(t.yy - (chao - 8)) < 0.6) * 0.2, OLIVA if k else VERMELHO + ["laranja_escuro"])
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    return t


def caixa_dagua(altura=110, semente=0):
    """Caixa d'água de aduelas com cintas de ferro numa torre de toras: tampa cônica de
    zinco, escada, cano descendo com a torneira e a lata embaixo."""
    W = 54
    t = Tela(W, altura)
    base = altura - 1
    topo_t = 40
    for (xb_, xt_) in ((12, 16), (42, 38)):
        cilindro(t, xb_, base, xt_, topo_t, 1.6, 1.4, semente=semente + xb_, rachas=1, nos=0, escurecer=0.25)
    for y0 in range(topo_t + 8, base - 8, 20):
        cilindro(t, 8, y0, 46, y0 + 18, 1.0, 1.0, semente=y0, rachas=0, nos=0, escurecer=0.1)
        cilindro(t, 46, y0, 8, y0 + 18, 1.0, 1.0, semente=y0 + 1, rachas=0, nos=0, escurecer=0.15)
    for (xb_, xt_) in ((3, 10), (51, 44)):
        cilindro(t, xb_, base, xt_, topo_t, 2.2, 1.9, semente=semente + xb_ + 5, rachas=2, nos=1)
    cilindro(t, 6, topo_t + 1, 48, topo_t + 1, 2.0, 2.0, semente=semente + 9, rachas=1, nos=0)
    # Tanque de aduelas.
    tq = t.retangulo(7, 14, 40, topo_t - 14)
    v = 0.25 + np.clip(1 - np.abs((t.xx - 20) / 18), 0, 1) * 0.6
    v = np.where((t.xx.astype(int) % 4) == 0, v - 0.18, v)
    pintar(t, tq, v, MAD)
    for y in (17, 27, 36):
        cin = t.retangulo(6, y, 42, 2)
        pintar(t, cin, 0.6 - np.abs(t.xx - 20) / 50, FERRO)
        t.ponto(9, y, "aco_brilho")
    tampa = t.poligono([(4, 15), (27, 3), (50, 15)])
    zinco(t, tampa, semente + 4, 0.62)
    t.linha(4, 15, 50, 15, "mad_n1")
    # Escada e cano com torneira.
    for x in (28, 34):
        cilindro(t, x, base, x, topo_t - 4, 0.8, 0.8, semente=x, rachas=0, nos=0)
    for y in range(topo_t, base - 2, 6):
        t.linha(28, y, 34, y, "mad_n4")
    for y in range(topo_t + 2, base - 10):
        t.ponto(20, y, "sombra_media")
        t.ponto(21, y, "cinza_medio")
    t.chapado(t.retangulo(18, base - 11, 5, 2), "cinza_medio")
    lt = t.retangulo(16, base - 6, 8, 6)
    pintar(t, lt, 0.7 - (t.xx - 16) / 12, FERRO)
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    return t


def poste_telegrafo(altura=96, semente=0):
    """Poste de telégrafo alto: tora com duas cruzetas, isoladores de louça e degraus de
    ferro cravados. Os fios são passados à parte (fios())."""
    t = Tela(30, altura)
    cilindro(t, 15, altura - 1, 15, 2, 2.0, 1.6, semente=semente, rachas=3, nos=2, topo_cortado=True)
    for y in (8, 16):
        cilindro(t, 2, y, 28, y, 1.1, 1.1, semente=semente + y, rachas=0, nos=0)
        for x in (4, 10, 20, 26):
            t.chapado(t.elipse(x, y - 2, 1.2, 1.5), "lona_n5")
            t.ponto(x - 0.4, y - 2.6, "branco")
    for y in range(30, altura - 10, 8):
        t.linha(13 if (y // 8) % 2 else 17, y, 10 if (y // 8) % 2 else 20, y, "cinza_medio")
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    return t


ISOLADORES = [(4, 6), (10, 6), (20, 6), (26, 6), (4, 14), (10, 14), (20, 14), (26, 14)]


def fios(t, x0, y0, x1, y1, flecha=6.0, cor="sombra"):
    n = int(abs(x1 - x0)) + 1
    for k in range(n + 1):
        f = k / n
        t.ponto(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f + math.sin(f * math.pi) * flecha, cor)


def tambores(n=5, semente=0):
    """Pilha de tambores de gasolina deitados e em pé, com tinta descascada e letras."""
    t = Tela(n * 11 + 10, 30)
    chao = t.h - 1
    rng = np.random.default_rng(semente)
    for k in range(n):
        bx = 2 + k * 11
        rampa = [OLIVA, VERMELHO + ["laranja_escuro"], FERRO][int(rng.integers(0, 3))]
        tb = t.retangulo(bx, chao - 15, 10, 15)
        v = 0.22 + np.clip(1 - np.abs((t.xx - bx - 3.5) / 5), 0, 1) * 0.66
        for yy in (chao - 11, chao - 4):
            v = np.where(np.abs(t.yy - yy) < 0.6, v + 0.22, v)
        pintar(t, tb, v, rampa)
        t.chapado(t.elipse(bx + 5, chao - 15, 5, 1.2), rampa[-2])
        t.ponto(bx + 7, chao - 15, "preto")
    for k in range(max(1, n // 2)):
        bx = 7 + k * 22
        e = t.elipse(bx + 5, chao - 20, 5, 5)
        pintar(t, e, 0.8 - ((t.xx - bx) + (t.yy - (chao - 24))) / 14, OLIVA)
        t.chapado(t.elipse(bx + 5, chao - 20, 2, 2), "oliva_n2")
        t.chapado(t.elipse(bx + 5, chao - 20, 4.2, 4.2) & ~t.elipse(bx + 5, chao - 20, 3.4, 3.4), "oliva_n4")
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    return t


def caixotes_lona(semente=0):
    """Pilha de caixotes coberta por lona amarrada com cordas, com a ponta levantada."""
    t = Tela(64, 40)
    chao = t.h - 1
    caixote(t, 2, chao, 28, 16, "TNT", semente=semente)
    caixote(t, 30, chao, 30, 16, semente=semente + 1)
    caixote(t, 10, chao - 16, 26, 14, semente=semente + 2)
    lona_ = t.poligono([(30, chao - 15), (36, chao - 30), (62, chao - 18), (62, chao - 2), (34, chao - 2)])
    v = 0.6 + np.sin(t.xx / 2.5) * 0.08 - (t.yy - (chao - 30)) / 60
    pintar(t, lona_, v, OLIVA)
    for x in (40, 52):
        corda(t, x, chao - 26 + (x - 36) * 0.4, x + 2, chao - 1, 0.5)
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    return t


def barraca_pequena(w=40, h=24, semente=0, rampa=OLIVA, acesa=True):
    """Barraca de campanha pequena (fundo): duas águas com vinco, porta com luz e cordas."""
    t = Tela(w + 8, h + 2)
    chao = t.h - 1
    cx = w / 2 + 4
    corpo = t.poligono([(4, chao), (cx, 2), (w + 4, chao)])
    v = 0.75 - np.abs(t.xx - cx) / w * 0.1 - (t.xx > cx) * 0.25 - (t.yy - 2) / h * 0.2
    v = np.where(np.abs(t.xx - cx) < 0.6, v + 0.15, v)
    pintar(t, corpo, v, rampa)
    porta = t.poligono([(cx - 4, chao), (cx, chao - h * 0.6), (cx + 4, chao)])
    pintar(t, porta, 0.7 - (t.yy - (chao - h * 0.6)) / h if acesa else 0.1 + 0 * t.yy,
           ["mad_n1", "lona_q1", "lona_q2", "lona_q3"] if acesa else ["mad_n1", "mad_n2"])
    for (a, b, c, d) in ((4, chao, 0, chao), (w + 4, chao, w + 7, chao), (cx, 2, cx, 0)):
        t.linha(a, b, c, d, "corda_n2")
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    _ = semente
    return t


def andaime(w=60, h=60, semente=0):
    """Andaime de varas amarradas com rampa de tábuas em zigue-zague (fundo)."""
    t = Tela(w, h)
    for x in range(2, w, 14):
        cilindro(t, x, h - 1, x, 2, 1.0, 0.9, semente=semente + x, rachas=0, nos=0)
    for y in range(6, h, 14):
        cilindro(t, 0, y, w - 1, y, 0.8, 0.8, semente=semente + y, rachas=0, nos=0)
    for k, y in enumerate(range(6, h - 6, 14)):
        a, b = (0, w - 1) if k % 2 == 0 else (w - 1, 0)
        rm = t.capsula(a, y + 13, b, y + 1, 1.2)
        pintar(t, rm, 0.65 - (t.yy - y) / 40, MAD)
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    return t
