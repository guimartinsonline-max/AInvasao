"""Chão largo (como no Metal Slug 4), aprovado em 22/10.

O chão vai do horizonte (y 198 na tela) até a borda de baixo. O cenário de fundo fica na
beira de trás (y 216 na tela); personagens, objetos e sólidos pisam no meio (y 264 na tela,
o y 194 do mundo de sempre). O chão é desenhado em faixas que andam em velocidades
diferentes (mais devagar no longe, mais rápido na frente), como o "line scroll" do Metal Slug.

Daqui saem:
- `textura_chao()`: a textura do chão (repete na horizontal), cortada em faixas no jogo;
- `faixas()`: a altura e a velocidade de cada faixa;
- `limpar_chao_jogo()`: tira o chão pintado do plano do jogo e deixa só a sombra das peças;
- `tirar_sobrepostos()`: tira árvore e casa do fundo que ficariam atrás das construções da rua;
- `pecas_fase1()`: as peças baixas em 2.5D (lajedo, girau, sacos, carroça) da fase 1.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

import caatinga_ms as cm
from caatinga_ms import Quadro, ruido, escurecer

TELA_H = 308
HZ = 198            # horizonte do chão na tela
FUNDO = 216         # beira de trás do chão: o pé do plano de trás (perto)
PE = 264            # onde se anda, na tela (o y 194 do mundo)
CHAO_MUNDO = 194
DESCE = 22          # a câmera desce 22 px em relação ao jeito antigo (y -70 em vez de -92)
FRENTE = 19         # as peças 2.5D apoiam a frente 19 px à frente da linha onde se anda
TEX_W = 1024
# Construções altas (casas, capela, cruzeiro) ficam recuadas: a frente delas apoia RECUO px
# atrás da linha onde se anda (nunca em cima dela), para não parecer que o Lampião anda colado.
RECUO = 22
FUNDO_MUNDO = CHAO_MUNDO - (PE - FUNDO)   # beira de trás do chão, no mundo (146)


def textura_chao(sem=12):
    """Chão de terra batida indo para trás: miúdo e enevoado no longe, graúdo na frente,
    pedrinhas diminuindo com a distância e a beira de baixo mais escura."""
    h = TELA_H - HZ
    q = Quadro(TEX_W, h)
    X, Y = q.xx, q.yy
    yb = h + 26
    d = np.clip(Y / yb, 0, 1)
    n = ruido(h, TEX_W, (0.6, 7), sem) * d + ruido(h, TEX_W, (0.4, 3), sem + 1) * (1 - d)
    lz = 0.58 + 0.08 * n - 0.06 * d + 0.03 * (1 - d)
    q.pinta(np.ones((h, TEX_W), bool), 'terra', np.clip(lz, 0, 0.999))
    rng = np.random.default_rng(sem)
    for _ in range(260):
        y = yb * rng.random() ** 0.7
        dd = y / yb
        x = rng.uniform(0, TEX_W)
        r = 0.6 + 2.6 * dd
        for xx in (x, x - TEX_W, x + TEX_W):          # a textura emenda nas pontas
            pe = ((X - xx) / r) ** 2 + ((Y - y) / (r * 0.5)) ** 2 < 1
            if pe.any():
                q.pinta(pe, 'terra', np.where(Y < y, 0.85, 0.4))
    # névoa: o longe clareia e perde contraste; perto do horizonte some no pé dos morros
    # (23/10: o fundo do chão na mesma cor da frente, só um pouco mais claro no horizonte)
    lon = d < 0.3
    k = (0.3 - d[lon]) / 0.3 * 0.12
    alvo = cm.RGB['longe'][-2].astype(float)
    q.img[lon] = cm.encaixar((q.img[lon] * (1 - k[:, None]) + alvo * k[:, None]).reshape(-1, 1, 3).astype(np.uint8)).reshape(-1, 3)
    for k_ in (14, 5):
        m = Y >= h - k_
        q.img[m] = escurecer(q.img[m], 1)
    out = q.rgba()
    # as 4 primeiras linhas misturam no fundo (sem linha dura no horizonte)
    for y in range(4):
        out[y, :, 3] = int(255 * (y + 1) / 5)
    return Image.fromarray(out, 'RGBA')


def faixas():
    """[(y na textura, altura, fator)]: faixas finas no longe, mais grossas na frente."""
    out = []
    y = 0
    h = TELA_H - HZ
    while y < h:
        ys = HZ + y
        alt = 3 if ys < 214 else 4 if ys < PE else 6
        alt = min(alt, h - y)
        meio = ys + alt / 2
        if meio <= PE:
            f = 0.62 + 0.38 * (meio - HZ) / (PE - HZ)
        else:
            f = 1 + 0.14 * (meio - PE) / (TELA_H - PE)
        out.append((y, alt, round(f, 3)))
        y += alt
    return out


def limpar_chao_jogo(im, topo_mundo, x_fim):
    """Plano do jogo: tira o chão pintado (até x_fim) e põe a sombra de contato de quem
    está apoiado nele (meio transparente, o chão de baixo aparece escurecido)."""
    a = np.array(im.convert('RGBA'))
    y0 = CHAO_MUNDO - 3 - topo_mundo                     # primeira linha só de chão (a beira clara sai junto)
    base = a[y0 - 2, :x_fim, 3] > 0                     # o que encosta no chão
    a[y0:, :x_fim, 3] = 0
    # sombra: elipse achatada embaixo de cada trecho apoiado
    rot, n = ndimage.label(base)
    sombra = np.zeros(a.shape[:2], float)
    yy, xx = np.mgrid[0:6, 0:x_fim]
    for sl in ndimage.find_objects(rot):
        x0, x1 = sl[0].start, sl[0].stop
        cx, rx = (x0 + x1) / 2 + 2, (x1 - x0) / 2 * 1.1 + 2
        e = ((xx - cx) / rx) ** 2 + ((yy - 1.5) / 3.2) ** 2
        sombra[y0:y0 + 6, :x_fim] = np.maximum(sombra[y0:y0 + 6, :x_fim], np.where(e < 1, np.where(e < 0.4, 0.5, 0.32), 0))
    m = sombra > 0
    a[m, :3] = (26, 16, 22)
    a[m, 3] = (sombra[m] * 255).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def tirar_sobrepostos(camada, fator, base_y, ocupado, morro=False, centro=274):
    """Tira do plano de fundo (inteira, com o tronco) cada árvore ou casa que, quando está no
    meio da tela, fica atrás de uma construção da rua (`ocupado`: colunas do mundo)."""
    a = np.array(camada.convert('RGBA'))
    al = a[..., 3] > 0
    if morro:
        topo = np.where(al.any(0), al.argmax(0), a.shape[0])
        perfil = ndimage.percentile_filter(topo, 85, 121)
        alto = al & (np.arange(a.shape[0])[:, None] < perfil[None, :] + 3)
    else:
        alto = al.copy()
        alto[base_y - 22:] = False
    rot, n = ndimage.label(alto)
    for k, sl in enumerate(ndimage.find_objects(rot), 1):
        xa, xb = sl[1].start, sl[1].stop
        cam = ((xa + xb) / 2 - centro) / fator
        wa, wb = int(xa - cam * fator + cam), int(xb - cam * fator + cam)
        wa, wb = max(0, wa), min(len(ocupado), wb)
        if wb <= wa or not ocupado[wa:wb].any():
            continue
        m = rot == k
        if not morro:
            # leva junto o tronco e o pé que descem até o chão
            col = np.zeros_like(al); col[:, xa:xb] = al[:, xa:xb]
            r2, _ = ndimage.label(col)
            ids = np.unique(r2[m]); ids = ids[ids > 0]
            m = m | (np.isin(r2, ids) & (np.arange(a.shape[0])[:, None] < base_y + 3))
        a[m, 3] = 0
    return Image.fromarray(a, 'RGBA')


def ocupacao(jogo, topo_mundo, casas, largura):
    """Colunas do mundo com construção alta na rua (paredes e telhados do plano do jogo e
    as casas da vila, que são objetos à parte)."""
    a = np.array(jogo.convert('RGBA'))[..., 3] > 0
    lim = CHAO_MUNDO - 34 - topo_mundo
    occ = np.zeros(largura, bool)
    occ[:a.shape[1]] = a[:lim].sum(0) > 6
    for x, w, h in casas:
        occ[x:x + w] = True
    return ndimage.binary_dilation(occ, np.ones(13))


# ---------------------------------------------------------------- peças 2.5D da fase 1
def pecas_fase1(F):
    """Lista [(Quadro, x, y_topo_mundo)] das peças baixas 2.5D da fase 1 (a frente apoiada
    FRENTE px à frente da linha onde se anda; o meio do tampo na altura do sólido)."""
    import pecas25 as p5
    fg = CHAO_MUNDO + FRENTE
    sol = F["solidos"]
    D = 19
    out = []

    def poe(q, x):
        out.append((q, int(x), fg - (q.h - 1)))

    # rochedos de arenito (do mais baixo para o mais alto: o alto fica na frente da emenda);
    # o meio do tampo na altura do sólido
    # (23/10, como a barreira do Metal Slug: tampo fino aceso e a frente descendo só até o
    # chão, apoiada nele com sombra; nada de laje gigante até a borda da tela)
    lajes = [(sol[k], 40 + k, 'cal') for k in (1, 3, 4, 5, 6, 10)] + [(sol[8], 48, 'terra')]
    DL = 12
    for (sx, sy, sw, *_), sem, rampa in sorted(lajes, key=lambda e: -e[0][1]):
        topo = int(round(sy - DL / 2))
        q, _ = p5.rochedo2(W=sw, D=DL, BAIXO=fg - topo - DL, sem=sem, rampa=rampa)
        out.append((q, int(sx - q.ox), topo))
    # trincheiras de sacos
    for sx, sy, sw, *_ in [s for s in sol if s[:2] in ([884, 176], [4290, 176])]:
        # pilha de frente no jeito do Metal Slug, um pouco à frente da linha onde se anda
        q, _ = p5.sacos3(W=sw + 8, ALT=36, sem=sx)
        out.append((q, int(sx - 9), CHAO_MUNDO + 8 - (q.h - 1)))
    # giraus (plataforma de um lado só: o meio do tampo na altura dela)
    for k in (7, 9, 11):
        gx, gy, gw = sol[k][:3]
        perna = int(round(fg - 5 - D / 2 - gy))
        q, _ = p5.girau(W=gw + 8, PERNA=perna, D=D, sem=gx, carga=k != 11)
        poe(q, gx - 4)
    # carros de boi largados (não são sólidos)
    # (23/10: foram para a beira de trás do chão, menores pela distância, atrás de todo mundo)
    for x in (1470, 2500):
        q, _ = p5.carroca(W=78, D=13, sem=x)
        out.append((q, int(x - 20), FUNDO_MUNDO + 14 - (q.h - 1), 4.6))
    return out
