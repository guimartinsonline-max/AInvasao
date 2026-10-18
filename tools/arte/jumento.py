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
from motor import Tela  # noqa: E402

PELO = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]
PELO_CLARO = ["cinza_medio", "cinza_luz", "cinza_claro", "branco"]
FERRO = ["preto", "sombra", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza"]
COURO = ["couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz"]
CASCO = ["preto", "sombra", "sombra_media"]

W, H = 72, 60
CHAO = H - 1


def pata(t, x, y, dx, dy, atras=False):
    """Pata fina com joelho e casco, do quadril (x, y) até o chão deslocado."""
    joelho = (x + dx * 0.5, y + (CHAO - y) * 0.55 + dy * 0.5)
    pe = (x + dx, CHAO - 1 + dy)
    m = t.capsula(x, y, joelho[0], joelho[1], 2.6, 1.8) | t.capsula(joelho[0], joelho[1], pe[0], pe[1] - 1, 1.8, 1.5)
    t.volume(m, PELO, achatado=1.2, suave=0.4, ambiente=0.15 if atras else 0.3, deslocar=-0.15 if atras else 0)
    t.volume(t.elipse(pe[0] + 0.5, pe[1], 2.2, 1.4), CASCO, achatado=1, suave=0.2)


def jumento(quadro=0):
    t = Tela(W, H)
    pelado = quadro in (6, 7)
    pulo = quadro == 5
    passo = {1: 0, 2: 1, 3: 2, 4: 3, 6: 0, 7: 2}.get(quadro)
    y0 = 4 + (-3 if pulo else (-1 if passo in (1, 3) else 0))  # 4 px de folga em cima para as orelhas
    # Rabo com tufo, atrás de tudo.
    t.volume(t.capsula(13, 26 + y0, 6, 38 + y0, 1.4, 1.0), PELO, achatado=1, suave=0.3)
    t.volume(t.elipse(6, 40 + y0, 2.2, 3.4), ["preto", "sombra", "cinza_escuro"], achatado=1, suave=0.3)
    # Patas de trás (mais escuras) e da frente, conforme o passo do trote.
    trote = [(-5, 4), (0, 0), (5, -4), (0, 0)]
    if pulo:
        pernas = [(-6, -6), (6, -8)]
    elif passo is None:
        pernas = [(-1, 1), (1, -1)]
    else:
        pernas = trote[passo]
        pernas = [(pernas[0], 0), (pernas[1], 0)]
    for (hx, dx), atras in (((17, pernas[0][0]), True), ((50, pernas[1][0]), True)):
        pata(t, hx + 3, 36 + y0, dx * -1, pernas[0][1] if hx < 30 else pernas[1][1], atras=atras)
    # Corpo (barriga redonda) e pescoço.
    corpo = t.elipse(33, 31 + y0, 20, 10)
    t.volume(corpo, PELO, achatado=4, suave=1.2, ambiente=0.3, textura=0.15, semente=2)
    t.volume(t.elipse(34, 37 + y0, 14, 4) & corpo, PELO_CLARO, achatado=1.5, suave=0.6, ambiente=0.2)  # barriga clara
    pescoco = t.poligono([(46, 25 + y0), (54, 13 + y0), (61, 15 + y0), (55, 30 + y0)])
    t.volume(pescoco, PELO, achatado=3, suave=0.8, ambiente=0.3, textura=0.15, semente=3)
    t.linha(47, 24 + y0, 53, 14 + y0, "preto")  # crina curta
    t.linha(48, 24 + y0, 54, 14 + y0, "sombra")
    # Cabeça comprida, focinho branco, orelhonas.
    cab = t.capsula(57, 14 + y0, 67, 21 + y0, 5, 4)
    t.volume(cab, PELO, achatado=2.5, suave=0.7, ambiente=0.3)
    focinho = t.elipse(67, 21 + y0, 4.2, 3.6)
    t.volume(focinho, PELO_CLARO, achatado=1.5, suave=0.5, ambiente=0.35)
    t.ponto(69, 20 + y0, "preto")  # venta
    t.linha(65, 24 + y0, 69, 23.5 + y0, "sombra")  # boca
    for k, (bx, ang) in enumerate(((55, -0.35), (58, 0.05))):
        orelha = t.elipse(bx + math.sin(ang) * 6, 5 + y0, 2.2, 6.5, ang=ang)
        t.volume(orelha, PELO, achatado=1.5, suave=0.4, ambiente=0.25 + 0.1 * k)
        t.chapado(t.elipse(bx + math.sin(ang) * 6 + 0.5, 5.5 + y0, 0.9, 4.5, ang=ang), "rosa_poeira")
    t.chapado(t.elipse(61.5, 15 + y0, 1.8, 1.8), "branco")
    t.ponto(62, 15 + y0, "preto")
    t.linha(59, 13 + y0, 63, 13.5 + y0, "sombra")  # sobrancelha brava
    if not pelado:
        # Chapa da cabeça (testeira) com rebites, deixando olho e orelhas de fora.
        test = t.poligono([(56, 10 + y0), (66, 15 + y0), (69, 18 + y0), (64, 19 + y0), (57, 16 + y0)]) & ~t.elipse(61.5, 15 + y0, 2.3, 2.3)
        t.volume(test, FERRO, achatado=1.5, suave=0.4, ambiente=0.35, brilho=1.2)
        for (x, y) in ((58, 12), (65, 16)):
            t.ponto(x, y + y0, "cinza_claro")
        # Chapas no pescoço e no corpo, presas com correia de couro.
        gola = t.poligono([(48, 22 + y0), (55, 12 + y0), (58, 16 + y0), (55, 28 + y0)])
        t.volume(gola, FERRO, achatado=2, suave=0.5, ambiente=0.3, brilho=1.1)
        manta = t.elipse(31, 29 + y0, 18, 8) & (t.yy < 37 + y0)
        t.volume(manta, FERRO, achatado=3, suave=0.8, ambiente=0.3, textura=0.1, semente=5, brilho=1.15)
        for x in range(17, 47, 7):
            t.linha(x, 22 + y0, x - 1, 36 + y0, "sombra")  # emendas das chapas
            for y in (25, 33):
                t.ponto(x + 2, y + y0, "cinza_claro")
        t.volume(t.retangulo(14, 35 + y0, 34, 2), COURO, achatado=1, suave=0.3)  # correia
        t.ponto(31, 35 + y0, "amarelo_fogo")  # fivela
        # Sela de couro e o suporte da metralhadora na frente dela.
        sela = t.elipse(31, 21 + y0, 9, 3.5) & (t.yy < 23 + y0)
        t.volume(sela, COURO, achatado=1.5, suave=0.5, ambiente=0.3)
        t.volume(t.retangulo(41, 13 + y0, 3, 9), FERRO, achatado=1, suave=0.3)
        t.volume(t.elipse(42.5, 13 + y0, 3, 2), FERRO, achatado=1, suave=0.3)
        # Caixa de munição pendurada.
        t.volume(t.retangulo(20, 27 + y0, 9, 7), ["sombra", "caatinga_esc", "caatinga_media", "caatinga"], achatado=1.5,
                 suave=0.4)
        t.chapado(t.retangulo(22, 29 + y0, 5, 1), "amarelo_fogo")
    else:
        # Sem blindagem: só a manta rasgada e o olho arregalado de susto.
        t.chapado(t.elipse(61.5, 15 + y0, 2.3, 2.3), "branco")
        t.ponto(62, 14 + y0, "preto")
        t.volume(t.elipse(31, 24 + y0, 8, 2.5) & (t.yy < 25 + y0), ["vermelho_esc", "vermelho_medio", "vermelho"],
                 achatado=1, suave=0.3)
    # Patas da frente por cima do corpo (a de trás de cada par já foi desenhada).
    for hx, dx in ((20, pernas[1][0]), (47, pernas[0][0])):
        pata(t, hx, 36 + y0, dx, pernas[1][1] if hx < 30 else pernas[0][1])
    t.contorno("sombra")
    return t


def metralhadora():
    """Metralhadora giratória do jumento: cano com camisa furada, pivô à esquerda."""
    t = Tela(28, 9)
    t.volume(t.retangulo(0, 2, 9, 5), ["preto", "sombra", "cinza_escuro", "cinza_medio"], achatado=1, suave=0.3)
    t.volume(t.retangulo(8, 2.5, 15, 4), ["sombra", "caatinga_esc", "caatinga_media", "caatinga"], achatado=1, suave=0.3)
    for x in range(10, 22, 3):
        t.ponto(x, 4, "preto")
    t.volume(t.retangulo(22, 3, 6, 3), ["sombra", "cinza_escuro", "cinza_medio", "cinza"], achatado=1, suave=0.3)
    t.volume(t.retangulo(3, 0, 4, 2.5), ["sombra", "cinza_escuro", "cinza_medio"], achatado=1, suave=0.2)  # carregador
    t.contorno("sombra")
    return t


QUADROS = [jumento(q) for q in range(8)]
