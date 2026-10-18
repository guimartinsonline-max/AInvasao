"""Peças dos trechos novos da fase 1: vila de taipa (capela, cruzeiro),
leito de rio seco (chão rachado, ponte de madeira, canoa velha, carnaúba) e
acampamento da Volante (barraca, torre de vigia, mastro, caixas de munição).
Mesmo estilo e rampas de fase1.py. Usado por fase1.py.
"""
import math

import numpy as np

from motor import IDX, VAZIO, Tela
import fase1 as f

LONA = ["terra_escura", "terra", "terra_media", "barro", "areia_media", "areia"]
LONA_VERDE = ["sombra", "caatinga_esc", "caatinga_media", "caatinga", "mandacaru"]
CAL = ["cinza_medio", "cinza", "cinza_luz", "cinza_claro", "branco"]
LAMA = ["sombra", "terra_escura", "terra", "terra_media", "barro", "areia_media"]


def capela(w=96, h=112, semente=0):
    """Capelinha caiada: frontão com cruz, sino na torrinha, porta em arco
    (de onde a Volante sai), reboco descascando e barra azul na base."""
    t = Tela(w, h)
    rng = np.random.default_rng(semente)
    base = h - 1
    corpo_y = 40
    frontao = t.poligono([(6, corpo_y + 2), (w / 2, 12), (w - 6, corpo_y + 2)])
    corpo = t.retangulo(8, corpo_y, w - 16, h - corpo_y)
    torre = t.retangulo(w / 2 - 9, 2, 18, 16)
    t.volume(corpo | frontao | torre, CAL, achatado=3, suave=1.0, ambiente=0.35, textura=0.15, semente=semente,
             luz=(-0.3, -0.9))
    # Cornija do frontão e beiral.
    for k in range(2):
        t.linha(6, corpo_y + 2 - k, w / 2, 12 - k, "cinza_medio" if k else "cinza_escuro")
        t.linha(w / 2, 12 - k, w - 6, corpo_y + 2 - k, "cinza_medio" if k else "cinza_escuro")
    t.chapado(t.retangulo(6, corpo_y + 2, w - 12, 2), "cinza_escuro")
    # Torrinha do sino com o vão escuro e o sino.
    t.chapado(t.retangulo(w / 2 - 5, 5, 10, 9) | t.elipse(w / 2, 5, 5, 3), "sombra")
    t.volume(t.elipse(w / 2, 10, 3.2, 3.5) & (t.yy < 12.5), ["couro_profundo", "ouro_escuro", "amarelo_fogo", "amarelo_claro"],
             achatado=1, suave=0.3)
    t.linha(w / 2, 0, w / 2, 3, "couro_escuro")
    t.linha(w / 2 - 2, 1, w / 2 + 2, 1, "couro_escuro")
    # Cruz no alto do frontão.
    cx = w / 2
    t.volume(t.retangulo(cx - 1, 18, 2, 12) | t.retangulo(cx - 4, 21, 8, 2), f.MADEIRA, achatado=1, suave=0.3)
    # Óculo redondo.
    t.chapado(t.elipse(cx, 34, 4, 4), "sombra")
    t.chapado(t.elipse(cx, 34, 2.5, 2.5), "azul_medio")
    # Porta em arco, aberta (escura) com as folhas de madeira.
    pw, ph = 22, 38
    porta = t.retangulo(cx - pw / 2, base - ph + pw / 2, pw, ph - pw / 2) | t.elipse(cx, base - ph + pw / 2, pw / 2, pw / 2)
    t.chapado(porta, "marrom_noite")
    for lado in (-1, 1):
        folha = f.tabuas(5, ph - 8, vertical=True, semente=semente + lado + 5, rampa=f.MADEIRA)
        f.colar(t, folha, cx + lado * (pw / 2 + 1) - (5 if lado < 0 else 0), base - ph + 8)
    t.chapado(t.retangulo(cx - pw / 2 - 2, base - 1, pw + 4, 2), "cinza")  # degrau
    # Janelinhas laterais.
    for jx in (16, w - 24):
        t.chapado(t.retangulo(jx, corpo_y + 20, 8, 12) | t.elipse(jx + 4, corpo_y + 20, 4, 3), "sombra")
        t.chapado(t.retangulo(jx + 1, corpo_y + 21, 6, 10), "azul_sombra")
    # Barra azul na base, reboco caído e manchas de umidade.
    barra = (corpo) & (t.yy > base - 10)
    t.px[barra] = IDX["azul_medio"]
    t.px[barra & (t.yy > base - 3)] = IDX["azul_sombra"]
    caido = (f.ruido(h, w, 2.5, semente + 2) > 1.1) & corpo & (t.yy > corpo_y + 8) & (t.yy < base - 10) & ~porta
    t.px[caido] = IDX["barro"]
    t.px[caido & (f.ruido(h, w, 0.8, semente + 3) > 0.6)] = IDX["terra_media"]
    for _ in range(3):
        x, y = rng.uniform(14, w - 14), rng.uniform(corpo_y + 6, base - 14)
        for k in range(9):
            x += rng.uniform(-1, 1)
            y += 1
            if corpo[int(y), int(x)]:
                t.px[int(y), int(x)] = IDX["cinza_escuro"]
    t.contorno("sombra")
    return t


def cruzeiro(h=64):
    """Cruzeiro de madeira na praça, sobre base de pedra caiada, com fitas de promessa."""
    t = Tela(30, h)
    base = h - 1
    t.volume(t.retangulo(5, base - 10, 20, 11), CAL, achatado=2, suave=0.6, ambiente=0.3)
    t.volume(t.retangulo(8, base - 14, 14, 5), CAL, achatado=1.5, suave=0.5, ambiente=0.3)
    t.volume(t.retangulo(13, 2, 4, base - 15), f.MADEIRA, achatado=1.5, suave=0.4, ambiente=0.25)
    t.volume(t.retangulo(4, 14, 22, 4), f.MADEIRA, achatado=1.5, suave=0.4, ambiente=0.25)
    for k, (x, cor) in enumerate(((7, "vermelho"), (22, "amarelo_fogo"), (10, "ceu_medio"))):
        t.linha(x, 18, x + (k - 1), 26 + k * 2, cor)
    t.contorno("sombra")
    return t


def chao_rachado(w, h=26, semente=0):
    """Leito de rio seco: lama endurecida em placas rachadas, mais escura que a terra."""
    t = f.chao(w, h, semente=semente)
    rng = np.random.default_rng(semente)
    topo = t.yy < 6
    n = f.ruido(h, w, 1.2, semente + 9)
    t.px[topo] = np.array([IDX[c] for c in LAMA])[np.clip((3 + n * 1.2).astype(int), 1, 5)][topo]
    t.px[(t.yy < 1)] = IDX["barro"]
    # Placas de lama: rede de rachaduras poligonais no topo.
    for _ in range(w // 9):
        x = rng.uniform(0, w)
        y = 0
        for k in range(rng.integers(3, 7)):
            nx, ny = x + rng.uniform(-2.5, 2.5), y + 1
            t.linha(x, y, nx, ny, "sombra")
            x, y = nx, ny
    # Lascas levantadas (borda clara).
    for _ in range(w // 14):
        x = int(rng.uniform(1, w - 4))
        t.linha(x, 0, x + 3, 0, "areia_luz")
    return t


def ponte(w=200, alt=48, semente=0):
    """Ponte de tábuas sobre o leito: tabuleiro com corrimão de varas e pilares
    de madeira fincados no leito."""
    t = Tela(w, alt)
    tab = f.tabuas(w, 6, vertical=False, semente=semente, rampa=f.MADEIRA)
    # Tábuas atravessadas (vistas de lado): faixa com juntas verticais.
    for x in range(0, w, 5):
        tab.px[:, x] = IDX["marrom_noite"]
    f.colar(t, tab, 0, 0)
    t.chapado(t.retangulo(0, 6, w, 2), "marrom_noite")
    # Pilares e mãos-francesas.
    for x in range(10, w - 6, 46):
        m = t.retangulo(x, 7, 5, alt - 7)
        t.volume(m, f.MADEIRA, achatado=1.5, suave=0.4, ambiente=0.25, textura=0.15, semente=x)
        t.linha(x - 10, 8, x, 20, "couro_escuro")
        t.linha(x + 15, 8, x + 5, 20, "couro_escuro")
        t.chapado(t.retangulo(x - 1, 18, 7, 2), "couro_profundo")
    t.contorno("sombra")
    return t


def corrimao(w=200, h=12):
    """Corrimão de varas em cima da ponte (desenhado atrás dos personagens)."""
    t = Tela(w, h)
    for x in range(2, w, 23):
        t.volume(t.capsula(x, h - 1, x, 1, 1.0), f.GALHO_SECO, achatado=1, suave=0.3)
    for y in (2, 7):
        for xx in range(w):
            if t.px[y, xx] == VAZIO:
                t.px[y, xx] = IDX["cinza_medio"] if y == 2 else IDX["cinza_escuro"]
    t.contorno("sombra")
    return t


def canoa():
    """Canoa velha encalhada no leito, rachada, com a proa enterrada."""
    t = Tela(64, 16)
    casco = t.poligono([(2, 4), (62, 2), (56, 13), (8, 14)])
    t.volume(casco, f.MADEIRA, achatado=3, suave=0.8, ambiente=0.2, textura=0.2, semente=4)
    t.chapado(t.poligono([(6, 4), (58, 3), (55, 6), (8, 7)]), "marrom_noite")
    for x in (20, 36):
        t.volume(t.retangulo(x, 4, 3, 7), f.MADEIRA, achatado=1, suave=0.3)
    t.linha(30, 8, 33, 13, "sombra")
    t.contorno("sombra")
    return t


def carnauba(altura=80, semente=0):
    """Carnaúba da beira do rio: tronco fino com anéis e leque de folhas."""
    t = Tela(48, altura)
    rng = np.random.default_rng(semente)
    cx = 24 + rng.uniform(-2, 2)
    tronco = t.capsula(24, altura - 1, cx, 16, 2.6, 2.0)
    t.volume(tronco, f.CASCA, achatado=1.5, suave=0.4, ambiente=0.25)
    for y in range(20, altura - 2, 4):
        t.linha(cx - 2, y, cx + 2, y + 1, "couro_profundo")
    for k in range(13):
        a = math.pi + k / 12 * math.pi + rng.uniform(-0.08, 0.08)
        comp = rng.uniform(14, 21)
        x1, y1 = cx + math.cos(a) * comp, 16 + math.sin(a) * comp * 0.75 + (6 if abs(math.cos(a)) > 0.8 else 0)
        m = t.capsula(cx, 16, x1, y1, 1.0, 2.4)
        t.volume(m, f.FOLHA, achatado=1, suave=0.4, ambiente=0.3)
    t.volume(t.elipse(cx, 16, 4, 3), f.FOLHA, achatado=1, suave=0.3)
    t.contorno("sombra")
    return t


def barraca(w=84, h=44, semente=0, aberta=True):
    """Barraca de lona da Volante: duas águas, cordas e estacas, porta aberta."""
    t = Tela(w, h)
    base = h - 1
    corpo = t.poligono([(2, base), (w * 0.3, 4), (w * 0.7, 4), (w - 2, base)])
    t.volume(corpo, LONA_VERDE, achatado=4, suave=1.0, ambiente=0.25, textura=0.15, semente=semente,
             luz=(-0.5, -0.8))
    t.linha(w * 0.3, 4, w * 0.7, 4, "caatinga_esc")
    for x in (w * 0.4, w * 0.6):
        t.linha(x, 5, x - (w * 0.5 - x) * 0.6, base, "caatinga_esc")
    if aberta:
        porta = t.poligono([(w * 0.5, 10), (w * 0.38, base), (w * 0.62, base)])
        t.chapado(porta, "marrom_noite")
        t.chapado(t.poligono([(w * 0.5, 10), (w * 0.38, base), (w * 0.33, base), (w * 0.47, 12)]), "caatinga_media")
    # Cordas e estacas.
    for lado in (-1, 1):
        x0 = w / 2 + lado * w * 0.2
        t.linha(x0, 6, w / 2 + lado * (w / 2 - 1), base - 6, "areia_media")
    t.contorno("sombra")
    # Remendos.
    for (x, y) in ((w * 0.24, h * 0.6), (w * 0.7, h * 0.4)):
        t.chapado(t.retangulo(x, y, 6, 4), "terra_media")
        t.pontos([(x, y), (x + 5, y), (x, y + 3), (x + 5, y + 3)], "areia")
    return t


def torre_vigia(altura=90, larg=40):
    """Torre de vigia de troncos com plataforma de tábuas, guarda-corpo e
    escada; a plataforma é onde o soldado fica."""
    t = Tela(larg + 12, altura)
    base = altura - 1
    for x in (6, larg + 2):
        t.volume(t.capsula(x, base, x + (3 if x < 10 else -3), 20, 2.2), f.MADEIRA, achatado=1.5, suave=0.4,
                 ambiente=0.25, textura=0.15, semente=x)
    for y in range(36, base - 6, 18):
        t.linha(8, y, larg, y + 14, "couro_escuro")
        t.linha(larg, y, 8, y + 14, "couro_escuro")
    # Plataforma (tábuas) em y=20 e guarda-corpo de varas.
    tab = f.tabuas(larg + 12, 5, vertical=False, semente=3, rampa=f.MADEIRA)
    for x in range(0, larg + 12, 5):
        tab.px[:, x] = IDX["marrom_noite"]
    f.colar(t, tab, 0, 20)
    for x in (2, larg / 2 + 4, larg + 8):
        t.volume(t.capsula(x, 20, x, 4, 1.0), f.MADEIRA, achatado=1, suave=0.3)
    t.chapado(t.retangulo(1, 6, larg + 10, 2), "couro")
    # Escada.
    for y in range(28, base, 6):
        t.linha(larg + 6, y, larg + 11, y, "couro_medio")
    t.linha(larg + 6, 25, larg + 6, base, "couro_escuro")
    t.linha(larg + 11, 25, larg + 11, base, "couro_escuro")
    t.contorno("sombra")
    return t


def mastro(altura=110):
    """Mastro com flâmula verde e amarela da Volante tremulando."""
    t = Tela(36, altura)
    base = altura - 1
    t.volume(t.capsula(4, base, 4, 2, 1.4), f.METAL, achatado=1, suave=0.3)
    t.chapado(t.elipse(4, 2, 2, 2), "amarelo_fogo")
    fl = t.poligono([(5, 5), (34, 9), (32, 13), (34, 18), (5, 21)])
    t.volume(fl, ["sombra", "caatinga_esc", "caatinga", "mandacaru"], achatado=2, suave=0.6, ambiente=0.3)
    t.chapado(t.poligono([(8, 13), (18, 8), (28, 13), (18, 18)]) & fl, "amarelo_fogo")
    t.volume(t.retangulo(0, base - 5, 9, 6), CAL, achatado=1, suave=0.3)
    t.contorno("sombra")
    return t


def caixas_municao(n=3, semente=0):
    """Pilha de caixas de munição verdes com alça e letras pintadas."""
    t = Tela(n * 15 + 2, 22)
    for k in range(n):
        x, y = 1 + k * 15, 9
        m = t.retangulo(x, y, 14, 12)
        t.volume(m, LONA_VERDE, achatado=1.5, suave=0.4, ambiente=0.3, textura=0.1, semente=k)
        t.chapado(t.retangulo(x + 4, y + 4, 6, 1), "amarelo_fogo")
        t.chapado(t.retangulo(x + 5, y - 1, 4, 1), "cinza_escuro")
    t.volume(t.retangulo(8, 0, 14, 9), LONA_VERDE, achatado=1.5, suave=0.4, ambiente=0.35)
    t.contorno("sombra")
    return t
