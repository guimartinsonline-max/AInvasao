"""Rio seco e acampamento da Volante no chão largo (23/10), no jeito do Metal Slug: sem
contorno, luz da esquerda e de cima, peças em 2.5D (frente, lado fugindo para trás e tampo
visto de cima) na escala do Lampião (~45 px de altura).

Peças:
- barranco(): a margem de trás do rio, um corte de terra em camadas com o capim na beira;
- lama(): o leito rachado (placas de barro seco com as rachaduras escuras);
- ponte(): tabuleiro de tábuas com pilares roliços e escoras em X, frente e fundo;
- carnauba(): palmeira de leque, tronco com os anéis das folhas velhas;
- canoa(): canoa de tábua encalhada, vista um pouco de cima;
- barraca(): barraca de lona da Volante (empena de frente, telhado fugindo para trás);
- torre(): torre de vigia de toras com plataforma, parapeito e telhadinho.
"""
import numpy as np

from caatinga_ms import Quadro, ruido, escurecer
from pecas25 import P, poly, linha, tora


# ---------------------------------------------------------------- rio seco
def barranco(W=300, H=26, sem=1):
    """Margem de trás do rio: terra cortada em camadas (estratos ondulados), raízes e capim
    pendendo da beira, pedrinhas saindo do corte; a beira de cima ondula e o pé espalha terra."""
    q = Quadro(W, H + 6)
    X, Y = q.xx.astype(float), q.yy.astype(float)
    topo = 4 + 2.5 * ruido(1, W, 18, sem)[0][None, :] + 1.0 * ruido(1, W, 4, sem + 1)[0][None, :]
    pe = H + 2 + 1.5 * ruido(1, W, 10, sem + 2)[0][None, :]
    m = (Y >= topo) & (Y < pe)
    k = (Y - topo) / np.maximum(1, pe - topo)
    estr = np.sin((Y + 3 * ruido(q.h, W, (3, 25), sem + 3)) * 0.9)
    luz = 0.55 - 0.22 * k + 0.08 * estr + 0.04 * ruido(q.h, W, (1, 3), sem + 4)
    luz = np.where(ruido(q.h, W, (8, 2), sem + 5) > 1.4, luz - 0.12, luz)          # sulcos da chuva
    P(q, m, 'terra', luz[m])
    beira = m & (Y < topo + 2)
    P(q, beira, 'terra', 0.8)
    capim = (Y < topo + 1) & (Y >= topo - 3) & (((X * 7 + sem) % 5) < 2) & (ruido(q.h, W, (1, 6), sem + 6) > -0.3)
    P(q, capim, 'verde', np.where(Y < topo - 1, 0.65, 0.4)[capim])
    raiz = m & (np.abs(Y - topo - 3 - 6 * ((X * 13 + sem) % 7) / 7) < 0.6) & ((X * 3 + sem) % 23 < 2)
    P(q, raiz, 'madeira', 0.25)
    rng = np.random.default_rng(sem)
    for _ in range(W // 25):
        cx, cy = rng.uniform(4, W - 4), rng.uniform(8, H - 2)
        pm = (((X - cx) / 2.2) ** 2 + ((Y - cy) / 1.6) ** 2 < 1) & m
        P(q, pm, 'cal', np.where(Y < cy, 0.7, 0.35)[pm])
    # o pé escurece (sombra do corte) e a terra caída espalha no chão
    P(q, m & (Y > pe - 3), 'terra', 0.22)
    return q


def lama(q, x0, x1, y0, y1, sem=2):
    """Leito rachado pintado no chão: placas claras de barro seco (Voronoi achatado pela
    perspectiva), rachaduras escuras e beirada das placas levantada e acesa."""
    from scipy import ndimage as nd
    X, Y = q.xx.astype(float), q.yy.astype(float)
    zona = (Y >= y0) & (Y < y1)
    borda = np.minimum(X - x0, x1 - X) + 22 * ruido(q.h, q.w, (14, 20), sem) - 10
    zona &= borda > 0
    rng = np.random.default_rng(sem)
    n = int((x1 - x0) * (y1 - y0) / 140)
    pts = np.stack([rng.uniform(x0, x1, n), rng.uniform(y0, y1, n)], 1)
    prof = np.clip((Y - y0) / max(1, y1 - y0), 0, 1)
    d = np.full(q.xx.shape, 1e9)
    d2 = np.full(q.xx.shape, 1e9)
    for px, py in pts:
        e = np.hypot(X - px, (Y - py) * 2.4)
        d2 = np.where(e < d, d, np.minimum(d2, e))
        d = np.minimum(d, e)
    racha = (d2 - d) < (0.9 + 0.8 * prof)
    luz = 0.68 + 0.05 * ruido(q.h, q.w, (2, 4), sem + 1) - 0.06 * (1 - prof)
    P(q, zona & ~racha, 'terra', (luz + 0.02)[zona & ~racha])
    P(q, zona & racha, 'terra', 0.2)
    acesa = zona & ~racha & np.roll(racha, 1, axis=0)
    P(q, acesa, 'terra', 0.9)


def ponte(W=556, PERNA=44, D=12, sem=3):
    """Ponte de tábuas no jeito do girau: tampo de tábuas atravessadas fugindo para trás,
    viga da frente, pilares roliços (os de trás na sombra) com escoras em X e corrimão."""
    VG = 5
    h = D + VG + PERNA + 1
    q = Quadro(W + 4, h + 10)
    o = 10                                     # folga em cima para o corrimão
    gb = o + VG + PERNA
    gf = q.h - 1
    vaos = list(range(6, W - 4, 70)) + [W - 7]
    for xb in vaos:                            # pilares de trás
        tora(q, xb + 4, o + 2, xb + 4, gb, 5, base=0.18)
    for a, b in zip(vaos[:-1], vaos[1:]):      # escoras de trás
        P(q, linha(q.w, q.h, (a + 6, o + 6), (b + 2, gb - 2), 2), 'madeira', 0.1)
        P(q, linha(q.w, q.h, (b + 2, o + 6), (a + 6, gb - 2), 2), 'madeira', 0.1)
    # tampo: tábuas atravessadas (riscos verticais), a de trás mais escura
    m = (q.yy >= o) & (q.yy < o + D) & (q.xx < W)
    tab = (q.xx // 5) % 7
    prof = (q.yy - o) / D
    luz = 0.58 + 0.04 * tab / 6 + 0.25 * prof
    P(q, m, 'madeira', np.clip(luz + 0.05 * ruido(q.h, q.w, (4, 1), sem), 0.05, 0.97)[m])
    P(q, m & (q.xx % 5 == 0), 'madeira', 0.18)
    falta = m & (((q.xx // 5) * 31 + sem) % 19 == 0) & (q.yy < o + D // 2)
    P(q, falta, 'madeira', 0.05)
    # viga da frente
    m = (q.yy >= o + D) & (q.yy < o + D + VG) & (q.xx < W)
    yv = q.yy - o - D
    P(q, m, 'madeira', np.where(yv == 0, 0.92, np.where(yv == VG - 1, 0.22, 0.5))[m])
    # pilares da frente com escoras em X e amarração
    for a, b in zip(vaos[:-1], vaos[1:]):
        P(q, linha(q.w, q.h, (a + 6, o + D + VG), (b, gf - 4), 2), 'madeira', 0.36)
        P(q, linha(q.w, q.h, (b, o + D + VG), (a + 6, gf - 4), 2), 'madeira', 0.3)
    for x in vaos:
        tora(q, x + 2, o + D - 1, x + 2, gf, 6, base=0.55)
        P(q, (q.xx >= x - 1) & (q.xx < x + 6) & ((q.yy == o + D + 1) | (q.yy == o + D + 3)), 'cal', 0.45)
    # corrimão de vara na beira de trás, com mourões
    for x in vaos:
        tora(q, x + 5, 1, x + 5, o + 2, 2, base=0.4)
    P(q, linha(q.w, q.h, (4, 2), (W, 2), 2), 'madeira', 0.45)
    return q, dict(o=o, D=D, VG=VG)


def carnauba(alt=72, sem=4):
    """Carnaúba: tronco fino e reto com os anéis das folhas velhas, copa em leques abertos
    (folhas em raios), as de baixo secas e caídas."""
    q = Quadro(70, alt + 4)
    X, Y = q.xx.astype(float), q.yy.astype(float)
    cx = 35
    chao = q.h - 2
    cy0 = 22
    tronco = (np.abs(X - cx - 0.04 * (chao - Y)) < 2.2) & (Y > cy0) & (Y <= chao)
    u = (X - cx - 0.04 * (chao - Y)) / 2.2
    anel = (Y.astype(int) % 3) == 0
    P(q, tronco, 'madeira', (0.55 - 0.3 * u - 0.15 * anel)[tronco])
    rng = np.random.default_rng(sem)
    cy = 22
    # leques: cada folha é um disco recortado em raios (folíolos), virado para um lado
    folhas = [(-2.6, 21, False), (-0.5, 20, False), (-1.6, 19, False), (-3.0, 19, True), (0.1, 18, True),
              (-1.1, 22, False), (-2.1, 21, False), (-1.55, 14, False)]
    for ang, L, seca in folhas:
        ang += rng.uniform(-0.1, 0.1)
        fx = cx + np.cos(ang) * L * 0.75
        fy = cy + np.sin(ang) * L * 0.55 + (6 if seca else 0)
        P(q, linha(q.w, q.h, (cx, cy), (fx, fy), 1), 'madeira', 0.4)       # pecíolo
        r = L * 0.62
        d = np.hypot(X - fx, (Y - fy) * 1.25)
        th = np.arctan2(Y - fy, X - fx)
        raio = np.cos((th - ang) * 9) > -0.2                                  # folíolos
        m = (d < r) & raio & (np.cos(th - ang) > -0.45)
        if seca:
            m &= Y > fy - 2
        lz = 0.7 - 0.35 * (X - cx) / 24 - 0.25 * (Y - fy) / r - 0.15 * (d / r)
        P(q, m, 'madeira' if seca else 'verde', np.clip(lz, 0.06, 0.95)[m])
    P(q, (((X - cx) / 7) ** 2 + ((Y - chao) / 2) ** 2 < 1), 'terra', 0.35)
    return q


def canoa(W=58, sem=5):
    """Canoa de tábuas encalhada, um pouco inclinada, vista de cima: costado de tábuas com a
    borda acesa, o fundo por dentro na sombra com um remo e um pouco de areia."""
    q = Quadro(W + 4, 18)
    X, Y = q.xx.astype(float), q.yy.astype(float)
    u = (X - 2) / W
    bico = np.clip(np.minimum(u, 1 - u) * 6, 0, 1)
    topo = 5 - 1.5 * (1 - bico) + 1.5 * u
    base = 15 - 4 * (1 - bico) ** 2 + 0.5 * u
    costado = (Y >= topo + 2) & (Y < base) & (u >= 0) & (u <= 1)
    P(q, costado, 'madeira', (0.55 - 0.25 * (Y - topo) / 10 + 0.06 * ((Y.astype(int) % 3) == 0))[costado])
    dentro = (Y >= topo - 2 * bico) & (Y < topo + 2) & (u > 0.04) & (u < 0.96)
    P(q, dentro, 'madeira', 0.18)
    P(q, (np.abs(Y - topo - 2) < 0.6) & costado, 'madeira', 0.9)          # borda acesa
    P(q, linha(q.w, q.h, (W * 0.3, 3), (W * 0.75, 6), 1), 'madeira', 0.7)  # remo
    P(q, (((X - W * 0.5) / (W * 0.55)) ** 2 + ((Y - base) / 2) ** 2 < 1) & (Y >= base - 1), 'terra', 0.3)
    return q


# ---------------------------------------------------------------- acampamento
def barraca(W=96, H=46, S=26, SH=14, sem=6, texto=True):
    """Barraca de lona da Volante em 2.5D: empena triangular de frente (lona acesa, porta
    aberta mostrando o escuro de dentro), o telhado fugindo para trás e para a direita (na
    sombra), mastro, cordas esticadas até as estacas e a barra suja de barro."""
    q = Quadro(W + S + 12, H + SH + 4)
    X, Y = q.xx.astype(float), q.yy.astype(float)
    x0, yb = 6, q.h - 2
    ap = (x0 + W / 2, yb - H)                                   # cume da frente
    # telhado (lado direito, fugindo para trás)
    tel = poly(q.w, q.h, [ap, (ap[0] + S, ap[1] - SH), (x0 + W + S, yb - SH - 6), (x0 + W, yb - 6)])
    lz = 0.38 - 0.12 * (Y - ap[1]) / H + 0.05 * np.sin(X / 3.0) + 0.04 * ruido(q.h, q.w, (3, 8), sem)
    P(q, tel, 'verde', lz[tel] * 0.8)
    parede = poly(q.w, q.h, [(x0 + W, yb - 6), (x0 + W + S, yb - SH - 6), (x0 + W + S, yb - SH), (x0 + W, yb)])
    P(q, parede, 'verde', 0.15)
    # empena da frente
    emp = poly(q.w, q.h, [ap, (x0 + W, yb - 6), (x0 + W, yb), (x0, yb), (x0, yb - 6)])
    k = (Y - ap[1]) / H
    lz = 0.62 - 0.12 * (X - x0) / W - 0.08 * k + 0.05 * ruido(q.h, q.w, (6, 2), sem + 1)
    lz = np.where(np.abs(X - ap[0]) < 0.6, lz - 0.15, lz)                      # costura do meio
    P(q, emp, 'verde', lz[emp])
    P(q, emp & (Y > yb - 5), 'terra', 0.35)                                     # barro na barra
    # porta: aba aberta mostrando o escuro, com a aba enrolada
    pw = W * 0.34
    porta = poly(q.w, q.h, [(ap[0], ap[1] + 10), (ap[0] + pw / 2, yb), (ap[0] - pw / 2, yb)])
    P(q, porta, 'madeira', 0.05)
    aba = poly(q.w, q.h, [(ap[0], ap[1] + 10), (ap[0] - pw / 2, yb), (ap[0] - pw / 2 - 5, yb), (ap[0] - 3, ap[1] + 12)])
    P(q, aba, 'verde', 0.75)
    if texto:                                                                   # estrela pintada
        sx, sy = x0 + W * 0.8, yb - 16
        for r_ in range(5):
            a = -np.pi / 2 + r_ * 2 * np.pi / 5
            P(q, linha(q.w, q.h, (sx, sy), (sx + 4 * np.cos(a), sy + 4 * np.sin(a)), 1), 'cal', 0.85)
    # mastro do cume, cordas e estacas
    tora(q, ap[0], ap[1] - 6, ap[0], ap[1] + 2, 2, base=0.5)
    for (ax, ay), (bx, by) in (((ap[0], ap[1] + 1), (x0 - 5, yb)), ((x0 + W, yb - 6), (x0 + W + 9, yb)),
                               ((ap[0] + S, ap[1] - SH + 1), (x0 + W + S + 8, yb - SH + 6))):
        P(q, linha(q.w, q.h, (ax, ay), (bx, by), 1), 'cal', 0.5)
        P(q, (np.abs(X - bx) < 1) & (Y >= by - 3) & (Y <= by), 'madeira', 0.4)
    return q


def torre(alt=96, W=40, S=10, SH=7, sem=7):
    """Torre de vigia de toras em 2.5D: quatro pernas (as de trás na sombra, para cima e
    para a direita), escoras em X, plataforma com parapeito de tábuas, telhadinho de zinco
    e escada encostada."""
    q = Quadro(W + S + 10, alt + SH + 10)
    X, Y = q.xx.astype(float), q.yy.astype(float)
    yb = q.h - 2
    pt = yb - alt + 24                       # piso da plataforma (frente)
    xl, xr = 5, 5 + W
    # pernas de trás
    for x in (xl + S, xr + S):
        tora(q, x, pt - SH, x - 2, yb - SH, 4, base=0.15)
    for a, b in ((xl + S, xr + S),):
        for y0 in range(pt - SH, yb - SH - 14, 22):
            P(q, linha(q.w, q.h, (a, y0), (b - 2, y0 + 22), 2), 'madeira', 0.1)
            P(q, linha(q.w, q.h, (b - 2, y0), (a, y0 + 22), 2), 'madeira', 0.1)
    # escoras do lado (direita, fugindo para trás)
    for y0 in range(pt, yb - 14, 22):
        P(q, linha(q.w, q.h, (xr, y0), (xr + S - 1, y0 + 22 - SH), 2), 'madeira', 0.2)
    # pernas da frente, abrindo para baixo, e X da frente
    pe_l, pe_r = xl - 3, xr + 3
    for a, b in ((xl, pe_l), (xr, pe_r)):
        tora(q, a, pt, b, yb, 5, base=0.55)
    for y0 in range(pt + 2, yb - 14, 22):
        f0 = (y0 - pt) / (yb - pt)
        f1 = (y0 + 22 - pt) / (yb - pt)
        la, ra = xl - 3 * f0, xr + 3 * f0
        lb, rb = xl - 3 * f1, xr + 3 * f1
        P(q, linha(q.w, q.h, (la + 2, y0), (rb - 2, y0 + 20), 2), 'madeira', 0.38)
        P(q, linha(q.w, q.h, (ra - 2, y0), (lb + 2, y0 + 20), 2), 'madeira', 0.32)
    # parapeito de trás (aparece por cima do piso, na sombra) e os postes de trás do telhado
    tras = (X >= xl - 3 + S) & (X <= xr + 3 + S) & (Y >= pt - SH - 14) & (Y < pt - SH)
    P(q, tras, 'madeira', np.where(((Y.astype(int) - (pt - SH - 14)) % 5) == 0, 0.32, 0.16)[tras])
    for x in (xl - 1 + S, xr + 1 + S):
        tora(q, x, pt - 30 - SH, x, pt - 14 - SH, 2, base=0.2)
    # plataforma: piso visto de cima e parapeito de tábuas
    piso = poly(q.w, q.h, [(xl - 3, pt), (xr + 3, pt), (xr + 3 + S, pt - SH), (xl - 3 + S, pt - SH)])
    P(q, piso, 'madeira', 0.7)
    par_lado = poly(q.w, q.h, [(xr + 3, pt - 14), (xr + 3 + S, pt - 14 - SH), (xr + 3 + S, pt - SH), (xr + 3, pt)])
    P(q, par_lado, 'madeira', (0.3 + 0.05 * ((X.astype(int) % 3) == 0))[par_lado])
    par = (X >= xl - 3) & (X <= xr + 3) & (Y >= pt - 14) & (Y < pt + 3)
    tab = (Y.astype(int) - (pt - 14)) % 5
    P(q, par, 'madeira', np.where(tab == 0, 0.8, np.where(tab == 4, 0.25, 0.55) - 0.12 * (X - xl) / W)[par])
    # telhadinho de zinco em duas águas, com os postes
    for x in (xl - 1, xr + 1):
        tora(q, x, pt - 30, x, pt - 14, 2, base=0.45)
    tel = poly(q.w, q.h, [(xl - 7, pt - 28), (xr + 7, pt - 28), (xr + 7 + S, pt - 28 - SH), (xl - 7 + S, pt - 28 - SH)])
    P(q, tel, 'azul', (0.6 + 0.12 * ((X.astype(int) % 4) == 0) - 0.15 * (Y < pt - 31))[tel])
    beira = (X >= xl - 7) & (X <= xr + 7) & (Y >= pt - 28) & (Y < pt - 26)
    P(q, beira, 'azul', 0.3)
    # escada encostada na frente
    for x in (xr - 9, xr - 3):
        P(q, linha(q.w, q.h, (x + 4, pt + 2), (x + 8, yb), 1), 'madeira', 0.6)
    for y in range(pt + 6, yb, 6):
        f = (y - pt) / (yb - pt)
        P(q, linha(q.w, q.h, (xr - 5 + 4 * f, y), (xr + 1 + 4 * f, y), 1), 'madeira', 0.75)
    return q


def leito(q, xt, yt, wt, xb, yb, wb, sem=8):
    """O leito do rio seco vindo do fundo até a beira de baixo da tela: estreito e longe em
    cima (sai de uma grota entre os morros), largo embaixo. Barro rachado no meio, areia
    clara e seixos nas beiras, barranquinho de terra (a margem da esquerda acesa, a da
    direita na sombra) e o chão normal entrando em manchas na beira (sem corte reto)."""
    X, Y = q.xx.astype(float), q.yy.astype(float)
    t = np.clip((Y - yt) / (yb - yt), 0, 1)
    tp = t ** 1.6                                  # perspectiva: estreita rápido no longe
    meio = xt + (xb - xt) * tp + 6 * np.sin(t * 5 + sem) * t
    larg = (wt + (wb - wt) * tp) / 2
    n = ruido(q.h, q.w, (6, 14), sem) * (2 + 6 * t)
    d = np.abs(X - meio) - larg - n
    dentro = (Y >= yt) & (d < 0)
    beira = (Y >= yt) & (d >= 0) & (d < 2 + 3 * t)
    areia = dentro & (d > -(3 + 7 * t))
    antes = q.img.copy()
    lama(q, -40, q.w + 40, int(yt), q.h, sem=sem)     # barro rachado no miolo
    miolo = dentro & ~areia
    q.img[~miolo] = antes[~miolo]
    # areia clara e seixos na beira de dentro
    lz = 0.62 + 0.08 * ruido(q.h, q.w, (1, 3), sem + 1) - 0.1 * (1 - t)
    P(q, areia, 'cal', (lz - 0.12)[areia])
    rng = np.random.default_rng(sem)
    for _ in range(int(q.w * 0.35)):
        y = rng.uniform(yt, q.h)
        tt = (y - yt) / (yb - yt)
        r = 0.8 + 2.2 * tt
        lado = rng.choice((-1, 1))
        mm = xt + (xb - xt) * tt ** 1.6
        ll = (wt + (wb - wt) * tt ** 1.6) / 2
        x = mm + lado * (ll + rng.uniform(-8 * tt - 2, 10 * tt + 3))
        pm = ((X - x) / r) ** 2 + ((Y - y) / (r * 0.6)) ** 2 < 1
        P(q, pm, 'cal', np.where(Y < y, 0.85, 0.42)[pm])
    # barranquinho: a margem da esquerda (virada para a direita) na sombra, a da direita
    # (virada para a luz que vem da esquerda) acesa
    esq = beira & (X < meio)
    P(q, esq, 'terra', 0.22)
    dir_ = beira & (X >= meio)
    P(q, dir_, 'terra', (0.8 - 0.1 * (d / (2 + 3 * t)))[dir_])
    return dentro
