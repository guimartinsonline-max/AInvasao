"""Camadas do cenário da fase 1 (caatinga), geradas por script.

Todas as camadas têm 384 px de largura e emendam nas bordas (repetem sem costura).
"""
import numpy as np
from scipy import ndimage

from motor import BAYER4, IDX, VAZIO, Tela

L = 384

NUVEM = ["ceu", "ceu_claro", "horizonte", "branco"]
SERRA = ["ceu", "ceu", "ceu_claro", "horizonte"]
ARENITO = ["terra_escura", "terra", "barro", "areia", "areia_clara"]
GALHO = ["sombra", "cinza_escuro", "cinza", "cinza_claro"]
FOLHA = ["sombra", "caatinga_esc", "caatinga", "mandacaru"]
CACTO = ["caatinga_esc", "caatinga_esc", "caatinga", "mandacaru"]
PEDRA = ["sombra", "azul_sombra", "cinza_escuro", "cinza", "cinza_claro"]
MADEIRA = ["couro_escuro", "couro", "couro_claro", "barro"]


def bayer(h, w, dx=0, dy=0):
    return np.roll(np.tile(BAYER4, (h // 4 + 2, w // 4 + 2)), (dy, dx), axis=(0, 1))[:h, :w]


def ruido(h, w, sigma, semente, wrap=True):
    rng = np.random.default_rng(semente)
    r = ndimage.gaussian_filter(rng.standard_normal((h, w)), sigma, mode="wrap" if wrap else "reflect")
    return r / (r.std() + 1e-9)


def degrade(t, y0, y1, cor_cima, cor_baixo, x0=0, x1=None, mascara=None):
    """Transição pontilhada (Bayer) entre duas cores nas linhas y0..y1."""
    x1 = t.w if x1 is None else x1
    b = bayer(t.h, t.w)
    for y in range(max(0, y0), min(t.h, y1)):
        f = (y - y0 + 0.5) / max(1, (y1 - y0))
        linha = np.where(b[y, x0:x1] < f, IDX[cor_baixo], IDX[cor_cima])
        if mascara is not None:
            m = mascara[y, x0:x1]
            t.px[y, x0:x1][m] = linha[m]
        else:
            t.px[y, x0:x1] = linha


def ceu(h=308, w=548):
    """Céu da tela inteira (548x308): a faixa clara do horizonte fica atrás das serras."""
    t = Tela(w, h)
    faixas = [(0, "ceu_escuro"), (92, "ceu"), (176, "ceu_claro"), (240, "horizonte")]
    for k, (y, cor) in enumerate(faixas):
        fim = faixas[k + 1][0] if k + 1 < len(faixas) else h
        t.px[y:fim] = IDX[cor]
        if k + 1 < len(faixas):
            degrade(t, fim - 10, fim + 6, cor, faixas[k + 1][1])
    return t


def nuvens(semente=3):
    t = Tela(L, 90)
    rng = np.random.default_rng(semente)
    for (cx, by, larg) in [(50, 46, 70), (190, 30, 56), (300, 60, 90)]:
        puffs = []
        n = int(larg / 9)
        for k in range(n):
            x = cx - larg / 2 + (k + 0.5) * larg / n + rng.uniform(-3, 3)
            centro = 1 - abs((k + 0.5) / n - 0.5) * 2
            r = 6 + centro * larg * 0.16 + rng.uniform(-2, 2)
            puffs.append((x, by - r * 0.55, r))
        # Puffs de trás (mais escuros) primeiro, depois os da frente.
        for k, (x, y, r) in enumerate(sorted(puffs, key=lambda p: -p[2])):
            m = t.elipse(x % L, y, r, r * 0.85) | t.elipse(x % L - L, y, r, r * 0.85) | t.elipse(x % L + L, y, r, r * 0.85)
            m &= t.yy < by
            t.cel(m, NUVEM, sombra=3, luz=2, linha=False, rebaixo=True)
        # Base reta e sombreada.
        base = (t.yy >= by - 3) & (t.yy < by) & (t.px != VAZIO)
        t.px[base] = IDX["ceu_claro"]
    return t


def serras(h=200, Ls=768):
    """Serras azuladas ao longe em duas fileiras (a de trás mais clara), com
    volume suave, encostas na sombra e névoa até o horizonte."""
    t = Tela(Ls, h)
    x = np.arange(Ls)

    def fileira(base, amp, semente, rampa):
        perfil = (base + amp * np.sin(x / Ls * 2 * np.pi * 3 + semente) + amp * 0.45 * np.sin(x / Ls * 2 * np.pi * 7 + 2 * semente)
                  + 2.5 * ruido(1, Ls, 10, semente)[0])
        perfil = ndimage.uniform_filter1d(perfil, 11, mode="wrap")
        m = t.yy >= perfil[None, :]
        sub = Tela(Ls, h)
        sub.volume(m, rampa, luz=(-0.8, -0.5), achatado=14, suave=4, ambiente=0.3, linha=False)
        t.px[m] = sub.px[m]
        return m

    m1 = fileira(46, 12, 7, ["ceu_medio", "ceu_claro", "ceu_claro", "ceu_luz"])
    m2 = fileira(78, 9, 13, ["ceu", "ceu_medio", "ceu_claro", "ceu_luz"])
    m = m1 | m2
    # Névoa: as serras clareiam para baixo até sumir no horizonte.
    degrade(t, 110, 140, "ceu_medio", "ceu_claro", mascara=m & (t.yy >= 110) & (t.px == IDX["ceu_medio"]))
    t.px[m & (t.yy >= 140) & (t.px != IDX["ceu_luz"])] = IDX["ceu_claro"]
    degrade(t, h - 30, h, "ceu_claro", "horizonte", mascara=m)
    return t


def paredoes(semente=11, h=130):
    """Paredões de arenito em blocos com volume (tools/arte/rocha.py), 768 px emendando."""
    import rocha
    return rocha.paredoes(768, h, semente)


def planicie(h=40):
    """Chão distante entre os paredões e a caatinga."""
    t = Tela(L, h)
    t.px[:] = IDX["areia"]
    degrade(t, 0, 10, "areia_clara", "areia")
    degrade(t, h - 14, h, "areia", "barro")
    return t


def galho(t, x, y, ang, comp, esp, prof, rng):
    if prof == 0 or comp < 2:
        return
    x2 = x + np.cos(ang) * comp
    y2 = y - np.sin(ang) * comp
    for dx in (0, L, -L):
        t.cel(t.capsula(x + dx, y, x2 + dx, y2, esp, max(esp * 0.7, 0.5)), GALHO, sombra=1, luz=0, linha=False)
    n = 2 if prof > 1 else 3
    for k in range(n):
        da = rng.uniform(0.25, 0.7) * (1 if k % 2 else -1)
        galho(t, x2, y2, ang + da, comp * rng.uniform(0.55, 0.75), esp * 0.7, prof - 1, rng)
    if prof <= 2 and rng.random() < 0.6:
        for dx in (0, L, -L):
            t.cel(t.elipse(x2 + dx, y2, rng.uniform(2.5, 4.5), rng.uniform(1.6, 2.6)), FOLHA, sombra=1, luz=1)


def mandacaru(t, x, chao, altura, rng):
    corpo = t.capsula(x, chao, x, chao - altura, 3.2, 3.0)
    bracos = []
    for lado, hb, ab in ((-1, 0.45, 0.35), (1, 0.6, 0.3)):
        if rng.random() < 0.85:
            yb = chao - altura * hb
            xb = x + lado * 7
            bracos.append(t.capsula(x, yb, xb, yb, 2.2) | t.capsula(xb, yb, xb, yb - altura * ab, 2.3, 2.1))
    for m in bracos + [corpo]:
        t.cel(m, CACTO, sombra=1, luz=1)
        # Costelas: listras verticais claras e escuras.
        cols = np.where(m.any(0))[0]
        for c in cols[1:-1:2]:
            col = m[:, c] & (t.px[:, c] != IDX["caatinga_esc"])
            t.px[col, c] = IDX["mandacaru"] if c % 4 == 1 else IDX["caatinga"]
    # Espinhos.
    ys, xs = np.where(corpo | (bracos[0] if bracos else corpo))
    for k in range(0, len(xs), 11):
        t.ponto(xs[k] + (1 if xs[k] > x else -1), ys[k], "areia_clara")


def caatinga(semente=21):
    h = 80
    t = Tela(L, h)
    rng = np.random.default_rng(semente)
    chao = h - 6
    # Moitas de fundo.
    for _ in range(18):
        cx, r = rng.uniform(0, L), rng.uniform(6, 14)
        for dx in (0, L, -L):
            t.cel(t.elipse(cx + dx, chao - r * 0.4, r, r * 0.6), FOLHA, sombra=2, luz=1, linha=False, deslocar=-1)
    # Árvores secas retorcidas.
    for xa in (30, 150, 255, 345):
        galho(t, xa + rng.uniform(-8, 8), chao, np.pi / 2 + rng.uniform(-0.2, 0.2), rng.uniform(16, 22), 2.2, 4, rng)
    for xm in (95, 205, 310):
        mandacaru(t, xm, chao, rng.uniform(26, 38), rng)
    # Moitas da frente.
    for _ in range(14):
        cx, r = rng.uniform(0, L), rng.uniform(5, 11)
        for dx in (0, L, -L):
            t.cel(t.elipse(cx + dx, chao - r * 0.3, r, r * 0.55), FOLHA, sombra=2, luz=1)
    # Faixa de terra no pé.
    m = t.yy >= chao
    t.chapado(m, "areia")
    degrade(t, chao, h, "areia", "barro")
    t.contorno("caatinga_esc")
    return t


def chao_tile(w=256, h=24, semente=31):
    """Ladrilho do chão do campo de treino: o mesmo chão em corte da fase 1."""
    import rocha
    return rocha.chao(w, h, semente)

def touceira(semente):
    """Tufo de capim seco para enfeitar a beira do chão."""
    t = Tela(14, 10)
    rng = np.random.default_rng(semente)
    for _ in range(9):
        x = rng.uniform(2, 12)
        topo = rng.uniform(0, 5)
        inc = rng.uniform(-3, 3)
        cor = rng.choice(["areia_clara", "areia", "barro", "mandacaru"])
        t.linha(int(x), 9, int(x + inc), int(topo), cor)
    return t


def caixote():
    t = Tela(24, 18)
    m = t.retangulo(0, 0, 24, 18)
    t.cel(m, MADEIRA, sombra=1, luz=1, linha=False)
    for y in (6, 12):
        t.px[y, :] = IDX["couro_escuro"]
    for y0 in (1, 7, 13):
        for x in range(2, 22, 5):
            t.ponto(x, y0 + 2, "couro")
    # Travessas e cantoneiras de metal.
    for x0 in (2, 19):
        t.cel(t.retangulo(x0, 0, 3, 18), MADEIRA, sombra=1, luz=1, deslocar=-1)
    for (x, y) in ((0, 0), (21, 0), (0, 15), (21, 15)):
        t.cel(t.retangulo(x, y, 3, 3), PEDRA, sombra=1, luz=1)
    t.contorno("sombra")
    return t


def laje(w=32, h=12):
    t = Tela(w, h)
    t.cel(t.retangulo(0, 0, w, h), PEDRA, sombra=3, luz=2, linha=False, rebaixo=True)
    n = ruido(h, w, 1.0, 4)
    t.px[(n > 1.3) & (t.yy > 2) & (t.yy < h - 2)] = IDX["cinza_escuro"]
    t.linha(9, 3, 12, 7, "azul_sombra")
    t.linha(22, 4, 20, 8, "azul_sombra")
    t.px[0, :] = IDX["cinza_claro"]
    t.px[1, ::3] = IDX["branco"]
    return t
