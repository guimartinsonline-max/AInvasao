"""Peças comuns para desenhar bonecos pixel a pixel no estilo Metal Slug.

A grade é uma lista de listas de caracteres (legenda em pixel.py).
Luz sempre vem de cima à esquerda.
"""
import numpy as np

# Posições (joelho, pé) relativas ao quadril.
CICLO_CORRIDA = [((4, 4), (5, 9)), ((2, 4), (1, 9)), ((-1, 4), (-3, 9)),
                 ((-3, 4), (-7, 8)), ((-2, 4), (-6, 5)), ((3, 2), (1, 6))]
CICLO_ANDAR = [((2, 4), (3, 9)), ((1, 4), (0, 9)), ((-1, 4), (-2, 9)), ((0, 3), (1, 7))]


def grade(w, h):
    return [["."] * w for _ in range(h)]


def texto(g):
    return "\n".join("".join(l) for l in g)


def pintar(g, y, x, txt):
    for k, ch in enumerate(txt):
        if ch != "." and 0 <= y < len(g) and 0 <= x + k < len(g[0]):
            g[y][x + k] = ch


def bloco(g, y, x, linhas):
    for k, l in enumerate(linhas):
        pintar(g, y + k, x, l)


def trocar(linhas, mapa):
    """Troca caracteres (recolorir um bloco): mapa = {'i': 'p', ...}."""
    return [(y, x, "".join(mapa.get(c, c) for c in t)) for (y, x, t) in linhas]


def segmento(forma, a, b, r):
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]]
    px, py = xx + 0.5 - a[0], yy + 0.5 - a[1]
    vx, vy = b[0] - a[0], b[1] - a[1]
    L2 = max(vx * vx + vy * vy, 1e-6)
    t = np.clip((px * vx + py * vy) / L2, 0, 1)
    dx, dy = px - t * vx, py - t * vy
    return np.hypot(dx, dy) <= r, dx


def pintar_tons(g, mascara, lado, tons, escurecer=0, raio=2.6):
    n = len(tons)
    for y, x in zip(*np.where(mascara)):
        f = (lado[y, x] + raio) / (2 * raio)
        g[y][x] = tons[min(n - 1, max(0, int(f * n) + escurecer))]


def contorno(g, mascara, cor="O"):
    m = np.pad(mascara, 1)
    viz = m[:-2, 1:-1] | m[2:, 1:-1] | m[1:-1, :-2] | m[1:-1, 2:]
    for y, x in zip(*np.where(viz & ~mascara)):
        if g[y][x] == ".":
            g[y][x] = cor


def perna(g, quadril, joelho, pe, atras, coxa_tons, canela_tons, sola="sd", gaspea="gd",
          r_coxa=2.6, r_canela=2.3, fivela=None, pe_largo=3.6):
    forma = (len(g), len(g[0]))
    hx, hy = quadril
    k = (hx + joelho[0], hy + joelho[1])
    p = (hx + pe[0], hy + pe[1])
    esc = 1 if atras else 0
    coxa, lado1 = segmento(forma, (hx + 0.5, hy + 0.5), (k[0] + 0.5, k[1] + 0.5), r_coxa)
    canela, lado2 = segmento(forma, (k[0] + 0.5, k[1] + 0.5), (p[0] + 0.5, p[1] - 1.5), r_canela)
    yy, xx = np.mgrid[0:forma[0], 0:forma[1]]
    bota = (((xx + 0.5 - (p[0] + 1.8)) / pe_largo) ** 2 + ((yy + 0.5 - (p[1] - 0.6)) / 1.7) ** 2) <= 1
    pintar_tons(g, coxa, lado1, coxa_tons, esc, r_coxa)
    pintar_tons(g, canela & ~coxa, lado2, canela_tons, esc, r_canela)
    for y, x in zip(*np.where(bota & ~canela)):
        g[y][x] = sola[1] if y >= p[1] else (gaspea[0] if x < p[0] + 1 else gaspea[1])
    if fivela and not atras:
        g[min(len(g) - 1, k[1] + 1)][k[0]] = fivela
    contorno(g, coxa | canela | bota)
