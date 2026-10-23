"""Construções da rua em 2.5D (22/10): fachada de frente, a parede do lado fugindo para trás
(para a direita e para cima, um pouco menor no fundo) e o telhado como um plano em
perspectiva. Pedido do Guilherme: casas e igreja com o 3D alinhado, portas e janelas na
proporção do Lampião (porta ~56 px), telhado destruído mostrando a estrutura de verdade.

- casa25(): casa de taipa da rua (inteira ou destelhada);
- capela25(): a capela da vila, o dobro da antiga.
Luz da esquerda e de cima, sem contorno, nas rampas de ambiente (cm.RGB).
"""
import numpy as np
from PIL import Image, ImageDraw

from caatinga_ms import Quadro, ruido, escurecer, RGB
from pecas25 import P, poly, linha


def _parede(q, m, sem, parede='cal', base=0.8, sombra=0.0, x0=0, w=1, yb=0, barro=22):
    """Reboco de cal (ou taipa de barro) com manchas, barro subindo da base e trama aparecendo."""
    X, Y = q.xx, q.yy
    n = ruido(q.h, q.w, (6, 10), sem)
    if parede == 'cal':
        luz = base - 0.1 * (X - x0) / max(1, w) + 0.03 * n - sombra
        luz = np.where(ruido(q.h, q.w, (1, 2), sem + 1) > 2.1, luz - 0.12, luz)        # reboco esfarelado
        P(q, m, 'cal', luz[m])
        caido = m & (ruido(q.h, q.w, (5, 7), sem + 2) > 1.6)                              # reboco caído: trama
        trama = caido & (((X + (Y // 4) * 3) % 6 < 2) | (Y % 4 == 0))
        P(q, caido, 'terra', (0.6 - sombra + 0.05 * n)[caido])
        P(q, trama, 'madeira', 0.35 - sombra)
        bar = m & (Y > yb - barro + 4 * ruido(q.h, q.w, (2, 6), sem + 3))                  # barro subindo
        P(q, bar, 'terra', (0.62 - sombra - 0.1 * (Y - (yb - barro)) / barro)[bar])
    else:
        luz = base - 0.12 - 0.1 * (X - x0) / max(1, w) + 0.05 * n - sombra
        P(q, m, 'terra', luz[m])
        trama = m & ((((X + (Y // 5) * 4) % 7) < 1) | (Y % 5 == 0)) & (ruido(q.h, q.w, (3, 3), sem + 4) > 0.2)
        P(q, trama, 'madeira', 0.4 - sombra)
    # rachaduras
    rng = np.random.default_rng(sem)
    for _ in range(3):
        xs = np.where(m.any(0))[0]
        if not len(xs):
            break
        x = rng.uniform(xs.min() + 4, xs.max() - 4); ys = np.where(m[:, int(x)])[0]
        if not len(ys):
            continue
        y = float(ys.min() + rng.uniform(2, 10))
        for _ in range(int(rng.uniform(8, 22))):
            xi, yi = int(x), int(y)
            if 0 <= yi < q.h and m[yi, xi]:
                q.img[yi, xi] = (q.img[yi, xi] * 0.62).astype(np.uint8)
            x += rng.choice([-0.8, 0, 0.8]); y += 1


def _porta(q, x, yb, w, h, sem, arco=False, aberta=True):
    """Porta de tábuas no batente, entreaberta mostrando o escuro de dentro."""
    X, Y = q.xx, q.yy
    yt = yb - h
    vao = (X >= x) & (X < x + w) & (Y >= yt) & (Y < yb)
    if arco:
        r = w / 2
        vao &= ~((Y < yt + r) & (((X - (x + r - 0.5)) ** 2 + (Y - (yt + r)) ** 2) > r * r))
    batente = vao & ~(((X >= x + 2) & (X < x + w - 2) & (Y >= yt + 2)) & vao)
    P(q, vao, 'madeira', 0.04)
    # luzinha de dentro (chão)
    P(q, vao & (Y > yb - 4) & (X > x + w * 0.5), 'madeira', 0.18)
    folha = vao & ~batente & (X < x + (w * 0.55 if aberta else w))
    tab = ((X - x) // 5) % 2
    luz = 0.42 + 0.08 * tab - 0.12 * ((X - x) % 5 == 0) + 0.04 * ruido(q.h, q.w, (6, 1), sem)
    P(q, folha, 'madeira', luz[folha])
    P(q, folha & ((Y == yt + int(h * 0.25)) | (Y == yt + int(h * 0.7))), 'madeira', 0.22)  # travessas
    P(q, batente, 'madeira', 0.62)
    P(q, batente & (X >= x + w - 2), 'madeira', 0.3)
    return vao


def _janela(q, x, y, w, h, sem, arco=False):
    """Janela com a folha aberta para fora, batente e o escuro de dentro."""
    X, Y = q.xx, q.yy
    vao = (X >= x) & (X < x + w) & (Y >= y) & (Y < y + h)
    if arco:
        r = w / 2
        vao &= ~((Y < y + r) & (((X - (x + r - 0.5)) ** 2 + (Y - (y + r)) ** 2) > r * r))
    P(q, vao, 'madeira', 0.05)
    P(q, vao & (Y > y + h * 0.6), 'madeira', 0.12)
    P(q, (X >= x - 1) & (X < x + w + 1) & (Y >= y + h) & (Y < y + h + 2), 'cal', 0.95)  # peitoril
    P(q, (X >= x - 1) & (X < x + w + 1) & (Y == y + h + 2), 'cal', 0.3)
    fol = (X >= x + w + 1) & (X < x + w + 1 + w * 0.45) & (Y >= y) & (Y < y + h)
    P(q, fol, 'madeira', (0.5 - 0.15 * ((X - x) % 3 == 0))[fol])


def _telhas(q, m, eixo, sem, base=0.6):
    """Telha canal: canais seguindo `eixo` (função x,y -> coordenada ao longo do beiral) e
    fiadas paralelas ao beiral; cada canal com luz à esquerda."""
    X, Y = q.xx, q.yy
    u = eixo(X, Y)
    canal = (u % 7) / 7.0
    luz = base + 0.25 * np.cos(canal * np.pi * 2 + 0.6) * 0.5 - 0.15 * (canal > 0.82)
    fiada = (Y % 6 == 0)
    luz = np.where(fiada, luz - 0.18, luz)
    luz += 0.05 * ruido(q.h, q.w, (2, 3), sem)
    luz = np.where(ruido(q.h, q.w, (1, 1), sem + 1) > 2.2, luz - 0.25, luz)               # telha quebrada
    P(q, m, 'telha', np.clip(luz, 0.02, 0.97)[m])
    # musgo/manchas escuras
    mm = m & (ruido(q.h, q.w, (2, 4), sem + 2) > 1.7)
    P(q, mm, 'verde', 0.3)


def casa25(W=124, HP=78, G=26, SW=30, SH=16, OV=5, sem=21, parede='cal', porta=(40, 28, 56),
           janela=(84, 22, 20, 22), destelhada=False, rombo=False):
    """Casa de taipa em 2.5D. W/HP: largura e altura da parede da frente; G: altura da
    cumeeira acima da parede; SW/SH: quanto a parede do lado foge para a direita e para cima;
    OV: beiral. porta=(x, largura, altura); janela=(x, y, largura, altura) ou None."""
    PADT = G + SH + 6
    w, h = W + SW + OV * 2 + 4, PADT + HP
    q = Quadro(w, h)
    X, Y = q.xx, q.yy
    x0 = OV + 1
    x1 = x0 + W
    yb = h                    # chão
    yt = yb - HP              # topo da parede da frente
    # parede do lado (sombra), fugindo para trás
    lado = poly(w, h, [(x1, yt), (x1 + SW, yt - SH), (x1 + SW, yb - SH), (x1, yb)])
    _parede(q, lado, sem + 9, parede, base=0.6, sombra=0.0, x0=x1, w=SW, yb=yb - SH * 0.5)
    q.img[lado] = (q.img[lado] * 0.8).astype(np.uint8)
    # oitão (triângulo do lado, embaixo do telhado)
    ry = yt - SH / 2 - G
    oit = poly(w, h, [(x1, yt), (x1 + SW, yt - SH), (x1 + SW / 2, ry)])
    _parede(q, oit, sem + 10, parede, base=0.55, x0=x1, w=SW, yb=yt)
    q.img[oit] = (q.img[oit] * 0.78).astype(np.uint8)
    # parede da frente
    fr = (X >= x0) & (X < x1) & (Y >= yt) & (Y < yb)
    _parede(q, fr, sem, parede, base=0.86, x0=x0, w=W, yb=yb)
    # sombra do beiral na parede
    sb = fr & (Y < yt + 5 + 2 * np.sin(X * 0.2))
    q.img[sb] = (q.img[sb] * 0.72).astype(np.uint8)
    # quina acesa entre frente e lado
    P(q, (X == x1 - 1) & (Y >= yt) & (Y < yb), 'cal' if parede == 'cal' else 'terra', 0.95)
    if porta:
        px, pw, ph = porta
        _porta(q, x0 + px, yb - 1, pw, ph, sem + 3)
        # degrau de pedra em 2.5D na frente da porta
        dg = poly(w, h, [(x0 + px - 4, yb - 3), (x0 + px + pw + 4, yb - 3), (x0 + px + pw + 6, yb), (x0 + px - 2, yb)])
        P(q, dg, 'cal', 0.55)
        P(q, dg & (Y == yb - 3), 'cal', 0.85)
    if janela:
        jx, jy, jw, jh = janela
        _janela(q, x0 + jx, yt + jy, jw, jh, sem + 4)
    if rombo:
        cx, cy = x0 + W * 0.78, yt + HP * 0.3
        d = np.hypot((X - cx) / 11, (Y - cy) / 9) + 0.25 * ruido(h, w, (1, 1), sem + 5)
        P(q, fr & (d < 1), 'madeira', 0.04)
        borda = fr & (d >= 1) & (d < 1.25)
        P(q, borda, 'terra', 0.4)
    # telhado: plano da frente do beiral até a cumeeira (fugindo para trás)
    ey = yt + 2
    pl = poly(w, h, [(x0 - OV, ey), (x1 + OV, ey), (x1 + OV + SW / 2, ry), (x0 - OV + SW / 2, ry)])
    # beirada do telhado em cima do oitão
    barge = poly(w, h, [(x1 + OV + SW / 2, ry), (x1 + OV, ey), (x1 + OV + 2, ey), (x1 + SW + 2, yt - SH + 1),
                        (x1 + OV + SW / 2 + 2, ry)])
    k = (SW / 2) / max(1, (ey - ry))                    # inclinação dos canais (fogem para a direita)
    eixo = lambda X_, Y_: X_ + (Y_ - ey) * k             # noqa: E731
    if not destelhada:
        _telhas(q, pl, eixo, sem + 6)
        P(q, barge, 'telha', 0.35)
        # beiral: linha de bicas na frente e a sombra embaixo
        P(q, pl & (Y >= ey - 2), 'telha', np.where(((X - x0) % 7) < 3, 0.75, 0.3)[pl & (Y >= ey - 2)])
        P(q, (Y >= ry - 2) & (Y <= ry) & pl, 'telha', 0.85)   # cumeeira
    else:
        # sem telha: o escuro de dentro (parede de trás iluminada pelo buraco), caibros e ripas
        dentro = pl.copy()
        luz = 0.08 + 0.18 * np.clip((Y - ry) / max(1, ey - ry), 0, 1) * (ruido(h, w, (3, 6), sem + 7) > -0.3)
        P(q, dentro, 'madeira', luz[dentro])
        # topo da parede de trás aparecendo
        tras = dentro & (np.abs(Y - (ry + 3)) < 1.5)
        P(q, tras, 'cal', 0.45)
        # ripas (horizontais) e caibros (do beiral à cumeeira)
        for yy in np.arange(ry + 6, ey - 1, 6):
            rp = dentro & (np.abs(Y - yy) < 0.6) & (ruido(h, w, (1, 4), int(yy) + sem) > -0.9)
            P(q, rp, 'madeira', 0.55)
        for xx in np.arange(x0 - OV + 3, x1 + OV, 11):
            cb = linha(w, h, (xx, ey), (xx + SW / 2, ry), 2) & dentro
            P(q, cb, 'madeira', 0.5)
            cl = linha(w, h, (xx - 1, ey), (xx - 1 + SW / 2, ry), 1) & dentro
            P(q, cl, 'madeira', 0.78)
        # cumeeira (tora) e algumas telhas que sobraram presas no beiral e na cumeeira
        P(q, pl & (Y >= ry - 1) & (Y <= ry + 1), 'madeira', 0.6)
        sobra = pl & (((Y > ey - 7) & (ruido(h, w, (1, 3), sem + 8) > 0.2)) |
                      ((Y < ry + 5) & (ruido(h, w, (1, 3), sem + 9) > 0.9)))
        _telhas(q, sobra, eixo, sem + 6, base=0.5)
        P(q, barge, 'madeira', 0.4)
    return q


def _esc(q, m, k=1):
    """Escurece k degraus da própria rampa (sombra sem sair da paleta)."""
    if m.any():
        q.img[m] = escurecer(q.img[m], k)


def _clarear(q, m, rampa, d=0.12):
    """Sobe a luz de quem já está pintado com a rampa (beirada acesa)."""
    if not m.any():
        return
    r = RGB[rampa].astype(int)
    px = q.img[m].astype(int)
    k = ((px[:, None, :] - r[None]) ** 2).sum(-1).argmin(1)
    k = np.clip(k + max(1, int(round(d * len(r)))), 0, len(r) - 1)
    q.img[m] = r[k]


def _vao_arco(X, Y, x, y, w, h):
    """Vão retangular com o topo em arco pleno (x, y: canto de cima à esquerda)."""
    r = w / 2
    m = (X >= x) & (X < x + w) & (Y >= y) & (Y < y + h)
    return m & ~((Y < y + r) & (((X - (x + r - 0.5)) ** 2 + (Y - (y + r)) ** 2) > r * r))


def _abertura(q, x, y, w, h, sem, tipo='porta'):
    """Porta ou janela em arco no padrão do Metal Slug: moldura saliente (acesa em cima e à
    esquerda, sombra embaixo e à direita), o ombro de dentro do vão aparecendo do lado esquerdo
    (a gente vê de frente e um pouco da direita), folhas de tábua com almofadas e a sombra do
    arco caindo nelas."""
    X, Y = q.xx, q.yy
    mold = _vao_arco(X, Y, x - 4, y - 4, w + 8, h + 4) & ~_vao_arco(X, Y, x, y, w, h)
    P(q, mold, 'cal', 0.84)
    _clarear(q, mold & (X < x + w / 2) & ~_vao_arco(X, Y, x - 3, y - 3, w + 6, h + 3), 'cal', 0.2)
    _esc(q, mold & (X >= x + w) & (Y > y + w / 2), 1)
    vao = _vao_arco(X, Y, x, y, w, h)
    P(q, vao, 'madeira', 0.05)
    ombro = vao & (X < x + 4)                                  # espessura da parede (lado de dentro)
    P(q, ombro, 'cal', 0.36)
    P(q, ombro & (X == x + 3), 'cal', 0.18)
    folha = vao & (X >= x + 4) & (Y >= y + 2)
    if tipo == 'porta':
        fx0, fx1 = x + 4, x + w - 1
        meio = (fx0 + fx1) // 2
        P(q, folha, 'madeira', 0.42)
        P(q, folha & ((X - fx0) % 5 == 0), 'madeira', 0.3)     # juntas das tábuas
        P(q, folha & (X == meio), 'madeira', 0.12)             # encontro das folhas
        for xa, xb in ((fx0 + 3, meio - 3), (meio + 3, fx1 - 3)):  # almofadas
            for ya, yb in ((y + w / 2 + 4, y + h * 0.55), (y + h * 0.62, y + h - 6)):
                al = (X >= xa) & (X <= xb) & (Y >= ya) & (Y <= yb)
                P(q, al, 'madeira', 0.36)
                P(q, al & ((Y == int(ya)) | (X == xa)), 'madeira', 0.2)
                P(q, al & ((Y == int(yb)) | (X == xb)), 'madeira', 0.62)
        for yy in (y + h * 0.3, y + h * 0.58, y + h - 4):       # cravos de ferro
            for xx in range(fx0 + 2, fx1, 4):
                if folha[int(yy), xx]:
                    q.img[int(yy), xx] = RGB['azul'][0]
        P(q, folha & (X > meio - 4) & (X < meio - 1) & (np.abs(Y - (y + h * 0.5)) < 2), 'cal', 0.3)  # argola
    else:
        P(q, folha, 'madeira', 0.38)
        P(q, folha & ((X - x) % 4 == 0), 'madeira', 0.2)        # venezianas
        P(q, folha & (Y % 3 == 0), 'madeira', 0.52)
        # peitoril saliente com a sombra embaixo
        pe = (X >= x - 5) & (X < x + w + 5) & (Y >= y + h) & (Y < y + h + 3)
        P(q, pe, 'cal', 0.9)
        P(q, pe & (Y == y + h + 2), 'cal', 0.5)
        _esc(q, (X >= x - 4) & (X < x + w + 6) & (Y >= y + h + 3) & (Y < y + h + 5) & q.a, 1)
        # escorrido de chuva saindo do peitoril
        esc_ = (Y >= y + h + 5) & (Y < y + h + 22) & (np.abs(X - (x + w * 0.3)) < 1.5 + (Y - y - h) * 0.05) & q.a
        _esc(q, esc_ & (ruido(q.h, q.w, (3, 1), sem) > -0.3), 1)
    # sombra do arco por dentro (o topo do vão é mais escuro)
    _esc(q, folha & (Y < y + w / 2 + 3) & ~_vao_arco(X, Y, x + 2, y + 3, w - 4, h), 1)


def extrudar(q, SW=10, SH=7):
    """Dá fundo a uma construção desenhada de frente (23/10): varre a silhueta para trás
    (para a direita e para cima), como no Metal Slug. O que sobra à direita da fachada é a
    parede do lado (na sombra, dois degraus abaixo) e o que sobra por cima é o tampo/telhado
    visto de cima (a cor da beirada continuando para trás). Devolve um Quadro maior, com a
    fachada original no canto de baixo à esquerda (x 0, y SH)."""
    out = Quadro(q.w + SW, q.h + SH)
    n = max(SW, SH)
    for k in range(n, 0, -1):
        t = k / n
        out.colar(q, int(round(t * SW)), int(round(SH - t * SH)))
    extra = out.a.copy()
    frente = np.zeros_like(out.a)
    frente[SH:SH + q.h, :q.w] = q.a
    extra &= ~frente
    # direita da fachada naquela linha = lado; o resto = tampo
    dir_ = np.where(frente.any(1), q.w - 1 - frente[:, ::-1].argmax(1) - 0, -1)[:, None]
    lado = extra & (out.xx > dir_)
    tampo = extra & ~lado
    if lado.any():
        out.img[lado] = escurecer(out.img[lado], 2)
    # quina de trás do tampo um pouco mais escura (o tampo some para trás)
    fundo = tampo & ~np.roll(tampo, -2, axis=0)
    if fundo.any():
        out.img[fundo] = escurecer(out.img[fundo], 1)
    out.colar(q, 0, SH)
    return out


def capela25(sem=3):
    """Capela da vila em 2.5D, redesenhada no jeito do Metal Slug (23/10): formas limpas,
    cada parte com volume (moldura saliente acesa em cima e com sombra embaixo), sem manchas
    soltas. Fachada caiada com cunhais, barrado azul e embasamento; cornija; frontão barroco
    de volutas com o óculo; sineira com o sino e a cruz; porta em arco funda (o ombro da parede
    aparece), duas janelas em arco com peitoril; a parede do lado e o telhado fogem para trás
    (o plano do telhado vai da cornija do lado até a cumeeira, escondida atrás do frontão);
    degraus de pedra. Devolve (Quadro, x do meio da porta)."""
    FW, HB = 170, 104                 # fachada e altura até a cornija
    SW, SH = 52, 26                   # parede do lado fugindo
    FR, SN, CR = 56, 32, 16           # frontão, sineira, cruz
    DEG = 6                           # degraus na frente da fachada
    w = FW + SW + 12
    h = HB + FR + SN + CR + DEG + 4
    q = Quadro(w, h)
    X, Y = q.xx, q.yy
    x0, x1 = 6, 6 + FW
    cx = (x0 + x1) // 2
    yb = h - DEG                      # pé da fachada
    yc = yb - HB                      # cornija
    # ---- telhado do lado: plano da cornija do lado até a cumeeira (atrás do frontão)
    rY = yc - 46
    tl = poly(w, h, [(cx, rY), (cx + SW, rY - SH), (x1 + SW + 4, yc - SH + 2), (x1 + 3, yc + 2)])
    dx, dy = (x1 - cx), (yc - rY)
    u = X - (Y - rY) * dx / dy                                  # canais descendo o telhado
    v = Y + (X - cx) * SH / SW                                  # fiadas paralelas ao beiral
    canal = (u % 6) / 6
    luz = 0.5 + 0.18 * np.cos(canal * 2 * np.pi + 0.8) - 0.16 * ((v % 5) < 1) + 0.04 * ruido(h, w, (2, 2), sem + 6)
    P(q, tl, 'telha', luz)
    _esc(q, tl & (ruido(h, w, (3, 6), sem + 7) > 1.3), 1)       # telhas escurecidas pelo tempo
    beiral = tl & (v > yc + (x1 - cx) * SH / SW - 3)
    P(q, beiral, 'telha', np.where((u % 6) < 3, 0.62, 0.22))
    # ---- parede do lado (na sombra), com barrado, janela estreita e contraforte
    lado = poly(w, h, [(x1, yc), (x1 + SW, yc - SH), (x1 + SW, yb - SH), (x1, yb)])
    fra = (X - x1) / SW
    P(q, lado, 'cal', 0.6 - 0.06 * fra)
    yl = lambda yy: yy - fra * SH                               # noqa: E731  (altura na parede do lado)
    P(q, lado & (Y > yl(yb - 18)), 'azul', 0.32)                # barrado
    P(q, lado & (np.abs(Y - yl(yb - 18)) < 0.8), 'cal', 0.4)
    P(q, lado & (Y > yl(yb - 6)), 'cal', 0.32)                  # embasamento
    _esc(q, lado & (Y < yl(yc) + 4), 1)                         # sombra do beiral
    for jf in (0.35, 0.75):                                     # janelas estreitas em perspectiva
        ja, jb = x1 + SW * jf, x1 + SW * jf + 7
        fa, fb = (ja - x1) / SW * SH, (jb - x1) / SW * SH
        jw = poly(w, h, [(ja, yc + 30 - fa), (jb, yc + 30 - fb), (jb, yc + 56 - fb), (ja, yc + 56 - fa)])
        jw &= lado
        P(q, jw, 'madeira', 0.06)
        P(q, jw & (X < ja + 2), 'cal', 0.3)
    # ---- fachada: corpo + frontão + sineira numa silhueta só
    corpo = (X >= x0) & (X < x1) & (Y >= yc) & (Y < yb)
    t = np.abs(X - cx) / (FW / 2 - 4)
    s_ = np.clip((t - 0.26) / 0.74, 0, 1)
    perfil = np.where(t < 0.26, 1.0, 0.18 + 0.82 * (1 - (3 * s_ ** 2 - 2 * s_ ** 3)))
    perfil += 0.10 * np.exp(-((t - 0.86) / 0.07) ** 2)          # ombro da voluta
    topo_fr = yc - FR * perfil
    front = (t <= 1) & (Y >= topo_fr) & (Y < yc)
    sw2 = 24
    ts = yc - FR - SN
    sine = (np.abs(X - cx) <= sw2) & (Y >= ts + 6) & (Y < yc - FR + 2)
    tamp = (Y >= ts) & (Y < ts + 7) & (np.abs(X - cx) <= sw2 + 3 - (ts + 7 - Y) * 3)  # capelo triangular
    fach = corpo | front | sine | tamp
    P(q, fach, 'cal', 0.88 - 0.05 * (X - x0) / FW)
    # moldura do frontão e do capelo (beirada acesa, sombra embaixo dela)
    borda = (front | sine | tamp) & ~np.roll(front | sine | tamp, 2, axis=0)
    P(q, borda, 'cal', 0.99)
    sob = (front | sine) & np.roll(borda, 2, axis=0) & ~borda
    _esc(q, sob, 1)
    # volutas: espiral nas pontas do frontão
    for sx in (-1, 1):
        vx, vy = cx + sx * (FW / 2 - 12), yc - 9
        d = np.hypot(X - vx, Y - vy)
        P(q, (d < 6) & (d >= 4.2), 'cal', 0.98)
        P(q, (d < 4.2) & (d >= 2.5), 'cal', 0.5)
        P(q, d < 2.5, 'cal', 0.9)
    # óculo com moldura
    oy = yc - FR * 0.47
    d = np.hypot(X - cx, Y - oy)
    P(q, (d < 11) & (d >= 8), 'cal', np.where(Y + X * 0.4 < oy + cx * 0.4, 0.98, 0.5))
    P(q, d < 8, 'madeira', 0.05)
    P(q, (d < 8) & ((np.abs(X - cx) < 0.6) | (np.abs(Y - oy) < 0.6)), 'madeira', 0.3)
    # vão da sineira com o sino
    vb = _vao_arco(X, Y, cx - 10, ts + 10, 20, 22)
    P(q, vb, 'madeira', 0.05)
    P(q, vb & (X < cx - 7), 'cal', 0.35)
    bs = ts + 15
    sino = vb & (Y >= bs) & (Y < bs + 13) & (np.abs(X - cx) < 3 + (Y - bs) * 0.42)
    P(q, sino, 'telha', np.clip(0.85 - 0.11 * (X - cx + 4), 0.1, 0.95))
    P(q, sino & (Y == bs + 12), 'telha', 0.2)
    P(q, (np.abs(X - cx) < 1) & (Y >= ts + 11) & (Y < bs), 'madeira', 0.3)
    # cruz de ferro
    cr = ((np.abs(X - cx) < 1.5) & (Y >= ts - CR) & (Y < ts + 1)) | \
         ((np.abs(Y - (ts - CR + 5)) < 1.2) & (np.abs(X - cx) < 6))
    P(q, cr, 'azul', 0.2)
    P(q, cr & (X < cx), 'azul', 0.45)
    # cunhais (pilastras salientes): beirada acesa à esquerda, sombra jogada à direita
    for px in (x0, x1 - 12, cx - 44, cx + 32):
        pw = 12
        cun = (X >= px) & (X < px + pw) & (Y >= yc + 4) & (Y < yb)
        P(q, cun, 'cal', 0.84)
        P(q, cun & (X == px), 'cal', 0.99)
        P(q, cun & (X == px + pw - 1), 'cal', 0.6)
        if px + pw < x1:
            _esc(q, (X >= px + pw) & (X < px + pw + 2) & (Y >= yc + 5) & (Y < yb) & corpo, 1)
        cap = (X >= px - 1) & (X < px + pw + 1) & (Y >= yc + 4) & (Y < yc + 7)
        P(q, cap, 'cal', 0.95)
    # barrado azul e embasamento
    bar = corpo & (Y >= yb - 18)
    P(q, bar, 'azul', 0.42 + 0.04 * ruido(h, w, (3, 8), sem + 2))
    P(q, corpo & (Y == yb - 18), 'cal', 0.98)
    P(q, corpo & (Y == yb - 17), 'azul', 0.22)
    emb = corpo & (Y >= yb - 6)
    P(q, emb, 'cal', 0.42)
    P(q, emb & (Y == yb - 6), 'cal', 0.75)
    # cornija: três frisos (luz em cima, sombra embaixo) e a sombra dela na parede
    for k, (dy_, lz) in enumerate(((-3, 0.99), (-1, 0.82), (1, 0.62), (3, 0.3))):
        P(q, (X >= x0 - 4) & (X < x1 + 4) & (Y >= yc + dy_ - 1) & (Y < yc + dy_ + 1), 'cal', lz)
    _esc(q, corpo & (Y >= yc + 4) & (Y < yc + 8), 1)
    # desgaste: sujeira subindo da base e escorridos embaixo da cornija (sem manchas soltas)
    n = ruido(h, w, (2, 5), sem + 11)
    _esc(q, corpo & (Y < yb - 18) & (Y > yb - 30 + 5 * n) & (ruido(h, w, (1, 2), sem + 12) > 0.6), 1)
    esc_ = corpo & (Y > yc + 8) & (Y < yc + 30 + 12 * n) & (ruido(h, w, (0.8, 4), sem + 13) > 1.4)
    _esc(q, esc_, 1)
    # reboco caído: duas falhas com borda (sombra em cima, luz embaixo) mostrando o adobe
    for (fx, fy, fr) in ((x0 + 22, yc + 62, 7), (x1 - 26, yc + 70, 6)):
        dd = np.hypot((X - fx) / fr, (Y - fy) / (fr * 0.7)) + 0.18 * ruido(h, w, (1, 1), fx)
        buraco = corpo & (dd < 1)
        P(q, buraco, 'terra', 0.55)
        tij = buraco & (((Y - fy) % 4 == 0) | (((X + ((Y - fy) // 4) * 4) % 8) == 0))
        P(q, tij, 'terra', 0.32)
        P(q, buraco & (dd > 0.75) & (Y < fy), 'terra', 0.2)
        P(q, corpo & (dd >= 1) & (dd < 1.18) & (Y > fy), 'cal', 0.98)
    # porta (maior que o Lampião) e janelas
    pw_, ph_ = 38, 66
    _abertura(q, cx - pw_ // 2, yb - 6 - ph_, pw_, ph_, sem + 3, 'porta')
    for jx in (cx - 38 - 22 - 4, cx + 38 + 4):
        _abertura(q, int(jx - 0), yc + 20, 22, 34, sem + 4, 'janela')
    # degraus de pedra em 2.5D (tampo aceso, frente na sombra)
    for k, (dw, yy) in enumerate(((78, yb + DEG - 3), (60, yb + 0))):
        a_, b_ = cx - dw / 2, cx + dw / 2
        tampo = poly(w, h, [(a_, yy), (b_, yy), (b_ + 2, yy - 2), (a_ + 2, yy - 2)])
        frente = (X >= a_) & (X < b_) & (Y >= yy) & (Y < yy + 3)
        P(q, tampo, 'cal', 0.8)
        P(q, frente, 'cal', 0.45)
        P(q, frente & (Y == yy + 2), 'cal', 0.3)
    return q, int(cx)


if __name__ == '__main__':
    import sys
    cp, _ = capela25()
    im = Image.fromarray(cp.rgba(), 'RGBA')
    out = Image.new('RGBA', (im.width + 8, im.height + 8), (196, 160, 120, 255))
    out.alpha_composite(im, (4, 4))
    out.resize((out.width * 3, out.height * 3), Image.NEAREST).save(sys.argv[1])


# ---------------------------------------------------------------- cruzeiro 2.5D (23/10)
def _caixa(q, x0, y0, z0, w, h, d, H0, kx, ky, rampa, sem, luzes=(0.62, 0.34, 0.86), veio=None):
    """Caixa em 3D (x para a direita, y para cima, z para trás), vista como no Metal Slug:
    frente reta, lado direito fugindo para cima e o tampo visto de cima."""
    def pr(x, y, z):
        return (x + z * kx, H0 - y - z * ky)
    f = poly(q.w, q.h, [pr(x0, y0, z0), pr(x0 + w, y0, z0), pr(x0 + w, y0 + h, z0), pr(x0, y0 + h, z0)])
    lado = poly(q.w, q.h, [pr(x0 + w, y0, z0), pr(x0 + w, y0, z0 + d), pr(x0 + w, y0 + h, z0 + d),
                           pr(x0 + w, y0 + h, z0)]) & ~f
    topo = poly(q.w, q.h, [pr(x0, y0 + h, z0), pr(x0 + w, y0 + h, z0), pr(x0 + w, y0 + h, z0 + d),
                           pr(x0, y0 + h, z0 + d)]) & ~f & ~lado
    X, Y = q.xx, q.yy
    n = ruido(q.h, q.w, (3, 1.2) if veio == 'v' else (1.2, 3) if veio == 'h' else (2, 2), sem)
    lf, ll, lt = luzes
    sx0, sy1 = pr(x0, y0 + h, z0)
    luz_f = lf - 0.08 * (X - sx0) / max(1, w) + 0.05 * n
    if veio:                                   # veio da madeira lavrada e rachas
        rach = ruido(q.h, q.w, (6, 0.5) if veio == 'v' else (0.5, 6), sem + 1) > 1.8
        luz_f = np.where(rach, luz_f - 0.2, luz_f)
    P(q, f, rampa, luz_f[f])
    P(q, lado, rampa, (ll + 0.04 * n)[lado])
    P(q, topo, rampa, (lt + 0.03 * n)[topo])
    # quina acesa entre a frente e o tampo, quina escura entre a frente e o lado
    qa = f & ~np.roll(f, 1, axis=0)
    P(q, qa, rampa, min(0.99, lt + 0.08))
    qe = lado & ~np.roll(lado, 1, axis=1)
    P(q, qe, rampa, max(0.0, ll - 0.12))
    return f, lado, topo


def cruzeiro25(sem=5):
    """Cruzeiro de madeira lavrada (viga quadrada com frente, lado e topo) em pé no meio de
    uma base caiada de três degraus em 3D, plaquinha, fitas de promessa caindo do braço na
    frente da viga e tocos de vela nos degraus. Devolve (Quadro, x da frente da haste)."""
    kx, ky = 0.55, 0.42
    D = 18
    W = 46 + int(D * kx) + 2
    H = 104
    H0 = H - 1
    q = Quadro(W, H)
    # degraus caiados (o de baixo largo; cada um recuado e menor)
    for k, (x0, z0, w, d) in enumerate(((2, 0, 42, D), (6.5, 2.5, 33, D - 5), (11, 5, 24, D - 10))):
        f, l_, t_ = _caixa(q, x0, 7 * k, z0, w, 7, d, H0, kx, ky, 'cal', sem + k, luzes=(0.72, 0.42, 0.93))
        X, Y = q.xx, q.yy
        tri = f & (ruido(H, W, (1, 4), sem + 10 + k) > 1.7)                # reboco lascado mostrando o barro
        P(q, tri, 'terra', 0.55)
        suj = f & (Y > H0 - 7 * k - 3)                                      # barro na base de cada degrau
        P(q, suj, 'cal', 0.5)
    # haste e braço (viga de 8x8, centrada no degrau de cima)
    hx, hz, s = 19, 9, 8
    top_deg = 21
    _caixa(q, hx, top_deg, hz, s, 78, s, H0, kx, ky, 'madeira', sem + 20, veio='v')
    bra_y = top_deg + 52
    _caixa(q, hx - 16, bra_y, hz, 16 * 2 + s, 7, s, H0, kx, ky, 'madeira', sem + 21, veio='h')
    # a haste continua por cima do braço (mesma viga)
    _caixa(q, hx, bra_y + 7, hz, s, 78 - 52 - 7, s, H0, kx, ky, 'madeira', sem + 20, veio='v')
    X, Y = q.xx, q.yy
    pr = lambda x, y, z: (x + z * kx, H0 - y - z * ky)  # noqa: E731
    fx0, fy0 = pr(hx, 0, hz)
    # plaquinha INRI pregada na frente da haste
    pl = (X >= fx0 + 1) & (X < fx0 + 7) & (Y >= H0 - (bra_y + 21) - hz * ky) & (Y < H0 - (bra_y + 15) - hz * ky)
    P(q, pl, 'cal', np.where(Y == Y[pl].min(), 0.95, 0.75)[pl])
    # fitas de promessa amarradas no braço, caindo na frente (não fazem parte da viga)
    by = H0 - bra_y - hz * ky
    for k, (bx, rampa, comp) in enumerate(((fx0 - 13, 'telha', 15), (fx0 - 9, 'cal', 11), (fx0 + 13, 'verde', 13),
                                           (fx0 + 18, 'telha', 9))):
        for yy in range(int(by), int(by + comp)):
            xx = bx + 1.3 * np.sin((yy - by) / 3.0 + k)
            m = (np.abs(X - xx) < 1.0) & (Y == yy)
            P(q, m, rampa, (0.8 if rampa != 'cal' else 0.92) - 0.25 * (yy > by + comp * 0.6) - 0.15 * (X > xx))
        P(q, (np.abs(X - bx) < 1.5) & (Y == int(by)), rampa, 0.5)                         # nó
    # tocos de vela e cera escorrida nos degraus
    for vx, k in ((8, 0), (13, 1), (36, 1), (40, 0)):
        yb = H0 - 7 * (k + 1) - (2.5 if k == 0 else 5) * ky - 1
        P(q, (X >= vx) & (X < vx + 2) & (Y > yb - 4) & (Y <= yb), 'cal', np.where(X == vx, 0.99, 0.75))
        P(q, (X == vx) & (Y == yb - 4), 'telha', 0.95)
    return q, int(fx0)
