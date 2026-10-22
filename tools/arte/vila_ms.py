"""Trecho 2 da fase 1 (vila de taipa) no jeito do Metal Slug (ESTILO.md, Cenários).

Continua a pintura da caatinga (`caatinga_ms`) sem emenda: as camadas contínuas (chão,
morros, chapada) são as mesmas, só que vão até o fim da vila, e por cima entram as peças
da vila: as duas casas da rua (sprites à parte, a explosão arranca o telhado), a capela,
o cruzeiro, as casas de trás, a vila alta vista de longe no morro.

Mesmas regras: sem contorno, cor de ambiente da tarde (rampas `amb_*`), formas grandes com
textura dentro, luz da esquerda. A emenda com o estilo antigo fica fora da tela enquanto a
câmera está na vila (até CAMERA_FIM) e só aparece quando se entra na vila alta.
"""
import numpy as np
from PIL import Image

import caatinga_ms as cm
from caatinga_ms import Quadro, ambientar, fbm, nevoa, quantiza_limpo, ruido

VILA_INI = cm.CAATINGA_FIM     # 2980
VILA_FIM = 3880                # x do mundo onde começa a vila alta (casario de platibanda)
TELA_W = cm.TELA_W
CAMERA_FIM = VILA_FIM - TELA_W


def limite(fator):
    """x da camada até onde vai o jeito novo (caatinga + vila)."""
    return int(CAMERA_FIM * fator + TELA_W)


def antigo(x, fator):
    """A peça antiga nessa posição da camada continua (fica depois da vila)."""
    return x >= limite(fator)


# ---------------------------------------------------------------- casas da rua (sprites)
# x, largura, altura, semente, rombo. A porta da 1ª casa fica em x 3098 (os soldados saem por ela).
CASAS = [[3040, 168, 130, 21, False], [3664, 150, 122, 22, True]]
PORTA_CASA0 = 3098


def casa_rua(k, destelhada=False):
    """Casa de taipa da rua em 2.5D (predios25.casa25, 22/10): a fachada de frente, a parede
    do lado fugindo para trás e o telhado em perspectiva; porta mais alta que o Lampião.
    A 2ª é de barro sem reboco e tem um rombo de canhão."""
    import predios25 as p25
    x, W, H, sem, rombo = CASAS[k]
    if k == 0:
        pdx = PORTA_CASA0 - x - 6 - 14            # centro da porta (28 de largura) em x 3098
        q = p25.casa25(W=124, HP=80, G=28, sem=sem, porta=(pdx, 28, 56), janela=(84, 22, 20, 22),
                       destelhada=destelhada)
    else:
        q = p25.casa25(W=106, HP=74, G=26, sem=sem, parede="terra", porta=(18, 26, 54), janela=None,
                       rombo=rombo, destelhada=destelhada)
    assert (q.w, q.h) == (W, H), (q.w, q.h, W, H)
    return q


def folha_casa(k):
    """Folha do sprite: inteira e destelhada lado a lado."""
    a, b = casa_rua(k), casa_rua(k, destelhada=True)
    im = Image.new("RGBA", (a.w * 2, a.h))
    im.paste(Image.fromarray(a.rgba(), "RGBA"), (0, 0))
    im.paste(Image.fromarray(b.rgba(), "RGBA"), (a.w, 0))
    return im


# ---------------------------------------------------------------- capela
def capela(sem=3):
    """Capela de sertão: frontão com volutas e a sineira com o sino, cruz de ferro no alto,
    cornija, cunhais nas quinas, porta em arco de tábuas, duas janelinhas em arco, barrado
    de barro, calçada de dois degraus e a parede do lado na sombra com a telha por cima."""
    W, H = 150, 150
    q = Quadro(W, H)
    X, Y = q.xx, q.yy
    rz = lambda e, s_: ruido(H, W, e, sem * 31 + s_)  # noqa: E731
    x0, x1 = 8, 114                      # fachada
    cx = (x0 + x1) / 2
    yt, yb = 70, H                       # cornija / chão
    lado = 26
    # silhueta do frontão: miolo reto em cima, volutas descendo para as quinas
    d = np.abs(X + 0.5 - cx)
    meia = (x1 - x0) / 2
    topo = np.where(d < 15, 24.0,
                    np.where(d < 20, 24 + (d - 15) * 1.5,
                             32 + (yt - 30 - 32) * np.clip((d - 20) / (meia - 24), 0, 1) ** 0.6))
    topo = np.where(d < 15, topo, topo + 4 * np.sin(np.clip((d - 20) / (meia - 24), 0, 1) * np.pi))
    topo = np.where(d >= meia - 4, yt - 6, topo)
    frontao = (X >= x0) & (X < x1) & (Y >= topo) & (Y < yt)
    corpo = (X >= x0) & (X < x1) & (Y >= yt) & (Y < yb)
    fach = frontao | corpo
    luz = 0.88 - 0.12 * (X - x0) / (x1 - x0) + 0.03 * rz(12, 1)
    # barro subindo da calçada, escorridos de chuva da cornija
    luz -= 0.28 * np.clip((Y - (yb - 26)) / 26, 0, 1) * (0.7 + 0.3 * (rz(3, 2) > 0))
    esc = (ruido(1, W, 1.2, sem + 3)[0] > 1.3)[None, :] & (Y > yt + 3) & (Y < yt + 22 + 14 * rz(8, 4))
    luz = np.where(esc, luz - 0.16, luz)
    luz = np.where(rz(0.7, 5) > 2.4, luz - 0.18, luz)
    # borda do frontão acesa (a luz bate de cima)
    borda_f = frontao & ~np.roll(frontao, 2, axis=0)
    luz = np.where(borda_f, 0.99, luz)
    q.pinta(fach, "cal", quantiza_limpo(np.clip(luz, 0, 0.999), 6))
    # rachaduras
    for fx, fy, n in ((0.18, yt + 6, 26), (0.86, yt + 30, 20), (0.64, 40, 14)):
        x, y = x0 + fx * (x1 - x0), float(fy)
        rr = np.random.default_rng(sem + n)
        for _ in range(n):
            if fach[int(y), int(x)]:
                q.img[int(y), int(x)] = cm.RGB["cal"][1]
            x += rr.choice([-1, 0, 1]) * 0.8; y += 1
    # reboco caído mostrando o tijolo de adobe
    caido = (fbm(H, W, sem + 6) > 1.05) & corpo & (Y > yt + 8) & (Y < yb - 14)
    from scipy import ndimage
    caido = ndimage.binary_opening(caido, np.ones((3, 3)))
    adobe = ((Y % 6) == 0) | (((X + 5 * ((Y // 6) % 2)) % 11) == 0)
    q.pinta(caido, "terra", np.where(adobe, 0.28, 0.55 - 0.1 * (X > cx)))
    # barrado de barro pintado embaixo
    barr = corpo & (Y >= yb - 12)
    q.pinta(barr, "terra", quantiza_limpo(np.clip(0.52 - 0.1 * (X - x0) / (x1 - x0) + 0.05 * rz(3, 7)
                                                  - 0.15 * (Y >= yb - 3), 0, 0.999), 5))
    q.pinta(corpo & (Y == yb - 13), "terra", np.full((H, W), 0.35))
    # cunhais (pilastras nas quinas): um degrau mais claros, sombra à direita
    for px in (x0, x1 - 7):
        cun = (X >= px) & (X < px + 7) & (Y >= yt - 6) & (Y < yb - 12)
        q.pinta(cun, "cal", np.where(X == px + 6, 0.5, np.where(X == px, 0.99, 0.9 - 0.05 * (px > cx))))
    # cornija: faixa saliente com luz em cima e sombra embaixo
    cor = (X >= x0 - 3) & (X < x1 + 3) & (Y >= yt - 4) & (Y < yt + 1)
    q.pinta(cor, "cal", np.where(Y == yt - 4, 0.99, np.where(Y == yt - 3, 0.8, np.where(Y == yt, 0.25, 0.6))))
    q.pinta((X >= x0) & (X < x1) & (Y >= yt + 1) & (Y < yt + 3), "cal", np.full((H, W), 0.35))
    # sineira no frontão: vão em arco, escuro, com o sino de bronze pendurado
    sx, sy0, sy1, sl = cx, 32, 58, 9
    arco = (np.abs(X + 0.5 - sx) < sl) & (Y >= sy0 + sl) & (Y < sy1) | \
        (np.hypot(X + 0.5 - sx, Y - (sy0 + sl)) < sl) & (Y < sy0 + sl)
    q.pinta(arco, "madeira", np.where(X + 0.5 < sx - sl + 3, 0.02, 0.1))
    moldura = ndimage.binary_dilation(arco, np.ones((3, 3))) & ~arco & frontao
    q.pinta(moldura, "cal", np.where(Y < sy0 + sl, 0.99, np.where(X > sx, 0.5, 0.8)))
    sino = (np.abs(X + 0.5 - sx) < 2.5 + (Y - (sy0 + 7)) * 0.4) & (Y >= sy0 + 7) & (Y < sy0 + 20)
    sino |= (np.abs(X + 0.5 - sx) < 8) & (Y >= sy0 + 19) & (Y < sy0 + 21)
    q.pinta(sino, "terra", np.clip(0.8 - 0.6 * (X + 0.5 - sx + 5) / 12 - 0.15 * (Y == sy0 + 20)
                                   + 0.15 * ((X + 0.5 - sx > -4) & (X + 0.5 - sx < -2)), 0, 0.999))
    q.pinta((np.abs(X + 0.5 - sx) < 1) & (Y >= sy0 + 1) & (Y < sy0 + 7), "madeira", np.full((H, W), 0.5))
    q.pinta((np.abs(X + 0.5 - sx) < 1) & (Y >= sy0 + 21) & (Y < sy0 + 24), "terra", np.full((H, W), 0.2))
    q.pinta((Y >= sy0 + 1) & (Y < sy0 + 3) & (np.abs(X + 0.5 - sx) < sl), "madeira", np.where(Y == sy0 + 1, 0.55, 0.25))
    # cruz de ferro no alto
    cruz = ((np.abs(X + 0.5 - cx) < 1.5) & (Y >= 1) & (Y < 24)) | ((np.abs(X + 0.5 - cx) < 7.5) & (Y >= 6) & (Y < 9))
    q.pinta(cruz, "madeira", np.where((X + 0.5 < cx) | (Y == 6), 0.5, 0.15))
    q.pinta((np.abs(X + 0.5 - cx) < 4.5) & (Y >= 21) & (Y < 24), "cal", np.where(Y == 21, 0.9, 0.55))
    # porta em arco: tábuas, ferragem, o vão um pouco aberto no meio
    pw, ph = 30, 58
    pa = (np.abs(X + 0.5 - cx) < pw / 2) & (Y >= yb - ph + pw / 2) & (Y < yb - 3) | \
        (np.hypot(X + 0.5 - cx, Y - (yb - ph + pw / 2)) < pw / 2) & (Y < yb - ph + pw / 2)
    tab = (X - int(cx - pw / 2)) % 6
    lz = 0.48 + 0.14 * (tab == 1) - 0.25 * (tab == 5) + 0.06 * rz(1, 8) - 0.18 * (X > cx)
    lz = np.where(np.abs(X + 0.5 - cx) < 1, 0.03, lz)
    lz = np.where((Y % 14 == 0) & (np.abs(X + 0.5 - cx) > 2), 0.15, lz)        # travessas de ferro
    q.pinta(pa, "madeira", np.clip(lz, 0, 0.999))
    cant = ndimage.binary_dilation(pa, np.ones((5, 5))) & ~pa & corpo & (Y < yb - 3)
    q.pinta(cant, "cal", np.where(X < cx, 0.95, 0.6))
    q.pinta(ndimage.binary_dilation(pa, np.ones((3, 3))) & ~pa & cant & (X >= cx), "cal", np.full((H, W), 0.4))
    # janelinhas em arco no alto, de folha fechada
    for jx in (cx - 34, cx + 34):
        ja = (np.abs(X + 0.5 - jx) < 5) & (Y >= yt + 14) & (Y < yt + 32) | \
            (np.hypot(X + 0.5 - jx, Y - (yt + 14)) < 5) & (Y < yt + 14)
        q.pinta(ja, "madeira", np.where(X + 0.5 < jx, 0.35, 0.2) + 0.12 * ((Y - yt) % 5 == 0))
        mj = ndimage.binary_dilation(ja, np.ones((3, 3))) & ~ja & corpo
        q.pinta(mj, "cal", np.where(X < jx, 0.99, 0.55))
        q.pinta((np.abs(X + 0.5 - jx) < 7) & (Y >= yt + 32) & (Y < yt + 34), "cal", np.where(Y == yt + 32, 0.99, 0.35))
    # parede do lado na sombra, com a água do telhado por cima
    ml = (X >= x1) & (X < x1 + lado) & (Y >= yt + 2 + (X - x1) * 0.25) & (Y < yb)
    lz = 0.32 + 0.05 * rz(2.5, 9) - 0.15 * np.clip((Y - (yb - 20)) / 20, 0, 1)
    q.pinta(ml, "cal", quantiza_limpo(np.clip(lz, 0, 0.999), 6))
    q.pinta(ml & (Y >= yb - 12), "terra", np.full((H, W), 0.3))
    tt = (X >= x1 - 1) & (X < x1 + lado + 4) & (Y >= yt - 6 + (X - x1) * 0.25) & (Y < yt + 4 + (X - x1) * 0.25)
    u = (X - x1) % 7 / 7.0
    lz = 0.25 + 0.5 * np.cos((u - 0.38) * np.pi) - 0.25 * (Y > yt + 1 + (X - x1) * 0.25)
    q.pinta(tt, "telha", quantiza_limpo(np.clip(lz, 0, 0.999), 6))
    # calçada de dois degraus na frente da porta
    for k, (larg, alt) in enumerate(((50, 3), (40, 3))):
        yy0 = yb - 3 * (k + 1)
        dg = (np.abs(X + 0.5 - cx) < larg / 2) & (Y >= yy0) & (Y < yy0 + alt)
        q.pinta(dg, "cal", np.where(Y == yy0, 0.8, 0.35 + 0.1 * ((X // 7) % 2)))
    return q


def cruzeiro(sem=5):
    """Cruzeiro de madeira lavrada sobre base caiada de três degraus, com fitas de promessa
    amarradas no braço e tocos de vela no pé."""
    W, H = 50, 96
    q = Quadro(W, H)
    X, Y = q.xx, q.yy
    cx = W / 2
    for k, (larg, a0, a1) in enumerate(((46, 88, 96), (36, 81, 88), (26, 75, 81))):
        m = (np.abs(X + 0.5 - cx) < larg / 2) & (Y >= a0) & (Y < a1)
        u = (X + 0.5 - (cx - larg / 2)) / larg
        lz = np.where(Y == a0, 0.99, 0.82 - 0.25 * u) - 0.25 * (u > 0.82)
        lz = lz - 0.18 * ((X + 3 * k) % 9 == 0) * (Y > a0)
        q.pinta(m, "cal", quantiza_limpo(np.clip(lz, 0, 0.999), 6))
    # haste e braço de madeira lavrada (quina acesa à esquerda)
    def viga(m, u):
        lz = 0.3 + 0.5 * np.cos((u - 0.3) * np.pi) + 0.06 * ruido(H, W, (3, 0.6), sem)
        lz = np.where(((Y * 3 + X) % 11 == 0) & (u > 0.2) & (u < 0.8), lz - 0.15, lz)
        q.pinta(m, "madeira", np.clip(lz, 0, 0.999))
    hx0, hx1 = cx - 4.5, cx + 4.5
    viga((X + 0.5 >= hx0) & (X + 0.5 < hx1) & (Y >= 3) & (Y < 75), (X + 0.5 - hx0) / 9)
    viga((X >= 3) & (X < W - 3) & (Y >= 20) & (Y < 28), np.clip((Y - 20) / 8.0, 0, 1))
    q.pinta((X >= 3) & (X < W - 3) & (Y == 28), "madeira", np.full((H, W), 0.1))
    q.pinta((X + 0.5 >= hx0) & (X + 0.5 < hx1) & (Y == 3), "madeira", np.full((H, W), 0.9))
    q.pinta(((X == 3) | (X == W - 4)) & (Y >= 20) & (Y < 28), "madeira", np.full((H, W), 0.7))
    # plaquinha e fitas de promessa
    q.pinta((np.abs(X + 0.5 - cx) < 5) & (Y >= 9) & (Y < 15), "cal", np.where(Y == 9, 0.9, 0.6))
    for fx, rampa, comp in ((8, "telha", 16), (12, "cal", 11), (37, "verde", 14), (41, "telha", 10)):
        fita = (np.abs(X - (fx + 1.2 * np.sin((Y - 28) / 3.0))) < 1) & (Y >= 28) & (Y < 28 + comp)
        q.pinta(fita, rampa, np.full((H, W), 0.75 if rampa != "cal" else 0.9) - 0.2 * (Y > 28 + comp * 0.6))
    # tocos de vela no degrau
    for vx in (13, 16, 34):
        q.pinta((X >= vx) & (X < vx + 2) & (Y >= 70 + (vx % 3)) & (Y < 75), "cal", np.where(X == vx, 0.99, 0.7))
    q.pinta((X >= 6) & (X < 44) & (Y == 75), "madeira", np.full((H, W), 0.18))
    return q


# ---------------------------------------------------------------- camadas
# `ate`: até onde a camada vai (o trecho seguinte estende a mesma pintura); as peças da vila
# continuam sorteadas só até o limite dela, para não mudar quando a camada cresce.
def camada_paredao(h=130, ate=None):
    return cm.camada_paredao(h, ate=ate or limite(0.2))


def camada_meio(h=90, ate=None, planos_extra=()):
    """Os morros da caatinga continuam; no fim, num patamar, a vila alta vista de longe."""
    fator = 0.45
    lim = limite(fator)
    v0, v1 = 1780, 2010                       # patamar da vila alta ao longe
    q = cm.camada_meio(h, ate=ate or lim, planos_extra=[(v0, v1, 30)] + list(planos_extra))
    oy = h - 90                               # folga em cima (ver caatinga_ms.camada_meio)
    rng = np.random.default_rng(21)
    x0 = cm.limite(fator) - 20
    # moitas e árvores pequenas enevoadas na encosta
    topo = np.argmax(q.a, axis=0)
    for _ in range(26):
        cx = rng.uniform(x0, lim); r = rng.uniform(3, 6)
        cy = topo[int(cx)] + rng.uniform(3, 24)
        d = np.hypot(q.xx - cx, (q.yy - cy) * 1.4) / r
        mm = (d < 1) & (q.yy < cy + 2)
        lz = 0.5 - 0.35 * (q.xx - cx) / r - 0.45 * (q.yy - cy) / r
        q.pinta(mm, "verde", np.clip(lz * 0.5 + 0.2, 0, 0.999))
    x = x0 + 30.0
    while x < lim:
        if not (v0 - 30 < x < v1 + 30):
            p = nevoa(cm.arvore(int(rng.uniform(34, 50)), sem=int(x), folhas=rng.random() > 0.25), 0.42)
            q.colar(p, x - p.w / 2, topo[int(min(x, q.w - 1))] + rng.uniform(2, 8) - p.h)
        x += rng.uniform(50, 110)
    # casario da vila alta: casinhas lado a lado e a torre da igreja matriz
    x = v0 + 6
    k = 0
    while x < v1 - 40:
        c = nevoa(cm.casinha_longe(int(rng.integers(38, 54)), int(rng.integers(18, 26)), sem=90 + k), 0.36)
        q.colar(c, x, 30 + oy - c.h + 1)
        x += c.w + int(rng.integers(2, 10))
        k += 1
        if k == 2:                             # torre da matriz entre as casas
            t = Image.fromarray(capela(7).rgba(), "RGBA")
            t = t.resize((t.width * 2 // 5, t.height * 2 // 5), Image.BOX)
            a = np.array(t)
            tq = Quadro(a.shape[1], a.shape[0])
            tq.img = cm.encaixar(a[..., :3]); tq.a = a[..., 3] > 140
            nevoa(tq, 0.36)
            q.colar(tq, x, 30 + oy - tq.h + 1)
            x += tq.w + 4
    return q


def camada_perto(h=160, ate=None):
    """Plano de trás (0,75): as casas da vila atrás da rua, uma de barro sem reboco,
    uma arrombada, árvores e mandacarus entre elas, moitas no pé."""
    fator = 0.75
    lim = limite(fator)
    q = cm.camada_perto(h, ate=ate or lim)
    chao = h - 1
    rng = np.random.default_rng(32)
    x0 = cm.limite(fator)
    # moitas enchendo o pé
    x = float(x0 - 10)
    while x < lim:
        if rng.random() < 0.72:
            p = cm.moita(int(rng.integers(30, 56)), int(rng.integers(14, 22)), sem=int(x), seca=rng.uniform(0.2, 0.7))
        else:
            p = cm.xiquexique(int(rng.integers(22, 34)), int(rng.integers(16, 24)), sem=int(x) + 1)
        q.colar(p, x, chao - p.h + 3)
        x += rng.integers(26, 64)
    # casas menores que as da rua (estão mais longe) e um pouco enevoadas
    casa = lambda *a, **k: nevoa(cm.casa(*a, sombra_beiral=True, **k), 0.14)  # noqa: E731
    pecas = [
        (x0 - 10, cm.arvore(132, sem=140, folhas=True)),
        (x0 + 60, casa(96, 52, 32, sem=41, alpendre=False, lado=16, porta=(24, 20, 36), janela=(62, 12, 16))),
        (x0 + 236, cm.arvore(118, sem=141, folhas=False)),
        (x0 + 290, casa(84, 50, 30, sem=42, alpendre=True, lado=14, porta=(18, 20, 34), janela=(52, 12, 14),
                        parede="terra")),
        (x0 + 476, cm.mandacaru(84, sem=240)),
        (x0 + 530, casa(104, 56, 34, sem=43, alpendre=False, lado=18, porta=(70, 20, 36), janela=(16, 14, 18))),
        (x0 + 690, cm.arvore(140, sem=142, folhas=True)),
    ]
    for x, p in sorted(pecas, key=lambda e: -e[1].h):
        q.colar(p, x, chao - p.h + 2)
    return q


def camada_frente(h=44, ate=None):
    return cm.camada_frente(h, ate=ate or limite(1.1))


def camada_jogo(fase, alt=176, topo_mundo=40, ate=None):
    """Plano do jogo: o chão da caatinga continua pela rua da vila (mais batido, menos
    pedra), a capela, o cruzeiro, o girau, potes e cabaças na luz da cena."""
    import fase1 as f1
    F = fase.FASE
    CH = f1.CHAO
    q = cm.camada_jogo(fase, alt, topo_mundo, ate=ate or VILA_FIM + 40)
    w = VILA_FIM + 120               # as contas do sorteio seguem a largura da vila
    y = lambda wy: wy - topo_mundo  # noqa: E731
    yc = y(CH) - 1
    rng = np.random.default_rng(73)
    # pedrinhas encaixadas no chão da rua (menos que na caatinga)
    for _ in range(int((w - VILA_INI) / 548 * 40)):
        px = rng.uniform(VILA_INI - 60, w); py = rng.uniform(y(CH) + 3, alt + 2)
        rx = rng.uniform(2.5, 6) * (1 + (py - y(CH)) / 30); ry = rx * rng.uniform(0.45, 0.7)
        j0, j1 = int(max(0, py - ry - 3)), int(min(alt, py + ry + 4))
        i0, i1 = int(max(0, px - rx - 3)), int(min(w, px + rx + 4))
        if j1 <= j0 or i1 <= i0:
            continue
        sub = Quadro(i1 - i0, j1 - j0)
        sub.img[:] = q.img[j0:j1, i0:i1]; sub.a[:] = q.a[j0:j1, i0:i1]
        X, Y = sub.xx + i0, sub.yy + j0
        d = np.hypot((X - px) / rx, (Y - py) / ry) + 0.12 * ruido(sub.h, sub.w, 0.8, int(px))
        som = (np.hypot((X - px - 1.5) / rx, (Y - py - 1.5) / ry) < 1) & (Y > py) & sub.a
        sub.img[som] = cm.escurecer(sub.img[som], 1)
        lz = 0.55 - 0.35 * (X - px) / rx - 0.5 * (Y - py) / ry
        sub.pinta(d < 1, "terra", np.clip(lz, 0, 0.999))
        q.img[j0:j1, i0:i1] = sub.img
    # capim no pé das paredes e das coisas
    x = VILA_INI - 40.0
    while x < VILA_FIM:
        c = cm.capim(rng.uniform(5, 9), int(x), folhas=int(rng.integers(3, 6)))
        q.colar(c, x, yc - c.h + 2)
        x += rng.uniform(20, 56)
    # capela: sprite à parte em 2.5D (predios25.capela25, porta em x 3468). O cruzeiro fica
    # recuado como as casas (chao_largo.RECUO): nada alto na linha onde se anda.
    import chao_largo as cl
    q.sombra(3592, yc - cl.RECUO + 1, 22, 2.5)
    q.assentar(cruzeiro(), 3585, yc - cl.RECUO)
    # pedras e xique-xiques soltos
    for k, x in enumerate((3000, 3640)):
        q.assentar(cm.pedra(int(rng.integers(18, 28)), int(rng.integers(10, 14)), sem=k + 80), x, yc, afundar=2)
    for x in (3050, 3540, 3870):
        q.assentar(cm.xiquexique(int(rng.integers(24, 32)), int(rng.integers(18, 24)), sem=x), x, yc, afundar=2)
    # girau da vila e os objetos miúdos, na luz da cena
    amb = lambda t: ambientar(t.imagem())  # noqa: E731
    # (o girau agora é peça 2.5D à parte: chao_largo.pecas_fase1)
    for x, peca in ((3170, f1.pote_barro(7)), (3400, f1.cabacas()), (3840, f1.pilao()), (3560, f1.pote_barro(8, 12))):
        q.assentar(amb(peca), x, yc)
    if ate:                          # o trecho seguinte continua daqui e faz a passagem
        return q
    # a passagem para a vila alta: o chão novo some em manchas sobre o antigo
    corte = np.clip((VILA_FIM + 40 - q.xx) / 120.0, 0, 1) + 0.25 * ruido(alt, q.w, 3, 99)
    q.a &= corte > 0.5
    return q
