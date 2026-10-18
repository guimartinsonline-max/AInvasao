"""Chefe da fase 1: o trem blindado da Volante ("A JARARACA"), locomotiva da
Great Western coberta de chapas, virada para a esquerda (de frente para o
Lampião), com um vagão de soldados atrás. Partes que quebram separadas são
desenhos à parte: metralhadoras do limpa-trilhos, chaminé (cospe carvão em
brasa), torre do canhão na cabine e a porta da fornalha (o ponto fraco).

Coordenadas dos encaixes das partes em PARTES (canto de cima à esquerda da
locomotiva). Usado por tools/arte/exportar.py.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from motor import BAYER4, IDX, Tela  # noqa: E402
import veiculos as vc  # noqa: E402

OLIVA = ["preto", "sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru"]
FERRO = ["preto", "sombra", "azul_sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]
LATAO = ["couro_profundo", "ouro_escuro", "amarelo_fogo", "amarelo_claro"]
VERMELHO = ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"]
MADEIRA = ["couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz"]

W, H = 210, 116
CHAO = H - 1
# Encaixes das partes (x, y do canto de cima à esquerda) na locomotiva.
PARTES = {
    "mg": (2, 58),        # metralhadoras no limpa-trilhos (16 x 30)
    "chamine": (34, 2),   # chaminé (22 x 40)
    "torre": (156, 0),    # torre do canhão no teto da cabine (44 x 26)
    "porta": (8, 46),     # porta da fornalha na frente (24 x 30): o ponto fraco
}


def rebites(t, pts, luz="cinza_claro", sombra="sombra"):
    for x, y in pts:
        t.ponto(x, y, luz)
        t.ponto(x, y + 1, sombra)


def roda(t, cx, cy, r, quadro):
    t.volume(t.elipse(cx, cy, r, r), FERRO, achatado=2, suave=0.6, ambiente=0.2)
    t.chapado(t.elipse(cx, cy, r - 2, r - 2), "sombra")
    for k in range(8):
        a = k / 8 * math.pi + quadro * math.pi / 16
        t.linha(cx - math.cos(a) * (r - 2), cy - math.sin(a) * (r - 2), cx + math.cos(a) * (r - 2), cy + math.sin(a) * (r - 2),
                "cinza_medio")
    t.volume(t.elipse(cx, cy, r * 0.3, r * 0.3), VERMELHO, achatado=1, suave=0.3)
    t.ponto(cx, cy, "amarelo_claro")


def locomotiva(quadro=0, giro=None, biela=None):
    """0 e 1: rodas girando; 2: destruída (queimada, chapas arrancadas)."""
    t = Tela(W, H)
    q = quadro if quadro < 2 else 0
    # Cabine blindada atrás (à direita) com seteiras.
    cab = t.retangulo(150, 22, 58, 72)
    t.volume(cab, OLIVA, achatado=4, suave=1.0, ambiente=0.25, textura=0.0, semente=3)
    t.volume(t.retangulo(146, 18, 64, 6), FERRO, achatado=1.5, suave=0.4)  # beiral do teto
    for x in (160, 178, 196):
        t.chapado(t.retangulo(x, 36, 9, 3), "preto")
        t.ponto(x + 1, 36, "laranja_escuro")
    rebites(t, [(x, y) for x in range(153, 207, 6) for y in (27, 60, 88)])
    t.linha(150, 58, 208, 58, "caatinga_esc")
    # Caldeira comprida coberta de chapas, com anéis de latão.
    caldeira = t.retangulo(24, 38, 128, 48) | t.elipse(24, 62, 10, 24)
    t.volume(caldeira, OLIVA, achatado=8, suave=2.0, ambiente=0.25, textura=0.0, semente=5, luz=(-0.3, -0.9))
    for x in (54, 86, 118):
        t.volume(t.retangulo(x, 38, 4, 48), LATAO, achatado=1, suave=0.3)
    for x in range(30, 150, 8):
        rebites(t, [(x, 42), (x + 4, 80)])
    # Estrela branca e o nome pintado (faixa).
    est_c = (100, 60)
    est = t.poligono([(est_c[0] + math.cos(a) * (7 if k % 2 == 0 else 2.8), est_c[1] + math.sin(a) * (7 if k % 2 == 0 else 2.8))
                      for k, a in enumerate(np.linspace(-math.pi / 2, 3 * math.pi / 2, 11)[:-1])])
    t.chapado(est, "branco")
    t.chapado(t.retangulo(62, 70, 76, 7), "vermelho_esc")
    for x in range(64, 136, 4):
        t.chapado(t.retangulo(x, 72, 2, 3), "amarelo_claro")  # letreiro (riscos de tinta)
    # Domos de vapor e de areia no alto.
    for cx in (84, 120):
        t.volume(t.elipse(cx, 36, 9, 7) & (t.yy < 40), LATAO, achatado=2, suave=0.5, ambiente=0.3)
    # Caixa de fumaça na frente (onde fica a porta da fornalha) e farol.
    t.volume(t.retangulo(6, 40, 26, 46), FERRO, achatado=3, suave=0.8, ambiente=0.2)
    t.volume(t.retangulo(10, 30, 12, 10), FERRO, achatado=1.5, suave=0.4)
    t.volume(t.elipse(16, 30, 6, 5), LATAO, achatado=1.5, suave=0.4, ambiente=0.3)
    t.chapado(t.elipse(12, 30, 3, 3.5), "amarelo_claro")
    t.ponto(11, 29, "branco")
    # Estrutura, cilindros e tubos.
    t.volume(t.retangulo(0, 84, 152, 8), FERRO, achatado=1.5, suave=0.4)
    t.volume(t.retangulo(30, 72, 26, 14), FERRO, achatado=2, suave=0.5, ambiente=0.3)  # cilindro
    t.linha(30, 66, 150, 66, "cinza_escuro")
    t.linha(30, 67, 150, 67, "sombra")
    # Limpa-trilhos: grade em cunha na frente.
    limpa = t.poligono([(0, 112), (10, 88), (36, 88), (36, 112)])
    t.volume(limpa, VERMELHO, achatado=2, suave=0.5, ambiente=0.2)
    for x in range(4, 36, 4):
        t.linha(x, 90, x - 3, 111, "vermelho_esc")
    # Rodas: dianteiras pequenas e as motrizes grandes, com a biela.
    for cx in (22, 42):
        roda(t, cx, CHAO - 8, 8, q if giro is None else giro)
    motrizes = (74, 108, 142)
    for cx in motrizes:
        roda(t, cx, CHAO - 15, 15, q if giro is None else giro)
    a = (q if biela is None else biela) * math.pi / 2
    ox, oy = math.cos(a) * 8, math.sin(a) * 8
    t.volume(t.capsula(motrizes[0] + ox, CHAO - 15 + oy, motrizes[-1] + ox, CHAO - 15 + oy, 2), FERRO, achatado=1, suave=0.3)
    t.volume(t.capsula(43, 79, motrizes[0] + ox, CHAO - 15 + oy, 1.8), FERRO, achatado=1, suave=0.3)
    t.contorno("sombra")
    # Poeira e graxa na parte de baixo.
    for y in range(78, 92):
        for x in range(0, 152):
            if t.px[y, x] >= 0 and BAYER4[y % 4, x % 4] < (y - 78) / 26:
                t.px[y, x] = IDX["sombra_media"]
    if quadro == 2:
        vc.queimar(t, 21)
    return t


def mg(quadro=0):
    """Duas metralhadoras no limpa-trilhos. 1: atirando (cano clareado); 2: arrebentadas."""
    t = Tela(16, 30)
    for y in (6, 20):
        t.volume(t.elipse(10, y, 6, 5), OLIVA, achatado=2, suave=0.5, ambiente=0.3)
        if quadro == 2:
            t.chapado(t.elipse(9, y, 3, 2.5), "preto")
            t.ponto(9, y, "laranja_fogo")
        else:
            t.volume(t.capsula(0, y, 8, y, 1.6), FERRO, achatado=1, suave=0.3)
            if quadro == 1:
                t.chapado(t.elipse(1, y, 1.8, 1.8), "amarelo_claro")
    t.contorno("sombra")
    return t


def chamine(quadro=0):
    """Chaminé alta de boca larga. 1: brasa acesa (vai cuspir); 2: quebrada pela metade."""
    t = Tela(22, 40)
    if quadro == 2:
        t.volume(t.retangulo(5, 24, 12, 16), FERRO, achatado=1.5, suave=0.4)
        for x in range(5, 17, 3):
            t.ponto(x, 24 - (x % 2) * 2, "cinza_luz")
        t.chapado(t.elipse(11, 25, 4, 1.5), "preto")
    else:
        t.volume(t.retangulo(6, 10, 10, 30), FERRO, achatado=2, suave=0.5, ambiente=0.25)
        boca = t.poligono([(0, 0), (22, 0), (17, 11), (5, 11)])
        t.volume(boca, FERRO, achatado=2, suave=0.5, ambiente=0.3)
        t.chapado(t.elipse(11, 1.5, 9, 1.6), "laranja_fogo" if quadro == 1 else "preto")
        t.volume(t.retangulo(5, 30, 12, 3), LATAO, achatado=1, suave=0.3)
    t.contorno("sombra")
    return t


def torre(quadro=0):
    """Torre do canhão no teto da cabine. 1: canhão recuado (tiro); 2: arrebentada."""
    t = Tela(44, 26)
    corpo = t.poligono([(8, 26), (10, 10), (18, 6), (34, 6), (40, 12), (42, 26)])
    t.volume(corpo, OLIVA, achatado=3, suave=0.8, ambiente=0.3, textura=0.0, semente=4)
    rebites(t, [(x, 22) for x in range(12, 40, 5)])
    if quadro == 2:
        t.chapado(t.elipse(25, 14, 7, 5), "preto")
        t.chapado(t.elipse(25, 14, 3.5, 2.5), "laranja_fogo")
        t.volume(t.capsula(2, 14, 10, 15, 2), FERRO, achatado=1, suave=0.3)
    else:
        r = 3 if quadro == 1 else 0
        t.volume(t.capsula(0 + r, 13, 14 + r, 13, 2.6), FERRO, achatado=1, suave=0.3, brilho=1.1)
        t.volume(t.retangulo(0 + r, 10, 4, 7), FERRO, achatado=1, suave=0.3)
        t.chapado(t.retangulo(26, 11, 8, 2), "preto")
    t.contorno("sombra")
    return t


def porta(quadro=0):
    """Porta da fornalha: 0 fechada (chapa grossa), 1 aberta com o fogo da caldeira à mostra (ponto fraco)."""
    t = Tela(24, 30)
    if quadro == 0:
        t.volume(t.elipse(12, 15, 11, 14), FERRO, achatado=3, suave=0.7, ambiente=0.3, brilho=1.1)
        rebites(t, [(12 + math.cos(a) * 8, 15 + math.sin(a) * 11) for a in np.linspace(0, 2 * math.pi, 9)[:-1]])
        t.volume(t.retangulo(3, 13, 18, 3), LATAO, achatado=1, suave=0.3)
    else:
        t.chapado(t.elipse(12, 15, 11, 14), "preto")
        t.volume(t.elipse(12, 16, 9, 11), ["vermelho_esc", "vermelho_medio", "laranja_fogo", "amarelo_fogo", "amarelo_claro"],
                 achatado=4, suave=1.2, ambiente=0.4, brilho=1.3)
        t.chapado(t.elipse(12, 18, 4, 5), "branco")
        for x in (6, 18):
            t.linha(x, 4, x, 26, "sombra")  # grelha
    t.contorno("sombra")
    return t


def vagao(quadro=0, giro=0):
    """Vagão de soldados atrás da locomotiva: chapas, sacos de areia em cima. 1: destruído."""
    t = Tela(150, 92)
    corpo = t.retangulo(4, 30, 144, 50)
    t.volume(corpo, OLIVA, achatado=4, suave=1.0, ambiente=0.25, textura=0.0, semente=8)
    for x in range(10, 146, 8):
        rebites(t, [(x, 34), (x, 76)])
    for x in (30, 70, 110):
        t.chapado(t.retangulo(x, 44, 12, 3), "preto")
    # Sacos de areia na beira de cima (onde os soldados ficam).
    for k in range(11):
        x = 8 + k * 13
        t.volume(t.elipse(x + 6, 27, 7, 4), ["terra_escura", "terra", "terra_media", "areia_media", "areia"], achatado=2,
                 suave=0.6, ambiente=0.2, textura=0.2, semente=k)
    t.volume(t.retangulo(0, 80, 150, 5), FERRO, achatado=1.5, suave=0.4)
    for cx in (28, 52, 98, 122):
        roda(t, cx, 91 - 8, 8, giro)
    t.contorno("sombra")
    if quadro == 1:
        vc.queimar(t, 9)
    return t


def carvao(quadro=0):
    """Carvão em brasa que a chaminé cospe (2 quadros)."""
    t = Tela(8, 8)
    t.volume(t.elipse(4, 4, 3.4, 3), ["preto", "sombra", "sombra_media"], achatado=1, suave=0.3)
    for (x, y) in ((3, 3), (5, 4)) if quadro == 0 else ((4, 2), (2, 5)):
        t.ponto(x, y, "laranja_fogo")
    t.ponto(4, 4, "amarelo_fogo")
    return t


def trilhos(w):
    """Trilhos no chão: dormentes de madeira e dois trilhos de aço (vistos de lado)."""
    t = Tela(w, 8)
    for x in range(0, w, 10):
        t.volume(t.retangulo(x, 3, 8, 4), MADEIRA, achatado=1, suave=0.3)
    t.volume(t.retangulo(0, 1, w, 2.5), FERRO, achatado=1, suave=0.3, brilho=1.2)
    t.linha(0, 1, w - 1, 1, "cinza_claro")
    return t
