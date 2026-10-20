"""Peças dos trechos novos da fase 1: vila de taipa (capela, cruzeiro),
leito de rio seco (chão rachado, ponte de madeira, canoa velha, carnaúba) e
acampamento da Volante (barraca, torre de vigia, mastro, caixas de munição).
Mesmo estilo e rampas de fase1.py. Usado por fase1.py.
"""
import math

import numpy as np
from scipy import ndimage

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
    t.volume(corpo | frontao | torre, CAL, achatado=3, suave=1.0, ambiente=0.35, textura=0.06, semente=semente,
             luz=(-0.3, -0.9))
    # Caiação lisa: cada pixel fica com a cor que mais aparece em volta (tira o granulado).
    cal = corpo | frontao | torre
    moda = ndimage.generic_filter(t.px, lambda v: np.bincount(v.astype(int) + 1).argmax() - 1, size=3)
    t.px[cal] = moda[cal]
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
    f.envelhecer(t, corpo, corpo_y + 4, semente)
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
    t.linha(w * 0.3, 5, w * 0.7, 5, "mandacaru")  # cumeeira iluminada
    for x in (w * 0.4, w * 0.6):
        t.linha(x, 5, x - (w * 0.5 - x) * 0.6, base, "caatinga_esc")
    # Dobras da lona: caimentos verticais (vão escuro com borda clara) e barra suja embaixo.
    rng = np.random.default_rng(semente + 5)
    for k in range(9):
        x0 = w * (0.12 + k * 0.095) + rng.uniform(-2, 2)
        for y in range(6, base + 1):
            fx = x0 + (x0 - w / 2) * (y - 6) / max(1, base - 6) * 0.35
            xi = int(fx)
            if 0 < xi < w - 1 and corpo[y, xi] and rng.random() < 0.85:
                t.px[y, xi] = f.ESCURO[t.px[y, xi]]
                if corpo[y, xi - 1]:
                    t.px[y, xi - 1] = IDX["caatinga"] if y < base - 6 else t.px[y, xi - 1]
    f.envelhecer(t, corpo, 0, semente, escorridos=False)
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


def caixa_municao(t, x, y, w=16, h=12, semente=0, aberta=False):
    """Caixote de munição de madeira pintado de verde-oliva, visto um pouco de
    cima: face de cima clara com as tábuas da tampa, frente com tábuas e tinta
    gasta, cantoneiras de ferro com rebite, alça de corda e estêncil amarelo.
    aberta: sem tampa, mostrando os pentes de latão lá dentro."""
    topo = 3  # altura da face de cima
    rng = np.random.default_rng(semente)
    frente = t.retangulo(x, y + topo, w, h - topo)
    t.volume(frente, LONA_VERDE, achatado=1.4, suave=0.3, ambiente=0.28)
    for yy in range(int(y + topo) + 3, int(y + h) - 1, 3):
        t.linha(x + 1, yy, x + w - 2, yy, "caatinga_esc")
    for _ in range(3):  # tinta lascada mostrando a madeira
        px, py = x + rng.uniform(2, w - 3), y + topo + rng.uniform(2, h - topo - 2)
        t.ponto(px, py, "couro")
        t.ponto(px + 1, py, "couro_escuro")
    cima = t.retangulo(x, y, w, topo)
    if aberta:
        # Boca aberta: borda de madeira e os pentes de latão enfileirados.
        t.volume(cima, ["couro_profundo", "couro_escuro", "couro"], achatado=0.6, suave=0.2)
        t.chapado(t.retangulo(x + 1, y + 1, w - 2, topo - 1), "preto")
        for j in range(int(w - 3)):
            t.ponto(x + 1.5 + j, y + 1, "amarelo_claro" if j % 2 else "ouro_escuro")
            if j % 2:
                t.ponto(x + 1.5 + j, y, "amarelo_fogo")  # pontas das balas saindo
    else:
        t.volume(cima, LONA_VERDE, achatado=0.8, suave=0.2, ambiente=0.55, brilho=1.25)
        t.linha(x, y, x + w - 1, y, "mandacaru_luz")
        t.linha(x + w // 2, y, x + w // 2, y + topo - 1, "caatinga_media")  # junta da tampa
    t.linha(x, y + topo, x + w - 1, y + topo, "sombra")  # quina entre a tampa e a frente
    # Cantoneiras de ferro nos cantos da frente.
    for cx in (x, x + w - 2):
        for cy in (y + topo, y + h - 2):
            t.chapado(t.retangulo(cx, cy, 2, 2), "cinza_escuro")
            t.ponto(cx, cy, "cinza_luz")
    # Estêncil amarelo e alça de corda no lado.
    t.chapado(t.retangulo(x + 3, y + topo + (h - topo) / 2 - 1, w - 6, 1.6), "amarelo_fogo")
    for k in range(int((w - 6) // 3)):
        t.ponto(x + 4 + k * 3, y + topo + (h - topo) / 2 - 0.5, "ouro_escuro")
    t.linha(x + w - 1, y + topo + 2, x + w + 1, y + topo + 4, "areia")
    t.linha(x + w + 1, y + topo + 4, x + w - 1, y + topo + 6, "areia_media")


def caixas_municao(n=3, semente=0):
    """Pilha de caixotes de munição sobre um estrado: fileira de baixo inteira,
    a de cima centrada (a da ponta aberta, mostrando os pentes) e a tampa dela
    encostada de pé no lado da pilha."""
    cw, ch = 16, 12
    W = n * (cw + 1) + 12
    H = ch * 2 + 5
    t = Tela(W, H)
    base_y = H - 3 - ch
    t.volume(t.retangulo(1, H - 3, n * (cw + 1) + 2, 3), ["marrom_noite", "couro_profundo", "couro_escuro", "couro"],
             achatado=1, suave=0.2, ambiente=0.35)
    for x in range(3, n * (cw + 1), 5):
        t.ponto(x, H - 1, "preto")
    for k in range(n):
        caixa_municao(t, 2 + k * (cw + 1), base_y, cw, ch, semente + k)
    for k in range(n - 1):
        x = 2 + (cw + 1) / 2 + k * (cw + 1)
        caixa_municao(t, x, base_y - ch + 1, cw, ch, semente + 10 + k, aberta=(k == n - 2))
    # Tampa da caixa aberta largada no chão, ao lado do estrado.
    x0 = n * (cw + 1) + 3
    tampa = t.poligono([(x0, H - 1), (x0 + 6, H - 3.5), (x0 + 7, H - 2), (x0 + 1, H + 0.5)])
    t.volume(tampa, LONA_VERDE, achatado=0.8, suave=0.2, ambiente=0.45)
    t.contorno("sombra")
    return t


# ================================================================ cenário vivo
URUBU = ["preto", "sombra", "sombra_media", "cinza_escuro"]
PENA_BRANCA = ["cinza_medio", "cinza_luz", "cinza_claro", "branco"]
PENA_RUIVA = ["couro_escuro", "couro", "couro_claro", "barro"]


def urubu(quadro=0):
    """Urubu: 0 pousado encolhido, 1 asas para cima, 2 asas para baixo (voando)."""
    t = Tela(26, 18)
    if quadro == 0:
        corpo = t.elipse(13, 11, 6, 6)
        t.volume(corpo, URUBU, achatado=2, suave=0.6, ambiente=0.3, textura=0.2, semente=1)
        t.volume(t.elipse(17, 5, 2.4, 2.2), ["vermelho_esc", "vermelho_medio", "rosa_poeira"], achatado=1, suave=0.3)
        t.chapado(t.poligono([(19, 5), (22, 6), (19, 6.5)]), "cinza_claro")  # bico
        t.ponto(18, 4, "preto")
        t.linha(12, 17, 12, 17, "cinza_luz")
        t.linha(15, 17, 15, 17, "cinza_luz")
    else:
        corpo = t.elipse(13, 10, 6, 3)
        t.volume(corpo, URUBU, achatado=1.5, suave=0.5, ambiente=0.3)
        dy = -6 if quadro == 1 else 6
        for lado in (-1, 1):
            asa = t.poligono([(13, 9), (13 + lado * 12, 9 + dy), (13 + lado * 11, 11 + dy * 0.6), (13 + lado * 3, 11)])
            t.volume(asa, URUBU, achatado=1, suave=0.3, ambiente=0.35)
            t.ponto(13 + lado * 11, 9 + dy, "cinza_luz")
        t.volume(t.elipse(20, 9, 2.2, 2), ["vermelho_esc", "vermelho_medio", "rosa_poeira"], achatado=1, suave=0.3)
        t.ponto(23, 9, "cinza_claro")
    t.contorno("sombra")
    return t


def galinha(quadro=0):
    """Galinha caipira: 0 parada, 1 bicando o chão, 2 e 3 correndo de asa aberta,
    4 e 5 andando (pernas alternando e a cabeça indo e voltando no passo)."""
    t = Tela(16, 15)
    bica = quadro == 1
    anda = quadro in (4, 5)
    corre = quadro in (2, 3)
    corpo = t.elipse(7, 9, 5.5, 4)
    t.volume(corpo, PENA_RUIVA, achatado=2, suave=0.6, ambiente=0.3, textura=0.15, semente=quadro)
    t.volume(t.poligono([(2, 8), (0, 3), (3, 6)]), PENA_RUIVA, achatado=1, suave=0.3, deslocar=-0.2)  # rabo
    hx, hy = (12, 10) if bica else (12, 5) if quadro == 4 else (11, 4)
    t.volume(t.elipse(hx, hy, 2.6, 2.6), PENA_RUIVA, achatado=1, suave=0.3, ambiente=0.4)
    t.chapado(t.retangulo(hx - 1, hy - 4, 3, 2), "vermelho")  # crista
    t.ponto(hx + 1, hy + 2, "vermelho")  # barbela
    t.chapado(t.poligono([(hx + 2, hy - 0.5), (hx + 5, hy + 0.5), (hx + 2, hy + 1.5)]), "amarelo_fogo")
    t.ponto(hx + 1, hy - 1, "preto")
    if corre:
        asa = t.poligono([(6, 8), (2 if quadro == 2 else 4, 3 if quadro == 2 else 12), (10, 9)])
        t.volume(asa, PENA_RUIVA, achatado=1, suave=0.3, ambiente=0.45)
    if anda:
        # Uma perna no chão puxando para trás, a outra levantada dando o passo.
        a, b = (5, 8) if quadro == 4 else (8, 5)
        t.linha(6, 12, a, 14, "amarelo_fogo")
        t.linha(7, 12, b + 1, 13, "amarelo_fogo")
        t.ponto(b + 2, 13, "amarelo_fogo")
    else:
        pe = (4, 9) if quadro == 2 else (6, 8) if quadro == 3 else (6, 8)
        for x in pe:
            t.linha(x, 12, x - (1 if corre else 0), 14, "amarelo_fogo")
    t.contorno("sombra")
    return t


def galinha_assada():
    """Galinha assada no prato de barro (comida que vale bastante)."""
    t = Tela(18, 13)
    t.volume(t.elipse(9, 10.5, 8.5, 2.4), ["vermelho_esc", "terra_escura", "terra", "barro"], achatado=1.5, suave=0.4)
    corpo = t.elipse(9, 7, 6, 4)
    t.volume(corpo, ["couro_profundo", "couro", "laranja_escuro", "ouro_escuro", "amarelo_fogo"], achatado=2, suave=0.6,
             ambiente=0.3)
    for x in (3, 15):
        t.volume(t.capsula(x, 6, x + (2 if x < 9 else -2), 3, 1.4, 1.0), ["couro_escuro", "couro", "ouro_escuro"],
                 achatado=1, suave=0.3)
        t.ponto(x + (2 if x < 9 else -2), 2, "branco")  # ossinho
    t.ponto(7, 5, "amarelo_claro")
    t.contorno("sombra")
    return t


def varal(quadro=0):
    """Varal de roupa entre duas varas. Quadro 1: corda arrebentada, roupa voou."""
    t = Tela(70, 40)
    for x in (2, 66):
        t.volume(t.capsula(x, 39, x + (1 if x < 30 else -1), 4, 1.2), f.MADEIRA, achatado=1, suave=0.3)
    if quadro == 0:
        for xx in range(4, 66):
            y = 6 + int(math.sin((xx - 4) / 62 * math.pi) * 5)
            t.ponto(xx, y, "areia_media")
        for (x0, w, h, cores) in ((10, 11, 12, ["azul_sombra", "azul_medio", "ceu_escuro", "ceu_medio"]),
                                  (27, 14, 16, ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"]),
                                  (47, 10, 10, ["cinza_medio", "cinza_luz", "cinza_claro", "branco"])):
            y0 = 7 + int(math.sin((x0 + w / 2 - 4) / 62 * math.pi) * 5)
            t.volume(t.retangulo(x0, y0, w, h), cores, achatado=1.5, suave=0.4, ambiente=0.3)
            for xx in (x0 + 1, x0 + w - 2):
                t.ponto(xx, y0, "couro_luz")  # prendedor
    else:
        for xx in range(4, 20):
            t.ponto(xx, 6 + (xx - 4) // 2, "areia_media")
        for xx in range(50, 66):
            t.ponto(xx, 6 + (66 - xx) // 2, "areia_media")
    t.contorno("sombra")
    return t


def roupa(quadro=0):
    """Peça de roupa voando do varal (camisa, calça, pano)."""
    t = Tela(12, 12)
    if quadro == 0:
        m = t.retangulo(2, 2, 8, 9) | t.retangulo(0, 2, 12, 3)
        t.volume(m, ["azul_sombra", "azul_medio", "ceu_escuro", "ceu_medio"], achatado=1, suave=0.3)
    elif quadro == 1:
        m = t.retangulo(2, 1, 8, 4) | t.retangulo(2, 4, 3, 7) | t.retangulo(7, 4, 3, 7)
        t.volume(m, ["vermelho_esc", "vermelho_medio", "vermelho", "laranja_fogo"], achatado=1, suave=0.3)
    else:
        t.volume(t.poligono([(1, 2), (11, 1), (10, 10), (2, 9)]), ["cinza_medio", "cinza_luz", "cinza_claro", "branco"],
                 achatado=1, suave=0.3)
    t.contorno("sombra")
    return t


def destelhar(t, h):
    """Tira as telhas da casa (explosão): sobram os caibros e umas telhas na beirada."""
    beiral = max(9, int(h * 0.3))
    rng = np.random.default_rng(7)
    telha = {IDX[c] for c in f.TELHA} | {IDX["vermelho_esc"]}
    for y in range(0, beiral + 1):
        for x in range(t.w):
            if t.px[y, x] in telha and not (y > beiral - 3 and rng.random() < 0.6):
                t.px[y, x] = VAZIO
    for x in range(int(t.w * 0.12), int(t.w * 0.9), 7):
        t.linha(x, 3, x - 3, beiral, "couro_escuro")
        t.linha(x + 1, 3, x - 2, beiral, "couro")
    t.linha(int(t.w * 0.15), 3, int(t.w * 0.85), 2, "couro_escuro")  # cumeeira
    t.contorno("sombra")
    return t


def casa_vila(w, h, semente, quebrada, destelhada=False, porta_x=None):
    """Casa da vila no nível novo (caatinga_detalhe.casa_taipa); a explosão tira as telhas."""
    import caatinga_detalhe as ca
    c = ca.casa_taipa(w, h, semente=semente, quebrada=quebrada, alpendre=False, porta_x=porta_x)
    return ca.destelhar(c, h) if destelhada else c


def ponte_segmento(w, alt=48, quebrada=False, semente=0):
    """Pedaço da ponte de tábuas com corrimão (a granada quebra pedaço por pedaço).
    O tabuleiro fica em y=12 dentro do desenho."""
    t = Tela(w, alt + 12)
    if not quebrada:
        f.colar(t, corrimao(w), 0, 0)
        f.colar(t, ponte(w, alt, semente=semente), 0, 12)
        return t
    # Quebrada: só os pilares e tábuas penduradas.
    inteira = ponte(w, alt, semente=semente)
    for y in range(inteira.h):
        for x in range(inteira.w):
            if y < 10 and not (x < 6 or x > w - 6):
                inteira.px[y, x] = VAZIO
    f.colar(t, inteira, 0, 12)
    rng = np.random.default_rng(semente)
    for x in (4, w - 8):
        for k in range(3):
            t.volume(t.capsula(x + k * 2, 14, x + k * 2 + rng.uniform(-2, 2), 22 + k * 3, 1.0),
                     f.MADEIRA, achatado=1, suave=0.3)
    return t
