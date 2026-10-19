"""Fase 2, a base da cratera. Trecho 1: a borda da cratera (0 a 1700 px).

O trecho conta a explosão andando para a direita, sem repetir o fundo:
  A) 0-550    beira da caatinga pegando fogo: ainda tem verde, fumaça, casa ardendo ao fundo.
  B) 550-1150 terra arrasada: tudo queimado e deitado para longe da cratera, bois mortos,
              postes de telégrafo tombados, cerca da Volante.
  C) 1150-1700 chão virado vidro: pedra derretida, vidro verde-escuro rachado, a borda da
              cratera subindo no fundo com a coluna de fumaça verde, e a cancela da Volante.

Camadas (como na fase 1): f2_ceu (panorama do céu, 0,06), f2_longe (0,22), f2_meio (0,45),
f2_perto (0,75), f2_jogo (1), f2_frente (1,1). Prévia: python3 tools/arte/fase2.py
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from motor import IDX, VAZIO, Tela, RAIZ  # noqa: E402
from aliens import relevo, domo  # noqa: E402
import fase1 as f1  # noqa: E402

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
LARGURA = 1700
CHAO = 194
ALTURA_TELA, DY = 308, 92

CARVAO = ["preto", "marrom_noite", "couro_profundo", "sombra", "sombra_media", "cinza_escuro"]
CINZA_Q = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "cinza_claro"]
VIDRO = ["preto", "sombra", "alien_profundo", "alien_esc", "alien_medio", "alien"]
BRASA = ["vermelho_esc", "laranja_escuro", "laranja_fogo", "amarelo_fogo"]
TERRA_Q = ["marrom_noite", "couro_profundo", "terra_escura", "terra", "terra_media", "barro"]
OSSO = ["cinza_medio", "cinza", "cinza_luz", "cinza_claro", "branco"]
COURO_BOI = ["marrom_noite", "couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_claro"]


def ruido(h, w, s, semente):
    r = ndimage.gaussian_filter(np.random.default_rng(semente).standard_normal((h, w)), s)
    return r / (r.std() + 1e-9)


_GRAO = {}


def lim(h, w, s=1.1):
    """Limiar para misturar tons. Em vez do xadrez (Bayer), manchas orgânicas: ruído
    suave com distribuição uniforme, então a mistura sai em grumos irregulares."""
    k = (h, w, s)
    if k not in _GRAO:
        r = ndimage.gaussian_filter(np.random.default_rng(h * 7919 + w).standard_normal((h, w)), s)
        _GRAO[k] = (np.argsort(np.argsort(r.ravel())) / r.size).reshape(h, w)
    return _GRAO[k]


def colar_organico(t, peca, x, y, borda=80, semente=0, grao=5.0):
    """Cola um chão de outro tipo misturando nas pontas em manchas grandes e irregulares
    (ilhas de um no outro, como queimado avançando pelo chão), nunca em pontilhado."""
    h, w = peca.px.shape
    rng = np.random.default_rng(semente)
    xs = np.arange(w)[None, :].repeat(h, 0)
    rampa = np.clip(np.minimum(xs, w - 1 - xs) / borda, 0, 1)
    n = ruido(h, w, (grao * 0.6, grao), semente) * 0.55 + ruido(h, w, 1.0, semente + 1) * 0.12
    # Mais queimado em cima (a crosta) que embaixo: a mancha avança pela superfície.
    n += (0.5 - np.arange(h)[:, None] / h) * 0.3
    m = (rampa * 2 - 1 + n) > 0
    m = ndimage.binary_opening(m, iterations=1)
    p = peca.px.copy()
    p[~m] = VAZIO
    tmp = Tela(w, h)
    tmp.px = p
    t.colar(tmp, x, y)


def pintar_niveis(t, m, v, rampa, dither=False):
    """Pinta a máscara com o valor v (0-1) em faixas da rampa, com pontilhado na transição."""
    k = len(rampa)
    vv = np.clip(v, 0, 0.999) * k
    base = np.floor(vv)
    if dither:
        frac = vv - base
        base = base + ((frac > 0.75) & (lim(*m.shape) < (frac - 0.75) * 4))
    n = np.clip(base, 0, k - 1).astype(int)
    t.px[m] = np.array([IDX[c] for c in rampa])[n[m]]


# ------------------------------------------------------------------ chão

TERRA_CORTE = ["marrom_noite", "terra_escura", "terra", "terra_media", "barro", "areia_media"]


def chao_base(w, h=26, semente=0):
    """Chão em corte da fase 2, sem pontilhado: crosta clara com calombos, estratos de
    terra ondulados em faixas lisas que escurecem para baixo, pedras enterradas com
    volume e contorno, pedrisco, raízes e rachaduras."""
    import rocha
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    yy = t.yy - 0.5
    n = ruido(h, w, (1.2, 7), semente)
    faixa = np.floor((yy + n * 1.8) / 5)
    v = 0.92 - yy / h * 0.62 + np.where(faixa % 2 == 0, 0.0, -0.13) + ruido(h, w, (1.5, 4), semente + 1) * 0.05
    pintar_niveis(t, np.ones((h, w), bool), v, TERRA_CORTE)
    # Manchas de cascalho claro dentro dos estratos.
    casc = (ruido(h, w, (1, 3), semente + 2) > 1.5) & (t.yy > 5)
    t.px[casc] = IDX["areia_media"]
    # Pedras enterradas com volume e contorno.
    for k in range(w // 12):
        grande = rng.random() < 0.35
        pw = rng.uniform(5, 11) if grande else rng.uniform(2, 4.5)
        ph = pw * rng.uniform(0.5, 0.75)
        cx, cy = rng.uniform(0, w), rng.uniform(h * 0.5, h - 1) if grande else rng.uniform(6, h - 2)
        m = t.elipse(cx, cy, pw, ph, ang=rng.uniform(-0.3, 0.3))
        relevo(t, m, domo(t, cx, cy, pw, ph) * 2.5, rocha.PEDRA_CHAO if rng.random() < 0.6 else rocha.PEDRA_TERRA,
               ambiente=0.1, linha=False)
        t.px[m & ~ndimage.binary_erosion(m)] = IDX["marrom_noite"]
    # Pedrisco.
    for _ in range(w // 4):
        x, y = int(rng.integers(0, w)), int(rng.integers(5, h))
        t.px[y, x] = IDX[rng.choice(["cinza_luz", "cinza_medio", "areia_luz", "terra_escura"])]
    # Raízes finas descendo do topo.
    for _ in range(w // 30):
        x, y = rng.uniform(0, w), 3
        for _k in range(int(rng.integers(5, 12))):
            x += rng.uniform(-1.2, 1.2)
            y += 1
            if 0 <= int(x) < w and int(y) < h:
                t.px[int(y), int(x)] = IDX["couro_escuro"]
    # Crosta de cima: lábio claro com calombos e a sombra logo abaixo.
    topo = (ruido(1, w, 3, semente + 3)[0] > 0.4).astype(int)
    for x in range(w):
        t.px[0, x] = IDX["areia_clara" if topo[x] else "areia_luz"]
        t.px[1, x] = IDX["areia_luz" if topo[x] else "areia"]
        t.px[2, x] = IDX["areia"]
        t.px[3, x] = IDX["barro"] if (x // 3 + topo[x]) % 4 else IDX["terra"]
    # Rachaduras com aresta clara.
    for _ in range(w // 24):
        x, y = rng.uniform(0, w), 2
        for _k in range(int(rng.integers(3, 8))):
            x += rng.uniform(-1, 1)
            y += 1
            X, Y = int(x) % w, int(y)
            if Y < h:
                t.px[Y, X] = IDX["terra_escura"]
                t.px[Y, (X + 1) % w] = IDX["barro"]
    return t


CHAMUSCA = {"areia_clara": "areia_media", "areia_luz": "barro", "areia": "terra_media", "areia_media": "terra",
            "barro": "terra", "terra_media": "terra_escura", "terra": "couro_profundo", "terra_escura": "marrom_noite"}


def chao_chamuscado(w, h=26, semente=0):
    """Estágio do meio: a terra escureceu com o calor, a crosta virou marrom e há
    tocos de capim pretos, mas ainda não é cinza."""
    t = chao_base(w, h, semente)
    tab = {IDX[a]: IDX[b] for a, b in CHAMUSCA.items()}
    px = t.px.copy()
    for a_, b_ in tab.items():
        px[(t.px == a_) & (t.yy < 14 + ruido(h, w, (1, 6), semente + 4) * 3)] = b_
    t.px = px
    fuligem = (ruido(h, w, (0.8, 4), semente + 5) > 1.0) & (t.yy < 4)
    t.px[fuligem] = IDX["marrom_noite"]
    # Manchas de cinza na crosta, cada vez mais para o lado da queimada.
    cinza = (ruido(h, w, (0.7, 5), semente + 6) > 1.3 - t.xx / w * 1.8) & (t.yy < 2.5)
    t.px[cinza & (t.yy < 1)] = IDX["cinza_luz"]
    t.px[cinza & (t.yy >= 1)] = IDX["cinza_medio"]
    return t


def chao_queimado(w, h=26, semente=0):
    """Chão em corte queimado: crosta de cinza clara fofa com calombos e montinhos, logo
    abaixo uma faixa de carvão preta com brasas nas rachaduras, depois a terra torrada
    em estratos (mais escura e fria que a terra normal) com pedras escurecidas e raízes
    viradas carvão; o fundo volta aos poucos para a cor da terra."""
    t = chao_base(w, h, semente=semente)
    rng = np.random.default_rng(semente)
    L = lim(h, w, 2.0)
    n = ruido(h, w, (1, 5), semente + 1)
    prof = (t.yy - 0.5) + n * 1.4
    # Terra toda torrada: cada tom desce dois degraus para o lado frio/escuro.
    torra = {"areia_clara": "cinza", "areia_luz": "cinza_medio", "areia": "terra_media", "areia_media": "terra",
             "barro": "terra_escura", "terra_media": "couro_profundo", "terra": "couro_profundo",
             "terra_escura": "marrom_noite", "cinza_luz": "cinza_medio", "cinza": "cinza_escuro",
             "cinza_medio": "azul_sombra", "couro_escuro": "preto"}
    tab = {IDX[a]: IDX[b] for a, b in torra.items()}
    fundo = prof > 14 + n * 2
    px = t.px.copy()
    for a, b in tab.items():
        px[(t.px == a) & ~(fundo & (L < 0.5))] = b
    t.px = px
    # Faixa de carvão logo abaixo da crosta.
    carv = (prof > 2.2) & (prof < 5.5)
    t.px[carv & (L < 0.75)] = IDX["preto"]
    t.px[carv & (L >= 0.75)] = IDX["marrom_noite"]
    # Crosta de cinza: calombos fofos com luz em cima.
    t.px[0, :] = np.where(ruido(1, w, 2, semente + 2)[0] > -0.3, IDX["cinza_claro"], IDX["cinza_luz"])
    t.px[1, :] = np.where(L[1] < 0.6, IDX["cinza_luz"], IDX["cinza"])
    t.px[2, :] = np.where(L[2] < 0.4, IDX["cinza"], IDX["cinza_medio"])
    mancha = (ruido(h, w, (0.6, 3), semente + 3) > 1.1) & (t.yy < 3)
    t.px[mancha] = IDX["sombra"]
    # Rachaduras na crosta com brasa viva no fundo.
    for _ in range(w // 22):
        x, y = rng.uniform(0, w), 0
        comp = int(rng.integers(3, 8))
        for i in range(comp):
            X, Y = int(x) % w, int(y)
            if Y < h:
                quente = 1 <= i < comp - 1
                t.px[Y, X] = IDX["laranja_fogo" if quente and i % 2 else "vermelho_esc" if quente else "preto"]
                t.px[Y, (X + 1) % w] = IDX["preto"]
                if quente and i == 2 and Y + 1 < h:
                    t.px[Y, X] = IDX["amarelo_fogo"]
            x += rng.uniform(-1.3, 1.3)
            y += 1
    # Brasas soltas na faixa de carvão.
    for _ in range(w // 12):
        x, y = int(rng.integers(0, w)), int(rng.integers(3, 6))
        if t.px[y, x] == IDX["preto"]:
            t.px[y, x] = IDX["vermelho_esc" if rng.random() < 0.6 else "laranja_escuro"]
    return t


def chao_vidro(w, h=26, semente=0):
    """Chão virado vidro pelo calor do disco: placa verde-escura lisa e brilhante por
    cima (reflexo do céu em faixas), rachada em lascas com arestas claras, bolhas presas,
    areia fundida grudada; por baixo a terra torrada em estratos."""
    t = chao_queimado(w, h, semente)
    rng = np.random.default_rng(semente + 5)
    esp = (6 + ruido(1, w, 6, semente + 6)[0] * 1.5).clip(4, 9)
    m = t.yy < esp[None, :]
    # Vidro: escuro em baixo, reflexo do céu em faixa na parte de cima.
    v = 0.25 + (1 - t.yy / esp[None, :]) * 0.55 + ruido(h, w, (1, 8), semente + 7) * 0.08
    pintar_niveis(t, m, v, VIDRO)
    faixa = m & (t.yy >= 1) & (t.yy < 2.2) & (ruido(h, w, (0.5, 10), semente + 8) > -0.2)
    t.px[faixa] = IDX["ceu_luz"]
    t.px[m & (t.yy < 1)] = IDX["aco_brilho"]
    # Lascas: rachaduras quase retas com aresta clara de um lado.
    for _ in range(w // 18):
        x, y = rng.uniform(0, w), 0
        ang = rng.uniform(0.9, 2.2)
        for _k in range(int(rng.integers(4, 10))):
            X, Y = int(x) % w, int(y)
            if Y < h and m[Y, X]:
                t.px[Y, X] = IDX["preto"]
                if X + 1 < w and m[Y, X + 1]:
                    t.px[Y, X + 1] = IDX["alien_luz"]
            x += math.cos(ang) * 1.2
            y += math.sin(ang) * 1.0
    # Bolhas presas no vidro e grãos de areia fundida.
    for _ in range(w // 16):
        x, y = int(rng.integers(1, w - 2)), int(rng.integers(2, 6))
        if m[y, x]:
            t.px[y, x] = IDX["alien_brilho"]
            if m[y + 1, x]:
                t.px[y + 1, x] = IDX["alien_profundo"]
    for _ in range(w // 9):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, 7))
        if m[y, x] and rng.random() < 0.5:
            t.px[y, x] = IDX["areia_media"]
    # Borda de baixo do vidro: escorrido para dentro da terra.
    for x in range(w):
        y = int(esp[x])
        if y < h:
            t.px[y, x] = IDX["alien_profundo"]
            if rng.random() < 0.15 and y + 2 < h:
                t.px[y + 1, x] = IDX["alien_esc"]
                t.px[y + 2, x] = IDX["alien_profundo"]
    return t


# ------------------------------------------------------------------ madeira e metal detalhados

MADEIRA_V = ["preto", "couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_claro"]
MADEIRA_Q = ["preto", "preto", "marrom_noite", "couro_profundo", "couro_escuro", "couro"]
FERRO = ["preto", "sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]


def madeira(t, m, vertical=True, semente=0, rampa=MADEIRA_V, queima=0.0):
    """Madeira rústica: volume roliço, veios compridos no sentido da peça, nós escuros com
    anel claro, rachas e, com queima>0, a parte de baixo virando carvão com brasa."""
    if not m.any():
        return
    H = np.minimum(ndimage.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1], 3)
    relevo(t, m, H, rampa, ambiente=0.05, contraste=1.1, brilho=0.4, linha=False)
    rng = np.random.default_rng(semente)
    eixo = t.xx if vertical else t.yy
    ao_longo = t.yy if vertical else t.xx
    veio = (np.sin(eixo * 2.6 + np.sin(ao_longo * 0.35 + semente) * 1.2) > 0.82)
    interior = ndimage.binary_erosion(m)
    t.px[interior & veio] = IDX[rampa[2]]
    ys, xs = np.where(interior)
    for _ in range(len(ys) // 90 if len(ys) else 0):
        i = int(rng.integers(len(ys)))
        x, y = xs[i], ys[i]
        t.ponto(x, y, rampa[0])
        t.ponto(x + (0 if vertical else 1), y + (1 if vertical else 0), rampa[0])
        t.ponto(x - 1, y, rampa[4])
    if queima > 0:
        ys2, xs2 = np.where(m)
        y0, y1 = ys2.min(), ys2.max()
        frac = (t.yy - y0) / max(1, y1 - y0)
        q = m & (frac + ruido(t.h, t.w, 1.0, semente) * 0.12 > 1 - queima)
        t.px[q] = IDX["preto"]
        t.px[q & (lim(t.h, t.w) < 0.2)] = IDX["marrom_noite"]
        borda = q & ~ndimage.binary_erosion(q) & interior
        t.px[borda & (lim(t.h, t.w) < 0.4)] = IDX["laranja_escuro"]


def mourao(t, x, base, alto, inc=0.0, r=1.8, semente=0, queima=0.0):
    """Mourão de cerca: tora torta com casca, topo rachado em lasca."""
    m = t.capsula(x, base, x + inc, base - alto, r, r * 0.85)
    madeira(t, m, True, semente, queima=queima)
    t.ponto(x + inc, base - alto - r * 0.6, "couro_claro")
    t.ponto(x + inc + 0.6, base - alto + 1, "preto")
    return m


def farpa(t, x, y):
    """Farpa do arame: nozinho com quatro pontas."""
    t.ponto(x, y, "cinza_luz")
    for dx, dy in ((-1, -1), (1, 1), (1, -1), (-1, 1)):
        t.ponto(x + dx, y + dy, "cinza_escuro")


def fio(t, x0, y0, x1, y1, flecha=2.0, farpas=5, cor="cinza_escuro", luz="cinza"):
    """Arame esticado entre dois pontos, cedendo no meio (catenária), com farpas."""
    n = int(abs(x1 - x0) * 1.5) + 2
    for k in range(n):
        s_ = k / (n - 1)
        x = x0 + (x1 - x0) * s_
        y = y0 + (y1 - y0) * s_ + flecha * 4 * s_ * (1 - s_)
        t.ponto(x, y, cor)
        if k % 3 == 0:
            t.ponto(x, y - 1, luz) if False else None
    if farpas:
        for k in range(1, farpas + 1):
            s_ = k / (farpas + 1)
            x = x0 + (x1 - x0) * s_
            y = y0 + (y1 - y0) * s_ + flecha * 4 * s_ * (1 - s_)
            farpa(t, x, y)


# ------------------------------------------------------------------ peças

def vidro_liso(t, m, w, h, semente=0):
    """Vidro vulcânico (obsidiana verde): liso, escuro, clareando para cima à esquerda,
    com um reflexo do céu em faixa logo dentro da borda iluminada, fraturas em concha
    com aresta clara e pontinhos de brilho duro."""
    if not m.any():
        return
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    ny = (t.yy - y0) / max(1, y1 - y0)
    nx = (t.xx - x0) / max(1, x1 - x0)
    v = 0.62 - ny * 0.5 - nx * 0.18
    rng0 = np.random.default_rng(semente + 50)
    # Facetas: planos lascados um pouco mais claros ou escuros.
    for _ in range(max(2, (x1 - x0) // 10)):
        fx, fy = rng0.uniform(x0, x1), rng0.uniform(y0, y1)
        pts = [(fx + math.cos(a) * rng0.uniform(4, 10), fy + math.sin(a) * rng0.uniform(3, 8))
               for a in np.sort(rng0.uniform(0, 2 * math.pi, 5))]
        v = v + t.poligono(pts) * rng0.choice([-0.12, 0.14])
    # Reflexo largo em faixa diagonal, com um fio branco no meio.
    diag = nx * 0.8 + ny
    v = v + ((diag > 0.32) & (diag < 0.46)) * 0.22
    pintar_niveis(t, m, v, ["preto", "sombra", "alien_profundo", "alien_esc", "alien_medio"], dither=False)
    t.px[m & (np.abs(diag - 0.39) < 0.012 * 30 / max(10, y1 - y0)) & (ny < 0.7)] = IDX["ceu_claro"]
    # Reflexo do céu: faixa a 2 px da borda de cima/esquerda.
    dentro = ndimage.binary_erosion(m, iterations=2)
    fora1 = ndimage.binary_erosion(m, iterations=1)
    luz_borda = fora1 & ~dentro & (ny < 0.55) & (nx < 0.75)
    t.px[luz_borda] = IDX["ceu_medio"]
    t.px[m & ~fora1 & (ny < 0.5)] = IDX["alien_medio"]
    # Fraturas em concha: arcos finos com aresta clara.
    rng = np.random.default_rng(semente)
    for _ in range(max(2, (x1 - x0) // 12)):
        cx, cy = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.uniform(3, 7)
        a0 = rng.uniform(0, 6)
        for a in np.linspace(a0, a0 + 2.2, 12):
            x, y = cx + math.cos(a) * r, cy + math.sin(a) * r * 0.7
            if 0 <= int(y) < t.h and 0 <= int(x) < t.w and dentro[int(y), int(x)]:
                t.ponto(x, y, "preto")
                if int(y) > 0 and dentro[int(y) - 1, int(x)]:
                    t.ponto(x, y - 1, "alien_esc")
    for _ in range(max(2, (x1 - x0) // 14)):
        i = int(rng.integers(len(ys)))
        if ny[ys[i], xs[i]] < 0.6:
            t.ponto(xs[i], ys[i], "branco")


def pedra_vitrificada(w, h, semente=0, derrete=0.55):
    """Rochedo meio pedra meio vidro: do lado de longe da cratera (esquerda) é pedra com
    textura e líquen queimado; do lado da cratera derreteu, virou vidro verde-escuro
    brilhante com escorridos congelados descendo e pingos pendurados."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    # Silhueta: bloco irregular com topo arredondado.
    ang = np.arctan2(t.yy - h * 0.75, t.xx - w / 2)
    borda = 1 + 0.08 * np.sin(ang * 5 + rng.uniform(0, 6)) + 0.05 * np.sin(ang * 11)
    dx, dy = (t.xx - w / 2) / (w / 2), (t.yy - h * 0.78) / (h * 0.78)
    m = (dx ** 2 + np.minimum(dy, 0) ** 2 * 1.0 < borda ** 2) & (t.yy < h)
    m &= ~((dy > 0) & (np.abs(dx) > 0.98))
    H = ndimage.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
    H = np.minimum(H, min(w, h) * 0.35) + ruido(h, w, 1.2, semente) * 1.2
    # Pedra (lado esquerdo): rampa fria de pedra queimada.
    corte = w * (1 - derrete) + ruido(h, w, (3, 1), semente + 1) * 3 + (t.yy - h / 2) * 0.25
    pedra_m = m & (t.xx < corte)
    vidro_m = m & ~pedra_m
    relevo(t, pedra_m, H, ["sombra", "sombra_media", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza"],
           ambiente=0.05, contraste=1.1, brilho=0.3)
    # Rachaduras e líquen torrado na pedra.
    for _ in range(max(2, w // 14)):
        x, y = rng.uniform(2, w * 0.5), rng.uniform(h * 0.2, h * 0.8)
        for _k in range(int(rng.integers(3, 7))):
            X, Y = int(x), int(y)
            if pedra_m[Y, X]:
                t.px[Y, X] = IDX["sombra"]
                if Y > 0 and pedra_m[Y - 1, X]:
                    t.px[Y - 1, X] = IDX["cinza"]
            x += rng.uniform(-0.8, 1.2)
            y += rng.uniform(0.3, 1.1)
    liq = pedra_m & (ruido(h, w, 1.4, semente + 2) > 1.1)
    t.px[liq] = IDX["couro_profundo"]
    # Vidro: liso, com reflexo largo e faixas.
    vidro_liso(t, vidro_m, w, h, semente)
    # Reflexos do céu em faixas finas e inclinadas, e o brilho duro nas arestas de cima.

    # Junção pedra/vidro: pedra borbulhada (bolhas claras).
    junta = pedra_m & ndimage.binary_dilation(vidro_m, iterations=2)
    t.px[junta & (lim(h, w) < 0.3)] = IDX["alien_esc"]
    # Escorridos congelados descendo pela frente e pingos pendurados.
    base_v = np.where(vidro_m.any(0))[0]
    for i in range(max(2, w // 9)):
        if not len(base_v):
            break
        x = int(rng.choice(base_v))
        col = np.where(m[:, x])[0]
        y0 = int(col.max()) if len(col) else h - 1
        L_ = int(rng.integers(2, 6))
        for k in range(L_):
            y = min(h - 1, y0 - L_ + k + 2)
            t.px[y, x] = IDX["alien_esc"]
        t.px[min(h - 1, y0 + 1), x] = IDX["alien_luz"]
    t.contorno("sombra")
    return t


def entortar(t, forca, vento=-1):
    """Dobra a peça para o lado do vento, mais no alto (o pé fica no lugar)."""
    h, w = t.px.shape
    extra = int(abs(forca) * h) + 2
    o = Tela(w + extra, h)
    for y in range(h):
        d = forca * h * ((h - 1 - y) / h) ** 2
        for x in range(w):
            v = t.px[y, x]
            if v != VAZIO:
                nx = int(round(x + vento * d)) + (extra if vento < 0 else 0)
                if 0 <= nx < o.w:
                    o.px[y, nx] = v
    # Fecha buraquinhos da dobra.
    cheio = o.px != VAZIO
    buraco = ndimage.binary_closing(cheio, structure=np.ones((1, 2))) & ~cheio
    for y, x in zip(*np.where(buraco)):
        o.px[y, x] = o.px[y, x - 1] if x > 0 else o.px[y, x + 1]
    return f1.cortar(o)


def arvore_queimada(altura=80, semente=0, vento=-1, forca=0.25):
    """Árvore da caatinga torrada pela explosão: a mesma silhueta das árvores da fase 1,
    sem folha, dobrada para longe da cratera; casca virada carvão em escamas com aresta
    cinza, brasa viva nas fendas, pontas quebradas mostrando a madeira e fiapos de fumaça."""
    rng = np.random.default_rng(semente)
    t = f1.arvore(altura, semente=semente, folhas=False)
    m = t.px != VAZIO
    # Carvão: tons do galho seco trocados pelos do carvão.
    troca = {"sombra": "preto", "cinza_escuro": "marrom_noite", "cinza_medio": "couro_profundo",
             "cinza": "sombra_media", "cinza_luz": "cinza_escuro"}
    px = t.px.copy()
    for a_, b_ in troca.items():
        px[t.px == IDX[a_]] = IDX[b_]
    t.px = px
    # Escamas de carvão (casca rachada em quadradinhos) com aresta clara.
    gr = ((t.xx.astype(int) // 2 + (t.yy.astype(int) // 3) % 2) % 2 == 0) & ((t.yy.astype(int) % 3) == 0)
    interior = ndimage.binary_erosion(m, iterations=1)
    t.px[interior & gr] = IDX["cinza_medio"]
    # Brasas nas fendas do tronco, mais embaixo.
    tronco = interior & (t.yy > t.h * 0.45)
    ys, xs = np.where(tronco)
    for i in rng.choice(len(ys), size=min(len(ys), max(3, altura // 10)), replace=False) if len(ys) else []:
        t.px[ys[i], xs[i]] = IDX["laranja_fogo"]
        if ys[i] + 1 < t.h and tronco[ys[i] + 1, xs[i]]:
            t.px[ys[i] + 1, xs[i]] = IDX["vermelho_esc"]
    # Pontas quebradas: madeira clara à mostra.
    pontas = m & ~ndimage.binary_dilation(~m, iterations=1, structure=np.ones((3, 3)))
    topo = m & (t.yy < t.h * 0.5)
    viz = ndimage.convolve(m.astype(int), np.ones((3, 3)), mode="constant")
    ponta = topo & (viz <= 3)
    t.px[ponta & (rng.random(m.shape) < 0.5)] = IDX["couro_medio"]
    t = entortar(t, forca, vento)
    return t


def mandacaru_queimado(altura=48, semente=0):
    """Mandacaru cozido pelo calor: a coluna amoleceu e entortou para longe da cratera,
    um braço quebrou e pende de ponta-cabeça preso pela casca, os gomos murcharam
    (vão fundo preto, aresta marrom chamuscada), a casca rachou mostrando a polpa
    amarelada cozida, espinhos cinza e a ponta virou carvão com brasa."""
    W = 40
    t = Tela(W, altura)
    rng = np.random.default_rng(semente)
    cx = W / 2 + 4
    partes = []
    # Coluna mole: vários segmentos, cada um curvando mais para a esquerda.
    pts = [(cx, altura - 1)]
    for k in range(6):
        x, y = pts[-1]
        pts.append((x - k * 0.55, y - altura * 0.15))
    col = np.zeros((altura, W), bool)
    for (a_, b_) in zip(pts, pts[1:]):
        col |= t.capsula(a_[0], a_[1], b_[0], b_[1], 4.6, 4.2)
    partes.append((col, cx))
    # Braço inteiro de um lado e braço quebrado pendurado do outro.
    y0 = altura * 0.55
    bx = cx + 10
    braco = t.capsula(cx, y0, bx, y0 - 2, 3, 3) | t.capsula(bx, y0 - 2, bx - 1.5, y0 - altura * 0.33, 3.2, 2.8)
    partes.append((braco, bx))
    y1 = altura * 0.42
    qx = cx - 8
    quebrado = t.capsula(cx - 2, y1, qx, y1 + 1, 2.8, 2.8) | t.capsula(qx, y1 + 1, qx - 1, y1 + altura * 0.3, 3.0, 2.6)
    partes.append((quebrado, qx))
    xs = t.xx.astype(int)
    QUEIMADO = ["preto", "marrom_noite", "couro_profundo", "couro_escuro", "couro"]
    for m, px_ in partes:
        H = np.minimum(ndimage.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1], 3)
        relevo(t, m, H, QUEIMADO, ambiente=0.05, contraste=1.2, brilho=0.4)
        fase = int(px_) % 3
        t.px[m & ((xs - fase) % 3 == 0)] = IDX["preto"]
        aresta = m & ((xs - fase) % 3 == 2) & (t.xx < px_ + 1)
        t.px[aresta] = IDX["couro_medio"]
    tudo = np.zeros((altura, W), bool)
    for m, _ in partes:
        tudo |= m
    # Racha da casca mostrando a polpa cozida.
    for (x, y, L_) in ((cx - 1, altura * 0.7, 6), (bx, y0 - 8, 4)):
        for k in range(L_):
            yy = y + k
            if tudo[int(yy), int(x)]:
                t.ponto(x, yy, "areia_media" if k % 2 else "barro")
                t.ponto(x + 1, yy, "preto")
    # Fiapo de casca segurando o braço quebrado.
    t.linha(cx - 3, y1 - 1, qx + 2, y1 - 1, "couro_escuro")
    # Espinhos cinza nas arestas.
    esp = tudo & ((xs % 3) == 1) & (t.yy.astype(int) % 4 == 1)
    t.px[esp] = IDX["cinza_medio"]
    # Topo em carvão com brasa.
    topo = tudo & (t.yy < altura * 0.2)
    t.px[topo & (lim(altura, W) < 0.75)] = IDX["preto"]
    for _ in range(4):
        ys, xs_ = np.where(topo | (tudo & (t.yy > altura * 0.6)))
        if len(ys):
            i = int(rng.integers(len(ys)))
            t.ponto(xs_[i], ys[i], "laranja_escuro")
    t.contorno("preto")
    return f1.cortar(t)


class TelaDesloc(Tela):
    """Tela com a origem descida dy px (para desenhar com y negativo sem cortar)."""

    def __init__(self, w, h, dy):
        super().__init__(w, h)
        self.dy = dy
        self.yy = self.yy - dy

    def ponto(self, x, y, cor):
        super().ponto(x, y + self.dy, cor)


def boi_morto(semente=0):
    """Boi caído de lado e inchado, as quatro pernas duras esticadas para o lado, couro
    pintado chamuscado, rasgo na barriga mostrando as costelas e a gosma verde brilhando
    (contaminado), cabeça largada com chifre, olho revirado e língua de fora."""
    t = TelaDesloc(58, 34, 10)
    corpo = t.elipse(25, 14, 17, 8.5)
    anca = t.elipse(12, 14, 8, 8)
    cab = t.elipse(48, 18.5, 6.5, 4.2, ang=0.25)
    focinho = t.elipse(54, 20, 3, 2.6)
    pescoco = t.capsula(36, 15, 45, 18, 5.5, 4)
    pernas = np.zeros_like(corpo)
    patas = []
    # De barriga para cima, as quatro pernas duras esticadas para o alto (morte cômica).
    for (x0, x1, dx) in ((9, 8, -1), (15, 15, 0.5), (29, 30, -0.5), (35, 37, 1)):
        jy = -1.5
        pernas |= t.capsula(x0, 9, x1, jy + 4, 2.3, 1.7)
        pernas |= t.capsula(x1, jy + 4, x1 + dx, jy - 4, 1.6, 1.2)
        patas.append((x1 + dx, jy - 4.5))
    m = corpo | anca | cab | focinho | pescoco | pernas
    H = ndimage.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
    relevo(t, m, np.minimum(H, 6) + ruido(t.h, t.w, 1, semente) * 0.35, COURO_BOI, ambiente=0.0, contraste=1.15, brilho=0.5)
    # Junta da perna mais clara (joelho) e cascos pretos rachados.
    for (x, y) in patas:
        t.chapado(t.elipse(x, y, 1.7, 1.3), "preto")
        t.ponto(x - 0.5, y - 0.5, "cinza_escuro")
    # Couro pintado (manchas claras) e chamuscado em placas.
    for (x, y, r) in ((20, 11, 4), (31, 15, 3), (11, 16, 3)):
        t.chapado(t.elipse(x, y, r * 1.3, r) & (corpo | anca), "areia_media")
        t.chapado(t.elipse(x - 0.6, y - 0.6, r * 0.8, r * 0.55) & (corpo | anca), "areia")
    t.px[(corpo | anca) & (ruido(t.h, t.w, 1.1, semente + 3) > 1.15)] = IDX["marrom_noite"]
    # Rasgo na barriga: borda de couro virado, carne, costelas curvas e gosma acesa.
    # Barriga estufada para cima, brilhando de esticada.
    barriga = t.elipse(23, 9.5, 11, 3.5) & corpo
    t.px[barriga & (t.yy < 8.5) & (lim(t.h, t.w + 0) < 0.6)] = IDX["couro_claro"]
    t.px[barriga & t.elipse(19, 7.5, 4, 1)] = IDX["areia_media"]
    # Pelo riscado: tracinhos escuros curtos seguindo o corpo.
    rng = np.random.default_rng(semente)
    ys, xs = np.where(ndimage.binary_erosion(corpo | anca, iterations=2))
    for i in rng.choice(len(ys), size=min(len(ys), 40), replace=False):
        t.ponto(xs[i], ys[i] - 10, "couro_escuro")
        t.ponto(xs[i] + 1, ys[i] - 10, "couro_profundo")
    # Rabo caído em curva com o tufo.
    for k in range(8):
        t.ponto(7 - k * 0.6, 17 + k * 0.7 + math.sin(k * 0.7) * 0.6, "couro_escuro")
    t.chapado(t.elipse(2.5, 23, 1.6, 1.2), "marrom_noite")
    # Poça escura de sangue seco embaixo.
    poca = t.elipse(28, 23.5, 16, 1.3) & (t.px == VAZIO)
    t.px[poca] = IDX["vermelho_esc"]
    t.px[poca & (lim(t.h, t.w) < 0.4)] = IDX["marrom_noite"]
    rasgo = t.elipse(24, 11.5, 6.5, 2.8) & corpo
    t.chapado(rasgo, "vermelho_esc")
    t.chapado(rasgo & t.elipse(24, 12, 4.8, 1.8), "roxo_escuro")
    for x in (20, 23, 26, 29):
        for k in range(4):
            yy = 9.5 + k
            xx = x + math.sin(k * 0.8) * 0.8
            if rasgo[int(yy), int(xx)]:
                t.ponto(xx, yy, "cinza_claro" if k < 2 else "cinza_luz")
    borda = rasgo & ~ndimage.binary_erosion(rasgo)
    t.px[borda & (t.yy < 11.5)] = IDX["couro_claro"]
    for (x, y) in ((21, 12.5), (26, 12)):
        t.ponto(x, y, "alien_brilho")
    # Gosma verde transbordando do rasgo e escorrendo pelo lado.
    t.chapado(t.elipse(25, 13.6, 3.2, 0.8), "alien")
    t.ponto(24, 13.6, "alien_brilho")
    for k in range(5):
        t.ponto(30 + k * 0.3, 13 + k * 1.4, "alien_medio")
    t.ponto(31.5, 20, "alien_luz")
    # Cabeça: chifre curvo claro, orelha, olho revirado branco, ventas e língua.
    t.linha(47, 15, 49.5, 12, "cinza_claro")
    t.linha(49.5, 12, 49, 10, "cinza_luz")
    t.ponto(49, 9.5, "cinza")
    t.chapado(t.elipse(44, 15.5, 2, 1), "couro_escuro")
    t.chapado(t.elipse(48, 17.5, 1.3, 1.0), "branco")
    t.ponto(48.5, 18, "cinza")
    t.ponto(55, 19, "preto")
    t.linha(54, 22, 56, 23.4, "rosa_poeira")
    t.ponto(56, 23, "vermelho_medio")
    t.contorno("preto")
    return t


def cerca_volante(w=110, semente=0, queima=0.4):
    """Cerca da Volante: mourões tortos de pau com casca e topo lascado, três fios de
    arame farpado cedendo entre os mourões e enrolados em volta deles, um fio arrebentado
    pendurado, um trapo preso nas farpas e latas de alarme penduradas; o lado da cratera
    chamuscado."""
    t = Tela(w, 30)
    rng = np.random.default_rng(semente)
    base = 29
    xs = [3 + k * 22 + rng.uniform(-2, 2) for k in range(int((w - 6) / 22) + 1)]
    topos = []
    pau = Tela(w, 30)
    for k, x in enumerate(xs):
        alto = rng.uniform(22, 26)
        inc = rng.uniform(-1.5, 1.5)
        mourao(pau, x, base, alto, inc, semente=semente * 10 + k, queima=queima * (k / max(1, len(xs) - 1)))
        topos.append((x + inc * 0.5, base))
    pau.contorno("preto")
    t.colar(pau, 0, 0)
    for j, y0 in enumerate((8, 15, 22)):
        for k in range(len(xs) - 1):
            if j == 0 and k == len(xs) // 2:
                # Fio de cima arrebentado: as duas pontas pendem enroladas.
                xa, xb = xs[k], xs[k + 1]
                for s_ in range(9):
                    t.ponto(xa + s_ * 0.9, y0 + s_ * 0.8 + math.sin(s_) * 0.5, "cinza_escuro")
                    t.ponto(xb - s_ * 0.9, y0 + s_ * 1.1, "cinza_escuro")
                farpa(t, xa + 3, y0 + 3)
                continue
            fio(t, xs[k] + 1.5, y0, xs[k + 1] - 1.5, y0 + rng.uniform(-0.6, 0.6), flecha=1.6, farpas=4)
        for x in xs:
            # Arame enrolado no mourão.
            t.ponto(x - 1, y0, "cinza_luz")
            t.ponto(x + 1, y0 + 1, "cinza")
    # Trapo preso nas farpas e latas de alarme.
    xt = xs[1] + 9
    trapo = t.poligono([(xt, 14), (xt + 5, 15), (xt + 4, 20), (xt + 1, 22), (xt - 1, 18)])
    relevo(t, trapo, np.ones(trapo.shape), ["vermelho_esc", "vermelho_medio", "vermelho"], ambiente=0.2)
    t.px[trapo & (lim(30, w) < 0.3)] = IDX["vermelho_esc"]
    t.px[trapo & ~ndimage.binary_erosion(trapo)] = IDX["vermelho_esc"]
    for x in (xs[0] + 11, xs[-2] + 12):
        t.linha(x, 16, x, 19, "cinza_escuro")
        lata = t.retangulo(x - 1.5, 19, 3, 4)
        t.chapado(lata, "cinza_medio")
        t.ponto(x - 1, 19, "cinza_luz")
        t.ponto(x + 1, 22, "terra")
        t.px[(t.xx >= x - 2.5) & (t.xx < x + 2.5) & (t.yy >= 18) & (t.yy < 24) & (t.px == VAZIO)] = VAZIO
    return t


def boi_vidro(semente=0):
    """Boi virado estátua de vidro pelo clarão do disco, parado no meio do passo: corpo
    de vidro verde-escuro com reflexos do céu, chifres e rachaduras brancas, uma perna
    quebrada caída do lado e o chão fundido em volta da base."""
    t = Tela(52, 36)
    corpo = t.elipse(24, 15, 15, 7.5)
    cab = t.elipse(43, 11, 5.5, 4, ang=-0.3)
    pesc = t.capsula(34, 14, 41, 11, 5, 3.5)
    pernas = t.capsula(14, 19, 13, 33, 2, 1.6) | t.capsula(19, 19, 21, 33, 2, 1.6) | t.capsula(31, 19, 30, 33, 2, 1.6)
    rabo = t.capsula(9, 12, 6, 24, 0.8)
    m = corpo | cab | pesc | pernas | rabo
    vidro_liso(t, m, t.w, t.h, semente + 3)
    t.linha(44, 8, 47, 4, "alien_luz")
    t.linha(41, 8, 40, 4, "alien_luz")
    rng = np.random.default_rng(semente)
    # O esqueleto do boi aparece por dentro do vidro, como num raio X.
    osso_c = "alien_medio"
    t.linha(11, 12, 34, 12, osso_c)                      # espinha
    for x in range(12, 34, 4):
        t.ponto(x, 12, "alien_luz")
    for x in range(15, 31, 3):                           # costelas
        for k in range(4):
            t.ponto(x + k * 0.25, 13 + k, osso_c)
    t.linha(34, 12, 40, 10, osso_c)                       # pescoço
    t.chapado(t.elipse(43, 10.5, 2.5, 1.6), "alien_medio")  # crânio
    t.ponto(44, 10, "preto")
    for (x0, x1) in ((14, 13), (19, 21)):
        t.linha(x0, 18, x1, 30, osso_c)                   # ossos das pernas
    t.linha(31, 18, 30, 26, osso_c)
    # Bolhas presas no vidro.
    for (x, y) in ((17, 9), (27, 16), (36, 13), (22, 20)):
        t.ponto(x, y, "branco")
    # Olho de vidro leitoso.
    t.ponto(45, 9.5, "cinza_claro")
    # Perna quebrada caída e o toco.
    t.px[pernas & (t.xx > 28) & (t.yy > 26)] = VAZIO
    caida = t.capsula(34, 34, 42, 33, 1.8, 1.5)
    relevo(t, caida, np.minimum(ndimage.distance_transform_edt(np.pad(caida, 1))[1:-1, 1:-1], 2),
           ["sombra", "alien_profundo", "alien_esc", "alien_medio"], ambiente=0.0, brilho=1.5)
    t.contorno("preto")
    return t


def poste_telegrafo(altura=74, tomba=0.0, semente=0):
    """Poste de telégrafo de pau roliço com veios, nós e degraus de cravo, cinta de ferro,
    travessa com mão-francesa e quatro isoladores de vidro verde com brilho; tombado
    (tomba em rad, para a esquerda) pela explosão, chamuscado de baixo para cima, com o
    fio arrebentado pendurado em curva até o chão."""
    w = int(altura * (0.5 + abs(math.sin(tomba)) * 0.95)) + 12
    t = Tela(w, altura + 2)
    bx, by = (w - 8 if tomba > 0.05 else w / 2), altura
    c, s_ = math.cos(tomba), math.sin(tomba)
    tx, ty = bx - s_ * altura * 0.95, by - c * altura * 0.95
    pau = Tela(w, altura + 2)
    poste = pau.capsula(bx, by, tx, ty, 2.4, 1.8)
    madeira(pau, poste, True, semente, queima=0.15 + tomba * 0.3)
    # Cravos-degrau alternados e cinta de ferro perto do topo.
    for k in range(4, 12):
        f = k / 13
        x, y = bx + (tx - bx) * f, by + (ty - by) * f
        lado = 1 if k % 2 else -1
        pau.ponto(x + c * 3 * lado, y + s_ * 3 * lado, "cinza_medio")
    for f in (0.78, 0.8):
        x, y = bx + (tx - bx) * f, by + (ty - by) * f
        pau.ponto(x - c * 2, y - s_ * 2, "cinza_escuro")
        pau.ponto(x, y, "cinza")
        pau.ponto(x + c * 2, y + s_ * 2, "cinza_escuro")
    # Travessa com mão-francesa.
    px_, py_ = bx + (tx - bx) * 0.9, by + (ty - by) * 0.9
    trav = pau.capsula(px_ - c * 11, py_ + s_ * 11, px_ + c * 11, py_ - s_ * 11, 1.3)
    madeira(pau, trav, False, semente + 1)
    for d in (-6, 6):
        mx, my = px_ + c * d * 0.6 + s_ * 5, py_ - s_ * d * 0.6 + c * 5
        pau.linha(px_ + c * d - s_ * 0.5, py_ - s_ * d, mx, my, "cinza_escuro")
    pau.contorno("preto")
    t.colar(pau, 0, 0)
    # Isoladores de vidro (sino verde com brilho e pino de ferro).
    for d in (-9, -4, 4, 9):
        ix, iy = px_ + c * d - s_ * 2.5, py_ - s_ * d - c * 2.5
        t.ponto(ix, iy + 1.5, "cinza_escuro")
        iso = t.elipse(ix, iy, 1.4, 1.6)
        t.chapado(iso, "alien_esc")
        t.ponto(ix - 0.5, iy - 0.6, "alien_luz")
        t.ponto(ix + 0.6, iy + 0.6, "alien_profundo")
    # Fio arrebentado pendurado até perto do chão.
    x0, y0 = px_ + c * 9 - s_ * 2.5, py_ - s_ * 9 - c * 2.5
    for k in range(40):
        f = k / 39
        x = x0 + f * 10 + math.sin(f * 6) * 1.2
        y = y0 + f * (altura - y0 - 6) * 0.9
        if 0 <= y < t.h:
            t.ponto(x, y, "sombra")
    return t


def placa(texto="PERIGO", w=40, h=26, semente=0):
    """Placa da Volante: tábuas pregadas em estaca, letras vermelhas grossas pintadas à
    mão com sombra e tinta escorrendo, caveira com ossos cruzados, pregos enferrujados
    escorrendo ferrugem, buracos de bala com lasca clara e o canto queimado em brasa."""
    t = Tela(w, h + 14)
    tab = f1.tabuas(w, h, vertical=False, semente=semente)
    t.colar(tab, 0, 0)
    est = t.retangulo(w / 2 - 2.5, h - 1, 5, 15)
    madeira(t, est, True, semente + 3)
    # Letras com sombra escura e escorridos.
    x0 = int((w - len(texto) * 5 + 1) // 2)
    escrever(t, texto, x0, 3, "vermelho", grossa=True)
    rng = np.random.default_rng(semente)
    for k in range(len(texto)):
        if rng.random() < 0.35:
            xx = x0 + k * 5 + int(rng.integers(0, 3))
            L_ = int(rng.integers(1, 4))
            t.linha(xx, 8, xx, 8 + L_, "vermelho_medio")
            t.ponto(xx, 9 + L_, "vermelho")
    # Caveira com ossos cruzados.
    cx, cy = w / 2, h * 0.68
    for d in (-1, 1):
        t.linha(cx - 5, cy + 4 * d * -1 + 1, cx + 5, cy - 4 * d * -1 + 1, "cinza_claro")
        t.ponto(cx - 5.5, cy + 4 * d * -1 + 1, "branco")
        t.ponto(cx + 5.5, cy - 4 * d * -1 + 1, "branco")
    t.chapado(t.elipse(cx, cy - 0.5, 3.4, 3.0), "branco")
    t.chapado(t.retangulo(cx - 2, cy + 1.5, 4, 2.4), "cinza_claro")
    t.chapado(t.elipse(cx - 1.3, cy - 0.5, 0.9, 1.0), "preto")
    t.chapado(t.elipse(cx + 1.3, cy - 0.5, 0.9, 1.0), "preto")
    t.ponto(cx, cy + 1.2, "preto")
    for x in (cx - 1, cx + 0.5):
        t.ponto(x, cy + 3, "sombra")
    # Pregos enferrujados com escorrido.
    for (x, y) in ((2, 1), (w - 3, 1), (2, h - 4), (w - 3, h - 4)):
        t.ponto(x, y, "cinza_claro")
        t.ponto(x, y + 1, "laranja_escuro")
        t.ponto(x, y + 2, "couro")
    # Buracos de bala com lasca clara em volta.
    for (x, y) in ((w * 0.8, h * 0.4), (w * 0.17, h * 0.62), (w * 0.62, h * 0.85)):
        t.chapado(t.elipse(x, y, 1.0, 1.0), "preto")
        t.ponto(x + 1.2, y - 1, "couro_claro")
        t.ponto(x - 1.2, y + 1, "couro_claro")
        t.ponto(x + 1.4, y + 0.8, "couro_luz")
    # Canto queimado com brasa na borda.
    canto = t.elipse(w + 1, -1, 8, 7) & (t.px != VAZIO)
    t.px[canto] = IDX["preto"]
    borda = canto & ~ndimage.binary_erosion(canto)
    t.px[borda & (lim(t.h, t.w) < 0.5)] = IDX["laranja_escuro"]
    t.px[borda & (lim(t.h, t.w) >= 0.5)] = IDX["vermelho_esc"]
    t.contorno("preto")
    return t


FONTE = {  # 3x5
    "P": ["111", "101", "111", "100", "100"], "E": ["111", "100", "110", "100", "111"],
    "R": ["110", "101", "110", "101", "101"], "I": ["111", "010", "010", "010", "111"],
    "G": ["111", "100", "101", "101", "111"], "O": ["111", "101", "101", "101", "111"],
    "A": ["010", "101", "111", "101", "101"], "S": ["111", "100", "111", "001", "111"],
    "T": ["111", "010", "010", "010", "010"], "N": ["101", "111", "111", "101", "101"],
    "V": ["101", "101", "101", "101", "010"], "L": ["100", "100", "100", "100", "111"],
    "D": ["110", "101", "101", "101", "110"], "B": ["110", "101", "110", "101", "110"],
    "!": ["010", "010", "010", "000", "010"], " ": ["000"] * 5, "C": ["111", "100", "100", "100", "111"],
}


def escrever(t, texto, x, y, cor, grossa=False):
    """Letras 3x5 (grossa: cada coluna dobrada, 4x5 com espaço de 5)."""
    for ch in texto:
        g = FONTE.get(ch, FONTE[" "])
        for j, l in enumerate(g):
            for i, b in enumerate(l):
                if b == "1":
                    t.ponto(x + i, y + j, cor)
                    if grossa:
                        t.ponto(x + i + 1, y + j, cor)
        x += 5 if grossa else 4


def cancela(w=70):
    """Cancela da Volante: mourões grossos de pau com capa, barra roliça listrada de
    vermelho e branco com brilho e a tinta lascada, contrapeso de pedras amarrado,
    placa ALTO pendurada, lampião de lata com vidro aceso, sacos de areia empilhados e
    um rolo de arame farpado por cima."""
    t = Tela(w + 10, 48)
    pau = Tela(w + 10, 48)
    for x in (5, w):
        mo = pau.retangulo(x - 2.5, 7, 6, 41)
        madeira(pau, mo, True, x)
        pau.chapado(pau.retangulo(x - 3, 6, 7, 2), "couro_escuro")
        pau.ponto(x - 2, 6, "couro_claro")
    pau.contorno("preto")
    t.colar(pau, 0, 0)
    # Barra listrada roliça.
    barra = t.capsula(5, 12, w, 13.5, 1.8)
    listra = ((t.xx + t.yy * 0.2) // 6) % 2 == 0
    yb = 12 + (t.xx - 5) / (w - 5) * 1.5
    tom = np.clip(1 - np.abs(t.yy - yb + 0.6) / 2.2, 0, 1)
    pintar_niveis(t, barra & listra, 0.2 + tom * 0.75, ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_escuro"], dither=False)
    pintar_niveis(t, barra & ~listra, 0.2 + tom * 0.75, ["cinza_medio", "cinza_luz", "cinza_claro", "branco"], dither=False)
    lasca = barra & (ruido(48, w + 10, 0.7, 3) > 1.3)
    t.px[lasca] = IDX["couro_escuro"]
    t.px[barra & ~ndimage.binary_erosion(barra)] = IDX["preto"]
    # Contrapeso: pedras amarradas na ponta de trás.
    for (x, y, r) in ((1.5, 12, 2.2), (3, 9.5, 1.8), (0.5, 15, 1.6)):
        pm = t.elipse(x, y, r, r * 0.85)
        relevo(t, pm, domo(t, x, y, r, r * 0.85) * 2, FERRO, ambiente=0.1, linha=False)
    t.linha(0, 11, 4, 11, "terra")
    # Placa ALTO pendurada na barra.
    px0 = w * 0.32
    t.linha(px0 + 1, 14, px0 + 1, 16, "sombra")
    t.linha(px0 + 9, 14, px0 + 9, 16, "sombra")
    pl = t.retangulo(px0 - 1, 16, 19, 7)
    t.chapado(pl, "areia_luz")
    t.px[pl & ~ndimage.binary_erosion(pl)] = IDX["preto"]
    escrever(t, "ALTO", px0 + 1, 17, "vermelho")
    # Lampião de lata com vidro aceso.
    lx_ = w * 0.62
    t.linha(lx_, 14, lx_, 17, "sombra")
    t.chapado(t.retangulo(lx_ - 2, 17, 5, 1), "cinza_escuro")
    t.chapado(t.retangulo(lx_ - 1.5, 18, 4, 4), "amarelo_fogo")
    t.ponto(lx_ - 1, 19, "amarelo_claro")
    t.ponto(lx_ + 1.5, 20, "ouro_escuro")
    t.chapado(t.retangulo(lx_ - 2, 22, 5, 1), "cinza_escuro")
    # Sacos de areia e rolo de arame farpado por cima.
    sa = f1.sacos_detalhados(3, 2, 7)
    t.colar(sa, 9, 48 - sa.h)
    yr = 48 - sa.h + int(np.where((sa.px != VAZIO).any(1))[0].min()) + 1
    for k in range(int(sa.w / 3.2)):
        xc = 10 + k * 3.2
        anel = t.elipse(xc, yr, 2.6, 2.4) & ~t.elipse(xc, yr, 1.7, 1.5)
        t.px[anel & (t.px == VAZIO)] = IDX["cinza_escuro"]
        t.ponto(xc - 1, yr - 2, "cinza_luz")
        farpa(t, xc + 1.5, yr + 1.5)
    return t


def destroco_disco(semente=0, w=40, h=34):
    """Pedaço do casco do disco cravado de lado no chão: chapa curva prateada em faixas
    concêntricas, borda de cima redonda e a de baixo rasgada em dentes, rebites roxos,
    uma escotilha com luz verde ainda acesa, fios arrebentados soltando faísca e terra
    amontoada na base."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    cx, cy = w * 0.2, h * 1.35
    R1, R2 = h * 1.25, h * 0.55
    d = np.hypot(t.xx - cx, t.yy - cy)
    ang = np.arctan2(t.yy - cy, t.xx - cx)
    m = (d < R1) & (d > R2) & (ang > -1.75) & (ang < -0.55)
    # Ponta da direita rasgada em dentes.
    dentes = ang > -0.75 + 0.06 * np.sin(d * 1.3)
    m &= ~dentes
    H = (R1 - d) / (R1 - R2)
    v = 0.3 + 0.5 * np.sin(np.clip(H, 0, 1) * math.pi) + (ang + 1.75) * 0.12
    pintar_niveis(t, m, v * 0.85, ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "aco_brilho"])
    # Fuligem e queimado espalhados na chapa.
    fuli = m & (ruido(h, w, 1.5, semente + 4) > 0.9)
    t.px[fuli & (lim(h, w) < 0.6)] = IDX["sombra_media"]
    # Faixas concêntricas (emendas das chapas) e reflexo forte.
    for rr in (R2 + (R1 - R2) * 0.33, R2 + (R1 - R2) * 0.66):
        t.px[m & (np.abs(d - rr) < 0.55)] = IDX["sombra_media"]
        t.px[m & (np.abs(d - rr - 1) < 0.5)] = IDX["cinza_luz"]
    t.px[m & (np.abs(d - (R1 - 2)) < 0.5)] = IDX["branco"]
    # Rebites roxos ao longo das emendas.
    for a_ in np.linspace(-1.65, -0.85, 6):
        for rr in (R2 + (R1 - R2) * 0.33, R2 + (R1 - R2) * 0.66):
            x, y = cx + math.cos(a_) * (rr + 1.5), cy + math.sin(a_) * (rr + 1.5)
            if 0 <= int(y) < h and 0 <= int(x) < w and m[int(y), int(x)]:
                t.ponto(x, y, "lilas")
                t.ponto(x + 0.6, y + 0.6, "roxo_escuro")
    # Runas estranhas gravadas na faixa do meio (marcas que ninguém sabe ler).
    rr = R2 + (R1 - R2) * 0.5
    for k, a_ in enumerate(np.linspace(-1.6, -0.95, 7)):
        x, y = cx + math.cos(a_) * rr, cy + math.sin(a_) * rr
        if 0 <= int(y) < h and 0 <= int(x) < w and m[int(y), int(x)]:
            forma = k % 3
            if forma == 0:
                t.ponto(x, y, "roxo"); t.ponto(x + 1, y + 1, "roxo"); t.ponto(x - 1, y + 1, "roxo")
            elif forma == 1:
                t.ponto(x, y - 1, "roxo"); t.ponto(x, y, "roxo"); t.ponto(x + 1, y, "roxo")
            else:
                t.ponto(x - 1, y, "roxo"); t.ponto(x + 1, y, "roxo"); t.ponto(x, y + 1, "roxo")
    # Rasgo da ponta: espessura da chapa à mostra em favo escuro, com a borda ainda quente.
    rasgo_b = m & ndimage.binary_dilation(dentes & ~m, iterations=2)
    t.px[rasgo_b] = IDX["sombra"]
    favo = rasgo_b & (((t.xx.astype(int) + t.yy.astype(int)) % 3) == 0)
    t.px[favo] = IDX["cinza_escuro"]
    quente = m & ndimage.binary_dilation(dentes & ~m, iterations=1)
    t.px[quente] = IDX["laranja_escuro"]
    t.px[quente & (lim(h, w) < 0.4)] = IDX["amarelo_fogo"]
    # Escotilha com luz verde.
    a_ = -1.2
    ex, ey = cx + math.cos(a_) * (R2 + (R1 - R2) * 0.5), cy + math.sin(a_) * (R2 + (R1 - R2) * 0.5)
    t.chapado(t.elipse(ex, ey, 3.2, 3.0), "sombra")
    t.chapado(t.elipse(ex, ey, 2.3, 2.1), "alien_esc")
    t.chapado(t.elipse(ex - 0.3, ey - 0.3, 1.4, 1.2), "alien_brilho")
    t.ponto(ex - 1, ey - 1, "branco")
    # Fios arrebentados saindo do rasgo, com faísca na ponta.
    borda_r = m & ndimage.binary_dilation(dentes & ~m, iterations=1)
    ys, xs = np.where(borda_r)
    for k in range(3):
        if not len(ys):
            break
        i = int(rng.integers(len(ys)))
        x, y = float(xs[i]), float(ys[i])
        cor = ("vermelho", "amarelo_fogo", "alien")[k]
        for j in range(6):
            x += 0.8
            y += math.sin(j * 0.9 + k) * 0.9 + 0.2
            t.ponto(x, y, cor)
        t.ponto(x + 1, y - 1, "amarelo_claro")
    # Terra amontoada na base.
    monte = t.elipse(w * 0.45, h + 1, w * 0.45, 4)
    relevo(t, monte, domo(t, w * 0.45, h + 1, w * 0.45, 4) * 3, TERRA_Q, ambiente=0.1)
    t.contorno("preto")
    return t


def casa_ardendo(w=70, h=48, semente=0):
    """Casa de taipa ao fundo pegando fogo: telhado desabado, paredes enegrecidas e
    labaredas saindo da janela e do buraco do telhado."""
    c = f1.casa_taipa(w, h, semente=semente, quebrada=True)
    m = c.px != VAZIO
    fuligem = m & (ruido(c.h, c.w, (2, 3), semente) + (1 - c.yy / c.h) * 1.4 > 1.0)
    c.px[fuligem & (lim(c.h, c.w) < 0.7)] = IDX["sombra"]
    t = Tela(w, h + 20)
    t.colar(c, 0, 20)
    for (x, y, r) in ((w * 0.35, 22, 6), (w * 0.7, 26, 4.5), (w * 0.5, 34, 3)):
        for k in range(4):
            yy = y - k * r * 0.5
            fl = t.elipse(x + math.sin(k * 2.3) * 1.5, yy, r * (1 - k * 0.22), r * 0.9 * (1 - k * 0.18))
            t.chapado(fl, BRASA[min(3, k)])
    t.contorno("preto")
    return t


# ------------------------------------------------------------------ camadas

def camada_jogo():
    alt = 120
    topo = 216 - alt
    t = Tela(LARGURA, alt)
    y = lambda wy: wy - topo  # noqa: E731
    yc = y(CHAO) - 1
    rng = np.random.default_rng(21)
    # Capim: verde e seco no começo, torrado no meio, nada no vidro.
    for x in range(0, 1150, 7):
        if rng.random() < (0.6 if x < 550 else 0.3):
            c = f1.capim(semente=x, seco=x > 300)
            if x > 550:
                c.px[c.px != VAZIO] = IDX["preto"] if rng.random() < 0.5 else IDX["marrom_noite"]
            f1.colar(t, c, x + rng.integers(-3, 3), y(CHAO) - c.h + 1)
    # Chão: terra -> queimado -> vidro, misturando sem corte reto.
    t.colar(chao_base(LARGURA, 26, semente=11), 0, y(CHAO) - 2)
    colar_organico(t, chao_chamuscado(1150 - 300, 26, semente=15), 300, y(CHAO) - 2, borda=110, semente=15)
    colar_organico(t, chao_queimado(1150 - 440, 26, semente=12), 440, y(CHAO) - 2, borda=130, semente=12)
    colar_organico(t, chao_queimado(LARGURA - 1050, 26, semente=13), 1050, y(CHAO) - 2, borda=40, semente=13)
    colar_organico(t, chao_vidro(LARGURA - 1120, 26, semente=14), 1120, y(CHAO) - 2, borda=80, semente=14)
    # A) Beira da caatinga: xique-xique, pedras, cerca velha, mandacaru ainda verde.
    for x in (60, 240, 420):
        f1.assentar(t, f1.xiquexique(semente=x), x, yc)
    for k, x in enumerate((130, 330, 500)):
        f1.assentar(t, f1.pedra(int(rng.integers(14, 24)), int(rng.integers(8, 13)), semente=k + 5), x, yc, afundar=2)
    f1.assentar(t, f1.pote_barro(3), 280, yc)
    # B) Terra arrasada: boi morto, ossada, cerca farpada da Volante, placa, toco fumegando.
    f1.assentar(t, boi_morto(1), 640, yc + 2)
    f1.assentar(t, f1.cranio_boi(), 905, yc)
    f1.assentar(t, cerca_volante(110, 4), 760, yc)
    f1.assentar(t, placa("PERIGO", semente=2), 985, yc)
    f1.assentar(t, boi_morto(2), 1060, yc + 2)
    # C) Vidro: rochedos derretidos (sólidos), destroço do disco cravado, cancela no fim.
    for (x, w_, h_, sem) in ROCHEDOS:
        pv = pedra_vitrificada(w_, h_, semente=sem)
        f1.sombra_contato(t, x + w_ / 2, yc + 1, w_ * 1.1, 3)
        f1.colar(t, pv, x, yc - pv.h + 3)
    f1.assentar(t, destroco_disco(1), 1215, yc + 3)
    f1.assentar(t, destroco_disco(2, 30, 26), 1450, yc + 3)
    f1.assentar(t, boi_vidro(1), 1270, yc + 1)
    f1.assentar(t, cancela(70), 1600, yc + 1)
    return t, topo


# x, largura, altura dos rochedos vitrificados (o topo é plataforma sólida no jogo).
ROCHEDOS = [(1170, 46, 30, 3), (1330, 62, 44, 4), (1510, 40, 24, 5)]


def camada_perto():
    fator = 0.75
    W = int(LARGURA * fator + 548)
    alt = 116
    base = alt - 2
    t = Tela(W, alt)
    rng = np.random.default_rng(31)
    lx = lambda wx: int(wx * fator)  # noqa: E731
    pecas = []
    # A) árvores ainda com folha, mandacarus verdes, uma árvore pegando fogo.
    for k, wx in enumerate((10, 300, 470)):
        pecas.append((lx(wx), f1.arvore(int(rng.integers(68, 84)), semente=k + 400)))
    for k, wx in enumerate((150, 380)):
        pecas.append((lx(wx), f1.mandacaru(int(rng.integers(40, 54)), semente=k + 410, bracos=2)))
    # B) tudo torrado e dobrado para longe da cratera, postes tombando cada vez mais.
    for k, wx in enumerate((560, 700, 880, 1010, 1120)):
        pecas.append((lx(wx), arvore_queimada(int(rng.integers(66, 90)), semente=k + 420)))
    for k, wx in enumerate((620, 940)):
        pecas.append((lx(wx), mandacaru_queimado(int(rng.integers(40, 52)), semente=k + 430)))
    for k, (wx, ang) in enumerate(((520, 0.0), (760, 0.25), (1000, 0.6), (1220, 1.1))):
        pecas.append((lx(wx), poste_telegrafo(76, ang, semente=k)))
    # C) rochedos vitrificados grandes e pedaços do disco.
    for k, (wx, w_, h_) in enumerate(((1180, 70, 50), (1400, 90, 62), (1600, 60, 40))):
        pecas.append((lx(wx), pedra_vitrificada(w_, h_, semente=440 + k, derrete=0.65)))
    pecas.append((lx(1300), destroco_disco(7, 52, 44)))
    for x, p in sorted(pecas, key=lambda e: -e[1].h):
        f1.colar(t, p, x, base - p.h + 2)
    # Escurece um pouco (perspectiva: fica atrás do plano do jogo).
    return t, fator


# ------------------------------------------------------------------ fundo (muda ao longo do trecho)

FUMACA_CINZA = ["azul_sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]
FUMACA_ESCURA_C = ["sombra", "sombra_media", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza"]
FUMACA_ESCURA = ["preto", "sombra", "sombra_media", "azul_sombra", "cinza_escuro"]


def bolas(t, lista, rampa, luz=(-0.45, -0.5), borda=None):
    """Pinta bolas (x, y, r) com luz própria em faixas, das de trás para as da frente."""
    for (x, y, r) in lista:
        m = t.elipse(x, y, r, r * 0.9)
        if not m.any():
            continue
        hx, hy = x + luz[0] * r, y + luz[1] * r
        d = np.hypot((t.xx - hx) / r, (t.yy - hy) / (r * 0.9))
        v = np.clip(1.05 - d / 1.5, 0, 0.999)
        pintar_niveis(t, m, v, rampa)
        if borda:
            aro = m & ~t.elipse(x, y, r - 1, r * 0.9 - 1) & (t.yy > y)
            t.px[aro] = IDX[borda]


def coluna_fumaca(t, x, base, altura, larg, rampa, semente=0, vento=-0.35, brilho_base=None, abre=1.0, fino=3.0, denso=1.0,
                  fase=0.0, luz_verde=False):
    """Coluna de fumaça saindo de um fogo: começa fina na boca do fogo e vai engrossando
    em rolos, deitando com o vento. Cada rolo tem luz em cima à esquerda e sombra
    embaixo, com vinco escuro entre os rolos; a borda de fora é escura e no alto ela se
    desfaz em fiapos. fase (0-1): os rolos sobem pela coluna; em fase=1 cada rolo chegou
    onde o seguinte começou, então a animação emenda sem pulo."""
    rng = np.random.default_rng(semente)
    n = int(altura / 3.2 * denso)
    vagas = [(i / n, rng.uniform(-0.7, 0.7), rng.uniform(-0.3, 0.3), rng.uniform(0.42, 0.8)) for i in range(n)]
    rolos = []
    for (s0, ox, oy, rf) in vagas:
        s_ = (s0 + fase) % 1.0
        y = base - altura * s_ ** 1.1
        cx = x + vento * altura * s_ ** 1.6 + math.sin(s_ * 7 + semente) * larg * 0.1
        r = fino + (larg * abre - fino) * s_ ** 0.75
        # No alto o rolo murcha e se desfaz; embaixo nasce pequeno.
        rr = r * rf * (1 - max(0, s_ - 0.85) * 3.5)
        if rr < 1:
            continue
        rolos.append((cx + ox * r, y + oy * r, rr, s_))
    # Do alto para baixo: os rolos de baixo (mais novos) ficam por cima.
    rolos.sort(key=lambda b: b[1])
    uniao = np.zeros((t.h, t.w), bool)
    nivel = np.full((t.h, t.w), -1, int)
    k_ = len(rampa)
    for (rx, ry, rr, s_) in rolos:
        m = t.elipse(rx, ry, rr, rr * 0.85)
        if not m.any():
            continue
        hx, hy = rx - rr * 0.38, ry - rr * 0.42
        d = np.hypot((t.xx - hx) / rr, (t.yy - hy) / (rr * 0.85))
        v = np.clip(1.02 - d / 1.55 + s_ * 0.12, 0, 0.999)
        nv = (v * k_).astype(int)
        borda = m & ~t.elipse(rx, ry, rr - 1, rr * 0.85 - 1) & uniao & ((t.xx - rx) * 0.6 + (t.yy - ry) > -rr * 0.2)
        nv[borda] = np.maximum(nv[borda] - 2, 0)
        nivel[m] = nv[m]
        uniao |= m
    cores = np.array([IDX[c] for c in rampa])
    t.px[uniao] = cores[np.clip(nivel[uniao], 0, k_ - 1)]
    fora = uniao & ~ndimage.binary_erosion(uniao)
    t.px[fora & (t.xx > x + vento * (base - t.yy) * 0.5)] = IDX[rampa[0]]
    alto = uniao & (t.yy < base - altura * 0.8)
    furo = alto & (ruido(t.h, t.w, 1.2, semente + 9) > 1.25 - (base - altura * 0.8 - t.yy) / (altura * 0.2) * 0.6)
    t.px[furo] = VAZIO
    if luz_verde:
        # Barriga iluminada de verde pelo disco: borda de baixo dos rolos perto da base.
        perto = np.clip(1 - (base - t.yy) / (altura * 0.45), 0, 1)
        baixo = uniao & ~np.roll(uniao, -2, 0)
        t.px[baixo & (perto > lim(t.h, t.w) * 0.9) & (t.px != VAZIO)] = IDX["alien_esc"]
        miolo = uniao & t.elipse(x - 4, base - 12, larg * 0.6, 22) & (t.px != IDX["preto"]) & (t.px != VAZIO)
        t.px[miolo & (lim(t.h, t.w) < 0.45)] = IDX["alien_profundo"]
    if brilho_base:
        for (bx, by, br, s_) in rolos[-10:]:
            m = t.elipse(bx, by + br * 0.35, br * 0.9, br * 0.45) & uniao
            t.px[m & (lim(t.h, t.w) < 0.6)] = IDX[brilho_base]


FUMACAS = []  # colunas animadas registradas pelas camadas (exportadas como sprites à parte)


def registrar_fumaca(camada, x, base, altura, larg, rampa, **kw):
    """Guarda uma coluna de fumaça para virar sprite animado (em vez de pintada parada)."""
    FUMACAS.append(dict(camada=camada, x=x, base=base, altura=altura, larg=larg, rampa=rampa, kw=kw))


def quadros_fumaca(f, n=16):
    """Quadros de uma coluna registrada, recortados num retângulo próprio.
    Devolve (quadros, x0, y0) com o canto do recorte nas coordenadas da camada."""
    vento = f["kw"].get("vento", -0.35)
    abre = f["kw"].get("abre", 1.0)
    largura = int(f["larg"] * abre * 2.2 + abs(vento) * f["altura"] + 16)
    alt = int(f["altura"] + f["larg"] * abre + 10)
    x0 = int(f["x"] + min(0, vento) * f["altura"] - f["larg"] * abre * 1.1 - 6)
    y0 = int(f["base"] - alt + 8)
    qs = []
    for k in range(n):
        t = Tela(largura, alt)
        coluna_fumaca(t, f["x"] - x0, f["base"] - y0, f["altura"], f["larg"], f["rampa"], fase=k / n, **f["kw"])
        qs.append(t)
    return qs, x0, y0


def folha_grade(quadros, caminho, maxw=2048):
    """Folha em grade (várias linhas) para não passar do limite de textura do iPhone."""
    from PIL import Image
    w, h = quadros[0].w, quadros[0].h
    cols = max(1, min(len(quadros), maxw // w))
    linhas = (len(quadros) + cols - 1) // cols
    img = Image.new("RGBA", (w * cols, h * linhas))
    for k, q in enumerate(quadros):
        img.paste(q.imagem(), ((k % cols) * w, (k // cols) * h))
    img.save(caminho, optimize=True)
    return w, h


def ceu_fumaca(h=308, w=548):
    """Céu tomado pela fumaça perto da cratera: azul pesado em cima, lilás doente no meio
    e horizonte amarelado, como sol filtrado por fumaça."""
    import cenario as cn
    t = Tela(w, h)
    faixas = [(0, "azul_medio"), (90, "ceu_medio"), (170, "lilas_claro"), (232, "areia_luz")]
    for k, (y, cor) in enumerate(faixas):
        fim = faixas[k + 1][0] if k + 1 < len(faixas) else h
        t.px[y:fim] = IDX[cor]
        if k + 1 < len(faixas):
            cn.degrade(t, fim - 12, fim + 8, cor, faixas[k + 1][1])
    return t


def camada_longe():
    """Bem longe (0,25): serras azuladas que somem atrás da fumaça; plumas cinza dos
    incêndios; no fim, a borda da cratera subindo e a coluna de fumaça verde do disco."""
    fator = 0.25
    W = int(LARGURA * fator + 548)
    alt = 280
    t = Tela(W, alt)
    x = np.arange(W)
    # Serras em duas fileiras (sem repetir: perfil próprio do trecho).
    for base, amp, sem, rampa in ((alt - 92, 14, 3, ["ceu_medio", "ceu_claro", "ceu_claro", "ceu_luz"]),
                                  (alt - 66, 10, 8, ["ceu", "ceu_medio", "ceu_claro", "ceu_luz"])):
        perfil = base + amp * np.sin(x / 90 + sem) + amp * 0.5 * np.sin(x / 31 + 2 * sem) + 3 * ruido(1, W, 9, sem)[0]
        m = t.yy >= perfil[None, :]
        sub = Tela(W, alt)
        sub.volume(m, rampa, luz=(-0.8, -0.5), achatado=14, suave=4, ambiente=0.3, linha=False)
        t.px[m] = sub.px[m]
    # Névoa baixa.
    t.px[(t.px != VAZIO) & (t.yy > alt - 40)] = IDX["ceu_luz"]
    # Coluna de fumaça do disco, enorme, subindo de trás da borda e saindo pelo alto da
    # tela: preta e grossa, deitando para a esquerda, com a barriga iluminada de verde.
    cx = 1560 * fator + 300
    registrar_fumaca("longe", cx + 10, alt - 62, alt - 40, 58, FUMACA_ESCURA, semente=7, vento=-0.4, abre=1.25, fino=14,
                     denso=2.2, luz_verde=True)
    # A borda da cratera vai numa imagem à parte, na frente da fumaça (a base da coluna fica atrás dela).
    fundo_px = t.px.copy()
    # Borda da cratera (C): encosta de terra arrancada com blocos de pedra, a parte de
    # cima queimada preta pelo calor, veios de vidro escorrendo da crista, lajes
    # levantadas tortas na crista e o contorno verde do brilho que vem de dentro.
    n = ruido(1, W, 7, 9)[0] * 5 + ruido(1, W, 2, 10)[0] * 1.2
    crista = alt - 74 + ((x - cx) / 150) ** 2 * 46 + n
    borda = (t.yy > crista[None, :]) & (np.abs(x[None, :] - cx) < 250)
    prof = t.yy - crista[None, :]
    v = 0.55 - np.clip(prof, 0, 60) / 60 * 0.1 + ruido(alt, W, (2, 7), 11) * 0.06 - (x[None, :] - cx) / 900
    pintar_niveis(t, borda, v, ["sombra", "marrom_noite", "couro_profundo", "terra_escura", "terra", "terra_media"])
    # Estratos deitados acompanhando a crista.
    camada_ = ((prof + ruido(alt, W, (1, 10), 13) * 1.6) % 8) < 1
    t.px[borda & camada_ & (prof > 4)] = IDX["marrom_noite"]
    # Parte de cima torrada preta.
    torra = borda & (prof < 6 + ruido(alt, W, (1, 4), 15) * 2)
    t.px[torra] = IDX["sombra"]
    t.px[torra & (lim(alt, W) < 0.3)] = IDX["preto"]
    rng = np.random.default_rng(12)
    # Blocos de pedra encravados na encosta, com volume e contorno.
    for k in range(16):
        bx_ = cx + rng.uniform(-210, 210)
        by_ = crista[int(np.clip(bx_, 0, W - 1))] + rng.uniform(8, 50)
        rw, rh = rng.uniform(4, 9), rng.uniform(3, 6)
        pm = t.elipse(bx_, by_, rw, rh) & borda
        if pm.any():
            relevo(t, pm, domo(t, bx_, by_, rw, rh) * 3, ["preto", "sombra", "azul_sombra", "cinza_escuro", "cinza_medio"],
                   ambiente=0.05, linha=False)
            t.px[pm & ~ndimage.binary_erosion(pm)] = IDX["preto"]
    # Veios de vidro derretido escorrendo da crista para baixo.
    for k in range(12):
        vx = cx + rng.uniform(-200, 200)
        y = crista[int(np.clip(vx, 0, W - 1))] + 1
        for j in range(int(rng.integers(8, 26))):
            vx += rng.uniform(-0.6, 0.6)
            y += 1
            if 0 <= int(y) < alt and 0 <= int(vx) < W - 1 and borda[int(y), int(vx)]:
                t.ponto(vx, y, "alien_profundo")
                t.ponto(vx + 1, y, "alien_esc" if j % 3 else "alien_medio")
        t.ponto(vx, y + 1, "alien_luz")
    # Foguinhos pela encosta.
    for k in range(6):
        fx = cx + rng.uniform(-180, 180)
        fy = crista[int(np.clip(fx, 0, W - 1))] + rng.uniform(10, 40)
        for j in range(3):
            t.chapado(t.elipse(fx + j * 0.5, fy - j * 1.3, 1.6 - j * 0.4, 1.1), BRASA[j + 1])
    # Lajes de pedra levantadas pela queda, tortas, de tamanhos diferentes.
    for k, (off, hh, ww, inc) in enumerate(((-170, 14, 12, -0.5), (-95, 22, 16, -0.25), (-40, 10, 9, 0.1),
                                            (30, 26, 18, 0.3), (120, 16, 13, 0.6), (185, 9, 8, 0.9))):
        lx_ = cx + off + rng.uniform(-6, 6)
        ly_ = crista[int(np.clip(lx_, 0, W - 1))] + 5
        pts = [(lx_ - ww / 2, ly_ + 4), (lx_ - ww * 0.35 + inc * hh, ly_ - hh), (lx_ + ww * 0.1 + inc * hh, ly_ - hh * 1.08),
               (lx_ + ww * 0.4 + inc * hh * 0.8, ly_ - hh * 0.7), (lx_ + ww / 2, ly_ + 4)]
        laje = t.poligono(pts)
        lado = t.xx < (lx_ + inc * (ly_ - t.yy))
        t.px[laje & lado] = IDX["cinza_escuro"]
        t.px[laje & ~lado] = IDX["sombra"]
        # Estrias da pedra e a ponta quebrada clara.
        t.px[laje & lado & (((t.yy + t.xx * 0.3) % 4) < 0.8)] = IDX["azul_sombra"]
        t.px[laje & ~ndimage.binary_erosion(laje)] = IDX["preto"]
        topo_l = laje & ~np.roll(laje, 1, 0)
        t.px[topo_l] = IDX["alien_esc"]
        borda |= laje
    topo_b = borda & ~np.roll(borda, 1, 0)
    t.px[topo_b] = IDX["alien_medio"]
    t.px[ndimage.binary_dilation(topo_b) & ~borda & (t.px != VAZIO) & (lim(alt, W) < 0.5)] = IDX["alien_esc"]
    frente = Tela(W, alt)
    frente.px = np.where(t.px != fundo_px, t.px, VAZIO).astype(t.px.dtype)
    fundo = Tela(W, alt)
    fundo.px = fundo_px
    return fundo, frente, fator


def chama(t, x, y, tam=6, semente=0):
    """Labareda em línguas: três a cinco pontas tremidas, amarelo no miolo, laranja e
    vermelho por fora, brasa no pé e o chão em volta clareado pelo fogo."""
    rng = np.random.default_rng(semente)
    for k in range(int(rng.integers(3, 6))):
        dx = rng.uniform(-tam * 0.6, tam * 0.6)
        h = tam * rng.uniform(1.0, 1.9) * (1 - abs(dx) / (tam * 1.4))
        w_ = tam * rng.uniform(0.35, 0.55)
        for camada, cor in enumerate(("vermelho_esc", "laranja_escuro", "laranja_fogo", "amarelo_fogo")):
            f = 1 - camada * 0.22
            pts = [(x + dx - w_ * f, y), (x + dx - w_ * f * 0.4, y - h * f * 0.55), (x + dx + rng.uniform(-1, 1), y - h * f),
                   (x + dx + w_ * f * 0.45, y - h * f * 0.5), (x + dx + w_ * f, y)]
            t.chapado(t.poligono(pts), cor)
    t.chapado(t.elipse(x, y, tam * 1.1, 1.2), "vermelho_esc")
    t.ponto(x, y - 1, "amarelo_claro")


def camada_meio():
    """Longe (0,45): morros. A) caatinga ainda verde e a casa ardendo assentada no morro,
    com a fumaça saindo do telhado; B) morros chamuscados e depois torrados (a queimada
    avança em manchas, sem pontilhado), árvores mortas, focos de fogo com a fumaça subindo
    de cada um; C) encosta da cratera com veios de vidro e as barracas da base no alto."""
    fator = 0.45
    W = int(LARGURA * fator + 548)
    alt = 240
    t = Tela(W, alt)
    rng = np.random.default_rng(5)
    xs = np.arange(W)
    n = ruido(1, W, 30, 6)[0]
    alto = (alt - 28 + n * 6 - np.clip((xs - 1150 * fator) / 300, 0, 1) * 10).astype(int)
    morro = t.yy >= alto[None, :]
    zona = xs / fator
    # Queimada em três estágios (normal, chamuscado, torrado) avançando em manchas.
    q = np.clip((zona[None, :] - 380) / 520, 0, 1) + ruido(alt, W, (4, 12), 31) * 0.22
    prof = (t.yy - alto[None, :]).astype(float)
    v = 0.78 - np.clip(prof, 0, 30) / 30 * 0.45 + ruido(alt, W, (1.5, 5), 32) * 0.08
    NORMAL = ["azul_sombra", "terra", "terra_media", "barro", "areia_media", "areia"]
    CHAMUSCADO = ["sombra", "couro_profundo", "terra_escura", "terra", "terra_media", "barro"]
    TORRADO = ["preto", "sombra", "marrom_noite", "couro_profundo", "cinza_escuro", "cinza_medio"]
    for rampa, sel in ((NORMAL, q < 0.35), (CHAMUSCADO, (q >= 0.35) & (q < 0.68)), (TORRADO, q >= 0.68)):
        pintar_niveis(t, morro & sel, v, rampa)
    # Textura: capim riscado no normal, cinza clara e brasas no torrado, pedrinhas.
    for _ in range(W // 2):
        x = int(rng.integers(0, W))
        y = int(rng.integers(alto[x] + 2, alt - 1))
        qq = q[y, x]
        if qq < 0.35:
            t.px[y, x] = IDX["areia_luz"]
            t.px[y + 1, x] = IDX["terra"]
        elif qq < 0.68:
            t.px[y, x] = IDX["couro_profundo"]
        else:
            t.px[y, x] = IDX["cinza_luz" if rng.random() < 0.6 else "laranja_escuro"]
    for _ in range(W // 12):
        x = int(rng.integers(1, W - 3))
        y = int(rng.integers(alto[x] + 3, alt - 2))
        t.px[y, x:x + 2] = IDX["cinza_luz"]
        t.px[y + 1, x:x + 2] = IDX["sombra"]
    # Crista do morro com aresta clara (luz do céu).
    for x in range(W):
        t.px[alto[x], x] = IDX["areia" if q[alto[x], x] < 0.35 else "terra_media" if q[alto[x], x] < 0.68 else "cinza_medio"]
    def assentar_morro(p, x):
        x = int(x)
        fim = min(W - 1, x + p.w)
        y = int(max(alto[x:fim + 1])) if fim > x else alto[x]
        f1.colar(t, p, x, y - p.h + 4)
        return y
    # Vegetação: viva no A, árvores mortas no B, nada no C.
    x = 0
    while x < W:
        wx = x / fator
        qq = q[alto[min(W - 1, x)], min(W - 1, x)]
        if wx < 1120:
            if qq < 0.35:
                a = f1.arvore(int(rng.integers(12, 24)), semente=int(x), folhas=rng.random() > 0.25)
                assentar_morro(a, x)
                x += int(rng.integers(8, 22))
            else:
                a = arvore_queimada(int(rng.integers(16, 28)), semente=int(x), forca=0.12 + (wx - 450) / 1500)
                assentar_morro(a, x)
                x += int(rng.integers(18, 40))
        else:
            x += 20
    # Casa ardendo assentada no morro (A), com a fumaça saindo do buraco do telhado.
    ca = casa_ardendo(46, 30, semente=12)
    cx_ = int(330 * fator)
    yb = assentar_morro(ca, cx_)
    # Focos de fogo (B): a labareda no chão do morro e a fumaça subindo de cada um.
    fogos = [(int(wx * fator), sem) for wx, sem in ((640, 1), (790, 2), (960, 3), (1060, 4))]
    for k, (fx, sem) in enumerate(fogos):
        fy = alto[fx] + 2
        registrar_fumaca("meio", fx, fy - 4, (150, 110, 175, 95)[k], (24, 16, 28, 14)[k], FUMACA_ESCURA_C,
                         semente=sem, vento=(-0.45, -0.3, -0.55, -0.35)[k], fino=2.5, denso=1.4)
    registrar_fumaca("meio", cx_ + 18, yb - ca.h + 14, 170, 24, FUMACA_ESCURA_C, semente=9, vento=-0.4, fino=3.0)
    for (fx, sem) in fogos:
        brilho = t.elipse(fx, alto[fx] + 3, 9, 3) & morro
        t.px[brilho & (lim(alt, W) < 0.5)] = IDX["laranja_escuro"]
        chama(t, fx, alto[fx] + 3, tam=6, semente=sem)
    # Refaz a casa por cima da fumaça (a fumaça sai de trás do telhado).
    assentar_morro(ca, cx_)
    # Veios de vidro na encosta da cratera (C).
    for k in range(50):
        xx = int(rng.integers(int(1150 * fator), W - 2))
        yy = int(rng.integers(alto[xx] + 2, alt - 2))
        if morro[yy, xx]:
            t.px[yy, xx] = IDX["alien_esc"]
            t.px[yy, xx + 1] = IDX["alien_medio"]
    # Barracas da base ao longe (o próximo trecho), pequenas no alto da encosta.
    import fase1_extra as ext
    for k, wx in enumerate((1500, 1580, 1660)):
        b = ext.barraca(26, 14, semente=k + 20)
        assentar_morro(b, int(wx * fator))
    return t, fator


def camada_frente():
    """Na frente do Lampião (1,1): tocos queimados, capim torrado e cacos de vidro
    escuros, poucos e espalhados."""
    fator = 1.1
    W = int(LARGURA * fator + 548)
    alt = 24
    t = Tela(W, alt)
    rng = np.random.default_rng(41)
    x = 160
    while x < W - 40:
        wx = x / fator
        if wx < 1150 and rng.random() < 0.5:
            c = f1.capim(22, semente=int(x))
            c.px[c.px != VAZIO] = IDX["preto"]
            f1.colar(t, c, x, alt - c.h)
        elif wx < 1150:
            toco = Tela(10, 18)
            m = toco.capsula(5, 17, 5.5, 4, 2.6, 2.0)
            toco.chapado(m, "preto")
            toco.ponto(5, 4, "vermelho_esc")
            toco.ponto(6, 9, "laranja_escuro")
            f1.colar(t, toco, x, alt - 18)
        else:
            caco = Tela(16, 10)
            m = caco.poligono([(1, 9), (5, 2), (9, 4), (14, 9)])
            caco.chapado(m, "sombra")
            caco.chapado(m & (caco.xx < 6), "alien_profundo")
            caco.ponto(5, 3, "alien_esc")
            f1.colar(t, caco, x, alt - 10)
        x += int(rng.integers(220, 460))
    return t, fator


def dados_fase():
    """Dados do trecho 1 (assets/fases/fase2.json), lidos por src/scenes/Fase2Scene.js."""
    solidos = [[0, CHAO, LARGURA, 200]]
    for (x, w_, h_, _s) in ROCHEDOS:
        solidos.append([x + 5, CHAO - h_ + 5, w_ - 10, h_ - 5])
    return {
        "largura": LARGURA,
        "inicio": [40, CHAO - 20],
        "solidos": solidos,
        "caixotes": [[220, CHAO - 18], [244, CHAO - 18], [232, CHAO - 36], [930, CHAO - 24, "barril"],
                     [948, CHAO - 24, "barril"], [1480, CHAO - 18]],
        "refens": [[470, CHAO], [1365, CHAO - 44 + 5]],
        "itens": [],
        "bodes": [[160, CHAO]],
        "discos": [],
        # Guardas de máscara já no posto (cerca, placa, rochedo e cancela).
        "inimigos": [
            [820, CHAO, "mascarado"], [1000, CHAO, "mascarado", {"distraido": True}],
            [1360, CHAO - 44 + 5, "mascarado"], [1640, CHAO, "mascarado", {"escudo": True}],
        ],
        # Ondas: contaminados pulam de trás dos bois mortos; os mascarados vêm da cancela.
        "ondas": [
            {"gatilho": 420, "trava": [260, 808], "inimigos": [["contaminado", "salta:662", 0], ["contaminado", "dir", 900],
                                                               ["contaminado", "salta:662", 1900], ["mascarado", "dir", 2600]]},
            {"gatilho": 960, "trava": [820, 1368], "inimigos": [["contaminado", "salta:1082", 0], ["mascarado", "dir", 700],
                                                                ["contaminado", "esq", 1500], ["mascarado", "dir", 2200, {"refem": True}],
                                                                ["contaminado", "salta:1082", 3000]]},
            {"gatilho": 1440, "trava": [1152, 1700], "inimigos": [["mascarado", "dir", 0], ["mascarado", "salta:1620", 600],
                                                                  ["contaminado", "esq", 1400], ["mascarado", "dir", 2200],
                                                                  ["contaminado", "dir", 3000]]},
        ],
        "fogueiras": [], "forquilhas": [], "buracos": [], "fim": 1660,
        "casas": [], "varais": [], "jumentos": [], "urubus": [[650, CHAO], [1060, CHAO]], "galinhas": [],
        "biplanos": [], "segredos": [],
    }


def exportar(saida, raiz):
    """Grava as camadas do trecho em assets/sprites (f2_*.png) e assets/fases/fase2.json."""
    import json
    FUMACAS.clear()
    jogo, topo = camada_jogo()
    perto, fp = camada_perto()
    meio, fm = camada_meio()
    longe, borda_l, fl = camada_longe()
    frente, ff = camada_frente()
    for nome, c in (("f2_jogo", jogo), ("f2_perto", perto), ("f2_meio", meio), ("f2_longe", longe),
                    ("f2_borda", borda_l), ("f2_frente", frente)):
        c.imagem().save(saida / f"{nome}.png", optimize=True)
    # Colunas de fumaça animadas: cada uma vira uma folha de quadros em grade.
    fumacas = []
    for k, f in enumerate(FUMACAS):
        qs, x0, y0 = quadros_fumaca(f)
        w_, h_ = folha_grade(qs, saida / f"f2_fumaca_{k}.png")
        fumacas.append({"chave": f"f2_fumaca_{k}", "camada": f["camada"], "x": x0, "y": y0, "w": w_, "h": h_, "n": len(qs)})
    ceu_fumaca().imagem().save(saida / "ceu_fumaca.png", optimize=True)
    d = dados_fase()
    d["fumacas"] = fumacas
    d["camadas"] = {"jogo": {"y": topo, "fator": 1}, "perto": {"base": 194, "fator": fp}, "meio": {"base": 192, "fator": fm},
                    "longe": {"base": 160, "fator": fl}, "borda": {"base": 160, "fator": fl}, "frente": {"base": 216, "fator": ff},
                    "fumaca": {"de": 300, "ate": 1100}}
    pasta = raiz / "assets/fases"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "fase2.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")))


def previa(saida, cams=(0, 560, 1150)):
    """Monta telas do trecho em várias posições da câmera para mostrar a mudança do fundo."""
    from PIL import Image
    import cenario as cn
    FUMACAS.clear()
    jogo, topo = camada_jogo()
    perto, fp = camada_perto()
    meio, fm = camada_meio()
    longe, borda_l, fl = camada_longe()
    fumacas = [(f, *quadros_fumaca(f, n=1)) for f in FUMACAS]
    ceu1, ceu2 = cn.ceu().imagem(), ceu_fumaca().imagem()
    ims = []
    for cam in cams:
        o = Image.new("RGBA", (548, 308))
        mistura = min(1, max(0, (cam - 300) / 800))
        o.alpha_composite(Image.blend(ceu1, ceu2, mistura), (0, 0))
        camadas = {"longe": (longe, 160, fl), "meio": (meio, 192, fm)}
        def fum(nome):
            c, base, fat = camadas[nome]
            for f, qs, x0, y0 in fumacas:
                if f["camada"] == nome:
                    o.alpha_composite(qs[0].imagem(), (x0 - int(cam * fat), base + DY - c.h + y0))
        for im, base, fat, antes in ((longe.imagem(), 160, fl, None), (None, 160, fl, "longe"), (borda_l.imagem(), 160, fl, None),
                                     (None, 192, fm, "meio"), (meio.imagem(), 192, fm, None), (perto.imagem(), 194, fp, None)):
            if antes:
                fum(antes)
                continue
            o.alpha_composite(im, (-int(cam * fat), base + DY - im.height))
        o.alpha_composite(jogo.imagem(), (-cam, topo + DY))
        ims.append(o)
    folha = Image.new("RGBA", (548, 308 * len(ims) + 6 * (len(ims) - 1)), (0, 0, 0, 255))
    for k, i in enumerate(ims):
        folha.alpha_composite(i, (0, k * 314))
    folha.save(saida)
    return saida


if __name__ == "__main__":
    print(previa(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "tools/arte/pixel/fase2_previa.png"))
