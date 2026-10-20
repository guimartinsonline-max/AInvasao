"""Fase 2, trecho 2: o acampamento da base (0 a 1800 px), logo depois da cancela.

Anoitece enquanto o Lampião avança, sem repetir o fundo:
  A) 0-600     entrada da base: o chão de vidro da borda vira terra batida pisoteada,
               sacos de areia, barraca da tropa, a primeira torre de holofote e o gerador.
  B) 600-1250  coração do acampamento: barraca-laboratório com o cientista amarrado,
               jaulas com aliens capturados, barraca de quarentena (contaminados), varal
               de lâmpadas, a segunda torre e o segundo gerador.
  C) 1250-1800 beira da cratera: o guindaste de madeira içando um pedaço do casco do
               disco, o brilho verde subindo do buraco e o elevador de carga no fim.

Camadas: f2b_longe (0,25), f2b_meio (0,45), f2b_perto (0,75), f2b_jogo, f2b_frente (1,1),
céus ceu_tarde e ceu_noite (a noite entra aos poucos). Tudo que se mexe (bandeira, lâmpadas,
fogo, fumaça, holofotes, gerador, jaulas, guindaste) é sprite animado à parte.
Prévia: python3 tools/arte/fase2b.py saida.png
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from motor import IDX, VAZIO, Tela, RGB, N_BASE  # noqa: E402
import fase1 as f1  # noqa: E402
import fase1_extra as fx  # noqa: E402
import fase2 as f2  # noqa: E402
from fase2 import ruido, lim, colar_organico, pintar_niveis, madeira, fio, placa, escrever  # noqa: E402

LARGURA = 1800
CHAO = 194
FIM = 1700  # centro do elevador de carga

# Peças de jogo (o JS desenha e anima por cima; a arte só deixa o lugar pronto).
TORRES = [(470, 0), (1170, 1)]          # (x, gerador que alimenta)
GERADORES = [(560, 0), (1240, 1)]       # (x, id)
JAULAS = [(845, "olheiro"), (915, "cerebrao")]
GUINDASTE_X = 1330                      # pé do guindaste; a ponta da lança fica em +150
PONTA_LANCA = (GUINDASTE_X + 150, 40)   # (x, y de mundo) de onde desce o cabo
LAB_X = 640
QUARENTENA_X = 1040
TROPA_X = 270
ELEVADOR_X = FIM - 34


# ------------------------------------------------------------------ noite
def _mapa_noite(forca):
    """Para cada cor da paleta, a cor mais parecida com ela à noite (mais escura e fria)."""
    alvo = RGB.astype(float) * np.array([0.5, 0.52, 0.72]) + np.array([4, 6, 22])
    mix = RGB.astype(float) * (1 - forca) + alvo * forca
    d = ((mix[:, None, :] - RGB[None, :, :].astype(float)) ** 2).sum(-1)
    d[:N_BASE, N_BASE:] = 1e12  # cor antiga escurece para cor antiga
    return d.argmin(1)


_NOITE = {}


def anoitecer(t, forca):
    """Escurece a peça para a hora do trecho (0 tarde, 1 noite fechada)."""
    k = round(forca * 8) / 8
    if k <= 0:
        return t
    if k not in _NOITE:
        _NOITE[k] = _mapa_noite(k)
    m = t.px != VAZIO
    t.px[m] = _NOITE[k][t.px[m]]
    return t


def hora(wx):
    """Quanto já anoiteceu no ponto wx do trecho (de 0,35 na entrada a 1 no fim)."""
    return float(np.clip(0.35 + wx / 1300 * 0.65, 0, 1))


def luz_no_chao(t, cx, cy, rx, ry, cores=("areia_media", "areia"), semente=0):
    """Mancha de luz amarela no chão debaixo de uma lâmpada (borda em manchas, sem xadrez)."""
    m = t.elipse(cx, cy, rx, ry) & (t.px != VAZIO)
    d = np.hypot((t.xx - cx) / rx, (t.yy - cy) / ry)
    g = lim(t.h, t.w)
    t.px[m & (d < 0.95 - g * 0.25)] = IDX[cores[0]]
    t.px[m & (d < 0.55 - g * 0.2)] = IDX[cores[1]]


# ------------------------------------------------------------------ céus
def ceu(faixas, h=308, w=548, estrelas=0, semente=0):
    """Céu em faixas que se misturam em manchas orgânicas (nada de pontilhado)."""
    t = Tela(w, h)
    g = lim(h, w, 3.0)
    for k, (y, cor) in enumerate(faixas):
        fim = faixas[k + 1][0] if k + 1 < len(faixas) else h
        t.px[y:fim] = IDX[cor]
        if k + 1 < len(faixas):
            prox = faixas[k + 1][1]
            for yy in range(max(0, fim - 14), min(h, fim + 10)):
                f = (yy - (fim - 14)) / 24
                t.px[yy][g[yy] < f] = IDX[prox]
    rng = np.random.default_rng(semente)
    for _ in range(estrelas):
        x, y = int(rng.integers(0, w)), int(rng.integers(4, h * 0.45))
        t.ponto(x, y, "ceu_luz" if rng.random() < 0.7 else "branco")
    return t


def nuvens(t, faixas, semente=0):
    """Bancos de nuvem de fumaça com volume: corpo escuro, miolo, beirada de cima clara e a
    barriga acesa por baixo (luz do poente ou da cratera). faixas: (y, espessura, cores
    [sombra, corpo, luz de cima, barriga acesa, barriga forte])."""
    h, w = t.h, t.w
    for k, (yc, esp, cores) in enumerate(faixas):
        n = ruido(h, w, (esp * 0.45, 16), semente + k) * 0.7 + ruido(h, w, (3.5, 6), semente + 10 + k) * 0.3
        perfil = 1 - np.abs(t.yy - yc) / esp
        dens = n + perfil * 2.0 - 0.55
        m = dens > 0
        m = ndimage.binary_opening(m, iterations=2)
        m = ndimage.binary_closing(m, iterations=2)
        acima = np.roll(m, 3, 0)
        abaixo = np.roll(m, -3, 0)
        barriga = m & ~abaixo
        barriga2 = m & ~np.roll(m, -1, 0)
        topo = m & ~acima
        miolo = m & (dens > 0.45)
        t.px[m] = IDX[cores[0]]
        t.px[miolo] = IDX[cores[1]]
        t.px[topo] = IDX[cores[2]]
        t.px[barriga] = IDX[cores[3]]
        t.px[barriga2] = IDX[cores[4]]


def ceu_tarde():
    """Fim de tarde roxo: lilás em cima, laranja queimado no horizonte (sol atrás da fumaça),
    bancos de nuvem de fumaça com a barriga acesa de laranja."""
    t = ceu([(0, "roxo_escuro"), (70, "roxo"), (140, "lilas"), (200, "rosa_poeira"), (240, "laranja_escuro"),
             (262, "laranja_fogo")])
    nuvens(t, [(34, 24, ["sombra", "sombra_media", "roxo", "rosa_poeira", "lilas_claro"]),
               (112, 20, ["sombra_media", "roxo_escuro", "lilas", "rosa_poeira", "laranja_escuro"]),
               (184, 15, ["roxo_escuro", "roxo", "lilas_claro", "laranja_escuro", "laranja_fogo"])], semente=5)
    return t


def ceu_noite():
    """Noite fechada: azul quase preto, roxo perto do chão e o horizonte esverdeado pelo
    brilho do disco; nuvens de fumaça com a barriga verde e poucas estrelas nas brechas."""
    t = ceu([(0, "sombra"), (80, "sombra_media"), (150, "azul_sombra"), (215, "roxo_escuro"), (250, "alien_profundo")],
            estrelas=60, semente=3)
    nuvens(t, [(44, 24, ["preto", "preto", "sombra_media", "azul_sombra", "roxo_escuro"]),
               (128, 20, ["preto", "sombra", "azul_sombra", "roxo_escuro", "roxo"]),
               (200, 15, ["sombra", "sombra_media", "roxo", "alien_profundo", "alien_esc"])], semente=9)
    return t


# ------------------------------------------------------------------ peças do cenário
def lona(cores):
    return {"sombra": cores[0], "caatinga_esc": cores[1], "caatinga_media": cores[2], "caatinga": cores[3],
            "mandacaru": cores[4]}


def recolorir(t, mapa):
    for a, b in mapa.items():
        t.px[t.px == IDX[a]] = IDX[b]
    return t


def barraca_grande(w=110, h=58, semente=0, tipo="tropa"):
    """Barraca grande da base. tipo: tropa (lona verde), laboratorio (lona branca com cruz
    vermelha e placa), quarentena (lona encardida com fita listrada e placa)."""
    b = fx.barraca(w, h, semente=semente, aberta=True)
    if tipo == "laboratorio":
        recolorir(b, lona(["sombra", "cinza_medio", "cinza", "cinza_luz", "cinza_claro"]))
        cx, cy = w * 0.5, h * 0.3
        b.chapado(b.retangulo(cx - 1.5, cy - 4.5, 3, 9), "vermelho")
        b.chapado(b.retangulo(cx - 4.5, cy - 1.5, 9, 3), "vermelho")
        b.ponto(cx - 1, cy - 4, "vermelho_medio")
    elif tipo == "quarentena":
        recolorir(b, lona(["sombra", "terra_escura", "terra", "terra_media", "barro"]))
        # Fita listrada amarela e preta cruzando a porta, toda torta.
        for k in range(int(w * 0.8)):
            x = w * 0.1 + k
            y = h * 0.55 + math.sin(k / 7) * 1.5 + (k - w * 0.4) * 0.12
            cor = "amarelo_fogo" if (k // 3) % 2 else "preto"
            b.ponto(x, y, cor)
            b.ponto(x, y + 1, cor)
        # Manchas verdes de gosma escorrendo da porta.
        for (x, y) in ((w * 0.47, h * 0.75), (w * 0.55, h * 0.85)):
            b.chapado(b.elipse(x, y, 2.4, 1.6), "alien_esc")
            b.linha(x, y, x, y + 4, "alien_medio")
    # Placa pregada na lona.
    rotulo = {"laboratorio": "LAB", "quarentena": "QUARENTENA", "tropa": ""}[tipo]
    if rotulo:
        pw = len(rotulo) * 5 + 5
        p = Tela(pw, 10)
        p.volume(p.retangulo(0, 0, pw, 10), ["couro_profundo", "couro_escuro", "couro", "couro_medio"], achatado=1, suave=0.3)
        escrever(p, rotulo, 3, 2, "amarelo_fogo" if tipo == "quarentena" else "branco", grossa=True)
        p.contorno("sombra")
        b.colar(p, int(w * 0.5 - pw / 2), int(h * 0.42 if tipo == "quarentena" else h * 0.5))
    return b


def torre_holofote(altura=118, semente=0):
    """Torre de holofote de ferro e madeira: quatro pernas travadas em X, plataforma de
    tábuas com guarda-corpo, escada, cabo elétrico descendo e a caixa de luz no alto (o
    holofote em si é peça de jogo e gira por cima)."""
    larg = 34
    t = Tela(larg + 12, altura)
    base = altura - 1
    for (x0, x1) in ((4, 12), (larg + 6, larg - 2)):
        madeira(t, t.capsula(x0, base, x1, 16, 2.2, 1.8), True, semente + x0)
    for y in range(26, base - 8, 16):
        t.linha(10, y, larg - 2, y + 13, "cinza_escuro")
        t.linha(larg - 2, y, 10, y + 13, "cinza_escuro")
        t.linha(9, y, larg - 1, y, "couro_escuro")
    plat = f1.tabuas(larg + 12, 5, vertical=False, semente=semente + 2, rampa=f1.MADEIRA)
    t.colar(plat, 0, 14)
    for x in (2, larg / 2 + 5, larg + 9):
        madeira(t, t.capsula(x, 14, x, 3, 1.0), True, semente + int(x))
    t.chapado(t.retangulo(1, 4, larg + 10, 2), "couro")
    for y in range(22, base, 6):
        t.linha(larg + 7, y, larg + 11, y, "couro_medio")
    t.linha(larg + 7, 19, larg + 7, base, "couro_escuro")
    t.linha(larg + 11, 19, larg + 11, base, "couro_escuro")
    # Cabo elétrico preto descendo enrolado na perna.
    for y in range(18, base, 2):
        t.ponto(13 + math.sin(y / 4) * 1.2, y, "preto")
    t.contorno("sombra")
    return t


def guindaste(semente=0):
    """Guindaste de madeira enorme: torre treliçada de toras amarradas, lança comprida em
    diagonal com cabos de ferro esticados, roldana na ponta, cabine de tábuas com o
    sarilho e contrapeso de pedras num caixote. A ponta da lança fica em (+150, 40)."""
    W, H = 190, 160
    t = Tela(W, H)
    base = H - 1
    # Torre: dois montantes e travessas em X.
    for (x0, x1) in ((6, 22), (46, 30)):
        madeira(t, t.capsula(x0, base, x1, 30, 2.6, 2.0), True, semente + x0)
    for y in range(40, base - 6, 18):
        k = (y - 30) / (base - 30)
        xa, xb = 22 - 16 * k + 2, 30 + 16 * k - 2
        f1.tora(t, xa, y, xb, y + 16, 1.2, semente + y, pontas=False)
        f1.tora(t, xb, y, xa, y + 16, 1.2, semente + y + 1, pontas=False)
        f1.amarra(t, (xa + xb) / 2, y + 8, 1.8)
    # Lança (duas toras paralelas) da torre até a ponta.
    px, py = 150 + 26, 40 - (H - 160) + 0
    for d in (0, 4):
        f1.tora(t, 26, 34 + d, px, py + d, 2.0, semente + 7 + d)
    for k in range(1, 9):
        x = 26 + (px - 26) * k / 9
        y = 34 + (py - 34) * k / 9
        t.linha(x, y, x + 3, y + 4, "couro_escuro")
    # Cabos de ferro do topo da torre à ponta e ao contrapeso.
    fio(t, 26, 26, px - 2, py - 2, flecha=3, farpas=0, cor="cinza_escuro", luz="cinza")
    fio(t, 26, 26, 4, 70, flecha=2, farpas=0, cor="cinza_escuro", luz="cinza")
    # Roldana na ponta.
    t.cel(t.elipse(px, py + 2, 4, 4), f1.METAL, sombra=1)
    t.chapado(t.elipse(px, py + 2, 1.4, 1.4), "preto")
    # Cabine do sarilho com telhado de zinco e a manivela.
    cab = t.retangulo(30, base - 36, 30, 30)
    tab = f1.tabuas(30, 30, vertical=True, semente=semente + 4)
    t.colar(tab, 30, base - 36)
    t.chapado(t.poligono([(27, base - 36), (45, base - 44), (63, base - 36)]), "cinza_medio")
    t.linha(27, base - 36, 63, base - 36, "cinza_escuro")
    t.chapado(t.retangulo(38, base - 28, 12, 9), "marrom_noite")  # janela
    t.chapado(t.retangulo(39, base - 27, 10, 3), "laranja_escuro")  # luz de lampião dentro
    t.cel(t.elipse(56, base - 14, 5, 5), f1.METAL, sombra=1)  # tambor do cabo
    t.linha(56, base - 14, 62, base - 18, "cinza_escuro")
    # Contrapeso: caixote de pedras atrás.
    cx = Tela(24, 18)
    cx.colar(f1.tabuas(24, 18, vertical=False, semente=semente + 9), 0, 0)
    for k in range(5):
        cx.cel(cx.elipse(4 + k * 4, 2, 2.6, 2.2), f1.PEDRA, sombra=1)
    cx.contorno("sombra")
    t.colar(cx, 0, base - 17)
    t.contorno("sombra")
    return t


def elevador(semente=0):
    """Elevador de carga na beira da cratera (castelete de madeira): dois postes altos com
    travessa, roldana dupla e cabos, gaiola de grade de ferro aberta na frente, placa e
    lampião. A plataforma é peça de jogo (desce com o Lampião no fim)."""
    W, H = 92, 150
    t = Tela(W, H)
    base = H - 1
    for x0 in (10, W - 12):
        madeira(t, t.capsula(x0, base, x0, 8, 3.0, 2.6), True, semente + x0)
    f1.tora(t, 4, 12, W - 4, 12, 3.0, semente + 3)
    for x0 in (10, W - 12):
        f1.tora(t, x0, 40, W / 2, 16, 1.4, semente + x0 + 1, pontas=False)
    for xr in (W / 2 - 8, W / 2 + 8):
        t.cel(t.elipse(xr, 6, 5, 5), f1.METAL, sombra=1)
        t.chapado(t.elipse(xr, 6, 1.6, 1.6), "preto")
        t.linha(xr, 10, xr, base - 20, "cinza_escuro")
    # Grade lateral da gaiola (os lados; a frente fica aberta).
    for x in range(14, W - 14, 6):
        t.linha(x, base - 46, x, base - 18, "cinza_escuro")
    t.linha(14, base - 46, W - 14, base - 46, "cinza_medio")
    # Placa ELEVADOR e lampião pendurado.
    p = Tela(32, 9)
    p.volume(p.retangulo(0, 0, 32, 9), ["couro_profundo", "couro_escuro", "couro"], achatado=1, suave=0.3)
    escrever(p, "DESCE", 3, 2, "amarelo_fogo", grossa=True)
    p.contorno("sombra")
    t.colar(p, W // 2 - 16, 20)
    t.contorno("sombra")
    return t


def jaula_base(w=40):
    """Chão de tábuas e o fundo de uma jaula (atrás do alien preso), com palha suja e
    gosma; as grades da frente são peça de jogo (quebram)."""
    t = Tela(w, 8)
    t.colar(f1.tabuas(w, 6, vertical=False, semente=w, rampa=f1.MADEIRA), 0, 2)
    for x in range(2, w - 2, 3):
        t.ponto(x, 1, "areia_media" if x % 2 else "areia")
    t.chapado(t.elipse(w * 0.6, 1, 4, 1.2), "alien_esc")
    t.contorno("sombra")
    return t


def poste_lampadas(altura=60, semente=0):
    t = Tela(10, altura)
    madeira(t, t.capsula(5, altura - 1, 5, 2, 1.8, 1.4), True, semente)
    t.chapado(t.retangulo(1, 3, 9, 2), "couro_escuro")
    t.contorno("sombra")
    return t


def gerador_pad():
    """Base de concreto rachado com mancha de óleo onde fica o gerador (que é peça de jogo)."""
    t = Tela(54, 6)
    t.cel(t.retangulo(0, 1, 54, 5), ["sombra", "cinza_escuro", "cinza_medio", "cinza"], sombra=1)
    t.chapado(t.elipse(36, 3, 9, 1.6), "preto")
    t.linha(12, 2, 16, 5, "cinza_escuro")
    t.contorno("sombra")
    return t


# ------------------------------------------------------------------ chão
def chao_batido(w, h=26, semente=0):
    """Terra batida da base: pisoteada e escura, com marcas de pneu e de bota, tábuas
    largadas, cascalho e poças de óleo."""
    t = f2.chao_base(w, h, semente)
    rng = np.random.default_rng(semente)
    # Trilhas de pneu (dois sulcos escuros com as marcas da banda).
    for y0 in (3, 7):
        for x in range(w):
            yy = y0 + int(math.sin(x / 90 + y0) * 1.5)
            if 0 <= yy < h:
                t.px[yy, x] = IDX["terra_escura"]
                if x % 4 == 0 and yy + 1 < h:
                    t.px[yy + 1, x] = IDX["terra"]
    for _ in range(w // 70):
        x = int(rng.integers(0, w - 30))
        tb = f1.tabuas(int(rng.integers(18, 34)), 3, vertical=False, semente=int(x))
        t.colar(tb, x, int(rng.integers(1, 5)))
    for _ in range(w // 90):
        x, y = int(rng.integers(10, w - 10)), int(rng.integers(2, 8))
        t.chapado(t.elipse(x, y, rng.uniform(4, 9), 1.2), "preto")
        t.ponto(x - 2, y, "azul_sombra")  # reflexo no óleo
    return t


# ------------------------------------------------------------------ camadas
def noite_bd(wx):
    """Escurecimento das peças de base_detalhe no ponto wx (0 na barraca-laboratório)."""
    return (hora(wx) - 0.67) * 0.35


def pilha_sacos(bd, colunas=3, linhas=2, semente=0):
    t = Tela(colunas * 14 + 6, linhas * 7 + 4)
    chao = t.h - 1
    for j in range(linhas):
        for k in range(colunas - j):
            bd.saco(t, k * 14 + j * 7, chao - j * 7, 16, 8, semente=semente + j * 10 + k)
    return t


def camada_jogo():
    import base_detalhe as bd
    alt = 200
    topo = 216 - alt
    t = Tela(LARGURA, alt)
    y = lambda wy: wy - topo  # noqa: E731
    yc = y(CHAO) - 1
    noite = np.array([noite_bd(x) for x in range(LARGURA)])
    luzes = [(x, 34) for x in (400, 430, 520, 680, 752, 800, 1125, 1140, 1230)] + [(TROPA_X, 40), (LAB_X + 25, 46)]
    verdes = [(1600, 50), (1690, 60), (1760, 50), (QUARENTENA_X, 34)]
    t.colar(bd.chao_acampamento(LARGURA, 26, semente=21, noite=noite, luzes=luzes, verdes=verdes), 0, y(CHAO) - 2)
    # O vidro da borda (fim do trecho 1) ainda entra no começo, misturando em manchas.
    colar_organico(t, f2.chao_vidro(200, 26, semente=14), 0, y(CHAO) - 2, borda=110, semente=4)
    pecas = []

    def por(peca, x, afundar=1, novo=True):
        pecas.append((x, peca, afundar, novo))

    def nova(fn, wx, *a, **k):
        bd.NOITE = noite_bd(wx)
        p = fn(*a, **k)
        bd.NOITE = 0.0
        return p

    # Cerca de arame farpado fechando a base por trás.
    por(nova(bd.cerca, 800, LARGURA - 40, semente=5, placas=(("ÁREA MILITAR", 60), ("PERIGO", 1480))), 20)
    # A) entrada: sacos, placa, barraca da tropa, caixotes, torre, gerador e poste.
    por(nova(pilha_sacos, 110, bd, 4, 2, 3), 96)
    por(nova(bd.barraca, TROPA_X, "tropa", 11), TROPA_X - bd.PORTA_BARRACA)
    por(nova(bd.torre_holofote, TORRES[0][0], 118, 1), TORRES[0][0] - 32)
    por(nova(bd.base_gerador, GERADORES[0][0]), GERADORES[0][0] - 27, 0)
    por(nova(bd.poste_lampadas, 400, 58, 1), 392)
    # B) laboratório, jaulas, quarentena, segunda torre.
    por(nova(bd.barraca, LAB_X, "lab", 12), LAB_X - 98)
    for (x, _a) in JAULAS:
        por(nova(jaula_base_nova, x, bd, 40), x - 20, 0)
    por(nova(pilha_sacos, 780, bd, 3, 2, 6), 770)
    por(nova(bd.poste_lampadas, 760, 58, 2), 752)
    por(nova(bd.barraca, QUARENTENA_X, "quarentena", 13), QUARENTENA_X - bd.PORTA_BARRACA)
    por(nova(bd.poste_lampadas, 1125, 58, 3), 1117)
    por(nova(bd.torre_holofote, TORRES[1][0], 118, 2), TORRES[1][0] - 32)
    por(nova(bd.base_gerador, GERADORES[1][0]), GERADORES[1][0] - 27, 0)
    # C) guindaste, sacos do metralhador e o elevador na beira.
    por(nova(bd.guindaste, GUINDASTE_X, 3), GUINDASTE_X - 26)
    por(nova(pilha_sacos, 1545, bd, 4, 3, 8), 1540)
    por(nova(bd.elevador, FIM, 2), FIM - 50)
    # Peças novas já vêm pintadas na hora certa: o anoitecer pula os pixels delas.
    fixo = np.zeros(t.px.shape, bool)
    fixo[y(CHAO) - 2:] = True
    for x, p, afundar, novo in pecas:
        f1.sombra_contato(t, int(x) + p.w / 2, yc + 1, p.w * (0.9 if novo else 1.05))
        y0 = yc - p.h + afundar
        m = p.px != VAZIO
        sub = t.px[max(0, y0):y0 + p.h, int(x):int(x) + p.w]
        mm = m[max(0, -y0):, :sub.shape[1]][:sub.shape[0]]
        sub[mm] = p.px[max(0, -y0):, :sub.shape[1]][:sub.shape[0]][mm]
        fixo[max(0, y0):y0 + p.h, int(x):int(x) + p.w][mm] = novo
    for x0 in range(0, LARGURA, 40):
        faixa = Tela(min(40, LARGURA - x0), alt)
        faixa.px = t.px[:, x0:x0 + 40].copy()
        anoitecer(faixa, hora(x0 + 20) * 0.85)
        sel = ~fixo[:, x0:x0 + 40]
        t.px[:, x0:x0 + 40][sel] = faixa.px[sel]
    # Cabo elétrico no chão do gerador até as torres.
    for (gx, gid) in GERADORES:
        tx = [tx for (tx, g) in TORRES if g == gid][0]
        a, b = sorted((gx, tx))
        for x in range(a, b):
            t.ponto(x, yc + 1 + math.sin(x / 9) * 0.8, "preto")
    return t, topo


def jaula_base_nova(bd, w=40):
    """Estrado de tábuas da jaula com palha suja, ossos roídos e gosma."""
    t = Tela(w, 9)
    for k, x in enumerate(range(0, w, 5)):
        bd.tabua(t, x, 3, 5, 6, semente=k + w, vertical=True)
    for x in range(2, w - 2, 2):
        t.ponto(x, 2, "corda_n2" if x % 4 else "corda_n3")
        t.ponto(x + 1, 1 + (x % 3 == 0), "corda_n1")
    t.chapado(t.elipse(w * 0.62, 2, 5, 1.2), "alien_esc")
    t.ponto(w * 0.6, 1.6, "alien_luz")
    t.linha(w * 0.25, 1, w * 0.35, 2, "lona_n6")
    t.ponto(w * 0.25, 0.4, "lona_n6")
    t.contorno("mad_n1")
    return t


def camada_perto():
    """Perto (0,75): o miolo do acampamento atrás da cerca, no mesmo nível de detalhe das
    peças de jogo, um pouco mais apagado: barracões de tábua e zinco com janelas acesas
    (ALMOXARIFADO, RÁDIO com antena, RANCHO), caixa d'água na torre, caminhões da Volante,
    tambores, caixotes com lona, barracas e a linha de postes de telégrafo com os fios
    cruzando a tela; mastro da bandeira."""
    import base_detalhe as bd
    import veiculos as vc
    fator = 0.75
    W = int(LARGURA * fator + 548)
    alt = 200
    base = alt - 2
    t = Tela(W, alt)
    lx = lambda wx: int(wx * fator)  # noqa: E731
    pecas = []

    def nova(fn, wx, *a, **k):
        bd.NOITE = noite_bd(wx) + 0.08
        bd.CONTRASTE = 0.85
        p = fn(*a, **k)
        bd.NOITE, bd.CONTRASTE = 0.0, 1.0
        return p
    # Postes de telégrafo e os fios (atrás de tudo).
    postes = list(range(-40, int(W / fator) + 300, 300))
    xs_p = []
    for k, wx in enumerate(postes):
        p = nova(bd.poste_telegrafo, wx, 132, k)
        x = lx(wx)
        f1.colar(t, p, x, base - p.h + 2)
        xs_p.append((x, base - p.h + 2))
    for (xa, ya), (xb, yb) in zip(xs_p[:-1], xs_p[1:]):
        for (ix, iy) in bd.ISOLADORES[:6]:
            bd.fios(t, xa + ix, ya + iy - 1, xb + ix, yb + iy - 1, flecha=9 + ix * 0.1, cor="sombra")
    # Aterro do miolo do acampamento: terra socada com muro de toras e sacos na frente
    # (levanta os barracões acima da cerca).
    ATERRO = 34
    rng = np.random.default_rng(52)
    topo_a = base - ATERRO + (ruido(1, W, 8, 3)[0] * 1.5).astype(int)
    m = t.yy >= topo_a[None, :]
    noite = np.array([noite_bd(x / fator) + 0.06 for x in range(W)])
    va = 0.6 - (t.yy - topo_a[None, :]) / ATERRO * 0.3 + ruido(alt, W, (1, 4), 7) * 0.05
    va = np.where(t.yy < topo_a[None, :] + 1.5, 0.85, va)
    bd.CONTRASTE = 0.8
    bd.pintar(t, m, va - noite[None, :], bd.CHAO)
    for x in range(0, W, 5):
        bd.NOITE = noite[x]
        bd.cilindro(t, x + 2, base + 2, x + 2 + rng.uniform(-0.6, 0.6), topo_a[x] + 6, 2.2, 2.0, semente=x, rachas=1,
                    nos=0, topo_cortado=True, escurecer=0.05)
    bd.NOITE, bd.CONTRASTE = 0.0, 1.0
    base = int(base - ATERRO + 4)
    cam = vc.caminhao(0) if hasattr(vc, "caminhao") else None
    for k, wx in enumerate((150, 980)):
        if cam is not None:
            c = Tela(cam.w, cam.h)
            c.px = cam.px.copy()
            if k:
                c.espelhar()
            anoitecer(c, hora(wx) * 0.75 + 0.15)
            pecas.append((lx(wx), c))
    pecas.append((lx(40), nova(bd.barracao, 40, 120, 64, "ALMOXARIFADO", 1)))
    pecas.append((lx(372), nova(bd.caixa_dagua, 372, 124, 2)))
    pecas.append((lx(540), nova(bd.barracao, 540, 92, 60, "RÁDIO", 3, antena=True)))
    pecas.append((lx(1140), nova(bd.barracao, 1140, 104, 62, "RANCHO", 4)))
    pecas.append((lx(1480), nova(bd.barracao, 1480, 96, 58, "OFICINA", 5)))
    for k, wx in enumerate((330, 820, 1300)):
        pecas.append((lx(wx), nova(bd.tambores, wx, 5, k)))
    for k, wx in enumerate((700, 1400)):
        pecas.append((lx(wx), nova(bd.caixotes_lona, wx, k)))
    for k, wx in enumerate((260, 760, 1050, 1620)):
        pecas.append((lx(wx), nova(bd.barraca_pequena, wx, 52, 30, k, bd.OLIVA)))
    # Mastro sem a bandeira (a bandeira tremula num sprite à parte).
    ms = Tela(10, 120)
    ms.volume(ms.capsula(4, 119, 4, 2, 1.4), f1.METAL, achatado=1, suave=0.3)
    ms.chapado(ms.elipse(4, 2, 2, 2), "amarelo_fogo")
    ms.volume(ms.retangulo(0, 114, 9, 6), fx.CAL, achatado=1, suave=0.3)
    ms.contorno("sombra")
    anoitecer(ms, hora(880) * 0.75 + 0.15)
    pecas.append((lx(880), ms))
    global MASTRO_Y
    MASTRO_Y = base - ms.h + 2
    for x, p in sorted(pecas, key=lambda e: -e[1].h):
        f1.colar(t, p, x, base - p.h + 2)
    return t, fator


MASTRO_Y = 0


def camada_meio():
    """Meio (0,45): a borda levantada da cratera atrás do acampamento, subindo em terraços
    de terra cortada com muro de toras e de sacos; barracas pequenas em fileiras com luz na
    porta, andaimes com rampas, torres de vigia acesas, varais de lâmpadas e fogueiras;
    no fim, a beira da cratera iluminada de verde por baixo."""
    import base_detalhe as bd
    fator = 0.45
    W = int(LARGURA * fator + 548)
    alt = 230
    t = Tela(W, alt)
    rng = np.random.default_rng(8)
    xs = np.arange(W)
    # Terraços: degraus de altura que sobem para a direita, com o ruído da terra.
    degraus = []
    x = 0
    nivel = alt - 70
    while x < W:
        larg = int(rng.integers(90, 170))
        degraus.append((x, x + larg, nivel))
        x += larg
        nivel = int(np.clip(nivel + rng.choice([-26, -18, 14, -10]), 70, alt - 56))
    alto = np.zeros(W, int)
    for (a, b, n) in degraus:
        alto[a:min(W, b)] = n
    alto = (alto + ruido(1, W, 3, 9)[0] * 1.2).astype(int)
    terra = t.yy >= alto[None, :]
    prof = t.yy - alto[None, :]
    # Terra cortada em camadas (estratos) com pedras.
    v = 0.62 - np.clip(prof, 0, 60) / 60 * 0.3 + np.sin((t.yy + ruido(alt, W, (2, 20), 4) * 3) / 3.2) * 0.06 \
        + ruido(alt, W, (1, 3), 5) * 0.05
    v = np.where(prof < 2, 0.82, v)
    # Encosta: riscos de enxurrada descendo, manchas de cascalho e de mato seco.
    v = v + (np.abs(np.sin(t.xx / 7 + ruido(alt, W, (6, 1), 11) * 2)) > 0.96) * -0.12
    v = v + (ruido(alt, W, (3, 6), 12) > 1.1) * 0.08
    v = v - (ruido(alt, W, (2, 4), 13) > 1.3) * 0.1
    noite = np.array([noite_bd(x / fator) for x in xs])
    bd.CONTRASTE = 0.5
    bd.pintar(t, terra, v + 0.12 - noite[None, :], bd.CHAO)
    bd.CONTRASTE = 1.0
    # Muro de arrimo em cada degrau: toras em pé ou sacos.
    for k, (a, b, n) in enumerate(degraus[1:], 1):
        pa, pb, pn = degraus[k - 1]
        if pn == n or a >= W:
            continue
        topo, fundo = min(pn, n), max(pn, n)
        x0 = a - 4 if n < pn else a
        bd.NOITE = noite_bd(a / fator) - 0.04
        bd.CONTRASTE = 0.55
        if k % 2:
            for xx in range(x0, x0 + 8, 3):
                bd.cilindro(t, xx, fundo + 2, xx, topo - 2, 1.4, 1.4, semente=xx, rachas=0, nos=0, topo_cortado=True)
        else:
            for j, yy in enumerate(range(fundo, topo - 2, -6)):
                bd.saco(t, x0 - 4 + (j % 2) * 3, yy, 12, 6, semente=xx if False else j + k)
        bd.NOITE, bd.CONTRASTE = 0.0, 1.0
    # Peças nos terraços.
    def por(fn, x, *a, **kw):
        x = int(x)
        if x < 0 or x >= W - 10:
            return None
        bd.NOITE = noite_bd(x / fator) - 0.04
        bd.CONTRASTE = 0.6
        p = fn(*a, **kw)
        bd.NOITE, bd.CONTRASTE = 0.0, 1.0
        fim = min(W - 1, x + p.w)
        if alto[x:fim + 1].max() - alto[x:fim + 1].min() > 4:
            return None  # não fica em cima de degrau (nada flutuando)
        yy = int(max(alto[x:fim + 1]))
        f1.colar(t, p, x, yy - p.h + 2)
        return yy
    # Pedras grandes meio enterradas na encosta.
    for _ in range(W // 40):
        x = int(rng.integers(0, W - 1))
        yy = int(alto[x] + rng.integers(8, 50))
        if yy >= alt - 2:
            continue
        r = float(rng.uniform(3, 7))
        e = t.elipse(x, yy, r * 1.4, r) & terra
        bd.CONTRASTE = 0.55
        bd.pintar(t, e, 0.95 - ((t.xx - x) + (t.yy - yy)) / (3 * r) - noite[x], bd.CHAO)
        bd.CONTRASTE = 1.0
    for k, (a, b, n) in enumerate(degraus):
        x = a + 8
        while x < b - 40:
            r = rng.random()
            if r < 0.55:
                yb = por(bd.barraca_pequena, x, int(rng.integers(30, 44)), int(rng.integers(18, 24)), int(x), bd.OLIVA,
                         rng.random() < 0.6)
                x += int(rng.integers(44, 60))
            elif r < 0.7:
                por(bd.andaime, x, 44, int(rng.integers(40, 70)), int(x))
                x += 52
            elif r < 0.82:
                tr = torre_vigia_fundo(bd, int(x))
                por(lambda tr=tr: tr, x)
                x += 40
            else:
                por(bd.tambores, x, 3, int(x))
                x += 40
        # Varal de lâmpadas acesas ao longo do terraço.
        if k % 2 == 0 and b - a > 100:
            y0 = n - 26
            for xx in range(a + 10, min(W, b - 10)):
                yy = y0 + math.sin((xx - a - 10) / (b - a - 20) * math.pi) * 5
                t.ponto(xx, yy, "sombra")
                if (xx - a) % 9 == 0:
                    t.ponto(xx, yy + 1, "ouro_escuro")
                    t.ponto(xx, yy + 2, "amarelo_claro")
    # Fogueiras do acampamento com fumaça (animadas).
    for k, wx in enumerate((520, 1180)):
        fxp = int(wx * fator)
        f2.registrar_fogo("meio", fxp, alto[fxp] + 2, 3.5, 70 + k)
        f2.registrar_fumaca("meio", fxp, alto[fxp] - 2, 90, 12, f2.FUMACA_ESCURA_C, semente=80 + k, vento=-0.3, fino=1.6)
    # Beira da cratera no fim: crista com brilho verde vindo de baixo.
    ini = int(1380 * fator)
    for x in range(ini, W):
        f = min(1, (x - ini) / 80)
        y = alto[x]
        if f > 0:
            t.ponto(x, y, "alien_medio" if f > 0.5 else "alien_esc")
            if f > 0.6:
                t.ponto(x, y + 1, "alien_esc")
    return t, fator


def torre_vigia_fundo(bd, semente=0):
    """Torre de vigia pequena para o fundo, com a guarita acesa."""
    t = Tela(30, 64)
    base = 63
    for (a, b) in ((3, 9), (27, 21)):
        bd.cilindro(t, a, base, b, 16, 1.2, 1.0, semente=semente + a, rachas=0, nos=0)
    for y in range(24, base - 4, 12):
        bd.cilindro(t, 6, y, 24, y + 10, 0.7, 0.7, semente=y, rachas=0, nos=0)
        bd.cilindro(t, 24, y, 6, y + 10, 0.7, 0.7, semente=y + 1, rachas=0, nos=0)
    bd.tabua(t, 4, 6, 22, 11, semente=semente)
    t.chapado(t.retangulo(8, 9, 14, 5), "lona_q2")
    t.chapado(t.elipse(13, 11, 3, 2), "lona_q3")
    zinco(t, t.poligono([(2, 6), (15, 0), (28, 6)]), semente) if False else None
    roof = t.poligono([(2, 7), (15, 1), (28, 7)])
    bd.zinco(t, roof, semente, 0.6)
    corpo = t.px != VAZIO
    t.px[ndimage.binary_dilation(corpo) & ~corpo] = IDX["mad_n1"]
    return t


def camada_longe():
    """Bem longe (0,25): serras roxas recortadas contra o céu e, no fim, a borda da cratera
    enorme com a coluna de fumaça do disco iluminada de verde por baixo."""
    fator = 0.25
    W = int(LARGURA * fator + 548)
    alt = 280
    t = Tela(W, alt)
    x = np.arange(W)
    for base, amp, sem, rampa in ((alt - 92, 16, 5, ["sombra_media", "azul_sombra", "roxo_escuro", "roxo"]),
                                  (alt - 64, 10, 9, ["sombra", "sombra_media", "azul_sombra", "roxo_escuro"])):
        perfil = base + amp * np.sin(x / 80 + sem) + amp * 0.6 * np.sin(x / 27 + 2 * sem) + 3 * ruido(1, W, 9, sem)[0]
        m = t.yy >= perfil[None, :]
        sub = Tela(W, alt)
        sub.volume(m, rampa, luz=(-0.8, -0.5), achatado=14, suave=4, ambiente=0.3, linha=False)
        t.px[m] = sub.px[m]
    cx = 1650 * fator + 300
    f2.registrar_fumaca("longe", cx, alt - 60, alt - 30, 70, f2.FUMACA_ESCURA, semente=17, vento=-0.3, abre=1.3, fino=16,
                        denso=2.2, luz_verde=True)
    fundo_px = t.px.copy()
    n = ruido(1, W, 7, 19)[0] * 5
    crista = alt - 84 + ((x - cx) / 170) ** 2 * 40 + n
    borda = (t.yy > crista[None, :]) & (np.abs(x[None, :] - cx) < 330)
    prof = t.yy - crista[None, :]
    v = 0.5 - np.clip(prof, 0, 60) / 60 * 0.15 + ruido(alt, W, (2, 7), 21) * 0.06
    pintar_niveis(t, borda, v, ["preto", "marrom_noite", "couro_profundo", "terra_escura"])
    topo_b = borda & ~np.roll(borda, 1, 0)
    t.px[topo_b] = IDX["alien"]
    t.px[ndimage.binary_dilation(topo_b, iterations=2) & ~borda & (t.px != VAZIO) & (lim(alt, W) < 0.55)] = IDX["alien_esc"]
    frente = Tela(W, alt)
    frente.px = np.where(t.px != fundo_px, t.px, VAZIO).astype(t.px.dtype)
    fundo = Tela(W, alt)
    fundo.px = fundo_px
    return fundo, frente, fator


def camada_frente():
    """Na frente (1,1): passa por cima do chão, escura e com a beirada pega pela luz:
    touceiras de capim seco alto, sacos de areia, rolo de arame farpado, caixote quebrado e
    pedras. Espalhadas sem tapar o jogo (só a faixa de baixo)."""
    import base_detalhe as bd
    fator = 1.1
    W = int(LARGURA * fator + 548)
    alt = 34
    t = Tela(W, alt)
    rng = np.random.default_rng(61)
    chao = alt - 1

    def capim(x):
        for k in range(int(rng.integers(9, 16))):
            a = rng.uniform(-0.8, 0.8)
            L = rng.uniform(8, 22)
            x0 = x + rng.uniform(-6, 6)
            for j in range(int(L)):
                f = j / L
                px = x0 + math.sin(a) * j + a * f * f * 6
                py = chao - j
                t.ponto(px, py, "preto" if f < 0.75 else "sombra")
                if j % 3 == 0 and a < 0:
                    t.ponto(px - 1, py, "sombra_media")
            t.ponto(x0 + math.sin(a) * L + a * 6, chao - L, "chao_n3")

    x = 60
    while x < W - 60:
        r = rng.random()
        if r < 0.45:
            capim(x)
            if rng.random() < 0.5:
                capim(x + rng.uniform(8, 16))
        elif r < 0.65:
            bd.NOITE = 0.42
            bd.saco(t, x, chao, 18, 9, semente=int(x))
            bd.saco(t, x + 14, chao, 17, 9, semente=int(x) + 1)
            bd.saco(t, x + 7, chao - 8, 17, 8, semente=int(x) + 2)
            bd.NOITE = 0.0
        elif r < 0.82:
            # Rolo de arame farpado (espiral) com farpas.
            for k in range(70):
                a = k / 70 * math.pi * 10
                px = x + k * 0.7 + math.cos(a) * 3
                py = chao - 6 + math.sin(a) * 5
                t.ponto(px, py, "sombra" if math.sin(a) > 0 else "preto")
                if k % 6 == 0:
                    t.ponto(px, py - 1, "cinza_escuro")
        else:
            bd.NOITE = 0.42
            e = t.elipse(x + 10, chao - 3, 12, 6)
            bd.pintar(t, e, 0.8 - ((t.xx - x) + (t.yy - chao + 9)) / 24, bd.CHAO)
            bd.NOITE = 0.0
            capim(x + 20)
        x += int(rng.integers(170, 340))
    return t, fator


# ------------------------------------------------------------------ peças de jogo (sprites)
def holofote(q=0):
    """Cabeça do holofote (24x18): tambor de chapa com aletas, aro grosso, vidro aceso
    (q0, q1 piscando forte) ou quebrado (q2), alça e base giratória."""
    t = Tela(24, 18)
    t.cel(t.retangulo(9, 13, 6, 5), f1.METAL, sombra=1)  # base
    corpo = t.capsula(5, 8, 15, 8, 6, 5)
    t.cel(corpo, ["preto", "sombra", "cinza_escuro", "cinza_medio", "cinza"], sombra=1)
    for x in (6, 8, 10):
        t.linha(x, 3, x, 13, "sombra")
    t.cel(t.elipse(17, 8, 4.4, 6.6), ["sombra", "cinza_medio", "cinza_luz"], sombra=0)  # aro
    vidro = t.elipse(18, 8, 3.0, 5.2)
    if q == 2:
        t.chapado(vidro, "preto")
        t.linha(16, 4, 19, 9, "cinza_luz")
        t.linha(19, 6, 17, 12, "cinza")
    else:
        t.chapado(vidro, "amarelo_claro")
        t.chapado(t.elipse(18.6, 8, 1.8, 3.6), "branco")
        if q == 1:
            t.chapado(t.elipse(21, 8, 2, 5) & ~vidro, "amarelo_claro")
    t.linha(7, 2, 14, 2, "cinza_escuro")  # alça
    t.contorno("sombra")
    return t


def gerador(q=0):
    """Gerador a diesel (46x34) num chassi de ferro: motor com aletas, volante grande de
    raios, tanque com tampa, escapamento soltando fumaça, painel com relógio e lâmpada
    vermelha, cabos saindo. q0/q1: roncando (tremendo, volante girado), q2: arrebentado
    (chapa rasgada, volante caído, fogo)."""
    t = Tela(46, 34)
    d = 1 if q == 1 else 0
    quebrado = q == 2
    t.cel(t.retangulo(2, 28, 42, 5), ["preto", "sombra", "cinza_escuro", "cinza_medio"], sombra=1)  # chassi
    for x in (6, 38):
        t.chapado(t.retangulo(x, 31, 3, 3), "sombra")
    # Tanque de combustível em cima (cilindro vermelho desbotado).
    t.cel(t.capsula(8, 6 + d, 30, 6 + d, 4), ["sombra", "vermelho_esc", "vermelho_medio", "vermelho"], sombra=1)
    t.chapado(t.retangulo(26, 1 + d, 3, 2), "cinza_medio")
    # Motor com aletas.
    motor = t.retangulo(10, 11 + d, 20, 17)
    t.cel(motor, ["preto", "sombra", "caatinga_esc", "caatinga_media", "caatinga"], sombra=1)
    for y in range(13 + d, 27 + d, 2):
        t.linha(11, y, 28, y, "caatinga_esc")
    # Volante de raios do lado.
    vx, vy = 37, 18 + d
    t.cel(t.elipse(vx, vy, 7, 7) & ~t.elipse(vx, vy, 5, 5), f1.METAL, sombra=1)
    for k in range(4):
        a = k * math.pi / 4 + (math.pi / 8 if q == 1 else 0)
        t.linha(vx - math.cos(a) * 5, vy - math.sin(a) * 5, vx + math.cos(a) * 5, vy + math.sin(a) * 5, "cinza_escuro")
    t.chapado(t.elipse(vx, vy, 1.4, 1.4), "cinza_luz")
    # Painel com relógio e lâmpada.
    t.cel(t.retangulo(2, 13 + d, 8, 10), f1.METAL, sombra=1)
    t.chapado(t.elipse(6, 16 + d, 2, 2), "branco")
    t.linha(6, 16 + d, 7, 15 + d, "preto")
    t.ponto(5, 20 + d, "vermelho" if q != 2 else "sombra")
    # Escapamento.
    t.cel(t.capsula(14, 10 + d, 14, 2 + d, 1.4), ["preto", "sombra", "cinza_escuro"], sombra=0)
    if quebrado:
        rasgo = t.poligono([(12, 14), (20, 11), (27, 18), (19, 25), (13, 22)])
        t.chapado(rasgo, "preto")
        t.chapado(t.elipse(19, 18, 3, 3) & rasgo, "laranja_fogo")
        t.chapado(t.elipse(19, 18, 1.4, 1.4) & rasgo, "amarelo_fogo")
        t.px[(t.xx > 30) & (t.yy < 26) & (t.px != VAZIO)] = IDX["sombra"]  # volante caído/queimado
        t.chapado(t.elipse(38, 30, 6, 2), "cinza_escuro")
    t.contorno("sombra")
    return t


def jaula(q=0, w=40, h=44):
    """Grades da frente de uma jaula de ferro rebitado (40x44): barras grossas com luz,
    travessas, cadeado e placa de PERIGO; q1 arrebentada (barras tortas e abertas)."""
    t = Tela(w, h)
    base = h - 1
    aberta = q == 1
    for k, x in enumerate(range(3, w - 2, 5)):
        if aberta and 1 <= k <= 5:
            # Barras entortadas para fora, rompidas no meio.
            t.cel(t.capsula(x, 2, x - (k - 3) * 3, 16, 1.0), f1.METAL, sombra=0)
            t.cel(t.capsula(x, base - 2, x + (k - 3) * 4, base - 14, 1.0), f1.METAL, sombra=0)
            continue
        t.cel(t.capsula(x, 2, x, base - 2, 1.0), f1.METAL, sombra=0)
    for y in (2, base - 2):
        t.cel(t.capsula(1, y, w - 2, y, 1.6), ["sombra", "cinza_escuro", "cinza_medio", "cinza"], sombra=1)
    if not aberta:
        t.cel(t.capsula(1, h * 0.5, w - 2, h * 0.5, 1.0), ["sombra", "cinza_escuro", "cinza_medio"], sombra=0)
        t.cel(t.retangulo(w * 0.5 - 3, h * 0.5 - 2, 6, 6), ["sombra", "ouro_escuro", "amarelo_fogo"], sombra=1)
        t.ponto(w * 0.5, h * 0.5 + 1, "preto")
    p = Tela(18, 7)
    p.chapado(p.retangulo(0, 0, 18, 7), "amarelo_fogo")
    escrever(p, "ET", 5, 1, "preto")
    p.contorno("sombra")
    t.colar(p, int(w / 2 - 9), 6 if not aberta else 30)
    t.contorno("sombra")
    return t


def pedaco_disco(q=0):
    """Pedaço do casco do disco pendurado (56x40): chapa curva de liga alienígena com
    runas verdes acesas que pulsam (q0/q1), borda arrancada com fios soltos e a corrente
    passando pelo furo."""
    t = Tela(56, 40)
    casco = t.elipse(28, 34, 27, 26) & (t.yy > 10) & (t.yy < 36)
    t.cel(casco, ["preto", "sombra", "cinza_escuro", "cinza_medio", "cinza", "cinza_luz"], sombra=2)
    # Borda arrancada (dentes) embaixo.
    for x in range(3, 54, 4):
        t.chapado(t.poligono([(x, 35), (x + 2, 39 - (x % 3)), (x + 4, 35)]), "cinza_escuro")
    # Faixa e runas.
    t.chapado(casco & (np.abs(t.yy - 24) < 1.2), "sombra")
    cor = "alien_brilho" if q else "alien"
    for k, x in enumerate(range(10, 48, 6)):
        t.linha(x, 21, x + 2, 21, cor)
        t.ponto(x + (k % 2) * 2, 22 + (k % 3), cor)
    t.chapado(t.elipse(28, 17, 4, 3), "preto")  # furo da corrente
    t.ponto(28, 16, "alien_esc" if q else "alien_profundo")
    # Fios soltos pendurados da borda.
    for x in (8, 44):
        t.linha(x, 35, x + 1, 39, "vermelho_esc")
    t.contorno("sombra")
    return t


def lampada(q=0):
    """Lâmpada do varal de luz (6x8): acesa (q0), acesa forte (q1), apagada (q2)."""
    t = Tela(6, 8)
    t.chapado(t.retangulo(2, 0, 2, 2), "cinza_escuro")
    if q == 2:
        t.chapado(t.elipse(3, 4.5, 2, 2.4), "sombra_media")
    else:
        t.chapado(t.elipse(3, 4.5, 2.2, 2.6), "laranja_fogo" if q == 0 else "amarelo_fogo")
        t.chapado(t.elipse(2.6, 4, 1, 1.4), "amarelo_claro" if q == 0 else "branco")
    return t


def bandeira(q=0):
    """Bandeira da Volante no mastro tremulando (34x20, 4 quadros, sem o mastro)."""
    t = Tela(34, 20)
    pts_c, pts_b = [], []
    for k in range(13):
        x = 1 + k * 2.6
        o = math.sin(k * 0.7 - q * math.pi / 2) * (k / 12) * 3
        pts_c.append((x, 2 + o))
        pts_b.append((x, 17 + o * 0.8))
    fl = t.poligono(pts_c + pts_b[::-1])
    t.volume(fl, ["sombra", "caatinga_esc", "caatinga", "mandacaru"], achatado=2, suave=0.6, ambiente=0.3)
    # Dobras: faixas escuras onde a onda desce.
    for k in range(12):
        if math.cos(k * 0.7 - q * math.pi / 2) < -0.4:
            x = 1 + k * 2.6
            t.px[fl & (np.abs(t.xx - x) < 1)] = IDX["caatinga_esc"]
    t.chapado(t.poligono([(9, 10), (17, 5), (25, 10), (17, 15)]) & fl, "amarelo_fogo")
    t.contorno("sombra")
    return t


def plataforma_elevador():
    """Plataforma do elevador (60x12): estrado de ferro com grade e correntes nos cantos."""
    t = Tela(60, 12)
    t.cel(t.retangulo(0, 6, 60, 6), ["preto", "sombra", "cinza_escuro", "cinza_medio", "cinza"], sombra=1)
    for x in range(3, 58, 5):
        t.linha(x, 7, x, 11, "sombra")
    for x in (2, 57):
        for y in range(0, 6, 2):
            t.ponto(x, y, "cinza_medio")
    t.contorno("sombra")
    return t


# Peças vivas no nível novo (base_detalhe) substituem as de cima.
from base_detalhe import holofote, gerador, jaula, pedaco_disco, lampada, bandeira, plataforma_elevador  # noqa: E402,F811


# ------------------------------------------------------------------ dados
def dados_fase():
    """Dados do trecho 2 (assets/fases/fase2b.json), lidos por src/scenes/Fase2bScene.js."""
    solidos = [[0, CHAO, LARGURA, 200]]
    # Plataformas das torres (dá para subir e atirar de cima) e o teto do sarilho.
    for (x, _g) in TORRES:
        solidos.append([x - 23, CHAO - 118 + 14, 46, 6, 1])
    solidos.append([GUINDASTE_X + 4, CHAO - 44, 32, 6, 1])
    return {
        "largura": LARGURA,
        "inicio": [40, CHAO - 20],
        "solidos": solidos,
        "caixotes": [[330, CHAO - 18], [700, CHAO - 24, "barril"], [880, CHAO - 24, "barril"],
                     [1290, CHAO - 18], [1308, CHAO - 18], [1299, CHAO - 36], [1500, CHAO - 24, "barril"]],
        "refens": [],
        "cientistas": [[LAB_X + 50, CHAO]],
        "itens": [],
        "bodes": [],
        "discos": [],
        "inimigos": [
            [250, CHAO, "mascarado", {"distraido": True}],
            [TORRES[0][0], CHAO - 104 + 5, "mascarado"],
            [415, CHAO, "volante", {"cena": "truco", "olha": 1}], [445, CHAO, "volante", {"cena": "truco", "olha": -1, "prop": False}],
            [1120, CHAO, "mascarado", {"distraido": True}],
            [TORRES[1][0], CHAO - 104 + 5, "mascarado"],
            [1560, CHAO, "metralhador"],
        ],
        "ondas": [
            {"gatilho": 380, "trava": [230, 778], "inimigos": [["mascarado", f"porta:{TROPA_X}", 0], ["mascarado", "dir", 800],
                                                               ["volante", f"porta:{TROPA_X}", 1500], ["mascarado", "dir", 2300]]},
            {"gatilho": 900, "trava": [720, 1268], "inimigos": [["contaminado", f"porta:{QUARENTENA_X}", 0],
                                                                ["mascarado", "dir", 700],
                                                                ["contaminado", f"porta:{QUARENTENA_X}", 1600],
                                                                ["mascarado", "dir", 2200, {"escudo": True}],
                                                                ["contaminado", f"porta:{QUARENTENA_X}", 3000]]},
            {"gatilho": 1430, "trava": [1252, 1800], "inimigos": [["oficial", "dir", 0], ["mascarado", "dir", 500],
                                                                  ["mascarado", "esq", 1200], ["contaminado", "dir", 1900],
                                                                  ["mascarado", "dir", 2600, {"escudo": True}],
                                                                  ["metralhador", "dir", 3300]]},
        ],
        "fogueiras": [[430, CHAO]], "forquilhas": [], "buracos": [], "fim": FIM,
        "casas": [], "varais": [], "jumentos": [], "urubus": [], "galinhas": [],
        "biplanos": [], "segredos": [],
        # Peças vivas da base (src/objetos/Base.js).
        "base": {
            "holofotes": [{"x": x, "y": CHAO - 118 + 2, "gerador": g, "de": 0.55, "ate": 1.25} for (x, g) in TORRES],
            "geradores": [{"x": x, "id": g} for (x, g) in GERADORES],
            "jaulas": [{"x": x, "alien": a} for (x, a) in JAULAS],
            "guindaste": {"x": PONTA_LANCA[0], "y": PONTA_LANCA[1] + 2, "comprimento": 70},
            "lampadas": [{"x0": 400, "x1": 760, "y": CHAO - 58 + 4, "gerador": 0},
                         {"x0": 760, "x1": 1125, "y": CHAO - 58 + 4, "gerador": 1}],
            "elevador": {"x": FIM, "y": CHAO},
            "noite": {"de": 0, "ate": 1300},
        },
    }


def exportar(saida, raiz):
    """Grava as camadas do trecho 2 (f2b_*.png), as peças vivas e assets/fases/fase2b.json."""
    import json
    from motor import folha
    f2.FUMACAS.clear()
    f2.FOGOS.clear()
    jogo, topo = camada_jogo()
    perto, fp = camada_perto()
    meio, fm = camada_meio()
    longe, borda_l, fl = camada_longe()
    frente, ff = camada_frente()
    for nome, c in (("f2b_jogo", jogo), ("f2b_perto", perto), ("f2b_meio", meio), ("f2b_longe", longe),
                    ("f2b_borda", borda_l), ("f2b_frente", frente)):
        c.imagem().save(saida / f"{nome}.png", optimize=True)
    ceu_tarde().imagem().save(saida / "ceu_tarde.png", optimize=True)
    ceu_noite().imagem().save(saida / "ceu_noite.png", optimize=True)
    fumacas = []
    for k, f in enumerate(f2.FUMACAS):
        qs, x0, y0 = f2.quadros_fumaca(f)
        w_, h_ = f2.folha_grade(qs, saida / f"f2b_fumaca_{k}.png")
        fumacas.append({"chave": f"f2b_fumaca_{k}", "camada": f["camada"], "x": x0, "y": y0, "w": w_, "h": h_, "n": len(qs)})
    qs = [q for f in f2.FOGOS for q in f2.quadros_fogo(f)]
    f2.folha_grade(qs, saida / "f2b_fogo.png")
    fogos = [{"camada": f["camada"], "x": int(round(f["x"] - f2.FOGO_W / 2)), "y": int(round(f["y"] - (f2.FOGO_H - 2))),
              "q": k * f2.FOGO_N} for k, f in enumerate(f2.FOGOS)]
    # Peças vivas.
    folha([holofote(q) for q in range(3)], saida / "holofote.png")
    folha([gerador(q) for q in range(3)], saida / "gerador.png")
    folha([jaula(q) for q in range(2)], saida / "jaula.png")
    folha([pedaco_disco(q) for q in range(2)], saida / "pedaco_disco.png")
    folha([lampada(q) for q in range(3)], saida / "lampada.png")
    folha([bandeira(q) for q in range(4)], saida / "bandeira.png")
    folha([plataforma_elevador()], saida / "plataforma_elevador.png")
    import cientista as ci
    folha(ci.folha(), saida / "cientista.png")
    d = dados_fase()
    d["fumacas"] = fumacas
    d["fogos"] = fogos
    d["fogo"] = {"w": f2.FOGO_W, "h": f2.FOGO_H, "n": f2.FOGO_N}
    # Bandeira no mastro da camada de perto (mastro em wx 880, fator 0,75).
    d["bandeira"] = {"camada": "perto", "x": int(880 * fp) + 5, "y": MASTRO_Y + 3}
    d["camadas"] = {"jogo": {"y": topo, "fator": 1}, "perto": {"base": 194, "fator": fp}, "meio": {"base": 192, "fator": fm},
                    "longe": {"base": 160, "fator": fl}, "borda": {"base": 160, "fator": fl}, "frente": {"base": 220, "fator": ff}}
    pasta = raiz / "assets/fases"
    (pasta / "fase2b.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")))


def previa(caminho, cams=(0, 450, 900, 1252)):
    """Telas do trecho em várias posições da câmera (céu, camadas e as peças vivas paradas)."""
    from PIL import Image
    f2.FUMACAS.clear()
    f2.FOGOS.clear()
    jogo, topo = camada_jogo()
    perto, fp = camada_perto()
    meio, fm = camada_meio()
    longe, borda_l, fl = camada_longe()
    frente, ff = camada_frente()
    fumacas = [(f, *f2.quadros_fumaca(f, n=1)) for f in f2.FUMACAS]
    ct, cn_ = ceu_tarde().imagem(), ceu_noite().imagem()
    d = dados_fase()
    vivas = []
    for h in d["base"]["holofotes"]:
        vivas.append((holofote(0), h["x"] - 12, h["y"] - 14))
    for g in d["base"]["geradores"]:
        vivas.append((gerador(0), g["x"] - 23, CHAO - 34 + 1))
    for j in d["base"]["jaulas"]:
        vivas.append((jaula(0), j["x"] - 20, CHAO - 44 - 1))
    gx, gy = d["base"]["guindaste"]["x"], d["base"]["guindaste"]["y"]
    vivas.append((pedaco_disco(1), gx - 28, gy + 70 - 14))
    vivas.append((plataforma_elevador(), FIM - 30, CHAO - 8))
    ims = []
    DY = 92
    for cam in cams:
        o = Image.new("RGBA", (548, 308))
        nf = float(np.clip(cam / 1300, 0, 1))
        o.alpha_composite(Image.blend(ct.convert("RGBA"), cn_.convert("RGBA"), nf))
        for (c, fat, base) in ((longe, fl, 160), (borda_l, fl, 160)):
            o.alpha_composite(c.imagem(), (-int(cam * fat), base - c.h + DY))
            if c is longe:
                for f, qs, x0, y0 in fumacas:
                    if f["camada"] == "longe":
                        o.alpha_composite(qs[0].imagem(), (x0 - int(cam * fat), base - longe.h + DY + y0))
        o.alpha_composite(meio.imagem(), (-int(cam * fm), 192 - meio.h + DY))
        for f, qs, x0, y0 in fumacas:
            if f["camada"] == "meio":
                o.alpha_composite(qs[0].imagem(), (x0 - int(cam * fm), 192 - meio.h + DY + y0))
        o.alpha_composite(perto.imagem(), (-int(cam * fp), 194 - perto.h + DY))
        o.alpha_composite(jogo.imagem(), (-cam, topo + DY))
        for (p, x, y) in vivas:
            o.alpha_composite(p.imagem(), (int(x - cam), int(y + DY)))
        o.alpha_composite(frente.imagem(), (-int(cam * ff), 220 - frente.h + DY))
        ims.append(o)
    out = Image.new("RGBA", (548 * 2, 308 * ((len(ims) + 1) // 2)))
    for k, im in enumerate(ims):
        out.alpha_composite(im, ((k % 2) * 548, (k // 2) * 308))
    out.save(caminho)


if __name__ == "__main__":
    previa(sys.argv[1] if len(sys.argv) > 1 else "/tmp/f2b.png")
