"""Gente do sertão no corpo do Metal Slug (padrão de 20/10, pedido do Guilherme):
cabeça pequena (~1/4 da altura, não 1/3), tronco largo e comprido, mãos e botas
grandes, joelho dobrado e o corpo inclinado para a frente.

Usado pelos NPCs humanos (romeiro e cientista). Quadro 52x46, pé em y=45, virado
para a direita. Sombreado com volume3d.sombrear2d e as rampas saturadas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np  # noqa: E402
from motor import IDX, Tela  # noqa: E402
from volume3d import sombrear2d  # noqa: E402

W, H = 52, 46
CHAO = 45


def R(nome, a, b):
    return [f"{nome}_{k}" for k in range(a, b + 1)]


CARNE = R("carne", 1, 7)
NARIZ = R("carne", 2, 7)
PELO = R("pelo", 2, 7)
BARBA = R("pelo", 3, 7)
OSSO = R("osso", 1, 5)
PALHA = R("osso", 2, 5) + ["latao_6"]
FUBA = R("fuba", 1, 5)
ACO = R("aco", 1, 6)
CAMISA = R("osso", 3, 5) + ["pelo_6", "pelo_7"]
CORDA = R("osso", 1, 4)
SAPATO = ["negro_1", "fuba_1", "fuba_2", "fuba_3", "fuba_4"]

ROUPA = {
    "romeiro": {"tronco": CAMISA, "calca": OSSO, "braco": CAMISA},
    "cientista": {"tronco": PELO, "calca": ACO, "braco": PELO},
}


def membro(t, a, b, c, r1, r2, rampa, d=0.0):
    m = t.capsula(a[0], a[1], b[0], b[1], r1) | t.capsula(b[0], b[1], c[0], c[1], r2)
    sombrear2d(t, m, rampa, d)
    # Separação clara da peça de trás: a beirada de baixo/direita leva o tom mais escuro.
    from scipy import ndimage
    borda = m & ~ndimage.binary_erosion(m)
    baixo = np.zeros_like(m)
    baixo[:-1] = ~m[1:]
    t.px[borda & baixo & (t.yy > a[1] + 1)] = IDX[rampa[0]]
    return m


def mao(t, x, y, d=0.0):
    sombrear2d(t, t.elipse(x, y, 1.9, 1.8), CARNE, d)


def bota(t, x, y, d=0.0):
    """(x, y) = calcanhar no chão; bico grande para a frente."""
    m = t.elipse(x + 2.4, y - 1.4, 3.6, 2.0) & (t.yy < y + 0.5)
    sombrear2d(t, m, SAPATO, d)
    t.linha(x - 1, y, x + 5, y, "negro_1")


# ---------------------------------------------------------------- cabeças
def cabeca(t, fig, x, y, rosto="feliz", chapeu=0):
    """Cabeça pequena (10x11). (x, y) = centro do rosto."""
    x, y = int(round(x)), int(round(y))
    if fig == "cientista":
        tufo = t.poligono([(x - 3, y - 5), (x - 7, y - 7), (x - 6, y - 3), (x - 9, y - 2), (x - 6, y), (x - 8, y + 3),
                           (x - 4, y + 2)])
        sombrear2d(t, tufo, PELO)
    else:
        for k, cor in enumerate(("rubro_4", "latao_5", "ceu", "verde_5")):  # fitas do chapéu
            t.linha(x - 6 + k * 0.5, y - 3 + chapeu, x - 8 - k * 0.6, y + 3 + k * 1.2, cor)
    sombrear2d(t, t.elipse(x - 4, y + 1, 1.3, 1.7), CARNE)  # orelha
    sombrear2d(t, t.elipse(x, y, 5, 5.3), CARNE)
    # Barba / bigode.
    if fig == "romeiro":
        barba = t.poligono([(x - 3, y + 1), (x + 5, y + 1), (x + 5, y + 5), (x + 2, y + 9), (x - 1, y + 7)])
        sombrear2d(t, barba, BARBA)
        t.linha(x + 1, y + 5, x + 2, y + 7, "pelo_3")
    else:
        sombrear2d(t, t.poligono([(x + 1, y + 2), (x + 7, y + 2), (x + 7, y + 4), (x + 4, y + 4), (x + 1, y + 5)]), BARBA)
    # Narigão.
    sombrear2d(t, t.elipse(x + 5, y + 0.5, 1.8, 1.5), NARIZ)
    # Boca.
    if rosto == "feliz":
        t.linha(x + 2, y + 4 + (fig == "cientista"), x + 4, y + 4 + (fig == "cientista"), "rubro_2")
    elif rosto == "chorando":
        t.ponto(x + 3, y + 5, "rubro_1")
    # Olho (MS: pequeno, branco com a pupila).
    ex, ey = x + 2, y - 1
    if fig == "cientista":
        t.chapado(t.elipse(ex + 0.5, ey, 2.3, 2.2), "negro_1")
        t.chapado(t.elipse(ex + 0.5, ey, 1.4, 1.3), "ceu_claro")
        t.ponto(ex + 1, ey, "negro_1")
        t.ponto(ex, ey - 1, "branco")
        t.linha(ex - 2, ey - 1, x - 3, y - 1, "negro_1")  # haste
        t.linha(ex - 1, ey - 3, ex + 2, ey - 3, "pelo_7")  # sobrancelha
    else:
        if rosto == "feliz":
            t.pontos([(ex, ey), (ex + 1, ey - 1), (ex + 2, ey)], "negro_1")
        else:
            t.chapado(t.retangulo(ex, ey - 1, 2, 2), "branco")
            t.ponto(ex + 1, ey, "negro_1")
        t.linha(ex - 1, ey - 2, ex + 2, ey - 2 - (rosto != "feliz"), "pelo_7")
        if rosto == "chorando":
            t.linha(ex, ey + 1, ex - 1, ey + 3, "ceu_claro")
    if fig == "cientista":
        t.pontos([(x - 2, y - 4), (x - 1, y - 4)], "carne_7")  # careca brilhando
    else:
        cy = y - 4 + chapeu
        sombrear2d(t, t.elipse(x, cy - 1.5, 4.2, 3.2) & (t.yy < cy + 0.5), PALHA)
        t.chapado(t.retangulo(x - 4, cy - 1, 8.5, 1), "rubro_3")
        sombrear2d(t, t.elipse(x + 0.5, cy + 0.5, 8.5, 1.6), PALHA)


def peito(t, fig, x, y):
    if fig == "cientista":
        t.chapado(t.poligono([(x - 1, y - 1), (x + 2, y), (x - 1, y + 1)]), "rubro_3")
        t.chapado(t.poligono([(x + 4, y - 1), (x + 2, y), (x + 4, y + 1)]), "rubro_2")
        t.pontos([(x - 2, y + 4), (x - 1, y + 3)], "azul_medio")  # canetas no bolso
        t.pontos([(x + 2, y + 7), (x + 3, y + 7)], "alien_medio")  # respingo de gosma
    else:
        for k in range(5):  # terço
            t.ponto(x - 2 + k, y + abs(k - 2) * -0.5 + 1, "fuba_2")
        t.chapado(t.retangulo(x, y + 2, 1, 3), "fuba_2")
        t.chapado(t.retangulo(x - 1, y + 3, 3, 1), "fuba_2")


# ---------------------------------------------------------------- corpo
def em_pe(fig="romeiro", pose="continencia", passo=0, rosto="feliz"):
    """Poses em pé: solto (pula de braço para cima), procura, entrega, continencia,
    corre (passo 0-3)."""
    t = Tela(W, H)
    r = ROUPA[fig]
    dy = {"solto": -4, "entrega": -1}.get(pose, 0)
    if pose == "corre":
        dy = -1 if passo in (1, 3) else 0
    bx = 18
    quadril = 31 + dy
    # Perna de trás.
    if pose == "corre":
        k = [(-5, 5), (0, 0), (5, -5), (0, 0)][passo]
        pe_t, pe_f = (bx - 2 + k[1], CHAO - (2 if k[1] < 0 else 0)), (bx + 3 + k[0], CHAO - (2 if k[0] < 0 else 0))
    elif pose == "solto":
        pe_t, pe_f = (bx - 6, 42 + dy), (bx + 5, 41 + dy)
    else:
        pe_t, pe_f = (bx - 5, CHAO), (bx + 6, CHAO)
    joelho_t = ((bx - 1 + pe_t[0]) / 2 + 1.5, (quadril + pe_t[1]) / 2)
    membro(t, (bx - 1, quadril), joelho_t, (pe_t[0], pe_t[1] - 2), 3.0, 2.4, r["calca"], -1.2)
    bota(t, pe_t[0] - 2, pe_t[1], -1.2)
    # Braço de trás.
    if pose == "solto":
        membro(t, (bx - 3, 19 + dy), (bx - 8, 15 + dy), (bx - 10, 9 + dy), 2.3, 2.0, r["braco"], -1.2)
        mao(t, bx - 10.5, 8 + dy, -1)
    elif pose == "corre":
        k = [-1, 0, 1, 0][passo]
        membro(t, (bx - 3, 19 + dy), (bx - 4 - k * 3, 25 + dy), (bx - 2 - k * 5, 27 + dy), 2.3, 2.0, r["braco"], -1.2)
        mao(t, bx - 2 - k * 5, 28 + dy, -1)
    # Tronco largo, inclinado para a frente.
    lean = 1.5
    tronco = t.elipse(bx + lean, 24 + dy, 7.8, 8.0) | t.elipse(bx, 29 + dy, 7, 4)
    if fig == "cientista":  # jaleco desce até a coxa e voa na corrida
        voa = 2 if pose == "corre" else 0
        tronco |= t.poligono([(bx - 7, 28 + dy), (bx + 7, 28 + dy), (bx + 7, 36 + dy), (bx - 7 - voa * 2, 35 + dy)])
    sombrear2d(t, tronco, r["tronco"])
    if fig == "cientista":
        t.linha(bx + 3, 20 + dy, bx + 3, 35 + dy, "pelo_3")  # abertura do jaleco
    # Bornal com alça cruzada.
    t.linha(bx - 5, 18 + dy, bx + 6, 29 + dy, "fuba_3")
    sombrear2d(t, t.elipse(bx + 7, 30 + dy, 3, 3), FUBA)
    t.chapado(t.retangulo(bx + 4, 28 + dy, 6, 1), "fuba_1")
    if fig == "romeiro":
        t.chapado(t.retangulo(bx - 6, 31 + dy, 13, 1), "osso_2")  # cordão na cintura
    # Perna da frente.
    joelho_f = ((bx + 2 + pe_f[0]) / 2 + 2, (quadril + pe_f[1]) / 2)
    if fig == "romeiro" or pose != "corre":
        membro(t, (bx + 2, quadril), joelho_f, (pe_f[0], pe_f[1] - 2), 3.0, 2.4, r["calca"])
    else:
        membro(t, (bx + 2, quadril + 3), joelho_f, (pe_f[0], pe_f[1] - 2), 3.0, 2.4, r["calca"])
    bota(t, pe_f[0] - 2, pe_f[1])
    if pose == "solto":
        for x0 in (7, 23):
            sombrear2d(t, t.capsula(x0, CHAO - 1, x0 + 7, CHAO - 2, 1), CORDA)
    # Cabeça (pequena, à frente do tronco).
    hx, hy = bx + 5 + (1 if pose == "procura" else 0), 12 + dy + (1 if pose == "procura" else 0)
    cabeca(t, fig, hx, hy, rosto, chapeu=-2 if pose == "solto" else 0)
    peito(t, fig, bx + 1, 19 + dy)
    # Braço da frente.
    ombro = (bx + 4, 19 + dy)
    if pose == "solto":
        membro(t, ombro, (bx + 9, 14 + dy), (bx + 12, 8 + dy), 2.3, 2.0, r["braco"])
        mao(t, bx + 12.5, 7 + dy)
    elif pose == "procura":
        membro(t, ombro, (bx + 7, 24 + dy), (bx + 8, 28 + dy), 2.3, 2.0, r["braco"])
        mao(t, bx + 8, 29 + dy)
    elif pose == "entrega":
        membro(t, ombro, (bx + 10, 21 + dy), (bx + 15, 18 + dy), 2.3, 2.0, r["braco"])
        mao(t, bx + 16, 18 + dy)
    elif pose == "continencia":
        membro(t, ombro, (bx + 12, 17 + dy), (bx + 11, 9 + dy), 2.3, 2.0, r["braco"])
        mao(t, bx + 11, 8 + dy)
    else:
        k = [1, 0, -1, 0][passo]
        membro(t, ombro, (bx + 4 - k * 3, 25 + dy), (bx + 8 - k * 4, 25 + dy), 2.3, 2.0, r["braco"])
        mao(t, bx + 8.5 - k * 4, 25 + dy)
    t.contorno("negro_1")
    if pose == "corre":
        t.pontos([(5, 9 + dy), (4, 10 + dy)], "ceu_claro")
    return t


def amarrado(fig="romeiro", balanco=0, pulo=0, rosto="triste"):
    """Ajoelhado e amarrado com corda grossa, se debatendo."""
    t = Tela(W, H)
    r = ROUPA[fig]
    b, p = balanco, pulo
    sombrear2d(t, t.elipse(18, 40 - p, 10, 4.5), r["calca"])  # pernas dobradas
    bota(t, 7, CHAO - p, -1)
    tronco = t.elipse(18 + b * 0.5, 30 - p, 8, 8.5)
    sombrear2d(t, tronco, r["tronco"])
    sombrear2d(t, t.elipse(10 + b * 0.5, 32 - p, 3, 3.5), FUBA)
    for k, y in enumerate((25, 29, 33)):
        volta = t.capsula(9 + b * 0.5, y - p + k * 0.3, 27 + b * 0.5, y - p - 1, 1.3) & t.elipse(18 + b * 0.5, 30 - p, 9.5, 9.5)
        sombrear2d(t, volta, CORDA)
    sombrear2d(t, t.elipse(25 + b * 0.5, 31 - p, 1.8, 1.5), CORDA)
    t.linha(26 + b * 0.5, 32 - p, 28 + b, 36 - p, "osso_3")
    cabeca(t, fig, 20 + b, 16 - p, rosto, chapeu=1 if p else 0)
    t.contorno("negro_1")
    return t


def pendurado(fig="romeiro", balanco=0, rosto="chorando"):
    t = Tela(W, H)
    r = ROUPA[fig]
    bx, b = 18, balanco
    membro(t, (bx - 1, 32), (bx - 2 - b, 38), (bx - 3 - b * 2, 42), 2.8, 2.3, r["calca"], -1.2)
    bota(t, bx - 5 - b * 2, 44, -1.2)
    tronco = t.elipse(bx, 25, 7.2, 8.4)
    if fig == "cientista":
        tronco |= t.poligono([(bx - 7, 28), (bx + 7, 28), (bx + 7, 35), (bx - 7, 35)])
    sombrear2d(t, tronco, r["tronco"])
    membro(t, (bx + 2, 32), (bx + 3 + b, 38), (bx + 4 + b * 2, 42), 2.8, 2.3, r["calca"])
    bota(t, bx + 2 + b * 2, 44)
    membro(t, (bx - 4, 19), (bx - 7, 9), (bx + 1, 1.5), 2.2, 1.9, r["braco"], -1.2)
    membro(t, (bx + 4, 19), (bx + 9, 9), (bx + 3, 1.5), 2.2, 1.9, r["braco"])
    cabeca(t, fig, bx + 1, 13, rosto, chapeu=1)
    peito(t, fig, bx, 19)
    mao(t, bx + 2, 1.8)
    sombrear2d(t, t.retangulo(bx, 2, 4.5, 1.4), CORDA)
    t.contorno("negro_1")
    return t


def quadros(fig):
    return {
        "amarrado1": amarrado(fig, 0, 0, "triste"),
        "amarrado2": amarrado(fig, -1, 1, "chorando"),
        "amarrado3": amarrado(fig, 1, 0, "triste"),
        "solto": em_pe(fig, "solto"),
        "procura": em_pe(fig, "procura", rosto="concentrado"),
        "entrega": em_pe(fig, "entrega"),
        "continencia": em_pe(fig, "continencia"),
        "corre1": em_pe(fig, "corre", 0),
        "corre2": em_pe(fig, "corre", 1),
        "corre3": em_pe(fig, "corre", 2),
        "corre4": em_pe(fig, "corre", 3),
        "pendurado1": pendurado(fig, -1, "chorando"),
        "pendurado2": pendurado(fig, 1, "triste"),
    }
