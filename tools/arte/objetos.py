"""Objetos de cenário e equipamento desenhados com o motor:
barril de querosene (explode) e escudo de madeira do soldado da Volante.
Usado por tools/arte/exportar.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela  # noqa: E402

LATA = ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"]
FAIXA = ["laranja_escuro", "ouro_escuro", "amarelo_fogo", "amarelo_claro"]
TABUA = ["couro_profundo", "couro", "couro_medio", "couro_luz"]
TABUA_ESC = ["couro_profundo", "couro_escuro", "couro", "couro_medio"]
FERRO = ["sombra", "cinza_escuro", "cinza", "cinza_claro"]


def barril(quadro=0):
    """Tambor de querosene vermelho com faixa amarela e o desenho da chama.
    Quadro 1: amassado e soltando faísca (levou tiro)."""
    t = Tela(18, 24)
    corpo = t.retangulo(1, 2, 16, 21) | t.elipse(9, 2.5, 8, 1.5) | t.elipse(9, 22.5, 8, 1.5)
    t.cel(corpo, LATA, sombra=2)
    for y in (6, 17):
        t.cel(t.retangulo(1, y, 16, 1.6), FERRO, sombra=0)
    t.cel(t.retangulo(1, 9, 16, 6), FAIXA, sombra=1, linha=False)
    # Chama desenhada na faixa (perigo!).
    t.chapado(t.poligono([(7.5, 14), (9, 9.5), (10.5, 14)]), "vermelho")
    t.chapado(t.poligono([(8.3, 14), (9, 11.5), (9.7, 14)]), "preto")
    t.cel(t.elipse(9, 2, 7, 1.2), FERRO, sombra=0)
    t.ponto(12, 1, "cinza_claro")
    t.contorno("sombra")
    if quadro == 1:
        # Amassado com um furo pingando querosene.
        t.chapado(t.elipse(13, 12, 1.4, 1.4), "preto")
        t.linha(13, 13, 13, 18, "couro_profundo")
        t.pontos([(14, 11), (15, 10)], "amarelo_fogo")
        t.ponto(15, 9, "branco")
    return t


def escudo(quadro=0):
    """Escudo de tábuas pregadas com aro de ferro. Quadro 1: rachado."""
    t = Tela(12, 26)
    for k, x in enumerate((1, 4.5, 8)):
        t.cel(t.retangulo(x, 1 + (k % 2), 3.5, 24 - (k % 2)), TABUA if k % 2 else TABUA_ESC, sombra=1)
    for y in (5, 19):
        t.cel(t.retangulo(1, y, 11, 2), FERRO, sombra=0)
        for x in (2, 6, 10):
            t.ponto(x, y, "cinza_claro")
    t.contorno("sombra")
    if quadro == 1:
        t.linha(5, 8, 7, 13, "couro_profundo")
        t.linha(7, 13, 5, 17, "couro_profundo")
        t.linha(9, 2, 8, 6, "couro_profundo")
        t.pontos([(2, 12), (3, 13)], "couro_profundo")
    return t
