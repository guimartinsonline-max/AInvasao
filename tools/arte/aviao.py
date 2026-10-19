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
    """Atirador de trás (28x24) no anel da metralhadora (anel Scarff de ferro rebitado
    com o pino central). A arma é outra peça (metralhadora_torreta) que gira no pino e
    aponta para onde ele atira. Quadros: 0 mirando, 1 olhando para baixo, 2 atirando
    (gritando), 3 morto. Desenhado olhando para a esquerda; o jogo espelha."""
    t = Tela(28, 24)
    morto = q == 3
    # Anel de ferro em volta da cabine, com rebites e o pino que segura a arma.
    anel = t.capsula(3, 21, 25, 21, 1.6)
    t.cel(anel, FERRO, sombra=1)
    for x in range(5, 25, 4):
        t.ponto(x, 20, "cinza_luz")
    t.cel(t.capsula(14, 20, 14, 15, 1.1), FERRO, sombra=0)  # pino
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
    baixo = q == 1
    # Jaqueta de couro com gola de pele, cachecol vermelho esvoaçando.
    corpo = t.elipse(16, 16, 5, 5) & (t.yy < 21)
    t.volume(corpo, ["sombra", "couro_escuro", "couro", "couro_medio", "couro_luz"], achatado=2, suave=0.6, ambiente=0.3)
    t.cel(t.capsula(17, 12, 24, 11 + (1 if q == 2 else 0), 1.0, 0.5), ["vermelho_esc", "vermelho_medio", "vermelho"], sombra=0)
    hx, hy = (14, 10) if baixo else (15, 9)
    # Capacete de couro com abas, óculos de aviador puxados nos olhos.
    t.cel(t.elipse(hx, hy, 3.8, 3.8), COURO, sombra=1)
    t.cel(t.elipse(hx - 2.3, hy + 1.3 + (1 if baixo else 0), 2.3, 2.2), PELE, sombra=1)
    t.cel(t.capsula(hx - 4.5, hy, hx + 1, hy, 1.1), ["sombra", "cinza_escuro", "cinza_medio"], sombra=0)
    t.chapado(t.elipse(hx - 3.5, hy, 1.1, 1), "ceu_claro")
    t.ponto(hx - 3.9, hy - 0.4, "branco")
    t.cel(t.capsula(hx + 2.5, hy + 1, hx + 3, hy + 4, 0.9), COURO, sombra=0)  # aba do capacete
    if q == 2:
        t.chapado(t.elipse(hx - 2.2, hy + 3.4, 1.0, 0.9), "preto")  # gritando
    else:
        t.ponto(hx - 2, hy + 3.5, "preto")
    # Braços nos punhos da arma (que fica no pino em 14,14).
    t.cel(t.capsula(16, 15, 11, 14, 1.3), ["sombra", "couro_escuro", "couro", "couro_medio"], sombra=0)
    t.cel(t.elipse(10.5, 14, 1.5, 1.3), PELE, sombra=0)
    t.contorno("sombra")
    return t


def metralhadora_torreta(q=0):
    """Metralhadora de tambor no anel do artilheiro (estilo Lewis), apontando para a
    direita a partir do pino (6, 6): punho de pá de madeira, culatra de ferro, tambor
    chato em cima com raios e trava, camisa de refrigeração com aletas, alça e massa
    de mira, boca com quebra-chamas. Quadro 1: atirando (recuo e clarão)."""
    t = Tela(30, 12)
    r = -1 if q == 1 else 0  # recuo
    cy = 6
    # Punho de pá (madeira) e coronha curta.
    t.cel(t.capsula(1 + r, cy + 1, 5 + r, cy + 1, 1.6), MADEIRA, sombra=1)
    t.cel(t.capsula(2 + r, cy - 1, 2 + r, cy + 3, 0.9), MADEIRA, sombra=0)
    # Culatra.
    t.cel(t.retangulo(5 + r, cy - 1.5, 7, 4), FERRO, sombra=1)
    t.ponto(9 + r, cy + 2.5, "preto")  # gatilho
    # Camisa de refrigeração grossa com aletas.
    camisa = t.capsula(12 + r, cy, 23 + r, cy, 2.3, 1.9)
    t.cel(camisa, ["preto", "sombra", "cinza_escuro", "cinza_medio"], sombra=1)
    for x in range(13, 23, 2):
        t.linha(x + r, cy - 1.5, x + r, cy + 1.5, "sombra")
    t.linha(13 + r, cy - 1.8, 22 + r, cy - 1.8, "cinza")  # brilho de cima
    # Cano e quebra-chamas na boca.
    t.cel(t.capsula(23 + r, cy, 27 + r, cy, 0.9), FERRO, sombra=0)
    t.cel(t.retangulo(26 + r, cy - 1.2, 2, 2.6), FERRO, sombra=0)
    # Massa de mira e alça.
    t.ponto(25 + r, cy - 2, "cinza_escuro")
    t.ponto(11 + r, cy - 3, "cinza_escuro")
    # Tambor chato em cima: disco cinza com raios e o centro.
    tambor = t.elipse(8 + r, cy - 3.2, 4.2, 1.6)
    t.cel(tambor, ["sombra", "cinza_escuro", "cinza_medio", "cinza"], sombra=1)
    for dx in (-2.5, -0.8, 0.9, 2.6):
        t.ponto(8 + dx + r, cy - 3.4, "sombra")
    t.ponto(8 + r, cy - 3.8, "cinza_luz")
    t.contorno("sombra")
    if q == 1:
        # Clarão curto na boca.
        t.chapado(t.elipse(29, cy, 1.6, 2.2), "laranja_fogo")
        t.chapado(t.elipse(29, cy, 0.8, 1.2), "amarelo_claro")
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


def destrocado():
    """Carcaça do biplano no chão: lona queimada mostrando o esqueleto de cavernas,
    cauda partida caída na terra, asa de cima desabada em V, hélice com uma pá só,
    nariz arriado sobre o trem quebrado; fuligem, brasas e pedaços espalhados."""
    import destrocos as ds
    from motor import VAZIO
    t = biplano(4)
    px = t.px
    h, w = px.shape
    # Hélice: some a pá de baixo (fica um toco).
    px[33:h, 110:118] = np.where(px[33:h, 110:118] >= 0, VAZIO, px[33:h, 110:118])
    # Lona do meio da fuselagem queimada: só o esqueleto (cavernas e longarinas).
    yy, xx = np.mgrid[0:h, 0:w]
    meio = (xx > 30) & (xx < 74) & (yy > 23) & (yy < 38) & (px != VAZIO)
    esqueleto = meio & (((xx - 30) % 6 == 0) | (np.abs(yy - 25) < 0.6) | (np.abs(yy - 36) < 0.6)
                        | (np.abs((xx - 30) % 12 - (yy - 24) * 0.85) < 0.6))
    px[meio & ~esqueleto] = VAZIO
    px[esqueleto] = IDX["cinza_escuro"]
    px[esqueleto & ((xx + yy) % 5 == 0)] = IDX["laranja_escuro"]
    # Asa de cima desabada em V: a metade de trás cai mais (e a ponta encosta na fuselagem).
    asa = (yy < 15) & (xx > 48) & (xx < 102) & (px != VAZIO)
    copia = np.where(asa, px, VAZIO)
    px[asa] = VAZIO
    for x in range(49, 102):
        d = int(10 - (x - 49) * 0.12) if x < 74 else int(3 + (x - 74) * 0.05)
        if 72 <= x <= 75:
            continue  # quebrada no meio
        col = copia[:15, x]
        for y in range(15):
            if col[y] != VAZIO and y + d < h:
                px[y + d, x] = col[y]
    # Cauda partida: tudo à esquerda de x=30 cai torto até a bequilha bater no chão.
    cauda = px[:, :31].copy()
    px[:, :31] = VAZIO
    for x in range(31):
        d = int(4 + (30 - x) * 0.45)
        col = cauda[:, x]
        for y in range(h - 1, -1, -1):
            if col[y] != VAZIO and y + d < h:
                px[y + d, x] = col[y]
    # Nariz arriado: a frente desce 4 px sobre o trem quebrado (a roda fica).
    roda = (xx > 82) & (xx < 103) & (yy > 40)
    frente = (xx > 60) & (px != VAZIO) & ~roda
    copia = np.where(frente, px, VAZIO)
    px[frente] = VAZIO
    for y in range(h - 1, -1, -1):
        for x in range(61, w):
            if copia[y, x] != VAZIO and y + 4 < h and not roda[y + 4, x]:
                px[y + 4, x] = copia[y, x]
    t.px = px
    return ds.destrocar(t, semente=11, partir=False, afunda=2, rasgos=3, pedacos=6, chassi=0.9)
