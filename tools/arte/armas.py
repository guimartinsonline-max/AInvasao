"""Armas vistas de lado (cano para a direita), desenhadas com o motor e salvas
em tools/arte/pixel/armas.txt para retoque à mão.

Uso: python3 tools/arte/armas.py
PROPOSTA: aguardando aprovação do Guilherme antes de entrar no jogo.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela  # noqa: E402
import pixel  # noqa: E402

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


def coronha(t, x0, y0, comprimento=10, rampa=MADEIRA):
    """Coronha de madeira em cunha, encostando no corpo da arma em x0."""
    t.cel(t.poligono([(x0 - comprimento, y0 - 1), (x0, y0), (x0, y0 + 4), (x0 - comprimento + 2, y0 + 6),
                      (x0 - comprimento, y0 + 5)]), rampa, sombra=1)


def punho(t, x, y, rampa=MADEIRA_ESC):
    t.cel(t.poligono([(x, y), (x + 4, y), (x + 3, y + 5), (x - 1, y + 5)]), rampa, sombra=1)


def gatilho(t, x, y):
    t.pontos([(x, y), (x, y + 1), (x + 1, y + 2), (x + 2, y + 2), (x + 3, y + 1)], "sombra")
    t.ponto(x + 1, y, "cinza_claro")


def madsen():
    t = Tela(40, 16)
    coronha(t, 10, 7)
    punho(t, 12, 10)
    gatilho(t, 15, 10)
    # Carregador curvo em cima (marca da Madsen).
    t.cel(t.poligono([(13, 7), (18, 7), (20, 1.5), (19, 0), (16, 0), (15, 3)]), ACO_ESC, sombra=1)
    t.linha(17, 1, 16, 5, "cinza")
    t.cel(t.retangulo(10, 6, 10, 5), ACO)
    # Camisa do cano com furos de refrigeração.
    t.cel(t.retangulo(20, 7, 14, 3), ACO, sombra=1)
    for x in range(21, 33, 2):
        t.ponto(x, 8, "sombra")
    t.cel(t.retangulo(34, 8, 3, 1), ACO_ESC, sombra=0)
    t.cel(t.retangulo(36, 6, 3, 5), ACO_ESC, sombra=1)
    # Bipé dobrado embaixo do cano.
    t.linha(22, 11, 34, 11, "cinza_escuro")
    t.pontos([(22, 12), (34, 12)], "sombra")
    t.pontos([(27, 6), (37, 5)], "cinza")
    t.contorno("sombra")
    return t


def bacamarte():
    t = Tela(40, 16)
    coronha(t, 11, 7, 11)
    # Forro de madeira embaixo do cano.
    t.cel(t.retangulo(12, 10, 15, 2), MADEIRA_ESC, sombra=1)
    t.cel(t.retangulo(11, 7, 21, 3), LATAO, sombra=1)
    for x in (16, 22, 28):
        t.chapado(t.retangulo(x, 7, 1, 3), "laranja_escuro")
    # Boca de sino.
    t.cel(t.poligono([(31, 7), (38, 2.5), (40, 2.5), (40, 13.5), (38, 13.5), (31, 10)]), LATAO, sombra=1)
    t.linha(39, 4, 39, 12, "couro_profundo")
    t.linha(38, 5, 38, 11, "couro_escuro")
    # Fecho de pederneira com o cão.
    t.cel(t.retangulo(10, 7, 4, 3), ACO, sombra=1)
    t.linha(11, 6, 12, 4, "cinza_escuro")
    t.ponto(13, 4, "cinza_claro")
    gatilho(t, 12, 10)
    t.contorno("sombra")
    return t


def rojao():
    t = Tela(40, 16)
    punho(t, 14, 11)
    # Tubo de papel com faixas de festa junina.
    t.cel(t.retangulo(3, 4, 29, 7), VERMELHO, sombra=2)
    for x in range(6, 30, 8):
        t.cel(t.poligono([(x, 4), (x + 4, 4), (x + 2, 11), (x - 2, 11)]), PAPEL, sombra=1, linha=False)
    for x in (3, 31):
        t.cel(t.retangulo(x, 3, 2, 9), MADEIRA_ESC, sombra=1)
    # Ponta do foguete saindo do tubo.
    t.cel(t.poligono([(33, 5), (36, 5), (39, 7.5), (36, 10), (33, 10)]), ACO, sombra=1)
    t.ponto(37, 7, "branco")
    # Pavio aceso atrás.
    t.linha(2, 7, 0, 9, "couro_escuro")
    t.pontos([(0, 10), (1, 11)], "amarelo_fogo")
    t.ponto(0, 11, "branco")
    t.contorno("sombra")
    t.pontos([(0, 12), (2, 12)], "amarelo_claro")
    return t


def desintegrador():
    t = Tela(40, 16)
    t.cel(t.poligono([(8, 9), (13, 9), (11, 15), (6, 15)]), ROXO, sombra=1)
    t.cel(t.elipse(15, 7, 10, 4), LILAS, sombra=2)
    t.cel(t.retangulo(23, 6, 10, 3), ROXO, sombra=1)
    for x in (25, 29):
        t.cel(t.retangulo(x, 3, 2, 9), LILAS, sombra=1)
    t.cel(t.elipse(34.5, 7.5, 2.5, 2.5), ALIEN, sombra=1)
    t.ponto(34, 6, "branco")
    # Bulbo de vidro verde em cima, com gosma brilhando.
    t.cel(t.elipse(14, 3, 3.2, 3), ALIEN, sombra=1)
    t.ponto(13, 1, "branco")
    for x in (9, 12, 15, 18):
        t.ponto(x, 8, "alien_brilho")
    t.contorno("sombra")
    return t


def candeeiro():
    t = Tela(40, 16)
    coronha(t, 9, 8, 9)
    # Lata de querosene amarrada na arma.
    t.cel(t.retangulo(9, 1, 10, 10), VERMELHO, sombra=2)
    t.cel(t.retangulo(10, 4, 8, 4), PAPEL, sombra=1, linha=False)
    t.chapado(t.retangulo(12, 5, 4, 1), "couro_profundo")
    t.chapado(t.retangulo(11, 6, 6, 1), "couro_escuro")
    t.cel(t.retangulo(12, 0, 3, 2), ACO, sombra=0)
    # Cano de ferro com a boca de latão.
    t.cel(t.retangulo(19, 7, 14, 3), ACO, sombra=1)
    t.cel(t.retangulo(33, 6, 4, 5), LATAO, sombra=1)
    punho(t, 20, 10)
    gatilho(t, 23, 10)
    t.contorno("sombra")
    # Chama-piloto acesa na boca.
    t.pontos([(38, 9), (38, 10), (39, 10)], "laranja_fogo")
    t.ponto(38, 11, "amarelo_fogo")
    return t


def papo_amarelo():
    t = Tela(40, 16)
    coronha(t, 11, 6, 11)
    # Caixa da culatra de latão: o "papo amarelo" da Winchester.
    t.cel(t.poligono([(11, 5), (18, 5), (18, 10), (12, 10), (11, 9)]), LATAO, sombra=1)
    t.ponto(13, 6, "branco")
    t.cel(t.retangulo(18, 5, 21, 2), ACO, sombra=0)
    t.cel(t.retangulo(18, 7, 16, 1), ACO_ESC, sombra=0)
    t.cel(t.retangulo(18, 8, 9, 2), MADEIRA, sombra=1)
    # Alavanca de recarregar.
    t.pontos([(12, 10), (12, 11), (12, 12), (13, 13), (14, 13), (15, 13), (16, 12), (16, 11)], "cinza_escuro")
    t.ponto(38, 4, "cinza")
    t.contorno("sombra")
    return t


def estilingue():
    t = Tela(40, 16)
    t.cel(t.capsula(19, 9, 19, 15, 1.6), MADEIRA, sombra=1)
    t.cel(t.capsula(19, 9, 15, 2, 1.4), MADEIRA, sombra=1)
    t.cel(t.capsula(19, 9, 23, 2, 1.4), MADEIRA, sombra=1)
    t.cel(t.retangulo(17, 12, 5, 2), MADEIRA_ESC, sombra=0)
    t.contorno("sombra")
    # Liga de borracha esticada com a pedra na bolsa de couro.
    t.linha(15, 2, 9, 6, "vermelho_medio")
    t.linha(23, 2, 11, 7, "vermelho_esc")
    t.cel(t.elipse(9, 7, 2.2, 2), ["sombra", "cinza_escuro", "cinza", "cinza_claro"], sombra=1)
    t.chapado(t.retangulo(8, 8, 3, 1), "couro_escuro")
    return t


def buscape():
    t = Tela(40, 16)
    punho(t, 15, 11)
    # Três buscapés num suporte de madeira, cada um de uma cor.
    for k, (y, rampa) in enumerate([(1, VERMELHO), (4, PAPEL), (7, AZUL)]):
        x = 6 + (k % 2) * 2
        t.cel(t.retangulo(x, y, 22, 3), rampa, sombra=1)
        t.cel(t.poligono([(x + 22, y), (x + 25, y + 1.5), (x + 22, y + 3)]), ACO, sombra=0)
        t.ponto(x - 1, y + 1, "couro_escuro")
    t.cel(t.retangulo(4, 10, 26, 2), MADEIRA, sombra=1)
    for x in (9, 23):
        t.cel(t.retangulo(x, 1, 2, 10), MADEIRA_ESC, sombra=1)
    t.contorno("sombra")
    t.pontos([(2, 2), (3, 6), (1, 9)], "amarelo_fogo")
    t.pontos([(1, 3), (2, 8)], "branco")
    return t


ARMAS = {
    "madsen": madsen, "bacamarte": bacamarte, "rojao": rojao, "desintegrador": desintegrador,
    "candeeiro": candeeiro, "papo_amarelo": papo_amarelo, "estilingue": estilingue, "buscape": buscape,
}

if __name__ == "__main__":
    pixel.salvar("armas.txt", {n: f() for n, f in ARMAS.items()})
    print("tools/arte/pixel/armas.txt atualizado")
