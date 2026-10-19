"""Objetos das cenas cômicas dos soldados distraídos (antes de verem o Lampião):

- mesa_truco(q): caixote de munição virado de mesa, com cartas, garrafa de
  cachaça, copinhos e moedas. q=1: derrubado (o soldado largou tudo no susto).
- panela(q): panela de barro no fogo com o feijão fervendo. q=0/1 vapor
  subindo; q=2 virada, derramando.
- carta_voa(q): carta solta voando (frente e verso) quando a mesa vira.
- foto_voa(q): o retrato da noiva caindo no chão, balançando.
Usado por tools/arte/exportar.py.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela  # noqa: E402

MADEIRA = ["marrom_noite", "couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz"]
BARRO = ["marrom_noite", "terra_escura", "terra", "terra_media", "barro", "areia_media"]
VIDRO = ["sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru_luz"]
CARTA = ["sombra", "cinza_luz", "cinza_claro", "branco"]
METAL = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]


def _carta_deitada(t, x, y, cor):
    t.chapado(t.retangulo(x, y, 4, 2), "sombra")
    t.chapado(t.retangulo(x + 0.5, y, 3, 1), "branco")
    t.ponto(x + 2, y, cor)


def mesa_truco(q=0):
    """Caixote virado de mesa (36x22), pé no centro de baixo."""
    W, H = 36, 22
    t = Tela(W, H)
    if q == 0:
        # Caixote em pé com a tampa servindo de mesa.
        cx = t.retangulo(7, 10, 22, 12)
        t.volume(cx, MADEIRA, achatado=2, suave=0.6, ambiente=0.3, textura=0.08, semente=4)
        for y in (14, 18):
            t.linha(7, y, 28, y, "couro_profundo")
        t.linha(7, 10, 28, 21, "couro_escuro")  # travessa em X
        t.linha(7, 21, 28, 10, "couro_escuro")
        tampa = t.retangulo(4, 8, 28, 3)
        t.volume(tampa, MADEIRA, achatado=1.2, suave=0.4, ambiente=0.35, brilho=1.2)
        # Cartas na mesa, monte do baralho e moedas.
        _carta_deitada(t, 8, 7, "vermelho")
        _carta_deitada(t, 13, 7, "preto")
        t.chapado(t.retangulo(19, 5, 4, 3), "sombra")
        t.chapado(t.retangulo(19.5, 5, 3, 2), "vermelho_esc")  # verso do monte
        t.pontos([(25, 7), (27, 7)], "amarelo_fogo")
        t.pontos([(26, 6)], "amarelo_claro")
        # Garrafa de cachaça e um copinho.
        t.cel(t.capsula(29, 7, 29, 1, 1.6, 0.7), VIDRO, sombra=1)
        t.chapado(t.retangulo(28.5, -0.5, 1.2, 1.5), "couro")
        t.chapado(t.retangulo(28.4, 4, 1.4, 2), "areia_clara")  # rótulo
        t.cel(t.retangulo(5, 5, 2, 3), ["sombra", "cinza_luz", "cinza_claro", "branco"], sombra=0)
    else:
        # Derrubado de lado, garrafa rolando, cartas espalhadas no chão.
        cx = t.retangulo(10, 9, 13, 13)
        t.volume(cx, MADEIRA, achatado=2, suave=0.6, ambiente=0.3, textura=0.08, semente=4)
        t.linha(10, 9, 22, 21, "couro_escuro")
        t.linha(10, 21, 22, 9, "couro_escuro")
        tampa = t.retangulo(23, 6, 3, 16)
        t.volume(tampa, MADEIRA, achatado=1.2, suave=0.4, ambiente=0.35)
        t.cel(t.capsula(28, 20, 34, 20, 1.6, 0.7), VIDRO, sombra=1)
        t.chapado(t.elipse(4, 21, 4, 0.8), "terra_escura")  # cachaça derramada
        for x, cor in ((1, "vermelho"), (6, "preto"), (31, "vermelho")):
            _carta_deitada(t, x, 20, cor)
    t.contorno("sombra")
    return t


def panela(q=0):
    """Panela de barro (22x26) com alça; o vapor sobe por cima. Pé no centro de baixo."""
    W, H = 22, 26
    t = Tela(W, H)
    if q < 2:
        corpo = t.elipse(11, 19, 7.5, 6) & (t.yy > 14)
        t.volume(corpo, BARRO, achatado=2, suave=0.8, ambiente=0.3, textura=0.08, semente=2)
        t.volume(t.elipse(11, 14.5, 8, 2), BARRO, achatado=1, suave=0.4, ambiente=0.35, brilho=1.2)
        t.chapado(t.elipse(11, 14.5, 6.3, 1.2), "marrom_noite")
        t.chapado(t.elipse(11, 14.8, 5.5, 0.8), "couro_escuro")  # feijão
        for x in (8, 13):
            t.ponto(x + q, 14, "couro_medio")  # bolhas
        t.chapado(t.retangulo(2, 16, 2.5, 2), "terra")
        t.chapado(t.retangulo(17.5, 16, 2.5, 2), "terra")
        t.contorno("sombra")
        # Vapor em voltas subindo (sem contorno, translúcido no jogo pela cor clara).
        for k in range(3):
            y = 11 - k * 4 - q * 2
            x = 9 + math.sin(k * 1.7 + q * 1.2) * 2.5
            if y > 0:
                t.chapado(t.elipse(x, y, 2.0 - k * 0.3, 1.4), "cinza_claro")
                t.ponto(x - 1, y - 1, "branco")
    else:
        # Virada de lado: o feijão escorrendo no chão.
        corpo = t.elipse(9, 20, 6, 5.5)
        t.volume(corpo, BARRO, achatado=2, suave=0.8, ambiente=0.3, textura=0.08, semente=2)
        t.chapado(t.elipse(15, 20, 1.6, 5), "marrom_noite")
        t.chapado(t.elipse(18, 24.5, 4, 1.2), "couro_escuro")
        t.pontos([(16, 24), (19, 24), (21, 25)], "couro_medio")
        t.contorno("sombra")
    return t


def carta_voa(q=0):
    t = Tela(5, 7)
    t.chapado(t.retangulo(0, 0, 5, 7), "sombra")
    if q == 0:
        t.chapado(t.retangulo(1, 1, 3, 5), "branco")
        t.ponto(2, 3, "vermelho")
    else:
        t.chapado(t.retangulo(1, 1, 3, 5), "vermelho_esc")
        t.ponto(2, 3, "vermelho")
    return t


def foto_voa(q=0):
    t = Tela(8, 9)
    if q == 0:
        t.chapado(t.retangulo(0, 0, 8, 9), "sombra")
        t.chapado(t.retangulo(1, 1, 6, 7), "areia_clara")
        t.chapado(t.retangulo(2, 2, 4, 5), "terra_media")
        t.chapado(t.elipse(4, 3.5, 1.1, 1.2), "areia_luz")
        t.chapado(t.retangulo(3, 5, 2, 2), "areia_media")
    else:
        t.chapado(t.retangulo(0, 3, 8, 3), "sombra")
        t.chapado(t.retangulo(1, 4, 6, 1), "areia_clara")
    return t
