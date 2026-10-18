"""Inimigos e refém caricatos no estilo Metal Slug: cabeça grande, nariz e
olhos exagerados, corpo atarracado e poses cômicas.

Desenhados com o motor (volume em faixas e contorno) e com o rosto ajustado
pixel a pixel. Gera tools/arte/pixel/volante.txt, xeremita.txt e refem.txt,
que continuam editáveis à mão.

Uso: python3 tools/arte/caricatos.py
Todos virados para a direita; o jogo espelha. Quadro 44x46, pé em y=45.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela, IDX, VAZIO  # noqa: E402
import pixel  # noqa: E402

W, H = 52, 46  # folga à direita para o cano e o clarão do tiro
CHAO = 45

PELE = ["pele_sombra", "pele_media", "pele", "pele_luz"]
PELE_CLARA = ["pele_media", "pele", "pele_luz", "pele_brilho"]
FARDA = ["caatinga_esc", "caatinga_media", "caatinga", "mandacaru"]
FARDA_ESC = ["sombra", "caatinga_esc", "caatinga_media", "caatinga"]
COURO = ["couro_profundo", "couro_escuro", "couro", "couro_medio"]
BOTA = ["preto", "couro_profundo", "couro_escuro", "couro"]
ACO = ["sombra", "cinza_escuro", "cinza", "cinza_claro"]
MADEIRA = ["couro_profundo", "couro", "couro_medio", "couro_luz"]
ALIEN = ["alien_profundo", "alien_medio", "alien", "alien_luz"]
ALIEN_ESC = ["sombra", "alien_profundo", "alien_esc", "alien_medio"]
LILAS = ["roxo_escuro", "roxo", "lilas", "lilas_claro"]
TRAPO = ["cinza", "cinza_luz", "cinza_claro", "branco"]
PALHA = ["terra", "areia_media", "areia", "areia_clara"]
BARBA = ["cinza", "cinza_luz", "cinza_claro", "branco"]
CORDA = ["terra_escura", "terra_media", "barro", "areia_luz"]


# ---------------------------------------------------------------- peças
def membro(t, a, b, c, r1, r2, rampa, deslocar=0):
    """Braço ou perna em dois segmentos (a-b-c)."""
    m = t.capsula(a[0], a[1], b[0], b[1], r1) | t.capsula(b[0], b[1], c[0], c[1], r2)
    t.cel(m, rampa, sombra=1, deslocar=deslocar)
    return m


def bota(t, x, y, comprido=4.2, deslocar=0):
    """Bota grandona com o bico para a frente; (x, y) é o calcanhar no chão."""
    m = t.elipse(x + comprido * 0.55, y - 1.6, comprido, 2.3) & (t.yy < y + 0.5)
    t.cel(m, BOTA, sombra=1, deslocar=deslocar)
    t.chapado(t.retangulo(x - 1, y - 0.5, comprido * 1.7, 1) & m, "preto")
    return m


def perna(t, quadril, joelho, pe, rampa, atras=False):
    d = -1 if atras else 0
    membro(t, quadril, joelho, (pe[0], pe[1] - 2), 2.6, 2.2, rampa, d)
    bota(t, pe[0] - 1, pe[1], deslocar=d)


def olho(t, x, y, tipo="normal", olhar=1):
    """Olho caricato: branco grande com a pupila. x, y = centro."""
    if tipo == "fechado":
        t.linha(x - 2, y, x + 2, y, "preto")
        return
    if tipo == "x":
        t.linha(x - 2, y - 2, x + 2, y + 2, "preto")
        t.linha(x - 2, y + 2, x + 2, y - 2, "preto")
        return
    rx, ry = (3.2, 3.4) if tipo == "esbugalhado" else (2.4, 2.2)
    t.chapado(t.elipse(x, y, rx, ry), "preto")
    t.chapado(t.elipse(x, y, rx - 0.9, ry - 0.9), "branco")
    if tipo == "esbugalhado":
        t.chapado(t.retangulo(x + olhar * 0.5 - 0.5, y - 0.5, 1, 1), "preto")
    elif tipo == "bravo":
        t.chapado(t.retangulo(x + olhar - 1, y - 0.5, 2, 2), "preto")
        t.chapado(t.retangulo(x - 3, y - 2.5, 6, 1.2), "preto")  # pálpebra caída
    else:
        t.chapado(t.retangulo(x + olhar - 1, y - 1, 2, 2), "preto")


def suor(t, x, y):
    t.chapado(t.elipse(x, y, 1, 1.6), "ceu_claro")
    t.ponto(int(x), int(y - 1), "branco")


# ================================================================ Volante
def volante(rosto="serio", pose="parado", passo=0, tipo="fuzil"):
    """Soldado da Volante: narigão, bigodão, barriga redonda. Variações (tipo):
    fuzil (quepe), granadeiro (capacete, dinamite), metralhador (capacete,
    metralhadora, mais gordo) e facao (sargento de quepe com faixa vermelha)."""
    t = Tela(W, H)
    pulo = 0
    if pose == "anda":
        ciclo = [(-3, 3), (0, 0), (3, -3), (0, 0)][passo]
        pulo = 1 if passo in (1, 3) else 0
        perna(t, (12, 35 + pulo), (12 + ciclo[1] * 0.5, 40), (11 + ciclo[1], CHAO), FARDA, atras=True)
    elif pose == "panico":
        perna(t, (12, 35), (9, 39), (6, CHAO), FARDA, atras=True)
    elif pose != "sem_pernas":
        perna(t, (12, 35), (11, 40), (9, CHAO), FARDA, atras=True)

    # Braço de trás (segura o fuzil por baixo ou balança no pânico).
    if pose == "panico":
        membro(t, (11, 24), (7, 18), (5, 12), 2.2, 2.0, FARDA, -1)
        t.cel(t.elipse(5, 11, 2.2, 2.2), PELE, sombra=1)
    else:
        membro(t, (12, 25), (15, 31), (22, 31), 2.2, 2.0, FARDA, -1)

    # Barriga redonda com cinto e cartucheira (o metralhador é mais gordo).
    if tipo in ("metralhador", "oficial"):
        corpo = t.elipse(15, 29.5, 8.8, 7.2) | t.retangulo(8, 24, 14, 8)
    else:
        corpo = t.elipse(15, 29.5, 7.5, 6.5) | t.retangulo(9, 24.5, 12, 8)
    t.cel(corpo, FARDA, sombra=2)
    t.chapado(t.capsula(9, 23, 21, 33, 0.9) & corpo, "couro")
    t.chapado(t.capsula(9, 22.5, 21, 32.5, 0.5) & corpo, "couro_medio")
    t.chapado(t.retangulo(7, 33, 17, 2) & t.elipse(15, 30, 9, 8), "couro_escuro")
    t.chapado(t.retangulo(19, 33, 2, 2), "amarelo_fogo")
    for x in (10, 13):
        t.chapado(t.retangulo(x, 30, 2, 3) & corpo, "couro")
    if tipo == "oficial":
        # Medalhas no peito e dragona dourada no ombro.
        for k, cor in enumerate(("vermelho", "ceu_medio", "amarelo_fogo")):
            t.chapado(t.retangulo(16 + k * 2.2, 25, 1.6, 1.5), cor)
            t.chapado(t.elipse(16.8 + k * 2.2, 27.5, 0.9, 0.9), "amarelo_claro")
        t.cel(t.elipse(12, 23.5, 3.2, 1.6), ["ouro_escuro", "amarelo_fogo", "amarelo_claro"], sombra=0)
    if tipo == "granadeiro":
        # Bananas de dinamite presas na cartucheira.
        for k in range(4):
            t.chapado(t.retangulo(10 + k * 2.6, 24.5 + k * 2.2, 1.6, 3), "vermelho")
            t.ponto(int(10 + k * 2.6), int(24.5 + k * 2.2), "amarelo_claro")

    if pose == "anda":
        ciclo = [(-3, 3), (0, 0), (3, -3), (0, 0)][passo]
        perna(t, (17, 35 + pulo), (18 + ciclo[0] * 0.5, 40), (17 + ciclo[0], CHAO), FARDA)
    elif pose == "panico":
        perna(t, (17, 35), (21, 38), (22, CHAO - 2), FARDA)
    elif pose != "sem_pernas":
        perna(t, (17, 35), (19, 40), (19, CHAO), FARDA)

    # Lança-rojão no ombro: o tubo passa por trás da cabeça, rente ao olho.
    if tipo == "rojao" and pose not in ("panico",):
        ty = 14.5 + pulo
        tubo = t.capsula(5, ty + 1, 35, ty, 2.3)
        t.cel(tubo, ["sombra", "caatinga_esc", "caatinga_media", "caatinga"], sombra=1)
        for bx_ in (9, 30):
            t.chapado(t.retangulo(bx_, ty - 2, 1.5, 4.5) & tubo, "sombra")
        t.chapado(t.elipse(35, ty, 1.2, 2.2), "sombra")
        if rosto != "grito":
            # Rojão carregado aparecendo na boca do tubo.
            t.cel(t.poligono([(35, ty - 1.8), (39.5, ty), (35, ty + 1.8)]), ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"], sombra=0)

    # Cabeça no tamanho da do Lampião (caricata, sem exagero).
    hy = 17 + pulo
    t.cel(t.elipse(10.5, hy + 1.5, 1.8, 2.4), PELE, sombra=1)  # orelha
    cabeca = t.elipse(17, hy, 7.6, 7.4) & (t.yy < hy + 7)
    t.cel(cabeca, PELE, sombra=2)
    # Barba por fazer no queixo.
    queixo = t.elipse(19.5, hy + 5, 6, 2.8) & cabeca & (t.yy > hy + 3)
    xadrez = ((t.xx.astype(int) + t.yy.astype(int)) % 2) == 0
    t.px[queixo & xadrez & (t.px != IDX["pele_luz"])] = IDX["pele_media"]
    t.chapado(t.elipse(20.5, hy + 2.5, 1.3, 0.9), "rosa_poeira")

    q = -2 if pose == "panico" else 0
    if tipo in ("granadeiro", "metralhador", "rojao"):
        # Capacete Adrian (usado pelo Exército nos anos 30): cúpula com crista e aba em volta.
        t.cel(t.elipse(17, hy - 3.5 + q, 10.5, 1.8), FARDA_ESC, sombra=1)
        t.cel(t.elipse(17, hy - 5 + q, 8, 5.5) & (t.yy < hy - 3.5 + q), FARDA_ESC, sombra=1)
        t.cel(t.capsula(12, hy - 9 + q, 21, hy - 10 + q, 0.9), FARDA, sombra=0)
        t.chapado(t.elipse(14, hy - 7 + q, 1.6, 1), "caatinga")
    else:
        # Quepe com aba (sobe de susto no pânico); o sargento do facão tem faixa vermelha.
        t.cel(t.poligono([(9.5, hy - 4 + q), (11, hy - 10 + q), (23, hy - 11 + q), (24.5, hy - 5 + q)]), FARDA_ESC, sombra=1)
        faixa = {"facao": "vermelho", "oficial": "amarelo_fogo"}.get(tipo, "caatinga_esc")
        t.chapado(t.retangulo(10, hy - 6 + q, 14.5, 1.6), faixa)
        if tipo == "oficial":
            # Quepe de oficial, mais alto, com cordão dourado.
            t.cel(t.poligono([(10, hy - 9 + q), (11, hy - 13 + q), (24, hy - 13 + q), (24.5, hy - 9 + q)]), FARDA_ESC, sombra=1)
            t.linha(11, hy - 5 + q, 24, hy - 5 + q, "amarelo_claro")
        t.cel(t.poligono([(20, hy - 5 + q), (27.5, hy - 4.5 + q), (27.5, hy - 3.2 + q), (20, hy - 3.2 + q)]), BOTA, sombra=0)
        t.chapado(t.retangulo(16, hy - 9 + q, 2, 2), "amarelo_fogo")

    # Rosto.
    ox, oy = 22, hy - 0.5
    if rosto == "panico":
        t.chapado(t.elipse(ox, oy, 2.6, 2.8), "preto")
        t.chapado(t.elipse(ox, oy, 1.7, 1.9), "branco")
        t.ponto(ox, int(oy), "preto")
        suor(t, 12, hy - 2)
        suor(t, 27, hy - 6)
        if tipo == "oficial":
            # Chorando: lágrimas escorrendo em bica.
            for dx in (-2, 2):
                t.linha(ox + dx, oy + 2, ox + dx * 1.5, hy + 10, "ceu_claro")
                t.ponto(ox + dx * 1.5, hy + 10, "branco")
    elif rosto == "morto":
        t.linha(ox - 1.5, oy - 1.5, ox + 1.5, oy + 1.5, "preto")
        t.linha(ox - 1.5, oy + 1.5, ox + 1.5, oy - 1.5, "preto")
    elif rosto in ("dorme", "ronca"):
        # Olho fechado, sobrancelha caída.
        t.linha(ox - 2, oy + 0.5, ox + 1.5, oy + 0.5, "preto")
        t.linha(19, hy - 2.5, 24, hy - 2, "couro_profundo")
    else:
        bravo = rosto in ("bravo", "grito")
        t.chapado(t.elipse(ox, oy, 2, 1.8), "preto")
        t.chapado(t.elipse(ox, oy, 1.2, 1.1), "branco")
        t.chapado(t.retangulo(ox, oy - 0.5, 1, 1.5), "preto")
        inclina = 1 if bravo else 0
        t.linha(19, hy - 3 - inclina, 24, hy - 3 + inclina, "couro_profundo")
    # Nariz grande, mas na medida.
    t.cel(t.elipse(26, hy + 1.5, 2.5, 2.2), PELE_CLARA, sombra=1)
    t.ponto(25, hy + 2, "pele_sombra")
    # Bigode.
    t.cel(t.poligono([(20, hy + 3.5), (27, hy + 3.5), (29, hy + 5.5), (26.5, hy + 5), (24, hy + 6), (21, hy + 5.5)]),
          ["couro_profundo", "couro_profundo", "couro_escuro", "couro"], sombra=1)
    # Boca.
    if rosto == "grito":
        t.chapado(t.elipse(23.5, hy + 7, 2.2, 1.4), "preto")
        t.chapado(t.retangulo(22, hy + 6, 3.5, 1), "branco")
    elif rosto == "panico":
        t.chapado(t.elipse(23, hy + 7.5, 2.4, 2.2), "preto")
        t.chapado(t.elipse(23, hy + 8.5, 1.4, 0.9), "vermelho")
    elif rosto == "morto":
        t.chapado(t.elipse(23.5, hy + 7, 1.6, 1.1), "preto")
        t.chapado(t.elipse(24.5, hy + 8.3, 1, 1.2), "vermelho")
    elif rosto == "ronca":
        t.chapado(t.elipse(23.5, hy + 7, 1.4, 1.4), "preto")
    else:
        t.linha(22, hy + 6.5, 24, hy + 6.5, "couro_profundo")

    # Braço da frente e a arma de cada tipo.
    recuo = -1 if rosto == "grito" else 0
    if pose == "panico":
        membro(t, (18, 24), (22, 18), (24, 11), 2.2, 2.0, FARDA)
        t.cel(t.elipse(24.5, 10, 2.2, 2.2), PELE, sombra=1)
    elif tipo == "oficial":
        if rosto == "grito":
            # Atira de pistola, braço esticado.
            membro(t, (18, 25), (23, 27), (28, 27), 2.3, 2.1, FARDA)
            t.cel(t.retangulo(28, 25.5, 6, 2), ACO, sombra=0)
            t.cel(t.retangulo(28, 26.5, 2, 3.5), MADEIRA, sombra=0)
            t.cel(t.elipse(28.5, 27, 2, 1.8), PELE, sombra=1)
        else:
            # Dá a ordem: espada erguida apontando para a frente ("AVANÇAR!").
            membro(t, (18, 25), (24, 26), (30, 22), 2.3, 2.0, FARDA)
            t.cel(t.capsula(31, 21, 42, 11, 0.9, 0.5), ["sombra", "cinza_escuro", "cinza_claro", "branco"], sombra=0)
            t.chapado(t.capsula(28.5, 22.5, 32.5, 19.5, 0.8), "amarelo_fogo")  # guarda dourada
            t.cel(t.elipse(30.5, 22, 2, 1.8), PELE, sombra=1)
    elif tipo == "rojao":
        # Mão da frente segurando o punho do tubo, logo abaixo dele.
        membro(t, (18, 25), (26, 27), (31, 18 + pulo), 2.3, 2.0, FARDA)
        t.cel(t.elipse(31.5, 17.5 + pulo, 2, 1.8), PELE, sombra=1)
        if rosto == "grito":
            # Disparo: fumaça saindo por trás do tubo.
            for k, (dx, r) in enumerate(((0, 3.5), (-3, 2.8), (-5, 2))):
                t.volume(t.elipse(3 + dx, 15.5 - k, r, r * 0.9), ["cinza_escuro", "cinza", "cinza_luz", "cinza_claro"],
                         achatado=1.5, suave=0.4, ambiente=0.35, linha=False)
    elif tipo == "metralhador":
        # Metralhadora pesada no quadril: camisa do cano furada e carregador em cima.
        t.cel(t.poligono([(9 + recuo, 27.5), (17 + recuo, 27.5), (17 + recuo, 31.5), (11 + recuo, 32)]), MADEIRA, sombra=1)
        t.cel(t.retangulo(17 + recuo, 27, 8, 4), ["sombra", "sombra_media", "cinza_escuro", "cinza_medio"], sombra=1)
        t.cel(t.retangulo(19 + recuo, 23.5, 3.5, 3.5), ["sombra", "sombra_media", "cinza_escuro", "cinza_medio"], sombra=0)
        t.cel(t.retangulo(25 + recuo, 27.5, 14, 2.6), ACO, sombra=0)
        for x in range(26, 38, 2):
            t.ponto(x + recuo, 28, "sombra")
        t.cel(t.retangulo(39 + recuo, 27, 2.5, 3.5), ["sombra", "sombra_media", "cinza_escuro", "cinza_medio"], sombra=0)
        membro(t, (18, 25), (21, 30), (26, 31), 2.3, 2.1, FARDA)
        t.cel(t.elipse(26.5, 31, 2, 1.8), PELE, sombra=1)
    elif tipo == "granadeiro":
        if rosto == "grito":
            # Braço lá em cima, jogando a dinamite com o pavio aceso.
            membro(t, (18, 24), (16, 17), (13, 11), 2.2, 2.0, FARDA)
            t.cel(t.elipse(13, 10, 2, 2), PELE, sombra=1)
            t.cel(t.capsula(10, 7, 15, 9, 1.2), ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"], sombra=0)
            t.linha(15, 9, 17, 7, "couro_escuro")
            t.pontos([(17, 6), (18, 7)], "amarelo_fogo")
            t.ponto(18, 6, "branco")
        else:
            t.cel(t.capsula(25, 27, 29, 32, 1.2), ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"], sombra=0)
            t.linha(29, 32, 31, 31, "couro_escuro")
            t.ponto(32, 30, "amarelo_fogo")
            membro(t, (18, 25), (21, 30), (25, 30), 2.3, 2.1, FARDA)
            t.cel(t.elipse(25.5, 30, 2, 1.8), PELE, sombra=1)
    elif tipo == "facao":
        if rosto == "grito":
            # Golpe: braço esticado e o facão na horizontal, com o rastro do corte.
            membro(t, (18, 25), (23, 26), (28, 27), 2.3, 2.1, FARDA)
            t.cel(t.capsula(28, 26.5, 41, 25, 1.4, 0.8), ["sombra", "cinza_escuro", "cinza_claro", "branco"], sombra=0)
            t.cel(t.elipse(28.5, 27, 2, 1.8), PELE, sombra=1)
            for k in range(9):
                a = -1.1 + k * 0.25
                t.ponto(int(30 + math.cos(a) * 12), int(27 + math.sin(a) * 12), "branco")
        else:
            # Facão erguido, correndo para cima do Lampião.
            membro(t, (18, 25), (24, 27), (30, 22), 2.2, 2.0, FARDA)
            t.cel(t.capsula(31, 20, 37, 7, 1.4, 0.8), ["sombra", "cinza_escuro", "cinza_claro", "branco"], sombra=0)
            t.cel(t.capsula(30, 23, 31, 20, 1.1), ["couro_profundo", "couro_escuro", "couro", "couro_medio"], sombra=0)
            t.cel(t.elipse(30.5, 22, 2, 1.9), PELE, sombra=1)
    else:
        t.cel(t.poligono([(10 + recuo, 28), (19 + recuo, 28.5), (19 + recuo, 31.5), (12 + recuo, 32)]), MADEIRA, sombra=1)
        t.cel(t.retangulo(19 + recuo, 28.5, 23, 1.6), ACO, sombra=0)
        t.cel(t.retangulo(19 + recuo, 30, 12, 1.6), MADEIRA, sombra=0)
        t.ponto(41 + recuo, 28, "cinza")
        membro(t, (18, 25), (20, 30), (25, 30), 2.3, 2.1, FARDA)
        t.cel(t.elipse(25.5, 30, 2, 1.8), PELE, sombra=1)
    t.contorno("sombra")
    if rosto == "grito" and tipo == "fuzil":
        t.pontos([(43, 28), (42, 27), (42, 29)], "amarelo_fogo")
    if rosto == "grito" and tipo == "rojao":
        t.pontos([(38, 14), (39, 15), (38, 16)], "amarelo_fogo")
    if rosto == "grito" and tipo == "metralhador":
        t.pontos([(43, 28), (42, 27), (42, 29), (43, 29)], "amarelo_fogo")
    return t


def sentado(tipo, k=0):
    """Soldado sentado no chão cochilando (k=1: cabeça mais baixa, roncando)."""
    cima = volante("ronca" if k else "dorme", "sem_pernas", tipo=tipo)
    t = Tela(W, H)
    perna(t, (12, 42), (19, 40), (25, CHAO), FARDA, atras=True)
    perna(t, (16, 42), (23, 39), (30, CHAO), FARDA)
    desce = 8 + k
    for y in range(H - 1, -1, -1):
        yy = y + desce
        if yy >= H:
            continue
        linha = cima.px[y]
        m = linha != VAZIO
        t.px[yy][m] = linha[m]
    t.contorno("sombra")
    return t


def variante(tipo):
    """Os 8 quadros da Volante para um tipo de soldado."""
    return {
        "parado": lambda: volante("serio", tipo=tipo),
        "atira": lambda: volante("grito", tipo=tipo),
        "panico": lambda: volante("panico", "panico", tipo=tipo),
        "anda1": lambda: volante("bravo" if tipo == "facao" else "serio", "anda", 0, tipo=tipo),
        "anda2": lambda: volante("bravo" if tipo == "facao" else "serio", "anda", 1, tipo=tipo),
        "anda3": lambda: volante("bravo" if tipo == "facao" else "serio", "anda", 2, tipo=tipo),
        "anda4": lambda: volante("bravo" if tipo == "facao" else "serio", "anda", 3, tipo=tipo),
        "morte": lambda: volante("morto", "panico", tipo=tipo),
        "sentado1": lambda: sentado(tipo, 0),
        "sentado2": lambda: sentado(tipo, 1),
    }


GRANADEIRO = variante("granadeiro")
METRALHADOR = variante("metralhador")
FACAO = variante("facao")
ROJAO = variante("rojao")
OFICIAL = variante("oficial")
VOLANTE = variante("fuzil")




# ================================================================ Xeremita
def tentaculo(t, x0, y0, fase, comprimento=12, rampa=ALIEN, deslocar=0, para_cima=False, lado=1):
    """Tentáculo que ondula: cadeia de cápsulas afinando da raiz para a ponta."""
    pts = []
    for k in range(7):
        f = k / 6
        if para_cima:
            x = x0 + math.sin(fase + f * 3) * 1.5 * f + f * 6 * lado
            y = y0 - f * comprimento
        else:
            x = x0 + math.sin(fase + f * 2.6) * 2.4 * f
            y = y0 + f * comprimento
        pts.append((x, y))
    m = np.zeros((H, W), dtype=bool)
    for k in range(6):
        r = 2.3 - k * 0.3
        m |= t.capsula(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1], r, r - 0.3)
    t.cel(m, rampa, sombra=1, deslocar=deslocar)
    return pts[-1]


def xeremita(cara="normal", pose="parado", passo=0):
    """Alienígena xeremita: cabeçona verde, olho gigante, tentáculos e pistola de raio."""
    t = Tela(W, H)
    fases = [0, 1.5, 3, 4.5]
    f = fases[passo] if pose == "anda" else 0.6
    pulo = 1 if pose == "anda" and passo in (1, 3) else 0
    cima = pose == "panico"
    # Tentáculos de trás, depois os da frente.
    for k, x in enumerate((12, 16)):
        tentaculo(t, x, 33 + pulo, f + k * 1.7, 12 - pulo, ALIEN_ESC, deslocar=0)
    corpo = t.elipse(17, 29.5 + pulo, 6, 5.5)
    t.cel(corpo, ACO, sombra=2)
    t.chapado(t.retangulo(11, 31 + pulo, 13, 1) & corpo, "cinza_escuro")
    t.cel(t.elipse(19, 29 + pulo, 1.6, 1.6), ["alien_esc", "alien", "alien_brilho", "branco"], sombra=0)
    for k, x in enumerate((14, 19)):
        tentaculo(t, x, 34 + pulo, f + 0.8 + k * 1.9, 11 - pulo, ALIEN)

    # Braço de tentáculo de trás (só aparece no pânico, para cima).
    if cima:
        tentaculo(t, 9, 26, 2.0, 16, ALIEN_ESC, para_cima=True, lado=-1)

    # Cabeçona com caroços.
    hy = 17 + pulo
    cabeca = t.elipse(18, hy, 9, 8.6) | t.elipse(14, hy + 5, 5.5, 4.5)
    t.cel(cabeca, ALIEN, sombra=2)
    for (x, y, r) in ((12, hy - 4, 1.4), (16, hy - 6.5, 1.1), (10.5, hy + 1, 1.1), (14, hy - 1.5, 0.9)):
        t.chapado(t.elipse(x, y, r, r * 0.8), "alien_medio")
        t.ponto(int(x - r * 0.5), int(y - r * 0.5), "alien_luz")
    t.chapado(t.elipse(13, hy - 5.5, 1.8, 1.1), "alien_brilho")
    # Antena com bolinha.
    t.linha(16, hy - 8.5, 14, hy - 12, "alien_esc")
    t.cel(t.elipse(13.5, hy - 12.5, 1.6, 1.6), ["alien_esc", "alien", "alien_brilho", "branco"], sombra=0)

    # Olhão.
    ox, oy = 23, hy - 1
    if cara == "morto":
        t.chapado(t.elipse(ox, oy, 3.8, 4.3), "preto")
        t.chapado(t.elipse(ox, oy, 2.8, 3.3), "branco")
        for a in range(0, 360, 30):  # espiral tonta
            r = 0.5 + a / 360 * 2.3
            t.ponto(int(ox + math.cos(math.radians(a * 2)) * r), int(oy + math.sin(math.radians(a * 2)) * r), "preto")
    else:
        rx, ry = (4.4, 4.9) if cara in ("grito", "susto") else (3.8, 4.3)
        t.chapado(t.elipse(ox, oy, rx, ry), "preto")
        t.chapado(t.elipse(ox, oy, rx - 1, ry - 1), "branco")
        if cara == "susto":
            t.chapado(t.elipse(ox + 1, oy, 1, 1), "preto")
        else:
            t.chapado(t.elipse(ox + 1.2, oy + 0.5, 1.8, 2.1), "preto")
            t.ponto(ox + 1, oy - 1, "branco")
        if cara in ("bravo", "grito"):
            # Pálpebra caída de raiva.
            t.chapado(t.elipse(ox, oy - ry + 0.5, rx + 0.5, 2.8) & t.elipse(ox, oy, rx + 0.5, ry + 0.5), "alien_esc")
            t.linha(ox - rx, oy - ry + 2, ox + rx, oy - ry + 3, "preto")
    # Boca.
    by = hy + 5
    if cara == "grito":
        t.chapado(t.elipse(22.5, by + 1, 2.6, 1.8), "preto")
        t.pontos([(21, by), (23, by)], "branco")
        t.chapado(t.elipse(22.5, by + 2, 1.2, 0.6), "vermelho_medio")
    elif cara == "susto":
        t.chapado(t.elipse(22.5, by + 1, 1.8, 2), "preto")
        t.chapado(t.elipse(22.5, by + 2, 1, 0.8), "vermelho_medio")
    elif cara == "morto":
        t.linha(20, by, 25, by + 1, "preto")
        t.chapado(t.elipse(23.5, by + 2.2, 1.1, 1.5), "vermelho")
    else:
        t.linha(20, by, 24, by + 1, "alien_profundo")
        t.ponto(22, by + 1, "branco")

    # Braço-tentáculo com a pistola de raio.
    if cima:
        tentaculo(t, 27, 28, 3.5, 16, ALIEN, para_cima=True, lado=1)
    else:
        m = t.capsula(20, 28 + pulo, 24, 31, 2.2, 1.8) | t.capsula(24, 31, 28, 30, 1.8, 1.6)
        t.cel(m, ALIEN, sombra=1)
        recuo = -1 if cara == "grito" else 0
        t.cel(t.elipse(31 + recuo, 29.5, 4, 2.4), LILAS, sombra=1)
        t.cel(t.retangulo(33 + recuo, 28.5, 4, 2), LILAS, sombra=0)
        t.cel(t.elipse(37.5 + recuo, 29.5, 1.5, 1.5), ["alien_esc", "alien", "alien_brilho", "branco"], sombra=0)
        t.cel(t.poligono([(28 + recuo, 30), (31 + recuo, 30), (30 + recuo, 34), (28 + recuo, 34)]), LILAS, sombra=1, deslocar=-1)
    t.contorno("sombra")
    if cara == "grito":
        t.pontos([(39, 29), (40, 28), (40, 30), (41, 29)], "alien_brilho")
    return t


XEREMITA = {
    "parado": lambda: xeremita("normal"),
    "atira": lambda: xeremita("grito"),
    "grito": lambda: xeremita("susto", "panico"),
    "anda1": lambda: xeremita("bravo", "anda", 0),
    "anda2": lambda: xeremita("bravo", "anda", 1),
    "anda3": lambda: xeremita("bravo", "anda", 2),
    "anda4": lambda: xeremita("bravo", "anda", 3),
    "morte": lambda: xeremita("morto", "panico"),
}


# ================================================================ Refém
CRU = ["terra_media", "areia_media", "areia", "areia_luz"]
CAMISA = ["areia_media", "areia_luz", "areia_clara", "branco"]


def cabeca_romeiro(t, x, y, rosto="triste", chapeu=0):
    """Cabeça do romeiro: chapéu de palha com fitas, narigão e barba branca comprida.
    (x, y) = centro do rosto."""
    x, y = int(round(x)), int(round(y))
    # Fitas coloridas do chapéu caindo atrás.
    for k, cor in enumerate(("vermelho", "amarelo_fogo", "ceu", "mandacaru")):
        balanco = 1 if chapeu else 0
        t.linha(x - 9 + k * 0.6, y - 5 + chapeu, x - 11 - k * 0.8 - balanco, y + 3 + k * 1.5, cor)
    t.cel(t.elipse(x - 7, y + 1, 1.8, 2.4), PELE, sombra=1)  # orelha
    t.cel(t.elipse(x, y, 7, 7.5), PELE, sombra=2)
    # Barba branca e comprida, até o peito.
    barba = t.poligono([(x - 6, y + 1), (x + 7, y + 1), (x + 8, y + 7), (x + 4, y + 14), (x, y + 15), (x - 4, y + 9)])
    t.cel(barba, BARBA, sombra=2)
    t.linha(x + 1, y + 7, x + 2, y + 12, "cinza")
    t.linha(x + 5, y + 6, x + 4, y + 10, "cinza")
    # Bigode e boca.
    t.cel(t.poligono([(x + 1, y + 3), (x + 8, y + 3), (x + 9, y + 5), (x + 2, y + 5)]), BARBA, sombra=1)
    if rosto == "feliz":
        t.chapado(t.elipse(x + 5, y + 6.5, 2.4, 1.6), "preto")
        t.chapado(t.retangulo(x + 3, y + 5.5, 4, 1), "branco")
        t.chapado(t.elipse(x + 5, y + 7.5, 1.2, 0.6), "vermelho")
    elif rosto == "chorando":
        t.chapado(t.elipse(x + 5, y + 6.5, 1.8, 1.4), "preto")
    else:
        t.linha(x + 3, y + 6, x + 6, y + 6, "cinza_escuro")
    # Olhos e sobrancelhas brancas e grossas.
    if rosto == "feliz":
        t.pontos([(x + 3, y - 2), (x + 4, y - 3), (x + 5, y - 2)], "preto")  # olho fechado de alegria
        t.linha(x + 2, y - 5, x + 6, y - 5, "cinza_claro")
    elif rosto == "concentrado":
        t.linha(x + 3, y - 2, x + 6, y - 2, "preto")
        t.linha(x + 2, y - 4, x + 7, y - 3, "cinza_claro")
    else:
        t.chapado(t.elipse(x + 4.5, y - 2, 1.8, 1.8), "preto")
        t.chapado(t.elipse(x + 4.5, y - 2, 1, 1), "branco")
        t.ponto(x + 5, y - 2, "preto")
        # Sobrancelha triste, levantada no meio.
        t.linha(x + 2, y - 4, x + 7, y - 6, "cinza_claro")
        t.linha(x + 2, y - 5, x + 6, y - 6, "branco")
        if rosto == "chorando":
            t.chapado(t.capsula(x + 3, y, x + 2, y + 4, 0.7), "ceu_claro")
    # Narigão.
    t.cel(t.elipse(x + 8, y + 1, 2.6, 2.3), PELE_CLARA, sombra=1)
    t.ponto(x + 7, y + 2, "pele_sombra")
    # Chapéu de palha com aba larga e fita vermelha.
    cy = y - 6 + chapeu
    t.cel(t.elipse(x, cy - 2, 6, 4.5) & (t.yy < cy + 0.5), PALHA, sombra=1)
    t.chapado(t.retangulo(x - 5.5, cy - 2, 11.5, 1.5), "vermelho")
    t.cel(t.elipse(x, cy + 0.5, 12.5, 2.2), PALHA, sombra=1)
    for k in range(-10, 11, 3):
        t.ponto(int(x + k), int(cy + 1), "areia_media")


def terco(t, x, y):
    """Terço de contas no peito, com a cruzinha."""
    x, y = int(round(x)), int(round(y))
    for k in range(6):
        t.ponto(int(x - 4 + k * 1.5), int(y + abs(k - 2.5) * -0.6 + 1.5), "couro_escuro")
    t.chapado(t.retangulo(x, y + 2, 1, 3), "couro_escuro")
    t.chapado(t.retangulo(x - 1, y + 3, 3, 1), "couro_escuro")


def romeiro_amarrado(balanco=0, pulo=0, rosto="triste"):
    """Ajoelhado, amarrado com corda grossa, se debatendo."""
    t = Tela(W, H)
    b, p = balanco, pulo
    # Pernas dobradas (sentado nos calcanhares).
    t.cel(t.elipse(17, 41 - p, 9, 4), CRU, sombra=2)
    t.cel(t.elipse(9, 43 - p, 3, 2), COURO, sombra=1)
    # Tronco de camisa de algodão.
    tronco = t.elipse(17 + b * 0.5, 32 - p, 7.5, 8)
    t.cel(tronco, CAMISA, sombra=2)
    # Bornal nas costas.
    t.cel(t.elipse(10 + b * 0.5, 34 - p, 3, 3.5), COURO, sombra=1)
    # Voltas de corda.
    for k, y in enumerate((28, 32, 36)):
        volta = t.capsula(9 + b * 0.5, y - p + k * 0.3, 25 + b * 0.5, y - p - 1, 1.2) & t.elipse(17 + b * 0.5, 32 - p, 9, 9)
        t.cel(volta, CORDA, sombra=1)
    t.cel(t.elipse(24 + b * 0.5, 33 - p, 1.8, 1.5), CORDA, sombra=1)  # nó
    t.linha(25 + b * 0.5, 34 - p, 27 + b, 38 - p, "barro")
    cabeca_romeiro(t, 18 + b, 18 - p, rosto, chapeu=1 if p else 0)
    t.contorno("sombra")
    if rosto == "chorando":
        t.pontos([(30 + b, 14 - p), (31 + b, 15 - p)], "ceu_claro")
    return t


def romeiro_em_pe(pose="parado", passo=0, rosto="feliz"):
    """Romeiro solto: pulando de alegria, procurando no bornal, entregando,
    batendo continência ou correndo."""
    t = Tela(W, H)
    dy = {"solto": -4, "entrega": -1}.get(pose, 0)
    if pose == "corre":
        dy = -1 if passo in (1, 3) else 0
    bx = 17
    # Perna de trás.
    if pose == "corre":
        k = [(-4, 4), (0, 0), (4, -4), (0, 0)][passo]
        membro(t, (bx - 1, 34 + dy), (bx - 1 + k[1] * 0.4, 39 + dy), (bx - 2 + k[1], CHAO - 1), 2, 1.8, CRU, -1)
        t.cel(t.elipse(bx - 1 + k[1], CHAO - 0.5, 2.4, 1.2), COURO, sombra=0, deslocar=-1)
    elif pose == "solto":
        membro(t, (bx - 1, 34 + dy), (bx - 4, 38 + dy), (bx - 5, 42 + dy), 2, 1.8, CRU, -1)
        t.cel(t.elipse(bx - 6, 42.5 + dy, 2.4, 1.2), COURO, sombra=0, deslocar=-1)
    else:
        membro(t, (bx - 1, 34 + dy), (bx - 2, 39 + dy), (bx - 3, CHAO - 1), 2, 1.8, CRU, -1)
        t.cel(t.elipse(bx - 2, CHAO - 0.5, 2.6, 1.2), COURO, sombra=0, deslocar=-1)
    # Braço de trás.
    if pose == "solto":
        membro(t, (bx - 3, 25 + dy), (bx - 9, 21 + dy), (bx - 12, 15 + dy), 1.8, 1.6, CAMISA, -1)
        t.cel(t.elipse(bx - 12.5, 14 + dy, 1.8, 1.8), PELE, sombra=1)
    elif pose == "corre":
        k = [-1, 0, 1, 0][passo]
        membro(t, (bx - 3, 25 + dy), (bx - 3 - k * 3, 30 + dy), (bx - 1 - k * 5, 31 + dy), 1.8, 1.6, CAMISA, -1)
    # Tronco magrinho e bornal.
    curva = 2 if pose == "procura" else 0
    tronco = t.elipse(bx + curva, 29 + dy, 6.5, 7) | t.retangulo(bx - 5 + curva, 29 + dy, 11, 5)
    t.cel(tronco, CAMISA, sombra=2)
    t.chapado(t.capsula(bx - 5 + curva, 23 + dy, bx + 5 + curva, 34 + dy, 0.8) & tronco, "couro")
    t.cel(t.elipse(bx + 6 + curva, 34 + dy, 3.4, 3.4), COURO, sombra=1)
    t.chapado(t.retangulo(bx + 3 + curva, 31 + dy, 7, 1.5), "couro_escuro")
    t.chapado(t.retangulo(bx - 5, 34 + dy, 11, 1.2), "barro")  # cordão na cintura
    # Perna da frente.
    if pose == "corre":
        k = [(-4, 4), (0, 0), (4, -4), (0, 0)][passo]
        membro(t, (bx + 2, 34 + dy), (bx + 3 + k[0] * 0.4, 39 + dy), (bx + 2 + k[0], CHAO - 1), 2, 1.8, CRU)
        t.cel(t.elipse(bx + 3 + k[0], CHAO - 0.5, 2.4, 1.2), COURO, sombra=0)
    elif pose == "solto":
        membro(t, (bx + 2, 34 + dy), (bx + 6, 37 + dy), (bx + 5, 41 + dy), 2, 1.8, CRU)
        t.cel(t.elipse(bx + 6, 41.5 + dy, 2.4, 1.2), COURO, sombra=0)
    else:
        membro(t, (bx + 2, 34 + dy), (bx + 3, 39 + dy), (bx + 4, CHAO - 1), 2, 1.8, CRU)
        t.cel(t.elipse(bx + 5, CHAO - 0.5, 2.6, 1.2), COURO, sombra=0)
    if pose == "solto":
        # Cordas caindo no chão.
        for x0 in (8, 22):
            t.cel(t.capsula(x0, CHAO - 1, x0 + 7, CHAO - 2, 1), CORDA, sombra=0)
    hx, hy = bx + 1 + curva * 1.5, 16 + dy + curva
    cabeca_romeiro(t, hx, hy, rosto, chapeu=-2 if pose == "solto" else 0)
    terco(t, bx, 24 + dy)
    # Braço da frente.
    if pose == "solto":
        membro(t, (bx + 3, 25 + dy), (bx + 10, 21 + dy), (bx + 14, 14 + dy), 1.8, 1.6, CAMISA)
        t.cel(t.elipse(bx + 14.5, 13 + dy, 1.8, 1.8), PELE, sombra=1)
    elif pose == "procura":
        membro(t, (bx + 4, 25 + dy), (bx + 7, 30 + dy), (bx + 7, 33 + dy), 1.8, 1.6, CAMISA)
    elif pose == "entrega":
        membro(t, (bx + 4, 25 + dy), (bx + 11, 25 + dy), (bx + 17, 21 + dy), 1.8, 1.6, CAMISA)
        t.cel(t.elipse(bx + 17.5, 20.5 + dy, 1.9, 1.9), PELE, sombra=1)
    elif pose == "continencia":
        membro(t, (bx + 4, 25 + dy), (bx + 9, 21 + dy), (bx + 7, 13 + dy), 1.8, 1.6, CAMISA)
        t.cel(t.elipse(bx + 7, 12 + dy, 1.9, 1.7), PELE, sombra=1)
    else:  # corre
        k = [1, 0, -1, 0][passo]
        membro(t, (bx + 3, 25 + dy), (bx + 3 - k * 3, 30 + dy), (bx + 6 - k * 4, 30 + dy), 1.8, 1.6, CAMISA)
        t.cel(t.elipse(bx + 6.5 - k * 4, 30 + dy, 1.7, 1.7), PELE, sombra=1)
    t.contorno("sombra")
    if pose == "corre":
        # Gotas de suor voando para trás.
        t.pontos([(5, 12 + dy), (4, 13 + dy), (7, 9)], "ceu_claro")
    return t


def romeiro_pendurado(balanco=0, rosto="chorando"):
    """Romeiro pendurado pelas mãos amarradas (a corda é desenhada no jogo),
    pernas balançando."""
    t = Tela(W, H)
    bx = 17
    b = balanco
    # Pernas soltas no ar.
    membro(t, (bx - 1, 34), (bx - 2 - b, 39), (bx - 3 - b * 2, 43), 2, 1.8, CRU, -1)
    t.cel(t.elipse(bx - 2 - b * 2, 43.5, 2.2, 1.2), COURO, sombra=0, deslocar=-1)
    tronco = t.elipse(bx, 29, 6.5, 7) | t.retangulo(bx - 5, 29, 11, 5)
    t.cel(tronco, CAMISA, sombra=2)
    t.chapado(t.capsula(bx - 5, 23, bx + 5, 34, 0.8) & tronco, "couro")
    t.chapado(t.retangulo(bx - 5, 34, 11, 1.2), "barro")
    membro(t, (bx + 2, 34), (bx + 3 + b, 39), (bx + 4 + b * 2, 43), 2, 1.8, CRU)
    t.cel(t.elipse(bx + 5 + b * 2, 43.5, 2.2, 1.2), COURO, sombra=0)
    # Braços esticados para cima, por trás da cabeça (aparecem os cotovelos e as mãos amarradas lá em cima).
    membro(t, (bx - 4, 24), (bx - 7, 13), (bx + 1, 1.5), 1.8, 1.6, CAMISA, -1)
    membro(t, (bx + 4, 24), (bx + 9, 13), (bx + 3, 1.5), 1.8, 1.6, CAMISA)
    cabeca_romeiro(t, bx + 1, 18, rosto, chapeu=1)
    terco(t, bx, 25)
    t.cel(t.elipse(bx + 2, 1.5, 2.6, 1.6), PELE, sombra=1)
    t.cel(t.retangulo(bx, 2, 4.5, 1.4), CORDA, sombra=0)
    t.contorno("sombra")
    return t


REFEM = {
    "amarrado1": lambda: romeiro_amarrado(0, 0, "triste"),
    "amarrado2": lambda: romeiro_amarrado(-1, 1, "chorando"),
    "amarrado3": lambda: romeiro_amarrado(1, 0, "triste"),
    "solto": lambda: romeiro_em_pe("solto", rosto="feliz"),
    "procura": lambda: romeiro_em_pe("procura", rosto="concentrado"),
    "entrega": lambda: romeiro_em_pe("entrega", rosto="feliz"),
    "continencia": lambda: romeiro_em_pe("continencia", rosto="feliz"),
    "corre1": lambda: romeiro_em_pe("corre", 0, "feliz"),
    "corre2": lambda: romeiro_em_pe("corre", 1, "feliz"),
    "corre3": lambda: romeiro_em_pe("corre", 2, "feliz"),
    "corre4": lambda: romeiro_em_pe("corre", 3, "feliz"),
    "pendurado1": lambda: romeiro_pendurado(-1, "chorando"),
    "pendurado2": lambda: romeiro_pendurado(1, "triste"),
}


def gravar(arquivo, quadros):
    pixel.salvar(arquivo, {n: f() for n, f in quadros.items()})


if __name__ == "__main__":
    gravar("volante.txt", VOLANTE)
    gravar("xeremita.txt", XEREMITA)
    gravar("refem.txt", REFEM)
    gravar("granadeiro.txt", GRANADEIRO)
    gravar("metralhador.txt", METRALHADOR)
    gravar("facao.txt", FACAO)
    gravar("rojao.txt", ROJAO)
    gravar("oficial.txt", OFICIAL)
    print("volante.txt, xeremita.txt e refem.txt atualizados")
