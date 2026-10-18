"""Cenário detalhado da fase 1 (caatinga), no nível de detalhe do Metal Slug:
volume em todas as peças, textura, rachaduras, sombras frias e luz quente.

Peças soltas (árvore, mandacaru, pedra, casa de taipa, sacos de areia...) e as
funções que montam as camadas da fase. Usado por tools/arte/exportar.py.
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from motor import BAYER4, IDX, VAZIO, Tela  # noqa: E402

# Rampas (escuro -> claro). Sombras puxando para o azul, luz quente.
TERRA = ["sombra", "terra_escura", "terra", "terra_media", "barro", "areia_media"]
TERRA_ESC = ["marrom_noite", "sombra", "terra_escura", "terra", "terra_media"]
AREIA = ["terra", "barro", "areia_media", "areia", "areia_luz", "areia_clara"]
PEDRA = ["sombra", "sombra_media", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]
PEDRA_QUENTE = ["sombra", "azul_sombra", "terra_escura", "terra", "terra_media", "barro", "areia_media"]
CASCA = ["marrom_noite", "couro_profundo", "couro_escuro", "couro", "couro_medio"]
GALHO_SECO = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]
FOLHA = ["sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru", "mandacaru_luz"]
CACTO = ["sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru", "mandacaru_luz"]
REBOCO = ["terra", "terra_media", "barro", "areia_media", "areia", "areia_luz"]
TELHA = ["marrom_noite", "vermelho_esc", "terra_escura", "terra", "laranja_escuro", "barro"]
MADEIRA = ["marrom_noite", "couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz"]
SACO = ["terra_escura", "terra", "terra_media", "areia_media", "areia", "areia_luz"]
OSSO = ["cinza_medio", "cinza", "cinza_luz", "cinza_claro", "branco"]
METAL = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "cinza_claro"]


def ruido(h, w, sigma, semente):
    rng = np.random.default_rng(semente)
    r = ndimage.gaussian_filter(rng.standard_normal((h, w)), sigma)
    return r / (r.std() + 1e-9)


def colar(base, peca, x, y):
    """Cola a peça com o canto de cima à esquerda em (x, y)."""
    base.colar(peca, int(round(x)), int(round(y)))


def cortar(t):
    """Recorta a tela ao conteúdo (para peças desenhadas numa tela folgada)."""
    ys, xs = np.where(t.px != VAZIO)
    if len(xs) == 0:
        return t
    n = Tela(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
    n.px = t.px[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    return n


# ================================================================ acabamento
def _mapa_escuro():
    """Para cada cor da paleta, a cor mais parecida que seja mais escura (sombra de contato)."""
    from motor import RGB
    lum = RGB.astype(float) @ np.array([0.3, 0.59, 0.11])
    mapa = np.arange(len(RGB))
    for i in range(len(RGB)):
        melhor, dist = i, 1e9
        for j in range(len(RGB)):
            if lum[j] >= lum[i] * 0.86 or lum[j] < lum[i] * 0.45:
                continue
            ci = RGB[i] / max(lum[i], 1)
            cj = RGB[j] / max(lum[j], 1)
            d = np.sum((ci - cj) ** 2) * 900 + (lum[i] * 0.72 - lum[j]) ** 2 * 0.02
            if d < dist:
                melhor, dist = j, d
        mapa[i] = melhor
    mapa[IDX["preto"]] = IDX["preto"]
    return mapa


ESCURO = _mapa_escuro()


def sombra_contato(t, cx, y, larg, alt=3.0):
    """Escurece o chão embaixo de um objeto, para ele 'assentar' (não parecer colado)."""
    m = t.elipse(cx, y, larg / 2, alt) & (t.px != VAZIO)
    t.px[m] = ESCURO[t.px[m]]
    m2 = t.elipse(cx, y, larg * 0.35, alt * 0.6) & (t.px != VAZIO)
    t.px[m2] = ESCURO[t.px[m2]]


def assentar(t, peca, x, chao_y, afundar=1):
    """Cola a peça em pé no chão (y do chão), com sombra de contato embaixo."""
    sombra_contato(t, x + peca.w / 2, chao_y + 1, peca.w * 1.05)
    colar(t, peca, x, chao_y - peca.h + afundar)


def tabuas(w, h, vertical=True, semente=0, rampa=None):
    """Tábuas uma a uma: contorno entre elas, veio da madeira, nós, pregos,
    luz na borda de cima/esquerda e sombra na de baixo/direita."""
    rampa = rampa or ["couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_claro", "couro_luz"]
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    comp = h if vertical else w
    larg_total = w if vertical else h
    pos = 0
    while pos < larg_total:
        lt = int(rng.integers(4, 7))
        base = int(rng.integers(2, 4))
        for a in range(lt):
            for b in range(comp):
                x, y = (pos + a, b) if vertical else (b, pos + a)
                if x >= w or y >= h:
                    continue
                n = base
                if a == 0:
                    n = base + 1  # luz na borda
                if a == lt - 1:
                    n = base - 1  # sombra na borda
                t.px[y, x] = IDX[rampa[max(0, min(len(rampa) - 1, n))]]
        # Veio: linhas onduladas ao longo da tábua.
        for k in range(2):
            a0 = rng.uniform(1, lt - 1.5)
            for b in range(comp):
                a = a0 + math.sin(b / rng.uniform(4, 7) + k) * 0.6
                x, y = (pos + int(a), b) if vertical else (b, pos + int(a))
                if x < w and y < h and rng.random() < 0.75:
                    t.px[y, x] = IDX[rampa[max(0, base - 1)]]
        # Nó da madeira.
        if rng.random() < 0.5 and comp > 8:
            b = rng.uniform(3, comp - 3)
            cx, cy = (pos + lt / 2, b) if vertical else (b, pos + lt / 2)
            t.chapado(t.elipse(cx, cy, 1.2, 1.0), rampa[0])
            t.ponto(int(cx) - 1, int(cy) - 1, rampa[min(len(rampa) - 1, base + 2)])
        # Pregos perto das pontas.
        for b in (1, comp - 2):
            x, y = (pos + lt // 2, b) if vertical else (b, pos + lt // 2)
            if x < w and y < h:
                t.ponto(x, y, "cinza_claro")
        # Junta escura entre uma tábua e a próxima.
        pos += lt
        for b in range(comp):
            x, y = (pos, b) if vertical else (b, pos)
            if x < w and y < h:
                t.px[y, x] = IDX[rampa[0]]
        pos += 1
    return t


def caixote_detalhado():
    """Caixote de tábuas com travessa em X, cantoneiras de ferro e marca pintada."""
    t = tabuas(24, 18, vertical=False, semente=8)
    for (x0, y0, x1, y1) in ((2, 2, 21, 15), (2, 15, 21, 2)):
        m = t.capsula(x0, y0, x1, y1, 1.4)
        t.volume(m, MADEIRA, achatado=1, suave=0.3, ambiente=0.35, linha=True)
    for x in (0, 21):
        t.cel(t.retangulo(x, 0, 3, 18), ["sombra", "couro_escuro", "couro", "couro_medio"], sombra=1)
    for (x, y) in ((0, 0), (21, 0), (0, 15), (21, 15)):
        t.cel(t.retangulo(x, y, 3, 3), ["sombra", "cinza_escuro", "cinza", "cinza_claro"], sombra=1)
        t.ponto(x + 1, y + 1, "branco")
    t.contorno("sombra")
    return t


# ================================================================ peças
def pedra(w, h, semente=0, rampa=PEDRA, musgo=True):
    """Pedregulho: contorno irregular, volume, facetas, rachaduras e líquen."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    cx, cy = w / 2, h * 0.58
    ang = np.arctan2(t.yy - cy, t.xx - cx)
    raio = np.hypot((t.xx - cx) / (w / 2), (t.yy - cy) / (h * 0.58))
    borda = 0.86 + 0.1 * np.sin(ang * 3 + rng.uniform(0, 6)) + 0.06 * np.sin(ang * 7 + rng.uniform(0, 6))
    m = (raio < borda) & (t.yy < h - 0.5)
    t.volume(m, rampa, achatado=min(w, h) * 0.35, suave=1.0, ambiente=0.18, textura=0.18, semente=semente)
    # Facetas: linhas de quebra com um lado iluminado.
    for _ in range(max(1, w // 12)):
        x0 = rng.uniform(w * 0.2, w * 0.8)
        y0 = rng.uniform(h * 0.15, h * 0.5)
        x1 = x0 + rng.uniform(-w * 0.25, w * 0.25)
        y1 = y0 + rng.uniform(h * 0.25, h * 0.45)
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for k in range(n):
            x = int(x0 + (x1 - x0) * k / n + rng.integers(-1, 2) * (k % 3 == 0))
            y = int(y0 + (y1 - y0) * k / n)
            if 0 <= y < h and 0 <= x < w and m[y, x]:
                t.px[y, x] = IDX[rampa[0]]
                if x - 1 >= 0 and m[y, x - 1]:
                    t.px[y, x - 1] = IDX[rampa[-1]]
    if musgo:
        # Líquen amarelado e verde-acinzentado nas partes de cima.
        manchas = (ruido(h, w, 1.2, semente + 5) > 1.1) & m & (t.yy < h * 0.55)
        t.px[manchas] = IDX["mandacaru_luz"]
        manchas2 = (ruido(h, w, 0.8, semente + 9) > 1.6) & m
        t.px[manchas2] = IDX["areia_luz"]
    t.contorno("sombra")
    return t


def arvore(altura=70, semente=0, folhas=True):
    """Árvore da caatinga: tronco torto com casca, galhos finos e copa em tufos."""
    W = int(altura * 1.1)
    t = Tela(W, altura)
    rng = np.random.default_rng(semente)
    galhos = np.zeros((altura, W), dtype=bool)
    pontas = []

    def ramo(x, y, ang, comp, esp, prof):
        x1 = x + math.cos(ang) * comp
        y1 = y + math.sin(ang) * comp
        nonlocal galhos
        galhos |= t.capsula(x, y, x1, y1, esp, max(0.5, esp * 0.65))
        if prof == 0 or comp < 4:
            pontas.append((x1, y1))
            return
        n = 2 if prof > 1 else rng.integers(2, 4)
        for k in range(n):
            da = rng.uniform(0.25, 0.75) * (1 if k % 2 else -1)
            ramo(x1, y1, ang + da, comp * rng.uniform(0.62, 0.8), esp * 0.68, prof - 1)

    base = W / 2
    tronco_topo = altura * 0.55
    # Tronco torto em dois segmentos.
    meio = (base + rng.uniform(-4, 4), altura - altura * 0.25)
    galhos |= t.capsula(base, altura - 1, meio[0], meio[1], altura * 0.06, altura * 0.05)
    topo = (meio[0] + rng.uniform(-5, 5), tronco_topo)
    galhos |= t.capsula(meio[0], meio[1], topo[0], topo[1], altura * 0.05, altura * 0.04)
    galhos |= t.elipse(base, altura - 1.5, altura * 0.1, 2)  # raízes
    for k in range(3):
        ramo(topo[0], topo[1], -math.pi / 2 + (k - 1) * 0.65, altura * 0.22, altura * 0.035, 3)
    t.volume(galhos, CASCA if folhas else GALHO_SECO, achatado=2, suave=0.6, ambiente=0.15, textura=0.25,
             semente=semente)
    # Casca: estrias verticais escuras no tronco.
    estrias = galhos & (((t.xx.astype(int) * 3 + (ruido(altura, W, 0.6, semente) > 0.5)) % 4) == 0) & (t.yy > tronco_topo)
    t.px[estrias] = IDX[(CASCA if folhas else GALHO_SECO)[1]]
    if folhas:
        # Copa em tufos: muitas bolinhas com volume, das de trás (escuras) às da frente.
        tufos = []
        for (px, py) in pontas:
            for _ in range(2):
                tufos.append((px + rng.uniform(-3, 3), py + rng.uniform(-2, 3), rng.uniform(3, 6)))
        tufos.sort(key=lambda c: c[1])
        for k, (x, y, r) in enumerate(tufos):
            m = t.elipse(x, y, r * 1.25, r) & ~(t.yy > altura * 0.75)
            t.volume(m, FOLHA, achatado=r * 0.7, suave=0.8, ambiente=0.1 + 0.25 * (k / len(tufos)),
                     textura=0.35, semente=semente + k)
        # Folhinhas soltas na borda da copa.
        cheio = t.px != VAZIO
        borda = ndimage.binary_dilation(cheio) & ~cheio
        solto = borda & (np.random.default_rng(semente + 3).random(borda.shape) < 0.25) & (t.yy < altura * 0.65)
        t.px[solto] = IDX["caatinga_media"]
    t.contorno("sombra")
    return t


def mandacaru(altura=48, semente=0, bracos=2):
    """Mandacaru: coluna com gomos, braços em candelabro, espinhos e flor."""
    W = 34
    t = Tela(W, altura)
    rng = np.random.default_rng(semente)
    cx = W / 2
    partes = [t.capsula(cx, altura - 1, cx, 5, 3.6, 3.2)]
    for k in range(bracos):
        lado = -1 if k % 2 == 0 else 1
        y0 = altura * rng.uniform(0.45, 0.7)
        x1 = cx + lado * rng.uniform(7, 10)
        y1 = y0 - rng.uniform(2, 4)
        topo = y0 - altura * rng.uniform(0.3, 0.45)
        partes.append(t.capsula(cx, y0, x1, y1, 2.6, 2.6) | t.capsula(x1, y1, x1, topo, 2.7, 2.4))
    for m in partes:
        t.volume(m, CACTO, achatado=2.5, suave=0.6, ambiente=0.15)
        # Gomos: linhas verticais escuras e claras alternadas.
        xs = t.xx.astype(int)
        gomo = m & (xs % 3 == 0)
        t.px[gomo] = IDX["caatinga_esc"]
        luz = m & (xs % 3 == 1) & (t.px == IDX["mandacaru"])
        t.px[luz] = IDX["mandacaru_luz"]
    tudo = np.zeros((altura, W), dtype=bool)
    for m in partes:
        tudo |= m
    # Espinhos: pontinhos claros na borda dos gomos.
    esp = tudo & ((t.xx.astype(int) % 3 == 0) & (t.yy.astype(int) % 3 == 1))
    t.px[esp] = IDX["areia_clara"]
    t.contorno("sombra")
    if rng.random() < 0.6:
        t.ponto(int(cx), 3, "rosa_poeira")
        t.ponto(int(cx) - 1, 4, "lilas_claro")
    return t


def xiquexique(w=26, semente=0):
    """Touceira baixa de xique-xique: hastes deitadas que sobem nas pontas."""
    t = Tela(w, 16)
    rng = np.random.default_rng(semente)
    for k in range(5):
        x0 = w / 2 + rng.uniform(-3, 3)
        x1 = rng.uniform(2, w - 2)
        m = t.capsula(x0, 15, x1, 15 - rng.uniform(5, 13), 1.6, 1.3)
        t.volume(m, CACTO, achatado=1.5, suave=0.5, ambiente=0.2)
    esp = (t.px != VAZIO) & ((t.xx.astype(int) + t.yy.astype(int)) % 3 == 0)
    t.px[esp] = IDX["areia_clara"]
    t.contorno("sombra")
    return t


def capim(w=14, semente=0, seco=True):
    """Tufo de capim seco: fios finos curvados."""
    t = Tela(w, 10)
    rng = np.random.default_rng(semente)
    cores = ["barro", "areia_media", "areia", "areia_luz", "terra_media"] if seco else ["caatinga_esc", "caatinga", "mandacaru"]
    for k in range(9):
        x0 = w / 2 + rng.uniform(-2, 2)
        x1 = x0 + rng.uniform(-6, 6)
        y1 = rng.uniform(0, 5)
        t.linha(x0, 9, x1, y1, cores[k % len(cores)])
    return t


def cranio_boi():
    """Caveira de boi com chifres, largada no chão."""
    t = Tela(22, 11)
    t.volume(t.elipse(11, 6, 4.5, 4) | t.elipse(11, 9, 2.6, 2), OSSO, achatado=2, suave=0.5, ambiente=0.3)
    chifre = t.capsula(7, 4, 2, 1, 1.4, 0.5) | t.capsula(15, 4, 20, 1, 1.4, 0.5)
    t.volume(chifre, OSSO, achatado=1, suave=0.4, ambiente=0.35)
    t.chapado(t.elipse(9, 5.5, 1.1, 1.3), "sombra")
    t.chapado(t.elipse(13, 5.5, 1.1, 1.3), "sombra")
    t.pontos([(10, 9), (12, 9)], "cinza_escuro")
    t.contorno("sombra")
    return t


def sacos_areia(n=4, filas=2):
    """Trincheira de sacos de areia empilhados, com costura e sombra entre eles."""
    W = n * 13 + 6
    H = filas * 7 + 4
    t = Tela(W, H)
    for f in range(filas):
        y = H - 5 - f * 7
        desloc = 6 if f % 2 else 0
        for k in range(n - (f % 2)):
            x = 3 + desloc + k * 13
            m = t.elipse(x + 6.5, y, 7, 4)
            t.volume(m, SACO, achatado=2.5, suave=0.7, ambiente=0.2, textura=0.2, semente=f * 10 + k)
            t.linha(x + 2, y - 1, x + 11, y - 1, "terra")
            t.pontos([(x + 3, y - 2), (x + 6, y - 2), (x + 9, y - 2)], "areia_clara")
    t.contorno("sombra")
    return t


def cerca(w=80, semente=0):
    """Cerca de varas tortas amarradas com arame."""
    t = Tela(w, 26)
    rng = np.random.default_rng(semente)
    x = 2
    while x < w - 2:
        alt = rng.uniform(16, 24)
        inc = rng.uniform(-1.2, 1.2)
        m = t.capsula(x, 25, x + inc, 25 - alt, 1.3, 1.0)
        t.volume(m, GALHO_SECO, achatado=1, suave=0.4, ambiente=0.25)
        x += rng.uniform(5, 8)
    for y in (9, 16):
        for xx in range(0, w):
            yy = y + int(math.sin(xx / 7) * 0.8)
            if t.px[yy, xx] == VAZIO:
                t.px[yy, xx] = IDX["cinza_escuro"]
    t.contorno("sombra")
    return t


def casa_taipa(w=120, h=86, semente=0, quebrada=True):
    """Casa de taipa: parede rebocada descascando (aparece o trançado de varas
    e barro), porta e janela de madeira, telhado de telha canal."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    beiral = max(9, int(h * 0.3))
    alt_porta = min(40, h - beiral - 3)
    parede = t.retangulo(6, beiral, w - 12, h - beiral)
    t.volume(parede, REBOCO, achatado=3, suave=1.0, ambiente=0.35, textura=0.22, semente=semente, luz=(-0.3, -0.9))
    # Reboco caído: manchas mostrando o trançado de varas com barro.
    caido = (ruido(h, w, 3.0, semente + 1) > 1.0) & parede & (t.yy > beiral + 6)
    # Onde o reboco caiu aparecem os tijolos de adobe, um a um, com junta escura.
    xi = t.xx.astype(int)
    yi = t.yy.astype(int)
    fila = yi // 4
    junta = ((yi % 4) == 0) | (((xi + (fila % 2) * 4) % 8) == 0)
    tons = np.array([IDX["barro"], IDX["terra_media"], IDX["areia_media"], IDX["terra"]])
    tijolo = tons[((xi + (fila % 2) * 4) // 8 * 7 + fila * 3) % 4]
    t.px[caido] = tijolo[caido]
    t.px[caido & junta] = IDX["terra_escura"]
    t.px[caido & ~junta & ((yi % 4) == 1)] = IDX["areia_luz"]
    borda_caido = ndimage.binary_dilation(caido) & ~caido & parede
    t.px[borda_caido] = IDX["areia_luz"]
    borda_baixo = ndimage.binary_dilation(caido) & ~caido & parede & (np.roll(caido, 1, 0))
    t.px[borda_baixo] = IDX["terra"]
    # Sombra do beiral na parede.
    sob = parede & (t.yy < beiral + 3)
    t.px[sob] = ESCURO[t.px[sob]]
    # Rachaduras.
    for _ in range(4):
        x, y = rng.uniform(12, w - 12), rng.uniform(beiral + 2, max(beiral + 3, h - 10))
        for k in range(10):
            x += rng.uniform(-1.2, 1.2)
            y += 1
            if 0 <= int(y) < h and parede[int(y), int(x)]:
                t.px[int(y), int(x)] = IDX["terra_escura"]
    # Porta de tábuas entreaberta.
    lp_ = max(6, w * 0.15)  # largura da porta
    porta = t.retangulo(w * 0.22, h - alt_porta, lp_, alt_porta)
    t.chapado(porta, "marrom_noite")
    folha = tabuas(max(4, int(lp_ * 0.6)), int(alt_porta), vertical=True, semente=semente + 3)
    colar(t, folha, w * 0.22, h - alt_porta)
    t.chapado(t.retangulo(w * 0.22 - 1, h - alt_porta - 1, lp_ + 2, 1.5), "couro_profundo")
    # Janela com tramela.
    jw = max(6, w * 0.17)
    jh = max(5, (h - beiral) * 0.27)
    jx, jy = w * 0.62, beiral + (h - beiral) * 0.27
    t.chapado(t.retangulo(jx, jy, jw, jh), "marrom_noite")
    t.volume(t.retangulo(jx, jy, jw * 0.35, jh), MADEIRA, achatado=1.2, suave=0.5, ambiente=0.25)
    t.volume(t.retangulo(jx + jw * 0.7, jy, jw * 0.3, jh), MADEIRA, achatado=1.2, suave=0.5, ambiente=0.2)
    t.chapado(t.retangulo(jx - 2, jy + jh, jw + 4, 2), "couro")
    # Telhado de telha canal: fileiras de telhas com volume.
    telhado = t.poligono([(0, beiral + 1), (w * 0.15, 4), (w * 0.85, 2), (w, beiral + 1)])
    if quebrada:
        buraco = t.elipse(w * 0.7, 10, 9, 6)
        telhado &= ~buraco
    t.chapado(telhado, "vermelho_esc")
    for fila in range(0, beiral + 2, 3):
        for x in range(-2, w + 2, 4):
            xx = x + (2 if (fila // 3) % 2 else 0)
            m = t.elipse(xx + 2, fila + 1.5, 2.2, 2.0) & telhado
            t.volume(m, TELHA, achatado=1, suave=0.3, ambiente=0.25, linha=False)
    t.chapado(t.retangulo(2, beiral, w - 4, 2) & ~parede, "terra_escura")
    # Caibros aparecendo no buraco do telhado.
    if quebrada:
        for k in range(4):
            t.linha(w * 0.62 + k * 4, 4, w * 0.6 + k * 4, 16, "couro_escuro")
    t.contorno("sombra")
    return t


def cata_vento(altura=70):
    """Cata-vento de metal: torre treliçada e a roda de pás."""
    t = Tela(40, altura)
    base = altura - 1
    for lado in (-1, 1):
        t.linha(20 + lado * 9, base, 20 + lado * 1.5, 14, "cinza_escuro")
    for y in range(20, base, 8):
        f = (y - 14) / (base - 14)
        w = 1.5 + 7.5 * f
        t.linha(20 - w, y, 20 + w, y + 6, "cinza_medio")
        t.linha(20 + w, y, 20 - w, y + 6, "cinza_medio")
    for k in range(12):
        a = k * math.pi / 6
        m = t.capsula(20, 12, 20 + math.cos(a) * 11, 12 + math.sin(a) * 11, 1.0, 2.0)
        t.volume(m, METAL, achatado=1, suave=0.4, ambiente=0.3)
    t.cel(t.elipse(20, 12, 2.2, 2.2), ["sombra", "cinza_escuro", "cinza", "cinza_claro"], sombra=1)
    t.cel(t.poligono([(22, 10), (34, 9), (34, 15), (22, 14)]), ["sombra", "vermelho_esc", "vermelho_medio", "vermelho"], sombra=1)
    t.contorno("sombra")
    return t


# ================================================================ chão em corte
def chao(w, h=26, semente=0, queimado=False):
    """Faixa de chão vista em corte: capim e pedrisco em cima, camadas de terra
    com pedras enterradas, raízes e rachaduras."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    n = ruido(h, w, 2.0, semente)
    # Camadas de terra (estratos) levemente onduladas.
    camada = (t.yy + n * 1.5) / h
    rampa = TERRA_ESC if queimado else TERRA
    nivel = np.clip((1 - camada) * (len(rampa) - 1), 0, len(rampa) - 1)
    lim = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
    nivel = np.floor(nivel + (lim - 0.5) * 0.6).clip(0, len(rampa) - 1).astype(int)
    t.px[:, :] = np.array([IDX[c] for c in rampa])[nivel]
    # Faixas escuras de estrato.
    for y0 in (9, 16):
        faixa = (np.abs(t.yy - y0 - n * 1.2) < 0.6)
        t.px[faixa] = IDX[rampa[1]]
    # Crosta clara no topo.
    t.px[0:2, :] = IDX["areia" if not queimado else "terra"]
    t.px[0, :] = IDX["areia_luz" if not queimado else "terra_media"]
    # Pedras enterradas.
    for _ in range(w // 18):
        pw, ph = rng.integers(4, 9), rng.integers(3, 6)
        p = pedra(pw, ph, semente=int(rng.integers(0, 9999)), musgo=False)
        colar(t, p, rng.uniform(0, w - pw), rng.uniform(4, h - ph))
    # Pedrisco na crosta.
    for _ in range(w // 4):
        x = int(rng.uniform(0, w))
        t.ponto(x, int(rng.integers(1, 4)), rng.choice(["cinza_luz", "cinza", "terra_escura", "areia_clara"]))
    # Raízes finas.
    for _ in range(w // 40):
        x = rng.uniform(0, w)
        y = 2
        for k in range(rng.integers(6, 12)):
            nx, ny = x + rng.uniform(-1.5, 1.5), y + 1
            t.linha(x, y, nx, ny, "couro_escuro" if not queimado else "preto")
            x, y = nx, ny
    # Rachaduras.
    for _ in range(w // 30):
        x = rng.uniform(0, w)
        y = 1
        for k in range(rng.integers(4, 9)):
            nx, ny = x + rng.uniform(-1, 1), y + 1
            t.linha(x, y, nx, ny, "sombra")
            x, y = nx, ny
    return t


def lajedo(w, h=40, semente=0):
    """Lajedo de granito: blocos arredondados empilhados, topo plano onde se pisa,
    fendas, líquen e sombra fria por baixo."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    GRANITO = ["sombra", "sombra_media", "azul_sombra", "cinza_escuro", "terra_media", "barro", "areia_media", "areia_luz"]
    # Blocos de trás para a frente: de cima (largos e chatos) para baixo (mais redondos).
    blocos = []
    y = 1
    while y < h - 2:
        alt = rng.uniform(8, 13)
        x = rng.uniform(-4, 4)
        while x < w:
            larg = rng.uniform(16, 30)
            blocos.append((x, y, larg, alt))
            x += larg - rng.uniform(2, 5)
        y += alt - 3
    tudo = np.zeros((h, w), dtype=bool)
    ids = np.full((h, w), -1)
    for k, (x, y, larg, alt) in enumerate(blocos):
        r = min(alt, larg) * 0.45
        m = (t.retangulo(x + r, y, larg - 2 * r, alt) | t.retangulo(x, y + r, larg, alt - 2 * r) |
             t.elipse(x + r, y + r, r, r) | t.elipse(x + larg - r, y + r, r, r) |
             t.elipse(x + r, y + alt - r, r, r) | t.elipse(x + larg - r, y + alt - r, r, r))
        m &= (t.yy >= 0) & ~tudo
        t.volume(m, GRANITO, achatado=3, suave=0.9, ambiente=0.2, textura=0.22, semente=semente * 31 + k,
                 luz=(-0.45, -0.85))
        tudo |= m
        ids[m] = k
    # Fendas escuras entre os blocos e um fio de luz na borda de cima de cada um.
    cima = np.roll(ids, 1, 0)
    esq = np.roll(ids, 1, 1)
    fenda = tudo & (((cima != ids) & (cima >= 0)) | ((esq != ids) & (esq >= 0)))
    t.px[fenda] = IDX["sombra"]
    luz = tudo & ~fenda & np.roll(fenda, 1, 0)
    t.px[luz] = IDX["areia_luz"]
    # Topo plano e claro (onde se pisa).
    t.px[(t.px != VAZIO) & (t.yy < 3)] = IDX["areia_media"]
    t.px[(t.px != VAZIO) & (t.yy < 1.5)] = IDX["areia_luz"]
    # Fendas finas.
    for _ in range(max(1, w // 18)):
        x = rng.uniform(4, w - 4)
        for yy in range(3, h, 1):
            x += rng.uniform(-0.7, 0.7)
            if 0 <= int(x) < w and tudo[yy, int(x)] and rng.random() < 0.8:
                t.px[yy, int(x)] = IDX["sombra"]
    # Líquen.
    liquen = (ruido(h, w, 1.0, semente + 3) > 1.4) & tudo & (t.yy > 3)
    t.px[liquen] = IDX["mandacaru_luz"]
    t.contorno("sombra")
    return t

def pote_barro(semente=0, alt=14):
    """Pote de barro (moringa) com boca, alça e mancha de umidade."""
    t = Tela(14, alt)
    corpo = t.elipse(7, alt - 6, 6, 5.5) | t.retangulo(4, 1.5, 6, alt - 8)
    t.volume(corpo, ["marrom_noite", "terra_escura", "terra", "laranja_escuro", "barro", "areia_media"], achatado=3,
             suave=0.8, ambiente=0.25, textura=0.2, semente=semente)
    t.cel(t.elipse(7, 2, 3.4, 1.4), ["sombra", "terra_escura", "terra", "barro"], sombra=0)
    t.chapado(t.elipse(7, 2, 2, 0.7), "marrom_noite")
    t.linha(3, alt - 7, 11, alt - 7, "terra_escura")
    t.contorno("sombra")
    return t


def roda_carroca(r=9):
    """Roda de carroça de madeira com raios e aro de ferro."""
    t = Tela(2 * r + 2, 2 * r + 2)
    c = r + 1
    aro = t.elipse(c, c, r, r) & ~t.elipse(c, c, r - 2, r - 2)
    t.volume(aro, MADEIRA, achatado=1, suave=0.3, ambiente=0.25)
    t.px[t.elipse(c, c, r, r) & ~t.elipse(c, c, r - 0.8, r - 0.8)] = IDX["cinza_escuro"]
    for k in range(8):
        a = k * math.pi / 4
        m = t.capsula(c, c, c + math.cos(a) * (r - 1.5), c + math.sin(a) * (r - 1.5), 0.8)
        t.volume(m, MADEIRA, achatado=0.5, suave=0.2, ambiente=0.3)
    t.cel(t.elipse(c, c, 2.2, 2.2), MADEIRA[:4], sombra=1)
    t.contorno("sombra")
    return t


def carroca_quebrada():
    """Carroça tombada: plataforma de tábuas inclinada, uma roda e o cabeçalho no chão."""
    t = Tela(64, 30)
    tab = tabuas(44, 7, vertical=True, semente=21)
    # Plataforma inclinada (pende para a esquerda, onde falta a roda).
    for x in range(tab.w):
        dy = int(x * 0.18)
        for y in range(tab.h):
            if tab.px[y, x] != VAZIO:
                yy = 12 - dy + y + 6
                if 0 <= yy < t.h:
                    t.px[yy, x + 6] = tab.px[y, x]
    for x in (8, 44):
        t.volume(t.retangulo(x, 18 - int((x - 6) * 0.18), 2, 8), MADEIRA, achatado=0.5, suave=0.2, ambiente=0.3)
    roda = roda_carroca(9)
    colar(t, roda, 36, 30 - roda.h)
    t.volume(t.capsula(48, 22, 63, 28, 1.2), MADEIRA, achatado=0.5, suave=0.2, ambiente=0.3)
    t.contorno("sombra")
    return t


def pilao():
    """Pilão de madeira com a mão de pilão encostada."""
    t = Tela(14, 20)
    corpo = t.poligono([(2, 8), (12, 8), (10, 14), (11, 20), (3, 20), (4, 14)])
    t.volume(corpo, MADEIRA, achatado=2, suave=0.5, ambiente=0.25, textura=0.2)
    t.chapado(t.elipse(7, 8.5, 4.5, 1.2), "couro_profundo")
    t.volume(t.capsula(9, 9, 12, 0.5, 1.0), MADEIRA, achatado=0.5, suave=0.2, ambiente=0.35)
    t.contorno("sombra")
    return t


def cabacas():
    """Penca de cabaças penduradas numa corda."""
    t = Tela(12, 18)
    t.linha(6, 0, 6, 5, "terra_media")
    for (x, y, r) in ((4, 9, 3), (8, 11, 3.3), (5, 14, 2.6)):
        m = t.elipse(x, y, r, r * 1.1) | t.elipse(x, y - r, r * 0.45, r * 0.6)
        t.volume(m, ["terra_escura", "couro", "couro_medio", "areia_media", "areia_luz"], achatado=2, suave=0.5,
                 ambiente=0.3)
    t.contorno("sombra")
    return t


def cerca_farpada(w=90, semente=0):
    """Cerca de mourões tortos com três fios de arame farpado."""
    t = Tela(w, 26)
    rng = np.random.default_rng(semente)
    postes = list(range(3, w - 2, 18))
    for x in postes:
        inc = rng.uniform(-1, 1)
        m = t.capsula(x, 25, x + inc, 4, 1.6, 1.3)
        t.volume(m, GALHO_SECO, achatado=1, suave=0.4, ambiente=0.25, textura=0.3, semente=x)
    for y0 in (8, 14, 20):
        for x in range(0, w):
            y = y0 + int(math.sin(x / 9 + y0) * 0.8)
            if t.px[y, x] == VAZIO:
                t.px[y, x] = IDX["cinza_escuro"]
            if x % 4 == 0:
                t.ponto(x, y - 1, "cinza_claro")
                t.ponto(x, y + 1, "cinza_escuro")
    t.contorno("sombra")
    return t


def forquilha(altura=90, semente=0):
    """Árvore seca com um galho comprido na horizontal, onde penduram o refém.
    O galho fica a 16 px do topo e vai até x = 40."""
    t = Tela(48, altura)
    tronco = t.capsula(8, altura - 1, 9, 10, 3.2, 2.2) | t.elipse(8, altura - 1.5, 6, 2)
    galho = t.capsula(8, 18, 44, 15, 2.0, 1.2)
    ramos = t.capsula(9, 12, 3, 2, 1.2, 0.6) | t.capsula(10, 13, 16, 3, 1.1, 0.5) | t.capsula(30, 16, 35, 8, 0.9, 0.4)
    t.volume(tronco | galho | ramos, GALHO_SECO, achatado=2, suave=0.5, ambiente=0.2, textura=0.3, semente=semente)
    estrias = tronco & ((t.xx.astype(int) % 3) == 0) & (t.yy > 20)
    t.px[estrias] = IDX["cinza_escuro"]
    t.contorno("sombra")
    return t


def buraco(w=26):
    """Buraco cavado no chão (de onde saltam soldados), com terra amontoada em volta."""
    t = Tela(w + 8, 9)
    monte = t.elipse(w / 2 + 4, 6, w / 2 + 4, 4) & (t.yy < 7)
    t.volume(monte, TERRA_ESC, achatado=2, suave=0.6, ambiente=0.3, textura=0.3)
    t.chapado(t.elipse(w / 2 + 4, 6.5, w / 2, 2.4), "preto")
    t.chapado(t.elipse(w / 2 + 4, 6, w / 2 - 1, 1.4), "marrom_noite")
    t.contorno("sombra")
    return t


def fogueira():
    """Fogueira apagando: lenha cruzada e pedras em volta (o fogo é animado no jogo),
    com a panela no tripé."""
    t = Tela(24, 22)
    for (x0, x1) in ((3, 20), (20, 4)):
        t.volume(t.capsula(x0, 20, x1, 17, 1.4), MADEIRA, achatado=0.6, suave=0.3, ambiente=0.3)
    for x in (2, 7, 16, 21):
        t.volume(t.elipse(x, 20, 2.2, 1.8), PEDRA, achatado=1, suave=0.4, ambiente=0.3)
    for (x0, x1) in ((4, 12), (20, 12)):
        t.linha(x0, 21, x1, 2, "cinza_escuro")
    t.volume(t.elipse(12, 9, 5, 3.6) & (t.yy > 6), METAL, achatado=1.5, suave=0.5, ambiente=0.25)
    t.chapado(t.elipse(12, 7, 5, 1.2), "sombra")
    t.contorno("sombra")
    return t


def disco_caido():
    """O disco voador caído, meio enterrado e torto, com a cúpula rachada."""
    t = Tela(130, 64)
    casco = t.elipse(65, 40, 60, 14) & (t.yy < 52)
    t.volume(casco, METAL, achatado=5, suave=1.2, ambiente=0.3, textura=0.15, semente=4)
    aro = t.elipse(65, 40, 60, 14) & ~t.elipse(65, 38, 58, 12) & (t.yy < 52)
    t.px[aro] = IDX["cinza_escuro"]
    for k in range(9):
        x = 18 + k * 12
        t.chapado(t.elipse(x, 42, 2.2, 1.6), "alien" if k % 3 else "alien_brilho")
    cupula = t.elipse(70, 28, 24, 18) & (t.yy < 34)
    t.volume(cupula, ["sombra", "azul_sombra", "ceu_escuro", "ceu_medio", "ceu_claro", "horizonte"], achatado=6,
             suave=1.5, ambiente=0.3)
    t.chapado(t.elipse(62, 18, 5, 3) & cupula, "branco")
    # Rachaduras na cúpula e um rombo no casco.
    for (x0, y0, x1, y1) in ((70, 14, 78, 26), (78, 26, 74, 32), (78, 26, 88, 30), (60, 22, 66, 30)):
        t.linha(x0, y0, x1, y1, "sombra")
    t.chapado(t.elipse(104, 44, 9, 5) & casco, "preto")
    t.chapado(t.elipse(104, 44, 6, 3) & casco, "vermelho_esc")
    t.chapado(t.elipse(104, 45, 3, 1.5) & casco, "laranja_fogo")
    # Terra amontoada na frente (o disco afundou no chão).
    monte = t.elipse(65, 64, 66, 14)
    t.volume(monte, TERRA_ESC, achatado=4, suave=1.5, ambiente=0.2, textura=0.3, semente=7)
    t.contorno("sombra")
    return t


def destrocos(semente=0):
    """Pedaço retorcido do casco do disco, cravado no chão."""
    t = Tela(26, 20)
    rng = np.random.default_rng(semente)
    pts = [(2, 19), (4 + rng.uniform(0, 4), 6), (12, 2 + rng.uniform(0, 3)), (22, 7), (24, 19)]
    m = t.poligono(pts)
    t.volume(m, METAL, achatado=2, suave=0.6, ambiente=0.3, textura=0.25, semente=semente)
    t.chapado(t.elipse(12, 12, 2, 1.5) & m, "alien")
    t.contorno("sombra")
    return t


# ================================================================ a fase
LARGURA_FASE = 5800
PEDACO = 2048
CHAO = 194  # topo do chão sólido (o desenho do chão começa 2 px acima)

# Tudo o que compõe a fase. Coordenadas do mundo; pé = y do chão onde a coisa pisa.
FASE = {
    "largura": LARGURA_FASE,
    "inicio": [40, CHAO - 20],
    "solidos": [
        [0, CHAO, LARGURA_FASE, 30],
        [440, 178, 100, 16],          # lajedo baixo
        [884, 176, 50, 18],           # trincheira de sacos de areia
        [1080, 172, 130, 22],         # lajedo grande: degraus
        [1170, 152, 110, 42],
        [1280, 138, 60, 56],
        [1340, 160, 50, 34],
        [1622, 158, 66, 6, True],     # girau de madeira do curral
        [2120, 170, 90, 24],          # barranco
        [2300, 150, 72, 6, True],     # girau
        [2780, 172, 30, 22],          # pedra grande
        # --- vila de taipa
        [3290, 160, 64, 6, True],     # girau da vila
        # --- leito de rio seco: barrancos em degrau e a ponte por cima
        [3940, 176, 40, 18],
        [3972, 146, 52, 48],
        [4024, 146, 556, 6, True],    # ponte
        [4580, 146, 56, 48],
        [4636, 176, 40, 18],
        # --- acampamento da Volante
        [4900, 176, 56, 18],          # trincheira de sacos de areia
        [5030, 116, 52, 6, True],     # plataforma da torre de vigia
        [5400, 176, 56, 18],          # trincheira
    ],
    "caixotes": [
        [250, CHAO - 18], [740, CHAO - 18], [764, CHAO - 18], [752, CHAO - 36],
        [820, CHAO - 24, "barril"], [838, CHAO - 24, "barril"],
        [1230, 152 - 18], [1760, CHAO - 24, "barril"], [1778, CHAO - 24, "barril"], [1769, CHAO - 48, "barril"],
        [1800, CHAO - 18], [1824, CHAO - 18], [2150, 170 - 18], [2560, CHAO - 18], [2584, CHAO - 18],
        [2700, CHAO - 24, "barril"],
        [3200, CHAO - 18], [3224, CHAO - 18], [3212, CHAO - 36], [3800, CHAO - 24, "barril"],
        [3818, CHAO - 24, "barril"], [4450, CHAO - 18], [4980, CHAO - 24, "barril"], [4998, CHAO - 24, "barril"],
        [4989, CHAO - 48, "barril"], [5300, CHAO - 18], [5560, CHAO - 18], [5584, CHAO - 18],
    ],
    "refens": [[330, CHAO], [1300, 138], [1700, CHAO], [2330, 150], [2640, CHAO],
               [1048, 166, {"pendurado": 124}], [2448, 166, {"pendurado": 124}],
               [3350, CHAO], [4300, 188, {"pendurado": 152}], [5120, CHAO]],
    "itens": [[560, CHAO - 20, "madsen"]],
    "bodes": [[1400, CHAO], [4400, CHAO]],
    "discos": [],
    # Inimigos que já estão no lugar quando o Lampião chega.
    "inimigos": [
        [600, CHAO, "volante"], [940, CHAO, "granadeiro", {"distraido": True}],
        [968, CHAO, "volante", {"distraido": True}], [995, CHAO, "volante", {"escudo": True}],
        [1250, 152, "volante"], [1312, 138, "rojao"], [1650, 158, "granadeiro", {"distraido": True}],
        [2160, 170, "metralhador"], [2340, 150, "granadeiro"], [2560, CHAO, "rojao", {"distraido": True}],
        [3330, 160, "granadeiro"], [3520, CHAO, "volante", {"distraido": True}], [4300, 146, "volante"],
        [4480, CHAO, "facao"], [5056, 116, "rojao"], [5250, CHAO, "volante", {"distraido": True}],
        [5280, CHAO, "granadeiro", {"distraido": True}],
    ],
    # Ondas: ao passar do gatilho, a câmera trava entre trava[0] e trava[1] até todos caírem.
    # Cada inimigo: [tipo, de onde vem, atraso em ms, opções]. De onde vem: "dir"/"esq" (entra pela
    # borda), "salta:x" (pula de um esconderijo), "porta:x" (sai de uma porta). Tipos "caminhao"
    # (traz soldados) e "blindado" são veículos.
    "ondas": [
        {"gatilho": 300, "trava": [140, 524], "inimigos": [["volante", "dir", 0], ["volante", "dir", 900],
                                                           ["volante", "salta:500", 1700]]},
        {"gatilho": 860, "trava": [700, 1084], "inimigos": [["volante", "salta:910", 0], ["facao", "dir", 700],
                                                            ["volante", "esq", 1600], ["metralhador", "dir", 2400],
                                                            ["rojao", "dir", 3200]]},
        {"gatilho": 1720, "trava": [1560, 1944], "inimigos": [["volante", "salta:1700", 0], ["volante", "dir", 500],
                                                              ["granadeiro", "dir", 1200], ["metralhador", "esq", 1800],
                                                              ["facao", "salta:1862", 2400], ["volante", "salta:1862", 3000]]},
        {"gatilho": 2260, "trava": [2100, 2484], "inimigos": [["metralhador", "dir", 0], ["volante", "salta:2382", 300],
                                                              ["volante", "dir", 400], ["rojao", "dir", 2600],
                                                              ["volante", "dir", 1000, {"escudo": True}],
                                                              ["facao", "esq", 1400], ["granadeiro", "dir", 1800],
                                                              ["volante", "salta:2382", 2200]]},
        # Vila: a Volante sai das casas e da capela, e chega um caminhão.
        {"gatilho": 3250, "trava": [3060, 3608], "inimigos": [["volante", "porta:3098", 0], ["volante", "porta:3468", 600],
                                                              ["caminhao", "dir", 1200, {"soldados": ["volante", "granadeiro", "volante"]}],
                                                              ["facao", "porta:3468", 3400], ["volante", "esq", 4000]]},
        # Rio seco: soldados pelo leito e pulando da ponte.
        {"gatilho": 4150, "trava": [3990, 4538], "inimigos": [["volante", "dir", 0], ["granadeiro", "salta:4320", 500],
                                                              ["metralhador", "dir", 1500], ["rojao", "esq", 2300],
                                                              ["volante", "salta:4440", 2800], ["facao", "dir", 3400]]},
        # Acampamento: saem das barracas e de um caminhão.
        {"gatilho": 4880, "trava": [4700, 5248], "inimigos": [["volante", "porta:4782", 0],
                                                              ["caminhao", "dir", 600, {"soldados": ["volante", "facao", "granadeiro", "volante"]}],
                                                              ["metralhador", "salta:4930", 1800], ["volante", "porta:5222", 3000]]},
        # Carro blindado da Volante.
        {"gatilho": 5420, "trava": [5230, 5778], "inimigos": [["blindado", "dir", 300, {"para": 5640}],
                                                              ["volante", "esq", 5000], ["volante", "esq", 9000]]},
    ],
    "fogueiras": [[918, CHAO], [2580, CHAO], [5266, CHAO]],
    "forquilhas": [[1010, 90], [2410, 90]],
    "buracos": [1862, 2382],
    "fim": 5720,
}


def camada_jogo():
    """Plano do jogo: chão em corte, lajedos, trincheira, giraus, barranco,
    mais os enfeites que ficam no chão."""
    alt = 140  # alto o bastante para a capela, a torre de vigia e o mastro
    topo = 216 - alt  # y do mundo onde a camada começa
    t = Tela(LARGURA_FASE, alt)
    rng = np.random.default_rng(1)
    y = lambda wy: wy - topo  # noqa: E731
    # Enfeites atrás das plataformas: capim, xique-xique, pedras, caveira.
    for x in range(0, LARGURA_FASE, 9):
        if rng.random() < 0.55:
            c = capim(semente=x, seco=True)
            colar(t, c, x + rng.integers(-3, 3), y(CHAO) - c.h + 1)
    # Chão de terra batida; no leito do rio, lama seca rachada.
    import fase1_extra as ext
    t.colar(chao(LARGURA_FASE, 26, semente=3), 0, y(CHAO) - 2)
    t.colar(ext.chao_rachado(4636 - 3972, 26, semente=8), 3972, y(CHAO) - 2)
    yc = y(CHAO) - 1  # linha do chão na camada
    for x in (70, 205, 640, 1010, 1470, 1930, 2420, 2700, 2900, 3050, 3870, 4760, 5160, 5700):
        assentar(t, xiquexique(semente=x), x, yc)
    for k, x in enumerate((120, 380, 690, 1050, 1520, 1990, 2470, 2610, 2850, 3000, 3640, 4100, 4520, 5350, 5750)):
        assentar(t, pedra(int(rng.integers(12, 26)), int(rng.integers(8, 14)), semente=k + 20), x, yc, afundar=2)
    assentar(t, cranio_boi(), 1880, yc)
    assentar(t, cranio_boi(), 2540, yc)
    # Forquilhas secas (refém pendurado no galho), buracos e fogueiras.
    for fx, falt in FASE["forquilhas"]:
        assentar(t, forquilha(falt, semente=fx), fx, yc)
    for bx_ in FASE["buracos"]:
        bu = buraco()
        colar(t, bu, bx_ - bu.w / 2, yc - bu.h + 3)
    for gx_, _ in FASE["fogueiras"]:
        fg = fogueira()
        assentar(t, fg, gx_ - fg.w / 2, yc)
    # Objetos miúdos do sertão espalhados pelo chão.
    for x, peca in ((300, pote_barro(1)), (318, pote_barro(2, 11)), (860 - 40, pilao()), (1545, carroca_quebrada()),
                    (1720, pote_barro(3)), (1910, roda_carroca(8)), (2080, pote_barro(4, 12)), (2450, pilao()),
                    (2500, carroca_quebrada()), (180, cerca_farpada(70, 1)), (1950, cerca_farpada(100, 2))):
        assentar(t, peca, x, yc)
    # Lajedos e barranco (sólidos).
    for (sx, sy, sw, sh, *_), sem in zip([FASE["solidos"][k] for k in (1, 3, 4, 5, 6, 8, 10, 12, 13, 15, 16)], range(11)):
        lj = lajedo(sw + 4, CHAO - sy + 6, semente=40 + sem)
        sombra_contato(t, sx + sw / 2, yc + 1, sw * 1.15, 3.5)
        colar(t, lj, sx - 2, y(sy) - 2)
    # Trincheira de sacos de areia.
    sx, sy, sw, sh = FASE["solidos"][2]
    sa = sacos_areia(4, 3)
    assentar(t, sa, sx - 3, yc, afundar=3)
    # Giraus: tábuas sobre forquilhas.
    for k in (7, 9, 11):
        gx, gy, gw = FASE["solidos"][k][:3]
        for px in (gx + 2, gx + gw - 5):
            m = t.capsula(px + 1, y(gy) + 3, px + 1, y(CHAO), 1.5, 1.6)
            t.volume(m, MADEIRA, achatado=1, suave=0.4, ambiente=0.2)
        tab = tabuas(gw, 5, vertical=True, semente=gx)
        tab.contorno("sombra")
        colar(t, tab, gx, y(gy))
    # Cerca no fim do primeiro trecho.
    assentar(t, cerca_farpada(90, 3), 2860, yc)
    # ---- Vila de taipa: casas e capela (os soldados saem pelas portas), cruzeiro.
    assentar(t, casa_taipa(130, 84, semente=21, quebrada=False), 3060, yc + 1)
    assentar(t, ext.capela(96, 112, semente=3), 3420, yc + 1)
    assentar(t, ext.cruzeiro(), 3590, yc)
    assentar(t, casa_taipa(110, 72, semente=22), 3680, yc + 1)
    for x, peca in ((3200 - 30, pote_barro(7)), (3400, cabacas()), (3800 + 40, pilao()), (3560, pote_barro(8, 12))):
        assentar(t, peca, x, yc)
    # ---- Leito de rio seco: canoa velha encalhada, ossada, ponte com corrimão.
    assentar(t, ext.canoa(), 4170, yc, afundar=3)
    assentar(t, cranio_boi(), 4390, yc)
    pt = ext.ponte(4580 - 4024, 48, semente=2)
    colar(t, pt, 4024, y(146))
    colar(t, ext.corrimao(4580 - 4024), 4024, y(146) - 12)
    # ---- Acampamento da Volante: barracas, torre de vigia, mastro, munição.
    assentar(t, ext.barraca(84, 44, semente=1), 4740, yc + 1)
    assentar(t, ext.caixas_municao(3, 1), 4862, yc)
    sa2 = sacos_areia(4, 3)
    for sx_ in (4900, 5400):
        assentar(t, sa2, sx_ - 3, yc, afundar=3)
    tv = ext.torre_vigia(98, 40)
    colar(t, tv, 5030, y(CHAO) - tv.h + 1)
    assentar(t, ext.barraca(84, 44, semente=2), 5180, yc + 1)
    assentar(t, ext.mastro(110), 5330, yc)
    assentar(t, ext.caixas_municao(2, 2), 5470, yc)
    return t, topo


def camada_perto():
    """Atrás do plano do jogo (anda a 0,75 da câmera): casa de taipa, árvores
    grandes, mandacarus, cerca do curral, cata-vento e pedras grandes."""
    fator = 0.75
    W = int(LARGURA_FASE * fator + 548)
    alt = 112
    base = alt - 2
    t = Tela(W, alt)
    rng = np.random.default_rng(2)
    lx = lambda wx: int(wx * fator)  # noqa: E731
    pecas = []
    import fase1_extra as ext
    import veiculos as vc
    for k, wx in enumerate((20, 330, 560, 1000, 1500, 2050, 2400, 2700, 3000, 3900, 5600)):
        pecas.append((lx(wx), arvore(int(rng.integers(64, 84)), semente=k + 100)))
    for k, wx in enumerate((150, 460, 880, 1240, 1880, 2250, 2600, 2950, 3820, 4720, 5500)):
        pecas.append((lx(wx), mandacaru(int(rng.integers(36, 56)), semente=k + 200, bracos=int(rng.integers(1, 4)))))
    for k, wx in enumerate((270, 1120, 2150)):
        pecas.append((lx(wx), pedra(int(rng.integers(34, 52)), int(rng.integers(20, 30)), semente=k + 300)))
    pecas.append((lx(700), casa_taipa(124, 86, semente=5)))
    pecas.append((lx(700) + 128, pote_barro(5)))
    pecas.append((lx(700) - 14, pote_barro(6, 12)))
    pecas.append((lx(1480), cerca(110, semente=9)))
    pecas.append((lx(1590), cata_vento(78)))
    pecas.append((lx(2460), casa_taipa(100, 70, semente=8)))
    # Vila: mais casas atrás, uma ao lado da outra.
    for k, (wx, w_, h_) in enumerate(((3150, 96, 66), (3300, 80, 58), (3560, 104, 70), (3760, 88, 60))):
        pecas.append((lx(wx), casa_taipa(w_, h_, semente=40 + k, quebrada=k % 2 == 1)))
    # Rio seco: carnaúbas na beira.
    for k, wx in enumerate((3980, 4080, 4230, 4380, 4520, 4640)):
        pecas.append((lx(wx), ext.carnauba(int(rng.integers(70, 96)), semente=k + 60)))
    # Acampamento: barracas enfileiradas e um caminhão parado.
    for k, wx in enumerate((4800, 4960, 5260, 5450)):
        pecas.append((lx(wx), ext.barraca(70, 38, semente=k + 10, aberta=k % 2 == 0)))
    pecas.append((lx(5120), vc.caminhao(0)))
    for x, p in sorted(pecas, key=lambda e: -e[1].h):
        colar(t, p, x, base - p.h + 2)
    return t, fator


def camada_meio():
    """Longe (anda a 0,45 da câmera): morros baixos com caatinga miúda e uma casinha.
    (O disco que cai no fim passa atrás dela, animado no jogo.)"""
    fator = 0.45
    W = int(LARGURA_FASE * fator + 548)
    alt = 64
    t = Tela(W, alt)
    rng = np.random.default_rng(3)
    # Morros: faixa ondulada com volume suave.
    n = ruido(1, W, 30, 5)[0]
    alto = (alt - 26 + n * 6).astype(int)
    morro = t.yy >= alto[np.newaxis, :].repeat(alt, 0)
    t.volume(morro, ["azul_sombra", "terra", "terra_media", "barro", "areia_media", "areia"], achatado=6,
             suave=3, ambiente=0.35, textura=0.2, semente=2, linha=False)
    # Caatinga miúda e espalhada: arbustos em tufos, algumas árvores secas sem folha.
    x = 0
    while x < W:
        h = int(rng.integers(10, 26))
        seca = rng.random() < 0.35
        a = arvore(h, semente=int(x), folhas=not seca)
        if not seca:
            # Folhagem mais acinzentada, de seca, vista de longe.
            troca = {IDX["mandacaru_luz"]: IDX["areia_media"], IDX["mandacaru"]: IDX["caatinga_media"],
                     IDX["caatinga"]: IDX["caatinga_media"]}
            for de, para in troca.items():
                a.px[a.px == de] = para
        colar(t, a, x, alto[min(W - 1, x)] - a.h + 4)
        x += int(rng.integers(6, 30))
    casinha = casa_taipa(40, 30, semente=12, quebrada=False)
    colar(t, casinha, int(900 * fator), alto[int(900 * fator)] - 26)
    # A vila vista de longe: casinhas juntas no morro.
    for k, wx in enumerate((3200, 3260, 3330, 3420, 3500)):
        c = casa_taipa(int(rng.integers(26, 40)), int(rng.integers(20, 30)), semente=70 + k, quebrada=False)
        xx = int(wx * fator)
        colar(t, c, xx, alto[min(W - 1, xx)] - c.h + 5)
    return t, fator


def camada_frente():
    """Na frente do Lampião (anda a 1,1 da câmera): tufos e pedras escuras,
    poucos e espalhados, para dar profundidade sem atrapalhar."""
    fator = 1.1
    W = int(LARGURA_FASE * fator + 548)
    alt = 22
    t = Tela(W, alt)
    rng = np.random.default_rng(4)
    escuro = ["preto", "sombra", "sombra_media", "caatinga_esc", "terra_escura"]
    x = 200
    while x < W - 40:
        if rng.random() < 0.5:
            c = capim(22, semente=int(x))
            c.px[c.px != VAZIO] = IDX["sombra"]
            colar(t, c, x, alt - c.h)
            c2 = capim(18, semente=int(x) + 1)
            c2.px[c2.px != VAZIO] = IDX["caatinga_esc"]
            colar(t, c2, x + 6, alt - c2.h)
        else:
            p = pedra(int(rng.integers(16, 30)), int(rng.integers(8, 14)), semente=int(x), musgo=False)
            p.px[p.px != VAZIO] = np.array([IDX[c] for c in escuro])[np.clip((p.px[p.px != VAZIO] % 5), 0, 4)]
            colar(t, p, x, alt - p.h + 3)
        x += int(rng.integers(260, 520))
    return t, fator


def exportar(saida, raiz):
    """Grava as camadas da fase 1 em assets/sprites e os dados em assets/fases/fase1.json."""
    import json
    jogo, topo = camada_jogo()
    perto, fp = camada_perto()
    meio, fm = camada_meio()
    frente, ff = camada_frente()
    # Cada camada vai em pedaços de até 2048 px (o iPhone não aceita textura larga demais).
    pedacos = {}
    for nome, c in (("f1_jogo", jogo), ("f1_perto", perto), ("f1_meio", meio), ("f1_frente", frente)):
        im = c.imagem()
        n = (im.width + PEDACO - 1) // PEDACO
        for k in range(n):
            im.crop((k * PEDACO, 0, min(im.width, (k + 1) * PEDACO), im.height)).save(saida / f"{nome}_{k}.png", optimize=True)
        velho = saida / f"{nome}.png"
        if velho.exists():
            velho.unlink()
        pedacos[nome] = n
    (raiz / "src/fase1_pedacos.js").write_text(
        "// Gerado por tools/arte/fase1.py: quantos pedaços (de " + str(PEDACO) + " px) tem cada camada da fase 1.\n"
        "export const PEDACO = " + str(PEDACO) + ";\nexport const PEDACOS = " + json.dumps(pedacos) + ";\n")
    dados = dict(FASE)
    dados["camadas"] = {
        "jogo": {"y": topo, "fator": 1}, "perto": {"base": 194, "fator": fp},
        "meio": {"base": 192, "fator": fm}, "frente": {"base": 216, "fator": ff},
    }
    pasta = raiz / "assets/fases"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "fase1.json").write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
