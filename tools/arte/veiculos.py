"""Veículos da Volante desenhados com o motor, virados para a direita
(o jogo espelha quando andam para a esquerda):

- caminhao(q): caminhão de 1936 com carroceria de tábuas e lona. Quadros:
  0 e 1 andando (raios da roda girando), 2 parado com a lona de trás aberta
  (os soldados pulam por ali), 3 destruído (carcaça queimada).
- blindado(q): carro blindado com torre, canhão e metralhadora no casco.
  Quadros: 0 e 1 andando, 2 canhão recuado (tiro), 3 torre quebrada (sem
  canhão, chapa furada), 4 destruído.
Usado por tools/arte/exportar.py.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela, IDX  # noqa: E402

OLIVA = ["sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru"]
OLIVA_ESC = ["preto", "sombra", "caatinga_esc", "caatinga_media", "caatinga"]
LONA = ["terra_escura", "terra", "terra_media", "barro", "areia_media"]
TABUA = ["couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz"]
FERRO = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]
PNEU = ["preto", "sombra", "sombra_media", "cinza_escuro"]
VIDRO = ["azul_sombra", "azul_medio", "ceu_escuro", "ceu_medio"]

QUEIMADO = {  # cor -> cor da carcaça queimada
    "mandacaru": "cinza_escuro", "caatinga": "sombra_media", "caatinga_media": "sombra_media",
    "caatinga_esc": "sombra", "areia_media": "cinza_medio", "barro": "cinza_escuro", "terra_media": "sombra_media",
    "terra": "sombra", "terra_escura": "preto", "couro_luz": "cinza_escuro", "couro_medio": "sombra_media",
    "couro": "sombra", "couro_escuro": "preto", "couro_profundo": "preto", "cinza_luz": "cinza_medio",
    "cinza": "cinza_escuro", "cinza_medio": "sombra_media", "ceu_medio": "sombra", "ceu_escuro": "preto",
    "azul_medio": "preto", "branco": "cinza", "amarelo_claro": "cinza_escuro", "areia": "cinza_escuro",
}


def queimar(t, semente=0):
    """Escurece tudo como lataria queimada, com manchas de ferrugem e furos."""
    inv = {v: k for k, v in IDX.items()}
    for y in range(t.h):
        for x in range(t.w):
            c = t.px[y, x]
            if c >= 0 and inv[int(c)] in QUEIMADO:
                t.px[y, x] = IDX[QUEIMADO[inv[int(c)]]]
    rng = np.random.default_rng(semente)
    cheio = t.px >= 0
    for _ in range(14):
        x, y = rng.integers(0, t.w), rng.integers(0, t.h)
        m = t.elipse(x, y, rng.uniform(2, 5), rng.uniform(1.5, 3)) & cheio
        t.px[m] = IDX["couro_profundo" if rng.random() < 0.6 else "terra_escura"]
    for _ in range(6):
        x, y = rng.integers(8, t.w - 8), rng.integers(8, t.h - 14)
        t.chapado(t.elipse(x, y, 1.6, 1.4) & cheio, "preto")


def roda(t, cx, cy, r, quadro, raios=4):
    """Pneu com banda, aro de ferro e raios que giram entre os quadros."""
    t.volume(t.elipse(cx, cy, r, r), PNEU, achatado=2, suave=0.6, ambiente=0.15)
    for k in range(10):  # cravos da banda
        a = k / 10 * 2 * np.pi + quadro * 0.31
        t.ponto(cx + np.cos(a) * (r - 0.8), cy + np.sin(a) * (r - 0.8), "preto")
    t.volume(t.elipse(cx, cy, r * 0.55, r * 0.55), FERRO, achatado=1.5, suave=0.5, ambiente=0.3)
    for k in range(raios):
        a = k / raios * np.pi + quadro * np.pi / (raios * 2)
        dx, dy = np.cos(a) * r * 0.5, np.sin(a) * r * 0.5
        t.linha(cx - dx, cy - dy, cx + dx, cy + dy, "cinza_escuro")
    t.chapado(t.elipse(cx, cy, 1.6, 1.6), "cinza_luz")
    t.ponto(cx, cy, "sombra")


def caminhao(quadro=0):
    W, H = 124, 62
    t = Tela(W, H)
    chao = H - 1
    andando = quadro in (0, 1)
    bob = 1 if quadro == 1 else 0
    y0 = -bob  # carroceria sobe 1 px num dos quadros (motor sacudindo)
    # Chassi e para-choque.
    t.volume(t.retangulo(4, 44 + y0, 112, 4), FERRO, achatado=1.5, suave=0.4)
    t.volume(t.retangulo(110, 42 + y0, 10, 4), FERRO, achatado=1.5, suave=0.4, brilho=1.2)
    # Carroceria de tábuas.
    caixa = t.retangulo(3, 27 + y0, 64, 18)
    t.volume(caixa, TABUA, achatado=2, suave=0.6, ambiente=0.3, textura=0.08, semente=3)
    for y in (32, 37, 42):
        t.linha(3, y + y0, 66, y + y0, "couro_profundo")
    for x in (3, 22, 44, 66):
        t.volume(t.retangulo(x - 1, 27 + y0, 3, 18), FERRO, achatado=1, suave=0.3)
        t.pontos([(x, 29 + y0), (x, 42 + y0)], "cinza_luz")
    # Lona arqueada com as varetas marcando.
    if quadro == 3:
        for x in (8, 22, 36, 50, 62):  # só as varetas queimadas sobraram
            t.linha(x, 27 + y0, x, 10 + y0 + abs(x - 35) * 0.25, "sombra")
        t.linha(8, 12 + y0, 62, 12 + y0, "sombra")
    else:
        lona = t.elipse(35, 28 + y0, 33, 21) & (t.yy < 28 + y0) & (t.xx > 2) & (t.xx < 68)
        t.volume(lona, LONA, achatado=4, suave=1.2, ambiente=0.25, textura=0.1, semente=5)
        for x in (12, 24, 35, 46, 58):
            m = lona & (np.abs(t.xx - x) < 0.8)
            t.px[m] = IDX["terra"]
        # Cordas amarrando a lona na carroceria.
        for x in (8, 30, 52):
            t.linha(x, 24 + y0, x + 3, 28 + y0, "couro_profundo")
        if quadro == 2:
            # Lona de trás enrolada: fundo escuro onde os soldados pulam.
            abre = t.elipse(4, 28 + y0, 11, 15) & lona
            t.chapado(abre, "preto")
            t.chapado(abre & (t.xx > 9), "marrom_noite")
            t.chapado(t.retangulo(3, 27 + y0, 6, 17), "sombra")
            # Lona enrolada presa em cima da abertura.
            t.volume(t.capsula(3, 14 + y0, 13, 13 + y0, 2.4), LONA, achatado=1, suave=0.3, ambiente=0.4)
    # Cabine: teto arredondado, janela, porta.
    cab = (t.retangulo(68, 18 + y0, 24, 27) | t.elipse(80, 19 + y0, 12, 5)) & (t.yy > 13 + y0)
    t.volume(cab, OLIVA, achatado=3, suave=1, ambiente=0.25, textura=0.06, semente=2)
    jan = t.retangulo(73, 21 + y0, 15, 9)
    t.volume(jan, VIDRO, achatado=1.5, suave=0.5, ambiente=0.1)
    t.linha(75, 22 + y0, 78, 22 + y0, "ceu_luz")
    t.linha(72, 31 + y0, 72, 43 + y0, "caatinga_esc")
    t.linha(88, 31 + y0, 88, 43 + y0, "caatinga_esc")
    t.chapado(t.retangulo(84, 34 + y0, 3, 1), "cinza_luz")  # maçaneta
    # Estrela branca da Volante na porta.
    sx, sy = 80, 37 + y0
    est = t.poligono([(sx + np.cos(a) * (3.2 if k % 2 == 0 else 1.3), sy + np.sin(a) * (3.2 if k % 2 == 0 else 1.3))
                      for k, a in enumerate(np.linspace(-np.pi / 2, 3 * np.pi / 2, 11)[:-1])])
    t.chapado(est, "branco")
    # Capô comprido com grade e farol.
    capo = t.poligono([(92, 27 + y0), (112, 29 + y0), (114, 44 + y0), (92, 44 + y0)])
    t.volume(capo, OLIVA, achatado=3, suave=1, ambiente=0.3, textura=0.06, semente=4)
    for y in (33, 37):
        t.linha(96, y + y0, 108, y + y0, "caatinga_esc")
    grade = t.retangulo(112, 28 + y0, 5, 15)
    t.volume(grade, FERRO, achatado=1.5, suave=0.4)
    for y in range(29, 43, 2):
        t.linha(112, y + y0, 116, y + y0, "sombra")
    farol = t.elipse(110, 27 + y0, 3.2, 3)
    t.volume(farol, FERRO, achatado=1, suave=0.3)
    t.chapado(t.elipse(111, 27 + y0, 2, 2), "amarelo_claro" if quadro != 3 else "sombra")
    # Para-lamas redondos por cima das rodas.
    for cx in (26, 100):
        pl = t.elipse(cx, 50 + y0, 14, 9) & (t.yy < 50 + y0) & ~t.elipse(cx, 50 + y0, 11, 7)
        t.volume(pl, OLIVA_ESC, achatado=1.5, suave=0.4, ambiente=0.3)
    # Rodas (com raios girando) e estepe.
    q = quadro if andando else 0
    roda(t, 26, chao - 9.5, 9.5, q)
    roda(t, 100, chao - 9.5, 9.5, q)
    t.contorno("sombra")
    if quadro == 3:
        queimar(t, 7)
    return t


def blindado(quadro=0):
    W, H = 132, 76
    t = Tela(W, H)
    chao = H - 1
    andando = quadro in (0, 1)
    y0 = -1 if quadro == 1 else 0
    torre_quebrada = quadro in (3, 4)
    # Canhão (atrás da torre, sai pela frente). No tiro recua 4 px.
    rec = 4 if quadro == 2 else 0
    if not torre_quebrada:
        cano = t.capsula(78 - rec, 19 + y0, 120 - rec, 18 + y0, 2.4)
        t.volume(cano, FERRO, achatado=1.5, suave=0.4, ambiente=0.2, brilho=1.1)
        t.volume(t.retangulo(116 - rec, 15.5 + y0, 7, 6), FERRO, achatado=1.5, suave=0.4)  # freio de boca
        t.chapado(t.retangulo(121 - rec, 17 + y0, 2, 2), "preto")
    else:
        t.volume(t.capsula(78, 19 + y0, 88, 21 + y0, 2.4), FERRO, achatado=1.5, suave=0.4)  # toco quebrado
        for k, (x, y) in enumerate(((88, 18), (89, 22), (90, 20))):
            t.ponto(x, y + y0, "cinza_luz" if k % 2 else "sombra")
    # Torre arredondada com escotilha e periscópio.
    torre = t.poligono([(42, 32 + y0), (46, 15 + y0), (56, 9 + y0), (78, 9 + y0), (86, 16 + y0), (88, 32 + y0)])
    t.volume(torre, OLIVA, achatado=4, suave=1.2, ambiente=0.25, textura=0.08, semente=9)
    t.volume(t.elipse(64, 8 + y0, 9, 3) & (t.yy < 9 + y0), OLIVA_ESC, achatado=1.5, suave=0.4)  # escotilha
    t.volume(t.retangulo(72, 3 + y0, 3, 6), FERRO, achatado=1, suave=0.3)
    t.chapado(t.retangulo(78, 18 + y0, 6, 2), "preto")  # fenda de visão
    for x in range(48, 86, 6):
        t.ponto(x, 29 + y0, "mandacaru")
    if torre_quebrada:
        # Chapa furada e retorcida.
        t.chapado(t.elipse(70, 18 + y0, 7, 5), "preto")
        t.chapado(t.elipse(70, 18 + y0, 4, 3), "vermelho_esc")
        t.chapado(t.elipse(70, 18 + y0, 2, 1.5), "laranja_fogo")
        for (x0, y_, x1, y1) in ((63, 13, 60, 9), (77, 14, 81, 10), (64, 23, 61, 26)):
            t.linha(x0, y_ + y0, x1, y1 + y0, "cinza_luz")
    # Casco de chapas inclinadas com rebites.
    casco = t.poligono([(4, 60 + y0), (8, 40 + y0), (26, 31 + y0), (104, 31 + y0), (124, 42 + y0), (126, 60 + y0)])
    t.volume(casco, OLIVA, achatado=5, suave=1.4, ambiente=0.22, textura=0.08, semente=11)
    # Faixas de chapa e sombra das dobras.
    t.linha(9, 41 + y0, 123, 43 + y0, "caatinga_esc")
    t.linha(6, 52 + y0, 125, 52 + y0, "caatinga_esc")
    for x in range(12, 122, 7):
        t.ponto(x, 44 + y0, "mandacaru")
        t.ponto(x + 3, 55 + y0, "caatinga_esc")
    # Seteiras e a metralhadora no casco, na altura do peito do Lampião.
    for x in (30, 52, 74):
        t.chapado(t.retangulo(x, 46 + y0, 7, 2), "preto")
    t.volume(t.capsula(116, 47 + y0, 130, 47 + y0, 1.4), FERRO, achatado=1, suave=0.3)
    t.volume(t.elipse(117, 47 + y0, 3.4, 3.4), OLIVA_ESC, achatado=1.5, suave=0.4)
    # Estrela da Volante.
    sx, sy = 96, 46 + y0
    est = t.poligono([(sx + np.cos(a) * (4 if k % 2 == 0 else 1.6), sy + np.sin(a) * (4 if k % 2 == 0 else 1.6))
                      for k, a in enumerate(np.linspace(-np.pi / 2, 3 * np.pi / 2, 11)[:-1])])
    t.chapado(est, "branco")
    # Para-lamas e rodas grandes.
    for cx in (28, 102):
        pl = t.elipse(cx, 62 + y0, 16, 10) & (t.yy < 61 + y0) & ~t.elipse(cx, 62, 13, 9)
        t.volume(pl, OLIVA_ESC, achatado=1.5, suave=0.4, ambiente=0.3)
    q = quadro if andando else 0
    roda(t, 28, chao - 11, 11, q, raios=3)
    roda(t, 102, chao - 11, 11, q, raios=3)
    # Lama nas chapas de baixo.
    rng = np.random.default_rng(4)
    for _ in range(18):
        x, y = rng.integers(8, 124), rng.integers(54, 60)
        if t.px[y, x] >= 0:
            t.ponto(x, y, "terra")
    t.contorno("sombra")
    if quadro == 4:
        queimar(t, 13)
    return t
