"""Soldados da Volante no padrão novo (20/10): corpo do Metal Slug (cabeça ~1/4 da
altura, tronco largo arredondado, botinas grandes, joelho dobrado), volume de cúpula com
luz de um lado (volume3d.sombrear2d) e as rampas saturadas da paleta.

Mesmos tipos, quadros e pé (14, 45) dos caricatos.py antigos: fuzil (quepe),
granadeiro, metralhador e rojão (capacete Adrian), facão (sargento de faixa vermelha)
e oficial (quepe alto com cordão dourado). Narigão, bigodão, barriga e perneira enrolada.
Gera tools/arte/pixel/<tipo>.txt (lidos pelo exportar.py).
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
import pixel  # noqa: E402
from gente import R, tronco_forma  # noqa: E402
from motor import IDX, VAZIO, Tela  # noqa: E402
from volume3d import sombrear2d  # noqa: E402

W, H = 52, 46
CHAO = 45
PE = (14, 45)

PELE = R("carne", 1, 7)
NARIZ = R("carne", 2, 7)
FARDA = R("verde", 1, 7)
FARDA_ESC = R("verde", 1, 5)
PERNEIRA = R("verde", 2, 7)
BIGODE = ["negro_1", "fuba_1", "fuba_2", "fuba_3"]
BOTA = R("negro", 1, 5)
MADEIRA = R("fuba", 1, 6)
COURO = R("fuba", 1, 5)
ACO = R("aco", 1, 6) + ["aco_brilho"]
LONA = R("osso", 1, 5)
COBERTOR = R("rubro", 1, 4)
LATAO = R("latao", 2, 6)
VERMELHO = R("rubro", 1, 6)
LAMINA = ["aco_2", "aco_4", "aco_6", "pelo_6", "pelo_7"]

BX = 13
QUADRIL = 31
TOPO, BASE = 16, 32
CABECA = (16, 11)
OMBRO_F = (17, 19)
OMBRO_T = (12, 19)
CANO = {}  # boca da arma no quadro "atira", em relação ao pé (para o src/quadros.js)


def _borda_baixo(t, m, cor, y_min):
    borda = m & ~ndimage.binary_erosion(m)
    baixo = np.zeros_like(m)
    baixo[:-1] = ~m[1:]
    t.px[borda & baixo & (t.yy > y_min)] = IDX[cor]


def botina(t, x, y, d=0.0):
    """Botina grandona, bico para a frente; (x, y) = calcanhar no chão."""
    m = t.elipse(x + 2.6, y - 1.5, 3.9, 2.2) & (t.yy < y + 0.5)
    sombrear2d(t, m, BOTA, d)
    t.linha(x - 1, y, x + 6, y, "negro_1")
    t.ponto(x + 4, y - 2, "negro_6" if d >= 0 else "negro_4")  # bico engraxado


def perna(t, quadril, pe, atras=False, joelho=None):
    """Calça de farda e perneira de pano enrolada até a botina."""
    d = -1.2 if atras else 0.0
    hx, hy = quadril
    px, py = pe
    jx, jy = joelho or ((hx + px) / 2 + 2, (hy + py) / 2 - (1 if py < CHAO else 0))
    coxa = t.capsula(hx, hy, jx, jy, 3.1, 2.7)
    sombrear2d(t, coxa, FARDA, d)
    canela = t.capsula(jx, jy, px, py - 2, 2.5, 2.2) & ~coxa
    sombrear2d(t, canela, PERNEIRA, d)
    # Faixas da perneira em diagonal.
    for f in (0.3, 0.55, 0.8):
        cx, cy = jx + (px - jx) * f, jy + (py - 2 - jy) * f
        t.linha(cx - 2, cy + 0.5, cx + 2, cy - 1, "verde_2" if atras else "verde_3")
    _borda_baixo(t, coxa | canela, "verde_1", hy + 1)
    botina(t, px - 2, py, d)


def braco(t, ombro, cotovelo, punho, atras=False):
    d = -1.2 if atras else 0.0
    m = t.capsula(*ombro, *cotovelo, 2.4, 2.1) | t.capsula(*cotovelo, *punho, 2.1, 1.8)
    sombrear2d(t, m, FARDA, d)
    _borda_baixo(t, m, "verde_1", ombro[1] + 1)
    return m


def mao(t, x, y, atras=False):
    sombrear2d(t, t.elipse(x, y, 2.1, 1.9), PELE, -1 if atras else 0)
    t.ponto(x + 1, y + 1, "carne_3")


# ---------------------------------------------------------------- cabeça
def cabeca(t, x, y, rosto="serio", tipo="fuzil", q=0):
    """Cabeça pequena (10x11) de soldado caricato. (x, y) = centro do rosto;
    q: o quepe/capacete pula de susto."""
    x, y = int(round(x)), int(round(y))
    sombrear2d(t, t.elipse(x - 4, y + 1, 1.3, 1.7), PELE)  # orelha
    sombrear2d(t, t.elipse(x, y, 5, 5.3), PELE, 0.8)
    t.ponto(x - 4, y + 1, "carne_2")
    # Barba por fazer no queixo.
    for px_, py_ in ((x - 1, y + 4), (x + 1, y + 5), (x, y + 3), (x - 2, y + 3), (x + 2, y + 4)):
        t.ponto(px_, py_, "carne_3")
    # Narigão.
    sombrear2d(t, t.elipse(x + 5.2, y + 0.8, 2.3, 1.9), NARIZ)
    t.ponto(x + 4, y + 2, "carne_2")
    # Bigodão.
    bigode = t.poligono([(x + 1, y + 2.5), (x + 7, y + 2.5), (x + 8.5, y + 4.5), (x + 6, y + 4), (x + 4, y + 5),
                         (x + 1.5, y + 4.5)])
    sombrear2d(t, bigode, BIGODE)
    _rosto(t, x, y, rosto, tipo)
    if tipo in ("granadeiro", "metralhador", "rojao"):
        capacete(t, x, y + q)
    else:
        quepe(t, x, y + q, tipo)


def _rosto(t, x, y, rosto, tipo):
    ex, ey = x + 2, y - 1
    sob = "negro_1"
    if rosto == "morto":
        t.pontos([(ex - 1, ey - 1), (ex + 1, ey - 1), (ex, ey), (ex - 1, ey + 1), (ex + 1, ey + 1)], "negro_1")
    elif rosto in ("dorme", "ronca"):
        t.linha(ex - 1, ey, ex + 1, ey, "negro_1")
        t.linha(ex - 1, ey - 2, ex + 2, ey - 1, sob)
    elif rosto in ("saudade", "chora"):
        t.pontos([(ex - 1, ey), (ex, ey - 1), (ex + 1, ey - 1), (ex + 2, ey)], "negro_1")
        t.linha(ex - 1, ey - 2, ex + 2, ey - 3, sob)
        t.ponto(ex + 1, ey + 1, "ceu_claro")
        if rosto == "chora":
            t.linha(ex + 1, ey + 1, ex + 1, ey + 4, "ceu_claro")
            t.linha(ex - 1, ey + 1, ex - 2, ey + 4, "ceu_claro")
    elif rosto == "panico":
        t.chapado(t.retangulo(ex - 1, ey - 2, 3, 3), "branco")
        t.ponto(ex + 1, ey - 1, "negro_1")
        t.linha(ex - 1, ey - 4, ex + 2, ey - 4, sob)
        if tipo == "oficial":
            for dx in (-1, 2):
                t.linha(ex + dx, ey + 1, ex + dx, ey + 6, "ceu_claro")
    else:
        t.chapado(t.retangulo(ex, ey - 1, 2, 2), "branco")
        t.ponto(ex + 1, ey, "negro_1")
        if rosto in ("bravo", "grito"):
            t.linha(ex - 1, ey - 3, ex + 2, ey - 2, sob)
            t.ponto(ex - 1, ey - 2, sob)
        else:
            t.linha(ex - 1, ey - 2, ex + 2, ey - 2, sob)
    bx, by = x + 3, y + 6
    if rosto == "grito":
        t.chapado(t.elipse(bx, by, 2, 1.3), "negro_1")
        t.linha(bx - 1, by - 1, bx + 1, by - 1, "pelo_7")
    elif rosto == "panico":
        t.chapado(t.elipse(bx, by + 0.5, 1.6, 1.8), "negro_1")
        t.ponto(bx, by + 1, "rubro_4")
    elif rosto == "morto":
        t.chapado(t.elipse(bx, by, 1.5, 1.1), "negro_1")
        t.ponto(bx + 1, by + 1, "rubro_4")
    elif rosto == "ronca":
        t.chapado(t.elipse(bx, by, 1.2, 1.2), "negro_1")
    elif rosto == "lambe":
        t.chapado(t.elipse(bx, by, 1.6, 1.1), "negro_1")
        t.ponto(bx + 1, by + 1, "rubro_4")
    elif rosto in ("saudade", "chora"):
        t.pontos([(bx - 1, by), (bx, by - 1), (bx + 1, by)], "carne_1")


def quepe(t, x, y, tipo):
    alto = 2 if tipo == "oficial" else 0
    copa = t.poligono([(x - 5.5, y - 3), (x - 4.5, y - 8 - alto), (x + 4, y - 9 - alto), (x + 5.5, y - 3.5)])
    sombrear2d(t, copa, FARDA_ESC)
    faixa = {"facao": "rubro_3", "oficial": "latao_4"}.get(tipo, "verde_1")
    t.chapado(t.retangulo(x - 5, y - 5, 10.5, 1.4) & copa, faixa)
    if tipo == "oficial":
        t.linha(x - 4, y - 3.5, x + 5, y - 3.5, "latao_6")  # cordão dourado
    pala = t.poligono([(x + 2, y - 4), (x + 9, y - 3.2), (x + 9, y - 2.2), (x + 2, y - 2.6)])
    sombrear2d(t, pala, BOTA)
    t.linha(x + 3, y - 3.6, x + 7, y - 3.2, "negro_5")
    t.ponto(x + 1, y - 7 - alto, "latao_5")  # estrela do quepe
    t.ponto(x + 1, y - 6 - alto, "latao_3")
    t.linha(x - 4, y - 3, x - 3, y + 2, "fuba_1")  # jugular


def capacete(t, x, y):
    """Capacete Adrian: cúpula com crista e aba em volta."""
    copa = t.elipse(x, y - 4.5, 5.8, 4.4) & (t.yy < y - 3)
    sombrear2d(t, copa, FARDA_ESC)
    aba = t.elipse(x + 0.5, y - 3.2, 8, 1.4)
    sombrear2d(t, aba, FARDA_ESC, -0.3)
    t.linha(x - 3, y - 9, x + 3, y - 9.5, "verde_5")  # crista
    t.ponto(x - 2, y - 7, "verde_6")


# ---------------------------------------------------------------- corpo
def tronco(t, dy, tipo, mochila=True):
    topo, base = TOPO + dy, BASE + dy
    gordo = tipo in ("metralhador", "oficial")
    m = tronco_forma(t, BX, topo, base)
    if gordo:
        m |= t.elipse(BX + 2.5, base - 5, 6.6, 5)  # barriga maior
    else:
        m |= t.elipse(BX + 2.2, base - 5, 5.6, 4.6)  # barriga
    sombrear2d(t, m, FARDA)
    # Bolso do peito com lapela e botão, carreira de botões.
    t.linha(BX + 3, topo + 5, BX + 6, topo + 5, "verde_2")
    t.ponto(BX + 4, topo + 6, "latao_5")
    for yb in (topo + 8, topo + 11):
        if m[int(yb), BX + 7]:
            t.ponto(BX + 7, yb, "verde_7")
    # Cinto com as cartucheiras de couro e a fivela.
    cy = base - 3
    cinto = t.retangulo(BX - 6, cy, 16, 2.2) & m
    t.chapado(cinto, "fuba_2")
    t.linha(BX - 6, cy, BX + 9, cy, "fuba_3")
    for x0 in (BX - 4, BX - 1):
        bolsa = t.retangulo(x0, cy - 2, 2.6, 3.4) & m
        sombrear2d(t, bolsa, COURO)
        t.ponto(x0 + 1, cy - 1, "latao_4")
    t.chapado(t.retangulo(BX + 4, cy, 2, 2.2) & m, "latao_4")
    t.ponto(BX + 4, cy, "latao_6")
    if tipo == "metralhador":
        for k in range(10):  # fita de balas no peito
            x, y = BX - 3 + k * 1.1, topo + 1 + k * 1.15
            if m[int(y), int(x)]:
                t.ponto(x, y, "latao_5" if k % 2 == 0 else "latao_3")
                t.ponto(x + 1, y, "fuba_2")
    if tipo == "oficial":
        for k in range(10):  # talabarte
            x, y = BX - 2 + k, topo + 1 + k * 1.1
            if m[int(y), int(x)]:
                t.ponto(x, y, "fuba_4")
                t.ponto(x, y + 1, "fuba_2")
        for k, cor in enumerate(("rubro_4", "ceu_medio", "latao_5")):  # medalhas
            t.ponto(BX + 3 + k * 1.5, topo + 7, cor)
            t.ponto(BX + 3 + k * 1.5, topo + 8, "latao_6")
        sombrear2d(t, t.elipse(BX - 1, topo + 1.5, 3, 1.4), LATAO)  # dragona
    if tipo == "granadeiro":
        for k in range(3):  # dinamites na cartucheira
            x0 = BX - 3 + k * 3
            t.chapado(t.retangulo(x0, topo + 4 + k * 2, 1.6, 3), "rubro_3")
            t.ponto(x0, topo + 4 + k * 2, "rubro_5")
    return m


def mochila(t, dy):
    """Mochila de lona com o cobertor enrolado em cima, presa por correias."""
    mo = t.retangulo(BX - 10, TOPO + dy + 3, 7, 10) | t.elipse(BX - 6.5, TOPO + dy + 12, 3.5, 2.5)
    sombrear2d(t, mo, LONA, -0.4)
    t.linha(BX - 10, TOPO + dy + 7, BX - 4, TOPO + dy + 7, "osso_1")
    t.ponto(BX - 7, TOPO + dy + 8, "latao_4")
    rolo = t.capsula(BX - 11, TOPO + dy + 1.5, BX - 3, TOPO + dy + 1.5, 2.2)
    sombrear2d(t, rolo, COBERTOR)
    for x in (BX - 9, BX - 5):
        t.linha(x, TOPO + dy - 0.5, x, TOPO + dy + 3.5, "fuba_1")


def cantil(t, dy):
    sombrear2d(t, t.elipse(BX - 6, BASE + dy - 1, 2.6, 3.2), FARDA_ESC, -0.6)
    t.ponto(BX - 6, BASE + dy - 5, "aco_5")


# ---------------------------------------------------------------- armas
def fuzil(t, gx, gy):
    """Mosquetão: coronha de madeira, cano de aço; (gx, gy) = mão no punho."""
    coronha = t.poligono([(gx - 9, gy - 1), (gx + 1, gy - 1), (gx + 1, gy + 2), (gx - 7, gy + 3)])
    sombrear2d(t, coronha, MADEIRA)
    t.linha(gx - 7, gy + 1, gx, gy, "fuba_2")
    guarda = t.retangulo(gx + 1, gy - 0.5, 12, 1.8)
    sombrear2d(t, guarda, MADEIRA, 0.3)
    cano = t.retangulo(gx + 1, gy - 2, 23, 1.6)
    t.chapado(cano, "aco_3")
    t.linha(gx + 1, gy - 2, gx + 23, gy - 2, "aco_6")
    for bx in (gx + 5, gx + 11):
        t.ponto(bx, gy - 0.5, "aco_5")
        t.ponto(bx, gy + 0.5, "aco_2")
    t.ponto(gx + 2, gy - 3, "aco_6")  # ferrolho
    t.ponto(gx + 21, gy - 3, "aco_3")  # massa de mira
    return (gx + 24, gy - 2)


def facao_lamina(t, a, b, r0=1.4, r1=0.8):
    m = t.capsula(*a, *b, r0, r1)
    sombrear2d(t, m, LAMINA, 0.4)
    return m


def flash(t, x, y):
    t.pontos([(x, y), (x + 1, y - 1), (x + 1, y + 1), (x + 2, y)], "latao_5")
    t.ponto(x + 1, y, "latao_6")


# ---------------------------------------------------------------- quadro
def _pernas(t, pose, passo):
    q = QUADRIL
    if pose == "anda":
        ciclo = [(-4, 4), (0, 0), (4, -4), (0, 0)][passo]
        sobe = -1 if passo in (1, 3) else 0
        tras = (BX - 1 + ciclo[1] - 3, CHAO - (1 if ciclo[1] < 0 else 0))
        frente = (BX + 4 + ciclo[0], CHAO - (1 if ciclo[0] < 0 else 0))
        return tras, frente, sobe
    if pose in ("panico", "morte"):
        return (BX - 8, CHAO), (BX + 7, CHAO - 3), 0
    return (BX - 6, CHAO), (BX + 6, CHAO), 0


def soldado(rosto="serio", pose="parado", passo=0, tipo="fuzil", braco_c=None, k=0, pernas=True):
    t = Tela(W, H)
    tras, frente, dy = _pernas(t, pose, passo)
    q = QUADRIL + dy
    if pernas:
        perna(t, (BX - 1, q), tras, atras=True)
    of, ot = (OMBRO_F[0], OMBRO_F[1] + dy), (OMBRO_T[0], OMBRO_T[1] + dy)
    hx, hy = CABECA[0], CABECA[1] + dy
    tem_mochila = braco_c is None and tipo not in ("rojao", "oficial", "facao") and MOCHILA
    # Fuzil pendurado nas costas nas cenas cômicas.
    if braco_c in ("colher", "foto"):
        sombrear2d(t, t.capsula(BX - 8, BASE + dy + 3, BX + 1, TOPO + dy - 4, 1.1), MADEIRA, -0.5)
        t.linha(BX - 3, TOPO + dy + 2, BX + 1, TOPO + dy - 6, "aco_3")
    # Braço de trás.
    if braco_c:
        braco(t, ot, (ot[0] - 2, ot[1] + 6), (ot[0] + 3, ot[1] + 9), atras=True)
        mao(t, ot[0] + 3.5, ot[1] + 9, True)
    elif pose in ("panico", "morte"):
        braco(t, ot, (ot[0] - 4, ot[1] - 6), (ot[0] - 6, ot[1] - 12), atras=True)
        mao(t, ot[0] - 6, ot[1] - 13, True)
    elif tipo in ("fuzil", "metralhador") or (tipo == "rojao"):
        pass  # mão de trás vai no punho da arma (desenhada depois)
    else:
        braco(t, ot, (ot[0] + 1, ot[1] + 6), (ot[0] + 4, ot[1] + 10), atras=True)
        mao(t, ot[0] + 4, ot[1] + 10.5, True)
    if tem_mochila:
        mochila(t, dy)
    if braco_c is None and pernas:
        cantil(t, dy)
    if tipo == "facao":
        sombrear2d(t, t.capsula(BX - 4, BASE + dy - 2, BX - 8, BASE + dy + 7, 1.2), COURO, -0.5)  # bainha
    tronco(t, dy, tipo)
    if pernas:
        perna(t, (BX + 2, q), frente)
    # Lança-rojão no ombro: tubo atrás da cabeça, rente ao olho.
    rojao_no_ombro = tipo == "rojao" and pose not in ("panico", "morte") and not braco_c
    if rojao_no_ombro:
        ty = hy + 4
        tubo = t.capsula(BX - 10, ty + 1, BX + 20, ty, 2.4)
        sombrear2d(t, tubo, FARDA_ESC)
        for bx_ in (BX - 6, BX + 15):
            t.linha(bx_, ty - 2, bx_, ty + 2, "verde_1")
        t.chapado(t.elipse(BX + 20, ty, 1.1, 2.2), "negro_1")
        if rosto != "grito":
            sombrear2d(t, t.poligono([(BX + 20.5, ty - 1.8), (BX + 25, ty), (BX + 20.5, ty + 1.8)]), VERMELHO)
    q_pula = -2 if pose == "panico" else 0
    cabeca(t, hx, hy, rosto, tipo, q_pula)

    # Braço da frente e a arma.
    boca = None
    recuo = -1 if rosto == "grito" else 0
    if braco_c:
        braco_comico(t, braco_c, k, of)
    elif pose in ("panico", "morte"):
        braco(t, of, (of[0] + 4, of[1] - 6), (of[0] + 6, of[1] - 13))
        mao(t, of[0] + 6.5, of[1] - 14)
    elif tipo == "oficial":
        if rosto == "grito":
            braco(t, of, (of[0] + 5, of[1] + 2), (of[0] + 10, of[1] + 2))
            sombrear2d(t, t.retangulo(of[0] + 10, of[1], 6, 2), ACO)
            sombrear2d(t, t.retangulo(of[0] + 10, of[1] + 1.5, 2, 3.5), MADEIRA)
            mao(t, of[0] + 10.5, of[1] + 2)
            boca = (of[0] + 16, of[1] + 0.5)
        else:
            braco(t, of, (of[0] + 6, of[1] + 1), (of[0] + 12, of[1] - 3))  # espada erguida: "AVANÇAR!"
            facao_lamina(t, (of[0] + 13, of[1] - 4), (of[0] + 24, of[1] - 14), 0.9, 0.5)
            t.linha(of[0] + 11, of[1] - 2.5, of[0] + 14, of[1] - 5.5, "latao_5")
            mao(t, of[0] + 12.5, of[1] - 3)
    elif tipo == "rojao":
        ty = hy + 4
        braco(t, ot, (ot[0] + 4, ot[1] + 5), (BX + 6, ty + 3), atras=True)
        mao(t, BX + 6, ty + 3, True)
        braco(t, of, (of[0] + 7, of[1] + 3), (of[0] + 11, ty + 3))
        mao(t, of[0] + 11.5, ty + 2.5)
        boca = (BX + 24, ty)
        if rosto == "grito":
            for kk, (dx, r) in enumerate(((0, 3.4), (-3, 2.7), (-5, 2))):
                sombrear2d(t, t.elipse(BX - 12 + dx, ty - kk, r, r * 0.9), R("pelo", 2, 6), 0.3, linha=False)
    elif tipo == "metralhador":
        gx, gy = of[0] + 1 + recuo, of[1] + 9
        sombrear2d(t, t.poligono([(gx - 8, gy - 1), (gx, gy - 1), (gx, gy + 3), (gx - 6, gy + 3.5)]), MADEIRA)
        caixa = t.retangulo(gx, gy - 1.5, 8, 4.5)
        sombrear2d(t, caixa, ACO[:5])
        sombrear2d(t, t.retangulo(gx + 2, gy - 5, 3.5, 3.5), ACO[:5])  # carregador
        camisa = t.retangulo(gx + 8, gy - 1, 14, 2.8)
        sombrear2d(t, camisa, ACO)
        for x in range(int(gx) + 9, int(gx) + 21, 2):
            t.ponto(x, gy, "aco_1")
        t.chapado(t.retangulo(gx + 22, gy - 1.5, 2.5, 3.5), "aco_2")
        braco(t, ot, (ot[0] + 3, ot[1] + 7), (gx - 1, gy + 1), atras=True)
        braco(t, of, (of[0] + 4, of[1] + 6), (gx + 9, gy + 3))
        mao(t, gx - 1, gy + 1.5, True)
        mao(t, gx + 9.5, gy + 3)
        boca = (gx + 25, gy + 0.5)
    elif tipo == "granadeiro":
        if rosto == "grito":
            braco(t, of, (of[0] - 1, of[1] - 7), (of[0] - 4, of[1] - 13))  # jogando a dinamite
            sombrear2d(t, t.capsula(of[0] - 7, of[1] - 16, of[0] - 2, of[1] - 14, 1.2), VERMELHO)
            t.linha(of[0] - 2, of[1] - 14, of[0], of[1] - 16, "fuba_1")
            t.pontos([(of[0], of[1] - 17), (of[0] + 1, of[1] - 16)], "latao_5")
            t.ponto(of[0] + 1, of[1] - 17, "pelo_7")
            mao(t, of[0] - 4, of[1] - 13.5)
            boca = (of[0] - 4, of[1] - 16)
        else:
            sombrear2d(t, t.capsula(of[0] + 7, of[1] + 6, of[0] + 10, of[1] + 11, 1.2), VERMELHO)
            t.linha(of[0] + 10, of[1] + 11, of[0] + 12, of[1] + 10, "fuba_1")
            t.ponto(of[0] + 13, of[1] + 9, "latao_5")
            braco(t, of, (of[0] + 4, of[1] + 6), (of[0] + 8, of[1] + 6))
            mao(t, of[0] + 8.5, of[1] + 6)
    elif tipo == "facao":
        if rosto == "grito":
            braco(t, of, (of[0] + 5, of[1] + 2), (of[0] + 10, of[1] + 3))  # golpe
            facao_lamina(t, (of[0] + 10, of[1] + 2.5), (of[0] + 23, of[1] + 1))
            mao(t, of[0] + 10.5, of[1] + 3)
            for kk in range(9):
                a = -1.1 + kk * 0.25
                t.ponto(of[0] + 12 + math.cos(a) * 12, of[1] + 3 + math.sin(a) * 12, "pelo_7")
            boca = (of[0] + 23, of[1] + 1)
        else:
            braco(t, of, (of[0] + 6, of[1] + 2), (of[0] + 12, of[1] - 3))  # facão erguido
            facao_lamina(t, (of[0] + 13, of[1] - 5), (of[0] + 19, of[1] - 17))
            sombrear2d(t, t.capsula(of[0] + 12, of[1] - 2, of[0] + 13, of[1] - 5, 1.1), COURO)
            mao(t, of[0] + 12.5, of[1] - 3)
    else:
        gx, gy = of[0] + 2 + recuo, of[1] + 7
        braco(t, ot, (ot[0] + 3, ot[1] + 7), (gx, gy), atras=True)
        boca = fuzil(t, gx, gy)
        braco(t, of, (of[0] + 3, of[1] + 7), (gx + 8, gy + 1))
        mao(t, gx, gy + 0.5, True)
        mao(t, gx + 8.5, gy + 1)
    t.contorno("negro_1")
    if rosto == "grito" and boca and tipo in ("fuzil", "metralhador", "rojao", "oficial"):
        flash(t, boca[0] + 1, boca[1])
    if boca and pose == "parado" and rosto == "grito":
        CANO[tipo] = [int(round(boca[0])) - PE[0], PE[1] - int(round(boca[1]))]
    return t


CARTA = ["negro_2", "pelo_4", "pelo_6", "pelo_7"]


def carta(t, cx, cy, ang, naipe="rubro_3"):
    c, s_ = math.cos(ang), math.sin(ang)
    cantos = [(-1.6, -2.6), (1.6, -2.6), (1.6, 2.6), (-1.6, 2.6)]
    pts = [(cx + x * c - y * s_, cy + x * s_ + y * c) for x, y in cantos]
    sombrear2d(t, t.poligono(pts), CARTA, 0.6)
    t.ponto(cx, cy, naipe)


def braco_comico(t, tipo_braco, k, of):
    if tipo_braco == "cartas":
        if k == 1:  # "TRUCO!": braço lá em cima batendo a carta
            braco(t, of, (of[0] + 6, of[1] - 4), (of[0] + 12, of[1] - 12))
            carta(t, of[0] + 14, of[1] - 16, 0.6, "negro_1")
            mao(t, of[0] + 12, of[1] - 12)
        else:  # leque de cartas na frente do peito
            braco(t, of, (of[0] + 5, of[1] + 3), (of[0] + 8, of[1] - 1))
            for n, (dx, a, cor) in enumerate(((-2, -0.6, "rubro_3"), (0, -0.2, "negro_1"), (2, 0.2, "rubro_3"),
                                              (4, 0.6, "negro_1"))):
                carta(t, of[0] + 8 + dx, of[1] - 5 + abs(dx - 1) * 0.3, a, cor)
            mao(t, of[0] + 8.5, of[1] - 1)
    elif tipo_braco == "colher":
        dx = (-2, 2)[k % 2]
        braco(t, of, (of[0] + 5, of[1] + 5), (of[0] + 9 + dx, of[1] + 6))
        sombrear2d(t, t.capsula(of[0] + 9 + dx, of[1] + 5, of[0] + 13 + dx * 1.5, of[1] + 16, 0.8, 0.6), MADEIRA)
        mao(t, of[0] + 9.5 + dx, of[1] + 6)
    elif tipo_braco == "foto":
        sobe = k % 2
        braco(t, of, (of[0] + 6, of[1] + 1), (of[0] + 10, of[1] - 4 - sobe))
        fx, fy = of[0] + 10, of[1] - 13 - sobe
        t.chapado(t.retangulo(fx, fy, 7, 8), "negro_1")
        t.chapado(t.retangulo(fx + 0.5, fy + 0.5, 6, 7), "osso_5")
        t.chapado(t.retangulo(fx + 1.5, fy + 1.5, 4, 5), "osso_2")
        t.chapado(t.elipse(fx + 3.5, fy + 3, 1.1, 1.2), "osso_4")
        t.chapado(t.retangulo(fx + 2.3, fy + 4.5, 2.5, 2), "osso_3")
        mao(t, of[0] + 10.5, of[1] - 4 - sobe)


def sentado(tipo, k=0, rosto=None, braco_c=None):
    """Sentado no chão cochilando (k=1: cabeça mais baixa, roncando) ou jogando truco."""
    cima = soldado(rosto or ("ronca" if k else "dorme"), "parado", tipo=tipo, braco_c=braco_c, k=k if braco_c else 0,
                   pernas=False)
    t = Tela(W, H)
    desce = 9 + k
    for y in range(H - 1, -1, -1):
        yy = y + desce
        if yy >= H:
            continue
        linha = cima.px[y]
        mm = linha != VAZIO
        t.px[yy][mm] = linha[mm]
    # Joelhos para cima, na frente da barriga.
    perna(t, (BX - 1, 41), (BX + 9, CHAO), atras=True, joelho=(BX + 6, 35))
    perna(t, (BX + 3, 41), (BX + 14, CHAO), joelho=(BX + 11, 34))
    t.contorno("negro_1")
    return t


def comico(nome, tipo="fuzil"):
    if nome == "cartas1":
        return sentado(tipo, 0, rosto="serio", braco_c="cartas")
    if nome == "cartas2":
        return sentado(tipo, 1, rosto="grito", braco_c="cartas")
    k = int(nome[-1]) - 1
    if nome.startswith("mexe"):
        return soldado("lambe" if k else "serio", "parado", tipo=tipo, braco_c="colher", k=k)
    return soldado("chora" if k else "saudade", "parado", tipo=tipo, braco_c="foto", k=k)


MOCHILA = True


def variante(tipo):
    anda = "bravo" if tipo == "facao" else "serio"
    d = {
        "parado": lambda: soldado("serio", tipo=tipo),
        "atira": lambda: soldado("grito", tipo=tipo),
        "panico": lambda: soldado("panico", "panico", tipo=tipo),
        "anda1": lambda: soldado(anda, "anda", 0, tipo=tipo),
        "anda2": lambda: soldado(anda, "anda", 1, tipo=tipo),
        "anda3": lambda: soldado(anda, "anda", 2, tipo=tipo),
        "anda4": lambda: soldado(anda, "anda", 3, tipo=tipo),
        "morte": lambda: soldado("morto", "morte", tipo=tipo),
        "sentado1": lambda: sentado(tipo, 0),
        "sentado2": lambda: sentado(tipo, 1),
    }
    if tipo == "fuzil":
        for n in ("cartas1", "cartas2", "mexe1", "mexe2", "foto1", "foto2"):
            d[n] = (lambda n: lambda: comico(n))(n)
    return d


ARQUIVOS = {"volante": "fuzil", "granadeiro": "granadeiro", "metralhador": "metralhador", "facao": "facao",
            "rojao": "rojao", "oficial": "oficial"}


def gravar():
    for arq, tipo in ARQUIVOS.items():
        pixel.salvar(f"{arq}.txt", {n: f() for n, f in variante(tipo).items()})
    return CANO


if __name__ == "__main__":
    print(gravar())
