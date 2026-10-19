"""Biplano da Aviação Militar (subchefe da fase 1), desenhado com o motor,
virado para a direita (o jogo espelha):

- biplano(q): fuselagem de lona verde-oliva com as nervuras marcando, asas
  prateadas em perfil, montantes em N, motor radial com cilindros, leme
  listrado de verde e amarelo com a estrela, trem de pouso e bequilha.
  q=0 hélice parada; q=1..3 hélice girando (borrão e pá em posições);
  q=4 carcaça queimada.
- artilheiro(q): o atirador do banco de trás com a metralhadora no anel,
  sprite à parte (quebra separado): 0 mira para trás, 1 mira para baixo
  (rasante), 2 atirando, 3 morto pendurado para fora.
- bomba(q): bomba de aviação com aletas (2 quadros, girando a aleta).
- biruta(q): biruta do campo de pouso balançando no vento (3 quadros).
Pé (roda no chão) em BIPLANO_RODA. Usado por tools/arte/exportar.py.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from motor import Tela, IDX  # noqa: E402
import veiculos as vc  # noqa: E402

W, H = 132, 60
BIPLANO_RODA = (92, 59)  # ponto de contato da roda com o chão

OLIVA = ["sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru"]
PRATA = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz", "cinza_claro"]
MOTOR = ["preto", "sombra", "sombra_media", "cinza_escuro", "cinza_medio", "cinza"]
MADEIRA = ["marrom_noite", "couro_profundo", "couro_escuro", "couro", "couro_medio", "couro_luz"]
COURO = ["marrom_noite", "couro_profundo", "couro_escuro", "couro"]
PELE = ["pele_sombra", "pele_media", "pele", "pele_luz"]
FERRO = ["sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"]


def asa(t, x0, x1, y, espessura=4.5):
    """Asa vista de lado: perfil com bordo de ataque redondo à direita e fino atrás."""
    corda = x1 - x0
    pts = []
    for k in range(0, 21):
        f = k / 20
        # Perfil Clark Y simplificado: barriga quase reta, dorso em curva.
        dorso = espessura * (1.4 * math.sqrt(max(0.0, 1 - f)) * f ** 0.35)
        pts.append((x1 - f * corda, y - dorso))
    for k in range(20, -1, -1):
        f = k / 20
        barriga = espessura * 0.18 * math.sqrt(max(0.0, 1 - f)) * 2
        pts.append((x1 - f * corda, y + barriga))
    m = t.poligono(pts)
    t.volume(m, PRATA, achatado=1.4, suave=0.5, ambiente=0.35, brilho=1.25)
    # Nervuras da lona e o bordo de ataque brilhando.
    for x in range(int(x0) + 5, int(x1) - 3, 5):
        t.px[(np.abs(t.xx - x) < 0.5) & m & (t.yy < y)] = IDX["cinza_medio"]
    t.chapado(m & (t.xx > x1 - 3) & (t.yy < y), "cinza_claro")
    return m


def montante(t, a, b, r=0.8):
    t.cel(t.capsula(a[0], a[1], b[0], b[1], r), FERRO, sombra=0)


def biplano(q=0):
    t = Tela(W, H)
    queimado = q == 4
    # Asa de baixo e estabilizador ficam atrás da fuselagem.
    asa(t, 4, 30, 30.5, espessura=2.6)  # estabilizador horizontal
    # Trem de pouso: V de tubos até o eixo, roda de raios com pneu.
    rx, ry, rr = 92, 50, 9
    montante(t, (84, 40), (rx, ry), 1.1)
    montante(t, (98, 40), (rx, ry), 1.1)
    # Bequilha na cauda.
    montante(t, (16, 34), (13, 40), 0.9)
    t.chapado(t.elipse(13, 40, 1.5, 1.2), "sombra")
    # Fuselagem de lona esticada sobre a estrutura (afinando até a cauda).
    corpo = t.poligono([(103, 22), (86, 19.5), (60, 20.5), (30, 25), (12, 28), (10, 30.5), (12, 33),
                        (30, 35.5), (60, 39.5), (86, 41), (103, 40)])
    t.volume(corpo, OLIVA, achatado=4, suave=1.4, ambiente=0.3, textura=0.06, semente=3)
    # Nervuras das cavernas e longarinas aparecendo pela lona.
    for x in range(22, 100, 7):
        t.px[(np.abs(t.xx - x) < 0.5) & corpo & ~(t.yy < 23)] = IDX["caatinga_esc"]
    t.px[corpo & (np.abs(t.yy - (24 + (100 - t.xx) * 0.03)) < 0.5)] = IDX["mandacaru"]
    # Faixa de chapa perto do motor (rebites).
    chapa = corpo & (t.xx > 92)
    t.volume(chapa, FERRO, achatado=2, suave=0.6, ambiente=0.35, brilho=1.1)
    for y in range(23, 40, 3):
        t.ponto(93, y, "cinza_claro")
    # Escapamento soltando fuligem pelo lado.
    t.cel(t.capsula(88, 35, 70, 36.5, 1.1), MOTOR, sombra=0)
    t.chapado(t.elipse(66, 36, 3.5, 1.2) & corpo, "caatinga_esc")
    # Estrela da aviação na fuselagem: círculo azul, estrela amarela.
    t.cel(t.elipse(30, 31, 4.6, 4.6) & corpo, ["sombra", "ceu_escuro", "azul_medio", "ceu_medio"], sombra=1)
    estrela = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        r = 4.2 if k % 2 == 0 else 1.8
        estrela.append((30 + math.cos(a) * r * 0.9, 31 + math.sin(a) * r * 0.9))
    t.cel(t.poligono(estrela), ["ouro_escuro", "amarelo_fogo", "amarelo_fogo", "amarelo_claro"], sombra=0)
    # Leme listrado de verde e amarelo (como os aviões militares brasileiros da época).
    leme = t.poligono([(11, 29), (7, 16), (9, 12.5), (15, 12), (22, 27)])
    t.volume(leme, OLIVA, achatado=2, suave=0.6, ambiente=0.35)
    for k, cor in enumerate(("caatinga", "amarelo_fogo", "caatinga")):
        faixa = leme & (t.xx >= 8 + k * 2.6) & (t.xx < 10.6 + k * 2.6)
        t.chapado(faixa, cor)
    t.chapado(leme & (t.xx < 8.5), "caatinga_esc")
    # Cabines: buraco escuro com a borda de couro acolchoada.
    for cx_, larg in ((80, 9), (46, 9)):
        t.chapado(t.elipse(cx_, 21, larg / 2, 2.2) & (t.yy > 19), "preto")
        t.cel(t.capsula(cx_ - larg / 2, 21.5, cx_ + larg / 2, 21, 0.8), COURO, sombra=0)
    # Para-brisa do piloto.
    t.chapado(t.poligono([(85, 21), (87, 15.5), (88.5, 15.5), (88, 21)]), "ceu_medio")
    t.linha(87, 15.5, 88.5, 15.5, "cinza_claro")
    # Piloto: capacete de couro, óculos de aviador, cachecol branco voando para trás.
    if not queimado:
        hx, hy = 79.5, 15.5
        t.cel(t.elipse(hx, hy, 4, 4), COURO, sombra=1)
        t.cel(t.elipse(hx + 2.5, hy + 1.5, 2.5, 2.3), PELE, sombra=1)
        t.cel(t.capsula(hx - 1, hy, hx + 4.5, hy, 1.2), ["sombra", "cinza_escuro", "cinza_medio"], sombra=0)
        t.chapado(t.elipse(hx + 3.5, hy, 1.2, 1.1), "ceu_claro")
        t.ponto(hx + 3, hy - 1, "branco")
        t.cel(t.poligono([(hx - 1, hy + 3.5), (hx - 9, hy + 2.5 - q % 2), (hx - 12, hy + 4 - q % 2), (hx - 2, hy + 5)]),
              ["cinza_luz", "cinza_claro", "branco", "branco"], sombra=0)
    # Asa de cima com os montantes de cabana e os montantes em N entre as asas.
    montante(t, (76, 20), (73, 11))
    montante(t, (86, 20), (84, 10.5))
    asa(t, 52, 99, 10.5, espessura=4.6)
    asa(t, 54, 99, 41.5, espessura=4.2)  # asa de baixo (bordo na frente da fuselagem)
    for xs in (64, 90):
        montante(t, (xs, 11), (xs + 1, 38))
        montante(t, (xs - 5, 11.5), (xs + 1, 38), 0.6)  # cabo de aço em diagonal
    # Roda por cima do trem.
    vc.roda(t, rx, ry, rr, quadro=q % 3, raios=5)
    # Motor radial: capô redondo e os cilindros com aletas aparecendo.
    capo = t.elipse(105, 31, 5.5, 10.5)
    t.volume(capo, MOTOR, achatado=2.5, suave=0.7, ambiente=0.3, brilho=1.2)
    for k in range(5):
        a = -1.1 + k * 0.55
        cy = 31 + math.sin(a) * 8.5
        t.cel(t.capsula(106, cy, 110, cy, 1.4), FERRO, sombra=0)
        t.pontos([(107, int(cy)), (109, int(cy))], "sombra")
    t.cel(t.elipse(111.5, 31, 1.8, 2.6), MOTOR, sombra=0)  # cubo
    t.contorno("sombra")
    # Hélice de madeira (desenhada depois do contorno para o borrão ficar leve).
    if q == 0 or queimado:
        pa = t.capsula(113, 14, 113, 48, 1.3)
        t.cel(pa, MADEIRA, sombra=1)
        t.chapado(t.retangulo(112.4, 14, 1.4, 3), "cinza_claro")  # ponteira de metal
        t.chapado(t.retangulo(112.4, 45, 1.4, 3), "cinza_claro")
    else:
        # Disco borrado (pontilhado claro) e a pá numa posição diferente a cada quadro.
        disco = t.elipse(113.5, 31, 1.6, 17)
        xadrez = ((t.xx.astype(int) + t.yy.astype(int) + q) % 3) == 0
        t.px[disco & xadrez] = IDX["cinza_claro"]
        meia = {1: (14, 31), 2: (31, 48), 3: (22, 40)}[q]
        t.cel(t.capsula(113.5, meia[0], 113.5, meia[1], 1.1), MADEIRA, sombra=0)
        t.pontos([(113, 13 + q * 2), (114, 49 - q * 2)], "branco")
    t.cel(t.elipse(114, 31, 1.6, 1.8), FERRO, sombra=0)
    if queimado:
        vc.queimar(t, semente=9)
    return t


def artilheiro(q=0):
    """Atirador de trás (28x24), virado para a direita (a arma aponta para trás, à esquerda).
    O pé do quadro (centro de baixo) fica na borda da cabine."""
    t = Tela(28, 24)
    morto = q == 3
    # Anel da metralhadora em volta da cabine.
    t.cel(t.capsula(4, 21, 24, 21, 1.2), FERRO, sombra=0)
    if morto:
        # Debruçado para fora da cabine, braços pendurados, olhos em X.
        corpo = t.elipse(10, 17, 5, 4)
        t.volume(corpo, ["sombra", "couro_escuro", "couro", "couro_medio"], achatado=2, suave=0.6)
        t.cel(t.elipse(5, 19, 3.6, 3.4), COURO, sombra=1)
        t.cel(t.elipse(4, 21, 2.4, 1.8), PELE, sombra=1)
        t.cel(t.capsula(8, 19, 6, 23.5, 1.1), ["sombra", "couro_escuro", "couro"], sombra=0)
        t.linha(3, 20, 5, 22, "preto")
        t.linha(3, 22, 5, 20, "preto")
        t.contorno("sombra")
        return t
    # Jaqueta de couro e o capacete com óculos.
    corpo = t.elipse(15, 16, 5, 5) & (t.yy < 21)
    t.volume(corpo, ["sombra", "couro_escuro", "couro", "couro_medio", "couro_luz"], achatado=2, suave=0.6, ambiente=0.3)
    hx, hy = 15, 9
    t.cel(t.elipse(hx, hy, 3.8, 3.8), COURO, sombra=1)
    t.cel(t.elipse(hx - 2.3, hy + 1.3, 2.3, 2.2), PELE, sombra=1)  # olhando para trás
    t.cel(t.capsula(hx - 4.5, hy, hx + 1, hy, 1.1), ["sombra", "cinza_escuro", "cinza_medio"], sombra=0)
    t.chapado(t.elipse(hx - 3.5, hy, 1.1, 1), "ceu_claro")
    t.ponto(hx - 2, hy + 3.5, "preto")  # boca gritando
    # Metralhadora de tambor no anel, apontando para trás (ou para baixo no rasante).
    baixo = q == 1
    ang = math.pi + (0.55 if baixo else 0.0)
    bx, by = 14, 14
    ex, ey = bx + math.cos(ang) * 13, by - math.sin(ang) * 13 * (-1)
    ey = by + math.sin(0.55) * 13 if baixo else by
    t.cel(t.capsula(bx, by, ex, ey, 1.2), FERRO, sombra=0)
    t.cel(t.capsula(bx + 2, by + 1, bx - 1, by + 1, 1.6), MADEIRA, sombra=0)
    t.cel(t.elipse(bx - 2, by - 2.5, 2.8, 1.4), ["sombra", "cinza_escuro", "cinza_medio"], sombra=0)  # tambor
    t.chapado(t.elipse(ex, ey, 1, 1), "preto")
    # Mãos na arma.
    t.cel(t.elipse(bx - 3, by + 1.5, 1.6, 1.4), PELE, sombra=0)
    t.contorno("sombra")
    if q == 2:
        t.pontos([(int(ex) - 1, int(ey)), (int(ex) - 2, int(ey) - 1), (int(ex) - 2, int(ey) + 1)], "amarelo_fogo")
    return t


def bomba(q=0):
    t = Tela(14, 8)
    corpo = t.elipse(7, 4, 5.5, 2.6)
    t.volume(corpo, ["sombra", "caatinga_esc", "caatinga_media", "caatinga"], achatado=1.5, suave=0.5, ambiente=0.35)
    t.chapado(t.retangulo(8, 1.6, 1, 4.8) & corpo, "amarelo_fogo")  # faixa
    d = 1 if q else 0
    t.cel(t.poligono([(1.5, 4), (0, 1 + d), (2.5, 2.5)]), FERRO, sombra=0)
    t.cel(t.poligono([(1.5, 4), (0, 7 - d), (2.5, 5.5)]), FERRO, sombra=0)
    t.contorno("sombra")
    return t


def biruta(q=0):
    """Mastro com a biruta listrada de laranja e branco (18x46), pé no centro de baixo."""
    t = Tela(26, 46)
    t.cel(t.capsula(4, 45, 4, 4, 0.9), FERRO, sombra=0)
    t.chapado(t.elipse(4, 4, 1.4, 1.4), "cinza_claro")
    cai = (0, 2, 4)[q]
    pts = [(5, 4), (24, 5 + cai), (24, 9 + cai), (5, 10)]
    m = t.poligono(pts)
    t.volume(m, ["laranja_escuro", "laranja_fogo", "amarelo_fogo"], achatado=1.2, suave=0.4, ambiente=0.4)
    for k in range(2):
        x0 = 10 + k * 8
        t.chapado(m & (t.xx >= x0) & (t.xx < x0 + 4), "branco")
    t.contorno("sombra")
    return t
