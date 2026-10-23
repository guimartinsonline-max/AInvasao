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
    # carga: fardos de feno amarrados (blocos com tampo, palha riscada e corda), bem
    # diferentes do chão (23/10)
    rng = np.random.default_rng(sem)
    X, Y = q.xx, q.yy
    fw, fh, fd = 22, 11, 5
    palha = ruido(q.h, q.w, (0.4, 2.5), sem + 3)
    for fila, (yb_, x_ini, n) in enumerate(((y0 + 2, 26, int((W - 8) / fw)), (y0 + 2 - fh, 26 + fw // 2, int((W - 8) / fw) - 1))):
        for k in range(max(1, n)):
            xa = x_ini + k * fw + rng.integers(-1, 2)
            if xa + fw > 22 + W - 2:
                continue
            fr = (X >= xa) & (X < xa + fw - 1) & (Y >= yb_ - fh) & (Y < yb_)
            tp = poly(q.w, q.h, [(xa, yb_ - fh), (xa + fw - 1, yb_ - fh), (xa + fw + 2, yb_ - fh - fd), (xa + 3, yb_ - fh - fd)])
            ld = poly(q.w, q.h, [(xa + fw - 1, yb_ - fh), (xa + fw + 2, yb_ - fh - fd), (xa + fw + 2, yb_ - fd), (xa + fw - 1, yb_)])
            P(q, ld, 'telha', 0.3)
            P(q, fr, 'cal', np.clip(0.62 + 0.18 * palha - 0.1 * (Y - (yb_ - fh)) / fh, 0.2, 0.9))
            P(q, fr & (palha > 0.9), 'telha', 0.75)                    # palha dourada
            P(q, tp, 'cal', np.clip(0.86 + 0.08 * palha, 0.5, 0.97))
            for cc in (xa + 6, xa + fw - 7):                            # cordas
                P(q, fr & (np.abs(X - cc) < 0.6), 'madeira', 0.2)
                P(q, tp & (np.abs(X - cc - (yb_ - fh - Y) * 3 / fd) < 0.7), 'madeira', 0.3)
            # fiapos soltos saindo das beiradas
            for _ in range(4):
                x = rng.uniform(xa, xa + fw); y = yb_ - fh - rng.uniform(0, 2)
                P(q, linha(q.w, q.h, (x, y), (x + rng.uniform(-2, 2), y - rng.uniform(2, 4))), 'cal', 0.95)
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


def rochedo(W=110, TOPO=20, BAIXO=60, D=19, sem=3, rampa='cal'):
    """Rochedo de arenito saindo do chão da frente: tampo irregular onde se pisa (o meio dele
    na altura do sólido), quina gasta e a frente em camadas que descem até sair pela borda de
    baixo da tela. TOPO: px do meio do tampo até a quina da frente; BAIXO: px da quina até o
    pé (fora da tela). Sem canto reto: as beiradas são tortas e o pé alarga."""
    rng = np.random.default_rng(sem)
    h = D + BAIXO
    q = Quadro(W + 16, h)
    X, Y = q.xx, q.yy
    ox = 8
    xs = np.arange(q.w)
    n1 = ruido(1, q.w, 4, sem)[0]
    n2 = ruido(1, q.w, 9, sem + 1)[0]
    # silhueta: lados tortos, o pé abre para fora
    def lado(y, esq):
        k = (y - D) / max(1, BAIXO)
        base = 3 + 2 * np.sin(y * 0.21 + sem) + 1.2 * np.sin(y * 0.53 + sem * 2)
        return (ox + base - 5 * np.clip(k, 0, 1)) if esq else (ox + W - base + 5 * np.clip(k, 0, 1))
    xe = np.array([lado(y, True) for y in range(h)])
    xd = np.array([lado(y, False) for y in range(h)])
    # tampo: borda de trás e da frente tortas, cantos arredondados
    tras = 1.5 + 1.3 * n1 + 0.0 * xs
    frente = D + 1.2 * n2
    u = np.clip((xs - ox) / W, 0, 1)
    canto = 6 * (1 - np.sqrt(np.clip(1 - ((u - 0.5) / 0.5) ** 2 * 0.85, 0, 1)))
    tras = tras + canto
    corpo = (X >= xe[Y]) & (X < xd[Y]) & (Y >= tras[X])
    tampo = corpo & (Y < frente[X])
    face = corpo & ~tampo
    # luz do tampo: claro, mais escuro para trás, granulado e bacias de água da chuva
    nt = ruido(h, q.w, (1.2, 3), sem + 2)
    prof = np.clip((Y - tras[X]) / np.maximum(1, frente[X] - tras[X]), 0, 1)
    P(q, tampo, rampa, (0.66 + 0.08 * nt - 0.14 * (1 - prof) - 0.1 * (X - ox) / W)[tampo])
    bacia = tampo & (ruido(h, q.w, (1.5, 4), sem + 3) > 1.5)
    P(q, bacia, rampa, 0.42)
    # face: camadas do arenito acompanhando a quina, blocos e fissuras, mais escura embaixo
    camada = ((Y - frente[X]) + 2.5 * ruido(h, q.w, (2, 14), sem + 4)) / 6.0
    banda = np.floor(camada)
    tom = 0.5 + 0.08 * ((banda * 37 + sem) % 3 - 1)
    lateral = np.clip((X - xe[Y]) / np.maximum(1, xd[Y] - xe[Y]), 0, 1)
    luz = tom + 0.16 * (1 - lateral) ** 2 - 0.22 * lateral ** 3 - 0.22 * np.clip((Y - D) / BAIXO, 0, 1) \
        + 0.05 * ruido(h, q.w, (1, 3), sem + 5)
    luz = np.where((camada - banda) < 0.16, luz - 0.18, luz)          # junta entre camadas
    luz = np.where(((camada - banda) > 0.16) & ((camada - banda) < 0.3), luz + 0.06, luz)  # beira acesa
    P(q, face, rampa, luz[face])
    # fissuras verticais com a beirada esquerda acesa
    for _ in range(int(W / 22) + 1):
        x = rng.uniform(ox + 8, ox + W - 8); y = float(frente[int(x)] + rng.uniform(0, 4))
        comp = rng.uniform(10, BAIXO * 0.8)
        for _ in range(int(comp)):
            xi, yi = int(round(x)), int(round(y))
            if 0 <= yi < h and face[yi, xi]:
                P(q, (X == xi) & (Y == yi), rampa, 0.08)
                if xi - 1 >= 0 and face[yi, xi - 1]:
                    P(q, (X == xi - 1) & (Y == yi), rampa, 0.72)
            x += rng.choice([-0.6, 0, 0, 0.6]); y += 1
    # quina da frente gasta e acesa
    quina = face & (Y - frente[X] < 1.5) & (Y - frente[X] >= 0)
    P(q, quina, rampa, 0.92)
    # líquen e capim no pé das camadas
    lq = (face | tampo) & (ruido(h, q.w, (1.5, 2), sem + 6) > 1.55)
    P(q, lq, 'verde', 0.5)
    for _ in range(int(W / 18)):
        x = int(rng.uniform(ox + 4, ox + W - 4)); y = int(rng.uniform(D + 8, h - 4))
        if face[y, x]:
            for d in range(-2, 3):
                hh = 3 + (2 - abs(d))
                P(q, (X == x + d) & (Y >= y - hh) & (Y <= y), 'verde', 0.35 + 0.1 * (d < 0))
    return q, dict(D=D, chao=h - 1)


def sacos2(W=56, ALT=26, D=19, sem=7):
    """Trincheira de sacos de estopa: cada saco é um travesseiro estufado com as orelhas
    amarradas, trama da estopa, costura e vinco; fileiras desencontradas e, em cima, os
    sacos deitados indo para trás (o tampo), com sombra entre eles."""
    rng = np.random.default_rng(sem)
    h = D + ALT + 2
    q = Quadro(W + 8, h)
    X, Y = q.xx, q.yy
    tram = ((X + Y) % 3 == 0) | ((X - Y) % 4 == 0)

    def saco(cx, cy, rx, ry, base, vira=1.0):
        # travesseiro: superelipse, mais cheio no meio
        d = (np.abs((X - cx) / rx) ** 2.6 + np.abs((Y - cy) / ry) ** 2.2)
        anel = (d < 1.22) & ~(d < 1)
        P(q, anel, 'meio', 0.08)
        m = d < 1
        nx, ny = (X - cx) / rx, (Y - cy) / ry
        luz = base + 0.22 * (-nx * 0.6 - ny) * vira - 0.18 * d
        luz = np.where(tram, luz - 0.05, luz)
        P(q, m, 'meio', np.clip(luz, 0.02, 0.97)[m])
        # orelhas amarradas nas pontas
        for s in (-1, 1):
            ox_ = cx + s * (rx + 0.5)
            o = (np.abs(X - ox_) <= 1) & (np.abs(Y - cy) <= 1)
            P(q, o, 'meio', base - 0.12)
        # costura de cima e vinco de baixo
        P(q, m & (np.abs(Y - (cy - ry * 0.55)) < 0.5) & ((X % 2) == 0), 'meio', base - 0.25)
        P(q, m & (np.abs(Y - (cy + ry * 0.5)) < 0.5) & (np.abs(X - cx) < rx * 0.5), 'meio', base - 0.3)
        return m

    # tampo: duas fileiras de sacos deitados, a de trás menor e mais escura
    for r, (yy, esc, b) in enumerate(((5, 0.85, 0.5), (D - 4, 1.0, 0.74))):
        off = 5 if r % 2 else 0
        n = int(W / (18 * esc)) + 2
        for i in range(n):
            cx = 7 + off + i * 18 * esc + rng.uniform(-1, 1)
            if cx > W + 2:
                continue
            saco(cx, yy + rng.uniform(-0.5, 0.5), 10.5 * esc, 6.5 * esc, b + rng.uniform(-0.05, 0.05))
    # frente: fileiras de baixo para cima (a de cima por último), desencontradas
    linhas = max(2, int(round(ALT / 9.5)))
    for r in range(linhas):
        cy = h - 7 - r * 9.4
        off = 9 if r % 2 else 0
        for i in range(int(W / 18) + 2):
            cx = 7 + off + i * 18 + rng.uniform(-0.8, 0.8)
            if cx > W + 3:
                continue
            saco(cx, cy, 10.5, 6.6, 0.6 + rng.uniform(-0.07, 0.05))
    # um saco furado vazando areia
    fx = int(W * 0.6)
    P(q, (np.abs(X - fx) <= 1) & (Y > h - 7) & (Y < h), 'terra', 0.85)
    P(q, (np.abs(X - fx) <= 3) & (Y == h - 1), 'terra', 0.75)
    return q, dict(D=D, chao=h - 1)


def sacos3(W=56, ALT=36, sem=7):
    """Barricada de sacos no jeito do Metal Slug (23/10): pilha em pirâmide, cada fileira um
    pouco mais estreita e por cima da de baixo como telha (a de cima tapa a beirada da de
    baixo), sacos estufados de estopa clara com luz de cima e da esquerda, vinco escuro entre
    eles, orelhas amarradas; duas estacas de madeira escorando, cruzadas em cima. Sem tampo:
    é um objeto de frente, apoiado no chão com sombra."""
    rng = np.random.default_rng(sem)
    h = ALT + 8
    q = Quadro(W + 10, h)
    X, Y = q.xx.astype(float), q.yy.astype(float)
    cx0 = (W + 10) / 2
    # estacas (atrás das fileiras de cima): saem do chão dos lados e cruzam acima do topo
    topo = h - ALT
    tora(q, cx0 + W * 0.34, h - 2, cx0 - 5, topo - 6, 3, base=0.45)
    linhas = max(3, int(round(ALT / 8)))
    for r in range(linhas):
        cy = h - 6 - r * (ALT - 6) / (linhas - 0.4)
        larg = W * (1 - 0.6 * r / linhas)
        n = max(1, int(round(larg / 15)))
        passo = larg / n
        for k in range(n):
            cx = cx0 - larg / 2 + passo * (k + 0.5) + rng.uniform(-1, 1)
            rx, ry = passo / 2 + 2.5, 5.6
            inc = rng.uniform(-0.12, 0.12)
            nx = (X - cx) / rx
            ny = (Y - cy - inc * (X - cx)) / ry
            d = np.abs(nx) ** 2.4 + np.abs(ny) ** 2
            m = d < 1
            anel = (d < 1.25) & ~m
            P(q, anel, 'cal', 0.12)
            luz = 0.78 - 0.32 * ny - 0.14 * nx - 0.28 * d ** 2
            luz = np.where(((X + Y) % 3 == 0) & m, luz - 0.06, luz)       # trama da estopa
            luz = np.where(m & (ny > 0.55), luz - 0.18, luz)               # barriga apoiada
            P(q, m, 'cal', np.clip(luz, 0.04, 0.97))
            # vinco no meio e costura em cima
            P(q, m & (np.abs(X - cx - 0.3 * rx) < 0.6) & (ny > -0.2) & (ny < 0.6), 'cal', 0.22)
            P(q, m & (np.abs(ny + 0.55) < 0.12) & (np.abs(nx) < 0.7) & ((X.astype(int) % 2) == 0), 'cal', 0.4)
            # orelha amarrada numa ponta
            s_ = 1 if (k + r) % 2 else -1
            o = (np.abs(X - (cx + s_ * (rx + 0.3))) <= 1.2) & (np.abs(Y - cy) <= 1.4)
            P(q, o, 'cal', 0.55)
            P(q, o & (Y > cy), 'cal', 0.25)
    # a outra estaca na frente, cruzando a de trás em cima, com a corda amarrando
    tora(q, cx0 - W * 0.3, h - 1, cx0 + 6, topo - 6, 3, base=0.8)
    P(q, (np.abs(X - cx0) < 2.5) & (np.abs(Y - (topo - 1)) < 1.2), 'cal', 0.35)
    # areia escorrendo de um saco furado
    fx = int(cx0 + W * 0.18)
    P(q, (np.abs(X - fx) <= 1) & (Y > h - 7), 'terra', 0.8)
    P(q, (np.abs(X - fx) <= 3) & (Y >= h - 2), 'terra', 0.7)
    return q, dict(chao=h - 1)


def rochedo2(W=110, D=19, BAIXO=60, sem=3, rampa='cal'):
    """Rochedo de arenito com volume de verdade: dois ou três blocos arredondados colados,
    fenda entre eles, tampo largo e mais claro onde se pisa, lados estufados e o pé abrindo
    até sair pela borda de baixo da tela. Luz de cima e da esquerda pela forma (mapa de altura)."""
    from scipy import ndimage as nd
    rng = np.random.default_rng(sem)
    h = D + BAIXO
    pad = 10
    q = Quadro(W + 2 * pad, h)
    X, Y = q.xx.astype(float), q.yy.astype(float)
    nb = max(1, int(round(W / 55)))
    # silhueta: cada bloco é uma cúpula achatada; o pé alarga para fora
    m = np.zeros((h, q.w), bool)
    cortes = np.linspace(pad, pad + W, nb + 1)
    for i in range(nb):
        a, b = cortes[i], cortes[i + 1]
        cx, rx = (a + b) / 2, (b - a) / 2 + 3
        topo = 1 + rng.uniform(0, 3)
        k = np.clip((Y - topo) / (h - topo), 0, 1)
        larg = rx * (0.82 + 0.35 * np.sqrt(k)) + 1.5 * np.sin(Y * 0.31 + i * 3 + sem)
        dome = topo + 5 * (np.abs(X - cx) / rx) ** 3
        m |= (np.abs(X - cx) < larg) & (Y >= dome)
    m = nd.binary_opening(m, np.ones((3, 3)))
    # mapa de altura: distância à borda (arredonda as beiradas) + ruído grosso
    dist = nd.distance_transform_edt(m)
    alt = np.sqrt(np.minimum(dist, 14) / 14) * 14 + 1.6 * ruido(h, q.w, (3, 4), sem)
    gy, gx = np.gradient(nd.gaussian_filter(alt, 1.2))
    # o tampo (onde se pisa) é virado para cima: soma a luz de cima nele
    frente = D + 1.5 * ruido(1, q.w, 5, sem + 8)[0][None, :]
    tampo = m & (Y < frente)
    # lado: claro à esquerda, escuro à direita, pela distância às beiradas de cada linha
    esq = np.where(m.any(1), m.argmax(1), 0)[:, None]
    dir_ = np.where(m.any(1), q.w - 1 - m[:, ::-1].argmax(1), q.w)[:, None]
    lat = np.clip((X - esq) / np.maximum(1, dir_ - esq), 0, 1)
    # frente bem mais escura que o tampo (como a barreira do Metal Slug: o tampo é a faixa acesa)
    luz = 0.46 + 0.16 * (1 - lat) ** 2 - 0.2 * lat ** 3 + 0.05 * (-gx) * 3 + 0.05 * (-gy) * 2 \
        - 0.22 * np.clip((Y - D) / max(1, BAIXO), 0, 1)
    luz = np.where(tampo, 0.8 + 0.05 * ruido(h, q.w, (1, 3), sem + 9) - 0.1 * (1 - Y / D) - 0.08 * lat, luz)
    # camadas do arenito: bandas tortas seguindo o tampo, juntas escuras
    camada = (Y - D + 2.2 * ruido(h, q.w, (2, 12), sem + 4)) / 6.5
    fr = camada - np.floor(camada)
    face = ~tampo
    luz = np.where(face & (fr < 0.14), luz - 0.15, luz)
    luz = np.where(face & (fr > 0.14) & (fr < 0.26), luz + 0.05, luz)
    # fenda entre os blocos
    for i in range(1, nb):
        c = cortes[i] + rng.uniform(-3, 3)
        fen = np.abs(X - c - 1.2 * np.sin(Y * 0.4)) < (0.6 + 1.2 * np.clip((Y - 2) / h, 0, 1))
        luz = np.where(fen, 0.06, np.where(np.abs(X - c + 1.5) < 0.7, luz + 0.1, luz))
    # trincas finas
    for _ in range(int(W / 30) + 1):
        x = rng.uniform(pad + 6, pad + W - 6); y = rng.uniform(D, D + 8)
        for _ in range(int(rng.uniform(8, BAIXO * 0.6))):
            xi, yi = int(round(x)), int(round(y))
            if 0 <= yi < h and 0 <= xi < q.w:
                luz[yi, xi] = 0.1
                if xi > 0:
                    luz[yi, xi - 1] += 0.08
            x += rng.choice([-0.7, 0, 0.7]); y += 1
    luz += 0.04 * ruido(h, q.w, (0.8, 2), sem + 7)
    P(q, m, rampa, np.clip(luz, 0.02, 0.97)[m])
    # beirada do tampo gasta e acesa
    quina = m & ~tampo & (Y < frente + 1.5)
    P(q, quina, rampa, 0.88)
    P(q, m & ~tampo & (Y >= frente + 1.5) & (Y < frente + 3), rampa, 0.3)   # sombra embaixo da quina
    # pouco líquen, só nas partes viradas para cima
    lq = m & (ruido(h, q.w, (1.5, 2), sem + 6) > 1.9) & (Y < D + 10)
    P(q, lq, 'verde', 0.5)
    q.ox = pad
    return q, dict(D=D, chao=h - 1)


def _cerca_linha(q, p0, p1, h0, h1, passo, sem, esc=0.0):
    """Varas fincadas de p0 a p1 (pés), altura indo de h0 a h1, duas travessas seguindo."""
    rng = np.random.default_rng(sem)
    (x0, y0), (x1, y1) = p0, p1
    comp = max(1.0, np.hypot(x1 - x0, y1 - y0))
    n = max(2, int(comp / passo) + 1)
    # travessas (atrás das varas)
    for fr in (0.38, 0.7):
        for t in np.linspace(0, 1, int(comp) * 2 + 2):
            x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
            hh = h0 + (h1 - h0) * t
            yy = y - hh * (1 - fr)
            r = 1.4 * (hh / max(h0, h1))
            m = (np.abs(q.xx - x) <= 0.6) & (np.abs(q.yy - yy) <= r)
            P(q, m, 'madeira', np.where(q.yy[m] < yy - 0.3, 0.75, 0.42) - esc)
    for i in range(n):
        t = i / (n - 1)
        x = x0 + (x1 - x0) * t + rng.uniform(-0.6, 0.6); y = y0 + (y1 - y0) * t
        hh = (h0 + (h1 - h0) * t) * rng.uniform(0.85, 1.0)
        r = max(0.8, 2.0 * (h0 + (h1 - h0) * t) / max(h0, h1))
        m = (np.abs(q.xx - x) <= r) & (q.yy <= y) & (q.yy >= y - hh)
        u = (q.xx[m] - x) / r
        luz = 0.62 - 0.38 * u - esc - 0.15 * (q.yy[m] > y - 3)
        luz = np.where(q.yy[m] < y - hh + 1.5, 0.85 - esc, luz)
        P(q, m, 'madeira', np.clip(luz, 0.02, 0.95))
        for fr in (0.38, 0.7):
            yy = y - hh * (1 - fr)
            mm = (np.abs(q.xx - x) <= r + 0.5) & (np.abs(q.yy - yy) <= 0.8)
            P(q, mm, 'cal', 0.55 - esc)


def curral(W=170, H=40, D=26, sem=9):
    """Curral visto um pouco de cima: cerca de trás menor e mais escura, os lados fugindo em
    diagonal e a cerca da frente; chão de dentro pisado e mais escuro."""
    h = H + D + 4
    q = Quadro(W + 4, h)
    yf, yt = h - 2, h - 2 - D
    ins = D * 0.9
    # chão pisado de dentro
    m = poly(q.w, q.h, [(2 + ins, yt), (W - ins, yt), (W, yf), (2, yf)])
    P(q, m, 'terra', 0.45 + 0.04 * ruido(q.h, q.w, (1, 4), sem)[m])
    _cerca_linha(q, (2 + ins, yt), (W - ins, yt), H * 0.78, H * 0.78, 12, sem, esc=0.12)
    _cerca_linha(q, (2 + ins, yt), (2, yf), H * 0.78, H, 8, sem + 1, esc=0.06)
    _cerca_linha(q, (W - ins, yt), (W, yf), H * 0.78, H, 8, sem + 2, esc=0.08)
    _cerca_linha(q, (2, yf), (W, yf), H, H, 13, sem + 3)
    return q
