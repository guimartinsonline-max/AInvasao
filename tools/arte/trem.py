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


COBRE = ["couro_escuro", "laranja_escuro", "laranja_fogo", "amarelo_fogo", "amarelo_claro"]
LUZ_JANELA = ["laranja_escuro", "laranja_fogo", "amarelo_fogo", "amarelo_claro"]
SACO = ["terra_escura", "terra", "terra_media", "areia_media", "areia"]
LISTRA = ("amarelo_fogo", "preto")


def janela_acesa(t, x, y, w, h, figura=True, semente=0):
    """Janela com luz quente lá dentro (como as do Metal Slug) e um soldado de quepe
    em contraluz; moldura de chapa e grade."""
    t.volume(t.retangulo(x - 1, y - 1, w + 2, h + 2), FERRO, achatado=1, suave=0.3)
    t.volume(t.retangulo(x, y, w, h), LUZ_JANELA, achatado=2, suave=0.8, ambiente=0.55, brilho=1.3,
             luz=(0.0, 0.9), linha=False)
    if figura:
        cx = x + w * (0.35 + 0.3 * ((semente * 7) % 3) / 2)
        t.chapado(t.elipse(cx, y + h * 0.62, w * 0.22, h * 0.32), "marrom_noite")  # cabeça
        t.chapado(t.retangulo(cx - w * 0.3, y + h * 0.35, w * 0.6, h * 0.12), "marrom_noite")  # aba do quepe
        t.chapado(t.elipse(cx, y + h * 0.36, w * 0.2, h * 0.14), "marrom_noite")
        t.chapado(t.retangulo(cx - w * 0.35, y + h * 0.9, w * 0.7, h * 0.1), "marrom_noite")  # ombros
    for gx in range(int(x) + 3, int(x + w), 4):
        t.linha(gx, y, gx, y + h - 1, "sombra")  # grade
    t.linha(x, y, x + w - 1, y, "cinza_luz")


def listrado(t, mascara, passo=4):
    """Faixa de aviso amarela e preta em diagonal."""
    xi, yi = t.xx.astype(int), t.yy.astype(int)
    t.px[mascara & (((xi + yi) // passo) % 2 == 0)] = IDX[LISTRA[0]]
    t.px[mascara & (((xi + yi) // passo) % 2 == 1)] = IDX[LISTRA[1]]


def cano(t, pts, r=1.2, rampa=None):
    """Tubulação com flanges nas emendas."""
    rampa = rampa or COBRE
    for a, b in zip(pts, pts[1:]):
        t.volume(t.capsula(a[0], a[1], b[0], b[1], r), rampa, achatado=1, suave=0.3, brilho=1.2)
    for p in pts[1:-1]:
        t.volume(t.elipse(p[0], p[1], r + 0.9, r + 0.9), FERRO, achatado=1, suave=0.3)


def valvula(t, x, y):
    """Volante de válvula vermelho com raios."""
    t.volume(t.elipse(x, y, 3.2, 1.6), VERMELHO, achatado=1, suave=0.3, brilho=1.2)
    t.linha(x - 2, y, x + 2, y, "vermelho_esc")
    t.volume(t.retangulo(x - 0.5, y + 1, 1.5, 3), FERRO, achatado=0.5, suave=0.2)


def sacos(t, x, y, n, semente=0):
    for k in range(n):
        t.volume(t.elipse(x + k * 7 + 3.5, y, 4.2, 2.8), SACO, achatado=1.5, suave=0.5, ambiente=0.25,
                 textura=0.25, semente=semente + k)
        t.linha(x + k * 7 + 1, y - 1, x + k * 7 + 5, y - 1, "areia_luz")


def roda_motriz(t, cx, cy, r, quadro):
    """Roda motriz com aro claro, raios, contrapeso em meia-lua e cubo vermelho."""
    t.volume(t.elipse(cx, cy, r, r), FERRO, achatado=2, suave=0.6, ambiente=0.2)
    t.chapado(t.elipse(cx, cy, r - 2, r - 2), "sombra")
    a0 = quadro * math.pi / 8
    n = 10 if r > 10 else 8
    for k in range(n):
        a = k / n * 2 * math.pi + a0
        t.linha(cx, cy, cx + math.cos(a) * (r - 2), cy + math.sin(a) * (r - 2), "cinza_medio")
    # Contrapeso (meia-lua) girando junto.
    cp = t.elipse(cx + math.cos(a0 + math.pi) * r * 0.45, cy + math.sin(a0 + math.pi) * r * 0.45, r * 0.45, r * 0.45)
    t.chapado(cp & t.elipse(cx, cy, r - 2, r - 2), "cinza_escuro")
    t.volume(t.elipse(cx, cy, r * 0.28, r * 0.28), VERMELHO, achatado=1, suave=0.3)
    t.ponto(cx, cy, "amarelo_claro")
    # Aro com brilho em cima.
    aro = t.elipse(cx, cy, r, r) & ~t.elipse(cx, cy, r - 1.2, r - 1.2) & (t.yy < cy - r * 0.3)
    t.chapado(aro, "cinza_luz")


def locomotiva(quadro=0, giro=None, biela=None):
    """0 e 1: rodas girando; 2: destruída. Locomotiva da Great Western blindada,
    virada para a esquerda, carregada de detalhe como as máquinas do Metal Slug."""
    t = Tela(W, H)
    q = quadro if quadro < 2 else 0
    g = q if giro is None else giro
    # ---- Cabine blindada (atrás, à direita): chapas, janelas acesas, escada, lanterna.
    cab = t.retangulo(150, 22, 58, 72)
    t.volume(cab, OLIVA, achatado=4, suave=1.0, ambiente=0.25, semente=3)
    t.volume(t.retangulo(146, 17, 64, 6), FERRO, achatado=1.5, suave=0.4)  # beiral do teto
    t.chapado(t.retangulo(146, 22, 64, 1), "sombra")
    janela_acesa(t, 156, 30, 14, 12, semente=1)
    janela_acesa(t, 176, 30, 12, 12, figura=False)
    t.chapado(t.retangulo(194, 30, 10, 3), "preto")  # seteira
    t.ponto(195, 30, "laranja_escuro")
    for x in range(152, 208, 5):
        rebites(t, [(x, 26), (x, 48), (x, 90)])
    for y in (47, 70):
        t.linha(150, y, 208, y, "caatinga_esc")
        t.linha(150, y + 1, 208, y + 1, "mandacaru")
    # Porta de correr com puxador e a placa de número de latão.
    t.volume(t.retangulo(182, 52, 16, 36), OLIVA, achatado=1.5, suave=0.4, ambiente=0.15)
    t.chapado(t.retangulo(182, 52, 1, 36), "sombra")
    t.volume(t.retangulo(194, 66, 2, 6), LATAO, achatado=0.5, suave=0.2)
    t.volume(t.retangulo(156, 56, 18, 10), LATAO, achatado=1, suave=0.3, brilho=1.2)
    t.chapado(t.retangulo(158, 58, 14, 6), "ouro_escuro")
    for x0 in (160, 165):  # "07" em relevo
        t.chapado(t.retangulo(x0, 59, 3, 4), "amarelo_claro")
        t.chapado(t.retangulo(x0 + 1, 60, 1, 2), "ouro_escuro")
    # Escada na traseira e lanterna vermelha.
    for y in range(52, 92, 5):
        t.linha(203, y, 208, y, "cinza_luz")
    t.linha(203, 50, 203, 92, "sombra")
    t.linha(208, 50, 208, 92, "sombra")
    t.volume(t.retangulo(198, 74, 6, 8), FERRO, achatado=1, suave=0.3)
    t.chapado(t.elipse(201, 78, 2, 2.5), "vermelho")
    t.ponto(200, 77, "laranja_fogo")
    # ---- Caldeira com brilho de metal, anéis de latão, saia blindada e corrimão.
    caldeira = t.retangulo(24, 38, 128, 46) | t.elipse(24, 61, 10, 23)
    t.volume(caldeira, OLIVA, achatado=9, suave=2.2, ambiente=0.25, semente=5, luz=(-0.2, -0.95), brilho=1.15)
    t.chapado(t.retangulo(28, 43, 122, 1) & caldeira, "mandacaru_luz")  # reflexo comprido
    for x in (50, 82, 114, 140):
        t.volume(t.retangulo(x, 38, 4, 46), LATAO, achatado=1, suave=0.3, brilho=1.2)
        t.ponto(x + 1, 41, "branco")
    for x in range(28, 150, 6):
        rebites(t, [(x, 50), (x + 3, 78)])
    saia = t.retangulo(24, 70, 128, 14)
    t.volume(saia, OLIVA, achatado=2, suave=0.6, ambiente=0.15, semente=6)
    for x in range(28, 152, 21):
        t.linha(x, 70, x, 83, "sombra")  # emendas das chapas
        t.linha(x + 1, 70, x + 1, 83, "mandacaru")
    t.linha(24, 70, 151, 70, "sombra")
    # Corrimão com as colunetas.
    t.linha(28, 46, 150, 46, "cinza_luz")
    t.linha(28, 47, 150, 47, "sombra")
    for x in range(32, 150, 14):
        t.linha(x, 47, x, 50, "cinza_medio")
    # Tubulação de cobre correndo pela caldeira, com flanges, e as válvulas.
    cano(t, [(40, 58), (66, 58), (70, 54), (130, 54), (134, 60), (148, 60)], r=1.7)
    cano(t, [(44, 65), (110, 65), (114, 68), (148, 68)], r=1.3, rampa=FERRO[2:])
    for x in (70, 104):
        valvula(t, x, 51)
    # Bomba de ar e o tambor do aquecedor no flanco.
    t.volume(t.retangulo(118, 56, 9, 14), FERRO, achatado=1.5, suave=0.4, brilho=1.1)
    for y in (58, 62, 66):
        t.linha(118, y, 126, y, "sombra")
    t.volume(t.capsula(58, 76, 96, 76, 3.2), FERRO, achatado=1.5, suave=0.4, brilho=1.1)
    # Estrela e faixa com o nome pintado.
    est_c = (96, 62)
    est = t.poligono([(est_c[0] + math.cos(a) * (6.5 if k % 2 == 0 else 2.6), est_c[1] + math.sin(a) * (6.5 if k % 2 == 0 else 2.6))
                      for k, a in enumerate(np.linspace(-math.pi / 2, 3 * math.pi / 2, 11)[:-1])])
    t.chapado(t.elipse(96, 62, 8, 8), "vermelho_esc")
    t.chapado(est, "branco")
    # ---- Domos, sino, apito e areia em cima.
    for cx in (80, 122):
        t.volume(t.elipse(cx, 36, 9, 7) & (t.yy < 40), LATAO, achatado=2, suave=0.5, ambiente=0.15, brilho=0.95)
        t.ponto(cx - 3, 31, "branco")
    t.volume(t.elipse(101, 34, 4, 4) & (t.yy < 38), LATAO, achatado=1.5, suave=0.4, brilho=1.3)  # sino
    t.linha(101, 28, 101, 30, "sombra")
    t.volume(t.retangulo(142, 26, 3, 12), LATAO, achatado=0.8, suave=0.3, brilho=1.3)  # apito
    t.volume(t.elipse(143.5, 26, 2.2, 1.6), LATAO, achatado=0.8, suave=0.3)
    sacos(t, 58, 35, 2, semente=3)
    # Rolo de arame farpado em cima da caldeira.
    for k in range(18):
        a = k * 1.1
        t.ponto(128 + k * 1.1, 34 + math.sin(a) * 2.5, "cinza")
        t.ponto(128 + k * 1.1 + 0.5, 34 + math.cos(a) * 2.5, "sombra")
    # ---- Caixa de fumaça na frente, farol grande e placa redonda.
    t.volume(t.retangulo(6, 40, 26, 46), FERRO, achatado=3, suave=0.8, ambiente=0.2)
    t.volume(t.retangulo(8, 30, 16, 10), FERRO, achatado=1.5, suave=0.4)
    t.volume(t.elipse(16, 29, 7.5, 6.5), LATAO, achatado=1.5, suave=0.4, ambiente=0.3, brilho=1.2)
    t.volume(t.elipse(13, 29, 4.5, 5), ["amarelo_fogo", "amarelo_claro", "branco"], achatado=1.5, suave=0.6,
             ambiente=0.6, luz=(-0.6, -0.4))
    t.ponto(11, 27, "branco")
    t.volume(t.elipse(19, 50, 6, 6), LATAO, achatado=1, suave=0.3)  # placa redonda
    t.chapado(t.elipse(19, 50, 4, 4), "vermelho_esc")
    t.chapado(t.retangulo(18, 48, 2, 4), "amarelo_claro")
    # ---- Estrutura: estribo listrado, cilindro com guias, biela e mecanismo.
    estribo = t.retangulo(0, 84, 152, 7)
    t.volume(estribo, FERRO, achatado=1.5, suave=0.4)
    listrado(t, t.retangulo(0, 85, 36, 5))
    t.linha(0, 84, 151, 84, "cinza_luz")
    t.volume(t.retangulo(28, 70, 30, 16), FERRO, achatado=2, suave=0.5, ambiente=0.3, brilho=1.1)  # cilindro
    for x in (31, 55):
        t.volume(t.elipse(x, 78, 3, 7), FERRO, achatado=1, suave=0.3, brilho=1.2)
    t.linha(58, 75, 92, 75, "cinza_luz")  # guias da cruzeta
    t.linha(58, 81, 92, 81, "cinza_luz")
    # Limpa-trilhos em cunha com listras e sacos de areia em cima.
    limpa = t.poligono([(0, 112), (10, 91), (36, 91), (36, 112)])
    t.volume(limpa, VERMELHO, achatado=2, suave=0.5, ambiente=0.2)
    for x in range(4, 36, 4):
        t.linha(x, 92, x - 3, 111, "vermelho_esc")
    # Rodas: dianteiras pequenas e motrizes grandes com contrapeso; biela e manivelas.
    for cx in (22, 42):
        roda_motriz(t, cx, CHAO - 8, 8, g)
    motrizes = (74, 108, 142)
    for cx in motrizes:
        roda_motriz(t, cx, CHAO - 15, 15, g)
    a = (q if biela is None else biela) * math.pi / 2
    ox, oy = math.cos(a) * 8, math.sin(a) * 8
    t.volume(t.capsula(motrizes[0] + ox, CHAO - 15 + oy, motrizes[-1] + ox, CHAO - 15 + oy, 2), FERRO, achatado=1, suave=0.3,
             brilho=1.2)
    t.volume(t.capsula(60, 78, motrizes[0] + ox, CHAO - 15 + oy, 1.8), FERRO, achatado=1, suave=0.3, brilho=1.2)
    for cx in motrizes:
        t.volume(t.elipse(cx + ox, CHAO - 15 + oy, 2.2, 2.2), LATAO, achatado=0.8, suave=0.3)
    t.contorno("sombra")
    # Graxa e poeira na parte de baixo; óleo pingando.
    for y in range(80, 94):
        for x in range(0, 152):
            if t.px[y, x] >= 0 and BAYER4[y % 4, x % 4] < (y - 80) / 26:
                t.px[y, x] = IDX["sombra_media"]
    for x in (48, 96, 130):
        t.linha(x, 92, x, 95 + (x % 3), "preto")
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
        t.volume(t.retangulo(6, 10, 10, 30), FERRO, achatado=2, suave=0.5, ambiente=0.25, brilho=1.15)
        t.chapado(t.retangulo(8, 12, 1, 26), "cinza_luz")  # reflexo
        boca = t.poligono([(0, 0), (22, 0), (17, 11), (5, 11)])
        t.volume(boca, FERRO, achatado=2, suave=0.5, ambiente=0.3, brilho=1.15)
        t.chapado(t.elipse(11, 1.5, 9, 1.6), "laranja_fogo" if quadro == 1 else "preto")
        # Tela de faíscas na boca e as cintas de latão rebitadas.
        for x in range(4, 19, 3):
            t.ponto(x, 1, "cinza" if quadro != 1 else "amarelo_claro")
        for y in (17, 30):
            t.volume(t.retangulo(5, y, 12, 3), LATAO, achatado=1, suave=0.3, brilho=1.2)
            rebites(t, [(7, y + 1), (11, y + 1), (15, y + 1)], luz="amarelo_claro")
        rebites(t, [(x, 7) for x in (3, 8, 13, 18)])
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
        # Canhão comprido com camisa de recuo, freio de boca e cintas.
        t.volume(t.capsula(0 + r, 13, 16 + r, 13, 2.8), FERRO, achatado=1, suave=0.3, brilho=1.2)
        t.volume(t.retangulo(0 + r, 9.5, 5, 7), FERRO, achatado=1, suave=0.3, brilho=1.1)
        for x in (8, 12):
            t.chapado(t.retangulo(x + r, 10, 1.2, 6), "sombra")
        t.chapado(t.retangulo(26, 11, 8, 2), "preto")  # visor
        # Escotilha aberta com o artilheiro de capacete espiando e a antena com flâmula.
        t.volume(t.elipse(30, 6, 5, 2), FERRO, achatado=1, suave=0.3)
        t.volume(t.elipse(30, 3, 3.2, 3) & (t.yy < 5), ["sombra", "caatinga_esc", "caatinga_media"], achatado=1, suave=0.3)
        t.chapado(t.retangulo(27, 4, 6, 1), "sombra")
        t.ponto(31, 5, "pele")
        t.linha(39, 6, 41, 0, "cinza_luz")
        t.chapado(t.poligono([(41, 0), (44, 1), (41, 2.5)]), "amarelo_fogo")
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
    """Vagão blindado de soldados: janelas acesas com a tropa, ninho de metralhadora
    de sacos em cima, caixotes de munição, tambores, lona, truques com mola. 1: destruído."""
    t = Tela(150, 92)
    corpo = t.retangulo(4, 30, 144, 50)
    t.volume(corpo, OLIVA, achatado=4, suave=1.0, ambiente=0.25, semente=8)
    t.chapado(t.retangulo(4, 34, 144, 1), "mandacaru_luz")
    for x in range(8, 146, 6):
        rebites(t, [(x, 33), (x, 77)])
    for x in range(4, 148, 24):
        t.linha(x, 30, x, 79, "sombra")
        t.linha(x + 1, 30, x + 1, 79, "mandacaru")
    for k, x in enumerate((12, 46, 84, 118)):
        janela_acesa(t, x, 42, 18, 12, figura=k != 2, semente=k)
    # Letreiro pintado e faixa de aviso embaixo.
    t.chapado(t.retangulo(40, 62, 70, 6), "caatinga_esc")
    for x in range(42, 108, 3):
        t.chapado(t.retangulo(x, 63, 2, 4), "amarelo_fogo")  # "VOLANTE" em traços de tinta
    listrado(t, t.retangulo(4, 72, 144, 4))
    # Ninho de sacos em cima com a metralhadora e o atirador escondido.
    for k in range(10):
        x = 6 + k * 14
        t.volume(t.elipse(x + 7, 27, 7.5, 4), SACO, achatado=2, suave=0.6, ambiente=0.2, textura=0.25, semente=k)
        t.linha(x + 3, 25, x + 10, 25, "areia_luz")
    t.volume(t.capsula(60, 18, 78, 18, 1.5), FERRO, achatado=1, suave=0.3, brilho=1.2)  # cano da metralhadora
    t.volume(t.retangulo(74, 15, 8, 7), FERRO, achatado=1, suave=0.3)
    t.volume(t.poligono([(76, 22), (73, 26), (85, 26), (82, 22)]), FERRO, achatado=1, suave=0.3)  # tripé
    # Caixotes de munição, tambor e lona amarrada na traseira do teto.
    for x, y in ((104, 16), (114, 16), (109, 9)):
        t.volume(t.retangulo(x, y, 10, 8), MADEIRA, achatado=1, suave=0.3, ambiente=0.3, textura=0.1, semente=x)
        t.linha(x, y + 4, x + 9, y + 4, "couro_profundo")
    t.volume(t.retangulo(126, 12, 9, 12), ["sombra", "caatinga_esc", "caatinga_media", "caatinga"], achatado=1.5, suave=0.4)
    t.chapado(t.retangulo(126, 15, 9, 1), "sombra")
    t.volume(t.elipse(26, 22, 14, 5) & (t.yy < 24), ["terra_escura", "terra", "terra_media", "barro"], achatado=1.5,
             suave=0.5, ambiente=0.3)  # lona
    for x in (18, 34):
        t.linha(x, 18, x + 1, 24, "couro_profundo")
    # Engates e para-choques nas pontas, com corrente.
    for x in (0, 146):
        t.volume(t.retangulo(x, 60, 4, 8), FERRO, achatado=1, suave=0.3, brilho=1.2)
    for k in range(4):
        t.ponto(147 - k * 0, 70 + k * 2, "cinza")
    # Estrado, truques com feixe de molas e as rodas.
    t.volume(t.retangulo(0, 79, 150, 5), FERRO, achatado=1.5, suave=0.4)
    for cx0 in (40, 110):
        t.volume(t.retangulo(cx0 - 24, 76, 48, 5), FERRO, achatado=1, suave=0.3)
        for k in range(3):
            t.linha(cx0 - 8, 77 + k, cx0 + 8, 77 + k, "cinza_luz" if k == 0 else "cinza_medio")  # molas
    for cx in (28, 52, 98, 122):
        roda_motriz(t, cx, 91 - 8, 8, giro)
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
