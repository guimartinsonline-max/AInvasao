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

from caatinga_ms import Quadro, ruido
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


def capela25(sem=3):
    """Capela da vila em 2.5D, o dobro da antiga: fachada caiada com frontão de volutas e a
    sineira com o sino, cruz de ferro, cornija, cunhais, porta em arco (60 px, maior que o
    Lampião), duas janelas em arco e o óculo; a parede do lado foge para trás com o telhado de
    telha por cima; dois degraus de pedra em 2.5D na frente. Devolve (Quadro, x do meio da porta)."""
    FW, HW = 176, 112                 # fachada e altura até a cornija
    SW, SH = 46, 24                   # parede do lado fugindo
    FR = 66                           # frontão acima da cornija
    SN = 34                           # sineira acima do frontão
    CR = 18                           # cruz
    w = FW + SW + 12
    h = HW + FR + SN + CR + 6
    q = Quadro(w, h)
    X, Y = q.xx, q.yy
    x0, x1 = 4, 4 + FW
    cx = (x0 + x1) / 2
    yb = h
    yc = yb - HW                       # cornija
    # parede do lado e o telhado dela (o telhado corre da fachada para trás)
    lado = poly(w, h, [(x1, yc), (x1 + SW, yc - SH), (x1 + SW, yb - SH), (x1, yb)])
    _parede(q, lado, sem + 9, 'cal', base=0.62, x0=x1, w=SW, yb=yb - SH * 0.5)
    q.img[lado] = (q.img[lado] * 0.82).astype(np.uint8)
    # janela do lado, em perspectiva (estreita)
    jl = poly(w, h, [(x1 + 14, yc + 36), (x1 + 24, yc + 31), (x1 + 24, yc + 58), (x1 + 14, yc + 63)])
    P(q, jl, 'madeira', 0.06)
    tl = poly(w, h, [(x1 - 2, yc - 40), (x1 + SW, yc - SH - 40), (x1 + SW + 4, yc - SH + 2), (x1 + 2, yc + 3)])
    _telhas(q, tl, lambda X_, Y_: (X_ - x1) * 1.4, sem + 6, base=0.5)
    P(q, tl & (Y > yc - (X - x1) * SH / SW), 'telha', 0.3)            # beiral na sombra
    # fachada: corpo, frontão de volutas e sineira (uma silhueta só)
    corpo = (X >= x0) & (X < x1) & (Y >= yc) & (Y < yb)
    u = (X - cx) / (FW / 2)
    curva = yc - FR * np.clip(1 - np.abs(u) ** 1.6, 0, 1) - 6 * np.exp(-((np.abs(u) - 0.62) / 0.08) ** 2)
    front = (np.abs(u) <= 1) & (Y >= curva) & (Y < yc)
    sw2 = 22
    sineira = (np.abs(X - cx) <= sw2) & (Y >= yc - FR - SN) & (Y < yc - FR + 4)
    topo_s = yc - FR - SN
    sineira &= ~((Y < topo_s + 10) & (np.hypot((X - cx) / sw2, (Y - (topo_s + 10)) / 10) > 1))
    fach = corpo | front | sineira
    _parede(q, fach, sem, 'cal', base=0.9, x0=x0, w=FW, yb=yb, barro=26)
    # cunhais (pilastras) e cornija com luz em cima e sombra embaixo
    for px in (x0, x1 - 10):
        cun = (X >= px) & (X < px + 10) & (Y >= yc) & (Y < yb)
        P(q, cun, 'cal', (0.8 - 0.25 * (X - px) / 10)[cun])
    cor = (X >= x0 - 3) & (X < x1 + 3) & (Y >= yc - 2) & (Y < yc + 5)
    P(q, cor, 'cal', np.where(Y[cor] < yc, 0.98, np.where(Y[cor] < yc + 3, 0.7, 0.35)))
    borda_fr = front & ~np.roll(front, 2, axis=0)
    P(q, borda_fr, 'cal', 0.98)                                      # beirada do frontão acesa
    # óculo no frontão
    oc = np.hypot(X - cx, Y - (yc - FR * 0.45)) < 7
    P(q, oc, 'madeira', 0.06)
    P(q, (np.hypot(X - cx, Y - (yc - FR * 0.45)) >= 7) & (np.hypot(X - cx, Y - (yc - FR * 0.45)) < 9), 'cal', 0.6)
    # vão do sino com o sino de bronze
    vb = (np.abs(X - cx) <= 10) & (Y >= topo_s + 6) & (Y < topo_s + 30)
    vb &= ~((Y < topo_s + 16) & (np.hypot((X - cx) / 10, (Y - (topo_s + 16)) / 10) > 1))
    P(q, vb, 'madeira', 0.06)
    raio = np.maximum(1, 5 + (Y - (topo_s + 12)) * 0.25)
    sino = vb & (np.abs(X - cx) < raio) & (Y > topo_s + 12) & (Y < topo_s + 27)
    P(q, sino, 'telha', np.clip(0.75 - 0.08 * (X - cx), 0.1, 0.95)[sino])
    P(q, (np.abs(X - cx) < 1) & (Y >= topo_s + 7) & (Y < topo_s + 12), 'madeira', 0.3)
    # cruz de ferro no alto
    cr = ((np.abs(X - cx) < 1.5) & (Y >= topo_s - CR) & (Y < topo_s + 1)) | \
         ((np.abs(Y - (topo_s - CR + 6)) < 1.5) & (np.abs(X - cx) < 7))
    P(q, cr, 'azul', 0.25)
    # porta em arco (maior que o Lampião) e janelas em arco
    pw, ph = 36, 62
    _porta(q, int(cx - pw / 2), yb - 7, pw, ph, sem + 3, arco=True, aberta=False)
    moldura = (np.abs(X - cx) < pw / 2 + 4) & (Y >= yb - 7 - ph - 4) & (Y < yb - 7) & ~((np.abs(X - cx) < pw / 2) & (Y >= yb - 7 - ph))
    moldura &= ~((Y < yb - 7 - ph + pw / 2) & (np.hypot(X - cx, Y - (yb - 7 - ph + pw / 2)) > pw / 2 + 4))
    P(q, moldura & fach, 'cal', 0.72)
    for jx in (cx - 58, cx + 42):
        _janela(q, int(jx), yc + 24, 16, 30, sem + 4, arco=True)
    # degraus de pedra em 2.5D
    d1 = poly(w, h, [(cx - 40, yb - 7), (cx + 46, yb - 7), (cx + 44, yb - 4), (cx - 42, yb - 4)])
    P(q, d1, 'cal', 0.7)
    P(q, (np.abs(X - cx - 2) < 43) & (Y >= yb - 4) & (Y < yb), 'cal', 0.42)
    P(q, (np.abs(X - cx - 2) < 43) & (Y == yb - 4), 'cal', 0.85)
    return q, int(cx)


if __name__ == '__main__':
    import vila_ms
    out = Image.new('RGBA', (680, 260), (196, 160, 120, 255))
    cp, _ = capela25()
    x = 4
    for qq in (vila_ms.casa_rua(1, True), cp):
        im = Image.fromarray(qq.rgba(), 'RGBA')
        out.alpha_composite(im, (x, 258 - im.height)); x += im.width + 6
    out.resize((1360, 520), Image.NEAREST).save('/tmp/claude-0/-home-user-ainvasao/6868aa79-06a4-51d4-906b-bf467f5d6e0d/scratchpad/p4.png')
