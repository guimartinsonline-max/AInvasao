"""Armas vistas de lado (cano para a direita), em tamanho proporcional ao
Lampião (o fuzil dele tem 24 px). Salvas em tools/arte/pixel/armas.txt.

Uso: python3 tools/arte/armas.py
Cada arma tem PUNHO (onde a mão de trás segura), APOIO (onde a mão da frente
segura por baixo) e BOCA (de onde sai o tiro), em pixels do desenho.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela  # noqa: E402
import pixel  # noqa: E402

W, H = 30, 12

# Rampas curtas (linha interna, sombra, base, luz).
MADEIRA = ["couro_profundo", "couro", "couro_medio", "couro_luz"]
MADEIRA_ESC = ["couro_profundo", "couro_escuro", "couro", "couro_medio"]
ACO = ["sombra", "cinza_escuro", "cinza", "cinza_claro"]
ACO_ESC = ["sombra", "sombra_media", "cinza_escuro", "cinza_medio"]
LATAO = ["couro_escuro", "ouro_escuro", "amarelo_fogo", "amarelo_claro"]
VERMELHO = ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"]
ROXO = ["sombra", "roxo_escuro", "roxo", "lilas"]
LILAS = ["roxo_escuro", "roxo", "lilas", "lilas_claro"]
ALIEN = ["alien_profundo", "alien_medio", "alien", "alien_brilho"]
AZUL = ["sombra", "azul_medio", "ceu_escuro", "ceu_medio"]
PAPEL = ["laranja_escuro", "ouro_escuro", "amarelo_fogo", "amarelo_claro"]

PUNHO = {}
APOIO = {}
BOCA = {}


def coronha(t, x0, y0, comprimento=7, rampa=MADEIRA):
    t.cel(t.poligono([(x0 - comprimento, y0), (x0, y0), (x0, y0 + 3.5), (x0 - comprimento + 1, y0 + 4.5),
                      (x0 - comprimento, y0 + 4)]), rampa, sombra=1)


def punho(t, x, y, rampa=MADEIRA_ESC):
    t.cel(t.poligono([(x, y), (x + 3, y), (x + 2.2, y + 4), (x - 0.8, y + 4)]), rampa, sombra=1)


def madsen():
    t = Tela(W, H)
    coronha(t, 8, 4)
    punho(t, 8, 7)
    t.cel(t.poligono([(9.5, 4.5), (13, 4.5), (14.5, 1), (13.5, 0), (11.5, 0), (10.5, 2)]), ACO_ESC, sombra=1)
    t.cel(t.retangulo(8, 4, 7, 4), ACO)
    t.cel(t.retangulo(15, 5, 10, 2), ACO, sombra=0)
    for x in range(16, 24, 2):
        t.ponto(x, 5, "sombra")
    t.cel(t.retangulo(25, 4, 3, 4), ACO_ESC, sombra=1)
    t.linha(16, 7.5, 24, 7.5, "cinza_escuro")
    t.contorno("sombra")
    PUNHO["madsen"], APOIO["madsen"], BOCA["madsen"] = (9, 8), (15, 8), (28, 5)
    return t


def bacamarte():
    t = Tela(W, H)
    coronha(t, 8, 4, 8)
    t.cel(t.retangulo(9, 6, 10, 1.6), MADEIRA_ESC, sombra=0)
    t.cel(t.retangulo(8, 4, 15, 2.2), LATAO, sombra=0)
    for x in (12, 17):
        t.chapado(t.retangulo(x, 4, 1, 2), "laranja_escuro")
    t.cel(t.poligono([(22, 4), (28, 1.5), (30, 1.5), (30, 9), (28, 9), (22, 6.5)]), LATAO, sombra=1)
    t.linha(29, 3, 29, 8, "couro_profundo")
    t.cel(t.retangulo(7, 4, 3, 2.5), ACO, sombra=0)
    t.ponto(8, 3, "cinza_escuro")
    punho(t, 8, 6.5, MADEIRA_ESC)
    t.contorno("sombra")
    PUNHO["bacamarte"], APOIO["bacamarte"], BOCA["bacamarte"] = (9, 7), (14, 7), (29, 5)
    return t


def rojao():
    t = Tela(W, H)
    t.cel(t.retangulo(1, 2, 23, 5), VERMELHO, sombra=1)
    for x in range(4, 22, 6):
        t.cel(t.poligono([(x, 2), (x + 3, 2), (x + 1.5, 7), (x - 1.5, 7)]), PAPEL, sombra=1, linha=False)
    for x in (1, 23):
        t.cel(t.retangulo(x, 1.5, 1.5, 6), MADEIRA_ESC, sombra=0)
    t.cel(t.poligono([(24.5, 3), (27, 3), (29.5, 4.5), (27, 6), (24.5, 6)]), ACO, sombra=1)
    punho(t, 9, 7)
    t.contorno("sombra")
    t.pontos([(0, 8), (0, 9)], "amarelo_fogo")
    PUNHO["rojao"], APOIO["rojao"], BOCA["rojao"] = (10, 8), (17, 7), (29, 4)
    return t


def desintegrador():
    t = Tela(W, H)
    t.cel(t.poligono([(5, 6), (9, 6), (8, 11), (4, 11)]), ROXO, sombra=1)
    t.cel(t.elipse(10, 5, 7, 3), LILAS, sombra=1)
    t.cel(t.retangulo(16, 4, 8, 2), ROXO, sombra=0)
    for x in (18, 21):
        t.cel(t.retangulo(x, 2, 1.6, 6), LILAS, sombra=0)
    t.cel(t.elipse(25, 5, 2, 2), ALIEN, sombra=0)
    t.ponto(24, 4, "branco")
    t.cel(t.elipse(9, 2, 2.2, 2), ALIEN, sombra=0)
    t.ponto(8, 1, "branco")
    t.pontos([(6, 6), (9, 6), (12, 6)], "alien_brilho")
    t.contorno("sombra")
    PUNHO["desintegrador"], APOIO["desintegrador"], BOCA["desintegrador"] = (6, 7), (15, 7), (27, 5)
    return t


def candeeiro():
    t = Tela(W, H)
    t.cel(t.retangulo(2, 0.5, 7, 8), VERMELHO, sombra=1)
    t.cel(t.retangulo(3, 3, 5, 3), PAPEL, sombra=0, linha=False)
    t.chapado(t.retangulo(4, 4, 3, 1), "couro_profundo")
    t.cel(t.retangulo(9, 5, 14, 2), ACO, sombra=0)
    t.cel(t.retangulo(23, 4, 3, 4), LATAO, sombra=1)
    punho(t, 10, 7)
    t.contorno("sombra")
    t.pontos([(27, 6), (27, 7), (28, 7)], "laranja_fogo")
    t.ponto(28, 8, "amarelo_fogo")
    PUNHO["candeeiro"], APOIO["candeeiro"], BOCA["candeeiro"] = (11, 8), (18, 7), (27, 6)
    return t


def papo_amarelo():
    t = Tela(W, H)
    coronha(t, 8, 3, 8)
    t.cel(t.poligono([(8, 3), (13, 3), (13, 7), (9, 7), (8, 6)]), LATAO, sombra=1)
    t.ponto(9, 4, "branco")
    t.cel(t.retangulo(13, 3, 16, 1.6), ACO, sombra=0)
    t.cel(t.retangulo(13, 4.6, 12, 1), ACO_ESC, sombra=0)
    t.cel(t.retangulo(13, 5.6, 7, 1.6), MADEIRA, sombra=0)
    t.pontos([(9, 7), (9, 8), (10, 9), (11, 9), (12, 8), (12, 7)], "cinza_escuro")
    t.contorno("sombra")
    PUNHO["papo_amarelo"], APOIO["papo_amarelo"], BOCA["papo_amarelo"] = (10, 7), (17, 7), (29, 3)
    return t


def estilingue():
    t = Tela(W, H)
    t.cel(t.capsula(12, 7, 12, 11.5, 1.3), MADEIRA, sombra=1)
    t.cel(t.capsula(12, 7, 9.5, 1.5, 1.1), MADEIRA, sombra=1)
    t.cel(t.capsula(12, 7, 14.5, 1.5, 1.1), MADEIRA, sombra=1)
    t.contorno("sombra")
    t.linha(9, 1, 5, 4, "vermelho_medio")
    t.linha(15, 1, 6, 5, "vermelho_esc")
    t.cel(t.elipse(5, 5, 1.6, 1.4), ["sombra", "cinza_escuro", "cinza", "cinza_claro"], sombra=0)
    PUNHO["estilingue"], APOIO["estilingue"], BOCA["estilingue"] = (12, 9), (5, 5), (14, 2)
    return t


def buscape():
    t = Tela(W, H)
    for k, (y, rampa) in enumerate([(0.5, VERMELHO), (3, PAPEL), (5.5, AZUL)]):
        x = 3 + (k % 2) * 2
        t.cel(t.retangulo(x, y, 18, 2.4), rampa, sombra=0)
        t.cel(t.poligono([(x + 18, y), (x + 21, y + 1.2), (x + 18, y + 2.4)]), ACO, sombra=0)
    t.cel(t.retangulo(2, 8, 20, 1.6), MADEIRA, sombra=0)
    for x in (7, 18):
        t.cel(t.retangulo(x, 0.5, 1.5, 9), MADEIRA_ESC, sombra=0)
    punho(t, 10, 8.5)
    t.contorno("sombra")
    t.pontos([(1, 2), (0, 5), (1, 7)], "amarelo_fogo")
    PUNHO["buscape"], APOIO["buscape"], BOCA["buscape"] = (11, 9), (17, 9), (27, 4)
    return t


ARMAS = {
    "madsen": madsen, "bacamarte": bacamarte, "rojao": rojao, "desintegrador": desintegrador,
    "candeeiro": candeeiro, "papo_amarelo": papo_amarelo, "estilingue": estilingue, "buscape": buscape,
}


def desenhar():
    """Desenha todas as armas e preenche PUNHO, APOIO e BOCA."""
    return {n: f() for n, f in ARMAS.items()}


if __name__ == "__main__":
    pixel.salvar("armas.txt", desenhar())
    print("tools/arte/pixel/armas.txt atualizado")
