"""Armas vistas de lado (cano para a direita), desenhadas pixel a pixel em
tools/arte/pixel/armas_mao.txt (até 32x15), no tamanho e detalhe das armas do
Metal Slug: coronha, ferrolho, gatilho, pente, braçadeiras e brilho.

Uso: python3 tools/arte/armas.py
Cada arma tem PUNHO (onde a mão de trás segura), APOIO (onde a mão da frente
segura por baixo) e BOCA (de onde sai o tiro), em pixels do desenho.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela  # noqa: E402
import pixel  # noqa: E402

W, H = 32, 15

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


# Âncoras de cada arma no desenho de tools/arte/pixel/armas_mao.txt:
# punho (mão de trás no cabo), apoio (mão da frente por baixo) e boca do cano.
ANCORAS = {
    "pistola": ((3, 8), (3, 8), (22, 2)),
    "madsen": ((11, 10), (21, 9), (31, 6)),
    "bacamarte": ((7, 10), (17, 9), (29, 5)),
    "papo_amarelo": ((10, 8), (19, 8), (31, 3)),
    "rojao": ((9, 8), (18, 8), (30, 3)),
    "desintegrador": ((5, 10), (14, 9), (27, 6)),
    "candeeiro": ((14, 9), (22, 9), (30, 7)),
    "estilingue": ((9, 9), (9, 9), (9, 1)),
    "buscape": ((6, 13), (16, 13), (25, 5)),
}
# Pontas da forquilha da baladeira (onde a liga prende).
LIGA = [(6, 2), (13, 2)]


def _carregar():
    desenhos = pixel.ler("armas_mao.txt")
    for nome, (p, a, b) in ANCORAS.items():
        PUNHO[nome], APOIO[nome], BOCA[nome] = p, a, b
    return desenhos


_DESENHOS = None


def _arma(nome):
    def f():
        global _DESENHOS
        if _DESENHOS is None:
            _DESENHOS = _carregar()
        return _DESENHOS[nome]
    return f


ARMAS = {n: _arma(n) for n in ANCORAS}


def desenhar():
    """Desenha todas as armas e preenche PUNHO, APOIO e BOCA."""
    return {n: f() for n, f in ARMAS.items()}



