"""Peças baixas do plano do jogo desenhadas em 2.5D de verdade (vista de frente, um pouco de cima):
tampo indo para trás em perspectiva, pernas da frente e de trás, sombra embaixo."""
import numpy as np
from PIL import Image, ImageDraw
from caatinga_ms import Quadro, ruido


def P(q, m, rampa, v):
    full = np.zeros(m.shape)
    v = np.asarray(v, float)
    if v.ndim == 0:
        full[:] = v
    elif v.shape == m.shape:
        full = v
    else:
        full[m] = v
    q.pinta(m, rampa, np.clip(full, 0, 0.999))


def poly(w, h, pts):
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=1)
    return np.array(im, bool)


def linha(w, h, p0, p1, larg=1):
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).line([tuple(p0), tuple(p1)], fill=1, width=larg)
    return np.array(im, bool)


def tora(q, x0, y0, x1, y1, larg, rampa='madeira', base=0.5):
    """Perna/viga roliça: luz da esquerda (cilindro)."""
    m = linha(q.w, q.h, (x0, y0), (x1, y1), larg)
    xs = q.xx[m]
    # posição dentro da largura, pela distância à linha central
    cx = x0 + (x1 - x0) * np.clip((q.yy[m] - y0) / max(1, (y1 - y0)), 0, 1)
    u = (xs - cx) / max(1, larg / 2)
    luz = base + 0.28 * (-u) - 0.1 * np.abs(u) ** 2
    n = ruido(q.h, q.w, (6, 1), int(x0 * 7 + y0))[m] * 0.06
    P(q, m, rampa, np.clip(luz + n, 0.02, 0.97))
    return m


def girau(W=84, PERNA=26, D=16, INSET=6, carga=True, sem=1):
    """Girau de tábuas: tampo de tábuas correndo para trás, viga da frente, pernas roliças,
    escoras em X na frente e pernas de trás (mais escuras) aparecendo por baixo."""
    VG = 5
    h = D + VG + PERNA + 1
    q = Quadro(W + 2, h)
    gb = VG + PERNA                       # chão de trás (D acima do chão da frente)
    gf = h - 1
    # pernas de trás e viga de trás (na sombra)
    for xb in (INSET + 1, W // 2 - 1, W - INSET - 5):
        tora(q, xb + 2, 2, xb + 2, gb, 4, base=0.18)
    m = poly(q.w, q.h, [(INSET, 1), (W - INSET, 1), (W - INSET, 4), (INSET, 4)])
    P(q, m, 'madeira', 0.15)
    # escora em X de trás (bem escura)
    for a, b in ((INSET + 3, W // 2), (W // 2, W - INSET - 3)):
        P(q, linha(q.w, q.h, (a, 5), (b, gb - 2), 2), 'madeira', 0.1)
        P(q, linha(q.w, q.h, (b, 5), (a, gb - 2), 2), 'madeira', 0.1)
    # tampo: tábuas que fogem para o meio
    nt = 8
    for i in range(nt):
        fa, fb = W * i / nt, W * (i + 1) / nt
        ba = INSET + (W - 2 * INSET) * i / nt
        bb = INSET + (W - 2 * INSET) * (i + 1) / nt
        m = poly(q.w, q.h, [(ba, 0), (bb - 1, 0), (fb - 1, D), (fa, D)])
        prof = q.yy[m] / D                    # 0 fundo, 1 frente
        tom = 0.62 + 0.18 * ((i * 37 + sem) % 5) / 4
        veio = ruido(q.h, q.w, (1, 5), sem * 10 + i)[m] * 0.08
        P(q, m, 'madeira', np.clip(tom - 0.18 * (1 - prof) + veio, 0.05, 0.97))
        # fresta entre tábuas
        P(q, linha(q.w, q.h, (ba, 0), (fa, D), 1) & (q.xx > 0), 'madeira', 0.12)
        # prego na frente
        P(q, (q.yy == D - 2) & (q.xx == int(fa + 3)), 'madeira', 0.08)
    # uma tábua quebrada/faltando na beira de trás
    k = (sem * 3) % (nt - 2) + 1
    ba = INSET + (W - 2 * INSET) * k / nt
    P(q, poly(q.w, q.h, [(ba, 0), (ba + 7, 0), (ba + 6, 4), (ba + 1, 3)]), 'madeira', 0.05)
    # viga da frente
    m = (q.yy >= D) & (q.yy < D + VG) & (q.xx < W)
    luz = np.where(q.yy[m] == D, 0.92, np.where(q.yy[m] == D + VG - 1, 0.22, 0.5))
    P(q, m, 'madeira', luz + ruido(q.h, q.w, (1, 6), sem + 5)[m] * 0.06)
    # pernas da frente com escoras em X
    xs = (1, W // 2 - 2, W - 6)
    for a, b in zip(xs[:-1], xs[1:]):
        P(q, linha(q.w, q.h, (a + 4, D + VG), (b, gf - 3), 2), 'madeira', 0.36)
        P(q, linha(q.w, q.h, (b, D + VG), (a + 4, gf - 3), 2), 'madeira', 0.3)
        # amarração no cruzamento
        cx, cy = (a + b + 4) // 2, (D + VG + gf - 3) // 2
        P(q, ((q.xx - cx) ** 2 + (q.yy - cy) ** 2 < 4), 'cal', 0.35)
    for x in xs:
        tora(q, x + 2, D - 1, x + 2, gf, 5, base=0.55)
        # amarração de corda na viga
        P(q, (q.xx >= x) & (q.xx < x + 5) & ((q.yy == D + 1) | (q.yy == D + 3)), 'cal', 0.45)
    if carga:
        # cabaça e saco em cima do tampo
        cx, cy = int(W * 0.72), D - 6
        m = ((q.xx - cx) / 5) ** 2 + ((q.yy - cy) / 6) ** 2 < 1
        P(q, m, 'verde', np.clip(0.55 - (q.xx[m] - cx) * 0.06 - (q.yy[m] - cy) * 0.04, 0.05, 0.95))
        P(q, (q.xx == cx) & (q.yy >= cy - 9) & (q.yy < cy - 5), 'madeira', 0.3)
        sx, sy = int(W * 0.22), D - 8
        m = ((q.xx - sx) / 9) ** 2 + ((q.yy - sy) / 6) ** 2 < 1
        P(q, m, 'cal', np.clip(0.6 - (q.xx[m] - sx) * 0.04 - (q.yy[m] - sy) * 0.06, 0.05, 0.95))
        P(q, (q.xx == sx + 8) & (q.yy == sy - 3), 'cal', 0.1)
    return q, dict(D=D, topo_frente=D, topo_tras=0, chao=gf, chao_tras=gb)


def laje(W=104, ALT=12, D=16, sem=3, rampa='cal'):
    """Laje de pedra: tampo com rachaduras e líquen, frente em camadas, quina iluminada."""
    h = D + ALT + 1
    q = Quadro(W + 2, h)
    r = 3
    topo = poly(q.w, q.h, [(r + 2, 0), (W - 6, 0), (W - 1, D), (0, D)])
    n = ruido(q.h, q.w, (3, 5), sem)
    prof = q.yy / D
    P(q, topo, rampa, np.clip(0.62 + 0.14 * n - 0.2 * (1 - prof), 0.05, 0.97)[topo])
    # rachaduras
    rng = np.random.default_rng(sem)
    for _ in range(4):
        x = rng.uniform(10, W - 10); y = 0
        pts = [(x, y)]
        while y < D:
            y += rng.uniform(2, 4); x += rng.uniform(-3, 3); pts.append((x, y))
        im = Image.new('L', (q.w, q.h)); ImageDraw.Draw(im).line(pts, fill=1)
        m = np.array(im, bool) & topo
        P(q, m, rampa, 0.1)
    # líquen
    lq = (ruido(q.h, q.w, (2, 2), sem + 9) > 1.1) & topo
    P(q, lq, 'verde', 0.55)
    # frente em camadas
    fr = (q.yy >= D) & (q.yy < h) & (q.xx < W) & ~((q.xx < 2) & (q.yy > h - 3))
    cam = ((q.yy - D) // 4) % 2
    P(q, fr, rampa, np.clip(0.36 - 0.08 * cam + 0.06 * n - 0.1 * (q.yy - D) / ALT, 0.03, 0.9)[fr])
    P(q, fr & ((q.yy - D) % 4 == 3), rampa, 0.1)
    P(q, (q.yy == D) & (q.xx < W), rampa, 0.95)       # quina de cima acesa
    # lado direito (sombra) e esquerdo (luz)
    P(q, poly(q.w, q.h, [(W - 6, 0), (W + 1, D), (W + 1, h - 1), (W - 1, h - 1), (W - 1, D)]), rampa, 0.1)
    return q, dict(D=D, topo_frente=D, topo_tras=0, chao=h - 1, chao_tras=h - 1 - D)


def roda(q, cx, cy, r, base=0.5, sem=0):
    """Roda maciça de carro de boi: tábuas, aro de ferro, cubo."""
    d = np.sqrt((q.xx - cx) ** 2 + (q.yy - cy) ** 2)  # elipse (roda vista um pouco de lado)
    disco = d < r
    P(q, disco, 'madeira', np.clip(base + 0.25 * (cx - q.xx) / r - 0.1 * (d / r) ** 2, 0.03, 0.95)[disco])
    P(q, disco & (np.abs(q.yy - cy) % 5 == 0), 'madeira', base - 0.3)  # juntas das tábuas
    aro = disco & (d > r - 1.6)
    P(q, aro, 'azul', np.clip(0.35 + 0.4 * (cx - q.xx[aro]) / r, 0.05, 0.9))
    cubo = d < r * 0.28
    P(q, cubo, 'madeira', base - 0.25)
    P(q, d < r * 0.12, 'madeira', 0.05)


def carroca(W=78, D=14, sem=5):
    """Carro de boi largado: caixa de tábuas com fueiros, carga de capim, rodas maciças
    (a de trás mais alta e escura), cabeçalho no chão."""
    R = max(13, W // 6)
    h = D + 18 + R + 4
    q = Quadro(W + 34, h)
    gf = h - 1
    gb = gf - D
    cx = 22 + W // 2 - 4
    # roda de trás (atrás da caixa, mais alta)
    roda(q, cx + 6, gb - R, R, base=0.2, sem=sem)
    # fundo e chão da caixa (vistos de cima)
    y0 = gf - R - 18                     # beira de cima da tábua da frente
    m = poly(q.w, q.h, [(22 + 4, y0 - D), (22 + W - 4, y0 - D), (22 + W, y0), (22, y0)])
    P(q, m, 'madeira', 0.2)
    # tábua de trás (lado de dentro, sombra)
    P(q, poly(q.w, q.h, [(26, y0 - D - 5), (22 + W - 4, y0 - D - 5), (22 + W - 4, y0 - D), (26, y0 - D)]), 'madeira', 0.42)
    P(q, (q.yy == y0 - D - 5) & (q.xx >= 26) & (q.xx < 22 + W - 4), 'madeira', 0.75)
    # carga de capim seco amontoada
    rng = np.random.default_rng(sem)
    for _ in range(26):
        x = rng.uniform(30, 22 + W - 8); y = rng.uniform(y0 - D - 7, y0 - 3)
        rx, ry = rng.uniform(4, 8), rng.uniform(2.5, 4)
        mm = ((q.xx - x) / rx) ** 2 + ((q.yy - y) / ry) ** 2 < 1
        P(q, mm, 'meio', np.clip(0.75 - (q.yy[mm] - y) / ry * 0.18 - (q.xx[mm] - x) / rx * 0.08 + rng.uniform(-0.08, 0.08), 0.05, 0.97))
    for _ in range(30):
        x = rng.uniform(28, 22 + W - 6); y = rng.uniform(y0 - D - 6, y0 - 4)
        P(q, linha(q.w, q.h, (x, y), (x + rng.uniform(-3, 3), y - rng.uniform(2, 5))), 'meio', 0.95)
    # tábuas da frente da caixa
    for i in range(3):
        m = (q.xx >= 22) & (q.xx < 22 + W) & (q.yy >= y0 + i * 6) & (q.yy < y0 + i * 6 + 6)
        tom = 0.55 + 0.08 * ((i + sem) % 3)
        P(q, m, 'madeira', np.clip(tom + ruido(q.h, q.w, (1, 6), sem + i)[m] * 0.08 - 0.12 * (q.xx[m] - 22) / W, 0.05, 0.95))
        P(q, m & (q.yy == y0 + i * 6), 'madeira', tom + 0.25)
        P(q, m & (q.yy == y0 + i * 6 + 5), 'madeira', 0.18)
    # fueiros (estacas) com o topo passando da carga
    for x in range(24, 22 + W, 14):
        tora(q, x, y0 - 8, x, y0 + 18, 3, base=0.45)
    # eixo e roda da frente
    P(q, (q.xx >= 22) & (q.xx < 22 + W) & (q.yy >= y0 + 18) & (q.yy < y0 + 20), 'madeira', 0.15)
    roda(q, cx, gf - R, R, base=0.55, sem=sem)
    # cabeçalho (lança) no chão, para a esquerda
    tora(q, 22, y0 + 16, 1, gf - 1, 3, base=0.5)
    return q, dict(D=D, topo_frente=y0, topo_tras=y0 - D, chao=gf, chao_tras=gb)


def sacos(W=50, ALT=18, D=14, sem=7):
    """Trincheira de sacos de areia: fileiras de sacos estufados na frente e a fileira de trás
    aparecendo por cima, mais escura (profundidade de verdade, não esticada)."""
    h = D + ALT + 2
    q = Quadro(W + 4, h)
    rng = np.random.default_rng(sem)
    linhas = max(2, ALT // 7)
    def saco(cx, cy, rx, ry, base):
        m = ((q.xx - cx) / rx) ** 2 + ((q.yy - cy) / ry) ** 2 < 1
        luz = base + 0.3 * (cx - q.xx) / rx * 0.5 - 0.35 * (q.yy - cy) / ry
        P(q, m, 'cal', np.clip(luz + ruido(q.h, q.w, (1, 1), int(cx * 3 + cy))[m] * 0.05 if False else luz, 0.03, 0.95))
        # costura e orelha amarrada
        P(q, m & (np.abs(q.xx - (cx + rx - 2)) < 0.6), 'cal', base - 0.25)
        return m
    # fileira de trás (em cima, recuada D px), escura
    for i in range(int(W / 12) + 1):
        saco(4 + i * 12 + 6, 5, 7, 4, 0.32)
    # fileiras da frente, desencontradas, de baixo para cima (a de cima por último)
    for r in range(linhas):
        cy = h - 4 - r * 7
        off = 6 if r % 2 else 0
        for i in range(int(W / 12) + 1):
            cx = 2 + off + i * 12 + 5
            if cx > W:
                continue
            saco(cx, cy, 7, 4.3, 0.62 + rng.uniform(-0.06, 0.06))
    # tampo: a fileira de cima vista de cima (sacos deitados indo para trás)
    for i in range(int(W / 12) + 1):
        saco(4 + i * 12 + 6, D - 3 + 2, 7, 5, 0.78)
    # um furado vazando areia
    fx = int(W * 0.6)
    P(q, (np.abs(q.xx - fx) <= 1) & (q.yy > h - 6), 'terra', 0.85)
    return q, dict(D=D, chao=h - 1)


if __name__ == '__main__':
    out = Image.new('RGBA', (400, 80), (200, 170, 130, 255))
    x = 4
    for q, _ in (girau(), laje(), carroca()):
        im = Image.fromarray(q.rgba(), 'RGBA')
        out.alpha_composite(im, (x, 78 - im.height)); x += im.width + 8
    out.resize((1600, 320), Image.NEAREST).save('pecas25.png')
