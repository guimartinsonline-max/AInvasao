"""Jumento blindado: o "tanque" do Lampião (como o Metal Slug do Metal Slug).
Jumento cinzento de focinho branco e orelhas grandes, com chapas de ferro
rebitadas no corpo e na cabeça, sela de couro e o suporte da metralhadora.
O Lampião (só o tronco) e a metralhadora são sprites à parte no jogo.

Quadros (virado para a direita): 0 parado, 1-4 trote, 5 pulo (patas encolhidas),
6-7 sem a blindagem correndo assustado (quando a blindagem estoura).
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela, IDX  # noqa: E402
from sombreado import vol as _vol, cel as _cel  # noqa: E402

PELO = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]
PELO_ESC = ["preto", "sombra", "cinza_escuro", "cinza_medio", "cinza"]
FOCINHO = ["terra", "areia_media", "areia", "areia_luz", "areia_clara"]
PELO_CLARO = ["cinza_medio", "cinza_luz", "cinza_claro", "branco"]
FERRO = ["preto", "sombra", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza"]
COURO = ["couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz"]
CASCO = ["preto", "sombra", "sombra_media"]

W, H = 72, 60
ESC_PELO = {IDX[a]: IDX[b] for a, b in (("cinza_luz", "cinza"), ("cinza", "cinza_medio"), ("cinza_medio", "cinza_escuro"),
                                          ("cinza_escuro", "sombra"))}
CHAO = H - 1


def pata(t, x, y, dx, dy, atras=False, joelheira=False):
    """Pata de jegue: coxa grossa, joelho marcado, tufo de pelo no boleto e
    casco escuro com ferradura brilhando."""
    joelho = (x + dx * 0.5, y + (CHAO - y) * 0.5 + dy * 0.5)
    pe = (x + dx, CHAO - 2 + dy)
    coxa = t.capsula(x, y, joelho[0], joelho[1], 3.4, 2.0)
    canela = t.capsula(joelho[0], joelho[1], pe[0], pe[1] - 1, 1.7, 1.4)
    rampa = PELO_ESC if atras else PELO
    _vol(t, coxa | canela, rampa, achatado=1.6, suave=0.5, ambiente=0.25)
    _vol(t, t.elipse(joelho[0], joelho[1], 2.4, 1.8), rampa, achatado=1, suave=0.3, ambiente=0.35)
    # Tufo de pelo claro em cima do casco.
    _vol(t, t.elipse(pe[0] - 0.2, pe[1] - 1.5, 2.6, 1.6), PELO_CLARO, achatado=1, suave=0.3, ambiente=0.2)
    casco = t.poligono([(pe[0] - 2.4, pe[1] - 0.8), (pe[0] + 2.2, pe[1] - 0.8), (pe[0] + 3.0, pe[1] + 1.6),
                        (pe[0] - 2.6, pe[1] + 1.6)])
    _vol(t, casco, CASCO, achatado=1, suave=0.2, ambiente=0.4)
    t.linha(pe[0] - 2.5, pe[1] + 1.6, pe[0] + 2.8, pe[1] + 1.6, "cinza_claro")  # ferradura
    if joelheira and not atras:
        jp = t.elipse(joelho[0] + 0.6, joelho[1], 2.8, 2.4)
        _vol(t, jp, FERRO, achatado=1.2, suave=0.3, ambiente=0.35, brilho=1.2)
        t.ponto(joelho[0], joelho[1] - 1, "branco")


def pelos(t, mascara, semente=0, passo=3):
    """Riscos curtos de pelo (escuros, inclinados) para tirar o liso de borracha."""
    rng = np.random.default_rng(semente)
    ys, xs = np.where(mascara)
    for y, x in zip(ys, xs):
        if (x + y * 2) % (passo * 3) == 0 and rng.random() < 0.55:
            for k in range(2):
                if 0 <= y + k < t.h and 0 <= x - k < t.w and mascara[y + k, x - k]:
                    t.px[y + k, x - k] = ESC_PELO.get(int(t.px[y + k, x - k]), t.px[y + k, x - k])


def jumento(quadro=0):
    t = Tela(W, H)
    pelado = quadro in (6, 7)
    pulo = quadro == 5
    passo = {1: 0, 2: 1, 3: 2, 4: 3, 6: 0, 7: 2}.get(quadro)
    y0 = 4 + (-3 if pulo else (-1 if passo in (1, 3) else 0))
    # Rabo de corda com tufo grande, atrás de tudo (balança no trote).
    ponta = 3 + (2 if passo in (1, 3) else 0) + (-3 if pulo else 0)
    _vol(t, t.capsula(14, 25 + y0, 7, 34 + y0 + ponta * 0.3, 1.5, 1.1), PELO, achatado=1, suave=0.3)
    tufo = t.elipse(6, 38 + y0 + ponta * 0.3, 2.8, 4.2, ang=0.3)
    _vol(t, tufo, ["preto", "sombra", "cinza_escuro", "cinza_medio"], achatado=1.2, suave=0.3)
    # Patas de trás (do outro lado do corpo, mais escuras).
    trote = [(-5, 4), (0, 0), (5, -4), (0, 0)]
    if pulo:
        pernas = [(-7, -7), (7, -9)]
    elif passo is None:
        pernas = [(-1, 1), (1, -1)]
    else:
        pernas = [(trote[passo][0], 0), (trote[passo][1], 0)]
    pata(t, 21, 35 + y0, -pernas[0][0], pernas[0][1], atras=True)
    pata(t, 50, 35 + y0, -pernas[1][0], pernas[1][1], atras=True)
    # Corpo barrigudo, barriga clara e pescoço grosso.
    corpo = t.elipse(33, 29 + y0, 20, 11)
    _vol(t, corpo, PELO, achatado=5, suave=1.3, ambiente=0.3)
    barriga = t.elipse(33, 37 + y0, 15, 4.5) & corpo
    _vol(t, barriga, PELO_CLARO, achatado=1.8, suave=0.6, ambiente=0.25)
    pescoco = t.poligono([(44, 26 + y0), (51, 13 + y0), (60, 14 + y0), (57, 31 + y0)])
    _vol(t, pescoco, PELO, achatado=3.5, suave=0.9, ambiente=0.32)
    pelos(t, corpo & ~barriga, 2)
    pelos(t, pescoco, 3)
    # Crina espetada e escura, do cocuruto até a cernelha.
    for k in range(7):
        bx = 45.5 + k * 1.3
        by = 24 + y0 - k * 1.7
        t.linha(bx, by, bx - 1.8, by - 2.6 - (k % 2), "preto")
        t.ponto(bx + 0.6, by - 0.5, "cinza_escuro")
    # Cabeçona caricata: comprida, focinho creme enorme, dentuço, ventas grandes.
    cab = t.capsula(55, 15 + y0, 66, 21 + y0, 6, 5)
    _vol(t, cab, PELO, achatado=3, suave=0.8, ambiente=0.32)
    focinho = t.elipse(67, 22 + y0, 5.4, 4.6)
    _vol(t, focinho, FOCINHO, achatado=2, suave=0.6, ambiente=0.35)
    t.chapado(t.elipse(69.5, 20.5 + y0, 1.2, 1.5), "sombra")  # venta
    t.ponto(69, 20 + y0, "preto")
    if pelado:
        # Boca aberta zurrando de medo.
        t.chapado(t.elipse(66, 25.5 + y0, 3.4, 1.8), "preto")
        t.chapado(t.retangulo(64, 24 + y0, 4, 1), "branco")
    else:
        # Sorriso dentuço de quem gosta de briga.
        t.linha(62, 24.5 + y0, 70, 23.5 + y0, "preto")
        t.chapado(t.retangulo(66, 24.5 + y0, 3, 2), "branco")
        t.ponto(67, 25 + y0, "cinza_luz")
    # Orelhonas com ponta preta e dentro rosado (uma de cada lado).
    for k, (bx, ang) in enumerate(((54, -0.45), (58, 0.0))):
        cx = bx + math.sin(ang) * 6
        orelha = t.elipse(cx, 5 + y0, 2.6, 7, ang=ang)
        _vol(t, orelha, PELO if k else PELO_ESC, achatado=1.6, suave=0.4, ambiente=0.3)
        t.chapado(t.elipse(cx + 0.5, 6 + y0, 1.1, 4.8, ang=ang) & orelha, "rosa_poeira")
        t.chapado(t.elipse(cx + math.sin(ang) * 5, 0.5 + y0, 1.8, 1.6) & orelha, "preto")
    # Olho grande, sobrancelha brava (ou arregalado sem blindagem).
    t.chapado(t.elipse(61.5, 15 + y0, 2.4, 2.2), "branco")
    t.chapado(t.elipse(62.3, 15.2 + y0, 1.0, 1.3), "preto")
    t.ponto(62, 14 + y0, "branco")
    if not pelado:
        t.linha(58.5, 12.5 + y0, 63.5, 13.5 + y0, "preto")
    if not pelado:
        # Testeira de ferro com a estrela do cangaço.
        test = t.poligono([(55, 9 + y0), (64, 13 + y0), (67, 17 + y0), (63, 18.5 + y0), (56, 15 + y0)]) \
            & ~t.elipse(61.5, 15 + y0, 2.6, 2.4)
        _vol(t, test, FERRO, achatado=1.5, suave=0.4, ambiente=0.35, brilho=1.25)
        t.ponto(58, 12 + y0, "amarelo_claro")
        t.ponto(57, 12 + y0, "ouro_escuro")
        t.ponto(59, 12 + y0, "ouro_escuro")
        t.ponto(58, 11 + y0, "ouro_escuro")
        t.ponto(58, 13 + y0, "ouro_escuro")
        # Cabresto de couro com argola.
        t.linha(57, 19 + y0, 66, 17 + y0, "couro_escuro")
        t.ponto(64, 18 + y0, "amarelo_fogo")
        # Peitoral de couro cravejado de tachas de latão.
        peito = t.poligono([(46, 22 + y0), (55, 20 + y0), (58, 31 + y0), (50, 36 + y0), (45, 33 + y0)])
        _vol(t, peito, COURO, achatado=2, suave=0.5, ambiente=0.3)
        for (x, y) in ((49, 25), (53, 24), (51, 29), (55, 28), (48, 32), (53, 33)):
            t.ponto(x, y + y0, "amarelo_fogo")
            t.ponto(x + 1, y + 1 + y0, "couro_profundo")
        # Manta de sela bordada (losangos vermelho e amarelo, franja embaixo).
        manta = t.poligono([(17, 20 + y0), (44, 20 + y0), (45, 34 + y0), (16, 34 + y0)]) & corpo
        _vol(t, manta, ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"], achatado=2, suave=0.5,
                 ambiente=0.3)
        for x in range(19, 44, 5):
            for dx, dy in ((0, 0), (1, 1), (-1, 1), (0, 2)):
                t.ponto(x + dx, 26 + dy + y0, "amarelo_fogo")
            t.ponto(x, 27 + y0, "ouro_escuro")
        t.linha(16, 23 + y0, 45, 23 + y0, "amarelo_fogo")
        for x in range(17, 45, 2):
            t.linha(x, 34 + y0, x, 35.5 + y0, "ouro_escuro")
        # Chapas de ferro rebitadas por cima da manta (blindagem).
        for x0, x1 in ((19, 29), (30, 40)):
            ch = t.retangulo(x0, 28 + y0, x1 - x0, 5)
            _vol(t, ch, FERRO, achatado=1.4, suave=0.4, ambiente=0.35, brilho=1.15)
            t.linha(x0, 28 + y0, x1 - 1, 28 + y0, "cinza_luz")
            for x in (x0 + 1, x1 - 2):
                t.ponto(x, 30 + y0, "cinza_claro")
                t.ponto(x, 31 + y0, "sombra")
        # Sela de couro de arção alto.
        sela = t.elipse(31, 20 + y0, 10, 3.6) & (t.yy < 22 + y0)
        _vol(t, sela, COURO, achatado=1.6, suave=0.5, ambiente=0.32)
        _vol(t, t.elipse(40, 17.5 + y0, 2.2, 3), COURO, achatado=1, suave=0.3, ambiente=0.35)  # arção
        _vol(t, t.elipse(22, 18.5 + y0, 2, 2.4), COURO, achatado=1, suave=0.3)
        # Alforje pendurado atrás, com fivela, e a cabaça d'água.
        alf = t.retangulo(13, 24 + y0, 7, 9)
        _vol(t, alf, COURO, achatado=1.4, suave=0.4, ambiente=0.3)
        t.linha(13, 27 + y0, 19, 27 + y0, "couro_escuro")
        t.ponto(16, 29 + y0, "amarelo_fogo")
        cabaca = t.elipse(44, 37 + y0, 2.3, 2.8) | t.elipse(44, 34 + y0, 1.4, 1.4)
        _vol(t, cabaca, ["terra_escura", "terra", "barro", "areia_media", "areia"], achatado=1.2, suave=0.3,
                 ambiente=0.35)
        t.linha(41, 30 + y0, 44, 33 + y0, "couro_escuro")
        # Suporte da metralhadora na paleta do ombro (a arma vai baixa, como no camelo).
        _vol(t, t.retangulo(48, 27 + y0, 6, 4), FERRO, achatado=1, suave=0.3, ambiente=0.35)
        _vol(t, t.elipse(53, 29 + y0, 2.6, 2.6), FERRO, achatado=1, suave=0.3, ambiente=0.4, brilho=1.2)
        t.ponto(53, 29 + y0, "cinza_claro")
    else:
        # Sem blindagem: manta rasgada pendurada e o lombo de fora.
        rasgo = t.poligono([(22, 21 + y0), (40, 21 + y0), (38, 28 + y0), (33, 25 + y0), (27, 30 + y0), (23, 26 + y0)]) & corpo
        _vol(t, rasgo, ["vermelho_esc", "vermelho_medio", "vermelho"], achatado=1, suave=0.3)
        for y, x in ((28, 34), (27, 26)):
            t.ponto(x, y + y0, "amarelo_fogo")
        # Suor de medo.
        t.chapado(t.elipse(56, 8 + y0, 1, 1.4), "ceu_claro")
    # Patas da frente por cima do corpo.
    pata(t, 24, 35 + y0, pernas[1][0], pernas[1][1], joelheira=not pelado)
    pata(t, 47, 35 + y0, pernas[0][0], pernas[0][1], joelheira=not pelado)
    t.contorno("sombra")
    return t


def metralhadora():
    """Metralhadora de três canos (como a do camelo), presa baixa no ombro do jumento:
    culatra de ferro, punho de madeira, caixa de munição de latão, canos com
    braçadeiras e boca larga. Pivô à esquerda."""
    t = Tela(32, 12)
    _vol(t, t.retangulo(0, 3, 10, 7), FERRO, achatado=1.4, suave=0.3, ambiente=0.3, brilho=1.1)  # culatra
    _vol(t, t.retangulo(2, 0, 6, 3.5), ["ouro_escuro", "amarelo_fogo", "amarelo_claro"], achatado=1, suave=0.2)  # munição
    t.linha(2, 1, 7, 1, "couro")
    _vol(t, t.capsula(3, 9, 1, 11.5, 1.4, 1.2), COURO, achatado=1, suave=0.2)  # punho
    for k, y in enumerate((4.2, 6.2, 8.2)):
        _vol(t, t.retangulo(9, y - 0.9, 18, 1.8), ["preto", "sombra", "cinza_escuro", "cinza_medio", "cinza"][k:] or FERRO,
                 achatado=0.8, suave=0.2, ambiente=0.3)
    for x in (13, 20):
        _vol(t, t.retangulo(x, 2.6, 2, 7), FERRO, achatado=0.8, suave=0.2, ambiente=0.4, brilho=1.2)
    _vol(t, t.retangulo(26, 2.8, 5, 6.6), FERRO, achatado=1, suave=0.2, ambiente=0.35, brilho=1.2)  # boca
    t.chapado(t.retangulo(30, 4, 1, 4), "preto")
    t.linha(1, 3, 9, 3, "cinza_luz")
    t.contorno("sombra")
    return t


QUADROS = [jumento(q) for q in range(8)]
