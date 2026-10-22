"""Itens no padrão novo (ESTILO.md, 20/10): caixas de arma, comidas, caixote e barril.

Volume pelo `volume3d` (luz de um lado só, cima-esquerda), rampas saturadas da
paleta (`aco_*`, `fuba_*`, `rubro_*`, `latao_*`...), contorno escuro só na silhueta
e desgaste (risco, ferrugem, amassado, migalha). Tamanhos iguais aos de antes,
para o jogo não precisar mudar a física.

Usado por tools/arte/exportar.py:
  item_<arma>.png (24x22), comida_<nome>.png, caixote.png (24x18), barril.png (2 x 18x24).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from motor import IDX, VAZIO, Tela  # noqa: E402
from volume3d import Cena, sombrear2d  # noqa: E402

ACO = [f"aco_{k}" for k in range(1, 7)]
FUBA = [f"fuba_{k}" for k in range(1, 8)]
RUBRO = [f"rubro_{k}" for k in range(1, 7)]
LATAO = [f"latao_{k}" for k in range(1, 7)]
VERDE = [f"verde_{k}" for k in range(1, 8)]
OSSO = [f"osso_{k}" for k in range(1, 6)]
PELO = [f"pelo_{k}" for k in range(1, 8)]
CARNE = [f"carne_{k}" for k in range(1, 8)]
NEGRO = [f"negro_{k}" for k in range(1, 7)]
CONTORNO = "negro_1"

# Barro de panela e prato: terracota saturada.
BARRO = ["fuba_1", "rubro_2", "fuba_3", "fuba_4", "fuba_5"]

# ------------------------------------------------------------ util


def pinta(t, x, y, cor):
    if 0 <= x < t.w and 0 <= y < t.h:
        t.px[y, x] = IDX[cor]


def contornar(t, cor=CONTORNO):
    t.contorno(cor)
    return t


def reluz(t, mascara, de, para):
    """Troca uma cor por outra dentro da máscara (risco, ferrugem)."""
    sel = mascara & (t.px == IDX[de])
    t.px[sel] = IDX[para]


# ------------------------------------------------------------ caixas de arma

LETRAS = {
    "M": ["XXX......XXX", "XXXX....XXXX", "XXXXX..XXXXX", "XXX.XXXX.XXX", "XXX..XX..XXX", "XXX......XXX",
          "XXX......XXX", "XXX......XXX", "XXX......XXX", "XXX......XXX", "XXX......XXX"],
    "B": ["XXXXXXXX.", "XXXXXXXXX", "XXX...XXX", "XXX...XXX", "XXXXXXXX.", "XXXXXXXX.",
          "XXX...XXX", "XXX...XXX", "XXX...XXX", "XXXXXXXXX", "XXXXXXXX."],
    "R": ["XXXXXXXX.", "XXXXXXXXX", "XXX...XXX", "XXX...XXX", "XXX...XXX", "XXXXXXXX.",
          "XXXXXXX..", "XXX.XXX..", "XXX..XXX.", "XXX...XXX", "XXX...XXX"],
    "D": ["XXXXXXX..", "XXXXXXXX.", "XXX..XXXX", "XXX...XXX", "XXX...XXX", "XXX...XXX",
          "XXX...XXX", "XXX...XXX", "XXX..XXXX", "XXXXXXXX.", "XXXXXXX.."],
    "C": ["..XXXXXX.", ".XXXXXXXX", "XXXX...XX", "XXX......", "XXX......", "XXX......",
          "XXX......", "XXX......", "XXXX...XX", ".XXXXXXXX", "..XXXXXX."],
    "P": ["XXXXXXXX.", "XXXXXXXXX", "XXX...XXX", "XXX...XXX", "XXX...XXX", "XXXXXXXXX",
          "XXXXXXXX.", "XXX......", "XXX......", "XXX......", "XXX......"],
    "E": ["XXXXXXXXX", "XXXXXXXXX", "XXX......", "XXX......", "XXXXXXX..", "XXXXXXX..",
          "XXX......", "XXX......", "XXX......", "XXXXXXXXX", "XXXXXXXXX"],
    "F": ["XXXXXXXXX", "XXXXXXXXX", "XXX......", "XXX......", "XXXXXXX..", "XXXXXXX..",
          "XXX......", "XXX......", "XXX......", "XXX......", "XXX......"],
    "G": ["..XXXXXX.", ".XXXXXXXX", "XXXX...XX", "XXX......", "XXX......", "XXX..XXXX",
          "XXX..XXXX", "XXX...XXX", "XXXX..XXX", ".XXXXXXXX", "..XXXXXX."],
}

# Cor da letra de cada arma (escuro -> brilho). A mesma cor de antes, agora em rampa saturada.
CORES_ARMA = {
    "madsen": ("M", RUBRO),
    "bacamarte": ("B", LATAO),
    "rojao": ("R", ["vermelho_esc", "vermelho_medio", "laranja_escuro", "laranja_fogo", "amarelo_fogo", "amarelo_claro"]),
    "desintegrador": ("D", ["alien_profundo", "alien_esc", "alien_medio", "alien", "alien_luz", "alien_brilho"]),
    "candeeiro": ("C", ["azul_sombra", "azul_medio", "ceu_escuro", "ceu", "ceu_medio", "ceu_luz"]),
    "papo_amarelo": ("P", PELO[1:]),
    "estilingue": ("E", FUBA[1:]),
    "buscape": ("F", ["roxo_escuro", "roxo", "lilas", "lilas_claro", "pelo_6", "pelo_7"]),
    "granadas": ("G", VERDE[1:]),
}

CAIXA_W, CAIXA_H = 24, 22


def caixa_arma(nome, semente=0):
    """Caixa de chapa vista um pouco de cima (tampa aparecendo), bisel aceso em cima
    e à esquerda, painel afundado e a letra gorda da arma com volume e extrusão."""
    letra, rampa = CORES_ARMA[nome]
    rng = np.random.default_rng(semente + 11)
    W, H = CAIXA_W, CAIXA_H
    t = Tela(W, H)
    # Tampa (face de cima), um trapézio fino: fundo mais escuro, beirada da frente acesa.
    for y in range(1, 5):
        rec = 4 - y
        for x in range(1 + rec, W - 1 - rec):
            cor = "aco_4" if y < 3 else "aco_5"
            if y == 4:
                cor = "aco_6"
            pinta(t, x, y, cor)
    # Faixa da cor da arma pintada na tampa.
    for x in range(7, W - 7):
        pinta(t, x, 2, rampa[3])
        pinta(t, x, 3, rampa[2])
    # Frente: chapa com luz de cima-esquerda (degradê em faixas), lado direito na sombra.
    for y in range(5, H - 1):
        for x in range(1, W - 1):
            v = 0.62 - (y - 5) / (H - 6) * 0.30 - (x - 1) / (W - 2) * 0.16
            cor = ACO[int(np.clip(v * 6, 1, 4))]
            if x == 1:
                cor = "aco_5"
            if x >= W - 3:
                cor = "aco_2"
            if y == H - 2:
                cor = "aco_1" if x > 2 else "aco_2"
            pinta(t, x, y, cor)
    # Quina de cima da frente: dobra da chapa acesa.
    for x in range(1, W - 1):
        pinta(t, x, 5, "aco_5" if x < W - 3 else "aco_3")
    # Painel afundado: sombra em cima e à esquerda, lábio aceso embaixo e à direita.
    x0, y0, x1, y1 = 4, 7, W - 5, H - 3
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cor = "negro_2"
            if y == y0 or x == x0:
                cor = "negro_1"
            elif y == y1 or x == x1:
                cor = "aco_5" if y == y1 else "aco_4"
            pinta(t, x, y, cor)
    # Rebites: cabeça acesa e sombra embaixo à direita.
    for (rx, ry) in ((2, 6), (W - 4, 6), (2, H - 4), (W - 4, H - 4)):
        pinta(t, rx, ry, "aco_6")
        pinta(t, rx + 1, ry + 1, "aco_1")
    # Letra: extrusão escura 1 px para baixo e à direita, depois o volume de cúpula.
    glifo = LETRAS[letra]
    lw, lh = len(glifo[0]), len(glifo)
    ox = x0 + 1 + (x1 - x0 - 1 - lw) // 2
    oy = y0 + 1 + (y1 - y0 - 1 - lh - 1) // 2
    m = np.zeros((H, W), bool)
    for y, linha in enumerate(glifo):
        for x, ch in enumerate(linha):
            if ch == "X":
                m[oy + y, ox + x] = True
    ext = np.roll(np.roll(m, 1, 0), 1, 1) & ~m
    t.px[ext] = IDX[rampa[0]]
    sombrear2d(t, m, rampa[1:], deslocar=0.6, linha=False)
    # Brilho de molhado na quina de cima-esquerda da letra.
    ys, xs = np.where(m)
    topo = ys.min()
    xb = xs[ys == topo].min()
    pinta(t, xb + 1, topo, rampa[-1])
    pinta(t, xb, topo + 1, rampa[-1])
    # Desgaste: riscos claros, amassado e ferrugem escorrendo de um rebite.
    for _ in range(3):
        x = int(rng.integers(2, W - 4))
        y = int(rng.integers(6, H - 3))
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            pinta(t, x, y, "aco_6")
    rx = W - 4
    for y in range(H - 3, H - 1):
        pinta(t, rx + int(rng.integers(0, 2)), y, "fuba_3")
    pinta(t, 2, H - 3, "fuba_4")
    return contornar(t)


# ------------------------------------------------------------ comidas


def _render(c, w, h):
    t = c.render(linhas=True)
    return t


def caja():
    """Dois cajás maduros, amarelo-laranja e brilhantes, com cabinho e folha."""
    c = Cena(14, 14)
    fruta = ["rubro_2", "fuba_3", "fuba_4", "fuba_5", "latao_5", "latao_6"]
    c.elipsoide((9.2, 9.0, 0), (3.6, 4.0, 3.6), fruta, brilho=0.08)
    c.elipsoide((5.0, 8.4, 2), (3.7, 4.2, 3.7), fruta, brilho=0.08)
    c.caminho([(6, 4.6, 4), (8.5, 3.2, 4), (11.5, 2.4, 4)], [1.3, 1.6, 0.8], VERDE[1:6])
    t = _render(c, 14, 14)
    pinta(t, 6, 4, "mad_n3")
    pinta(t, 6, 3, "mad_n4")
    # Manchinhas da casca.
    for (x, y) in ((4, 10), (10, 11), (6, 7)):
        if t.px[y, x] != VAZIO:
            pinta(t, x, y, "fuba_3")
    return contornar(t)


def rapadura():
    """Rapadura embrulhada na palha seca, amarrada em cruz com barbante."""
    W, H = 18, 12
    t = Tela(W, H)
    palha = t.retangulo(1, 2, 16, 9) | t.elipse(2, 6.5, 1.5, 4.2) | t.elipse(16, 6.5, 1.5, 4.2)
    sombrear2d(t, palha, OSSO, linha=False)
    # Fibras da palha (veios na horizontal).
    rng = np.random.default_rng(3)
    for y in (3, 5, 8, 10):
        for x in range(2, 16):
            if rng.random() < 0.45 and palha[y, x]:
                pinta(t, x, y, "osso_2" if y > 6 else "osso_3")
    # Rapadura aparecendo pela abertura: bloco marrom com quina acesa.
    bloco = t.retangulo(5, 3, 8, 6)
    sombrear2d(t, bloco, FUBA[0:5], deslocar=0.2)
    pinta(t, 6, 4, "fuba_6")
    pinta(t, 7, 4, "fuba_5")
    # Barbante em cruz.
    for y in range(1, 11):
        pinta(t, 9, y, "pelo_6" if y < 6 else "pelo_5")
    for x in range(1, 17):
        pinta(t, x, 6, "pelo_6" if x < 9 else "pelo_5")
    pinta(t, 9, 6, "pelo_7")
    pinta(t, 10, 7, "pelo_4")
    return contornar(t)


def queijo():
    """Queijo coalho no espeto, dourado na brasa, com a marca da grelha."""
    W, H = 10, 20
    t = Tela(W, H)
    espeto = t.capsula(5, 19, 5, 11, 0.7)
    sombrear2d(t, espeto, ["mad_n3", "mad_n5", "mad_n6"], linha=False)
    bloco = t.retangulo(1, 1, 8, 12) & ~(t.elipse(1, 1, 1.2, 1.2) | t.elipse(9, 1, 1.2, 1.2))
    sombrear2d(t, bloco, OSSO + ["pelo_7"], deslocar=0.4)
    # Marcas da grelha (tostado em diagonal) e pontas douradas.
    for y0 in (3, 7):
        for x in range(1, 9):
            y = y0 + (x - 1) // 3
            if bloco[y, x]:
                pinta(t, x, y, "fuba_3")
                if bloco[y + 1, x]:
                    pinta(t, x, y + 1, "latao_4")
    for x in range(2, 8):
        pinta(t, x, 12, "latao_3")
    pinta(t, 2, 2, "pelo_7")
    return contornar(t)


def cuscuz():
    """Cuscuz de milho no prato de barro, com manteiga derretendo por cima."""
    c = Cena(18, 15)
    c.elipsoide((9, 12.2, -4), (8.6, 2.6, 2.0), BARRO, achata=0.5)
    c.elipsoide((9, 10.0, 0), (6.4, 6.2, 5.0), LATAO[1:] + ["amarelo_claro"], brilho=0.0)
    c.elipsoide((9, 5.5, 3), (3.4, 2.4, 3.0), LATAO[1:] + ["amarelo_claro"], brilho=0.0)
    t = c.render()
    t.px[13:, :][t.px[13:, :] != VAZIO] = IDX["fuba_2"]  # barriga do prato na sombra
    t.px[11, :][t.px[11, :] == IDX["latao_2"]] = IDX["fuba_5"]  # aba do prato acesa
    # Grão: pontinhos de tom vizinho espalhados.
    rng = np.random.default_rng(5)
    for _ in range(14):
        x, y = int(rng.integers(4, 15)), int(rng.integers(4, 11))
        if t.px[y, x] == IDX["latao_4"]:
            pinta(t, x, y, "latao_5")
        elif t.px[y, x] == IDX["latao_5"]:
            pinta(t, x, y, "latao_4")
    # Manteiga: placa clara no topo e escorrido.
    for (x, y, cor) in ((8, 4, "pelo_7"), (9, 4, "amarelo_claro"), (10, 4, "amarelo_claro"),
                        (8, 5, "amarelo_claro"), (9, 5, "latao_6"), (10, 5, "latao_6"), (11, 6, "latao_6"),
                        (11, 7, "latao_6"), (11, 8, "amarelo_claro"), (7, 4, "latao_6")):
        pinta(t, x, y, cor)
    return contornar(t)


def buchada():
    """Buchada de bode fumegando na panela de barro, com alças e caldo."""
    W, H = 20, 18
    c = Cena(W, H)
    c.elipsoide((10, 12.5, 0), (8.6, 5.2, 6.0), BARRO, brilho=0.0)
    c.elipsoide((1.8, 10.5, 3), (1.6, 1.3, 1.2), BARRO)
    c.elipsoide((18.2, 10.5, 3), (1.6, 1.3, 1.2), BARRO)
    t = c.render()
    # Boca da panela: aro aceso e caldo escuro dentro.
    boca = t.elipse(10, 8.6, 7.6, 2.1)
    t.px[boca] = IDX["fuba_2"]
    borda = t.elipse(10, 8.6, 8.4, 2.6) & ~boca
    t.px[borda & (t.yy < 8.6)] = IDX["fuba_5"]
    t.px[borda & (t.yy >= 8.6)] = IDX["fuba_4"]
    # Bucho saindo do caldo, com volume.
    bucho = t.elipse(10, 7.4, 4.4, 2.6) & (t.yy < 9.2)
    sombrear2d(t, bucho, CARNE[1:6], deslocar=0.3)
    pinta(t, 8, 6, "carne_7")
    pinta(t, 12, 7, "carne_2")
    # Coentro picado.
    for (x, y) in ((6, 9), (14, 8), (11, 6)):
        pinta(t, x, y, "verde_5")
    t = contornar(t)
    # Fumaça subindo (fora do contorno, clara e leve).
    for k, x in enumerate((7, 11, 14)):
        for y in range(1, 5):
            pinta(t, x + (y + k) % 2, y - k % 2, "pelo_6" if y < 3 else "pelo_5")
    return t


def galinha():
    """Galinha assada dourada no prato de barro, coxas para cima com ossinho."""
    W, H = 20, 15
    c = Cena(W, H)
    dourado = ["fuba_2", "fuba_3", "fuba_4", "fuba_5", "latao_5", "latao_6"]
    c.elipsoide((10, 12.6, -4), (9.2, 2.2, 2.0), BARRO, achata=0.5)
    c.elipsoide((10, 9.0, 0), (6.2, 3.8, 4.4), dourado, brilho=0.1)
    for lado in (1, -1):
        x0 = 10 - lado * 3.8
        c.caminho([(x0, 9.4, 4), (x0 - lado * 2.4, 6.4, 6)], [2.3, 1.4], dourado)
        c.capsula((x0 - lado * 2.4, 6.4, 7), (x0 - lado * 3.4, 4.0, 7), 1.0, 0.9, OSSO)
        c.elipsoide((x0 - lado * 3.7, 2.8, 8), (1.6, 1.4, 1.2), OSSO)
    t = c.render()
    # Pele tostada: manchas.
    for (x, y) in ((8, 11), (12, 10), (13, 8)):
        if t.px[y, x] != VAZIO:
            pinta(t, x, y, "fuba_3")
    return contornar(t)


COMIDAS_MS = {
    "caja": caja,
    "rapadura": rapadura,
    "queijo": queijo,
    "cuscuz": cuscuz,
    "buchada": buchada,
    "galinha": galinha,
}

# ------------------------------------------------------------ caixote e barril


def caixote():
    """Caixote de tábuas em 2.5D (22/10): frente de tábuas com veio e nó, travessa em X,
    tampa de tábuas vista de cima fugindo para trás, lateral na sombra, cantoneiras de ferro
    com rebite e marca de estêncil. Frente 28x32 (o sólido), tampa de 5 px por cima."""
    FW, FH, D, S = 28, 32, 5, 6
    W, H = FW + S, FH + D
    t = Tela(W, H)
    rng = np.random.default_rng(8)
    y0 = D                                    # topo da frente
    # Frente: tábuas horizontais de 5 px, luz em cima de cada uma, fresta escura.
    for y in range(y0, H):
        k = (y - y0) % 5
        for x in range(FW):
            v = [5, 4, 4, 3, 1][k]
            if x > FW - 5 and v > 1:
                v -= 1
            cor = FUBA[v]
            if k in (1, 2, 3) and rng.random() < 0.16:
                cor = FUBA[max(1, v - 1)]  # veio
            pinta(t, x, y, cor)
    for (x, y) in ((7, y0 + 7), (19, y0 + 13), (12, y0 + 22)):
        pinta(t, x, y, "fuba_1"); pinta(t, x + 1, y, "fuba_2")
    # Travessa em X, com volume.
    for (a, b) in (((4, y0 + 4), (FW - 5, H - 5)), ((4, H - 5), (FW - 5, y0 + 4))):
        m = t.capsula(a[0], a[1], b[0], b[1], 1.5)
        sombrear2d(t, m, FUBA[1:6], deslocar=0.2)
    # Tampa: tábuas fugindo para trás (paralelogramo), acesa de cima.
    for y in range(D):
        off = D - y                                       # sobe e anda para a direita
        for x in range(FW):
            xx = x + int(round(off * S / D))
            v = 6 if (x // 7) % 2 == 0 else 5
            if x % 7 == 6:
                v = 3                                     # fresta entre tábuas
            if y == D - 1:
                v = 6                                     # quina da frente acesa
            pinta(t, xx, y, FUBA[v])
    # Lateral: tábuas na sombra fugindo para trás.
    for x in range(FW, W):
        k = x - FW
        topo = D - int(round(k * D / S)) if k else D
        for y in range(topo, H - int(round(k * D / S))):
            v = [2, 2, 1, 2, 1][(y - topo) % 5]
            pinta(t, x, y, FUBA[v])
    # Cantoneiras de ferro na frente e na quina da lateral.
    for x in (0, FW - 3):
        for y in range(y0, H):
            for dx in range(3):
                cor = ACO[[4, 3, 2][dx]] if x == 0 else ACO[[3, 2, 1][dx]]
                pinta(t, x + dx, y, cor)
        for y in (y0 + 2, y0 + FH // 2, H - 3):
            pinta(t, x + 1, y, "aco_6")
            pinta(t, x + 2, y + 1, "aco_1")
    for x in range(FW - 1, W):                         # cantoneira da tampa
        pinta(t, x, D - 1 - int(round((x - FW + 1) * D / S)), ACO[4])
    # Estêncil apagado e ferrugem escorrendo.
    for (x, y) in ((11, y0 + 9), (12, y0 + 9), (14, y0 + 9), (15, y0 + 9), (13, y0 + 10)):
        pinta(t, x, y, "fuba_2")
    for (x, y) in ((2, y0 + 7), (2, y0 + 8), (FW - 2, y0 + 15), (FW - 2, y0 + 16)):
        pinta(t, x, y, "fuba_3")
    return contornar(t)


def barril(quadro=0):
    """Tambor de querosene: cilindro vermelho com luz da esquerda, aros salientes,
    losango de perigo, tinta descascada e ferrugem. Quadro 1: furado, esguichando."""
    W, H = 18, 24
    t = Tela(W, H)
    VERM = ["rubro_1", "rubro_2", "rubro_3", "rubro_4", "rubro_5", "rubro_6"]
    corpo = t.retangulo(1, 3, 16, 18) | t.elipse(8.5, 20.5, 8, 1.6)
    # Cilindro: luz por coluna (forte à esquerda do meio, sombra à direita).
    nx = (t.xx - 9) / 8
    luz = np.clip(-nx * 0.55 + np.sqrt(np.clip(1 - nx * nx, 0, 1)) * 0.62, 0, 1)
    nivel = np.clip((luz ** 1.2 * 5.0).astype(int), 0, 4)
    cores = np.array([IDX[c] for c in VERM])[nivel]
    t.px[corpo] = cores[corpo]
    t.px[corpo & (np.abs(t.xx - 5.5) < 0.5)] = IDX["rubro_5"]  # brilho da tinta
    t.px[corpo & (t.xx > 16)] = IDX["rubro_1"]
    t.px[corpo & (np.abs(t.xx - 15.5) < 0.5)] = IDX["rubro_3"]  # luz refletida
    # Tampa: elipse de cima com borda acesa e bujão.
    tampa = t.elipse(8.6, 3, 7.4, 1.6)
    t.px[tampa] = IDX["rubro_3"]
    t.px[tampa & (t.yy < 2.6)] = IDX["rubro_5"]
    pinta(t, 5, 3, "aco_4")
    pinta(t, 6, 3, "aco_5")
    pinta(t, 12, 3, "negro_2")
    # Aros de rolagem: faixa clara em cima, escura embaixo.
    for y in (8, 16):
        for x in range(W):
            if corpo[y, x]:
                pinta(t, x, y, "rubro_5" if x < 12 else "rubro_3")
                pinta(t, x, y + 1, "rubro_2")
    # Losango de perigo amarelo com chama.
    cx, cy = 7, 12
    for dy in range(-3, 4):
        for dx in range(-(3 - abs(dy)), 4 - abs(dy)):
            pinta(t, cx + dx, cy + dy, "latao_5" if dx + dy < 1 else "latao_4")
    for (x, y) in ((7, 11), (7, 12), (6, 12), (8, 13), (7, 13)):
        pinta(t, x, y, "rubro_3")
    # Tinta descascada mostrando o metal, ferrugem escorrendo.
    for (x, y, cor) in ((12, 5, "aco_4"), (13, 5, "aco_3"), (13, 6, "aco_3"), (3, 18, "aco_4"),
                        (14, 11, "fuba_3"), (14, 12, "fuba_3"), (14, 13, "fuba_2"), (4, 20, "fuba_3"), (10, 20, "fuba_2")):
        pinta(t, x, y, cor)
    # Terra na base.
    for x in range(W):
        if corpo[21, x]:
            pinta(t, x, 21, "fuba_2" if x % 3 else "fuba_3")
    if quadro == 1:
        # Amassado e furo com querosene esguichando e faísca.
        for (x, y) in ((11, 12), (12, 12), (11, 13)):
            pinta(t, x, y, "rubro_1")
        pinta(t, 12, 13, "negro_1")
    t = contornar(t)
    if quadro == 1:
        for k, (x, y) in enumerate(((13, 12), (14, 11), (15, 11), (16, 12), (17, 13))):
            pinta(t, x, y, "pelo_6" if k % 2 else "latao_6")
        pinta(t, 12, 11, "amarelo_claro")
        pinta(t, 13, 10, "latao_6")
    return t
