"""NPCs no padrão do ESTILO.md (lote 2 de gráficos): bode Fubá, galinha e urubu
em formas 3D; romeiro e cientista vêm do gente.py (corpo do Metal Slug).


Uso: python3 tools/arte/npcs.py   (grava pixel/refem.txt e cientista.txt; os PNGs saem no exportar.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
# ================================================================ bichos (volume 3D)
# Montados com formas 3D (volume3d.Cena), luz de cima-esquerda e rampas saturadas;
# olho, boca e detalhes pequenos são pintados por cima, pixel a pixel.
from volume3d import Cena, contornar  # noqa: E402

PELO3 = ["pelo_1", "pelo_2", "pelo_3", "pelo_4", "pelo_5", "pelo_6", "pelo_7"]
FUBA3 = ["fuba_1", "fuba_2", "fuba_3", "fuba_4", "fuba_5", "fuba_6"]
OSSO3 = ["osso_1", "osso_2", "osso_3", "osso_4", "osso_5"]
CASCO3 = ["negro_1", "negro_2", "negro_3", "negro_4"]
FOCINHO = ["carne_2", "carne_3", "carne_5", "carne_6"]
LATAO3 = ["latao_1", "latao_2", "latao_3", "latao_4", "latao_5", "latao_6"]
RUBRO3 = ["rubro_1", "rubro_2", "rubro_3", "rubro_4", "rubro_5"]
NEGRO3 = ["negro_1", "negro_2", "negro_3", "negro_4", "negro_5", "negro_6"]
PERNA_AM = ["latao_2", "latao_3", "latao_4", "latao_5"]

BODE_W, BODE_H = 40, 32


def bode(quadro="parado"):
    """Bode Fubá: parado, mastiga, abduzido e anda1-4 (trote em diagonal)."""
    c = Cena(BODE_W, BODE_H)
    ergue = quadro == "abduzido"
    passo = int(quadro[-1]) - 1 if quadro.startswith("anda") else None
    sobe = 1 if passo in (1, 3) else 0
    hy = (2 if ergue else 0) - sobe
    for k, (x, z) in enumerate(((12, -4), (26, -4), (15, 3), (29, 3))):
        dx, fim = 0, 30
        if passo is not None:
            fase = (passo + (0 if k in (0, 3) else 1) * 2) % 4
            dx = (-3, 0, 3, 0)[fase]
            fim -= 2 if fase == 1 else 0
        if ergue:
            dx, fim = (-3, 3, -1, 4)[k], fim - (3, 6, 2, 5)[k]
        esc = 0.2 if z < 0 else 0
        jy = (19 - sobe + fim) / 2
        c.capsula((x, 19 - sobe, z), (x + dx * 0.4, jy, z), 2.0, 1.4, PELO3, escurece=esc)
        c.capsula((x + dx * 0.4, jy, z), (x + dx, fim - 1, z), 1.4, 1.1, PELO3, escurece=esc)
        c.elipsoide((x + dx + 0.3, fim, z), (1.7, 1.3, 1.5), CASCO3, brilho=0.1)
    c.elipsoide((19, 16 - sobe, 0), (12, 6.8, 6), PELO3)
    c.elipsoide((14, 13 - sobe, 3.5), (4, 2.6, 3), FUBA3)
    c.elipsoide((22, 19 - sobe, 4.5), (3, 2, 2.5), FUBA3)
    c.elipsoide((9, 17 - sobe, 4.5), (1.8, 1.6, 2), FUBA3)
    c.caminho([(8, 13 - sobe, 0), (6, 10 - sobe, 0), (5, 7 - sobe, 0)], [1.6, 1.2, 0.6], PELO3)
    c.capsula((27, 15 - sobe, 1), (31, 8 + hy, 1), 4, 3.4, PELO3)
    c.elipsoide((29, 11 + hy, 4.6), (1.5, 1.4, 1), LATAO3, brilho=0.15)
    c.caminho([(31, 3 + hy, -1), (29, 0.5 + hy, -1), (25.5, 0.5 + hy, -1), (23.5, 3 + hy, -1), (24.5, 5 + hy, -1)],
              [2.2, 1.9, 1.5, 1.1, 0.6], OSSO3)
    c.capsula((30.5, 6 + hy, 2), (36, 9.5 + hy, 2), 5.0, 3.4, PELO3)
    c.elipsoide((37.2, 9.8 + hy, 3), (2.2, 2, 2), FOCINHO)
    c.caminho([(29, 6 + hy, -1), (26, 8 + hy, -1), (24, 10 + hy, -1)], [1.8, 1.4, 0.9], PELO3, escurece=0.15)
    c.caminho([(34.5, 12.5 + hy, 3), (35, 15.5 + hy, 3), (34, 18.5 + hy, 3)], [2.0, 1.4, 0.6], FUBA3)
    t = c.render()
    contornar(t)
    ex, ey = 33, 5 + hy
    if ergue:  # esbugalhado
        t.chapado(t.elipse(ex, ey, 3.0, 2.9), "preto")
        t.chapado(t.elipse(ex, ey, 2.2, 2.1), "branco")
        t.ponto(ex + 1, ey, "preto")
    else:
        t.chapado(t.elipse(ex, ey, 2.8, 2.6), "preto")
        t.chapado(t.elipse(ex, ey, 2.0, 1.8), "latao_6")
        t.ponto(ex - 1, ey - 1, "branco")
        t.linha(ex - 1, ey + 0.3, ex + 1, ey + 0.3, "preto")
        t.linha(ex - 3, ey - 2.5, ex + 2, ey - 3, "pelo_3")  # pálpebra pesada
    for (hx, h_) in ((30, 1), (27, 0), (25, 2)):
        t.ponto(hx, h_ + hy, "osso_1")  # anéis do chifre
    for (x, y) in ((31, 15), (30, 17), (14, 22), (18, 23), (22, 22)):
        t.ponto(x, y - sobe, "pelo_3")  # tufos
    t.linha(27, 12 + hy, 31, 14 + hy, "rubro_3")  # coleira
    t.ponto(38, 9 + hy, "carne_1")  # venta
    if quadro == "mastiga":
        t.linha(35, 12 + hy, 37, 12 + hy, "carne_1")
        t.linha(37, 12 + hy, 40, 9 + hy, "verde_4")
        t.ponto(39, 9 + hy, "verde_6")
    elif ergue:
        t.chapado(t.elipse(37, 12 + hy, 1.6, 1.4), "preto")
        t.ponto(37, 12 + hy, "rubro_4")
        t.pontos([(26, 0), (25, 1), (39, 2)], "ceu_claro")
    else:
        t.linha(35, 12 + hy, 37, 12 + hy, "carne_1")
    return t


GAL_W, GAL_H = 18, 17


def galinha(quadro=0):
    """Galinha caipira: 0 parada, 1 bicando, 2-3 correndo de asa aberta, 4-5 andando."""
    bica, corre, anda = quadro == 1, quadro in (2, 3), quadro in (4, 5)
    c = Cena(GAL_W, GAL_H)
    c.caminho([(5, 9, -1), (2, 5, -1), (2, 1.5, -1)], [2.2, 1.6, 0.8], NEGRO3, brilho=0.2)  # rabo
    c.elipsoide((8.5, 10, 0), (5.8, 4.3, 4), FUBA3)
    if corre:
        tip = (2, 3) if quadro == 2 else (3, 14)
        c.caminho([(8, 9, 3.5), ((8 + tip[0]) / 2, (9 + tip[1]) / 2, 3.5), (tip[0], tip[1], 3.5)], [2.4, 1.8, 0.8], FUBA3)
    else:
        c.elipsoide((8, 10, 3), (3.4, 2.2, 1.5), FUBA3, escurece=0.1)
    hx, hy = (13, 11) if bica else (14, 5) if quadro == 4 else (13, 4)
    c.capsula((11, 8, 1), (hx, hy, 1), 2.4, 2.2, FUBA3)
    c.elipsoide((hx, hy, 1.5), (2.7, 2.6, 2.4), FUBA3)
    t = c.render()
    pe = GAL_H - 1
    if anda:
        a, b = (6, 9) if quadro == 4 else (9, 6)
        t.linha(8, 13, a, pe, "latao_3")
        t.linha(9, 13, b + 1, pe - 1, "latao_4")
        t.linha(b + 1, pe - 1, b + 3, pe - 1, "latao_4")
        t.linha(a - 1, pe, a + 1, pe, "latao_3")
    else:
        for k, x in enumerate((6, 10) if quadro == 2 else (7, 9) if quadro == 3 else (7, 10)):
            cor = "latao_3" if k == 0 else "latao_4"
            t.linha(x, 13, x - (1 if corre else 0), pe, cor)
            t.linha(x - 1, pe, x + 1, pe, cor)
    t.chapado(t.poligono([(hx - 2, hy - 2), (hx - 1, hy - 5), (hx, hy - 3), (hx + 1, hy - 5), (hx + 2, hy - 2)]), "rubro_3")
    t.pontos([(hx - 1, hy - 4), (hx + 1, hy - 4)], "rubro_5")
    t.chapado(t.elipse(hx + 1.5, hy + 3, 0.9, 1.3), "rubro_3")
    t.chapado(t.poligono([(hx + 2, hy - 0.5), (hx + 5, hy + 0.5), (hx + 2, hy + 1.5)]), "latao_5")
    if corre:
        t.chapado(t.elipse(hx + 0.5, hy - 0.5, 1.4, 1.4), "branco")
    t.ponto(hx + 1, hy - 1, "preto")
    contornar(t)
    if corre:
        t.pontos([(1, 13), (2, 12)], "fuba_5")
    return t


URU_W, URU_H = 28, 20


def urubu(quadro=0):
    """Urubu: 0 pousado corcunda, 1 asas para cima, 2 asas para baixo."""
    c = Cena(URU_W, URU_H)
    if quadro == 0:
        c.caminho([(7, 14, -1), (3, 18, -1)], [2.4, 1.2], NEGRO3, escurece=0.15)
        c.elipsoide((12, 12, 0), (7, 6.5, 5), NEGRO3, brilho=0.12)
        c.elipsoide((12.5, 11.5, 3), (5, 4.6, 2.5), NEGRO3, brilho=0.12)
        c.capsula((16, 8, 2), (19, 5, 2), 1.7, 1.5, RUBRO3)
        c.elipsoide((20, 5, 2.5), (2.7, 2.4, 2.2), RUBRO3)
        t = c.render()
        for k in range(3):
            t.linha(9 + k * 2, 14, 7 + k * 2, 16, "negro_5")  # penas da asa
        t.linha(15, 8, 18, 8, "negro_4")  # gola
        t.chapado(t.poligono([(21, 4), (25, 5), (24, 7), (21, 6.5)]), "osso_4")
        t.ponto(24, 7, "osso_2")
        t.chapado(t.elipse(20, 4, 1.2, 1.1), "branco")
        t.ponto(21, 4, "preto")
        t.linha(8, 18, 10, 18, "carne_5")
        t.linha(14, 18, 16, 18, "carne_5")
    else:
        dy = -7 if quadro == 1 else 6
        for lado in (-1, 1):
            z = -2 if lado < 0 else 2
            c.caminho([(14, 10, z), (14 + lado * 7, 10 + dy * 0.6, z), (14 + lado * 12, 9 + dy, z)], [2.6, 2.0, 1.0],
                      NEGRO3, escurece=0.15 if lado < 0 else 0)
        c.elipsoide((13, 11, 0), (6.5, 3.2, 3), NEGRO3, brilho=0.12)
        c.caminho([(7, 11, 0), (3, 12.5, 0)], [2, 1], NEGRO3)
        c.elipsoide((21, 10, 1), (2.4, 2.2, 2), RUBRO3)
        t = c.render()
        for lado in (-1, 1):
            for k in range(3):  # dedos de pena na ponta
                t.ponto(14 + lado * (12 - k * 1.5), 9 + dy + (1 if dy < 0 else -1) * k * 0.6, "negro_6")
        t.chapado(t.poligono([(22, 9), (26, 10), (25, 12), (22, 11.5)]), "osso_4")
        t.ponto(21, 9, "preto")
    contornar(t)
    return t


if __name__ == "__main__":
    import gente
    import pixel
    for fig, arq in (("romeiro", "refem.txt"), ("cientista", "cientista.txt")):
        pixel.salvar(arq, gente.quadros(fig))
    print("pixel/refem.txt e pixel/cientista.txt atualizados")
