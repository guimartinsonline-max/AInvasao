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


def lim(h, w):
    return np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]


def pintar_niveis(t, m, v, rampa, dither=True):
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

def chao_queimado(w, h=26, semente=0):
    """Chão em corte queimado: crosta de cinza clara fofa com calombos e montinhos, logo
    abaixo uma faixa de carvão preta com brasas nas rachaduras, depois a terra torrada
    em estratos (mais escura e fria que a terra normal) com pedras escurecidas e raízes
    viradas carvão; o fundo volta aos poucos para a cor da terra."""
    t = f1.chao(w, h, semente=semente)
    rng = np.random.default_rng(semente)
    L = lim(h, w)
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
    """Mandacaru cozido pelo calor: gomos murchos de carvão com a aresta de cada gomo
    ainda marrom, espinhos cinza, topo preto torrado, brasas e o corpo amolecido
    tombando para longe da cratera."""
    t = f1.mandacaru(altura, semente=semente, bracos=2)
    troca = {"mandacaru_luz": "couro_escuro", "mandacaru": "couro_profundo", "caatinga": "marrom_noite",
             "caatinga_media": "marrom_noite", "caatinga_esc": "preto", "areia_luz": "cinza_escuro",
             "areia_clara": "cinza_medio", "sombra": "preto"}
    px = t.px.copy()
    for a_, b_ in troca.items():
        px[t.px == IDX[a_]] = IDX[b_]
    t.px = px
    m = t.px != VAZIO
    topo = m & (t.yy < altura * 0.22)
    t.px[topo & (lim(t.h, t.w) < 0.7)] = IDX["preto"]
    rng = np.random.default_rng(semente)
    ys, xs = np.where(m & (t.yy > altura * 0.3))
    for i in rng.choice(len(ys), size=min(len(ys), 4), replace=False):
        t.px[ys[i], xs[i]] = IDX["laranja_escuro"]
    return entortar(t, 0.1, -1)


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
    rasgo = t.elipse(25, 18.5, 7.5, 3.2) & corpo
    t.chapado(rasgo, "vermelho_esc")
    t.chapado(rasgo & t.elipse(25, 19, 5.5, 2.0), "roxo_escuro")
    for x in (20, 23, 26, 29):
        for k in range(4):
            yy = 16.5 + k
            xx = x + math.sin(k * 0.8) * 0.8
            if rasgo[int(yy), int(xx)]:
                t.ponto(xx, yy, "cinza_claro" if k < 2 else "cinza_luz")
    borda = rasgo & ~ndimage.binary_erosion(rasgo)
    t.px[borda & (t.yy < 18.5)] = IDX["couro_claro"]
    for (x, y) in ((22, 20), (27, 19.5)):
        t.ponto(x, y, "alien_brilho")
    t.chapado(t.elipse(26, 21.6, 3.5, 0.7), "alien")
    t.ponto(25, 21.6, "alien_brilho")
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
    # Olho de vidro leitoso.
    t.ponto(44, 10, "cinza_claro")
    # Perna quebrada caída e o toco.
    t.px[pernas & (t.xx > 28) & (t.yy > 26)] = VAZIO
    caida = t.capsula(34, 34, 42, 33, 1.8, 1.5)
    relevo(t, caida, np.minimum(ndimage.distance_transform_edt(np.pad(caida, 1))[1:-1, 1:-1], 2),
           ["sombra", "alien_profundo", "alien_esc", "alien_medio"], ambiente=0.0, brilho=1.5)
    t.contorno("preto")
    return t


def poste_telegrafo(altura=74, tomba=0.0, semente=0):
    """Poste de telégrafo de madeira com travessa e isoladores de vidro; tomba: ângulo
    (rad) para a esquerda, empurrado pela explosão, com o fio arrebentado pendurado."""
    w = int(altura * (0.6 + abs(math.sin(tomba)) * 0.9))
    t = Tela(w, altura + 2)
    bx, by = w - 6 if tomba > 0 else w / 2, altura
    tx, ty = bx - math.sin(tomba) * altura * 0.95, by - math.cos(tomba) * altura * 0.95
    poste = t.capsula(bx, by, tx, ty, 2.2, 1.7)
    H = ndimage.distance_transform_edt(np.pad(poste, 1))[1:-1, 1:-1]
    relevo(t, poste, np.minimum(H, 3), CARVAO[1:] if tomba > 0.3 else f1.MADEIRA, ambiente=0.1, brilho=0.5)
    # Travessa e isoladores.
    px_, py_ = bx + (tx - bx) * 0.9, by + (ty - by) * 0.9
    c, s = math.cos(tomba), math.sin(tomba)
    trav = t.capsula(px_ - c * 9, py_ + s * 9, px_ + c * 9, py_ - s * 9, 1.2)
    relevo(t, trav, np.minimum(ndimage.distance_transform_edt(np.pad(trav, 1))[1:-1, 1:-1], 2), f1.MADEIRA, ambiente=0.1)
    for d in (-7, 7):
        ix, iy = px_ + c * d - s * 2, py_ - s * d - c * 2
        t.chapado(t.elipse(ix, iy, 1.2, 1.4), "alien_esc")
        t.ponto(ix - 0.4, iy - 0.6, "alien_luz")
    # Fio arrebentado pendurado em curva.
    for k in range(14):
        x = px_ + c * 7 + k * 0.6
        y = py_ - s * 7 + k * 1.1 + math.sin(k * 0.5) * 0.6
        t.ponto(x, y, "sombra")
    t.contorno("preto")
    return t


def placa(texto="PERIGO", w=38, h=26, semente=0):
    """Placa de madeira da Volante pregada em estaca: tábuas, pregos, letras pintadas de
    vermelho escorrendo, caveira desenhada, buracos de bala e canto queimado."""
    t = Tela(w, h + 14)
    tab = f1.tabuas(w, h, vertical=False, semente=semente)
    t.colar(tab, 0, 0)
    est = t.retangulo(w / 2 - 2, h - 1, 4, 15)
    relevo(t, est, np.minimum(ndimage.distance_transform_edt(np.pad(est, 1))[1:-1, 1:-1], 2), f1.MADEIRA, ambiente=0.1)
    escrever(t, texto, 3, 3, "vermelho")
    # Caveira simples pintada.
    cx, cy = w / 2, h * 0.68
    t.chapado(t.elipse(cx, cy, 3.2, 2.8), "branco")
    t.chapado(t.retangulo(cx - 2, cy + 2, 4, 2), "branco")
    t.ponto(cx - 1.2, cy - 0.2, "preto")
    t.ponto(cx + 1.2, cy - 0.2, "preto")
    t.ponto(cx, cy + 2.6, "preto")
    for (x, y) in ((2, 1), (w - 3, 1), (2, h - 3), (w - 3, h - 3)):
        t.ponto(x, y, "cinza_claro")
    for (x, y) in ((w * 0.75, h * 0.35), (w * 0.2, h * 0.6)):
        t.chapado(t.elipse(x, y, 0.9, 0.9), "preto")
        t.ponto(x + 1, y + 1, "couro_medio")
    canto = t.elipse(w, 0, 7, 6) & (t.px != VAZIO)
    t.px[canto] = IDX["preto"]
    t.px[canto & ~ndimage.binary_erosion(canto) & (lim(t.h, t.w) < 0.5)] = IDX["laranja_escuro"]
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


def escrever(t, texto, x, y, cor):
    for ch in texto:
        g = FONTE.get(ch, FONTE[" "])
        for j, l in enumerate(g):
            for i, b in enumerate(l):
                if b == "1":
                    t.ponto(x + i, y + j, cor)
                    if j == 4 and (x + i) % 3 == 0:
                        t.ponto(x + i, y + j + 1, "vermelho_esc")
        x += 4


def cancela(w=70):
    """Cancela da Volante: dois mourões listrados, barra listrada vermelha e branca
    abaixada, lampião pendurado, placa ÁREA DO GOVERNO e sacos de areia na base."""
    t = Tela(w + 10, 46)
    for x in (4, w):
        mo = t.retangulo(x - 2, 14, 5, 32)
        relevo(t, mo, np.minimum(ndimage.distance_transform_edt(np.pad(mo, 1))[1:-1, 1:-1], 2), f1.MADEIRA, ambiente=0.1)
    barra = t.capsula(4, 18, w, 19.5, 1.6)
    listra = ((t.xx // 6) % 2 == 0)
    relevo(t, barra & listra, np.ones(barra.shape) * 0, ["vermelho_esc", "vermelho", "vermelho"], ambiente=0.4)
    relevo(t, barra & ~listra, np.ones(barra.shape) * 0, ["cinza_luz", "cinza_claro", "branco"], ambiente=0.4)
    t.px[barra & (t.yy > 20)] = IDX["sombra"]
    # Contrapeso e lampião pendurado.
    t.chapado(t.retangulo(0, 15, 4, 6), "cinza_escuro")
    t.linha(w * 0.55, 20, w * 0.55, 24, "sombra")
    t.chapado(t.retangulo(w * 0.55 - 1.5, 24, 3, 4), "ouro_escuro")
    t.ponto(w * 0.55, 25, "amarelo_claro")
    sa = f1.sacos_detalhados(3, 2, 7)
    t.colar(sa, 0, 46 - sa.h)
    t.contorno("preto")
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
    t.colar(f1.chao(LARGURA, 26, semente=11), 0, y(CHAO) - 2)
    f1.colar_suave(t, chao_queimado(1150 - 380, 26, semente=12), 380, y(CHAO) - 2, borda=90, semente=12)
    f1.colar_suave(t, chao_queimado(LARGURA - 1050, 26, semente=13), 1050, y(CHAO) - 2, borda=40, semente=13)
    f1.colar_suave(t, chao_vidro(LARGURA - 1120, 26, semente=14), 1120, y(CHAO) - 2, borda=80, semente=14)
    # A) Beira da caatinga: xique-xique, pedras, cerca velha, mandacaru ainda verde.
    for x in (60, 240, 420):
        f1.assentar(t, f1.xiquexique(semente=x), x, yc)
    for k, x in enumerate((130, 330, 500)):
        f1.assentar(t, f1.pedra(int(rng.integers(14, 24)), int(rng.integers(8, 13)), semente=k + 5), x, yc, afundar=2)
    f1.assentar(t, f1.pote_barro(3), 280, yc)
    # B) Terra arrasada: boi morto, ossada, cerca farpada da Volante, placa, toco fumegando.
    f1.assentar(t, boi_morto(1), 640, yc + 2)
    f1.assentar(t, f1.cranio_boi(), 905, yc)
    f1.assentar(t, f1.cerca_farpada(110, 4), 760, yc)
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


def coluna_fumaca(t, x, base, altura, larg, rampa, semente=0, vento=-0.35, brilho_base=None, abre=1.0):
    """Coluna de fumaça como no Metal Slug: rolos grandes e sobrepostos com sombra em
    faixas (cel), cada rolo com a luz em cima à esquerda e a borda de baixo escura,
    subindo, engrossando e deitando com o vento; no alto abre num chapéu largo."""
    rng = np.random.default_rng(semente)
    rolos = []
    n = int(altura / 4)
    for i in range(n):
        s_ = i / max(1, n - 1)
        y = base - s_ * altura
        cx = x + vento * altura * s_ ** 1.5
        r = larg * (0.32 + s_ ** 0.8 * 0.68 * abre)
        espalha = r * (0.5 + s_ * 0.6)
        for _ in range(2 + int(s_ * 3)):
            rolos.append((cx + rng.uniform(-espalha, espalha), y + rng.uniform(-4, 4), r * rng.uniform(0.45, 0.7)))
    # De cima para baixo: os rolos de baixo ficam na frente (a coluna sobe "de dentro").
    rolos.sort(key=lambda b: b[1])
    for (rx, ry, rr) in rolos:
        m = t.elipse(rx, ry, rr, rr * 0.82)
        t.cel(m, rampa, sombra=min(4, max(2, int(rr * 0.3))), luz=min(3, max(1, int(rr * 0.15))), linha=False, rebaixo=True)
    if brilho_base:
        for (bx, by, br) in rolos[-8:]:
            m = t.elipse(bx, by + br * 0.35, br * 0.9, br * 0.45) & (t.px != VAZIO)
            t.px[m & (lim(t.h, t.w) < 0.6)] = IDX[brilho_base]


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
    # Plumas dos incêndios (A e B).
    for wx, h_, l_, sem in ((300, 90, 16, 1), (720, 110, 20, 2), (980, 80, 14, 3)):
        coluna_fumaca(t, wx * fator + 120, alt - 50, h_, l_ * 1.6, FUMACA_CINZA, semente=sem, vento=-0.5)
    # Coluna de fumaça do disco, enorme, subindo de trás da borda e saindo pelo alto da
    # tela: preta e grossa, deitando para a esquerda, com a barriga iluminada de verde.
    cx = 1560 * fator + 140
    coluna_fumaca(t, cx + 10, alt - 62, alt - 40, 58, FUMACA_ESCURA, semente=7, vento=-0.4, abre=1.25)
    fum = t.px != VAZIO
    # Luz verde vinda de baixo: borda de baixo de cada rolo e o miolo perto da base.
    perto_base = np.clip(1 - (alt - 62 - t.yy) / 120, 0, 1)
    baixo = fum & ~np.roll(fum, -2, 0) & (t.px != IDX["ceu_luz"])
    t.px[baixo & (perto_base > lim(alt, W) * 0.9)] = IDX["alien_esc"]
    miolo = fum & t.elipse(cx + 6, alt - 74, 34, 22) & (t.px != IDX["preto"])
    t.px[miolo & (lim(alt, W) < 0.45)] = IDX["alien_profundo"]
    # Borda da cratera (C): crista de terra arrancada e pedra, recortada e escura,
    # contornada de verde pelo brilho que vem de dentro.
    n = ruido(1, W, 7, 9)[0] * 5 + ruido(1, W, 2, 10)[0] * 1.5
    crista = alt - 74 + ((x - cx) / 150) ** 2 * 46 + n
    borda = (t.yy > crista[None, :]) & (np.abs(x[None, :] - cx) < 250)
    H = np.minimum(ndimage.distance_transform_edt(np.pad(borda, 1))[1:-1, 1:-1], 8) * 0.6 + ruido(alt, W, (3, 9), 11) * 0.6
    relevo(t, borda, H, ["sombra", "azul_sombra", "marrom_noite", "couro_profundo", "terra_escura", "terra"],
           ambiente=-0.15, contraste=1.0, brilho=0.1, linha=False)
    # Lajes de pedra arrancadas e levantadas pela queda, espetadas na crista.
    rng_l = np.random.default_rng(14)
    for k in range(9):
        lx_ = cx + (k - 4) * 44 + rng_l.uniform(-10, 10)
        ly_ = crista[int(np.clip(lx_, 0, W - 1))] + 6
        inc = (lx_ - cx) / 260
        hh, ww = rng_l.uniform(12, 24), rng_l.uniform(10, 18)
        pts = [(lx_ - ww / 2, ly_ + 4), (lx_ - ww * 0.3 + inc * hh, ly_ - hh), (lx_ + ww * 0.3 + inc * hh, ly_ - hh * 0.8),
               (lx_ + ww / 2, ly_ + 4)]
        laje = t.poligono(pts)
        lado = t.xx < (lx_ + inc * (ly_ - t.yy))
        t.px[laje & lado] = IDX["cinza_escuro"]
        t.px[laje & ~lado] = IDX["sombra"]
        t.px[laje & ~ndimage.binary_erosion(laje)] = IDX["preto"]
        topo_l = laje & ~np.roll(laje, 1, 0)
        t.px[topo_l] = IDX["alien_esc"]
        borda |= laje
    # Estratos de rocha arrancada: faixas escuras deitadas acompanhando a crista.
    camada_ = ((t.yy - crista[None, :] + ruido(alt, W, (1, 8), 13) * 1.5) % 7) < 1
    t.px[borda & camada_ & (t.yy > crista[None, :] + 3)] = IDX["sombra"]
    topo_b = borda & ~np.roll(borda, 1, 0)
    t.px[topo_b] = IDX["alien_medio"]
    t.px[ndimage.binary_dilation(topo_b) & ~borda & (t.px != VAZIO) & (lim(alt, W) < 0.5)] = IDX["alien_esc"]
    # Pedras soltas na encosta e vidro brilhando.
    rng = np.random.default_rng(12)
    for k in range(30):
        xx = cx + rng.uniform(-220, 220)
        yy = crista[int(np.clip(xx, 0, W - 1))] + rng.uniform(4, 30)
        if 0 <= int(xx) < W - 2 and int(yy) < alt and borda[int(yy), int(xx)]:
            if k % 3 == 0:
                t.ponto(xx, yy, "alien_medio")
                t.ponto(xx + 1, yy, "alien_luz")
            else:
                t.chapado(t.elipse(xx, yy, 2, 1.2), "cinza_escuro")
                t.ponto(xx - 1, yy - 1, "cinza")
    return t, fator


def camada_meio():
    """Longe (0,45): morros. A) com caatinga ainda verde e uma casa ardendo; B) morros
    torrados com árvores deitadas e focos de fogo; C) encosta da cratera com veios de vidro."""
    fator = 0.45
    W = int(LARGURA * fator + 548)
    alt = 72
    t = Tela(W, alt)
    rng = np.random.default_rng(5)
    n = ruido(1, W, 30, 6)[0]
    xs = np.arange(W)
    alto = (alt - 28 + n * 6 - np.clip((xs - 1150 * fator) / 300, 0, 1) * 10).astype(int)
    morro = t.yy >= alto[None, :]
    zona = xs / fator  # x do mundo correspondente (aprox.)
    queimado = np.clip((zona - 450) / 250, 0, 1)
    sub_n = Tela(W, alt)
    sub_n.volume(morro, ["azul_sombra", "terra", "terra_media", "barro", "areia_media", "areia"], achatado=6, suave=3,
                 ambiente=0.35, textura=0.2, semente=2, linha=False)
    sub_q = Tela(W, alt)
    sub_q.volume(morro, ["sombra", "marrom_noite", "couro_profundo", "terra_escura", "cinza_escuro", "cinza_medio"],
                 achatado=6, suave=3, ambiente=0.35, textura=0.25, semente=3, linha=False)
    usa_q = (queimado[None, :] > lim(alt, W)) & morro
    t.px[morro] = sub_n.px[morro]
    t.px[usa_q] = sub_q.px[usa_q]
    f1.textura_morro(t, morro & ~usa_q, alto, rng)
    # Vegetação: viva no A, torrada e deitada no B, nada no C.
    x = 0
    while x < W:
        wx = x / fator
        if wx < 1150:
            h = int(rng.integers(10, 24))
            if wx < 500:
                a = f1.arvore(h, semente=int(x), folhas=rng.random() > 0.3)
            else:
                a = arvore_queimada(h, semente=int(x), forca=0.15 + (wx - 500) / 1300)
            f1.colar(t, a, x, alto[min(W - 1, x)] - a.h + 4)
        x += int(rng.integers(6, 26))
    # Focos de fogo nos morros torrados.
    for wx in (600, 760, 900, 1040):
        xx = int(wx * fator)
        yy = alto[xx] + 2
        for k in range(3):
            t.chapado(t.elipse(xx + k * 2 - 2, yy - k * 1.6, 2.4 - k * 0.6, 1.6), BRASA[k + 1])
    # Casa ardendo no morro (A).
    ca = casa_ardendo(46, 30, semente=12)
    xx = int(330 * fator)
    f1.colar(t, ca, xx, alto[xx] - ca.h + 5)
    # Veios de vidro na encosta da cratera (C).
    for k in range(40):
        xx = int(rng.integers(int(1150 * fator), W - 2))
        yy = int(rng.integers(alto[xx] + 2, alt - 2))
        if morro[yy, xx]:
            t.px[yy, xx] = IDX["alien_esc"]
            t.px[yy, xx + 1] = IDX["alien_medio"]
    # Barracas da base ao longe (o próximo trecho), pequenas no alto da encosta.
    import fase1_extra as ext
    for k, wx in enumerate((1500, 1580, 1660)):
        b = ext.barraca(26, 14, semente=k + 20)
        xx = int(wx * fator)
        f1.colar(t, b, xx, alto[min(W - 1, xx)] - b.h + 3)
    return t, fator


def previa(saida, cams=(0, 560, 1150)):
    """Monta telas do trecho em várias posições da câmera para mostrar a mudança do fundo."""
    from PIL import Image
    import cenario as cn
    jogo, topo = camada_jogo()
    perto, fp = camada_perto()
    meio, fm = camada_meio()
    longe, fl = camada_longe()
    ceu1, ceu2 = cn.ceu().imagem(), ceu_fumaca().imagem()
    ims = []
    for cam in cams:
        o = Image.new("RGBA", (548, 308))
        mistura = min(1, max(0, (cam - 300) / 800))
        o.alpha_composite(Image.blend(ceu1, ceu2, mistura), (0, 0))
        for im, base, fat in ((longe.imagem(), 160, fl), (meio.imagem(), 192, fm), (perto.imagem(), 194, fp)):
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
