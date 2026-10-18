"""Comidas do sertão que dão pontos (como as frutas e comidas do Metal Slug).
Comer muitas seguidas deixa o Lampião gordo. Cada função devolve uma Tela.
Usado por tools/arte/exportar.py (assets/sprites/comida_<nome>.png).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela  # noqa: E402

PALHA = ["couro_escuro", "ouro_escuro", "areia_media", "areia", "areia_luz"]
RAPADURA = ["couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz"]
QUEIJO = ["ouro_escuro", "areia_media", "areia", "areia_luz", "areia_clara"]
TOSTADO = ["couro_profundo", "couro", "laranja_escuro", "ouro_escuro"]
MILHO = ["laranja_escuro", "ouro_escuro", "amarelo_fogo", "amarelo_claro"]
BARRO = ["vermelho_esc", "terra_escura", "terra", "barro", "terra_media"]
CAJA = ["vermelho_esc", "vermelho_medio", "laranja_fogo", "amarelo_fogo"]
FOLHA = ["sombra", "caatinga_esc", "caatinga", "mandacaru"]


def caja():
    """Cajá: frutinha amarela e laranja com folhinha."""
    t = Tela(14, 14)
    for cx, cy in ((5, 8), (9, 9)):
        t.volume(t.elipse(cx, cy, 3.6, 4), CAJA, achatado=2, suave=0.5, ambiente=0.3)
        t.ponto(cx - 1, cy - 2, "amarelo_claro")
    t.volume(t.elipse(9, 3, 3, 1.6, ang=-0.5), FOLHA, achatado=1, suave=0.3)
    t.linha(7, 4, 7, 6, "couro_escuro")
    t.contorno("sombra")
    return t


def rapadura():
    """Rapadura embrulhada em palha de bananeira, amarrada com barbante."""
    t = Tela(18, 12)
    t.volume(t.retangulo(1, 2, 16, 9), PALHA, achatado=2, suave=0.5, ambiente=0.3, textura=0.15, semente=2)
    t.volume(t.retangulo(5, 3, 9, 7), RAPADURA, achatado=2, suave=0.5, ambiente=0.25, textura=0.2, semente=3)
    t.linha(9, 1, 9, 11, "couro_luz")
    t.linha(1, 6, 17, 6, "couro_luz")
    t.contorno("sombra")
    return t


def queijo():
    """Queijo coalho no espeto, tostado na brasa."""
    t = Tela(10, 20)
    t.volume(t.capsula(5, 19, 5, 10, 0.8), ["couro_escuro", "couro", "couro_claro"], achatado=1, suave=0.3)
    t.volume(t.retangulo(1, 1, 8, 11), QUEIJO, achatado=2, suave=0.5, ambiente=0.35)
    for y in (3, 7):
        t.linha(1, y, 8, y + 1, "couro")  # marcas da grelha
        t.linha(1, y + 1, 8, y + 2, "laranja_escuro")
    t.contorno("sombra")
    return t


def cuscuz():
    """Cuscuz de milho num prato de barro, com manteiga derretendo."""
    t = Tela(18, 15)
    t.volume(t.elipse(9, 12, 8.5, 2.6), BARRO, achatado=1.5, suave=0.4, ambiente=0.3)
    cus = t.elipse(9, 9, 6.5, 6) & (t.yy < 11.5)
    t.volume(cus, MILHO, achatado=3, suave=0.8, ambiente=0.3, textura=0.25, semente=5)
    t.chapado(t.elipse(9, 4.5, 2.5, 1.2), "amarelo_claro")
    t.ponto(8, 4, "branco")
    t.linha(10, 5, 11, 8, "amarelo_claro")
    t.contorno("sombra")
    return t


def buchada():
    """Buchada de bode fumegando numa panela de barro (vale muito)."""
    t = Tela(20, 18)
    t.volume(t.elipse(10, 12, 9, 5.5) & (t.yy > 8), BARRO, achatado=2.5, suave=0.6, ambiente=0.25)
    t.volume(t.elipse(10, 9, 8, 2.2), ["couro_profundo", "couro_escuro", "couro", "couro_medio"], achatado=1,
             suave=0.3, ambiente=0.3)
    t.volume(t.elipse(10, 8, 4.5, 3) & (t.yy < 9), ["couro_escuro", "pele_sombra", "pele_media", "pele"],
             achatado=1.5, suave=0.4)
    for x in (1, 18):
        t.volume(t.elipse(x, 10, 1.5, 1.2), BARRO, achatado=1, suave=0.2)  # alças
    t.contorno("sombra")
    for k, x in enumerate((7, 11, 14)):  # fumaça
        t.linha(x, 4 - k % 2, x + 1, 1, "cinza_luz")
    return t


COMIDAS = {
    "caja": (caja, 100),
    "rapadura": (rapadura, 300),
    "queijo": (queijo, 500),
    "cuscuz": (cuscuz, 1000),
    "buchada": (buchada, 2000),
}
