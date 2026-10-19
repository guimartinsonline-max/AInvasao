"""Objetos de cenário e equipamento desenhados com o motor:
barril de querosene (explode) e escudo de madeira do soldado da Volante.
Usado por tools/arte/exportar.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from motor import IDX, Tela  # noqa: E402

LATA = ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"]
FAIXA = ["laranja_escuro", "ouro_escuro", "amarelo_fogo", "amarelo_claro"]
TABUA = ["couro_profundo", "couro", "couro_medio", "couro_luz"]
TABUA_ESC = ["couro_profundo", "couro_escuro", "couro", "couro_medio"]
FERRO = ["sombra", "cinza_escuro", "cinza", "cinza_claro"]


def barril(quadro=0):
    """Tambor de querosene de 200 litros, no nível de detalhe do Metal Slug: corpo
    cilíndrico com luz de lado, aros de rolagem salientes, tampa com borda, bujão e
    respiro, losango amarelo de perigo com a chama, tinta descascada mostrando o
    metal, ferrugem escorrendo, amassado, mancha de querosene e terra na base.
    Quadro 1: furado por bala, amassado e esguichando querosene com faísca."""
    import numpy as np
    W, H = 18, 24
    t = Tela(W, H)
    VERM = ["marrom_noite", "vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"]
    corpo = t.retangulo(1, 3, 16, 19) | t.elipse(9, 21.5, 8, 1.8)
    # Cilindro: luz vinda da esquerda em faixas verticais (sem granulado).
    xs = t.xx
    nivel = np.clip(((1 - np.abs((xs - 6.5) / 8.5)) * 4.6).astype(int), 0, 4)
    cores = np.array([IDX[c] for c in VERM])[nivel]
    t.px[corpo] = cores[corpo]
    t.px[corpo & (xs >= 15.5)] = IDX["marrom_noite"]
    t.px[corpo & (np.abs(xs - 14.5) < 0.5)] = IDX["vermelho_medio"]  # luz refletida na borda
    t.px[corpo & (np.abs(xs - 5) < 0.6)] = IDX["laranja_fogo"]  # brilho do metal pintado
    # Aros de rolagem salientes (claro em cima, escuro embaixo).
    for y in (8, 16):
        aro = t.retangulo(0.5, y, 17, 1.2)
        t.px[aro & corpo | aro] = IDX["vermelho_medio"]
        t.chapado(t.retangulo(1, y, 15, 1) & (xs < 13), "laranja_fogo")
        t.chapado(t.retangulo(1, y + 1, 16, 1), "marrom_noite")
    # Losango amarelo de perigo com a chama preta.
    los = t.poligono([(8.5, 9.2), (12, 12.4), (8.5, 15.6), (5, 12.4)])
    t.chapado(los, "amarelo_fogo")
    t.chapado(los & (xs < 7.5), "amarelo_claro")
    t.linha(5, 12.4, 8.5, 9.2, "preto")  # borda preta do losango
    t.linha(8.5, 9.2, 12, 12.4, "preto")
    t.linha(12, 12.4, 8.5, 15.6, "preto")
    t.linha(8.5, 15.6, 5, 12.4, "preto")
    # Chama de três línguas (pictograma de inflamável).
    t.chapado(t.elipse(8.5, 13.4, 1.6, 1.2) | t.poligono([(7, 13.2), (8.9, 10.6), (10, 13.2)]), "preto")
    t.ponto(8.5, 13.5, "laranja_fogo")
    # Tinta descascada mostrando o metal e ferrugem escorrendo dos aros.
    for (x, y) in ((3, 5), (13, 11), (11, 19), (4, 18)):
        t.chapado(t.elipse(x, y, 1.3, 0.9), "cinza_medio")
        t.ponto(x - 0.5, y - 0.4, "cinza_luz")
    for x, y0, n in ((6, 10, 3), (14, 18, 3), (10, 17, 2)):
        for k in range(n):
            t.ponto(x, y0 + k, "couro_escuro" if k < n - 1 else "couro_profundo")
    # Amassado: uma meia-lua escura com a borda clara.
    t.chapado(t.elipse(13.5, 5.5, 1.6, 1.2), "vermelho_esc")
    t.ponto(12.5, 4.5, "laranja_fogo")
    # Tampa: borda grossa, a face de cima vista de leve, bujão e respiro.
    t.volume(t.elipse(9, 3, 8.5, 2.2), ["sombra", "cinza_escuro", "cinza_medio", "cinza"], achatado=1, suave=0.3, brilho=1.2)
    t.chapado(t.elipse(9, 3, 6.8, 1.2), "cinza_escuro")
    t.chapado(t.elipse(9, 2.7, 6.4, 0.8), "cinza_medio")
    t.chapado(t.retangulo(4, 2, 2.5, 1.5), "cinza_luz")  # bujão
    t.ponto(4, 1, "sombra")
    t.chapado(t.elipse(13, 2.6, 1, 0.6), "sombra")  # respiro
    # Mancha de querosene e terra na base.
    t.chapado(t.retangulo(1, 20, 16, 1.5) & (xs > 2), "marrom_noite")
    for x in range(2, 16, 2):
        t.ponto(x, 21, "terra")
    t.contorno("sombra")
    if quadro == 1:
        # Furo de bala com borda de metal, esguicho de querosene e faísca.
        t.chapado(t.elipse(12, 12, 1.5, 1.5), "preto")
        t.pontos([(11, 11), (13, 13)], "cinza_luz")
        t.linha(13, 12, 17, 13, "couro_medio")
        t.ponto(17, 14, "couro_escuro")
        t.linha(12, 14, 12, 20, "couro_profundo")
        t.pontos([(14, 10), (15, 9)], "amarelo_fogo")
        t.ponto(16, 8, "branco")
        t.chapado(t.elipse(6, 6, 2, 1.5), "vermelho_esc")  # mais um amassado
        t.ponto(5, 5, "laranja_fogo")
    return t


def escudo(quadro=0):
    """Escudo de chapa de aço da Volante (16x30), seguro pela mão do soldado na borda
    de trás. Pintado de verde-oliva gasto nas quinas (aparece o aço), aro rebitado,
    visor de mira em cima, seteira por onde passa o cano do fuzil, estrela pintada,
    riscos e amassados de bala. Quadro 1: arrebentado (amassados fundos, furo, quina
    entortada, tinta descascando)."""
    import numpy as np
    W, H = 16, 30
    t = Tela(W, H)
    xs, ys = t.xx, t.yy
    chapa = t.poligono([(2, 3), (4, 1), (12, 1), (14.5, 3), (14.5, 29), (1.5, 29), (1.5, 3)])
    # Chapa abaulada: luz da esquerda em faixas, pintura oliva.
    OLIVA_E = ["sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru"]
    nivel = np.clip(((1 - np.abs((xs - 6) / 9.5)) * 5).astype(int), 0, 4)
    t.px[chapa] = np.array([IDX[c] for c in OLIVA_E])[nivel][chapa]
    # Aço aparecendo nas quinas e bordas gastas.
    borda = chapa & ~t.poligono([(3.5, 4), (5, 2.5), (11, 2.5), (13, 4), (13, 27.5), (3, 27.5), (3, 4)])
    aco = ["cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]
    t.px[borda] = np.array([IDX[c] for c in aco])[np.clip(((1 - np.abs((xs - 6) / 9.5)) * 3.9).astype(int), 0, 3)][borda]
    # Rebites do aro.
    for y in range(5, 28, 4):
        for x in (2.5, 13.5):
            t.ponto(x, y, "cinza_claro")
            t.ponto(x, y + 1, "sombra")
    for x in (5, 8, 11):
        t.ponto(x, 1.6, "cinza_claro")
        t.ponto(x, 28, "cinza_claro")
    # Visor de mira em cima, com aba de proteção.
    t.chapado(t.retangulo(4, 6, 8, 1.5), "preto")
    t.chapado(t.retangulo(4, 5, 8, 1), "cinza_luz")
    t.chapado(t.retangulo(4, 7.5, 8, 0.8), "caatinga_esc")
    # Seteira do fuzil (vazada: o cano do soldado aparece por ela) com borda reforçada.
    seteira = t.elipse(10.5, 12.5, 4.5, 1.4)
    t.chapado(ndimage_dilatar(t, seteira) & chapa, "cinza")
    t.px[seteira & chapa] = -1
    # Estrela da Volante pintada, meio apagada.
    import math
    est = [(8, 21) if False else (8 + math.cos(a) * (3 if k % 2 == 0 else 1.3), 21 + math.sin(a) * (3 if k % 2 == 0 else 1.3))
           for k, a in enumerate(np.linspace(-math.pi / 2, 3 * math.pi / 2, 11)[:-1])]
    estrela = t.poligono(est) & chapa
    t.chapado(estrela, "amarelo_fogo")
    t.px[estrela & (((xs.astype(int) * 3 + ys.astype(int)) % 4) == 0)] = IDX["ouro_escuro"]
    # Riscos de bala de raspão e terra subindo da base.
    for (x0, y0, x1, y1) in ((4, 15, 7, 14), (9, 24, 12, 25), (5, 9, 6, 10)):
        t.linha(x0, y0, x1, y1, "cinza_luz")
    t.px[chapa & (ys > 26) & (((xs.astype(int) + ys.astype(int)) % 2) == 0)] = IDX["terra_escura"]
    # Amassado de bala: miolo escuro, borda clara.
    def amassado(x, y, fundo=False):
        t.chapado(t.elipse(x, y, 1.4, 1.2), "cinza_luz")
        t.chapado(t.elipse(x + 0.3, y + 0.3, 0.8, 0.7), "preto" if fundo else "cinza_escuro")
    amassado(6, 17)
    if quadro == 1:
        for x, y in ((11, 19), (5, 24), (9, 8), (12, 26), (4, 12)):
            amassado(x, y, True)
        t.px[t.elipse(7.5, 14.5, 1.1, 1.1) & chapa] = -1  # furou
        t.px[t.poligono([(11, 0), (15, 0), (15, 5)])] = -1  # quina entortada para trás
        t.linha(11.5, 1.5, 14, 4, "cinza_luz")
        lasca = (t.yy > 9) & (t.yy < 26) & chapa & (((xs.astype(int) * 5 + ys.astype(int) * 3) % 11) == 0)
        t.px[lasca] = IDX["cinza_medio"]
    t.contorno("sombra")
    # Mão do soldado agarrando a borda de trás (fica por cima do contorno).
    mao = ["O55O", "4554", "3443", "O33O"]
    cor = {"O": "sombra", "5": "pele_luz", "4": "pele", "3": "pele_media"}
    for dy, linha in enumerate(mao):
        for dx, ch in enumerate(linha):
            t.ponto(dx, 14 + dy, cor[ch])
    return t


def ndimage_dilatar(t, m):
    from scipy import ndimage
    return ndimage.binary_dilation(m)
